"""Document repository"""
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repository import BaseRepository
from app.features.documents.models import Document, DocumentChunk, DocumentStatus


class DocumentRepository(BaseRepository[Document]):
    model = Document

    async def get_by_user(
        self,
        user_id: int,
        *,
        skip: int = 0,
        limit: int = 20,
        status: DocumentStatus | None = None,
    ) -> list[Document]:
        """Foydalanuvchining hujjatlari."""
        stmt = select(Document).where(Document.user_id == user_id)

        if status:
            stmt = stmt.where(Document.status == status)

        stmt = stmt.order_by(Document.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user(
        self,
        user_id: int,
        status: DocumentStatus | None = None,
    ) -> int:
        """Foydalanuvchi hujjatlari soni."""
        stmt = (
            select(func.count())
            .select_from(Document)
            .where(Document.user_id == user_id)
        )
        if status:
            stmt = stmt.where(Document.status == status)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_user_document(
        self, document_id: int, user_id: int
    ) -> Document | None:
        """Bitta hujjat — faqat o'z hujjati."""
        stmt = select(Document).where(
            Document.id == document_id,
            Document.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class DocumentChunkRepository(BaseRepository[DocumentChunk]):
    model = DocumentChunk

    async def bulk_create(self, chunks_data: list[dict]) -> list[DocumentChunk]:
        """Ko'p chunklarni bir vaqtda yaratish."""
        chunks = [DocumentChunk(**data) for data in chunks_data]
        self.db.add_all(chunks)
        await self.db.flush()
        return chunks

    async def delete_by_document(self, document_id: int) -> None:
        """Hujjatning chunklarini o'chirish."""
        stmt = delete(DocumentChunk).where(
            DocumentChunk.document_id == document_id
        )
        await self.db.execute(stmt)
