"""
Tests package initialization
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def test_client():
    """Create a test client for FastAPI app"""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def auth_token(test_client):
    """Get a valid JWT token for testing (if login exists)"""
    # This is a placeholder - update based on your auth implementation
    return None
