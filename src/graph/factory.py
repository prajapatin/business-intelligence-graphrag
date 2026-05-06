from src.graph.base_store import BaseGraphStore
from config.settings import settings


def create_graph_store() -> BaseGraphStore:
    """Create a graph store based on the configured settings."""
    backend = settings.graph_backend

    if backend == "networkx":
        from src.graph.networkx_store import NetworkXGraphStore
        return NetworkXGraphStore()
    elif backend == "neo4j":
        from src.graph.neo4j_store import Neo4jGraphStore
        return Neo4jGraphStore()
    else:
        raise ValueError(f"Unknown graph backend: {backend}. Choose from: networkx, neo4j")
