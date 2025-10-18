# User Story: Implement MCP Resource Server for Templates

## Metadata
- **Story ID:** US-031
- **Title:** Implement MCP Resource Server for Templates
- **Type:** Feature
- **Status:** Draft
- **Priority:** High (enables centralized template maintenance, complements pattern resources)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-006 (MCP Resources Migration)
- **Functional Requirements Covered:** FR-02
- **Informed By Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Functional Requirements - FR-02: MCP Server SHALL expose all artifact templates as named MCP resources
- **Functional Requirements Coverage:**
  - **FR-02:** MCP Server SHALL expose all artifact templates as named MCP resources

**Parent High-Level Story:** [HLS-006: MCP Resources Migration]
- **Link:** `/artifacts/hls/HLS-006_mcp_resources_migration_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 4: Implement MCP Resource Server for Templates

## User Story
As a Claude Code user, I want artifact templates (PRD, Epic, HLS, Backlog Story, etc.) accessible via MCP protocol, so that I receive centrally maintained templates without manual file synchronization.

## Description
Artifact templates (`prompts/templates/*.xml`) define the structure for SDLC artifacts (PRD, Epic, HLS, Backlog Story, Spike, ADR, Tech Spec, Implementation Task). Currently, these templates reside as local files in each project repository, creating version drift across projects.

This story extends the MCP resource server (from US-030) to expose templates as named MCP resources. The server will:
1. Load template files from disk (`prompts/templates/*.xml`)
2. Expose them as MCP resources with URI scheme: `mcp://resources/templates/{artifact-type}-template`
3. Return template XML content when Claude Code requests resource
4. Handle missing templates with clear error messages
5. Support all 10 artifact template types: product-vision, initiative, epic, prd, hls, backlog-story, spike, adr, tech-spec, implementation-task

After implementation, generators can request `mcp://resources/templates/prd-template` and receive prd-template.xml content from the server, eliminating per-project duplication.

## Implementation Research References

**Primary Research Document:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

**Technical Patterns Applied:**
- **§2.2: FastAPI Backend Framework:** Extend existing FastAPI resource endpoints to serve templates (ref: Implementation Research §2.2 - Backend Framework: FastAPI 0.100+)
- **§2.1: Python 3.11+ with Async I/O:** Use async file I/O (aiofiles) to read template files without blocking event loop (ref: Implementation Research §2.1 - Programming Language: Python 3.11+)
- **§5.3: Input Validation:** Validate template name parameter to prevent path traversal attacks using Pydantic constrained strings (ref: Implementation Research §5.3 - Input Validation and Command Injection Prevention)
- **§6.1: Structured Logging:** Log template access events with template name, latency, and client context (ref: Implementation Research §6.1 - Structured Logging)

**Anti-Patterns Avoided:**
- **§8.2: Synchronous Blocking Calls in Async Context:** Use aiofiles for async file reading, not synchronous `open()` (ref: Implementation Research §8.2 - Anti-Pattern 1)

**Performance Considerations:**
- **§2.4: Caching Layer:** Template caching deferred to US-032. Initial implementation reads from disk on each request

## Functional Requirements
1. MCP Server exposes resource endpoint handling `mcp://resources/templates/{artifact-type}-template` URIs
2. Template name parameter validated to prevent path traversal (e.g., reject "../", absolute paths)
3. Server loads file from `prompts/templates/{artifact-type}-template.xml`
4. File content returned as plain text (XML format) in MCP response
5. Missing template returns MCP error with clear message: "Resource not found: mcp://resources/templates/{artifact-type}-template"
6. Server logs template access events (template name, latency, success/failure)
7. Support for all 10 artifact templates:
   - product-vision-template
   - initiative-template
   - epic-template
   - prd-template
   - hls-template
   - backlog-story-template
   - spike-template
   - adr-template
   - tech-spec-template
   - implementation-task-template

## Non-Functional Requirements
- **Performance:** Template loading latency <100ms p95 (measured from request arrival to response sent, no caching yet)
- **Security:** Input validation prevents path traversal attacks
- **Reliability:** Graceful error handling for missing files, disk I/O errors
- **Observability:** Structured logging captures template access patterns for optimization
- **Maintainability:** Code reuses resource loading logic from US-030 (DRY principle)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** When implementing template resource server, follow established implementation standards. Supplement with story-specific technical guidance.

**References to Implementation Standards:**
- **prompts/CLAUDE/python/patterns-tooling.md:** Use Taskfile commands for development workflow
- **prompts/CLAUDE/python/patterns-testing.md:** Follow testing patterns (80% coverage minimum, async test support)
- **prompts/CLAUDE/python/patterns-typing.md:** Apply type hints (strict mode, Pydantic models for validation)
- **prompts/CLAUDE/python/patterns-architecture.md:** Follow project structure, modularity patterns
- **prompts/CLAUDE/python/patterns-validation.md:** Input validation with Pydantic, security patterns

### Implementation Guidance

**Story-Specific Technical Approach:**

1. **Extend Resource Handler (FastAPI):**
   ```python
   from fastapi import FastAPI, HTTPException
   from pydantic import BaseModel, constr
   import aiofiles
   from pathlib import Path

   @app.get("/mcp/resources/templates/{artifact_type}-template")
   async def get_template_resource(artifact_type: str):
       """Returns artifact template XML content as MCP resource"""
       # Validate input to prevent path traversal
       if ".." in artifact_type or artifact_type.startswith("/"):
           raise HTTPException(status_code=400, detail="Invalid template name")

       # Validate artifact_type against allowed template names
       allowed_templates = [
           "product-vision", "initiative", "epic", "prd", "hls",
           "backlog-story", "spike", "adr", "tech-spec", "implementation-task"
       ]
       if artifact_type not in allowed_templates:
           raise HTTPException(
               status_code=404,
               detail=f"Resource not found: mcp://resources/templates/{artifact_type}-template"
           )

       # Construct file path
       file_path = Path(f"prompts/templates/{artifact_type}-template.xml")

       # Check file exists
       if not file_path.exists():
           raise HTTPException(
               status_code=404,
               detail=f"Resource not found: mcp://resources/templates/{artifact_type}-template"
           )

       # Read file asynchronously
       async with aiofiles.open(file_path, mode='r') as f:
           content = await f.read()

       return {"uri": f"mcp://resources/templates/{artifact_type}-template", "content": content}
   ```

2. **Template Enumeration Endpoint (Optional):**
   - Add endpoint to list all available templates
   - Useful for Claude Code to discover available template resources
   ```python
   @app.get("/mcp/resources/templates")
   async def list_template_resources():
       """Returns list of available template resources"""
       templates_dir = Path("prompts/templates")
       template_files = [f.stem for f in templates_dir.glob("*-template.xml")]
       return {
           "templates": [
               {"name": name, "uri": f"mcp://resources/templates/{name}"}
               for name in template_files
           ]
       }
   ```

3. **Refactor Shared Logic:**
   - Extract common file loading logic from patterns and templates into shared utility function
   - Reduce code duplication (DRY principle)

4. **Testing Strategy:**
   - Unit tests: Validate template name validation, allowed template list
   - Integration tests: Verify template loading for all 10 artifact types
   - Security tests: Attempt path traversal attacks, verify rejection

### Technical Tasks
- [ ] Implement FastAPI resource endpoint: `GET /mcp/resources/templates/{artifact_type}-template`
- [ ] Add Pydantic validation for template name (path traversal protection)
- [ ] Implement whitelist validation (allowed template names only)
- [ ] Implement async file loading with aiofiles (reuse from US-030)
- [ ] Add structured logging for template access events
- [ ] Implement error handling (file not found, I/O errors)
- [ ] Optional: Implement template enumeration endpoint (`GET /mcp/resources/templates`)
- [ ] Refactor shared file loading logic into utility function (DRY)
- [ ] Write unit tests for template handler (80% coverage)
- [ ] Write integration tests for all 10 template types
- [ ] Write security tests for path traversal protection

## Acceptance Criteria

### Scenario 1: Template resource accessible via MCP
**Given** MCP Server is running
**When** Claude Code requests `mcp://resources/templates/prd-template`
**Then** server returns prd-template.xml file content
**And** response includes URI: "mcp://resources/templates/prd-template"
**And** content is plain text (XML format)
**And** response latency <100ms (p95 target)

### Scenario 2: All 10 artifact templates accessible
**Given** MCP Server is running
**When** Claude Code requests each of the 10 template URIs (product-vision, initiative, epic, prd, hls, backlog-story, spike, adr, tech-spec, implementation-task)
**Then** server returns corresponding template XML content for each request
**And** all responses have latency <100ms (p95)

### Scenario 3: Missing template handled gracefully
**Given** MCP Server is running
**When** Claude Code requests `mcp://resources/templates/nonexistent-template`
**Then** server returns 404 error
**And** error message includes: "Resource not found: mcp://resources/templates/nonexistent-template"
**And** error is logged with structured logging

### Scenario 4: Path traversal attack prevented
**Given** MCP Server is running
**When** Claude Code requests `mcp://resources/templates/../../../etc/passwd-template`
**Then** server returns 400 error (Bad Request)
**And** error message indicates invalid template name
**And** security event logged with template name attempt
**And** no file system access occurs outside prompts/templates/ directory

### Scenario 5: Template name whitelist enforced
**Given** MCP Server is running
**When** Claude Code requests template with valid path syntax but not in whitelist (e.g., `custom-template`)
**Then** server returns 404 error
**And** error message indicates template not found

### Scenario 6: Template access logged
**Given** MCP Server is running and logging configured
**When** Claude Code requests any template
**Then** server logs event with fields: resource_uri, latency_ms, status_code, file_size_bytes
**And** log format is JSON (structured logging)

### Scenario 7: Optional - Template enumeration
**Given** MCP Server is running with enumeration endpoint
**When** Claude Code requests `mcp://resources/templates`
**Then** server returns list of all available templates with URIs
**And** list includes all 10 artifact template names

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 5 SP (at threshold - CONSIDER territory)
- **Developer Count:** Single developer (extends US-030 implementation)
- **Domain Span:** Single domain (backend API, similar to US-030)
- **Complexity:** Low-moderate - extends existing pattern resource server with similar logic
- **Uncertainty:** Low - reuses patterns from US-030, straightforward extension
- **Override Factors:** None - not cross-domain, not security-critical beyond path validation already implemented in US-030

Per SDLC Section 11.6 Decision Matrix: "3-5 SP, single dev, familiar domain → CONSIDER". Since this story extends US-030 with very similar logic (file loading, validation, error handling), and developer is already familiar with codebase from US-030, overhead of task decomposition is not justified.

**Note:** If US-030 implementation complexity proves higher than estimated, reconsider task decomposition for US-031.

## Definition of Done
- [ ] FastAPI template resource endpoint implemented (`/mcp/resources/templates/{artifact_type}-template`)
- [ ] Template name validation implemented (whitelist + path traversal protection)
- [ ] Async file loading with aiofiles (reused from US-030)
- [ ] Structured logging for template access events
- [ ] Error handling (404, 400, 500) with clear messages
- [ ] Unit tests written and passing (80% coverage)
- [ ] Integration tests passing for all 10 template types
- [ ] Security tests passing (path traversal protection validated)
- [ ] Optional: Template enumeration endpoint implemented
- [ ] Shared file loading logic refactored (DRY)
- [ ] Manual testing: Claude Code can fetch templates via MCP protocol
- [ ] Product Owner approval obtained

## Additional Information
**Suggested Labels:** backend, mcp-resources, templates, security
**Estimated Story Points:** 5
**Dependencies:**
- **Depends On:** US-030 (reuses resource server infrastructure and file loading patterns)
- **Blocks:** US-032 (caching implementation includes templates)

**Related PRD Section:** PRD-006 §Functional Requirements - FR-02

## Open Questions & Implementation Uncertainties

No open implementation questions. All technical approaches clear from US-030 implementation patterns and HLS-006 decomposition plan.

**Implementation strategy is straightforward:** Extend US-030 resource handler with templates endpoint, reuse validation and file loading logic. No technical decisions required beyond code reuse.

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-006_mcp_resources_migration_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md` (§2.2 FastAPI, §2.1 Python Async, §5.3 Input Validation, §6.1 Structured Logging)
