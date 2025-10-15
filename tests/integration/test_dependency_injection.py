"""
Integration tests for dependency injection in realistic usage scenarios.

Tests demonstrate dependency injection patterns in FastAPI endpoints and verify
that dependencies can be overridden for testing.
"""

import logging
from typing import Annotated
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from mcp_server.config import Settings
from mcp_server.core.dependencies import (
    HttpClientDep,
    LoggerDep,
    SessionDep,
    SettingsDep,
    close_db_session_maker,
    close_http_client,
    get_db_session,
    get_http_client,
    get_logger,
    get_settings,
    initialize_db_session_maker,
    initialize_http_client,
)


@pytest.mark.integration
@pytest.mark.asyncio
class TestDependencyInjectionInEndpoints:
    """Test dependency injection in FastAPI endpoint handlers."""

    async def test_settings_dependency_injection_in_endpoint(self) -> None:
        """Test that Settings can be injected into FastAPI endpoint."""
        # Create a test FastAPI app with endpoint using dependency injection
        test_app = FastAPI()

        @test_app.get("/test-settings")
        async def test_endpoint(settings: SettingsDep) -> dict[str, str]:
            return {"app_name": settings.app_name, "version": settings.app_version}

        # Test the endpoint
        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.get("/test-settings")
            assert response.status_code == 200
            data = response.json()
            assert data["app_name"] == "AI Agent MCP Server"
            assert data["version"] == "0.1.0"

    async def test_logger_dependency_injection_in_endpoint(self) -> None:
        """Test that Logger can be injected into FastAPI endpoint."""
        test_app = FastAPI()

        @test_app.get("/test-logger")
        async def test_endpoint(logger: LoggerDep) -> dict[str, str]:
            logger.info("Test log message")
            return {"logger_name": logger.name}

        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.get("/test-logger")
            assert response.status_code == 200
            data = response.json()
            assert data["logger_name"] == "mcp_server"

    async def test_http_client_dependency_injection_in_endpoint(self) -> None:
        """Test that HTTP client can be injected into FastAPI endpoint."""
        # Initialize HTTP client
        await initialize_http_client()

        try:
            test_app = FastAPI()

            @test_app.get("/test-http-client")
            async def test_endpoint(client: HttpClientDep) -> dict[str, str]:
                return {"client_type": type(client).__name__}

            async with AsyncClient(
                transport=ASGITransport(app=test_app), base_url="http://test"
            ) as client:
                response = await client.get("/test-http-client")
                assert response.status_code == 200
                data = response.json()
                assert data["client_type"] == "AsyncClient"
        finally:
            await close_http_client()

    async def test_database_session_dependency_injection_in_endpoint(self) -> None:
        """Test that database session can be injected into FastAPI endpoint."""
        # Mock the database engine and session maker
        with patch("mcp_server.core.dependencies.create_async_engine") as mock_engine:
            mock_engine_instance = MagicMock()
            mock_engine.return_value = mock_engine_instance

            mock_session = AsyncMock(spec=AsyncSession)
            mock_session.commit = AsyncMock()
            mock_session.rollback = AsyncMock()

            with patch("mcp_server.core.dependencies.async_sessionmaker") as mock_session_maker:
                mock_session_maker.return_value = lambda: mock_session

                await initialize_db_session_maker()

                try:
                    test_app = FastAPI()

                    @test_app.get("/test-db-session")
                    async def test_endpoint(session: SessionDep) -> dict[str, str]:
                        return {"session_type": type(session).__name__}

                    async with AsyncClient(
                        transport=ASGITransport(app=test_app), base_url="http://test"
                    ) as client:
                        response = await client.get("/test-db-session")
                        assert response.status_code == 200
                        data = response.json()
                        # AsyncMock type name
                        assert "Mock" in data["session_type"]
                finally:
                    await close_db_session_maker()


@pytest.mark.integration
@pytest.mark.asyncio
class TestDependencyOverrideForTesting:
    """Test dependency override mechanism for testing."""

    async def test_settings_dependency_override(self) -> None:
        """Test that Settings dependency can be overridden for testing."""
        test_app = FastAPI()

        @test_app.get("/test-override")
        async def test_endpoint(settings: SettingsDep) -> dict[str, str]:
            return {"app_name": settings.app_name}

        # Create mock settings
        mock_settings = Settings(app_name="Test App Override", app_version="99.99.99")

        # Override dependency
        test_app.dependency_overrides[get_settings] = lambda: mock_settings

        try:
            async with AsyncClient(
                transport=ASGITransport(app=test_app), base_url="http://test"
            ) as client:
                response = await client.get("/test-override")
                assert response.status_code == 200
                data = response.json()
                assert data["app_name"] == "Test App Override"
        finally:
            test_app.dependency_overrides.clear()

    async def test_logger_dependency_override(self) -> None:
        """Test that Logger dependency can be overridden for testing."""
        test_app = FastAPI()

        @test_app.get("/test-logger-override")
        async def test_endpoint(logger: LoggerDep) -> dict[str, str]:
            logger.info("Test message")
            return {"logger_name": logger.name}

        # Create mock logger
        mock_logger = logging.getLogger("test_override_logger")

        # Override dependency
        test_app.dependency_overrides[get_logger] = lambda: mock_logger

        try:
            async with AsyncClient(
                transport=ASGITransport(app=test_app), base_url="http://test"
            ) as client:
                response = await client.get("/test-logger-override")
                assert response.status_code == 200
                data = response.json()
                assert data["logger_name"] == "test_override_logger"
        finally:
            test_app.dependency_overrides.clear()

    async def test_http_client_dependency_override(self) -> None:
        """Test that HTTP client dependency can be overridden for testing."""
        # Initialize real HTTP client first
        await initialize_http_client()

        try:
            test_app = FastAPI()

            @test_app.get("/test-http-override")
            async def test_endpoint(client: HttpClientDep) -> dict[str, bool]:
                return {"is_mock": hasattr(client, "_mock_marker")}

            # Create mock HTTP client with marker
            mock_client = AsyncMock(spec=httpx.AsyncClient)
            mock_client._mock_marker = True  # type: ignore[attr-defined]

            # Override dependency
            test_app.dependency_overrides[get_http_client] = lambda: mock_client

            try:
                async with AsyncClient(
                    transport=ASGITransport(app=test_app), base_url="http://test"
                ) as client:
                    response = await client.get("/test-http-override")
                    assert response.status_code == 200
                    data = response.json()
                    assert data["is_mock"] is True
            finally:
                test_app.dependency_overrides.clear()
        finally:
            await close_http_client()

    async def test_database_session_dependency_override(self) -> None:
        """Test that database session dependency can be overridden for testing."""
        with patch("mcp_server.core.dependencies.create_async_engine") as mock_engine:
            mock_engine_instance = MagicMock()
            mock_engine.return_value = mock_engine_instance

            mock_session = AsyncMock(spec=AsyncSession)
            mock_session.commit = AsyncMock()

            with patch("mcp_server.core.dependencies.async_sessionmaker") as mock_session_maker:
                mock_session_maker.return_value = lambda: mock_session

                await initialize_db_session_maker()

                try:
                    test_app = FastAPI()

                    @test_app.get("/test-session-override")
                    async def test_endpoint(session: SessionDep) -> dict[str, bool]:
                        return {"is_mock": hasattr(session, "_test_marker")}

                    # Create mock session with marker
                    override_session = AsyncMock(spec=AsyncSession)
                    override_session._test_marker = True  # type: ignore[attr-defined]
                    override_session.commit = AsyncMock()
                    override_session.rollback = AsyncMock()

                    async def mock_get_session():  # type: ignore[no-untyped-def]
                        yield override_session
                        await override_session.commit()

                    # Override dependency
                    test_app.dependency_overrides[get_db_session] = mock_get_session

                    try:
                        async with AsyncClient(
                            transport=ASGITransport(app=test_app), base_url="http://test"
                        ) as client:
                            response = await client.get("/test-session-override")
                            assert response.status_code == 200
                            data = response.json()
                            assert data["is_mock"] is True
                    finally:
                        test_app.dependency_overrides.clear()
                finally:
                    await close_db_session_maker()


@pytest.mark.integration
@pytest.mark.asyncio
class TestMultipleDependenciesInSingleEndpoint:
    """Test injecting multiple dependencies into single endpoint."""

    async def test_multiple_dependencies_injection(self) -> None:
        """Test that multiple dependencies can be injected into single endpoint."""
        await initialize_http_client()

        try:
            test_app = FastAPI()

            @test_app.get("/test-multiple")
            async def test_endpoint(
                settings: SettingsDep,
                logger: LoggerDep,
                client: HttpClientDep,
            ) -> dict[str, str]:
                logger.info("Multiple dependencies injected")
                return {
                    "app_name": settings.app_name,
                    "logger_name": logger.name,
                    "client_type": type(client).__name__,
                }

            async with AsyncClient(
                transport=ASGITransport(app=test_app), base_url="http://test"
            ) as client:
                response = await client.get("/test-multiple")
                assert response.status_code == 200
                data = response.json()
                assert data["app_name"] == "AI Agent MCP Server"
                assert data["logger_name"] == "mcp_server"
                assert data["client_type"] == "AsyncClient"
        finally:
            await close_http_client()

    async def test_nested_dependencies(self) -> None:
        """Test that dependencies can depend on other dependencies."""
        test_app = FastAPI()

        # Define a service that depends on settings and logger
        class ExampleService:
            def __init__(self, settings: Settings, logger: logging.Logger):
                self.settings = settings
                self.logger = logger

            def get_info(self) -> dict[str, str]:
                self.logger.info("Service method called")
                return {"app": self.settings.app_name}

        def get_example_service(
            settings: SettingsDep,
            logger: LoggerDep,
        ) -> ExampleService:
            return ExampleService(settings, logger)

        example_service_dep = Annotated[ExampleService, Depends(get_example_service)]

        @test_app.get("/test-nested")
        async def test_endpoint(
            service: example_service_dep,  # type: ignore[valid-type]
        ) -> dict[str, str]:
            return service.get_info()

        async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
        ) as client:
            response = await client.get("/test-nested")
            assert response.status_code == 200
            data = response.json()
            assert data["app"] == "AI Agent MCP Server"
