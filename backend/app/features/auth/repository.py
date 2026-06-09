"""User repository"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.features.auth.models import User


class UserRepository(BaseRepository[User]):
    model = User

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_by_email(self, email: str) -> User | None:
        """Email bo'yicha foydalanuvchi."""
        stmt = select(User).where(User.email == email.lower())
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """Email mavjudligi."""
        user = await self.get_by_email(email)
        return user is not None
