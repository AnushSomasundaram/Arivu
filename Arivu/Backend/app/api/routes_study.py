"""API route for Study Mode (Global Document Understanding).

Uses RAPTOR summaries (if available) or raw chunks to generate high-level
study materials like Quizzes, Summaries, and Flashcards.
"""

from __future__ import annotations

import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool
from langchain_core.messages import HumanMessage, SystemMessage

from app.api.schemas import StudyRequest, StudyResponse, SourceOut
from app.db import crud
from app.db.session import get_db
from app.rag.prompts import STUDY_GUIDE_CHAT_PROMPT
from app.rag.vectorstore import get_project_vectorstore
from app.rag.llm import get_llm
from app.rag.retriever import doc_to_chunk

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects/{project_id}/study", tags=["study"])


@router.post("", response_model=StudyResponse)
async def generate_study_guide(
    project_id: str,
    body: StudyRequest,
    db: AsyncSession = Depends(get_db),
):
    project = await crud.get_project(db, project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    # 1. Initialize LLM
    s = body.settings
    try:
        llm = get_llm(
            s.model if s else "gpt-4o",
            api_key=getattr(s, 'api_key', None) if s else None,
            base_url=getattr(s, 'base_url', None) if s else None,
            temperature=0.7  # Creative for study guides
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2. Retrieve Global Context
    # Strategy: Prioritize RAPTOR summaries (level > 0). If none, use base chunks.
    vectorstore = get_project_vectorstore(project_id)
    
    # helper to fetch from chroma
    def fetch_context():
        # A. Try fetching summaries (level >= 1)
        # We sort by level descending to get highest abstraction first
        # Note: Chroma get() doesn't support sorting easily, so we sort in python.
        results = vectorstore.get(where={"level": {"$gte": 1}})
        
        docs = []
        if results and results["documents"]:
            # Reconstruct as chunks
            for i, text in enumerate(results["documents"]):
                meta = results["metadatas"][i] if results["metadatas"] else {}
                docs.append({"text": text, "metadata": meta})
            
            # Sort by level descending
            docs.sort(key=lambda x: x["metadata"].get("level", 0), reverse=True)
            return docs, "summaries"

        # B. Fallback: Fetch base chunks (limit 50 to avoid context overflow)
        # In a real system, we'd use Map-Reduce here for large docs without RAPTOR.
        results = vectorstore.get(limit=50) # default fetch
        if results and results["documents"]:
             for i, text in enumerate(results["documents"]):
                meta = results["metadatas"][i] if results["metadatas"] else {}
                docs.append({"text": text, "metadata": meta})
             return docs, "raw_chunks"
             
        return [], "empty"

    docs, source_type = await run_in_threadpool(fetch_context)
    
    if not docs:
        raise HTTPException(400, "No documents found in project. Please upload files first.")

    # 3. Format Context
    context_text = ""
    sources_out = []
    
    # We take top N chunks to fit context window
    # Assuming ~4k-8k context, 10-20 chunks is safe.
    # If we have high level summaries, a few is enough.
    MAX_CHUNKS = 20
    selected_docs = docs[:MAX_CHUNKS]
    
    for i, d in enumerate(selected_docs, 1):
        content = d["text"]
        meta = d["metadata"]
        filename = meta.get("filename", "unknown")
        context_text += f"[Source {i}] {filename} (Level {meta.get('level', 0)})\n{content}\n\n"
        
        # Prepare source output
        sources_out.append(SourceOut(
            source_id=meta.get("chunk_id", ""),
            filename=filename,
            snippet=content[:300],
            content=content,
            page=meta.get("page"),
            file_id=meta.get("doc_id"),
            source_type="local"
        ))

    # 4. Generate Guide
    chain = STUDY_GUIDE_CHAT_PROMPT | llm
    
    response = await run_in_threadpool(
        chain.invoke,
        {
            "context": context_text,
            "mode": body.mode,
            "count": body.count,
            "topic": body.topic or "General Overview"
        }
    )
    
    content = response.content if hasattr(response, "content") else str(response)

    return StudyResponse(
        content=content,
        mode=body.mode,
        sources=sources_out
    )
