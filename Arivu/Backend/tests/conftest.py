"""Shared test fixtures — in-memory DB, test client, mock embeddings."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Base
from app.db.session import get_db

# Override data dir before importing app
_tmpdir = tempfile.mkdtemp()
os.environ["ARIVU_DATA_DIR"] = _tmpdir
os.environ["ARIVU_DATABASE_URL"] = "sqlite+aiosqlite://"

from app.core.config import settings  # noqa: E402

settings.data_dir = Path(_tmpdir)

from app.main import app  # noqa: E402


# ── Async DB engine for tests (in-memory SQLite) ─────────

_test_engine = create_async_engine("sqlite+aiosqlite://", echo=False)
_test_session_factory = async_sessionmaker(_test_engine, class_=AsyncSession, expire_on_commit=False)


async def _override_get_db():
    async with _test_session_factory() as session:
        yield session


app.dependency_overrides[get_db] = _override_get_db


@pytest_asyncio.fixture(autouse=True)
async def _setup_db():
    """Create tables before each test, drop after."""
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db():
    """Provide a test DB session."""
    async with _test_session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    """Provide an async test client for the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ── Mock embedding backend ────────────────────────────────

class FakeEmbedding:
    """Returns deterministic 8-dim embeddings for testing."""

    @property
    def dimension(self) -> int:
        return 8

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        import hashlib
        result = []
        for t in texts:
            h = hashlib.md5(t.encode()).digest()[:self.dimension]
            vec = [b / 255.0 for b in h]
            result.append(vec)
        return result

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


@pytest.fixture(autouse=True)
def _mock_embeddings():
    """Replace the real embedding backend with a fast fake everywhere it's instantiated.

    Note: This patches the shared embeddings factory in app.rag.embeddings.get_embeddings
    which is used by both routes_query and routes_files.
    """
    fake = FakeEmbedding()
    with patch("app.rag.embeddings.get_embeddings", return_value=fake):
        yield
