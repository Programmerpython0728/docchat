"""Redis client — connection pool bilan"""
import logging

import redis.asyncio as redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_redis: redis.Redis | None = None


def init_redis() -> redis.Redis:
    """Redis client (pool bilan) — lifespan startup da."""
    global _redis
    if _redis is not None:
        return _redis

    settings = get_settings()
    _redis = redis.from_url(
        str(settings.redis_url),
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
        health_check_interval=30,
    )
    logger.info("Redis client yaratildi")
    return _redis


async def close_redis():
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None
        logger.info("Redis client yopildi")


def get_redis() -> redis.Redis:
    if _redis is None:
        raise RuntimeError("Redis ishga tushmagan")
    return _redis
