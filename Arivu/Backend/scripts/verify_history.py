
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def verify_history():
    print("1. Creating Project...")
    resp = requests.post(f"{BASE_URL}/projects", json={"name": "History_Test", "embedding_model": "local:all-MiniLM-L6-v2"})
    if resp.status_code == 200:
        project_id = resp.json()["id"]
    else:
        # Try to find existing
        resp = requests.get(f"{BASE_URL}/projects")
        projects = resp.json()
        target = next((p for p in projects if p["name"] == "History_Test"), None)
        if target:
            project_id = target["id"]
        else:
            print("Failed to create project")
            return

    print(f"Using Project: {project_id}")

    # 2. Post a Query (which saves to history)
    print("2. Querying...")
    # Using a simple query. Even if no docs, it should return an answer (e.g. "I don't know") and save it.
    payload = {
        "question": "Hello, are you there?",
        "settings": {"model": "ollama:llama3"} 
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/projects/{project_id}/query", json=payload)
        resp.raise_for_status()
        print("Query success.")
    except Exception as e:
        print(f"Query Failed: {e}")
        # Proceed to check history anyway, maybe previous run worked?
        
    # 3. Fetch History
    print("3. Fetching History...")
    resp = requests.get(f"{BASE_URL}/projects/{project_id}/history")
    if resp.status_code == 200:
        history = resp.json()
        print(f"History Length: {len(history)}")
        for msg in history:
            print(f"- [{msg['role']}] {msg['content']} (Meta: {msg.get('metadata_json')})")
            
        if len(history) >= 2:
            print("Verified: History persisted.")
        else:
            print("Failed: History empty or incomplete.")
    else:
        print(f"Failed to fetch history: {resp.status_code} {resp.text}")

    # 4. Clear History
    print("4. Clearing History...")
    requests.delete(f"{BASE_URL}/projects/{project_id}/history")
    
    # 5. Verify Empty
    resp = requests.get(f"{BASE_URL}/projects/{project_id}/history")
    if len(resp.json()) == 0:
        print("Verified: History cleared.")
    else:
        print("Failed: History not cleared.")

if __name__ == "__main__":
    verify_history()
