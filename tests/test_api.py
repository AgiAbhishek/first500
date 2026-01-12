"""
Basic tests for the AI RAG Agent API.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AI RAG Agent API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert "vector_store_initialized" in data


def test_ask_endpoint_simple_query():
    """Test the /ask endpoint with a simple query."""
    response = client.post(
        "/api/ask",
        json={"query": "What is 2+2?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "session_id" in data
    assert isinstance(data["sources"], list)


def test_ask_endpoint_with_session():
    """Test the /ask endpoint with session continuity."""
    # First request
    response1 = client.post(
        "/api/ask",
        json={"query": "Hello, my name is Alice"}
    )
    assert response1.status_code == 200
    session_id = response1.json()["session_id"]
    
    # Second request with same session
    response2 = client.post(
        "/api/ask",
        json={
            "query": "What's my name?",
            "session_id": session_id
        }
    )
    assert response2.status_code == 200
    data = response2.json()
    assert session_id == data["session_id"]
    # The AI should remember the name from previous conversation


def test_ask_endpoint_validation():
    """Test request validation."""
    # Empty query should fail
    response = client.post(
        "/api/ask",
        json={"query": ""}
    )
    assert response.status_code == 422  # Validation error


def test_ask_endpoint_company_query():
    """Test query that should trigger document search."""
    response = client.post(
        "/api/ask",
        json={"query": "What is the company's leave policy?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    # If documents are loaded, should have sources
    if data.get("sources"):
        assert len(data["sources"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
