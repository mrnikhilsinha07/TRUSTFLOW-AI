import os
import base64
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("PAYPAL_CLIENT_ID")
client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
base_url = os.getenv(
    "PAYPAL_BASE_URL",
    "https://api-m.sandbox.paypal.com",
)

if not client_id or not client_secret:
    print("ERROR: PayPal credentials are missing from .env")
    raise SystemExit(1)

credentials = f"{client_id}:{client_secret}"
encoded_credentials = base64.b64encode(
    credentials.encode()
).decode()

request = urllib.request.Request(
    f"{base_url}/v1/oauth2/token",
    data=b"grant_type=client_credentials",
    headers={
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    },
    method="POST",
)

try:
    with urllib.request.urlopen(request, timeout=20) as response:
        print("PayPal Sandbox authentication: SUCCESS")
        print(f"HTTP status: {response.status}")

except urllib.error.HTTPError as error:
    print("PayPal Sandbox authentication: FAILED")
    print(f"HTTP status: {error.code}")
    print("Response:", error.read().decode()[:500])

except Exception as error:
    print("Connection error:", type(error).__name__)