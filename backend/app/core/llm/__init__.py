"""LLM provider factory"""
from functools import lru_cache

from app.core.config import get_settings
from app.core.llm.base import LLMProvider
from app.core.llm.ollama_provider import OllamaProvider
from app.core.llm.openai_provider import OpenAIProvider


@lru_cache
def get_llm_provider() -> LLMProvider:
    """Settings ga ko'ra provider qaytaradi."""
    settings = get_settings()
    if settings.llm_provider == "openai":
        return OpenAIProvider()
    elif settings.llm_provider == "ollama":
        return OllamaProvider()
    raise ValueError(f"Noma'lum provider: {settings.llm_provider}")
