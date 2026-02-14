from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.api.schemas import ChatMessageOut
from app.db import models
from app.db.session import get_db

router = APIRouter(prefix="/api/projects/{project_id}/history", tags=["history"])


@router.get("", response_model=list[ChatMessageOut])
async def get_history(project_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve chat history for a project."""
    stmt = (
        select(models.ChatMessage)
        .where(models.ChatMessage.project_id == project_id)
        .order_by(models.ChatMessage.created_at)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.delete("", status_code=204)
async def clear_history(project_id: str, db: AsyncSession = Depends(get_db)):
    """Clear all chat history for a project."""
    stmt = delete(models.ChatMessage).where(models.ChatMessage.project_id == project_id)
    await db.execute(stmt)
    await db.commit()
