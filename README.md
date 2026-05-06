# Business Intelligence - GraphRAG & Vector RAG

**Identify trends and relationships in corporate data using Hybrid RAG - combining Knowledge Graph retrieval with Vector semantic search.**

A production-style reference project that builds a knowledge graph and a vector store from corporate data (sales, employees, departments, products, customers, and business reports). It answers natural language BI questions by fusing structured graph context with semantically retrieved document insights, then generating data-driven answers via LLM.

## Architecture

```
┌──────────────────────┐      ┌──────────────────────┐
│   React Frontend     │◄────►│   FastAPI Backend    │
│  (Graph viz + Chat)  │      │   /query, /graph,    │
│  TailwindCSS +       │      │   /insights, /health │
│  Canvas Graph        │      └──────────┬───────────┘
└──────────────────────┘                 │
                              ┌──────────▼───────────┐
                              │  Hybrid RAG Engine   │
                              │  ┌─────────────────┐ │
                              │  │ Graph Retriever │ │  ← Subgraph retrieval
                              │  │ Vector Retriever│ │  ← Semantic search
                              │  │ Hybrid Fusion   │ │  ← Merge both contexts
                              │  │ Answer Generator│ │  ← LLM generates answer
                              │  └─────────────────┘ │
                              └──────────┬───────────┘
                      ┌──────────────────┼─────────────────┐
                      │                  │                 │
              ┌───────▼──────┐  ┌────────▼───────┐ ┌───────▼──────┐
              │ LLM Provider │  │ Graph + Vector │ │  Corporate   │
              │ (abstract)   │  │ NetworkX/Neo4j │ │  Data (CSV + │
              │ Groq/OpenAI/ │  │ + ChromaDB     │ │  Reports)    │
              │ Ollama       │  └────────────────┘ └──────────────┘
              └──────────────┘
```

**Key insight:** This is a **Hybrid RAG** system combining two retrieval strategies:
- **Graph retrieval** - Keyword-matched subgraph traversal over a knowledge graph of entities and relationships
- **Vector retrieval** - Semantic similarity search over embedded business reports using ChromaDB + sentence-transformers

Both contexts are fused and fed to the LLM, yielding richer, more accurate answers than either method alone.

## Project Structure

```
business-intelligence-graphrag/
├── README.md                      <- You are here
├── requirements.txt               <- Python dependencies
├── pyproject.toml                 <- Project metadata
├── .env.example                   <- Environment template
├── config/
│   └── settings.py                <- Central config (env-overridable)
├── data/
│   └── synthetic/                 <- Generated CSV data + reports
│       ├── sales_transactions.csv
│       ├── employees.csv
│       ├── departments.csv
│       ├── products.csv
│       ├── customers.csv
│       └── reports/               <- Business reports for vector search
│           ├── quarterly_report_*.txt
│           ├── dept_memo_*.txt
│           ├── product_brief_*.txt
│           ├── regional_summary_*.txt
│           ├── case_study_*.txt
│           └── annual_review_*.txt
├── scripts/
│   ├── generate_data.py           <- Synthetic data generator
│   ├── build_graph.py             <- Build knowledge graph from CSVs
│   └── query_cli.py               <- Interactive CLI for queries
├── src/
│   ├── llm/
│   │   ├── base_provider.py       <- Abstract LLM provider
│   │   ├── openai_provider.py     <- OpenAI implementation
│   │   ├── groq_provider.py       <- Groq implementation
│   │   ├── ollama_provider.py     <- Ollama implementation
│   │   └── factory.py             <- Provider factory
│   ├── graph/
│   │   ├── base_store.py          <- Abstract graph store
│   │   ├── networkx_store.py      <- NetworkX (default, in-memory)
│   │   ├── neo4j_store.py         <- Neo4j (optional, persistent)
│   │   └── factory.py             <- Store factory
│   ├── ingestion/
│   │   ├── csv_loader.py          <- Load CSV data
│   │   ├── entity_extractor.py    <- Extract entities & relationships
│   │   └── graph_builder.py       <- Populate graph store
│   ├── vectorstore/
│   │   ├── base_store.py          <- Abstract vector store
│   │   ├── chroma_store.py        <- ChromaDB + sentence-transformers
│   │   └── document_chunker.py    <- Split reports into embeddable chunks
│   ├── retrieval/
│   │   ├── graph_retriever.py     <- Subgraph retrieval for queries
│   │   ├── vector_retriever.py    <- Semantic search over reports
│   │   ├── hybrid_retriever.py    <- Fuse graph + vector contexts
│   │   └── context_builder.py     <- Format graph context for LLM
│   ├── generation/
│   │   └── answer_generator.py    <- Full Hybrid RAG pipeline
│   ├── analytics/
│   │   └── trend_detector.py      <- Graph-based trend detection
│   └── api/
│       ├── app.py                 <- FastAPI application
│       ├── routes.py              <- API endpoints
│       └── schemas.py             <- Pydantic models
├── frontend/                      <- React + TailwindCSS UI
│   ├── package.json
│   └── src/
│       ├── App.tsx
│       ├── api/client.ts
│       └── components/
│           ├── Layout.tsx
│           ├── ChatPanel.tsx      <- NL query interface
│           ├── GraphView.tsx      <- Interactive graph visualization
│           └── InsightsPanel.tsx  <- Charts & dashboards
└── tests/
    ├── test_llm_providers.py
    ├── test_graph_store.py
    ├── test_ingestion.py
    ├── test_retrieval.py
    ├── test_vector_store.py       <- Vector store + chunker tests
    ├── test_hybrid_retriever.py   <- Hybrid retrieval tests
    └── test_api.py
```

## Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)
- An API key for one of: **Groq** (free tier available), **OpenAI**, or **Ollama** running locally

## Quick Start

### 1. Install & setup virtual environment

```bash
cd business-intelligence-graphrag
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your API key and preferred provider
```

### 3. Generate synthetic data

```bash
python scripts/generate_data.py
```

This creates 6 departments, 8 products, 60 employees, 80 customers, 500 sales transactions across 2023-2024 with seasonal trends, and **~36 business report text files** (quarterly reports, department memos, product briefs, regional summaries, customer case studies, annual reviews).

### 4. Build the knowledge graph

```bash
python scripts/build_graph.py
```

Extracts entities and relationships from the CSV data, builds the knowledge graph, **and indexes business reports into the ChromaDB vector store** at `rag_data/vector_store/`.

### 5. Start the API server

```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

### 6. Start the React frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

### 7. (Optional) Use the CLI

```bash
python scripts/query_cli.py
```

## API Reference

### GET /api/health

```bash
curl http://localhost:8000/api/health
```

```json
{
  "status": "healthy",
  "graph_loaded": true,
  "llm_provider": "groq",
  "graph_backend": "networkx",
  "retrieval_mode": "hybrid",
  "node_count": 175,
  "edge_count": 885
}
```

### POST /api/query

Ask a natural language BI question:

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the top-selling products by revenue?"}'
```

```json
{
  "query": "What are the top-selling products by revenue?",
  "answer": "Based on the knowledge graph and business reports...",
  "subgraph": {
    "node_count": 60,
    "edge_count": 138,
    "matched_terms": ["top-selling", "products", "revenue"]
  },
  "vector_chunks_used": 5,
  "retrieval_mode": "hybrid",
  "context_preview": "=== KNOWLEDGE GRAPH CONTEXT === ... === DOCUMENT CONTEXT (from business reports) === ..."
}
```

### GET /api/graph

Returns the full knowledge graph for visualization.

### GET /api/insights

Returns pre-computed business insights (quarterly revenue, top products, department performance, regional distribution, etc.).

## How Hybrid RAG Works

1. **Ingest** — CSV data is loaded and entities are extracted. Business reports are generated from the same data.

2. **Build** — Entities become graph nodes and edges. Report text files are chunked and embedded into ChromaDB.

3. **Retrieve (Hybrid)** — On query:
   - **Graph path**: Keywords -> match nodes -> traverse subgraph -> structured context
   - **Vector path**: Query embedding -> top-K similar report chunks -> semantic context

4. **Fuse** — Both contexts are merged: `[KNOWLEDGE GRAPH CONTEXT]` + `[DOCUMENT CONTEXT]`

5. **Generate** — The LLM receives the fused context + your question and produces a grounded, data-driven answer.

```
Question: "Which department generates the most sales?"
    │
    ├─► [Graph] Match nodes -> 60 nodes, 103 edges -> structured context
    │
    ├─► [Vector] Embed query -> top-5 report chunks -> semantic context
    │
    ▼
[Fuse contexts] -> 10K chars graph + 5K chars reports
    │
    ▼
[LLM Generate] -> "The Sales department leads with $320K in revenue..."
```

### Retrieval Modes

| Mode | Graph | Vector | Use case |
|------|-------|--------|----------|
| `hybrid` (default) | ✅ | ✅ | Best quality — structured + semantic context |
| `graph_only` | ✅ | ❌ | Fast, relationship-focused answers |
| `vector_only` | ❌ | ✅ | Narrative/report-focused answers |

## Configuration

All settings in `config/settings.py` are overridable via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `groq` | `openai`, `groq`, or `ollama` |
| `GROQ_API_KEY` | - | Groq API key |
| `OPENAI_API_KEY` | - | OpenAI API key |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `GRAPH_BACKEND` | `networkx` | `networkx` or `neo4j` |
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j connection URI |
| `GRAPH_PERSIST_PATH` | `rag_data/knowledge_graph.gpickle` | Graph file path |
| `RETRIEVAL_MODE` | `hybrid` | `hybrid`, `graph_only`, or `vector_only` |
| `VECTOR_PERSIST_PATH` | `rag_data/vector_store` | ChromaDB persistence path |
| `VECTOR_TOP_K` | `5` | Number of vector chunks to retrieve |

## Running Tests

Tests use mocks - no GPU, LLM API key, or Neo4j required:

```bash
pytest tests/ -v
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| **LLM** | Groq / OpenAI / Ollama (abstract provider) |
| **Graph** | NetworkX (default) / Neo4j (optional) |
| **Vector** | ChromaDB + sentence-transformers (all-MiniLM-L6-v2) |
| **Backend** | FastAPI, Uvicorn, Pydantic |
| **Frontend** | React 18, Vite, TailwindCSS, Recharts |
| **Data** | Pandas, Faker |
| **Testing** | pytest, httpx |

## License

MIT - This project is provided for educational and demonstration purposes.
