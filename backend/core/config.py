import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
IS_POSTGRES = DATABASE_URL.startswith("postgres")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

UPLOAD_DIR = PROJECT_ROOT / "uploads"
STATIC_DIR = PROJECT_ROOT / "static"
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"


def ensure_directories() -> None:
    UPLOAD_DIR.mkdir(exist_ok=True)
    STATIC_DIR.mkdir(exist_ok=True)
