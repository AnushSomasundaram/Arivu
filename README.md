# Arivu

**Arivu** (Tamil for *knowledge / wisdom*) is a local-first Electron desktop application for Retrieval-Augmented Generation (RAG) over your own documents. It runs entirely on your machine with no data sent to the cloud unless you explicitly configure a cloud LLM or embedding provider.

---

## Table of Contents

- [Features](#features)
- [Supported Document Types](#supported-document-types)
- [RAG Architecture](#rag-architecture)
  - [Ingestion Pipeline](#ingestion-pipeline)
  - [RAPTOR Hierarchical Summarization](#raptor-hierarchical-summarization)
  - [Query Pipeline](#query-pipeline)
  - [Study Mode Pipeline](#study-mode-pipeline)
- [LLM & Embedding Providers](#llm--embedding-providers)
- [Settings Reference](#settings-reference)
  - [Environment Variables](#environment-variables)
  - [Per-Project UI Settings](#per-project-ui-settings)
- [API Reference](#api-reference)
- [Frontend Views](#frontend-views)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)

---

## Features

- **Multi-project workspace** — separate knowledge bases per project, each with its own vectorstore, settings, and chat history
- **Broad document support** — PDFs, Office docs, code files, images (OCR), emails, spreadsheets, and more
- **Local-first** — runs fully offline with Ollama + HuggingFace embeddings; cloud providers are optional
- **Hierarchical RAG (RAPTOR)** — automatic multi-level summarization clusters for long documents, giving the LLM global + local context simultaneously
- **History-aware querying** — reformulates follow-up questions into standalone queries using conversation history
- **Multi-query expansion** — generates 3 alternative phrasings of every question to improve recall
- **Cross-encoder reranking** — re-scores retrieved chunks for relevance before sending to the LLM
- **MMR retrieval** — Maximal Marginal Relevance search to reduce redundant chunks
- **Study mode** — generate quizzes, flashcard sets, or summaries directly from your documents
- **Web search integration** — optional Tavily web search in fallback or augment mode
- **Per-project settings** — all retrieval, LLM, embedding, and chunking parameters are configurable per project and persisted locally
- **Electron desktop app** — native macOS (and Windows/Linux) experience with packaged backend

---

## Supported Document Types

| Category | Extensions |
|---|---|
| PDF | `.pdf` |
| Plain text | `.txt`, `.md` |
| Web | `.html`, `.htm`, `.xml` |
| Rich text | `.rtf`, `.epub` |
| Word | `.docx`, `.doc` |
| Excel | `.xlsx`, `.xls` |
| PowerPoint | `.pptx`, `.ppt` |
| LibreOffice | `.odt`, `.ods`, `.odp` |
| Data | `.csv`, `.json`, `.jsonl` |
| Code | `.py`, `.js`, `.ts`, `.java`, `.c`, `.cpp`, `.go`, `.rs`, `.sql`, `.sh`, `.bash` |
| Notebooks | `.ipynb` |
| Images (OCR) | `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.tif` |
| Email | `.eml`, `.msg` |

---

## RAG Architecture

### Ingestion Pipeline

Every uploaded file goes through the following sequential stages. Progress and status are tracked in the database and surfaced in the UI.

```
Upload
  │
  ▼
Validate file type
  │
  ▼
Save to disk
  │
  ▼  status: "parsing"  | progress: 10%
Parse — extract raw text using file-type-specific loaders
  │
  ▼  status: "chunking" | progress: 20%
Chunk — RecursiveCharacterTextSplitter
  │     chunk_size: 1000 chars (configurable)
  │     chunk_overlap: 200 chars (configurable)
  │     separators: ["\n\n", "\n", ". ", " ", ""]
  │
  ▼  status: "indexing"  | progress: 40%
Initialise embeddings model
  │
  ▼  status: "indexing"  | progress: 60%
RAPTOR (only if document has >10 chunks)
  │   → UMAP dimensionality reduction (2D, cosine)
  │   → Gaussian Mixture Model clustering (k auto-selected by BIC)
  │   → LLM summarises each cluster
  │   → Hierarchical levels: level 0 = raw chunks, level 1+ = summaries
  │
  ▼  status: "indexing"  | progress: 80%
Add all chunks + summaries to ChromaDB vectorstore
  │
  ▼  status: "indexed"   | progress: 100%
Persist chunk metadata to SQLite
```

### RAPTOR Hierarchical Summarization

RAPTOR (Recursive Abstractive Processing for Tree-Organized Retrieval) builds a tree of summaries over large documents, enabling the model to reason at multiple levels of abstraction simultaneously.

**When it activates:** documents with more than 10 chunks after splitting.

**Steps:**
1. Compute embeddings for all base chunks
2. Reduce to 2 dimensions with UMAP (cosine distance)
3. Cluster with a Gaussian Mixture Model; number of clusters is chosen automatically by minimising Bayesian Information Criterion (BIC), capped at `sqrt(n_chunks)`
4. The configured LLM writes a concise summary for each cluster
5. Summaries are stored in ChromaDB with `level=1` (or higher for recursive passes) alongside the base chunks at `level=0`

**At query time:** the top-5 highest-level RAPTOR summaries are injected as global context ahead of the regular retrieved chunks.

### Query Pipeline

```
User question
  │
  ▼
Prepare chat history (last 6 messages)
  │
  ▼  (if history present)
Condense question — LLM rewrites follow-up into a self-contained query
  │
  ▼  (if multi-query enabled)
Multi-query expansion — LLM generates 3 alternative phrasings
  │
  ▼
Retrieve chunks — for each query variant:
  │   search_type: "similarity" (cosine) or "mmr" (Maximal Marginal Relevance)
  │   k: configurable (default 5)
  │   optional min_score filter
  │
  ▼  (if reranking enabled)
Cross-encoder reranking — BAAI/bge-reranker-base scores all candidates,
  │   top-k kept, rest discarded
  │
  ▼
Fetch RAPTOR global context — top-5 level-1+ summaries for the project
  │
  ▼
Merge context — RAPTOR summaries prepended to retrieved chunks,
  │   deduplicated, capped at max_context_tokens
  │
  ▼
LLM generation — stuff-documents chain
  │
  ▼
Post-process — extract sources, scores, debug metadata
  │
  ▼
Persist to chat history → return answer + sources + (optional) debug info
```

**Retrieval modes:**

| Mode | Description |
|---|---|
| `similarity` | Standard cosine similarity search. Fast and deterministic. |
| `mmr` | Maximal Marginal Relevance. Trades some relevance for diversity to avoid redundant chunks. |

**Query translation options:**

| Option | Effect |
|---|---|
| Condense question | Rewrites follow-up questions using conversation history into a standalone query |
| Multi-query | Generates 3 alternative phrasings and merges results for better recall |

### Study Mode Pipeline

```
Fetch all vectorstore documents for the project
  │
  ▼
Prioritise RAPTOR summaries (level ≥ 1):
  │   If available: top 20 summaries sorted by level (highest first)
  │   Fallback: raw chunks (limit 50)
  │
  ▼
Format context with source info
  │
  ▼
LLM generation with study prompt
  │   mode: quiz | summary | flashcards
  │   count: number of items
  │   topic: optional focus topic
  │
  ▼
Return content + sources
```

---

## LLM & Embedding Providers

### LLM Backends

| Backend | Detection | Default model | Notes |
|---|---|---|---|
| **Ollama** (default) | Model name does not contain `gpt`, `openai`, `o1`, `o3` | `llama3` | Requires Ollama running locally at `http://localhost:11434` |
| **OpenAI** | Model name contains `gpt`, `openai`, `o1`, or `o3` | `gpt-4o-mini` | Requires `ARIVU_OPENAI_API_KEY` |

Recommended Ollama models: `llama3`, `llama3.1`, `llama3.2`, `mistral`, `qwen2.5`, `phi3`, `gemma2`

### Embedding Backends

| Backend | Detection | Models | Dimensions | Notes |
|---|---|---|---|---|
| **HuggingFace (local)** (default) | Model name not matching OpenAI or Ollama patterns | `all-MiniLM-L6-v2` | 384 | Fast, no internet required |
| | | `all-mpnet-base-v2` | 768 | More accurate, slower |
| **OpenAI** | Model name contains `gpt`, `text-embedding`, or `openai` | `text-embedding-3-small` | 1536 | Requires API key |
| | | `text-embedding-3-large` | 3072 | Highest quality |
| **Ollama** | Model name contains `ollama` or a base URL is provided | `nomic-embed-text` | 768 | Requires Ollama locally |

> **Note:** the embedding model is set per-project at creation time. Changing a project's embedding model requires reindexing all documents.

### Reranker

| Component | Default model | Notes |
|---|---|---|
| Cross-encoder reranker | `cross-encoder/ms-marco-MiniLM-L-12-v2` | Runs locally; downloads on first use |

---

## Settings Reference

### Environment Variables

All variables are optional and have sensible defaults.

#### Application

| Variable | Default | Description |
|---|---|---|
| `ARIVU_APP_NAME` | `Arivu RAG Backend` | Application name shown in API responses |
| `ARIVU_DEBUG` | `false` | Enable debug logging |
| `ARIVU_DATA_DIR` | `~/.arivu` | Root directory for databases and uploads |
| `ARIVU_BACKEND_HOST` | `127.0.0.1` | Host the backend binds to |
| `ARIVU_BACKEND_PORT` | `8000` | Port the backend listens on |
| `ARIVU_CORS_ORIGINS` | `http://localhost:5173, http://127.0.0.1:5173` | Comma-separated allowed CORS origins |
| `ARIVU_DATABASE_URL` | `sqlite+aiosqlite:///~/.arivu/arivu.db` | SQLite async connection string |

#### LLM

| Variable | Default | Description |
|---|---|---|
| `ARIVU_LLM_BACKEND` | `ollama` | `ollama` or `openai` |
| `ARIVU_OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `ARIVU_OLLAMA_MODEL` | `llama3` | Default Ollama model |
| `ARIVU_OPENAI_CHAT_MODEL` | `gpt-4o-mini` | Default OpenAI chat model |
| `ARIVU_OPENAI_API_KEY` | — | OpenAI API key (required for OpenAI LLM/embeddings) |

#### Embeddings

| Variable | Default | Description |
|---|---|---|
| `ARIVU_EMBEDDING_BACKEND` | `local` | `local`, `openai`, or `ollama` |
| `ARIVU_LOCAL_EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace model name |
| `ARIVU_OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model |

#### Chunking

| Variable | Default | Description |
|---|---|---|
| `ARIVU_DEFAULT_CHUNK_SIZE` | `1000` | Characters per chunk |
| `ARIVU_DEFAULT_CHUNK_OVERLAP` | `200` | Overlap between consecutive chunks |

#### Retrieval

| Variable | Default | Description |
|---|---|---|
| `ARIVU_DEFAULT_TOP_K` | `5` | Number of chunks to retrieve |
| `ARIVU_DEFAULT_MIN_SCORE` | `0.0` | Minimum relevance score threshold (0–1) |
| `ARIVU_DEFAULT_MAX_CONTEXT_TOKENS` | `6000` | Maximum tokens sent to LLM as context |

#### Reranking

| Variable | Default | Description |
|---|---|---|
| `ARIVU_RERANKER_ENABLED` | `true` | Enable cross-encoder reranking |
| `ARIVU_RERANKER_MODEL` | `cross-encoder/ms-marco-MiniLM-L-12-v2` | HuggingFace cross-encoder model |

#### Web Search

| Variable | Default | Description |
|---|---|---|
| `ARIVU_WEB_SEARCH_BACKEND` | `tavily` | Search provider (`tavily` only) |
| `ARIVU_TAVILY_API_KEY` | — | Tavily API key |
| `ARIVU_WEB_SEARCH_RESULTS_COUNT` | `3` | Number of web results to fetch |
| `ARIVU_WEB_SEARCH_ENABLED_DEFAULT` | `false` | Enable web search by default for new projects |

---

### Per-Project UI Settings

These are configurable per project in the Settings view and persisted to `localStorage`.

#### Retrieval

| Setting | Default | Description |
|---|---|---|
| Top-K | `5` | Number of chunks returned from vectorstore |
| Search type | `similarity` | `similarity` (cosine) or `mmr` (Maximal Marginal Relevance) |
| Query translation | `true` | Condense follow-up questions using chat history |
| Multi-query | `false` | Generate 3 alternative queries for better recall |
| Show debug panel | `false` | Show retrieved chunks, scores, and rewritten query |

#### LLM

| Setting | Default | Description |
|---|---|---|
| Model | server default | Model name (auto-routes to Ollama or OpenAI by name) |
| Temperature | `0.2` | LLM sampling temperature (0 = deterministic, 1 = creative) |
| API key override | — | Per-project API key (overrides environment variable) |
| Base URL override | — | Per-project LLM endpoint |

#### Embedding

| Setting | Default | Description |
|---|---|---|
| Embedding model | project default | Set at project creation; changing requires reindexing |
| API key override | — | Per-project embedding API key |
| Base URL override | — | Per-project embedding endpoint |

#### RAG Quality

| Setting | Default | Description |
|---|---|---|
| Min score | `0.0` | Discard chunks below this relevance score |
| Enable reranking | `true` | Cross-encoder reranking of retrieved chunks |
| Max context tokens | `6000` | Hard cap on tokens sent to the LLM |

#### Web Search

| Setting | Default | Description |
|---|---|---|
| Enabled | `false` | Toggle web search on/off |
| Threshold | `0.5` | Min relevance score below which web search activates (fallback mode) |
| Mode | `fallback` | `fallback` (use web only when retrieval score is low) or `augment` (always add web results) |
| API key | — | Tavily API key override |

---

## API Reference

All endpoints are prefixed with `/api`.

### Projects

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/projects` | Create a project (`name`, `description`, `embedding_model`) |
| `GET` | `/api/projects` | List all projects |
| `GET` | `/api/projects/{id}` | Get project details |
| `PATCH` | `/api/projects/{id}` | Update project name or embedding model |
| `DELETE` | `/api/projects/{id}` | Delete project and all data |

### Files

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/projects/{id}/files/upload` | Upload one or more files (multipart) |
| `GET` | `/api/projects/{id}/files` | List files and their indexing status |
| `DELETE` | `/api/projects/{id}/files/{file_id}` | Delete file from vectorstore and DB |
| `POST` | `/api/projects/{id}/files/{file_id}/reindex` | Re-run ingestion pipeline on a file |

### Query

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/projects/{id}/query` | RAG query (`question`, `history`, `settings`) |

### Study

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/projects/{id}/study` | Generate study materials (`mode`, `count`, `topic`) |

### Chat History

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/projects/{id}/history` | Retrieve full chat history |
| `DELETE` | `/api/projects/{id}/history` | Clear chat history |

### Models

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/models/embeddings` | List available embedding models with metadata |

### Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Returns `{ ok: true, version: "..." }` |

---

## Frontend Views

| View | Route | Description |
|---|---|---|
| **Chat** | `/chat` | Ask questions, view answers with sources, typing indicator, Shift+Enter for multiline |
| **Documents** | `/documents` | Drag-and-drop upload, file table with indexing progress, delete and reindex actions |
| **Settings** | `/settings` | All per-project RAG, LLM, embedding, and web-search settings |
| **Study** | `/study` | Generate quizzes, flashcard sets, or summaries from indexed documents |
| **Sources** | `/sources` | Inspect retrieved source chunks and relevance scores for the last query |

---

## Project Structure

```
arivu/
├── Arivu/
│   ├── Backend/                     # FastAPI Python application
│   │   ├── app/
│   │   │   ├── core/config.py       # All environment variable settings
│   │   │   ├── db/models.py         # SQLAlchemy models (Project, Document, Chunk, ChatMessage)
│   │   │   ├── rag/
│   │   │   │   ├── ingestion.py     # Full ingestion pipeline + RAPTOR
│   │   │   │   ├── retriever.py     # Retriever setup, reranking, multi-query
│   │   │   │   ├── embeddings.py    # Embedding provider factory
│   │   │   │   ├── llm.py           # LLM provider factory
│   │   │   │   └── vectorstore.py   # ChromaDB helpers
│   │   │   └── routes/              # FastAPI routers (projects, files, query, study, history)
│   │   └── .venv/                   # Python virtual environment
│   └── Frontend/
│       └── vue-project/             # Vue 3 + Vite + Electron
│           ├── src/
│           │   ├── views/           # Chat, Documents, Settings, Study, Sources
│           │   ├── components/      # ChatMessage, FileDropzone, FileTable, etc.
│           │   └── stores/          # Pinia stores (chat, settings, projects, files, study)
│           ├── electron/            # Electron main process
│           └── ELECTRON_README.md
├── start-arivu.command              # Start dev servers (backend + frontend)
├── test-electron-dev.sh             # Test Electron in dev mode
├── build-electron-app.sh            # Build production DMG
├── build-backend.sh                 # Build backend binary with PyInstaller
└── clean-databases.sh               # Wipe all user data and databases
```

---

## Quick Start

### Web / Development mode

```bash
./start-arivu.command
```

Backend runs at `http://localhost:8000`, frontend at `http://localhost:5173`.

### Electron (desktop) dev mode

```bash
./test-electron-dev.sh
```

### Production DMG build

```bash
./build-electron-app.sh
```

### Clean all data

```bash
./clean-databases.sh
```
