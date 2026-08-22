import pickle
import re
from pathlib import Path
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
from app.core.config import settings
from app.core.logging import logger


def tokenize_text(text: str) -> List[str]:
    """Tokenizes and normalizes text for BM25 keyword matching."""
    return re.findall(r"\w+", text.lower())


class BM25StoreManager:
    """Manages persistent BM25 index for sparse keyword retrieval."""

    def __init__(self):
        self.index_path = settings.get_abs_path(settings.BM25_INDEX_DIR)
        self.chunks: List[Dict[str, Any]] = []
        self.bm25: BM25Okapi = None
        self._load_index()

    def _load_index(self):
        """Loads BM25 index from pickle storage if present."""
        if self.index_path.exists():
            try:
                with open(self.index_path, "rb") as f:
                    data = pickle.load(f)
                    self.chunks = data.get("chunks", [])
                    corpus = [tokenize_text(c["content"]) for c in self.chunks]
                    if corpus:
                        self.bm25 = BM25Okapi(corpus)
                logger.info(f"Loaded BM25 index with {len(self.chunks)} chunks.")
            except Exception as e:
                logger.warning(f"Failed to load BM25 index ({e}). Initializing empty index.")
                self.chunks = []
                self.bm25 = None

    def _save_index(self):
        """Persists BM25 index and chunk metadata to disk."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_path, "wb") as f:
            pickle.dump({"chunks": self.chunks}, f)

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Adds new document chunks to BM25 index and updates file."""
        if not chunks:
            return

        # Avoid duplicate chunk IDs
        existing_ids = {c["chunk_id"] for c in self.chunks}
        new_chunks = [c for c in chunks if c["chunk_id"] not in existing_ids]

        if not new_chunks:
            return

        self.chunks.extend(new_chunks)
        tokenized_corpus = [tokenize_text(c["content"]) for c in self.chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)
        self._save_index()
        logger.info(f"Updated BM25 index. Total chunks: {len(self.chunks)}")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Performs sparse BM25 keyword search."""
        if not self.bm25 or not self.chunks:
            return []

        tokenized_query = tokenize_text(query)
        if not tokenized_query:
            return []

        scores = self.bm25.get_scores(tokenized_query)
        
        # Zip chunks with scores
        scored_chunks = list(zip(self.chunks, scores))
        # Sort by score descending
        scored_chunks.sort(key=lambda x: x[1], reverse=True)

        results = []
        top_items = scored_chunks[:top_k]
        max_score = top_items[0][1] if top_items and top_items[0][1] > 0 else 1.0

        for chunk, score in top_items:
            if score > 0:
                normalized_score = float(score / max_score)
                chunk_copy = dict(chunk)
                chunk_copy["score"] = normalized_score
                chunk_copy["search_type"] = "bm25"
                results.append(chunk_copy)

        return results


bm25_store = BM25StoreManager()
