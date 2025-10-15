# Extension Guide: Adding a New MCP Tool

**Last Updated**: 2025-10-15
**Version**: 1.0
**Status**: Active

## Purpose

This guide provides step-by-step instructions for implementing new MCP tools following established patterns from the example tool (US-011).

**After following this guide, you will have**:
- A new MCP tool registered with the server
- Type-safe input/output validation
- Proper error handling and logging
- Comprehensive unit tests
- Integration with dependency injection

**Prerequisites**:
- Python 3.11+ environment set up
- Understanding of Pydantic models
- Familiarity with async/await patterns

---

## Step 1: Define Input Model

Create Pydantic model for tool input with validation rules.

**File**: `src/mcp_server/tools/my_new_tool.py`

```python
"""
My New Tool implementation.

Brief description of what this tool does and when to use it.
"""

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class MyToolInput(BaseModel):
    """
    Input model for my_new_tool.

    Include docstring explaining:
    - What each field represents
    - Valid value ranges/patterns
    - When agents should use this tool
    """

    # Required field with validation
    resource_id: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            pattern=r"^[A-Za-z0-9_-]+$",
            description="Unique identifier for the resource (alphanumeric, underscore, hyphen)",
        ),
    ]

    # Optional field with default
    include_details: Annotated[
        bool,
        Field(
            default=False,
            description="Whether to include detailed information in response",
        ),
    ]

    # Enum field for type-safe options
    output_format: Annotated[
        str,
        Field(
            default="json",
            pattern="^(json|yaml|text)$",
            description="Output format: json, yaml, or text",
        ),
    ]

    @field_validator("resource_id")
    @classmethod
    def validate_resource_id_safe(cls, v: str) -> str:
        """
        Validate resource_id is safe (no injection attacks).

        Raises:
            ValueError: If resource_id contains invalid characters
        """
        # Add custom validation logic
        if ".." in v or "/" in v:
            raise ValueError("Resource ID cannot contain '..' or '/'")
        return v
```

**Key Patterns**:
- Use `Annotated[type, Field(...)]` for all fields
- Add `description` to help LLM agents understand field purpose
- Use `Field(min_length, max_length, pattern)` for declarative validation
- Add custom validators with `@field_validator` for complex rules
- Validate for security (prevent injection attacks, path traversal)

**Reference**: See `src/mcp_server/tools/example_tool.py:41-94` for complete example.

---

## Step 2: Define Output Model

Create Pydantic model for structured tool output.

```python
class MyToolOutput(BaseModel):
    """
    Output model for my_new_tool.

    Explain what information is returned and how agents should use it.
    """

    resource_name: Annotated[str, Field(description="Name of the resource")]

    status: Annotated[
        str,
        Field(description="Current status of the resource"),
    ]

    details: Annotated[
        dict[str, str] | None,
        Field(
            default=None,
            description="Detailed information (if include_details=True)",
        ),
    ]

    metadata: Annotated[
        dict[str, str],
        Field(description="Metadata about the operation"),
    ]
```

**Key Patterns**:
- Use typed fields (`str`, `int`, `dict[str, str]`, `list[MyModel]`)
- Optional fields use `| None` with `default=None`
- Include `metadata` dict for operation context (tool version, timestamp, etc.)
- Add descriptions for all fields

---

## Step 3: Implement Business Logic Function

Create core business logic function with dependency injection.

```python
import logging
from mcp_server.config import Settings
from mcp_server.core.exceptions import BusinessLogicError


async def process_my_tool(
    params: MyToolInput,
    settings: Settings,
    logger: logging.Logger,
) -> MyToolOutput:
    """
    Process my_new_tool request.

    This is the testable business logic function (separate from MCP registration).

    Args:
        params: Validated input parameters
        settings: Application configuration (injected)
        logger: Structured logger instance (injected)

    Returns:
        MyToolOutput: Structured output with results

    Raises:
        BusinessLogicError: If business rules violated or operation fails
    """
    logger.info(
        "Processing my_new_tool",
        extra={
            "resource_id": params.resource_id,
            "include_details": params.include_details,
        },
    )

    try:
        # 1. Implement business logic
        resource_name = f"Resource-{params.resource_id}"
        status = "active"

        # 2. Apply business rules
        if params.resource_id.startswith("test-"):
            # Example business rule
            raise BusinessLogicError(
                "Test resources cannot be processed",
                details={"resource_id": params.resource_id},
            )

        # 3. Prepare details if requested
        details = None
        if params.include_details:
            details = {
                "created_at": "2025-10-15T10:30:00Z",
                "updated_at": "2025-10-15T12:00:00Z",
            }

        # 4. Prepare metadata
        metadata = {
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "tool": "my_new_tool",
        }

        logger.info(
            "Tool processing complete",
            extra={"resource_id": params.resource_id, "status": status},
        )

        return MyToolOutput(
            resource_name=resource_name,
            status=status,
            details=details,
            metadata=metadata,
        )

    except BusinessLogicError:
        # Re-raise business logic errors as-is
        logger.error("Business logic error", extra={"resource_id": params.resource_id})
        raise

    except Exception as e:
        # Wrap unexpected errors in BusinessLogicError
        logger.exception("Unexpected error", extra={"error": str(e)})
        raise BusinessLogicError(
            "Failed to process tool due to unexpected error",
            details={"error": str(e), "resource_id": params.resource_id},
        ) from e
```

**Key Patterns**:
- Accept dependencies as parameters (`settings`, `logger`)
- Log tool invocation with structured data (`extra` dict)
- Raise `BusinessLogicError` for business rule violations
- Catch unexpected exceptions and wrap in `BusinessLogicError`
- Include `metadata` in output (app version, tool name)

---

## Step 4: Register MCP Tool Wrapper

Create thin MCP tool wrapper that accesses dependencies and calls business logic.

```python
# At the end of my_new_tool.py, or in main.py if preferred

from mcp_server.main import mcp  # Import FastMCP instance


@mcp.tool(
    name="my_namespace.my_new_tool",
    description="""
    Brief description of tool purpose and when agents should use it.

    Use this tool when:
    - Scenario 1 description
    - Scenario 2 description

    Input parameters:
    - resource_id: Unique identifier for resource
    - include_details: Whether to include detailed information
    - output_format: Output format (json/yaml/text)

    Returns structured information about the resource including name, status,
    and optional detailed information.
    """,
)
async def my_new_tool_mcp(params: MyToolInput) -> MyToolOutput:
    """
    MCP tool wrapper for my_new_tool.

    This is a thin wrapper that accesses dependencies and delegates to
    business logic function.

    Args:
        params: Validated input parameters

    Returns:
        MyToolOutput: Structured output

    Raises:
        BusinessLogicError: If processing fails
    """
    # Access dependencies directly (not as function parameters)
    from mcp_server.config import settings
    from mcp_server.core.dependencies import get_logger

    logger = get_logger("mcp_server.tools.my_new_tool")

    # Delegate to business logic function
    return await process_my_tool(params, settings, logger)
```

**Key Patterns**:
- Use namespace in tool name (`my_namespace.my_new_tool`) to group related tools
- Provide comprehensive description (when to use, what it does)
- Access dependencies directly inside function (FastMCP limitation)
- Delegate to business logic function immediately (thin wrapper)

**Why Separate Wrapper and Business Logic?**:
- Business logic function testable with mocked dependencies
- Business logic reusable in different contexts (REST API, CLI, batch jobs)
- Clear separation between protocol (FastMCP) and domain logic

---

## Step 5: Register Tool in main.py

If tool wrapper is in separate module, import and register in `main.py`.

**Option A: Define wrapper in tool module** (recommended for organization):

```python
# src/mcp_server/tools/my_new_tool.py

from mcp_server.main import mcp

@mcp.tool(name="my_namespace.my_new_tool")
async def my_new_tool_mcp(params: MyToolInput) -> MyToolOutput:
    ...
```

**Option B: Import and register in main.py** (recommended for visibility):

```python
# src/mcp_server/main.py

from mcp_server.tools.my_new_tool import (
    MyToolInput,
    MyToolOutput,
    process_my_tool,
)

@mcp.tool(name="my_namespace.my_new_tool", description="...")
async def my_new_tool_mcp(params: MyToolInput) -> MyToolOutput:
    from mcp_server.config import settings
    from mcp_server.core.dependencies import get_logger

    logger = get_logger("mcp_server.tools.my_new_tool")
    return await process_my_tool(params, settings, logger)
```

**Recommendation**: Use Option A for cleaner organization (tool definition in tool module), but ensure tool module is imported in `main.py` so decorator executes.

---

## Step 6: Write Unit Tests

Create comprehensive unit tests with mocked dependencies.

**File**: `tests/unit/test_my_new_tool.py`

```python
import pytest
from unittest.mock import MagicMock
from mcp_server.tools.my_new_tool import (
    MyToolInput,
    process_my_tool,
)
from mcp_server.core.exceptions import BusinessLogicError


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    settings = MagicMock()
    settings.app_name = "Test App"
    settings.app_version = "1.0.0"
    return settings


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    return MagicMock()


@pytest.mark.asyncio
async def test_process_my_tool_success(mock_settings, mock_logger):
    """Test successful tool processing."""
    # Arrange
    params = MyToolInput(
        resource_id="resource-123",
        include_details=True,
        output_format="json",
    )

    # Act
    result = await process_my_tool(params, mock_settings, mock_logger)

    # Assert
    assert result.resource_name == "Resource-resource-123"
    assert result.status == "active"
    assert result.details is not None
    assert result.metadata["app_name"] == "Test App"

    # Verify logging
    mock_logger.info.assert_called()


@pytest.mark.asyncio
async def test_process_my_tool_business_rule_violation(mock_settings, mock_logger):
    """Test business rule violation (test resources rejected)."""
    # Arrange
    params = MyToolInput(resource_id="test-123")

    # Act & Assert
    with pytest.raises(BusinessLogicError) as exc_info:
        await process_my_tool(params, mock_settings, mock_logger)

    assert "Test resources cannot be processed" in str(exc_info.value)
    assert exc_info.value.details["resource_id"] == "test-123"


@pytest.mark.asyncio
async def test_process_my_tool_invalid_input():
    """Test Pydantic validation for invalid input."""
    # Act & Assert
    with pytest.raises(ValueError):
        MyToolInput(resource_id="../etc/passwd")  # Path traversal attempt


@pytest.mark.asyncio
async def test_process_my_tool_without_details(mock_settings, mock_logger):
    """Test tool processing without detailed information."""
    # Arrange
    params = MyToolInput(resource_id="resource-456", include_details=False)

    # Act
    result = await process_my_tool(params, mock_settings, mock_logger)

    # Assert
    assert result.details is None
```

**Key Patterns**:
- Use `pytest.mark.asyncio` for async test functions
- Mock dependencies (settings, logger) with fixtures
- Test success cases and error cases
- Test Pydantic validation (invalid inputs)
- Verify logging with `mock_logger.info.assert_called()`

**Reference**: See `tests/unit/test_example_tool.py` for complete examples.

---

## Step 7: Write Integration Tests (Optional)

Create integration tests with real MCP protocol if needed.

**File**: `tests/integration/test_my_new_tool_mcp.py`

```python
import pytest
from fastapi.testclient import TestClient
from mcp_server.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_my_new_tool_registered(client):
    """Test tool is registered with MCP server."""
    # TODO: Test tool discovery endpoint
    # This requires understanding MCP client-server protocol
    pass
```

**Note**: Integration testing with MCP protocol requires MCP client setup. For most tools, comprehensive unit tests are sufficient.

---

## Step 8: Verify Tool Works

Test tool manually before deploying.

### Check Tool Registration

```bash
# Start server
task dev

# Tool should appear in server startup logs
grep "my_new_tool" logs/mcp_server.log
```

### Test with MCP Client

Use Claude Desktop or MCP inspector to invoke tool:

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "my_namespace.my_new_tool",
    "arguments": {
      "resource_id": "test-resource",
      "include_details": true
    }
  },
  "id": 1
}
```

### Run Tests

```bash
# Run unit tests
task test

# Run with coverage
task test-cov

# Verify >80% coverage for new tool
```

---

## Common Patterns

### Pattern 1: Database Access

```python
from mcp_server.core.dependencies import SessionDep
from sqlalchemy import select

async def my_tool_with_db(
    params: MyToolInput,
    session: AsyncSession,
    logger: logging.Logger,
) -> MyToolOutput:
    # Query database
    result = await session.execute(select(MyModel).where(MyModel.id == params.resource_id))
    record = result.scalar_one_or_none()

    if not record:
        raise BusinessLogicError(f"Resource {params.resource_id} not found")

    return MyToolOutput(resource_name=record.name, ...)
```

See [add-database-access.md](add-database-access.md) for detailed database patterns.

### Pattern 2: External API Call

```python
from mcp_server.core.dependencies import HttpClientDep
import httpx

async def my_tool_with_api(
    params: MyToolInput,
    client: httpx.AsyncClient,
    logger: logging.Logger,
) -> MyToolOutput:
    try:
        response = await client.get(
            f"https://api.example.com/resources/{params.resource_id}",
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()

        return MyToolOutput(resource_name=data["name"], ...)

    except httpx.TimeoutException:
        raise BusinessLogicError("External API timeout", details={"resource_id": params.resource_id})
    except httpx.HTTPStatusError as e:
        raise BusinessLogicError(
            f"External API error: {e.response.status_code}",
            details={"resource_id": params.resource_id, "status_code": str(e.response.status_code)},
        )
```

See [add-external-service.md](add-external-service.md) for detailed external service patterns.

### Pattern 3: Enum-Based Options

```python
from enum import Enum

class OutputFormat(str, Enum):
    """Output format options."""
    JSON = "json"
    YAML = "yaml"
    TEXT = "text"

class MyToolInput(BaseModel):
    format: Annotated[OutputFormat, Field(default=OutputFormat.JSON)]

# Usage
if params.format == OutputFormat.JSON:
    # Handle JSON output
    ...
```

---

## Checklist

Before considering tool complete:

- [ ] Input model defined with Pydantic validation
- [ ] Output model defined with typed fields
- [ ] Business logic function implements core logic with DI
- [ ] MCP tool wrapper registered with `@mcp.tool()` decorator
- [ ] Tool name follows namespace convention (`namespace.tool_name`)
- [ ] Comprehensive description provided (when to use, what it does)
- [ ] Error handling covers business logic and unexpected errors
- [ ] Structured logging with contextual information
- [ ] Unit tests written for success and error cases
- [ ] Test coverage >80% for new tool code
- [ ] Type checking passes (`task lint:types`)
- [ ] Linting passes (`task lint`)
- [ ] Tool tested manually with MCP client

---

## Related Documentation

- **Example Tool**: `src/mcp_server/tools/example_tool.py` - Complete reference implementation
- **Dependency Injection**: [../dependency-injection.md](../dependency-injection.md) - DI patterns
- **Request Flow**: [../request-flow.md](../request-flow.md) - Tool invocation lifecycle
- **Database Access**: [add-database-access.md](add-database-access.md) - Database patterns
- **External Services**: [add-external-service.md](add-external-service.md) - API integration patterns

### CLAUDE.md Standards

- **CLAUDE-typing.md**: Type hints, annotations
- **CLAUDE-testing.md**: Testing patterns, fixtures
- **CLAUDE-validation.md**: Input validation, security

---

## Changelog

- **2025-10-15** (v1.0): Initial extension guide (US-013)
