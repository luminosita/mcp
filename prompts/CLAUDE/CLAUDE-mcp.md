# CLAUDE-mcp.md - Model Context Protocol (MCP) Tool Implementation

> **Purpose**: Guidelines for implementing MCP tools with FastMCP SDK, including critical patterns learned from US-011 implementation.

## 📚 Related Documentation
- **[CLAUDE-core.md](./CLAUDE-core.md)** - Core development philosophy
- **[CLAUDE-validation-models.md](./CLAUDE-validation-models.md)** - Pydantic validation patterns
- **[CLAUDE-typing.md](./CLAUDE-typing.md)** - Type safety requirements

---

## 🎯 Core Principle: Pydantic-Serializable Parameters Only

**CRITICAL**: FastMCP generates JSON schema from all function parameters. MCP tool functions **MUST have ONLY Pydantic-serializable parameters**.

### ✅ Allowed Parameter Types
- Pydantic `BaseModel` subclasses
- Primitive types: `str`, `int`, `float`, `bool`
- Collections: `list`, `dict`, `tuple`, `set` (of serializable types)
- `Optional` types, `Union` types
- `Enum` subclasses

### ❌ Forbidden Parameter Types
- `logging.Logger` instances
- Database sessions (`AsyncSession`, `Session`)
- HTTP clients (`httpx.AsyncClient`, `requests.Session`)
- Settings objects (unless Pydantic `BaseSettings`)
- File handles, sockets, connections
- Any non-Pydantic class instances

### Error if Violated
```python
# ❌ THIS WILL FAIL
@mcp.tool(name="example")
async def bad_tool(
    params: MyInput,
    logger: logging.Logger,  # ❌ Cannot serialize to JSON schema
    settings: Settings,       # ❌ Cannot serialize to JSON schema
) -> MyOutput:
    pass

# Error at registration time:
# PydanticInvalidForJsonSchema: Cannot generate a JsonSchema for
# core_schema.IsInstanceSchema (<class 'logging.Logger'>)
```

---

## 🏗️ MCP Tool Implementation Pattern

### Tool Structure Template

```python
from enum import Enum
from typing import Annotated
import logging

from pydantic import BaseModel, Field, field_validator
from mcp_server.config import settings  # Module-level access
from mcp_server.core.exceptions import BusinessLogicError


class ToolStyle(str, Enum):
    """
    Enumeration for type-safe options.

    WHY ENUM: Provides compile-time type safety and clear documentation
    of supported options for LLM agents.
    """
    OPTION_A = "option_a"
    OPTION_B = "option_b"


class ToolInput(BaseModel):
    """
    Input model for MCP tool.

    WHY PYDANTIC: Automatic validation prevents runtime errors from
    invalid inputs. Field constraints enforce business rules before
    business logic executes.

    WHY FIELD DESCRIPTIONS: LLM agents use field descriptions to
    understand parameter usage and provide appropriate values.
    """

    name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description="Name parameter (1-100 characters)",
        ),
    ]

    style: Annotated[
        ToolStyle,
        Field(
            default=ToolStyle.OPTION_A,
            description="Processing style to apply",
        ),
    ]

    @field_validator("name")
    @classmethod
    def validate_name_format(cls, v: str) -> str:
        """
        Custom validation for security or business rules.

        WHY CUSTOM VALIDATOR: Prevents injection attacks and ensures
        input meets business requirements beyond simple type checking.
        """
        if not v.isalpha():
            raise ValueError("Name must contain only letters")
        return v.strip()


class ToolOutput(BaseModel):
    """
    Output model for MCP tool.

    WHY TYPED OUTPUT: Structured output with type hints enables:
    - Static type checking in consumers
    - Automatic JSON schema generation
    - Clear contract documentation
    - Consistent serialization
    """

    result: Annotated[str, Field(description="Processing result")]
    metadata: Annotated[dict[str, str], Field(description="Additional metadata")]


async def process_tool_logic(
    params: ToolInput,
    settings: Settings,
    logger: logging.Logger,
) -> ToolOutput:
    """
    Business logic for tool (separate from MCP registration).

    WHY SEPARATE: Enables:
    - Testing business logic without MCP protocol overhead
    - Reusing business logic in different contexts (REST API, CLI)
    - Clear separation between protocol concerns and domain logic

    Args:
        params: Validated tool input parameters
        settings: Application configuration (injected)
        logger: Structured logger (injected)

    Returns:
        ToolOutput: Structured tool response

    Raises:
        BusinessLogicError: If processing fails business rules
        ValidationError: If input validation fails (raised by Pydantic)
    """
    logger.info(f"Processing tool: name={params.name}, style={params.style.value}")

    try:
        # Business logic implementation
        result = f"Processed: {params.name}"

        # Business rule validation
        if len(result) > 500:
            raise BusinessLogicError(
                "Result exceeds maximum length",
                details={"result_length": str(len(result)), "max_length": "500"},
            )

        metadata = {
            "app_name": settings.app_name,
            "style": params.style.value,
        }

        logger.info(f"Processing successful: result_length={len(result)}")

        return ToolOutput(result=result, metadata=metadata)

    except BusinessLogicError:
        logger.error(f"Business logic error: name={params.name}")
        raise

    except Exception as e:
        logger.exception(f"Unexpected error: name={params.name}, error={e!s}")
        raise BusinessLogicError(
            "Processing failed due to unexpected error",
            details={"error": str(e)},
        ) from e
```

### MCP Tool Registration

```python
# In main.py or tool registration module
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="AI Agent MCP Server")


@mcp.tool(
    name="example.process",
    description="""
    Processes input with specified style (example tool for pattern demonstration).

    Use this tool when:
    - Demonstrating MCP tool patterns to developers
    - Testing MCP server functionality
    - Learning tool implementation best practices

    This is an example tool showing:
    - Pydantic input/output validation
    - Error handling for validation and business logic
    - Enum-based type-safe options
    - Comprehensive docstrings

    Processing styles:
    - option_a: Standard processing
    - option_b: Alternative processing

    Returns structured result with metadata.
    """,
)
async def example_tool(params: ToolInput) -> ToolOutput:
    """
    MCP tool wrapper for process_tool_logic function.

    WHY WRAPPER: Separates MCP tool registration (@mcp.tool decorator)
    from business logic. This enables testing and reuse without MCP.

    WHY NO DEPENDENCY PARAMETERS: FastMCP generates JSON schema from
    function signature, so only Pydantic-serializable types allowed.
    Dependencies accessed directly inside function instead.

    Args:
        params: Validated tool input parameters

    Returns:
        ToolOutput: Structured tool response

    Raises:
        BusinessLogicError: If processing fails business rules
        ValidationError: If input validation fails (handled by Pydantic/FastMCP)
    """
    import logging

    # Access dependencies directly (not as function parameters)
    # WHY: FastMCP requires all parameters to be Pydantic-serializable
    # for JSON schema generation. Logger and Settings can't be serialized.
    logger = logging.getLogger("mcp_server.tools.example")
    return await process_tool_logic(params, settings, logger)
```

---

## 🔍 Dependency Access Patterns

### Accessing Settings

```python
# Module-level import
from mcp_server.config import settings

@mcp.tool(name="example.tool")
async def tool(params: Input) -> Output:
    # Access settings directly inside function
    app_name = settings.app_name
    debug_mode = settings.debug
    return process(params, settings)
```

### Accessing Logger

```python
import logging

@mcp.tool(name="example.tool")
async def tool(params: Input) -> Output:
    # Create logger inside function
    logger = logging.getLogger("mcp_server.tools.example")
    logger.info(f"Tool invoked: {params}")
    return process(params, logger)
```

### Accessing Database Session

```python
from mcp_server.core.dependencies import get_db_session

@mcp.tool(name="example.tool")
async def tool(params: Input) -> Output:
    # Get session from dependency provider inside function
    async for session in get_db_session():
        result = await query_database(session, params)
        return Output(result=result)
```

### Accessing HTTP Client

```python
from mcp_server.core.dependencies import get_http_client

@mcp.tool(name="example.tool")
async def tool(params: Input) -> Output:
    # Get client from dependency provider inside function
    client = get_http_client()
    response = await client.get(f"https://api.example.com/{params.id}")
    return Output(data=response.json())
```

---

## 📝 Tool Description Best Practices

### LLM-Friendly Descriptions

Tool descriptions are read by LLM agents to decide when and how to use tools. Write from the LLM's perspective:

```python
@mcp.tool(
    name="jira.create_issue",
    description="""
    Creates a new JIRA issue in the specified project.

    Use this tool when:
    - A user requests creation of a task, bug, or feature
    - You need to track work items discovered during analysis
    - Converting discussion into actionable work

    DO NOT use this tool for:
    - Querying existing issues (use jira.search_issues instead)
    - Updating issues (use jira.update_issue instead)

    Required parameters:
    - project: JIRA project key (e.g., "ENG", "PROD")
    - summary: Brief description of the issue (50-255 characters)

    Optional parameters:
    - description: Detailed explanation with acceptance criteria
    - issue_type: "Task", "Bug", "Story" (default: "Task")
    - priority: 1-5 (1=Highest, 5=Lowest, default: 3)

    Returns:
    - issue_key: Created issue identifier (e.g., "ENG-123")
    - url: Link to view the issue in JIRA

    Example usage:
    "Create a bug for login failure" → Creates Bug in current project
    """,
)
async def create_jira_issue(params: CreateIssueInput) -> CreateIssueOutput:
    pass
```

### Description Structure

1. **What**: One-sentence summary of tool purpose
2. **When**: Bullet list of scenarios to use this tool
3. **When NOT**: Bullet list of scenarios to avoid (if applicable)
4. **Parameters**: Required vs optional, with examples
5. **Returns**: What the tool outputs
6. **Example**: Brief usage example showing input → output

---

## ⚠️ Common Anti-Patterns

### Anti-Pattern 1: Non-Serializable Parameters

```python
# ❌ WRONG - Will fail at registration
@mcp.tool(name="bad.tool")
async def bad_tool(
    params: Input,
    logger: logging.Logger,  # Cannot serialize to JSON schema!
) -> Output:
    pass

# ✅ CORRECT - Access logger inside function
@mcp.tool(name="good.tool")
async def good_tool(params: Input) -> Output:
    logger = logging.getLogger("mcp_server.tools.good")
    logger.info("Tool invoked")
    return process(params)
```

### Anti-Pattern 2: Overly Broad Tool Scope

```python
# ❌ WRONG - Too many operations in one tool
@mcp.tool(name="jira.manage")
async def jira_manage(
    action: Literal["create", "update", "delete", "query"],
    # ... 20 optional parameters
) -> dict:
    if action == "create":
        # Complex logic
    elif action == "update":
        # Different logic
    # LLMs struggle with tools having many conditional behaviors

# ✅ CORRECT - Focused single-purpose tools
@mcp.tool(name="jira.create_issue")
async def create_issue(params: CreateInput) -> CreateOutput:
    # Simple, clear implementation

@mcp.tool(name="jira.update_issue")
async def update_issue(params: UpdateInput) -> UpdateOutput:
    # Simple, focused on one task
```

### Anti-Pattern 3: Blocking Calls in Async Functions

```python
# ❌ WRONG - Blocking event loop
import requests

@mcp.tool(name="bad.fetch")
async def bad_fetch(url: str) -> dict:
    response = requests.get(url)  # Blocks entire event loop!
    return response.json()

# ✅ CORRECT - Async all the way
import httpx

@mcp.tool(name="good.fetch")
async def good_fetch(url: str) -> dict:
    client = get_http_client()
    response = await client.get(url)
    return response.json()
```

---

## 🧪 Testing MCP Tools

### Testing Business Logic (Without MCP)

```python
import pytest
from mcp_server.tools.example_tool import process_tool_logic, ToolInput, ToolStyle

@pytest.mark.asyncio
async def test_process_tool_logic_success(mock_settings, mock_logger):
    """Tests business logic with mocked dependencies."""
    # Arrange
    params = ToolInput(name="Alice", style=ToolStyle.OPTION_A)

    # Act
    result = await process_tool_logic(params, mock_settings, mock_logger)

    # Assert
    assert result.result == "Processed: Alice"
    assert result.metadata["style"] == "option_a"
    mock_logger.info.assert_called()


@pytest.mark.asyncio
async def test_process_tool_logic_validation_error():
    """Tests Pydantic validation of invalid inputs."""
    with pytest.raises(ValueError) as exc_info:
        ToolInput(name="Alice123", style=ToolStyle.OPTION_A)

    assert "must contain only letters" in str(exc_info.value)
```

### Testing MCP Tool Registration (Integration)

```python
import pytest
from mcp_server.main import mcp

def test_tool_registered():
    """Verify tool is registered with FastMCP server."""
    tool_names = [tool.name for tool in mcp.list_tools()]
    assert "example.process" in tool_names


@pytest.mark.asyncio
async def test_tool_invocation():
    """Test tool invocation through MCP protocol."""
    # Invoke tool through MCP
    result = await mcp.call_tool(
        "example.process",
        {"name": "Alice", "style": "option_a"},
    )

    # Verify response structure
    assert result["result"] == "Processed: Alice"
    assert "metadata" in result
```

---

## 🚀 Production Checklist

Before deploying MCP tools to production:

### Type Safety
- [ ] All tool functions have type hints (100% coverage)
- [ ] Only Pydantic-serializable parameters used
- [ ] `mypy --strict` passes with zero errors

### Validation
- [ ] All inputs validated with Pydantic models
- [ ] Custom validators for security-critical fields
- [ ] Error messages are clear and actionable

### Error Handling
- [ ] Validation errors caught and logged
- [ ] Business logic errors wrapped in BusinessLogicError
- [ ] Unexpected errors logged with full context

### Documentation
- [ ] Tool description explains WHEN to use
- [ ] Tool description explains WHEN NOT to use
- [ ] Parameter descriptions are clear
- [ ] Return value structure documented

### Testing
- [ ] Business logic has unit tests (>80% coverage)
- [ ] Pydantic validation tested (valid + invalid inputs)
- [ ] Error handling tested (all failure modes)
- [ ] MCP tool registration verified

### Performance
- [ ] Async/await used consistently
- [ ] No blocking calls in async functions
- [ ] Database connections properly managed
- [ ] HTTP clients reused (connection pooling)

---

## 📖 Reference Implementation

See `src/mcp_server/tools/example_tool.py` for complete working example demonstrating all patterns.

---

**Document Version**: 1.0
**Last Updated**: 2025-10-15
**Related Story**: US-011 Example MCP Tool Implementation
