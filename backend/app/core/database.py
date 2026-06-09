"""
Database connection management.
SQLAlchemy 2.0 async engine va session lifecycle.
"""
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Hamma model lar uchun bosh klass."""
    pass


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_engine() -> AsyncEngine:
    """Engine yaratish — lifespan startup da chaqiriladi."""
    global _engine, _session_factory

    if _engine is not None:
        return _engine

    settings = get_settings()

    _engine = create_async_engine(
        str(settings.database_url),
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=settings.db_echo,
    )

    _session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    logger.info(f"DB engine yaratildi (pool_size={settings.db_pool_size})")
    return _engine


async def close_engine() -> None:
    """Engine yopish — lifespan shutdown da."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        logger.info("DB engine yopildi")


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency — har request uchun yangi session."""
    if _session_factory is None:
        raise RuntimeError("DB engine ishga tushmagan")

    async with _session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def get_db_context() -> AsyncIterator[AsyncSession]:
    """Context manager versiyasi — script va background tasks uchun."""
    if _session_factory is None:
        raise RuntimeError("DB engine ishga tushmagan")

    async with _session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def import_all_models() -> None:
    """
    Hamma model lar import — Alembic autogenerate ko'rishi uchun.
    """
    from app.features.auth import models as _auth  # noqa: F401
    from app.features.chat import models as _chat  # noqa: F401
    from app.features.documents import models as _doc  # noqa: F401