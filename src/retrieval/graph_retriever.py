from typing import Any, Dict, List, Optional

from loguru import logger

from src.graph.base_store import BaseGraphStore


class GraphRetriever:
    """Retrieves relevant subgraph context for a given query."""

    def __init__(self, graph_store: BaseGraphStore):
        self.graph_store = graph_store

    def retrieve(self, query: str, max_depth: int = 2, limit: int = 12) -> Dict[str, Any]:
        """Find relevant nodes and return their subgraph neighborhood.

        Strategy:
        1. Search for nodes matching query keywords
        2. Expand to neighbor nodes up to max_depth
        3. Return subgraph with nodes + edges
        """
        # Extract search terms from query
        search_terms = self._extract_search_terms(query)
        logger.debug(f"Search terms: {search_terms}")

        # Find matching nodes
        matched_nodes = []
        for term in search_terms:
            results = self.graph_store.search_nodes(term, limit=limit)
            matched_nodes.extend(results)

        # If few results, try searching by node type keywords
        type_keywords = {
            "product": "Product", "products": "Product",
            "department": "Department", "departments": "Department",
            "employee": "Employee", "employees": "Employee",
            "customer": "Customer", "customers": "Customer",
            "region": "Region", "regions": "Region",
            "quarter": "Quarter", "quarters": "Quarter",
            "category": "Category", "categories": "Category",
        }
        if len(matched_nodes) < 3:
            for term in search_terms:
                if term.lower() in type_keywords:
                    type_results = self.graph_store.search_nodes(
                        "", node_type=type_keywords[term.lower()], limit=limit
                    )
                    matched_nodes.extend(type_results)

        # Deduplicate by ID
        seen = set()
        unique_nodes = []
        for node in matched_nodes:
            nid = node.get("id", "")
            if nid not in seen:
                seen.add(nid)
                unique_nodes.append(node)

        if not unique_nodes:
            logger.warning(f"No matching nodes found for query: {query}")
            return {"nodes": [], "edges": [], "matched_terms": search_terms}

        # Get subgraph around matched nodes
        node_ids = [n["id"] for n in unique_nodes[:limit]]
        subgraph = self.graph_store.get_subgraph(node_ids, max_depth=max_depth)

        # Cap subgraph size to avoid blowing up LLM context
        max_nodes = 60
        if len(subgraph["nodes"]) > max_nodes:
            subgraph["nodes"] = subgraph["nodes"][:max_nodes]
            kept_ids = {n["id"] for n in subgraph["nodes"]}
            subgraph["edges"] = [
                e for e in subgraph["edges"]
                if e["source"] in kept_ids and e["target"] in kept_ids
            ]

        logger.info(
            f"Retrieved subgraph: {len(subgraph['nodes'])} nodes, "
            f"{len(subgraph['edges'])} edges for query: {query[:80]}"
        )

        subgraph["matched_terms"] = search_terms
        return subgraph

    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract meaningful search terms from a natural language query."""
        stop_words = {
            "what", "which", "who", "how", "is", "are", "was", "were", "the",
            "a", "an", "in", "on", "at", "to", "for", "of", "and", "or", "by",
            "from", "with", "that", "this", "it", "do", "does", "did", "has",
            "have", "had", "be", "been", "being", "can", "could", "will", "would",
            "shall", "should", "may", "might", "must", "about", "between",
            "show", "me", "tell", "give", "find", "list", "get", "most", "top",
            "best", "worst", "highest", "lowest", "total", "all", "any", "each",
            "many", "much", "our", "their", "my", "your", "its",
            "relationships", "relationship", "exist", "exists", "trends", "trend",
            "compare", "versus", "analysis", "analyze", "performance", "data",
        }
        words = query.lower().replace("?", "").replace(",", "").split()
        terms = [w for w in words if w not in stop_words and len(w) > 2]

        # Also try multi-word phrases from the query
        known_phrases = [
            "north america", "asia pacific", "latin america",
            "sales rep", "department head",
            "cloudsync pro", "datavault enterprise", "securenet gateway",
            "analyticsdash", "smartoffice suite", "edgecompute module",
            "ai assistant api", "compliance tracker",
        ]
        query_lower = query.lower()
        for phrase in known_phrases:
            if phrase in query_lower:
                terms.append(phrase)

        return terms if terms else [query.strip()[:50]]
