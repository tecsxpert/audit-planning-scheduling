from __future__ import annotations

import json
import logging
from datetime import UTC, datetime

from groq import Groq

from services.config import settings


LOGGER = logging.getLogger(__name__)


class GroqClientService:
    def __init__(self) -> None:
        self._client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None

    def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        fallback_payload: dict,
    ) -> dict:
        if self._client is None:
            return self._fallback_response(fallback_payload, "missing_api_key")

        import time
        start_time = time.time()
        try:
            completion = self._client.chat.completions.create(
                model=settings.groq_model,
                temperature=0.3,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            response_time_ms = round((time.time() - start_time) * 1000, 2)
            content = completion.choices[0].message.content or "{}"
            parsed = json.loads(content)
            
            # Extract confidence if present, default to 0.0
            confidence = parsed.get("confidence", 0.0)
            
            tokens_used = 0
            if hasattr(completion, 'usage') and completion.usage:
                tokens_used = completion.usage.total_tokens

            parsed.setdefault("meta", {})
            parsed["meta"].update(
                {
                    "confidence": confidence,
                    "model_used": settings.groq_model,
                    "tokens_used": tokens_used,
                    "response_time_ms": response_time_ms,
                    "cached": False,
                    "generated_at": datetime.now(UTC).isoformat(),
                    "is_fallback": False,
                }
            )
            return parsed
        except Exception as exc:
            LOGGER.exception("Groq call failed")
            return self._fallback_response(fallback_payload, str(exc))

    @staticmethod
    def _fallback_response(payload: dict, reason: str) -> dict:
        response = dict(payload)
        response.setdefault("meta", {})
        
        confidence = response.get("confidence", 0.0)
        
        response["meta"].update(
            {
                "confidence": confidence,
                "model_used": "fallback-template",
                "tokens_used": 0,
                "response_time_ms": 0.0,
                "cached": False,
                "generated_at": datetime.now(UTC).isoformat(),
                "is_fallback": True,
                "fallback_reason": reason,
            }
        )
        return response
