
import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from app.rag.raptor import perform_clustering, recursive_embed_cluster_summarize, summarize_cluster

class MockEmbeddingBackend:
    def embed_texts(self, texts):
        # Return random embeddings
        return [np.random.rand(10).tolist() for _ in texts]

class MockLLMBackend:
    def generate(self, system, user):
        return "Summary of cluster"

def test_perform_clustering_small():
    # Test with too few items
    embeddings = np.random.rand(3, 10)
    clusters = perform_clustering(embeddings, n_neighbors=2, n_components=2)
    # Should get 1 cluster with all items
    assert len(clusters) == 1
    assert len(clusters[0]) == 3

@patch("app.rag.raptor.umap.UMAP")
@patch("app.rag.raptor.GaussianMixture")
def test_perform_clustering_logic(mock_gmm, mock_umap):
    # Mock UMAP fit_transform
    mock_umap_instance = mock_umap.return_value
    mock_umap_instance.fit_transform.return_value = np.random.rand(10, 2)
    
    # Mock GMM
    mock_gmm_instance = mock_gmm.return_value
    mock_gmm_instance.bic.return_value = 100
    mock_gmm_instance.predict_proba.return_value = np.array([[0.9, 0.1]] * 10)
    
    embeddings = np.random.rand(10, 10)
    clusters = perform_clustering(embeddings, n_neighbors=2)
    
    assert len(clusters) > 0

def test_summarize_cluster():
    llm = MockLLMBackend()
    summary = summarize_cluster(["a", "b"], llm)
    assert summary == "Summary of cluster"

@pytest.mark.asyncio
async def test_recursive_embed_cluster_summarize():
    texts = [f"Text {i}" for i in range(20)]
    embeddings = [np.random.rand(10).tolist() for _ in range(20)]
    emb_backend = MockEmbeddingBackend()
    
    # Mock LLM within the function
    with patch("app.rag.raptor.get_llm_backend", return_value=MockLLMBackend()):
        # Mock clustering to return 2 clusters
        with patch("app.rag.raptor.perform_clustering", return_value=[list(range(10)), list(range(10, 20))]):
            
            summary_texts, summary_metas, summary_embs = recursive_embed_cluster_summarize(
                texts, embeddings, emb_backend, level=1, max_levels=2
            )
            
            # Level 1 should have 2 summaries
            # Level 2 should have 1 summary (recursive) or more
            assert len(summary_texts) >= 2
            assert len(summary_metas) == len(summary_texts)
            assert len(summary_embs) == len(summary_texts)
            
            # Check metadata
            assert summary_metas[0]["level"] == 1
            assert "child_indices" in summary_metas[0]
