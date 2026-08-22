from app.graph.state import DocuMindState
from app.core.logging import logger


def fallback_node(state: DocuMindState) -> DocuMindState:
    """Generates standard fallback response when insufficient evidence is retrieved after retries."""
    logger.info("Executing INSUFFICIENT_EVIDENCE_RESPONSE node...")
    trace = list(state.get("workflow_trace", []))
    trace.append("INSUFFICIENT_EVIDENCE_RESPONSE")

    fallback_answer = (
        "I could not find enough reliable information in the indexed documentation to answer this confidently."
    )

    return {
        **state,
        "generated_answer": fallback_answer,
        "citations": [],
        "confidence_score": 0.0,
        "status": "insufficient_evidence",
        "workflow_trace": trace,
    }
