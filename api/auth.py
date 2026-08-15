from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from dotenv import load_dotenv
import os
import time
import hmac
import hashlib

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")
    return key

def verify_hmac_signature(given_signature: str, timestamp: str, body: bytes) -> bool:
    # Timestamp-Check
    try:
        ts = int(timestamp)
    except ValueError:
        return False

    if abs(time.time() - ts) > 300:
        return False

    # HMAC-Check
    expected_signature = generate_hmac_signature(timestamp, body)

    if hmac.compare_digest(expected_signature, given_signature):
        return True
    else:
        return False

def generate_hmac_signature(timestamp: str, body: bytes) -> str:
    message = timestamp.encode() + body
    if not API_SECRET:
        raise RuntimeError("API_SECRET is not set in environment")
    return hmac.new(
        key = API_SECRET.encode(),
        msg = message,
        digestmod = hashlib.sha256
    ).hexdigest()