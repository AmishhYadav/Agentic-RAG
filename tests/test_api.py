from fastapi.testclient import TestClient
from main import app  # adjust import to match your app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200

def test_query_endpoint_exists():
    response = client.post("/query", json={"query": "test"})
    assert response.status_code in [200, 422]  # 422 = validation error is fine