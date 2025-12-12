"""
AI Maintenance Reporter - FastAPI Backend
This file is now in backend/ folder for deployment on Render.

Path adjustments:
- React build folder: ../frontend/dist (Vite builds to 'dist' by default)
- Static files: ../static
- Uploads: ../uploads
- .env file: ../.env (one level up)
"""
import os
import sys
import shutil
from contextlib import contextmanager
from typing import TypedDict, Annotated, Sequence
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, field_validator
from PIL import Image
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import jwt
import hashlib

load_dotenv(Path(__file__).parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
IS_POSTGRES = DATABASE_URL.startswith("postgres")

if not DATABASE_URL:
    print("WARNING: DATABASE_URL not set. Database operations will fail.")
else:
    print(f"Database configured: {'PostgreSQL' if IS_POSTGRES else 'Unknown'}")

if IS_POSTGRES:
    try:
        import psycopg2
        import psycopg2.extras
        print("PostgreSQL driver loaded successfully")
    except ImportError:
        print("ERROR: psycopg2-binary not found. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        import psycopg2
        import psycopg2.extras

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

security = HTTPBearer()

app = FastAPI(title="AI Maintenance Reporter", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

FRONTEND_DIST = BASE_DIR / "frontend" / "dist"


@contextmanager
def get_connection():
    """Get database connection (PostgreSQL for Neon)"""
    if IS_POSTGRES:
        connection_string = DATABASE_URL.replace('&channel_binding=require', '').replace('?channel_binding=require', '')
        
        try:
            conn = psycopg2.connect(connection_string)
        except Exception as e:
            print(f"Database connection failed: {str(e)}")
            print(f"Connection string (password hidden): {connection_string.split('@')[1] if '@' in connection_string else 'invalid'}")
            raise
            
        conn.autocommit = False
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


def adapt_query(query: str) -> str:
    """Adapt SQL query for PostgreSQL"""
    if IS_POSTGRES:
        counter = 0
        result = []
        for char in query:
            if char == '?':
                counter += 1
                result.append('%s')
            else:
                result.append(char)
        return ''.join(result)
    return query


def init_db():
    """Initialize database tables for PostgreSQL"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute(adapt_query("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                role VARCHAR(50) DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        cursor.execute(adapt_query("""
            CREATE TABLE IF NOT EXISTS tickets (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                student_name VARCHAR(255) NOT NULL,
                location VARCHAR(255) NOT NULL,
                issue_type VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                image_path VARCHAR(500),
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                priority VARCHAR(50) DEFAULT 'medium'
            )
        """))
        
        conn.commit()


try:
    print("Initializing database...")
    init_db()
    print("Database initialized successfully")
except Exception as e:
    print(f"CRITICAL: Database initialization failed: {str(e)}")
    import traceback
    traceback.print_exc()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using SHA-256 hash"""
    password_hash = hashlib.sha256((plain_password + SECRET_KEY).encode()).hexdigest()
    return password_hash == hashed_password


def get_password_hash(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256((password + SECRET_KEY).encode()).hexdigest()


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "student"
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        allowed_roles = ['student', 'admin']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str


class TicketRequest(BaseModel):
    student_name: str
    location: str
    issue_type: str
    description: str


class TicketResponse(BaseModel):
    id: int
    student_name: str
    location: str
    issue_type: str
    description: str
    status: str
    created_at: datetime
    priority: str


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    image_path: str
    issue_detected: str
    issue_type: str
    priority: str
    ticket_created: bool


def image_reasoning_tool(image_path: str) -> str:
    """
    Uses Gemini to analyze an image and detect broken or damaged objects.
    Especially checks for issues in fans, lights, furniture, or electronics.
    """
    try:
        if not os.path.exists(image_path):
            return f"Error: Image not found at {image_path}"

        import google.generativeai as genai
        
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        model = genai.GenerativeModel("gemini-2.5-flash")

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
    state["messages"] = list(state.get("messages", [])) + [
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
    state["messages"] = list(state.get("messages", [])) + [
        AIMessage(content=f"Issue classified as: {issue_type} (Priority: {priority})")
    ]
    
    return state


def create_ticket_node(state: AgentState) -> AgentState:
    """Node to mark ticket as ready for creation"""
    state["ticket_created"] = True
    state["messages"] = list(state.get("messages", [])) + [
        AIMessage(content="Maintenance ticket ready to be created")
    ]
    
    return state


def build_workflow():
    """Build the LangGraph workflow"""
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


@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify database and configuration"""
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "environment": "production" if DATABASE_URL else "development"
    }
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = f"error: {str(e)}"
    
    return health_status


@app.post("/api/auth/signup", response_model=TokenResponse)
async def signup(request: SignupRequest):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                adapt_query("SELECT id FROM users WHERE email = ?"),
                (request.email,)
            )
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Email already registered")
            
            hashed_password = get_password_hash(request.password)
            cursor.execute(
                adapt_query("INSERT INTO users (email, password_hash, full_name, role) VALUES (?, ?, ?, ?) RETURNING id"),
                (request.email, hashed_password, request.full_name, request.role)
            )
            user_id = cursor.fetchone()[0]
            conn.commit()
            
            token = create_access_token({"sub": request.email, "user_id": user_id})
            
            return TokenResponse(
                access_token=token,
                user={
                    "id": user_id,
                    "email": request.email,
                    "full_name": request.full_name,
                    "role": request.role
                }
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Signup error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                adapt_query("SELECT id, email, password_hash, full_name, role FROM users WHERE email = ?"),
                (request.email,)
            )
            user = cursor.fetchone()
            
            if not user or not verify_password(request.password, user[2]):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            token = create_access_token({"sub": user[1], "user_id": user[0]})
            
            return TokenResponse(
                access_token=token,
                user={
                    "id": user[0],
                    "email": user[1],
                    "full_name": user[3],
                    "role": user[4]
                }
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user(user: dict = Depends(verify_token)):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            adapt_query("SELECT id, email, full_name, role FROM users WHERE id = ?"),
            (user["user_id"],)
        )
        user_data = cursor.fetchone()
        
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            id=user_data[0],
            email=user_data[1],
            full_name=user_data[2],
            role=user_data[3]
        )


@app.post("/api/tickets/", response_model=TicketResponse)
async def create_ticket(
    student_name: str = Form(...),
    location: str = Form(...),
    image: UploadFile = File(...),
    user: dict = Depends(verify_token)
):
    """Upload an image and create a maintenance ticket using AI analysis"""
    try:
        user_id = user["user_id"]
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
            cursor.execute(
                adapt_query("""
                    INSERT INTO tickets (user_id, student_name, location, issue_type, description, image_path, priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    RETURNING id, user_id, student_name, location, issue_type, description, image_path, status, created_at, priority
                """),
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
            ticket = cursor.fetchone()
            conn.commit()
        
        print(f"Ticket #{ticket[0]} created successfully!")
        
        return TicketResponse(
            id=ticket[0],
            student_name=ticket[2],
            location=ticket[3],
            issue_type=ticket[4],
            description=ticket[5],
            status=ticket[7],
            created_at=ticket[8],
            priority=ticket[9]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/api/tickets/", response_model=list[TicketResponse])
async def get_tickets(user: dict = Depends(verify_token)):
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute(
            adapt_query("SELECT role FROM users WHERE id = ?"),
            (user["user_id"],)
        )
        user_data = cursor.fetchone()
        user_role = user_data[0] if user_data else "student"
        
        if user_role == "admin":
            cursor.execute(
                adapt_query("SELECT id, user_id, student_name, location, issue_type, description, image_path, status, created_at, priority FROM tickets ORDER BY created_at DESC")
            )
        else:
            cursor.execute(
                adapt_query("SELECT id, user_id, student_name, location, issue_type, description, image_path, status, created_at, priority FROM tickets WHERE user_id = ? ORDER BY created_at DESC"),
                (user["user_id"],)
            )
        
        tickets = cursor.fetchall()
        
        return [
            TicketResponse(
                id=ticket[0],
                student_name=ticket[2],
                location=ticket[3],
                issue_type=ticket[4],
                description=ticket[5],
                status=ticket[7],
                created_at=ticket[8],
                priority=ticket[9]
            )
            for ticket in tickets
        ]


@app.get("/api/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: int, user: dict = Depends(verify_token)):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            adapt_query("SELECT id, user_id, student_name, location, issue_type, description, image_path, status, created_at, priority FROM tickets WHERE id = ? AND user_id = ?"),
            (ticket_id, user["user_id"])
        )
        ticket = cursor.fetchone()
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return TicketResponse(
            id=ticket[0],
            student_name=ticket[2],
            location=ticket[3],
            issue_type=ticket[4],
            description=ticket[5],
            status=ticket[7],
            created_at=ticket[8],
            priority=ticket[9]
        )


@app.put("/api/tickets/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: int,
    ticket_status: str = Query(...),
    user: dict = Depends(verify_token)
):
    """Update ticket status (admin only)"""
    valid_statuses = ["pending", "in_progress", "resolved", "closed"]
    if ticket_status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                adapt_query("SELECT role FROM users WHERE id = ?"),
                (user["user_id"],)
            )
            user_data = cursor.fetchone()
            
            if not user_data or user_data[0] != "admin":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            print(f"Updating ticket {ticket_id} to status: {ticket_status}")
            cursor.execute(
                adapt_query("UPDATE tickets SET status = ? WHERE id = ?"),
                (ticket_status, ticket_id)
            )
            
            rows_affected = cursor.rowcount
            print(f"Rows affected: {rows_affected}")
            
            conn.commit()
            
            if rows_affected == 0:
                raise HTTPException(status_code=404, detail="Ticket not found")
            
            print(f"Ticket {ticket_id} successfully updated to {ticket_status}")
            
            return {
                "message": "Ticket status updated successfully",
                "ticket_id": ticket_id,
                "status": ticket_status
            }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating ticket status: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating ticket: {str(e)}")


class TicketUpdateRequest(BaseModel):
    student_name: str | None = None
    location: str | None = None
    issue_type: str | None = None
    description: str | None = None
    priority: str | None = None
    status: str | None = None
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        if v is not None:
            allowed_priorities = ['low', 'medium', 'high']
            if v not in allowed_priorities:
                raise ValueError(f'Priority must be one of: {", ".join(allowed_priorities)}')
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['pending', 'in_progress', 'resolved', 'closed']
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v


@app.patch("/api/tickets/{ticket_id}")
async def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdateRequest,
    user: dict = Depends(verify_token)
):
    """Update ticket fields (owner or admin only)"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                adapt_query("SELECT role FROM users WHERE id = ?"),
                (user["user_id"],)
            )
            user_data = cursor.fetchone()
            user_role = user_data[0] if user_data else "student"
            
            cursor.execute(
                adapt_query("SELECT user_id FROM tickets WHERE id = ?"),
                (ticket_id,)
            )
            ticket_data = cursor.fetchone()
            
            if not ticket_data:
                raise HTTPException(status_code=404, detail="Ticket not found")
            
            ticket_owner_id = ticket_data[0]
            
            if user_role != "admin" and ticket_owner_id != user["user_id"]:
                raise HTTPException(status_code=403, detail="Not authorized to update this ticket")
            
            update_fields = []
            update_values = []
            
            if ticket_update.student_name is not None:
                update_fields.append("student_name = ?")
                update_values.append(ticket_update.student_name)
            
            if ticket_update.location is not None:
                update_fields.append("location = ?")
                update_values.append(ticket_update.location)
            
            if ticket_update.issue_type is not None:
                update_fields.append("issue_type = ?")
                update_values.append(ticket_update.issue_type)
            
            if ticket_update.description is not None:
                update_fields.append("description = ?")
                update_values.append(ticket_update.description)
            
            if ticket_update.priority is not None:
                update_fields.append("priority = ?")
                update_values.append(ticket_update.priority)
            
            if ticket_update.status is not None:
                if user_role != "admin":
                    raise HTTPException(status_code=403, detail="Only admins can update ticket status")
                update_fields.append("status = ?")
                update_values.append(ticket_update.status)
            
            if not update_fields:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            update_query = f"UPDATE tickets SET {', '.join(update_fields)} WHERE id = ?"
            update_values.append(ticket_id)
            
            print(f"Updating ticket {ticket_id}: {update_fields}")
            cursor.execute(adapt_query(update_query), tuple(update_values))
            conn.commit()
            
            cursor.execute(
                adapt_query("SELECT id, user_id, student_name, location, issue_type, description, image_path, status, created_at, priority FROM tickets WHERE id = ?"),
                (ticket_id,)
            )
            ticket = cursor.fetchone()
            
            return TicketResponse(
                id=ticket[0],
                student_name=ticket[2],
                location=ticket[3],
                issue_type=ticket[4],
                description=ticket[5],
                status=ticket[7],
                created_at=ticket[8],
                priority=ticket[9]
            )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating ticket: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating ticket: {str(e)}")


@app.delete("/api/tickets/{ticket_id}")
async def delete_ticket(
    ticket_id: int,
    user: dict = Depends(verify_token)
):
    """Delete ticket (admin only)"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                adapt_query("SELECT role FROM users WHERE id = ?"),
                (user["user_id"],)
            )
            user_data = cursor.fetchone()
            
            if not user_data or user_data[0] != "admin":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            cursor.execute(
                adapt_query("SELECT image_path FROM tickets WHERE id = ?"),
                (ticket_id,)
            )
            ticket_data = cursor.fetchone()
            
            if not ticket_data:
                raise HTTPException(status_code=404, detail="Ticket not found")
            
            image_path = ticket_data[0]
            
            print(f"Deleting ticket {ticket_id}")
            cursor.execute(
                adapt_query("DELETE FROM tickets WHERE id = ?"),
                (ticket_id,)
            )
            conn.commit()
            
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    print(f"Deleted image file: {image_path}")
                except Exception as img_error:
                    print(f"Warning: Could not delete image file {image_path}: {str(img_error)}")
            
            print(f"Ticket {ticket_id} successfully deleted")
            
            return {
                "message": "Ticket deleted successfully",
                "ticket_id": ticket_id
            }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting ticket: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error deleting ticket: {str(e)}")


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")