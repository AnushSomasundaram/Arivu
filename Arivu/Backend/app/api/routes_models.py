"""API routes for model discovery and information."""

from __future__ import annotations

from fastapi import APIRouter

from app.rag.model_validation import get_available_embedding_models

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("/embeddings")
async def list_embedding_models():
    """Get list of available embedding models with metadata.
    
    Returns:
        List of embedding models with name, provider, dimensions, and description
    """
    return {
        "models": get_available_embedding_models()
    }
