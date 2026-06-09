"""Caching utilities"""
import functools
import hashlib
import json
import logging
from collections.abc import Callable

from app.core.redis_client import get_redis

logger = logging.getLogger(__name__)


def _make_hash(text: str) -> str:
    """Text dan deterministik hash."""
    return hashlib.sha256(text.encode()).hexdigest()


class EmbeddingCache:
    """Embedding lar uchun cache."""

    PREFIX = "emb:"
    TTL = 60 * 60 * 24 * 30  # 30 kun

    async def get(self, text: str) -> list[float] | None:
        """Cache dan embedding olish."""
        redis = get_redis()
        key = self.PREFIX + _make_hash(text)
        cached = await redis.get(key)
        if cached:
            logger.debug("Embedding cache HIT")
            return json.loads(cached)
        return None

    async def set(self, text: str, embedding: list[float]) -> None:
        """Embedding ni cache ga yozish."""
        redis = get_redis()
        key = self.PREFIX + _make_hash(text)
        await redis.set(key, json.dumps(embedding), ex=self.TTL)


class LLMResponseCache:
    """LLM javoblari uchun cache."""

    PREFIX = "llm:"
    TTL = 60 * 60 * 24  # 1 kun

    def _key(self, query: str, context: str) -> str:
        combined = f"{query}||{context}"
        return self.PREFIX + _make_hash(combined)

    async def get(self, query: str, context: str) -> str | None:
        redis = get_redis()
        cached = await redis.get(self._key(query, context))
        if cached:
            logger.debug("LLM cache HIT")
        return cached

    async def set(self, query: str, context: str, response: str) -> None:
        redis = get_redis()
        await redis.set(self._key(query, context), response, ex=self.TTL)


# Singletons
embedding_cache = EmbeddingCache()
llm_cache = LLMResponseCache()


def cached(prefix: str, ttl: int = 3600):
    """Funksiya natijasini cache qiluvchi decorator."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            redis = get_redis()
            key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
            key = prefix + ":" + _make_hash(key_data)

            cached_val = await redis.get(key)
            if cached_val:
                return json.loads(cached_val)

            result = await func(*args, **kwargs)
            await redis.set(key, json.dumps(result), ex=ttl)
            return result
        return wrapper
    return decorator
