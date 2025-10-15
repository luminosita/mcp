# Master Plan - Context Engineering PoC

**Document Version**: 1.3
**Last Updated**: 2025-10-14

---

## Current Phase: Implementation (HLS-003 Stories)

**Current Status**: Implementation in progress - Foundation stories completed (US-009, US-010)
**Last Completed**: TODO-041 (US-010 Dependency Injection Foundation - implemented)
**Next Task**: TODO-042 (Implement US-011 - Example MCP Tool Implementation)
**Implementation Progress**: 2/5 stories implemented (6/16 SP complete)
**Story Sequence**: US-009 ✅ → US-010 ✅ → US-011 + US-012 (parallel) → US-013

**Implementation TODOs Created:**
- TODO-040: US-009 (FastAPI Application Structure, 3 SP) ✅
- TODO-041: US-010 (Dependency Injection Foundation, 3 SP) ✅
- TODO-042: US-011 (Example MCP Tool Implementation, 5 SP) ⏳
- TODO-043: US-012 (Test Suite for Example Tool, 3 SP) ⏳
- TODO-044: US-013 (Application Architecture Documentation, 2 SP) ⏳

---

## Phase 1: Backlog Story Generation (HLS-003)

### TODO-035: Generate Backlog Story US-009 - FastAPI Application Structure with Health Check
**Priority**: High
**Dependencies**: HLS-003 generated (approved)
**Estimated Time**: 25 minutes
**Status**: ✅ Completed
**Context**: New session recommended
**Generator Name**: backlog-story
**ID Assignment**: US-009 (HLS-002 used US-003 through US-008)

**Description**:
Generate detailed backlog story for FastAPI Application Structure with Health Check endpoint from HLS-003.

**Command**: `/generate TODO-035`

**Input Data:**
- HLS-003 v1 (FastAPI Application Skeleton with Example MCP Tool)
- Backlog Story 1: Create FastAPI Application Structure with Health Check (~3 SP)

**Scope Guidance:**
- Set up FastAPI application entry point with proper project structure
- Implement configuration management with Pydantic validation
- Create health check endpoint returning system status (version, dependencies, uptime)
- Follow Python src layout with clear separation of concerns
- Enable server startup with minimal configuration

**Notes:**
- Foundation story for HLS-003 - MUST complete first per decomposition strategy
- Establishes application structure that all other stories build upon
- No external service integration (per HLS-003 Decision D1)

---

### TODO-036: Generate Backlog Story US-010 - Dependency Injection Foundation
**Priority**: High
**Dependencies**: HLS-003 generated (approved)
**Estimated Time**: 25 minutes
**Status**: ✅ Completed
**Context**: New session recommended
**Generator Name**: backlog-story
**ID Assignment**: US-010 (next after US-009)

**Description**:
Generate detailed backlog story for Dependency Injection Foundation from HLS-003.

**Command**: `/generate TODO-036`

**Input Data:**
- HLS-003 v1 (FastAPI Application Skeleton with Example MCP Tool)
- Backlog Story 2: Implement Dependency Injection Foundation (~3 SP)

**Scope Guidance:**
- Configure dependency injection pattern for sharing services across tools
- Document clear process for adding new dependencies
- Enable tools to access configuration, logging, and shared services
- Demonstrate dependency injection usage with example service
- Avoid "magic" - keep DI explicit and obvious

**Notes:**
- MUST complete before US-011 (example tool needs DI)
- Enables all future tool implementations to access shared services
- Foundation for testing patterns (dependency mocking)

---

### TODO-037: Generate Backlog Story US-011 - Example MCP Tool Implementation
**Priority**: High
**Dependencies**: HLS-003 generated (approved)
**Estimated Time**: 30 minutes
**Status**: ✅ Completed
**Context**: New session recommended
**Generator Name**: backlog-story
**ID Assignment**: US-011 (next after US-010)

**Description**:
Generate detailed backlog story for Example MCP Tool Implementation from HLS-003.

**Command**: `/generate TODO-037`

**Input Data:**
- HLS-003 v1 (FastAPI Application Skeleton with Example MCP Tool)
- Backlog Story 3: Create Example MCP Tool Implementation (~5 SP)

**Scope Guidance:**
- Implement complete example tool demonstrating all key patterns
- Use FastMCP decorators for MCP protocol integration
- Demonstrate Pydantic validation for type-safe inputs
- Show error handling patterns (validation errors, business logic errors)
- Use async patterns for consistency
- Keep business logic simple (abstract/dummy per HLS-003 Decision D3)
- Include comprehensive docstrings explaining patterns

**Notes:**
- Most complex story in HLS-003 (5 SP)
- Requires US-009 and US-010 complete (needs app structure + DI)
- Serves as living documentation for all future tool implementations
- Can be implemented in parallel with US-012 after US-009/US-010 complete

---

### TODO-038: Generate Backlog Story US-012 - Test Suite for Example Tool
**Priority**: High
**Dependencies**: HLS-003 generated (approved)
**Estimated Time**: 25 minutes
**Status**: ✅ Completed
**Context**: New session recommended
**Generator Name**: backlog-story
**ID Assignment**: US-012 (next after US-011)

**Description**:
Generate detailed backlog story for Test Suite for Example Tool from HLS-003.

**Command**: `/generate TODO-038`

**Input Data:**
- HLS-003 v1 (FastAPI Application Skeleton with Example MCP Tool)
- Backlog Story 4: Create Test Suite for Example Tool (~3 SP)

**Scope Guidance:**
- Write comprehensive test suite demonstrating testing patterns
- Include unit tests for tool business logic
- Demonstrate Pydantic model validation testing
- Show mocking patterns for external dependencies
- Test error handling scenarios (validation failures, business errors)
- Use async test patterns with pytest-asyncio
- Achieve >80% coverage per project standards

**Notes:**
- Can be implemented in parallel with US-011 after US-009/US-010 complete
- Establishes testing patterns for all future tool implementations
- Demonstrates fixture patterns from conftest.py

---

### TODO-039: Generate Backlog Story US-013 - Application Architecture Documentation
**Priority**: Medium
**Dependencies**: HLS-003 generated (approved)
**Estimated Time**: 20 minutes
**Status**: ✅ Completed
**Context**: New session recommended
**Generator Name**: backlog-story
**ID Assignment**: US-013 (next after US-012)

**Description**:
Generate detailed backlog story for Application Architecture Documentation from HLS-003.

**Command**: `/generate TODO-039`

**Input Data:**
- HLS-003 v1 (FastAPI Application Skeleton with Example MCP Tool)
- Backlog Story 5: Document Application Architecture and Patterns (~2 SP)

**Scope Guidance:**
- Write architecture documentation explaining application structure
- Document dependency injection pattern and extension points
- Create visual diagrams (application structure, request flow, DI graph)
- Reference example tool implementation as concrete demonstration
- Explain WHY patterns chosen, not just WHAT they are
- Extract architectural concepts from inline documentation
- Follow "documentation-driven development" approach (per HLS-003 Decision D4)

**Notes:**
- Implement last after architecture proven through US-009 through US-012
- Hybrid approach: inline docs for implementation details, separate docs for architecture
- Enables new team members to understand architecture within 1 hour (HLS-003 NFR)

---

## Phase 2: Implementation (HLS-003 Stories)

### TODO-040: Implement US-009 - FastAPI Application Structure with Health Check
**Priority**: Critical
**Dependencies**: HLS-001 (Development Environment Setup) - MUST be complete
**Estimated Time**: 1.5 days (1 day dev + 0.5 day testing/docs)
**Status**: ✅ Completed
**Context**: New session recommended
**Story Points**: 3 SP

**Description**:
Implement foundational FastAPI application structure with health check endpoint. Establishes application entry point, Pydantic-based configuration management, structured logging, and Python src layout that all subsequent features build upon.

**Implementation Scope:**
- Create `src/main.py` with FastAPI application initialization
- Create `src/config.py` with Pydantic BaseSettings model
- Create `src/core/constants.py` with application constants
- Implement `/health` endpoint returning system status JSON
- Configure structured logging with structlog (JSON output)
- Add startup event handler
- Configure CORS middleware for development
- Update `Taskfile.yml` with `task dev` command
- Create `.env.example` with configuration template
- Update `pyproject.toml` with dependencies (fastapi, uvicorn, pydantic-settings, structlog)

**Acceptance Criteria:**
- Application starts successfully with `task dev` command
- Health check endpoint returns valid JSON response (status, version, uptime, timestamp)
- Configuration validation works correctly (accepts valid, rejects invalid with clear errors)
- Structured logging configured with JSON output support
- Unit tests written and passing (>80% coverage)
- Type checking passes with mypy --strict
- Linting passes with ruff

**Reference**: /artifacts/backlog_stories/US-009_story_v1.md

---

### TODO-041: Implement US-010 - Dependency Injection Foundation
**Priority**: High
**Dependencies**: US-009 (Application Structure) - MUST be complete
**Estimated Time**: 1 day
**Status**: ✅ Completed
**Context**: New session recommended
**Story Points**: 3 SP

**Description**:
Implement FastAPI dependency injection infrastructure enabling MCP tools to access shared services (configuration, logging, database sessions, HTTP clients) through explicit injection rather than global variables.

**Implementation Scope:**
- Create `src/mcp_server/core/dependencies.py` module
- Implement `get_settings()` dependency (singleton Settings instance)
- Implement `get_logger()` dependency (structured logger with request context)
- Implement `get_db_session()` async generator (SQLAlchemy AsyncSession with auto-cleanup)
- Implement `get_http_client()` dependency (shared httpx.AsyncClient)
- Update `main.py` with lifespan context manager (HTTP client and database initialization)
- Create type aliases using `Annotated` syntax (SettingsDep, LoggerDep, SessionDep, etc.)
- Document dependency injection process in inline docstrings
- Add example usage demonstrating dependency injection

**Acceptance Criteria:**
- Settings dependency injection works (singleton pattern)
- Logger dependency injection provides structured logging
- Database session dependency injection with automatic cleanup
- HTTP client dependency injection with connection pooling
- Application lifespan management (startup/shutdown logic)
- Dependency override for testing (app.dependency_overrides)
- Unit tests written and passing (>80% coverage)
- Integration tests demonstrate realistic dependency usage

**Reference**: /artifacts/backlog_stories/US-010_story_v1.md

---

### TODO-042: Implement US-011 - Example MCP Tool Implementation
**Priority**: High
**Dependencies**: US-009 (Application Structure) + US-010 (Dependency Injection) - MUST be complete
**Estimated Time**: 1 day
**Status**: ⏳ Pending
**Context**: New session recommended
**Story Points**: 5 SP

**Description**:
Implement fully-featured example MCP tool serving as living documentation for all future tool implementations. Demonstrates FastMCP decorators, Pydantic validation, error handling, async patterns, and dependency injection access.

**Implementation Scope:**
- Create `src/tools/example_tool.py`
- Define Pydantic input model with validation rules (min_length, max_length, pattern)
- Define Pydantic output model for structured response
- Implement tool function with @mcp.tool decorator
- Add comprehensive docstrings explaining patterns
- Add type hints throughout (100% coverage)
- Implement error handling (validation errors, business errors)
- Demonstrate dependency injection access (configuration, logging)
- Register tool with FastMCP server in main.py
- Update main.py to mount example tool
- Validate tool works via health check endpoint

**Acceptance Criteria:**
- Example tool successfully registered with MCP server
- Tool accepts valid input and returns Pydantic-validated response
- Tool rejects invalid input with clear validation errors
- Error handling for business logic errors demonstrated
- Dependency injection access demonstrated (config, logging)
- Code includes comprehensive docstrings explaining patterns
- mypy --strict passes with zero errors
- ruff check and ruff format pass with zero errors
- Developer can understand key patterns in <15 minutes

**Reference**: /artifacts/backlog_stories/US-011_story_v1.md

---

### TODO-043: Implement US-012 - Test Suite for Example MCP Tool
**Priority**: High
**Dependencies**: US-009 + US-010 + US-011 - MUST be complete
**Estimated Time**: 1 day
**Status**: ⏳ Pending
**Context**: New session recommended
**Story Points**: 3 SP

**Description**:
Create comprehensive test suite for example MCP tool demonstrating testing patterns (unit tests, Pydantic validation testing, mocking, error handling, async testing). Serves as living documentation for testing approach.

**Implementation Scope:**
- Create `tests/conftest.py` with shared fixtures (sample inputs, mocked dependencies)
- Implement `tests/unit/test_example_tool.py`:
  - Unit tests for tool business logic with mocked dependencies
  - Pydantic validation tests (valid inputs, invalid inputs, edge cases)
  - Error handling tests (validation errors, external failures)
  - Async tests with @pytest.mark.asyncio
- Implement `tests/integration/test_mcp_protocol.py`:
  - MCP tool discovery tests
  - MCP tool invocation tests
  - MCP response validation tests
- Configure coverage reporting in pyproject.toml
- Add inline comments explaining testing patterns
- Verify >80% coverage with `task test-cov`

**Acceptance Criteria:**
- Unit tests validate tool business logic (mocked dependencies)
- Pydantic validation testing demonstrates type safety
- Mocking patterns enable fast, isolated tests (<1 second per test)
- Async tests demonstrate pytest-asyncio patterns
- Error handling tests validate all failure modes
- Test coverage >80% line and branch coverage
- Test organization follows project standards (tests/unit/, tests/integration/, conftest.py)
- Test suite serves as testing pattern reference for new tools

**Open Questions:**
- Test Data Management: Hardcoded fixtures vs. factory patterns? [REQUIRES TECH LEAD]
- Integration Test Scope: Real MCP client-server handshake vs. mocked client? [REQUIRES TECH LEAD]

**Reference**: /artifacts/backlog_stories/US-012_story_v1.md

---

### TODO-044: Implement US-013 - Application Architecture Documentation
**Priority**: Medium
**Dependencies**: US-009 + US-010 + US-011 + US-012 - SHOULD all be complete
**Estimated Time**: 1 day (8-10 hours)
**Status**: ⏳ Pending
**Context**: New session recommended
**Story Points**: 2 SP

**Description**:
Create architecture documentation extracting architectural concepts from implementation (US-009 through US-012). Explains WHY patterns were chosen, provides visual diagrams, and guides engineers to extension points.

**Implementation Scope:**
- Create /docs/architecture/ directory structure
- Write overview.md with system architecture diagram (Mermaid)
- Write dependency-injection.md with DI pattern explanation and extension guide
- Write request-flow.md with Mermaid sequence diagram
- Write design-decisions.md documenting technology choices with Implementation Research citations
- Write extension-guides/:
  - add-new-tool.md (references example tool)
  - add-database-access.md (placeholder DI pattern)
  - add-external-service.md (circuit breaker pattern reference)
- Create Mermaid diagrams (architecture-overview, dependency-graph, request-flow-sequence)
- Add "Last Updated" metadata to each document

**Acceptance Criteria:**
- New team member can explain architecture within 1 hour of reading docs
- Architecture diagram shows FastAPI → FastMCP → Tools layer clearly
- Dependency injection extension guide provides step-by-step process
- Request flow diagram shows complete lifecycle from client to tool to response
- Pattern rationale documented with Implementation Research citations
- Extension guide references example tool and CLAUDE.md standards
- Documentation links to CLAUDE.md files validated (no broken links)
- All Mermaid diagrams render correctly in GitHub/VSCode

**Reference**: /artifacts/backlog_stories/US-013_story_v1.md

---

## Task Status Legend

- ✅ Completed
- ⏳ Pending
- 🔄 In Progress
- ⏸️ Blocked
- ⚠️ Issues Found

---
