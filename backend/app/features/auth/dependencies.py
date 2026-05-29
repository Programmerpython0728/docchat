"""
Auth dependencies.

Hozircha mock — 5-kun da real JWT validation qo'shamiz.
"""
from datetime import datetime

from fastapi import Depends, Header

from app.core.exceptions import InvalidCredentialsError
from app.features.auth.schemas import UserResponse


# Hozircha mock — keyinroq haqiqiy JWT decode bo'ladi
async def get_current_user(
    authorization: str | None = Header(default=None),
) -> UserResponse:
    """Joriy foydalanuvchini olish.

    Header dan Bearer token o'qib, user qaytariladi.

    Bu 5-kun da haqiqiy JWT bilan to'ldiriladi.
    Hozir mock — har qanday token bilan ishlaydi (development).
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise InvalidCredentialsError("Authorization header yo'q yoki noto'g'ri formatda")

    token = authorization.replace("Bearer ", "")

    # TODO 5-kun: real JWT decode
    # Hozircha har qanday token bilan mock user qaytaramiz
    if token == "invalid":
        raise InvalidCredentialsError()

    return UserResponse(
        id=1,
        email="test@docchat.uz",
        full_name="Test Foydalanuvchi",
        is_active=True,
        created_at=datetime.now(),
    )


# Active user check (subsequent dependency)
async def get_current_active_user(
    user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """Aktiv foydalanuvchi (banned emas)."""
    if not user.is_active:
        raise InvalidCredentialsError("Foydalanuvchi aktiv emas")
    return user
