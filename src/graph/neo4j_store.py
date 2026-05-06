from typing import Any, Dict, List, Optional

from src.graph.base_store import BaseGraphStore
from config.settings import settings


class Neo4jGraphStore(BaseGraphStore):
    """Neo4j-backed graph store (optional backend)."""

    def __init__(self):
        from neo4j import GraphDatabase
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )

    def _run_query(self, query: str, parameters: Optional[Dict] = None) -> List[Dict]:
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def add_node(self, node_id: str, node_type: str, properties: Optional[Dict[str, Any]] = None) -> None:
        props = properties or {}
        props["node_type"] = node_type
        prop_str = ", ".join(f"n.{k} = ${k}" for k in props)
        query = f"MERGE (n {{id: $node_id}}) SET {prop_str}"
        props["node_id"] = node_id
        self._run_query(query, props)

    def add_edge(self, source_id: str, target_id: str, relation: str, properties: Optional[Dict[str, Any]] = None) -> None:
        props = properties or {}
        prop_str = ""
        if props:
            prop_str = " SET " + ", ".join(f"r.{k} = ${k}" for k in props)
        query = (
            f"MATCH (a {{id: $source_id}}), (b {{id: $target_id}}) "
            f"MERGE (a)-[r:{relation.replace(' ', '_').upper()}]->(b){prop_str}"
        )
        params = {"source_id": source_id, "target_id": target_id, **props}
        self._run_query(query, params)

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        results = self._run_query("MATCH (n {id: $node_id}) RETURN n", {"node_id": node_id})
        if not results:
            return None
        node = dict(results[0]["n"])
        node["id"] = node_id
        return node

    def get_neighbors(self, node_id: str, max_depth: int = 1) -> List[Dict[str, Any]]:
        query = (
            f"MATCH (start {{id: $node_id}})-[*1..{max_depth}]-(neighbor) "
            f"WHERE neighbor.id <> $node_id "
            f"RETURN DISTINCT neighbor"
        )
        results = self._run_query(query, {"node_id": node_id})
        neighbors = []
        for record in results:
            node_data = dict(record["neighbor"])
            neighbors.append(node_data)
        return neighbors

    def search_nodes(self, query: str, node_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        type_filter = ""
        if node_type:
            type_filter = f" AND n.node_type = '{node_type}'"
        cypher = (
            f"MATCH (n) WHERE toLower(n.id) CONTAINS toLower($query) "
            f"OR toLower(n.name) CONTAINS toLower($query){type_filter} "
            f"RETURN n LIMIT $limit"
        )
        results = self._run_query(cypher, {"query": query, "limit": limit})
        return [dict(r["n"]) for r in results]

    def get_subgraph(self, node_ids: List[str], max_depth: int = 1) -> Dict[str, Any]:
        query = (
            f"MATCH (n) WHERE n.id IN $node_ids "
            f"CALL apoc.path.subgraphAll(n, {{maxLevel: {max_depth}}}) YIELD nodes, relationships "
            f"RETURN nodes, relationships"
        )
        try:
            results = self._run_query(query, {"node_ids": node_ids})
        except Exception:
            # Fallback without APOC
            nodes_list = []
            for nid in node_ids:
                node = self.get_node(nid)
                if node:
                    nodes_list.append(node)
                neighbors = self.get_neighbors(nid, max_depth)
                nodes_list.extend(neighbors)

            seen_ids = set()
            unique_nodes = []
            for n in nodes_list:
                nid = n.get("id", "")
                if nid not in seen_ids:
                    seen_ids.add(nid)
                    unique_nodes.append(n)

            return {"nodes": unique_nodes, "edges": []}

        nodes = []
        edges = []
        for record in results:
            for node in record.get("nodes", []):
                nodes.append(dict(node))
            for rel in record.get("relationships", []):
                edges.append({
                    "source": rel.start_node["id"],
                    "target": rel.end_node["id"],
                    "relation": rel.type,
                })
        return {"nodes": nodes, "edges": edges}

    def get_all_nodes(self) -> List[Dict[str, Any]]:
        results = self._run_query("MATCH (n) RETURN n LIMIT 5000")
        return [dict(r["n"]) for r in results]

    def get_all_edges(self) -> List[Dict[str, Any]]:
        results = self._run_query(
            "MATCH (a)-[r]->(b) RETURN a.id AS source, b.id AS target, type(r) AS relation LIMIT 10000"
        )
        return results

    def get_statistics(self) -> Dict[str, Any]:
        node_count = self._run_query("MATCH (n) RETURN count(n) AS cnt")[0]["cnt"]
        edge_count = self._run_query("MATCH ()-[r]->() RETURN count(r) AS cnt")[0]["cnt"]
        node_types = self._run_query(
            "MATCH (n) RETURN n.node_type AS type, count(*) AS cnt"
        )
        edge_types = self._run_query(
            "MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS cnt"
        )
        return {
            "total_nodes": node_count,
            "total_edges": edge_count,
            "node_types": {r["type"]: r["cnt"] for r in node_types},
            "edge_types": {r["type"]: r["cnt"] for r in edge_types},
        }

    def persist(self, path: str) -> None:
        pass  # Neo4j persists automatically

    def load(self, path: str) -> None:
        pass  # Neo4j loads from its own storage

    def clear(self) -> None:
        self._run_query("MATCH (n) DETACH DELETE n")
