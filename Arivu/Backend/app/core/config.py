"""Application configuration loaded from environment variables."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All settings with sensible local-first defaults."""

    model_config = {"env_prefix": "ARIVU_", "env_file": ".env", "extra": "ignore"}

    # ── General ───────────────────────────────────────────
    app_name: str = "Arivu RAG Backend"
    debug: bool = False
    data_dir: Path = Path("data")

    # ── Server ────────────────────────────────────────────
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"  # Comma-separated list

    # ── Database ──────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///data/arivu.db"

    # ── Embedding ─────────────────────────────────────────
    embedding_backend: Literal["local", "openai"] = "local"
    local_embedding_model: str = "all-MiniLM-L6-v2"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_api_key: str = ""

    # ── Vector store ──────────────────────────────────────
    vector_backend: Literal["chroma"] = "chroma"

    # ── LLM ───────────────────────────────────────────────
    llm_backend: Literal["ollama", "openai"] = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    openai_chat_model: str = "gpt-4o-mini"

    # ── Chunking defaults ─────────────────────────────────
    default_chunk_size: int = 1000
    default_chunk_overlap: int = 200

    # ── Retrieval defaults ────────────────────────────────
    default_top_k: int = 5

    # ── Reranking ─────────────────────────────────────
    reranker_enabled: bool = True
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-12-v2"

    # ── RAG Quality ───────────────────────────────────
    default_min_score: float = 0.0
    default_max_context_tokens: int = 6000

    # ── Web Search ────────────────────────────────────
    web_search_backend: Literal["tavily"] = "tavily"
    tavily_api_key: str = ""
    web_search_results_count: int = 3
    web_search_enabled_default: bool = False


settings = Settings()
