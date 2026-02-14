"""Debug script to test RAPTOR with USER KEY."""

import asyncio
import httpx
import os
import sys

BASE_URL = "http://localhost:8000"

# User provided key
USER_KEY = os.getenv("OPENAI_API_KEY", "your-key-here")

async def test_raptor_ingestion():
    """Test uploading a LARGE file to trigger RAPTOR."""
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        print("=" * 80)
        print("TESTING RAPTOR INGESTION (LARGE FILE)")
        print("=" * 80)
        
        # Create project
        print("\n[STEP 1] Creating project...")
        response = await client.post(
            f"{BASE_URL}/api/projects",
            json={
                "name": "Raptor Test Project",
                "description": "Testing large file ingestion",
                "embedding_model": "openai:text-embedding-3-small"
            }
        )
        
        if response.status_code != 201:
            print(f"❌ Failed to create project: {response.status_code}")
            return
        
        project = response.json()
        print(f"✓ Project created: {project['id']}")
        
        # Create large content (needs > 10 chunks)
        # 1000 chars per chunk approx -> need > 10000 chars
        print("\n[STEP 2] Generating large file content...")
        large_content = (b"This is a sentence about artificial intelligence and rag systems. " * 500) 
        print(f"  - Size: {len(large_content)} bytes")
        
        files = {"files": ("large_test.txt", large_content, "text/plain")}
        data = {"embedding_api_key": USER_KEY}
        
        print("\n[STEP 3] Uploading file...")
        response = await client.post(
            f"{BASE_URL}/api/projects/{project['id']}/files/upload",
            files=files,
            data=data
        )
        
        if response.status_code != 201:
            print(f"\n❌ Upload failed! {response.status_code}")
            print(response.json())
            return
            
        print(f"✓ Upload accepted.")
        
        # Wait for ingestion
        print("\n[STEP 4] Waiting for ingestion (RAPTOR takes time)...")
        for i in range(30): # Wait up to 60s
            response = await client.get(f"{BASE_URL}/api/projects/{project['id']}/files")
            files_list = response.json()
            file = files_list[0]
            print(f"  - Status: {file['status']}")
            
            if file['status'] == 'indexed':
                print(f"\n✓ SUCCESS! Large file indexed (RAPTOR worked).")
                break
            if file['status'] == 'failed':
                 print(f"\n❌ FAILED! Ingestion failed.")
                 break
            await asyncio.sleep(2)
        
        print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(test_raptor_ingestion())
