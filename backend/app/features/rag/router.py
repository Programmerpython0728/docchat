"""RAG endpoints"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.auth.dependencies import get_current_active_user
from app.features.auth.schemas import UserResponse
from app.features.rag.embedding_service import EmbeddingService
from app.features.rag.search_repository import VectorSearchRepository
from app.features.rag.service import RAGService

router = APIRouter()


@router.get("/search", summary="Semantic search")
async def search(
    q: str = Query(..., description="Qidiruv so'rovi"),
    top_k: int = Query(5, ge=1, le=20),
    hybrid: bool = Query(False, description="Hybrid (vector + BM25) ishlatish"),
    user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Test: semantic / hybrid search."""
    rag = RAGService(db)
    if hybrid:
        results = await rag.retrieve_hybrid(q, user.id, top_k)
    else:
        results = await rag.retrieve(q, user.id, top_k)

    return {
        "query": q,
        "mode": "hybrid" if hybrid else "vector",
        "results": [
            {
                "chunk_id": r["chunk_id"],
                "document_id": r["document_id"],
                "preview": r["content"][:200],
                "score": r.get("similarity", r.get("rrf_score")),
            }
            for r in results
        ],
    }
