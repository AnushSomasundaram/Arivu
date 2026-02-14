"""LLM factory for LangChain model initialization.

This factory handles provider selection (OpenAI vs Ollama) based on
model name patterns. Returns standard LangChain ChatModel instances.

This is a configuration factory, NOT an abstraction layer. It returns
native LangChain chat model instances without any custom wrapping.
"""

from __future__ import annotations

import logging

from app.core.config import settings

log = logging.getLogger(__name__)


def get_llm(
    model_name: str,
    api_key: str | None = None,
    base_url: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 2048,
):
    """Get a LangChain LLM instance based on model name.

    Args:
        model_name: Name of the model (e.g., "gpt-4", "llama3", "mistral")
        api_key: Optional API key override (defaults to settings)
        base_url: Optional base URL override (defaults to settings)
        temperature: Temperature for generation (default: 0.3)

    Returns:
        LangChain ChatModel instance (ChatOpenAI or ChatOllama)

    Raises:
        ValueError: If OpenAI model is requested but no API key is available

    Examples:
        >>> llm = get_llm("gpt-4", api_key="sk-...")
        >>> llm = get_llm("llama3", base_url="http://localhost:11434")
    """
    # Normalize model name for checking
    model_lower = model_name.lower()

    # Helper to check if a value is truly empty
    def is_empty(val: str | None) -> bool:
        return val is None or val == "" or val.strip() == ""

    # Determine which provider to use
    is_openai = any(keyword in model_lower for keyword in ["gpt", "openai", "o1", "o3"])

    # OpenAI LLM
    if is_openai:
        from langchain_openai import ChatOpenAI

        # Get API key from parameter or settings
        final_api_key = api_key if not is_empty(api_key) else settings.openai_api_key

        # Validate API key
        if is_empty(final_api_key):
            raise ValueError(
                f"OpenAI model '{model_name}' requires an API key. "
                "Please provide it via the 'api_key' parameter or set ARIVU_OPENAI_API_KEY environment variable."
            )

        log.info(f"Using OpenAI LLM: {model_name} (temp={temperature})")
        
        # Strip prefix
        clean_model = model_name.replace("openai:", "")
        
        return ChatOpenAI(
            model=clean_model,
            api_key=final_api_key,
            temperature=temperature,
            max_tokens=max_tokens
        )

    # Ollama LLM (default for all non-OpenAI models)
    else:
        from langchain_ollama import ChatOllama

        # Get base URL from parameter or settings
        final_base_url = base_url if not is_empty(base_url) else settings.ollama_base_url

        # Clean model name (remove "ollama:" prefix if present)
        clean_model = model_name.replace("ollama:", "")

        log.info(f"Using Ollama LLM: {clean_model} at {final_base_url} (temp={temperature})")
        return ChatOllama(
            model=clean_model,
            base_url=final_base_url,
            temperature=temperature,
            timeout=120,
            num_predict=max_tokens
        )
