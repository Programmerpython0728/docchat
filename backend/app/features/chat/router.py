"""Chat endpoints"""
import asyncio
import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from jose import JWTError

from app.core.database import get_db_context
from app.core.exceptions import ChatNotFoundError
from app.core.security import decode_token
from app.features.auth.dependencies import get_current_active_user
from app.features.auth.schemas import UserResponse
from app.features.chat.connection_manager import manager
from app.features.chat.repository import MessageRepository
from app.features.chat.schemas import (
    ChatCreate,
    ChatDetailResponse,
    ChatResponse,
    MessageCreate,
    MessageResponse,
    MessageRole,
)
from app.features.rag.service import RAGService

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


# ============================================================
# WebSocket — real-time chat streaming
# ============================================================
@router.websocket("/ws")
async def chat_websocket(
    websocket: WebSocket,
    token: str = Query(...),  # WS da header qiyin, query orqali token
):
    """
    Real-time chat WebSocket.

    Ulanish: ws://localhost:8000/api/v1/chat/ws?token=<jwt>

    Protokol:
    - Client yuboradi: {"type": "message", "content": "savol"}
    - Server yuboradi: {"type": "token", "content": "so'z"}
    - Tugaganda: {"type": "done"}
    """
    # Token tekshirish (WS da Depends ishlamaydi, qo'lda)
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise JWTError("Access token kerak")
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        await websocket.close(code=4001, reason="Invalid token")
        return

    await manager.connect(websocket, user_id)

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") != "message":
                continue

            prompt = data.get("content", "")
            chat_id = data.get("chat_id")
            document_ids = data.get("document_ids")
            use_hybrid = data.get("hybrid", False)
            logger.info(f"WS message: user={user_id}, len={len(prompt)}, hybrid={use_hybrid}")

            llm_task = asyncio.create_task(
                _stream_rag_response(
                    websocket, prompt, user_id, chat_id, document_ids, use_hybrid
                )
            )

            try:
                await llm_task
            except WebSocketDisconnect:
                llm_task.cancel()
                raise

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"User {user_id} disconnected")


async def _stream_rag_response(
    websocket: WebSocket,
    prompt: str,
    user_id: int,
    chat_id: int | None,
    document_ids: list[int] | None,
    use_hybrid: bool = False,
):
    """To'liq RAG streaming + DB ga saqlash."""
    full_response = ""
    sources_data = None

    async with get_db_context() as db:
        rag = RAGService(db)
        async for event in rag.generate_stream(
            query=prompt,
            user_id=user_id,
            document_ids=document_ids,
            use_hybrid=use_hybrid,
        ):
            await websocket.send_json(event)
            if event["type"] == "token":
                full_response += event["content"]
            elif event["type"] == "sources":
                sources_data = event["sources"]

    # DB ga saqlash (chat_id bo'lsa)
    if chat_id:
        async with get_db_context() as db:
            msg_repo = MessageRepository(db)
            await msg_repo.create(
                chat_id=chat_id, role=MessageRole.USER, content=prompt,
            )
            await msg_repo.create(
                chat_id=chat_id,
                role=MessageRole.ASSISTANT,
                content=full_response,
                sources=json.dumps(sources_data) if sources_data else None,
            )
            await db.commit()
