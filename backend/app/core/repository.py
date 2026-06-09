"""
Base repository — barcha repositoriy lar uchun.
Generic CRUD operations.
"""
from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository — CRUD operations."""

    model: type[ModelType]

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, id: int) -> ModelType | None:
        """ID bo'yicha bitta record."""
        return await self.db.get(self.model, id)

    async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Hammasini olish."""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        """Jami son."""
        stmt = select(func.count()).select_from(self.model)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def create(self, **kwargs) -> ModelType:
        """Yangi record."""
        obj = self.model(**kwargs)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: ModelType, **kwargs) -> ModelType:
        """Yangilash."""
        for key, value in kwargs.items():
            setattr(obj, key, value)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        """O'chirish."""
        await self.db.delete(obj)
        await self.db.flush()
