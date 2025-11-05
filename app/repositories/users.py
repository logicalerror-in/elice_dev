from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self, db: AsyncSession, fullname: str, email: str, password_hash: str
    ) -> User | None:
        try:
            user = User(
                fullname=fullname,
                email=email,
                password_hash=password_hash,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user
        except IntegrityError:
            await db.rollback()
            return None

users_repo = UserRepository()
