import shutil
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.database import get_db
from api.main import app

MOCK_DB = "tests/resources/mock.db"

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