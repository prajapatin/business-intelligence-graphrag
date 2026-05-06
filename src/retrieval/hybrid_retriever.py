from typing import Any, Dict, Optional

from loguru import logger

from src.graph.base_store import BaseGraphStore
from src.vectorstore.base_store import BaseVectorStore
from src.retrieval.graph_retriever import GraphRetriever
from src.retrieval.vector_retriever import VectorRetriever
from src.retrieval.context_builder import ContextBuilder


class HybridRetriever:
    """Combines graph retrieval and vector retrieval for hybrid RAG.

    Supports three modes:
    - "hybrid": Use both graph and vector retrieval (default)
    - "graph_only": Use only graph retrieval
    - "vector_only": Use only vector retrieval
    """

    def __init__(
        self,
        graph_store: BaseGraphStore,
        vector_store: Optional[BaseVectorStore] = None,
        default_mode: str = "hybrid",
    ):
        self.graph_retriever = GraphRetriever(graph_store)
        self.vector_retriever = VectorRetriever(vector_store) if vector_store else None
        self.context_builder = ContextBuilder()
        self.default_mode = default_mode

    def retrieve(
        self,
        query: str,
        mode: Optional[str] = None,
        max_depth: int = 2,
        vector_top_k: int = 5,
    ) -> Dict[str, Any]:
        """Retrieve context using the specified mode.

        Returns:
            Dict with "context", "subgraph" info, "vector_chunks_used", and "retrieval_mode".
        """
        retrieval_mode = mode or self.default_mode

        graph_context = ""
        graph_subgraph = {"nodes": [], "edges": [], "matched_terms": []}
        vector_context = ""
        vector_chunks_used = 0

        # --- Graph retrieval ---
        if retrieval_mode in ("hybrid", "graph_only"):
            graph_subgraph = self.graph_retriever.retrieve(query, max_depth=max_depth)
            graph_context = self.context_builder.build(graph_subgraph)

        # --- Vector retrieval ---
        if retrieval_mode in ("hybrid", "vector_only") and self.vector_retriever:
            vector_result = self.vector_retriever.retrieve(query, top_k=vector_top_k)
            vector_chunks_used = vector_result["total_found"]
            vector_context = self.vector_retriever.format_context(vector_result)

        # --- Fuse contexts ---
        if retrieval_mode == "hybrid" and graph_context and vector_context:
            combined_context = f"{graph_context}\n\n{vector_context}"
        elif graph_context:
            combined_context = graph_context
        elif vector_context:
            combined_context = vector_context
        else:
            combined_context = "No relevant data found."

        logger.info(
            f"Hybrid retrieval [{retrieval_mode}]: "
            f"graph={len(graph_context)} chars, "
            f"vector={len(vector_context)} chars ({vector_chunks_used} chunks), "
            f"combined={len(combined_context)} chars"
        )

        return {
            "context": combined_context,
            "subgraph": {
                "node_count": len(graph_subgraph.get("nodes", [])),
                "edge_count": len(graph_subgraph.get("edges", [])),
                "matched_terms": graph_subgraph.get("matched_terms", []),
            },
            "vector_chunks_used": vector_chunks_used,
            "retrieval_mode": retrieval_mode,
        }
