"""
Unit tests for retry utility with exponential backoff.

Tests retry logic per PRD-006 NFR-Reliability-01 (US-039).
"""

import asyncio
from unittest.mock import AsyncMock

import pytest

from mcp_server.core.exceptions import (
    PromptConnectionError,
    PromptServerError,
    PromptTimeoutError,
)
from mcp_server.utils.retry import retry_with_backoff


class TestRetryWithBackoff:
    """Test retry_with_backoff utility function."""

    @pytest.mark.asyncio
    async def test_success_on_first_attempt_no_retry(self) -> None:
        """Test successful operation on first attempt requires no retries."""
        mock_func = AsyncMock(return_value="success")

        result = await retry_with_backoff(mock_func, operation_name="test_operation")

        assert result == "success"
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_success_after_one_retry(self) -> None:
        """Test successful operation after one retry."""
        mock_func = AsyncMock(
            side_effect=[
                PromptConnectionError("mcp://prompts/generator/epic", "http://localhost:3000"),
                "success",
            ]
        )

        result = await retry_with_backoff(
            mock_func,
            max_retries=3,
            backoff_ms=[100, 200, 400],
            operation_name="test_operation",
        )

        assert result == "success"
        assert mock_func.call_count == 2

    @pytest.mark.asyncio
    async def test_success_after_two_retries(self) -> None:
        """Test successful operation after two retries."""
        mock_func = AsyncMock(
            side_effect=[
                PromptConnectionError("mcp://prompts/generator/epic", "http://localhost:3000"),
                PromptTimeoutError("mcp://prompts/generator/epic", 5.0),
                "success",
            ]
        )

        result = await retry_with_backoff(
            mock_func,
            max_retries=3,
            backoff_ms=[100, 200, 400],
            operation_name="test_operation",
        )

        assert result == "success"
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_retry_exhausted_after_max_retries(self) -> None:
        """Test retry exhaustion after max retries."""
        mock_func = AsyncMock(
            side_effect=PromptConnectionError(
                "mcp://prompts/generator/epic", "http://localhost:3000"
            )
        )

        with pytest.raises(PromptConnectionError):
            await retry_with_backoff(
                mock_func,
                max_retries=3,
                backoff_ms=[100, 200, 400],
                operation_name="test_operation",
            )

        assert mock_func.call_count == 4  # Initial + 3 retries

    @pytest.mark.asyncio
    async def test_non_retryable_error_raises_immediately(self) -> None:
        """Test non-retryable error raises immediately without retry."""
        mock_func = AsyncMock(side_effect=ValueError("Invalid input"))

        with pytest.raises(ValueError, match="Invalid input"):
            await retry_with_backoff(
                mock_func,
                max_retries=3,
                backoff_ms=[100, 200, 400],
                operation_name="test_operation",
            )

        assert mock_func.call_count == 1  # No retries for non-retryable errors

    @pytest.mark.asyncio
    async def test_backoff_timing(self) -> None:
        """Test exponential backoff timing between retries."""
        mock_func = AsyncMock(
            side_effect=[
                PromptConnectionError("mcp://prompts/generator/epic", "http://localhost:3000"),
                PromptConnectionError("mcp://prompts/generator/epic", "http://localhost:3000"),
                "success",
            ]
        )

        start_time = asyncio.get_event_loop().time()

        result = await retry_with_backoff(
            mock_func,
            max_retries=3,
            backoff_ms=[100, 200, 400],
            operation_name="test_operation",
        )

        elapsed_time = asyncio.get_event_loop().time() - start_time

        assert result == "success"
        assert mock_func.call_count == 3
        # Total backoff: 100ms + 200ms = 300ms = 0.3s
        # Allow some margin for test execution
        assert elapsed_time >= 0.25  # At least 250ms (allowing for timing variance)
        assert elapsed_time < 0.5  # Less than 500ms (generous upper bound)

    @pytest.mark.asyncio
    async def test_custom_retryable_exceptions(self) -> None:
        """Test custom retryable exception types."""
        mock_func = AsyncMock(
            side_effect=[
                ConnectionError("Network error"),
                "success",
            ]
        )

        result = await retry_with_backoff(
            mock_func,
            max_retries=3,
            backoff_ms=[100, 200, 400],
            retryable_exceptions=(ConnectionError,),
            operation_name="test_operation",
        )

        assert result == "success"
        assert mock_func.call_count == 2

    @pytest.mark.asyncio
    async def test_server_error_is_retryable(self) -> None:
        """Test 5xx server errors are retryable."""
        mock_func = AsyncMock(
            side_effect=[
                PromptServerError("mcp://prompts/generator/epic", 500, "Internal error"),
                "success",
            ]
        )

        result = await retry_with_backoff(
            mock_func,
            max_retries=3,
            backoff_ms=[100, 200, 400],
            operation_name="test_operation",
        )

        assert result == "success"
        assert mock_func.call_count == 2

    @pytest.mark.asyncio
    async def test_timeout_error_is_retryable(self) -> None:
        """Test timeout errors are retryable."""
        mock_func = AsyncMock(
            side_effect=[
                PromptTimeoutError("mcp://prompts/generator/epic", 5.0),
                "success",
            ]
        )

        result = await retry_with_backoff(
            mock_func,
            max_retries=3,
            backoff_ms=[100, 200, 400],
            operation_name="test_operation",
        )

        assert result == "success"
        assert mock_func.call_count == 2

    @pytest.mark.asyncio
    async def test_default_backoff_values(self) -> None:
        """Test default backoff values are used when not specified."""
        mock_func = AsyncMock(
            side_effect=[
                PromptConnectionError("mcp://prompts/generator/epic", "http://localhost:3000"),
                "success",
            ]
        )

        result = await retry_with_backoff(
            mock_func,
            # No backoff_ms specified - should use defaults [100, 200, 400]
            operation_name="test_operation",
        )

        assert result == "success"
        assert mock_func.call_count == 2

    @pytest.mark.asyncio
    async def test_retry_with_different_error_types(self) -> None:
        """Test retry with different retryable error types across attempts."""
        mock_func = AsyncMock(
            side_effect=[
                PromptConnectionError("mcp://prompts/generator/epic", "http://localhost:3000"),
                PromptTimeoutError("mcp://prompts/generator/epic", 5.0),
                PromptServerError("mcp://prompts/generator/epic", 503, "Service unavailable"),
                "success",
            ]
        )

        result = await retry_with_backoff(
            mock_func,
            max_retries=3,
            backoff_ms=[100, 200, 400],
            operation_name="test_operation",
        )

        assert result == "success"
        assert mock_func.call_count == 4  # All 3 retries succeeded on 4th attempt
