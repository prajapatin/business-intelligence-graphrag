from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


class BaseGraphStore(ABC):
    """Abstract base class for knowledge graph storage backends."""

    @abstractmethod
    def add_node(self, node_id: str, node_type: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """Add a node to the graph."""
        ...

    @abstractmethod
    def add_edge(self, source_id: str, target_id: str, relation: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """Add an edge (relationship) between two nodes."""
        ...

    @abstractmethod
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a node and its properties."""
        ...

    @abstractmethod
    def get_neighbors(self, node_id: str, max_depth: int = 1) -> List[Dict[str, Any]]:
        """Get neighboring nodes up to max_depth hops away."""
        ...

    @abstractmethod
    def search_nodes(self, query: str, node_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search nodes by name/property substring match."""
        ...

    @abstractmethod
    def get_subgraph(self, node_ids: List[str], max_depth: int = 1) -> Dict[str, Any]:
        """Get a subgraph around the specified nodes.

        Returns:
            Dict with "nodes" and "edges" keys.
        """
        ...

    @abstractmethod
    def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Return all nodes in the graph."""
        ...

    @abstractmethod
    def get_all_edges(self) -> List[Dict[str, Any]]:
        """Return all edges in the graph."""
        ...

    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """Return graph statistics (node count, edge count, types, etc.)."""
        ...

    @abstractmethod
    def persist(self, path: str) -> None:
        """Persist the graph to disk."""
        ...

    @abstractmethod
    def load(self, path: str) -> None:
        """Load the graph from disk."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Remove all nodes and edges."""
        ...
