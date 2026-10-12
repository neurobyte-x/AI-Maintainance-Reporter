"""
AI Maintenance Reporter - FastAPI Backend
This file stays as the entry point and wires the application components.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.core.config import DATABASE_URL, FRONTEND_DIST, IS_POSTGRES, STATIC_DIR, UPLOAD_DIR, ensure_directories
from backend.db.init_db import init_db
from backend.routers import auth, health, tickets

app = FastAPI(title="AI Maintenance Reporter", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(tickets.router, prefix="/api")


@app.on_event("startup")
def startup() -> None:
    ensure_directories()
    if not DATABASE_URL:
        print("WARNING: DATABASE_URL not set. Database operations will fail.")
    else:
        print(f"Database configured: {'PostgreSQL' if IS_POSTGRES else 'Unknown'}")
    init_db()


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
