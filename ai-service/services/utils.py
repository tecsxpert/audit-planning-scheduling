import hashlib
from datetime import datetime


def make_meta(model_name: str, response_time_ms: float, cached: bool = False, fallback: bool = False) -> dict:
    return {
        "confidence": 0.0,
        "model_used": model_name,
        "tokens_used": None,
        "response_time_ms": round(response_time_ms, 2),
        "cached": cached,
        "fallback": fallback,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "trace_id": hashlib.sha256(f'{model_name}:{response_time_ms}:{datetime.utcnow().isoformat()}'.encode('utf-8')).hexdigest()[:12],
    }
