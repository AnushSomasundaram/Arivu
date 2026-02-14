"""CRUD helpers for projects, documents, and chunks."""

from __future__ import annotations

from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Project, Document, Chunk


# ── Projects ──────────────────────────────────────────────

async def create_project(
    db: AsyncSession, *, name: str, description: str = "", embedding_model: str | None = None
) -> Project:
    params = {"name": name, "description": description}
    params["embedding_model"] = embedding_model or "local:all-MiniLM-L6-v2"
    project = Project(**params)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def list_projects(db: AsyncSession) -> list[Project]:
    result = await db.execute(select(Project).order_by(Project.created_at.desc()))
    return list(result.scalars().all())


async def get_project(db: AsyncSession, project_id: str) -> Project | None:
    return await db.get(Project, project_id)


async def update_project(
    db: AsyncSession, project_id: str, *, name: str | None = None, embedding_model: str | None = None
) -> Project | None:
    project = await db.get(Project, project_id)
    if not project:
        return None
    if name is not None:
        project.name = name
    if embedding_model is not None:
        project.embedding_model = embedding_model
    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project_id: str) -> bool:
    project = await db.get(Project, project_id)
    if not project:
        return False
    await db.delete(project)
    await db.commit()
    return True


# ── Documents ─────────────────────────────────────────────

async def create_document(
    db: AsyncSession,
    *,
    project_id: str,
    filename: str,
    filetype: str,
    size_bytes: int,
    content_hash: str,
    mime_type: str | None = None,
    tags: list[str] | None = None,
) -> Document:
    doc = Document(
        project_id=project_id,
        filename=filename,
        filetype=filetype,
        size_bytes=size_bytes,
        content_hash=content_hash,
        mime_type=mime_type,
        tags=tags,
        status="queued",
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


async def list_documents(db: AsyncSession, project_id: str) -> list[Document]:
    result = await db.execute(
        select(Document)
        .where(Document.project_id == project_id)
        .order_by(Document.created_at.desc())
    )
    return list(result.scalars().all())


async def get_document(db: AsyncSession, doc_id: str) -> Document | None:
    return await db.get(Document, doc_id)


async def update_document_status(
    db: AsyncSession,
    doc_id: str,
    *,
    status: str,
    chunk_count: int | None = None,
    added_chunks: int | None = None,
    skipped_chunks: int | None = None,
    progress: int | None = None,
    error_message: str | None = None,
) -> None:
    doc = await db.get(Document, doc_id)
    if not doc:
        return
    doc.status = status
    if chunk_count is not None:
        doc.chunk_count = chunk_count
    if added_chunks is not None:
        doc.added_chunks = added_chunks
    if skipped_chunks is not None:
        doc.skipped_chunks = skipped_chunks
    if progress is not None:
        doc.progress = progress
    if error_message is not None:
        doc.error_message = error_message
    await db.commit()


async def delete_document(db: AsyncSession, doc_id: str) -> bool:
    doc = await db.get(Document, doc_id)
    if not doc:
        return False
    await db.delete(doc)
    await db.commit()
    return True


# ── Chunks ────────────────────────────────────────────────

async def create_chunks(db: AsyncSession, chunks: list[Chunk]) -> None:
    db.add_all(chunks)
    await db.commit()


async def get_chunks_for_document(db: AsyncSession, doc_id: str) -> list[Chunk]:
    result = await db.execute(
        select(Chunk).where(Chunk.document_id == doc_id).order_by(Chunk.chunk_index)
    )
    return list(result.scalars().all())


async def delete_chunks_for_document(db: AsyncSession, doc_id: str) -> int:
    result = await db.execute(sa_delete(Chunk).where(Chunk.document_id == doc_id))
    await db.commit()
    return result.rowcount  # type: ignore[return-value]
