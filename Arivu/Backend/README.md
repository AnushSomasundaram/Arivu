# Arivu RAG Backend

**A production-ready, multi-project RAG (Retrieval-Augmented Generation) system built entirely on LangChain.**

Arivu is a powerful document intelligence platform that enables semantic search and question-answering across your documents. Each project maintains isolated document sets, vector stores, and configurations.

## ✨ Key Features

### 🏗️ **Pure LangChain Architecture**
- Built exclusively with LangChain components for maximum compatibility and maintainability
- Uses `create_retrieval_chain` and `create_history_aware_retriever` for robust RAG pipelines
- Declarative chain composition with LangChain's `Runnable` interface

### 📁 **Universal File Support (50+ Formats)**
- **Office**: Word (`.docx`, `.doc`), Excel (`.xlsx`, `.xls`), PowerPoint (`.pptx`, `.ppt`)
- **LibreOffice**: `.odt`, `.ods`, `.odp`
- **Documents**: PDF, Markdown, HTML, XML, RTF, EPUB
- **Data**: CSV, JSON, YAML, TOML
- **Code**: Python, JavaScript/TypeScript, Java, C/C++, Go, Rust, SQL, Jupyter Notebooks
- **Images**: PNG, JPG, GIF, BMP, TIFF (with OCR via Unstructured)
- **Email**: EML, MSG

### 🧠 **Advanced Retrieval**
- **MultiQueryRetriever**: Automatically generates multiple query variations for improved recall
- **Chat History Context**: Maintains conversation context and resolves coreferences
- **MMR (Maximal Marginal Relevance)**: Diverse result selection
- **Cross-Encoder Reranking**: Precision-focused reranking with HuggingFace models
- **RAPTOR**: Recursive clustering and summarization for hierarchical document understanding

### 🤖 **Flexible LLM Support**
- **Local**: Ollama (Llama 3, Mistral, Qwen, etc.)
- **Cloud**: OpenAI (GPT-4o, GPT-4o-mini, etc.)
- **Embeddings**: Local (SentenceTransformers) or OpenAI

### 🏢 **Multi-Tenant Architecture**
- Isolated projects with independent document sets and vector stores
- Per-project configuration for chunking, retrieval, and generation
- ChromaDB for efficient vector storage

## 🔄 System Architecture

### Ingestion Pipeline

```
File Upload → Document Loader → Text Splitter → Embeddings → Vector Store
                                                      ↓
                                              RAPTOR (if >10 chunks)
                                                      ↓
                                        Clustering → Summarization → Recursive Processing
```

1. **Document Loading**: LangChain loaders for 50+ file types
2. **Text Splitting**: Configurable chunk size (default: 1000 chars, 200 overlap)
3. **Embedding**: Generate vectors using local or cloud models
4. **RAPTOR Processing** (for large documents):
   - Cluster chunks using UMAP + GMM
   - Generate hierarchical summaries with LLM
   - Store summaries as additional retrievable nodes

### Retrieval Pipeline

```
User Query → History-Aware Retriever → MultiQuery (optional) → Vector Search
                                                                      ↓
                                                              Reranking (optional)
                                                                      ↓
                                                          Retrieval Chain → LLM → Response
```

1. **Query Contextualization**: Incorporates chat history to resolve coreferences
2. **Multi-Query Generation**: Creates query variations for comprehensive retrieval
3. **Vector Search**: Similarity or MMR-based retrieval
4. **Reranking**: Cross-encoder scoring for precision
5. **Generation**: LLM generates cited, contextual responses

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- (Optional) [Ollama](https://ollama.ai/) for local LLM
- (Optional) OpenAI API key for cloud models

### Installation

```bash
cd Arivu/Backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Configuration

Create a `.env` file (all settings have sensible defaults):

```env
# Embedding Backend
ARIVU_EMBEDDING_BACKEND=local              # "local" or "openai"
ARIVU_LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2

# LLM Backend
ARIVU_LLM_BACKEND=ollama                   # "ollama" or "openai"
ARIVU_OLLAMA_BASE_URL=http://localhost:11434
ARIVU_OLLAMA_MODEL=llama3

# OpenAI (if using cloud models)
ARIVU_OPENAI_API_KEY=sk-...
ARIVU_OPENAI_CHAT_MODEL=gpt-4o-mini
ARIVU_OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Retrieval Configuration
ARIVU_DEFAULT_TOP_K=5
ARIVU_DEFAULT_MIN_SCORE=0.0
ARIVU_RERANKER_ENABLED=true
ARIVU_RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-12-v2

# Chunking
ARIVU_DEFAULT_CHUNK_SIZE=1000
ARIVU_DEFAULT_CHUNK_OVERLAP=200

# Web Search (optional)
ARIVU_TAVILY_API_KEY=tvly-...
ARIVU_WEB_SEARCH_ENABLED_DEFAULT=false
```

### Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

API documentation: http://localhost:8000/docs

### Run Tests

```bash
pytest -v
```

## 📚 API Usage

### 1. Create a Project

```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research Papers",
    "description": "ML and AI research",
    "embedding_model": "all-MiniLM-L6-v2",
    "chunk_size": 1000,
    "chunk_overlap": 200
  }'
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Research Papers",
  "created_at": "2024-02-12T10:30:00Z"
}
```

### 2. Upload Documents

```bash
PROJECT_ID="550e8400-e29b-41d4-a716-446655440000"

curl -X POST "http://localhost:8000/api/projects/${PROJECT_ID}/files/upload" \
  -F "files=@paper.pdf" \
  -F "files=@notes.docx" \
  -F "files=@data.csv"
```

Supports 50+ file formats including PDF, Office documents, code files, and images.

### 3. Query with RAG

```bash
curl -X POST "http://localhost:8000/api/projects/${PROJECT_ID}/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main findings?",
    "history": [
      {"role": "user", "content": "Tell me about the methodology"},
      {"role": "assistant", "content": "The study used a randomized controlled trial..."}
    ],
    "settings": {
      "k": 5,
      "search_type": "mmr",
      "rerank": true,
      "query_translation": true,
      "min_score": 0.3
    }
  }'
```

Response:
```json
{
  "answer": "The main findings indicate that...",
  "sources": [
    {
      "content": "...",
      "filename": "paper.pdf",
      "page": 5,
      "score": 0.89
    }
  ]
}
```

### Query Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `k` | int | 5 | Number of chunks to retrieve |
| `search_type` | string | "similarity" | "similarity" or "mmr" |
| `rerank` | bool | true | Enable cross-encoder reranking |
| `query_translation` | bool | false | Enable MultiQueryRetriever |
| `min_score` | float | 0.0 | Minimum similarity threshold |
| `web_search` | bool | false | Include web search results |

## 🏗️ Project Structure

```
app/
├── api/
│   ├── routes_projects.py    # Project CRUD
│   ├── routes_files.py        # File upload & ingestion
│   ├── routes_query.py        # RAG query endpoint
│   └── schemas.py             # Pydantic models
├── rag/
│   ├── ingestion.py           # Document loading & chunking
│   ├── retriever.py           # Retrieval strategies
│   ├── prompts.py             # LangChain prompt templates
│   ├── raptor.py              # Hierarchical summarization
│   ├── vectorstore.py         # ChromaDB interface
│   └── web_search.py          # Tavily integration
├── core/
│   ├── config.py              # Settings management
│   └── logging.py             # Structured logging
├── db/
│   ├── models.py              # SQLAlchemy models
│   ├── crud.py                # Database operations
│   └── session.py             # DB connection
└── main.py                    # FastAPI app entry point
```

## 🔧 Advanced Features

### RAPTOR (Recursive Abstractive Processing)

Automatically enabled for documents with >10 chunks:

1. **Clustering**: Groups related chunks using UMAP + GMM
2. **Summarization**: Generates hierarchical summaries
3. **Recursive Processing**: Builds multi-level abstraction tree
4. **Retrieval**: Searches both original chunks and summaries

### Chat History Context

The system maintains conversation context:

```python
# Example: Follow-up question
history = [
  {"role": "user", "content": "Who is the author?"},
  {"role": "assistant", "content": "The author is Dr. Smith."}
]

# This query will be contextualized automatically
query = "What is his background?"  # "his" → "Dr. Smith's"
```

### MultiQueryRetriever

Generates multiple query variations for improved recall:

```python
# Original query
"What are the benefits of RAG?"

# Generated variations
1. "What advantages does RAG provide?"
2. "How does RAG improve LLM performance?"
3. "What are the use cases for RAG systems?"
```

## 🌐 Frontend Integration

The backend is designed to work with the included Vue.js frontend:

```bash
cd Arivu/Frontend/vue-project
npm install
npm run dev
```

Frontend features:
- Project management UI
- Drag-and-drop file upload
- Interactive chat interface
- Source citation display
- Settings configuration

## 🔐 Security Considerations

- CORS enabled for development (configure for production)
- API key validation for cloud services
- File type validation on upload
- SQL injection protection via SQLAlchemy
- Input sanitization on all endpoints

## 📊 Performance Tips

1. **Use MMR for diverse results**: Set `search_type: "mmr"` when you need varied perspectives
2. **Enable reranking for precision**: Set `rerank: true` for high-accuracy requirements
3. **Adjust chunk size**: Smaller chunks (500-800) for precise retrieval, larger (1200-1500) for context
4. **Use MultiQuery sparingly**: Increases latency but improves recall for complex queries
5. **Set min_score threshold**: Filter low-quality results with `min_score: 0.3-0.5`

## 🤝 Contributing

Contributions are welcome! Please ensure:
- All code uses LangChain components (no custom wrappers)
- Tests pass (`pytest -v`)
- Code follows existing patterns
- Documentation is updated

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Built with:
- [LangChain](https://langchain.com/) - LLM application framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Unstructured](https://unstructured.io/) - Document parsing
- [Sentence Transformers](https://www.sbert.net/) - Embeddings
- [Ollama](https://ollama.ai/) - Local LLM runtime
