from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def enforce_password_length(password: str):
    if len(password.encode()) > 72:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be 72 bytes or less",
        )


def create_access_token(sub: str, jti: str | None = None) -> str:
    if jti is None:
        jti = str(uuid4())
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.ACCESS_TTL_MIN)
    claims = {
        "sub": sub,
        "type": "access",
        "jti": jti,
        "exp": exp,
        "iat": now,
    }
    return jwt.encode(
        claims, settings.JWT_SECRET, algorithm=settings.JWT_ALG
    )


def create_refresh_token(sub: str, jti: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(days=settings.REFRESH_TTL_DAYS)
    claims = {
        "sub": sub,
        "type": "refresh",
        "jti": jti,
        "exp": exp,
        "iat": now,
    }
    return jwt.encode(
        claims, settings.JWT_SECRET, algorithm=settings.JWT_ALG
    )


def decode_token(token: str, verify_exp: bool = True) -> dict:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
            options={"verify_exp": verify_exp},
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from e