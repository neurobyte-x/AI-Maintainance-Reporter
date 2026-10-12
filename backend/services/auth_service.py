import hashlib
from datetime import datetime, timedelta

import jwt

from backend.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_hash = hashlib.sha256((plain_password + SECRET_KEY).encode()).hexdigest()
    return password_hash == hashed_password


def get_password_hash(password: str) -> str:
    return hashlib.sha256((password + SECRET_KEY).encode()).hexdigest()


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
