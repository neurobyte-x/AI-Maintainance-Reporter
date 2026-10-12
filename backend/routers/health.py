from fastapi import APIRouter
from sqlalchemy import text

from backend.core.config import DATABASE_URL
from backend.db.session import get_engine

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "environment": "production" if DATABASE_URL else "development",
    }

    try:
        engine = get_engine()
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            health_status["database"] = "connected"
    except Exception as exc:
        health_status["status"] = "unhealthy"
        health_status["database"] = f"error: {str(exc)}"

    return health_status
