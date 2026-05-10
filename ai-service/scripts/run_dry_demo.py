from __future__ import annotations

import json
import sys
import time
from pathlib import Path


AI_SERVICE_DIR = Path(__file__).resolve().parents[1]
if str(AI_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(AI_SERVICE_DIR))

from app import app  # noqa: E402


OUTPUT_PATH = AI_SERVICE_DIR / "dry_run_results.json"


def timed_json_request(client, method: str, url: str, **kwargs):
    started = time.perf_counter()
    response = client.open(path=url, method=method, **kwargs)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    body = response.get_json(silent=True)
    return {
        "status_code": response.status_code,
        "elapsed_ms": elapsed_ms,
        "body": body,
    }


def main():
    client = app.test_client()
    results = {
        "health": timed_json_request(client, "GET", "/health"),
        "describe": timed_json_request(
            client,
            "POST",
            "/describe",
            json={"text": "Schedule a high-risk audit with multiple dependencies and a tight deadline."},
        ),
        "recommend": timed_json_request(
            client,
            "POST",
            "/recommend",
            json={"text": "There is a delayed audit with missing evidence and conflicting owners."},
        ),
        "generate_report": timed_json_request(
            client,
            "POST",
            "/generate-report",
            json={"text": "Prepare a status report for an audit programme with dependency risk."},
        ),
        "analyse_document": timed_json_request(
            client,
            "POST",
            "/analyse-document",
            json={"text": "Kickoff delayed. Dependency on finance approval remains open. Evidence not ready."},
        ),
        "query": timed_json_request(
            client,
            "POST",
            "/query",
            json={"question": "What should be checked first in audit planning?"},
        ),
        "batch_process": timed_json_request(
            client,
            "POST",
            "/batch-process",
            json={"items": ["Review overdue internal audit timeline", "Escalate missing owner confirmation"]},
        ),
    }

    stream_started = time.perf_counter()
    stream_response = client.post(
        "/generate-report?stream=true",
        json={"text": "Prepare a status report for an audit programme with dependency risk."},
        headers={"Accept": "text/event-stream"},
    )
    stream_elapsed = round((time.perf_counter() - stream_started) * 1000, 2)
    results["generate_report_stream"] = {
        "status_code": stream_response.status_code,
        "elapsed_ms": stream_elapsed,
        "mimetype": stream_response.mimetype,
        "preview": stream_response.get_data(as_text=True)[:300],
    }

    OUTPUT_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Saved dry run results to {OUTPUT_PATH}")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
