from uuid import uuid4

from fastapi import (
    APIRouter,
    Body,
    Cookie,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_current_user, get_db, get_redis
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    enforce_password_length,
    pwd_context,
)
from app.models.user import User
from app.repositories.users import users_repo
from app.schemas.auth import UserOut
from app.services import refresh_store

router = APIRouter()


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    email: str = Body(...),
    password: str = Body(...),
    return_refresh_in_body: bool = Body(False),
):
    # Rate limit
    client_ip = request.client.host
    rl_key = f"rl:login:{email}:{client_ip}"
    async with redis.pipeline() as pipe:
        pipe.incr(rl_key)
        pipe.expire(rl_key, 300)
        req_count, _ = await pipe.execute()

    if req_count > 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts",
        )

    enforce_password_length(password)
    user = await users_repo.get_by_email(db, email=email)
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    jti = str(uuid4())
    access_token = create_access_token(sub=str(user.id), jti=jti)
    refresh_token = create_refresh_token(sub=str(user.id), jti=jti)

    ttl_sec = settings.REFRESH_TTL_DAYS * 86400
    await refresh_store.save_refresh(redis, jti, str(user.id), ttl_sec)

    resp_body = {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserOut.model_validate(user).model_dump(),
    }
    if settings.REFRESH_IN_COOKIE:
        response.set_cookie("rt", refresh_token, **settings.refresh_cookie_kwargs())
        if return_refresh_in_body:
            resp_body["refresh_token"] = refresh_token
    else:
        resp_body["refresh_token"] = refresh_token

    return resp_body


@router.post("/refresh")
async def refresh(
    response: Response,
    redis: Redis = Depends(get_redis),
    refresh_token: str | None = Cookie(None, alias="rt"),
    refresh_token_body: str | None = Body(None, embed=True, alias="refresh_token"),
    return_refresh_in_body: bool = Body(False),
):
    token_str = refresh_token or refresh_token_body
    if not token_str:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Refresh token required")

    payload = decode_token(token_str)
    if payload.get("type") != "refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")

    jti = payload["jti"]
    if not await refresh_store.exists_refresh(redis, jti):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token invalid")

    await refresh_store.delete_refresh(redis, jti)

    user_id = payload["sub"]
    new_jti = str(uuid4())
    new_access = create_access_token(sub=user_id, jti=new_jti)
    new_refresh = create_refresh_token(sub=user_id, jti=new_jti)

    ttl_sec = settings.REFRESH_TTL_DAYS * 86400
    await refresh_store.save_refresh(redis, new_jti, user_id, ttl_sec)

    resp_body = {"access_token": new_access, "token_type": "bearer"}
    if settings.REFRESH_IN_COOKIE:
        response.set_cookie("rt", new_refresh, **settings.refresh_cookie_kwargs())
        if return_refresh_in_body:
            resp_body["refresh_token"] = new_refresh
    else:
        resp_body["refresh_token"] = new_refresh

    return resp_body


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    redis: Redis = Depends(get_redis),
    refresh_token: str | None = Cookie(None, alias="rt"),
    refresh_token_body: str | None = Body(None, embed=True, alias="refresh_token"),
):
    token_str = refresh_token or refresh_token_body
    if token_str:
        payload = decode_token(token_str, verify_exp=False)
        if payload.get("type") == "refresh":
            jti = payload.get("jti")
            if jti:
                await refresh_store.delete_refresh(redis, jti)

    if settings.REFRESH_IN_COOKIE:
        kwargs = settings.refresh_cookie_kwargs()
        kwargs.pop("samesite", None) # samesite=none requires secure=True
        response.delete_cookie("rt", **kwargs)

    return response


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user