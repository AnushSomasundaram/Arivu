"""Model validation utilities for embedding and LLM models.

Validates model names and provides helpful error messages.
"""

from __future__ import annotations

import logging
from typing import Literal

log = logging.getLogger(__name__)

ModelProvider = Literal["local", "openai", "ollama"]


def parse_model_name(model_name: str) -> tuple[ModelProvider, str]:
    """Parse a model name into provider and actual model name.
    
    Args:
        model_name: Model name in format "provider:model" or just "model"
        
    Returns:
        (provider, clean_model_name)
        
    Examples:
        >>> parse_model_name("local:all-MiniLM-L6-v2")
        ("local", "all-MiniLM-L6-v2")
        >>> parse_model_name("text-embedding-3-small")
        ("openai", "text-embedding-3-small")
        >>> parse_model_name("ollama:nomic-embed-text")
        ("ollama", "nomic-embed-text")
    """
    model_lower = model_name.lower()
    
    # Explicit prefix
    if model_lower.startswith("local:"):
        return "local", model_name.split(":", 1)[1]
    elif model_lower.startswith("openai:"):
        return "openai", model_name.split(":", 1)[1]
    elif model_lower.startswith("ollama:"):
        return "ollama", model_name.split(":", 1)[1]
    
    # Infer from model name
    if any(keyword in model_lower for keyword in ["gpt", "text-embedding", "ada"]):
        return "openai", model_name
    elif any(keyword in model_lower for keyword in ["nomic", "llama", "mistral", "qwen"]):
        return "ollama", model_name
    
    # Default to local
    return "local", model_name


def validate_embedding_model(model_name: str, require_api_key: bool = False) -> tuple[bool, str | None]:
    """Validate an embedding model name.
    
    Args:
        model_name: The embedding model name to validate
        require_api_key: If True, check that API keys are available for cloud models
        
    Returns:
        (is_valid, error_message)
        error_message is None if valid, otherwise contains helpful error text
        
    Examples:
        >>> validate_embedding_model("local:all-MiniLM-L6-v2")
        (True, None)
        >>> validate_embedding_model("invalid:")
        (False, "Model name cannot be empty after prefix")
    """
    if not model_name or not model_name.strip():
        return False, "Embedding model name cannot be empty"
    
    model_name = model_name.strip()
    
    # Check for invalid formats
    if model_name.endswith(":"):
        return False, "Model name cannot be empty after prefix (e.g., 'local:')"
    
    if model_name.count(":") > 1:
        return False, "Model name should have at most one ':' separator (e.g., 'local:model-name')"
    
    # Parse provider and model
    provider, clean_name = parse_model_name(model_name)
    
    if not clean_name or not clean_name.strip():
        return False, f"Model name cannot be empty for provider '{provider}'"
    
    # Provider-specific validation
    if provider == "openai":
        if require_api_key:
            from app.core.config import settings
            if not settings.openai_api_key:
                return False, (
                    f"OpenAI embedding model '{model_name}' requires an API key. "
                    "Set ARIVU_OPENAI_API_KEY environment variable."
                )
    
    # All checks passed
    return True, None


def normalize_model_name(model_name: str) -> str:
    """Normalize a model name to standard format with provider prefix.
    
    Args:
        model_name: Model name (with or without prefix)
        
    Returns:
        Normalized model name in format "provider:model"
        
    Examples:
        >>> normalize_model_name("all-MiniLM-L6-v2")
        "local:all-MiniLM-L6-v2"
        >>> normalize_model_name("local:all-MiniLM-L6-v2")
        "local:all-MiniLM-L6-v2"
        >>> normalize_model_name("text-embedding-3-small")
        "openai:text-embedding-3-small"
    """
    provider, clean_name = parse_model_name(model_name)
    return f"{provider}:{clean_name}"


def get_available_embedding_models() -> list[dict[str, str | int]]:
    """Get list of available embedding models with metadata.
    
    Returns:
        List of model info dicts with keys: name, provider, dimensions, description
    """
    return [
        {
            "name": "local:all-MiniLM-L6-v2",
            "provider": "local",
            "dimensions": 384,
            "description": "Fast, lightweight model for general use (free, runs locally)"
        },
        {
            "name": "local:all-mpnet-base-v2",
            "provider": "local",
            "dimensions": 768,
            "description": "Higher quality local model, slower but more accurate (free, runs locally)"
        },
        {
            "name": "openai:text-embedding-3-small",
            "provider": "openai",
            "dimensions": 1536,
            "description": "OpenAI's efficient embedding model (requires API key, paid)"
        },
        {
            "name": "openai:text-embedding-3-large",
            "provider": "openai",
            "dimensions": 3072,
            "description": "OpenAI's most powerful embedding model (requires API key, paid)"
        },
        {
            "name": "ollama:nomic-embed-text",
            "provider": "ollama",
            "dimensions": 768,
            "description": "High-quality embeddings via Ollama (requires Ollama running)"
        },
    ]


def validate_llm_model(model_name: str) -> tuple[bool, str | None]:
    """Validate an LLM model name.
    
    Args:
        model_name: The LLM model name to validate
        
    Returns:
        (is_valid, error_message)
    """
    if not model_name or not model_name.strip():
        return False, "LLM model name cannot be empty"
    
    # LLM validation is more lenient - just check it's not empty
    # The actual validation happens when trying to use the model
    return True, None
