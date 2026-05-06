from typing import Any, Dict, List

from loguru import logger

from src.vectorstore.base_store import BaseVectorStore


class VectorRetriever:
    """Retrieves relevant text chunks from the vector store using semantic search."""

    def __init__(self, vector_store: BaseVectorStore):
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Search the vector store for chunks similar to the query.

        Returns:
            Dict with "chunks" (list of text+metadata+score) and "total_found".
        """
        if self.vector_store.count() == 0:
            logger.warning("Vector store is empty — skipping vector retrieval")
            return {"chunks": [], "total_found": 0}

        results = self.vector_store.search(query, top_k=top_k)

        logger.info(
            f"Vector retrieval: {len(results)} chunks for query: {query[:80]}"
        )

        return {
            "chunks": results,
            "total_found": len(results),
        }

    def format_context(self, retrieval_result: Dict[str, Any], max_chars: int = 5000) -> str:
        """Format vector retrieval results into text context for the LLM."""
        chunks = retrieval_result.get("chunks", [])
        if not chunks:
            return ""

        lines = ["=== DOCUMENT CONTEXT (from business reports) ===\n"]

        for i, chunk in enumerate(chunks):
            source = chunk.get("metadata", {}).get("source", "unknown")
            doc_type = chunk.get("metadata", {}).get("doc_type", "unknown")
            score = chunk.get("score", 0.0)

            lines.append(f"--- [{doc_type}] {source} (relevance: {score:.2f}) ---")
            lines.append(chunk["text"])
            lines.append("")

        lines.append("=== END DOCUMENT CONTEXT ===")

        result = "\n".join(lines)
        if len(result) > max_chars:
            result = result[:max_chars] + "\n... [document context truncated]\n=== END DOCUMENT CONTEXT ==="

        return result
