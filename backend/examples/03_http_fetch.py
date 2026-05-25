"""
Mashq 3: 10 ta URL ni sync va async fetch qilib taqqoslash
- Bu eng katta "aha moment"
"""
import asyncio
import time

import httpx
import requests  # sync HTTP

URLS = [
    "https://httpbin.org/delay/1",  # har biri 1s kutadi
] * 10  # 10 ta bir xil URL


def sync_fetch_all() -> list[int]:
    """Sync — har bir request alohida kutiladi"""
    results = []
    for url in URLS:
        r = requests.get(url, timeout=10)
        results.append(r.status_code)
    return results


async def async_fetch_one(client: httpx.AsyncClient, url: str) -> int:
    r = await client.get(url, timeout=10)
    return r.status_code


async def async_fetch_all() -> list[int]:
    """Async — hamma request lar parallel"""
    async with httpx.AsyncClient() as client:
        tasks = [async_fetch_one(client, url) for url in URLS]
        results = await asyncio.gather(*tasks)
    return results


def main():
    # Sync
    print("Sync (requests) boshlanmoqda...")
    start = time.perf_counter()
    sync_results = sync_fetch_all()
    sync_time = time.perf_counter() - start
    print(f"Sync vaqti:  {sync_time:.2f}s")

    # Async
    print("\nAsync (httpx) boshlanmoqda...")
    start = time.perf_counter()
    async_results = asyncio.run(async_fetch_all())
    async_time = time.perf_counter() - start
    print(f"Async vaqti: {async_time:.2f}s")

    print(f"\n🚀 Tezlik farqi: {sync_time/async_time:.1f}x")


if __name__ == "__main__":
    main()