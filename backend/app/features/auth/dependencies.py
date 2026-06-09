"""
Auth dependencies.
Real JWT-based authentication.
"""
import logging

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.deps import get_user_repo
from app.core.exceptions import DocChatException, InvalidCredentialsError
from app.core.security import decode_token
from app.features.auth.repository import UserRepository
from app.features.auth.schemas import UserResponse

logger = logging.getLogger(__name__)


class ForbiddenError(DocChatException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Bu amal uchun admin huquqi kerak"


# OAuth2 scheme — Swagger UI "Authorize" tugmasi uchun
# tokenUrl — login endpoint (full path)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repo),
) -> UserResponse:
    """
    JWT token dan joriy foydalanuvchini olish.

    1. Token decode
    2. user_id (sub) ni olish
    3. DB dan user topish
    """
    try:
        payload = decode_token(token)
    except JWTError:
        raise InvalidCredentialsError("Token noto'g'ri yoki muddati o'tgan")

    # Token turini tekshirish (refresh token bilan access qilib bo'lmaydi)
    if payload.get("type") != "access":
        raise InvalidCredentialsError("Access token kerak")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise InvalidCredentialsError("Token ichida user ID yo'q")

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise InvalidCredentialsError("Token format xato")

    user = await user_repo.get(user_id)
    if not user:
        raise InvalidCredentialsError("Foydalanuvchi topilmadi")

    return UserResponse.model_validate(user)


async def get_current_active_user(
    user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """Aktiv foydalanuvchi."""
    if not user.is_active:
        raise InvalidCredentialsError("Foydalanuvchi aktiv emas")
    return user


async def get_current_superuser(
    user: UserResponse = Depends(get_current_active_user),
) -> UserResponse:
    """
    Faqat admin (superuser) ruxsat etiladi.
    Role-based access control uchun.
    """
    if not user.is_superuser:
        raise ForbiddenError()
    return user
