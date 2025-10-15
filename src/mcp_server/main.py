"""
FastAPI application entry point.

Defines the main FastAPI application instance with dependency injection support,
health check endpoint, structured logging, and CORS middleware.
"""

import sys
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from mcp_server.config import settings
from mcp_server.core.constants import (
    APP_DESCRIPTION,
    APP_NAME,
    APP_VERSION,
    CORS_ALLOW_HEADERS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_ORIGINS,
    HEALTH_STATUS_HEALTHY,
)
from mcp_server.core.dependencies import (
    close_db_session_maker,
    close_http_client,
    initialize_db_session_maker,
    initialize_http_client,
)
from mcp_server.tools.example_tool import (
    GreetingInput,
    GreetingOutput,
    generate_greeting,
)

# Application startup time for uptime calculation
_startup_time: float = 0.0

# Initialize FastMCP server
# WHY FASTMCP: Handles MCP protocol complexities (initialization handshake,
# bidirectional communication, JSON-RPC 2.0) while maintaining control over
# authentication and observability.
mcp = FastMCP(name="AI Agent MCP Server")


def configure_logging() -> None:
    """
    Configure structured logging with structlog.

    Sets up JSON or text output format based on configuration.
    Configures log processors for consistent structured logging.
    """
    import logging
    from typing import Any

    # Map string log level to logging constant
    log_level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    log_level = log_level_map.get(settings.log_level, logging.INFO)

    # Build processor list with proper typing
    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.log_format == "json":
        # JSON output for production (machine-readable)
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Text output for development (human-readable)
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events:
    - Configures structured logging
    - Initializes dependency injection resources (HTTP client, database)
    - Tracks application startup time for health check uptime
    """
    global _startup_time

    # Startup
    configure_logging()
    logger = structlog.get_logger()
    _startup_time = time.time()

    logger.info(
        "application_startup",
        app_name=settings.app_name,
        version=settings.app_version,
        host=settings.host,
        port=settings.port,
        debug=settings.debug,
        log_level=settings.log_level,
        log_format=settings.log_format,
    )

    # Initialize dependency injection resources
    await initialize_http_client()
    logger.info("http_client_initialized")

    await initialize_db_session_maker()
    logger.info("database_session_maker_initialized")

    logger.info("application_startup_complete")

    yield

    # Shutdown
    logger.info("application_shutdown_started")

    await close_http_client()
    logger.info("http_client_closed")

    await close_db_session_maker()
    logger.info("database_session_maker_closed")

    logger.info("application_shutdown_complete", uptime_seconds=time.time() - _startup_time)


# FastAPI application instance
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware for development
# Allows frontend applications running on localhost to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)


# Register MCP tools
# WHY SEPARATE REGISTRATION: Keeps tool definitions modular while centralizing
# registration for visibility. Tools can be organized by domain (jira, k8s, rag)
# in separate modules.
@mcp.tool(
    name="example.generate_greeting",
    description="""
    Generates a personalized greeting message (example tool for pattern demonstration).

    Use this tool when:
    - Demonstrating MCP tool patterns to developers
    - Testing MCP server functionality
    - Learning how to implement tools with validation and error handling

    This is an example tool showing best practices:
    - Pydantic input/output validation
    - Error handling for validation and business logic errors
    - Dependency injection for settings and logging
    - Async patterns for consistency
    - Comprehensive docstrings

    Greeting styles:
    - formal: "Good day, [name]"
    - casual: "Hey, [name]"
    - enthusiastic: "Hello there, [name]"

    Returns structured greeting with metadata including style used and character count.
    """,
)
async def example_greeting_tool(params: GreetingInput) -> GreetingOutput:
    """
    MCP tool wrapper for generate_greeting function.

    WHY WRAPPER: Separates MCP tool registration (@mcp.tool decorator) from
    business logic (generate_greeting function). This enables:
    - Testing business logic without MCP protocol overhead
    - Reusing business logic in different contexts (REST API, CLI)
    - Clear separation between protocol concerns and domain logic

    WHY NO DEPENDENCY PARAMETERS: FastMCP generates JSON schema from function
    signature, so only Pydantic-serializable types allowed. Dependencies
    accessed directly inside function instead of as parameters.

    Args:
        params: Validated greeting input parameters

    Returns:
        GreetingOutput: Structured greeting response with metadata

    Raises:
        BusinessLogicError: If greeting generation fails business rules
        ValidationError: If input validation fails (handled by Pydantic/FastMCP)
    """
    import logging

    # Access dependencies directly (not as function parameters)
    # WHY: FastMCP requires all function parameters to be Pydantic-serializable
    # for JSON schema generation. Logger and Settings can't be serialized to JSON.
    logger = logging.getLogger("mcp_server.tools.example_tool")
    return await generate_greeting(params, settings, logger)


class HealthCheckResponse(BaseModel):
    """
    Health check response schema.

    Returns current application health status and metadata.
    Used by monitoring tools and load balancers.
    """

    status: str
    version: str
    uptime_seconds: float
    timestamp: str


@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint.

    Returns application health status, version, uptime, and timestamp.
    Used by monitoring tools to verify server availability.

    Status values:
    - healthy: All systems operational
    - degraded: Partial functionality (not implemented in US-009)
    - unhealthy: Critical failure (not implemented in US-009)

    Returns:
        HealthCheckResponse: Current health status and metadata
    """
    current_time = time.time()
    uptime = current_time - _startup_time if _startup_time > 0 else 0.0

    return HealthCheckResponse(
        status=HEALTH_STATUS_HEALTHY,
        version=APP_VERSION,
        uptime_seconds=uptime,
        timestamp=datetime.now(UTC).isoformat(),
    )


# Mount MCP server using stdio transport
# WHY STDIO: FastMCP primarily uses stdio (standard input/output) for communication
# with MCP clients. This is the standard transport for server-side MCP implementations.
# The server can be invoked directly by MCP clients using stdio communication.
#
# Note: For HTTP-based access, FastMCP can be wrapped with SSE or other transports,
# but the basic FastMCP server works via stdio which is suitable for server-to-server
# and CLI-based MCP client communication.
