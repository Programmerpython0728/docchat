"""change embedding dimension to 768 (ollama)

Revision ID: 679a3eb4514d
Revises: 118a395dd3fe
Create Date: 2026-05-31 08:10:59.998394

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '679a3eb4514d'
down_revision: Union[str, Sequence[str], None] = '118a395dd3fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """OpenAI (1536) -> Ollama nomic-embed-text (768)."""
    # 1. Eski HNSW index (1536 uchun) o'chiriladi
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding_hnsw")

    # 2. Mavjud chunklarni tozalash (1536-dim qiymatlar 768 ga mos kelmaydi)
    op.execute("DELETE FROM document_chunks")

    # 3. Column dimension'ini o'zgartirish
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(768)")

    # 4. HNSW index 768 uchun qayta yaratiladi
    op.execute(
        "CREATE INDEX ix_document_chunks_embedding_hnsw "
        "ON document_chunks "
        "USING hnsw (embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding_hnsw")
    op.execute("DELETE FROM document_chunks")
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(1536)")
    op.execute(
        "CREATE INDEX ix_document_chunks_embedding_hnsw "
        "ON document_chunks "
        "USING hnsw (embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )
