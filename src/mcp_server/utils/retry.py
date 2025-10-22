"""
Retry utility with exponential backoff for transient failures.

Implements retry logic per PRD-006 NFR-Reliability-01 (US-039).
"""

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

import structlog

from mcp_server.core.exceptions import (
    PromptConnectionError,
    PromptServerError,
    PromptTimeoutError,
)

logger = structlog.get_logger(__name__)

T = TypeVar("T")

# Default retry configuration per PRD-006 NFR-Reliability-01
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_MS = [100, 200, 400]  # Exponential backoff: 100ms, 200ms, 400ms


async def retry_with_backoff(
    func: Callable[[], Awaitable[T]],
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_ms: list[int] | None = None,
    retryable_exceptions: tuple[type[Exception], ...] | None = None,
    operation_name: str = "operation",
) -> T:
    """
    Retry async function with exponential backoff for transient failures.

    Implements retry logic per PRD-006 NFR-Reliability-01:
    - 3 retries with exponential backoff (100ms, 200ms, 400ms)
    - Total retry time <1 second
    - Retries only transient errors (connection, timeout, 5xx server errors)

    Args:
        func: Async function to retry (no arguments)
        max_retries: Maximum number of retries (default: 3)
        backoff_ms: Backoff delays in milliseconds (default: [100, 200, 400])
        retryable_exceptions: Tuple of exception types to retry (default: transient errors)
        operation_name: Human-readable operation name for logging

    Returns:
        Result from successful function execution

    Raises:
        Exception: Original exception if all retries exhausted

    Example:
        >>> async def load_prompt():
        ...     return await mcp_client.get_prompt("epic")
        >>> content = await retry_with_backoff(
        ...     load_prompt,
        ...     operation_name="load_epic_prompt"
        ... )
    """
    if backoff_ms is None:
        backoff_ms = DEFAULT_BACKOFF_MS

    if retryable_exceptions is None:
        # Default: retry only transient errors
        retryable_exceptions = (
            PromptConnectionError,
            PromptTimeoutError,
            PromptServerError,
        )

    last_exception: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            result = await func()
            if attempt > 0:
                # Log successful retry
                logger.info(
                    "retry_succeeded",
                    operation=operation_name,
                    attempt=attempt + 1,
                    max_retries=max_retries,
                )
            return result

        except retryable_exceptions as e:
            last_exception = e

            if attempt == max_retries:
                # Final retry exhausted - log error and raise
                logger.error(
                    "retry_exhausted",
                    operation=operation_name,
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise

            # Retry with backoff
            backoff_duration = backoff_ms[attempt] / 1000.0  # Convert to seconds
            logger.warning(
                "retrying_after_failure",
                operation=operation_name,
                attempt=attempt + 1,
                max_retries=max_retries,
                backoff_ms=backoff_ms[attempt],
                error=str(e),
                error_type=type(e).__name__,
            )
            await asyncio.sleep(backoff_duration)

        except Exception as e:
            # Non-retryable error - log and raise immediately
            logger.error(
                "non_retryable_error",
                operation=operation_name,
                attempt=attempt + 1,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise

    # Should never reach here, but handle edge case
    if last_exception:
        raise last_exception
    raise RuntimeError(f"Retry logic failed for {operation_name}")


def log_mcp_error(
    error: Exception,
    context: dict[str, str | int | float],
) -> None:
    """
    Log MCP prompt error with structured details.

    Provides consistent structured logging for MCP prompt errors with
    error type, message, prompt URI, context, and troubleshooting guidance.

    Args:
        error: Exception that occurred
        context: Error context dictionary (generator_name, server_url, retry_count, etc.)

    Example:
        >>> error = PromptConnectionError(
        ...     "mcp://prompts/generator/epic",
        ...     "http://localhost:3000"
        ... )
        >>> log_mcp_error(error, {
        ...     "generator_name": "epic",
        ...     "server_url": "http://localhost:3000",
        ...     "retry_count": 3,
        ... })
    """
    from mcp_server.core.exceptions import MCPPromptError

    if isinstance(error, MCPPromptError):
        logger.error(
            "mcp_prompt_error",
            error_type=type(error).__name__,
            message=error.message,
            prompt_uri=error.prompt_uri,
            troubleshooting=error.troubleshooting,
            **context,
        )
    else:
        logger.error(
            "unexpected_error",
            error_type=type(error).__name__,
            message=str(error),
            **context,
        )
