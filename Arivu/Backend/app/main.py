"""Arivu RAG Backend — FastAPI application entry point."""

from __future__ import annotations
import os
from pathlib import Path
def log_startup(msg):
    try:
        with open("/tmp/backend_startup.log", "a") as f:
            f.write(f"PID {os.getpid()}: {msg}\n")
    except: pass

log_startup(f"Module loading started... CWD: {os.getcwd()}")

from contextlib import asynccontextmanager
log_startup("Imported asynccontextmanager")
# Force reload
from fastapi import FastAPI
log_startup("Imported FastAPI")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
log_startup("Imported FastAPI middleware")

def configure_environment():
    """Configure environment variables for packaged app."""
    # Use user's home directory for data storage
    user_data_dir = Path(os.path.expanduser("~")) / ".arivu"
    user_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Set data dir
    os.environ["ARIVU_DATA_DIR"] = str(user_data_dir)
    
    # Set database URL if not set
    if "ARIVU_DATABASE_URL" not in os.environ:
        db_path = user_data_dir / "arivu.db"
        # Use sync sqlite for reliability if async causes issues, but keep async for now
        os.environ["ARIVU_DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
        log_startup(f"Database URL set to: {os.environ['ARIVU_DATABASE_URL']}")

configure_environment()

from app.api.routes_files import router as files_router
log_startup("Imported routes_files")
from app.api.routes_projects import router as projects_router
log_startup("Imported routes_projects")
from app.api.routes_query import router as query_router
log_startup("Imported routes_query")
from app.api.routes_models import router as models_router
log_startup("Imported routes_models")
from app.api.schemas import HealthResponse
log_startup("Imported HealthResponse")
from app.core.config import settings
log_startup("Imported settings")
from app.core.logging import setup_logging
log_startup("Imported setup_logging")
from app.db.session import init_db
log_startup("Imported init_db")


def validate_configuration() -> None:
    """Validate critical configuration on startup."""
    import logging
    log = logging.getLogger(__name__)

    warnings = []

    # Check LLM configuration
    if settings.llm_backend == "ollama":
        log.info(f"LLM: Ollama ({settings.ollama_model}) at {settings.ollama_base_url}")
    elif settings.llm_backend == "openai":
        if not settings.openai_api_key:
            warnings.append("OpenAI API key not set (ARIVU_OPENAI_API_KEY)")
        log.info(f"LLM: OpenAI ({settings.openai_chat_model})")

    # Check embedding configuration
    if settings.embedding_backend == "local":
        log.info(f"Embeddings: Local ({settings.local_embedding_model})")
    elif settings.embedding_backend == "openai":
        if not settings.openai_api_key:
            warnings.append("OpenAI API key not set for embeddings (ARIVU_OPENAI_API_KEY)")
        log.info(f"Embeddings: OpenAI ({settings.openai_embedding_model})")

    # Check web search configuration
    if settings.web_search_enabled_default and not settings.tavily_api_key:
        warnings.append(
            "Web search enabled by default but Tavily API key not set (ARIVU_TAVILY_API_KEY). "
            "Web search will fail unless users provide their own API keys."
        )

    # Log warnings
    if warnings:
        log.warning("Configuration warnings:")
        for warning in warnings:
            log.warning(f"  - {warning}")
    else:
        log.info("Configuration validated successfully")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    setup_logging(debug=settings.debug)
    validate_configuration()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    await init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow the Vue frontend in dev
# Parse CORS origins from comma-separated string or use "*" for all
cors_origins_list = [origin.strip() for origin in settings.cors_origins.split(",")] if settings.cors_origins != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount route groups
app.include_router(projects_router)
app.include_router(files_router)
app.include_router(query_router)
app.include_router(models_router)
# New Study Mode router
from app.api.routes_study import router as study_router
log_startup("Imported study_router")
app.include_router(study_router)
# Chat History Ruter
from app.api.routes_history import router as history_router
log_startup("Imported history_router")
app.include_router(history_router)


@app.get("/api/health", response_model=HealthResponse, tags=["health"])
async def health():
    return HealthResponse()


from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
import logging

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.error(f"Validation Error: {exc.errors()}")
    logging.error(f"Body: {await request.body()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(exc.body)},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.exception(f"Global Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__},
    )

if __name__ == "__main__":
    import multiprocessing
    import sys
    import argparse

    # Add freeze_support for PyInstaller
    multiprocessing.freeze_support()

    parser = argparse.ArgumentParser(description="Arivu Backend")
    parser.add_argument("--host", type=str, default=None, help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=None, help="Port to run the server on")
    args = parser.parse_args()

    # Use CLI args if provided, otherwise fall back to environment variables (from settings)
    host = args.host if args.host is not None else settings.backend_host
    port = args.port if args.port is not None else settings.backend_port

    print("Backend starting...", flush=True)
    print(f"Configuration: host={host}, port={port}", flush=True)

    try:
        import uvicorn
        print("Uvicorn imported...", flush=True)
        print(f"Starting Uvicorn server on {host}:{port}...", flush=True)
        uvicorn.run(app, host=host, port=port, log_level="debug")
    except Exception as e:
        print(f"Failed to start backend: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
