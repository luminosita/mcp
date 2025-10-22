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
from pathlib import Path

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from mcp_server.api.routes import resources
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
from mcp_server.core.exception_handlers import setup_exception_handlers
from mcp_server.prompts.registry import PromptRegistry
from mcp_server.services import cache_service

# Application startup time for uptime calculation
_startup_time: float = 0.0

# Initialize FastMCP server
# WHY FASTMCP: Handles MCP protocol complexities (initialization handshake,
# bidirectional communication, JSON-RPC 2.0) while maintaining control over
# authentication and observability.
mcp = FastMCP(name="AI Agent MCP Server")

# Initialize prompt registry for generator prompts (US-035)
# Prompts directory path from configuration (supports environment overrides)
_prompts_dir = Path(settings.prompts_dir)
_prompt_registry = PromptRegistry(prompts_dir=_prompts_dir)


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

    # Initialize cache service (US-032)
    await cache_service.connect()
    logger.info(
        "cache_service_initialized",
        redis_url=settings.redis_url,
        cache_ttl=settings.cache_ttl,
    )

    logger.info("application_startup_complete")

    yield

    # Shutdown
    logger.info("application_shutdown_started")

    await close_http_client()
    logger.info("http_client_closed")

    await close_db_session_maker()
    logger.info("database_session_maker_closed")

    # Disconnect cache service (US-032)
    await cache_service.disconnect()
    logger.info("cache_service_disconnected")

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

# Setup centralized exception handlers for REST endpoints
# Follows patterns-architecture-middleware.md guidelines
setup_exception_handlers(app)

# Register API routers
# MCP resources endpoints for serving implementation patterns and SDLC content
app.include_router(resources.router)


# Register MCP prompts for generator XML files (US-035)
# WHY DYNAMIC REGISTRATION: Scans prompts/ directory and registers all generators
# as MCP prompts. New generators can be added by placing XML files in prompts/
# without code changes.
@mcp.prompt(
    name="generator",
    description="""
    Retrieve artifact generator prompt by artifact name.

    Exposes all SDLC artifact generators as MCP prompts:
    - product-vision: Generate product vision artifacts
    - initiative: Generate initiative artifacts
    - epic: Generate epic artifacts
    - prd: Generate PRD (Product Requirements Document) artifacts
    - high-level-user-story (hls): Generate high-level user story artifacts
    - backlog-story: Generate backlog user story artifacts
    - spike: Generate spike (technical investigation) artifacts
    - adr: Generate Architecture Decision Record artifacts
    - tech-spec: Generate technical specification artifacts
    - implementation-task: Generate implementation task artifacts

    Returns generator XML content for use in artifact generation workflows.
    Content is cached with 5-minute TTL for performance.

    Security: Input validation prevents path traversal attacks.
    Performance: p95 latency <100ms (cache hit <10ms, cache miss <100ms).

    Example usage:
        artifact_name: "epic"
        Returns: Full XML content of epic-generator.xml
    """,
)
async def get_generator_prompt(artifact_name: str) -> str:
    """
    MCP prompt for retrieving generator XML content.

    Args:
        artifact_name: Artifact name (e.g., "epic", "backlog-story")

    Returns:
        Generator XML content as string

    Raises:
        ValueError: If artifact_name fails security validation
        FileNotFoundError: If generator file doesn't exist
        OSError: If file read fails
    """
    logger = structlog.get_logger(__name__)
    logger.info(
        "generator_prompt_requested",
        artifact_name=artifact_name,
    )

    try:
        content = await _prompt_registry.load_prompt(artifact_name)
        cache_stats = await _prompt_registry.get_cache_stats()
        logger.info(
            "generator_prompt_loaded",
            artifact_name=artifact_name,
            content_length=len(content),
            cache_stats=cache_stats,
        )
        return content
    except (ValueError, FileNotFoundError, OSError) as e:
        logger.error(
            "generator_prompt_load_failed",
            artifact_name=artifact_name,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise


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
