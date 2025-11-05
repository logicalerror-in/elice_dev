from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_redis
from app.schemas.auth import SignUpIn, UserOut
from app.services.auth import auth_service

router = APIRouter()


class LoginPayload(BaseModel):
    email: str
    password: str


class RefreshPayload(BaseModel):
    refresh_token: str


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    payload: SignUpIn, db: AsyncSession = Depends(get_db)
) -> UserOut:
    return await auth_service.signup(db, payload)


@router.post("/login")
async def login(
    payload: LoginPayload,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    return await auth_service.login(db, redis, payload.email, payload.password)


@router.post("/refresh")
async def refresh(
    payload: RefreshPayload, redis: Redis = Depends(get_redis)
) -> dict:
    return await auth_service.refresh(redis, payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: RefreshPayload, redis: Redis = Depends(get_redis)
) -> Response:
    await auth_service.logout(redis, payload.refresh_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
