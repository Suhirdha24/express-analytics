from app.graph.state import DocuMindState
from app.services.llm_service import llm_service
from app.utils.citations import extract_citations_from_text, format_source_citation
from app.core.logging import logger

SYSTEM_PROMPT = """
You are DocuMind, an expert AI technical documentation assistant.
Generate a precise, well-structured, and technically clear answer to the user's question using ONLY the provided relevant document context.

Strict Instructions:
1. Ground every claim directly in the provided text chunks. Do NOT introduce outside knowledge or unverified facts.
2. Use clear headings, code blocks, or bullet points to explain concepts clearly.
3. Include inline citations for every factual statement using the format:
   [Source: Document Title – Document Source]
   Example: [Source: FastAPI Documentation – Dependency Injection]
4. Only cite sources explicitly present in the provided context.
5. If the context does not contain enough information to fully answer, state what is known and mention limitations clearly.
"""


def answer_generation_node(state: DocuMindState) -> DocuMindState:
    """Generates a grounded technical response with inline source citations."""
    logger.info("Executing ANSWER_GENERATION node...")
    question = state["question"]
    relevant_docs = state.get("relevant_documents", [])
    trace = list(state.get("workflow_trace", []))
    trace.append("ANSWER_GENERATION")

    if not relevant_docs:
        logger.warning("ANSWER_GENERATION called without relevant documents.")
        return {
            **state,
            "generated_answer": "No relevant documentation available.",
            "citations": [],
            "workflow_trace": trace,
        }

    # Format context blocks with exact source labels
    context_blocks = []
    source_citation_map = {}

    for index, doc in enumerate(relevant_docs):
        citation_label = format_source_citation(doc)
        source_citation_map[doc["chunk_id"]] = citation_label

        context_blocks.append(
            f"--- DOCUMENT CHUNK {index + 1} ---\n"
            f"Citation Tag: {citation_label}\n"
            f"Title: {doc['title']}\n"
            f"Source File/URL: {doc['source']}\n"
            f"Content:\n{doc['content']}\n"
        )

    context_str = "\n".join(context_blocks)
    prompt = f"User Question: {question}\n\nProvided Document Context:\n{context_str}"

    try:
        answer_text = llm_service.generate(prompt=prompt, system_prompt=SYSTEM_PROMPT)
        citations = extract_citations_from_text(answer_text)

        # Fallback: if citations missing in prompt text, append default valid source tags
        if not citations and relevant_docs:
            citations = list(set(source_citation_map.values()))

        return {
            **state,
            "generated_answer": answer_text,
            "citations": citations,
            "workflow_trace": trace,
        }
    except Exception as e:
        logger.error(f"Error in ANSWER_GENERATION node: {e}")
        return {
            **state,
            "generated_answer": "An error occurred while generating the answer.",
            "citations": [],
            "workflow_trace": trace,
        }
