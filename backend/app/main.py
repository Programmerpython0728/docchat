"""
DocChat FastAPI ilovasi.

Bu fayl — ilovaning entry point. Bu yerda:
- FastAPI app yaratiladi
- Lifespan events (startup/shutdown)
- Middleware lar qo'shiladi
- Exception handlers ro'yxatga olinadi
- Routerlar ulanadi
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.exceptions import DocChatException
from app.core.logging import setup_logging
from app.core.middleware import RequestIDMiddleware, TimingMiddleware

# Routerlarni import qilamiz
from app.features.auth.router import router as auth_router
from app.features.chat.router import router as chat_router
from app.features.documents.router import router as documents_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Lifespan event manager.

    `yield` dan oldin — startup
    `yield` dan keyin — shutdown

    Bu yerda DB connection pool, Redis client, ML model load
    kabi resurslarni ishga tushiramiz va to'g'ri yopamiz.
    """
    settings = get_settings()
    setup_logging(settings.log_level)

    # === Startup ===
    logger.info(f">>> {settings.app_name} v{settings.app_version} boshlanmoqda")
    logger.info(f"   Environment: {settings.app_env}")
    logger.info(f"   Debug: {settings.debug}")

    # TODO 4-kun: DB engine init
    # TODO 7-kun: Redis client init
    # TODO 8-kun: LLM client init

    yield  # <-- bu yerda app ishlaydi

    # === Shutdown ===
    logger.info(f"<<< {settings.app_name} to'xtatilmoqda")
    # TODO: resurslarni yopish


def create_app() -> FastAPI:
    """FastAPI ilovasini yaratuvchi factory."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-powered document Q&A platform with RAG",
        docs_url="/docs" if settings.is_development else None,    # prod da yashirib qo'yamiz
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    # === Middleware ===
    # Tartib MUHIM: birinchi qo'shilgan — birinchi ishlaydi
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # === Exception handlers ===
    @app.exception_handler(DocChatException)
    async def docchat_exception_handler(request: Request, exc: DocChatException):
        """Custom exception lar uchun handler."""
        logger.warning(f"DocChatException: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Hamma kutilmagan xatolar uchun handler."""
        logger.exception(f"Kutilmagan xato: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Server ichki xatosi"},
        )

    # === Health check ===
    @app.get("/health", tags=["health"])
    async def health_check():
        """Loyiha tirik ekanligini tekshirish.

        Production'da load balancer shu endpoint ga ping yuboradi.
        """
        return {
            "status": "ok",
            "app": settings.app_name,
            "version": settings.app_version,
            "environment": settings.app_env,
        }

    @app.get("/", tags=["root"])
    async def root():
        return {
            "message": f"{settings.app_name} API",
            "docs": "/docs",
            "health": "/health",
        }

    # === Routerlar ===
    app.include_router(
        auth_router,
        prefix=f"{settings.api_v1_prefix}/auth",
        tags=["auth"],
    )
    app.include_router(
        chat_router,
        prefix=f"{settings.api_v1_prefix}/chat",
        tags=["chat"],
    )
    app.include_router(
        documents_router,
        prefix=f"{settings.api_v1_prefix}/documents",
        tags=["documents"],
    )

    return app


# Module-level app — uvicorn shu bilan ishga tushadi
app = create_app()
