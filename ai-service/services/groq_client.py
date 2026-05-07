import json
import logging
import os

from dotenv import load_dotenv
from groq import Groq
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

load_dotenv()

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class GroqError(Exception):
    pass


class GroqClient:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        api_key = api_key or os.getenv("GROQ_API_KEY", "").strip()
        self.model_name = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.api_key = api_key
        self.client = Groq(api_key=api_key) if api_key else None

    def is_configured(self) -> bool:
        return self.client is not None

    @retry(retry=retry_if_exception_type(Exception), stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=5))
    def generate_response(self, prompt: str, temperature: float = 0.2, max_output_tokens: int = 512) -> str:
        if self.client is None:
            raise GroqError("Missing GROQ_API_KEY. Please set GROQ_API_KEY in .env.")

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_completion_tokens=max_output_tokens,
            )
            text = response.choices[0].message.content
            logger.info("Groq response generated successfully")
            return text
        except Exception as exc:
            logger.exception("Groq request failed")
            raise GroqError(str(exc)) from exc

    def generate_json(self, prompt: str, **kwargs) -> dict:
        raw = self.generate_response(prompt, **kwargs)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"text": raw.strip()}
