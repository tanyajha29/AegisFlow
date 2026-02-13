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
from app.models.role import Role  # noqa: E402
from app.models.user import User  # noqa: E402
from app.core.security import hash_password  # noqa: E402


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


@pytest.fixture()
def admin_user(client):
    db = SessionLocal()
    try:
        role = db.query(Role).filter(Role.name == "admin").first()
        if not role:
            role = Role(name="admin")
            db.add(role)
            db.commit()
            db.refresh(role)

        user = User(
            username="admin_user",
            hashed_password=hash_password("Password123!"),
            is_active=True,
            role_id=role.id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


@pytest.fixture()
def admin_token(client, admin_user):
    response = client.post(
        "/auth/login",
        json={"email": "admin_user", "password": "Password123!"}
    )
    return response.json()["access_token"]


@pytest.fixture()
def normal_user(client):
    response = client.post(
        "/auth/signup",
        json={"username": "normal_user", "password": "Password123!"}
    )
    return response.json()


@pytest.fixture()
def normal_token(client, normal_user):
    response = client.post(
        "/auth/login",
        json={"email": "normal_user", "password": "Password123!"}
    )
    return response.json()["access_token"]
