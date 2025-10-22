"""
MCP Resource API schemas.

Defines Pydantic models for MCP resource request and response payloads.
Includes validation for resource names to prevent path traversal attacks.
"""

from pydantic import BaseModel, Field, field_validator

# Artifact file name mapping (US-031, unified caching strategy)
# Maps simplified artifact names to full filenames for templates and generators
# Example: "prd" -> {"template": "prd-template.xml", "generator": "prd-generator.xml"}
ARTIFACT_FILE_MAP = {
    "vision": {
        "template": "product-vision-template.xml",
        "generator": "product-vision-generator.xml",
        "full_name": "product-vision",
    },
    "initiative": {
        "template": "initiative-template.xml",
        "generator": "initiative-generator.xml",
        "full_name": "initiative",
    },
    "epic": {
        "template": "epic-template.xml",
        "generator": "epic-generator.xml",
        "full_name": "epic",
    },
    "prd": {
        "template": "prd-template.xml",
        "generator": "prd-generator.xml",
        "full_name": "prd",
    },
    "hls": {
        "template": "hls-template.xml",
        "generator": "high-level-user-story-generator.xml",
        "full_name": "high-level-user-story",
    },
    "funcspec": {
        "template": "funcspec-template.xml",
        "generator": "funcspec-generator.xml",
        "full_name": "funcspec",
    },
    "story": {
        "template": "backlog-story-template.xml",
        "generator": "backlog-story-generator.xml",
        "full_name": "backlog-story",
    },
    "spike": {
        "template": "spike-template.xml",
        "generator": "spike-generator.xml",
        "full_name": "spike",
    },
    "adr": {
        "template": "adr-template.xml",
        "generator": "adr-generator.xml",
        "full_name": "adr",
    },
    "spec": {
        "template": "tech-spec-template.xml",
        "generator": "tech-spec-generator.xml",
        "full_name": "tech-spec",
    },
    "task": {
        "template": "implementation-task-template.xml",
        "generator": "implementation-task-generator.xml",
        "full_name": "implementation-task",
    },
}

# Backward compatibility: Keep TEMPLATE_FILE_MAP for existing code
TEMPLATE_FILE_MAP = {key: val["template"] for key, val in ARTIFACT_FILE_MAP.items()}


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
