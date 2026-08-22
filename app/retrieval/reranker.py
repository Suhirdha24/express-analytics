from typing import List, Dict, Any


class ReciprocalRankFusionReranker:
    """Combines and reranks dense and sparse search results using Reciprocal Rank Fusion (RRF)."""

    @staticmethod
    def combine_results(
        vector_results: List[Dict[str, Any]],
        bm25_results: List[Dict[str, Any]],
        top_k: int = 5,
        rrf_k: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Merges, deduplicates, and ranks document chunks using RRF scoring.
        RRF Score = 1 / (rrf_k + rank_dense) + 1 / (rrf_k + rank_sparse)
        """
        chunk_map: Dict[str, Dict[str, Any]] = {}
        scores: Dict[str, float] = {}

        # Process dense vector search results
        for rank, doc in enumerate(vector_results):
            cid = doc["chunk_id"]
            chunk_map[cid] = doc
            scores[cid] = scores.get(cid, 0.0) + (1.0 / (rrf_k + rank + 1))

        # Process sparse BM25 search results
        for rank, doc in enumerate(bm25_results):
            cid = doc["chunk_id"]
            if cid not in chunk_map:
                chunk_map[cid] = doc
            scores[cid] = scores.get(cid, 0.0) + (1.0 / (rrf_k + rank + 1))

        # Sort chunk IDs by RRF score descending
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

        reranked_chunks = []
        max_rrf = scores[sorted_ids[0]] if sorted_ids else 1.0

        for cid in sorted_ids[:top_k]:
            chunk = dict(chunk_map[cid])
            # Normalize RRF score to 0.0 - 1.0 range
            chunk["score"] = float(scores[cid] / max_rrf)
            chunk["search_type"] = "hybrid_rrf"
            reranked_chunks.append(chunk)

        return reranked_chunks
