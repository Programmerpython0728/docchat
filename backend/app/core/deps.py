"""Umumiy dependencies — DI containers."""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.auth.repository import UserRepository
from app.features.auth.service import AuthService
from app.features.chat.repository import ChatRepository, MessageRepository
from app.features.documents.repository import (
    DocumentChunkRepository,
    DocumentRepository,
)


def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
) -> AuthService:
    return AuthService(user_repo)


def get_chat_repo(db: AsyncSession = Depends(get_db)) -> ChatRepository:
    return ChatRepository(db)


def get_message_repo(db: AsyncSession = Depends(get_db)) -> MessageRepository:
    return MessageRepository(db)


def get_document_repo(db: AsyncSession = Depends(get_db)) -> DocumentRepository:
    return DocumentRepository(db)


def get_chunk_repo(db: AsyncSession = Depends(get_db)) -> DocumentChunkRepository:
    return DocumentChunkRepository(db)
