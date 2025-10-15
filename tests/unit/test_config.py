"""
Unit tests for configuration management.

Tests Pydantic settings validation, environment variable loading, and error handling.
"""

import pytest
from pydantic import ValidationError

from mcp_server.config import Settings


@pytest.mark.unit
def test_settings_default_values() -> None:
    """Test that Settings uses correct default values."""
    settings = Settings()

    assert settings.app_name == "AI Agent MCP Server"
    assert settings.app_version == "0.1.0"
    assert settings.debug is False
    assert settings.host == "0.0.0.0"  # noqa: S104
    assert settings.port == 8000
    assert settings.log_level == "INFO"
    assert settings.log_format == "json"


@pytest.mark.unit
def test_settings_accepts_valid_port() -> None:
    """Test that Settings accepts valid port numbers."""
    # Valid port range: 1-65535
    settings = Settings(port=8080)
    assert settings.port == 8080

    settings = Settings(port=1)
    assert settings.port == 1

    settings = Settings(port=65535)
    assert settings.port == 65535


@pytest.mark.unit
def test_settings_rejects_invalid_port_too_low() -> None:
    """Test that Settings rejects port number below 1."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(port=0)

    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert any(error["loc"] == ("port",) for error in errors)


@pytest.mark.unit
def test_settings_rejects_invalid_port_too_high() -> None:
    """Test that Settings rejects port number above 65535."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(port=65536)

    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert any(error["loc"] == ("port",) for error in errors)


@pytest.mark.unit
def test_settings_rejects_invalid_port_type() -> None:
    """Test that Settings rejects non-integer port values."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(port="invalid")  # type: ignore[arg-type]

    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert any(error["loc"] == ("port",) for error in errors)


@pytest.mark.unit
def test_settings_log_level_normalization() -> None:
    """Test that log level is normalized to uppercase."""
    settings = Settings(log_level="debug")
    assert settings.log_level == "DEBUG"

    settings = Settings(log_level="info")
    assert settings.log_level == "INFO"

    settings = Settings(log_level="WARNING")
    assert settings.log_level == "WARNING"


@pytest.mark.unit
def test_settings_accepts_valid_log_levels() -> None:
    """Test that Settings accepts all valid log levels."""
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    for level in valid_levels:
        settings = Settings(log_level=level)
        assert settings.log_level == level


@pytest.mark.unit
def test_settings_rejects_invalid_log_level() -> None:
    """Test that Settings rejects invalid log levels."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(log_level="INVALID")

    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert any(error["loc"] == ("log_level",) for error in errors)


@pytest.mark.unit
def test_settings_accepts_valid_log_formats() -> None:
    """Test that Settings accepts valid log formats."""
    settings = Settings(log_format="json")
    assert settings.log_format == "json"

    settings = Settings(log_format="text")
    assert settings.log_format == "text"


@pytest.mark.unit
def test_settings_rejects_invalid_log_format() -> None:
    """Test that Settings rejects invalid log formats."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(log_format="invalid")  # type: ignore[arg-type]

    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert any(error["loc"] == ("log_format",) for error in errors)


@pytest.mark.unit
def test_settings_debug_mode_boolean() -> None:
    """Test that debug mode accepts boolean values."""
    settings = Settings(debug=True)
    assert settings.debug is True

    settings = Settings(debug=False)
    assert settings.debug is False


@pytest.mark.unit
def test_settings_custom_app_name() -> None:
    """Test that Settings accepts custom application name."""
    custom_name = "Custom MCP Server"
    settings = Settings(app_name=custom_name)
    assert settings.app_name == custom_name


@pytest.mark.unit
def test_settings_custom_app_version() -> None:
    """Test that Settings accepts custom application version."""
    custom_version = "1.2.3"
    settings = Settings(app_version=custom_version)
    assert settings.app_version == custom_version


@pytest.mark.unit
def test_settings_custom_host() -> None:
    """Test that Settings accepts custom host address."""
    settings = Settings(host="127.0.0.1")
    assert settings.host == "127.0.0.1"

    settings = Settings(host="localhost")
    assert settings.host == "localhost"


@pytest.mark.unit
def test_settings_loads_from_environment_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that Settings loads configuration from environment variables."""
    # Set environment variables
    monkeypatch.setenv("APP_NAME", "Test Server")
    monkeypatch.setenv("APP_VERSION", "2.0.0")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("PORT", "9000")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("LOG_FORMAT", "text")

    # Create new Settings instance (will load from env vars)
    settings = Settings()

    assert settings.app_name == "Test Server"
    assert settings.app_version == "2.0.0"
    assert settings.debug is True
    assert settings.port == 9000
    assert settings.log_level == "DEBUG"
    assert settings.log_format == "text"


@pytest.mark.unit
def test_settings_case_insensitive_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that Settings accepts case-insensitive environment variables."""
    monkeypatch.setenv("app_name", "Test Server")
    monkeypatch.setenv("APP_VERSION", "2.0.0")
    monkeypatch.setenv("DebuG", "true")

    settings = Settings()

    assert settings.app_name == "Test Server"
    assert settings.app_version == "2.0.0"
    assert settings.debug is True


@pytest.mark.unit
def test_settings_validation_error_message_clear() -> None:
    """Test that validation errors provide clear, actionable messages."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(port="invalid")  # type: ignore[arg-type]

    error_message = str(exc_info.value)

    # Error message should mention the field and issue
    assert "port" in error_message.lower()
