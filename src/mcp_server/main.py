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

# Application startup time for uptime calculation
_startup_time: float = 0.0


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
