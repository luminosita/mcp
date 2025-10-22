"""
FastAPI exception handlers for centralized error handling.

Implements centralized exception handling for FastAPI REST API endpoints
following patterns-architecture-middleware.md guidelines.
"""

import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from mcp_server.core.exceptions import AppError

logger = structlog.get_logger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Setup application exception handlers.

    Registers centralized exception handlers for FastAPI REST endpoints.
    Follows pattern from patterns-architecture-middleware.md.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(AppError)
    async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
        """
        Handle application exceptions.

        Converts custom AppError subclasses to structured JSON responses
        with appropriate HTTP status codes.

        Args:
            request: FastAPI request object
            exc: Application exception instance

        Returns:
            JSONResponse with error details and status code
        """
        logger.error(
            "application_error",
            error_class=exc.__class__.__name__,
            message=exc.message,
            status_code=exc.status_code,
            path=str(request.url),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.__class__.__name__,
                "message": exc.message,
                "path": str(request.url),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Handle unexpected exceptions.

        Catches all uncaught exceptions and returns generic 500 error response.
        Logs full exception details for debugging while returning safe error
        message to clients.

        Args:
            request: FastAPI request object
            exc: Exception instance

        Returns:
            JSONResponse with generic error message and 500 status code
        """
        logger.error(
            "unexpected_error",
            error_class=exc.__class__.__name__,
            error_message=str(exc),
            path=str(request.url),
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "path": str(request.url),
            },
        )
