"""
Dependency injection providers for FastAPI application.

Provides injectable dependencies for MCP tools to access shared services:
- Settings: Application configuration (singleton)
- Logger: Structured logging with request context
- Database Session: SQLAlchemy async sessions with automatic cleanup
- HTTP Client: Shared httpx client with connection pooling

All dependencies use FastAPI's Depends() mechanism for type-safe injection.
"""

import logging
from collections.abc import AsyncGenerator
from typing import Annotated

import httpx
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from mcp_server.config import Settings

# Type aliases for dependency injection (improves readability and type safety)
SettingsDep = Annotated[Settings, Depends(lambda: get_settings())]
LoggerDep = Annotated[logging.Logger, Depends(lambda: get_logger())]
SessionDep = Annotated[AsyncSession, Depends(lambda: get_db_session())]
HttpClientDep = Annotated[httpx.AsyncClient, Depends(lambda: get_http_client())]


# Module-level variables for application-scoped resources
_http_client: httpx.AsyncClient | None = None
_session_maker: async_sessionmaker[AsyncSession] | None = None


def get_settings() -> Settings:
    """
    Get application settings (singleton).

    Returns the same Settings instance across all invocations within the application
    lifecycle. Settings are loaded from environment variables and .env file at module
    import time in config.py.

    Lifecycle: Application-scoped (singleton)

    Returns:
        Settings: Validated application configuration

    Example:
        ```python
        async def some_tool(settings: SettingsDep) -> dict:
            app_name = settings.app_name
            return {"app": app_name}
        ```
    """
    from mcp_server.config import settings

    return settings


def get_logger(name: str = "mcp_server") -> logging.Logger:
    """
    Get structured logger instance.

    Returns a configured logger with structured logging support. Logger includes
    contextual information (timestamp, log level, module name) and can write to
    configured output (stdout for development, file/service for production).

    Lifecycle: Request-scoped (new logger per request, or reuse if name matches)

    Args:
        name: Logger name (defaults to "mcp_server")

    Returns:
        logging.Logger: Configured logger instance

    Example:
        ```python
        async def some_tool(logger: LoggerDep) -> dict:
            logger.info("Tool invoked", extra={"tool": "some_tool"})
            return {"status": "success"}
        ```
    """
    logger = logging.getLogger(name)

    # Configure logger if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        settings = get_settings()

        # Use JSON format for structured logging in production
        if settings.log_format == "json":
            formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"name": "%(name)s", "message": "%(message)s"}'
            )
        else:
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    return logger


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session with automatic cleanup.

    Yields an active SQLAlchemy AsyncSession instance. The session is automatically
    closed after the request completes (including error cases). Database connections
    are reused from a connection pool for performance.

    Lifecycle: Request-scoped (new session per request, auto-cleanup)

    Yields:
        AsyncSession: Active database session

    Example:
        ```python
        async def some_tool(session: SessionDep) -> dict:
            result = await session.execute(select(User))
            users = result.scalars().all()
            return {"count": len(users)}
        ```

    Note:
        Session maker must be initialized during application startup via
        initialize_db_session_maker(). This function will raise an error if
        called before initialization.
    """
    if _session_maker is None:
        raise RuntimeError(
            "Database session maker not initialized. "
            "Call initialize_db_session_maker() during app startup."
        )

    async with _session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_http_client() -> httpx.AsyncClient:
    """
    Get shared HTTP client with connection pooling.

    Returns the shared httpx AsyncClient instance created at application startup.
    The client reuses connections for external API calls (connection pooling enabled)
    and is properly closed during application shutdown.

    Lifecycle: Application-scoped (singleton, shared across all requests)

    Returns:
        httpx.AsyncClient: Shared HTTP client instance

    Example:
        ```python
        async def some_tool(client: HttpClientDep) -> dict:
            response = await client.get("https://api.example.com/data")
            return response.json()
        ```

    Note:
        HTTP client must be initialized during application startup via
        initialize_http_client(). This function will raise an error if called
        before initialization.
    """
    if _http_client is None:
        raise RuntimeError(
            "HTTP client not initialized. Call initialize_http_client() during app startup."
        )
    return _http_client


# Application lifecycle management functions


async def initialize_http_client() -> None:
    """
    Initialize shared HTTP client at application startup.

    Creates a shared httpx.AsyncClient instance with connection pooling enabled.
    Should be called once during application startup in the lifespan context manager.

    Raises:
        RuntimeError: If HTTP client already initialized
    """
    global _http_client
    if _http_client is not None:
        raise RuntimeError("HTTP client already initialized")

    _http_client = httpx.AsyncClient(
        timeout=30.0,
        limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
    )


async def close_http_client() -> None:
    """
    Close shared HTTP client at application shutdown.

    Closes the shared httpx.AsyncClient instance and releases all connections.
    Should be called once during application shutdown in the lifespan context manager.
    """
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None


async def initialize_db_session_maker() -> None:
    """
    Initialize database session maker at application startup.

    Creates async SQLAlchemy engine and session maker with connection pooling.
    Should be called once during application startup in the lifespan context manager.

    Raises:
        RuntimeError: If session maker already initialized
    """
    global _session_maker
    if _session_maker is not None:
        raise RuntimeError("Database session maker already initialized")

    settings = get_settings()
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_pre_ping=True,  # Verify connections before using them
        pool_size=10,  # Number of permanent connections
        max_overflow=20,  # Additional connections when pool exhausted
    )

    _session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,  # Allow access to objects after commit
    )


async def close_db_session_maker() -> None:
    """
    Close database session maker at application shutdown.

    Disposes of the SQLAlchemy engine and releases all database connections.
    Should be called once during application shutdown in the lifespan context manager.
    """
    global _session_maker
    if _session_maker is not None:
        # Get the engine from the session maker and dispose it
        if hasattr(_session_maker, "kw") and "bind" in _session_maker.kw:
            engine = _session_maker.kw["bind"]
            if hasattr(engine, "dispose"):
                await engine.dispose()
        _session_maker = None
