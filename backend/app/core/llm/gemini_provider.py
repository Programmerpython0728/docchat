"""Gemini LLM provider"""
import logging
from collections.abc import AsyncIterator

from google import genai
from google.genai import types

from app.core.config import get_settings
from app.core.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    def __init__(self):
        settings = get_settings()
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.chat_model = "gemini-2.5-flash"
        self.embed_model = "gemini-embedding-001"
        # 503 UNAVAILABLE bo'lsa fallback model
        self.chat_model_fallback = "gemini-2.5-flash-lite"
        self.embed_dim = settings.embedding_dimension  # DB column'ga mos (768)

    async def chat_stream(self, messages: list[dict]) -> AsyncIterator[str]:
        """Streaming chat — system instruction + multi-turn + 503 fallback."""
        system_text = ""
        contents = []
        for msg in messages:
            if msg["role"] == "system":
                system_text = msg["content"]
            else:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(
                    types.Content(role=role, parts=[types.Part(text=msg["content"])])
                )

        config = types.GenerateContentConfig(
            system_instruction=system_text or None,
            temperature=0.3,
        )

        # Birinchi: 2.5-flash. 503 (UNAVAILABLE) bo'lsa: 2.5-flash-lite ga o'tamiz.
        for model_name in (self.chat_model, self.chat_model_fallback):
            try:
                stream = await self.client.aio.models.generate_content_stream(
                    model=model_name,
                    contents=contents,
                    config=config,
                )
                async for chunk in stream:
                    if chunk.text:
                        yield chunk.text
                return
            except Exception as e:
                msg = str(e)
                # 503 (UNAVAILABLE) bo'lsa fallback'ga sinaymиz, boshqa xato — qaytarib yuboramiz
                if "503" in msg or "UNAVAILABLE" in msg:
                    logger.warning(f"{model_name} 503, fallback ga o'tamiz")
                    continue
                raise

    async def embed(self, text: str) -> list[float]:
        """Bitta text uchun 768-dim embedding."""
        result = await self.client.aio.models.embed_content(
            model=self.embed_model,
            contents=text,
            config=types.EmbedContentConfig(output_dimensionality=self.embed_dim),
        )
        return result.embeddings[0].values

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Ko'p text uchun batch embedding."""
        result = await self.client.aio.models.embed_content(
            model=self.embed_model,
            contents=texts,
            config=types.EmbedContentConfig(output_dimensionality=self.embed_dim),
        )
        return [e.values for e in result.embeddings]
