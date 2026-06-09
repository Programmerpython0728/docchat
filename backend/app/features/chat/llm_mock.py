"""Mock LLM — 8-kunda real LLM bilan almashtiriladi"""
import asyncio
from collections.abc import AsyncIterator


async def mock_llm_stream(prompt: str) -> AsyncIterator[str]:
    """LLM streaming simulyatsiya — token-token."""
    response = (
        f"Savolingiz: '{prompt}'. "
        "Bu mock javob. 9-kunda haqiqiy RAG javobi keladi. "
        "Hozircha streaming mexanizmini test qilyapmiz."
    )
    for word in response.split():
        await asyncio.sleep(0.05)  # token generation simulyatsiya
        yield word + " "
