import tempfile
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Body
from app.models.schemas import IngestResponse, URLIngestRequest
from app.ingestion.pipeline import ingestion_pipeline
from app.core.logging import logger

router = APIRouter(prefix="/ingest", tags=["Ingestion Pipeline"])


@router.post("", response_model=IngestResponse, summary="Ingest document file or web URL")
async def ingest_document(
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
) -> IngestResponse:
    """
    Ingests technical documentation via file upload (Markdown, TXT, HTML) or web URL.
    Performs content hashing to prevent duplicate indexing.
    """
    if file and url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specify either a file or a url, not both."
        )

    if not file and not url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either a file upload or a url must be provided."
        )

    try:
        if file:
            filename = file.filename or "uploaded_doc.txt"
            ext = Path(filename).suffix.lower()
            if ext not in [".md", ".txt", ".html", ".htm"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported file type '{ext}'. Allowed types: .md, .txt, .html"
                )

            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                content = await file.read()
                if not content:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Uploaded file is empty."
                    )
                tmp.write(content)
                tmp_path = Path(tmp.name)

            try:
                res = ingestion_pipeline.ingest_file(tmp_path)
                return IngestResponse(**res)
            finally:
                if tmp_path.exists():
                    tmp_path.unlink()

        elif url:
            if not url.startswith("http://") and not url.startswith("https://"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid URL format. URL must start with http:// or https://"
                )
            res = ingestion_pipeline.ingest_url(url, title_override=title)
            return IngestResponse(**res)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}"
        )


@router.post("/url", response_model=IngestResponse, summary="Ingest document from URL via JSON body")
def ingest_url_json(req: URLIngestRequest) -> IngestResponse:
    """Ingests documentation by submitting a JSON object containing URL."""
    try:
        res = ingestion_pipeline.ingest_url(req.url, title_override=req.title)
        return IngestResponse(**res)
    except Exception as e:
        logger.error(f"Error ingesting URL JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"URL Ingestion failed: {str(e)}"
        )
