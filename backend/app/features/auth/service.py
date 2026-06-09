"""
Auth service — authentication biznes logikasi.

Router faqat HTTP bilan shug'ullanadi, biznes logika shu yerda:
- Foydalanuvchi yaratish (parol hash bilan)
- Login (parol tekshirish, token yaratish)
- Token refresh
"""
import logging

from app.core.config import get_settings
from app.core.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.features.auth.models import User
from app.features.auth.repository import UserRepository
from app.features.auth.schemas import TokenResponse, UserCreate

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication biznes logikasi."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, user_in: UserCreate) -> User:
        """
        Yangi foydalanuvchi yaratish.

        Raises:
            EmailAlreadyExistsError: email allaqachon mavjud
        """
        # Email tekshirish
        if await self.user_repo.email_exists(user_in.email):
            raise EmailAlreadyExistsError()

        # Parolni hash qilish va yaratish
        user = await self.user_repo.create(
            email=user_in.email.lower(),
            hashed_password=hash_password(user_in.password),
            full_name=user_in.full_name,
        )

        logger.info(f"Foydalanuvchi yaratildi: id={user.id}, email={user.email}")
        return user

    async def authenticate(self, email: str, password: str) -> User:
        """
        Foydalanuvchini autentifikatsiya qilish.

        Raises:
            InvalidCredentialsError: email yoki parol noto'g'ri
        """
        user = await self.user_repo.get_by_email(email)

        # Email topilmadi YOKI parol noto'g'ri — bir xil xato
        # (Xavfsizlik: hacker email mavjudligini bilmasligi kerak)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InvalidCredentialsError("Foydalanuvchi bloklangan")

        logger.info(f"Login muvaffaqiyatli: user_id={user.id}")
        return user

    def create_tokens(self, user: User) -> TokenResponse:
        """Foydalanuvchi uchun access va refresh tokenlar."""
        settings = get_settings()

        # Token ichiga role qo'shamiz (authorization uchun)
        role = "admin" if user.is_superuser else "user"

        access_token = create_access_token(
            subject=user.id,
            extra_claims={"role": role},
        )
        refresh_token = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_expire_minutes * 60,
        )

    async def login(self, email: str, password: str) -> TokenResponse:
        """To'liq login flow: authenticate + token yaratish."""
        user = await self.authenticate(email, password)
        return self.create_tokens(user)
