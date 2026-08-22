import chromadb
from pathlib import Path
from typing import List, Dict, Any
from app.core.config import settings
from app.core.logging import logger
from app.ingestion.embedder import embedding_service


class VectorStoreManager:
    """Manages persistent ChromaDB vector storage."""

    def __init__(self, collection_name: str = "documind_docs"):
        self.persist_dir = settings.get_abs_path(settings.CHROMA_PERSIST_DIR)
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Embeds and persists document chunks in ChromaDB."""
        if not chunks:
            return

        ids = [c["chunk_id"] for c in chunks]
        texts = [c["content"] for c in chunks]
        metadatas = [
            {
                "document_id": c["document_id"],
                "chunk_id": c["chunk_id"],
                "chunk_index": c["chunk_index"],
                "title": c["title"],
                "source": c["source"],
                "ingestion_timestamp": c["ingestion_timestamp"],
            }
            for c in chunks
        ]

        embeddings = embedding_service.embed_texts(texts)

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        logger.info(f"Added {len(chunks)} chunks to ChromaDB collection '{self.collection_name}'.")

    def similarity_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Performs vector similarity search against ChromaDB."""
        if self.collection.count() == 0:
            return []

        query_vector = embedding_service.embed_query(query)
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"]
        )

        matched_docs = []
        if results and results["documents"] and results["documents"][0]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0]

            for text, meta, dist in zip(docs, metas, distances):
                # Cosine distance to similarity score
                similarity = float(1.0 - dist)
                matched_docs.append({
                    "chunk_id": meta["chunk_id"],
                    "document_id": meta["document_id"],
                    "chunk_index": meta["chunk_index"],
                    "content": text,
                    "title": meta["title"],
                    "source": meta["source"],
                    "ingestion_timestamp": meta.get("ingestion_timestamp", ""),
                    "score": similarity,
                    "search_type": "vector"
                })

        return matched_docs

    def get_all_chunk_metadata(self) -> List[Dict[str, Any]]:
        """Returns metadata for all stored chunks."""
        if self.collection.count() == 0:
            return []
        data = self.collection.get(include=["metadatas"])
        return data["metadatas"] if data else []

    def get_indexed_document_count(self) -> int:
        """Returns total unique document count indexed."""
        metas = self.get_all_chunk_metadata()
        unique_docs = {m["document_id"] for m in metas if "document_id" in m}
        return len(unique_docs)

    def is_document_indexed(self, document_id: str) -> bool:
        """Checks if document ID is already present in vector store."""
        metas = self.get_all_chunk_metadata()
        return any(m.get("document_id") == document_id for m in metas)


vector_store = VectorStoreManager()
