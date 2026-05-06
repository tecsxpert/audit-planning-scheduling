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
@app.after_request
def hide_server_info(response):
    response.headers['Server'] = 'Tool-21-AI-Service'
    return response


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


# ─────────────────────────────────────────────
# 5. HEALTH CHECK
# ─────────────────────────────────────────────
@app.route("/health", methods=["GET"])
@limiter.exempt
def health():
    return jsonify({
        "status": "ok",
        "message": "AI service is running",
        "security": {
            "talisman": "enabled",
            "csp": "enabled",
            "x_content_type_options": "nosniff",
            "x_frame_options": "DENY",
            "rate_limiting": "30 req/min default"
        }
    }), 200


from routes.describe import describe_bp
from routes.recommend import recommend_bp
from routes.generate_report import generate_report_bp
from routes.analyse_document import analyse_document_bp
from routes.batch_process import batch_process_bp
from routes.query import query_bp

app.register_blueprint(describe_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(generate_report_bp)
app.register_blueprint(analyse_document_bp)
app.register_blueprint(batch_process_bp)
app.register_blueprint(query_bp)


# ─────────────────────────────────────────────
# 5. HEALTH CHECK
# ─────────────────────────────────────────────
@app.route("/health", methods=["GET"])
@limiter.exempt
def health():
    return jsonify({
        "status": "ok",
        "message": "AI service is running",
        "security": {
            "talisman": "enabled",
            "csp": "enabled",
            "x_content_type_options": "nosniff",
            "x_frame_options": "DENY",
            "rate_limiting": "30 req/min default"
        }
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
