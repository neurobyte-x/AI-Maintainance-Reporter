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
from contextlib import contextmanager
from typing import TypedDict, Annotated, Sequence
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from PIL import Image
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from passlib.context import CryptContext
import jwt

# Load environment variables from parent directory
load_dotenv(Path(__file__).parent.parent / ".env")

# Database configuration (Neon Postgres)
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
IS_POSTGRES = DATABASE_URL.startswith("postgres")

# Import appropriate database driver
if IS_POSTGRES:
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        print("ERROR: psycopg2-binary not found. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        import psycopg2
        import psycopg2.extras

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

app = FastAPI(title="AI Maintenance Reporter", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory setup (relative to backend folder)
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
        conn = psycopg2.connect(DATABASE_URL)
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
        # Replace ? with %s for PostgreSQL
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
        
        # Users table
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
        
        # Tickets table
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


# Initialize database on startup
init_db()

# ...existing code...

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


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


# Models
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


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
    reasoning: str
    priority: str


def image_reasoning_tool(image_path: str) -> str:
    """Tool to analyze maintenance issue images using Gemini Vision"""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        image = Image.open(image_path)
        
        prompt = """Analyze this maintenance issue image and provide:
        1. Detailed description of the problem
        2. Severity assessment (low/medium/high/critical)
        3. Recommended action
        4. Estimated urgency
        
        Be specific and focus on maintenance aspects."""
        
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return f"Error analyzing image: {str(e)}"


def reasoning_agent(state: AgentState) -> AgentState:
    """Agent that reasons about the maintenance issue"""
    messages = state["messages"]
    image_path = state["image_path"]
    
    if image_path and Path(image_path).exists():
        analysis = image_reasoning_tool(image_path)
        
        # Determine priority based on keywords
        analysis_lower = analysis.lower()
        if any(word in analysis_lower for word in ['critical', 'urgent', 'dangerous', 'immediate']):
            priority = 'high'
        elif any(word in analysis_lower for word in ['moderate', 'medium', 'soon']):
            priority = 'medium'
        else:
            priority = 'low'
        
        state["reasoning"] = analysis
        state["priority"] = priority
        state["messages"].append(AIMessage(content=f"Analysis complete. Priority: {priority}"))
    else:
        state["reasoning"] = "No image available for analysis"
        state["priority"] = "medium"
    
    return state


# Build the agent graph
workflow = StateGraph(AgentState)
workflow.add_node("analyze", reasoning_agent)
workflow.set_entry_point("analyze")
workflow.add_edge("analyze", END)
agent = workflow.compile()


# API Routes
@app.post("/api/auth/signup", response_model=TokenResponse)
async def signup(request: SignupRequest):
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute(
            adapt_query("SELECT id FROM users WHERE email = ?"),
            (request.email,)
        )
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        hashed_password = get_password_hash(request.password)
        cursor.execute(
            adapt_query("INSERT INTO users (email, password_hash, full_name, role) VALUES (?, ?, ?, ?) RETURNING id"),
            (request.email, hashed_password, request.full_name, "student")
        )
        user_id = cursor.fetchone()[0]
        conn.commit()
        
        # Create token
        token = create_access_token({"sub": request.email, "user_id": user_id})
        
        return TokenResponse(
            access_token=token,
            user={
                "id": user_id,
                "email": request.email,
                "full_name": request.full_name,
                "role": "student"
            }
        )


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
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
    issue_type: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(None),
    user: dict = Depends(verify_token)
):
    image_path = None
    if image:
        image_path = str(UPLOAD_DIR / f"{datetime.now().timestamp()}_{image.filename}")
        with open(image_path, "wb") as buffer:
            buffer.write(await image.read())
    
    # Run AI analysis
    initial_state = AgentState(
        messages=[HumanMessage(content=f"Analyze maintenance issue: {description}")],
        image_path=image_path or "",
        reasoning="",
        priority="medium"
    )
    
    result = agent.invoke(initial_state)
    priority = result.get("priority", "medium")
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            adapt_query("""
                INSERT INTO tickets (user_id, student_name, location, issue_type, description, image_path, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                RETURNING id, user_id, student_name, location, issue_type, description, image_path, status, created_at, priority
            """),
            (user["user_id"], student_name, location, issue_type, description, image_path, priority)
        )
        ticket = cursor.fetchone()
        conn.commit()
        
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


@app.get("/api/tickets/", response_model=list[TicketResponse])
async def get_tickets(user: dict = Depends(verify_token)):
    with get_connection() as conn:
        cursor = conn.cursor()
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


# Serve static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Serve React frontend
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