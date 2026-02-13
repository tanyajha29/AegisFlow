import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Configure test environment before importing app modules.
BASE_DIR = Path(__file__).resolve().parents[1]
TEST_DB_PATH = BASE_DIR / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("JWT_EXPIRY_MINUTES", "60")

from app.main import app  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import SessionLocal, engine, get_db  # noqa: E402


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
