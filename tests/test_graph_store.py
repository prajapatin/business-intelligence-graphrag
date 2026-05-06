import pytest
from src.graph.networkx_store import NetworkXGraphStore


@pytest.fixture
def store():
    s = NetworkXGraphStore()
    s.add_node("DEPT-001", "Department", {"name": "Engineering", "budget": 2500000})
    s.add_node("EMP-001", "Employee", {"name": "Alice", "role": "Engineer"})
    s.add_node("EMP-002", "Employee", {"name": "Bob", "role": "Sales Rep"})
    s.add_node("PROD-001", "Product", {"name": "CloudSync Pro", "base_price": 299.99})
    s.add_edge("EMP-001", "DEPT-001", "WORKS_IN")
    s.add_edge("EMP-002", "DEPT-001", "WORKS_IN")
    s.add_edge("EMP-002", "PROD-001", "SOLD", {"amount": 1500.0})
    return s


def test_add_and_get_node(store):
    node = store.get_node("DEPT-001")
    assert node is not None
    assert node["node_type"] == "Department"
    assert node["name"] == "Engineering"


def test_get_nonexistent_node(store):
    assert store.get_node("NOPE") is None


def test_get_neighbors(store):
    neighbors = store.get_neighbors("DEPT-001", max_depth=1)
    neighbor_ids = {n["id"] for n in neighbors}
    assert "EMP-001" in neighbor_ids
    assert "EMP-002" in neighbor_ids


def test_search_nodes(store):
    results = store.search_nodes("alice")
    assert len(results) == 1
    assert results[0]["name"] == "Alice"


def test_search_by_type(store):
    results = store.search_nodes("", node_type="Employee")
    assert len(results) == 2


def test_get_subgraph(store):
    sub = store.get_subgraph(["DEPT-001"], max_depth=1)
    assert len(sub["nodes"]) >= 2
    assert len(sub["edges"]) >= 2


def test_get_all_nodes(store):
    nodes = store.get_all_nodes()
    assert len(nodes) == 4


def test_get_all_edges(store):
    edges = store.get_all_edges()
    assert len(edges) == 3


def test_get_statistics(store):
    stats = store.get_statistics()
    assert stats["total_nodes"] == 4
    assert stats["total_edges"] == 3
    assert "Department" in stats["node_types"]
    assert "WORKS_IN" in stats["edge_types"]


def test_clear(store):
    store.clear()
    assert store.get_statistics()["total_nodes"] == 0


def test_persist_and_load(store, tmp_path):
    path = str(tmp_path / "test_graph.gpickle")
    store.persist(path)

    new_store = NetworkXGraphStore()
    new_store.load(path)
    assert new_store.get_statistics()["total_nodes"] == 4
