from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from backend.core.config import DATABASE_URL

engine: Optional[Engine] = None
SessionLocal = None


def get_engine() -> Engine:
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not set")

    global engine
    if engine is None:
        try:
            engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        except ModuleNotFoundError as exc:
            if exc.name == "psycopg2":
                raise RuntimeError("psycopg2 is required for PostgreSQL. Run: uv sync") from exc
            raise
    return engine


def get_session_local():
    global SessionLocal
    if SessionLocal is None:
        engine_instance = get_engine()
        SessionLocal = sessionmaker(bind=engine_instance, autoflush=False, autocommit=False)
    return SessionLocal
