import shutil
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from api.database import get_db
from api.main import app

MOCK_DB = Path(__file__).parent / "tests" / "resources" / "mock.db"

@pytest.fixture(scope="function")
def db(tmp_path):
    db_copy = tmp_path / "test.db"
    shutil.copy(MOCK_DB, db_copy)

    engine = create_engine(f"sqlite:///{db_copy}", connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    # teardown
    session.close()

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def event_batch_payload():
    return {
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