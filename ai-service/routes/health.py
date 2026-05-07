import time
from collections import deque

from flask import Blueprint, jsonify

from services.cache import AiCache
from services.chroma_client import ChromaClient
from services.groq_client import GroqClient

health_bp = Blueprint("health", __name__)
client = GroqClient()
chroma = ChromaClient()
cache = AiCache()
response_times = deque(maxlen=10)
start_time = time.time()


@health_bp.route("/health", methods=["GET"])
def health_endpoint():
    avg_ms = round(sum(response_times) / len(response_times), 2) if response_times else 0.0
    document_count = chroma.collection.count() if chroma.collection else 0
    return jsonify(
        status="ok",
        model_name=client.model_name,
        average_response_time_ms=avg_ms,
        chroma_document_count=document_count,
        uptime_seconds=int(time.time() - start_time),
        cache=cache.stats(),
    )
