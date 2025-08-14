"""API endpoint tests."""
import pytest
import pytest_asyncio
import json
import uuid
from pydantic import ValidationError
from webapp import create_app
from webapp.schemas import ChatRequest, ChatResponse, ChatMessage


@pytest_asyncio.fixture
async def app():
    """Create test app."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest_asyncio.fixture
async def client(app):
    """Create test client."""
    return app.test_client()


@pytest.mark.asyncio
async def test_chat_endpoint_valid_request(client):
    """Test chat endpoint with valid request."""
    payload = {"message": "Hello, world!"}
    
    response = await client.post("/api/chat", json=payload)
    
    assert response.status_code == 200
    data = await response.get_json()
    
    # Validate response structure using Pydantic
    chat_response = ChatResponse(**data)
    
    # Verify response structure
    assert chat_response.model == "demo-echo-1"
    assert len(chat_response.choices) == 1
    assert chat_response.choices[0].role == "assistant"
    assert "Echo: Hello, world!" in chat_response.choices[0].content
    
    # Verify UUID format
    assert uuid.UUID(chat_response.id)


@pytest.mark.asyncio
async def test_chat_endpoint_empty_message(client):
    """Test chat endpoint with empty message."""
    payload = {"message": ""}
    
    response = await client.post("/api/chat", json=payload)
    
    assert response.status_code == 200
    data = await response.get_json()
    
    chat_response = ChatResponse(**data)
    assert "Echo: " in chat_response.choices[0].content


@pytest.mark.asyncio
async def test_chat_endpoint_missing_message(client):
    """Test chat endpoint with missing message field."""
    payload = {}
    
    response = await client.post("/api/chat", json=payload)
    
    assert response.status_code == 400
    data = await response.get_json()
    assert "error" in data


@pytest.mark.asyncio
async def test_chat_endpoint_invalid_json(client):
    """Test chat endpoint with invalid JSON."""
    response = await client.post(
        "/api/chat", 
        data="invalid json",
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_chat_endpoint_long_message(client):
    """Test chat endpoint with very long message."""
    long_message = "x" * 1000
    payload = {"message": long_message}
    
    response = await client.post("/api/chat", json=payload)
    
    assert response.status_code == 200
    data = await response.get_json()
    
    chat_response = ChatResponse(**data)
    assert f"Echo: {long_message}" in chat_response.choices[0].content


@pytest.mark.asyncio
async def test_chat_endpoint_special_characters(client):
    """Test chat endpoint with special characters."""
    special_message = "Hello! 🌟 Testing with émojis & spëcial chars: <>&'\"\\n\\t"
    payload = {"message": special_message}
    
    response = await client.post("/api/chat", json=payload)
    
    assert response.status_code == 200
    data = await response.get_json()
    
    chat_response = ChatResponse(**data)
    assert f"Echo: {special_message}" in chat_response.choices[0].content


@pytest.mark.asyncio
async def test_pydantic_validation():
    """Test Pydantic model validation directly."""
    # Test valid ChatRequest
    valid_request = ChatRequest(message="Test message")
    assert valid_request.message == "Test message"
    
    # Test valid ChatResponse
    valid_response = ChatResponse(
        id=str(uuid.uuid4()),
        model="test-model",
        choices=[ChatMessage(role="assistant", content="Test response")]
    )
    assert len(valid_response.choices) == 1
    assert valid_response.choices[0].role == "assistant"
    
    # Test invalid role
    with pytest.raises(ValidationError):
        ChatMessage(role="invalid_role", content="Test")


@pytest.mark.asyncio
async def test_api_health_check(client):
    """Test if API endpoints are properly registered."""
    # This tests that the blueprint registration is working
    response = await client.post("/api/chat", json={"message": "health check"})
    assert response.status_code == 200
