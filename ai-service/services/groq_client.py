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

        from services.cache_service import cache_service
        cached_response = cache_service.get(system_prompt, user_prompt)
        if cached_response:
            cached_response.setdefault("meta", {})
            cached_response["meta"]["cached"] = True
            return cached_response

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
            content = completion.choices[0].message.content or "{}"
            parsed = json.loads(content)
            parsed.setdefault("meta", {})
            parsed["meta"].update(
                {
                    "model_used": settings.groq_model,
                    "generated_at": datetime.now(UTC).isoformat(),
                    "is_fallback": False,
                    "cached": False,
                }
            )
            cache_service.set(system_prompt, user_prompt, parsed)
            return parsed
        except Exception as exc:
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
