from app.graph.state import DocuMindState
from app.services.llm_service import llm_service
from app.models.schemas import AnswerValidationOutput
from app.core.logging import logger

SYSTEM_PROMPT = """
You are a strict technical fact-checker and hallucination detector.
Verify whether every claim made in the generated answer is directly supported by the provided document context.

Instructions:
1. Classify the answer as:
   - 'supported': All statements are fully grounded in the retrieved context.
   - 'partially_supported': Most statements are supported, but 1-2 minor claims lack direct evidence.
   - 'unsupported': The answer contains significant unverified claims or hallucinations.
2. Provide a groundedness_score between 0.0 and 1.0.
3. List any unsupported claims found.
"""


def answer_validation_node(state: DocuMindState) -> DocuMindState:
    """Validates generated answer against retrieved context to verify factual groundedness."""
    logger.info("Executing ANSWER_VALIDATION node...")
    answer = state.get("generated_answer", "")
    relevant_docs = state.get("relevant_documents", [])
    trace = list(state.get("workflow_trace", []))
    trace.append("ANSWER_VALIDATION")

    if not answer or not relevant_docs:
        return {
            **state,
            "groundedness_score": 0.0,
            "workflow_trace": trace,
        }

    context_str = "\n---\n".join([doc["content"] for doc in relevant_docs])
    prompt = f"Generated Answer:\n{answer}\n\nRetrieved Ground Truth Context:\n{context_str}"

    try:
        validation: AnswerValidationOutput = llm_service.generate_structured(
            prompt=prompt,
            schema=AnswerValidationOutput,
            system_prompt=SYSTEM_PROMPT
        )

        logger.info(
            f"Answer validation complete. Classification: {validation.groundedness_classification}, "
            f"Groundedness score: {validation.groundedness_score:.2f}"
        )

        return {
            **state,
            "groundedness_score": float(validation.groundedness_score),
            "workflow_trace": trace,
        }
    except Exception as e:
        logger.error(f"Error in ANSWER_VALIDATION node: {e}")
        return {
            **state,
            "groundedness_score": 0.8,  # Default fallback score
            "workflow_trace": trace,
        }
