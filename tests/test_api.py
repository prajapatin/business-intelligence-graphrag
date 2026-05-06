import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from src.api.app import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset module-level singletons before each test."""
    import src.api.routes as routes
    routes._graph_store = None
    routes._llm = None
    routes._vector_store = None
    routes._answer_generator = None
    routes._trend_detector = None


def test_health_endpoint(client):
    with patch("src.api.routes._get_graph_store") as mock_gs:
        mock_store = MagicMock()
        mock_store.get_statistics.return_value = {
            "total_nodes": 100,
            "total_edges": 500,
            "node_types": {},
            "edge_types": {},
        }
        mock_gs.return_value = mock_store

        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["node_count"] == 100


def test_graph_endpoint(client):
    with patch("src.api.routes._get_graph_store") as mock_gs:
        mock_store = MagicMock()
        mock_store.get_all_nodes.return_value = [{"id": "N1", "node_type": "Test", "name": "Node1"}]
        mock_store.get_all_edges.return_value = [{"source": "N1", "target": "N2", "relation": "REL"}]
        mock_store.get_statistics.return_value = {"total_nodes": 1, "total_edges": 1, "node_types": {}, "edge_types": {}}
        mock_gs.return_value = mock_store

        response = client.get("/api/graph")
        assert response.status_code == 200
        data = response.json()
        assert len(data["nodes"]) == 1
        assert len(data["edges"]) == 1


def test_query_endpoint(client):
    with patch("src.api.routes._get_answer_generator") as mock_gen:
        mock_generator = MagicMock()
        mock_generator.answer.return_value = {
            "query": "test query",
            "answer": "This is the answer",
            "subgraph": {"node_count": 5, "edge_count": 10, "matched_terms": ["test"]},
            "vector_chunks_used": 3,
            "retrieval_mode": "hybrid",
            "context_preview": "context...",
        }
        mock_gen.return_value = mock_generator

        response = client.post("/api/query", json={"query": "test query"})
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "This is the answer"


def test_insights_endpoint(client):
    with patch("src.api.routes._get_trend_detector") as mock_td:
        mock_detector = MagicMock()
        mock_detector.get_all_insights.return_value = {
            "quarterly_revenue": [{"quarter": "Q1-2023", "revenue": 50000}],
            "top_products": [],
            "top_customers": [],
            "department_performance": [],
            "regional_distribution": [],
            "category_breakdown": [],
            "graph_statistics": {"total_nodes": 100, "total_edges": 500},
        }
        mock_td.return_value = mock_detector

        response = client.get("/api/insights")
        assert response.status_code == 200
        data = response.json()
        assert len(data["quarterly_revenue"]) == 1
