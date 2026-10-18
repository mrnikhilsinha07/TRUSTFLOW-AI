# TRUSTFLOW AI dashboard package

This package adds a browser dashboard to the existing FastAPI + Ollama + PayPal Sandbox project.

## Install
1. Back up your current `main.py`.
2. Copy this package's `main.py` into your `D:\\TRUSTFLOW_AI` project folder, replacing the existing `main.py`.
3. Copy the entire `dashboard` folder beside `main.py`, so the path is `D:\\TRUSTFLOW_AI\\dashboard\\index.html`.
4. Keep your existing `.env`, `.venv`, tests, evaluation files, README, and LICENSE unchanged.

The updated `main.py` preserves the existing API routes and mounts the dashboard at `/dashboard`.

## Run
In PowerShell:
```powershell
cd D:\\TRUSTFLOW_AI
.\\.venv\\Scripts\\Activate.ps1
uvicorn main:app --reload
```
Open `http://127.0.0.1:8000/dashboard`.

## Included
- Responsive overview page with live FastAPI and PayPal Sandbox status checks.
- AI risk analysis form connected to `POST /analyze-payment`.
- PayPal Sandbox order creation connected to `POST /paypal/create-order`.
- Capture workflow connected to `POST /paypal/capture-order`.
- Local-browser activity history and session-only risk distribution.
- Clear loading, validation, and API error states.

## Notes
- The original `/` route remains the JSON health-style homepage and `/docs` remains available.
- The dashboard does not store transaction history on the server. Activity is saved in this browser's localStorage and can be cleared from the Activity page.
- PayPal order creation uses your backend's existing configured return/cancel URLs. Those URLs must point to a currently running public tunnel for the browser to return to your local app.
- This is a prototype, not a production payment system. Do not use real payment credentials or sensitive customer data. AI output is advisory and must be reviewed.
- Some currencies may be unsupported by PayPal Sandbox; USD is the safest option for a checkout demo.
