"""LLM provider interface"""
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class LLMProvider(ABC):
    """LLM provider abstract base."""

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[dict],
    ) -> AsyncIterator[str]:
        """Streaming chat — token-token yield."""
        ...

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Bitta text uchun embedding."""
        ...

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Ko'p text uchun embedding (batch)."""
        ...
