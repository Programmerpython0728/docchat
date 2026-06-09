"""Chat va Message repositories"""
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.core.repository import BaseRepository
from app.features.chat.models import Chat, Message


class ChatRepository(BaseRepository[Chat]):
    model = Chat

    async def get_by_user(
        self, user_id: int, *, skip: int = 0, limit: int = 50
    ) -> list[Chat]:
        """Foydalanuvchining chatlari."""
        stmt = (
            select(Chat)
            .where(Chat.user_id == user_id)
            .order_by(Chat.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_user_chat_with_messages(
        self, chat_id: int, user_id: int
    ) -> Chat | None:
        """Chat va xabarlari (eager load)."""
        stmt = (
            select(Chat)
            .where(Chat.id == chat_id, Chat.user_id == user_id)
            .options(selectinload(Chat.messages))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_message_count(self, chat_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(Message)
            .where(Message.chat_id == chat_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()


class MessageRepository(BaseRepository[Message]):
    model = Message

    async def get_by_chat(self, chat_id: int) -> list[Message]:
        """Chatdagi xabarlar."""
        stmt = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
