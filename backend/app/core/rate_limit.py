"""Rate limiting — sliding window (Redis)"""
import logging
import time

from app.core.exceptions import RateLimitExceededError
from app.core.redis_client import get_redis

logger = logging.getLogger(__name__)


async def check_rate_limit(
    identifier: str,
    max_requests: int,
    window_seconds: int,
) -> None:
    """
    Sliding window rate limit.

    Args:
        identifier: kim (user_id, ip)
        max_requests: ruxsat etilgan so'rovlar
        window_seconds: vaqt oynasi

    Raises:
        RateLimitExceededError: limit oshib ketsa
    """
    redis = get_redis()
    key = f"ratelimit:{identifier}"
    now = time.time()
    window_start = now - window_seconds

    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, window_seconds)
    results = await pipe.execute()

    request_count = results[2]
    if request_count > max_requests:
        logger.warning(f"Rate limit: {identifier} ({request_count}/{max_requests})")
        raise RateLimitExceededError(
            f"So'rovlar chegarasi: {max_requests}/{window_seconds}s"
        )
