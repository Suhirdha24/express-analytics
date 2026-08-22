import pytest
from app.retrieval.reranker import ReciprocalRankFusionReranker
from app.retrieval.hybrid_retriever import hybrid_retriever


def test_rrf_reranking():
    dense_results = [
        {"chunk_id": "doc1_0", "content": "FastAPI Depends", "title": "DI", "source": "di.md"},
        {"chunk_id": "doc2_0", "content": "FastAPI Path", "title": "Path", "source": "path.md"},
    ]
    bm25_results = [
        {"chunk_id": "doc2_0", "content": "FastAPI Path", "title": "Path", "source": "path.md"},
        {"chunk_id": "doc3_0", "content": "FastAPI Body", "title": "Body", "source": "body.md"},
    ]

    combined = ReciprocalRankFusionReranker.combine_results(
        vector_results=dense_results,
        bm25_results=bm25_results,
        top_k=5
    )

    assert len(combined) == 3
    # doc2_0 appears in both dense and sparse, so it should rank highest or have high score
    assert combined[0]["chunk_id"] == "doc2_0"
    assert combined[0]["search_type"] == "hybrid_rrf"


def test_hybrid_retriever_query():
    results = hybrid_retriever.retrieve("FastAPI dependency injection")
    assert isinstance(results, list)
