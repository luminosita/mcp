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
