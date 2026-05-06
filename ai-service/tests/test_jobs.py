import pytest
import time
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_async_report_flow(client):
    # 1. Start Job
    res = client.post("/generate-report", json={"text": "Audit planning testing"})
    assert res.status_code == 202
    data = res.get_json()
    assert "job_id" in data
    assert data["status"] == "processing"
    
    job_id = data["job_id"]
    
    # 2. Check Job Status immediately (might still be processing)
    poll_res = client.get(f"/jobs/{job_id}")
    assert poll_res.status_code == 200
    
    # Wait for completion (sleep 4s since simulation takes 3s)
    time.sleep(4)
    
    # 3. Check Job Status completed
    poll_res_2 = client.get(f"/jobs/{job_id}")
    assert poll_res_2.status_code == 200
    poll_data = poll_res_2.get_json()
    assert poll_data["status"] == "completed"
    assert "result" in poll_data
    assert "title" in poll_data["result"]
