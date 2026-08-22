from typing import TypedDict, List, Dict, Any, Optional


class DocuMindState(TypedDict):
    """LangGraph execution state dictionary."""
    question: str
    optimized_query: str
    query_type: str  # conceptual, how_to, troubleshooting, api_reference
    technical_keywords: List[str]
    is_ambiguous: bool
    retrieved_documents: List[Dict[str, Any]]
    graded_documents: List[Dict[str, Any]]
    relevant_documents: List[Dict[str, Any]]
    retry_count: int
    max_retries: int
    generated_answer: str
    citations: List[str]
    retrieval_quality: float
    relevance_quality: float
    groundedness_score: float
    confidence_score: float
    workflow_trace: List[str]
    status: str  # success, insufficient_evidence, error
    error_message: Optional[str]
