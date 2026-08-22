from typing import List, Dict, Any
from datetime import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings
from app.utils.hashing import generate_chunk_id


class DocumentChunker:
    """Intelligently splits document text into overlapping chunks."""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
            keep_separator=True,
        )

    def chunk_document(self, doc_data: Dict[str, Any], document_id: str) -> List[Dict[str, Any]]:
        """Splits document content into metadata-enriched chunks."""
        content = doc_data["content"]
        title = doc_data["title"]
        source = doc_data["source"]
        timestamp = datetime.utcnow().isoformat()

        raw_chunks = self.splitter.split_text(content)
        chunks = []

        for index, text in enumerate(raw_chunks):
            chunk_id = generate_chunk_id(document_id, index)
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "chunk_index": index,
                    "content": text.strip(),
                    "title": title,
                    "source": source,
                    "ingestion_timestamp": timestamp,
                }
            )

        return chunks
