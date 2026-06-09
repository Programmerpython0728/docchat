"""Authentication schemas — Pydantic v2"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Foydalanuvchi schemasining umumiy maydonlari."""
    email: EmailStr = Field(..., description="Foydalanuvchi email manzili")
    full_name: str | None = Field(None, max_length=100)


class UserCreate(UserBase):
    """Ro'yxatdan o'tish uchun input."""
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,  # bcrypt cheklovi
        description="Kuchli parol (min 8 belgi)",
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Parol kuchini tekshirish."""
        if not any(c.isupper() for c in v):
            raise ValueError("Parolda kamida 1 ta katta harf bo'lishi kerak")
        if not any(c.isdigit() for c in v):
            raise ValueError("Parolda kamida 1 ta raqam bo'lishi kerak")
        return v


class UserLogin(BaseModel):
    """Login uchun input."""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """API javobida qaytariladigan user ma'lumotlari.

    Diqqat: password yo'q!
    """
    model_config = ConfigDict(from_attributes=True)  # SQLAlchemy model dan o'qish uchun

    id: int
    is_active: bool
    is_superuser: bool = False
    created_at: datetime


class TokenResponse(BaseModel):
    """JWT token javobi."""
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token muddati (sekund)")


class TokenPayload(BaseModel):
    """JWT payload — decode qilingandan keyin."""
    sub: str           # user_id
    exp: int
    iat: int
    type: str          # access | refresh
    role: str | None = None


class RefreshTokenRequest(BaseModel):
    """Refresh token bilan yangi access token so'rovi."""
    refresh_token: str
