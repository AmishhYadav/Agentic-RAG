import sys
from pathlib import Path

from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from app_server import app  # noqa: E402

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200


def test_stream_query_endpoint():
    response = client.get("/stream_query?q=test")
    assert response.status_code == 200
