#!/usr/bin/env python3
"""Diagnostic script to check configuration and API keys."""

import os
import sys
from pathlib import Path

print("=" * 70)
print("ARIVU CONFIGURATION DIAGNOSTIC")
print("=" * 70)
print()

# Check environment variables
print("1. ENVIRONMENT VARIABLES CHECK:")
print("-" * 70)

env_vars = {
    "ARIVU_OPENAI_API_KEY": os.getenv("ARIVU_OPENAI_API_KEY"),
    "ARIVU_EMBEDDING_BACKEND": os.getenv("ARIVU_EMBEDDING_BACKEND"),
    "ARIVU_LLM_BACKEND": os.getenv("ARIVU_LLM_BACKEND"),
    "ARIVU_OLLAMA_BASE_URL": os.getenv("ARIVU_OLLAMA_BASE_URL"),
    "ARIVU_DATA_DIR": os.getenv("ARIVU_DATA_DIR"),
}

for key, value in env_vars.items():
    if value:
        # Mask API keys for security
        if "API_KEY" in key or "KEY" in key:
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"  ✓ {key}: {masked}")
        else:
            print(f"  ✓ {key}: {value}")
    else:
        print(f"  ✗ {key}: NOT SET")

print()

# Check .env file
print("2. .ENV FILE CHECK:")
print("-" * 70)

env_file = Path(".env")
if env_file.exists():
    print(f"  ✓ .env file exists at: {env_file.absolute()}")
    print()
    print("  Contents (with API keys masked):")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "API_KEY" in line or "_KEY" in line:
                    key = line.split("=")[0]
                    print(f"    {key}=***")
                else:
                    print(f"    {line}")
else:
    print(f"  ✗ .env file NOT FOUND at: {env_file.absolute()}")

print()

# Try to load settings
print("3. PYDANTIC SETTINGS LOADING:")
print("-" * 70)

try:
    from app.core.config import settings

    print(f"  ✓ Settings loaded successfully")
    print()
    print("  Values:")

    # Check OpenAI settings
    if settings.openai_api_key:
        masked = settings.openai_api_key[:8] + "..." + settings.openai_api_key[-4:] if len(settings.openai_api_key) > 12 else "***"
        print(f"    openai_api_key: {masked}")
    else:
        print(f"    openai_api_key: EMPTY ⚠️")

    print(f"    embedding_backend: {settings.embedding_backend}")
    print(f"    llm_backend: {settings.llm_backend}")
    print(f"    ollama_base_url: {settings.ollama_base_url}")
    print(f"    ollama_model: {settings.ollama_model}")
    print(f"    openai_chat_model: {settings.openai_chat_model}")
    print(f"    openai_embedding_model: {settings.openai_embedding_model}")
    print(f"    local_embedding_model: {settings.local_embedding_model}")

except Exception as e:
    print(f"  ✗ ERROR loading settings: {e}")
    import traceback
    traceback.print_exc()

print()

# Test factory functions
print("4. FACTORY FUNCTIONS TEST:")
print("-" * 70)

try:
    from app.rag.embeddings import get_embeddings
    from app.rag.llm import get_llm

    print("  Testing LLM factory:")

    # Test Ollama (should work without API key)
    try:
        llm = get_llm("llama3")
        print(f"    ✓ Ollama LLM: Success (llama3)")
    except Exception as e:
        print(f"    ✗ Ollama LLM failed: {e}")

    # Test OpenAI (will fail if no API key)
    try:
        llm = get_llm("gpt-4")
        print(f"    ✓ OpenAI LLM: Success (gpt-4)")
    except ValueError as e:
        print(f"    ⚠ OpenAI LLM requires API key: {str(e)[:50]}...")
    except Exception as e:
        print(f"    ✗ OpenAI LLM error: {e}")

    print()
    print("  Testing Embeddings factory:")

    # Test local embeddings (should work)
    try:
        emb = get_embeddings("local:all-MiniLM-L6-v2")
        print(f"    ✓ Local embeddings: Success (all-MiniLM-L6-v2)")
    except Exception as e:
        print(f"    ✗ Local embeddings failed: {e}")

    # Test Ollama embeddings
    try:
        emb = get_embeddings("nomic-embed-text", base_url="http://localhost:11434")
        print(f"    ✓ Ollama embeddings: Success (nomic-embed-text)")
    except Exception as e:
        print(f"    ✗ Ollama embeddings failed: {e}")

    # Test OpenAI embeddings (will fail if no API key)
    try:
        emb = get_embeddings("text-embedding-3-small")
        print(f"    ✓ OpenAI embeddings: Success (text-embedding-3-small)")
    except ValueError as e:
        print(f"    ⚠ OpenAI embeddings require API key: {str(e)[:50]}...")
    except Exception as e:
        print(f"    ✗ OpenAI embeddings error: {e}")

except Exception as e:
    print(f"  ✗ ERROR testing factories: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("DIAGNOSIS COMPLETE")
print("=" * 70)
print()

# Recommendations
print("RECOMMENDATIONS:")
print()

if not env_file.exists():
    print("  1. Create a .env file in the Backend directory with your configuration:")
    print("     ARIVU_OPENAI_API_KEY=sk-your-key-here")
    print()

if not os.getenv("ARIVU_OPENAI_API_KEY") and not (env_file.exists() and "ARIVU_OPENAI_API_KEY" in env_file.read_text()):
    print("  2. Add your OpenAI API key to the .env file or environment:")
    print("     ARIVU_OPENAI_API_KEY=sk-...")
    print()

print("  3. Restart the backend server after changing .env")
print("  4. Check that your API key starts with 'sk-' for OpenAI")
print()
