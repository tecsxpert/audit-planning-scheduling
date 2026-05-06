import uuid
import threading
import time
from typing import Dict, Any

# Simple in-memory job store
JOBS: Dict[str, Any] = {}

def process_report_job(job_id: str, text: str):
    try:
        # Simulate processing time
        time.sleep(3)
        
        # We would normally call the real groq_client here
        # For Day 11, we just return a simulated successful response
        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["result"] = {
            "title": "Audit Report",
            "executive_summary": f"Report generated for: {text[:20]}...",
            "top_items": ["Item 1", "Item 2"],
            "recommendations": ["Rec 1", "Rec 2"]
        }
    except Exception as e:
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["error"] = str(e)

def create_job(text: str) -> str:
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "processing", "result": None, "error": None}
    
    thread = threading.Thread(target=process_report_job, args=(job_id, text))
    thread.daemon = True
    thread.start()
    
    return job_id

def get_job_status(job_id: str) -> dict:
    if job_id not in JOBS:
        return {"status": "not_found"}
    return JOBS[job_id]
