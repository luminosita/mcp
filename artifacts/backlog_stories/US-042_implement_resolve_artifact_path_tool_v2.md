# User Story: Implement resolve_artifact_path Tool

## Metadata
- **Story ID:** US-042
- **Title:** Implement resolve_artifact_path Tool
- **Type:** Feature
- **Status:** Draft
- **Priority:** Critical (provides deterministic artifact resolution for MCP resource access)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-008 (MCP Tools - Validation and Path Resolution)
- **Functional Requirements Covered:** FR-07
- **Informed By Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Functional Requirements - FR-07
- **Functional Requirements Coverage:**
  - **FR-07:** MCP Server SHALL provide `resolve_artifact_path` tool that accepts artifact type, ID, and version, returning MCP resource URI for accessing the artifact

**Parent High-Level Story:** [HLS-008: MCP Tools - Validation and Path Resolution]
- **Link:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 3: Implement resolve_artifact_path Tool

## User Story
As Claude Code, I want a tool that resolves artifact identifiers to MCP resource URIs, so that I can access artifacts via MCP protocol with <5% error rate instead of 20-30% AI inference errors.

## Description
Currently, Claude Code uses AI inference to construct MCP resource URIs from artifact identifiers. This approach is error-prone (20-30% error rate due to ID format mistakes), token-intensive (~1-2k tokens per resolution), and slow (~1 second inference time).

This story implements a deterministic Python tool (`resolve_artifact_path`) that:
1. Accepts artifact metadata (type, ID, version)
2. Validates artifact identifier format
3. Constructs correct MCP resource URI following established patterns
4. Returns resource URI or structured error (artifact not found)

The tool reduces path resolution errors from 20-30% to <5%, execution time from ~1s to <200ms, and eliminates token consumption for path resolution operations.

## Implementation Research References

**Primary Research Document:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

**Technical Patterns Applied:**
- **§2.1: Python 3.11+ with Type Safety:** Use Pydantic models for input/output schemas with full type hints (ref: Implementation Research §2.1 - Programming Language: Python 3.11+)
- **§2.2: FastAPI Integration:** Expose tool as MCP tool via FastAPI with auto-generated OpenAPI documentation (ref: Implementation Research §2.2 - Backend Framework: FastAPI 0.100+)
- **§5.3: Input Validation:** Validate artifact type and ID with Pydantic, reject invalid inputs (ref: Implementation Research §5.3 - Input Validation and Command Injection Prevention)
- **§6.1: Structured Logging:** Log resolution invocations with artifact type, ID, version, result URI, duration (ref: Implementation Research §6.1 - Structured Logging)

**Anti-Patterns Avoided:**
- **§8.1: Poor Error Handling:** Return structured error responses distinguishing "not found", "invalid format" (ref: Implementation Research §8.1 - Pitfall 3)

**Performance Considerations:**
- **§2.4: Caching Layer:** Resource URI construction is lightweight (no caching needed for URI generation, but artifact existence checks may benefit from caching)

## Functional Requirements
1. Tool accepts three parameters:
   - `artifact_type` (string): Artifact type (e.g., "epic", "prd", "hls", "backlog_story")
   - `artifact_id` (string): Artifact ID (e.g., "006", "042")
   - `version` (int): Version number (e.g., 1, 2, 3)
2. Tool validates inputs:
   - Artifact type is allowed value (epic, prd, hls, backlog_story, tech_spec, adr, spike, task, etc.)
   - Artifact ID is numeric string (3 digits, e.g., "006", "042", "123")
   - Version is positive integer
3. Tool constructs MCP resource URI following pattern:
   - Pattern: `mcp://resources/artifacts/{artifact_type}/{artifact_id}`
   - Example: `mcp://resources/artifacts/epic/006`
   - Note: Version not included in URI (MCP resource server handles version resolution)
4. Tool verifies artifact exists at configured artifacts directory before returning URI
5. Tool returns structured JSON response:
   ```json
   // Success
   {
     "success": true,
     "resource_uri": "mcp://resources/artifacts/epic/006"
   }

   // Error (not found)
   {
     "success": false,
     "error": "not_found",
     "message": "Artifact not found: epic/006 version 1",
     "details": "No file matching pattern EPIC-006*_v1.md in artifacts/epics/"
   }

   // Error (invalid input)
   {
     "success": false,
     "error": "invalid_input",
     "message": "Invalid artifact type: unknown_type",
     "details": "Allowed types: epic, prd, hls, backlog_story, tech_spec, adr, spike, task"
   }
   ```
6. Tool execution completes in <200ms p95 (per PRD-006 NFR-Performance-02, path resolution subset)
7. Tool logs resolution invocations with timestamp, artifact type, ID, version, result URI, duration

## Non-Functional Requirements
- **Performance:** Path resolution latency <200ms p95 (subset of NFR-Performance-02 <500ms tool execution target)
- **Accuracy:** Deterministic resolution (same input → same output, 100% consistency)
- **Reliability:** Handle missing artifacts gracefully, return clear error messages
- **Observability:** Structured logging captures resolution patterns for debugging

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** Follow established implementation patterns for MCP tools. Supplement with story-specific URI resolution logic.

**References to Implementation Standards:**
- **prompts/CLAUDE/python/patterns-tooling.md:** Use Taskfile commands (`task test`, `task lint`, `task type-check`)
- **prompts/CLAUDE/python/patterns-testing.md:** Testing patterns (80% coverage, async tests)
- **prompts/CLAUDE/python/patterns-typing.md:** Type hints with mypy strict mode, Pydantic models
- **prompts/CLAUDE/python/patterns-validation.md:** Input validation with Pydantic, security patterns
- **prompts/CLAUDE/python/patterns-architecture.md:** Project structure following established patterns

### Implementation Guidance

**Story-Specific Technical Approach:**

1. **Pydantic Models for Tool Input/Output:**
   ```python
   from pydantic import BaseModel, Field, validator
   from typing import Optional, Literal

   class ResolveArtifactPathInput(BaseModel):
       """Input schema for resolve_artifact_path tool"""
       artifact_type: Literal[
           "epic", "prd", "hls", "backlog_story",
           "tech_spec", "adr", "spike", "task",
           "product_vision", "initiative"
       ] = Field(..., description="Artifact type")
       artifact_id: str = Field(
           ...,
           pattern=r'^\d{3}$',
           description="Artifact ID (3 digits, e.g., '006', '042')"
       )
       version: int = Field(..., ge=1, le=999, description="Version number")

   class ResolveArtifactPathSuccess(BaseModel):
       """Successful resolution result"""
       success: Literal[True] = True
       resource_uri: str = Field(..., description="MCP resource URI")

   class ResolveArtifactPathError(BaseModel):
       """Failed resolution result"""
       success: Literal[False] = False
       error: Literal["not_found", "invalid_input"]
       message: str
       details: Optional[str] = None

   ResolveArtifactPathResult = ResolveArtifactPathSuccess | ResolveArtifactPathError
   ```

2. **Artifact Resolution Logic:**
   ```python
   import glob
   from pathlib import Path
   from config import settings

   class ArtifactResolver:
       # Mapping from artifact type to ID prefix
       TYPE_PREFIX_MAP = {
           "epic": "EPIC",
           "prd": "PRD",
           "hls": "HLS",
           "backlog_story": "US",
           "tech_spec": "SPEC",
           "adr": "ADR",
           "spike": "SPIKE",
           "task": "TASK",
           "product_vision": "VIS",
           "initiative": "INIT"
       }

       # Mapping from artifact type to subdirectory
       TYPE_DIR_MAP = {
           "epic": "epics",
           "prd": "prds",
           "hls": "hls",
           "backlog_story": "backlog_stories",
           "tech_spec": "tech_specs",
           "adr": "adrs",
           "spike": "spikes",
           "task": "tasks",
           "product_vision": "product_visions",
           "initiative": "initiatives"
       }

       def __init__(self, artifacts_base_dir: Optional[str] = None):
           self.artifacts_base_dir = Path(artifacts_base_dir or settings.PATTERNS_BASE_DIR)

       def resolve(
           self,
           artifact_type: str,
           artifact_id: str,
           version: int
       ) -> ResolveArtifactPathResult:
           """Resolves artifact to MCP resource URI"""
           # Step 1: Construct file search pattern
           prefix = self.TYPE_PREFIX_MAP[artifact_type]
           subdir = self.TYPE_DIR_MAP[artifact_type]
           search_pattern = f"{prefix}-{artifact_id}*_v{version}.md"
           search_path = self.artifacts_base_dir / subdir / search_pattern

           # Step 2: Check if artifact file exists
           matches = list(glob.glob(str(search_path)))

           if len(matches) == 0:
               return ResolveArtifactPathError(
                   error="not_found",
                   message=f"Artifact not found: {artifact_type}/{artifact_id} version {version}",
                   details=f"No file matching pattern {search_pattern} in {self.artifacts_base_dir / subdir}/"
               )

           # Step 3: Construct MCP resource URI
           resource_uri = f"mcp://resources/artifacts/{artifact_type}/{artifact_id}"

           return ResolveArtifactPathSuccess(
               resource_uri=resource_uri
           )
   ```

3. **MCP Tool Implementation:**
   ```python
   from mcp.server.fastmcp import FastMCP
   import structlog
   import time

   mcp = FastMCP(name="MCPServer", version="1.0.0")
   logger = structlog.get_logger()
   resolver = ArtifactResolver()

   @mcp.tool(
       name="resolve_artifact_path",
       description="""
       Resolves artifact identifier to MCP resource URI.

       Use this tool when:
       - You need to access an artifact via MCP protocol
       - You have artifact type, ID, and version
       - You want deterministic URI construction instead of AI inference

       Supports artifact types:
       - epic, prd, hls, backlog_story
       - tech_spec, adr, spike, task
       - product_vision, initiative

       Returns MCP resource URI (e.g., mcp://resources/artifacts/epic/006)
       or structured error if artifact not found.

       Reduces URI construction errors from 20-30% (AI inference) to <5% (deterministic).
       """
   )
   async def resolve_artifact_path(params: ResolveArtifactPathInput) -> ResolveArtifactPathResult:
       """Resolves artifact identifier to MCP resource URI"""
       start_time = time.time()

       try:
           # Resolve artifact to resource URI
           result = resolver.resolve(
               artifact_type=params.artifact_type,
               artifact_id=params.artifact_id,
               version=params.version
           )

           # Log resolution invocation
           duration_ms = (time.time() - start_time) * 1000
           logger.info(
               "artifact_resolution_completed",
               artifact_type=params.artifact_type,
               artifact_id=params.artifact_id,
               version=params.version,
               success=result.success,
               resource_uri=result.resource_uri if result.success else None,
               error=result.error if not result.success else None,
               duration_ms=duration_ms
           )

           return result

       except Exception as e:
           logger.error("artifact_resolution_error", error=str(e))
           raise HTTPException(status_code=500, detail="Artifact resolution failed due to internal error")
   ```

4. **Testing Strategy:**
   - Unit tests: Validate input validation, URI construction, artifact existence checks
   - Integration tests: Verify tool resolves URIs for all artifact types
   - Error handling tests: Test not_found, invalid_input scenarios
   - Performance tests: Verify <200ms p95 latency with 10 sample artifacts

### Technical Tasks
- [ ] Implement Pydantic models for tool input/output
- [ ] Implement ArtifactResolver class with URI construction
- [ ] Implement artifact existence validation using glob patterns
- [ ] Implement MCP tool endpoint with FastMCP decorator
- [ ] Add structured logging for resolution invocations
- [ ] Write unit tests for ArtifactResolver methods (80% coverage)
- [ ] Write integration tests for all artifact types
- [ ] Write error handling tests
- [ ] Write performance tests (<200ms p95 latency)
- [ ] Add Taskfile commands for running tests

## Acceptance Criteria

### Scenario 1: Epic resource URI resolved successfully
**Given** Epic file exists at `artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md`
**When** Claude Code calls `resolve_artifact_path(artifact_type="epic", artifact_id="006", version=1)`
**Then** tool validates inputs (all valid)
**And** tool constructs URI: `mcp://resources/artifacts/epic/006`
**And** tool verifies artifact file exists
**And** returns `{success: true, resource_uri: "mcp://resources/artifacts/epic/006"}`
**And** execution completes in <200ms

### Scenario 2: Artifact not found error
**Given** No epic exists with ID 999
**When** Claude Code calls `resolve_artifact_path(artifact_type="epic", artifact_id="999", version=1)`
**Then** tool searches for EPIC-999*_v1.md
**And** tool returns `{success: false, error: "not_found", message: "Artifact not found: epic/999 version 1"}`
**And** error includes details about search pattern and directory
**And** error logged with structured logging

### Scenario 3: Invalid artifact type rejected
**Given** Invalid artifact type provided
**When** Claude Code calls `resolve_artifact_path(artifact_type="invalid", artifact_id="006", version=1)`
**Then** Pydantic validation fails
**And** returns `{success: false, error: "invalid_input", message: "Invalid artifact type: invalid"}`
**And** error includes list of allowed types

### Scenario 4: All artifact types resolvable
**Given** Sample artifacts exist for all types
**When** Claude Code calls resolve_artifact_path for each type:
  - Epic: `(artifact_type="epic", artifact_id="006", version=1)`
  - PRD: `(artifact_type="prd", artifact_id="006", version=3)`
  - HLS: `(artifact_type="hls", artifact_id="003", version=1)`
  - Backlog Story: `(artifact_type="backlog_story", artifact_id="001", version=1)`
  - Tech Spec: `(artifact_type="tech_spec", artifact_id="001", version=1)`
  - Task: `(artifact_type="task", artifact_id="001", version=1)`
**Then** All resolve successfully with correct resource URIs:
  - `mcp://resources/artifacts/epic/006`
  - `mcp://resources/artifacts/prd/006`
  - `mcp://resources/artifacts/hls/003`
  - `mcp://resources/artifacts/backlog_story/001`
  - `mcp://resources/artifacts/tech_spec/001`
  - `mcp://resources/artifacts/task/001`

### Scenario 5: Resolution execution logged
**Given** Claude Code calls resolve_artifact_path tool
**When** Resolution completes
**Then** tool logs structured event with fields: artifact_type, artifact_id, version, success, resource_uri, error, duration_ms
**And** log format is JSON (structured logging)

### Scenario 6: Performance target met
**Given** 10 sample artifacts (Epic, PRD, HLS, US, SPEC)
**When** Each artifact resolved 100 times
**Then** p95 latency <200ms for all artifact types
**And** p99 latency <500ms

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Not Needed (Single Sprint-Ready Task)

**Rationale:**
- **Story Points:** 3 SP (reduced from 5 SP in v1 due to simplified approach)
- **Developer Count:** Single developer (straightforward URI construction)
- **Domain Span:** Single domain (URI resolution and file system validation)
- **Complexity:** Low - simple pattern matching and URI construction (no variable parsing needed)
- **Uncertainty:** Low - clear implementation approach
- **Override Factors:** None

Per SDLC Section 11.6 Decision Matrix: "3 SP, single developer, low complexity → SKIP (Single sprint-ready task)".

**No task decomposition needed.** Story can be completed as single unit of work in 1-2 days.

## Definition of Done
- [ ] Pydantic models implemented for tool input/output
- [ ] ArtifactResolver class with URI construction
- [ ] Artifact existence validation using glob patterns
- [ ] MCP tool endpoint implemented with FastMCP
- [ ] Structured logging for resolution invocations
- [ ] Unit tests written and passing (80% coverage)
- [ ] Integration tests passing (all artifact types)
- [ ] Error handling tests passing
- [ ] Performance tests passing (<200ms p95 latency)
- [ ] Manual testing: Resolve URIs for EPIC-006, PRD-006, HLS-003
- [ ] Taskfile commands added for tests
- [ ] Product Owner approval obtained

## Additional Information
**Suggested Labels:** mcp-tools, uri-resolution, performance
**Estimated Story Points:** 3
**Dependencies:**
- **Depends On:** None (can be implemented independently)
- **Blocks:** US-046 (tool invocation logging depends on resolve_artifact_path working)
- **Blocks:** US-047 (integration testing depends on all tools including resolution)

**Related PRD Section:** PRD-006 §Functional Requirements - FR-07

## Decisions Made

**Decision 1: Simplified input interface (artifact_type, artifact_id, version)**
- **Made:** During v2 refinement (feedback from US-040-047_v1_comments.md)
- **Rationale:** Original v1 approach required pattern parsing and variable substitution, which added unnecessary complexity. Direct parameters (type, ID, version) are clearer and eliminate parsing errors
- **Impact:** Reduced story complexity from 5 SP to 3 SP, simplified implementation, removed pattern parsing logic

**Decision 2: Return only MCP resource URI (not file path)**
- **Made:** During v2 refinement (feedback from US-040-047_v1_comments.md)
- **Rationale:** Tool purpose is to resolve artifacts for MCP protocol access, not file system access. MCP resource URI is the correct abstraction. File paths are implementation details that should remain server-side
- **Impact:** Simplified response to `{success: true, resource_uri: "mcp://resources/artifacts/epic/006"}`, removed storage_path and match_count fields

**Decision 3: Externalize artifacts base directory path**
- **Made:** During v2 refinement (feedback from US-040-047_v1_comments.md)
- **Rationale:** Hardcoded paths prevent configuration flexibility and testing with different directory structures
- **Impact:** Use `settings.PATTERNS_BASE_DIR` from configuration instead of hardcoded `"artifacts"` path

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md` (§2.1 Python Type Safety, §2.2 FastAPI, §5.3 Input Validation, §6.1 Structured Logging)
- **Related Stories:** US-040 (validate_artifact tool), US-043 (store_artifact tool)
- **Feedback:** `/feedback/US-040-047_v1_comments.md`
