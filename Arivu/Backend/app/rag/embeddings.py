"""Embedding factory for LangChain embedding models.

Handles provider selection (OpenAI, Ollama, HuggingFace) based on
model name patterns and parameters. Returns standard LangChain
Embeddings instances.

This is a configuration factory, NOT an abstraction layer. It returns
native LangChain embedding instances without any custom wrapping.
"""

from __future__ import annotations

import logging

from langchain_core.embeddings import Embeddings
from app.core.config import settings

log = logging.getLogger(__name__)


def get_embeddings(
    model_name: str,
    api_key: str | None = None,
    base_url: str | None = None,
) -> Embeddings:
    """Get a LangChain Embeddings instance based on model name.

    Args:
        model_name: Name of the embedding model
                   - OpenAI models: Contains "gpt" or "text-embedding" or "openai"
                   - Ollama models: Contains "ollama" or when base_url is provided
                   - HuggingFace models: Local models (may have "local:" prefix)
        api_key: Optional API key override (defaults to settings)
        base_url: Optional base URL override (defaults to settings)

    Returns:
        LangChain Embeddings instance (OpenAIEmbeddings, OllamaEmbeddings,
        or HuggingFaceEmbeddings)

    Raises:
        ValueError: If OpenAI model is requested but no API key is available

    Examples:
        >>> embeddings = get_embeddings("text-embedding-3-small", api_key="sk-...")
        >>> embeddings = get_embeddings("nomic-embed-text", base_url="http://localhost:11434")
        >>> embeddings = get_embeddings("local:all-MiniLM-L6-v2")
    """
    # Normalize model name for checking
    model_lower = model_name.lower()

    # Helper to check if a value is truly empty
    def is_empty(val: str | None) -> bool:
        return val is None or val == "" or val.strip() == ""

    # Determine which provider to use
    is_openai = any(keyword in model_lower for keyword in ["gpt", "text-embedding", "openai"])
    is_ollama = "ollama" in model_lower or not is_empty(base_url)
    is_local = model_lower.startswith("local:") or (not is_openai and not is_ollama)

    # OpenAI Embeddings
    if is_openai:
        from langchain_openai import OpenAIEmbeddings

        # Get API key from parameter or settings
        final_api_key = api_key if not is_empty(api_key) else settings.openai_api_key

        # Validate API key
        if is_empty(final_api_key):
            log.error(f"OpenAI API key missing for model {model_name}")
            log.error(f"Parameter api_key provided: {'Yes' if api_key else 'No'}")
            log.error(f"Settings api_key available: {'Yes' if settings.openai_api_key else 'No'}")
            
            raise ValueError(
                f"OpenAI embedding model '{model_name}' requires an API key.\n"
                "Solutions:\n"
                "  1. Set ARIVU_OPENAI_API_KEY environment variable\n"
                "  2. Add to .env file: ARIVU_OPENAI_API_KEY=sk-...\n"
                "  3. Provide api_key parameter when calling\n"
                "Get your API key from: https://platform.openai.com/api-keys"
            )

        log.info(f"Using OpenAI embeddings: {model_name}")
        
        # Safe logging of key prefix
        key_str = final_api_key.get_secret_value() if hasattr(final_api_key, "get_secret_value") else str(final_api_key)
        log.info(f"API Key being used: {key_str[:3]}... (length: {len(key_str)})")
        
        # Strip prefix for OpenAI client
        clean_model = model_name.replace("openai:", "")
        
        return OpenAIEmbeddings(
            model=clean_model,
            api_key=final_api_key
        )

    # Ollama Embeddings
    elif is_ollama:
        import os
        from langchain_ollama import OllamaEmbeddings

        # Get base URL from parameter or settings
        final_base_url = base_url if not is_empty(base_url) else settings.ollama_base_url

        # Clean model name (remove "ollama:" prefix if present)
        clean_model = model_name.replace("ollama:", "").replace("local:", "")

        # OllamaEmbeddings uses OLLAMA_HOST environment variable for configuration
        # Set it temporarily if a custom base_url is provided
        original_host = os.environ.get("OLLAMA_HOST")
        if final_base_url:
            os.environ["OLLAMA_HOST"] = final_base_url

        try:
            log.info(f"Using Ollama embeddings: {clean_model} at {final_base_url}")
            return OllamaEmbeddings(model=clean_model)
        finally:
            # Restore original OLLAMA_HOST value
            if original_host is not None:
                os.environ["OLLAMA_HOST"] = original_host
            elif "OLLAMA_HOST" in os.environ:
                del os.environ["OLLAMA_HOST"]

    # HuggingFace Local Embeddings (default)
    else:
        from langchain_community.embeddings import HuggingFaceEmbeddings

        # Clean model name (remove "local:" prefix if present)
        clean_model = model_name.replace("local:", "")

        log.info(f"Using HuggingFace embeddings: {clean_model}")
        return HuggingFaceEmbeddings(model_name=clean_model)
