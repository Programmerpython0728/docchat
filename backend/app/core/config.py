"""
Application settings.

Pydantic Settings — environment variables va .env fayldan
sozlamalarni o'qiydi va type-safe qiladi.
"""
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

# .env fayl proyekt root da (docchat/.env), config.py esa backend/app/core/ da.
# CWD ga bog'liq bo'lmaslik uchun absolute path hisoblaymiz:
#   parents[0]=core, [1]=app, [2]=backend, [3]=docchat (root)
_ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Bosh sozlamalar klassi.

    Sozlamalar tartibi (yuqoridan pastga, yuqorisi g'olib):
    1. Environment variables (export DATABASE_URL=...)
    2. .env fayl (proyekt root da)
    3. Default qiymatlar (bu yerda berilgan)
    """

    model_config = SettingsConfigDict(
        env_file=_ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,       # DATABASE_URL = database_url
        extra="ignore",              # noma'lum env vars ignore qilinadi
    )

    # === App umumiy ===
    app_name: str = "DocChat"
    app_version: str = "0.1.0"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # === API ===
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:3000"]  # Next.js

    # === Database ===
    # Pydantic PostgresDsn URL formatini validatsiya qiladi
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://docchat:docchat_dev_password@localhost:5432/docchat",
        description="PostgreSQL ulanish stringi (asyncpg driver bilan)",
    )
    db_pool_size: int = Field(default=10, ge=1, le=100)
    db_max_overflow: int = Field(default=20, ge=0)
    db_echo: bool = False  # SQL queries ni log qilish (debug uchun)

    # === Redis ===
    redis_url: RedisDsn = Field(
        default="redis://localhost:6379/0",
        description="Redis ulanish stringi",
    )

    # === JWT ===
    jwt_secret: str = Field(
        default="change_me_in_production_minimum_32_chars_long",
        min_length=32,
        description="JWT signing uchun maxfiy kalit",
    )
    jwt_algorithm: Literal["HS256", "HS384", "HS512"] = "HS256"
    jwt_expire_minutes: int = Field(default=60 * 24 * 7, ge=1)  # 7 kun

    # === LLM ===
    llm_provider: Literal["openai", "ollama", "anthropic", "gemini"] = "gemini"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    gemini_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3.2:3b"
    ollama_embed_model: str = "nomic-embed-text"

    # Embedding
    embedding_provider: Literal["openai", "local", "gemini"] = "gemini"
    embedding_model: str = "gemini-embedding-001"
    embedding_dimension: int = 768   # Gemini text-embedding-004 = 768, Ollama nomic-embed-text = 768

    # === File uploads ===
    upload_max_size_mb: int = Field(default=50, ge=1, le=500)
    upload_dir: str = "./uploads"
    allowed_extensions: set[str] = {".pdf", ".docx", ".txt", ".md"}

    # === Rate limiting ===
    rate_limit_per_minute: int = 60

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    """Settings ni cache qilamiz — har safar fayldan o'qimaslik uchun.

    `lru_cache` bilan birinchi chaqirilganda yaratiladi,
    keyingi chaqiruvlarda o'sha instance qaytadi.

    Test uchun cache ni tozalash mumkin:
        get_settings.cache_clear()
    """
    return Settings()


# Convenience: settings = get_settings()
# Lekin DI uchun get_settings ni dependency sifatida ishlatamiz
