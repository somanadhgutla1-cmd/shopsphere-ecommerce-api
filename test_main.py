import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_register_user():
    response = client.post(
        "/register",
        json={"email": "testuser@example.com", "password": "securepassword123"}
    )
    # 201 Created or 400 if already exists from prior run
    assert response.status_code in [201, 400]

def test_get_products():
    response = client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
