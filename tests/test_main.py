from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "DevOps Lab" in data["message"]


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_secret_check():
    response = client.get("/secret-check")
    assert response.status_code == 200
    data = response.json()
    assert "api_key_exists" in data
    assert "api_key_length" in data


@patch.dict("os.environ", {"API_KEY": "test-key-123"})
def test_secret_check_with_key():
    response = client.get("/secret-check")
    data = response.json()
    assert data["api_key_exists"] is True
    assert data["api_key_length"] == 12
