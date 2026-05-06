import pytest

from src.graph.networkx_store import NetworkXGraphStore
from src.retrieval.graph_retriever import GraphRetriever
from src.retrieval.context_builder import ContextBuilder


@pytest.fixture
def populated_store():
    store = NetworkXGraphStore()
    store.add_node("DEPT-001", "Department", {"name": "Engineering"})
    store.add_node("EMP-001", "Employee", {"name": "Alice"})
    store.add_node("PROD-001", "Product", {"name": "CloudSync Pro"})
    store.add_node("CUST-001", "Customer", {"name": "Acme Corp"})
    store.add_edge("EMP-001", "DEPT-001", "WORKS_IN")
    store.add_edge("EMP-001", "PROD-001", "SOLD", {"amount": 1500})
    store.add_edge("CUST-001", "PROD-001", "PURCHASED", {"amount": 1500})
    return store


def test_retriever_finds_nodes(populated_store):
    retriever = GraphRetriever(populated_store)
    result = retriever.retrieve("CloudSync Pro sales")
    assert len(result["nodes"]) > 0


def test_retriever_finds_engineering(populated_store):
    retriever = GraphRetriever(populated_store)
    result = retriever.retrieve("Engineering department employees")
    assert len(result["nodes"]) > 0


def test_retriever_empty_query(populated_store):
    retriever = GraphRetriever(populated_store)
    result = retriever.retrieve("xyznonexistent12345")
    assert len(result["nodes"]) == 0


def test_context_builder_formats_output(populated_store):
    retriever = GraphRetriever(populated_store)
    subgraph = retriever.retrieve("CloudSync")
    builder = ContextBuilder()
    context = builder.build(subgraph)
    assert "KNOWLEDGE GRAPH CONTEXT" in context
    assert "CloudSync" in context


def test_context_builder_empty():
    builder = ContextBuilder()
    context = builder.build({"nodes": [], "edges": []})
    assert "No relevant data found" in context
