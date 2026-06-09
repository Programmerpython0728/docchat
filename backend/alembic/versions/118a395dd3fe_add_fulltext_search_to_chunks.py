"""add fulltext search to chunks

Revision ID: 118a395dd3fe
Revises: 486c66e7f48c
Create Date: 2026-05-31 06:58:53.221325

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '118a395dd3fe'
down_revision: Union[str, Sequence[str], None] = '486c66e7f48c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        ALTER TABLE document_chunks
        ADD COLUMN content_tsv tsvector
        GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED
    """)
    op.execute("""
        CREATE INDEX ix_chunks_content_tsv
        ON document_chunks USING gin(content_tsv)
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS ix_chunks_content_tsv")
    op.execute("ALTER TABLE document_chunks DROP COLUMN IF EXISTS content_tsv")
