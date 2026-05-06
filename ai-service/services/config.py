from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    chroma_path: Path = Path(os.getenv("CHROMA_PATH", BASE_DIR / "chroma_data"))
    prompts_path: Path = BASE_DIR / "prompts"
    data_path: Path = BASE_DIR / "data"
    rag_collection_name: str = os.getenv(
        "RAG_COLLECTION_NAME", "audit_planning_knowledge"
    )
    redis_url: str = os.getenv("REDIS_URL", "")


settings = Settings()
