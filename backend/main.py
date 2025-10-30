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
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import google.generativeai as genai
from PIL import Image
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import uvicorn
import jwt
from passlib.context import CryptContext

load_dotenv(Path(__file__).parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
IS_POSTGRES = DATABASE_URL.startswith("postgres")

try:
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

BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

FRONTEND_DIST = BASE_DIR / "frontend" / "dist"


@contextmanager
def get_connection():
    """Provide a database connection for SQLite or Postgres (Neon)."""
    if IS_POSTGRES:
        if psycopg2 is None:
            raise RuntimeError("psycopg2 is required for PostgreSQL. Please add 'psycopg2-binary' to requirements and install it.")
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
    else:
        conn = sqlite3.connect(str(BASE_DIR / "maintenance_tickets.db"))
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
