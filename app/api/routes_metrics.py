from fastapi import APIRouter
from app.models.schemas import MetricsResponse
from app.services.metrics_service import metrics_service

router = APIRouter(prefix="/metrics", tags=["Analytics & Performance"])


@router.get("", response_model=MetricsResponse, summary="Get application execution metrics")
def get_metrics() -> MetricsResponse:
    """Returns application query analytics, average confidence, retry stats, and feedback breakdown."""
    return metrics_service.get_metrics()
