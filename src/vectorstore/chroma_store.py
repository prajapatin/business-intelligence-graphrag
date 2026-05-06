import os
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
from loguru import logger

from src.vectorstore.base_store import BaseVectorStore


class ChromaVectorStore(BaseVectorStore):
    """ChromaDB-backed vector store with sentence-transformer embeddings."""

    def __init__(
        self,
        persist_directory: str = "rag_data/vector_store",
        collection_name: str = "bi_reports",
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        os.makedirs(persist_directory, exist_ok=True)

        self._client = chromadb.Client(ChromaSettings(
            is_persistent=True,
            persist_directory=persist_directory,
            anonymized_telemetry=False,
        ))

        self._ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model,
        )

        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
            embedding_function=self._ef,
        )
        logger.info(f"ChromaDB initialized: {persist_directory} (collection: {collection_name}, docs: {self._collection.count()})")

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """Add documents to ChromaDB. IDs are auto-generated if not provided."""
        if not documents:
            return

        if ids is None:
            existing = self._collection.count()
            ids = [f"doc_{existing + i}" for i in range(len(documents))]

        # ChromaDB metadata values must be str, int, float, or bool
        clean_metadatas = None
        if metadatas:
            clean_metadatas = []
            for m in metadatas:
                clean = {}
                for k, v in m.items():
                    if isinstance(v, (str, int, float, bool)):
                        clean[k] = v
                    else:
                        clean[k] = str(v)
                clean_metadatas.append(clean)

        self._collection.add(
            documents=documents,
            metadatas=clean_metadatas,
            ids=ids,
        )
        logger.info(f"Added {len(documents)} documents to vector store")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for semantically similar documents."""
        if self._collection.count() == 0:
            return []

        results = self._collection.query(
            query_texts=[query],
            n_results=min(top_k, self._collection.count()),
        )

        hits = []
        if results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results["metadatas"] else [{}] * len(docs)
            distances = results["distances"][0] if results["distances"] else [0.0] * len(docs)

            for doc, meta, dist in zip(docs, metas, distances):
                hits.append({
                    "text": doc,
                    "metadata": meta or {},
                    "score": 1.0 - dist,  # Convert distance to similarity
                })

        return hits

    def count(self) -> int:
        return self._collection.count()

    def clear(self) -> None:
        self._client.delete_collection(self.collection_name)
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("Vector store cleared")

    def persist(self) -> None:
        # PersistentClient auto-persists; this is a no-op for compatibility
        logger.info(f"Vector store persisted to {self.persist_directory}")
