from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseVectorStore(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """Add documents with optional metadata to the vector store."""
        ...

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents. Returns list of dicts with 'text', 'metadata', 'score'."""
        ...

    @abstractmethod
    def count(self) -> int:
        """Return the number of documents in the store."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Remove all documents."""
        ...

    @abstractmethod
    def persist(self) -> None:
        """Persist the store to disk."""
        ...
