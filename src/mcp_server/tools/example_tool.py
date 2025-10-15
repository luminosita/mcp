"""
Example MCP tool implementation demonstrating key patterns.

This module serves as living documentation for implementing MCP tools, demonstrating:
- Pydantic input/output models with validation
- FastMCP @mcp.tool decorator usage
- Error handling for validation and business logic errors
- Dependency injection for accessing shared services
- Async patterns for consistency with production code
- Comprehensive docstrings explaining architectural decisions

WHY SIMPLE BUSINESS LOGIC:
The tool uses "greeting" logic to keep focus on architectural patterns rather than
domain-specific complexity. Real tools will have more complex business logic but should
follow these same structural patterns.
"""

import logging
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from mcp_server.config import Settings
from mcp_server.core.exceptions import BusinessLogicError


class GreetingStyle(str, Enum):
    """
    Enumeration of supported greeting styles.

    WHY ENUM: Type-safe enumeration prevents invalid style values at compile time
    and provides clear documentation of supported options for LLM agents.
    """

    FORMAL = "formal"
    CASUAL = "casual"
    ENTHUSIASTIC = "enthusiastic"


class GreetingInput(BaseModel):
    """
    Input model for example greeting tool.

    WHY PYDANTIC: Automatic validation prevents runtime errors from invalid inputs.
    Field constraints (min_length, max_length, pattern) enforce business rules
    before business logic executes.

    WHY FIELD DESCRIPTIONS: LLM agents use field descriptions to understand parameter
    usage and provide appropriate values. Clear descriptions reduce tool misuse.
    """

    name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description="Name to greet (1-100 characters, alphabetic with spaces/hyphens)",
        ),
    ]

    style: Annotated[
        GreetingStyle,
        Field(
            default=GreetingStyle.CASUAL,
            description="Greeting style: formal, casual, or enthusiastic",
        ),
    ]

    message: Annotated[
        str | None,
        Field(
            default=None,
            max_length=500,
            description="Optional custom message to include (max 500 characters)",
        ),
    ]

    @field_validator("name")
    @classmethod
    def validate_name_format(cls, v: str) -> str:
        """
        Validate name contains only letters, spaces, and hyphens.

        WHY CUSTOM VALIDATOR: Prevents injection attacks and ensures name format
        meets business requirements beyond simple type checking.

        Raises:
            ValueError: If name contains invalid characters
        """
        if not all(c.isalpha() or c.isspace() or c == "-" for c in v):
            raise ValueError("Name must contain only letters, spaces, and hyphens")
        return v.strip()


class GreetingOutput(BaseModel):
    """
    Output model for example greeting tool.

    WHY TYPED OUTPUT: Structured output with type hints enables:
    - Static type checking in consumers
    - Automatic JSON schema generation
    - Clear contract documentation
    - Consistent serialization
    """

    greeting: Annotated[str, Field(description="Formatted greeting message")]
    style_used: Annotated[str, Field(description="Greeting style that was applied")]
    character_count: Annotated[int, Field(description="Length of greeting message")]
    metadata: Annotated[
        dict[str, str],
        Field(description="Additional metadata about greeting generation"),
    ]


async def generate_greeting(
    params: GreetingInput,
    settings: Settings,
    logger: logging.Logger,
) -> GreetingOutput:
    """
    Generate a personalized greeting message.

    This is an example tool demonstrating MCP server patterns. Real tools would
    have more complex business logic but should follow the same structural patterns:
    - Pydantic validation for inputs/outputs
    - Dependency injection for shared services
    - Async functions for consistency
    - Clear error handling
    - Comprehensive logging

    WHY ASYNC: Even though this function has no I/O operations, it uses async/await
    for consistency with production tools that make database queries or API calls.
    This pattern makes it easy to add async operations later without refactoring.

    WHY DEPENDENCY INJECTION: Accessing settings and logger through function parameters
    (rather than global imports) enables:
    - Easy testing with mocked dependencies
    - Different configurations per request
    - Request-scoped logging context
    - No hidden dependencies

    Args:
        params: Validated greeting input parameters
        settings: Application configuration (injected)
        logger: Structured logger instance (injected)

    Returns:
        GreetingOutput: Structured greeting response with metadata

    Raises:
        BusinessLogicError: If greeting generation fails business rules
        ValidationError: If input validation fails (raised by Pydantic)

    Example:
        ```python
        # Valid input
        params = GreetingInput(name="Alice", style=GreetingStyle.FORMAL)
        result = await generate_greeting(params, settings, logger)
        assert result.greeting == "Good day, Alice"

        # Invalid input (Pydantic raises ValidationError)
        params = GreetingInput(name="", style="invalid")  # Fails validation
        ```
    """
    logger.info(
        f"Generating greeting: name={params.name}, style={params.style.value}, "
        f"has_custom_message={params.message is not None}"
    )

    try:
        # Business logic: Generate greeting based on style
        if params.style == GreetingStyle.FORMAL:
            greeting_prefix = "Good day"
        elif params.style == GreetingStyle.CASUAL:
            greeting_prefix = "Hey"
        elif params.style == GreetingStyle.ENTHUSIASTIC:
            greeting_prefix = "Hello there"
        else:
            # This should never happen due to Enum validation, but defensive programming
            raise BusinessLogicError(
                f"Unsupported greeting style: {params.style}",
                details={"style": params.style.value, "name": params.name},
            )

        # Construct greeting message
        greeting = f"{greeting_prefix}, {params.name}"

        # Append custom message if provided
        greeting = f"{greeting}! {params.message}" if params.message else f"{greeting}!"

        # Business rule: Greeting must not exceed app-configured maximum length
        max_greeting_length = 600  # Could come from settings
        if len(greeting) > max_greeting_length:
            raise BusinessLogicError(
                f"Generated greeting exceeds maximum length of {max_greeting_length} characters",
                details={
                    "greeting_length": str(len(greeting)),
                    "max_length": str(max_greeting_length),
                    "name": params.name,
                },
            )

        # Prepare response with metadata
        metadata = {
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "style": params.style.value,
        }

        logger.info(
            f"Greeting generated successfully: length={len(greeting)}, style={params.style.value}"
        )

        return GreetingOutput(
            greeting=greeting,
            style_used=params.style.value,
            character_count=len(greeting),
            metadata=metadata,
        )

    except BusinessLogicError:
        # Re-raise business logic errors without wrapping
        logger.error(
            f"Business logic error during greeting generation: name={params.name}, "
            f"style={params.style.value}"
        )
        raise

    except Exception as e:
        # Catch unexpected errors and wrap in BusinessLogicError
        logger.exception(
            f"Unexpected error during greeting generation: name={params.name}, "
            f"style={params.style.value}, error={e!s}"
        )
        raise BusinessLogicError(
            "Failed to generate greeting due to unexpected error",
            details={"error": str(e), "name": params.name},
        ) from e
