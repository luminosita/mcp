"""
Configuration management using Pydantic Settings.

Handles application configuration from environment variables.
Validates settings on startup with clear error messages.
"""

from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Configuration values are loaded from:
    1. Environment variables (highest priority)
    2. .env file (development default)
    3. Default values (fallback)

    All settings include type hints for static analysis and Pydantic validation.
    Invalid settings will cause application startup to fail with clear error messages.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application metadata
    app_name: str = Field(
        default="AI Agent MCP Server",
        description="Application name displayed in logs and API docs",
    )
    app_version: str = Field(
        default="0.1.0",
        description="Application version (semver format)",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode (verbose logging, detailed errors)",
    )

    # Server configuration
    host: str = Field(
        default="0.0.0.0",  # noqa: S104
        description="Server bind host address",
    )
    port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Server bind port (1-65535)",
    )

    # Database configuration (US-010)
    database_url: str = Field(
        default="postgresql+asyncpg://user:pass@localhost:5432/mcp",
        description="Database connection URL",
    )

    # Logging configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    log_format: Literal["json", "text"] = Field(
        default="json",
        description="Log output format (json for production, text for development)",
    )

    # Security
    secret_key: str = Field(
        default="change-me-in-production",
        description="Secret key for session management",
    )

    # MCP Resources configuration (US-030, US-031)
    patterns_base_dir: str = Field(
        default="prompts/CLAUDE",
        description="Base directory for implementation pattern files",
    )
    sdlc_core_file_path: str = Field(
        default="prompts/CLAUDE/sdlc-core.md",
        description="Path to SDLC framework core file",
    )
    templates_dir: str = Field(
        default="prompts/templates",
        description="Directory containing artifact template files (US-031)",
    )
    prompts_dir: str = Field(
        default="prompts",
        description="Base directory for generator prompt files (US-035)",
    )

    # Cache configuration (US-032)
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for resource caching",
    )
    cache_ttl: int = Field(
        default=300,
        ge=1,
        description="Cache TTL in seconds (default: 5 minutes)",
    )
    cache_max_size: int = Field(
        default=1000,
        ge=1,
        description="Maximum number of cached resources (LRU eviction)",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("log_level", mode="before")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate and normalize log level to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return v


# Global settings instance
# Instantiated once on module import, validated immediately
# Application will fail fast on startup if configuration is invalid
settings = Settings()
