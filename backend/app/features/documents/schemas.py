"""Document schemas"""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, computed_field


class DocumentStatus(str, Enum):
    """Hujjat indekslash holati."""
    PENDING = "pending"          # Yuklandi, kutilmoqda
    PROCESSING = "processing"     # Indekslanmoqda
    INDEXED = "indexed"           # Tayyor
    FAILED = "failed"             # Xato bo'ldi


class DocumentBase(BaseModel):
    filename: str = Field(..., max_length=255)
    file_size: int = Field(..., gt=0, description="Bayt'larda")
    content_type: str


class DocumentResponse(DocumentBase):
    """Document API javobi."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: DocumentStatus
    error_message: str | None = None
    page_count: int | None = None
    chunk_count: int | None = None
    created_at: datetime
    indexed_at: datetime | None = None

    @computed_field
    @property
    def file_size_mb(self) -> float:
        """Hisoblangan maydon — MB hisobida hajm."""
        return round(self.file_size / (1024 * 1024), 2)

    @computed_field
    @property
    def is_ready(self) -> bool:
        """Hujjat ishlatishga tayyor mi?"""
        return self.status == DocumentStatus.INDEXED


class DocumentListResponse(BaseModel):
    """Hujjatlar ro'yxati pagination bilan."""
    items: list[DocumentResponse]
    total: int
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=100)

    @computed_field
    @property
    def total_pages(self) -> int:
        return (self.total + self.page_size - 1) // self.page_size


class DocumentUploadResponse(BaseModel):
    """Upload muvaffaqiyatli bo'lganda javob."""
    document_id: int
    filename: str
    status: DocumentStatus
    message: str = "Hujjat qabul qilindi, indekslash boshlandi"
