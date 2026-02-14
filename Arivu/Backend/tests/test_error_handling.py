from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)

def test_exception_handler():
    # Define a route that raises an exception
    @app.get("/error_test")
    def error_endpoint():
        raise ValueError("This is a test error")

    response = client.get("/error_test")
    assert response.status_code == 500
    assert response.json() == {"detail": "This is a test error", "type": "ValueError"}
