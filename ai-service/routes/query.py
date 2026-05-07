import os

from flask import Blueprint, jsonify, request

from services.groq_client import GroqClient, GroqError
from services.chroma_client import ChromaClient
from services.cache import AiCache
from services.utils import make_meta

query_bp = Blueprint("query", __name__)
client = GroqClient()
chroma = ChromaClient()
cache = AiCache()


@query_bp.route("/query", methods=["POST"])
def query_endpoint():
    payload = request.get_json(force=True, silent=True) or {}
    question = payload.get("question")
    if not question:
        return jsonify({"error": "Missing required field 'question'"}), 400

    cache_key = f"query:{question}"
    cached = cache.get(cache_key)
    if cached:
        cached["meta"]["cached"] = True
        return jsonify(cached)

    search = chroma.query(question, n_results=3)
    documents = search.get("documents", []) if isinstance(search, dict) else []
    context = "\n\n".join([f"Source {idx+1}: {doc}" for idx, doc in enumerate(documents)])
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "query.txt")
    with open(prompt_path, encoding="utf-8") as handle:
        prompt = handle.read().replace("{question}", question).replace("{context}", context)

    try:
        answer = client.generate_response(prompt)
        response = {
            "data": {
                "answer": answer.strip(),
                "sources": documents,
            },
            "meta": make_meta(model_name=client.model_name, response_time_ms=0.0, cached=False),
        }
        cache.set(cache_key, response)
        return jsonify(response)
    except GroqError:
        return jsonify({
            "data": {
                "answer": "Unable to answer at this time.",
                "sources": documents,
            },
            "meta": make_meta(model_name=client.model_name, response_time_ms=0.0, cached=False, fallback=True),
        }), 503
