"""
Mashq 4: Semaphore bilan concurrency limit
- 100 ta URL bor, lekin bir vaqtda max 10 ta request
"""
import asyncio
import time

import httpx

URLS = ["https://httpbin.org/delay/1"] * 50


async def fetch_with_limit(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    url: str,
    index: int,
) -> int:
    async with sem:  # max N ta concurrent
        print(f"  [{time.strftime('%H:%M:%S')}] Request {index} boshlanmoqda")
        r = await client.get(url, timeout=10)
        return r.status_code


async def main():
    sem = asyncio.Semaphore(10)  # 10 ta concurrent max
    start = time.perf_counter()

    async with httpx.AsyncClient() as client:
        tasks = [
            fetch_with_limit(client, sem, url, i)
            for i, url in enumerate(URLS)
        ]
        results = await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start
    print(f"\n50 ta request, 10 concurrent: {elapsed:.2f}s")
    # Kutilgan: ~5s (50 / 10 = 5 ta batch, har biri 1s)


if __name__ == "__main__":
    asyncio.run(main())