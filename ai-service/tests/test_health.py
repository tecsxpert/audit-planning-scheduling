import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint_advanced(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "model_name" in data
    assert "average_response_time_ms" in data
    assert "chromadb_document_count" in data
    assert "uptime_seconds" in data
    assert "cache_stats" in data
