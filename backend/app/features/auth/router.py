"""Authentication endpoints"""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, status

from app.features.auth.dependencies import get_current_active_user
from app.features.auth.schemas import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yangi foydalanuvchi ro'yxatdan o'tkazish",
)
async def register(user_in: UserCreate) -> UserResponse:
    """
    Yangi foydalanuvchi yaratish.

    - **email**: Email manzili (unique)
    - **password**: Kuchli parol (min 8 belgi, katta harf, raqam)
    - **full_name**: To'liq ism (ixtiyoriy)

    Muvaffaqiyatli bo'lsa, yangi user qaytariladi.
    """
    logger.info(f"Yangi foydalanuvchi ro'yxati: {user_in.email}")

    # TODO 5-kun: real implementation (DB ga saqlash, parol hash)
    return UserResponse(
        id=1,
        email=user_in.email,
        full_name=user_in.full_name,
        is_active=True,
        created_at=datetime.now(),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Tizimga kirish",
)
async def login(credentials: UserLogin) -> TokenResponse:
    """
    Email va parol bilan tizimga kirish.

    Muvaffaqiyatli bo'lsa, JWT access token qaytariladi.
    Token ni `Authorization: Bearer <token>` header'da yuborish kerak.
    """
    logger.info(f"Login urinishi: {credentials.email}")

    # TODO 5-kun: real implementation
    return TokenResponse(
        access_token="mock_jwt_token_for_development",
        token_type="bearer",
        expires_in=7 * 24 * 60 * 60,  # 7 kun
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Joriy foydalanuvchi ma'lumotlari",
)
async def get_me(
    current_user: UserResponse = Depends(get_current_active_user),
) -> UserResponse:
    """
    Hozirgi authenticated foydalanuvchi ma'lumotlari.

    `Authorization: Bearer <token>` header kerak.
    """
    return current_user
