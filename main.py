from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from ollama import chat

app = FastAPI(
    title="TRUSTFLOW AI",
    description="AI-powered payment risk analysis and management.",
    version="0.2.0",
)

MODEL = "qwen3:1.7b"


class PaymentRequest(BaseModel):
    invoice_description: str = Field(min_length=1, max_length=2000)
    amount: float = Field(gt=0, le=1000000000)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    recipient: str = Field(min_length=1, max_length=200)
    warning_details: str = Field(default="", max_length=2000)


@app.get("/")
def home():
    return {
        "app": "TRUSTFLOW AI",
        "status": "running",
        "message": "AI payment safety assistant is ready."
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/analyze-payment")
def analyze_payment(payment: PaymentRequest):
    prompt = f"""
    You are the payment risk analysis component of TRUSTFLOW AI.

    Analyze the following payment request.

    Invoice description: {payment.invoice_description}
    Amount: {payment.amount} {payment.currency}
    Recipient: {payment.recipient}
    Additional warning details: {payment.warning_details or "None provided"}

    Return:
    1. Risk level: LOW, MEDIUM, or HIGH.
    2. Warning signs.
    3. Explanation supported by the supplied information.
    4. Recommended action.

    Rules:
    - Do not claim fraud is confirmed without sufficient evidence.
    - Missing information is not proof of fraud.
    - Explain uncertainty.
    - Recommend independent verification when appropriate.
    - Do not authorize or execute any payment.
    """

    try:
        response = chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            think=False,
        )

        return {
            "status": "success",
            "payment": payment.model_dump(),
            "analysis": response.message.content,
            "payment_executed": False,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "AI analysis is currently unavailable. "
                "Check that Ollama is running and the model is installed."
            ),
        ) from exc