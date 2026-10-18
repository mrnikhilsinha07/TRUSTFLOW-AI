# TRUSTFLOW AI

### AI-Powered Payment Risk Analysis and Management

TRUSTFLOW AI is an AI-powered payment risk analysis and management assistant developed for the PayPal AI Hackathon.

It helps users identify suspicious payment requests, understand potential warning signs, and make informed decisions before proceeding with a payment.

The application combines local AI inference with PayPal Sandbox integration to analyze payment risks, create checkout orders, and capture payments after buyer approval.

## Features

- **AI-Powered Risk Analysis:** Evaluates payment requests and identifies potential warning signs.
- **Risk Classification:** Classifies payments as LOW, MEDIUM, HIGH, or UNCERTAIN.
- **Actionable Recommendations:** Provides guidance on verifying suspicious payment details.
- **Risk-Based Payment Controls:**
  - HIGH and UNCERTAIN payments are blocked.
  - MEDIUM-risk payments require independent verification confirmation.
  - LOW-risk payments can proceed to checkout.
- **PayPal Sandbox Integration:** Authenticates with PayPal and creates checkout orders.
- **Payment Capture:** Captures approved Sandbox orders and checks PayPal's response.
- **Local AI Inference:** Uses Ollama with the Qwen3 1.7B model.
- **REST API:** Built with FastAPI.
- **Interactive Documentation:** Explore and test endpoints through Swagger UI.
- **Automated Tests:** Includes tests for risk analysis, order creation, and payment capture.

> **Important:** TRUSTFLOW AI currently integrates with PayPal Sandbox for testing. It is not a live payment-processing deployment. Risk classifications are decision-support signals, not guarantees that a payment is safe or fraudulent.

## Technology Stack

- Python 3.13
- FastAPI
- Uvicorn
- Ollama
- Qwen3 1.7B
- PayPal Orders API v2
- Pydantic
- Pytest

## Prerequisites

Install the following:

- Python 3.13
- Git
- Ollama
- The `qwen3:1.7b` model
- A PayPal Developer account with Sandbox API credentials

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/mrnikhilsinha07/TRUSTFLOW-AI.git
cd TRUSTFLOW-AI
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Install and start Ollama

Install Ollama from its official website:

https://ollama.com/

Download the required model:

```powershell
ollama pull qwen3:1.7b
```

Confirm that the model is available:

```powershell
ollama list
```

Make sure the Ollama service is running before testing AI-powered endpoints.

### 5. Configure PayPal Sandbox credentials

Create a `.env` file in the project root directory.

Add your own PayPal Sandbox credentials:

```dotenv
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_client_secret
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
```

Replace the example values with your actual Sandbox credentials.

**Never commit your `.env` file, client secret, access tokens, or other credentials to GitHub.**

### 6. Start TRUSTFLOW AI

Run:

```powershell
uvicorn main:app --reload
```

The API should be available at:

http://127.0.0.1:8000

Open the interactive API documentation:

http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Application information |
| GET | `/health` | Health check |
| POST | `/analyze-payment` | Analyze payment risk |
| GET | `/paypal/status` | Check PayPal Sandbox connection status |
| POST | `/paypal/create-order` | Analyze risk and create an eligible Sandbox checkout order |
| POST | `/paypal/capture-order` | Capture an approved Sandbox order |

See `/docs` for request schemas, response formats, and interactive testing.

## Payment Workflow

1. The user submits payment details.
2. TRUSTFLOW AI analyzes the payment request.
3. The application applies risk-based controls.
4. Eligible payments proceed to PayPal Sandbox order creation.
5. The buyer opens the PayPal approval URL and approves checkout.
6. The application receives the buyer's return.
7. The capture endpoint requests payment capture.
8. TRUSTFLOW AI checks PayPal's response before reporting successful capture.

Creating an order does not itself capture a payment. A successful capture response is required before the application reports that the payment was executed.

## Running Tests

Activate the virtual environment, then run:

```powershell
pytest -v
```

The project has previously passed all 22 automated tests.

The tests cover application endpoints, risk controls, invalid payment inputs, PayPal order creation, and payment capture behavior.

## AI Evaluation

The project includes an evaluation dataset and script:

- `evaluation/payment_scenarios.json`
- `evaluation/evaluate_model.py`
- `evaluation/evaluation_results.json`

The evaluation dataset contains six payment scenarios.

The latest recorded evaluation achieved a 100% risk-level match rate across those six scenarios. This result applies only to the tested dataset and does not establish real-world fraud-detection accuracy.

## Project Structure

```text
TRUSTFLOW-AI/
├── main.py
├── requirements.txt
├── test_paypal_auth.py
├── tests/
│   └── test_main.py
├── evaluation/
│   ├── payment_scenarios.json
│   ├── evaluate_model.py
│   └── evaluation_results.json
├── .env.example
├── .gitignore
└── README.md
```

The exact files in your local repository may differ as the project develops.

## Security and Limitations

- Use PayPal Sandbox credentials for development and testing.
- Do not commit secrets or real customer payment information.
- Never treat an AI risk classification as definitive proof of fraud or legitimacy.
- Independent verification should use a trusted channel outside the suspicious payment request.
- Production deployment would require additional security reviews, monitoring, error handling, and operational controls.
- Temporary Cloudflare tunnels are intended for development and demonstration, not reliable production hosting.

## License

See the repository's `LICENSE` file for the applicable license terms.