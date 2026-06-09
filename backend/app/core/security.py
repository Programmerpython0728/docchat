"""
Security utilities — password hashing va JWT.

Bu modul auth ning eng past darajadagi qismi:
- Parol hash/verify (bcrypt)
- JWT yaratish/decode (python-jose)
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# bcrypt password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# === Password hashing ===
def hash_password(password: str) -> str:
    """Parolni bcrypt bilan hash qilish."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Parol hashga mos kelishini tekshirish."""
    return pwd_context.verify(plain_password, hashed_password)


# === JWT ===
def create_access_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """
    JWT access token yaratish.

    Args:
        subject: token egasi (odatda user_id)
        expires_delta: amal qilish muddati (None — settings dan default)
        extra_claims: qo'shimcha ma'lumotlar (role, etc.)

    Returns:
        Imzolangan JWT string
    """
    settings = get_settings()

    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.jwt_expire_minutes)

    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    to_encode: dict[str, Any] = {
        "sub": str(subject),       # subject (user_id)
        "exp": expire,              # expiration
        "iat": now,                 # issued at
        "type": "access",           # token turi
    }

    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def create_refresh_token(subject: str | int) -> str:
    """Refresh token — uzun muddat (30 kun)."""
    return create_access_token(
        subject=subject,
        expires_delta=timedelta(days=30),
        extra_claims={"type": "refresh"},
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    JWT ni decode qilish va tekshirish.

    Returns:
        Token payload (dict)

    Raises:
        JWTError: token noto'g'ri yoki muddati o'tgan
    """
    settings = get_settings()
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )
    return payload


def get_token_subject(token: str) -> str | None:
    """
    Token dan subject (user_id) ni olish.

    Xato bo'lsa None qaytaradi (exception ko'tarmaydi).
    """
    try:
        payload = decode_token(token)
        return payload.get("sub")
    except JWTError as e:
        logger.debug(f"Token decode xatosi: {e}")
        return None
