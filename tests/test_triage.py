import pytest

from app.services.triage import _fallback, _parse_result


def test_fallback_classifies_billing_email():
    result = _fallback(
        "Invoice payment",
        "I have a question about my invoice and payment."
    )

    assert result["category"] == "billing"


def test_fallback_detects_urgent_email():
    result = _fallback(
        "Urgent support needed",
        "This is urgent. Please help me immediately."
    )

    assert result["priority"].lower() in ("high", "urgent")


def test_fallback_returns_required_fields():
    result = _fallback(
        "General question",
        "I would like some information."
    )

    assert "category" in result
    assert "priority" in result
    assert "summary" in result
    assert "draft_reply" in result


def test_parse_result_valid_json():
    raw = """
    {
        "category": "billing",
        "priority": "high",
        "summary": "Customer has a billing issue.",
        "draft_reply": "Thank you for contacting us."
    }
    """

    result = _parse_result(raw)

    assert result["category"] == "billing"
    assert result["priority"] == "high"


def test_parse_result_json_code_fence():
    raw = """```json
    {
        "category": "support",
        "priority": "normal",
        "summary": "Customer needs help.",
        "draft_reply": "We are happy to help."
    }
    ```"""

    result = _parse_result(raw)

    assert result["category"] == "support"


def test_parse_result_invalid_json():
    with pytest.raises(ValueError):
        _parse_result("This is not valid JSON")
