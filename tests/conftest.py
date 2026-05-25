import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import TaskStorage
from app.dependencies import get_storage

# Override storage dependency so every test gets a fresh isolated instance
test_storage = TaskStorage()


def override_get_storage() -> TaskStorage:
    return test_storage


app.dependency_overrides[get_storage] = override_get_storage


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    """Reset storage before each test."""
    test_storage.clear()
    yield
