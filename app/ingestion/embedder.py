from typing import List
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.core.logging import logger


class EmbeddingService:
    """Provides local embeddings using sentence-transformers/all-MiniLM-L6-v2."""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generates embedding vectors for a batch of text chunks."""
        if not texts:
            return []
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """Generates an embedding vector for a single query string."""
        embedding = self.model.encode([query], convert_to_numpy=True, show_progress_bar=False)[0]
        return embedding.tolist()


embedding_service = EmbeddingService()
