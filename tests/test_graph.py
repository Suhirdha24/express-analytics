import pytest
from app.graph.state import DocuMindState
from app.graph.workflow import route_after_grading, run_documind_workflow
from app.graph.nodes.fallback import fallback_node
from app.graph.nodes.confidence import confidence_node


def test_conditional_router_with_relevant_docs():
    state: DocuMindState = {
        "question": "How to use Depends?",
        "relevant_documents": [{"chunk_id": "c1", "content": "Depends in FastAPI"}],
        "retry_count": 0,
        "max_retries": 2,
    }
    next_node = route_after_grading(state)
    assert next_node == "ANSWER_GENERATION"


def test_conditional_router_retry():
    state: DocuMindState = {
        "question": "Unrelated topic",
        "relevant_documents": [],
        "retry_count": 0,
        "max_retries": 2,
    }
    next_node = route_after_grading(state)
    assert next_node == "QUERY_REWRITER"


def test_conditional_router_max_retries_exceeded():
    state: DocuMindState = {
        "question": "Unrelated topic",
        "relevant_documents": [],
        "retry_count": 2,
        "max_retries": 2,
    }
    next_node = route_after_grading(state)
    assert next_node == "INSUFFICIENT_EVIDENCE_RESPONSE"


def test_fallback_node():
    initial_state: DocuMindState = {
        "question": "Unknown concept",
        "workflow_trace": [],
    }
    new_state = fallback_node(initial_state)

    assert new_state["status"] == "insufficient_evidence"
    assert "could not find enough reliable information" in new_state["generated_answer"]
    assert "INSUFFICIENT_EVIDENCE_RESPONSE" in new_state["workflow_trace"]


def test_confidence_score_formula():
    state: DocuMindState = {
        "retrieval_quality": 0.8,
        "relevance_quality": 0.9,
        "groundedness_score": 1.0,
        "workflow_trace": [],
    }
    res = confidence_node(state)

    # 0.40 * 0.8 + 0.35 * 0.9 + 0.25 * 1.0 = 0.32 + 0.315 + 0.25 = 0.885 -> 88.5%
    assert res["confidence_score"] == 88.5
    assert res["status"] == "success"


def test_full_workflow_execution():
    res = run_documind_workflow("How does dependency injection work in FastAPI?")
    assert res.status in ["success", "insufficient_evidence"]
    assert isinstance(res.workflow_trace, list)
    assert len(res.workflow_trace) > 0
