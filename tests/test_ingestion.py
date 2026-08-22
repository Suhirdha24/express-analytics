import pytest
from pathlib import Path
from app.ingestion.chunker import DocumentChunker
from app.utils.hashing import compute_content_hash
from app.ingestion.pipeline import ingestion_pipeline


def test_content_hashing():
    text1 = "  FastAPI Dependency Injection Tutorial  "
    text2 = "FastAPI Dependency Injection Tutorial"
    text3 = "FastAPI Path Parameters"

    assert compute_content_hash(text1) == compute_content_hash(text2)
    assert compute_content_hash(text1) != compute_content_hash(text3)


def test_document_chunking():
    chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
    sample_doc = {
        "title": "Test Title",
        "content": "Line 1 paragraph.\n\nLine 2 paragraph with longer text that should exceed chunk threshold bounds.",
        "source": "test.txt",
    }
    chunks = chunker.chunk_document(sample_doc, "test_doc_id_123")

    assert len(chunks) > 0
    assert chunks[0]["document_id"] == "test_doc_id_123"
    assert chunks[0]["title"] == "Test Title"
    assert "chunk_id" in chunks[0]


def test_duplicate_detection(tmp_path):
    test_file = tmp_path / "sample_test.md"
    test_file.write_text("# Unique Document\nThis is unique content for duplicate detection testing.", encoding="utf-8")

    res1 = ingestion_pipeline.ingest_file(test_file)
    assert res1["status"] == "success"
    assert res1["chunks_created"] > 0

    res2 = ingestion_pipeline.ingest_file(test_file)
    assert res2["status"] == "duplicate"
    assert res2["chunks_created"] == 0
