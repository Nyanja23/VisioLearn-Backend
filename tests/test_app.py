"""
Health check and basic endpoint tests
"""
import pytest


@pytest.mark.unit
def test_app_imports():
    """Test that the FastAPI app can be imported"""
    try:
        from app.main import app
        assert app is not None
    except ImportError as e:
        pytest.fail(f"Failed to import FastAPI app: {e}")


@pytest.mark.unit
def test_app_has_routes(test_client):
    """Test that the FastAPI app has routes registered"""
    # Get OpenAPI schema which lists all routes
    response = test_client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert len(schema["paths"]) > 0


@pytest.mark.unit
def test_swagger_ui_available(test_client):
    """Test that Swagger UI is available"""
    response = test_client.get("/docs")
    assert response.status_code == 200


@pytest.mark.integration
def test_app_can_generate_openapi_schema(test_client):
    """Test that OpenAPI schema can be generated without errors"""
    response = test_client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    
    # Verify schema structure
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema
    assert "components" in schema
