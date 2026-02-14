
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_embeddings")

def check_numpy_scipy():
    try:
        import numpy
        import scipy
        logger.info(f"Numpy version: {numpy.__version__}")
        logger.info(f"Scipy version: {scipy.__version__}")
    except Exception as e:
        logger.error(f"Numpy/Scipy check failed: {e}")
        return False
    return True

def check_sentence_transformers():
    print("Checking sentence-transformers...")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        emb = model.encode("hello world")
        logger.info(f"SentenceTransformer works. Embedding shape: {emb.shape}")
    except Exception as e:
        logger.error(f"SentenceTransformer check failed: {e}")
        return False
    return True

def check_ollama():
    print("Checking Ollama...")
    try:
        import httpx
        try:
            resp = httpx.post(
                "http://localhost:11434/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": "test"},
                timeout=5.0
            )
            if resp.status_code == 200:
                logger.info("Ollama embedding works.")
            else:
                logger.warning(f"Ollama returned {resp.status_code}: {resp.text}")
                # Try pulling if not found
                if "not found" in resp.text:
                    logger.info("Model not found. Try 'ollama pull nomic-embed-text'")
        except Exception as e:
             logger.error(f"Ollama connection failed: {e}")
             return False
    except ImportError:
        logger.error("httpx not installed")
        return False
    return True

def check_chromadb():
    print("Checking ChromaDB...")
    try:
        import chromadb
        logger.info(f"ChromaDB version: {chromadb.__version__}")
        client = chromadb.EphemeralClient()
        collection = client.create_collection("test")
        collection.add(
            documents=["hello world"],
            metadatas=[{"source": "test"}],
            ids=["id1"]
        )
        results = collection.query(query_texts=["hello"], n_results=1)
        logger.info(f"ChromaDB query works. Results: {results['ids']}")
    except Exception as e:
        logger.error(f"ChromaDB check failed: {e}")
        return False
    return True

if __name__ == "__main__":
    if not check_numpy_scipy():
        sys.exit(1)
    if not check_sentence_transformers():
        sys.exit(1)
    if not check_chromadb():
        sys.exit(1)
    # Ollama is optional for valid python env, but good to check
    check_ollama()
    print("All checks passed.")
