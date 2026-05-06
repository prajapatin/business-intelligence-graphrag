from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Business Intelligence - GraphRAG & Vector RAG",
        description="GraphRAG-powered BI system for identifying trends and relationships in corporate data",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS for React frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api")

    return app


app = create_app()
