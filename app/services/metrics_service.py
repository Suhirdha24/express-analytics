import threading
from typing import Dict, Any
from app.services.feedback_service import feedback_service
from app.models.schemas import MetricsResponse


class MetricsService:
    """Thread-safe analytics and execution metrics collector."""

    def __init__(self):
        self._lock = threading.Lock()
        self.total_queries = 0
        self.successful_queries = 0
        self.insufficient_evidence_queries = 0
        self.total_confidence = 0.0
        self.total_retries = 0

    def record_query(self, status: str, confidence_score: float, retry_count: int):
        """Records query execution results."""
        with self._lock:
            self.total_queries += 1
            if status == "success":
                self.successful_queries += 1
            elif status == "insufficient_evidence":
                self.insufficient_evidence_queries += 1

            self.total_confidence += confidence_score
            self.total_retries += retry_count

    def get_metrics(self) -> MetricsResponse:
        """Computes aggregate application performance metrics."""
        with self._lock:
            avg_confidence = (
                self.total_confidence / self.total_queries if self.total_queries > 0 else 0.0
            )
            avg_retries = (
                self.total_retries / self.total_queries if self.total_queries > 0 else 0.0
            )

        fb_stats = feedback_service.get_feedback_counts()

        return MetricsResponse(
            total_queries=self.total_queries,
            successful_queries=self.successful_queries,
            insufficient_evidence_queries=self.insufficient_evidence_queries,
            average_confidence=round(avg_confidence, 2),
            average_retries=round(avg_retries, 2),
            positive_feedback=fb_stats["positive"],
            negative_feedback=fb_stats["negative"],
        )


metrics_service = MetricsService()
