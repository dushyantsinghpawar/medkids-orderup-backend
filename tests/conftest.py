import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, AsyncMock

# Set env vars before importing app modules
os.environ.setdefault("DATABASE_URL", os.getenv("TEST_DATABASE_URL", "postgresql://medkids:medkids@localhost:5432/medkids_test"))
os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_for_testing_only")
os.environ.setdefault("JWT_ALGORITHM", "HS256")

from app.main import app
from app.db.database import Base, get_db

engine = create_engine(os.environ["DATABASE_URL"])
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with patch("app.api.auth.rate_limit", new=AsyncMock(return_value=True)), \
         patch("app.api.auth.rate_limit_by_email", new=AsyncMock(return_value=True)), \
         patch("app.api.auth.EmailService.send_verification_email"), \
         patch("app.api.auth.EmailService.send_password_reset_email"):
        yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    client.post("/auth/register", json={
        "email": "parent@test.com",
        "password": "TestPass123!"
    })
    return {"email": "parent@test.com", "password": "TestPass123!"}


@pytest.fixture
def auth_headers(client, registered_user):
    res = client.post("/auth/login", json=registered_user)
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
