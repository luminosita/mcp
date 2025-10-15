# Design Decisions and Technology Rationale

**Last Updated**: 2025-10-15
**Version**: 1.0
**Status**: Active

## Purpose

This document explains WHY key architectural and technology decisions were made, providing context for evaluating alternatives and proposing improvements.

**After reading this document, you should understand**:
- Rationale behind technology choices (FastAPI, Pydantic, FastMCP, etc.)
- Trade-offs considered for each decision
- References to Implementation Research supporting decisions
- Context for proposing architectural changes

**Target Audience**: Senior engineers evaluating architecture, architects, technical leads.

---

## Decision 1: FastAPI as Web Framework

### Decision

Use **FastAPI 0.100+** as the primary web framework for the MCP server.

### Rationale

**Key Advantages**:
1. **Async Performance**: Native async/await support for I/O-bound workloads (database queries, external API calls)
2. **Pydantic Integration**: Built-in Pydantic validation for request/response models (type safety across entire stack)
3. **Auto-Generated Documentation**: OpenAPI spec generation (`/docs`, `/redoc`) with zero manual configuration
4. **Developer Experience**: Modern Python type hints, auto-completion in IDEs, clear error messages
5. **Dependency Injection**: Built-in DI system for managing shared services (settings, logger, database, HTTP client)

**Alternatives Considered**:

| Framework | Pros | Cons | Decision |
|-----------|------|------|----------|
| **Flask** | Simple, mature, large ecosystem | No async support, manual validation, no type safety | ❌ Rejected - async required for MCP |
| **Django** | Full-featured, ORM included, admin UI | Heavy, synchronous, slower for async workloads | ❌ Rejected - overkill, not async-first |
| **FastAPI** | Async, Pydantic, DI, modern | Younger ecosystem than Flask/Django | ✅ **Selected** |

**Implementation Research Reference**: §2.2 - FastAPI Framework

**Example**:
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()  # Auto-generated docs at /docs

class GreetingInput(BaseModel):
    name: str  # Automatic validation
    style: str = "casual"

@app.post("/greet")
async def greet(input: GreetingInput):  # Type-safe, async
    return {"message": f"Hello, {input.name}!"}
```

**Impact**: FastAPI's async nature and Pydantic integration enable high-throughput MCP servers with type safety.

---

## Decision 2: FastMCP (Anthropic MCP SDK) for Protocol Handling

### Decision

Use **FastMCP** from the official Anthropic MCP Python SDK to handle MCP protocol details.

### Rationale

**Key Advantages**:
1. **Protocol Abstraction**: Handles JSON-RPC 2.0 over stdio/SSE, initialization handshake, bidirectional communication
2. **Official Implementation**: Maintained by Anthropic (protocol creators), guaranteed compatibility
3. **Auto-Generated Schemas**: Generates JSON schemas from Pydantic models (no manual schema writing)
4. **Control Retained**: Maintains control over authentication, observability, error handling (unlike higher-level abstractions)

**Why NOT Implement Protocol Manually**:
- **Complexity**: JSON-RPC 2.0 + MCP initialization + bidirectional communication = 1000+ lines of boilerplate
- **Maintenance Burden**: Protocol evolves (new MCP versions), manual implementation requires ongoing updates
- **Error-Prone**: Protocol details (handshake sequence, error codes) easy to get wrong

**Implementation Research Reference**: §2.4 - MCP SDK (FastMCP)

**Example**:
```python
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server (handles protocol complexity)
mcp = FastMCP(name="AI Agent MCP Server")

# Register tool with decorator (auto-generates JSON schema)
@mcp.tool(name="example.greet")
async def greet_tool(params: GreetingInput) -> GreetingOutput:
    return GreetingOutput(greeting=f"Hello, {params.name}!")

# FastMCP handles:
# - JSON-RPC deserialization
# - Parameter validation (Pydantic)
# - Tool routing
# - Response serialization
```

**Impact**: FastMCP reduces protocol-handling code by ~80%, enabling focus on business logic.

---

## Decision 3: Pydantic-First Architecture

### Decision

Use **Pydantic 2.x** for ALL data validation and serialization across the entire stack.

### Rationale

**Key Advantages**:
1. **Type Safety**: Static type checking (mypy) catches errors before runtime
2. **Runtime Validation**: Automatic validation of input/output data at API boundaries
3. **JSON Schema Generation**: Auto-generated schemas for MCP tool discovery
4. **Configuration Management**: Pydantic BaseSettings for type-safe environment variable loading
5. **Consistency**: Same validation approach everywhere (API, tools, config, database models)

**Pydantic Coverage**:
- **MCP Tool Inputs**: Validate agent parameters before business logic
- **MCP Tool Outputs**: Ensure tool responses match schema
- **Configuration**: Validate environment variables (database URL, API keys)
- **API Models**: FastAPI request/response validation
- **Database Models** (future): SQLAlchemy models with Pydantic validation

**Implementation Research Reference**: §2.5 - Pydantic-First Architecture, §1.2 - Type Safety Across Agent-Tool Boundary

**Example**:
```python
from pydantic import BaseModel, Field, field_validator

class GreetingInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)  # Declarative constraints
    style: str = Field(pattern="^(formal|casual|enthusiastic)$")

    @field_validator("name")
    @classmethod
    def validate_name_safe(cls, v: str) -> str:
        # Custom validation (prevent injection attacks)
        if not all(c.isalpha() or c.isspace() or c == "-" for c in v):
            raise ValueError("Name contains invalid characters")
        return v

# Pydantic validates BEFORE business logic runs
def greet(input: GreetingInput):  # input is guaranteed valid
    # No manual validation needed
    return f"Hello, {input.name}!"
```

**Impact**: Pydantic eliminates ~70% of manual validation code and catches type errors at development time (mypy).

---

## Decision 4: Explicit Dependency Injection Pattern

### Decision

Use **explicit dependency injection** via FastAPI's `Depends()` for shared services, avoiding global variables.

### Rationale

**Key Advantages**:
1. **Testability**: Tools can be tested with mocked dependencies (no global state manipulation)
2. **Explicitness**: Function signature shows all dependencies (no hidden imports)
3. **Flexibility**: Different dependencies per environment (dev database, prod database)
4. **Type Safety**: Annotated types enable static type checking

**Why NOT Global Variables**:
```python
# ❌ BAD: Global variables
from mcp_server.config import settings  # Global singleton
import logging

logger = logging.getLogger("mcp_server")  # Global logger

async def my_tool(params: MyInput):
    # Hidden dependencies - hard to test
    logger.info(f"Running in {settings.environment}")
```

**Problems with Globals**:
- **Testing Difficulty**: Requires monkey-patching or global state manipulation
- **Hidden Dependencies**: Function signature doesn't reveal dependencies
- **Inflexibility**: Can't swap implementations per environment

**DI Solution**:
```python
# ✅ GOOD: Explicit dependency injection
async def my_tool(
    params: MyInput,
    settings: SettingsDep,  # Explicit dependency
    logger: LoggerDep,      # Explicit dependency
):
    # Clear dependencies, easy to mock in tests
    logger.info(f"Running in {settings.environment}")
```

**Implementation Research Reference**: §4.2 - Dependency Injection Pattern

See [dependency-injection.md](dependency-injection.md) for detailed DI documentation.

**Impact**: Explicit DI improves testability (80%+ test coverage achievable) and makes dependencies visible.

---

## Decision 5: Structured Logging with structlog

### Decision

Use **structlog** for structured, machine-readable logging instead of traditional string-based logging.

### Rationale

**Key Advantages**:
1. **Machine-Readable**: JSON output for log aggregation systems (ELK, Datadog, CloudWatch)
2. **Structured Data**: Key-value pairs instead of unstructured strings
3. **Contextual Information**: Automatic timestamp, log level, module name
4. **Query-Friendly**: Filter logs by specific fields (e.g., "show all errors for tool=my_tool")

**Traditional Logging** (string-based):
```python
# ❌ BAD: Unstructured string logging
logger.info(f"User {user_id} invoked tool {tool_name} with params {params}")
# Hard to query: "show all logs for user_id=123"
```

**Structured Logging** (key-value pairs):
```python
# ✅ GOOD: Structured logging
logger.info(
    "tool_invoked",
    user_id=user_id,
    tool_name=tool_name,
    params=params,
)
# Easy query: log_aggregator.filter(user_id=123)
```

**JSON Output** (production):
```json
{
  "timestamp": "2025-10-15T10:30:00.000Z",
  "level": "info",
  "event": "tool_invoked",
  "user_id": 123,
  "tool_name": "example.greet",
  "params": {"name": "Alice"}
}
```

**Implementation**: See `src/mcp_server/main.py:52-94` (configure_logging function)

**Impact**: Structured logging enables efficient debugging in production (query specific fields, aggregate metrics).

---

## Decision 6: Async/Await Throughout

### Decision

Use **async/await** for ALL I/O operations (database, HTTP, tool functions).

### Rationale

**Key Advantages**:
1. **High Concurrency**: Handle 1000+ concurrent requests on single thread (vs. 10-100 with threads)
2. **Consistency**: Same patterns everywhere (database queries, API calls, tool functions)
3. **Performance**: No thread overhead (context switching, memory per thread)
4. **Scalability**: Horizontal scaling easier (less memory per worker)

**Why Async for MCP Servers**:
- MCP clients send concurrent tool invocations (multiple agents, multiple users)
- Tools often wait for I/O (database queries, external APIs, file system)
- Async enables high throughput without thread/process overhead

**Example**:
```python
# Async database query
async def query_users(session: AsyncSession) -> list[User]:
    result = await session.execute(select(User))  # Non-blocking
    return result.scalars().all()

# Async HTTP call
async def fetch_data(client: httpx.AsyncClient) -> dict:
    response = await client.get("https://api.example.com/data")  # Non-blocking
    return response.json()

# Async tool function
async def my_tool(params: MyInput) -> MyOutput:
    users = await query_users(session)  # Non-blocking
    data = await fetch_data(client)     # Non-blocking
    return MyOutput(users=users, data=data)
```

**Impact**: Async enables MCP servers to handle high-concurrency workloads with minimal resources.

**Note**: Even tools with no I/O use `async def` for consistency (makes adding I/O later trivial).

---

## Decision 7: PostgreSQL with pgvector for Data Layer

### Decision

Use **PostgreSQL 15+** with **pgvector** extension for persistent storage (including future RAG embeddings).

### Rationale

**Key Advantages**:
1. **Unified Storage**: Relational data + vector embeddings in single database (no separate vector DB)
2. **ACID Transactions**: Strong consistency guarantees (vs. eventual consistency in some vector DBs)
3. **Mature Ecosystem**: Battle-tested, extensive tooling, wide operational expertise
4. **Cost-Effective**: Lower total cost of ownership than specialized vector databases (Pinecone, Weaviate)
5. **pgvector Performance**: Sufficient for most use cases (up to millions of vectors with HNSW index)

**Alternatives Considered**:

| Database | Pros | Cons | Decision |
|----------|------|------|----------|
| **Pinecone** | Purpose-built vector DB, fast | Costly, vendor lock-in, no relational data | ❌ Rejected - cost, complexity |
| **Weaviate** | Open-source vector DB | Operational overhead (separate DB), no ACID | ❌ Rejected - complexity |
| **PostgreSQL + pgvector** | Unified storage, ACID, mature, cost-effective | Slower than purpose-built (acceptable trade-off) | ✅ **Selected** |

**Implementation Research Reference**: §2.6 - Database Layer (PostgreSQL + pgvector), §3.3 - RAG Data Layer

**When to Consider Alternatives**: If vector search becomes bottleneck (>10M vectors, <50ms latency required), re-evaluate with Pinecone/Weaviate.

---

## Decision 8: Separation of Tool Registration and Business Logic

### Decision

Separate MCP tool registration (`@mcp.tool` wrapper) from business logic (core function with DI).

### Rationale

**Key Advantages**:
1. **Testability**: Business logic testable without MCP protocol overhead
2. **Reusability**: Business logic reusable in different contexts (REST API, CLI, batch jobs)
3. **Clear Boundaries**: Protocol concerns (FastMCP) vs. domain logic (business function)

**Pattern**:
```python
# Business logic function (testable, reusable)
async def generate_greeting(
    params: GreetingInput,
    settings: Settings,
    logger: logging.Logger,
) -> GreetingOutput:
    # Core business logic with dependency injection
    logger.info(f"Generating greeting for {params.name}")
    greeting = f"Hello, {params.name}!"
    return GreetingOutput(greeting=greeting, ...)


# MCP tool wrapper (thin protocol layer)
@mcp.tool(name="example.generate_greeting")
async def generate_greeting_tool(params: GreetingInput) -> GreetingOutput:
    # Access dependencies directly (FastMCP limitation)
    from mcp_server.config import settings
    from mcp_server.core.dependencies import get_logger

    logger = get_logger("mcp_server.tools.example_tool")
    return await generate_greeting(params, settings, logger)
```

**Why Separation**:
- **Testing**: `generate_greeting()` testable with mocked dependencies (no FastMCP setup)
- **Reusability**: `generate_greeting()` callable from REST endpoint, CLI, batch job
- **FastMCP Limitation**: `@mcp.tool` functions can't use `Depends()` (all params must be JSON-serializable)

**Implementation**: See `src/mcp_server/tools/example_tool.py` for complete example.

**Impact**: Business logic testable in isolation, reusable across protocols (MCP, REST, gRPC).

---

## Decision 9: Type Checking with mypy --strict

### Decision

Enforce **strict type checking** using `mypy --strict` for all Python code.

### Rationale

**Key Advantages**:
1. **Catch Errors Early**: Type errors caught at development time (vs. runtime in production)
2. **Better IDE Support**: Auto-completion, refactoring, inline documentation
3. **Self-Documenting**: Function signatures show expected types
4. **Reduced Bugs**: 15-20% reduction in bugs from type errors (industry data)

**Example**:
```python
# mypy catches type errors
def greet(name: str) -> str:
    return f"Hello, {name}!"

greet(123)  # mypy error: Argument 1 has incompatible type "int"; expected "str"
```

**Implementation**: See `pyproject.toml` for mypy configuration, `CLAUDE-typing.md` for type hint standards.

**Impact**: Type checking reduces runtime errors and improves code quality.

---

## Decision 10: Linting and Formatting with Ruff

### Decision

Use **Ruff** for fast Python linting and formatting (replacing Flake8, Black, isort).

### Rationale

**Key Advantages**:
1. **Speed**: 10-100x faster than Flake8/Black (written in Rust)
2. **All-in-One**: Linting + formatting + import sorting (single tool)
3. **Compatible**: Drop-in replacement for Flake8/Black (same rules)
4. **Modern**: Active development, rapid bug fixes

**Alternatives**:

| Tool | Purpose | Speed | Decision |
|------|---------|-------|----------|
| **Flake8** | Linting | Slow | ❌ Replaced by Ruff |
| **Black** | Formatting | Medium | ❌ Replaced by Ruff |
| **isort** | Import sorting | Medium | ❌ Replaced by Ruff |
| **Ruff** | All-in-one | **Fast** | ✅ **Selected** |

**Implementation**: See `pyproject.toml` for Ruff configuration, `CLAUDE-tooling.md` for commands.

**Impact**: Ruff reduces CI/CD time (faster linting/formatting) and developer friction (single tool).

---

## Decision 11: Testing with pytest + pytest-asyncio

### Decision

Use **pytest** with **pytest-asyncio** for unit and integration testing.

### Rationale

**Key Advantages**:
1. **Async Support**: pytest-asyncio enables testing async functions
2. **Fixtures**: Powerful fixture system for shared test resources
3. **Parametrization**: Test multiple scenarios with single test function
4. **Coverage**: Integration with coverage.py for code coverage reporting

**Example**:
```python
import pytest

@pytest.mark.asyncio
async def test_generate_greeting(mock_settings, mock_logger):
    """Test greeting generation with formal style."""
    params = GreetingInput(name="Alice", style="formal")
    result = await generate_greeting(params, mock_settings, mock_logger)
    assert result.greeting == "Good day, Alice!"
```

**Implementation**: See `CLAUDE-testing.md` for testing standards, `tests/` for examples.

**Impact**: pytest enables comprehensive testing (unit, integration, E2E) with async support.

---

## Decision 12: UV for Package Management and Taskfile for Task Running

### Decision

Use **UV** for fast Python package management and **Taskfile** for unified task running (replacing Make/scripts).

### Rationale

**UV Advantages**:
1. **Speed**: 10-100x faster than pip (written in Rust)
2. **Deterministic**: Lock file ensures reproducible installs
3. **Compatibility**: Drop-in pip replacement (same commands)

**Taskfile Advantages**:
1. **Language-Agnostic**: Works across Python, Node.js, Go, Rust projects
2. **Self-Documenting**: `task --list` shows available commands
3. **Cross-Platform**: Works on Linux, macOS, Windows
4. **Modern**: Better than Make (YAML syntax, built-in help)

**Example Taskfile** (`Taskfile.yml`):
```yaml
tasks:
  dev:
    desc: Run development server
    cmds:
      - uv run uvicorn mcp_server.main:app --reload

  test:
    desc: Run test suite
    cmds:
      - uv run pytest

  lint:
    desc: Run linter
    cmds:
      - uv run ruff check src/
```

**Implementation**: See `CLAUDE-tooling.md` for complete Taskfile reference.

**Impact**: UV reduces dependency install time, Taskfile provides unified CLI interface.

---

## Key Product Decisions (from HLS-003)

### Decision D1: No External Service Integration in US-009/US-010/US-011

**Rationale**: Foundation stories (US-009, US-010, US-011) focus on establishing patterns, not integrating production services.

**Impact**: Example tool uses abstract business logic (greeting), not real services (JIRA, Kubernetes).

**When to Change**: EPIC-002+ (feature epics) will integrate real services using patterns from foundation.

---

### Decision D2: Single Example Tool (Not Multiple Domain Examples)

**Rationale**: One comprehensive example sufficient for pattern demonstration. Multiple examples add complexity without proportional value.

**Impact**: Example tool demonstrates ALL patterns (Pydantic validation, DI, error handling, async, logging).

---

### Decision D3: Abstract Business Logic (Not Real-World Complexity)

**Rationale**: Keep focus on architectural patterns, not domain-specific complexity.

**Impact**: Example tool uses simple "greeting" logic. Real tools (JIRA, K8s) will have complex business logic but same structural patterns.

---

### Decision D4: Hybrid Documentation Approach

**Rationale**: Balance between inline docs (implementation details) and separate docs (architecture context).

**Strategy**:
- **Inline Documentation**: Docstrings + comments in code for implementation details
- **Architecture Documentation**: Separate docs (`docs/architecture/`) for system context, diagrams, design rationale

**Impact**: Inline docs for "what code does", architecture docs for "why patterns chosen".

---

## Trade-Offs Summary

| Decision | Pros | Cons | Mitigation |
|----------|------|------|------------|
| **FastAPI** | Async, Pydantic, DI, modern | Younger ecosystem than Flask/Django | Use stable versions, strong community |
| **FastMCP** | Protocol abstraction, official | Anthropic-specific (not generic) | Acceptable - MCP is Anthropic protocol |
| **Pydantic** | Type safety, validation, JSON schema | Learning curve for advanced features | Comprehensive examples, inline docs |
| **PostgreSQL + pgvector** | Unified storage, ACID, mature | Slower than purpose-built vector DBs | Acceptable for <10M vectors |
| **Async/Await** | High concurrency, performance | More complex than sync (debugging) | Structured logging, tracing |
| **Explicit DI** | Testability, flexibility | More verbose than globals | Type aliases reduce boilerplate |

---

## When to Reconsider Decisions

### Trigger for Re-Evaluation

1. **Performance Bottlenecks**: If vector search becomes bottleneck (>10M vectors), evaluate Pinecone/Weaviate
2. **Scale Requirements**: If concurrent connections exceed 10,000, evaluate async server (Gunicorn + Uvicorn workers)
3. **Protocol Evolution**: If MCP protocol changes significantly, re-evaluate FastMCP abstraction
4. **Team Expertise**: If team has deep Django expertise, reconsider FastAPI (balance with async benefits)

### Decision Stability

| Decision | Stability | Likely Changes |
|----------|-----------|----------------|
| **FastAPI** | High | Unlikely to change (async foundation) |
| **FastMCP** | High | Unlikely (official Anthropic SDK) |
| **Pydantic** | High | Unlikely (core to FastAPI) |
| **PostgreSQL** | Medium | Possible at scale (evaluate vector DBs) |
| **Async/Await** | High | Unlikely (performance requirement) |

---

## Related Documentation

- **Architecture Overview**: [overview.md](overview.md) - System component overview
- **Dependency Injection**: [dependency-injection.md](dependency-injection.md) - DI implementation details
- **Request Flow**: [request-flow.md](request-flow.md) - Request lifecycle
- **Implementation Research**: `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md` - Detailed technical research

### CLAUDE.md Standards

- **CLAUDE-architecture.md**: Project structure, modularity patterns
- **CLAUDE-typing.md**: Type hints, mypy configuration
- **CLAUDE-tooling.md**: Taskfile, UV, Ruff, pytest commands

---

## Changelog

- **2025-10-15** (v1.0): Initial design decisions documentation (US-013)
