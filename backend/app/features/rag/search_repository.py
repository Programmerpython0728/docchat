"""Vector search — pgvector"""
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.documents.models import Document, DocumentChunk

logger = logging.getLogger(__name__)


class VectorSearchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_similar(
        self,
        query_embedding: list[float],
        user_id: int,
        top_k: int = 5,
        document_ids: list[int] | None = None,
    ) -> list[tuple[DocumentChunk, float]]:
        """
        Eng o'xshash chunklarni topish.

        Returns:
            [(chunk, distance), ...] — distance kichik = o'xshash
        """
        # cosine distance: embedding <=> query
        distance = DocumentChunk.embedding.cosine_distance(query_embedding)

        stmt = (
            select(DocumentChunk, distance.label("distance"))
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(Document.user_id == user_id)
        )

        if document_ids:
            stmt = stmt.where(DocumentChunk.document_id.in_(document_ids))

        stmt = stmt.order_by(distance).limit(top_k)

        result = await self.db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]
