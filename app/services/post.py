from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate


async def create_post(
    db: AsyncSession, author_id: int, data: PostCreate
) -> Post:
    post = Post(author_id=author_id, **data.model_dump())
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def get_post(
    db: AsyncSession, post_id: str, include_deleted: bool = False
) -> Post | None:
    stmt = select(Post).where(Post.id == post_id)
    if not include_deleted:
        stmt = stmt.where(Post.is_deleted == False)
    return await db.scalar(stmt)


async def list_posts(
    db: AsyncSession, q: str | None, skip: int = 0, limit: int = 20
) -> list[Post]:
    stmt = select(Post).where(Post.is_deleted == False)
    if q:
        stmt = stmt.where(Post.title.ilike(f"%{q}%"))
    stmt = stmt.offset(skip).limit(limit).order_by(Post.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_post(
    db: AsyncSession, post_id: str, author_id: int, data: PostUpdate
) -> Post:
    stmt = (
        select(Post)
        .where(Post.id == post_id, Post.is_deleted == False)
        .with_for_update()
    )
    post = await db.scalar(stmt)
    if not post:
        return None
    if post.author_id != author_id:
        raise PermissionError("Not the owner")

    update_data = data.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(post, k, v)

    await db.commit()
    await db.refresh(post)
    return post


async def delete_post(db: AsyncSession, post_id: str, author_id: int) -> bool:
    stmt = (
        select(Post)
        .where(Post.id == post_id, Post.is_deleted == False)
        .with_for_update()
    )
    post = await db.scalar(stmt)
    if not post:
        return False
    if post.author_id != author_id:
        raise PermissionError("Not the owner")

    post.is_deleted = True
    await db.commit()
    return True