"""Umumiy schemas — barcha feature lar tomonidan ishlatiladi."""
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    """Standart xato javobi formati."""
    detail: str
    code: str | None = None


class PaginationParams(BaseModel):
    """Pagination uchun query parametrlar."""
    page: int = Field(default=1, ge=1, description="Sahifa raqami")
    page_size: int = Field(default=20, ge=1, le=100, description="Bir sahifadagi elementlar")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response.

    Misol:
        PaginatedResponse[DocumentResponse]
    """
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
