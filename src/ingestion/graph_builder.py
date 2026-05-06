from typing import Any, Dict, List

from loguru import logger

from src.graph.base_store import BaseGraphStore


def build_graph(
    graph_store: BaseGraphStore,
    extracted: Dict[str, List[Dict[str, Any]]],
) -> None:
    """Populate the graph store from extracted entities and relationships.

    Args:
        graph_store: The target graph store.
        extracted: Dict with "entities" and "relationships" keys.
    """
    entities = extracted.get("entities", [])
    relationships = extracted.get("relationships", [])

    # Add entities as nodes
    for entity in entities:
        node_id = entity["id"]
        node_type = entity["type"]
        properties = {"name": entity["name"]}
        if entity.get("properties"):
            properties.update(entity["properties"])
        graph_store.add_node(node_id, node_type, properties)

    logger.info(f"Added {len(entities)} nodes to graph")

    # Add relationships as edges
    for rel in relationships:
        graph_store.add_edge(
            source_id=rel["source"],
            target_id=rel["target"],
            relation=rel["relation"],
            properties=rel.get("properties"),
        )

    logger.info(f"Added {len(relationships)} edges to graph")

    stats = graph_store.get_statistics()
    logger.info(f"Graph statistics: {stats}")
