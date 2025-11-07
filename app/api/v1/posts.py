import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.post import PostCreate, PostOut, PostUpdate
from app.services import post as post_service

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostOut)
async def create_post(
    data: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = await post_service.create_post(db, current_user.id, data)
    return post


@router.get("/", response_model=list[PostOut])
async def list_posts(
    db: AsyncSession = Depends(get_db),
    q: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    posts = await post_service.list_posts(db, q, skip, limit)
    return posts


@router.get("/{post_id}", response_model=PostOut)
async def get_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    post = await post_service.get_post(db, post_id)
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    return post


@router.patch("/{post_id}", response_model=PostOut)
async def update_post(
    post_id: uuid.UUID,
    data: PostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        post = await post_service.update_post(db, post_id, current_user.id, data)
        if not post:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
        return post
    except PermissionError:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not the owner")


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        deleted = await post_service.delete_post(db, post_id, current_user.id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    except PermissionError:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not the owner")
    return None