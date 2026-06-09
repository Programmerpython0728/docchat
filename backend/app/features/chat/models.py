"""Chat va Message models"""
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.db_mixins import IDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.features.auth.models import User


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Chat(Base, IDMixin, TimestampMixin):
    __tablename__ = "chats"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    title: Mapped[str] = mapped_column(
        String(200), default="Yangi suhbat", nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="chats", lazy="raise")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
        lazy="raise",
    )

    def __repr__(self) -> str:
        return f"<Chat(id={self.id}, title={self.title!r})>"


class Message(Base, IDMixin, TimestampMixin):
    __tablename__ = "messages"

    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    role: Mapped[MessageRole] = mapped_column(
        SQLEnum(MessageRole, name="message_role"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sources: Mapped[str | None] = mapped_column(Text, nullable=True)

    chat: Mapped["Chat"] = relationship(back_populates="messages", lazy="raise")

    __table_args__ = (
        Index("ix_messages_chat_created", "chat_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role})>"
