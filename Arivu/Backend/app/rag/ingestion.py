"""Pure LangChain document ingestion pipeline.

Uses LangChain loaders, splitters, embeddings, and Chroma directly.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.db import crud
from app.db.models import Chunk
from app.rag.raptor import recursive_embed_cluster_summarize
from app.rag.vectorstore import get_project_vectorstore
from app.db.session import async_session_factory
from app.rag.embeddings import get_embeddings
from app.rag.llm import get_llm

log = logging.getLogger(__name__)


def _get_loader_for_file(file_path: Path, filetype: str):
    """Return appropriate LangChain document loader for the file type."""
    path_str = str(file_path)
    
    # Office Documents
    if filetype == "docx":
        from langchain_community.document_loaders import UnstructuredWordDocumentLoader
        return UnstructuredWordDocumentLoader(path_str)
    elif filetype == "doc":
        from langchain_community.document_loaders import UnstructuredWordDocumentLoader
        return UnstructuredWordDocumentLoader(path_str)
    elif filetype == "xlsx":
        from langchain_community.document_loaders import UnstructuredExcelLoader
        return UnstructuredExcelLoader(path_str)
    elif filetype == "xls":
        from langchain_community.document_loaders import UnstructuredExcelLoader
        return UnstructuredExcelLoader(path_str)
    elif filetype == "pptx":
        from langchain_community.document_loaders import UnstructuredPowerPointLoader
        return UnstructuredPowerPointLoader(path_str)
    elif filetype == "ppt":
        from langchain_community.document_loaders import UnstructuredPowerPointLoader
        return UnstructuredPowerPointLoader(path_str)
    
    # LibreOffice
    elif filetype == "odt":
        from langchain_community.document_loaders import UnstructuredODTLoader
        return UnstructuredODTLoader(path_str)
    elif filetype == "ods":
        from langchain_community.document_loaders import UnstructuredODTLoader
        return UnstructuredODTLoader(path_str)
    elif filetype == "odp":
        from langchain_community.document_loaders import UnstructuredODTLoader
        return UnstructuredODTLoader(path_str)
    
    # Documents
    elif filetype == "pdf":
        return PyMuPDFLoader(path_str)
    elif filetype == "md":
        from langchain_community.document_loaders import UnstructuredMarkdownLoader
        return UnstructuredMarkdownLoader(path_str)
    elif filetype == "html" or filetype == "htm":
        from langchain_community.document_loaders import UnstructuredHTMLLoader
        return UnstructuredHTMLLoader(path_str)
    elif filetype == "xml":
        from langchain_community.document_loaders import UnstructuredXMLLoader
        return UnstructuredXMLLoader(path_str)
    elif filetype == "rtf":
        from langchain_community.document_loaders import UnstructuredRTFLoader
        return UnstructuredRTFLoader(path_str)
    elif filetype == "epub":
        from langchain_community.document_loaders import UnstructuredEPubLoader
        return UnstructuredEPubLoader(path_str)
    
    # Data Files
    elif filetype == "csv":
        from langchain_community.document_loaders import CSVLoader
        return CSVLoader(path_str)
    elif filetype == "json" or filetype == "jsonl":
        from langchain_community.document_loaders import JSONLoader
        return JSONLoader(path_str, jq_schema=".", text_content=False)
    
    # Code Files (including Jupyter Notebooks)
    elif filetype == "ipynb":
        from langchain_community.document_loaders import NotebookLoader
        return NotebookLoader(path_str, include_outputs=True, max_output_length=20)
    
    # Images (with OCR)
    elif filetype in ("png", "jpg", "jpeg", "gif", "bmp", "tiff", "tif"):
        from langchain_community.document_loaders import UnstructuredImageLoader
        return UnstructuredImageLoader(path_str)
    
    # Email
    elif filetype == "eml":
        from langchain_community.document_loaders import UnstructuredEmailLoader
        return UnstructuredEmailLoader(path_str)
    elif filetype == "msg":
        from langchain_community.document_loaders import UnstructuredEmailLoader
        return UnstructuredEmailLoader(path_str)
    
    # Default: Plain text (for code files and others)
    else:
        return TextLoader(path_str, encoding="utf-8")


def _extract_text(file_path: Path, filetype: str) -> str:
    """Extract plain text from a file using LangChain loaders."""
    loader = _get_loader_for_file(file_path, filetype)
    docs = loader.load()
    return "\n".join(doc.page_content for doc in docs)


async def save_uploaded_file(
    project_id: str,
    doc_id: str,
    filename: str,
    content: bytes,
) -> Path:
    """Persist an uploaded file to disk and return the path."""
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
    dest = settings.data_dir / "projects" / project_id / "files" / f"{doc_id}.{ext}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)
    return dest


async def ingest_document(
    db_session_factory: Any = None,  # For background tasks
    *,
    project_id: str,
    doc_id: str,
    file_path: Path,
    filetype: str,
    filename: str,
    embedding_model_config: dict[str, Any] | Embeddings,
    llm_config: dict[str, Any] | Any | None = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
) -> int:
    """Run the full ingestion pipeline for a single document."""
    
    # Use factory if provided (for background tasks), otherwise use session
    if db_session_factory and not isinstance(db_session_factory, AsyncSession):
        async with async_session_factory() as db:
            return await _ingest_document_internal(
                db, project_id=project_id, doc_id=doc_id, file_path=file_path,
                filetype=filetype, filename=filename, 
                embedding_model_config=embedding_model_config,
                llm_config=llm_config, chunk_size=chunk_size, chunk_overlap=chunk_overlap
            )
    else:
        # Fallback for sync calling if ever needed (not recommended now)
        raise ValueError("Background execution requires db_session_factory")

async def _ingest_document_internal(
    db: AsyncSession,
    *,
    project_id: str,
    doc_id: str,
    file_path: Path,
    filetype: str,
    filename: str,
    embedding_model_config: dict[str, Any] | Embeddings,
    llm_config: dict[str, Any] | Any | None = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
) -> int:
    try:
        # Initialize models if they are configs
        if isinstance(embedding_model_config, dict):
            embedding_model = get_embeddings(
                embedding_model_config["model_name"],
                api_key=embedding_model_config.get("api_key"),
                base_url=embedding_model_config.get("base_url")
            )
        else:
            embedding_model = embedding_model_config

        llm = None
        if isinstance(llm_config, dict):
            llm = get_llm(
                llm_config["model"],
                api_key=llm_config.get("api_key"),
                base_url=llm_config.get("base_url")
            )
        elif llm_config:
            llm = llm_config

        # 1. Parse
        await crud.update_document_status(db, doc_id, status="parsing", progress=10)
        raw_text = await asyncio.to_thread(_extract_text, file_path, filetype)

        # 2. Chunk
        await crud.update_document_status(db, doc_id, status="chunking", progress=20)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        docs = splitter.create_documents([raw_text])
        
        # 3. Embed & Index
        await crud.update_document_status(db, doc_id, status="indexing", progress=40)
        
        log.info(f"Indexing document {doc_id} with {len(docs)} chunks")
        vectorstore = get_project_vectorstore(project_id, embedding_function=embedding_model)
        
        texts: list[str] = []
        metadatas: list[dict[str, Any]] = []
        ids: list[str] = []
        db_chunks: list[Chunk] = []

        for i, doc in enumerate(docs):
            chunk_id = f"{doc_id}_{i}"
            meta = {
                "doc_id": doc_id,
                "filename": filename,
                "filetype": filetype,
                "chunk_index": i,
                "level": 0,
            }
            texts.append(doc.page_content)
            metadatas.append(meta)
            ids.append(chunk_id)
            
            db_chunks.append(
                Chunk(
                    document_id=doc_id,
                    chunk_index=i,
                    text=doc.page_content,
                    embedding_id=chunk_id,
                    metadata_json=meta,
                )
            )

        # RAPTOR Integration
        if len(texts) > 10:
            await crud.update_document_status(db, doc_id, status="indexing", progress=60)
            try:
                if llm is None:
                    llm_name = settings.openai_chat_model if "openai" in str(embedding_model.__class__).lower() else settings.ollama_model
                    llm = get_llm(llm_name)

                r_texts, r_metas = await asyncio.to_thread(
                    recursive_embed_cluster_summarize,
                    texts,
                    embedding_model,
                    llm,
                )
                for i, (rt, rm) in enumerate(zip(r_texts, r_metas)):
                    idx = len(texts) + i
                    rid = f"{doc_id}_r{i}"
                    rm.update({"doc_id": doc_id, "filename": filename, "filetype": filetype})
                    texts.append(rt)
                    metadatas.append(rm)
                    ids.append(rid)
                    db_chunks.append(
                        Chunk(
                            document_id=doc_id,
                            chunk_index=idx,
                            text=rt,
                            embedding_id=rid,
                            metadata_json=rm,
                        )
                    )
            except Exception as e:
                log.error(f"RAPTOR summarization failed: {e}")

        # 4. Add to Vectorstore
        await crud.update_document_status(db, doc_id, status="indexing", progress=80)
        from langchain_community.vectorstores.utils import filter_complex_metadata
        from langchain_core.documents import Document as LCDocument
        
        temp_docs = [LCDocument(page_content=t, metadata=m) for t, m in zip(texts, metadatas)]
        filtered_docs = filter_complex_metadata(temp_docs)
        final_metadatas = [d.metadata for d in filtered_docs]

        if len(texts) > 0:
            await asyncio.to_thread(
                vectorstore.add_texts,
                texts=texts,
                metadatas=final_metadatas,
                ids=ids
            )
        
        # Bulk create in DB
        await crud.create_chunks(db, db_chunks)

        await crud.update_document_status(
            db, doc_id, status="indexed", chunk_count=len(docs), added_chunks=len(texts), progress=100
        )
        return len(texts)

    except Exception as exc:
        log.exception("Ingestion failed: %s", exc)
        await crud.update_document_status(db, doc_id, status="failed", error_message=str(exc))
        return 0
