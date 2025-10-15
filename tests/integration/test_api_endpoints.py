"""
Integration tests for FastAPI endpoints.

These tests validate end-to-end API behavior including request/response handling,
HTTP status codes, and async endpoint functionality.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# ====================
# Synchronous Endpoint Tests
# ====================


@pytest.mark.integration
def test_should_return_ok_status_from_health_endpoint(client: TestClient):
    """Test health endpoint returns 200 OK with correct response structure."""
    # Arrange - client fixture provides TestClient
    # Act - make GET request to health endpoint
    response = client.get("/health")

    # Assert - verify response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "uptime_seconds" in data
    assert "timestamp" in data


@pytest.mark.integration
def test_should_have_correct_content_type_from_health_endpoint(client: TestClient):
    """Test health endpoint returns JSON content type."""
    # Arrange
    # Act
    response = client.get("/health")

    # Assert
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]


@pytest.mark.integration
def test_should_return_consistent_response_on_multiple_calls(client: TestClient):
    """Test health endpoint returns consistent responses across multiple calls."""
    # Arrange
    # Act - make multiple requests
    response1 = client.get("/health")
    response2 = client.get("/health")
    response3 = client.get("/health")

    # Assert - all responses identical status and version
    assert response1.status_code == response2.status_code == response3.status_code == 200
    data1 = response1.json()
    data2 = response2.json()
    data3 = response3.json()
    # Status and version should be identical
    assert data1["status"] == data2["status"] == data3["status"]
    assert data1["version"] == data2["version"] == data3["version"]


# ====================
# Async Endpoint Tests
# ====================


@pytest.mark.integration
@pytest.mark.asyncio
async def test_should_return_ok_status_from_health_endpoint_async(async_client: AsyncClient):
    """Test health endpoint with async client (demonstrates async test pattern)."""
    # Arrange - async_client fixture provides AsyncClient
    # Act - make async GET request
    response = await async_client.get("/health")

    # Assert - verify response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "uptime_seconds" in data


@pytest.mark.integration
@pytest.mark.asyncio
async def test_should_handle_concurrent_requests_async(async_client: AsyncClient):
    """Test FastAPI handles concurrent async requests correctly."""
    # Arrange
    import asyncio

    # Act - make 5 concurrent requests
    tasks = [async_client.get("/health") for _ in range(5)]
    responses = await asyncio.gather(*tasks)

    # Assert - all requests succeeded
    assert len(responses) == 5
    for response in responses:
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


# ====================
# Error Handling Tests
# ====================


@pytest.mark.integration
def test_should_return_404_for_nonexistent_endpoint(client: TestClient):
    """Test FastAPI returns 404 for undefined routes."""
    # Arrange
    # Act
    response = client.get("/nonexistent-endpoint")

    # Assert
    assert response.status_code == 404
    assert "application/json" in response.headers["content-type"]


@pytest.mark.integration
def test_should_return_405_for_unsupported_http_method(client: TestClient):
    """Test FastAPI returns 405 for unsupported HTTP methods on defined routes."""
    # Arrange - health endpoint only supports GET
    # Act - try POST on GET-only endpoint
    response = client.post("/health")

    # Assert
    assert response.status_code == 405
    assert "application/json" in response.headers["content-type"]


# ====================
# Application Metadata Tests
# ====================


@pytest.mark.integration
def test_should_provide_openapi_schema(client: TestClient):
    """Test FastAPI provides OpenAPI schema at /openapi.json."""
    # Arrange
    # Act
    response = client.get("/openapi.json")

    # Assert
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert schema["info"]["title"] == "AI Agent MCP Server"
    assert schema["info"]["version"] == "0.1.0"


@pytest.mark.integration
def test_should_provide_api_documentation(client: TestClient):
    """Test FastAPI provides interactive API documentation at /docs."""
    # Arrange
    # Act
    response = client.get("/docs")

    # Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # Verify Swagger UI is served
    assert b"swagger-ui" in response.content.lower()


@pytest.mark.integration
def test_should_provide_redoc_documentation(client: TestClient):
    """Test FastAPI provides ReDoc documentation at /redoc."""
    # Arrange
    # Act
    response = client.get("/redoc")

    # Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # Verify ReDoc is served
    assert b"redoc" in response.content.lower()


# ====================
# Async Pattern Demonstration Tests
# ====================


@pytest.mark.integration
@pytest.mark.asyncio
async def test_should_demonstrate_async_context_manager_pattern(async_client: AsyncClient):
    """
    Test demonstrating async context manager pattern for async_client fixture.

    This pattern ensures proper cleanup of async resources.
    """
    # Arrange - async_client is already in async context from fixture
    # Act - make multiple async requests in sequence
    response1 = await async_client.get("/health")
    response2 = await async_client.get("/openapi.json")

    # Assert - both requests succeeded
    assert response1.status_code == 200
    assert response2.status_code == 200


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_demonstrate_timeout_handling(async_client: AsyncClient):
    """
    Test demonstrating timeout handling in async tests.

    Marked as 'slow' to allow selective test execution (pytest -m "not slow").
    """
    # Arrange
    import asyncio

    # Act - make request with explicit timeout
    try:
        response = await asyncio.wait_for(
            async_client.get("/health"),
            timeout=5.0,  # 5 second timeout
        )
        # Assert - request completed within timeout
        assert response.status_code == 200
    except TimeoutError:
        pytest.fail("Request timed out after 5 seconds")


# ====================
# Response Validation Tests
# ====================


@pytest.mark.integration
def test_should_validate_response_schema_structure(client: TestClient):
    """Test response matches expected schema structure."""
    # Arrange
    expected_keys = {"status", "version", "uptime_seconds", "timestamp"}

    # Act
    response = client.get("/health")
    data = response.json()

    # Assert - validate structure
    assert response.status_code == 200
    assert set(data.keys()) == expected_keys
    assert isinstance(data["status"], str)
    assert isinstance(data["version"], str)
    assert isinstance(data["uptime_seconds"], int | float)
    assert isinstance(data["timestamp"], str)


@pytest.mark.integration
def test_should_validate_response_field_values(client: TestClient):
    """Test response field values match expected constraints."""
    # Arrange
    valid_statuses = {"healthy", "degraded", "unhealthy"}

    # Act
    response = client.get("/health")
    data = response.json()

    # Assert - validate field constraints
    assert data["status"] in valid_statuses
    assert len(data["version"]) > 0
    assert data["uptime_seconds"] >= 0
    assert "T" in data["timestamp"]  # ISO 8601 format
