from pathlib import Path
from typing import Dict, Any, Union
from app.core.logging import logger
from app.utils.hashing import compute_content_hash
from app.ingestion.loader import DocumentLoader
from app.ingestion.chunker import DocumentChunker
from app.ingestion.vector_store import vector_store
from app.ingestion.bm25_store import bm25_store


class IngestionPipeline:
    """Orchestrates loading, deduplication, chunking, vector embedding, and BM25 indexing."""

    def __init__(self):
        self.chunker = DocumentChunker()

    def ingest_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Ingests local document file (Markdown, TXT, HTML)."""
        path = Path(file_path)
        doc_data = DocumentLoader.load_from_file(path)
        return self._process_document(doc_data)

    def ingest_url(self, url: str, title_override: str = None) -> Dict[str, Any]:
        """Ingests content scraped from a web URL."""
        doc_data = DocumentLoader.load_from_url(url, title_override=title_override)
        return self._process_document(doc_data)

    def ingest_raw_text(self, title: str, content: str, source: str = "raw_input") -> Dict[str, Any]:
        """Ingests raw text input."""
        doc_data = {
            "title": title,
            "content": DocumentLoader._clean_text(content),
            "source": source,
            "file_type": "txt",
        }
        return self._process_document(doc_data)

    def _process_document(self, doc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Core pipeline: hashing, duplicate checking, chunking, indexing."""
        content_hash = compute_content_hash(doc_data["content"])

        if vector_store.is_document_indexed(content_hash):
            logger.info(f"Document '{doc_data['title']}' (ID: {content_hash[:8]}...) already indexed. Skipping.")
            return {
                "status": "duplicate",
                "document_id": content_hash,
                "chunks_created": 0,
                "message": f"Document '{doc_data['title']}' is already indexed in vector database.",
            }

        chunks = self.chunker.chunk_document(doc_data, content_hash)
        
        # Save embeddings & BM25 keyword index
        vector_store.add_chunks(chunks)
        bm25_store.add_chunks(chunks)

        logger.info(
            f"Successfully indexed document '{doc_data['title']}' ({len(chunks)} chunks, ID: {content_hash[:8]}...)"
        )
        return {
            "status": "success",
            "document_id": content_hash,
            "chunks_created": len(chunks),
            "message": f"Successfully indexed document '{doc_data['title']}' with {len(chunks)} chunks.",
        }


ingestion_pipeline = IngestionPipeline()
