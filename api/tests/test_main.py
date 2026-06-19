import pytest
import os
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