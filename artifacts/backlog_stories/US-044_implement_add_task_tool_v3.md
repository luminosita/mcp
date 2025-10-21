# User Story: Implement add_task Tool

## Metadata
- **Story ID:** US-044
- **Title:** Implement add_task Tool
- **Type:** Feature
- **Status:** Draft (v3)
- **Priority:** Must-have (enables automatic sub-artifact workflow initiation with validated inputs, critical for FR-24 and FR-25)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-008 (MCP Tools - Validation and Path Resolution)
- **Functional Requirements Covered:** FR-24
- **Informed By Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Functional Requirements - FR-24, FR-25
- **Functional Requirements Coverage:**
  - **FR-24:** MCP Server SHALL provide `add_task` tool (integrated with Task Tracking microservice) that adds new tasks to queue after artifact generation, enabling automatic sub-artifact workflow initiation
  - **FR-25 (Related):** All artifact generators SHALL evaluate whether sub-artifacts are required after generation and return appropriate metadata flags for automatic task queue population

**Parent High-Level Story:** [HLS-008: MCP Tools - Validation and Path Resolution]
- **Link:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 5: Implement add_task Tool

## User Story
As Claude Code, I want a tool to automatically add tasks with VALIDATED and RESOLVED generator inputs to the queue after generating artifacts, so that sub-artifact workflows initiate without manual TODO.md updates and without runtime path resolution errors.

## Description
Currently, after generating an artifact (e.g., PRD-006), Claude Code requires manual TODO.md updates to add tasks for sub-artifacts (e.g., "Generate HLS-006 from PRD-006"). This creates:
1. **Manual Overhead:** Human must update TODO.md after every artifact generation
2. **Forgetting Risk:** Sub-artifacts may be forgotten if not immediately documented
3. **Workflow Fragmentation:** No programmatic linkage between artifact generation and task creation
4. **Runtime Resolution Errors:** NEW - Tasks without pre-resolved inputs fail during generator execution

This story implements a deterministic Python tool (`add_task`) that:
1. Accepts task list with artifact IDs and **RESOLVED generator inputs** (MCP resource URIs)
2. Validates task metadata against schema (artifact ID format, status allowed, inputs complete)
3. **Validates all mandatory inputs present** (per generator requirements)
4. **Validates all input files exist** (resource paths valid)
5. **Validates all input artifacts approved** (status = "Approved" or "Finalized")
6. Calls Task Tracking microservice REST API (`POST /tasks/batch`) to add tasks to queue
7. Returns confirmation with task IDs added
8. Enables generators to automatically trigger sub-artifact workflows:
   - PRD generator finishes → calls `add_task` to create HLS generation tasks with resolved inputs
   - HLS generator finishes → calls `add_task` to create Backlog Story generation tasks with resolved inputs
   - Epic generator finishes → calls `add_task` to create PRD generation tasks with resolved inputs

**Key v3 Enhancement:** Tasks now include **all resolved generator inputs** (MCP resource URIs) at creation time. No runtime path resolution needed. All mandatory inputs validated before task creation.

The tool eliminates manual TODO.md updates for sub-artifact workflows, reduces human overhead, ensures complete artifact decomposition, and **guarantees task validity** before execution.

## Implementation Research References

**Primary Research Document:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

**Technical Patterns Applied:**
- **§2.1: Python 3.11+ with Type Safety:** Use Pydantic models for task metadata validation with full type hints (ref: Implementation Research §2.1 - Programming Language: Python 3.11+)
- **§2.2: FastAPI Integration:** Expose add_task tool as MCP tool via FastAPI with auto-generated OpenAPI documentation (ref: Implementation Research §2.2 - Backend Framework: FastAPI 0.100+)
- **§5.3: Input Validation:** Validate task metadata (artifact ID format, status values, inputs completeness) with Pydantic (ref: Implementation Research §5.3 - Input Validation and Command Injection Prevention)
- **§6.1: Structured Logging:** Log task addition events with task count, artifact IDs, generator names (ref: Implementation Research §6.1 - Structured Logging)

**Anti-Patterns Avoided:**
- **§8.1: Poor Error Handling:** Return structured error responses for API failures with retryable flag (ref: Implementation Research §8.1 - Pitfall 3)
- **§8.2: Synchronous Blocking Calls in Async Context:** Use async HTTP client (httpx) for Task Tracking API calls (ref: Implementation Research §8.2 - Anti-Pattern 1)

**Performance Considerations:**
- **§2.4: Caching Layer:** Not applicable for task addition (write-heavy, no cache benefit)

## Functional Requirements
1. Tool accepts two parameters:
   - `tasks` (list): List of TaskMetadata objects, each including:
     - `artifact_id`: Full artifact ID (e.g., "HLS-006", "US-040")
     - `generator`: Generator name (e.g., "hls-generator", "backlog-story-generator")
     - `inputs`: List of GeneratorInput objects with ALL resolved MCP resource URIs
     - `status`: Task status (default: "pending")
     - `description`: Optional task description (auto-generated if not provided)
   - `task_id` (string, mandatory): Task tracking ID for log correlation
2. **NEW v3:** Tool validates inputs completeness:
   - All GeneratorInput objects have valid MCP resource URIs
   - Resource paths exist in filesystem
   - Artifact inputs have status = "Approved" or "Finalized"
   - No duplicate artifact_id in batch
3. Tool validates task metadata against schema:
   - Artifact ID format matches pattern for type (e.g., `HLS-\d{3}` for hls)
   - Generator name follows convention
   - Status is allowed value (pending, in_progress, completed)
   - inputs list non-empty
4. Tool calls Task Tracking microservice REST API:
   - Endpoint: `POST /tasks/batch`
   - Request body: `{"project_id": "ai-agent-mcp-server", "tasks": [...]}`
   - **NEW v3:** Tasks include `inputs_json` JSONB field with resolved GeneratorInput list
   - Authentication: API key or JWT token (configured in settings)
5. Tool returns structured JSON response:
   ```json
   {
     "success": true,
     "tasks_added": 3,
     "task_ids": ["TASK-012", "TASK-013", "TASK-014"],
     "artifact_ids": ["HLS-012", "HLS-013", "HLS-014"]
   }
   ```
6. Tool execution completes in <500ms p95 (per PRD-006 NFR-Performance-02)
7. Tool logs task addition invocations with timestamp, task_id, task count, artifact IDs, generator names, duration
8. Tool handles API errors gracefully:
   - Connection errors → retry 3 times with exponential backoff (100ms, 200ms, 400ms)
   - Authentication errors → fail immediately with clear error message
   - Validation errors → fail immediately with validation details

## Non-Functional Requirements
- **Performance:** Task addition latency <500ms p95 (per NFR-Performance-02)
- **Reliability:** Retry transient failures (connection errors), fail fast on permanent failures (auth errors, validation errors)
- **Security:** API authentication required (API key or JWT token from environment variable)
- **Observability:** Structured logging captures task addition patterns for workflow analysis
- **Maintainability:** Clear separation between metadata validation, input validation, API calls, and retry logic

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** Follow established implementation patterns for MCP tools. Supplement with story-specific task addition logic.

**References to Implementation Standards:**
- **prompts/CLAUDE/python/patterns-tooling.md:** Use Taskfile commands (`task test`, `task lint`, `task type-check`)
- **prompts/CLAUDE/python/patterns-testing.md:** Testing patterns (80% coverage, async tests, mock API calls)
- **prompts/CLAUDE/python/patterns-typing.md:** Type hints with mypy strict mode, Pydantic models
- **prompts/CLAUDE/python/patterns-validation.md:** Input validation with Pydantic, security patterns
- **prompts/CLAUDE/python/patterns-architecture.md:** Project structure following established patterns

### Implementation Guidance

**Story-Specific Technical Approach:**

1. **Pydantic Models for Tool Input/Output (v3 Schema):**
   ```python
   from pydantic import BaseModel, Field, validator
   from typing import List, Literal, Optional
   from pathlib import Path

   class GeneratorInput(BaseModel):
       """Resolved generator input with MCP resource URI"""
       name: str = Field(..., description="Input name from generator config (e.g., 'prd', 'business_research')")
       classification: Literal["mandatory", "recommended", "conditional"] = Field(..., description="Input classification")
       artifact_type: str = Field(..., description="Artifact type (e.g., 'prd', 'research')")
       artifact_id: str = Field(..., description="Artifact ID (e.g., 'PRD-006') or 'N/A' for non-artifact inputs")
       resource_path: str = Field(..., description="Resolved file path (e.g., 'artifacts/prds/PRD-006_v3.md')")
       mcp_resource_uri: str = Field(..., pattern=r'^file:///.*', description="MCP resource URI")
       status: str = Field(..., description="Artifact status ('Approved', 'Finalized', etc.)")

   class TaskMetadata(BaseModel):
       """Task metadata schema (v3 - with resolved inputs)"""
       artifact_id: str = Field(..., pattern=r'^[A-Z]+-\d{3,}$')  # e.g., HLS-012, US-040
       generator: str = Field(..., description="Generator name (e.g., 'hls-generator')")
       task_id: str = Field(..., description="Task tracking ID for log correlation")
       inputs: List[GeneratorInput] = Field(..., min_items=1, description="ALL resolved generator inputs")
       status: Literal["pending", "in_progress", "completed"] = "pending"
       description: str = ""

       @validator('description', pre=True, always=True)
       def auto_generate_description(cls, v, values):
           """Auto-generates description if not provided"""
           if not v and 'artifact_id' in values and 'inputs' in values:
               # Extract parent artifact from inputs (first mandatory input)
               mandatory_inputs = [inp for inp in values['inputs'] if inp.classification == 'mandatory']
               if mandatory_inputs and mandatory_inputs[0].artifact_id != 'N/A':
                   parent_id = mandatory_inputs[0].artifact_id
                   return f"Generate {values['artifact_id']} from {parent_id}"
               return f"Generate {values['artifact_id']}"
           return v

       @validator('inputs')
       def validate_inputs_non_empty(cls, v):
           """Validates inputs list is non-empty"""
           if not v:
               raise ValueError("inputs list must contain at least one GeneratorInput")
           return v

       @validator('inputs')
       def validate_mandatory_inputs_present(cls, v):
           """Validates at least one mandatory input present"""
           mandatory_inputs = [inp for inp in v if inp.classification == 'mandatory']
           if not mandatory_inputs:
               raise ValueError("At least one mandatory input required")
           return v

       @validator('inputs')
       def validate_resource_uris_format(cls, v):
           """Validates all MCP resource URIs have correct format"""
           for inp in v:
               if not inp.mcp_resource_uri.startswith('file:///'):
                   raise ValueError(
                       f"Invalid MCP resource URI format: {inp.mcp_resource_uri}. "
                       f"Expected: file:///workspace/..."
                   )
           return v

       @validator('inputs')
       def validate_resource_paths_exist(cls, v):
           """Validates all resource paths exist in filesystem"""
           for inp in v:
               resource_path = Path(inp.resource_path)
               if not resource_path.exists():
                   raise ValueError(
                       f"Input file not found: {inp.resource_path} "
                       f"(input name: {inp.name}, artifact_id: {inp.artifact_id})"
                   )
           return v

       @validator('inputs')
       def validate_artifact_inputs_approved(cls, v):
           """Validates artifact inputs have status = Approved or Finalized"""
           for inp in v:
               # Skip non-artifact inputs (research documents can be Finalized)
               if inp.artifact_id == 'N/A':
                   if inp.status != 'Finalized':
                       raise ValueError(
                           f"Research input '{inp.name}' must have status='Finalized' "
                           f"(current status: {inp.status})"
                       )
               else:
                   # Artifact inputs must be Approved
                   if inp.status != 'Approved':
                       raise ValueError(
                           f"Input artifact {inp.artifact_id} must be Approved "
                           f"(current status: {inp.status})"
                       )
           return v

   class AddTaskInput(BaseModel):
       """Input schema for add_task tool"""
       tasks: List[TaskMetadata] = Field(..., min_items=1, max_items=100)
       task_id: str = Field(..., description="Task tracking ID for log correlation")

       @validator('tasks')
       def validate_no_duplicate_artifact_ids(cls, v):
           """Validates no duplicate artifact_id in batch"""
           artifact_ids = [task.artifact_id for task in v]
           duplicates = [aid for aid in artifact_ids if artifact_ids.count(aid) > 1]
           if duplicates:
               raise ValueError(
                   f"Duplicate artifact_id in batch: {', '.join(set(duplicates))}"
               )
           return v

   class AddTaskResult(BaseModel):
       """Task addition result"""
       success: bool
       tasks_added: int
       task_ids: List[str]  # e.g., ["TASK-012", "TASK-013", ...]
       artifact_ids: List[str]  # e.g., ["HLS-012", "HLS-013", ...]
   ```

2. **Task Tracking API Client (v3 - with inputs_json):**
   ```python
   import httpx
   from typing import List
   import asyncio
   from tenacity import retry, stop_after_attempt, wait_exponential

   class TaskTrackingClient:
       def __init__(self, base_url: str, api_key: str, project_id: str):
           self.base_url = base_url
           self.api_key = api_key
           self.project_id = project_id
           self.client = httpx.AsyncClient(
               headers={"Authorization": f"Bearer {api_key}"},
               timeout=5.0
           )

       @retry(
           stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=0.1, min=0.1, max=0.4),  # 100ms, 200ms, 400ms
           reraise=True
       )
       async def add_tasks_batch(self, tasks: List[TaskMetadata]) -> dict:
           """Adds tasks to Task Tracking microservice via REST API"""
           # Prepare request payload (v3 schema with inputs_json)
           payload = {
               "project_id": self.project_id,
               "tasks": [
                   {
                       "artifact_id": task.artifact_id,
                       "generator": task.generator,
                       "status": task.status,
                       "description": task.description,
                       # NEW v3: Include full inputs list as JSONB
                       "inputs_json": [
                           {
                               "name": inp.name,
                               "classification": inp.classification,
                               "artifact_type": inp.artifact_type,
                               "artifact_id": inp.artifact_id,
                               "resource_path": inp.resource_path,
                               "mcp_resource_uri": inp.mcp_resource_uri,
                               "status": inp.status
                           }
                           for inp in task.inputs
                       ]
                   }
                   for task in tasks
               ]
           }

           # Call API endpoint
           response = await self.client.post(
               f"{self.base_url}/tasks/batch",
               json=payload
           )

           # Handle response
           if response.status_code == 201:
               return response.json()  # {success: true, tasks_added: N, task_ids: [...]}
           elif response.status_code == 400:
               # Validation error - fail fast (no retry)
               error_detail = response.json().get("detail", "Unknown validation error")
               raise ValueError(f"Task validation failed: {error_detail}")
           elif response.status_code == 401:
               # Auth error - fail fast (no retry)
               raise PermissionError("Task Tracking API authentication failed")
           else:
               # Server error - retryable
               response.raise_for_status()

       async def close(self):
           """Closes HTTP client"""
           await self.client.aclose()
   ```

3. **MCP Tool Implementation (v3):**
   ```python
   from mcp.server.fastmcp import FastMCP
   import structlog
   import time
   from pydantic_settings import BaseSettings

   class Settings(BaseSettings):
       TASK_TRACKING_API_URL: str = "http://localhost:8080"
       TASK_TRACKING_API_KEY: str
       PROJECT_ID: str = "ai-agent-mcp-server"

       class Config:
           env_file = ".env"

   settings = Settings()

   mcp = FastMCP(name="MCPServer", version="1.0.0")
   logger = structlog.get_logger()
   task_client = TaskTrackingClient(
       base_url=settings.TASK_TRACKING_API_URL,
       api_key=settings.TASK_TRACKING_API_KEY,
       project_id=settings.PROJECT_ID
   )

   @mcp.tool(
       name="add_task",
       description="""
       Adds new tasks to task queue with VALIDATED and RESOLVED generator inputs.

       Use this tool when:
       - You have generated an artifact that requires sub-artifacts (e.g., PRD → HLS)
       - You want to automatically trigger sub-artifact generation workflows
       - You need to populate task queue without manual TODO.md updates
       - You have RESOLVED all generator input paths (MCP resource URIs)

       Input:
       - tasks: List of TaskMetadata with artifact_id, generator, and RESOLVED inputs
       - task_id: Task tracking ID for log correlation

       IMPORTANT v3 Change:
       - Tasks must include ALL resolved generator inputs (MCP resource URIs)
       - Tool validates inputs completeness before creating tasks
       - Tool validates all input files exist
       - Tool validates all input artifacts approved
       - No runtime path resolution needed (all paths pre-resolved)

       Integrates with Task Tracking microservice to add tasks via REST API.

       Reduces manual overhead for sub-artifact workflow initiation.
       Guarantees task validity before execution.
       """
   )
   async def add_task(params: AddTaskInput) -> AddTaskResult:
       """Adds tasks to task tracking queue with validated inputs"""
       start_time = time.time()

       try:
           # Validation already performed by Pydantic (inputs completeness, file existence, status)

           # Call Task Tracking API
           api_response = await task_client.add_tasks_batch(params.tasks)

           # Extract task IDs and artifact IDs
           task_ids = api_response.get("task_ids", [])
           artifact_ids = [task.artifact_id for task in params.tasks]

           # Log task addition invocation
           duration_ms = (time.time() - start_time) * 1000
           logger.info(
               "task_addition_completed",
               task_id=params.task_id,
               tasks_added=len(params.tasks),
               artifact_ids=artifact_ids,
               generators=[task.generator for task in params.tasks],
               task_ids=task_ids,
               inputs_validated=True,
               mandatory_inputs_count=sum(
                   len([inp for inp in task.inputs if inp.classification == 'mandatory'])
                   for task in params.tasks
               ),
               recommended_inputs_count=sum(
                   len([inp for inp in task.inputs if inp.classification == 'recommended'])
                   for task in params.tasks
               ),
               duration_ms=duration_ms
           )

           return AddTaskResult(
               success=True,
               tasks_added=len(params.tasks),
               task_ids=task_ids,
               artifact_ids=artifact_ids
           )

       except ValueError as e:
           # Validation error from API or Pydantic
           logger.error("task_addition_validation_error", task_id=params.task_id, error=str(e))
           raise  # Re-raise for FastMCP ErrorHandlingMiddleware (→ JSON-RPC -32602)
       except PermissionError as e:
           # Auth error from API
           logger.error("task_addition_auth_error", task_id=params.task_id, error=str(e))
           raise  # Re-raise for FastMCP ErrorHandlingMiddleware (→ JSON-RPC -32000)
       except Exception as e:
           # Server error or network error
           logger.error("task_addition_error", task_id=params.task_id, error=str(e))
           raise  # Re-raise for FastMCP ErrorHandlingMiddleware (→ JSON-RPC -32603)
   ```

4. **Testing Strategy:**
   - Unit tests: Validate TaskMetadata schema with inputs list
   - Unit tests: Validate GeneratorInput schema
   - Unit tests: Test input validation (mandatory present, files exist, status approved)
   - Unit tests: Test no duplicate artifact_id validation
   - Integration tests: Mock Task Tracking API, verify correct API calls with inputs_json
   - Retry tests: Simulate transient failures, verify exponential backoff retry logic
   - Error handling tests: Test validation errors (missing inputs, file not found, not approved), auth errors, server errors
   - Performance tests: Verify <500ms p95 latency with various task batch sizes

### Technical Tasks
- [ ] Implement GeneratorInput Pydantic model
- [ ] Implement updated TaskMetadata model with inputs list
- [ ] Implement input validation validators (mandatory present, files exist, status approved)
- [ ] Implement no duplicate artifact_id validator
- [ ] Update TaskTrackingClient to send inputs_json in API payload
- [ ] Implement MCP tool endpoint with FastMCP decorator
- [ ] Add structured logging for task addition with input validation metrics
- [ ] Add retry logic with exponential backoff (3 retries: 100ms, 200ms, 400ms)
- [ ] Add error handling for validation, auth, and server errors
- [ ] Write unit tests for GeneratorInput and TaskMetadata models (80% coverage)
- [ ] Write unit tests for input validation logic
- [ ] Write integration tests with mocked Task Tracking API (verify inputs_json sent)
- [ ] Write retry tests (simulate transient failures)
- [ ] Write performance tests (<500ms p95 latency)
- [ ] Add Taskfile commands for running add_task tool tests

## Acceptance Criteria

### Scenario 1: HLS tasks added with resolved inputs after PRD approval
**Given** approve_artifact tool finishes approving PRD-006
**And** approve_artifact has resolved ALL inputs for 3 HLS tasks:
  - Mandatory: PRD-006 (file:///workspace/artifacts/prds/PRD-006_v3.md, status: Approved)
  - Recommended: Business Research (file:///workspace/artifacts/research/..., status: Finalized)
  - Recommended: Implementation Research (file:///workspace/artifacts/research/..., status: Finalized)
**When** approve_artifact calls `add_task(tasks=[HLS-012 with inputs, HLS-013 with inputs, HLS-014 with inputs], task_id="task-123")`
**Then** tool validates all inputs complete (mandatory present, files exist, status correct)
**And** tool calls Task Tracking API `POST /tasks/batch` with inputs_json
**And** returns `{success: true, tasks_added: 3, task_ids: ["TASK-012", "TASK-013", "TASK-014"], artifact_ids: ["HLS-012", "HLS-013", "HLS-014"]}`
**And** execution completes in <500ms

### Scenario 2: Validation fails if mandatory input missing
**Given** Task has empty inputs list
**When** Claude Code calls `add_task(tasks=[{artifact_id: "HLS-012", generator: "hls-generator", task_id: "task-123", inputs: []}], task_id="task-123")`
**Then** tool returns validation error: "At least one mandatory input required"
**And** no API call made
**And** error logged with task_id for debugging

### Scenario 3: Validation fails if input file not found
**Given** Task has input with resource_path that doesn't exist
**When** Claude Code calls `add_task` with task containing non-existent path
**Then** tool returns validation error: "Input file not found: artifacts/prds/PRD-006_v3.md (input name: prd, artifact_id: PRD-006)"
**And** no API call made

### Scenario 4: Validation fails if input artifact not approved
**Given** Task has input artifact with status = "Draft"
**When** Claude Code calls `add_task` with task containing Draft input
**Then** tool returns validation error: "Input artifact PRD-006 must be Approved (current status: Draft)"
**And** no API call made

### Scenario 5: Validation fails if duplicate artifact_id in batch
**Given** Batch contains 2 tasks with same artifact_id
**When** Claude Code calls `add_task(tasks=[{artifact_id: "HLS-012", ...}, {artifact_id: "HLS-012", ...}], task_id="task-123")`
**Then** tool returns validation error: "Duplicate artifact_id in batch: HLS-012"
**And** no API call made

### Scenario 6: API auth error handled gracefully
**Given** Task Tracking API key is invalid
**When** Claude Code calls `add_task(tasks=[...], task_id="task-123")`
**Then** tool calls Task Tracking API
**And** API returns 401 Unauthorized
**And** tool returns 401 error with message: "Task Tracking API authentication failed"
**And** no retry attempts (auth errors are permanent, not transient)

### Scenario 7: Transient API failure retried with exponential backoff
**Given** Task Tracking API temporarily unavailable (503 error)
**When** Claude Code calls `add_task(tasks=[...], task_id="task-123")`
**Then** tool calls API, receives 503 error
**And** tool retries after 100ms → still fails
**And** tool retries after 200ms → still fails
**And** tool retries after 400ms → succeeds
**And** returns success result
**And** total duration ~700ms (within <500ms p95 target for most requests)

### Scenario 8: Task addition execution logged with input validation metrics
**Given** Claude Code calls add_task tool with 3 tasks
**When** Task addition completes
**Then** tool logs structured event with fields: task_id, tasks_added, artifact_ids, generators, task_ids, inputs_validated=true, mandatory_inputs_count, recommended_inputs_count, duration_ms
**And** log format is JSON (structured logging)
**And** log includes task_id for correlation with other tool calls

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Not Needed (Single Sprint-Ready Task)

**Rationale:**
- **Story Points:** 5 SP → 8 SP (increased due to v3 input validation complexity)
- **Developer Count:** Single developer (API client with enhanced Pydantic validation)
- **Domain Span:** Single domain (HTTP API integration with input validation)
- **Complexity:** Moderate - enhanced validation logic (file existence, status checks, input completeness)
- **Uncertainty:** Low - clear API contract, validation patterns well-established
- **Override Factors:** None (validation logic is standard Pydantic pattern, increased complexity but not requiring decomposition)

Per SDLC Section 11.6 Decision Matrix: "8 SP, single developer, moderate complexity → CONSIDER SKIPPING if complexity manageable in 3-5 days".

**Decision:** Skip decomposition. Enhanced validation adds complexity but story remains cohesive unit of work completable in 3-5 days.

## Definition of Done
- [ ] GeneratorInput Pydantic model implemented
- [ ] Updated TaskMetadata model with inputs list implemented
- [ ] Input validation validators implemented (mandatory present, files exist, status approved)
- [ ] No duplicate artifact_id validator implemented
- [ ] TaskTrackingClient updated to send inputs_json in API payload
- [ ] MCP tool endpoint implemented with FastMCP
- [ ] Structured logging for task addition with input validation metrics
- [ ] Retry logic with exponential backoff (3 retries)
- [ ] Error handling for validation, auth, and server errors
- [ ] Unit tests written and passing (80% coverage, includes input validation tests)
- [ ] Integration tests passing (mocked Task Tracking API, verify inputs_json sent)
- [ ] Retry tests passing (simulate transient failures)
- [ ] Performance tests passing (<500ms p95 latency)
- [ ] Manual testing: Add HLS tasks with resolved inputs, verify Task Tracking API receives inputs_json
- [ ] Taskfile commands added for add_task tool tests
- [ ] Product Owner approval obtained

## Additional Information
**Suggested Labels:** mcp-tools, task-tracking, api-integration, input-validation
**Estimated Story Points:** 8 (increased from 5 due to v3 input validation)
**Dependencies:**
- **Depends On:** US-048, US-049 (Task Tracking microservice API must exist), US-071 (approve_artifact generates tasks with resolved inputs)
- **Blocks:** US-045 (generator sub-artifact evaluation depends on add_task tool)
- **Blocks:** US-047 (integration testing depends on all tools including add_task)

**Related PRD Section:** PRD-006 §Functional Requirements - FR-24, FR-25

## Decisions Made

**Decision 1: Infer artifact_type from artifact_id (remove explicit parameter)**
- **Made:** During v2 refinement (feedback from US-040-047_v2_comments.md)
- **Rationale:** Artifact type is fully deterministic from artifact_id prefix. Explicit parameter creates opportunity for client errors (mismatched artifact_id/artifact_type). Inference ensures consistency
- **Impact:**
  - Removed `artifact_type` field from TaskMetadata input
  - Added Pydantic validator to infer artifact_type from artifact_id
  - Prefix mapping: HLS-006 → HLS → hls
  - Simpler client interface (one less parameter to provide)
  - Eliminates mismatched artifact_id/artifact_type errors

**Decision 2: Infer generator from artifact_type (remove explicit parameter)**
- **Made:** During v2 refinement (feedback from US-040-047_v2_comments.md)
- **Rationale:** Generator name follows strict convention: `{artifact_type.replace('_', '-')}-generator`. Explicit parameter creates opportunity for client errors (mismatched generator/artifact_type). Construction ensures consistency
- **Impact:**
  - Removed `generator` field from TaskMetadata input (v2)
  - Added Pydantic validator to construct generator from artifact_type (v2)
  - **REVERTED in v3:** Generator now explicit field (not inferred) because approve_artifact needs explicit control
  - Convention: hls → hls-generator, backlog_story → backlog-story-generator

**Decision 3: Rename request_id → task_id (mandatory parameter)**
- **Made:** During v2 refinement (feedback from US-040-047_v2_comments.md)
- **Rationale:** "task_id" provides better visibility and traceability in logs. Naming aligns with task tracking system terminology. Mandatory parameter ensures all tool invocations are correlated
- **Impact:**
  - Parameter renamed: `request_id: str = None` → `task_id: str` (mandatory)
  - All logging updated to use `task_id` field
  - Function signature change across all tool calls
  - Better log correlation with task tracking microservice

**Decision 4: Add TaskMetadata.inputs field with RESOLVED generator inputs (v2 → v3 major schema change)**
- **Made:** During v3 planning (feedback from new_work_feedback.md, 2025-10-20)
- **Rationale:** Tasks must be self-contained with ALL generator inputs pre-resolved. Eliminates runtime path resolution errors. Enables validation at task creation time (all mandatory inputs present, files exist, inputs approved). Provides audit trail of input artifacts at task creation
- **Impact:**
  - **MAJOR SCHEMA CHANGE:** Removed simple `parent_id` field
  - **ADDED:** `inputs: List[GeneratorInput]` field with full resolution:
    - name: str (input name from generator config)
    - classification: str ("mandatory", "recommended", "conditional")
    - artifact_type: str (artifact type)
    - artifact_id: str (full artifact ID or "N/A")
    - resource_path: str (resolved file path)
    - mcp_resource_uri: str (MCP resource URI: file:///workspace/...)
    - status: str (artifact status: "Approved", "Finalized")
  - **ADDED:** 5 new validators:
    - validate_inputs_non_empty
    - validate_mandatory_inputs_present
    - validate_resource_uris_format
    - validate_resource_paths_exist
    - validate_artifact_inputs_approved
  - **ADDED:** no_duplicate_artifact_ids validator in AddTaskInput
  - **BREAKING CHANGE:** Clients must provide resolved inputs list instead of simple parent_id
  - **BENEFIT:** Task creation fails early if inputs invalid (before execution)
  - **BENEFIT:** Generators don't need runtime path resolution (all paths in task metadata)
  - **BENEFIT:** Audit trail: task contains snapshot of input artifacts at creation time
  - **DATABASE CHANGE:** tasks table needs `inputs_json JSONB` column

**Decision 5: Make generator explicit field in v3 (revert v2 inference)**
- **Made:** During v3 planning (feedback from new_work_feedback.md, 2025-10-20)
- **Rationale:** approve_artifact tool constructs tasks and needs explicit control over generator field. Inference was convenient for simple parent_id approach but doesn't fit approve_artifact workflow where generator is determined during sub-artifact detection
- **Impact:**
  - Generator is now explicit required field in TaskMetadata (not inferred)
  - approve_artifact specifies generator when constructing task
  - Simpler validation logic (no inference needed)

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md` (§2.1 Python Type Safety, §2.2 FastAPI, §5.3 Input Validation, §6.1 Structured Logging)
- **Related Stories:** US-040 (validate_artifact tool - similar validation pattern), US-071 (approve_artifact - generates tasks with resolved inputs), US-072 (documents input validation requirements)
- **Feedback:** `/feedback/US-040-047_v2_comments.md` (v2 changes), `/feedback/new_work_feedback.md` (v3 schema change)
- **Sequence Diagram:** `/docs/mcp_tools_sequence_diagram_v3.md` (shows add_task with inputs_json workflow)
