from app.graph.state import DocuMindState
from app.services.llm_service import llm_service
from app.models.schemas import DocumentGradingOutput
from app.core.logging import logger

SYSTEM_PROMPT = """
You are an expert technical document grading assistant.
Grade each document chunk for relevance against the user's question.
Classify each chunk as:
- 'relevant': Direct, precise answer or context for the question.
- 'partially_relevant': Provides useful background or related concepts.
- 'irrelevant': Off-topic, unrelated, or lacks actionable information for this specific query.

Assign a relevance_score between 0.0 and 1.0.
"""


def document_grading_node(state: DocuMindState) -> DocuMindState:
    """Grades retrieved document chunks and filters out irrelevant context."""
    logger.info("Executing DOCUMENT_GRADING node...")
    retrieved = state.get("retrieved_documents", [])
    question = state["question"]
    trace = list(state.get("workflow_trace", []))
    trace.append("DOCUMENT_GRADING")

    if not retrieved:
        logger.info("No documents to grade.")
        return {
            **state,
            "graded_documents": [],
            "relevant_documents": [],
            "relevance_quality": 0.0,
            "workflow_trace": trace,
        }

    # Format chunks for LLM evaluation
    chunk_descriptions = []
    for doc in retrieved:
        chunk_descriptions.append(
            f"Chunk ID: {doc['chunk_id']}\nTitle: {doc['title']}\nContent:\n{doc['content']}\n"
        )

    prompt = f"User Question: {question}\n\nRetrieved Document Chunks:\n" + "\n---\n".join(chunk_descriptions)

    try:
        grading_res: DocumentGradingOutput = llm_service.generate_structured(
            prompt=prompt,
            schema=DocumentGradingOutput,
            system_prompt=SYSTEM_PROMPT
        )

        eval_map = {e.chunk_id: e for e in grading_res.evaluations}

        graded_docs = []
        relevant_docs = []

        for doc in retrieved:
            cid = doc["chunk_id"]
            eval_info = eval_map.get(cid)

            if eval_info:
                classification = eval_info.classification
                score = eval_info.relevance_score
            else:
                # Fallback if specific ID omitted by LLM output
                classification = "relevant" if doc.get("score", 0) > 0.5 else "irrelevant"
                score = doc.get("score", 0.5)

            graded_chunk = {
                **doc,
                "classification": classification,
                "relevance_score": float(score),
            }
            graded_docs.append(graded_chunk)

            if classification in ["relevant", "partially_relevant"] and score >= 0.4:
                relevant_docs.append(graded_chunk)

        relevance_quality = 0.0
        if relevant_docs:
            relevance_quality = sum(d["relevance_score"] for d in relevant_docs) / len(relevant_docs)

        logger.info(f"Grading complete. {len(relevant_docs)}/{len(retrieved)} chunks classified as relevant.")

        return {
            **state,
            "graded_documents": graded_docs,
            "relevant_documents": relevant_docs,
            "relevance_quality": float(relevance_quality),
            "workflow_trace": trace,
        }

    except Exception as e:
        logger.error(f"Error during document grading: {e}")
        # Soft fallback: keep chunks with initial vector score > 0.3
        relevant_docs = [d for d in retrieved if d.get("score", 0) >= 0.3]
        return {
            **state,
            "graded_documents": retrieved,
            "relevant_documents": relevant_docs,
            "relevance_quality": 0.5 if relevant_docs else 0.0,
            "workflow_trace": trace,
        }
