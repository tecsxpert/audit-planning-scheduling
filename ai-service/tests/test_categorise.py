def test_categorise_returns_category(client, monkeypatch):
    from unittest.mock import MagicMock
    mock_groq = MagicMock()
    mock_groq.chat.completions.create.return_value.choices[0].message.content = '{"category": "IT", "confidence": 0.9, "reasoning": "mentions systems"}'
    monkeypatch.setattr("services.groq_client.Groq", lambda api_key: mock_groq)
    
    response = client.post("/categorise", json={"text": "The IT systems are failing."})
    assert response.status_code == 200
    body = response.get_json()
    assert "category" in body
    assert "confidence" in body
    assert "reasoning" in body
    
def test_categorise_rejects_empty_text(client):
    response = client.post("/categorise", json={"text": ""})
    assert response.status_code == 400
    body = response.get_json()
    assert body["error"] == "Invalid input"
