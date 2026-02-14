"""API route for RAG query using direct LangChain calls."""

from __future__ import annotations

import logging
import time
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.api.schemas import QueryRequest, QueryResponse, RetrievalDebugOut, SourceOut, ChatMessage
from app.db import crud
from app.db.session import get_db
from app.core.config import settings
from app.rag.prompts import (
    RAG_SYSTEM_PROMPT,
    RAG_USER_TEMPLATE,
    CONDENSE_QUESTION_CHAT_PROMPT,
    MULTI_QUERY_CHAT_PROMPT,
    RAG_PROMPT,
)
from app.rag.retriever import get_retriever, doc_to_chunk
from app.rag.vectorstore import get_project_vectorstore
from app.rag.llm import get_llm
from app.rag.embeddings import get_embeddings

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects/{project_id}/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def query_rag(
    project_id: str,
    body: QueryRequest,
    db: AsyncSession = Depends(get_db),
):
    project = await crud.get_project(db, project_id)
    if not project: raise HTTPException(404)

    s = body.settings

    # Initialize LLM and embeddings with proper error handling
    try:
        llm = get_llm(
            s.model,
            api_key=getattr(s, 'api_key', None),
            base_url=getattr(s, 'base_url', None),
            temperature=s.temperature,
            max_tokens=2048
        )
        embeddings = get_embeddings(
            project.embedding_model,
            api_key=getattr(s, 'embedding_api_key', None),
            base_url=getattr(s, 'embedding_base_url', None)
        )
    except ValueError as e:
        # Re-raise as HTTP 400 with helpful message
        raise HTTPException(status_code=400, detail=str(e))

    vectorstore = get_project_vectorstore(project_id, embedding_function=embeddings)

    # 1. Setup Retriever
    retriever = get_retriever(vectorstore, s, llm)

    # 2. Setup History Awareness
    # If history is present, this chain rewrites the question.
    history_aware_retriever = create_history_aware_retriever(
        llm, 
        retriever, 
        CONDENSE_QUESTION_CHAT_PROMPT
    )

    # 3. Setup Document Combination (Generation)
    # This chain takes retrieved docs and passes them to the LLM with the prompt.
    question_answer_chain = create_stuff_documents_chain(llm, RAG_PROMPT)

    # 4. Fetch Global Summaries (RAPTOR Injection)
    # We fetch high-level summaries to provide "big picture" context
    async def get_global_context():
        # Fetch summaries (level > 0)
        # We limit to 5 to avoid polluting context too much, favoring highest levels
        try:
            results = await run_in_threadpool(
                vectorstore.get,
                where={"level": {"$gt": 0}},
                limit=5
            )
            docs = []
            if results and results["documents"]:
                from langchain_core.documents import Document
                for i, text in enumerate(results["documents"]):
                    meta = results["metadatas"][i] if results["metadatas"] else {}
                    docs.append(Document(page_content=text, metadata=meta))
            # Sort by level descending (highest abstraction first)
            docs.sort(key=lambda d: d.metadata.get("level", 0), reverse=True)
            return docs
        except Exception as e:
            log.warning(f"Failed to fetch global context: {e}")
            return []

    global_docs = await get_global_context()

    # 5. Prepare Chat History
    chat_history = []
    if body.history:
        for msg in body.history[-6:]:
            if msg.role == "user":
                chat_history.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                chat_history.append(AIMessage(content=msg.content))

    # 6. Query Translation (Standalone & Sub-queries)
    standalone_query = body.question
    sub_queries = []
    retrieval_method = s.search_type

    # A. If history, get standalone for search
    if body.history:
        # Use a simple prompt/chain to rephrase the question
        condense_chain = CONDENSE_QUESTION_CHAT_PROMPT | llm | (lambda x: x.content)
        standalone_query = await run_in_threadpool(
            condense_chain.invoke,
            {"input": body.question, "chat_history": chat_history}
        )
        log.info(f"Standalone Query: {standalone_query}")

    # B. If Multi-Query, generate alternatives
    if s.query_translation:
        retrieval_method = "multi_query_" + s.search_type
        mq_chain = MULTI_QUERY_CHAT_PROMPT | llm | (lambda x: x.content.split("\n"))
        alternatives = await run_in_threadpool(
            mq_chain.invoke,
            {"question": standalone_query}
        )
        # Parse lines and clean up artifacts like "1. ", "Query: ", etc.
        import re
        sub_queries = []
        for line in alternatives:
            clean = re.sub(r'^\d+\.\s*', '', line.strip()) # Remove "1. "
            if clean: sub_queries.append(clean)
        
        # LOGGING FOR DEBUGGING Hallucinations
        log.info(f"Generated {len(sub_queries)} sub-queries for focus: {standalone_query}")
        for idx, sq in enumerate(sub_queries):
            log.info(f"  [{idx}] {sq}")
            
        log.info(f"Sub-queries: {sub_queries}")
    
    # 7. Retrieve Specific Chunks
    # Combining all queries for retrieval
    all_queries = [standalone_query] + sub_queries
    retrived_docs_with_scores = []
    
    # We use vectorstore directly for retrieval to get SCORES if reranking is off
    # If reranking is ON, retriever.invoke handles it via ContextualCompression
    for q in all_queries:
        if s.enable_reranking:
            # ContextualCompressionRetriever returns docs with relevance_score in metadata
            batch = await run_in_threadpool(retriever.invoke, q)
            retrived_docs_with_scores.extend(batch)
        else:
            # chroma.similarity_search_with_score returns List[Tuple[Document, float]]
            # We convert Tuple to Document with score in metadata
            batch = await run_in_threadpool(
                vectorstore.similarity_search_with_score,
                q,
                k=s.k
            )
            for doc, score in batch:
                doc.metadata["score"] = score # Note: Chroma returns DISTANCE (lower is better usually)
                retrived_docs_with_scores.append(doc)
    
    # Remove duplicates by content
    seen = set()
    unique_docs = []
    for d in retrived_docs_with_scores:
        if d.page_content not in seen:
            unique_docs.append(d)
            seen.add(d.page_content)
    
    # Apply k limit after merging
    retrieved_docs = unique_docs[:s.k]

    # 8. Merge Context (Global + Local)
    all_docs = global_docs + retrieved_docs

    # 9. Generate Answer
    t0 = time.perf_counter()
    answer = await run_in_threadpool(
        question_answer_chain.invoke,
        {"context": all_docs, "input": standalone_query, "chat_history": chat_history}
    )
    duration_ms = (time.perf_counter() - t0) * 1000

    # 10. Process Output
    sources = []
    for doc in all_docs:
        chunk = doc_to_chunk(doc)
        sources.append(
            SourceOut(
                source_id=chunk.chunk_id,
                filename=chunk.filename,
                page=chunk.page,
                snippet=chunk.text[:300],
                content=chunk.text,
                score=round(chunk.score, 4) if chunk.score is not None else None,
                file_id=chunk.doc_id,
            )
        )

    # 11. Populate Debug Info
    debug_info = None
    if s.show_debug:
        debug_info = RetrievalDebugOut(
            rewritten_query=standalone_query if body.history else None,
            queries=sub_queries if sub_queries else None,
            retrieval_method=retrieval_method,
            k=s.k,
            scores=[s.score for s in sources if s.score is not None]
        )

    # 12. Save Interaction to History
    try:
        from app.db import models
        user_msg = models.ChatMessage(
            project_id=project_id,
            role="user",
            content=body.question
        )
        ai_msg = models.ChatMessage(
            project_id=project_id,
            role="assistant",
            content=answer,
            metadata_json={
                "sources": [s.model_dump() for s in sources],
                "debug": debug_info.model_dump() if debug_info else None
            }
        )
        db.add(user_msg)
        db.add(ai_msg)
        await db.commit()
    except Exception as e:
        log.error(f"Failed to save chat history: {e}")

    return QueryResponse(answer=answer, sources=sources, debug=debug_info)
