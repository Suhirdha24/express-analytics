from fastapi import APIRouter, HTTPException, status
from app.models.schemas import FeedbackRequest, FeedbackResponse
from app.services.feedback_service import feedback_service
from app.core.logging import logger

router = APIRouter(prefix="/feedback", tags=["Feedback Management"])


@router.post("", response_model=FeedbackResponse, summary="Submit user feedback")
def submit_feedback(req: FeedbackRequest) -> FeedbackResponse:
    """Submits user feedback (thumbs up / down and optional comment) for quality tracking."""
    try:
        feedback_id = feedback_service.record_feedback(req)
        return FeedbackResponse(
            status="success",
            feedback_id=feedback_id,
            message="Feedback recorded successfully."
        )
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record feedback."
        )
