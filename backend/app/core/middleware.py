"""
Custom middleware.

Middleware — har bir request ga "qo'shimcha" qatlam:
- Logging
- Request ID generation
- Timing
- Error handling
"""
import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import request_id_var

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Har bir request uchun unique ID generate qiladi.

    Header X-Request-ID bo'lsa o'sha ishlatiladi (tracing uchun),
    bo'lmasa yangi UUID yaratiladi.

    Bu ID log lar va response header da bo'ladi —
    foydalanuvchi xato yuborganda biz aniq ko'ramiz qaysi request edi.
    """

    async def dispatch(self, request: Request, call_next):
        # Header dan olamiz yoki yangi yaratamiz
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]
        request_id_var.set(request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class TimingMiddleware(BaseHTTPMiddleware):
    """Har bir request uchun bajarilish vaqtini o'lchaydi.

    Sekin endpoint larni topish uchun foydali.
    """

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.2f}"

        # Log: faqat sekin so'rovlarni
        if elapsed_ms > 1000:  # 1 sekund dan ko'p
            logger.warning(
                f"Sekin so'rov: {request.method} {request.url.path} — {elapsed_ms:.0f}ms"
            )

        return response
