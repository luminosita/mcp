"""
Configuration management using Pydantic Settings.

Handles application configuration from environment variables.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "AI Agent MCP Server"
    app_version: str = "0.1.0"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/mcp"

    log_level: str = "INFO"
    log_format: str = "json"

    secret_key: str = "change-me-in-production"

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False


settings = Settings()
