from typing import Dict, List
from fastapi import APIRouter
from app.models.schemas import DocumentListResponse, DocumentMetadata
from app.ingestion.vector_store import vector_store

router = APIRouter(prefix="/documents", tags=["Document Registry"])


@router.get("", response_model=DocumentListResponse, summary="List all indexed documents")
def list_documents() -> DocumentListResponse:
    """Retrieves a list of all indexed technical documentation files and chunk metrics."""
    metadatas = vector_store.get_all_chunk_metadata()

    doc_map: Dict[str, Dict] = {}

    for meta in metadatas:
        doc_id = meta.get("document_id")
        if not doc_id:
            continue

        if doc_id not in doc_map:
            doc_map[doc_id] = {
                "document_id": doc_id,
                "title": meta.get("title", "Untitled Document"),
                "source": meta.get("source", "Unknown"),
                "total_chunks": 0,
                "ingestion_timestamp": meta.get("ingestion_timestamp", ""),
            }

        doc_map[doc_id]["total_chunks"] += 1

    docs_list = [DocumentMetadata(**item) for item in doc_map.values()]

    return DocumentListResponse(
        documents=docs_list,
        total_count=len(docs_list)
    )
