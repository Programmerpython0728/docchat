"""Document endpoints"""
import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from app.core.config import get_settings
from app.core.exceptions import (
    DocumentNotFoundError,
    FileTooLargeError,
    UnsupportedFileTypeError,
)
from app.features.auth.dependencies import get_current_active_user
from app.features.auth.schemas import UserResponse
from app.features.documents.schemas import (
    DocumentListResponse,
    DocumentResponse,
    DocumentStatus,
    DocumentUploadResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Hujjat yuklash",
)
async def upload_document(
    file: UploadFile = File(...),
    user: UserResponse = Depends(get_current_active_user),
) -> DocumentUploadResponse:
    """
    Hujjat yuklash va indekslashni boshlash.

    Qo'llab-quvvatlanadi: PDF, DOCX, TXT, MD.
    Max hajm: settings da belgilangan (default 50MB).

    Hujjat indekslash background da boshlanadi —
    foydalanuvchi natijani kutmasdan davom etishi mumkin.
    """
    settings = get_settings()

    # Fayl turini tekshirish
    ext = Path(file.filename or "").suffix.lower()
    if ext not in settings.allowed_extensions:
        raise UnsupportedFileTypeError(
            f"'{ext}' qo'llab-quvvatlanmaydi. "
            f"Ruxsat etilgan: {', '.join(settings.allowed_extensions)}"
        )

    # Fayl hajmini tekshirish
    # UploadFile.size 0.106+ versiyada bor
    if file.size and file.size > settings.upload_max_size_mb * 1024 * 1024:
        raise FileTooLargeError(
            f"Fayl hajmi {settings.upload_max_size_mb}MB dan oshmasligi kerak"
        )

    logger.info(f"Hujjat yuklandi: {file.filename} ({file.size} bayt) by user={user.id}")

    # TODO 6-kun: real upload + background indexing
    return DocumentUploadResponse(
        document_id=1,
        filename=file.filename or "noma'lum",
        status=DocumentStatus.PENDING,
    )


@router.get(
    "/",
    response_model=DocumentListResponse,
    summary="Hujjatlar ro'yxati",
)
async def list_documents(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: DocumentStatus | None = Query(default=None, alias="status"),
    user: UserResponse = Depends(get_current_active_user),
) -> DocumentListResponse:
    """Foydalanuvchining hujjatlari pagination bilan."""
    # TODO 4-kun: real DB query
    mock_doc = DocumentResponse(
        id=1,
        user_id=user.id,
        filename="example.pdf",
        file_size=1024 * 500,  # 500 KB
        content_type="application/pdf",
        status=DocumentStatus.INDEXED,
        page_count=10,
        chunk_count=25,
        created_at=datetime.now(),
        indexed_at=datetime.now(),
    )

    return DocumentListResponse(
        items=[mock_doc],
        total=1,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Hujjat tafsilotlari",
)
async def get_document(
    document_id: int,
    user: UserResponse = Depends(get_current_active_user),
) -> DocumentResponse:
    """Bitta hujjat haqida ma'lumot."""
    # TODO: real DB
    if document_id != 1:
        raise DocumentNotFoundError()

    return DocumentResponse(
        id=document_id,
        user_id=user.id,
        filename="example.pdf",
        file_size=1024 * 500,
        content_type="application/pdf",
        status=DocumentStatus.INDEXED,
        page_count=10,
        chunk_count=25,
        created_at=datetime.now(),
        indexed_at=datetime.now(),
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hujjatni o'chirish",
)
async def delete_document(
    document_id: int,
    user: UserResponse = Depends(get_current_active_user),
) -> None:
    """Hujjat va uning chunklarini o'chirish."""
    logger.info(f"O'chirilmoqda: document_id={document_id}, user={user.id}")
    # TODO: real DB delete + vector chunks
    return None
