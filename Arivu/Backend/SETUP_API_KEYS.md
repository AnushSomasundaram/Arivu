# API Keys & Configuration Setup Guide

## 🚨 Quick Fix

You're seeing API key errors because your configuration isn't set up yet. Here's how to fix it:

### Option 1: Interactive Setup (Recommended)
```bash
cd Arivu/Backend
python setup_env.py
```

This will walk you through setting up your configuration interactively.

### Option 2: Manual Setup

1. **Create `.env` file:**
   ```bash
   cd Arivu/Backend
   cp .env.example .env
   ```

2. **Edit `.env` and add your API key:**
   ```bash
   # Open .env in your editor
   nano .env   # or vim, code, etc.
   ```

3. **Add your OpenAI API key:**
   ```env
   ARIVU_OPENAI_API_KEY=sk-your-actual-key-here
   ```

4. **Restart the backend server**

## 📋 Configuration Options

### For OpenAI (GPT-4, GPT-4o-mini, etc.)

```env
ARIVU_OPENAI_API_KEY=sk-proj-xxxxx
ARIVU_LLM_BACKEND=openai
ARIVU_OPENAI_CHAT_MODEL=gpt-4o-mini
```

Get your API key from: https://platform.openai.com/api-keys

### For Local (Ollama) - Free & Private

```env
ARIVU_LLM_BACKEND=ollama
ARIVU_OLLAMA_BASE_URL=http://localhost:11434
ARIVU_OLLAMA_MODEL=llama3
```

Make sure Ollama is running:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### For Embeddings

**Option A: Local (Free, runs on your machine)**
```env
ARIVU_EMBEDDING_BACKEND=local
ARIVU_LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
```

Note: First run will download the model (~90MB)

**Option B: OpenAI (Requires API key)**
```env
ARIVU_EMBEDDING_BACKEND=openai
ARIVU_OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

## 🔍 Verify Configuration

After setting up, verify everything works:

```bash
python check_config.py
```

This will show you:
- ✓ Environment variables loaded
- ✓ .env file found
- ✓ API keys configured (masked for security)
- ✓ Which backends are working

## ❌ Common Issues

### Issue: "OpenAI model requires an API key"

**Solution:** Add your API key to `.env`:
```env
ARIVU_OPENAI_API_KEY=sk-proj-xxxxx
```

Then restart the backend server.

### Issue: "Could not import sentence_transformers"

**Solution:** Install the package:
```bash
pip install sentence-transformers
# or
uv pip install sentence-transformers
```

### Issue: "Ollama connection failed"

**Solution:** Make sure Ollama is running:
```bash
# Check status
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve
```

### Issue: Changes to .env not taking effect

**Solution:** Restart the backend server:
```bash
# Stop the server (Ctrl+C)
# Then start it again
uvicorn app.main:app --reload
```

## 🎯 Recommended Configurations

### For Development (Free, Local)
```env
ARIVU_LLM_BACKEND=ollama
ARIVU_EMBEDDING_BACKEND=local
ARIVU_OLLAMA_MODEL=llama3
ARIVU_LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### For Production (Best Quality)
```env
ARIVU_LLM_BACKEND=openai
ARIVU_EMBEDDING_BACKEND=openai
ARIVU_OPENAI_CHAT_MODEL=gpt-4o-mini
ARIVU_OPENAI_EMBEDDING_MODEL=text-embedding-3-small
ARIVU_OPENAI_API_KEY=sk-proj-xxxxx
```

### Hybrid (Local embeddings, OpenAI for generation)
```env
ARIVU_LLM_BACKEND=openai
ARIVU_EMBEDDING_BACKEND=local
ARIVU_OPENAI_CHAT_MODEL=gpt-4o-mini
ARIVU_LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
ARIVU_OPENAI_API_KEY=sk-proj-xxxxx
```

## 📝 Example .env File

```env
# OpenAI API Key (get from https://platform.openai.com/api-keys)
ARIVU_OPENAI_API_KEY=sk-proj-xxxxx

# Backend Selection
ARIVU_LLM_BACKEND=ollama
ARIVU_EMBEDDING_BACKEND=local

# Ollama Configuration
ARIVU_OLLAMA_BASE_URL=http://localhost:11434
ARIVU_OLLAMA_MODEL=llama3

# OpenAI Models (when using OpenAI backend)
ARIVU_OPENAI_CHAT_MODEL=gpt-4o-mini
ARIVU_OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Local Embedding Model
ARIVU_LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2

# Database & Storage
ARIVU_DATABASE_URL=sqlite+aiosqlite:///data/arivu.db
ARIVU_DATA_DIR=data

# RAG Configuration
ARIVU_DEFAULT_CHUNK_SIZE=1000
ARIVU_DEFAULT_CHUNK_OVERLAP=200
ARIVU_DEFAULT_TOP_K=5
```

## 🛠 Troubleshooting

Run the diagnostic script to see what's wrong:
```bash
python check_config.py
```

This will show you exactly what's configured and what's missing.

Need help? Check the error message - the new error handling provides clear, actionable messages telling you exactly what's wrong and how to fix it.
