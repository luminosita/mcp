# User Story: Implement resolve_artifact_path Tool

**⚠️ DEPRECATION NOTICE ⚠️**

**This tool is DEPRECATED as of 2025-10-20.**

**Replacement:** US-071 (approve_artifact tool) embeds path resolution functionality within the approval workflow. Path resolution now happens automatically during artifact approval, eliminating the need for a separate standalone tool.

**Reason for Deprecation:** approve_artifact provides superset functionality (approval + path resolution + task creation) with better workflow integration. Standalone path resolution is no longer needed.

**For new implementations:** Use approve_artifact (US-071) instead of resolve_artifact_path.

**For existing code:** Migrate to approve_artifact workflow. This tool will be removed in future release.

---

## Metadata
- **Story ID:** US-042
- **Title:** Implement resolve_artifact_path Tool (DEPRECATED)
- **Type:** Feature
- **Status:** Deprecated (2025-10-20)
- **Priority:** N/A (deprecated - use US-071 approve_artifact instead)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-008 (MCP Tools - Validation and Path Resolution)
- **Functional Requirements Covered:** FR-07
- **Informed By Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Functional Requirements - FR-07
- **Functional Requirements Coverage:**
  - **FR-07:** MCP Server SHALL provide `resolve_artifact_path` tool that accepts artifact ID and version, returning MCP resource URI for accessing the artifact

**Parent High-Level Story:** [HLS-008: MCP Tools - Validation and Path Resolution]
- **Link:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 3: Implement resolve_artifact_path Tool

## User Story
As Claude Code, I want a tool that resolves artifact identifiers to MCP resource URIs, so that I can access artifacts via MCP protocol with <5% error rate instead of 20-30% AI inference errors.

## Description
Currently, Claude Code uses AI inference to construct MCP resource URIs from artifact identifiers. This approach is error-prone (20-30% error rate due to ID format mistakes), token-intensive (~1-2k tokens per resolution), and slow (~1 second inference time).

This story implements a deterministic Python tool (`resolve_artifact_path`) that:
1. Accepts artifact ID (full format, e.g., "EPIC-006") and version
2. Infers artifact type from artifact ID prefix (EPIC → epic)
3. Validates artifact identifier format
4. Constructs correct MCP resource URI following established patterns
5. Verifies artifact exists at configured artifacts directory
6. Returns resource URI or structured error (artifact not found)

The tool reduces path resolution errors from 20-30% to <5%, execution time from ~1s to <200ms, and eliminates token consumption for path resolution operations.

## Implementation Research References

**Primary Research Document:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

**Technical Patterns Applied:**
- **§2.1: Python 3.11+ with Type Safety:** Use Pydantic models for input/output schemas with full type hints (ref: Implementation Research §2.1 - Programming Language: Python 3.11+)
- **§2.2: FastAPI Integration:** Expose tool as MCP tool via FastAPI with auto-generated OpenAPI documentation (ref: Implementation Research §2.2 - Backend Framework: FastAPI 0.100+)
- **§5.3: Input Validation:** Validate artifact ID with Pydantic, reject invalid inputs (ref: Implementation Research §5.3 - Input Validation and Command Injection Prevention)
- **§6.1: Structured Logging:** Log resolution invocations with artifact ID, version, result URI, duration (ref: Implementation Research §6.1 - Structured Logging)

**Anti-Patterns Avoided:**
- **§8.1: Poor Error Handling:** Return structured error responses distinguishing "not found", "invalid format" (ref: Implementation Research §8.1 - Pitfall 3)

**Performance Considerations:**
- **§2.4: Caching Layer:** Resource URI construction is lightweight (no caching needed for URI generation, but artifact existence checks may benefit from caching)

## Functional Requirements
1. Tool accepts three parameters:
   - `artifact_id` (string): Full artifact ID with prefix (e.g., "EPIC-006", "US-040", "PRD-006")
   - `version` (int): Version number (e.g., 1, 2, 3)
   - `task_id` (string, mandatory): Task tracking ID for log correlation
2. Tool infers artifact type from artifact_id prefix:
   - EPIC-006 → epic
   - US-040 → backlog_story
   - PRD-006 → prd
   - (Same prefix mapping as validate_artifact and add_task tools)
3. Tool validates inputs:
   - Artifact ID matches pattern `[A-Z]+-\d{3,}` (e.g., "EPIC-006", "US-040")
   - Artifact type inferred successfully (prefix recognized)
   - Version is positive integer
4. Tool constructs MCP resource URI following pattern:
   - Pattern: `mcp://resources/artifacts/{artifact_type}/{id_number}`
   - Example: `mcp://resources/artifacts/epic/006` (from "EPIC-006")
   - Note: Version not included in URI (MCP resource server handles version resolution)
5. Tool verifies artifact exists at configured artifacts directory before returning URI:
   - Check path: `{ARTIFACTS_BASE_DIR}/{artifact_type}/{artifact_id}_v{version}.md`
   - Example: `/workspace/artifacts/epic/EPIC-006_v1.md`
6. Tool returns structured JSON response:
   ```json
   // Success
   {
     "success": true,
     "resource_uri": "mcp://resources/artifacts/epic/006",
     "path": "/workspace/artifacts/epic/EPIC-006_v1.md"
   }

   // Error (not found)
   {
     "success": false,
     "error": "not_found",
     "message": "Artifact not found: EPIC-006 version 1",
     "details": "No file at path: /workspace/artifacts/epic/EPIC-006_v1.md"
   }

   // Error (invalid input)
   {
     "success": false,
     "error": "invalid_input",
     "message": "Invalid artifact ID format: INVALID-006",
     "details": "Unknown artifact ID prefix: INVALID. Valid prefixes: EPIC, PRD, HLS, US, SPEC, ADR, SPIKE, TASK, VIS, INIT"
   }
   ```
7. Tool execution completes in <200ms p95 (per PRD-006 NFR-Performance-02, path resolution subset)
8. Tool logs resolution invocations with timestamp, task_id, artifact_id, artifact_type, version, result URI, duration

## Non-Functional Requirements
- **Performance:** Path resolution latency <200ms p95 (subset of NFR-Performance-02 <500ms tool execution target)
- **Accuracy:** Deterministic resolution (same input → same output, 100% consistency)
- **Reliability:** Handle missing artifacts gracefully, return clear error messages
- **Observability:** Structured logging captures resolution patterns for debugging
- **Maintainability:** Clear separation between ID inference, path construction, and existence verification

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** Follow established implementation patterns for MCP tools. Supplement with story-specific path resolution logic.

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
   from pathlib import Path

   class ResolveArtifactPathInput(BaseModel):
       """Input schema for resolve_artifact_path tool"""
       artifact_id: str = Field(
           ...,
           pattern=r'^[A-Z]+-\d{3,}$',
           description="Full artifact ID (e.g., 'EPIC-006', 'US-040')"
       )
       version: int = Field(..., ge=1, le=999, description="Artifact version")
       task_id: str = Field(..., description="Task tracking ID for log correlation")

       # Inferred field (not provided by client)
       artifact_type: str = None

       @validator('artifact_type', pre=True, always=True)
       def infer_artifact_type(cls, v, values):
           """Infers artifact type from artifact_id prefix"""
           if v is None and 'artifact_id' in values:
               artifact_id = values['artifact_id']
               prefix = artifact_id.split('-')[0]
               type_map = {
                   "EPIC": "epic",
                   "PRD": "prd",
                   "HLS": "hls",
                   "US": "backlog_story",
                   "SPEC": "tech_spec",
                   "ADR": "adr",
                   "SPIKE": "spike",
                   "TASK": "task",
                   "VIS": "product_vision",
                   "INIT": "initiative"
               }
               if prefix not in type_map:
                   raise ValueError(
                       f"Unknown artifact ID prefix: {prefix}. "
                       f"Valid prefixes: {', '.join(type_map.keys())}"
                   )
               return type_map[prefix]
           return v

   class ResolveArtifactPathResult(BaseModel):
       """Result for artifact path resolution"""
       success: bool
       resource_uri: Optional[str] = None
       path: Optional[str] = None
       error: Optional[Literal["not_found", "invalid_input"]] = None
       message: Optional[str] = None
       details: Optional[str] = None
   ```

2. **Artifact Path Resolver:**
   ```python
   from pathlib import Path
   from config import settings

   class ArtifactPathResolver:
       def __init__(self, base_dir: Optional[str] = None):
           self.base_dir = Path(base_dir or settings.ARTIFACTS_BASE_DIR)

       def resolve(
           self,
           artifact_id: str,
           artifact_type: str,
           version: int
       ) -> tuple[bool, Optional[str], Optional[Path]]:
           """
           Resolves artifact to MCP resource URI and file path

           Returns:
               (exists, resource_uri, file_path)
           """
           # Extract numeric ID from artifact_id
           # e.g., "EPIC-006" → "006"
           id_number = artifact_id.split('-')[1]

           # Construct resource URI
           resource_uri = f"mcp://resources/artifacts/{artifact_type}/{id_number}"

           # Construct file path
           artifact_dir = self.base_dir / artifact_type
           filename = f"{artifact_id}_v{version}.md"
           file_path = artifact_dir / filename

           # Check if artifact exists
           exists = file_path.exists()

           return exists, resource_uri, file_path if exists else None

       def get_artifact_type_directory(self, artifact_type: str) -> Path:
           """Returns directory path for artifact type"""
           type_dir_map = {
               "epic": "epic",
               "prd": "prd",
               "hls": "hls",
               "backlog_story": "backlog_story",
               "tech_spec": "tech_spec",
               "adr": "adr",
               "spike": "spike",
               "task": "task",
               "product_vision": "product_vision",
               "initiative": "initiative"
           }
           return self.base_dir / type_dir_map[artifact_type]
   ```

3. **MCP Tool Implementation:**
   ```python
   from mcp.server.fastmcp import FastMCP
   import structlog
   import time

   mcp = FastMCP(name="MCPServer", version="1.0.0")
   logger = structlog.get_logger()
   resolver = ArtifactPathResolver()

   @mcp.tool(
       name="resolve_artifact_path",
       description="""
       Resolves artifact identifier to MCP resource URI.

       Use this tool when:
       - You need to access an artifact via MCP protocol
       - You want to verify an artifact exists before referencing it
       - You need the MCP resource URI for an artifact

       Input:
       - artifact_id: Full artifact ID (e.g., "EPIC-006", "US-040")
       - version: Version number
       - task_id: Task tracking ID for log correlation

       Tool automatically infers artifact type from ID prefix.

       Returns MCP resource URI if artifact exists, or error if not found.
       """
   )
   async def resolve_artifact_path(params: ResolveArtifactPathInput) -> ResolveArtifactPathResult:
       """Resolves artifact path to MCP resource URI"""
       start_time = time.time()

       try:
           # Resolve artifact path
           exists, resource_uri, file_path = resolver.resolve(
               artifact_id=params.artifact_id,
               artifact_type=params.artifact_type,  # Inferred by validator
               version=params.version
           )

           # Log resolution invocation
           duration_ms = (time.time() - start_time) * 1000
           logger.info(
               "artifact_path_resolution_completed",
               task_id=params.task_id,
               artifact_id=params.artifact_id,
               artifact_type=params.artifact_type,
               version=params.version,
               resource_uri=resource_uri if exists else None,
               exists=exists,
               duration_ms=duration_ms
           )

           if exists:
               return ResolveArtifactPathResult(
                   success=True,
                   resource_uri=resource_uri,
                   path=str(file_path)
               )
           else:
               return ResolveArtifactPathResult(
                   success=False,
                   error="not_found",
                   message=f"Artifact not found: {params.artifact_id} version {params.version}",
                   details=f"No file at path: {resolver.base_dir / params.artifact_type / f'{params.artifact_id}_v{params.version}.md'}"
               )

       except ValueError as e:
           # Invalid artifact ID prefix
           logger.error("artifact_path_resolution_validation_error", task_id=params.task_id, artifact_id=params.artifact_id, error=str(e))
           return ResolveArtifactPathResult(
               success=False,
               error="invalid_input",
               message=str(e),
               details=str(e)
           )
       except Exception as e:
           logger.error("artifact_path_resolution_error", task_id=params.task_id, artifact_id=params.artifact_id, error=str(e))
           raise HTTPException(status_code=500, detail="Path resolution failed due to internal error")
   ```

4. **Testing Strategy:**
   - Unit tests: Validate artifact type inference from various artifact_id formats
   - Unit tests: Validate path construction for all artifact types
   - Integration tests: Verify resolution with real artifact directory structure
   - Error tests: Test invalid artifact ID prefixes, missing artifacts
   - Performance tests: Verify <200ms p95 latency

### Technical Tasks
- [ ] Implement Pydantic models for tool input/output
- [ ] Implement artifact type inference validator in ResolveArtifactPathInput
- [ ] Implement ArtifactPathResolver class with path construction logic
- [ ] Implement artifact existence verification
- [ ] Implement MCP tool endpoint with FastMCP decorator
- [ ] Add structured logging for resolution invocations (with task_id)
- [ ] Write unit tests for artifact type inference (80% coverage)
- [ ] Write unit tests for path construction
- [ ] Write integration tests with real artifact directory
- [ ] Write error tests for invalid artifact ID formats
- [ ] Write performance tests (<200ms p95 latency)
- [ ] Add Taskfile commands for running path resolution tool tests

## Acceptance Criteria

### Scenario 1: Epic path resolution with inference
**Given** Epic-006 v1 exists at `/workspace/artifacts/epic/EPIC-006_v1.md`
**When** Claude Code calls `resolve_artifact_path(artifact_id="EPIC-006", version=1, task_id="task-123")`
**Then** tool infers artifact_type="epic" from "EPIC" prefix
**And** tool constructs resource URI: `mcp://resources/artifacts/epic/006`
**And** tool verifies file exists
**And** returns `{success: true, resource_uri: "mcp://resources/artifacts/epic/006", path: "/workspace/artifacts/epic/EPIC-006_v1.md"}`
**And** execution completes in <200ms

### Scenario 2: Backlog Story path resolution
**Given** US-040 v2 exists at `/workspace/artifacts/backlog_story/US-040_v2.md`
**When** Claude Code calls `resolve_artifact_path(artifact_id="US-040", version=2, task_id="task-123")`
**Then** tool infers artifact_type="backlog_story" from "US" prefix
**And** tool constructs resource URI: `mcp://resources/artifacts/backlog_story/040`
**And** returns success with correct path

### Scenario 3: Artifact not found error
**Given** EPIC-999 v1 does NOT exist
**When** Claude Code calls `resolve_artifact_path(artifact_id="EPIC-999", version=1, task_id="task-123")`
**Then** tool infers artifact_type="epic"
**And** tool checks for file at `/workspace/artifacts/epic/EPIC-999_v1.md`
**And** file does not exist
**And** returns `{success: false, error: "not_found", message: "Artifact not found: EPIC-999 version 1", details: "No file at path: ..."}`

### Scenario 4: Invalid artifact ID prefix rejected
**Given** Invalid artifact ID with unknown prefix
**When** Claude Code calls `resolve_artifact_path(artifact_id="INVALID-006", version=1, task_id="task-123")`
**Then** artifact type inference fails
**And** tool returns `{success: false, error: "invalid_input", message: "Unknown artifact ID prefix: INVALID. Valid prefixes: EPIC, PRD, HLS, US, SPEC, ADR, SPIKE, TASK, VIS, INIT"}`
**And** error logged with task_id for debugging

### Scenario 5: All artifact types resolvable
**Given** Sample artifacts for all types exist
**When** Claude Code resolves each type:
  - `resolve_artifact_path(artifact_id="EPIC-006", version=1, task_id="task-123")`
  - `resolve_artifact_path(artifact_id="PRD-006", version=1, task_id="task-123")`
  - `resolve_artifact_path(artifact_id="HLS-006", version=1, task_id="task-123")`
  - `resolve_artifact_path(artifact_id="US-040", version=1, task_id="task-123")`
  - `resolve_artifact_path(artifact_id="SPEC-001", version=1, task_id="task-123")`
**Then** All artifact types resolve successfully with correct resource URIs:
  - `mcp://resources/artifacts/epic/006`
  - `mcp://resources/artifacts/prd/006`
  - `mcp://resources/artifacts/hls/006`
  - `mcp://resources/artifacts/backlog_story/040`
  - `mcp://resources/artifacts/tech_spec/001`

### Scenario 6: Path resolution execution logged with task_id
**Given** Claude Code calls resolve_artifact_path tool
**When** Resolution completes
**Then** tool logs structured event with fields: task_id, artifact_id, artifact_type, version, resource_uri, exists, duration_ms
**And** log format is JSON (structured logging)
**And** log includes task_id for correlation with other tool calls

### Scenario 7: Performance target met
**Given** 100 sample artifacts
**When** Each artifact resolved 100 times
**Then** p95 latency <200ms
**And** p99 latency <400ms
**And** Prometheus metrics capture latency histogram

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Not Needed (Single Sprint-Ready Task)

**Rationale:**
- **Story Points:** 3 SP (below 5 SP threshold - CONSIDER SKIPPING per decision matrix)
- **Developer Count:** Single developer (straightforward path resolution with inference)
- **Domain Span:** Single domain (file system path construction + inference)
- **Complexity:** Low - well-defined path resolution pattern with artifact type inference
- **Uncertainty:** Low - clear implementation approach similar to validate_artifact inference
- **Override Factors:** None (path resolution is straightforward, inference pattern reused)

Per SDLC Section 11.6 Decision Matrix: "3 SP, single developer, low complexity → SKIP (Single sprint-ready task)".

**No task decomposition needed.** Story can be completed as single unit of work in 1-2 days.

## Definition of Done
- [ ] Pydantic models implemented for tool input/output
- [ ] Artifact type inference validator implemented in ResolveArtifactPathInput
- [ ] ArtifactPathResolver class with path construction logic
- [ ] Artifact existence verification implemented
- [ ] MCP tool endpoint implemented with FastMCP
- [ ] Structured logging for resolution invocations (with task_id)
- [ ] Unit tests written and passing (80% coverage, includes inference tests)
- [ ] Integration tests passing (real artifact directory)
- [ ] Error tests passing (invalid artifact ID formats)
- [ ] Performance tests passing (<200ms p95 latency)
- [ ] Manual testing: Resolve EPIC-006, PRD-006, US-040 with tool
- [ ] Taskfile commands added for path resolution tool tests
- [ ] Product Owner approval obtained

## Additional Information
**Suggested Labels:** mcp-tools, path-resolution, performance
**Estimated Story Points:** 3
**Dependencies:**
- **Depends On:** None (can be implemented independently)
- **Blocks:** None (artifact access optimization, doesn't block other features)
- **Related:** US-030 (MCP resource pattern), FR-03 (artifact resources queryable)

**Related PRD Section:** PRD-006 §Functional Requirements - FR-07

## Decisions Made

**Decision 1: Remove artifact_type parameter, infer from artifact_id**
- **Made:** During v3 refinement (feedback from US-040-047_v2_comments.md)
- **Rationale:** Artifact type is fully deterministic from artifact_id prefix. Explicit parameter creates opportunity for client errors (mismatched artifact_id/artifact_type). Inference ensures consistency and simpler interface
- **Impact:**
  - Removed `artifact_type` field from ResolveArtifactPathInput
  - Added Pydantic validator to infer artifact_type from artifact_id prefix
  - Prefix mapping: EPIC-006 → epic, US-040 → backlog_story
  - Simpler client interface (one less parameter to provide)
  - Eliminates mismatched artifact_id/artifact_type errors
  - Consistent with validate_artifact and add_task tools (same inference pattern)
- **Alternative Considered:** Keep artifact_type parameter for explicit control, but this duplicates information already encoded in artifact_id

**Decision 2: Rename request_id → task_id (mandatory parameter)**
- **Made:** During v3 refinement (feedback from US-040-047_v2_comments.md)
- **Rationale:** "task_id" provides better visibility and traceability in logs. Naming aligns with task tracking system terminology. Mandatory parameter ensures all tool invocations are correlated
- **Impact:**
  - Parameter renamed and made mandatory in ResolveArtifactPathInput
  - All logging updated to use `task_id` field
  - Function signature change across all tool calls
  - Better log correlation with task tracking microservice

**Decision 3: DEPRECATE resolve_artifact_path tool, replace with approve_artifact workflow**
- **Made:** 2025-10-20 (architectural decision based on feedback: new_work_feedback.md)
- **Rationale:** Path resolution is now embedded in approve_artifact workflow (US-071). Standalone path resolution tool is redundant. approve_artifact provides superset functionality:
  - Validates approval prerequisites (4 checks)
  - Reserves ID range for placeholder resolution
  - Replaces placeholder IDs with final IDs
  - **Resolves ALL artifact paths automatically** (mandatory + recommended inputs)
  - Updates artifact status to Approved
  - Creates tasks with resolved inputs
  - Confirms ID reservation
- **Impact:**
  - **Tool Status:** DEPRECATED (2025-10-20)
  - **Replacement:** US-071 (approve_artifact tool)
  - **Migration Path:** Use approve_artifact instead of resolve_artifact_path
  - **Code Impact:** resolve_artifact_path tool will be removed in future release
  - **Workflow Impact:** Path resolution happens automatically during approval (no manual resolution step needed)
  - **Integration Tests:** US-047 v3 removes resolve_artifact_path tests, adds approve_artifact tests
  - **Sequence Diagram:** Updated to v3.0 showing approve_artifact workflow (no resolve_artifact_path)
- **Alternative Considered:** Keep both tools (approve_artifact + resolve_artifact_path), but this adds unnecessary complexity. Path resolution is always needed during approval, so embedding it in approval workflow is more efficient
- **Decision Authority:** Technical architecture team (documented in feedback and sequence diagram v3.0)

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md` (§2.1 Python Type Safety, §2.2 FastAPI, §5.3 Input Validation, §6.1 Structured Logging)
- **Related Stories:** US-040 v3 (validate_artifact tool - similar inference pattern), US-044 v3 (add_task tool - similar inference pattern)
- **Replacement Story:** **US-071 v1 (approve_artifact tool - REPLACES THIS TOOL)**
- **Deprecation Feedback:** `/feedback/new_work_feedback.md` (approve_artifact requirements)
- **Sequence Diagram:** `/docs/mcp_tools_sequence_diagram_v3.md` (approve_artifact workflow with embedded path resolution)
- **Integration Tests:** US-047 v3 (resolve_artifact_path tests REMOVED, approve_artifact tests ADDED)
- **Feedback v2:** `/feedback/US-040-047_v2_comments.md`
- **Changes Applied:** `/feedback/US-040-047_v2_changes_applied.md`
