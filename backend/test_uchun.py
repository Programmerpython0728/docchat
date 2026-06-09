import asyncio
from sqlalchemy import text
from app.core.database import init_engine, close_engine, get_db_context


async def main():
    init_engine()

    async with get_db_context() as db:
        result = await db.execute(text("SELECT version()"))
        print(f"✅ PostgreSQL: {result.scalar()}")

        result = await db.execute(
            text("SELECT extname FROM pg_extension WHERE extname='vector'")
        )
        print(f"✅ pgvector: {result.scalar()}")

    await close_engine()


if __name__ == "__main__":
    asyncio.run(main())