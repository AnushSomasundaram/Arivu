"""Pydantic request/response schemas — aligned with the Vue frontend types."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ── Projects ──────────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    embedding_model: str | None = "local:all-MiniLM-L6-v2"


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    embedding_model: str | None = None


class ProjectOut(BaseModel):
    id: str
    name: str
    description: str
    embedding_model: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Files (matches frontend FileRecord / UploadResult) ───

FileStatus = Literal[
    "queued", "parsing", "chunking", "embedding", "indexing", "indexed", "failed"
]


class FileRecordOut(BaseModel):
    """Matches the frontend's FileRecord interface."""

    id: str
    filename: str
    size_bytes: int
    status: str
    created_at: datetime
    chunk_count: int | None = None
    mime_type: str | None = None
    added_chunks: int | None = None
    skipped_chunks: int | None = None
    progress: int = 0

    model_config = {"from_attributes": True}


class UploadedItem(BaseModel):
    id: str
    filename: str
    status: str


class UploadResult(BaseModel):
    """Matches the frontend's UploadResult interface."""

    uploaded: list[UploadedItem]
    ingestion_job_id: str | None = None


# ── Query (matches frontend QuerySettings / Source / etc.) ─

class QuerySettingsIn(BaseModel):
    """Matches the frontend's QuerySettings type."""

    k: int = 5
    search_type: Literal["similarity", "mmr"] = "similarity"
    temperature: float = 0.2
    model: str = "llama3"
    chunk_size: int | None = None
    chunk_overlap: int | None = None
    embedding_model: str | None = None
    query_translation: bool | None = False
    show_debug: bool | None = False
    api_key: str | None = None
    base_url: str | None = None

    # RAG quality
    min_score: float | None = None
    enable_reranking: bool | None = None
    max_context_tokens: int | None = None

    # Web search
    web_search_enabled: bool | None = False
    web_search_threshold: float | None = 0.5
    web_search_mode: Literal["fallback", "augment"] | None = "fallback"
    web_search_api_key: str | None = None
    embedding_api_key: str | None = None
    embedding_base_url: str | None = None


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatMessageOut(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime
    metadata_json: dict | None = None

    model_config = {"from_attributes": True}


class QueryRequest(BaseModel):
    """The frontend sends { question, history, settings }."""

    question: str = Field(..., min_length=1)
    history: list[ChatMessage] = Field(default_factory=list)
    settings: QuerySettingsIn = Field(default_factory=QuerySettingsIn)


class SourceOut(BaseModel):
    """Matches the frontend's Source interface."""

    source_id: str
    filename: str
    page: int | None = None
    snippet: str
    content: str | None = None
    chunk_index: int | None = None
    file_id: str | None = None
    score: float | None = None
    source_type: Literal["local", "web"] | None = "local"
    url: str | None = None


class RetrievalDebugOut(BaseModel):
    """Matches the frontend's RetrievalDebug interface."""

    rewritten_query: str | None = None
    queries: list[str] | None = None
    retrieval_method: str | None = None
    k: int | None = None
    scores: list[float] | None = None


class QueryResponse(BaseModel):
    """Matches the frontend's QueryResponse interface."""

    answer: str
    sources: list[SourceOut] = []
    debug: RetrievalDebugOut | None = None


# ── Health ────────────────────────────────────────────────

class HealthResponse(BaseModel):
    ok: bool = True
    version: str = "0.1.0"


# ── Study Mode ────────────────────────────────────────────

class StudyRequest(BaseModel):
    mode: Literal["quiz", "summary", "flashcards"] = "quiz"
    count: int = 10
    topic: str | None = None
    settings: QuerySettingsIn | None = None


class StudyResponse(BaseModel):
    content: str
    mode: str
    sources: list[SourceOut] = []
