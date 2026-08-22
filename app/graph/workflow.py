from langgraph.graph import StateGraph, END, START
from app.core.config import settings
from app.graph.state import DocuMindState
from app.graph.nodes.query_analysis import query_analysis_node
from app.graph.nodes.hybrid_retrieval import hybrid_retrieval_node
from app.graph.nodes.document_grading import document_grading_node
from app.graph.nodes.query_rewriter import query_rewriter_node
from app.graph.nodes.answer_generation import answer_generation_node
from app.graph.nodes.answer_validation import answer_validation_node
from app.graph.nodes.confidence import confidence_node
from app.graph.nodes.fallback import fallback_node
from app.models.schemas import QueryResponse


def route_after_grading(state: DocuMindState) -> str:
    """Conditional router routing to Answer Generation, Query Rewriter, or Fallback."""
    relevant_docs = state.get("relevant_documents", [])
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", settings.MAX_RETRIES)

    if len(relevant_docs) > 0:
        return "ANSWER_GENERATION"
    elif retry_count < max_retries:
        return "QUERY_REWRITER"
    else:
        return "INSUFFICIENT_EVIDENCE_RESPONSE"


def build_workflow():
    """Constructs and compiles the self-correcting DocuMind RAG graph."""
    graph_builder = StateGraph(DocuMindState)

    # Add workflow nodes
    graph_builder.add_node("QUERY_ANALYSIS", query_analysis_node)
    graph_builder.add_node("HYBRID_RETRIEVAL", hybrid_retrieval_node)
    graph_builder.add_node("DOCUMENT_GRADING", document_grading_node)
    graph_builder.add_node("QUERY_REWRITER", query_rewriter_node)
    graph_builder.add_node("ANSWER_GENERATION", answer_generation_node)
    graph_builder.add_node("ANSWER_VALIDATION", answer_validation_node)
    graph_builder.add_node("CONFIDENCE_SCORE", confidence_node)
    graph_builder.add_node("INSUFFICIENT_EVIDENCE_RESPONSE", fallback_node)

    # Connect fixed edges
    graph_builder.add_edge(START, "QUERY_ANALYSIS")
    graph_builder.add_edge("QUERY_ANALYSIS", "HYBRID_RETRIEVAL")
    graph_builder.add_edge("HYBRID_RETRIEVAL", "DOCUMENT_GRADING")

    # Connect conditional routing edge
    graph_builder.add_conditional_edges(
        "DOCUMENT_GRADING",
        route_after_grading,
        {
            "ANSWER_GENERATION": "ANSWER_GENERATION",
            "QUERY_REWRITER": "QUERY_REWRITER",
            "INSUFFICIENT_EVIDENCE_RESPONSE": "INSUFFICIENT_EVIDENCE_RESPONSE",
        },
    )

    graph_builder.add_edge("QUERY_REWRITER", "HYBRID_RETRIEVAL")
    graph_builder.add_edge("ANSWER_GENERATION", "ANSWER_VALIDATION")
    graph_builder.add_edge("ANSWER_VALIDATION", "CONFIDENCE_SCORE")
    graph_builder.add_edge("CONFIDENCE_SCORE", END)
    graph_builder.add_edge("INSUFFICIENT_EVIDENCE_RESPONSE", END)

    return graph_builder.compile()


compiled_app = build_workflow()


def run_documind_workflow(question: str, max_retries: int = None) -> QueryResponse:
    """Executes the full self-correcting workflow for a given user question."""
    initial_state: DocuMindState = {
        "question": question,
        "optimized_query": question,
        "query_type": "conceptual",
        "technical_keywords": [],
        "is_ambiguous": False,
        "retrieved_documents": [],
        "graded_documents": [],
        "relevant_documents": [],
        "retry_count": 0,
        "max_retries": max_retries or settings.MAX_RETRIES,
        "generated_answer": "",
        "citations": [],
        "retrieval_quality": 0.0,
        "relevance_quality": 0.0,
        "groundedness_score": 0.0,
        "confidence_score": 0.0,
        "workflow_trace": [],
        "status": "success",
        "error_message": None,
    }

    final_state = compiled_app.invoke(initial_state)

    return QueryResponse(
        answer=final_state.get("generated_answer", ""),
        citations=final_state.get("citations", []),
        confidence_score=final_state.get("confidence_score", 0.0),
        query_type=final_state.get("query_type", "conceptual"),
        retry_count=final_state.get("retry_count", 0),
        workflow_trace=final_state.get("workflow_trace", []),
        status=final_state.get("status", "success"),
        error_message=final_state.get("error_message"),
    )
