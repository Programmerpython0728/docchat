"""Document endpoints"""
import logging
import os
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.arq_pool import get_arq_pool
from app.core.config import get_settings
from app.core.database import get_db
from app.core.deps import get_document_repo
from app.core.exceptions import (
    DocumentNotFoundError,
    FileTooLargeError,
    UnsupportedFileTypeError,
)
from app.features.auth.dependencies import get_current_active_user
from app.features.auth.schemas import UserResponse
from app.features.documents.repository import DocumentRepository
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
    doc_repo: DocumentRepository = Depends(get_document_repo),
    db: AsyncSession = Depends(get_db),
) -> DocumentUploadResponse:
    """
    Hujjat yuklash + background indexing.

    Qo'llab-quvvatlanadi: PDF, DOCX, TXT, MD.
    Max hajm: settings da belgilangan (default 50MB).

    Hujjat indekslash background'da (arq worker) boshlanadi —
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

    # Faylni o'qish va hajmni tekshirish
    content = await file.read()
    if len(content) > settings.upload_max_size_mb * 1024 * 1024:
        raise FileTooLargeError(
            f"Fayl hajmi {settings.upload_max_size_mb}MB dan oshmasligi kerak"
        )

    # Faylni diskka saqlash
    os.makedirs(settings.upload_dir, exist_ok=True)
    file_path = os.path.join(settings.upload_dir, f"{user.id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(content)

    # DB ga yozish
    doc = await doc_repo.create(
        user_id=user.id,
        filename=file.filename or "noma'lum",
        file_path=file_path,
        file_size=len(content),
        content_type=file.content_type or "application/octet-stream",
        status=DocumentStatus.PENDING,
    )
    await db.commit()

    logger.info(f"Hujjat yuklandi: id={doc.id}, {file.filename} ({len(content)} bayt) user={user.id}")

    # Background indexing enqueue
    arq = await get_arq_pool()
    await arq.enqueue_job("index_document", doc.id)

    return DocumentUploadResponse(
        document_id=doc.id,
        filename=doc.filename,
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
    doc_repo: DocumentRepository = Depends(get_document_repo),
) -> DocumentListResponse:
    """Real DB query."""
    skip = (page - 1) * page_size

    documents = await doc_repo.get_by_user(
        user_id=user.id,
        skip=skip,
        limit=page_size,
        status=status_filter,
    )

    total = await doc_repo.count_by_user(
        user_id=user.id, status=status_filter
    )

    return DocumentListResponse(
        items=[DocumentResponse.model_validate(d) for d in documents],
        total=total,
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
    doc_repo: DocumentRepository = Depends(get_document_repo),
) -> DocumentResponse:
    """Bitta hujjat haqida ma'lumot (real DB)."""
    doc = await doc_repo.get_user_document(document_id, user.id)
    if not doc:
        raise DocumentNotFoundError()
    return DocumentResponse.model_validate(doc)


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

list1=[1,2,3,4,5,6,7,8,9]
list_cop=[]
for i in list1:
    if i %2==0:
        list_cop.append(i)
