from typing import List, Dict, Any
from app.core.config import settings
from app.core.logging import logger
from app.ingestion.vector_store import vector_store
from app.ingestion.bm25_store import bm25_store
from app.retrieval.reranker import ReciprocalRankFusionReranker


class HybridRetriever:
    """Combines vector similarity search (ChromaDB) and keyword search (BM25)."""

    def __init__(self, top_k: int = None):
        self.top_k = top_k or settings.TOP_K_RETRIEVAL

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """Performs hybrid retrieval and returns reranked deduplicated chunks."""
        logger.info(f"Executing hybrid retrieval for query: '{query}'")

        # 1. Vector Search
        vector_chunks = vector_store.similarity_search(query, top_k=self.top_k * 2)

        # 2. BM25 Search
        bm25_chunks = bm25_store.search(query, top_k=self.top_k * 2)

        # 3. Combine & Rerank via RRF
        hybrid_chunks = ReciprocalRankFusionReranker.combine_results(
            vector_results=vector_chunks,
            bm25_results=bm25_chunks,
            top_k=self.top_k
        )

        logger.info(
            f"Hybrid retrieval returned {len(hybrid_chunks)} chunks "
            f"(Dense: {len(vector_chunks)}, Sparse: {len(bm25_chunks)})."
        )
        return hybrid_chunks


hybrid_retriever = HybridRetriever()
