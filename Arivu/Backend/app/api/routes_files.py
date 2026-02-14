"""API routes for file management using direct LangChain calls."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.embeddings import Embeddings

from app.api.schemas import FileRecordOut, UploadedItem, UploadResult
from app.db import crud
from app.db.session import get_db
from app.rag.ingestion import ingest_document, save_uploaded_file
from app.rag.vectorstore import get_project_vectorstore
from app.rag.embeddings import get_embeddings
from app.utils.filetype import detect_filetype
from app.utils.hashing import sha256_bytes
from app.core.config import settings

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects/{project_id}/files", tags=["files"])


def _doc_to_file_record(doc) -> FileRecordOut:
    return FileRecordOut(
        id=doc.id,
        filename=doc.filename,
        size_bytes=doc.size_bytes,
        status=doc.status,
        created_at=doc.created_at,
        chunk_count=doc.chunk_count,
        mime_type=doc.mime_type,
        added_chunks=doc.added_chunks,
        skipped_chunks=doc.skipped_chunks,
        progress=doc.progress,
    )


@router.post("/upload", response_model=UploadResult, status_code=201)
async def upload(
    project_id: str,
    files: Annotated[list[UploadFile], File(...)],
    background_tasks: BackgroundTasks,
    embedding_api_key: Annotated[str | None, Form()] = None,
    embedding_base_url: Annotated[str | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
):
    project = await crud.get_project(db, project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    # Initialize embeddings with error handling
    try:
        log.info(f"Initializing embeddings for project {project_id}")
        log.info(f"Model: {project.embedding_model}")
        log.info(f"API Key provided in request: {'Yes' if embedding_api_key else 'No'}")
        if embedding_api_key:
            log.info(f"API Key length: {len(embedding_api_key)}")
            log.info(f"API Key prefix: {embedding_api_key[:3]}...")
            
        embedding_model = get_embeddings(
            project.embedding_model,
            api_key=embedding_api_key,
            base_url=embedding_base_url
        )
    except ValueError as e:
        log.error(f"Failed to initialize embeddings: {e}")
        # Re-raise as HTTP 400 with helpful message
        raise HTTPException(status_code=400, detail=str(e))

    uploaded: list[UploadedItem] = []

    for upload_file in files:
        filename = upload_file.filename or "unknown"
        content_type = upload_file.content_type
        filetype = detect_filetype(filename, content_type)
        if not filetype: continue

        content = await upload_file.read()
        doc = await crud.create_document(
            db, project_id=project_id, filename=filename, filetype=filetype,
            size_bytes=len(content), content_hash=sha256_bytes(content),
            mime_type=content_type
        )
        
        file_path = await save_uploaded_file(project_id, doc.id, filename, content)
        
        # Determine which LLM to use for RAPTOR based on embedding provider
        llm_config = None
        if "openai" in str(type(embedding_model)).lower():
            llm_config = {
                "model": "gpt-4o-mini",
                "api_key": embedding_api_key,
                "base_url": embedding_base_url
            }

        # Queue background task
        background_tasks.add_task(
            ingest_document,
            db_session_factory=get_db,
            project_id=project_id,
            doc_id=doc.id,
            file_path=file_path,
            filetype=filetype,
            filename=filename,
            embedding_model_config={
                "model_name": project.embedding_model,
                "api_key": embedding_api_key,
                "base_url": embedding_base_url
            },
            llm_config=llm_config
        )

        uploaded.append(UploadedItem(id=doc.id, filename=filename, status="queued"))

    return UploadResult(uploaded=uploaded)


@router.get("", response_model=list[FileRecordOut])
async def list_files(project_id: str, db: AsyncSession = Depends(get_db)):
    docs = await crud.list_documents(db, project_id)
    return [_doc_to_file_record(d) for d in docs]


@router.delete("/{file_id}", status_code=204)
async def delete_file(project_id: str, file_id: str, db: AsyncSession = Depends(get_db)):
    vectorstore = get_project_vectorstore(project_id)
    vectorstore.delete(where={"doc_id": file_id})
    await crud.delete_document(db, file_id)


@router.post("/{file_id}/reindex", status_code=202)
async def reindex_file(
    project_id: str,
    file_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    doc = await crud.get_document(db, file_id)
    project = await crud.get_project(db, project_id)
    if not doc or not project: raise HTTPException(404)

    vectorstore = get_project_vectorstore(project_id)
    vectorstore.delete(where={"doc_id": file_id})
    await crud.delete_chunks_for_document(db, file_id)

    raw_file = settings.data_dir / "projects" / project_id / "files" / f"{file_id}.{doc.filetype}"

    background_tasks.add_task(
        ingest_document,
        db_session_factory=get_db,
        project_id=project_id,
        doc_id=file_id,
        file_path=raw_file,
        filetype=doc.filetype,
        filename=doc.filename,
        embedding_model_config={
            "model_name": project.embedding_model,
        }
        # Note: API keys are not persisted in project, so they must be passed or used from env
    )
    return {"status": "queued"}
