from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal


class Settings(BaseSettings):
    # LLM Provider
    llm_provider: Literal["openai", "groq", "ollama"] = "groq"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Groq
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    # Graph Backend
    graph_backend: Literal["networkx", "neo4j"] = "networkx"

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Graph persistence
    graph_persist_path: str = "rag_data/knowledge_graph.gpickle"

    # Vector store
    vector_persist_path: str = "rag_data/vector_store"
    vector_top_k: int = 5
    retrieval_mode: Literal["hybrid", "graph_only", "vector_only"] = "hybrid"
    reports_directory: str = "data/synthetic/reports"

    # LLM generation
    temperature: float = 0.3
    max_tokens: int = 1024

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
