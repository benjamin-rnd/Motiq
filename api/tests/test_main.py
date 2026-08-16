import json
import os
import time

import pytest

from fastapi.testclient import TestClient
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("API_KEY") or ""
secret = os.getenv("API_SECRET") or ""

def test_get_device_breakdown(client: TestClient):
    response = client.get("/analytics/devices/breakdown", headers={"X-API-KEY": key})
    assert response.status_code == 200
    assert response.json() == {"number_of_devices":{"iPhone 15 Pro":3,"iPhone 14":3,"iPhone 13":3,"iPhone 15":2},
                                "percentage_of_devices":{"iPhone 13":27.3,"iPhone 14":27.3,"iPhone 15":18.2,"iPhone 15 Pro":27.3}}

def test_post_add_event_batch_success(client: TestClient, db, event_batch_payload):
    payload_bytes = json.dumps(event_batch_payload, separators = (',', ':')).encode()
    timestamp = str(int(time.time()))
    from api.auth import generate_hmac_signature
    signature = generate_hmac_signature(timestamp, payload_bytes)

    response = client.post(
        "/events/batch", 
        headers={
            "X-Timestamp": timestamp,
            "X-Signature": signature
            }, 
        json=event_batch_payload)
    
    from api.orm_models import Event
    events = db.query(Event).filter(Event.user_id == "post_request_test").all()

    assert response.status_code == 201
    assert len(events) == 2
    assert events[0].event_name == "app_launched"
    assert events[0].timestamp == "2026-06-20T01:30:00Z"
    assert len(json.loads(events[0].properties)) == 5
    assert events[1].event_name == "button_tapped"
    assert events[1].timestamp == "2026-06-20T01:30:08Z"
    assert len(json.loads(events[1].properties)) == 3

def test_post_add_event_batch_invalid_signature(client: TestClient, db, event_batch_payload):
    payload_bytes = json.dumps(event_batch_payload, separators = (',', ':')).encode()
    timestamp = str(int(time.time()))
    signature = "this is a wrong signature"

    response = client.post(
        "/events/batch", 
        headers={
            "X-Timestamp": timestamp,
            "X-Signature": signature
            }, 
        json=event_batch_payload)

    from api.orm_models import Event
    events = db.query(Event).filter(Event.user_id == "post_request_test").all()

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid signature"
    assert len(events) == 0

def test_post_add_event_batch_missing_header_signature(client: TestClient, db, event_batch_payload):
    payload_bytes = json.dumps(event_batch_payload, separators = (',', ':')).encode()
    timestamp = str(int(time.time()))

    response = client.post(
        "/events/batch", 
        headers={"X-Timestamp": timestamp},
        json=event_batch_payload)

    from api.orm_models import Event
    events = db.query(Event).filter(Event.user_id == "post_request_test").all()

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing authentication headers"
    assert len(events) == 0

def test_post_add_event_batch_missing_header_timestamp(client: TestClient, db, event_batch_payload):
    payload_bytes = json.dumps(event_batch_payload, separators = (',', ':')).encode()
    timestamp = str(int(time.time()))
    from api.auth import generate_hmac_signature
    signature = generate_hmac_signature(timestamp, payload_bytes)

    response = client.post(
        "/events/batch", 
        headers={"X-Signature": signature},
        json=event_batch_payload)

    from api.orm_models import Event
    events = db.query(Event).filter(Event.user_id == "post_request_test").all()

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing authentication headers"
    assert len(events) == 0

def test_post_add_event_batch_expired_timestamp(client: TestClient, db, event_batch_payload):
    payload_bytes = json.dumps(event_batch_payload, separators = (',', ':')).encode()

    expired_timestamp = str(int(time.time()) - 301)
    from api.auth import generate_hmac_signature
    signature = generate_hmac_signature(expired_timestamp, payload_bytes)

    response = client.post(
        "/events/batch",
        headers={
            "X-Timestamp": expired_timestamp,
            "X-Signature": signature
            }, 
        json=event_batch_payload)
    
    from api.orm_models import Event
    events = db.query(Event).filter(Event.user_id == "post_request_test").all()

    assert response.status_code == 401
    assert response.json()["detail"] == "Expired timestamp"
    assert len(events) == 0