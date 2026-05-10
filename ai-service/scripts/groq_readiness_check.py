from __future__ import annotations

import json
import os
import sys
from pathlib import Path


AI_SERVICE_DIR = Path(__file__).resolve().parents[1]
if str(AI_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(AI_SERVICE_DIR))

from app import app  # noqa: E402


OUTPUT_PATH = AI_SERVICE_DIR / "groq_readiness_report.json"


def main():
    client = app.test_client()
    has_key = bool(os.getenv("GROQ_API_KEY"))
    report = {
        "groq_api_key_present": has_key,
        "checks": {
            "health_status": client.get("/health").status_code,
            "describe_status": client.post("/describe", json={"text": "Audit readiness review"}).status_code,
            "recommend_status": client.post("/recommend", json={"text": "Delayed audit due to missing evidence"}).status_code,
            "report_status": client.post("/generate-report", json={"text": "Prepare an audit report"}).status_code,
            "analyse_status": client.post("/analyse-document", json={"text": "Kickoff delayed and approval pending"}).status_code,
            "query_status": client.post("/query", json={"question": "What should be checked first in audit planning?"}).status_code,
        },
        "note": "Live Groq output requires a valid GROQ_API_KEY. Without it, the service will use fallback payloads.",
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Saved readiness report to {OUTPUT_PATH}")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
