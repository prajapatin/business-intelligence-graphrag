#!/usr/bin/env python3
"""Build the knowledge graph from synthetic corporate data."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from loguru import logger

from config.settings import settings
from src.graph import create_graph_store
from src.ingestion.csv_loader import load_all_data
from src.ingestion.entity_extractor import extract_from_structured_data
from src.ingestion.graph_builder import build_graph
from src.vectorstore.chroma_store import ChromaVectorStore
from src.vectorstore.document_chunker import DocumentChunker


def main():
    logger.info("=== Building Knowledge Graph + Vector Store ===")

    # Step 1: Load CSV data
    logger.info("Step 1: Loading synthetic data...")
    tables = load_all_data()
    if not tables:
        logger.error("No data files found. Run 'python scripts/generate_data.py' first.")
        sys.exit(1)

    # Step 2: Extract entities and relationships
    logger.info("Step 2: Extracting entities and relationships...")
    extracted = extract_from_structured_data(tables)

    # Step 3: Build graph
    logger.info("Step 3: Building graph...")
    graph_store = create_graph_store()
    build_graph(graph_store, extracted)

    # Step 4: Persist graph
    persist_path = settings.graph_persist_path
    logger.info(f"Step 4: Persisting graph to {persist_path}...")
    graph_store.persist(persist_path)

    # Step 5: Build vector store from reports
    logger.info("Step 5: Building vector store from business reports...")
    reports_dir = settings.reports_directory
    chunker = DocumentChunker(chunk_size=500, chunk_overlap=100)
    chunks = chunker.chunk_directory(reports_dir)

    if chunks:
        vector_store = ChromaVectorStore(persist_directory=settings.vector_persist_path)
        vector_store.clear()
        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        vector_store.add_documents(documents, metadatas=metadatas, ids=ids)
        vector_store.persist()
        logger.info(f"  Vector store: {vector_store.count()} chunks indexed")
    else:
        logger.warning("No report files found. Run 'python scripts/generate_data.py' first.")

    # Summary
    stats = graph_store.get_statistics()
    logger.info("=== Build Complete ===")
    logger.info(f"  Total nodes: {stats['total_nodes']}")
    logger.info(f"  Total edges: {stats['total_edges']}")
    logger.info(f"  Node types: {stats['node_types']}")
    logger.info(f"  Edge types: {stats['edge_types']}")
    logger.info(f"  Vector chunks: {len(chunks)}")


if __name__ == "__main__":
    main()
