import logging
import os
import sys
import threading
import time
import uuid
from collections import deque
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

sys.path.insert(0, os.path.dirname(__file__))

from services.cache import AiCache
from services.chroma_client import ChromaClient
from services.groq_client import GroqClient, GroqError
from services.utils import make_meta

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address, default_limits=["30 per minute"])

groq_client = GroqClient()
chroma_client = ChromaClient()
cache = AiCache()
start_time = time.time()
response_times = deque(maxlen=10)
job_results = {}
job_lock = threading.Lock()


def record_response_time(value_ms: float):
    response_times.append(value_ms)


def _safe_run(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as exc:
        logger.exception("Internal AI service error")
        return None


def background_report_job(job_id: str, payload: dict, webhook_url: str | None):
    try:
        output = _safe_run(groq_client.generate_response, payload["prompt"], temperature=0.2)
        if output is None:
            output = "Report generation failed."

        result = {
            "job_id": job_id,
            "status": "completed",
            "report": output,
            "finished_at": datetime.utcnow().isoformat() + "Z",
        }

        with job_lock:
            job_results[job_id] = result

        if webhook_url:
            try:
                import requests
                requests.post(webhook_url, json=result, timeout=5)
            except Exception:
                logger.warning("Failed to send webhook for job %s", job_id)

    except Exception as exc:
        logger.exception("Report job failed for %s", job_id)
        with job_lock:
            job_results[job_id] = {
                "job_id": job_id,
                "status": "failed",
                "error": str(exc),
                "finished_at": datetime.utcnow().isoformat() + "Z",
            }


@app.route("/health", methods=["GET"])
@limiter.limit("30/minute")
def health():
    model_name = groq_client.model_name
    avg_ms = round(sum(response_times) / len(response_times), 2) if response_times else 0.0
    collection_count = chroma_client.collection.count() if chroma_client.collection else 0
    cache_stats = cache.stats()
    uptime_seconds = int(time.time() - start_time)
    return jsonify(
        status="ok",
        model_name=model_name,
        average_response_time_ms=avg_ms,
        chroma_document_count=collection_count,
        uptime_seconds=uptime_seconds,
        cache=cache_stats,
    )


@app.route("/categorise", methods=["POST"])
@limiter.limit("30/minute")
def categorise():
    payload = request.get_json(force=True, silent=True) or {}
    text = payload.get("text")
    if not text:
        return jsonify({"error": "Missing required field 'text'"}), 400

    cached_response = cache.get(text)
    if cached_response:
        response = cached_response
        response["meta"]["cached"] = True
        return jsonify(response)

    prompt = open(os.path.join(os.path.dirname(__file__), "prompts", "categorise.txt"), encoding="utf-8").read().replace("{input}", text)
    start = time.time()
    try:
        raw = groq_client.generate_response(prompt)
        elapsed = (time.time() - start) * 1000
        record_response_time(elapsed)
        response = {
            "data": {
                "category": raw.strip(),
                "confidence": 0.8,
                "reasoning": "The AI selected a category based on the text content.",
            },
            "meta": make_meta(model_name=groq_client.model_name, response_time_ms=elapsed, cached=False),
        }
        cache.set(text, response)
        return jsonify(response)
    except GroqError as exc:
        elapsed = (time.time() - start) * 1000
        record_response_time(elapsed)
        fallback = {
            "data": {
                "category": "Unknown",
                "confidence": 0.0,
                "reasoning": "Groq API is unavailable, returning fallback category.",
            },
            "meta": make_meta(model_name=groq_client.model_name, response_time_ms=elapsed, cached=False, fallback=True),
        }
        return jsonify(fallback), 503


@app.route("/query", methods=["POST"])
@limiter.limit("30/minute")
def query():
    payload = request.get_json(force=True, silent=True) or {}
    question = payload.get("question")
    if not question:
        return jsonify({"error": "Missing required field 'question'"}), 400

    cache_key = f"query:{question}"
    cached_response = cache.get(cache_key)
    if cached_response:
        cached_response["meta"]["cached"] = True
        return jsonify(cached_response)

    top_results = chroma_client.query(question, n_results=3)
    sources = []
    context = "\n\n".join([f"Source {idx+1}: {doc}" for idx, doc in enumerate(top_results["documents"])])
    prompt_template = open(os.path.join(os.path.dirname(__file__), "prompts", "query.txt"), encoding="utf-8").read()
    prompt = prompt_template.replace("{question}", question).replace("{context}", context)

    start = time.time()
    try:
        answer = groq_client.generate_response(prompt)
        elapsed = (time.time() - start) * 1000
        record_response_time(elapsed)
        response = {
            "data": {
                "answer": answer.strip(),
                "sources": top_results["documents"],
            },
            "meta": make_meta(model_name=groq_client.model_name, response_time_ms=elapsed, cached=False),
        }
        cache.set(cache_key, response)
        return jsonify(response)
    except GroqError as exc:
        elapsed = (time.time() - start) * 1000
        record_response_time(elapsed)
        response = {
            "data": {
                "answer": "Unable to answer at this time.",
                "sources": top_results["documents"],
            },
            "meta": make_meta(model_name=groq_client.model_name, response_time_ms=elapsed, cached=False, fallback=True),
        }
        return jsonify(response), 503


@app.route("/generate-report", methods=["POST"])
@limiter.limit("20/minute")
def generate_report():
    payload = request.get_json(force=True, silent=True) or {}
    title = payload.get("title")
    context = payload.get("context", "No additional context provided.")
    webhook_url = payload.get("webhook_url")
    if not title:
        return jsonify({"error": "Missing required field 'title'"}), 400

    prompt_template = open(os.path.join(os.path.dirname(__file__), "prompts", "generate_report.txt"), encoding="utf-8").read()
    prompt = prompt_template.replace("{request}", title).replace("{context}", context)

    job_id = str(uuid.uuid4())
    job_payload = {"prompt": prompt}
    with job_lock:
        job_results[job_id] = {"job_id": job_id, "status": "running", "started_at": datetime.utcnow().isoformat() + "Z"}

    thread = threading.Thread(target=background_report_job, args=(job_id, job_payload, webhook_url), daemon=True)
    thread.start()
    return jsonify({"job_id": job_id, "status": "queued"}), 202


@app.route("/report/<job_id>", methods=["GET"])
@limiter.limit("30/minute")
def get_report(job_id):
    with job_lock:
        result = job_results.get(job_id)
    if not result:
        return jsonify({"error": "Unknown job_id"}), 404
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.getenv("AI_SERVICE_PORT", 5000))
    app.run(host="0.0.0.0", port=port)
