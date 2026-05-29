"""
Mashq 13: Sync PDF parserni async wrapper bilan ishlatish
- Bu DocChat da real ishlatadigan pattern
"""
import asyncio
import time
from pathlib import Path

# Avval o'rnatish kerak:
# uv add pypdf
from pypdf import PdfReader


def extract_pdf_text_sync(file_path: str) -> str:
    """SYNC — pypdf sync kutubxona"""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


async def extract_pdf_text_async(file_path: str) -> str:
    """ASYNC wrapper — to_thread orqali"""
    return await asyncio.to_thread(extract_pdf_text_sync, file_path)


async def process_many_pdfs(file_paths: list[str]):
    """N ta PDF ni parallel parse qilish"""
    print(f"📚 {len(file_paths)} ta PDF parse qilinmoqda...")
    start = time.perf_counter()

    tasks = [extract_pdf_text_async(fp) for fp in file_paths]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    elapsed = time.perf_counter() - start

    success = sum(1 for r in results if isinstance(r, str))
    failed = len(results) - success
    print(f"⏱️  {elapsed:.2f}s | ✅ {success} | ❌ {failed}")


# Test uchun sample PDFlar (yoki ixtiyoriy PDF lar)
async def main():
    # O'z PDF fayllaringizni qo'ying yoki test PDF download qiling
    sample_pdfs = [
        # "/path/to/your/test.pdf",
       " D:\docchat\backend\examples\3 - kurssuniy intellekt va raqamli texnologiyalar.pdf"
    ]

    if not sample_pdfs:
        print("⚠️  Test uchun PDF qo'shing yoki bu mashqni o'tkazib yuboring")
        return

    await process_many_pdfs(sample_pdfs)


if __name__ == "__main__":
    asyncio.run(main())