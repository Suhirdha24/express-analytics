from app.graph.state import DocuMindState
from app.core.logging import logger


def confidence_node(state: DocuMindState) -> DocuMindState:
    """Calculates composite system confidence score normalized to 0 - 100."""
    logger.info("Executing CONFIDENCE_SCORE node...")
    retrieval_quality = state.get("retrieval_quality", 0.0)
    relevance_quality = state.get("relevance_quality", 0.0)
    groundedness_score = state.get("groundedness_score", 0.0)
    trace = list(state.get("workflow_trace", []))
    trace.append("CONFIDENCE_SCORE")

    # Formula: 0.40 * retrieval_quality + 0.35 * relevance_quality + 0.25 * groundedness_score
    raw_confidence = (
        0.40 * retrieval_quality +
        0.35 * relevance_quality +
        0.25 * groundedness_score
    )

    # Normalize to 0 - 100
    confidence_score = round(min(max(raw_confidence * 100.0, 0.0), 100.0), 2)

    logger.info(f"Final confidence score calculated: {confidence_score:.2f}%")

    return {
        **state,
        "confidence_score": float(confidence_score),
        "status": "success",
        "workflow_trace": trace,
    }
