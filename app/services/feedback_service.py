import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Any
from app.core.config import settings
from app.core.logging import logger
from app.models.schemas import FeedbackRequest


class FeedbackService:
    """Manages user feedback storage and retrieval in SQLite."""

    def __init__(self):
        self.db_path = settings.get_abs_path(settings.FEEDBACK_DB_DIR)
        self._init_db()

    def _init_db(self):
        """Creates feedback table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    rating TEXT NOT NULL,
                    comment TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.commit()

    def record_feedback(self, feedback: FeedbackRequest) -> str:
        """Saves user feedback and returns generated feedback_id."""
        feedback_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO feedback (id, question, answer, rating, comment, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (feedback_id, feedback.question, feedback.answer, feedback.rating, feedback.comment, timestamp),
            )
            conn.commit()

        logger.info(f"Recorded feedback {feedback_id} with rating '{feedback.rating}'")
        return feedback_id

    def get_feedback_counts(self) -> Dict[str, int]:
        """Returns positive and negative feedback counts."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT rating, COUNT(*) FROM feedback GROUP BY rating")
            results = dict(cursor.fetchall())
            return {
                "positive": results.get("up", 0),
                "negative": results.get("down", 0),
            }


feedback_service = FeedbackService()
