"""Debug script to test OpenAI embedding upload with CLEAN SLATE (no env vars) - FIXED."""

import asyncio
import httpx
import os
import sys

BASE_URL = "http://localhost:8000"

# MOCK KEY FOR TESTING - In real world, this would be a real key
# We will use a placeholder that will fail validation at OpenAI but PASS our internal checks
# until it hits the API. This lets us verify propagation.
MOCK_API_KEY = "sk-proj-1234567890abcdef1234567890abcdef"

async def test_clean_slate_upload_logging():
    """Test uploading a file with OpenAI embeddings to trigger logs."""
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("=" * 80)
        print("TESTING CLEAN SLATE UPLOAD LOGGING")
        print("=" * 80)
        
        print(f"\n✓ Using MOCK API key: {MOCK_API_KEY[:10]}...")
        
        # Create project with OpenAI embedding model
        print("\n[STEP 1] Creating project with OpenAI embeddings...")
        response = await client.post(
            f"{BASE_URL}/api/projects",
            json={
                "name": "Clean Slate Log Test",
                "description": "Testing log tracing",
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
        test_content = b"This is a test document to trace API key propagation."
        
        files = {"files": ("log_trace.txt", test_content, "text/plain")}
        data = {"embedding_api_key": MOCK_API_KEY}
        
        response = await client.post(
            f"{BASE_URL}/api/projects/{project['id']}/files/upload",
            files=files,
            data=data
        )
        
        result = response.json()
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 201:
            print(f"\n❌ Upload failed!")
            print(f"Error: {result}")
            return
        
        print(f"\n✓ File uploaded successfully (Mock key accepted by backend)!")
        print("  - Check backend logs now to see trace.")
        
        print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(test_clean_slate_upload_logging())
