import pytest
import os
import json
from fastapi.testclient import TestClient
from dotenv import load_dotenv

key = os.getenv("API_KEY") or ""

def test_get_root(client: TestClient):
    response = client.get("/", headers={"X-API-KEY": key})
    assert response.status_code == 200
    assert response.json() == {"message": "Hello! Look at http://localhost:8000/docs for documentation."}

def test_get_device_breakdown(client: TestClient):
    response = client.get("/analytics/devices/breakdown", headers={"X-API-KEY": key})
    assert response.status_code == 200
    assert response.json() == {"number_of_devices":{"iPhone 15 Pro":3,"iPhone 14":3,"iPhone 13":3,"iPhone 15":2},
                                "percentage_of_devices":{"iPhone 13":27.3,"iPhone 14":27.3,"iPhone 15":18.2,"iPhone 15 Pro":27.3}}
    
def test_post_add_event_batch(client: TestClient, db):
    payload = {
            "events": [
                {
                    "event_name": "app_launched",
                    "user_id": "post_request_test",
                    "session_id": "F9E8D7C6-B5A4-3210-FEDC-BA9876543210",
                    "timestamp": "2026-06-20T01:30:00Z",
                    "properties": {
                        "device_model": "iPhone 15",
                        "os_version": "iOS 26.4",
                        "app_version": "1.2.0",
                        "color_scheme": "dark",
                        "accessibility_features": ["voiceover","larger_text"]
                    }
                },
                {
                    "event_name": "button_tapped",
                    "user_id": "post_request_test",
                    "session_id": "F9E8D7C6-B5A4-3210-FEDC-BA9876543210",
                    "timestamp": "2026-06-20T01:30:08Z",
                    "properties": {
                        "button_id": "login_button",
                        "screen": "account_settings",
                        "foo": "bar"
                    }
                }
            ]
        }
    
    response = client.post("/events/batch", headers={"X-API-KEY": key}, json=payload)
    
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
