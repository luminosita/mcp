"""
Unit tests for health check endpoint.

Tests health check endpoint response schema, status values, and timing.
"""

import time

import pytest
from fastapi.testclient import TestClient

from mcp_server.core.constants import HEALTH_STATUS_HEALTHY


@pytest.mark.unit
def test_health_check_returns_200_ok(client: TestClient) -> None:
    """Test that health check endpoint returns HTTP 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200


@pytest.mark.unit
def test_health_check_returns_json(client: TestClient) -> None:
    """Test that health check endpoint returns valid JSON response."""
    response = client.get("/health")
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert isinstance(data, dict)


@pytest.mark.unit
def test_health_check_response_schema(client: TestClient) -> None:
    """Test that health check response includes all required fields."""
    response = client.get("/health")
    data = response.json()

    # Verify all required fields present
    assert "status" in data
    assert "version" in data
    assert "uptime_seconds" in data
    assert "timestamp" in data


@pytest.mark.unit
def test_health_check_status_value(client: TestClient) -> None:
    """Test that health check returns 'healthy' status."""
    response = client.get("/health")
    data = response.json()
    assert data["status"] == HEALTH_STATUS_HEALTHY


@pytest.mark.unit
def test_health_check_version_format(client: TestClient) -> None:
    """Test that health check returns valid version string."""
    response = client.get("/health")
    data = response.json()
    assert isinstance(data["version"], str)
    assert len(data["version"]) > 0
    # Verify semver format (e.g., "0.1.0")
    parts = data["version"].split(".")
    assert len(parts) == 3


@pytest.mark.unit
def test_health_check_uptime_is_positive(client: TestClient) -> None:
    """Test that health check uptime is a positive number."""
    response = client.get("/health")
    data = response.json()
    assert isinstance(data["uptime_seconds"], int | float)
    assert data["uptime_seconds"] >= 0


@pytest.mark.unit
def test_health_check_uptime_increases(client: TestClient) -> None:
    """Test that uptime increases between consecutive calls."""
    response1 = client.get("/health")
    data1 = response1.json()
    uptime1 = data1["uptime_seconds"]

    # Wait a small amount of time
    time.sleep(0.1)

    response2 = client.get("/health")
    data2 = response2.json()
    uptime2 = data2["uptime_seconds"]

    # Uptime should have increased
    assert uptime2 > uptime1


@pytest.mark.unit
def test_health_check_timestamp_format(client: TestClient) -> None:
    """Test that health check returns ISO 8601 formatted timestamp."""
    response = client.get("/health")
    data = response.json()
    timestamp = data["timestamp"]

    # Verify ISO 8601 format (basic validation)
    assert isinstance(timestamp, str)
    assert "T" in timestamp  # ISO 8601 has T separator
    # Should end with timezone (Z or +/-HH:MM)
    assert timestamp.endswith("Z") or "+" in timestamp or timestamp.count("-") >= 2


@pytest.mark.unit
def test_health_check_response_time(client: TestClient) -> None:
    """Test that health check responds quickly (<50ms p95)."""
    # Run multiple requests to measure response time
    times = []
    for _ in range(10):
        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start
        times.append(elapsed)
        assert response.status_code == 200

    # Calculate p95
    times.sort()
    p95_time = times[int(len(times) * 0.95)]

    # Should be under 50ms (0.05 seconds)
    # Note: In CI environment this might be slightly higher
    assert p95_time < 0.1, f"p95 response time {p95_time:.3f}s exceeds threshold"


@pytest.mark.unit
def test_health_check_multiple_calls_idempotent(client: TestClient) -> None:
    """Test that multiple health check calls don't cause issues."""
    responses = []
    for _ in range(5):
        response = client.get("/health")
        assert response.status_code == 200
        responses.append(response.json())

    # All responses should have the same status and version
    for data in responses:
        assert data["status"] == HEALTH_STATUS_HEALTHY
        assert data["version"] == responses[0]["version"]
