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
