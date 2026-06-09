"""RAG service — retrieval + generation"""
import logging
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.llm import get_llm_provider
from app.features.rag.embedding_service import EmbeddingService
from app.features.rag.search_repository import VectorSearchRepository

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """Sen yordamchi AI assistantsan. Foydalanuvchi savoliga FAQAT berilgan kontekst asosida javob ber.

Qoidalar:
- Faqat kontekstdagi ma'lumotdan foydalan
- Agar kontekstda javob yo'q bo'lsa: "Berilgan hujjatlarda bu haqida ma'lumot topilmadi" deb javob ber
- Javobingni manbalar bilan asoslab ber

Kontekst:
{context}
"""


class RAGService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embed_service = EmbeddingService()
        self.search_repo = VectorSearchRepository(db)
        self.llm = get_llm_provider()
        self._hybrid_repo = None

    @property
    def hybrid_repo(self):
        if self._hybrid_repo is None:
            from app.features.rag.hybrid_search import HybridSearchRepository
            self._hybrid_repo = HybridSearchRepository(self.db)
        return self._hybrid_repo

    async def retrieve(
        self,
        query: str,
        user_id: int,
        top_k: int = 5,
        document_ids: list[int] | None = None,
    ) -> list[dict]:
        """Relevant chunklarni topish (vector only)."""
        query_emb = await self.embed_service.embed_text(query)
        results = await self.search_repo.search_similar(
            query_embedding=query_emb,
            user_id=user_id,
            top_k=top_k,
            document_ids=document_ids,
        )
        return [
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "content": chunk.content,
                "distance": float(distance),
                "similarity": 1 - float(distance),
            }
            for chunk, distance in results
        ]

    async def retrieve_hybrid(
        self,
        query: str,
        user_id: int,
        top_k: int = 5,
    ) -> list[dict]:
        """Hybrid retrieval (vector + BM25 + RRF)."""
        query_emb = await self.embed_service.embed_text(query)
        return await self.hybrid_repo.hybrid_search(
            query_text=query,
            query_embedding=query_emb,
            user_id=user_id,
            top_k=top_k,
        )

    def _build_context(self, chunks: list[dict]) -> str:
        """Chunklardan kontekst matn."""
        parts = []
        for i, chunk in enumerate(chunks, 1):
            parts.append(f"[Manba {i}]\n{chunk['content']}")
        return "\n\n".join(parts)

    async def generate_stream(
        self,
        query: str,
        user_id: int,
        top_k: int = 5,
        document_ids: list[int] | None = None,
        use_hybrid: bool = False,
    ) -> AsyncIterator[dict]:
        """To'liq RAG: retrieve → generate (streaming)."""
        if use_hybrid and not document_ids:
            chunks = await self.retrieve_hybrid(query, user_id, top_k)
        else:
            chunks = await self.retrieve(query, user_id, top_k, document_ids)

        yield {
            "type": "sources",
            "sources": [
                {
                    "chunk_id": c["chunk_id"],
                    "document_id": c["document_id"],
                    "preview": c["content"][:150],
                    "similarity": round(c.get("similarity", c.get("rrf_score", 0)), 3),
                }
                for c in chunks
            ],
        }

        if not chunks:
            yield {"type": "token", "content": "Hujjatlaringizda bu haqida ma'lumot topilmadi."}
            yield {"type": "done"}
            return

        context = self._build_context(chunks)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
            {"role": "user", "content": query},
        ]

        async for tok in self.llm.chat_stream(messages):
            yield {"type": "token", "content": tok}

        yield {"type": "done"}
