from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_jwt,
    issue_refresh_token,
    pwd_context,
    revoke_refresh_token,
)
from app.errors.exceptions import Conflict, Unauthorized
from app.repositories.users import users_repo
from app.schemas.auth import SignUpIn, UserOut


class AuthService:
    async def signup(self, db: AsyncSession, payload: SignUpIn) -> UserOut:
        password_hash = pwd_context.hash(payload.password)
        user = await users_repo.create(
            db,
            fullname=payload.fullname,
            email=payload.email,
            password_hash=password_hash,
        )
        if not user:
            raise Conflict("Email already registered")
        return UserOut.from_orm(user)

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
