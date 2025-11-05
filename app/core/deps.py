from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app.db.session import async_session
from app.core.config import settings

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def get_redis():
    return redis.from_url(settings.REDIS_URL, decode_responses=True)
