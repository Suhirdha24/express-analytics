from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# --- API Models ---

class QueryRequest(BaseModel):
    question: str = Field(..., description="User technical question", min_length=2)
    session_id: Optional[str] = Field(None, description="Optional session tracking ID")


class QueryResponse(BaseModel):
    answer: str = Field(..., description="Generated answer or fallback explanation")
    citations: List[str] = Field(default_factory=list, description="Inline citations referenced")
    confidence_score: float = Field(..., description="Overall confidence score (0-100)")
    query_type: str = Field(..., description="Classified intent (conceptual, how_to, troubleshooting, api_reference)")
    retry_count: int = Field(..., description="Number of query expansion retries executed")
    workflow_trace: List[str] = Field(..., description="Chronological node execution trace")
    status: str = Field(..., description="Execution status (success, insufficient_evidence, error)")
    error_message: Optional[str] = Field(None, description="Error message if status is error")


class URLIngestRequest(BaseModel):
    url: str = Field(..., description="URL to scrape and ingest")
    title: Optional[str] = Field(None, description="Optional document title override")


class IngestResponse(BaseModel):
    status: str = Field(..., description="Ingestion status (success, duplicate, error)")
    document_id: str = Field(..., description="Unique document ID (SHA256 hash)")
    chunks_created: int = Field(..., description="Number of text chunks created and embedded")
    message: str = Field(..., description="Human-readable result summary")


class DocumentMetadata(BaseModel):
    document_id: str
    title: str
    source: str
    total_chunks: int
    ingestion_timestamp: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentMetadata]
    total_count: int


class FeedbackRequest(BaseModel):
    question: str = Field(..., description="User question")
    answer: str = Field(..., description="Answer provided by system")
    rating: Literal["up", "down"] = Field(..., description="User rating: up or down")
    comment: Optional[str] = Field(None, description="Optional feedback notes")


class FeedbackResponse(BaseModel):
    status: str = "success"
    feedback_id: str
    message: str = "Feedback recorded successfully"


class HealthResponse(BaseModel):
    status: str = "healthy"
    vector_store: str = "available"
    indexed_documents: int = 0
    bm25_index: str = "available"


class MetricsResponse(BaseModel):
    total_queries: int = 0
    successful_queries: int = 0
    insufficient_evidence_queries: int = 0
    average_confidence: float = 0.0
    average_retries: float = 0.0
    positive_feedback: int = 0
    negative_feedback: int = 0


# --- Structured Output LLM Schemas ---

class QueryAnalysisOutput(BaseModel):
    query_type: Literal["conceptual", "how_to", "troubleshooting", "api_reference"] = Field(
        ..., description="Intent classification"
    )
    technical_keywords: List[str] = Field(
        ..., description="Extracted key technical concepts and terms"
    )
    is_ambiguous: bool = Field(
        ..., description="Whether the user query is vague or ambiguous"
    )
    optimized_query: str = Field(
        ..., description="Standardized, search-optimized technical query"
    )


class ChunkEvaluation(BaseModel):
    chunk_id: str = Field(..., description="Chunk ID evaluated")
    classification: Literal["relevant", "partially_relevant", "irrelevant"] = Field(
        ..., description="Relevance classification"
    )
    relevance_score: float = Field(
        ..., description="Numeric score between 0.0 and 1.0"
    )
    reason: str = Field(..., description="Brief rationale for the grade")


class DocumentGradingOutput(BaseModel):
    evaluations: List[ChunkEvaluation] = Field(..., description="Grading per chunk")


class QueryRewriteOutput(BaseModel):
    rewritten_query: str = Field(..., description="Expanded technical query with synonyms and alternative terms")
    explanation: str = Field(..., description="Reasoning for query expansion")


class AnswerValidationOutput(BaseModel):
    groundedness_classification: Literal["supported", "partially_supported", "unsupported"] = Field(
        ..., description="Whether answer claims are derived strictly from retrieved context"
    )
    groundedness_score: float = Field(
        ..., description="Score between 0.0 and 1.0 representing proportion of supported statements"
    )
    unsupported_claims: List[str] = Field(
        default_factory=list, description="Any statements made in answer that lack evidence in context"
    )
