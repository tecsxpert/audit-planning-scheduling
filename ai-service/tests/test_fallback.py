import pytest
from services.groq_client import GroqClientService

def test_fallback_handles_timeout(monkeypatch):
    from unittest.mock import MagicMock
    mock_groq = MagicMock()
    mock_groq.chat.completions.create.side_effect = Exception("Timeout Error")
    monkeypatch.setattr("services.groq_client.Groq", lambda api_key: mock_groq)
    monkeypatch.setattr("services.config.settings.groq_api_key", "test")

    client = GroqClientService()
    fallback = {"status": "default fallback"}
    
    res = client.generate_json(system_prompt="sys", user_prompt="user", fallback_payload=fallback)
    
    assert res["status"] == "default fallback"
    assert res["meta"]["is_fallback"] is True
    assert res["meta"]["model_used"] == "fallback-template"
    assert "Timeout Error" in res["meta"]["fallback_reason"]

def test_fallback_handles_missing_api_key(monkeypatch):
    monkeypatch.setattr("services.config.settings.groq_api_key", "")
    
    client = GroqClientService()
    fallback = {"status": "default fallback"}
    
    res = client.generate_json(system_prompt="sys", user_prompt="user", fallback_payload=fallback)
    
    assert res["status"] == "default fallback"
    assert res["meta"]["is_fallback"] is True
    assert res["meta"]["fallback_reason"] == "missing_api_key"
