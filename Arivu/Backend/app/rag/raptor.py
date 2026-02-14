"""RAPTOR using direct LangChain calls.

Hierarchical clustering and summarization.
"""

from __future__ import annotations

import logging
from typing import List, Tuple

from langchain_core.embeddings import Embeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from app.rag.prompts import RAPTOR_SUMMARIZATION_PROMPT
from app.core.config import settings

log = logging.getLogger(__name__)


def perform_clustering(
    embeddings: list[list[float]],
    n_neighbors: int = 10,
    n_components: int = 2,
    random_state: int = 42,
) -> List[List[int]]:
    """Cluster embeddings using UMAP + GMM."""
    import numpy as np
    from umap import UMAP
    from sklearn.mixture import GaussianMixture

    emb_array = np.array(embeddings)
    if len(emb_array) <= n_components + 2 or len(emb_array) < 5:
        return [list(range(len(emb_array)))]

    actual_n_neighbors = min(n_neighbors, len(emb_array) - 1)
    umap_model = UMAP(
        n_neighbors=actual_n_neighbors if actual_n_neighbors > 1 else 2,
        n_components=n_components,
        metric="cosine",
        random_state=random_state,
    )
    reduced_embeddings = umap_model.fit_transform(emb_array)

    n_samples = len(emb_array)
    max_k = min(int(np.sqrt(n_samples)) + 1, 10)
    
    best_k = 1
    best_bic = np.inf
    best_gmm = None

    for k in range(1, max_k + 1):
        gmm = GaussianMixture(n_components=k, random_state=random_state)
        gmm.fit(reduced_embeddings)
        bic = gmm.bic(reduced_embeddings)
        if bic < best_bic:
            best_bic = bic
            best_k = k
            best_gmm = gmm
    
    probs = best_gmm.predict_proba(reduced_embeddings)
    clusters: List[List[int]] = [[] for _ in range(best_k)]
    for i, p_vec in enumerate(probs):
        label = int(np.argmax(p_vec))
        clusters[label].append(i)
        
    return [c for c in clusters if c]


def summarize_cluster(cluster_texts: List[str], llm) -> str:
    """Generate a summary for a cluster using direct LangChain call."""
    context = "\n\n".join(cluster_texts)
    prompt = RAPTOR_SUMMARIZATION_PROMPT.format(context=context)
    
    resp = llm.invoke([SystemMessage(content="You are a helpful assistant."), HumanMessage(content=prompt)])
    return (resp.content or "").strip()


def recursive_embed_cluster_summarize(
    texts: List[str],
    embedding_backend: Embeddings,
    llm,
    level: int = 1,
    max_levels: int = 3,
) -> Tuple[List[str], List[dict]]:
    """Recursively process texts to build a RAPTOR tree."""
    if level > max_levels or len(texts) <= 5:
        return [], []

    embeddings = embedding_backend.embed_documents(texts)
    clusters = perform_clustering(embeddings)

    summary_texts: List[str] = []
    summary_metadatas: List[dict] = []
    
    for i, cluster_indices in enumerate(clusters):
        cluster_content = [texts[idx] for idx in cluster_indices]
        summary = summarize_cluster(cluster_content, llm)
        if not summary: continue
            
        summary_texts.append(summary)
        summary_metadatas.append({
            "level": level,
            "cluster_id": i,
            "child_indices": str(cluster_indices), 
            "child_count": len(cluster_indices)
        })

    if not summary_texts: return [], []

    next_texts, next_metas = recursive_embed_cluster_summarize(
        summary_texts, embedding_backend, llm, level=level + 1, max_levels=max_levels,
    )

    return (summary_texts + next_texts, summary_metadatas + next_metas)
