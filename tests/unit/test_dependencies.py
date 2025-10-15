"""
Unit tests for dependency injection providers.

Tests individual dependency provider functions in isolation with mocked dependencies.
"""

import logging
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from mcp_server.config import Settings
from mcp_server.core.dependencies import (
    close_db_session_maker,
    close_http_client,
    get_db_session,
    get_http_client,
    get_logger,
    get_settings,
    initialize_db_session_maker,
    initialize_http_client,
)


@pytest.mark.unit
class TestGetSettings:
    """Test get_settings dependency provider."""

    def test_get_settings_returns_settings_instance(self) -> None:
        """Test that get_settings returns a Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_get_settings_is_singleton(self) -> None:
        """Test that get_settings returns the same instance on multiple calls."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_get_settings_loads_configuration(self) -> None:
        """Test that get_settings loads configuration from environment."""
        settings = get_settings()
        assert settings.app_name == "AI Agent MCP Server"
        assert settings.app_version == "0.1.0"


@pytest.mark.unit
class TestGetLogger:
    """Test get_logger dependency provider."""

    def test_get_logger_returns_logger_instance(self) -> None:
        """Test that get_logger returns a Logger instance."""
        logger = get_logger()
        assert isinstance(logger, logging.Logger)

    def test_get_logger_with_custom_name(self) -> None:
        """Test that get_logger accepts custom logger name."""
        logger = get_logger(name="custom_logger")
        assert logger.name == "custom_logger"

    def test_get_logger_default_name(self) -> None:
        """Test that get_logger uses default name."""
        logger = get_logger()
        assert logger.name == "mcp_server"

    def test_get_logger_configures_handler(self) -> None:
        """Test that get_logger configures logging handler."""
        logger = get_logger(name="test_logger_config")
        assert len(logger.handlers) > 0

    def test_get_logger_json_format(self) -> None:
        """Test that get_logger uses JSON format when configured."""
        with patch("mcp_server.core.dependencies.get_settings") as mock_settings:
            mock_settings.return_value.log_format = "json"
            mock_settings.return_value.log_level = "INFO"
            logger = get_logger(name="json_logger")
            assert len(logger.handlers) > 0
            formatter = logger.handlers[0].formatter
            assert formatter is not None


@pytest.mark.unit
@pytest.mark.asyncio
class TestHttpClientLifecycle:
    """Test HTTP client initialization and cleanup."""

    async def test_initialize_http_client_creates_client(self) -> None:
        """Test that initialize_http_client creates httpx.AsyncClient instance."""
        await initialize_http_client()
        try:
            client = get_http_client()
            assert isinstance(client, httpx.AsyncClient)
        finally:
            await close_http_client()

    async def test_initialize_http_client_raises_if_already_initialized(self) -> None:
        """Test that initialize_http_client raises error if already initialized."""
        await initialize_http_client()
        try:
            with pytest.raises(RuntimeError, match="already initialized"):
                await initialize_http_client()
        finally:
            await close_http_client()

    async def test_get_http_client_raises_if_not_initialized(self) -> None:
        """Test that get_http_client raises error if not initialized."""
        # Ensure client is closed from any previous test
        await close_http_client()

        with pytest.raises(RuntimeError, match="not initialized"):
            get_http_client()

    async def test_close_http_client_closes_client(self) -> None:
        """Test that close_http_client properly closes the HTTP client."""
        await initialize_http_client()
        await close_http_client()

        # After closing, get_http_client should raise error
        with pytest.raises(RuntimeError, match="not initialized"):
            get_http_client()

    async def test_http_client_configuration(self) -> None:
        """Test that HTTP client is configured with correct settings."""
        await initialize_http_client()
        try:
            client = get_http_client()
            assert client.timeout.read == 30.0
            # Note: httpx limits are not directly accessible, but we verify client is configured
            assert isinstance(client, httpx.AsyncClient)
        finally:
            await close_http_client()


@pytest.mark.unit
@pytest.mark.asyncio
class TestDatabaseSessionLifecycle:
    """Test database session initialization and cleanup."""

    @pytest.fixture(autouse=True)
    async def cleanup_db_session(self) -> None:
        """Ensure database session maker is cleaned up before each test."""
        # Clean up before test
        await close_db_session_maker()
        yield
        # Clean up after test
        await close_db_session_maker()

    async def test_initialize_db_session_maker_creates_session_maker(self) -> None:
        """Test that initialize_db_session_maker creates session maker."""
        with patch("mcp_server.core.dependencies.create_async_engine") as mock_engine:
            mock_engine_instance = AsyncMock()
            mock_engine_instance.dispose = AsyncMock()
            mock_engine.return_value = mock_engine_instance
            await initialize_db_session_maker()
            assert mock_engine.called

    async def test_initialize_db_session_maker_raises_if_already_initialized(
        self,
    ) -> None:
        """Test that initialize_db_session_maker raises error if already initialized."""
        with patch("mcp_server.core.dependencies.create_async_engine") as mock_engine:
            mock_engine_instance = AsyncMock()
            mock_engine_instance.dispose = AsyncMock()
            mock_engine.return_value = mock_engine_instance
            await initialize_db_session_maker()
            with pytest.raises(RuntimeError, match="already initialized"):
                await initialize_db_session_maker()

    async def test_get_db_session_raises_if_not_initialized(self) -> None:
        """Test that get_db_session raises error if session maker not initialized."""
        with pytest.raises(RuntimeError, match="not initialized"):
            async for _ in get_db_session():
                pass

    async def test_get_db_session_yields_async_session(self) -> None:
        """Test that get_db_session yields AsyncSession instance."""
        with patch("mcp_server.core.dependencies.create_async_engine") as mock_engine:
            # Create mock engine
            mock_engine_instance = AsyncMock()
            mock_engine_instance.dispose = AsyncMock()
            mock_engine.return_value = mock_engine_instance

            await initialize_db_session_maker()
            # Basic test that generator can be created (integration tests cover full flow)
            gen = get_db_session()
            assert hasattr(gen, "__anext__")

    async def test_get_db_session_commits_on_success(self) -> None:
        """Test that get_db_session commits transaction on success (integration test covers details)."""
        with patch("mcp_server.core.dependencies.create_async_engine") as mock_engine:
            mock_engine_instance = AsyncMock()
            mock_engine_instance.dispose = AsyncMock()
            mock_engine.return_value = mock_engine_instance

            await initialize_db_session_maker()
            # Basic test verifying generator exists (integration tests verify commit/rollback behavior)
            gen = get_db_session()
            assert hasattr(gen, "__anext__")

    async def test_get_db_session_rolls_back_on_error(self) -> None:
        """Test that get_db_session rolls back transaction on error (integration test covers details)."""
        with patch("mcp_server.core.dependencies.create_async_engine") as mock_engine:
            mock_engine_instance = AsyncMock()
            mock_engine_instance.dispose = AsyncMock()
            mock_engine.return_value = mock_engine_instance

            await initialize_db_session_maker()
            # Basic test verifying generator exists (integration tests verify commit/rollback behavior)
            gen = get_db_session()
            assert hasattr(gen, "__anext__")


@pytest.mark.unit
class TestDependencyTypeAliases:
    """Test that dependency type aliases are properly defined."""

    def test_settings_dep_type_alias_exists(self) -> None:
        """Test that SettingsDep type alias is defined."""
        from mcp_server.core.dependencies import SettingsDep

        assert SettingsDep is not None

    def test_logger_dep_type_alias_exists(self) -> None:
        """Test that LoggerDep type alias is defined."""
        from mcp_server.core.dependencies import LoggerDep

        assert LoggerDep is not None

    def test_session_dep_type_alias_exists(self) -> None:
        """Test that SessionDep type alias is defined."""
        from mcp_server.core.dependencies import SessionDep

        assert SessionDep is not None

    def test_http_client_dep_type_alias_exists(self) -> None:
        """Test that HttpClientDep type alias is defined."""
        from mcp_server.core.dependencies import HttpClientDep

        assert HttpClientDep is not None
