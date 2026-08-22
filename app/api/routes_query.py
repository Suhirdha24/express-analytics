from fastapi import APIRouter, HTTPException, status
from app.models.schemas import QueryRequest, QueryResponse
from app.graph.workflow import run_documind_workflow
from app.services.metrics_service import metrics_service
from app.core.logging import logger

router = APIRouter(prefix="/query", tags=["Query Engine"])


@router.post("", response_model=QueryResponse, summary="Query the self-correcting RAG workflow")
def execute_query(req: QueryRequest) -> QueryResponse:
    """
    Submits a technical question to the self-correcting LangGraph workflow.
    Performs query analysis, hybrid retrieval, document grading, self-correction retries,
    grounded answer generation, answer validation, and confidence scoring.
    """
    if not req.question or not req.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question string cannot be empty."
        )

    try:
        response = run_documind_workflow(question=req.question.strip())
        metrics_service.record_query(
            status=response.status,
            confidence_score=response.confidence_score,
            retry_count=response.retry_count
        )
        return response
    except Exception as e:
        logger.error(f"Error handling query request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred while processing the query."
        )
