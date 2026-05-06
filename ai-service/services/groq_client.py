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
        self._failure_count = 0
        self._last_failure_time = 0
        self._circuit_open = False
        self._failure_threshold = 5
        self._recovery_timeout = 60 # seconds


    def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        fallback_payload: dict,
    ) -> dict:
        if self._client is None:
            return self._fallback_response(fallback_payload, "missing_api_key")

        # Circuit Breaker Logic
        current_time = datetime.now(UTC).timestamp()
        if self._circuit_open:
            if current_time - self._last_failure_time > self._recovery_timeout:
                LOGGER.info("Circuit breaker entering half-open state...")
                self._circuit_open = False
            else:
                LOGGER.warning("Circuit breaker is OPEN. Fast-failing request.")
                return self._fallback_response(fallback_payload, "circuit_breaker_open")

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
            # Reset failure count on success
            self._failure_count = 0
            
            content = completion.choices[0].message.content or "{}"
            parsed = json.loads(content)
            parsed.setdefault("meta", {})
            parsed["meta"].update(
                {
                    "model_used": settings.groq_model,
                    "generated_at": datetime.now(UTC).isoformat(),
                    "is_fallback": False,
                }
            )
            return parsed
        except Exception as exc:
            self._failure_count += 1
            self._last_failure_time = current_time
            if self._failure_count >= self._failure_threshold:
                self._circuit_open = True
                LOGGER.error(f"Circuit breaker OPENED after {self._failure_count} failures.")
            
            LOGGER.exception("Groq call failed")
            return self._fallback_response(fallback_payload, str(exc))


    @staticmethod
    def _fallback_response(payload: dict, reason: str) -> dict:
        response = dict(payload)
        response.setdefault("meta", {})
        response["meta"].update(
            {
                "model_used": "fallback-template",
                "generated_at": datetime.now(UTC).isoformat(),
                "is_fallback": True,
                "fallback_reason": reason,
            }
        )
        return response
