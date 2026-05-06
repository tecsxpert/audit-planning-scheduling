from __future__ import annotations

import json
import logging
import time
from datetime import UTC, datetime

from groq import Groq
from groq import InternalServerError, RateLimitError, APIConnectionError

from services.config import settings

LOGGER = logging.getLogger(__name__)

class GroqClientService:
    def __init__(self) -> None:
        self._client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None
        self.max_retries = 3

    def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        fallback_payload: dict,
    ) -> dict:
        if self._client is None:
            return self._fallback_response(fallback_payload, "missing_api_key")

        attempt = 0
        last_exception = None

        while attempt < self.max_retries:
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
                        "attempts": attempt + 1,
                    }
                )
                return parsed
            except json.JSONDecodeError as exc:
                LOGGER.error("Failed to parse JSON response from Groq: %s", exc)
                return self._fallback_response(fallback_payload, "invalid_json")
            except (InternalServerError, RateLimitError, APIConnectionError) as exc:
                last_exception = exc
                LOGGER.warning(f"Groq API error on attempt {attempt + 1}: {exc}")
                attempt += 1
                if attempt < self.max_retries:
                    sleep_time = 2 ** attempt
                    time.sleep(sleep_time)
            except Exception as exc:
                LOGGER.exception("Unexpected Groq call failure")
                return self._fallback_response(fallback_payload, str(exc))
                
        LOGGER.error("Groq call failed after %d attempts", self.max_retries)
        return self._fallback_response(fallback_payload, str(last_exception))

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
