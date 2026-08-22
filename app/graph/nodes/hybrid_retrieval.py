from app.graph.state import DocuMindState
from app.retrieval.hybrid_retriever import hybrid_retriever
from app.core.logging import logger


def hybrid_retrieval_node(state: DocuMindState) -> DocuMindState:
    """Executes hybrid retrieval combining dense vector similarity and BM25 sparse search."""
    logger.info("Executing HYBRID_RETRIEVAL node...")
    query = state.get("optimized_query") or state["question"]
    trace = list(state.get("workflow_trace", []))
    trace.append("HYBRID_RETRIEVAL")

    retrieved = hybrid_retriever.retrieve(query)

    # Calculate retrieval quality as average top score
    retrieval_quality = 0.0
    if retrieved:
        retrieval_quality = sum(doc.get("score", 0.0) for doc in retrieved) / len(retrieved)

    return {
        **state,
        "retrieved_documents": retrieved,
        "retrieval_quality": float(retrieval_quality),
        "workflow_trace": trace,
    }
