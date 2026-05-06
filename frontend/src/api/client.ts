const API_BASE = '/api';

export interface QueryRequest {
  query: string;
  max_depth?: number;
  retrieval_mode?: string;
}

export interface SubgraphInfo {
  node_count: number;
  edge_count: number;
  matched_terms: string[];
}

export interface QueryResponse {
  query: string;
  answer: string;
  subgraph: SubgraphInfo;
  vector_chunks_used: number;
  retrieval_mode: string;
  context_preview: string;
}

export interface GraphNode {
  id: string;
  node_type?: string;
  name?: string;
  [key: string]: any;
}

export interface GraphEdge {
  source: string;
  target: string;
  relation: string;
  [key: string]: any;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  statistics: Record<string, any>;
}

export interface InsightsResponse {
  quarterly_revenue: Array<{ quarter: string; revenue: number }>;
  top_products: Array<{ product_id: string; product_name: string; total_revenue: number; transaction_count: number }>;
  top_customers: Array<{ customer_id: string; customer_name: string; total_spend: number; purchase_count: number }>;
  department_performance: Array<{ department_name: string; total_revenue: number; sales_count: number; active_sellers: number; revenue_per_seller: number }>;
  regional_distribution: Array<{ region_name: string; total_revenue: number; customer_count: number }>;
  category_breakdown: Array<{ category_name: string; total_revenue: number; transaction_count: number }>;
  graph_statistics: Record<string, any>;
}

export interface HealthResponse {
  status: string;
  graph_loaded: boolean;
  llm_provider: string;
  graph_backend: string;
  retrieval_mode: string;
  node_count: number;
  edge_count: number;
}

export async function queryGraph(request: QueryRequest): Promise<QueryResponse> {
  const res = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!res.ok) throw new Error(`Query failed: ${res.statusText}`);
  return res.json();
}

export async function getGraph(): Promise<GraphResponse> {
  const res = await fetch(`${API_BASE}/graph`);
  if (!res.ok) throw new Error(`Failed to load graph: ${res.statusText}`);
  return res.json();
}

export async function getInsights(): Promise<InsightsResponse> {
  const res = await fetch(`${API_BASE}/insights`);
  if (!res.ok) throw new Error(`Failed to load insights: ${res.statusText}`);
  return res.json();
}

export async function getHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}
