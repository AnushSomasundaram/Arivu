"""Debug script to test OpenAI embedding upload with CLEAN SLATE (no env vars)."""

import asyncio
import httpx
import os
import sys

BASE_URL = "http://localhost:8000"

# You need to set your OpenAI API key here for testing
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

async def test_clean_slate_upload():
    """Test uploading a file with OpenAI embeddings with NO env vars on backend."""
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("=" * 80)
        print("TESTING CLEAN SLATE UPLOAD (No Backend Env Vars)")
        print("=" * 80)
        
        if not OPENAI_API_KEY:
            print("\n❌ No OpenAI API key found!")
            print("Set OPENAI_API_KEY environment variable and try again.")
            return
        
        print(f"\n✓ Using API key: {OPENAI_API_KEY[:10]}...")
        
        # Create project with OpenAI embedding model
        print("\n[STEP 1] Creating project with OpenAI embeddings...")
        response = await client.post(
            f"{BASE_URL}/api/projects",
            json={
                "name": "Clean Slate Test",
                "description": "Testing without env vars",
                "embedding_model": "openai:text-embedding-3-small"
            }
        )
        
        if response.status_code != 201:
            print(f"❌ Failed to create project: {response.status_code}")
            return
        
        project = response.json()
        print(f"✓ Project created: {project['id']}")
        
        # Upload a test file
        print("\n[STEP 2] Uploading file with explicit API key...")
        # Make a larger file to trigger RAPTOR (needs > 10 chunks)
        # 1000 chars per chunk approx, so we need > 10k chars
        test_content = (b"This is a test document about massive language models and deep learning. " * 500)
        print(f"  - File size: {len(test_content)} bytes")
        
        files = {"files": ("clean_slate_raptor.txt", test_content, "text/plain")}
        data = {"embedding_api_key": OPENAI_API_KEY}
        
        response = await client.post(
            f"{BASE_URL}/api/projects/{project['id']}/files/upload",
            files=files,
            data=data
        )
        
        result = response.json()
        if response.status_code != 201:
            print(f"\n❌ Upload failed!")
            print(f"Error: {result}")
            return
        
        print(f"\n✓ File uploaded successfully!")
        
        # Wait a bit for ingestion
        print("\n[STEP 3] Waiting for ingestion (including RAPTOR)...")
        # Poll for status
        for i in range(20):
            print(f"  - Checking status ({i+1}/20)...")
            response = await client.get(f"{BASE_URL}/api/projects/{project['id']}/files")
            files_list = response.json()
            file = files_list[0]
            
            if file['status'] == 'indexed':
                print(f"\n✓ Success! File indexed.")
                print(f"  - Chunks: {file['chunk_count']}")
                break
            elif file['status'] == 'failed':
                print(f"\n❌ Failure! File status is failed.")
                # We can't see the error message in the list, sadly.
                break
            
            await asyncio.sleep(2)
        
        print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(test_clean_slate_upload())
