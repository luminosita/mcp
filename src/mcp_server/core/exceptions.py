"""
Custom exception classes.

Defines application-specific exceptions for error handling.
"""


class MCPServerError(Exception):
    """Base exception for MCP Server errors."""

    pass


class ConfigurationError(MCPServerError):
    """Raised when configuration is invalid or missing."""

    pass


class ToolExecutionError(MCPServerError):
    """Raised when MCP tool execution fails."""

    pass


class BusinessLogicError(MCPServerError):
    """
    Raised when business logic validation fails.

    Used to distinguish business rule violations from technical errors.
    Includes optional details dictionary for structured error context.
    """

    def __init__(self, message: str, details: dict[str, str] | None = None) -> None:
        """
        Initialize business logic error.

        Args:
            message: Human-readable error message
            details: Optional dictionary with error context
        """
        super().__init__(message)
        self.details = details or {}


# MCP Prompt Error Classes (US-039)


class MCPPromptError(MCPServerError):
    """
    Base class for MCP prompt errors.

    Provides structured error information with troubleshooting guidance
    for users encountering generator prompt loading failures.
    """

    def __init__(self, message: str, prompt_uri: str, troubleshooting: str) -> None:
        """
        Initialize MCP prompt error.

        Args:
            message: Human-readable error message
            prompt_uri: MCP prompt URI that failed (e.g., "mcp://prompts/generator/epic")
            troubleshooting: Troubleshooting steps for user
        """
        self.message = message
        self.prompt_uri = prompt_uri
        self.troubleshooting = troubleshooting
        super().__init__(self.message)


class PromptConnectionError(MCPPromptError):
    """MCP Server unreachable - connection failed or timed out."""

    def __init__(self, prompt_uri: str, server_url: str) -> None:
        """
        Initialize connection error.

        Args:
            prompt_uri: MCP prompt URI that failed
            server_url: MCP Server URL that was unreachable
        """
        super().__init__(
            message=f"Cannot connect to MCP Server at {server_url}",
            prompt_uri=prompt_uri,
            troubleshooting=(
                "Troubleshooting steps:\n"
                f"1. Verify MCP Server is running: curl {server_url}/health\n"
                "2. Check server URL in .mcp/config.json\n"
                "3. Verify network connectivity\n"
                "4. Falling back to local file: prompts/{generator_name}-generator.xml"
            ),
        )
        self.server_url = server_url


class PromptNotFoundError(MCPPromptError):
    """Prompt does not exist on MCP Server - 404 response."""

    def __init__(self, prompt_uri: str, server_url: str) -> None:
        """
        Initialize prompt not found error.

        Args:
            prompt_uri: MCP prompt URI that was not found
            server_url: MCP Server URL
        """
        super().__init__(
            message=f"Prompt not found: {prompt_uri}",
            prompt_uri=prompt_uri,
            troubleshooting=(
                "Troubleshooting steps:\n"
                "1. Verify prompt name is correct (available prompts: epic, prd, hls, backlog-story, etc.)\n"
                "2. Check MCP Server version (generator may not be exposed yet)\n"
                f"3. List available prompts: curl {server_url}/mcp/prompts\n"
                "4. Falling back to local file: prompts/{generator_name}-generator.xml"
            ),
        )
        self.server_url = server_url


class PromptServerError(MCPPromptError):
    """MCP Server returned 5xx error - server-side failure."""

    def __init__(self, prompt_uri: str, status_code: int, response_body: str = "") -> None:
        """
        Initialize server error.

        Args:
            prompt_uri: MCP prompt URI that failed
            status_code: HTTP status code (500, 502, 503, etc.)
            response_body: Server response body (truncated to 200 chars)
        """
        truncated_response = response_body[:200] if response_body else "(empty)"
        super().__init__(
            message=f"MCP Server error {status_code} for {prompt_uri}",
            prompt_uri=prompt_uri,
            troubleshooting=(
                "Troubleshooting steps:\n"
                "1. Check MCP Server logs for error details\n"
                f"2. Server response: {truncated_response}\n"
                "3. Retry in a few minutes (server may be temporarily overloaded)\n"
                "4. Falling back to local file: prompts/{generator_name}-generator.xml"
            ),
        )
        self.status_code = status_code
        self.response_body = response_body


class PromptMalformedContentError(MCPPromptError):
    """MCP Server returned invalid XML content - parsing failed."""

    def __init__(self, prompt_uri: str, parse_error: str) -> None:
        """
        Initialize malformed content error.

        Args:
            prompt_uri: MCP prompt URI that returned invalid content
            parse_error: XML parsing error message
        """
        super().__init__(
            message=f"Invalid generator XML from {prompt_uri}",
            prompt_uri=prompt_uri,
            troubleshooting=(
                "Troubleshooting steps:\n"
                f"1. XML parsing error: {parse_error}\n"
                "2. Report issue to MCP Server maintainer\n"
                "3. Falling back to local file: prompts/{generator_name}-generator.xml"
            ),
        )
        self.parse_error = parse_error


class PromptTimeoutError(MCPPromptError):
    """MCP Server request timed out - response took too long."""

    def __init__(self, prompt_uri: str, timeout_seconds: float) -> None:
        """
        Initialize timeout error.

        Args:
            prompt_uri: MCP prompt URI that timed out
            timeout_seconds: Timeout duration in seconds
        """
        super().__init__(
            message=f"MCP Server request timed out after {timeout_seconds}s for {prompt_uri}",
            prompt_uri=prompt_uri,
            troubleshooting=(
                "Troubleshooting steps:\n"
                f"1. Request timed out after {timeout_seconds} seconds\n"
                "2. Check MCP Server performance (may be overloaded)\n"
                "3. Verify network latency is acceptable\n"
                "4. Falling back to local file: prompts/{generator_name}-generator.xml"
            ),
        )
        self.timeout_seconds = timeout_seconds


# FastAPI REST API Exception Classes (patterns-architecture-middleware.md)


class AppError(Exception):
    """
    Base application exception for FastAPI REST endpoints.

    Used for centralized exception handling via setup_exception_handlers().
    All FastAPI-specific exceptions should inherit from this class.
    """

    def __init__(self, message: str, status_code: int = 500) -> None:
        """
        Initialize application exception.

        Args:
            message: Human-readable error message
            status_code: HTTP status code (default: 500)
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ResourceNotFoundError(AppError):
    """Resource not found exception (HTTP 404)."""

    def __init__(self, message: str = "Resource not found") -> None:
        """
        Initialize resource not found error.

        Args:
            message: Error message describing missing resource
        """
        super().__init__(message, status_code=404)


class ValidationError(AppError):
    """Validation error exception (HTTP 422)."""

    def __init__(self, message: str = "Validation failed") -> None:
        """
        Initialize validation error.

        Args:
            message: Error message describing validation failure
        """
        super().__init__(message, status_code=422)


class UnauthorizedError(AppError):
    """Unauthorized access exception (HTTP 401)."""

    def __init__(self, message: str = "Unauthorized") -> None:
        """
        Initialize unauthorized error.

        Args:
            message: Error message describing authorization failure
        """
        super().__init__(message, status_code=401)


class ForbiddenError(AppError):
    """Forbidden access exception (HTTP 403)."""

    def __init__(self, message: str = "Forbidden") -> None:
        """
        Initialize forbidden error.

        Args:
            message: Error message describing permission denial
        """
        super().__init__(message, status_code=403)
