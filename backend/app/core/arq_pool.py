"""arq Redis pool — job enqueue uchun"""
from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from app.core.config import get_settings

_arq_pool: ArqRedis | None = None


async def init_arq_pool() -> ArqRedis:
    global _arq_pool
    if _arq_pool is None:
        settings = get_settings()
        _arq_pool = await create_pool(
            RedisSettings.from_dsn(str(settings.redis_url))
        )
    return _arq_pool


async def get_arq_pool() -> ArqRedis:
    if _arq_pool is None:
        return await init_arq_pool()
    return _arq_pool


async def close_arq_pool():
    global _arq_pool
    if _arq_pool is not None:
        await _arq_pool.close()
        _arq_pool = None
