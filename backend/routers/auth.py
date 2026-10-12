from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.custom_errors import AuthError, ConflictError, NotFoundError
from backend.dependencies.auth import verify_token
from backend.dependencies.db import get_db
from backend.repositories.sqlalchemy_repos import SqlAlchemyUserRepository
from backend.schemas.auth import LoginRequest, SignupRequest, TokenResponse, UserResponse
from backend.services.user_service import get_user_or_404, login_user, signup_user

router = APIRouter(tags=["auth"])


def _handle_auth_error(exc: Exception) -> None:
    if isinstance(exc, ConflictError):
        raise HTTPException(status_code=400, detail=str(exc))
    if isinstance(exc, AuthError):
        raise HTTPException(status_code=401, detail=str(exc))
    if isinstance(exc, NotFoundError):
        raise HTTPException(status_code=404, detail=str(exc))
    raise exc


@router.post("/auth/signup", response_model=TokenResponse)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    repo = SqlAlchemyUserRepository(db)
    try:
        return signup_user(request, repo)
    except Exception as exc:
        _handle_auth_error(exc)


@router.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    repo = SqlAlchemyUserRepository(db)
    try:
        return login_user(request, repo)
    except Exception as exc:
        _handle_auth_error(exc)


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user(user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    repo = SqlAlchemyUserRepository(db)
    try:
        user_record = get_user_or_404(user["user_id"], repo)
        return UserResponse(
            id=user_record.id,
            email=user_record.email,
            full_name=user_record.full_name,
            role=user_record.role,
        )
    except Exception as exc:
        _handle_auth_error(exc)
