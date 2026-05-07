import os

from flask import Blueprint, jsonify, request

from services.groq_client import GroqClient, GroqError
from services.cache import AiCache
from services.utils import make_meta

categorise_bp = Blueprint("categorise", __name__)
client = GroqClient()
cache = AiCache()


@categorise_bp.route("/categorise", methods=["POST"])
def categorise_endpoint():
    payload = request.get_json(force=True, silent=True) or {}
    text = payload.get("text")
    if not text:
        return jsonify({"error": "Missing required field 'text'"}), 400

    cached = cache.get(text)
    if cached:
        cached["meta"]["cached"] = True
        return jsonify(cached)

    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "categorise.txt")
    with open(prompt_path, encoding="utf-8") as handle:
        prompt = handle.read().replace("{input}", text)

    try:
        raw = client.generate_response(prompt)
        response = {
            "data": {
                "category": raw.strip(),
                "confidence": 0.8,
                "reasoning": "AI selected the category based on the request.",
            },
            "meta": make_meta(model_name=client.model_name, response_time_ms=0.0, cached=False),
        }
        cache.set(text, response)
        return jsonify(response)
    except GroqError as exc:
        return jsonify({
            "data": {
                "category": "Unknown",
                "confidence": 0.0,
                "reasoning": "Groq API unavailable, returning fallback.",
            },
            "meta": make_meta(model_name=client.model_name, response_time_ms=0.0, cached=False, fallback=True),
        }), 503
