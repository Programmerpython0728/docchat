"""Document va DocumentChunk models"""
from enum import Enum
from typing import TYPE_CHECKING, Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Enum as SQLEnum
from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import get_settings
from app.core.database import Base
from app.core.db_mixins import IDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.features.auth.models import User


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class Document(Base, IDMixin, TimestampMixin):
    __tablename__ = "documents"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)

    status: Mapped[DocumentStatus] = mapped_column(
        SQLEnum(DocumentStatus, name="document_status"),
        default=DocumentStatus.PENDING,
        nullable=False, index=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user: Mapped["User"] = relationship(back_populates="documents", lazy="raise")
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename={self.filename!r})>"


class DocumentChunk(Base, IDMixin, TimestampMixin):
    """Hujjat bo'lagi — embedding bilan."""
    __tablename__ = "document_chunks"

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # pgvector column
    embedding: Mapped[list[float]] = mapped_column(
        Vector(get_settings().embedding_dimension),
        nullable=False,
    )

    # `metadata` SQLAlchemy reserved word — chunk_metadata deymiz
    chunk_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True,
    )

    document: Mapped["Document"] = relationship(
        back_populates="chunks", lazy="raise"
    )

    __table_args__ = (
        Index("ix_chunks_document_index", "document_id", "chunk_index"),
        # HNSW vector index Alembic da qo'lda qo'shamiz
    )

    def __repr__(self) -> str:
        return f"<DocumentChunk(id={self.id}, doc={self.document_id}, idx={self.chunk_index})>"
