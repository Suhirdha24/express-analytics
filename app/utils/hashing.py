import hashlib


def compute_content_hash(content: str) -> str:
    """Computes a SHA256 hex digest string for document content to detect duplicates."""
    normalized = content.strip().encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def generate_chunk_id(document_id: str, chunk_index: int) -> str:
    """Generates a deterministic unique chunk ID."""
    return f"{document_id}_{chunk_index}"
