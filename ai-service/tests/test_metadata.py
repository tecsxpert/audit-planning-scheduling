import pytest
from services.groq_client import GroqClientService

def test_metadata_structure(monkeypatch):
    from unittest.mock import MagicMock
    mock_groq = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = '{"category": "test", "confidence": 0.9}'
    mock_completion.usage.total_tokens = 42
    mock_groq.chat.completions.create.return_value = mock_completion
    monkeypatch.setattr("services.groq_client.Groq", lambda api_key: mock_groq)
    monkeypatch.setattr("services.config.settings.groq_api_key", "test")

    client = GroqClientService()
    res = client.generate_json(system_prompt="sys", user_prompt="user", fallback_payload={"test": "fallback"})
    
    meta = res["meta"]
    assert "confidence" in meta
    assert "model_used" in meta
    assert "tokens_used" in meta
    assert "response_time_ms" in meta
    assert "cached" in meta
    
    assert meta["tokens_used"] == 42
    assert meta["confidence"] == 0.9

def test_fallback_metadata_structure():
    res = GroqClientService._fallback_response({"confidence": 0.5}, "error")
    meta = res["meta"]
    
    assert meta["confidence"] == 0.5
    assert meta["model_used"] == "fallback-template"
    assert meta["tokens_used"] == 0
    assert meta["response_time_ms"] == 0.0
    assert meta["cached"] is False
    assert meta["is_fallback"] is True
