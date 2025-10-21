# User Story: Implement store_artifact Tool

## Metadata
- **Story ID:** US-043
- **Title:** Implement store_artifact Tool
- **Type:** Feature
- **Status:** Draft (v3)
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
1. Accepts artifact content (markdown text)
2. Extracts metadata from artifact markdown (artifact ID, type, version, status, parent ID, title)
3. Validates extracted metadata against schema
4. Stores artifact to centralized location at configured base directory
5. Makes artifact accessible via MCP resource URI
6. Returns storage confirmation with resource URI

**Placeholder ID Support:** Draft artifacts stored by this tool may contain placeholder IDs (e.g., HLS-AAA, HLS-BBB, US-XXX) for sub-artifacts that will be resolved during the approval workflow (US-071 approve_artifact). This is expected behavior - placeholders are allowed in Draft status and will be replaced with final IDs when the artifact is approved.

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
1. Tool accepts one parameter:
   - `artifact_content` (string): Full artifact markdown text including metadata section
2. Tool extracts metadata from artifact markdown by parsing "## Metadata" section:
   - `artifact_id`: Artifact ID (e.g., "EPIC-006", "PRD-006")
   - `artifact_type`: Inferred from ID prefix (EPIC → epic, PRD → prd, etc.)
   - `version`: Extracted from filename pattern in metadata or inferred from content
   - `status`: Artifact status (e.g., "Draft", "Approved", "Planned")
   - `parent_id`: Optional parent artifact ID from metadata
   - `title`: Artifact title from metadata
3. Tool validates extracted metadata against schema:
   - Artifact ID format matches pattern for type (e.g., `EPIC-\d{3}` for epics)
   - Artifact type is allowed value (epic, prd, hls, backlog_story, tech_spec, adr, spike, task)
   - Status is valid for artifact lifecycle (Draft → Review → Approved → Planned → In Progress → Completed)
   - Version is positive integer
4. Tool generates storage path using configured artifacts base directory:
   - Pattern: `{ARTIFACTS_BASE_DIR}/{artifact_type}/{artifact_id}_v{version}.md`
   - Example: `{ARTIFACTS_BASE_DIR}/epic/EPIC-006_v1.md` (if ARTIFACTS_BASE_DIR="/workspace/artifacts")
   - Note: ARTIFACTS_BASE_DIR is separate from PATTERNS_BASE_DIR (patterns/templates directory)
5. Tool writes artifact content to storage location using async file I/O with atomic writes
6. Tool extracts and stores artifact metadata separately for queryability:
   - Metadata file: `{ARTIFACTS_BASE_DIR}/{artifact_type}/{artifact_id}_v{version}_metadata.json`
   - Enables fast metadata queries without loading full artifact content
7. Tool returns structured JSON response:
   ```json
   {
     "success": true,
     "resource_uri": "mcp://resources/artifacts/epic/006"
   }
   ```
8. Tool execution completes in <500ms p95 (per PRD-006 NFR-Performance-02)
9. Tool logs storage invocations with timestamp, artifact ID, type, size (bytes), storage path, duration

## Non-Functional Requirements
- **Performance:** Artifact storage latency <500ms p95 (per NFR-Performance-02)
- **Reliability:** Atomic write operations (temp file + rename to prevent partial writes)
- **Security:** Validate artifact ID and type to prevent directory traversal attacks
- **Observability:** Structured logging captures storage patterns for capacity planning
- **Maintainability:** Clear separation between metadata extraction, validation, storage, and response formatting

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
   import re

   class ArtifactMetadata(BaseModel):
       """Artifact metadata schema (extracted from markdown)"""
       artifact_id: str = Field(..., pattern=r'^[A-Z]+-\d{3}$')  # e.g., EPIC-006, PRD-006
       artifact_type: Literal[
           "epic", "prd", "hls", "backlog_story", "tech_spec", "adr", "spike", "task",
           "product_vision", "initiative"
       ]
       version: int = Field(..., ge=1, le=999)
       status: Literal[
           "Draft", "In Review", "Approved", "Planned", "In Progress", "Completed"
       ]
       parent_id: Optional[str] = Field(None, pattern=r'^[A-Z]+-\d{3}$')
       title: str = Field(..., min_length=5, max_length=200)

       @validator('artifact_type', pre=True, always=True)
       def infer_type_from_id(cls, v, values):
           """Infers artifact type from ID prefix if not provided"""
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
               return type_map.get(prefix)
           return v

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
               "task": "TASK",
               "product_vision": "VIS",
               "initiative": "INIT"
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
       artifact_content: str = Field(
           ...,
           min_length=100,
           description="Full artifact markdown text including metadata section"
       )
       task_id: str = Field(..., description="Task tracking ID for log correlation")

   class StoreArtifactResult(BaseModel):
       """Artifact storage result"""
       success: bool
       resource_uri: str  # e.g., mcp://resources/artifacts/epic/006
   ```

2. **Metadata Extraction from Markdown:**
   ```python
   import re
   from typing import Dict, Optional

   class MetadataExtractor:
       """Extracts metadata from artifact markdown"""

       @staticmethod
       def extract_metadata(artifact_content: str) -> Dict[str, str]:
           """Parses ## Metadata section and extracts fields"""
           metadata = {}

           # Extract Story ID / Epic ID / PRD ID, etc.
           id_patterns = [
               r'\*\*Story ID:\*\*\s+([A-Z]+-\d{3})',
               r'\*\*Epic ID:\*\*\s+([A-Z]+-\d{3})',
               r'\*\*PRD ID:\*\*\s+([A-Z]+-\d{3})',
               r'\*\*HLS ID:\*\*\s+([A-Z]+-\d{3})',
               r'\*\*SPEC ID:\*\*\s+([A-Z]+-\d{3})',
           ]
           for pattern in id_patterns:
               match = re.search(pattern, artifact_content)
               if match:
                   metadata['artifact_id'] = match.group(1)
                   break

           # Extract Title
           title_match = re.search(r'\*\*Title:\*\*\s+(.+)', artifact_content)
           if title_match:
               metadata['title'] = title_match.group(1).strip()

           # Extract Status
           status_match = re.search(r'\*\*Status:\*\*\s+(.+)', artifact_content)
           if status_match:
               metadata['status'] = status_match.group(1).strip()

           # Extract Parent ID
           parent_patterns = [
               r'\*\*Parent PRD:\*\*\s+([A-Z]+-\d{3})',
               r'\*\*Parent Epic:\*\*\s+([A-Z]+-\d{3})',
               r'\*\*Parent HLS:\*\*\s+([A-Z]+-\d{3})',
               r'\*\*Parent Initiative:\*\*\s+([A-Z]+-\d{3})',
           ]
           for pattern in parent_patterns:
               match = re.search(pattern, artifact_content)
               if match:
                   metadata['parent_id'] = match.group(1)
                   break

           # Extract or infer version (default to 1 if not found)
           # Check filename pattern in content or default
           metadata['version'] = '1'  # Default version

           return metadata

       @staticmethod
       def parse_to_model(artifact_content: str) -> ArtifactMetadata:
           """Extracts metadata and validates against Pydantic model"""
           metadata_dict = MetadataExtractor.extract_metadata(artifact_content)

           # Convert version to int
           metadata_dict['version'] = int(metadata_dict.get('version', 1))

           return ArtifactMetadata(**metadata_dict)
   ```

3. **Artifact Storage Logic:**
   ```python
   import aiofiles
   import json
   from pathlib import Path
   import tempfile
   import os
   from config import settings

   class ArtifactStorageManager:
       def __init__(self, base_dir: Optional[str] = None):
           self.base_dir = Path(base_dir or settings.ARTIFACTS_BASE_DIR)
           self.base_dir.mkdir(parents=True, exist_ok=True)

       async def store(
           self,
           artifact_content: str,
           metadata: ArtifactMetadata
       ) -> StoreArtifactResult:
           """Stores artifact content and metadata to centralized storage"""
           # Step 1: Generate storage paths using configured base directory
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
               resource_uri=resource_uri
           )

       def _generate_storage_path(self, metadata: ArtifactMetadata) -> Path:
           """Generates storage path using configured artifacts base directory"""
           # Pattern: {ARTIFACTS_BASE_DIR}/{type}/{id}_v{version}.md
           # Example: /workspace/artifacts/epic/EPIC-006_v1.md
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

4. **MCP Tool Implementation:**
   ```python
   from mcp.server.fastmcp import FastMCP
   import structlog
   import time

   mcp = FastMCP(name="MCPServer", version="1.0.0")
   logger = structlog.get_logger()
   storage_manager = ArtifactStorageManager()

   @mcp.tool(
       name="store_artifact",
       description="""
       Stores generated artifact to centralized storage accessible across projects.

       Use this tool when:
       - You have generated a new artifact (Epic, PRD, HLS, Backlog Story, etc.)
       - You want to make artifact accessible to other projects via MCP resources
       - You need to create shared reference artifacts (Product Vision, Initiative)

       Input:
       - artifact_content: Full markdown text including metadata section
       - task_id: Task tracking ID for log correlation

       Tool extracts metadata from artifact markdown (ID, type, version, status, title)
       and stores to centralized location with MCP resource URI.

       Supports multi-project workflows where artifacts are shared across teams.
       """
   )
   async def store_artifact(params: StoreArtifactInput) -> StoreArtifactResult:
       """Stores artifact to centralized storage"""
       start_time = time.time()

       try:
           # Extract metadata from artifact content
           metadata = MetadataExtractor.parse_to_model(params.artifact_content)

           # Store artifact
           result = await storage_manager.store(
               artifact_content=params.artifact_content,
               metadata=metadata
           )

           # Log storage invocation
           duration_ms = (time.time() - start_time) * 1000
           logger.info(
               "artifact_storage_completed",
               task_id=params.task_id,
               artifact_id=metadata.artifact_id,
               artifact_type=metadata.artifact_type,
               version=metadata.version,
               size_bytes=len(params.artifact_content),
               resource_uri=result.resource_uri,
               duration_ms=duration_ms
           )

           return result

       except ValidationError as e:
           logger.error("artifact_storage_validation_error", error=str(e))
           raise  # Re-raise for FastMCP ErrorHandlingMiddleware (→ JSON-RPC -32602)
       except Exception as e:
           logger.error("artifact_storage_error", error=str(e))
           raise  # Re-raise for FastMCP ErrorHandlingMiddleware (→ JSON-RPC -32603)
   ```

5. **Testing Strategy:**
   - Unit tests: Validate metadata extraction, storage path generation, atomic writes
   - Integration tests: Verify tool stores artifact and metadata correctly
   - Security tests: Attempt directory traversal via artifact_id, verify rejection
   - Performance tests: Verify <500ms p95 latency with various artifact sizes
   - Edge case tests: Handle large artifacts (>100KB), concurrent storage requests

### Technical Tasks
- [ ] Implement metadata extraction from markdown
- [ ] Implement Pydantic models for metadata validation
- [ ] Implement ArtifactStorageManager class with atomic write operations
- [ ] Implement storage path generation using configured base directory
- [ ] Implement metadata JSON generation
- [ ] Implement MCP tool endpoint with FastMCP decorator
- [ ] Add structured logging for artifact storage invocations
- [ ] Write unit tests for metadata extraction and validation (80% coverage)
- [ ] Write integration tests for full storage workflow
- [ ] Write security tests for directory traversal protection
- [ ] Write performance tests (<500ms p95 latency)
- [ ] Add Taskfile commands for running artifact storage tool tests

## Acceptance Criteria

### Scenario 1: Epic artifact stored successfully
**Given** Claude Code has generated Epic-006 artifact
**When** Claude Code calls `store_artifact(artifact_content=epic_text, task_id="task-123")` where epic_text contains metadata section with Story ID: EPIC-006, Title: "MCP Server Integration", Status: "Draft"
**Then** tool extracts metadata from markdown (artifact_id=EPIC-006, artifact_type=epic, version=1, status=Draft)
**And** tool validates metadata schema (passes)
**And** tool writes artifact to `{ARTIFACTS_BASE_DIR}/epic/EPIC-006_v1.md`
**And** tool writes metadata to `{ARTIFACTS_BASE_DIR}/epic/EPIC-006_v1_metadata.json`
**And** returns `{success: true, resource_uri: "mcp://resources/artifacts/epic/006"}`
**And** execution completes in <500ms

### Scenario 2: Metadata extraction fails gracefully
**Given** Artifact content missing required metadata fields
**When** Claude Code calls `store_artifact(artifact_content=malformed_text)`
**Then** tool attempts to extract metadata from markdown
**And** extraction fails (missing artifact ID)
**And** tool returns validation error: "Metadata extraction failed: artifact_id not found"
**And** no files written to storage

### Scenario 3: Atomic write prevents partial file on failure
**Given** Disk write operation fails midway (simulated I/O error)
**When** Claude Code calls `store_artifact(artifact_content=large_text)`
**Then** tool writes to temp file first
**And** disk error occurs during temp file write
**And** tool cleans up temp file (no partial file left)
**And** returns 500 error with retryable flag
**And** next retry succeeds (no corrupted state)

### Scenario 4: Metadata JSON queryable without loading full artifact
**Given** Multiple artifacts stored at configured artifacts directory
**When** User wants to list all approved epics without loading full content
**Then** user reads metadata JSON files: `{ARTIFACTS_BASE_DIR}/epic/*_metadata.json`
**And** metadata includes artifact_id, type, status, version, parent_id, title, size_bytes
**And** query completes 10x faster than loading full artifacts (benchmark validation)

### Scenario 5: Resource URI enables MCP access
**Given** Epic-006 stored at `{ARTIFACTS_BASE_DIR}/epic/EPIC-006_v1.md`
**When** Claude Code requests `mcp://resources/artifacts/epic/006`
**Then** MCP Server returns EPIC-006 v1 content
**And** resource accessible from any project connected to MCP Server

### Scenario 6: All artifact types storable
**Given** Sample artifacts for all types
**When** Claude Code stores each type (Epic, PRD, HLS, US, SPEC, TASK, ADR, SPIKE)
**Then** All artifacts stored to configured artifacts directory with correct subdirectories:
  - `{ARTIFACTS_BASE_DIR}/epic/EPIC-006_v1.md`
  - `{ARTIFACTS_BASE_DIR}/prd/PRD-006_v1.md`
  - `{ARTIFACTS_BASE_DIR}/hls/HLS-006_v1.md`
  - `{ARTIFACTS_BASE_DIR}/backlog_story/US-040_v1.md`
  - `{ARTIFACTS_BASE_DIR}/tech_spec/SPEC-001_v1.md`
  - `{ARTIFACTS_BASE_DIR}/task/TASK-001_v1.md`
  - `{ARTIFACTS_BASE_DIR}/adr/ADR-001_v1.md`
  - `{ARTIFACTS_BASE_DIR}/spike/SPIKE-001_v1.md`

### Scenario 7: Artifact storage execution logged with task_id
**Given** Claude Code calls store_artifact tool
**When** Storage completes
**Then** tool logs structured event with fields: task_id, artifact_id, artifact_type, version, size_bytes, resource_uri, duration_ms
**And** log format is JSON (structured logging)
**And** log includes task_id for correlation with other tool calls

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Not Needed (Single Sprint-Ready Task)

**Rationale:**
- **Story Points:** 5 SP (at threshold - CONSIDER SKIPPING per decision matrix)
- **Developer Count:** Single developer (metadata extraction + file I/O)
- **Domain Span:** Single domain (file system operations and metadata parsing)
- **Complexity:** Low-moderate - metadata extraction adds complexity but follows standard regex patterns
- **Uncertainty:** Low - clear implementation approach using markdown parsing and async file I/O
- **Override Factors:** None (metadata extraction straightforward, no complex business logic)

Per SDLC Section 11.6 Decision Matrix: "5 SP, single developer, low-moderate complexity → SKIP (Metadata extraction is straightforward pattern matching)".

**No task decomposition needed.** Story can be completed as single unit of work in 2-3 days.

## Definition of Done
- [ ] Metadata extraction from markdown implemented
- [ ] Pydantic models implemented for metadata validation
- [ ] ArtifactStorageManager class with atomic write operations
- [ ] Storage path generation using configured base directory
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

## Decisions Made

**Decision 1: Single parameter input (artifact_content only)**
- **Made:** During v2 refinement (feedback from US-040-047_v1_comments.md)
- **Rationale:** Requiring AI Agent to manually extract and provide metadata as separate parameter adds unnecessary burden. Tool should extract metadata from artifact markdown automatically, reducing client-side complexity
- **Impact:** Changed from three parameters (artifact_content, metadata, file_path) to single parameter (artifact_content). Added metadata extraction logic to tool implementation
- **Alternative Considered:** If generators can return metadata as JSON, could accept metadata parameter, but this requires generator prompt changes and evaluation (deferred to implementation phase)

**Decision 2: Storage path uses configured base directory (PATTERNS_BASE_DIR)**
- **Made:** During v2 refinement (feedback from US-040-047_v1_comments.md)
- **Rationale:** Hardcoded paths prevent configuration flexibility and testing with different directory structures. Base directory should be configurable for local development, testing, and production environments
- **Impact:** Use `settings.PATTERNS_BASE_DIR` from configuration instead of hardcoded `"shared_artifacts"` path

**Decision 3: Simplified response (success + resource_uri only)**
- **Made:** During v2 refinement (feedback from US-040-047_v1_comments.md)
- **Rationale:** Client only needs to know storage succeeded and how to access artifact via MCP. Storage path, metadata path, artifact ID, type, and version are server-side implementation details
- **Impact:** Response reduced from 7 fields to 2 fields: `{success: true, resource_uri: "mcp://resources/artifacts/epic/006"}`

**Decision 4: File path parameter removed from input**
- **Made:** During v2 refinement (feedback from US-040-047_v1_comments.md)
- **Rationale:** File paths are server-side configuration concerns. Client should not specify storage location (security risk, prevents centralized path management)
- **Impact:** Removed `file_path` optional parameter from input schema

**Decision 5: Separate ARTIFACTS_BASE_DIR from PATTERNS_BASE_DIR**
- **Made:** During v3 refinement (feedback from US-040-047_v2_comments.md)
- **Rationale:** Patterns (templates) and artifacts (generated content) can come from different file system sources. Separation enables: (1) Patterns from read-only shared directory (e.g., /opt/mcp/patterns/), (2) Artifacts to writable project directory (e.g., /workspace/artifacts/), (3) Better security (patterns can be read-only), (4) Flexible deployment configurations
- **Impact:**
  - Introduced `ARTIFACTS_BASE_DIR` configuration variable for generated artifact storage
  - Retained `PATTERNS_BASE_DIR` as separate configuration for templates/patterns
  - Updated all storage paths to use ARTIFACTS_BASE_DIR
  - Configuration example:
    ```python
    class Settings(BaseSettings):
        PATTERNS_BASE_DIR: str = "/opt/mcp/patterns"  # Templates (read-only)
        ARTIFACTS_BASE_DIR: str = "/workspace/artifacts"  # Generated artifacts (read-write)
        VALIDATION_RESOURCES_DIR: str = "/opt/mcp/validation"  # Validation checklists
    ```
- **Alternative Considered:** Use single directory for both patterns and artifacts, but this prevents flexible deployment scenarios and security hardening

**Decision 6: Rename request_id → task_id (mandatory parameter)**
- **Made:** During v3 refinement (feedback from US-040-047_v2_comments.md)
- **Rationale:** "task_id" provides better visibility and traceability in logs. Naming aligns with task tracking system terminology. Mandatory parameter ensures all tool invocations are correlated
- **Impact:**
  - Parameter renamed in StoreArtifactInput (was optional, now mandatory)
  - All logging updated to use `task_id` field
  - Function signature change across all tool calls
  - Better log correlation with task tracking microservice

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md` (§2.1 Python Type Safety, §2.2 FastAPI, §5.3 Input Validation, §6.1 Structured Logging)
- **Related Stories:** US-040 (validate_artifact tool), US-042 (resolve_artifact_path tool)
- **Feedback v1:** `/feedback/US-040-047_v1_comments.md`
- **Feedback v2:** `/feedback/US-040-047_v2_comments.md`
- **Changes Applied:** `/feedback/US-040-047_v2_changes_applied.md`
