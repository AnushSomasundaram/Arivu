"""Retrieval logic using LangChain Chroma directly.

No custom wrappers — just LangChain classes and minimal data structures.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma

log = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    """A single retrieved chunk with score and metadata."""

    chunk_id: str
    doc_id: str
    filename: str
    filetype: str
    text: str
    score: float
    chunk_index: int | None = None
    page: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MetadataFilter:
    """Optional metadata filters for retrieval."""

    doc_id: str | None = None
    filetype: str | None = None


def _build_chroma_where(filters: MetadataFilter | None) -> dict[str, Any] | None:
    """Convert MetadataFilter to a Chroma where clause."""
    if not filters:
        return None

    conditions: list[dict[str, Any]] = []

    if filters.doc_id:
        conditions.append({"doc_id": {"$eq": filters.doc_id}})
    if filters.filetype:
        conditions.append({"filetype": {"$eq": filters.filetype}})

    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def doc_to_chunk(doc, score: float) -> RetrievedChunk:
    """Convert a LangChain Document + score to RetrievedChunk."""
    meta = doc.metadata or {}
    return RetrievedChunk(
        chunk_id=meta.get("chunk_id", ""),
        doc_id=meta.get("doc_id", ""),
        filename=meta.get("filename", ""),
        filetype=meta.get("filetype", ""),
        text=doc.page_content,
        score=score,
        chunk_index=meta.get("chunk_index"),
        page=meta.get("page"),
        metadata=meta,
    )


from langchain_core.retrievers import BaseRetriever
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

def get_retriever(
    vectorstore: Chroma,
    settings: Any,  # QuerySettingsIn
    llm: Any,
) -> BaseRetriever:
    """
    Construct a LangChain retriever based on settings.
    Composes:
      - VectorStoreRetriever (base)
      - MultiQueryRetriever (optional query translation)
      - ContextualCompressionRetriever (optional reranking)
    """
    # 1. Base Retriever
    search_type = settings.search_type  # "similarity" or "mmr"
    search_kwargs = {"k": settings.k}
    if search_type == "mmr":
        search_kwargs.update({"fetch_k": 20, "lambda_mult": 0.5})

    base_retriever = vectorstore.as_retriever(
        search_type=search_type,
        search_kwargs=search_kwargs,
    )

    # 2. Query Translation (DEPRECATED here, moved to routes_query.py for debug visibility)
    current_retriever = base_retriever

    # 3. Reranking (Contextual Compression)
    if settings.enable_reranking:
        model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-base")
        compressor = CrossEncoderReranker(model=model, top_n=settings.k)
        current_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=current_retriever
        )

    return current_retriever

# Helper to standardizing output is still useful if we need to convert manually,
# but usually chains return Documents.
def doc_to_chunk(doc, score: float = 0.0) -> RetrievedChunk:
    """Convert a LangChain Document + score to RetrievedChunk."""
    meta = doc.metadata or {}
    # If using ContextualCompression, 'relevance_score' might be in metadata
    final_score = score
    if "relevance_score" in meta:
         final_score = meta["relevance_score"]
    elif hasattr(doc, "metadata") and "score" in doc.metadata:
        final_score = doc.metadata["score"]
        
    return RetrievedChunk(
        chunk_id=meta.get("chunk_id", ""),
        doc_id=meta.get("doc_id", ""),
        filename=meta.get("filename", ""),
        filetype=meta.get("filetype", ""),
        text=doc.page_content,
        score=final_score,
        chunk_index=meta.get("chunk_index"),
        page=meta.get("page"),
        metadata=meta,
    )
