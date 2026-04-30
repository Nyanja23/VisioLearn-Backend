"""
Sample test file for API endpoints - shows testing structure
Run actual tests against your endpoints by expanding this file
"""
import pytest


@pytest.mark.unit
def test_openapi_documentation():
    """Test that OpenAPI documentation includes required information"""
    from app.main import app
    
    openapi_schema = app.openapi()
    assert openapi_schema is not None
    assert openapi_schema["info"]["title"] == "VisioLearn Backend"
    assert "version" in openapi_schema["info"]


@pytest.mark.integration
def test_api_auth_routes_exist(test_client):
    """Test that auth routes are registered"""
    # The /openapi.json endpoint lists all routes
    response = test_client.get("/openapi.json")
    schema = response.json()
    paths = schema["paths"]
    
    # Check for expected auth routes
    expected_auth_endpoints = [
        "/api/v1/auth/login",
        "/api/v1/auth/register",
    ]
    
    available_paths = list(paths.keys())
    for endpoint in expected_auth_endpoints:
        assert endpoint in available_paths, f"Missing endpoint: {endpoint}"


@pytest.mark.integration
def test_api_voice_routes_exist(test_client):
    """Test that voice session routes are registered"""
    response = test_client.get("/openapi.json")
    schema = response.json()
    paths = schema["paths"]
    
    # Check for expected voice routes
    expected_voice_endpoints = [
        "/api/v1/voice/session/start",
        "/api/v1/voice/session/event",
        "/api/v1/voice/session/end",
    ]
    
    available_paths = list(paths.keys())
    for endpoint in expected_voice_endpoints:
        assert endpoint in available_paths, f"Missing voice endpoint: {endpoint}"
