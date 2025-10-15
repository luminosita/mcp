"""
Application constants.

Defines constant values used throughout the application.
Provides single source of truth for application-wide constants.
"""

# Application metadata
APP_NAME = "AI Agent MCP Server"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "Model Context Protocol server for AI agent tools"

# API configuration
API_PREFIX = "/api/v1"
DOCS_URL = "/docs"
REDOC_URL = "/redoc"

# Health check status values
HEALTH_STATUS_HEALTHY = "healthy"
HEALTH_STATUS_DEGRADED = "degraded"
HEALTH_STATUS_UNHEALTHY = "unhealthy"

# CORS configuration (development)
CORS_ALLOW_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
]
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
CORS_ALLOW_HEADERS = ["*"]

# Logging
LOG_FORMAT_JSON = "json"
LOG_FORMAT_TEXT = "text"
