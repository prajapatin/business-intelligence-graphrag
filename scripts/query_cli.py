#!/usr/bin/env python3
"""Interactive CLI for querying the knowledge graph."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from loguru import logger

from config.settings import settings
from src.graph import create_graph_store
from src.llm import create_llm_provider
from src.generation.answer_generator import AnswerGenerator


EXAMPLE_QUERIES = [
    "What are the top-selling products by revenue?",
    "Which department generates the most sales revenue?",
    "Show me the quarterly revenue trend for 2024 and 2025",
    "Which customers spend the most? What industries are they in?",
    "What is the relationship between the Engineering department and product sales?",
    "Which region has the highest sales concentration?",
    "Who are the top-performing sales representatives?",
    "What product categories are trending upward?",
]


def main():
    logger.info("Loading knowledge graph...")
    graph_store = create_graph_store()

    persist_path = settings.graph_persist_path
    if os.path.exists(persist_path):
        graph_store.load(persist_path)
        stats = graph_store.get_statistics()
        logger.info(f"Graph loaded: {stats['total_nodes']} nodes, {stats['total_edges']} edges")
    else:
        logger.error(f"No persisted graph found at {persist_path}. Run 'python scripts/build_graph.py' first.")
        sys.exit(1)

    logger.info("Initializing LLM provider...")
    llm = create_llm_provider()
    generator = AnswerGenerator(llm, graph_store)

    print("\n" + "=" * 60)
    print("  Business Intelligence GraphRAG & Vector RAG — Interactive Query CLI")
    print("=" * 60)
    print("\nExample queries:")
    for i, q in enumerate(EXAMPLE_QUERIES, 1):
        print(f"  {i}. {q}")
    print("\nType 'quit' to exit.\n")

    while True:
        try:
            query = input("🔍 Ask a BI question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        # Allow number selection from examples
        if query.isdigit() and 1 <= int(query) <= len(EXAMPLE_QUERIES):
            query = EXAMPLE_QUERIES[int(query) - 1]
            print(f"  → {query}")

        print("\n⏳ Analyzing...")
        try:
            result = generator.answer(query)
            print(f"\n📊 Answer:\n{result['answer']}")
            print(f"\n📈 Graph context: {result['subgraph']['node_count']} nodes, "
                  f"{result['subgraph']['edge_count']} edges retrieved")
            print(f"🔑 Matched terms: {', '.join(result['subgraph']['matched_terms'])}")
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"\n❌ Error: {e}")

        print()


if __name__ == "__main__":
    main()
