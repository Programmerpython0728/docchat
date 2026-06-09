"""Gemini provider test"""
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.core.llm.gemini_provider import GeminiProvider


async def main():
    provider = GeminiProvider()

    # Embedding test
    emb = await provider.embed("Salom dunyo")
    print(f"[OK] Embedding dimension: {len(emb)}")  # 768 bo'lishi kerak
    print(f"     birinchi 3: {emb[:3]}")

    # Batch embedding
    embs = await provider.embed_batch(["Bir", "Ikki", "Uch"])
    print(f"[OK] Batch embedding: {len(embs)} ta, har biri {len(embs[0])} dim")

    # Chat test
    messages = [
        {"role": "system", "content": "Sen O'zbek tilida javob beradigan yordamchisan. Qisqa javob ber."},
        {"role": "user", "content": "RAG nima va u qanday ishlaydi? 2-3 jumlada javob ber."},
    ]
    print("\nJavob: ", end="", flush=True)
    async for token in provider.chat_stream(messages):
        print(token, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())
