"""
Mashq 6: PostgreSQL va Redis ga Python dan ulanish testi
"""
import asyncio
import sys

# Windows uchun: ProactorEventLoop o'rniga SelectorEventLoop ishlatamiz.
# asyncpg Windows'da ProactorEventLoop bilan WinError 64 beradi.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def test_postgres():
    """asyncpg orqali PostgreSQL ga ulanamiz"""
    import asyncpg

    conn = await asyncpg.connect(
        host="localhost",
        port=5433,  # Docker postgres — 5432 mahalliy postgres tomonidan band
        user="dasturchi_05",
        password="571632",
        database="docchat",
    )

    # pgvector extension borligini tekshirish
    result = await conn.fetchval(
        "SELECT extname FROM pg_extension WHERE extname = 'vector'"
    )
    print(f"[OK] PostgreSQL ulandi. pgvector: {result}")

    await conn.close()


async def test_redis():
    """redis.asyncio orqali Redis ga ulanamiz"""
    import redis.asyncio as redis

    client = redis.from_url("redis://localhost:6379/0")
    await client.set("test_key", "Salom DocChat")
    value = await client.get("test_key")
    print(f"[OK] Redis ulandi. Test qiymat: {value.decode()}")
    await client.delete("test_key")
    await client.aclose()


async def main():
    await test_postgres()
    await test_redis()


if __name__ == "__main__":
    asyncio.run(main())