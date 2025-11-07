from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from redis.asyncio import Redis

from app.core.config import settings
from app.core.security import (
    create_access_jwt,
    issue_refresh_token,
    revoke_refresh_token,
)
from app.errors.exceptions import Unauthorized
from app.models.user import User
from app.repositories.users import users_repo
from app.schemas.auth import SignUpPayload, SignUpResponse

try:
    from app.errors.http import http_conflict
except ImportError:
    from fastapi import HTTPException

    def http_conflict(detail: str):
        raise HTTPException(status_code=409, detail=detail)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    async def signup(self, db: AsyncSession, payload: SignUpPayload) -> SignUpResponse:
        existing = await db.execute(select(User).where(User.email == payload.email))
        if existing.scalar_one_or_none():
            raise http_conflict("Email already registered")

        password_hash = pwd_context.hash(payload.password[:72])

        user = User(
            fullname=payload.fullname,
            email=payload.email,
            password_hash=password_hash,
        )
        db.add(user)
        await db.flush()
        await db.commit()
        await db.refresh(user)

        return SignUpResponse(
            id=user.id,
            fullname=user.fullname,
            email=user.email,
            created_at=user.created_at,
        )

    async def login(
        self, db: AsyncSession, redis: Redis, email: str, password: str
    ) -> dict:
        user = await users_repo.get_by_email(db, email)
        if not user or not pwd_context.verify(password, user.password_hash):
            raise Unauthorized("Invalid email or password")

        access_token = create_access_jwt(
            user.id,
            settings.JWT_SECRET,
            settings.JWT_ALG,
            settings.ACCESS_MIN,
        )
        refresh_token = await issue_refresh_token(
            redis, user.id, settings.REFRESH_DAYS
        )

        return {
            "access_token": access_token,
            "expires_in": settings.ACCESS_MIN * 60,
            "refresh_token": refresh_token,
        }

    async def refresh(self, redis: Redis, refresh_token: str) -> dict:
        key = f"refresh:{refresh_token}"
        user_id = await redis.get(key)
        if not user_id:
            raise Unauthorized("Invalid or expired refresh token")

        access_token = create_access_jwt(
            int(user_id),
            settings.JWT_SECRET,
            settings.JWT_ALG,
            settings.ACCESS_MIN,
        )
        return {
            "access_token": access_token,
            "expires_in": settings.ACCESS_MIN * 60,
        }

    async def logout(self, redis: Redis, refresh_token: str) -> None:
        await revoke_refresh_token(redis, refresh_token)


auth_service = AuthService()