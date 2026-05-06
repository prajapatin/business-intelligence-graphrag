from typing import Any, Dict, Optional

from loguru import logger

from src.llm.base_provider import BaseLLMProvider
from src.retrieval.hybrid_retriever import HybridRetriever
from src.graph.base_store import BaseGraphStore
from src.vectorstore.base_store import BaseVectorStore


SYSTEM_PROMPT = """You are a Business Intelligence analyst powered by a corporate knowledge graph and business document archive.
You answer questions about business trends, relationships, performance metrics, and organizational structure.

Instructions:
- Base your answers ONLY on the provided context (both graph data and document excerpts).
- Cite specific entities, relationships, data points, and report findings from the context.
- If the context doesn't contain enough information, say so clearly.
- Format your response with clear structure: use bullet points, tables, or numbered lists where appropriate.
- Highlight key insights and trends.
- Be concise but thorough."""


class AnswerGenerator:
    """Full Hybrid RAG pipeline: query → retrieve (graph + vector) → augment → generate."""

    def __init__(
        self,
        llm: BaseLLMProvider,
        graph_store: BaseGraphStore,
        vector_store: Optional[BaseVectorStore] = None,
        retrieval_mode: str = "hybrid",
    ):
        self.llm = llm
        self.hybrid_retriever = HybridRetriever(
            graph_store=graph_store,
            vector_store=vector_store,
            default_mode=retrieval_mode,
        )
        self.graph_store = graph_store

    def answer(
        self,
        query: str,
        max_depth: int = 2,
        retrieval_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Answer a natural language BI question using Hybrid RAG.

        Args:
            query: Natural language question.
            max_depth: How many hops to traverse for graph context.
            retrieval_mode: Override retrieval mode (hybrid/graph_only/vector_only).

        Returns:
            Dict with answer, context, subgraph metadata, and retrieval info.
        """
        # Step 1: Hybrid retrieval (graph + vector)
        logger.info(f"Processing query: {query}")
        retrieval = self.hybrid_retriever.retrieve(
            query, mode=retrieval_mode, max_depth=max_depth,
        )

        context = retrieval["context"]
        logger.debug(f"Context length: {len(context)} chars (mode: {retrieval['retrieval_mode']})")

        # Step 2: Generate answer with LLM
        prompt = f"""Based on the following context from our knowledge graph and business documents, answer the business intelligence question.

{context}

Question: {query}

Provide a detailed, data-driven answer:"""

        answer = self.llm.generate(prompt, system_prompt=SYSTEM_PROMPT)

        return {
            "query": query,
            "answer": answer,
            "subgraph": retrieval["subgraph"],
            "vector_chunks_used": retrieval["vector_chunks_used"],
            "retrieval_mode": retrieval["retrieval_mode"],
            "context_preview": context[:500] + "..." if len(context) > 500 else context,
        }
