"""
Pytest configuration and shared fixtures.

Defines fixtures and test configuration for the entire test suite.
"""

from collections.abc import AsyncGenerator, Callable, Generator
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from mcp_server.main import app as fastapi_app

# ====================
# FastAPI Test Clients
# ====================


@pytest.fixture
def app() -> FastAPI:
    """
    Provide the FastAPI application instance for testing.

    Returns:
        FastAPI application instance
    """
    return fastapi_app


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    """
    Provide a synchronous FastAPI TestClient for testing sync endpoints.

    Use this for testing synchronous endpoints or when you don't need async features.

    Args:
        app: FastAPI application instance

    Yields:
        TestClient instance

    Example:
        def test_root_endpoint(client):
            response = client.get("/")
            assert response.status_code == 200
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an async FastAPI client for testing async endpoints.

    Use this for testing async endpoints, SSE streams, or WebSocket connections.

    Args:
        app: FastAPI application instance

    Yields:
        AsyncClient instance

    Example:
        @pytest.mark.asyncio
        async def test_async_endpoint(async_client):
            response = await async_client.get("/")
            assert response.status_code == 200
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# ====================
# Database Fixtures
# ====================


@pytest.fixture
def db_session() -> Generator[Mock, None, None]:
    """
    Provide a mocked database session for testing.

    Use this for unit tests that need database interaction without
    connecting to a real database.

    Yields:
        Mock database session

    Example:
        def test_user_repository(db_session):
            db_session.query.return_value.filter.return_value.first.return_value = User(id=1)
            user = user_repo.get_by_id(db_session, 1)
            assert user.id == 1
    """
    session = Mock()
    yield session
    session.reset_mock()


@pytest.fixture
async def async_db_session() -> AsyncGenerator[AsyncMock, None]:
    """
    Provide a mocked async database session for testing.

    Use this for async database operations in services and repositories.

    Yields:
        AsyncMock database session

    Example:
        @pytest.mark.asyncio
        async def test_async_repository(async_db_session):
            async_db_session.execute.return_value.scalar.return_value = User(id=1)
            user = await user_repo.get_by_id(async_db_session, 1)
            assert user.id == 1
    """
    session = AsyncMock()
    yield session


# ====================
# Mock External Services
# ====================


@pytest.fixture
def mock_http_client() -> Mock:
    """
    Provide a mocked HTTP client for testing external API calls.

    Use this to mock httpx.AsyncClient or other HTTP clients.

    Returns:
        Mock HTTP client

    Example:
        def test_external_api_call(mock_http_client):
            mock_http_client.get.return_value.json.return_value = {"data": "value"}
            service = ExternalService(client=mock_http_client)
            result = service.fetch_data()
            assert result["data"] == "value"
    """
    return Mock()


@pytest.fixture
def mock_async_http_client() -> AsyncMock:
    """
    Provide a mocked async HTTP client for testing external API calls.

    Use this to mock async HTTP operations with httpx.AsyncClient.

    Returns:
        AsyncMock HTTP client

    Example:
        @pytest.mark.asyncio
        async def test_async_external_api(mock_async_http_client):
            mock_response = AsyncMock()
            mock_response.json.return_value = {"data": "value"}
            mock_async_http_client.get.return_value = mock_response
            service = ExternalService(client=mock_async_http_client)
            result = await service.fetch_data()
            assert result["data"] == "value"
    """
    return AsyncMock()


@pytest.fixture
def mock_jira_client() -> Mock:
    """
    Provide a mocked JIRA client for testing JIRA integration.

    Use this to mock JIRA API operations without connecting to real JIRA instance.

    Returns:
        Mock JIRA client

    Example:
        def test_jira_issue_creation(mock_jira_client):
            mock_jira_client.create_issue.return_value = {"id": "PROJ-123"}
            result = jira_service.create_issue(mock_jira_client, {...})
            assert result["id"] == "PROJ-123"
    """
    client = Mock()
    client.create_issue = Mock(return_value={"id": "PROJ-123", "key": "PROJ-123"})
    client.get_issue = Mock(return_value={"id": "PROJ-123", "fields": {"summary": "Test"}})
    client.search_issues = Mock(return_value=[])
    return client


@pytest.fixture
def mock_ci_cd_client() -> Mock:
    """
    Provide a mocked CI/CD client for testing CI/CD integration.

    Use this to mock GitHub Actions, Jenkins, or other CI/CD API operations.

    Returns:
        Mock CI/CD client

    Example:
        def test_trigger_build(mock_ci_cd_client):
            mock_ci_cd_client.trigger_workflow.return_value = {"run_id": 123}
            result = ci_service.trigger_build(mock_ci_cd_client, "main")
            assert result["run_id"] == 123
    """
    client = Mock()
    client.trigger_workflow = Mock(return_value={"run_id": 123})
    client.get_workflow_run = Mock(return_value={"status": "completed", "conclusion": "success"})
    return client


# ====================
# Sample Data Fixtures
# ====================


@pytest.fixture
def sample_user_data() -> dict[str, Any]:
    """
    Provide sample user data for testing.

    Returns:
        Dictionary with sample user data

    Example:
        def test_user_creation(sample_user_data):
            user = User(**sample_user_data)
            assert user.email == "test@example.com"
    """
    return {
        "id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "is_active": True,
    }


@pytest.fixture
def sample_tool_request() -> dict[str, Any]:
    """
    Provide sample MCP tool request data for testing.

    Returns:
        Dictionary with sample tool request data

    Example:
        def test_tool_execution(sample_tool_request):
            result = tool_executor.execute(sample_tool_request)
            assert result["status"] == "success"
    """
    return {
        "tool_name": "search_jira",
        "parameters": {
            "query": "project = TEST",
            "max_results": 10,
        },
    }


@pytest.fixture
def sample_tool_response() -> dict[str, Any]:
    """
    Provide sample MCP tool response data for testing.

    Returns:
        Dictionary with sample tool response data

    Example:
        def test_tool_response_validation(sample_tool_response):
            assert sample_tool_response["status"] == "success"
            assert "result" in sample_tool_response
    """
    return {
        "status": "success",
        "result": {
            "issues": [
                {"key": "TEST-1", "summary": "Test issue"},
                {"key": "TEST-2", "summary": "Another test issue"},
            ],
        },
    }


# ====================
# Fixture Factories
# ====================


@pytest.fixture
def user_factory() -> Callable[..., dict[str, Any]]:
    """
    Provide a factory function to create user instances with custom data.

    Returns:
        Factory function that creates user dictionaries

    Example:
        def test_multiple_users(user_factory):
            user1 = user_factory(email="user1@example.com")
            user2 = user_factory(email="user2@example.com")
            assert user1["email"] != user2["email"]
    """

    def _create_user(
        id: int = 1,
        email: str = "test@example.com",
        username: str = "testuser",
        full_name: str = "Test User",
        is_active: bool = True,
    ) -> dict[str, Any]:
        return {
            "id": id,
            "email": email,
            "username": username,
            "full_name": full_name,
            "is_active": is_active,
        }

    return _create_user


# ====================
# Example Tool Fixtures
# ====================


@pytest.fixture
def sample_greeting_input() -> dict[str, Any]:
    """
    Provide sample greeting tool input data for testing.

    Returns:
        Dictionary with sample greeting input data

    Example:
        def test_greeting_tool(sample_greeting_input):
            params = GreetingInput(**sample_greeting_input)
            assert params.name == "Alice"
    """
    return {
        "name": "Alice",
        "style": "casual",
        "message": None,
    }


@pytest.fixture
def sample_greeting_input_with_message() -> dict[str, Any]:
    """
    Provide sample greeting tool input with custom message.

    Returns:
        Dictionary with greeting input including custom message

    Example:
        def test_greeting_with_message(sample_greeting_input_with_message):
            params = GreetingInput(**sample_greeting_input_with_message)
            assert params.message is not None
    """
    return {
        "name": "Bob",
        "style": "formal",
        "message": "Hope you have a wonderful day",
    }


@pytest.fixture
def mock_settings() -> Mock:
    """
    Provide a mocked Settings instance for testing.

    Returns:
        Mock Settings object with common attributes

    Example:
        def test_tool_with_settings(mock_settings):
            result = tool_function(params, mock_settings, logger)
            assert result.metadata["app_name"] == "TestApp"
    """
    settings = Mock()
    settings.app_name = "TestApp"
    settings.app_version = "1.0.0"
    settings.environment = "test"
    settings.log_level = "INFO"
    return settings


@pytest.fixture
def mock_logger() -> Mock:
    """
    Provide a mocked logger for testing.

    Returns:
        Mock logger with common logging methods

    Example:
        def test_tool_logging(mock_logger):
            tool_function(params, settings, mock_logger)
            mock_logger.info.assert_called()
    """
    logger = Mock()
    logger.info = Mock()
    logger.error = Mock()
    logger.warning = Mock()
    logger.exception = Mock()
    return logger
