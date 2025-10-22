"""
Unit tests for MCP resource schemas.

Tests Pydantic models and validation logic for resource requests and responses.
Focuses on path traversal protection and input validation.
"""

import pytest
from pydantic import ValidationError

from mcp_server.api.schemas.resources import (
    PatternResourceRequest,
    ResourceNameValidator,
    ResourceResponse,
)


class TestResourceNameValidator:
    """Test ResourceNameValidator path traversal protection."""

    def test_valid_resource_names(self):
        """Test that valid resource names pass validation."""
        valid_names = [
            "core",
            "tooling",
            "testing",
            "typing",
            "validation",
            "validation-api",
            "validation-auth",
            "architecture/patterns",
            "architecture-patterns",
        ]

        for name in valid_names:
            result = ResourceNameValidator.validate_resource_name(name)
            assert result == name

    def test_reject_parent_directory_references(self):
        """Test that parent directory references (..) are rejected."""
        invalid_names = [
            "../etc/passwd",
            "../../etc/passwd",
            "foo/../bar",
            "..core",
            "core..",
        ]

        for name in invalid_names:
            with pytest.raises(ValueError, match="parent directory references"):
                ResourceNameValidator.validate_resource_name(name)

    def test_reject_absolute_paths(self):
        """Test that absolute paths are rejected."""
        invalid_names = [
            "/etc/passwd",
            "/core",
            "/prompts/CLAUDE/python/core",
        ]

        for name in invalid_names:
            with pytest.raises(ValueError, match="absolute path"):
                ResourceNameValidator.validate_resource_name(name)

    def test_reject_invalid_characters(self):
        """Test that invalid characters are rejected."""
        invalid_names = [
            "core.md",  # Dots not allowed (except in ..)
            "core;rm -rf",  # Shell injection attempt
            "core | cat",  # Pipe character
            "core&",  # Ampersand
            "core$USER",  # Variable expansion
            "core\x00",  # Null byte injection
            "CORE",  # Uppercase not allowed
            "Core",  # Mixed case not allowed
        ]

        for name in invalid_names:
            with pytest.raises(ValueError, match="must contain only"):
                ResourceNameValidator.validate_resource_name(name)


class TestPatternResourceRequest:
    """Test PatternResourceRequest Pydantic model."""

    def test_valid_request_default_language(self):
        """Test valid request with default language (python)."""
        request = PatternResourceRequest(name="core")
        assert request.name == "core"
        assert request.language == "python"

    def test_valid_request_explicit_language(self):
        """Test valid request with explicit language."""
        request = PatternResourceRequest(name="tooling", language="go")
        assert request.name == "tooling"
        assert request.language == "go"

    def test_reject_invalid_resource_name(self):
        """Test that invalid resource names trigger validation error."""
        with pytest.raises(ValidationError) as exc_info:
            PatternResourceRequest(name="../etc/passwd")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("name",)
        assert "parent directory" in errors[0]["msg"].lower()

    def test_reject_invalid_language(self):
        """Test that invalid language values trigger validation error."""
        # Uppercase not allowed
        with pytest.raises(ValidationError) as exc_info:
            PatternResourceRequest(name="core", language="Python")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("language",)

        # Numbers not allowed
        with pytest.raises(ValidationError) as exc_info:
            PatternResourceRequest(name="core", language="python3")

        errors = exc_info.value.errors()
        assert len(errors) == 1

    def test_language_pattern_validation(self):
        """Test that language pattern validation works."""
        # Valid languages
        valid_languages = ["python", "go", "rust", "java"]
        for lang in valid_languages:
            request = PatternResourceRequest(name="core", language=lang)
            assert request.language == lang

        # Invalid patterns (non-lowercase, non-alpha)
        invalid_languages = ["Python", "python3", "go-lang", "rust_lang"]
        for lang in invalid_languages:
            with pytest.raises(ValidationError):
                PatternResourceRequest(name="core", language=lang)


class TestResourceResponse:
    """Test ResourceResponse Pydantic model."""

    def test_valid_response(self):
        """Test valid resource response."""
        response = ResourceResponse(
            uri="mcp://resources/patterns/core",
            content="# Core Patterns\n\nImplementation patterns...",
            size_bytes=1024,
        )

        assert response.uri == "mcp://resources/patterns/core"
        assert "Core Patterns" in response.content
        assert response.size_bytes == 1024

    def test_response_validation(self):
        """Test that response fields are validated."""
        # Missing required fields
        with pytest.raises(ValidationError):
            ResourceResponse()

        # Invalid size_bytes (negative)
        with pytest.raises(ValidationError) as exc_info:
            ResourceResponse(
                uri="mcp://resources/patterns/core",
                content="content",
                size_bytes=-1,
            )

        errors = exc_info.value.errors()
        assert any(err["loc"] == ("size_bytes",) for err in errors)

    def test_response_examples(self):
        """Test that example URIs from schema are valid."""
        example_uris = [
            "mcp://resources/patterns/core",
            "mcp://resources/sdlc/core",
        ]

        for uri in example_uris:
            response = ResourceResponse(
                uri=uri,
                content="Example content",
                size_bytes=15,
            )
            assert response.uri == uri
