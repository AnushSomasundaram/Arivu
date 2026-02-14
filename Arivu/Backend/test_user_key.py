"""Debug script to test OpenAI embedding upload with USER KEY."""

import asyncio
import httpx
import os
import sys

BASE_URL = "http://localhost:8000"

# User provided key
USER_KEY = os.getenv("OPENAI_API_KEY", "your-key-here")

async def test_user_key_upload():
    """Test uploading a file with User's OpenAI key."""
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("=" * 80)
        print("TESTING USER KEY UPLOAD")
        print("=" * 80)
        
        print(f"\n✓ Using Key: {USER_KEY[:15]}...")
        
        # Create project with OpenAI embedding model
        print("\n[STEP 1] Creating project with OpenAI embeddings...")
        response = await client.post(
            f"{BASE_URL}/api/projects",
            json={
                "name": "User Key Test",
                "description": "Testing provided key",
                "embedding_model": "openai:text-embedding-3-small"
            }
        )
        
        if response.status_code != 201:
            print(f"❌ Failed to create project: {response.status_code}")
            print(response.json())
            return
        
        project = response.json()
        print(f"✓ Project created: {project['id']}")
        
        # Upload a test file
        print("\n[STEP 2] Uploading file with explicit API key...")
        test_content = b"This is a test document to verify the user's API key works."
        
        files = {"files": ("user_key_test.txt", test_content, "text/plain")}
        data = {"embedding_api_key": USER_KEY}
        
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
        
        print(f"\n✓ File uploaded successfully!")
        
        # Wait a bit for ingestion
        print("\n[STEP 3] Waiting for ingestion status...")
        for i in range(10):
            response = await client.get(f"{BASE_URL}/api/projects/{project['id']}/files")
            files_list = response.json()
            file = files_list[0]
            print(f"  - Status: {file['status']}")
            
            if file['status'] == 'indexed':
                print(f"\n✓ SUCCESS! File indexed with user key.")
                break
            if file['status'] == 'failed':
                 print(f"\n❌ FAILED! Ingestion failed.")
                 break
            await asyncio.sleep(2)
        
        print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(test_user_key_upload())
