from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.ingestion.vector_store import vector_store
from app.ingestion.bm25_store import bm25_store

router = APIRouter(prefix="/health", tags=["Health & Readiness"])


@router.get("", response_model=HealthResponse, summary="Get system health status")
def check_health() -> HealthResponse:
    """Returns application health, vector database status, and indexed document counts."""
    doc_count = vector_store.get_indexed_document_count()
    vector_status = "available" if vector_store.collection else "unavailable"
    bm25_status = "available" if bm25_store else "unavailable"

    return HealthResponse(
        status="healthy",
        vector_store=vector_status,
        indexed_documents=doc_count,
        bm25_index=bm25_status,
    )
