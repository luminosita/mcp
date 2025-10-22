"""
Unit tests for MCP prompt exception classes.

Tests exception hierarchy and user-friendly error messages (US-039).
"""

from mcp_server.core.exceptions import (
    MCPPromptError,
    MCPServerError,
    PromptConnectionError,
    PromptMalformedContentError,
    PromptNotFoundError,
    PromptServerError,
    PromptTimeoutError,
)


class TestMCPPromptErrorHierarchy:
    """Test MCP prompt error class hierarchy."""

    def test_mcp_prompt_error_inherits_from_mcp_server_error(self) -> None:
        """Test MCPPromptError inherits from MCPServerError."""
        error = MCPPromptError(
            message="Test error",
            prompt_uri="mcp://prompts/generator/epic",
            troubleshooting="Test steps",
        )

        assert isinstance(error, MCPServerError)
        assert isinstance(error, Exception)

    def test_prompt_connection_error_inherits_from_mcp_prompt_error(self) -> None:
        """Test PromptConnectionError inherits from MCPPromptError."""
        error = PromptConnectionError("mcp://prompts/generator/epic", "http://localhost:3000")

        assert isinstance(error, MCPPromptError)
        assert isinstance(error, MCPServerError)

    def test_all_prompt_errors_inherit_from_mcp_prompt_error(self) -> None:
        """Test all prompt error types inherit from MCPPromptError."""
        error_classes = [
            PromptConnectionError,
            PromptNotFoundError,
            PromptServerError,
            PromptMalformedContentError,
            PromptTimeoutError,
        ]

        for error_class in error_classes:
            # Create instance with appropriate constructor args
            if error_class == PromptServerError:
                error = error_class("mcp://prompts/generator/epic", 500)
            elif error_class == PromptTimeoutError:
                error = error_class("mcp://prompts/generator/epic", 5.0)
            elif error_class == PromptMalformedContentError:
                error = error_class("mcp://prompts/generator/epic", "Parsing error")
            else:
                error = error_class("mcp://prompts/generator/epic", "http://localhost:3000")

            assert isinstance(error, MCPPromptError)
            assert isinstance(error, MCPServerError)


class TestPromptConnectionError:
    """Test PromptConnectionError class."""

    def test_error_message_format(self) -> None:
        """Test error message includes server URL."""
        error = PromptConnectionError("mcp://prompts/generator/epic", "http://localhost:3000")

        assert "Cannot connect to MCP Server at http://localhost:3000" in str(error)
        assert error.prompt_uri == "mcp://prompts/generator/epic"
        assert error.server_url == "http://localhost:3000"

    def test_troubleshooting_includes_curl_command(self) -> None:
        """Test troubleshooting guidance includes curl command."""
        error = PromptConnectionError("mcp://prompts/generator/epic", "http://localhost:3000")

        assert "curl http://localhost:3000/health" in error.troubleshooting
        assert "Troubleshooting steps:" in error.troubleshooting

    def test_troubleshooting_includes_fallback_guidance(self) -> None:
        """Test troubleshooting includes fallback to local file."""
        error = PromptConnectionError("mcp://prompts/generator/epic", "http://localhost:3000")

        assert "Falling back to local file" in error.troubleshooting


class TestPromptNotFoundError:
    """Test PromptNotFoundError class."""

    def test_error_message_format(self) -> None:
        """Test error message includes prompt URI."""
        error = PromptNotFoundError("mcp://prompts/generator/invalid", "http://localhost:3000")

        assert "Prompt not found: mcp://prompts/generator/invalid" in str(error)
        assert error.prompt_uri == "mcp://prompts/generator/invalid"
        assert error.server_url == "http://localhost:3000"

    def test_troubleshooting_includes_available_prompts(self) -> None:
        """Test troubleshooting lists available prompt names."""
        error = PromptNotFoundError("mcp://prompts/generator/invalid", "http://localhost:3000")

        assert "epic, prd, hls, backlog-story" in error.troubleshooting

    def test_troubleshooting_includes_list_prompts_command(self) -> None:
        """Test troubleshooting includes command to list available prompts."""
        error = PromptNotFoundError("mcp://prompts/generator/invalid", "http://localhost:3000")

        assert "curl http://localhost:3000/mcp/prompts" in error.troubleshooting


class TestPromptServerError:
    """Test PromptServerError class."""

    def test_error_message_includes_status_code(self) -> None:
        """Test error message includes HTTP status code."""
        error = PromptServerError("mcp://prompts/generator/epic", 500, "Internal server error")

        assert "MCP Server error 500" in str(error)
        assert error.status_code == 500
        assert error.response_body == "Internal server error"

    def test_troubleshooting_includes_response_body(self) -> None:
        """Test troubleshooting includes server response body."""
        error = PromptServerError(
            "mcp://prompts/generator/epic",
            500,
            "Internal server error: Database connection failed",
        )

        assert "Internal server error: Database connection failed" in error.troubleshooting

    def test_response_body_truncated_to_200_chars(self) -> None:
        """Test response body is truncated to 200 characters."""
        long_response = "A" * 300
        error = PromptServerError("mcp://prompts/generator/epic", 500, long_response)

        # Full response stored
        assert len(error.response_body) == 300

        # Troubleshooting shows truncated version
        assert len(error.troubleshooting) < 500  # Includes other text too

    def test_empty_response_body(self) -> None:
        """Test error handles empty response body gracefully."""
        error = PromptServerError("mcp://prompts/generator/epic", 503)

        assert "(empty)" in error.troubleshooting
        assert error.response_body == ""


class TestPromptMalformedContentError:
    """Test PromptMalformedContentError class."""

    def test_error_message_format(self) -> None:
        """Test error message indicates invalid XML."""
        error = PromptMalformedContentError(
            "mcp://prompts/generator/spike",
            "mismatched tag at line 42: expected </section>, got </content>",
        )

        assert "Invalid generator XML" in str(error)
        assert error.parse_error == "mismatched tag at line 42: expected </section>, got </content>"

    def test_troubleshooting_includes_parse_error(self) -> None:
        """Test troubleshooting includes XML parsing error details."""
        error = PromptMalformedContentError(
            "mcp://prompts/generator/spike", "mismatched tag at line 42"
        )

        assert "mismatched tag at line 42" in error.troubleshooting
        assert "XML parsing error:" in error.troubleshooting

    def test_troubleshooting_suggests_reporting_issue(self) -> None:
        """Test troubleshooting suggests reporting to maintainer."""
        error = PromptMalformedContentError("mcp://prompts/generator/spike", "Parse error")

        assert "Report issue to MCP Server maintainer" in error.troubleshooting


class TestPromptTimeoutError:
    """Test PromptTimeoutError class."""

    def test_error_message_includes_timeout_duration(self) -> None:
        """Test error message includes timeout duration."""
        error = PromptTimeoutError("mcp://prompts/generator/prd", 5.0)

        assert "timed out after 5.0s" in str(error)
        assert error.timeout_seconds == 5.0

    def test_troubleshooting_includes_timeout_duration(self) -> None:
        """Test troubleshooting includes timeout duration."""
        error = PromptTimeoutError("mcp://prompts/generator/prd", 5.0)

        assert "5.0 seconds" in error.troubleshooting

    def test_troubleshooting_suggests_performance_check(self) -> None:
        """Test troubleshooting suggests checking server performance."""
        error = PromptTimeoutError("mcp://prompts/generator/prd", 5.0)

        assert "server performance" in error.troubleshooting.lower()


class TestMCPPromptErrorAttributes:
    """Test MCPPromptError base class attributes."""

    def test_base_error_has_required_attributes(self) -> None:
        """Test MCPPromptError has message, prompt_uri, and troubleshooting."""
        error = MCPPromptError(
            message="Test error",
            prompt_uri="mcp://prompts/generator/epic",
            troubleshooting="Step 1\nStep 2",
        )

        assert error.message == "Test error"
        assert error.prompt_uri == "mcp://prompts/generator/epic"
        assert error.troubleshooting == "Step 1\nStep 2"

    def test_error_message_matches_str_representation(self) -> None:
        """Test error message is used for string representation."""
        error = MCPPromptError(
            message="Custom error message",
            prompt_uri="mcp://prompts/generator/epic",
            troubleshooting="Steps",
        )

        assert str(error) == "Custom error message"

    def test_all_errors_have_troubleshooting_guidance(self) -> None:
        """Test all prompt errors provide troubleshooting guidance."""
        errors = [
            PromptConnectionError("mcp://prompts/generator/epic", "http://localhost:3000"),
            PromptNotFoundError("mcp://prompts/generator/epic", "http://localhost:3000"),
            PromptServerError("mcp://prompts/generator/epic", 500),
            PromptMalformedContentError("mcp://prompts/generator/epic", "Error"),
            PromptTimeoutError("mcp://prompts/generator/epic", 5.0),
        ]

        for error in errors:
            assert hasattr(error, "troubleshooting")
            assert len(error.troubleshooting) > 0
            assert "Troubleshooting steps:" in error.troubleshooting
