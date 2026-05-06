import os

from fastapi import APIRouter, HTTPException
from loguru import logger

from config.settings import settings
from src.api.schemas import (
    GraphResponse,
    HealthResponse,
    InsightsResponse,
    QueryRequest,
    QueryResponse,
)
from src.graph import create_graph_store
from src.llm import create_llm_provider
from src.generation.answer_generator import AnswerGenerator
from src.analytics.trend_detector import TrendDetector
from src.vectorstore.chroma_store import ChromaVectorStore


router = APIRouter()

# --- Singletons (initialized on first use) ---
_graph_store = None
_llm = None
_vector_store = None
_answer_generator = None
_trend_detector = None


def _get_graph_store():
    global _graph_store
    if _graph_store is None:
        _graph_store = create_graph_store()
        persist_path = settings.graph_persist_path
        if os.path.exists(persist_path):
            _graph_store.load(persist_path)
            stats = _graph_store.get_statistics()
            logger.info(f"Graph loaded: {stats['total_nodes']} nodes, {stats['total_edges']} edges")
        else:
            logger.warning(f"No persisted graph found at {persist_path}")
    return _graph_store


def _get_llm():
    global _llm
    if _llm is None:
        _llm = create_llm_provider()
        logger.info(f"LLM provider initialized: {settings.llm_provider}")
    return _llm


def _get_vector_store():
    global _vector_store
    if _vector_store is None:
        persist_path = settings.vector_persist_path
        if os.path.exists(persist_path):
            _vector_store = ChromaVectorStore(persist_directory=persist_path)
            logger.info(f"Vector store loaded: {_vector_store.count()} chunks")
        else:
            logger.warning(f"No vector store found at {persist_path}")
    return _vector_store


def _get_answer_generator():
    global _answer_generator
    if _answer_generator is None:
        _answer_generator = AnswerGenerator(
            llm=_get_llm(),
            graph_store=_get_graph_store(),
            vector_store=_get_vector_store(),
            retrieval_mode=settings.retrieval_mode,
        )
    return _answer_generator


def _get_trend_detector():
    global _trend_detector
    if _trend_detector is None:
        _trend_detector = TrendDetector(_get_graph_store())
    return _trend_detector


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint."""
    graph = _get_graph_store()
    stats = graph.get_statistics()
    return HealthResponse(
        status="healthy",
        graph_loaded=stats["total_nodes"] > 0,
        llm_provider=settings.llm_provider,
        graph_backend=settings.graph_backend,
        retrieval_mode=settings.retrieval_mode,
        node_count=stats["total_nodes"],
        edge_count=stats["total_edges"],
    )


@router.post("/query", response_model=QueryResponse)
def query_graph(request: QueryRequest):
    """Answer a natural language BI question using GraphRAG."""
    try:
        generator = _get_answer_generator()
        result = generator.answer(
            request.query,
            max_depth=request.max_depth,
            retrieval_mode=request.retrieval_mode,
        )
        return QueryResponse(**result)
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph", response_model=GraphResponse)
def get_full_graph():
    """Return the full knowledge graph for visualization."""
    graph = _get_graph_store()
    nodes = graph.get_all_nodes()
    edges = graph.get_all_edges()
    stats = graph.get_statistics()
    return GraphResponse(nodes=nodes, edges=edges, statistics=stats)


@router.get("/insights", response_model=InsightsResponse)
def get_insights():
    """Return pre-computed business insights from the graph."""
    detector = _get_trend_detector()
    insights = detector.get_all_insights()
    return InsightsResponse(**insights)
