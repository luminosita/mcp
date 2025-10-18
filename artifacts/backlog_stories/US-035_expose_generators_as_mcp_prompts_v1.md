# User Story: Expose Generators as MCP Prompts

## Metadata
- **Story ID:** US-035
- **Title:** Expose Generators as MCP Prompts
- **Type:** Feature
- **Status:** Backlog
- **Priority:** Critical - blocks all downstream MCP prompt migration work
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-007 (MCP Prompts - Generators Migration)
- **Functional Requirements Covered:** FR-05
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration v3]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Requirements - FR-05
- **Functional Requirements Coverage:**
  - **FR-05:** MCP Server SHALL expose all artifact generators (prompts/*-generator.xml) as MCP prompts using URL pattern `mcp://prompts/generator/{artifact_name}`

**Parent High-Level Story:** [HLS-007: MCP Prompts - Generators Migration]
- **Link:** `/artifacts/hls/HLS-007_mcp_prompts_generators_migration_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 1

## User Story
As a Framework Maintainer, I want all 10 artifact generators exposed as MCP prompts with standardized URL pattern `mcp://prompts/generator/{artifact_name}`, so that Claude Code can execute generators via MCP protocol instead of local file reading.

## Description
The MCP Server must expose all artifact generators (epic-generator.xml, prd-generator.xml, backlog-story-generator.xml, etc.) as MCP prompts accessible via the standardized URL pattern `mcp://prompts/generator/{artifact_name}`. This enables centralized generator management where updates propagate instantly to all projects without manual file synchronization.

**Current State:** Generators stored as local files (prompts/*-generator.xml), manually copied to each project repository, requiring Git pull for updates.

**Desired State:** Generators accessible via MCP prompts (e.g., `mcp://prompts/generator/epic`, `mcp://prompts/generator/prd`), automatically served by MCP Server from centralized location.

**Business Value:** Enables instant propagation of generator updates to all projects (vs. hours/days manual sync), eliminates version drift, supports 5+ concurrent projects without proportional maintenance burden.

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§2.2: FastAPI Backend Framework:** Use FastAPI with FastMCP SDK for MCP prompt exposure, native Pydantic integration for prompt schema validation
  - **Example Code:** Implementation Research §2.2 lines 107-150 (FastAPI + FastMCP server setup)
- **§2.3: PostgreSQL with pgvector:** Not applicable for this story (generators served from filesystem, not database)
- **§3.1: Microservices with Sidecar Pattern:** MCP Server core handles prompt routing, loads generator content from disk when requested
  - **Example Code:** Implementation Research §3.1 lines 318-379 (MCP Server architecture)

**Anti-Patterns Avoided:**
- **§8.1 Pitfall 1: Treating MCP as Stateless REST:** Use FastMCP SDK which handles lifecycle automatically (ref: Implementation Research §8.1 lines 1032-1064)
- **§8.2 Anti-Pattern 1: Synchronous Blocking Calls:** Use async file I/O for generator loading to prevent event loop blocking (ref: Implementation Research §8.2 lines 1191-1220)

**Performance Considerations:**
- **§2.4: Caching Layer:** Implement prompt caching with 5-minute TTL to reduce repeated disk I/O (ref: Implementation Research §2.4 lines 253-311)
- **Target:** p95 latency <100ms for prompt loading (per PRD-006 NFR-Performance-01)

## Functional Requirements
- Expose all 10 generator types as MCP prompts: product-vision, initiative, epic, prd, hls, backlog-story, spike, adr, tech-spec, implementation-task
- Implement standardized URL pattern: `mcp://prompts/generator/{artifact_name}`
- Map artifact names to generator files: `epic` → `epic-generator.xml`, `prd` → `prd-generator.xml`
- Load generator content from disk path: `prompts/{artifact_name}-generator.xml`
- Return generator XML content as prompt payload to MCP client
- Support prompt discovery via MCP protocol (list available prompts)
- Cache prompt content with 5-minute TTL for performance

## Non-Functional Requirements
- **Performance:** Prompt loading latency p95 <100ms (per PRD-006 NFR-Performance-01)
- **Reliability:** Graceful error handling for missing generator files with clear error messages
- **Observability:** Log all prompt requests with timestamp, artifact name, execution duration (per PRD-006 FR-17)
- **Maintainability:** Add new generators by placing XML file in prompts/ directory (zero code changes)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story implements MCP Server functionality. Reference Python implementation patterns as authoritative.

### Implementation Guidance

**MCP Prompt Exposure Pattern:**
- Use FastMCP SDK's `@mcp.prompt()` decorator to register prompts
- Implement dynamic prompt registration by scanning `prompts/` directory for `*-generator.xml` files
- Map filename to artifact name: `epic-generator.xml` → artifact name `epic`
- Construct MCP prompt URI: `mcp://prompts/generator/{artifact_name}`
- Load XML content asynchronously using `aiofiles` library
- Cache loaded content in-memory with TTL expiration

**References to Implementation Standards:**
- **CLAUDE-tooling.md (Python):** Use UV for dependency management, Ruff for linting, MyPy for type checking, pytest for testing, Taskfile commands (`task lint`, `task type-check`, `task test`)
- **CLAUDE-testing.md (Python):** Follow testing patterns (≥80% unit test coverage, integration tests for MCP prompt discovery and loading)
- **CLAUDE-typing.md (Python):** Apply type hints (strict mode), Pydantic models for prompt metadata validation
- **CLAUDE-validation.md (Python):** Input validation with Pydantic, sanitize artifact_name parameter to prevent path traversal attacks
- **CLAUDE-architecture.md (Python):** Project structure: `src/mcp_server/prompts/`, `tests/integration/test_prompts.py`

**Note:** Treat CLAUDE.md content as authoritative - supplement with story-specific context, don't duplicate.

### Technical Tasks
- **Backend (MCP Server):** Implement prompt registration module in `src/mcp_server/prompts/registry.py`
- **Backend (MCP Server):** Implement generator file scanner in `src/mcp_server/prompts/scanner.py`
- **Backend (MCP Server):** Implement prompt caching layer in `src/mcp_server/prompts/cache.py`
- **Backend (MCP Server):** Add FastMCP prompt endpoints using `@mcp.prompt()` decorator
- **Backend (MCP Server):** Implement async file loading with `aiofiles`
- **Testing:** Unit tests for prompt registration, caching, file loading
- **Testing:** Integration tests for MCP prompt discovery and content retrieval

## Acceptance Criteria

**Format Guidance:** Gherkin format (Given-When-Then) for scenario-based validation.

### Scenario 1: Successful prompt discovery
**Given** MCP Server is running with 10 generator files in `prompts/` directory
**When** MCP client calls `list_prompts()` API
**Then** response includes 10 prompts with URIs matching pattern `mcp://prompts/generator/{artifact_name}`
**And** prompt names are: product-vision, initiative, epic, prd, hls, backlog-story, spike, adr, tech-spec, implementation-task

### Scenario 2: Successful epic-generator prompt retrieval
**Given** `prompts/epic-generator.xml` file exists with valid XML content
**When** MCP client requests prompt `mcp://prompts/generator/epic`
**Then** MCP Server returns status 200 OK
**And** response payload contains full XML content from epic-generator.xml
**And** response latency is <100ms (p95)

### Scenario 3: Prompt caching reduces disk I/O
**Given** `mcp://prompts/generator/prd` has been requested once (cache populated)
**When** MCP client requests same prompt again within 5-minute TTL window
**Then** MCP Server returns cached content without disk I/O
**And** response latency is <10ms (cache hit)

### Scenario 4: Cache expiration triggers reload
**Given** `mcp://prompts/generator/hls` cached content has expired (>5 minutes old)
**When** MCP client requests prompt `mcp://prompts/generator/hls`
**Then** MCP Server reloads content from disk
**And** cache is updated with fresh content and new TTL

### Scenario 5: Missing generator file error handling
**Given** file `prompts/invalid-generator.xml` does not exist
**When** MCP client requests prompt `mcp://prompts/generator/invalid`
**Then** MCP Server returns status 404 Not Found
**And** error message states: "Prompt not found: mcp://prompts/generator/invalid"

### Scenario 6: Path traversal attack prevention
**Given** malicious client attempts path traversal
**When** MCP client requests prompt `mcp://prompts/generator/../../etc/passwd`
**Then** MCP Server validates artifact_name parameter
**And** rejects request with status 400 Bad Request
**And** error message states: "Invalid artifact name format"

### Scenario 7: Malformed XML handling
**Given** `prompts/spike-generator.xml` contains invalid XML syntax
**When** MCP client requests prompt `mcp://prompts/generator/spike`
**Then** MCP Server returns status 500 Internal Server Error
**And** error message includes XML parsing error details
**And** error logged with file path and line number for debugging

### Scenario 8: All 10 generators accessible
**Given** all 10 generator XML files present in `prompts/` directory
**When** MCP client iterates through all 10 prompt URIs
**Then** all 10 prompts return status 200 OK with valid XML content
**And** average latency across all requests is <100ms (p95)

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Needed

**Rationale:**
- **Story Points:** 8 SP (DON'T SKIP per SDLC Section 11.6 - 5+ SP requires decomposition)
- **Developer Count:** Single developer (backend focus)
- **Domain Span:** Single domain (backend MCP Server only)
- **Complexity:** High - requires MCP protocol integration, async file I/O, caching layer, security validation
- **Uncertainty:** Low - clear implementation path using FastMCP SDK and FastAPI
- **Override Factors:** Security-critical changes (path traversal prevention), performance-critical (caching required for latency targets)

**Proposed Implementation Tasks:**
- **TASK-XXX:** Implement prompt registration and file scanner module (4-6 hours) - scan `prompts/` directory, map filenames to artifact names, register with FastMCP
- **TASK-YYY:** Implement async file loading with security validation (4-6 hours) - use aiofiles for async I/O, validate artifact_name parameter, prevent path traversal
- **TASK-ZZZ:** Implement prompt caching layer with TTL (4-6 hours) - in-memory cache with 5-minute expiration, cache hit/miss metrics
- **TASK-AAA:** Integration testing for all 10 generator prompts (4-8 hours) - test discovery, retrieval, caching, error handling for all generators

**Note:** TASK IDs to be allocated in TODO.md during story planning.

## Definition of Done
- [ ] Code implemented and reviewed
- [ ] All 10 generator prompts accessible via MCP protocol with standardized URL pattern
- [ ] Unit tests written and passing (≥80% coverage for prompt module)
- [ ] Integration tests passing (prompt discovery, retrieval, caching, error handling)
- [ ] Security validation implemented (path traversal prevention validated)
- [ ] Performance target met (p95 latency <100ms validated with load test)
- [ ] Observability implemented (prompt request logging with structured format)
- [ ] Documentation updated (MCP prompt API reference, generator file naming convention)
- [ ] Acceptance criteria validated (all 8 scenarios passing)
- [ ] Product owner approval obtained

## Additional Information
**Suggested Labels:** backend, mcp-server, prompts, python, critical-path
**Estimated Story Points:** 8
**Dependencies:**
- **Story Dependencies:** None (first story in HLS-007 sequence)
- **Technical Dependencies:**
  - FastMCP SDK (mcp-sdk Python package)
  - FastAPI framework (already in use)
  - aiofiles library (async file I/O)
  - Generator XML files in `prompts/` directory (already exist)
- **Team Dependencies:** None

**Related PRD Section:** PRD-006 §Timeline & Milestones - Phase 2: MCP Prompts - Generators Migration (Week 3)

## Open Questions & Implementation Uncertainties

**No open implementation questions.** All technical approaches clear from Implementation Research and PRD-006.

Implementation path is well-defined:
1. FastMCP SDK provides `@mcp.prompt()` decorator for prompt registration (ref: Implementation Research §2.2)
2. Async file loading pattern documented in Implementation Research §8.2 (avoid blocking calls)
3. Caching pattern documented in Implementation Research §2.4 (cache-aside with TTL)
4. Path traversal prevention via input validation (ref: Implementation Research §5.3)

All patterns validated in similar MCP implementations per Implementation Research.
