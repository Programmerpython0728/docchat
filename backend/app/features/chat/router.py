"""Chat endpoints"""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, status

from app.core.exceptions import ChatNotFoundError
from app.features.auth.dependencies import get_current_active_user
from app.features.auth.schemas import UserResponse
from app.features.chat.schemas import (
    ChatCreate,
    ChatDetailResponse,
    ChatResponse,
    MessageCreate,
    MessageResponse,
    MessageRole,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yangi suhbat yaratish",
)
async def create_chat(
    chat_in: ChatCreate,
    user: UserResponse = Depends(get_current_active_user),
) -> ChatResponse:
    """Yangi suhbat yaratish."""
    logger.info(f"Yangi suhbat: {chat_in.title} (user={user.id})")

    # TODO 4-6 kun: real DB save
    return ChatResponse(
        id=1,
        user_id=user.id,
        title=chat_in.title,
        message_count=0,
        last_message_at=None,
        created_at=datetime.now(),
    )


@router.get(
    "/",
    response_model=list[ChatResponse],
    summary="Foydalanuvchining suhbatlari ro'yxati",
)
async def list_chats(
    user: UserResponse = Depends(get_current_active_user),
) -> list[ChatResponse]:
    """Joriy foydalanuvchining barcha suhbatlari."""
    # TODO: real DB query
    return [
        ChatResponse(
            id=1,
            user_id=user.id,
            title="Demo suhbat",
            message_count=3,
            last_message_at=datetime.now(),
            created_at=datetime.now(),
        ),
    ]


@router.get(
    "/{chat_id}",
    response_model=ChatDetailResponse,
    summary="Suhbat tafsilotlari",
)
async def get_chat(
    chat_id: int,
    user: UserResponse = Depends(get_current_active_user),
) -> ChatDetailResponse:
    """Bitta suhbat va uning xabarlari."""
    # TODO: real DB query
    if chat_id != 1:
        raise ChatNotFoundError()

    return ChatDetailResponse(
        id=chat_id,
        user_id=user.id,
        title="Demo suhbat",
        message_count=2,
        last_message_at=datetime.now(),
        created_at=datetime.now(),
        messages=[
            MessageResponse(
                id=1,
                chat_id=chat_id,
                role=MessageRole.USER,
                content="Hujjatlar nimadan iborat?",
                created_at=datetime.now(),
            ),
            MessageResponse(
                id=2,
                chat_id=chat_id,
                role=MessageRole.ASSISTANT,
                content="Hujjatlar AI va RAG haqida.",
                created_at=datetime.now(),
            ),
        ],
    )


@router.post(
    "/{chat_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Suhbatga xabar yuborish (mock)",
)
async def send_message(
    chat_id: int,
    message: MessageCreate,
    user: UserResponse = Depends(get_current_active_user),
) -> MessageResponse:
    """
    Suhbatga xabar yuborish.

    **Eslatma**: Hozircha mock javob qaytadi.
    6-kunda WebSocket streaming bilan almashtiriladi.
    """
    logger.info(f"Xabar: chat_id={chat_id}, content_len={len(message.content)}")

    return MessageResponse(
        id=999,
        chat_id=chat_id,
        role=MessageRole.ASSISTANT,
        content=f"Mock javob: '{message.content}' savolingiz qabul qilindi. "
                "Haqiqiy RAG javobi 9-kunda paydo bo'ladi!",
        created_at=datetime.now(),
    )
