# User Story: Task Tracking REST API Implementation (Go)

## Metadata
- **Story ID:** US-050
- **Title:** Task Tracking REST API Implementation (Go)
- **Type:** Feature
- **Status:** Backlog
- **Priority:** High - Core microservice functionality (blocks US-053 MCP integration)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-009
- **Functional Requirements Covered:** FR-08, FR-09, FR-14, FR-18, FR-24
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration v3]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Technical Considerations - Architecture - Task Tracking Microservice REST API
- **Functional Requirements Coverage:**
  - **FR-08:** get_next_task tool (requires GET /tasks/next endpoint)
  - **FR-09:** update_task_status tool (requires PUT /tasks/{id}/status endpoint)
  - **FR-14:** Task Tracking microservice REST API endpoints specification
  - **FR-18:** Multi-project task tracking isolation (requires project_id query parameter filtering)
  - **FR-24:** add_task tool (requires POST /tasks/batch endpoint for sub-artifact workflows)

**Parent High-Level Story:** [HLS-009: Task Tracking Microservice]
- **Link:** `/artifacts/hls/HLS-009_task_tracking_microservice_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 3: Task Tracking REST API Implementation (Go)

## User Story
As an MCP Server developer, I want a Go REST API for task tracking with endpoints for retrieving next task, updating task status, querying tasks, and batch task addition, so that MCP tools can interact with the Task Tracking microservice via HTTP instead of direct database access.

## Description
The Task Tracking microservice exposes REST API endpoints for task management, enabling clean separation between MCP Server (Python) and task persistence layer (Go + PostgreSQL). This story implements four core endpoints:

1. **GET /tasks/next?project={id}&status={filter}** - Returns next pending task for specified project
2. **PUT /tasks/{id}/status** - Updates task status (pending→in_progress→completed) with validation
3. **GET /tasks?project={id}&status={filter}** - Queries tasks with filtering by project and status
4. **POST /tasks/batch** - Adds multiple tasks to queue (sub-artifact workflow support)

The API must enforce project_id filtering for multi-project isolation, validate task status transitions (prevent invalid state changes), handle database errors gracefully (return appropriate HTTP status codes), and log all API calls for observability.

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **REST API Design:** HTTP methods map to CRUD operations (GET = read, PUT = update, POST = create)
  - **Resource-Oriented URLs:** `/tasks/{id}` follows REST conventions for resource addressability
  - **Query Parameters:** `?project=X&status=Y` for filtering instead of POST body (cacheable, idempotent)
- **HTTP Status Codes:** 200 OK (success), 404 Not Found (task not exists), 400 Bad Request (validation error), 500 Internal Server Error (database error)
- **JSON Request/Response:** Standard JSON serialization for all payloads (Go encoding/json)
- **Database Connection Pooling:** pgx connection pool for efficient PostgreSQL access (reuse connections, limit concurrent queries)

**Anti-Patterns Avoided:**
- **Avoid Unvalidated Status Transitions:** Validate status changes before database update (e.g., completed→pending requires explicit reset flag)
- **Avoid Generic Error Messages:** Return specific error details (e.g., "Task TASK-051 not found" vs. "Error")
- **Avoid Unfiltered Queries:** Require project_id parameter for multi-project isolation (prevent cross-project data leakage)

**Performance Considerations:**
- **Connection Pooling:** Reuse PostgreSQL connections across requests (pgx pool with max 25 connections recommended)
- **Query Optimization:** Use prepared statements for repeated queries (GET /tasks/next, PUT /tasks/{id}/status)
- **Response Caching:** GET /tasks/next response not cached (always query database for latest pending task)

## Functional Requirements
- HTTP server listening on configurable port (default: 8080)
- Endpoint: `GET /tasks/next?project={project_id}&status={status_filter}` - Returns next task matching filter (default status=pending)
- Endpoint: `PUT /tasks/{task_id}/status` with JSON body `{status: string, completion_notes: string}` - Updates task status and completion timestamp
- Endpoint: `GET /tasks?project={project_id}&status={status_filter}` - Returns array of tasks matching filter
- Endpoint: `POST /tasks/batch` with JSON body `{tasks: [{task_id, project_id, description, generator_name, status, inputs, expected_outputs, context_notes}]}` - Adds multiple tasks in single request
- Request validation: Reject missing project_id, invalid status values, malformed JSON
- Status transition validation: Allow pending→in_progress, in_progress→completed, reject invalid transitions (e.g., completed→pending without reset flag)
- Database error handling: Return 500 Internal Server Error with error message (log full error server-side)
- Response format: JSON with consistent structure `{success: bool, data: object, error: string}`
- CORS headers: Allow cross-origin requests from MCP Server (configurable origins)

## Non-Functional Requirements
- **Performance:** API response time p99 <200ms under 100 RPS load (per NFR-Performance-04)
- **Scalability:** Support ≥100 concurrent requests without connection pool exhaustion
- **Reliability:** Database connection failures handled with retry logic (3 retries, exponential backoff per NFR-Reliability-01)
- **Observability:** Log all API requests with timestamp, endpoint, parameters, response status, duration
- **Security:** Input validation on all parameters (prevent SQL injection via prepared statements, validate project_id format)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story implements Go REST API. Reference Go implementation standards (CLAUDE-core.md, CLAUDE-tooling.md, CLAUDE-architecture.md) for HTTP framework choice, project structure, logging, and testing.

### Implementation Guidance

**HTTP Router Choice:**
- Deferred to implementation: chi, gin, or gorilla/mux
- Requirements: Path parameters support (`/tasks/{id}`), query parameters, JSON middleware
- Recommendation: chi (lightweight, stdlib-compatible) or gin (full-featured, fast)

**API Endpoints Specification:**

**1. GET /tasks/next**
- Query Parameters:
  - `project` (required): Project ID (e.g., "ai-agent-mcp-server")
  - `status` (optional): Status filter (default: "pending")
- Response 200 OK:
  ```json
  {
    "success": true,
    "task": {
      "task_id": "TASK-051",
      "project_id": "ai-agent-mcp-server",
      "description": "Generate PRD-006",
      "generator_name": "prd-generator",
      "status": "pending",
      "inputs": ["EPIC-006"],
      "expected_outputs": ["PRD-006"],
      "context_notes": "New session CX required",
      "created_at": "2025-10-18T10:00:00Z"
    }
  }
  ```
- Response 200 OK (no tasks):
  ```json
  {
    "success": true,
    "task": null,
    "message": "No pending tasks for project"
  }
  ```
- Response 400 Bad Request: Missing project parameter

**2. PUT /tasks/{task_id}/status**
- Path Parameter: `task_id` (e.g., "TASK-051")
- Request Body:
  ```json
  {
    "status": "completed",
    "completion_notes": "PRD-006 v1 generated, 26/26 validation passed"
  }
  ```
- Response 200 OK:
  ```json
  {
    "success": true,
    "updated_task": {
      "task_id": "TASK-051",
      "status": "completed",
      "completed_at": "2025-10-18T11:00:00Z",
      "completion_notes": "PRD-006 v1 generated, 26/26 validation passed"
    }
  }
  ```
- Response 404 Not Found: Task not found
- Response 400 Bad Request: Invalid status transition

**3. GET /tasks**
- Query Parameters:
  - `project` (required): Project ID
  - `status` (optional): Status filter
- Response 200 OK:
  ```json
  {
    "success": true,
    "tasks": [
      {
        "task_id": "TASK-050",
        "project_id": "ai-agent-mcp-server",
        "description": "Generate EPIC-006",
        "status": "completed",
        "completed_at": "2025-10-16T15:00:00Z"
      },
      {
        "task_id": "TASK-051",
        "project_id": "ai-agent-mcp-server",
        "description": "Generate PRD-006",
        "status": "in_progress"
      }
    ],
    "count": 2
  }
  ```

**4. POST /tasks/batch**
- Request Body:
  ```json
  {
    "tasks": [
      {
        "task_id": "TASK-046",
        "project_id": "ai-agent-mcp-server",
        "description": "Generate HLS-006",
        "generator_name": "hls-generator",
        "status": "pending",
        "inputs": ["PRD-006"],
        "expected_outputs": ["HLS-006"],
        "context_notes": ""
      },
      {
        "task_id": "TASK-047",
        "project_id": "ai-agent-mcp-server",
        "description": "Generate HLS-007",
        "generator_name": "hls-generator",
        "status": "pending",
        "inputs": ["PRD-006"],
        "expected_outputs": ["HLS-007"],
        "context_notes": ""
      }
    ]
  }
  ```
- Response 200 OK:
  ```json
  {
    "success": true,
    "tasks_added": 2,
    "task_ids": ["TASK-046", "TASK-047"]
  }
  ```
- Response 400 Bad Request: Validation error (missing required fields, invalid task_id format)

**Database Access:**
- Use pgx library for PostgreSQL access (connection pooling, prepared statements)
- Connection pool configuration: max 25 connections, idle timeout 5 minutes
- Prepared statements for repeated queries (GET /tasks/next, PUT /tasks/{id}/status)

**Error Handling:**
- Distinguish database errors (500) vs. validation errors (400) vs. not found (404)
- Log full error stack trace server-side, return sanitized error message to client
- Retry database connection failures (3 attempts, exponential backoff: 100ms, 200ms, 400ms)

**Logging:**
- Structured logging (JSON format): `{"timestamp": "...", "method": "GET", "path": "/tasks/next", "params": {...}, "status": 200, "duration_ms": 45}`
- Log level: INFO for successful requests, ERROR for 500 responses, WARN for 400 responses

**References to Implementation Standards:**
- **CLAUDE-core.md (Go):** Core development philosophy, error handling patterns
- **CLAUDE-tooling.md (Go):** HTTP framework selection, logging library, Taskfile integration (`task api-run`, `task api-test`)
- **CLAUDE-architecture.md (Go):** Project structure (cmd/api/main.go, internal/handlers/, internal/db/, internal/models/)
- **CLAUDE-validation.md (Go):** Input validation patterns (validate task_id format, validate status enum)

**Note:** Treat CLAUDE.md (Go) files as authoritative for framework choices and code organization.

### Technical Tasks
- Set up Go HTTP server with router (chi, gin, or gorilla/mux)
- Implement GET /tasks/next endpoint with database query
- Implement PUT /tasks/{id}/status endpoint with status transition validation
- Implement GET /tasks endpoint with filtering
- Implement POST /tasks/batch endpoint for bulk task addition
- Configure pgx connection pool for PostgreSQL access
- Add request validation middleware (validate JSON, required parameters)
- Add structured logging for all API calls
- Add error handling with appropriate HTTP status codes
- Write unit tests for endpoint handlers (mock database)
- Write integration tests for full API workflow (test database)

## Acceptance Criteria

### Scenario 1: Retrieve next pending task
**Given** tasks table contains pending task TASK-051 for project "ai-agent-mcp-server"
**When** client sends GET /tasks/next?project=ai-agent-mcp-server&status=pending
**Then** API returns 200 OK with task details in JSON response
**And** response includes task_id, description, inputs, expected_outputs
**And** response completes in <100ms (p95)

### Scenario 2: No pending tasks available
**Given** tasks table has zero pending tasks for project "ai-agent-mcp-server"
**When** client sends GET /tasks/next?project=ai-agent-mcp-server&status=pending
**Then** API returns 200 OK with null task and message "No pending tasks for project"

### Scenario 3: Update task status to completed
**Given** task TASK-051 exists with status "in_progress"
**When** client sends PUT /tasks/TASK-051/status with body `{status: "completed", completion_notes: "Done"}`
**Then** API returns 200 OK with updated task details
**And** database record updated with status = "completed", completed_at = current timestamp, completion_notes = "Done"
**And** response completes in <100ms (p95)

### Scenario 4: Reject invalid status transition
**Given** task TASK-051 exists with status "completed"
**When** client sends PUT /tasks/TASK-051/status with body `{status: "pending"}`
**Then** API returns 400 Bad Request with error message "Invalid status transition: completed → pending"
**And** database record remains unchanged

### Scenario 5: Query tasks by project and status
**Given** tasks table contains 3 completed tasks and 2 pending tasks for project "ai-agent-mcp-server"
**When** client sends GET /tasks?project=ai-agent-mcp-server&status=completed
**Then** API returns 200 OK with array of 3 completed tasks
**And** response includes count field = 3

### Scenario 6: Batch task addition (sub-artifact workflow)
**Given** tasks table is empty
**When** client sends POST /tasks/batch with array of 6 tasks (HLS-006 through HLS-011)
**Then** API returns 200 OK with tasks_added = 6 and task_ids array
**And** database contains 6 new rows with status = "pending"
**And** all tasks have correct project_id, generator_name, inputs, outputs

### Scenario 7: Multi-project isolation enforced
**Given** tasks table contains tasks for project-alpha and project-beta
**When** client sends GET /tasks/next?project=project-alpha
**Then** API returns only project-alpha task (no project-beta tasks in response)

### Scenario 8: Handle missing project parameter
**Given** API is running
**When** client sends GET /tasks/next without project query parameter
**Then** API returns 400 Bad Request with error message "Missing required parameter: project"

### Scenario 9: Handle database connection failure
**Given** PostgreSQL database is unavailable
**When** client sends GET /tasks/next?project=ai-agent-mcp-server
**Then** API retries connection 3 times with exponential backoff
**And** if all retries fail, API returns 500 Internal Server Error with message "Database unavailable"
**And** error logged server-side with full stack trace

### Scenario 10: Performance under load
**Given** API is running with tasks table populated (100 tasks)
**When** client sends 100 concurrent GET /tasks/next requests
**Then** p99 response time <200ms (per NFR-Performance-04)
**And** all requests return valid responses (no connection pool exhaustion)

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Needed

**Rationale:**
- **Story Points:** 8 SP - EXCEEDS 5+ SP threshold (DON'T SKIP per SDLC Section 11.6)
- **Developer Count:** Single backend developer, but significant complexity
- **Domain Span:** Single domain (backend only), but multiple concerns (HTTP routing, database access, validation, error handling, testing)
- **Complexity:** High - 4 endpoints with different patterns, database integration, connection pooling, retry logic, status validation
- **Uncertainty:** Low - clear API design from PRD, but implementation has multiple sub-components
- **Override Factors:** None apply (not cross-domain, not unfamiliar tech, not security-critical, not multi-system integration)

**Conclusion:** Story exceeds 5 SP threshold. Complexity warrants decomposition into focused tasks (4-8 hours each) for better tracking and parallel work if needed.

**Proposed Implementation Tasks:**
- **TASK-XXX:** Set up Go HTTP server with router and middleware (4-6 hours)
  - Brief: Initialize Go project, add HTTP framework (chi/gin), configure router, add logging middleware, add request validation middleware
- **TASK-XXX:** Implement GET /tasks/next and GET /tasks endpoints (4-6 hours)
  - Brief: Database query logic, project_id filtering, JSON serialization, error handling
- **TASK-XXX:** Implement PUT /tasks/{id}/status endpoint with validation (4-6 hours)
  - Brief: Status transition validation logic, database update, completed_at timestamp handling
- **TASK-XXX:** Implement POST /tasks/batch endpoint (3-4 hours)
  - Brief: Bulk insert logic, transaction handling, response formatting
- **TASK-XXX:** PostgreSQL connection pooling and retry logic (3-4 hours)
  - Brief: pgx pool configuration, connection health checks, exponential backoff retry, structured logging
- **TASK-XXX:** Integration testing for all endpoints (4-6 hours)
  - Brief: Test database setup, integration test suite covering all 10 acceptance criteria, performance testing (100 RPS load)

**Note:** TASK IDs to be allocated by Tech Lead during sprint planning.

## Definition of Done
- [ ] All 4 API endpoints implemented and functional
- [ ] Request validation middleware implemented
- [ ] Database connection pooling configured
- [ ] Retry logic implemented for database failures
- [ ] Structured logging implemented for all API calls
- [ ] Unit tests written and passing (80% coverage minimum)
- [ ] Integration tests passing (all 10 acceptance criteria validated)
- [ ] Performance test validates p99 <200ms under 100 RPS load
- [ ] Code review completed
- [ ] Documentation updated (API endpoint documentation, deployment guide)
- [ ] Product Owner acceptance obtained

## Additional Information
**Suggested Labels:** backend, go, rest-api, microservice, database
**Estimated Story Points:** 8
**Dependencies:**
- US-048 completed (tasks table schema)
- PostgreSQL 15+ database running (local or containerized)
- Go 1.21+ runtime

**Related PRD Section:** PRD-006 §Technical Considerations - Architecture (lines 296-347), §Requirements - FR-14 (lines 163)

## Open Questions & Implementation Uncertainties

**Q1: HTTP framework choice (chi vs. gin vs. gorilla/mux)?**
- **Type:** [REQUIRES TECH LEAD] - Framework selection
- **Context:** All three frameworks support required features (path parameters, query parameters, JSON middleware). Choice affects project dependencies and code style.
- **Recommendation:** chi (lightweight, stdlib-compatible, widely used in Go community) - deferred to implementation

**Q2: Should status transition validation be configurable (state machine) or hardcoded?**
- **Type:** [REQUIRES TECH LEAD] - Design decision
- **Context:** Current requirement: pending→in_progress→completed. Future may need additional states or custom workflows per project.
- **Recommendation:** Start with hardcoded validation (simple map: allowed_transitions["pending"] = ["in_progress"]). Refactor to configurable state machine if requirements expand (YAGNI principle).

All other technical approaches clear from PRD and Implementation Research. Database access patterns standard (pgx library, connection pooling). Error handling patterns standard (HTTP status codes, structured logging).
