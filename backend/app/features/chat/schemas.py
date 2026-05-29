"""Chat schemas"""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class MessageRole(str, Enum):
    """Xabar roli — kim yozgan."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageBase(BaseModel):
    role: MessageRole
    content: str = Field(..., min_length=1, max_length=10000)


class MessageCreate(BaseModel):
    """Yangi xabar yuborish uchun."""
    content: str = Field(..., min_length=1, max_length=10000)
    document_ids: list[int] | None = Field(
        None,
        description="Faqat shu hujjatlardan kontekst olish (None — hammasidan)",
    )


class SourceCitation(BaseModel):
    """Javob qaysi hujjatdan olinganligi."""
    document_id: int
    document_title: str
    chunk_id: int
    content_preview: str = Field(..., max_length=200)
    page_number: int | None = None
    relevance_score: float = Field(..., ge=0, le=1)


class MessageResponse(MessageBase):
    """Xabar API javobi."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: int
    sources: list["SourceCitation"] | None = None  # qaysi hujjatdan olingan
    created_at: datetime


class ChatBase(BaseModel):
    title: str = Field(default="Yangi suhbat", max_length=200)


class ChatCreate(ChatBase):
    pass


class ChatResponse(ChatBase):
    """Chat API javobi (xabarlarsiz)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    message_count: int = 0
    last_message_at: datetime | None = None
    created_at: datetime


class ChatDetailResponse(ChatResponse):
    """Chat to'liq xabarlar bilan."""
    messages: list[MessageResponse] = Field(default_factory=list)


# Forward reference uchun
MessageResponse.model_rebuild()
