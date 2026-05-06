from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# --- Request Models ---

class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language BI question", min_length=3)
    max_depth: int = Field(default=2, description="Max graph traversal depth", ge=1, le=4)
    retrieval_mode: Optional[str] = Field(default=None, description="Override retrieval mode: hybrid, graph_only, vector_only")


# --- Response Models ---

class SubgraphInfo(BaseModel):
    node_count: int
    edge_count: int
    matched_terms: List[str]


class QueryResponse(BaseModel):
    query: str
    answer: str
    subgraph: SubgraphInfo
    vector_chunks_used: int = 0
    retrieval_mode: str = "hybrid"
    context_preview: str


class GraphNode(BaseModel):
    id: str
    node_type: Optional[str] = None
    name: Optional[str] = None
    properties: Dict[str, Any] = {}


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str
    properties: Dict[str, Any] = {}


class GraphResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    statistics: Dict[str, Any]


class InsightsResponse(BaseModel):
    quarterly_revenue: List[Dict[str, Any]]
    top_products: List[Dict[str, Any]]
    top_customers: List[Dict[str, Any]]
    department_performance: List[Dict[str, Any]]
    regional_distribution: List[Dict[str, Any]]
    category_breakdown: List[Dict[str, Any]]
    graph_statistics: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    graph_loaded: bool
    llm_provider: str
    graph_backend: str
    retrieval_mode: str
    node_count: int
    edge_count: int
