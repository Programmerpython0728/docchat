"""
Admin foydalanuvchi yaratish skripti.

Ishga tushirish:
    uv run python scripts/create_admin.py
"""
import asyncio
import sys
from pathlib import Path

# backend/ ni sys.path ga qo'shamiz, shunda `app` import bo'ladi
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Windows: asyncpg uchun SelectorEventLoop
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.core.database import close_engine, get_db_context, import_all_models, init_engine
from app.core.security import hash_password
from app.features.auth.repository import UserRepository

# Barcha modellar Base.metadata ga ro'yxatdan o'tsin (relationship resolution uchun)
import_all_models()


async def create_admin(email: str, password: str, full_name: str):
    init_engine()
    async with get_db_context() as db:
        repo = UserRepository(db)

        if await repo.email_exists(email):
            print(f"[XATO] {email} allaqachon mavjud")
            await close_engine()
            return

        user = await repo.create(
            email=email.lower(),
            hashed_password=hash_password(password),
            full_name=full_name,
            is_superuser=True,
            is_active=True,
        )
        await db.commit()
        print(f"[OK] Admin yaratildi: id={user.id}, email={user.email}")

    await close_engine()


if __name__ == "__main__":
    email = input("Admin email: ").strip()
    password = input("Admin parol: ").strip()
    full_name = input("To'liq ism: ").strip()
    asyncio.run(create_admin(email, password, full_name))
