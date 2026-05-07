import os
import threading
import uuid
from datetime import datetime

from flask import Blueprint, jsonify, request

from services.groq_client import GroqClient, GroqError
from services.utils import make_meta

report_bp = Blueprint("report", __name__)
client = GroqClient()
job_store = {}
job_lock = threading.Lock()


def _process_report(job_id: str, prompt: str, webhook_url: str | None):
    try:
        report_text = client.generate_response(prompt)
        result = {
            "job_id": job_id,
            "status": "completed",
            "report": report_text.strip(),
            "finished_at": datetime.utcnow().isoformat() + "Z",
        }
    except GroqError as exc:
        result = {
            "job_id": job_id,
            "status": "failed",
            "error": str(exc),
            "finished_at": datetime.utcnow().isoformat() + "Z",
        }

    with job_lock:
        job_store[job_id] = result

    if webhook_url and result["status"] == "completed":
        try:
            import requests
            requests.post(webhook_url, json=result, timeout=5)
        except Exception:
            pass


@report_bp.route("/generate-report", methods=["POST"])
def generate_report_endpoint():
    payload = request.get_json(force=True, silent=True) or {}
    title = payload.get("title")
    context = payload.get("context", "No contextual data provided.")
    webhook_url = payload.get("webhook_url")
    if not title:
        return jsonify({"error": "Missing required field 'title'"}), 400

    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "generate_report.txt")
    with open(prompt_path, encoding="utf-8") as handle:
        prompt = handle.read().replace("{request}", title).replace("{context}", context)

    job_id = str(uuid.uuid4())
    with job_lock:
        job_store[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "created_at": datetime.utcnow().isoformat() + "Z",
        }

    thread = threading.Thread(target=_process_report, args=(job_id, prompt, webhook_url), daemon=True)
    thread.start()

    return jsonify({"job_id": job_id, "status": "queued"}), 202


@report_bp.route("/report/<job_id>", methods=["GET"])
def get_report_endpoint(job_id: str):
    with job_lock:
        result = job_store.get(job_id)
    if result is None:
        return jsonify({"error": "Unknown job_id"}), 404
    return jsonify(result)
