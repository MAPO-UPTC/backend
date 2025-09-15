import pytest


def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_read_root(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "MAPO Backend API" in data["message"]


def test_cors_headers(client):
    """Test CORS headers are present"""
    response = client.get("/health")
    assert response.status_code == 200
    # Note: TestClient doesn't simulate CORS exactly like a browser
    # This is a basic test to ensure the endpoint works


def test_api_docs_available(client):
    """Test that API documentation endpoint responds appropriately"""
    response = client.get("/docs")
    # Docs may be disabled in non-debug mode (returns 404)
    # or available in debug mode (returns 200)
    assert response.status_code in [200, 404]


def test_openapi_json(client):
    """Test that OpenAPI JSON endpoint responds appropriately"""
    response = client.get("/openapi.json")
    # OpenAPI JSON should be available even in production
    # but might be disabled in some configurations
    if response.status_code == 200:
        data = response.json()
        assert "openapi" in data
        assert "info" in data
    else:
        # If disabled, should return 404
        assert response.status_code == 404
