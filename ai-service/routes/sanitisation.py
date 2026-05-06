"""
sanitisation.py — Input Sanitisation Middleware
Tool-21: Audit Planning and Scheduling
AI Developer 3 — Day 3 Task
"""

import re
from flask import request, jsonify
from functools import wraps
import html


# ─────────────────────────────────────────────
# 1. LIST OF PROMPT INJECTION PATTERNS
# These are sneaky phrases hackers use to trick the AI
# ─────────────────────────────────────────────
PROMPT_INJECTION_PATTERNS = [
    r"ignore (all |previous |above )?(instructions|rules|prompts)",
    r"disregard (all |previous |above )?(instructions|rules|prompts)",
    r"forget (all |previous |above )?(instructions|rules|prompts)",
    r"you are now",
    r"act as (a |an )?",
    r"pretend (you are|to be)",
    r"your new instructions",
    r"override (instructions|rules|system)",
    r"system prompt",
    r"reveal (your |the )?(prompt|instructions|system|password|secret)",
    r"show me (your |the )?(prompt|instructions|system)",
    r"what (are|were) your instructions",
    r"bypass (security|filter|restriction)",
    r"jailbreak",
    r"do anything now",
    r"dan mode",
]

# ─────────────────────────────────────────────
# 1.5 PII DETECTION PATTERNS
# ─────────────────────────────────────────────
PII_PATTERNS = {
    "Email Address": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}",
    "Phone Number":  r"\b(\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b",
    "Credit Card":   r"\b(?:\d{4}[\s-]?){3}\d{4}\b",
}

def detect_pii(text: str) -> str | None:
    """Check if the text contains PII patterns. Returns the pattern name if found."""
    for name, pattern in PII_PATTERNS.items():
        if re.search(pattern, text):
            return name
    return None


# ─────────────────────────────────────────────
# 2. LIST OF HTML/SCRIPT PATTERNS TO STRIP
# These are harmful HTML tags hackers inject
# ─────────────────────────────────────────────
HTML_PATTERNS = [
    r"<script.*?>.*?</script>",
    r"<.*?>",              # any HTML tag
    r"javascript:",
    r"onerror=",
    r"onload=",
    r"onclick=",
    r"eval\(",
    r"document\.cookie",
    r"window\.location",
]


# ─────────────────────────────────────────────
# 3. STRIP HTML FROM TEXT
# Removes all HTML tags from user input
# ─────────────────────────────────────────────
def strip_html(text: str) -> str:
    """Remove all HTML tags and decode HTML entities."""
    # Decode HTML entities like &amp; &lt; &gt;
    text = html.unescape(text)
    # Remove script tags and their content first
    text = re.sub(r"<script.*?>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL)
    # Remove all other HTML tags
    text = re.sub(r"<.*?>", "", text, flags=re.IGNORECASE | re.DOTALL)
    # Remove javascript: and event handlers
    for pattern in HTML_PATTERNS[2:]:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return text.strip()


# ─────────────────────────────────────────────
# 4. DETECT PROMPT INJECTION
# Returns True if suspicious patterns found
# ─────────────────────────────────────────────
def detect_prompt_injection(text: str) -> bool:
    """Check if the text contains prompt injection patterns."""
    text_lower = text.lower()
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    return False


# ─────────────────────────────────────────────
# 5. SANITISE A SINGLE TEXT VALUE
# Strips HTML and checks for injection
# ─────────────────────────────────────────────
def sanitise_text(text: str) -> dict:
    """
    Sanitise a single text input.
    Returns: { "clean_text": str, "is_safe": bool, "reason": str }
    """
    if not isinstance(text, str):
        return {"clean_text": str(text), "is_safe": True, "reason": None}

    # Step 1 — Strip HTML
    clean_text = strip_html(text)

    # Step 2 — Check for prompt injection
    if detect_prompt_injection(clean_text):
        return {
            "clean_text": clean_text,
            "is_safe": False,
            "reason": "Prompt injection pattern detected in input"
        }

    # Step 2.5 — Check for PII
    pii_type = detect_pii(clean_text)
    if pii_type:
        return {
            "clean_text": clean_text,
            "is_safe": False,
            "reason": f"PII detected in input: {pii_type}. For security, PII cannot be sent to the AI."
        }

    # Step 3 — Check length (max 5000 characters)

    if len(clean_text) > 5000:
        return {
            "clean_text": clean_text[:5000],
            "is_safe": False,
            "reason": "Input exceeds maximum allowed length of 5000 characters"
        }

    return {"clean_text": clean_text, "is_safe": True, "reason": None}


# ─────────────────────────────────────────────
# 6. SANITISE ALL FIELDS IN A JSON BODY
# Goes through every field and cleans it
# ─────────────────────────────────────────────
def sanitise_request_body(body: dict) -> dict:
    """
    Sanitise all string fields in a JSON request body.
    Returns: { "clean_body": dict, "is_safe": bool, "reason": str, "field": str }
    """
    clean_body = {}

    for field, value in body.items():
        if isinstance(value, str):
            result = sanitise_text(value)
            if not result["is_safe"]:
                return {
                    "clean_body": None,
                    "is_safe": False,
                    "reason": result["reason"],
                    "field": field
                }
            clean_body[field] = result["clean_text"]
        else:
            clean_body[field] = value

    return {"clean_body": clean_body, "is_safe": True, "reason": None, "field": None}


# ─────────────────────────────────────────────
# 7. FLASK DECORATOR — USE ON ANY ROUTE
# Automatically sanitises incoming requests
# ─────────────────────────────────────────────
def sanitise_input(f):
    """
    Flask decorator that sanitises all incoming JSON request bodies.
    Usage: Add @sanitise_input above any Flask route.
    Returns HTTP 400 with clear error message if bad input detected.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Only check requests that have a JSON body
        if request.is_json:
            body = request.get_json(silent=True)

            if body is None:
                return jsonify({
                    "error": "Invalid JSON body",
                    "message": "Request body must be valid JSON",
                    "status": 400
                }), 400

            # Sanitise the request body
            result = sanitise_request_body(body)

            if not result["is_safe"]:
                return jsonify({
                    "error": "Invalid input detected",
                    "message": result["reason"],
                    "field": result["field"],
                    "status": 400
                }), 400

            # Replace request body with clean version
            request.sanitised_body = result["clean_body"]
        else:
            request.sanitised_body = {}

        return f(*args, **kwargs)
    return decorated_function
