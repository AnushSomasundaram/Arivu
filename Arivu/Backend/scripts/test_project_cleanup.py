
import requests
import os
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000/api"
DATA_DIR = Path("data")

def test_cleanup():
    # 1. Create Project
    print("Creating project...")
    resp = requests.post(f"{BASE_URL}/projects", json={"name": "Cleanup_Test"})
    if resp.status_code != 201:
        print(f"Failed to create project: {resp.text}")
        return
    project = resp.json()
    pid = project["id"]
    print(f"Project ID: {pid}")

    # 2. Verify Folder Created (it might not be created until files uploaded)
    project_path = DATA_DIR / "projects" / pid
    # Simulating file upload triggers folder creation
    files_path = project_path / "files"
    chroma_path = project_path / "chroma"
    
    # We can manually create these to simulate state if we don't want to use real upload
    # But better to use API.
    # Let's perform a fake upload? Or just manually create dirs to see if they get deleted.
    # The delete_project_data relies on project_id matching directory.
    
    print("Simulating data creation...")
    files_path.mkdir(parents=True, exist_ok=True)
    chroma_path.mkdir(parents=True, exist_ok=True)
    (chroma_path / "chroma.sqlite3").touch()
    
    if not project_path.exists():
        print("Error: Project path check failed.")
        return

    # 3. Delete Project
    print("Deleting project...")
    resp = requests.delete(f"{BASE_URL}/projects/{pid}")
    if resp.status_code != 204:
        print(f"Failed to delete project: {resp.status_code} {resp.text}")
        return
        
    # 4. Verify Cleanup
    if project_path.exists():
        print(f"FAILURE: Project data directory still exists: {project_path}")
        print(f"Contents: {list(project_path.glob('**/*'))}")
    else:
        print("SUCCESS: Project data directory deleted.")

if __name__ == "__main__":
    test_cleanup()
