from typing import Any, Dict, List


class ContextBuilder:
    """Builds textual context from a subgraph for LLM prompting."""

    def build(self, subgraph: Dict[str, Any], max_chars: int = 10000) -> str:
        """Convert a subgraph into a structured text context for the LLM.

        Args:
            subgraph: Dict with "nodes" and "edges" keys.
            max_chars: Maximum character length of the output context.

        Returns:
            Formatted text describing the graph context.
        """
        nodes = subgraph.get("nodes", [])
        edges = subgraph.get("edges", [])

        if not nodes:
            return "No relevant data found in the knowledge graph."

        lines = []
        lines.append("=== KNOWLEDGE GRAPH CONTEXT ===\n")

        # Group nodes by type
        nodes_by_type: Dict[str, List[Dict]] = {}
        node_lookup: Dict[str, Dict] = {}
        for node in nodes:
            ntype = node.get("node_type", "Unknown")
            nodes_by_type.setdefault(ntype, []).append(node)
            node_lookup[node.get("id", "")] = node

        # Describe entities
        lines.append("## Entities\n")
        for ntype, type_nodes in sorted(nodes_by_type.items()):
            lines.append(f"### {ntype}s ({len(type_nodes)})")
            for node in type_nodes[:15]:  # Cap per type
                name = node.get("name", node.get("id", "?"))
                props = {k: v for k, v in node.items() if k not in ("id", "name", "node_type")}
                prop_str = ", ".join(f"{k}={v}" for k, v in props.items()) if props else ""
                lines.append(f"  - {name} [{node.get('id', '')}] {prop_str}")
            lines.append("")

        # Describe relationships
        if edges:
            lines.append("## Relationships\n")
            # Aggregate by relation type
            by_relation: Dict[str, List[Dict]] = {}
            for edge in edges:
                rel = edge.get("relation", "RELATED_TO")
                by_relation.setdefault(rel, []).append(edge)

            for rel, rel_edges in sorted(by_relation.items()):
                lines.append(f"### {rel} ({len(rel_edges)} connections)")
                for edge in rel_edges[:20]:  # Cap
                    src = node_lookup.get(edge["source"], {})
                    tgt = node_lookup.get(edge["target"], {})
                    src_name = src.get("name", edge["source"])
                    tgt_name = tgt.get("name", edge["target"])
                    props = {k: v for k, v in edge.items() if k not in ("source", "target", "relation")}
                    prop_str = f" ({', '.join(f'{k}={v}' for k, v in props.items())})" if props else ""
                    lines.append(f"  - {src_name} --[{rel}]--> {tgt_name}{prop_str}")
                lines.append("")

        lines.append("=== END CONTEXT ===")
        result = "\n".join(lines)
        if len(result) > max_chars:
            result = result[:max_chars] + "\n... [context truncated]\n=== END CONTEXT ==="
        return result
