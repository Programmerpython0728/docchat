"""Ollama LLM provider — lokal modellar"""
import asyncio
import json
import logging
from collections.abc import AsyncIterator

from app.core.config import get_settings
from app.core.http_client import get_http_client
from app.core.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    def __init__(self):
        settings = get_settings()
        self.base_url = settings.ollama_base_url
        self.chat_model = settings.ollama_chat_model
        self.embed_model = settings.ollama_embed_model

    async def chat_stream(self, messages: list[dict]) -> AsyncIterator[str]:
        client = get_http_client()
        async with client.stream(
            "POST",
            f"{self.base_url}/api/chat",
            json={"model": self.chat_model, "messages": messages, "stream": True},
        ) as response:
            async for line in response.aiter_lines():
                if not line:
                    continue
                data = json.loads(line)
                content = data.get("message", {}).get("content", "")
                if content:
                    yield content

    async def embed(self, text: str) -> list[float]:
        client = get_http_client()
        response = await client.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.embed_model, "prompt": text},
        )
        return response.json()["embedding"]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        # Ollama batch'ni native qo'llab-quvvatlamaydi — ketma-ket
        return await asyncio.gather(*[self.embed(t) for t in texts])
