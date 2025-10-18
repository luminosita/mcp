# User Story: Implement store_artifact Tool

## Metadata
- **Story ID:** US-043
- **Title:** Implement store_artifact Tool
- **Type:** Feature
- **Status:** Draft
- **Priority:** Should-have (enables centralized artifact storage, supports FR-23)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-008 (MCP Tools - Validation and Path Resolution)
- **Functional Requirements Covered:** FR-23
- **Informed By Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Functional Requirements - FR-23
- **Functional Requirements Coverage:**
  - **FR-23:** MCP Server SHALL provide `store_artifact` tool that uploads generated artifacts to centralized storage accessible across projects

**Parent High-Level Story:** [HLS-008: MCP Tools - Validation and Path Resolution]
- **Link:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 4: Implement store_artifact Tool

## User Story
As Claude Code, I want a tool to upload generated artifacts to centralized storage, so that multiple projects can access shared reference artifacts without local file duplication.

## Description
Currently, generated artifacts are stored only in local Git repositories. Multi-project scenarios require either:
1. Manual copying of shared artifacts across project repositories (error-prone, version drift risk)
2. Git submodules for shared artifacts (complex setup, synchronization overhead)

This story implements a deterministic Python tool (`store_artifact`) that:
1. Accepts artifact content (markdown text), artifact metadata (ID, type, status, parent_id), and optional file path
2. Validates artifact metadata against schema (artifact ID format, type allowed values, status workflow)
3. Stores artifact to centralized location:
   - **Phase 1 (Pilot):** Local file system (`shared_artifacts/{artifact_type}/{artifact_id}_v{version}.md`)
   - **Phase 2 (Production):** Database or cloud storage (S3, GCS) - implementation detail deferred to Tech Spec
4. Makes artifact accessible via MCP resource URI: `mcp://resources/artifacts/{artifact_type}/{artifact_id}`
5. Returns storage confirmation with resource URI

The tool enables shared artifact access across projects, supporting use cases like:
- Reference artifacts (Product Vision, Initiative) shared across multiple Epic/PRD projects
- Approved artifact templates shared organization-wide
- Cross-project dependency tracking (Epic A depends on Epic B from different project)

## Implementation Research References

**Primary Research Document:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

**Technical Patterns Applied:**
- **§2.1: Python 3.11+ with Type Safety:** Use Pydantic models for artifact metadata validation with full type hints (ref: Implementation Research §2.1 - Programming Language: Python 3.11+)
- **§2.2: FastAPI Integration:** Expose store_artifact tool as MCP tool via FastAPI with auto-generated OpenAPI documentation (ref: Implementation Research §2.2 - Backend Framework: FastAPI 0.100+)
- **§5.3: Input Validation:** Validate artifact metadata (ID format, status values) and content with Pydantic (ref: Implementation Research §5.3 - Input Validation and Command Injection Prevention)
- **§6.1: Structured Logging:** Log artifact storage events with artifact ID, type, size, storage location (ref: Implementation Research §6.1 - Structured Logging)

**Anti-Patterns Avoided:**
- **§8.1: Poor Error Handling:** Return structured error responses for validation failures, storage errors with retryable flag (ref: Implementation Research §8.1 - Pitfall 3)
- **§8.2: Synchronous Blocking Calls in Async Context:** Use async file I/O (aiofiles) for artifact writing (ref: Implementation Research §8.2 - Anti-Pattern 1)

**Performance Considerations:**
- **§2.4: Caching Layer:** Not applicable for storage operation (write-heavy, no cache benefit)

## Functional Requirements
1. Tool accepts three parameters:
   - `artifact_content` (string): Full artifact markdown text
   - `metadata` (dict): Artifact metadata including:
     - `artifact_id`: Artifact ID (e.g., "EPIC-006", "PRD-006")
     - `artifact_type`: Artifact type (e.g., "epic", "prd", "hls", "backlog_story")
     - `version`: Version number (integer, e.g., 1, 2, 3)
     - `status`: Artifact status (e.g., "Draft", "Approved", "Planned")
     - `parent_id`: Optional parent artifact ID (e.g., "INIT-001" for Epic-006)
     - `title`: Artifact title (for metadata indexing)
   - `file_path` (optional string): Override default file path for storage location
2. Tool validates artifact metadata against schema:
   - Artifact ID format matches pattern for type (e.g., `EPIC-\d{3}` for epics)
   - Artifact type is allowed value (epic, prd, hls, backlog_story, tech_spec, adr, spike, task)
   - Status is valid for artifact lifecycle (Draft → Review → Approved → Planned → In Progress → Completed)
   - Version is positive integer
3. Tool generates storage path if not provided:
   - Default: `shared_artifacts/{artifact_type}/{artifact_id}_v{version}.md`
   - Example: `shared_artifacts/epics/EPIC-006_v1.md`
4. Tool writes artifact content to storage location using async file I/O
5. Tool extracts and stores artifact metadata separately for queryability:
   - Metadata file: `shared_artifacts/{artifact_type}/{artifact_id}_v{version}_metadata.json`
   - Enables fast metadata queries without loading full artifact content
6. Tool returns structured JSON response:
   ```json
   {
     "success": true,
     "artifact_id": "EPIC-006",
     "artifact_type": "epic",
     "version": 1,
     "storage_path": "shared_artifacts/epics/EPIC-006_v1.md",
     "resource_uri": "mcp://resources/artifacts/epic/006",
     "metadata_path": "shared_artifacts/epics/EPIC-006_v1_metadata.json"
   }
   ```
7. Tool execution completes in <500ms p95 (per PRD-006 NFR-Performance-02)
8. Tool logs storage invocations with timestamp, artifact ID, type, size (bytes), storage path, duration

## Non-Functional Requirements
- **Performance:** Artifact storage latency <500ms p95 (per NFR-Performance-02)
- **Reliability:** Atomic write operations (temp file + rename to prevent partial writes)
- **Security:** Validate artifact ID and type to prevent directory traversal attacks
- **Observability:** Structured logging captures storage patterns for capacity planning
- **Maintainability:** Clear separation between metadata validation, storage, and response formatting

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** Follow established implementation patterns for MCP tools. Supplement with story-specific artifact storage logic.

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

   class ArtifactMetadata(BaseModel):
       """Artifact metadata schema"""
       artifact_id: str = Field(..., pattern=r'^[A-Z]+-\d{3}$')  # e.g., EPIC-006, PRD-006
       artifact_type: Literal[
           "epic", "prd", "hls", "backlog_story", "tech_spec", "adr", "spike", "task"
       ]
       version: int = Field(..., ge=1, le=999)
       status: Literal[
           "Draft", "In Review", "Approved", "Planned", "In Progress", "Completed"
       ]
       parent_id: Optional[str] = Field(None, pattern=r'^[A-Z]+-\d{3}$')
       title: str = Field(..., min_length=5, max_length=200)

       @validator('artifact_id')
       def validate_id_type_match(cls, v, values):
           """Validates artifact ID prefix matches artifact type"""
           type_prefix_map = {
               "epic": "EPIC",
               "prd": "PRD",
               "hls": "HLS",
               "backlog_story": "US",
               "tech_spec": "SPEC",
               "adr": "ADR",
               "spike": "SPIKE",
               "task": "TASK"
           }
           if 'artifact_type' in values:
               expected_prefix = type_prefix_map[values['artifact_type']]
               if not v.startswith(expected_prefix):
                   raise ValueError(
                       f"Artifact ID '{v}' does not match type '{values['artifact_type']}' "
                       f"(expected prefix: {expected_prefix})"
                   )
           return v

   class StoreArtifactInput(BaseModel):
       """Input schema for store_artifact tool"""
       artifact_content: str = Field(..., min_length=100, description="Full artifact markdown text")
       metadata: ArtifactMetadata
       file_path: Optional[str] = None  # Override default storage path

   class StoreArtifactResult(BaseModel):
       """Artifact storage result"""
       success: bool
       artifact_id: str
       artifact_type: str
       version: int
       storage_path: str
       resource_uri: str  # e.g., mcp://resources/artifacts/epic/006
       metadata_path: str
   ```

2. **Artifact Storage Logic:**
   ```python
   import aiofiles
   import json
   from pathlib import Path
   import tempfile
   import os

   class ArtifactStorageManager:
       def __init__(self, base_dir: str = "shared_artifacts"):
           self.base_dir = Path(base_dir)
           self.base_dir.mkdir(parents=True, exist_ok=True)

       async def store(
           self,
           artifact_content: str,
           metadata: ArtifactMetadata,
           file_path: Optional[str] = None
       ) -> StoreArtifactResult:
           """Stores artifact content and metadata to centralized storage"""
           # Step 1: Generate storage paths
           if file_path:
               storage_path = Path(file_path)
           else:
               storage_path = self._generate_storage_path(metadata)

           metadata_path = storage_path.with_suffix('').with_suffix('.md_metadata.json')

           # Step 2: Ensure parent directory exists
           storage_path.parent.mkdir(parents=True, exist_ok=True)

           # Step 3: Write artifact content atomically (temp file + rename)
           await self._write_atomic(storage_path, artifact_content)

           # Step 4: Write metadata JSON
           metadata_json = metadata.dict()
           metadata_json['file_path'] = str(storage_path)
           metadata_json['size_bytes'] = len(artifact_content)
           await self._write_atomic(metadata_path, json.dumps(metadata_json, indent=2))

           # Step 5: Generate resource URI
           resource_uri = self._generate_resource_uri(metadata)

           return StoreArtifactResult(
               success=True,
               artifact_id=metadata.artifact_id,
               artifact_type=metadata.artifact_type,
               version=metadata.version,
               storage_path=str(storage_path),
               resource_uri=resource_uri,
               metadata_path=str(metadata_path)
           )

       def _generate_storage_path(self, metadata: ArtifactMetadata) -> Path:
           """Generates default storage path for artifact"""
           # Pattern: shared_artifacts/{type}/{id}_v{version}.md
           artifact_dir = self.base_dir / metadata.artifact_type
           filename = f"{metadata.artifact_id}_v{metadata.version}.md"
           return artifact_dir / filename

       def _generate_resource_uri(self, metadata: ArtifactMetadata) -> str:
           """Generates MCP resource URI for artifact"""
           # Extract ID number from artifact_id (e.g., "EPIC-006" → "006")
           id_number = metadata.artifact_id.split('-')[1]
           return f"mcp://resources/artifacts/{metadata.artifact_type}/{id_number}"

       async def _write_atomic(self, path: Path, content: str):
           """Writes file atomically using temp file + rename"""
           # Write to temp file first
           temp_fd, temp_path = tempfile.mkstemp(
               dir=path.parent,
               prefix=f".{path.name}.",
               suffix=".tmp"
           )

           try:
               async with aiofiles.open(temp_path, mode='w') as f:
                   await f.write(content)

               # Atomic rename (POSIX guarantees atomicity)
               os.replace(temp_path, path)
           except Exception as e:
               # Clean up temp file on error
               if os.path.exists(temp_path):
                   os.remove(temp_path)
               raise e
           finally:
               os.close(temp_fd)
   ```

3. **MCP Tool Implementation:**
   ```python
   from mcp.server.fastmcp import FastMCP
   import structlog
   import time

   mcp = FastMCP(name="MCPServer", version="1.0.0")
   logger = structlog.get_logger()
   storage_manager = ArtifactStorageManager(base_dir="shared_artifacts")

   @mcp.tool(
       name="store_artifact",
       description="""
       Stores generated artifact to centralized storage accessible across projects.

       Use this tool when:
       - You have generated a new artifact (Epic, PRD, HLS, Backlog Story, etc.)
       - You want to make artifact accessible to other projects via MCP resources
       - You need to create shared reference artifacts (Product Vision, Initiative)

       Stores artifact content and metadata to centralized location and returns
       MCP resource URI for accessing stored artifact.

       Supports multi-project workflows where artifacts are shared across teams.
       """
   )
   async def store_artifact(params: StoreArtifactInput) -> StoreArtifactResult:
       """Stores artifact to centralized storage"""
       start_time = time.time()

       try:
           # Store artifact
           result = await storage_manager.store(
               artifact_content=params.artifact_content,
               metadata=params.metadata,
               file_path=params.file_path
           )

           # Log storage invocation
           duration_ms = (time.time() - start_time) * 1000
           logger.info(
               "artifact_storage_completed",
               artifact_id=result.artifact_id,
               artifact_type=result.artifact_type,
               version=result.version,
               size_bytes=len(params.artifact_content),
               storage_path=result.storage_path,
               resource_uri=result.resource_uri,
               duration_ms=duration_ms
           )

           return result

       except ValidationError as e:
           logger.error("artifact_storage_validation_error", error=str(e))
           raise HTTPException(status_code=400, detail=f"Validation failed: {e}")
       except Exception as e:
           logger.error("artifact_storage_error", error=str(e))
           raise HTTPException(status_code=500, detail="Artifact storage failed due to internal error")
   ```

4. **Testing Strategy:**
   - Unit tests: Validate artifact metadata schema, storage path generation, atomic writes
   - Integration tests: Verify tool stores artifact and metadata correctly
   - Security tests: Attempt directory traversal via artifact_id, verify rejection
   - Performance tests: Verify <500ms p95 latency with various artifact sizes
   - Edge case tests: Handle large artifacts (>100KB), concurrent storage requests

### Technical Tasks
- [ ] Implement Pydantic models for tool input/output and artifact metadata
- [ ] Implement ArtifactStorageManager class with atomic write operations
- [ ] Implement storage path generation logic
- [ ] Implement metadata JSON generation
- [ ] Implement MCP tool endpoint with FastMCP decorator
- [ ] Add structured logging for artifact storage invocations
- [ ] Write unit tests for ArtifactStorageManager methods (80% coverage)
- [ ] Write integration tests for full storage workflow
- [ ] Write security tests for directory traversal protection
- [ ] Write performance tests (<500ms p95 latency)
- [ ] Add Taskfile commands for running artifact storage tool tests

## Acceptance Criteria

### Scenario 1: Epic artifact stored successfully
**Given** Claude Code has generated Epic-006 artifact
**When** Claude Code calls `store_artifact(artifact_content=epic_text, metadata={artifact_id: "EPIC-006", artifact_type: "epic", version: 1, status: "Draft", title: "MCP Server Integration"})`
**Then** tool validates metadata schema (passes)
**And** tool writes artifact to `shared_artifacts/epics/EPIC-006_v1.md`
**And** tool writes metadata to `shared_artifacts/epics/EPIC-006_v1_metadata.json`
**And** returns `{success: true, resource_uri: "mcp://resources/artifacts/epic/006", storage_path: "shared_artifacts/epics/EPIC-006_v1.md"}`
**And** execution completes in <500ms

### Scenario 2: Metadata validation rejects invalid artifact ID
**Given** Claude Code attempts to store artifact with mismatched ID
**When** Claude Code calls `store_artifact(artifact_content=text, metadata={artifact_id: "EPIC-006", artifact_type: "prd", ...})`
**Then** tool returns validation error: "Artifact ID 'EPIC-006' does not match type 'prd' (expected prefix: PRD)"
**And** no files written to storage
**And** error logged with validation failure details

### Scenario 3: Atomic write prevents partial file on failure
**Given** Disk write operation fails midway (simulated I/O error)
**When** Claude Code calls `store_artifact(artifact_content=large_text, metadata={...})`
**Then** tool writes to temp file first
**And** disk error occurs during temp file write
**And** tool cleans up temp file (no partial file left)
**And** returns 500 error with retryable flag
**And** next retry succeeds (no corrupted state)

### Scenario 4: Metadata JSON queryable without loading full artifact
**Given** Multiple artifacts stored in shared_artifacts/
**When** User wants to list all approved epics without loading full content
**Then** user reads metadata JSON files: `shared_artifacts/epics/*_metadata.json`
**And** metadata includes artifact_id, type, status, version, parent_id, title, size_bytes
**And** query completes 10x faster than loading full artifacts (benchmark validation)

### Scenario 5: Resource URI enables MCP access
**Given** Epic-006 stored at `shared_artifacts/epics/EPIC-006_v1.md`
**When** Claude Code requests `mcp://resources/artifacts/epic/006`
**Then** MCP Server returns EPIC-006 v1 content
**And** resource accessible from any project connected to MCP Server

### Scenario 6: All artifact types storable
**Given** Sample artifacts for all types
**When** Claude Code stores each type (Epic, PRD, HLS, US, SPEC, TASK, ADR, SPIKE)
**Then** All artifacts stored to correct directories:
  - `shared_artifacts/epics/EPIC-006_v1.md`
  - `shared_artifacts/prds/PRD-006_v1.md`
  - `shared_artifacts/hls/HLS-006_v1.md`
  - `shared_artifacts/backlog_stories/US-040_v1.md`
  - `shared_artifacts/tech_specs/SPEC-001_v1.md`
  - `shared_artifacts/tasks/TASK-001_v1.md`
  - `shared_artifacts/adrs/ADR-001_v1.md`
  - `shared_artifacts/spikes/SPIKE-001_v1.md`

### Scenario 7: Artifact storage execution logged
**Given** Claude Code calls store_artifact tool
**When** Storage completes
**Then** tool logs structured event with fields: artifact_id, artifact_type, version, size_bytes, storage_path, resource_uri, duration_ms
**And** log format is JSON (structured logging)

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Not Needed (Single Sprint-Ready Task)

**Rationale:**
- **Story Points:** 5 SP (at threshold - CONSIDER SKIPPING per decision matrix)
- **Developer Count:** Single developer (straightforward file I/O and metadata management)
- **Domain Span:** Single domain (file system operations and JSON serialization)
- **Complexity:** Low-moderate - well-defined atomic write pattern, standard file operations
- **Uncertainty:** Low - clear implementation approach using async file I/O
- **Override Factors:** None (no security-critical complexity, straightforward validation)

Per SDLC Section 11.6 Decision Matrix: "5 SP, single developer, low-moderate complexity → SKIP (Straightforward file operations)".

**No task decomposition needed.** Story can be completed as single unit of work in 2-3 days.

## Definition of Done
- [ ] Pydantic models implemented for tool input/output and artifact metadata
- [ ] ArtifactStorageManager class with atomic write operations
- [ ] Storage path generation logic
- [ ] Metadata JSON generation
- [ ] MCP tool endpoint implemented with FastMCP
- [ ] Structured logging for artifact storage invocations
- [ ] Unit tests written and passing (80% coverage)
- [ ] Integration tests passing (full storage workflow)
- [ ] Security tests passing (directory traversal protection)
- [ ] Performance tests passing (<500ms p95 latency)
- [ ] Manual testing: Store Epic-006, PRD-006, verify MCP resource access
- [ ] Taskfile commands added for artifact storage tool tests
- [ ] Product Owner approval obtained

## Additional Information
**Suggested Labels:** mcp-tools, artifact-storage, multi-project
**Estimated Story Points:** 5
**Dependencies:**
- **Depends On:** None (can be implemented independently)
- **Blocks:** None (optional feature, enables multi-project workflows)
- **Related:** US-030 (MCP resource pattern), US-031 (template resources), FR-03 (artifact resources queryable)

**Related PRD Section:** PRD-006 §Functional Requirements - FR-23

## Open Questions & Implementation Uncertainties

**No open implementation questions.** Storage approach and atomic write pattern clearly defined.

Technical implementation details (Pydantic metadata schema, atomic write operations, resource URI generation) defined in Implementation Guidance section above.

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md` (§2.1 Python Type Safety, §2.2 FastAPI, §5.3 Input Validation, §6.1 Structured Logging)
- **Related Stories:** US-040 (validate_artifact tool), US-042 (resolve_artifact_path tool)
