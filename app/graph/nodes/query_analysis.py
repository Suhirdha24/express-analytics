from app.graph.state import DocuMindState
from app.services.llm_service import llm_service
from app.models.schemas import QueryAnalysisOutput
from app.core.logging import logger


SYSTEM_PROMPT = """
You are a technical documentation search query analyzer.
Your task is to:
1. Classify the query intent into one of: 'conceptual', 'how_to', 'troubleshooting', 'api_reference'.
2. Extract technical keywords and frameworks.
3. Determine if the question is ambiguous or vague.
4. Formulate an optimized technical search query for retrieval.
"""


def query_analysis_node(state: DocuMindState) -> DocuMindState:
    """Analyzes raw question to extract intent, keywords, and optimized search query."""
    logger.info("Executing QUERY_ANALYSIS node...")
    question = state["question"]
    trace = list(state.get("workflow_trace", []))
    trace.append("QUERY_ANALYSIS")

    prompt = f"User Question: {question}"

    try:
        analysis: QueryAnalysisOutput = llm_service.generate_structured(
            prompt=prompt,
            schema=QueryAnalysisOutput,
            system_prompt=SYSTEM_PROMPT
        )

        return {
            **state,
            "query_type": analysis.query_type,
            "technical_keywords": analysis.technical_keywords,
            "is_ambiguous": analysis.is_ambiguous,
            "optimized_query": analysis.optimized_query or question,
            "workflow_trace": trace,
        }
    except Exception as e:
        logger.error(f"Error in QUERY_ANALYSIS node: {e}")
        return {
            **state,
            "query_type": "conceptual",
            "technical_keywords": [q for q in question.split() if len(q) > 3],
            "is_ambiguous": False,
            "optimized_query": question,
            "workflow_trace": trace,
        }
