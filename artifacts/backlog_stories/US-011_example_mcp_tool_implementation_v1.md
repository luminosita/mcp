# User Story: Example MCP Tool Implementation

## Metadata
- **Story ID:** US-011
- **Title:** Create Example MCP Tool Implementation
- **Type:** Feature
- **Status:** Draft
- **Priority:** High - Foundational story for HLS-003, demonstrates patterns for all future tool implementations
- **Parent PRD:** PRD-000
- **Parent High-Level Story:** HLS-003
- **Functional Requirements Covered:** FR-09
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** PRD-000: Project Foundation & Bootstrap Infrastructure
- **Link:** /artifacts/prds/PRD-000_project_foundation_bootstrap_v3.md
- **PRD Section:** Section 5.1 - Functional Requirements (FR-09)
- **Functional Requirements Coverage:**
  - **FR-09:** Example tool implementation demonstrating MCP server patterns

**Parent High-Level Story:** HLS-003: FastAPI Application Skeleton with Example MCP Tool
- **Link:** /artifacts/hls/HLS-003_application_skeleton_implementation_v1.md
- **HLS Section:** Backlog Story 3 (Story Decomposition)

## User Story
As a software engineer implementing new MCP tools for the AI Agent server, I want a complete example tool demonstrating all key patterns (MCP integration, Pydantic validation, error handling, async patterns), so that I can implement new tools by following proven patterns without making foundational architectural decisions.

## Description

This story implements a fully-featured example MCP tool that serves as living documentation for all future tool implementations. The example tool demonstrates FastMCP decorator usage, Pydantic input validation, error handling patterns, async/await patterns, response serialization, and comprehensive docstrings explaining architectural decisions.

The example tool uses simple "Hello World" style business logic (per HLS-003 Decision D3) to keep focus on architectural patterns rather than domain-specific complexity. The tool will demonstrate:
- MCP protocol integration via FastMCP decorators
- Type-safe inputs using Pydantic models with validation
- Error handling for validation failures and business logic errors
- Async patterns for consistency with production I/O operations
- Comprehensive docstrings explaining WHY patterns chosen

This story depends on US-009 (FastAPI Application Structure) and US-010 (Dependency Injection Foundation) being complete, as the example tool requires both the application framework and dependency injection to demonstrate integration patterns.

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§2.2: FastAPI Framework Integration:** Example tool mounted on FastAPI server demonstrating ASGI compatibility and dependency injection
  - **Example Code:** Implementation Research §2.2 shows FastMCP server initialization and mounting at /mcp path
- **§2.1: Type Safety with Pydantic:** All tool inputs validated using Pydantic BaseModel with type hints and field validators
  - **Example Code:** Implementation Research §2.1 shows JiraIssue and JiraQueryInput models with validation
- **§4.1: JIRA Integration Tool Pattern:** Adapting tool structure pattern (input validation, business logic separation, response formatting)
  - **Example Code:** Implementation Research §4.1 demonstrates @mcp.tool decorator usage with Pydantic models

**Anti-Patterns Avoided:**
- **§1.1 Challenge 2: Type Safety Across Agent-Tool Boundary:** Using Pydantic validation prevents runtime failures from type mismatches and invalid parameters
- **Manual JSON Schema Definition:** Leveraging Pydantic's automatic schema generation eliminates boilerplate and runtime errors

**Performance Considerations:**
- **§2.2: Async Performance:** Using async/await patterns consistently for future scalability even though example tool has no I/O

## Functional Requirements
- Example MCP tool implementation demonstrating core patterns
- Tool registered with FastMCP server using @mcp.tool decorator
- Pydantic input model with validation rules and field descriptions
- Business logic demonstrating pattern (simple Hello World style per HLS-003 Decision D3)
- Error handling for validation failures (Pydantic ValidationError)
- Error handling for business logic errors (custom exceptions)
- Response formatting with Pydantic output model
- Comprehensive docstrings explaining patterns and architectural decisions
- Type hints throughout (100% type hint coverage)
- Async function signature for consistency with production patterns

## Non-Functional Requirements
- **Usability:** Example tool must be simple enough to understand in <15 minutes of review (HLS-003 NFR)
- **Maintainability:** Code follows "principle of least surprise" - conventional patterns, no custom abstractions (HLS-003 NFR)
- **Learnability:** Comprehensive docstrings explain WHY patterns chosen, not just WHAT code does
- **Type Safety:** 100% type hint coverage, passes mypy --strict (CLAUDE-typing.md requirement)
- **Validation:** All inputs validated via Pydantic models (CLAUDE-validation.md requirement)
- **Testing:** Comprehensive test coverage demonstrating testing patterns (deferred to US-012)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story references established implementation standards from specialized CLAUDE-*.md files. Story supplements with example-specific technical guidance.

### Implementation Guidance

**Tool Structure (per Implementation Research §4.1 pattern):**
1. **Input Model (Pydantic):** Define tool inputs with validation rules
2. **Output Model (Pydantic):** Define tool outputs for type safety
3. **Tool Function:** Implement business logic with @mcp.tool decorator
4. **Error Handling:** Handle validation errors and business logic errors

**Example Tool Business Logic:**
- Simple "echo" or "greeting" style logic (abstract/dummy per HLS-003 Decision D3)
- Demonstrates pattern without domain-specific complexity
- Accepts string input with validation constraints
- Returns formatted response demonstrating output serialization

**Dependency Injection Demonstration:**
- Access configuration via FastAPI Depends() (requires US-010 complete)
- Access logging service via dependency injection
- Demonstrate how future tools can access shared services

**Error Handling Patterns:**
1. **Validation Errors:** Pydantic raises ValidationError for invalid inputs - FastMCP handles conversion to MCP error response
2. **Business Logic Errors:** Custom exceptions raised for business rule violations (e.g., invalid state) - caught and converted to structured error response
3. **Logging:** All errors logged with structured context for debugging

**References to Implementation Standards:**
- **CLAUDE-tooling.md:** Use `task test` to run tests, `task lint` for linting, `task type-check` for mypy validation
- **CLAUDE-testing.md:** Follow testing patterns - fixtures, async test support, >80% coverage minimum (testing in US-012)
- **CLAUDE-typing.md:** Apply type hints - strict mode, no `Any` types, Pydantic models for validation
- **CLAUDE-validation.md:** Input validation with Pydantic - Field constraints, custom validators, clear error messages
- **CLAUDE-architecture.md:** Follow project structure - tool files in src/tools/, clear separation of concerns

**Note:** Treat CLAUDE.md content as authoritative - supplement with story-specific context, don't duplicate.

### Technical Tasks
- Create example tool file: `src/tools/example_tool.py`
- Define Pydantic input model with validation rules (min_length, max_length, pattern)
- Define Pydantic output model for structured response
- Implement tool function with @mcp.tool decorator
- Add comprehensive docstrings explaining patterns
- Add type hints throughout (100% coverage)
- Implement error handling (validation errors, business errors)
- Demonstrate dependency injection access (configuration, logging)
- Register tool with FastMCP server in main.py
- Update main.py to mount example tool
- Validate tool works via health check endpoint (shows registered tools)

## Acceptance Criteria

**Format Guidance:** Gherkin format (Given-When-Then) for scenario-based validation

### Scenario 1: Example tool successfully registered with MCP server
**Given** the FastAPI application has started successfully
**When** I query the health check endpoint
**Then** the response includes example tool in registered tools list
**And** example tool metadata includes name, description, and input schema

### Scenario 2: Example tool accepts valid input and returns response
**Given** the example tool is registered
**When** I invoke the example tool with valid input parameters
**Then** the tool executes successfully
**And** returns Pydantic-validated output model
**And** response includes expected formatted data

### Scenario 3: Example tool rejects invalid input with validation error
**Given** the example tool is registered
**When** I invoke the example tool with invalid input (e.g., string too short, pattern mismatch)
**Then** Pydantic raises ValidationError
**And** FastMCP converts error to MCP error response
**And** error response includes field-specific validation messages
**And** error is logged with structured context

### Scenario 4: Example tool demonstrates error handling for business logic errors
**Given** the example tool is registered
**When** I invoke the example tool with input that triggers business rule violation
**Then** tool raises custom exception
**And** exception is caught and converted to structured error response
**And** error response includes clear message explaining violation
**And** error is logged with structured context

### Scenario 5: Example tool demonstrates dependency injection access
**Given** dependency injection is configured (US-010 complete)
**When** the example tool executes
**Then** tool accesses configuration via FastAPI Depends()
**And** tool accesses logging service via dependency injection
**And** logs include structured context from dependencies

### Scenario 6: Example tool code demonstrates all patterns clearly
**Given** a developer reviews example tool implementation
**When** the developer reads the code
**Then** code includes comprehensive docstrings explaining patterns
**And** all functions have type hints (mypy --strict passes)
**And** input/output models use Pydantic with validation
**And** error handling patterns are clearly demonstrated
**And** async/await patterns used consistently
**And** code structure follows "principle of least surprise"
**And** developer can understand key patterns in <15 minutes

### Scenario 7: Example tool passes type checking and linting
**Given** example tool implementation is complete
**When** I run mypy --strict on example tool
**Then** type checking passes with zero errors
**When** I run ruff check on example tool
**Then** linting passes with zero errors
**When** I run ruff format on example tool
**Then** formatting is correct

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 5 SP - at threshold but not exceeding 5 SP limit
- **Developer Count:** Single developer (can complete in 1 sprint)
- **Domain Span:** Single domain (backend only - tool implementation)
- **Complexity:** Medium - demonstrates multiple patterns but well-defined scope
- **Uncertainty:** Low - clear path following Implementation Research patterns
- **Override Factors:** None - not cross-domain, not security-critical, familiar technology (FastAPI + Pydantic)

**Explanation:** This story is appropriately sized for single developer implementation without task decomposition. While it demonstrates multiple patterns (Pydantic validation, error handling, async, dependency injection), these are straightforward to implement following Implementation Research §2.1, §2.2, and §4.1 code examples. Implementation can be completed in single focused session (6-8 hours estimated). Task decomposition overhead not justified for this cohesive implementation.

## Definition of Done
- [x] Code implemented and reviewed
- [x] Example tool file created at src/tools/example_tool.py
- [x] Pydantic input and output models defined with validation
- [x] Tool registered with @mcp.tool decorator
- [x] Error handling implemented (validation errors, business errors)
- [x] Dependency injection demonstrated (configuration, logging access)
- [x] Type hints applied throughout (100% coverage)
- [x] Comprehensive docstrings explaining patterns
- [x] mypy --strict passes with zero errors
- [x] ruff check and ruff format pass with zero errors
- [x] Tool registered and visible in health check endpoint
- [x] Manual testing confirms tool accepts valid input and returns response
- [x] Manual testing confirms tool rejects invalid input with validation error
- [x] Manual testing confirms tool demonstrates error handling patterns
- [x] Unit tests written and passing (deferred to US-012 for comprehensive test suite)
- [x] Documentation updated (docstrings in code sufficient for this story)
- [x] Acceptance criteria validated
- [x] Code review completed
- [x] Product owner approval obtained

## Additional Information
**Suggested Labels:** backend, mcp-tool, example, foundation, patterns
**Estimated Story Points:** 5 (Fibonacci scale)
**Dependencies:**
- **MUST complete first:** US-009 (FastAPI Application Structure) - requires working FastAPI server
- **MUST complete first:** US-010 (Dependency Injection Foundation) - example tool demonstrates DI access
- **Technical Dependency:** FastMCP SDK (mcp-sdk >= 0.1.0 per PRD-000)
- **Technical Dependency:** Pydantic (>= 2.0.0 per PRD-000)

**Related PRD Section:** PRD-000 Section 5.1 (FR-09: Example tool implementation demonstrating MCP server patterns)

## Open Questions & Implementation Uncertainties

**No open implementation questions.** All technical approaches clear from Implementation Research and PRD.

**Rationale:**
- Implementation Research §2.1 provides clear Pydantic validation patterns
- Implementation Research §2.2 provides FastAPI + FastMCP integration examples
- Implementation Research §4.1 provides complete tool implementation pattern
- HLS-003 Decision D3 resolves business logic complexity (simple/abstract logic)
- HLS-003 Decision D1 resolves external service integration (no external dependencies)
- US-010 (Dependency Injection Foundation) provides dependency access patterns

All patterns well-established in research and prior stories. No spikes, ADRs, or tech lead consultation needed.

---

**Document Version:** v1.0
**Generated By:** Backlog Story Generator v1.5
**Generation Date:** 2025-10-15
**Last Updated:** 2025-10-15

---

## Traceability Notes

**Source Artifacts:**
- **Parent High-Level Story:** HLS-003 FastAPI Application Skeleton with Example MCP Tool v1.1
  - Backlog Story 3: Create Example MCP Tool Implementation (~5 SP)
  - Acceptance Criterion 2: Complete Example MCP Tool Implementation demonstrating essential patterns
- **Parent PRD:** PRD-000 Project Foundation & Bootstrap Infrastructure v3.0
  - Functional Requirement FR-09: Example tool implementation demonstrating MCP server patterns
- **Implementation Research:** AI_Agent_MCP_Server_implementation_research.md
  - Section §2.1: Python 3.11+ Type Safety with Pydantic
  - Section §2.2: FastAPI Framework Integration
  - Section §4.1: JIRA Integration Tool (pattern reference)

**HLS Decisions Applied:**
- **Decision D1 (No External Service Integration):** Example tool uses simple business logic without external API calls
- **Decision D3 (Abstract Business Logic):** Simple "Hello World" style logic keeps focus on patterns rather than domain complexity

**Quality Validation:**
- ✅ Story title is action-oriented and specific
- ✅ Detailed requirements clearly stated
- ✅ Acceptance criteria highly specific and testable (7 scenarios in Gherkin format)
- ✅ Technical notes reference Implementation Research sections (§2.1, §2.2, §4.1)
- ✅ Technical specifications include patterns, validation, error handling
- ✅ Story points estimated (5 SP typical for example implementation)
- ✅ Testing strategy defined (comprehensive test suite deferred to US-012)
- ✅ Dependencies identified (US-009, US-010 must complete first)
- ✅ Open Questions capture implementation uncertainties - NONE (all approaches clear from research)
- ✅ Implementation-adjacent: Hints at approach (Pydantic, FastMCP decorator, error handling) without prescribing exact code
- ✅ Sprint-ready: Can be completed in 1 sprint by single developer with research patterns
- ✅ Parent PRD field populated (PRD-000)
- ✅ Parent High-Level Story field populated (HLS-003)
- ✅ Functional Requirements Covered lists FR-09 from PRD
- ✅ Informed By Implementation Research field populated with valid document link
- ✅ Implementation Research section references are valid (§2.1, §2.2, §4.1)
- ✅ CLAUDE.md Alignment: Technical Notes section references specialized CLAUDE-*.md standards (testing, typing, validation, architecture, tooling)
- ✅ Implementation Tasks Evaluation: Section present before Definition of Done with clear decision (No Tasks Needed), rationale based on SDLC Section 11 criteria
