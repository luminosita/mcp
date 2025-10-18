# User Story: Implement MCP Resource Server for Implementation Pattern Files

## Metadata
- **Story ID:** US-030
- **Title:** Implement MCP Resource Server for Implementation Pattern Files
- **Type:** Feature
- **Status:** Draft
- **Version:** v2 (Applied feedback from US-028-033_v1_comments.md)
- **Priority:** Critical (core MCP resources infrastructure enabling framework centralization)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-006 (MCP Resources Migration)
- **Functional Requirements Covered:** FR-01
- **Informed By Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Functional Requirements - FR-01: MCP Server SHALL expose all implementation pattern files as named MCP resources
- **Functional Requirements Coverage:**
  - **FR-01:** MCP Server SHALL expose all implementation pattern files (formerly CLAUDE.md files) as named MCP resources

**Parent High-Level Story:** [HLS-006: MCP Resources Migration]
- **Link:** `/artifacts/hls/HLS-006_mcp_resources_migration_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 3: Implement MCP Resource Server for Implementation Pattern Files

## User Story
As a Claude Code user, I want implementation pattern files (patterns-*.md, sdlc-core.md) accessible via MCP protocol, so that I receive centrally maintained framework instructions without manual file synchronization.

## Description
Implementation pattern files (patterns-core.md, patterns-tooling.md, patterns-testing.md, etc.) and SDLC framework content (sdlc-core.md) currently reside as local files in each project repository. This creates version drift and manual synchronization overhead across multiple projects.

This story implements MCP resource server functionality to expose these files as named MCP resources, enabling Claude Code to fetch them dynamically from the MCP server instead of reading local copies. The server will:
1. Load pattern files from disk (`prompts/CLAUDE/python/*.md`, `prompts/CLAUDE/sdlc-core.md`)
2. Expose them as MCP resources with URI scheme: `mcp://resources/patterns/{name}` and `mcp://resources/sdlc/core`
3. Support language-specific subdirectories (Python, Go) for multi-language projects
4. Return file content as plain text when Claude Code requests resource
5. Handle missing resources with clear error messages

After implementation, Claude Code can request `mcp://resources/patterns/core` and receive patterns-core.md content from the server, eliminating per-project duplication.

## Implementation Research References

**Primary Research Document:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

**Technical Patterns Applied:**
- **§2.2: FastAPI Backend Framework:** Use FastAPI to serve MCP resources with Pydantic validation for resource names (ref: Implementation Research §2.2 - Backend Framework: FastAPI 0.100+)
- **§2.1: Python 3.11+ with Async I/O:** Use async file I/O (aiofiles) to read pattern files without blocking event loop (ref: Implementation Research §2.1 - Programming Language: Python 3.11+)
- **§5.3: Input Validation:** Validate resource name parameter to prevent path traversal attacks (e.g., reject "../" sequences) using Pydantic constrained strings (ref: Implementation Research §5.3 - Input Validation and Command Injection Prevention)
- **§6.1: Structured Logging:** Log resource access events with resource name, latency, and client context (ref: Implementation Research §6.1 - Structured Logging)

**Anti-Patterns Avoided:**
- **§8.2: Synchronous Blocking Calls in Async Context:** Use aiofiles for async file reading, not synchronous `open()` (ref: Implementation Research §8.2 - Anti-Pattern 1)
- **§8.2: Storing State in Server Instance Variables:** Resource file paths derived from disk on each request, no in-memory state (deferred caching to US-032) (ref: Implementation Research §8.2 - Anti-Pattern 2)

**Performance Considerations:**
- **§2.4: Caching Layer:** Resource caching deferred to US-032. Initial implementation reads from disk on each request (acceptable latency with async I/O)

## Functional Requirements
1. MCP Server exposes resource endpoint handling `mcp://resources/patterns/{name}` URIs
2. MCP Server exposes resource endpoint handling `mcp://resources/sdlc/core` URI
3. Resource name parameter validated to prevent path traversal (e.g., reject "../", absolute paths)
4. Server loads file from `prompts/CLAUDE/python/{name}.md` for pattern resources
5. Server loads file from `prompts/CLAUDE/sdlc-core.md` for SDLC core resource
6. Language-specific subdirectory support: `mcp://resources/patterns/python/core` maps to `prompts/CLAUDE/python/patterns-core.md`
7. File content returned as plain text in MCP response
8. Missing resource returns MCP error with clear message: "Resource not found: mcp://resources/patterns/{name}"
9. Server logs resource access events (resource name, latency, success/failure)

## Non-Functional Requirements
- **Performance:** Resource loading latency <100ms p95 (measured from request arrival to response sent, no caching yet)
- **Security:** Input validation prevents path traversal attacks
- **Reliability:** Graceful error handling for missing files, disk I/O errors
- **Observability:** Structured logging captures resource access patterns for optimization
- **Maintainability:** Clear code structure separating resource routing, file loading, and error handling

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** When implementing resource server, follow established implementation standards. Supplement with story-specific technical guidance.

**References to Implementation Standards:**
- **prompts/CLAUDE/python/patterns-tooling.md:** Use Taskfile commands (`task test`, `task lint`, `task type-check`, `task format`) for development workflow
- **prompts/CLAUDE/python/patterns-testing.md:** Follow testing patterns (80% coverage minimum, async test support with pytest-asyncio)
- **prompts/CLAUDE/python/patterns-typing.md:** Apply type hints (strict mode, Pydantic models for validation per patterns-validation.md)
- **prompts/CLAUDE/python/patterns-architecture.md:** Follow project structure, modularity patterns
- **prompts/CLAUDE/python/patterns-validation.md:** Input validation with Pydantic, security patterns for path validation

### Implementation Guidance

**Story-Specific Technical Approach:**

1. **Configuration Settings (`.env` / `settings.py`):**
   ```python
   # .env.example
   PATTERNS_BASE_DIR=prompts/CLAUDE
   SDLC_CORE_FILE_PATH=prompts/CLAUDE/sdlc-core.md

   # settings.py
   from pydantic_settings import BaseSettings

   class Settings(BaseSettings):
       PATTERNS_BASE_DIR: str = "prompts/CLAUDE"
       SDLC_CORE_FILE_PATH: str = "prompts/CLAUDE/sdlc-core.md"

       class Config:
           env_file = ".env"

   settings = Settings()
   ```

2. **Resource Handler Implementation (FastAPI):**
   ```python
   from fastapi import FastAPI, HTTPException
   from pydantic import BaseModel, Field, constr
   import aiofiles
   from pathlib import Path

   app = FastAPI()

   class ResourceRequest(BaseModel):
       """MCP resource request model with path traversal protection"""
       name: constr(pattern=r'^[a-z0-9_/-]+$')  # Alphanumeric, underscores, hyphens, forward slashes only
       language: str = Field(default="python", pattern=r'^[a-z]+$')

   @app.get("/mcp/resources/patterns/{name}")
   async def get_pattern_resource(name: str, language: str = "python"):
       """Returns implementation pattern file content as MCP resource"""
       # Validate input to prevent path traversal
       if ".." in name or name.startswith("/"):
           raise HTTPException(status_code=400, detail="Invalid resource name")

       # Construct file path using configuration
       patterns_dir = Path(settings.PATTERNS_BASE_DIR) / language
       file_path = patterns_dir / f"patterns-{name}.md"

       # Check file exists
       if not file_path.exists():
           raise HTTPException(
               status_code=404,
               detail=f"Resource not found: mcp://resources/patterns/{name}"
           )

       # Read file asynchronously
       async with aiofiles.open(file_path, mode='r') as f:
           content = await f.read()

       return {"uri": f"mcp://resources/patterns/{name}", "content": content}

   @app.get("/mcp/resources/sdlc/core")
   async def get_sdlc_core_resource():
       """Returns SDLC framework core content as MCP resource"""
       # Use configuration for SDLC core file path
       file_path = Path(settings.SDLC_CORE_FILE_PATH)

       if not file_path.exists():
           raise HTTPException(
               status_code=404,
               detail="Resource not found: mcp://resources/sdlc/core"
           )

       async with aiofiles.open(file_path, mode='r') as f:
           content = await f.read()

       return {"uri": "mcp://resources/sdlc/core", "content": content}
   ```

3. **Structured Logging:**
   - Log resource access events with resource name, latency, file size
   - Use structlog for JSON-formatted logs (ref: Implementation Research §6.1)

4. **Error Handling:**
   - Distinguish file-not-found (404) from disk I/O errors (500)
   - Return user-friendly error messages with resource URI

5. **Testing Strategy:**
   - Unit tests: Validate resource name sanitization, path construction
   - Integration tests: Verify file loading, error handling for missing files
   - Security tests: Attempt path traversal attacks, verify rejection

### Technical Tasks
- [ ] Implement FastAPI resource endpoint: `GET /mcp/resources/patterns/{name}`
- [ ] Implement FastAPI resource endpoint: `GET /mcp/resources/sdlc/core`
- [ ] Add Pydantic validation for resource name (path traversal protection)
- [ ] Implement async file loading with aiofiles
- [ ] Add structured logging for resource access events
- [ ] Implement error handling (file not found, I/O errors)
- [ ] Write unit tests for resource handler (80% coverage)
- [ ] Write integration tests for file loading
- [ ] Write security tests for path traversal protection
- [ ] Add Taskfile commands for running resource server locally

## Acceptance Criteria

### Scenario 1: Pattern resource accessible via MCP
**Given** MCP Server is running
**When** Claude Code requests `mcp://resources/patterns/core`
**Then** server returns patterns-core.md file content
**And** response includes URI: "mcp://resources/patterns/core"
**And** content is plain text (markdown format)
**And** response latency <100ms (p95 target)

### Scenario 2: Language-specific pattern resource accessible
**Given** MCP Server has Python and Go pattern files
**When** Claude Code requests `mcp://resources/patterns/python/core`
**Then** server returns `prompts/CLAUDE/python/patterns-core.md` content
**And** when Claude Code requests `mcp://resources/patterns/go/core`
**Then** server returns `prompts/CLAUDE/go/patterns-core.md` content

### Scenario 3: SDLC core resource accessible
**Given** MCP Server is running
**When** Claude Code requests `mcp://resources/sdlc/core`
**Then** server returns sdlc-core.md file content
**And** response includes URI: "mcp://resources/sdlc/core"
**And** content is plain text (markdown format)

### Scenario 4: Missing resource handled gracefully
**Given** MCP Server is running
**When** Claude Code requests `mcp://resources/patterns/nonexistent`
**Then** server returns 404 error
**And** error message includes: "Resource not found: mcp://resources/patterns/nonexistent"
**And** error is logged with structured logging

### Scenario 5: Path traversal attack prevented
**Given** MCP Server is running
**When** Claude Code requests `mcp://resources/patterns/../../../etc/passwd`
**Then** server returns 400 error (Bad Request)
**And** error message indicates invalid resource name
**And** security event logged with resource name attempt
**And** no file system access occurs outside prompts/CLAUDE/ directory

### Scenario 6: Resource access logged
**Given** MCP Server is running and logging configured
**When** Claude Code requests any resource
**Then** server logs event with fields: resource_uri, latency_ms, status_code, file_size_bytes
**And** log format is JSON (structured logging)

### Scenario 7: Disk I/O error handled
**Given** resource file exists but disk I/O fails (e.g., permissions issue)
**When** Claude Code requests resource
**Then** server returns 500 error (Internal Server Error)
**And** error message indicates server-side issue (not missing file)
**And** error logged with exception details

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Needed

**Rationale:**
- **Story Points:** 8 SP (exceeds 5 SP threshold - DON'T SKIP per decision matrix)
- **Developer Count:** Potentially multiple developers (backend API + security validation + testing)
- **Domain Span:** Cross-domain (backend API, file I/O, security validation, observability)
- **Complexity:** Moderate - involves security considerations, async I/O, MCP protocol integration
- **Uncertainty:** Low-moderate - clear implementation approach but security validation requires careful testing
- **Override Factors:** Security-critical (path traversal protection essential)

Per SDLC Section 11.6 Decision Matrix: "5+ SP, any team size → DON'T SKIP (Complexity requires decomposition)". Additionally, security-critical override factor triggers task decomposition requirement.

**Proposed Implementation Tasks** (TASK IDs to be allocated):
- **TASK-XXX:** Implement FastAPI resource endpoints with Pydantic validation (4-6 hours)
  - FastAPI routes for patterns/{name} and sdlc/core
  - Pydantic models with path traversal protection
  - Basic error handling

- **TASK-YYY:** Implement async file loading and error handling (3-4 hours)
  - Async file I/O with aiofiles
  - File existence checks
  - Distinguish 404 vs 500 errors

- **TASK-ZZZ:** Add structured logging and observability (2-3 hours)
  - structlog integration
  - Resource access event logging
  - Security event logging (path traversal attempts)

- **TASK-AAA:** Comprehensive testing (unit, integration, security) (4-5 hours)
  - Unit tests for resource name validation
  - Integration tests for file loading
  - Security tests for path traversal attacks
  - 80% coverage target

**Total Estimated Task Hours:** 13-18 hours (aligns with 8 SP estimate)

**Note:** TASK IDs to be allocated in TODO.md during sprint planning.

## Definition of Done
- [ ] FastAPI resource endpoints implemented (`/mcp/resources/patterns/{name}`, `/mcp/resources/sdlc/core`)
- [ ] Pydantic validation implemented (path traversal protection)
- [ ] Async file loading with aiofiles
- [ ] Structured logging for resource access events
- [ ] Error handling (404, 400, 500) with clear messages
- [ ] Unit tests written and passing (80% coverage)
- [ ] Integration tests passing (file loading, error cases)
- [ ] Security tests passing (path traversal protection validated)
- [ ] Manual testing: Claude Code can fetch resources via MCP protocol
- [ ] Taskfile commands added for local server execution
- [ ] Product Owner approval obtained

## Additional Information
**Suggested Labels:** backend, mcp-resources, security, performance
**Estimated Story Points:** 8
**Dependencies:**
- **Depends On:** US-028 (sdlc-core.md must exist)
- **Depends On:** US-029 (files must be renamed to patterns-*.md)
- **Blocks:** US-032 (caching implementation depends on resource server working)
- **Blocks:** US-033 (performance optimization depends on baseline implementation)

**Related PRD Section:** PRD-006 §Functional Requirements - FR-01

## Decisions Made

### D1: MCP Resource URI Scheme
**Decision:** Use nested URI per HLS-006 examples. Aligns with REST best practices and semantic resource naming.

**Context:** HLS-006 shows nested URI examples (`mcp://resources/patterns/python/core`), which is more RESTful than query parameter approach (`mcp://resources/patterns/core?lang=python`).

**Rationale:** Nested URIs provide better semantic clarity and align with RESTful API design principles.

### D2: Error Response Format
**Decision:** Spike needed for this decision.

**Context:** MCP protocol may have specific error format expectations. FastAPI returns standard HTTP error format. Investigation needed to determine if custom exception handlers required.

**Action Required:** Create spike to investigate MCP SDK documentation for expected error response schema before implementing error handling.

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-006_mcp_resources_migration_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md` (§2.2 FastAPI, §2.1 Python Async, §5.3 Input Validation, §6.1 Structured Logging)
