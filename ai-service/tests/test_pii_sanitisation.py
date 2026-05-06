import pytest
from routes.sanitisation import sanitise_text

def test_pii_detection():
    # Test Email
    result = sanitise_text("My email is ganesh@example.com")
    assert result["is_safe"] is False
    assert "PII detected" in result["reason"]
    assert "Email Address" in result["reason"]

    # Test Phone
    result = sanitise_text("Call me at 123-456-7890")
    assert result["is_safe"] is False
    assert "Phone Number" in result["reason"]

    # Test Credit Card
    result = sanitise_text("Card number: 1234-5678-1234-5678")
    assert result["is_safe"] is False
    assert "Credit Card" in result["reason"]

    # Test Clean Text
    result = sanitise_text("Audit planning for Q3")
    assert result["is_safe"] is True
