import json

from redis.asyncio import Redis


async def save_refresh(r: Redis, jti: str, user_id: str, ttl_sec: int) -> None:
    key = f"rt:{jti}"
    value = json.dumps({"uid": user_id})
    await r.setex(key, ttl_sec, value)


async def exists_refresh(r: Redis, jti: str) -> bool:
    key = f"rt:{jti}"
    return await r.exists(key) > 0


async def delete_refresh(r: Redis, jti: str) -> None:
    key = f"rt:{jti}"
    await r.delete(key)