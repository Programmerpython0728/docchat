"""Embedding service — cache bilan"""
import logging

from app.core.cache import embedding_cache
from app.core.llm import get_llm_provider

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        self.provider = get_llm_provider()

    async def embed_text(self, text: str) -> list[float]:
        """Cache → API."""
        cached = await embedding_cache.get(text)
        if cached:
            return cached

        embedding = await self.provider.embed(text)
        await embedding_cache.set(text, embedding)
        return embedding

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Batch embedding — cache check + API."""
        results: list[list[float] | None] = [None] * len(texts)
        to_fetch: list[tuple[int, str]] = []

        # Cache check
        for i, text in enumerate(texts):
            cached = await embedding_cache.get(text)
            if cached:
                results[i] = cached
            else:
                to_fetch.append((i, text))

        # API for uncached
        if to_fetch:
            fetch_texts = [t for _, t in to_fetch]
            embeddings = await self.provider.embed_batch(fetch_texts)
            for (i, text), emb in zip(to_fetch, embeddings):
                results[i] = emb
                await embedding_cache.set(text, emb)

        return results  # type: ignore
