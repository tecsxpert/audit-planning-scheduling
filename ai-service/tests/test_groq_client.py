import pytest
import json
from unittest.mock import MagicMock, patch
from groq import InternalServerError
from services.groq_client import GroqClientService

@pytest.fixture
def mock_groq():
    with patch("services.groq_client.Groq") as MockGroq:
        mock_client = MagicMock()
        MockGroq.return_value = mock_client
        yield mock_client

@pytest.fixture
def groq_service(mock_groq, monkeypatch):
    monkeypatch.setattr("services.config.settings.groq_api_key", "test_key")
    monkeypatch.setattr("services.config.settings.groq_model", "test-model")
    return GroqClientService()

def test_generate_json_success(groq_service, mock_groq):
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = '{"category": "test", "confidence": 0.9}'
    mock_groq.chat.completions.create.return_value = mock_completion

    response = groq_service.generate_json(
        system_prompt="sys",
        user_prompt="user",
        fallback_payload={"fallback": True}
    )

    assert response["category"] == "test"
    assert response["meta"]["model_used"] == "test-model"
    assert response["meta"]["attempts"] == 1
    assert response["meta"]["is_fallback"] is False

def test_generate_json_invalid_json(groq_service, mock_groq):
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = 'invalid json response'
    mock_groq.chat.completions.create.return_value = mock_completion

    response = groq_service.generate_json(
        system_prompt="sys",
        user_prompt="user",
        fallback_payload={"fallback": True}
    )

    assert response["fallback"] is True
    assert response["meta"]["is_fallback"] is True
    assert response["meta"]["fallback_reason"] == "invalid_json"

@patch("services.groq_client.time.sleep", return_value=None)
def test_generate_json_retry_success(mock_sleep, groq_service, mock_groq):
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = '{"success": true}'
    
    # Fail first two times, succeed on the third
    mock_groq.chat.completions.create.side_effect = [
        InternalServerError("Server error", response=MagicMock(), body={}),
        InternalServerError("Server error", response=MagicMock(), body={}),
        mock_completion
    ]

    response = groq_service.generate_json(
        system_prompt="sys",
        user_prompt="user",
        fallback_payload={"fallback": True}
    )

    assert response["success"] is True
    assert response["meta"]["attempts"] == 3
    assert mock_sleep.call_count == 2
    
@patch("services.groq_client.time.sleep", return_value=None)
def test_generate_json_retry_exhausted(mock_sleep, groq_service, mock_groq):
    mock_groq.chat.completions.create.side_effect = InternalServerError("Server error", response=MagicMock(), body={})

    response = groq_service.generate_json(
        system_prompt="sys",
        user_prompt="user",
        fallback_payload={"fallback": True}
    )

    assert response["fallback"] is True
    assert response["meta"]["is_fallback"] is True
    assert "Server error" in response["meta"]["fallback_reason"]
    assert mock_sleep.call_count == 2  # Sleeps after attempt 1 and 2, but not 3
    assert mock_groq.chat.completions.create.call_count == 3
