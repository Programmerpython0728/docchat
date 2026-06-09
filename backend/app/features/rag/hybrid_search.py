"""Hybrid search — vector + BM25 + RRF"""
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class HybridSearchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def hybrid_search(
        self,
        query_text: str,
        query_embedding: list[float],
        user_id: int,
        top_k: int = 5,
        rrf_k: int = 60,
    ) -> list[dict]:
        """Hybrid search: vector + BM25, RRF bilan birlashtirilgan."""
        sql = text("""
            WITH vector_search AS (
                SELECT dc.id,
                       ROW_NUMBER() OVER (
                           ORDER BY dc.embedding <=> CAST(:query_emb AS vector)
                       ) AS rank
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                WHERE d.user_id = :user_id
                ORDER BY dc.embedding <=> CAST(:query_emb AS vector)
                LIMIT 20
            ),
            bm25_search AS (
                SELECT dc.id,
                       ROW_NUMBER() OVER (
                           ORDER BY ts_rank(dc.content_tsv, query) DESC
                       ) AS rank
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id,
                     plainto_tsquery('simple', :query_text) query
                WHERE d.user_id = :user_id
                  AND dc.content_tsv @@ query
                ORDER BY ts_rank(dc.content_tsv, query) DESC
                LIMIT 20
            ),
            combined AS (
                SELECT id, SUM(score) AS rrf_score FROM (
                    SELECT id, 1.0 / (:rrf_k + rank) AS score FROM vector_search
                    UNION ALL
                    SELECT id, 1.0 / (:rrf_k + rank) AS score FROM bm25_search
                ) scores
                GROUP BY id
            )
            SELECT dc.id, dc.content, dc.document_id, c.rrf_score
            FROM combined c
            JOIN document_chunks dc ON dc.id = c.id
            ORDER BY c.rrf_score DESC
            LIMIT :top_k
        """)

        emb_str = str(query_embedding)

        result = await self.db.execute(
            sql,
            {
                "query_emb": emb_str,
                "query_text": query_text,
                "user_id": user_id,
                "rrf_k": rrf_k,
                "top_k": top_k,
            },
        )

        return [
            {
                "chunk_id": row[0],
                "content": row[1],
                "document_id": row[2],
                "rrf_score": float(row[3]),
            }
            for row in result.all()
        ]
