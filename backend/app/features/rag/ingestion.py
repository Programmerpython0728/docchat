"""Document ingestion pipeline"""
import asyncio
import logging

from app.core.database import get_db_context
from app.features.documents.models import DocumentStatus
from app.features.documents.repository import (
    DocumentChunkRepository,
    DocumentRepository,
)
from app.features.rag.chunker import chunk_text
from app.features.rag.embedding_service import EmbeddingService
from app.features.rag.parser import parse_document

logger = logging.getLogger(__name__)


async def ingest_document(document_id: int) -> None:
    """
    To'liq ingestion: parse → chunk → embed → save.
    Bu arq worker tomonidan chaqiriladi (background).
    """
    logger.info(f"Ingestion boshlandi: doc={document_id}")

    async with get_db_context() as db:
        doc_repo = DocumentRepository(db)
        doc = await doc_repo.get(document_id)
        if not doc:
            logger.error(f"Document {document_id} yo'q")
            return

        await doc_repo.update(doc, status=DocumentStatus.PROCESSING)
        await db.commit()
        file_path = doc.file_path

    try:
        # 1. Parse (sync → to_thread)
        text, page_count = await asyncio.to_thread(parse_document, file_path)
        logger.info(f"Parsed: {len(text)} chars, {page_count} pages")

        # 2. Chunk
        chunks = chunk_text(text, chunk_size=500, overlap=50)
        logger.info(f"Chunked: {len(chunks)} chunks")

        # 3. Embed (batch, cache bilan)
        embed_service = EmbeddingService()
        chunk_contents = [c.content for c in chunks]
        embeddings = await embed_service.embed_texts(chunk_contents)

        # 4. Save
        async with get_db_context() as db:
            chunk_repo = DocumentChunkRepository(db)
            chunks_data = [
                {
                    "document_id": document_id,
                    "chunk_index": chunk.index,
                    "content": chunk.content,
                    "embedding": emb,
                    "chunk_metadata": chunk.metadata,
                }
                for chunk, emb in zip(chunks, embeddings)
            ]
            await chunk_repo.bulk_create(chunks_data)

            doc_repo = DocumentRepository(db)
            doc = await doc_repo.get(document_id)
            await doc_repo.update(
                doc,
                status=DocumentStatus.INDEXED,
                page_count=page_count,
                chunk_count=len(chunks),
            )
            await db.commit()

        logger.info(f"Ingestion tugadi: doc={document_id}, {len(chunks)} chunks")

    except Exception as e:
        logger.exception(f"Ingestion xato: {e}")
        async with get_db_context() as db:
            doc_repo = DocumentRepository(db)
            doc = await doc_repo.get(document_id)
            if doc:
                await doc_repo.update(
                    doc,
                    status=DocumentStatus.FAILED,
                    error_message=str(e)[:500],
                )
                await db.commit()
