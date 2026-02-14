"""Debug script to test OpenAI embedding upload."""

import asyncio
import httpx
import os

BASE_URL = "http://localhost:8000"

# You need to set your OpenAI API key here for testing
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

async def test_openai_upload():
    """Test uploading a file with OpenAI embeddings."""
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("=" * 80)
        print("TESTING OPENAI EMBEDDING UPLOAD")
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
                "name": "OpenAI Test Project",
                "description": "Testing OpenAI embeddings",
                "embedding_model": "openai:text-embedding-3-small"
            }
        )
        
        if response.status_code != 201:
            print(f"❌ Failed to create project: {response.status_code}")
            print(response.json())
            return
        
        project = response.json()
        print(f"✓ Project created: {project['id']}")
        print(f"  - Embedding model: {project['embedding_model']}")
        
        # Upload a test file
        print("\n[STEP 2] Uploading file with OpenAI API key...")
        test_content = b"This is a test document for OpenAI embeddings. It contains some text about machine learning and artificial intelligence."
        
        files = {"files": ("test_openai.txt", test_content, "text/plain")}
        data = {"embedding_api_key": OPENAI_API_KEY}
        
        response = await client.post(
            f"{BASE_URL}/api/projects/{project['id']}/files/upload",
            files=files,
            data=data
        )
        
        print(f"Response status: {response.status_code}")
        result = response.json()
        print(f"Response body: {result}")
        
        if response.status_code != 201:
            print(f"\n❌ Upload failed!")
            print(f"Error: {result}")
            return
        
        print(f"\n✓ File uploaded successfully!")
        uploaded_files = result.get("uploaded", [])
        for file in uploaded_files:
            print(f"  - {file['filename']}: {file['status']}")
        
        # Wait a bit for ingestion
        print("\n[STEP 3] Waiting for ingestion...")
        await asyncio.sleep(5)
        
        # Check file status
        print("\n[STEP 4] Checking file status...")
        response = await client.get(f"{BASE_URL}/api/projects/{project['id']}/files")
        files_list = response.json()
        
        for file in files_list:
            print(f"\nFile: {file['filename']}")
            print(f"  - Status: {file['status']}")
            print(f"  - Chunks: {file['chunk_count']}")
            if file['status'] == 'failed':
                print(f"  - Error: This is the problem!")
        
        print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(test_openai_upload())
