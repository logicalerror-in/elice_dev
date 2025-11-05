import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, Header
from passlib.context import CryptContext
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_db
from app.errors.exceptions import Unauthorized
from app.models.user import User
from app.repositories.users import users_repo

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_jwt(
    user_id: int, secret: str, alg: str, minutes: int
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, secret, algorithm=alg)


def verify_access_jwt(token: str, secret: str, alg: str) -> dict:
    try:
        return jwt.decode(token, secret, algorithms=[alg])
    except jwt.PyJWTError as e:
        raise Unauthorized("Invalid or expired token") from e


async def issue_refresh_token(
    redis: Redis, user_id: int, days: int
) -> str:
    token = uuid.uuid4().hex
    key = f"refresh:{token}"
    await redis.setex(key, timedelta(days=days), user_id)
    return token


async def revoke_refresh_token(redis: Redis, refresh_token: str) -> None:
    key = f"refresh:{refresh_token}"
    await redis.delete(key)


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization:
        raise Unauthorized("Authorization header is missing")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise Unauthorized("Invalid authentication scheme")
    except ValueError as e:
        raise Unauthorized("Invalid authorization header format") from e

    payload = verify_access_jwt(
        token, settings.JWT_SECRET, settings.JWT_ALG
    )
    user_id = payload.get("sub")
    if not user_id:
        raise Unauthorized("Invalid token payload")

    user = await db.get(User, int(user_id))
    if not user:
        raise Unauthorized("User not found")
    return user
