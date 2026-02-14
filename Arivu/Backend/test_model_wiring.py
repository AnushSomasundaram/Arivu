"""Test script to verify embedding and model wiring fixes."""

import asyncio
import httpx

BASE_URL = "http://localhost:8000"


async def test_model_wiring():
    """Test all model wiring fixes."""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("=" * 80)
        print("TESTING EMBEDDING AND MODEL WIRING FIXES")
        print("=" * 80)
        
        # ========== TEST 1: Model Discovery Endpoint ==========
        print("\n[TEST 1] Model discovery endpoint...")
        response = await client.get(f"{BASE_URL}/api/models/embeddings")
        assert response.status_code == 200
        models = response.json()["models"]
        print(f"✓ Found {len(models)} available embedding models:")
        for model in models:
            print(f"  - {model['name']} ({model['provider']}, {model['dimensions']} dims)")
        
        # ========== TEST 2: Create Project with Valid Model ==========
        print("\n[TEST 2] Create project with valid embedding model...")
        response = await client.post(
            f"{BASE_URL}/api/projects",
            json={
                "name": "Test Valid Model",
                "description": "Testing model validation",
                "embedding_model": "local:all-MiniLM-L6-v2"
            }
        )
        assert response.status_code == 201
        project1 = response.json()
        print(f"✓ Project created: {project1['name']}")
        print(f"  - Embedding model: {project1['embedding_model']}")
        assert project1['embedding_model'] == "local:all-MiniLM-L6-v2"
        
        # ========== TEST 3: Model Name Normalization ==========
        print("\n[TEST 3] Model name normalization (without prefix)...")
        response = await client.post(
            f"{BASE_URL}/api/projects",
            json={
                "name": "Test Normalization",
                "description": "Testing auto-prefix",
                "embedding_model": "all-mpnet-base-v2"  # No prefix
            }
        )
        assert response.status_code == 201
        project2 = response.json()
        print(f"✓ Project created with normalized model")
        print(f"  - Input: all-mpnet-base-v2")
        print(f"  - Stored: {project2['embedding_model']}")
        assert project2['embedding_model'].startswith("local:")
        
        # ========== TEST 4: Invalid Model Name ==========
        print("\n[TEST 4] Reject invalid embedding model...")
        response = await client.post(
            f"{BASE_URL}/api/projects",
            json={
                "name": "Test Invalid",
                "description": "Should fail",
                "embedding_model": "invalid:"  # Empty after prefix
            }
        )
        assert response.status_code == 400
        error = response.json()
        print(f"✓ Correctly rejected invalid model")
        print(f"  - Error: {error['detail']}")
        
        # ========== TEST 5: Cannot Change Model After Docs ==========
        print("\n[TEST 5] Prevent embedding model change after documents...")
        
        # Upload a file to project1
        test_file_content = b"This is a test document for model validation."
        files = {"files": ("test.txt", test_file_content, "text/plain")}
        upload_response = await client.post(
            f"{BASE_URL}/api/projects/{project1['id']}/files/upload",
            files=files
        )
        assert upload_response.status_code == 201
        print(f"✓ Uploaded test document to project")
        
        # Try to change embedding model
        update_response = await client.patch(
            f"{BASE_URL}/api/projects/{project1['id']}",
            json={"embedding_model": "local:all-mpnet-base-v2"}
        )
        assert update_response.status_code == 400
        error = update_response.json()
        print(f"✓ Correctly prevented model change")
        print(f"  - Error: {error['detail']}")
        assert "Cannot change embedding model" in error['detail']
        
        # ========== TEST 6: Can Change Model on Empty Project ==========
        print("\n[TEST 6] Allow model change on empty project...")
        update_response = await client.patch(
            f"{BASE_URL}/api/projects/{project2['id']}",
            json={"embedding_model": "local:all-MiniLM-L6-v2"}
        )
        assert update_response.status_code == 200
        updated_project = update_response.json()
        print(f"✓ Successfully changed model on empty project")
        print(f"  - Old: {project2['embedding_model']}")
        print(f"  - New: {updated_project['embedding_model']}")
        
        # ========== TEST 7: OpenAI Model Validation ==========
        print("\n[TEST 7] OpenAI model requires API key...")
        response = await client.post(
            f"{BASE_URL}/api/projects",
            json={
                "name": "Test OpenAI",
                "description": "Should work but warn about API key",
                "embedding_model": "openai:text-embedding-3-small"
            }
        )
        # This should succeed (validation only checks format, not API key availability)
        assert response.status_code == 201
        project3 = response.json()
        print(f"✓ OpenAI model accepted")
        print(f"  - Model: {project3['embedding_model']}")
        
        # ========== SUMMARY ==========
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print("✓ All 7 tests passed!")
        print("✓ Model discovery endpoint works")
        print("✓ Model validation prevents invalid names")
        print("✓ Model normalization adds prefixes automatically")
        print("✓ Cannot change embedding model after documents exist")
        print("✓ Can change embedding model on empty projects")
        print("✓ Helpful error messages provided")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_model_wiring())
