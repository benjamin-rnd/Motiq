from fastapi.testclient import TestClient
from api.main import app
from dotenv import load_dotenv
import os

key = os.getenv("API_KEY") or ""

client = TestClient(app)

def test_get_root():
    response = client.get("/", headers={"X-API-KEY": key})
    assert response.status_code == 200
    assert response.json() == {"message": "Hello! Look at http://localhost:8000/docs for documentation."}