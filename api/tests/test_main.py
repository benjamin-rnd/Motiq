import json
import os
import time

import pytest

from dotenv import load_dotenv
from fastapi.testclient import TestClient

load_dotenv()
key = os.getenv("API_KEY") or ""
secret = os.getenv("API_SECRET") or ""

def test_post_add_event_batch_success(client: TestClient, db, event_batch_payload):
    test_placeholder = "post_test_success"
    payload_bytes = json.dumps(event_batch_payload(test_placeholder), separators = (',', ':')).encode()
    timestamp = str(int(time.time()))
    from api.auth import generate_hmac_signature
    signature = generate_hmac_signature(timestamp, payload_bytes)

    response = client.post(
        "/events/batch", 
        headers={
            "X-Timestamp": timestamp,
            "X-Signature": signature
            }, 
        json=event_batch_payload(test_placeholder))
    
    from api.orm_models import Event
    events = db.query(Event).filter(Event.user_id == test_placeholder).all()

    assert response.status_code == 201
    assert len(events) == 2
    assert events[0].event_name == "app_launched"
    assert events[0].timestamp == "2026-06-20T01:30:00Z"
    assert len(json.loads(events[0].properties)) == 5
    assert events[1].event_name == "button_tapped"
    assert events[1].timestamp == "2026-06-20T01:30:08Z"
    assert len(json.loads(events[1].properties)) == 3

def test_post_add_event_batch_invalid_signature(client: TestClient, db, event_batch_payload):
    test_placeholder = "post_test_success_invalid_signature"
    payload_bytes = json.dumps(event_batch_payload(test_placeholder), separators = (',', ':')).encode()
    timestamp = str(int(time.time()))
    signature = "this is a wrong signature"

    response = client.post(
        "/events/batch", 
        headers={
            "X-Timestamp": timestamp,
            "X-Signature": signature
            }, 
        json=event_batch_payload(test_placeholder))

    from api.orm_models import Event
    events = db.query(Event).filter(Event.user_id == test_placeholder).all()

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid signature"
    assert len(events) == 0

def test_post_add_event_batch_missing_header_signature(client: TestClient, db, event_batch_payload):
    test_placeholder = "post_test_missing_signature"
    payload_bytes = json.dumps(event_batch_payload(test_placeholder), separators = (',', ':')).encode()
    timestamp = str(int(time.time()))

    response = client.post(
        "/events/batch", 
        headers={"X-Timestamp": timestamp},
        json=event_batch_payload(test_placeholder))

    from api.orm_models import Event
    events = db.query(Event).filter(Event.user_id == test_placeholder).all()

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing authentication headers"
    assert len(events) == 0

def test_post_add_event_batch_missing_header_timestamp(client: TestClient, db, event_batch_payload):
    test_placeholder = "post_test_missing_timestamp"
    payload_bytes = json.dumps(event_batch_payload(test_placeholder), separators = (',', ':')).encode()
    timestamp = str(int(time.time()))
    from api.auth import generate_hmac_signature
    signature = generate_hmac_signature(timestamp, payload_bytes)

    response = client.post(
        "/events/batch", 
        headers={"X-Signature": signature},
        json=event_batch_payload(test_placeholder))

    from api.orm_models import Event
    events = db.query(Event).filter(Event.user_id == test_placeholder).all()

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing authentication headers"
    assert len(events) == 0

def test_post_add_event_batch_expired_timestamp(client: TestClient, db, event_batch_payload):
    test_placeholder = "post_test_expired_timestamp"
    payload_bytes = json.dumps(event_batch_payload(test_placeholder), separators = (',', ':')).encode()

    expired_timestamp = str(int(time.time()) - 301)
    from api.auth import generate_hmac_signature
    signature = generate_hmac_signature(expired_timestamp, payload_bytes)

    response = client.post(
        "/events/batch",
        headers={
            "X-Timestamp": expired_timestamp,
            "X-Signature": signature
            }, 
        json=event_batch_payload(test_placeholder))
    
    from api.orm_models import Event
    events = db.query(Event).filter(Event.user_id == test_placeholder).all()

    assert response.status_code == 401
    assert response.json()["detail"] == "Expired timestamp"
    assert len(events) == 0