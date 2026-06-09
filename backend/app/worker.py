"""
arq background worker.

Ishga tushirish:
    uv run arq app.worker.WorkerSettings
"""
import asyncio
import logging

from arq.connections import RedisSettings

from app.core.config import get_settings
from app.core.database import close_engine, get_db_context, import_all_models, init_engine
from app.features.documents.models import DocumentStatus
from app.features.documents.repository import DocumentRepository

logger = logging.getLogger(__name__)

# Relationship resolution uchun barcha modellarni yuklash
import_all_models()


async def index_document(ctx: dict, document_id: int):
    """Real ingestion (parse → chunk → embed → save)."""
    from app.features.rag.ingestion import ingest_document
    await ingest_document(document_id)


async def startup(ctx: dict):
    """Worker startup."""
    from app.core.http_client import init_http_client
    from app.core.redis_client import init_redis
    init_engine()
    init_redis()
    init_http_client()
    logger.info("arq worker started")


async def shutdown(ctx: dict):
    """Worker shutdown."""
    from app.core.http_client import close_http_client
    from app.core.redis_client import close_redis
    await close_http_client()
    await close_redis()
    await close_engine()
    logger.info("arq worker stopped")


def _redis_settings() -> RedisSettings:
    settings = get_settings()
    return RedisSettings.from_dsn(str(settings.redis_url))


class WorkerSettings:
    """arq worker konfiguratsiyasi."""
    functions = [index_document]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = _redis_settings()
