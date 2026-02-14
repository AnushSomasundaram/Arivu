"""API routes for project CRUD."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import ProjectCreate, ProjectOut, ProjectUpdate
from app.db.crud import create_project, list_projects, get_project, update_project, delete_project, list_documents
from app.db.session import get_db
from app.rag.vectorstore import delete_project_data
from app.rag.model_validation import validate_embedding_model, normalize_model_name

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectOut, status_code=201)
async def create(body: ProjectCreate, db: AsyncSession = Depends(get_db)):
    """Create a new project with validated embedding model."""
    # Validate and normalize embedding model
    embedding_model = body.embedding_model or "local:all-MiniLM-L6-v2"
    is_valid, error_msg = validate_embedding_model(embedding_model)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid embedding model: {error_msg}")
    
    normalized_model = normalize_model_name(embedding_model)
    
    project = await create_project(
        db, name=body.name, description=body.description, embedding_model=normalized_model
    )
    return project


@router.get("", response_model=list[ProjectOut])
async def list_all(db: AsyncSession = Depends(get_db)):
    """List all projects."""
    return await list_projects(db)


@router.get("/{project_id}", response_model=ProjectOut)
async def get_one(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get project details."""
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectOut)
async def update(project_id: str, body: ProjectUpdate, db: AsyncSession = Depends(get_db)):
    """Update a project (cannot change embedding model if documents exist)."""
    # If trying to change embedding model, validate it
    if body.embedding_model is not None:
        # Check if project has documents
        existing_project = await get_project(db, project_id)
        if not existing_project:
            raise HTTPException(404, "Project not found")
        
        # Get document count
        documents = await list_documents(db, project_id)
        if documents:
            raise HTTPException(
                400, 
                f"Cannot change embedding model after documents have been added. "
                f"This project has {len(documents)} document(s). "
                f"Create a new project with the desired embedding model instead."
            )
        
        # Validate new model
        is_valid, error_msg = validate_embedding_model(body.embedding_model)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid embedding model: {error_msg}")
        
        # Normalize model name
        body.embedding_model = normalize_model_name(body.embedding_model)
    
    project = await update_project(
        db, project_id, name=body.name, embedding_model=body.embedding_model
    )
    if not project:
        raise HTTPException(404, "Project not found")
    return project


@router.delete("/{project_id}", status_code=204)
async def remove(project_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a project and all its on-disk data."""
    deleted = await delete_project(db, project_id)
    if not deleted:
        raise HTTPException(404, "Project not found")
    delete_project_data(project_id)
