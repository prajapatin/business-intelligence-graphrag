import os
import pickle
from collections import Counter
from typing import Any, Dict, List, Optional

import networkx as nx

from src.graph.base_store import BaseGraphStore


class NetworkXGraphStore(BaseGraphStore):
    """In-memory graph store backed by NetworkX."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node_id: str, node_type: str, properties: Optional[Dict[str, Any]] = None) -> None:
        attrs = {"node_type": node_type}
        if properties:
            attrs.update(properties)
        self.graph.add_node(node_id, **attrs)

    def add_edge(self, source_id: str, target_id: str, relation: str, properties: Optional[Dict[str, Any]] = None) -> None:
        attrs = {"relation": relation}
        if properties:
            attrs.update(properties)
        self.graph.add_edge(source_id, target_id, **attrs)

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        if node_id not in self.graph:
            return None
        data = dict(self.graph.nodes[node_id])
        data["id"] = node_id
        return data

    def get_neighbors(self, node_id: str, max_depth: int = 1) -> List[Dict[str, Any]]:
        if node_id not in self.graph:
            return []

        visited = set()
        neighbors = []
        queue = [(node_id, 0)]

        while queue:
            current, depth = queue.pop(0)
            if current in visited or depth > max_depth:
                continue
            visited.add(current)

            if current != node_id:
                node_data = dict(self.graph.nodes[current])
                node_data["id"] = current
                node_data["depth"] = depth
                neighbors.append(node_data)

            if depth < max_depth:
                for succ in self.graph.successors(current):
                    if succ not in visited:
                        queue.append((succ, depth + 1))
                for pred in self.graph.predecessors(current):
                    if pred not in visited:
                        queue.append((pred, depth + 1))

        return neighbors

    def search_nodes(self, query: str, node_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        results = []
        query_lower = query.lower()

        for node_id, data in self.graph.nodes(data=True):
            if node_type and data.get("node_type") != node_type:
                continue

            searchable = f"{node_id} {data.get('name', '')} {data.get('node_type', '')}".lower()
            if query_lower in searchable:
                node_data = dict(data)
                node_data["id"] = node_id
                results.append(node_data)

            if len(results) >= limit:
                break

        return results

    def get_subgraph(self, node_ids: List[str], max_depth: int = 1) -> Dict[str, Any]:
        all_node_ids = set()
        for nid in node_ids:
            if nid in self.graph:
                all_node_ids.add(nid)
                neighbors = self.get_neighbors(nid, max_depth)
                for n in neighbors:
                    all_node_ids.add(n["id"])

        nodes = []
        for nid in all_node_ids:
            node_data = dict(self.graph.nodes[nid])
            node_data["id"] = nid
            nodes.append(node_data)

        edges = []
        for src, tgt, data in self.graph.edges(data=True):
            if src in all_node_ids and tgt in all_node_ids:
                edge_data = dict(data)
                edge_data["source"] = src
                edge_data["target"] = tgt
                edges.append(edge_data)

        return {"nodes": nodes, "edges": edges}

    def get_all_nodes(self) -> List[Dict[str, Any]]:
        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            node_data = dict(data)
            node_data["id"] = node_id
            nodes.append(node_data)
        return nodes

    def get_all_edges(self) -> List[Dict[str, Any]]:
        edges = []
        for src, tgt, data in self.graph.edges(data=True):
            edge_data = dict(data)
            edge_data["source"] = src
            edge_data["target"] = tgt
            edges.append(edge_data)
        return edges

    def get_statistics(self) -> Dict[str, Any]:
        node_types = Counter(data.get("node_type", "unknown") for _, data in self.graph.nodes(data=True))
        edge_types = Counter(data.get("relation", "unknown") for _, _, data in self.graph.edges(data=True))

        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "node_types": dict(node_types),
            "edge_types": dict(edge_types),
        }

    def persist(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self.graph, f)

    def load(self, path: str) -> None:
        with open(path, "rb") as f:
            self.graph = pickle.load(f)

    def clear(self) -> None:
        self.graph.clear()
