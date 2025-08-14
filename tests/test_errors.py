"""Error handling tests."""
import pytest
from webapp import create_app


@pytest.fixture
async def app():
    """Create test app."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
async def client(app):
    """Create test client."""
    return app.test_client()


@pytest.mark.asyncio
async def test_404_error_json(client):
    """Test 404 error with JSON request."""
    response = await client.get(
        "/nonexistent/endpoint",
        headers={"Accept": "application/json"}
    )
    
    assert response.status_code == 404
    data = await response.get_json()
    assert "error" in data
    assert "not found" in data["error"].lower()


@pytest.mark.asyncio
async def test_404_error_html(client):
    """Test 404 error with HTML request."""
    response = await client.get("/nonexistent/page")
    
    assert response.status_code == 404
    data = await response.get_json()
    assert "error" in data


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test health endpoint."""
    response = await client.get("/health")
    
    assert response.status_code == 200
    data = await response.get_json()
    assert data["status"] == "ok"
