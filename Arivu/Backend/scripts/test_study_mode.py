
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def test_study_mode():
    # 1. Get Projects
    resp = requests.get(f"{BASE_URL}/projects")
    projects = resp.json()
    if not projects:
        print("No projects found. Create one first.")
        return
    
    project_id = projects[0]["id"]
    print(f"Testing project {project_id}...")
    
    # 2. Call Study Endpoint
    payload = {
        "mode": "quiz",
        "count": 3,
        "topic": "Key concepts",
        "settings": {
            "model": "openai:gpt-4o" # Ensure correct model name
        }
    }
    
    print("Sending request...")
    try:
        resp = requests.post(f"{BASE_URL}/projects/{project_id}/study", json=payload)
        resp.raise_for_status()
        data = resp.json()
        print("\n--- RESPONSE ---")
        print(f"Mode: {data['mode']}")
        print(f"Content:\n{data['content']}")
        print(f"Sources: {len(data['sources'])}")
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, "response"):
            print(e.response.text)

if __name__ == "__main__":
    test_study_mode()
