import os
import sqlite3
from contextlib import contextmanager
import shutil
import operator
from typing import TypedDict, Annotated, Sequence
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import google.generativeai as genai
from PIL import Image
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import uvicorn
import jwt
from passlib.context import CryptContext

load_dotenv()

# Database configuration (SQLite by default; Neon Postgres when DATABASE_URL is set)
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
IS_POSTGRES = DATABASE_URL.startswith("postgres")

try:
    # Only needed for Postgres
    import psycopg2  # type: ignore
except Exception:
    psycopg2 = None  # type: ignore

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


app = FastAPI(title="AI Maintenance Reporter", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

STATIC_DIR = Path("static")
STATIC_DIR.mkdir(exist_ok=True)


@contextmanager
def get_connection():
    """Provide a database connection for SQLite or Postgres (Neon)."""
    if IS_POSTGRES:
        if psycopg2 is None:
            raise RuntimeError("psycopg2 is required for PostgreSQL. Please add 'psycopg2-binary' to requirements and install it.")
        # Connect to Neon with proper SSL settings
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False  # Explicit transaction control
    else:
        conn = sqlite3.connect("maintenance_tickets.db")
    try:
        yield conn
    finally:
        conn.close()


def adapt_query(query: str) -> str:
    """Convert SQLite '?' placeholders to Postgres '%s' placeholders if needed."""
    return query.replace("?", "%s") if IS_POSTGRES else query


def init_db():
    """Create tables if they don't exist for the active DB engine."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if IS_POSTGRES:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255),
                    role VARCHAR(50) DEFAULT 'student',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    student_name VARCHAR(255),
                    location VARCHAR(255),
                    issue_type VARCHAR(100),
                    description TEXT,
                    image_path TEXT,
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    priority VARCHAR(50) DEFAULT 'medium',
                    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
                """
            )
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tickets_user_id ON tickets(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets(created_at DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        else:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    role TEXT DEFAULT 'student',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    student_name TEXT,
                    location TEXT,
                    issue_type TEXT,
                    description TEXT,
                    image_path TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    priority TEXT DEFAULT 'medium',
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
                """
            )
        conn.commit()


init_db()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "student"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str


class TicketRequest(BaseModel):
    student_name: str
    location: str


class TicketResponse(BaseModel):
    ticket_id: int
    student_name: str
    location: str
    issue_type: str
    description: str
    ticket_status: str
    priority: str
    created_at: str


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    image_path: str
    issue_detected: str
    issue_type: str
    priority: str
    ticket_created: bool


def image_reasoning_tool(image_path: str) -> str:
    """
    Uses Gemini 2.5 Pro to analyze an image and detect broken or damaged objects.
    Especially checks for issues in fans, lights, furniture, or electronics.
    
    """
    try:
        if not os.path.exists(image_path):
            return f"Error: Image not found at {image_path}"

        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        model = genai.GenerativeModel("gemini-2.5-pro")

        image = Image.open(image_path)

        prompt = (
            "You are a maintenance inspector. Analyze this image and provide a brief 2-3 sentence summary of any maintenance issues. "
            "Focus on: fans, lights, furniture, or electronics. "
            "If damaged: state the item and specific problem (e.g., 'Ceiling fan blade is severely bent and broken'). "
            "If no issues: respond with exactly 'No maintenance issues detected'. "
            "Keep your response concise and under 100 words."
        )

        response = model.generate_content([prompt, image])

        return response.text.strip() if response.text else "No visible issues detected."
    
    except Exception as e:
        return f"Error occurred: {str(e)}"


def analyze_image_node(state: AgentState) -> AgentState:
    """Node to analyze the uploaded image using Gemini"""
    image_path = state["image_path"]
    
    analysis_result = image_reasoning_tool(image_path)
    
    state["issue_detected"] = analysis_result
    state["messages"] = state.get("messages", []) + [
        AIMessage(content=f"Image Analysis Complete: {analysis_result}")
    ]
    
    return state


def classify_issue_node(state: AgentState) -> AgentState:
    """Node to classify the issue type and priority"""
    issue_text = state["issue_detected"].lower()
    
    if "fan" in issue_text:
        issue_type = "Fan"
    elif "light" in issue_text or "bulb" in issue_text or "lamp" in issue_text:
        issue_type = "Light"
    elif "furniture" in issue_text or "chair" in issue_text or "table" in issue_text or "desk" in issue_text:
        issue_type = "Furniture"
    elif "electronics" in issue_text or "computer" in issue_text or "screen" in issue_text:
        issue_type = "Electronics"
    elif "electrical" in issue_text or "wire" in issue_text or "socket" in issue_text:
        issue_type = "Electrical"
    else:
        issue_type = "Other"
    
    critical_keywords = ["severely", "broken", "damaged", "fire", "sparking", "dangerous", "hazard", "catastrophic", "major", "shattered"]
    high_keywords = ["not working", "malfunctioning", "cracked", "bent", "loose", "leaking"]
    low_keywords = ["no maintenance issues", "no issues", "no visible issues", "minor", "slight"]
    
    if any(keyword in issue_text for keyword in low_keywords):
        priority = "low"
    elif any(keyword in issue_text for keyword in critical_keywords):
        priority = "high"
    elif any(keyword in issue_text for keyword in high_keywords):
        priority = "medium"
    else:
        priority = "low"
    
    state["issue_type"] = issue_type
    state["priority"] = priority
    state["messages"] = state.get("messages", []) + [
        AIMessage(content=f"Issue classified as: {issue_type} (Priority: {priority})")
    ]
    
    return state


def create_ticket_node(state: AgentState) -> AgentState:
    """Node to create and store the maintenance ticket"""
    state["ticket_created"] = True
    state["messages"] = state.get("messages", []) + [
        AIMessage(content="Maintenance ticket created successfully")
    ]
    
    return state


def build_workflow():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("analyze_image", analyze_image_node)
    workflow.add_node("classify_issue", classify_issue_node)
    workflow.add_node("create_ticket", create_ticket_node)
    
    workflow.set_entry_point("analyze_image")
    workflow.add_edge("analyze_image", "classify_issue")
    workflow.add_edge("classify_issue", "create_ticket")
    workflow.add_edge("create_ticket", END)
    
    return workflow.compile()


agent_workflow = build_workflow()


@app.get("/")
async def root():
    return {"message": "AI Maintenance Reporter API", "status": "running"}


@app.post("/api/auth/signup", response_model=TokenResponse)
async def signup(user_data: SignupRequest):
    """Register a new user with @reva.edu.in email"""
    try:
        if not user_data.email.endswith("@reva.edu.in"):
            raise HTTPException(status_code=400, detail="Only @reva.edu.in emails are allowed")
        
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(adapt_query("SELECT id FROM users WHERE email = ?"), (user_data.email,))
            existing_user = cursor.fetchone()

            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")

            hashed_password = get_password_hash(user_data.password)

            if IS_POSTGRES:
                cursor.execute(
                    """
                    INSERT INTO users (email, password_hash, full_name, role)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (user_data.email, hashed_password, user_data.full_name, user_data.role),
                )
                user_id = cursor.fetchone()[0]
            else:
                cursor.execute(
                    """
                    INSERT INTO users (email, password_hash, full_name, role)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_data.email, hashed_password, user_data.full_name, user_data.role),
                )
                user_id = cursor.lastrowid
            conn.commit()
        
        access_token = create_access_token({"sub": user_data.email, "id": user_id})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user={"id": user_id, "email": user_data.email, "full_name": user_data.full_name, "role": user_data.role}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during signup: {str(e)}")


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """Login with email and password"""
    try:
        if not credentials.email.endswith("@reva.edu.in"):
            raise HTTPException(status_code=400, detail="Only @reva.edu.in emails are allowed")
        
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                adapt_query("SELECT id, email, password_hash, full_name, role FROM users WHERE email = ?"),
                (credentials.email,),
            )
            user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not verify_password(credentials.password, user[2]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        access_token = create_access_token({"sub": user[1], "id": user[0]})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user={"id": user[0], "email": user[1], "full_name": user[3], "role": user[4] if len(user) > 4 else "student"}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user(token_data: dict = Depends(verify_token)):
    """Get current user information"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                adapt_query("SELECT id, email, full_name, role FROM users WHERE email = ?"),
                (token_data["sub"],),
            )
            user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(id=user[0], email=user[1], full_name=user[2], role=user[3] if len(user) > 3 else "student")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")


@app.post("/api/tickets", response_model=TicketResponse)
async def create_ticket(
    student_name: str = Form(...),
    location: str = Form(...),
    image: UploadFile = File(...),
    token_data: dict = Depends(verify_token)
):
    """Upload an image and create a maintenance ticket (protected route)"""
    try:
        user_id = token_data["id"]
        print(f"Received request - Student: {student_name}, Location: {location}, Image: {image.filename}")
        
        if not image.filename:
            raise HTTPException(status_code=400, detail="No image file provided")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"{timestamp}_{image.filename}"
        image_path = UPLOAD_DIR / image_filename
        
        print(f"Saving image to: {image_path}")
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        print("Image saved successfully")
        
        initial_state: AgentState = {
            "messages": [HumanMessage(content=f"Analyzing image from {student_name} at {location}")],
            "image_path": str(image_path),
            "issue_detected": "",
            "issue_type": "",
            "priority": "",
            "ticket_created": False
        }
        
        print("Running LangGraph workflow...")
        final_state = agent_workflow.invoke(initial_state)
        print(f"Workflow complete - Issue: {final_state['issue_type']}, Priority: {final_state['priority']}")
        
        print("Storing ticket in database...")
        with get_connection() as conn:
            cursor = conn.cursor()
            if IS_POSTGRES:
                cursor.execute(
                    """
                    INSERT INTO tickets (user_id, student_name, location, issue_type, description, image_path, priority)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        user_id,
                        student_name,
                        location,
                        final_state["issue_type"],
                        final_state["issue_detected"],
                        str(image_path),
                        final_state["priority"],
                    ),
                )
                ticket_id = cursor.fetchone()[0]
            else:
                cursor.execute(
                    """
                    INSERT INTO tickets (user_id, student_name, location, issue_type, description, image_path, priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        student_name,
                        location,
                        final_state["issue_type"],
                        final_state["issue_detected"],
                        str(image_path),
                        final_state["priority"],
                    ),
                )
                ticket_id = cursor.lastrowid
            conn.commit()

            cursor.execute(adapt_query("SELECT * FROM tickets WHERE id = ?"), (ticket_id,))
            ticket = cursor.fetchone()
        
        print(f"Ticket #{ticket_id} created successfully!")
        
        # Column order: id, user_id, student_name, location, issue_type, description, image_path, status, created_at, priority
        return TicketResponse(
            ticket_id=ticket[0],
            student_name=ticket[2],
            location=ticket[3],
            issue_type=ticket[4],
            description=ticket[5],
            ticket_status=ticket[7],
            priority=ticket[9],
            created_at=str(ticket[8])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/api/tickets", response_model=list[TicketResponse])
async def get_all_tickets(token_data: dict = Depends(verify_token)):
    """Get all maintenance tickets (protected route)"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(adapt_query("SELECT * FROM tickets ORDER BY created_at DESC"))
            tickets = cursor.fetchall()
        
        # Column order: id, user_id, student_name, location, issue_type, description, image_path, status, created_at, priority
        return [
            TicketResponse(
                ticket_id=ticket[0],
                student_name=ticket[2],
                location=ticket[3],
                issue_type=ticket[4],
                description=ticket[5],
                ticket_status=ticket[7],
                priority=ticket[9],
                created_at=str(ticket[8])
            )
            for ticket in tickets
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tickets: {str(e)}")


@app.get("/api/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: int, token_data: dict = Depends(verify_token)):
    """Get a specific ticket by ID (protected route)"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(adapt_query("SELECT * FROM tickets WHERE id = ?"), (ticket_id,))
            ticket = cursor.fetchone()
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Column order: id, user_id, student_name, location, issue_type, description, image_path, status, created_at, priority
        return TicketResponse(
            ticket_id=ticket[0],
            student_name=ticket[2],
            location=ticket[3],
            issue_type=ticket[4],
            description=ticket[5],
            ticket_status=ticket[7],
            priority=ticket[9],
            created_at=str(ticket[8])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching ticket: {str(e)}")


@app.put("/api/tickets/{ticket_id}/status")
async def update_ticket_status(ticket_id: int, ticket_status: str, token_data: dict = Depends(verify_token)):
    """Update ticket status (protected route)"""
    valid_statuses = ["pending", "in_progress", "resolved", "closed"]
    if ticket_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(adapt_query("UPDATE tickets SET status = ? WHERE id = ?"), (ticket_status, ticket_id))
            conn.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Ticket not found")

        return {"message": "Ticket status updated successfully", "ticket_id": ticket_id, "status": ticket_status}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating ticket: {str(e)}")


try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception:
    pass


if __name__ == "__main__":
    print("🚀 Starting AI Maintenance Reporter API...")
    print("📍 API Docs: http://localhost:8000/docs")
    print("🌐 Frontend: http://localhost:8000/static/index.html")
    uvicorn.run(app, host="0.0.0.0", port=8000)
