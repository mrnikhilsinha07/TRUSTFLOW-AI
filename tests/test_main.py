import io
from unittest.mock import MagicMock, patch
import json
import urllib.error

from fastapi.testclient import TestClient

from main import app
client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@patch("main.chat")
def test_successful_payment_analysis(mock_chat):
    mock_chat.return_value.message.content = """
    {
        "risk_level": "LOW",
        "warning_signs": [],
        "explanation": "No significant warning signs were identified.",
        "recommended_action": "Verify the invoice before payment."
    }
    """

    payload = {
        "invoice_description": "Office supplies",
        "amount": 1200,
        "currency": "INR",
        "recipient": "ABC Office Supplies",
        "warning_details": "",
    }

    response = client.post("/analyze-payment", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["risk_level"] == "LOW"
    assert data["payment_executed"] is False


@patch("main.chat")
def test_unknown_recipient_is_uncertain(mock_chat):
    mock_chat.return_value.message.content = """
    {
        "risk_level": "LOW",
        "warning_signs": [],
        "explanation": "No significant warning signs were identified.",
        "recommended_action": "Verify the payment details."
    }
    """

    payload = {
        "invoice_description": "Payment",
        "amount": 100,
        "currency": "INR",
        "recipient": "Unknown",
        "warning_details": "",
    }

    response = client.post("/analyze-payment", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["risk_level"] == "MEDIUM"
    assert data["payment_executed"] is False
    assert any(
        "recipient identity" in warning.lower()
        for warning in data["warning_signs"]
    )


def test_invalid_payment_amount_is_rejected():
    payload = {
        "invoice_description": "Office supplies",
        "amount": -100,
        "currency": "INR",
        "recipient": "ABC Office Supplies",
        "warning_details": "",
    }

    response = client.post("/analyze-payment", json=payload)

    assert response.status_code == 422
@patch("main.chat")
def test_ollama_failure_returns_503(mock_chat):
    mock_chat.side_effect = RuntimeError("Ollama unavailable")

    payload = {
        "invoice_description": "Office supplies",
        "amount": 1200,
        "currency": "INR",
        "recipient": "ABC Office Supplies",
        "warning_details": "",
    }

    response = client.post("/analyze-payment", json=payload)

    assert response.status_code == 503
    assert "AI analysis failed" in response.json()["detail"]

@patch("main.chat")
def test_malformed_ai_response_returns_503(mock_chat):
    mock_chat.return_value.message.content = "This is not valid JSON"

    payload = {
        "invoice_description": "Office supplies",
        "amount": 1200,
        "currency": "INR",
        "recipient": "ABC Office Supplies",
        "warning_details": "",
    }

    response = client.post("/analyze-payment", json=payload)

    assert response.status_code == 503
    assert "AI analysis failed" in response.json()["detail"]
@patch("main.chat")
def test_high_risk_payment_is_flagged(mock_chat):
    mock_chat.return_value.message.content = """
    {
        "risk_level": "HIGH",
        "warning_signs": [
            "Recipient bank details differ from the verified invoice",
            "Recipient is pressuring immediate payment"
        ],
        "explanation": "Conflicting bank details and payment pressure require investigation.",
        "recommended_action": "Stop and independently verify the recipient's bank details."
    }
    """

    payload = {
        "invoice_description": "Laptop repair",
        "amount": 5000,
        "currency": "INR",
        "recipient": "ABC Repairs",
        "warning_details": (
            "The recipient's bank details differ from the verified invoice. "
            "The recipient is pressuring us to pay immediately."
        ),
    }

    response = client.post("/analyze-payment", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["risk_level"] == "HIGH"
    assert len(data["warning_signs"]) >= 2
    assert data["payment_executed"] is False

@patch("main.chat")
def test_medium_risk_payment_requires_verification(mock_chat):
    mock_chat.return_value.message.content = """
    {
        "risk_level": "MEDIUM",
        "warning_signs": [
            "Invoice description lacks sufficient detail"
        ],
        "explanation": "The invoice lacks sufficient detail to confidently assess the transaction.",
        "recommended_action": "Request a detailed invoice and verify it before payment."
    }
    """

    payload = {
        "invoice_description": "Consulting services",
        "amount": 25000,
        "currency": "INR",
        "recipient": "ABC Consulting",
        "warning_details": "The invoice does not specify the services provided.",
    }

    response = client.post("/analyze-payment", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["risk_level"] == "MEDIUM"
    assert len(data["warning_signs"]) > 0
    assert data["payment_executed"] is False
def test_invalid_currency_is_rejected():
    payload = {
        "invoice_description": "Office supplies",
        "amount": 1200,
        "currency": "INVALID",
        "recipient": "ABC Office Supplies",
        "warning_details": "",
    }

    response = client.post("/analyze-payment", json=payload)

    assert response.status_code == 422
def test_empty_invoice_description_is_rejected():
    payload = {
        "invoice_description": "",
        "amount": 1200,
        "currency": "INR",
        "recipient": "ABC Office Supplies",
        "warning_details": "",
    }

    response = client.post("/analyze-payment", json=payload)

    assert response.status_code == 422
def test_excessive_payment_amount_is_rejected():
    payload = {
        "invoice_description": "Office supplies",
        "amount": 1_000_000_001,
        "currency": "INR",
        "recipient": "ABC Office Supplies",
        "warning_details": "",
    }

    response = client.post("/analyze-payment", json=payload)

    assert response.status_code == 422
def test_whitespace_only_invoice_description_is_rejected():
    payload = {
        "invoice_description": "   ",
        "amount": 1200,
        "currency": "INR",
        "recipient": "ABC Office Supplies",
        "warning_details": "",
    }

    response = client.post("/analyze-payment", json=payload)

    assert response.status_code == 422

def make_paypal_order_payload(**overrides):
    payload = {
        "invoice_description": "Office supplies invoice",
        "amount": 100,
        "currency": "USD",
        "recipient": "ABC Office Supplies",
        "warning_details": "",
        "verification_confirmed": False,
    }
    payload.update(overrides)
    return payload


@patch("main.get_paypal_access_token")
@patch("main.chat")
def test_high_risk_order_is_blocked(mock_chat, mock_token):
    mock_chat.return_value.message.content = json.dumps({
        "risk_level": "HIGH",
        "warning_signs": [
            "Unknown recipient",
            "Urgent payment with incomplete documentation",
        ],
        "explanation": "The payment requires investigation.",
        "recommended_action": "Stop and verify independently.",
    })

    response = client.post(
        "/paypal/create-order",
        json=make_paypal_order_payload(
            recipient="unknown",
            warning_details=(
                "Demands immediate payment and "
                "invoice lacks sufficient detail"
            ),
        ),
    )

    assert response.status_code == 403
    assert response.json()["detail"]["risk_level"] == "HIGH"
    mock_token.assert_not_called()


@patch("main.get_paypal_access_token")
@patch("main.chat")
def test_medium_risk_order_requires_confirmation(mock_chat, mock_token):
    mock_chat.return_value.message.content = json.dumps({
        "risk_level": "LOW",
        "warning_signs": [],
        "explanation": "No major warning signs.",
        "recommended_action": "Verify the recipient.",
    })

    response = client.post(
        "/paypal/create-order",
        json=make_paypal_order_payload(
            recipient="unknown",
            verification_confirmed=False,
        ),
    )

    assert response.status_code == 409
    assert response.json()["detail"]["risk_level"] == "MEDIUM"
    assert response.json()["detail"]["verification_required"] is True
    mock_token.assert_not_called()


@patch("main.urllib.request.urlopen")
@patch("main.get_paypal_access_token", return_value="fake-access-token")
@patch("main.chat")
def test_eligible_order_returns_approval_url(
    mock_chat,
    mock_token,
    mock_urlopen,
):
    mock_chat.return_value.message.content = json.dumps({
        "risk_level": "LOW",
        "warning_signs": [],
        "explanation": "No significant warning signs.",
        "recommended_action": "Review the order before approval.",
    })

    paypal_response = MagicMock()
    paypal_response.status = 201
    paypal_response.read.return_value = json.dumps({
        "id": "TEST-ORDER-123",
        "links": [
            {
                "rel": "approve",
                "href": "https://sandbox.example/approve/TEST-ORDER-123",
            }
        ],
    }).encode("utf-8")

    mock_urlopen.return_value.__enter__.return_value = paypal_response

    response = client.post(
        "/paypal/create-order",
        json=make_paypal_order_payload(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "created"
    assert data["order_id"] == "TEST-ORDER-123"
    assert data["approval_url"] == (
        "https://sandbox.example/approve/TEST-ORDER-123"
    )
    assert data["payment_executed"] is False
    mock_token.assert_called_once()


@patch("main.urllib.request.urlopen")
@patch("main.get_paypal_access_token", return_value="fake-access-token")
@patch("main.chat")
def test_paypal_order_error_returns_502(
    mock_chat,
    mock_token,
    mock_urlopen,
):
    mock_chat.return_value.message.content = json.dumps({
        "risk_level": "LOW",
        "warning_signs": [],
        "explanation": "No significant warning signs.",
        "recommended_action": "Review the order before approval.",
    })

    error_body = json.dumps({
        "name": "UNPROCESSABLE_ENTITY",
        "message": "Sandbox test error",
    }).encode("utf-8")

    mock_urlopen.side_effect = urllib.error.HTTPError(
        url="https://api-m.sandbox.paypal.com/v2/checkout/orders",
        code=422,
        msg="Unprocessable Entity",
        hdrs=None,  # type: ignore[arg-type]
        fp=io.BytesIO(error_body),
    )

    response = client.post(
        "/paypal/create-order",
        json=make_paypal_order_payload(),
    )

    assert response.status_code == 502
    assert "paypal_error" in response.json()["detail"]
    mock_token.assert_called_once()