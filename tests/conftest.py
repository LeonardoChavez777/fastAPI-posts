import pytest
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import databasemodels
from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite://"

# SQLite no soporta now() de PostgreSQL; asignamos created_at en Python.
for model in (databasemodels.User, databasemodels.Post):
    model.__table__.c.created_at.server_default = None


@event.listens_for(databasemodels.User, "before_insert")
@event.listens_for(databasemodels.Post, "before_insert")
def set_created_at(_mapper, _connection, target):
    if target.created_at is None:
        target.created_at = datetime.now(timezone.utc)


@pytest.fixture()
def db_session():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def user_credentials():
    return {"email": "test@example.com", "password": "secret123"}


@pytest.fixture()
def test_user(client, user_credentials):
    response = client.post("/users/", json=user_credentials)
    assert response.status_code == 201
    return {**user_credentials, **response.json()}


@pytest.fixture()
def auth_token(client, test_user, user_credentials):
    response = client.post(
        "/auth/login",
        data={"username": user_credentials["email"], "password": user_credentials["password"]},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture()
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture()
def sample_post():
    return {"title": "Test post", "content": "Test content", "published": True}
