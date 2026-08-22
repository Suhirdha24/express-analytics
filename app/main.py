import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import logger
from app.api.routes_query import router as query_router
from app.api.routes_ingest import router as ingest_router
from app.api.routes_documents import router as documents_router
from app.api.routes_feedback import router as feedback_router
from app.api.routes_health import router as health_router
from app.api.routes_metrics import router as metrics_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A Self-Correcting Technical Documentation Assistant using LangGraph, ChromaDB, and BM25",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(query_router)
app.include_router(ingest_router)
app.include_router(documents_router)
app.include_router(feedback_router)
app.include_router(health_router)
app.include_router(metrics_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler ensuring internal details/keys are masked."""
    logger.error(f"Unhandled Exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An internal server error occurred.",
            "detail": str(exc) if settings.DEBUG else "Please check server logs."
        }
    )


@app.get("/", include_in_schema=False)
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
