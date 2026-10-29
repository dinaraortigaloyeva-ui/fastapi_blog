
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db


client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()
    assert data["xabar"] == "Blog API"
    assert data["version"] == "5.0.0"
    assert "environment" in data


def test_health_success():
    db = Mock()
    db.execute.return_value = None

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["database"] == "ok"
        db.execute.assert_called_once()
    finally:
        app.dependency_overrides.clear()


def test_health_database_error():
    db = Mock()
    db.execute.side_effect = Exception("Database error")
    db.rollback.return_value = None

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/health")

        assert response.status_code == 503
        assert response.json()["status"] == "error"
        assert response.json()["database"] == "error"
        db.rollback.assert_called_once()
    finally:
        app.dependency_overrides.clear()
