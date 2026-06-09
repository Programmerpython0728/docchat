"""Authentication endpoints — real JWT"""
import logging

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_auth_service, get_user_repo
from app.features.auth.dependencies import (
    get_current_active_user,
    get_current_superuser,
)
from app.features.auth.repository import UserRepository
from app.features.auth.schemas import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.features.auth.service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ro'yxatdan o'tish",
)
async def register(
    user_in: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Yangi foydalanuvchi yaratish (bcrypt hash bilan)."""
    user = await auth_service.register(user_in)
    await db.commit()
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Tizimga kirish (OAuth2 form)",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Email va parol bilan kirish.

    **MUHIM**: OAuth2 standarti `username` maydonini ishlatadi,
    biz email ni shu yerga yozamiz (Swagger UI mosligi uchun).

    Muvaffaqiyatli bo'lsa, JWT access + refresh token qaytadi.
    """
    return await auth_service.login(
        email=form_data.username,
        password=form_data.password,
    )


@router.post(
    "/login/json",
    response_model=TokenResponse,
    summary="Tizimga kirish (JSON)",
)
async def login_json(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    JSON formatda login (frontend uchun qulayroq).
    OAuth2 form o'rniga JSON body qabul qiladi.
    """
    return await auth_service.login(
        email=credentials.email,
        password=credentials.password,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Joriy foydalanuvchi",
)
async def get_me(
    current_user: UserResponse = Depends(get_current_active_user),
) -> UserResponse:
    """Hozirgi authenticated foydalanuvchi ma'lumotlari."""
    return current_user


@router.get(
    "/users",
    response_model=list[UserResponse],
    summary="Barcha foydalanuvchilar (faqat admin)",
)
async def list_all_users(
    admin: UserResponse = Depends(get_current_superuser),
    user_repo: UserRepository = Depends(get_user_repo),
) -> list[UserResponse]:
    """
    Barcha foydalanuvchilar ro'yxati.

    **Faqat admin** kira oladi. Oddiy user 403 oladi.
    """
    users = await user_repo.get_all(limit=100)
    return [UserResponse.model_validate(u) for u in users]
