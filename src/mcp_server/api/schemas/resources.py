"""
MCP Resource API schemas.

Defines Pydantic models for MCP resource request and response payloads.
Includes validation for resource names to prevent path traversal attacks.
"""

from pydantic import BaseModel, Field, field_validator

# Template name mapping (US-031)
# Maps simplified URI names to template filenames
# Example: "prd" -> "prd-template.xml"
TEMPLATE_FILE_MAP = {
    "vision": "product-vision-template.xml",
    "initiative": "initiative-template.xml",
    "epic": "epic-template.xml",
    "prd": "prd-template.xml",
    "hls": "hls-template.xml",
    "story": "backlog-story-template.xml",
    "spike": "spike-template.xml",
    "adr": "adr-template.xml",
    "spec": "tech-spec-template.xml",
    "task": "implementation-task-template.xml",
}


class ResourceResponse(BaseModel):
    """
    MCP resource response schema.

    Returns requested resource content with URI identifier.
    Used by Claude Code to fetch implementation patterns and SDLC framework content.
    """

    uri: str = Field(
        ...,
        description="Resource URI (e.g., mcp://resources/patterns/core)",
        examples=["mcp://resources/patterns/core", "mcp://resources/sdlc/core"],
    )
    content: str = Field(
        ...,
        description="Resource content as plain text (markdown format)",
    )
    size_bytes: int = Field(
        ...,
        description="Content size in bytes",
        ge=0,
    )


class ResourceNameValidator:
    """
    Validator for resource names to prevent path traversal attacks.

    Rejects:
    - Parent directory references (..)
    - Absolute paths (starting with /)
    - Non-alphanumeric characters (except underscores, hyphens, forward slashes)
    """

    @staticmethod
    def validate_resource_name(name: str) -> str:
        """
        Validate resource name to prevent path traversal.

        Args:
            name: Resource name to validate

        Returns:
            str: Validated resource name

        Raises:
            ValueError: If name contains path traversal sequences or invalid characters
        """
        # Check for path traversal attempts
        if ".." in name:
            raise ValueError("Resource name cannot contain parent directory references (..)")

        # Check for absolute paths
        if name.startswith("/"):
            raise ValueError("Resource name cannot be an absolute path")

        # Validate allowed characters: alphanumeric, underscore, hyphen, forward slash
        # Pattern: ^[a-z0-9_/-]+$
        import re

        if not re.match(r"^[a-z0-9_/-]+$", name):
            raise ValueError(
                "Resource name must contain only lowercase letters, numbers, "
                "underscores, hyphens, and forward slashes"
            )

        return name


class PatternResourceRequest(BaseModel):
    """
    Pattern resource request parameters.

    Validates resource name and language for pattern file retrieval.
    """

    name: str = Field(
        ...,
        description="Pattern resource name (e.g., 'core', 'tooling', 'testing')",
        examples=["core", "tooling", "testing", "typing", "validation"],
    )
    language: str = Field(
        default="python",
        description="Programming language subdirectory",
        pattern=r"^[a-z]+$",
        examples=["python", "go", "rust"],
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate resource name to prevent path traversal."""
        return ResourceNameValidator.validate_resource_name(v)

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate language parameter (lowercase alphabetic only)."""
        if not v.islower() or not v.isalpha():
            raise ValueError("Language must contain only lowercase letters")
        return v
