"""Minimal LangChain Chroma factory for project-specific vector stores.

All other logic (add, delete, query) should use the LangChain Chroma 
class directly in routes and ingestion.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma

from app.core.config import settings


def get_project_vectorstore(
    project_id: str,
    embedding_function: Embeddings | None = None,
    *,
    collection_name: str = "documents",
) -> Chroma:
    """Return a LangChain Chroma instance scoped to a project.

    This factory encapsulates:
    - Project-specific directory structure (data_dir/projects/{id}/chroma)
    - Chroma configuration (cosine similarity, collection naming)
    - Directory initialization (mkdir if not exists)

    This is NOT an abstraction layer - it returns a standard LangChain
    Chroma instance configured for this project's storage location.

    Args:
        project_id: Unique project identifier
        embedding_function: LangChain Embeddings instance
        collection_name: Chroma collection name (default: "documents")

    Returns:
        Configured langchain_chroma.Chroma instance
    """
    path = settings.data_dir / "projects" / project_id / "chroma"
    path.mkdir(parents=True, exist_ok=True)

    kwargs: dict[str, Any] = {
        "collection_name": collection_name,
        "persist_directory": str(path),
        "collection_metadata": {"hnsw:space": "cosine"},
    }
    if embedding_function is not None:
        kwargs["embedding_function"] = embedding_function

    return Chroma(**kwargs)


def delete_project_data(project_id: str) -> None:
    """Delete all on-disk data for a project (files + vector store)."""
    import shutil
    project_dir = settings.data_dir / "projects" / project_id
    if project_dir.exists():
        shutil.rmtree(project_dir)
