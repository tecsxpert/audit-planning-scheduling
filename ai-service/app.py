"""
app.py - Flask Entry Point with flask-talisman Security Headers
Tool-21: Audit Planning and Scheduling
AI Developer 3 - Day 12 Task
"""

from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from routes.sanitisation import sanitise_input

app = Flask(__name__)


# ─────────────────────────────────────────────
# 1. FLASK-TALISMAN — All Security Headers
# Fixes all remaining ZAP findings!
# ─────────────────────────────────────────────
csp = {
    'default-src': "'self'",
    'script-src': "'self'",
    'style-src': "'self'",
    'img-src': "'self' data:",
    'font-src': "'self'",
}

Talisman(
    app,
    force_https=False,          # Keep False for local development
    strict_transport_security=False,  # Keep False for local development
    content_security_policy=csp,
    x_content_type_options=True,      # Fixes ZAP Finding 4
    x_xss_protection=True,            # Extra XSS protection
    frame_options='DENY',             # Fixes clickjacking
    referrer_policy='strict-origin-when-cross-origin',
)


# ─────────────────────────────────────────────
# 2. HIDE SERVER VERSION
# Fixes ZAP Finding 3
# ─────────────────────────────────────────────
# (Removed duplicate after_request)


# ─────────────────────────────────────────────
# 3. FLASK-LIMITER
# Default: 30 req/min
# ─────────────────────────────────────────────
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["30 per minute"],
    storage_uri="memory://",
)


# ─────────────────────────────────────────────
# 4. CUSTOM 429 ERROR HANDLER
# ─────────────────────────────────────────────
@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify({
        "error": "Too Many Requests",
        "message": "You have exceeded the allowed request limit.",
        "retry_after": 60,
        "retry_after_unit": "seconds",
        "status": 429
    }), 429


import time
from collections import deque
from services.config import settings
from services.rag_service import RagService

START_TIME = time.time()
RESPONSE_TIMES = deque(maxlen=10)

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def record_time_and_headers(response):
    if hasattr(request, 'start_time'):
        elapsed = (time.time() - request.start_time) * 1000  # ms
        RESPONSE_TIMES.append(elapsed)
    response.headers['Server'] = 'Tool-21-AI-Service'
    return response

# ─────────────────────────────────────────────
# 5. HEALTH CHECK
# ─────────────────────────────────────────────
@app.route("/health", methods=["GET"])
@limiter.exempt
def health():
    rag = RagService()
    doc_count = rag.document_count()
    avg_time = sum(RESPONSE_TIMES) / len(RESPONSE_TIMES) if RESPONSE_TIMES else 0.0
    uptime = time.time() - START_TIME

    return jsonify({
        "status": "ok",
        "model_name": settings.groq_model,
        "average_response_time_ms": round(avg_time, 2),
        "chromadb_document_count": doc_count,
        "uptime_seconds": round(uptime, 2),
        "cache_stats": "Not enabled",
        "security": {
            "talisman": "enabled",
            "csp": "enabled",
            "rate_limiting": "30 req/min default"
        }
    }), 200


# ─────────────────────────────────────────────
# 6. DESCRIBE ENDPOINT
# ─────────────────────────────────────────────
@app.route("/describe", methods=["POST"])
@sanitise_input
def describe():
    clean_body = request.sanitised_body
    return jsonify({
        "message": "Describe endpoint working!",
        "received": clean_body,
        "status": 200
    }), 200


# ─────────────────────────────────────────────
# 7. RECOMMEND ENDPOINT
# ─────────────────────────────────────────────
@app.route("/recommend", methods=["POST"])
@sanitise_input
def recommend():
    clean_body = request.sanitised_body
    return jsonify({
        "message": "Recommend endpoint working!",
        "received": clean_body,
        "status": 200
    }), 200


# ─────────────────────────────────────────────
# 8. GENERATE REPORT — Strict 10 req/min
# ─────────────────────────────────────────────
@app.route("/generate-report", methods=["POST"])
@limiter.limit("10 per minute")
@sanitise_input
def generate_report():
    clean_body = request.sanitised_body
    return jsonify({
        "message": "Generate report endpoint working!",
        "received": clean_body,
        "status": 200
    }), 200


# ─────────────────────────────────────────────
# 9. CATEGORISE ENDPOINT
# ─────────────────────────────────────────────
@app.route("/categorise", methods=["POST"])
@sanitise_input
def categorise():
    clean_body = request.sanitised_body
    return jsonify({
        "message": "Categorise endpoint working!",
        "received": clean_body,
        "status": 200
    }), 200


# ─────────────────────────────────────────────
# 10. TEST SANITISATION ENDPOINT
# ─────────────────────────────────────────────
@app.route("/test-sanitise", methods=["POST"])
@sanitise_input
def test_sanitise():
    clean_body = request.sanitised_body
    return jsonify({
        "message": "Input is clean and safe!",
        "received": clean_body,
        "status": 200
    }), 200


# ─────────────────────────────────────────────
# RUN THE APP
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
