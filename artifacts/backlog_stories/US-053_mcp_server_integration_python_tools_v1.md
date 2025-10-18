# User Story: MCP Server Integration (Python MCP Tools)

## Metadata
- **Story ID:** US-053
- **Title:** MCP Server Integration (Python MCP Tools)
- **Type:** Feature
- **Status:** Backlog
- **Priority:** High - Bridges MCP Server to Task Tracking microservice (enables end-to-end workflow)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-009
- **Functional Requirements Covered:** FR-08, FR-09, FR-10, FR-11, FR-24
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration v3]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Technical Considerations - Architecture - MCP Tools Layer (Python)
- **Functional Requirements Coverage:**
  - **FR-08:** get_next_task tool (MCP tool calls Task Tracking microservice REST API)
  - **FR-09:** update_task_status tool (MCP tool calls Task Tracking microservice REST API)
  - **FR-10:** get_next_available_id tool (MCP tool calls Task Tracking microservice REST API)
  - **FR-11:** reserve_id_range tool (MCP tool calls Task Tracking microservice REST API)
  - **FR-24:** add_task tool (MCP tool calls Task Tracking microservice REST API)

**Parent High-Level Story:** [HLS-009: Task Tracking Microservice]
- **Link:** `/artifacts/hls/HLS-009_task_tracking_microservice_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 6: MCP Server Integration (Python MCP Tools)

## User Story
As an MCP Server developer, I want Python MCP tools (get_next_task, update_task_status, get_next_available_id, reserve_id_range, add_task) that call the Task Tracking microservice REST API, so that Claude Code can interact with task tracking and ID management through the MCP protocol instead of local TODO.md files.

## Description
The MCP Server exposes tools for task tracking and ID management to Claude Code. These tools act as a bridge between the MCP protocol (Python) and the Task Tracking microservice (Go + PostgreSQL). This story implements 5 MCP tools as Python functions that make HTTP requests to the Task Tracking microservice REST API, handle authentication (API key), parse JSON responses, and return structured data to Claude Code.

Each tool maps directly to a REST API endpoint implemented in US-050/US-051, providing a clean integration layer that abstracts HTTP details from Claude Code's perspective (Claude Code calls tools, not raw HTTP APIs).

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **HTTP Client Pattern:** Python `requests` library for HTTP client functionality
  - **Connection Pooling:** Session object reuses TCP connections across multiple requests
  - **Timeout Configuration:** Set timeout (5 seconds default) to prevent hanging on unresponsive microservice
  - **Error Handling:** Distinguish network errors (ConnectionError) vs. HTTP errors (4xx/5xx status codes)
- **MCP Tool Decorator:** FastMCP `@mcp.tool()` decorator registers functions as callable tools
  - **Input Validation:** Pydantic models validate tool parameters before execution
  - **Output Serialization:** Return Python dict/list, MCP SDK handles JSON serialization
- **Configuration Management:** Microservice URL and API key from environment variables
  - **Environment Variables:** TASK_TRACKING_URL (default: http://localhost:8080), TASK_TRACKING_API_KEY

**Anti-Patterns Avoided:**
- **Avoid Hardcoded URLs:** Load microservice URL from environment variable (supports local dev, staging, production)
- **Avoid Plaintext API Keys in Logs:** Do not log API key (log request URL and status code only)
- **Avoid Swallowing Errors:** Propagate errors to Claude Code with clear error messages (e.g., "Task Tracking microservice unavailable: Connection refused")

**Performance Considerations:**
- **Session Reuse:** Create single `requests.Session` object shared across all tool calls (connection pooling)
- **Timeout:** 5-second timeout prevents hanging on slow/dead microservice
- **Retry Logic:** Implement basic retry (3 attempts) for transient network errors (per NFR-Reliability-01)

## Functional Requirements
- MCP tool: `get_next_task(project_id: str, status_filter: str = "pending")` → Returns next task object or None
- MCP tool: `update_task_status(task_id: str, status: str, completion_notes: str = "")` → Returns updated task object
- MCP tool: `get_next_available_id(artifact_type: str, project_id: str)` → Returns next ID string (e.g., "US-028")
- MCP tool: `reserve_id_range(artifact_type: str, count: int, project_id: str)` → Returns reservation object with reserved_ids array
- MCP tool: `add_task(tasks: list[dict])` → Returns success status and task_ids array
- Configuration: Load TASK_TRACKING_URL and TASK_TRACKING_API_KEY from environment variables
- HTTP client: Use `requests.Session` with connection pooling and 5-second timeout
- Authentication: Include `Authorization: Bearer <API_KEY>` header on all requests
- Error handling: Catch HTTP errors (4xx/5xx) and network errors (ConnectionError, Timeout), return clear error message to Claude Code
- Retry logic: Retry transient errors 3 times with exponential backoff (100ms, 200ms, 400ms)

## Non-Functional Requirements
- **Performance:** Tool execution latency <500ms (p95) for all tools (per NFR-Performance-02) - includes HTTP round-trip to microservice
- **Reliability:** Retry transient network errors 3 times with exponential backoff (per NFR-Reliability-01)
- **Observability:** Log all tool invocations with timestamp, tool name, parameters, HTTP status code, duration
- **Maintainability:** Pydantic models for tool input validation (type safety)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story implements Python MCP tools. Reference Python implementation standards (CLAUDE-core.md, CLAUDE-tooling.md, CLAUDE-validation.md) for HTTP client patterns, Pydantic models, and error handling.

### Implementation Guidance

**MCP Tool Implementation Example:**

```python
import os
import requests
from typing import Optional
from pydantic import BaseModel, Field
from mcp import FastMCP

# Initialize MCP server
mcp = FastMCP("task-tracking-tools")

# Configuration from environment variables
TASK_TRACKING_URL = os.getenv("TASK_TRACKING_URL", "http://localhost:8080")
TASK_TRACKING_API_KEY = os.getenv("TASK_TRACKING_API_KEY")

if not TASK_TRACKING_API_KEY:
    raise ValueError("TASK_TRACKING_API_KEY environment variable not set")

# Shared HTTP session (connection pooling)
session = requests.Session()
session.headers.update({"Authorization": f"Bearer {TASK_TRACKING_API_KEY}"})
session.timeout = 5  # 5 second timeout

# Pydantic models for input validation
class GetNextTaskInput(BaseModel):
    project_id: str = Field(..., description="Project ID (e.g., 'ai-agent-mcp-server')")
    status_filter: str = Field("pending", description="Status filter (default: 'pending')")

class UpdateTaskStatusInput(BaseModel):
    task_id: str = Field(..., description="Task ID (e.g., 'TASK-051')")
    status: str = Field(..., description="New status (pending | in_progress | completed)")
    completion_notes: str = Field("", description="Completion notes (optional)")

class GetNextIDInput(BaseModel):
    artifact_type: str = Field(..., description="Artifact type (US, SPEC, TASK, etc.)")
    project_id: str = Field(..., description="Project ID")

class ReserveIDRangeInput(BaseModel):
    artifact_type: str = Field(..., description="Artifact type (US, SPEC, TASK, etc.)")
    count: int = Field(..., description="Number of IDs to reserve (1-100)")
    project_id: str = Field(..., description="Project ID")

class AddTaskInput(BaseModel):
    tasks: list[dict] = Field(..., description="Array of task objects to add")

# MCP Tools
@mcp.tool()
def get_next_task(input: GetNextTaskInput) -> Optional[dict]:
    """Get next pending task from Task Tracking microservice."""
    url = f"{TASK_TRACKING_URL}/tasks/next"
    params = {"project": input.project_id, "status": input.status_filter}

    try:
        response = session.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("task")  # Returns None if no tasks
    except requests.exceptions.ConnectionError:
        raise RuntimeError(f"Task Tracking microservice unavailable: Connection refused at {TASK_TRACKING_URL}")
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Task Tracking microservice timeout: No response within 5 seconds")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Task Tracking API error: {e.response.status_code} - {e.response.text}")

@mcp.tool()
def update_task_status(input: UpdateTaskStatusInput) -> dict:
    """Update task status in Task Tracking microservice."""
    url = f"{TASK_TRACKING_URL}/tasks/{input.task_id}/status"
    payload = {"status": input.status, "completion_notes": input.completion_notes}

    try:
        response = session.put(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("updated_task")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise RuntimeError(f"Task not found: {input.task_id}")
        elif e.response.status_code == 400:
            raise RuntimeError(f"Invalid status transition: {e.response.text}")
        else:
            raise RuntimeError(f"Task Tracking API error: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error: {str(e)}")

@mcp.tool()
def get_next_available_id(input: GetNextIDInput) -> str:
    """Get next available artifact ID from Task Tracking microservice."""
    url = f"{TASK_TRACKING_URL}/ids/next"
    params = {"type": input.artifact_type, "project": input.project_id}

    try:
        response = session.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("next_id")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"ID management API error: {str(e)}")

@mcp.tool()
def reserve_id_range(input: ReserveIDRangeInput) -> dict:
    """Reserve contiguous ID range from Task Tracking microservice."""
    url = f"{TASK_TRACKING_URL}/ids/reserve"
    payload = {"type": input.artifact_type, "count": input.count, "project_id": input.project_id}

    try:
        response = session.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return {
            "reservation_id": data.get("reservation_id"),
            "reserved_ids": data.get("reserved_ids"),
            "expires_at": data.get("expires_at"),
        }
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"ID reservation API error: {str(e)}")

@mcp.tool()
def add_task(input: AddTaskInput) -> dict:
    """Add batch of tasks to Task Tracking microservice."""
    url = f"{TASK_TRACKING_URL}/tasks/batch"
    payload = {"tasks": input.tasks}

    try:
        response = session.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return {
            "success": data.get("success"),
            "tasks_added": data.get("tasks_added"),
            "task_ids": data.get("task_ids"),
        }
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Batch task addition API error: {str(e)}")
```

**Environment Variable Configuration:**

```bash
# .env file (local development)
TASK_TRACKING_URL=http://localhost:8080
TASK_TRACKING_API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6=

# Docker Compose
services:
  mcp-server:
    environment:
      - TASK_TRACKING_URL=http://task-tracking:8080
      - TASK_TRACKING_API_KEY=${TASK_TRACKING_API_KEY}
```

**Retry Logic (Optional Enhancement):**

```python
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=0.1,  # 100ms, 200ms, 400ms
    status_forcelist=[500, 502, 503, 504],  # Retry on server errors
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)
```

**References to Implementation Standards:**
- **CLAUDE-core.md (Python):** HTTP client patterns, error handling, configuration management
- **CLAUDE-tooling.md (Python):** Environment variable loading (python-dotenv), Taskfile integration
- **CLAUDE-validation.md (Python):** Pydantic models for input validation, type safety
- **CLAUDE-testing.md (Python):** Unit testing with mocked HTTP responses (responses library or unittest.mock)

**Note:** Treat CLAUDE.md (Python) files as authoritative for HTTP client patterns and MCP tool implementation.

### Technical Tasks
- Implement `get_next_task` MCP tool with HTTP GET to /tasks/next
- Implement `update_task_status` MCP tool with HTTP PUT to /tasks/{id}/status
- Implement `get_next_available_id` MCP tool with HTTP GET to /ids/next
- Implement `reserve_id_range` MCP tool with HTTP POST to /ids/reserve
- Implement `add_task` MCP tool with HTTP POST to /tasks/batch
- Configure `requests.Session` with connection pooling and authentication header
- Load TASK_TRACKING_URL and TASK_TRACKING_API_KEY from environment variables
- Add error handling for HTTP errors (4xx/5xx) and network errors (ConnectionError, Timeout)
- Add Pydantic models for tool input validation
- Write unit tests for all 5 tools (mock HTTP responses)
- Write integration tests for tools calling real microservice (test environment)

## Acceptance Criteria

### Scenario 1: get_next_task returns pending task
**Given** Task Tracking microservice running with pending task TASK-051 for project "ai-agent-mcp-server"
**When** Claude Code calls `get_next_task(project_id="ai-agent-mcp-server", status_filter="pending")`
**Then** tool returns task object with task_id="TASK-051", description, inputs, outputs
**And** HTTP GET request sent to http://localhost:8080/tasks/next?project=ai-agent-mcp-server&status=pending
**And** Authorization header included: `Bearer <API_KEY>`

### Scenario 2: get_next_task returns None when no tasks
**Given** Task Tracking microservice running with zero pending tasks for project "ai-agent-mcp-server"
**When** Claude Code calls `get_next_task(project_id="ai-agent-mcp-server")`
**Then** tool returns None (no tasks available)

### Scenario 3: update_task_status updates task to completed
**Given** Task Tracking microservice has task TASK-051 with status "in_progress"
**When** Claude Code calls `update_task_status(task_id="TASK-051", status="completed", completion_notes="Done")`
**Then** tool returns updated task object with status="completed", completed_at timestamp
**And** HTTP PUT request sent to http://localhost:8080/tasks/TASK-051/status
**And** request body contains `{status: "completed", completion_notes: "Done"}`

### Scenario 4: get_next_available_id returns next sequential ID
**Given** Task Tracking microservice id_registry has last_assigned_id=27 for US type
**When** Claude Code calls `get_next_available_id(artifact_type="US", project_id="ai-agent-mcp-server")`
**Then** tool returns "US-028"
**And** HTTP GET request sent to http://localhost:8080/ids/next?type=US&project=ai-agent-mcp-server

### Scenario 5: reserve_id_range reserves contiguous ID range
**Given** Task Tracking microservice id_registry has last_assigned_id=27 for US type
**When** Claude Code calls `reserve_id_range(artifact_type="US", count=6, project_id="ai-agent-mcp-server")`
**Then** tool returns reservation object with reserved_ids=["US-028", "US-029", "US-030", "US-031", "US-032", "US-033"]
**And** reservation_id (UUID) and expires_at timestamp included in response

### Scenario 6: add_task adds batch of tasks
**Given** Task Tracking microservice running
**When** Claude Code calls `add_task(tasks=[{task_id: "TASK-046", project_id: "ai-agent-mcp-server", description: "Generate HLS-006", ...}, {task_id: "TASK-047", ...}])`
**Then** tool returns `{success: true, tasks_added: 2, task_ids: ["TASK-046", "TASK-047"]}`
**And** HTTP POST request sent to http://localhost:8080/tasks/batch

### Scenario 7: Handle microservice unavailable (ConnectionError)
**Given** Task Tracking microservice is stopped (not running)
**When** Claude Code calls `get_next_task(project_id="ai-agent-mcp-server")`
**Then** tool raises RuntimeError with message "Task Tracking microservice unavailable: Connection refused at http://localhost:8080"

### Scenario 8: Handle HTTP 404 error (task not found)
**Given** Task Tracking microservice running
**When** Claude Code calls `update_task_status(task_id="TASK-999", status="completed")` for non-existent task
**Then** tool raises RuntimeError with message "Task not found: TASK-999"

### Scenario 9: Handle HTTP 401 error (invalid API key)
**Given** Task Tracking microservice running
**And** TASK_TRACKING_API_KEY environment variable set to invalid key
**When** Claude Code calls any tool
**Then** tool raises RuntimeError with message "Task Tracking API error: 401 - Unauthorized"

### Scenario 10: Environment variable validation on startup
**Given** TASK_TRACKING_API_KEY environment variable not set
**When** MCP Server starts
**Then** MCP Server fails with ValueError "TASK_TRACKING_API_KEY environment variable not set" (fail-fast)

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 5 SP - CONSIDER threshold, but below 5+ SP (DON'T SKIP) threshold
- **Developer Count:** Single Python developer
- **Domain Span:** Single domain (backend integration layer - Python MCP tools calling Go REST API)
- **Complexity:** Low - 5 similar tool implementations (HTTP client pattern repeated 5 times with minor variations)
- **Uncertainty:** Low - HTTP client patterns well-established (requests library), MCP tool decorator standard
- **Override Factors:** None apply (not cross-domain, not unfamiliar tech, not security-critical beyond passing API key, not multi-system integration - just HTTP client wrapper)

**Conclusion:** Story is within single developer capacity. All 5 tools follow same HTTP client pattern (GET/POST/PUT to REST API). Pydantic models standard pattern. Task decomposition overhead not justified for repetitive implementation.

## Definition of Done
- [ ] All 5 MCP tools implemented (get_next_task, update_task_status, get_next_available_id, reserve_id_range, add_task)
- [ ] Pydantic models implemented for tool input validation
- [ ] Environment variable configuration implemented (TASK_TRACKING_URL, TASK_TRACKING_API_KEY)
- [ ] HTTP client configured with connection pooling and authentication
- [ ] Error handling implemented (HTTP errors, network errors)
- [ ] Unit tests written and passing (80% coverage minimum, mock HTTP responses)
- [ ] Integration tests passing (all 10 acceptance criteria validated, real microservice)
- [ ] Code review completed
- [ ] Documentation updated (tool usage examples, environment variable configuration)
- [ ] Product Owner acceptance obtained

## Additional Information
**Suggested Labels:** backend, python, mcp-tools, integration, http-client
**Estimated Story Points:** 5
**Dependencies:**
- US-050 completed (task tracking REST API)
- US-051 completed (ID management REST API)
- US-052 completed (API authentication)
- Task Tracking microservice running and accessible

**Related PRD Section:** PRD-006 §Technical Considerations - Architecture - MCP Tools Layer (lines 321-327)

## Open Questions & Implementation Uncertainties

**No open implementation questions. All technical approaches clear from Implementation Research and PRD.**

HTTP client patterns standard (requests library with Session). MCP tool decorator standard (FastMCP SDK). Error handling patterns standard (catch requests.exceptions, raise RuntimeError with clear message). Environment variable loading standard (os.getenv with validation).
