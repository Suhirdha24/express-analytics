import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Information
    APP_NAME: str = "DocuMind"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # LLM Provider Configuration
    LLM_PROVIDER: str = "gemini"  # "gemini", "openai", or "mock"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gemini-1.5-flash"
    LLM_TEMPERATURE: float = 0.0

    # Embeddings & Vector Database
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"
    BM25_INDEX_DIR: str = "./data/metadata/bm25_index.pkl"
    DOCUMENTS_DIR: str = "./data/documents"
    FEEDBACK_DB_DIR: str = "./data/feedback/feedback.db"
    METADATA_DIR: str = "./data/metadata"

    # RAG Workflow Parameters
    MAX_RETRIES: int = 2
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150
    TOP_K_RETRIEVAL: int = 5

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_abs_path(self, relative_path: str) -> Path:
        """Resolve absolute path relative to project root."""
        base_dir = Path(__file__).resolve().parent.parent.parent
        return (base_dir / relative_path).resolve()


settings = Settings()

# Ensure required directories exist
for path_attr in ["CHROMA_PERSIST_DIR", "DOCUMENTS_DIR", "METADATA_DIR"]:
    dir_path = settings.get_abs_path(getattr(settings, path_attr))
    dir_path.mkdir(parents=True, exist_ok=True)

feedback_db_path = settings.get_abs_path(settings.FEEDBACK_DB_DIR)
feedback_db_path.parent.mkdir(parents=True, exist_ok=True)
