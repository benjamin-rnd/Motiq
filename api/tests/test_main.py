import json
import os
import time

import pytest

from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import text

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

    # teardown
    db.execute(text(f"DELETE FROM events WHERE user_id = '{test_placeholder}'"))
    db.commit()

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

def test_analytics_unauthorized(client: TestClient):
    response = client.get("/analytics/users/active", headers={"X-API-Key": "wrong key"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API Key"

def test_get_dau_mau_success(client: TestClient):
    response = client.get("/analytics/users/active", headers={"X-API-Key": key})

    assert response.status_code == 200
    assert response.json()["dau"] == 7
    assert response.json()["mau"] == 20

def test_get_new_vs_returning_users(client: TestClient):
    response = client.get("/analytics/users/new-vs-returning", headers={"X-API-Key": key})

    assert response.status_code == 200
    assert response.json()["last_7d"]["absolute"] == { "new_users": 5, "returning_users": 9 }
    assert response.json()["last_7d"]["percentage"] == { "new_users": 35.7, "returning_users": 64.3 }
    assert response.json()["last_30d"]["absolute"] == { "new_users": 20, "returning_users": 0 }
    assert response.json()["last_30d"]["percentage"] == { "new_users": 100.0, "returning_users": 0.0 }

def test_get_session_summary(client: TestClient):
    response = client.get("/analytics/sessions/summary", headers={"X-API-Key": key})

    assert response.status_code == 200
    assert response.json() == { "sessions_today": 9, "avg_sessions_last_7d": 2.3,
        "avg_sessions_last_30d": 1.0, "avg_duration_per_session": 0.0 }

def test_get_device_breakdown(client: TestClient):
    response = client.get("/analytics/devices/breakdown", headers={"X-API-Key": key})

    assert response.status_code == 200
    assert response.json()["absolute"] == {
        "iPhone 13": 4,
        "iPhone 13 Pro": 1,
        "iPhone 14": 5,
        "iPhone 15": 3,
        "iPhone 15 Pro": 4,
        "iPhone 16": 2,
        "iPhone 16 Pro": 1
    }
    assert response.json()["percentage"] == {
        "iPhone 13": 20.0,
        "iPhone 13 Pro": 5.0,
        "iPhone 14": 25.0,
        "iPhone 15": 15.0,
        "iPhone 15 Pro": 20.0,
        "iPhone 16": 10.0,
        "iPhone 16 Pro": 5.0
    }

def test_get_environment_breakdown(client: TestClient):
    response = client.get("/analytics/environment/breakdown", headers={"X-API-Key": key})

    assert response.status_code == 200
    assert response.json()["os_version"]["absolute"] == { "18.1": 5, "18.2": 5, "18.3": 7, "18.4": 3 }
    assert response.json()["os_version"]["percentage"] == { 
        "18.1": 25.0, "18.2": 25.0, "18.3": 35.0, "18.4": 15.0 
    }
    assert response.json()["color_scheme"]["absolute"] == { "dark": 11, "light": 9 }
    assert response.json()["color_scheme"]["percentage"] == { "dark": 55.0, "light": 45.0 }
    assert response.json()["orientation"]["absolute"] == { "landscape": 2, "portrait": 19 }
    assert response.json()["orientation"]["percentage"] == { "landscape": 9.5, "portrait": 90.5 }
    assert response.json()["connectivity"]["absolute"] == { "cellular": 6, "wifi": 16 }
    assert response.json()["connectivity"]["percentage"] == { "cellular": 27.3, "wifi": 72.7 }
    assert response.json()["accessibility_features"]["absolute"] == { 
        "bold_text": 3, "larger_text": 5, "reduce_motion": 3, "voiceover": 1 
    }
    assert response.json()["accessibility_features"]["percentage"] == {
        "bold_text": 25.0, "larger_text": 41.7, "reduce_motion": 25.0, "voiceover": 8.3
    }
