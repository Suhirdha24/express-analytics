import re
from typing import List, Dict, Any


def extract_citations_from_text(text: str) -> List[str]:
    """
    Extracts citation strings matching [Source: ...] pattern from generated text.
    Returns deduplicated list of citations.
    """
    pattern = r"\[Source:\s*([^\]]+)\]"
    matches = re.findall(pattern, text)
    citations = []
    seen = set()
    for m in matches:
        clean_citation = f"[Source: {m.strip()}]"
        if clean_citation not in seen:
            seen.add(clean_citation)
            citations.append(clean_citation)
    return citations


def format_source_citation(doc: Dict[str, Any]) -> str:
    """Formats standardized citation string for a document chunk."""
    title = doc.get("title") or "Technical Documentation"
    source = doc.get("source") or "Indexed Document"
    return f"[Source: {title} – {source}]"
