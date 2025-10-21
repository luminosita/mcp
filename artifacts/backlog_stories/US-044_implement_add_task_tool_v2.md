# User Story: Implement add_task Tool

## Metadata
- **Story ID:** US-044
- **Title:** Implement add_task Tool
- **Type:** Feature
- **Status:** Draft
- **Priority:** Must-have (enables automatic sub-artifact workflow initiation, critical for FR-24 and FR-25)
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
As Claude Code, I want a tool to automatically add tasks to the queue after generating artifacts, so that sub-artifact workflows initiate without manual TODO.md updates.

## Description
Currently, after generating an artifact (e.g., PRD-006), Claude Code requires manual TODO.md updates to add tasks for sub-artifacts (e.g., "Generate HLS-006 from PRD-006"). This creates:
1. **Manual Overhead:** Human must update TODO.md after every artifact generation
2. **Forgetting Risk:** Sub-artifacts may be forgotten if not immediately documented
3. **Workflow Fragmentation:** No programmatic linkage between artifact generation and task creation

This story implements a deterministic Python tool (`add_task`) that:
1. Accepts task list with artifact IDs, parent IDs, and status
2. Infers artifact type from artifact ID prefix (HLS-006 → hls)
3. Constructs generator name from artifact type (hls → hls-generator)
4. Validates task metadata against schema (artifact ID format, status allowed)
5. Calls Task Tracking microservice REST API (`POST /tasks/batch`) to add tasks to queue
6. Returns confirmation with task IDs added
7. Enables generators to automatically trigger sub-artifact workflows:
   - PRD generator finishes → calls `add_task` to create HLS generation tasks
   - HLS generator finishes → calls `add_task` to create Backlog Story generation tasks
   - Epic generator finishes → calls `add_task` to create PRD generation tasks (if required)

The tool eliminates manual TODO.md updates for sub-artifact workflows, reducing human overhead and ensuring complete artifact decomposition.

## Implementation Research References

**Primary Research Document:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

**Technical Patterns Applied:**
- **§2.1: Python 3.11+ with Type Safety:** Use Pydantic models for task metadata validation with full type hints (ref: Implementation Research §2.1 - Programming Language: Python 3.11+)
- **§2.2: FastAPI Integration:** Expose add_task tool as MCP tool via FastAPI with auto-generated OpenAPI documentation (ref: Implementation Research §2.2 - Backend Framework: FastAPI 0.100+)
- **§5.3: Input Validation:** Validate task metadata (artifact ID format, status values) with Pydantic (ref: Implementation Research §5.3 - Input Validation and Command Injection Prevention)
- **§6.1: Structured Logging:** Log task addition events with task count, artifact IDs, generator names (ref: Implementation Research §6.1 - Structured Logging)

**Anti-Patterns Avoided:**
- **§8.1: Poor Error Handling:** Return structured error responses for API failures with retryable flag (ref: Implementation Research §8.1 - Pitfall 3)
- **§8.2: Synchronous Blocking Calls in Async Context:** Use async HTTP client (httpx) for Task Tracking API calls (ref: Implementation Research §8.2 - Anti-Pattern 1)

**Performance Considerations:**
- **§2.4: Caching Layer:** Not applicable for task addition (write-heavy, no cache benefit)

## Functional Requirements
1. Tool accepts two parameters:
   - `tasks` (list): List of task metadata dictionaries, each including:
     - `artifact_id`: Full artifact ID (e.g., "HLS-006", "US-040")
     - `parent_id`: Parent artifact ID (e.g., "PRD-006" for HLS-006)
     - `status`: Task status (default: "pending")
     - `description`: Optional task description (auto-generated if not provided: "Generate {artifact_id} from {parent_id}")
   - `task_id` (string, mandatory): Task tracking ID for log correlation
2. Tool infers artifact type from artifact_id prefix:
   - HLS-006 → hls
   - US-040 → backlog_story
   - EPIC-006 → epic
   - (Same prefix mapping as validate_artifact tool)
3. Tool constructs generator name from artifact type:
   - hls → hls-generator
   - backlog_story → backlog-story-generator
   - epic → epic-generator
   - (Convention: {artifact_type with underscores replaced by hyphens}-generator)
4. Tool validates task metadata against schema:
   - Artifact ID format matches pattern for type (e.g., `HLS-\d{3}` for hls)
   - Status is allowed value (pending, in_progress, completed)
   - Parent ID format valid (if provided)
5. Tool calls Task Tracking microservice REST API:
   - Endpoint: `POST /tasks/batch`
   - Request body: `{"project_id": "ai-agent-mcp-server", "tasks": [...]}`
   - Authentication: API key or JWT token (configured in settings)
6. Tool returns structured JSON response:
   ```json
   {
     "success": true,
     "tasks_added": 6,
     "task_ids": ["TASK-051", "TASK-052", "TASK-053", "TASK-054", "TASK-055", "TASK-056"],
     "artifact_ids": ["HLS-006", "HLS-007", "HLS-008", "HLS-009", "HLS-010", "HLS-011"]
   }
   ```
7. Tool execution completes in <500ms p95 (per PRD-006 NFR-Performance-02)
8. Tool logs task addition invocations with timestamp, task_id, task count, artifact IDs, generator names, duration
9. Tool handles API errors gracefully:
   - Connection errors → retry 3 times with exponential backoff (100ms, 200ms, 400ms)
   - Authentication errors → fail immediately with clear error message
   - Validation errors → fail immediately with validation details

## Non-Functional Requirements
- **Performance:** Task addition latency <500ms p95 (per NFR-Performance-02)
- **Reliability:** Retry transient failures (connection errors), fail fast on permanent failures (auth errors)
- **Security:** API authentication required (API key or JWT token from environment variable)
- **Observability:** Structured logging captures task addition patterns for workflow analysis
- **Maintainability:** Clear separation between metadata validation, API calls, and retry logic

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

1. **Pydantic Models for Tool Input/Output:**
   ```python
   from pydantic import BaseModel, Field, validator
   from typing import List, Literal

   class TaskMetadata(BaseModel):
       """Task metadata schema"""
       artifact_id: str = Field(..., pattern=r'^[A-Z]+-\d{3,}$')  # e.g., HLS-006, US-040
       parent_id: str = Field(..., pattern=r'^[A-Z]+-\d{3,}$')
       status: Literal["pending", "in_progress", "completed"] = "pending"
       description: str = ""

       # Inferred fields (not provided by client)
       artifact_type: str = None
       generator: str = None

       @validator('description', pre=True, always=True)
       def auto_generate_description(cls, v, values):
           """Auto-generates description if not provided"""
           if not v and 'artifact_id' in values and 'parent_id' in values:
               return f"Generate {values['artifact_id']} from {values['parent_id']}"
           return v

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

       @validator('generator', pre=True, always=True)
       def infer_generator(cls, v, values):
           """Constructs generator name from artifact_type"""
           if v is None and 'artifact_type' in values:
               artifact_type = values['artifact_type']
               # Convention: artifact_type with underscores → hyphens + "-generator"
               generator_name = artifact_type.replace('_', '-') + '-generator'
               return generator_name
           return v

       @validator('artifact_id')
       def validate_id_type_match(cls, v, values):
           """Validates artifact ID prefix matches inferred artifact type"""
           if 'artifact_type' in values and values['artifact_type']:
               prefix = v.split('-')[0]
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
               expected_prefix = type_prefix_map.get(values['artifact_type'])
               if expected_prefix and not v.startswith(expected_prefix):
                   raise ValueError(
                       f"Artifact ID '{v}' does not match type '{values['artifact_type']}' "
                       f"(expected prefix: {expected_prefix})"
                   )
           return v

   class AddTaskInput(BaseModel):
       """Input schema for add_task tool"""
       tasks: List[TaskMetadata] = Field(..., min_items=1, max_items=100)
       task_id: str = Field(..., description="Task tracking ID for log correlation")

   class AddTaskResult(BaseModel):
       """Task addition result"""
       success: bool
       tasks_added: int
       task_ids: List[str]  # e.g., ["TASK-051", "TASK-052", ...]
       artifact_ids: List[str]  # e.g., ["HLS-006", "HLS-007", ...]
   ```

2. **Task Tracking API Client:**
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
           # Prepare request payload
           payload = {
               "project_id": self.project_id,
               "tasks": [
                   {
                       "artifact_id": task.artifact_id,
                       "artifact_type": task.artifact_type,  # Inferred
                       "generator": task.generator,  # Inferred
                       "parent_id": task.parent_id,
                       "status": task.status,
                       "description": task.description,
                       "inputs": [task.parent_id],
                       "expected_outputs": [task.artifact_id]
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

3. **MCP Tool Implementation:**
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
       Adds new tasks to task queue after artifact generation.

       Use this tool when:
       - You have generated an artifact that requires sub-artifacts (e.g., PRD → HLS)
       - You want to automatically trigger sub-artifact generation workflows
       - You need to populate task queue without manual TODO.md updates

       Input:
       - tasks: List of task metadata with artifact_id and parent_id
       - task_id: Task tracking ID for log correlation

       Tool automatically infers:
       - artifact_type from artifact_id prefix (HLS-006 → hls)
       - generator from artifact_type (hls → hls-generator)

       Integrates with Task Tracking microservice to add tasks via REST API.

       Reduces manual overhead for sub-artifact workflow initiation.
       """
   )
   async def add_task(params: AddTaskInput) -> AddTaskResult:
       """Adds tasks to task tracking queue"""
       start_time = time.time()

       try:
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
               duration_ms=duration_ms
           )

           return AddTaskResult(
               success=True,
               tasks_added=len(params.tasks),
               task_ids=task_ids,
               artifact_ids=artifact_ids
           )

       except ValueError as e:
           # Validation error from API or inference
           logger.error("task_addition_validation_error", task_id=params.task_id, error=str(e))
           raise HTTPException(status_code=400, detail=str(e))
       except PermissionError as e:
           # Auth error from API
           logger.error("task_addition_auth_error", task_id=params.task_id, error=str(e))
           raise HTTPException(status_code=401, detail=str(e))
       except Exception as e:
           # Server error or network error
           logger.error("task_addition_error", task_id=params.task_id, error=str(e))
           raise HTTPException(status_code=500, detail="Task addition failed due to internal error")
   ```

4. **Testing Strategy:**
   - Unit tests: Validate task metadata schema, auto-description generation, artifact type inference
   - Unit tests: Validate generator name construction from artifact type
   - Integration tests: Mock Task Tracking API, verify correct API calls with inferred fields
   - Retry tests: Simulate transient failures, verify exponential backoff retry logic
   - Error handling tests: Test validation errors, auth errors, server errors
   - Performance tests: Verify <500ms p95 latency with various task batch sizes

### Technical Tasks
- [ ] Implement Pydantic models for tool input/output and task metadata
- [ ] Implement artifact type inference validator in TaskMetadata
- [ ] Implement generator name construction validator in TaskMetadata
- [ ] Implement TaskTrackingClient class with retry logic
- [ ] Implement MCP tool endpoint with FastMCP decorator
- [ ] Add structured logging for task addition invocations (with task_id)
- [ ] Add retry logic with exponential backoff (3 retries: 100ms, 200ms, 400ms)
- [ ] Add error handling for validation, auth, and server errors
- [ ] Write unit tests for TaskMetadata inference validators (80% coverage)
- [ ] Write integration tests with mocked Task Tracking API
- [ ] Write retry tests (simulate transient failures)
- [ ] Write performance tests (<500ms p95 latency)
- [ ] Add Taskfile commands for running add_task tool tests

## Acceptance Criteria

### Scenario 1: HLS tasks added after PRD generation with inference
**Given** PRD generator finishes generating PRD-006
**And** PRD requires 6 HLS decompositions (HLS-006 through HLS-011)
**When** PRD generator calls `add_task(tasks=[{artifact_id: "HLS-006", parent_id: "PRD-006"}, ...], task_id="task-123")`
**Then** tool infers artifact_type="hls" from "HLS" prefix
**And** tool constructs generator="hls-generator"
**And** tool validates task metadata (passes)
**And** tool calls Task Tracking API `POST /tasks/batch` with inferred fields
**And** returns `{success: true, tasks_added: 6, task_ids: ["TASK-051", ...], artifact_ids: ["HLS-006", ...]}`
**And** execution completes in <500ms

### Scenario 2: Auto-generated task descriptions
**Given** Tasks provided without description field
**When** Claude Code calls `add_task(tasks=[{artifact_id: "HLS-006", parent_id: "PRD-006"}], task_id="task-123")`
**Then** tool auto-generates description: "Generate HLS-006 from PRD-006"
**And** description included in API request payload

### Scenario 3: Artifact type inference from various prefixes
**Given** Tasks with different artifact types
**When** Claude Code calls `add_task` with tasks:
  - {artifact_id: "HLS-006", parent_id: "PRD-006"}
  - {artifact_id: "US-040", parent_id: "HLS-006"}
  - {artifact_id: "EPIC-007", parent_id: "INIT-001"}
**Then** tool infers artifact types correctly:
  - HLS-006 → hls → hls-generator
  - US-040 → backlog_story → backlog-story-generator
  - EPIC-007 → epic → epic-generator
**And** API payload includes correct artifact_type and generator fields

### Scenario 4: Invalid artifact ID prefix rejected
**Given** Task has unknown artifact ID prefix
**When** Claude Code calls `add_task(tasks=[{artifact_id: "INVALID-006", parent_id: "PRD-006"}], task_id="task-123")`
**Then** tool returns validation error: "Unknown artifact ID prefix: INVALID. Valid prefixes: EPIC, PRD, HLS, US, SPEC, ADR, SPIKE, TASK, VIS, INIT"
**And** no API call made
**And** error logged with task_id for debugging

### Scenario 5: API auth error handled gracefully
**Given** Task Tracking API key is invalid
**When** Claude Code calls `add_task(tasks=[...], task_id="task-123")`
**Then** tool calls Task Tracking API
**And** API returns 401 Unauthorized
**And** tool returns 401 error with message: "Task Tracking API authentication failed"
**And** no retry attempts (auth errors are permanent, not transient)

### Scenario 6: Transient API failure retried with exponential backoff
**Given** Task Tracking API temporarily unavailable (503 error)
**When** Claude Code calls `add_task(tasks=[...], task_id="task-123")`
**Then** tool calls API, receives 503 error
**And** tool retries after 100ms → still fails
**And** tool retries after 200ms → still fails
**And** tool retries after 400ms → succeeds
**And** returns success result
**And** total duration ~700ms (within <500ms p95 target for most requests)

### Scenario 7: Task addition execution logged with task_id
**Given** Claude Code calls add_task tool
**When** Task addition completes
**Then** tool logs structured event with fields: task_id, tasks_added, artifact_ids, generators, task_ids, duration_ms
**And** log format is JSON (structured logging)
**And** log includes task_id for correlation with other tool calls

### Scenario 8: Batch task addition (6 HLS from PRD) with inference
**Given** PRD generator completes
**When** Generator calls `add_task` with 6 HLS tasks (only artifact_id and parent_id provided)
**Then** Tool infers artifact_type and generator for all 6 tasks
**And** All 6 tasks added in single API call (batch operation)
**And** Task Tracking microservice receives 6 tasks with complete metadata
**And** Next `get_next_task` call returns first pending HLS generation task

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Not Needed (Single Sprint-Ready Task)

**Rationale:**
- **Story Points:** 5 SP (at threshold - CONSIDER SKIPPING per decision matrix)
- **Developer Count:** Single developer (straightforward API client with inference validators)
- **Domain Span:** Single domain (HTTP API integration with Pydantic validation)
- **Complexity:** Low-moderate - well-defined REST API integration with standard inference pattern
- **Uncertainty:** Low - clear API contract (Task Tracking microservice spec from PRD-006), inference logic similar to validate_artifact
- **Override Factors:** None (inference validators are standard Pydantic pattern, not complex)

Per SDLC Section 11.6 Decision Matrix: "5 SP, single developer, low-moderate complexity → SKIP (Standard API integration with inference)".

**No task decomposition needed.** Story can be completed as single unit of work in 2-3 days.

## Definition of Done
- [ ] Pydantic models implemented for tool input/output and task metadata
- [ ] Artifact type inference validator implemented in TaskMetadata
- [ ] Generator name construction validator implemented in TaskMetadata
- [ ] TaskTrackingClient class with retry logic
- [ ] MCP tool endpoint implemented with FastMCP
- [ ] Structured logging for task addition invocations (with task_id)
- [ ] Retry logic with exponential backoff (3 retries)
- [ ] Error handling for validation, auth, and server errors
- [ ] Unit tests written and passing (80% coverage, includes inference tests)
- [ ] Integration tests passing (mocked Task Tracking API)
- [ ] Retry tests passing (simulate transient failures)
- [ ] Performance tests passing (<500ms p95 latency)
- [ ] Manual testing: Add HLS tasks with inference, verify Task Tracking API receives complete metadata
- [ ] Taskfile commands added for add_task tool tests
- [ ] Product Owner approval obtained

## Additional Information
**Suggested Labels:** mcp-tools, task-tracking, api-integration
**Estimated Story Points:** 5
**Dependencies:**
- **Depends On:** US-048, US-049 (Task Tracking microservice API must exist)
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
  - Removed `generator` field from TaskMetadata input
  - Added Pydantic validator to construct generator from artifact_type
  - Convention: hls → hls-generator, backlog_story → backlog-story-generator
  - Simpler client interface (two fewer parameters total)
  - Eliminates mismatched generator/artifact_type errors

**Decision 3: Rename request_id → task_id (mandatory parameter)**
- **Made:** During v2 refinement (feedback from US-040-047_v2_comments.md)
- **Rationale:** "task_id" provides better visibility and traceability in logs. Naming aligns with task tracking system terminology. Mandatory parameter ensures all tool invocations are correlated
- **Impact:**
  - Parameter renamed: `request_id: str = None` → `task_id: str` (mandatory)
  - All logging updated to use `task_id` field
  - Function signature change across all tool calls
  - Better log correlation with task tracking microservice

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md` (§2.1 Python Type Safety, §2.2 FastAPI, §5.3 Input Validation, §6.1 Structured Logging)
- **Related Stories:** US-040 (validate_artifact tool - similar inference pattern), US-042 (resolve_artifact_path tool), US-045 (generator sub-artifact evaluation)
- **Feedback:** `/feedback/US-040-047_v2_comments.md`
- **Changes Applied:** `/feedback/US-040-047_v2_changes_applied.md`
