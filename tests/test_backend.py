import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_read_main(client):
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello world!"}
