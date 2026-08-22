import sys
from pathlib import Path

# Ensure root documind directory is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.core.config import settings
from app.core.logging import logger
from app.ingestion.pipeline import ingestion_pipeline


def main():
    """Ingests all sample FastAPI documentation files in data/documents/."""
    docs_dir = settings.get_abs_path(settings.DOCUMENTS_DIR)
    logger.info(f"Scanning for sample documents in: {docs_dir}")

    doc_files = sorted(list(docs_dir.glob("*.md")) + list(docs_dir.glob("*.txt")))

    if not doc_files:
        logger.warning("No sample document files found to ingest!")
        return

    logger.info(f"Found {len(doc_files)} sample documents. Beginning ingestion...")

    total_chunks = 0
    successful = 0

    for file_path in doc_files:
        try:
            res = ingestion_pipeline.ingest_file(file_path)
            logger.info(f"Result for {file_path.name}: {res['status']} ({res['chunks_created']} chunks)")
            total_chunks += res.get("chunks_created", 0)
            if res["status"] in ["success", "duplicate"]:
                successful += 1
        except Exception as e:
            logger.error(f"Failed to ingest {file_path.name}: {e}")

    logger.info(f"Ingestion process finished. Processed {successful}/{len(doc_files)} files ({total_chunks} total chunks indexed).")


if __name__ == "__main__":
    main()
