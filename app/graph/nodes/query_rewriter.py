from app.graph.state import DocuMindState
from app.services.llm_service import llm_service
from app.models.schemas import QueryRewriteOutput
from app.core.logging import logger

SYSTEM_PROMPT = """
You are a technical search query rewriting specialist.
Your task is to rephrase and expand a user's question because previous document retrieval attempts failed to return relevant technical documentation.

Use:
- Extracted technical keywords
- Query intent classification
- Synonyms, alternative technical terms, and standard terminology
- Core concepts

Return a clearer, expanded search query optimized for vector and keyword search engines.
"""


def query_rewriter_node(state: DocuMindState) -> DocuMindState:
    """Rewrites and expands search query to improve retrieval recall on retry."""
    logger.info("Executing QUERY_REWRITER node...")
    question = state["question"]
    previous_query = state.get("optimized_query", question)
    keywords = state.get("technical_keywords", [])
    intent = state.get("query_type", "conceptual")
    retry_count = state.get("retry_count", 0) + 1
    trace = list(state.get("workflow_trace", []))
    trace.append("QUERY_REWRITER")

    prompt = (
        f"Original Question: {question}\n"
        f"Previous Search Query: {previous_query}\n"
        f"Intent: {intent}\n"
        f"Technical Keywords: {', '.join(keywords)}\n\n"
        f"Please rewrite this query to be broader and use alternative technical terminology."
    )

    try:
        rewrite_res: QueryRewriteOutput = llm_service.generate_structured(
            prompt=prompt,
            schema=QueryRewriteOutput,
            system_prompt=SYSTEM_PROMPT
        )
        new_query = rewrite_res.rewritten_query

        logger.info(f"Query rewritten (Retry #{retry_count}): '{new_query}'")

        return {
            **state,
            "optimized_query": new_query,
            "retry_count": retry_count,
            "workflow_trace": trace,
        }
    except Exception as e:
        logger.error(f"Error in QUERY_REWRITER node: {e}")
        fallback_query = f"{question} {' '.join(keywords)}"
        return {
            **state,
            "optimized_query": fallback_query,
            "retry_count": retry_count,
            "workflow_trace": trace,
        }
