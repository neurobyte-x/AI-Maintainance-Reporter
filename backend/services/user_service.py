from backend.custom_errors import AuthError, ConflictError, NotFoundError
from backend.repositories.interfaces import UserRepository
from backend.services.auth_service import create_access_token, get_password_hash, verify_password


def signup_user(request, repo: UserRepository) -> dict:
    if repo.get_by_email(request.email):
        raise ConflictError("Email already registered")

    hashed_password = get_password_hash(request.password)
    user = repo.create(request.email, hashed_password, request.full_name, request.role)
    token = create_access_token({"sub": user.email, "user_id": user.id})

    return {
        "access_token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        },
    }


def login_user(request, repo: UserRepository) -> dict:
    user = repo.get_by_email(request.email)
    if not user or not verify_password(request.password, user.password_hash):
        raise AuthError("Invalid credentials")

    token = create_access_token({"sub": user.email, "user_id": user.id})
    return {
        "access_token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        },
    }


def get_user_or_404(user_id: int, repo: UserRepository):
    user = repo.get_by_id(user_id)
    if not user:
        raise NotFoundError("User not found")
    return user
