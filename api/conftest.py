import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.database import get_db, Base
from api.main import app
from .tests import seed

MOCK_DB = Path(__file__).parent / "tests" / "mock.db"

@pytest.fixture(scope="session")
def db():
    engine = create_engine(f"sqlite:///{MOCK_DB}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    # teardown
    session.close()

@pytest.fixture(scope="session", autouse=True)
def seed_database(db):
    seed.seed(db)

@pytest.fixture(scope="session")
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def event_batch_payload():
    def _make(user_id: str):
        return {
            "events": [
                {
                    "event_name": "app_launched",
                    "user_id": user_id,
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
                    "user_id": user_id,
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
    return _make