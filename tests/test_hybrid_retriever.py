import pytest

from src.graph.networkx_store import NetworkXGraphStore
from src.retrieval.hybrid_retriever import HybridRetriever
from tests.test_vector_store import InMemoryChromaStore


@pytest.fixture
def graph_store():
    store = NetworkXGraphStore()
    store.add_node("DEPT-001", "Department", {"name": "Engineering"})
    store.add_node("EMP-001", "Employee", {"name": "Alice"})
    store.add_node("PROD-001", "Product", {"name": "CloudSync Pro"})
    store.add_edge("EMP-001", "DEPT-001", "WORKS_IN")
    store.add_edge("EMP-001", "PROD-001", "SOLD", {"amount": 1500})
    return store


@pytest.fixture
def vector_store():
    store = InMemoryChromaStore(collection_name="test_hybrid")
    store.add_documents(
        documents=[
            "CloudSync Pro generated $50K in Q4 revenue. It is our top SaaS product.",
            "Engineering department has 12 employees and focuses on cloud solutions.",
            "North America accounts for 45% of total revenue with strong enterprise adoption.",
        ],
        metadatas=[
            {"source": "product_brief.txt", "doc_type": "product_brief"},
            {"source": "dept_memo.txt", "doc_type": "department_memo"},
            {"source": "regional.txt", "doc_type": "regional_summary"},
        ],
        ids=["c0", "c1", "c2"],
    )
    return store


def test_hybrid_mode(graph_store, vector_store):
    retriever = HybridRetriever(graph_store, vector_store, default_mode="hybrid")
    result = retriever.retrieve("CloudSync Pro sales performance")

    assert result["retrieval_mode"] == "hybrid"
    assert result["subgraph"]["node_count"] > 0
    assert result["vector_chunks_used"] > 0
    assert "KNOWLEDGE GRAPH CONTEXT" in result["context"]
    assert "DOCUMENT CONTEXT" in result["context"]


def test_graph_only_mode(graph_store, vector_store):
    retriever = HybridRetriever(graph_store, vector_store, default_mode="graph_only")
    result = retriever.retrieve("CloudSync Pro")

    assert result["retrieval_mode"] == "graph_only"
    assert result["subgraph"]["node_count"] > 0
    assert result["vector_chunks_used"] == 0
    assert "KNOWLEDGE GRAPH CONTEXT" in result["context"]
    assert "DOCUMENT CONTEXT" not in result["context"]


def test_vector_only_mode(graph_store, vector_store):
    retriever = HybridRetriever(graph_store, vector_store, default_mode="vector_only")
    result = retriever.retrieve("CloudSync Pro revenue")

    assert result["retrieval_mode"] == "vector_only"
    assert result["subgraph"]["node_count"] == 0
    assert result["vector_chunks_used"] > 0
    assert "DOCUMENT CONTEXT" in result["context"]


def test_mode_override(graph_store, vector_store):
    retriever = HybridRetriever(graph_store, vector_store, default_mode="hybrid")
    result = retriever.retrieve("Engineering department", mode="graph_only")
    assert result["retrieval_mode"] == "graph_only"
    assert result["vector_chunks_used"] == 0


def test_hybrid_no_vector_store(graph_store):
    retriever = HybridRetriever(graph_store, vector_store=None, default_mode="hybrid")
    result = retriever.retrieve("CloudSync Pro")
    # Should fall back to graph-only context
    assert result["subgraph"]["node_count"] > 0
    assert result["vector_chunks_used"] == 0


def test_hybrid_no_graph_matches(graph_store, vector_store):
    retriever = HybridRetriever(graph_store, vector_store, default_mode="hybrid")
    result = retriever.retrieve("xyznonexistent12345")
    # Graph returns nothing, but vector might still return semantic matches
    assert result["retrieval_mode"] == "hybrid"
