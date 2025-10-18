# High-Level User Story: Task Tracking Microservice

## Metadata
- **Story ID:** HLS-009
- **Status:** Draft
- **Priority:** High
- **Parent Epic:** EPIC-006
- **Parent PRD:** PRD-006
- **PRD Section:** Phase 4: Task Tracking Microservice (Weeks 5-6)
- **Functional Requirements:** FR-08, FR-09, FR-10, FR-11, FR-14, FR-15, FR-18, FR-19
- **Owner:** Product Manager + Tech Lead
- **Target Release:** Phase 4 (Weeks 5-6)

## Parent Artifact Context

**Parent Epic:** [EPIC-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v2.md`
- **Epic Contribution:** Replaces unbounded TODO.md file growth with database-backed task tracking and ID management, reducing token consumption by 40-60% (addresses Epic Acceptance Criterion 2 - MCP Tools Functional Equivalence)

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Timeline & Milestones - Phase 4: Task Tracking Microservice (Weeks 5-6)
- **Functional Requirements Coverage:**
  - **FR-08:** get_next_task tool (integrated with Task Tracking microservice)
  - **FR-09:** update_task_status tool (integrated with Task Tracking microservice)
  - **FR-10:** get_next_available_id tool (integrated with Task Tracking microservice)
  - **FR-11:** reserve_id_range tool (integrated with Task Tracking microservice)
  - **FR-14:** Task Tracking microservice REST API (tasks + IDs)
  - **FR-15:** Global ID uniqueness across concurrent requests (SERIALIZABLE isolation)
  - **FR-18:** Multi-project task tracking isolation
  - **FR-19:** Multi-project ID registry isolation

**User Persona Source:** PRD-006 §User Personas - Persona 1: Enterprise Development Team Lead

## User Story Statement

**As an** Enterprise Development Team Lead,
**I want** task tracking and ID management as a centralized microservice instead of local TODO.md files,
**So that** I can track task status across 5+ concurrent projects without manual file reviews and prevent artifact ID collisions.

## User Context

### Target Persona
**Enterprise Development Team Lead - "Sarah"**
- Manages 5-10 concurrent Python/Go microservice projects
- Each project uses SDLC framework for planning and implementation
- 8+ years experience, values consistency, automation, and operational simplicity

**User Characteristics:**
- Currently reviews TODO.md files manually across 7 projects to track status
- Frustrated by TODO.md file growth burning ~5-10k tokens per Claude Code interaction
- Needs visibility into task status across all projects (centralized view)
- Pain point: Manual ID tracking causes occasional duplicate artifact IDs across projects

### User Journey Context
**Before this story:** TODO.md files grow with every completed task. Sarah manually reviews 7 TODO.md files to check project status. Artifact IDs tracked manually, causing occasional collisions when multiple projects generate backlog stories simultaneously.

**After this story:** Task Tracking microservice provides centralized database with task status and ID registry. Sarah runs `task tracking-status --project all` to see combined view. Artifact IDs guaranteed globally unique via database transaction isolation.

**Downstream impact:** Enables HLS-010 (CLAUDE.md orchestration) to use MCP tools for task tracking instead of TODO.md file management.

## Business Value

### User Value
- **Centralized Visibility:** Single query shows task status across all 5+ projects (vs. reviewing 5+ TODO.md files)
- **Reduced Token Consumption:** Eliminates ~5-10k tokens per interaction from TODO.md file loading
- **ID Collision Prevention:** Guaranteed unique artifact IDs across concurrent requests (0% collision vs. occasional manual errors)
- **Operational Simplicity:** No manual TODO.md file maintenance or ID tracking

### Business Value
- **Token Cost Reduction:** Eliminates TODO.md token overhead, contributing to 40-60% overall token reduction (per PRD-006 §Executive Summary)
- **Quality Improvement:** Zero artifact ID collisions (vs. ~1-2% manual tracking errors)
- **Scalability:** Supports ≥5 concurrent projects without proportional token consumption increase
- **Time Savings:** Sarah saves 2-3 hours/week on manual TODO.md reviews

### Success Criteria
- Task Tracking API supports 100 RPS with p99 <200ms (per NFR-Performance-04)
- ID management API handles 50 concurrent reservations with zero collisions (per NFR-Performance-05)
- Multi-project isolation validated (5 projects with independent task/ID databases)
- API authentication implemented (API key or JWT)

## Functional Requirements (High-Level)

### Primary User Flow (Task Tracking)

**Happy Path:**
1. Claude Code completes backlog story generation for Project-Alpha
2. Claude Code calls MCP tool `update_task_status(task_id="TASK-045", status="completed", notes="US-015 generated successfully")`
3. MCP Server calls Task Tracking microservice REST API: `PUT /tasks/TASK-045/status`
4. Microservice updates PostgreSQL database record (status, timestamp, notes)
5. Microservice returns confirmation: `{success: true, updated_task: {...}}`
6. Claude Code calls `get_next_task(project_id="project-alpha", status_filter="pending")`
7. MCP Server calls microservice: `GET /tasks/next?project=project-alpha&status=pending`
8. Microservice queries database for next pending task
9. Microservice returns: `{task_id: "TASK-046", description: "Generate HLS-007", generator: "hls-generator", inputs: ["PRD-006"]}`
10. Claude Code proceeds with next task

**Happy Path (Sub-artifact Task Addition):**
1. Claude Code generates PRD-006 artifact successfully
2. MCP Server's `validate_artifact` tool returns JSON: `{requires_sub_artifacts: true, open_questions: true, required_artifacts_ids: ["HLS-006", "HLS-007", "HLS-008", "HLS-009", "HLS-010", "HLS-011"]}`
3. Claude Code presents report to developer showing sub-artifact requirement
4. Developer confirms sub-artifact generation should proceed
5. Claude Code calls MCP tool `add_task` with metadata for each sub-artifact:
```json
{
  "tasks": [
    {"artifact_id": "HLS-006", "artifact_type": "hls", "generator": "hls-generator", "parent_id": "PRD-006", "status": "pending"},
    {"artifact_id": "HLS-007", "artifact_type": "hls", "generator": "hls-generator", "parent_id": "PRD-006", "status": "pending"},
    ...
  ]
}
```
6. MCP Server calls Task Tracking microservice: `POST /tasks/batch`
7. Microservice adds 6 new tasks to database (HLS-006 through HLS-011)
8. Microservice returns: `{success: true, tasks_added: 6, task_ids: ["TASK-046", "TASK-047", ...]}`
9. Claude Code confirms to developer: "Added 6 HLS generation tasks to queue"
10. Developer can now run `/generate` command to process next task (HLS-006)

**Primary User Flow (ID Management):**
1. Claude Code starts HLS decomposition for PRD-006 (needs 6 backlog story IDs)
2. Claude Code calls MCP tool `reserve_id_range(artifact_type="US", count=6)`
3. MCP Server calls Task Tracking microservice: `POST /ids/reserve` with body `{type: "US", count: 6, project_id: "ai-agent-mcp-server"}`
4. Microservice starts database transaction (SERIALIZABLE isolation)
5. Microservice reads last_assigned_id for US type (27)
6. Microservice reserves US-028 through US-033
7. Microservice creates reservation record with 15-minute expiration
8. Microservice commits transaction and returns: `{reserved_ids: ["US-028", "US-029", "US-030", "US-031", "US-032", "US-033"], expires_at: "2025-10-18T14:30:00Z"}`
9. Claude Code generates 6 backlog stories using reserved IDs
10. Claude Code calls `confirm_reservation(reservation_id="abc123")` to prevent expiration

**Alternative Flows:**
- **Alt Flow 1: Concurrent ID Requests:** Two projects request US IDs simultaneously → database SERIALIZABLE isolation ensures non-overlapping ID ranges
- **Alt Flow 2: Reservation Expiration:** If Claude Code doesn't confirm within 15 minutes, IDs released for reuse
- **Alt Flow 3: Multi-Project Isolation:** Project-Alpha queries tasks → receives only Project-Alpha tasks (project_id filtering)

### User Interactions
- Claude Code calls MCP tools (get_next_task, update_task_status, get_next_available_id, reserve_id_range, add_task)
- Sarah runs CLI command `task tracking-status --project all` (custom tool, future enhancement)
- Sarah views task completion trends via observability dashboard (Grafana, future enhancement)

### System Behaviors (User Perspective)
- Task Tracking microservice persists task state in PostgreSQL database
- Microservice guarantees ID uniqueness via database transaction isolation (SERIALIZABLE)
- Microservice isolates data by project_id (no cross-project leakage)
- Microservice exposes REST API authenticated via API key/JWT
- Microservice implements health check endpoint for monitoring
- Microservice accepts batch task additions for sub-artifact workflows

## Acceptance Criteria (High-Level)

### Criterion 1: Task Tracking API Functional
**Given** task exists in database with status "pending"
**When** Claude Code calls `get_next_task(project_id="ai-agent-mcp-server")`
**Then** microservice returns next pending task with context (ID, description, inputs)

### Criterion 2: Task Status Updates Persist
**Given** Claude Code completes task
**When** Claude Code calls `update_task_status(task_id="TASK-045", status="completed")`
**Then** microservice updates database record and returns confirmation

### Criterion 3: Batch Task Addition Functional
**Given** Claude Code completes artifact requiring sub-artifacts
**When** Claude Code calls `add_task` with batch of sub-artifact metadata
**Then** microservice adds all tasks to database and returns task IDs

### Criterion 4: ID Reservation Guarantees Uniqueness
**Given** 10 concurrent `reserve_id_range` requests for same artifact type
**When** all requests execute simultaneously
**Then** all requests return non-overlapping ID ranges (zero collisions)

### Criterion 5: Multi-Project Isolation Works
**Given** Project-Alpha and Project-Beta both have tasks in database
**When** Claude Code queries `get_next_task(project_id="project-alpha")`
**Then** only Project-Alpha tasks returned (no cross-project leakage)

### Criterion 6: API Performance Meets Targets
**Given** microservice under load (100 RPS)
**When** API requests processed
**Then** p99 latency <200ms (per NFR-Performance-04)

### Criterion 7: API Authentication Required
**Given** unauthenticated request to microservice API
**When** request received
**Then** microservice returns 401 Unauthorized (no unauthenticated access)

### Edge Cases & Error Conditions
- **Task Not Found:** Return error: `{error: "Task not found", task_id: "..."}`
- **Invalid Status Transition:** If attempt completed→pending, return error: `{error: "Invalid status transition"}`
- **ID Exhaustion:** If artifact type reaches MAX_INT, return error with guidance
- **Database Unavailable:** MCP Server falls back to local file approach with warning (per NFR-Availability-03)

## Scope & Boundaries

### In Scope
- Task Tracking microservice (Go) with REST API
- PostgreSQL database for tasks and ID registry
- Task endpoints: GET /tasks/next, PUT /tasks/{id}/status, GET /tasks?project={id}, POST /tasks/batch
- ID endpoints: GET /ids/next, POST /ids/reserve, POST /ids/confirm
- Database transaction isolation (SERIALIZABLE) for ID uniqueness
- Multi-project isolation (project_id filtering)
- API authentication (API key or JWT)
- Health check endpoint (/health)
- Batch task addition for sub-artifact workflows

### Out of Scope (Deferred to Future Stories)
- Custom CLI tool for Sarah (`task tracking-status --project all`) - future enhancement
- Metrics endpoint (/metrics) for Prometheus - HLS-011 (Production Readiness)
- Database migration scripts - backlog stories
- Horizontal scaling (multiple microservice instances) - future enhancement
- Cloud-hosted database (AWS RDS, GCP Cloud SQL) - Decision D3: containerized PostgreSQL for pilot

## Decomposition into Backlog Stories

### Estimated Backlog Stories (Not Yet Detailed)

1. **Task Tracking Database Schema and Migrations** (~5 SP)
   - Brief: PostgreSQL schema for tasks table, indexes, project_id isolation

2. **ID Registry Database Schema and Migrations** (~5 SP)
   - Brief: PostgreSQL schema for id_registry and id_reservations tables, SERIALIZABLE isolation

3. **Task Tracking REST API Implementation (Go)** (~8 SP)
   - Brief: HTTP router, task endpoints (GET /tasks/next, PUT /tasks/{id}/status, GET /tasks, POST /tasks/batch), project_id filtering

4. **ID Management REST API Implementation (Go)** (~8 SP)
   - Brief: ID endpoints (GET /ids/next, POST /ids/reserve, POST /ids/confirm), transaction isolation

5. **API Authentication (API Key/JWT)** (~5 SP)
   - Brief: Middleware for API key or JWT validation on all endpoints

6. **MCP Server Integration (Python MCP Tools)** (~5 SP)
   - Brief: MCP tools (get_next_task, update_task_status, get_next_available_id, reserve_id_range, add_task) call microservice REST API

7. **Multi-Project Stress Testing** (~3 SP)
   - Brief: Validate 5 concurrent projects, zero ID collisions, <200ms p99 latency

8. **Observability (Health Check, Logging)** (~3 SP)
   - Brief: /health endpoint, structured logging for all API calls

**Total Estimated Story Points:** ~42 SP
**Estimated Sprints:** 2 sprints (Weeks 5-6 per PRD-006 timeline)

### Decomposition Strategy
**By Component:**
- Stories 1-2: Database layer (schemas, migrations)
- Stories 3-4: Microservice layer (REST API implementation)
- Story 5: Security layer (authentication)
- Story 6: Integration layer (MCP Server tools)
- Story 7: Quality assurance (stress testing)
- Story 8: Operational layer (observability)

**Priority Order:** 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 (sequential for 1-6, parallel for 7-8)

## Dependencies

### User Story Dependencies
- **Depends On:** HLS-006 (MCP Resources Migration - infrastructure foundation)
- **Depends On:** HLS-008 (MCP Tools - add_task tool implementation)
- **Blocks:** HLS-010 (CLAUDE.md orchestration uses task tracking tools)

### External Dependencies
- PostgreSQL 15+ (containerized via Docker Compose/Podman per Decision D3)
- Go 1.21+ runtime
- Go HTTP router library (chi, gin, or similar - deferred to ADR)
- PostgreSQL client library (pgx or similar)

## Non-Functional Requirements (User-Facing Only)

- **Performance:** API response time p99 <200ms under 100 RPS load
- **Reliability:** Database transactions ensure ID uniqueness (zero collisions guaranteed)
- **Scalability:** Supports ≥5 concurrent projects with independent task/ID databases
- **Observability:** Health check endpoint returns status within 100ms
- **Security:** API requires authentication (no unauthenticated access)

## Risks & Open Questions

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| **Database Performance Bottleneck** | Medium - could slow task tracking | Connection pooling, query performance monitoring, load testing |
| **ID Collision in Concurrent Requests** | High - data corruption | SERIALIZABLE isolation level, stress testing (50 concurrent requests) |
| **Go Microservice Development Complexity** | Medium - delays implementation | Reference Go CLAUDE-core.md and CLAUDE-tooling.md (already available) |

### Open Questions

**No open UX or functional questions at this time. Implementation uncertainties will be captured during backlog refinement.**

Technical implementation questions (HTTP framework choice, database migration tool) deferred to backlog stories and ADRs per PRD-006 §Decisions Made.

## Definition of Ready (Before Backlog Refinement)

- [x] User story statement complete and validated
- [x] User persona identified (Enterprise Development Team Lead - Sarah)
- [x] Business value articulated (2-3 hours/week saved, zero ID collisions)
- [x] High-level acceptance criteria defined (7 criteria)
- [x] Dependencies identified (depends on HLS-006 and HLS-008, blocks HLS-010)
- [ ] Product Owner approval obtained

## Definition of Done (High-Level Story Complete)

- [ ] All 8 decomposed backlog stories completed (US-047 through US-054)
- [ ] All acceptance criteria met and validated
- [ ] Task Tracking API supports 100 RPS with p99 <200ms
- [ ] ID management handles 50 concurrent reservations with zero collisions
- [ ] Batch task addition functional for sub-artifact workflows
- [ ] Multi-project isolation validated (5 projects tested)
- [ ] API authentication implemented (API key or JWT)
- [ ] Unit test coverage ≥80% (Go microservice)
- [ ] Integration tests passing (MCP tools → microservice → database)
- [ ] Product Owner acceptance obtained

## Related Documents
- **Parent Epic:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v2.md`
- **PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md` (§Timeline & Milestones - Phase 4)
- **Go Implementation Standards:** `/prompts/CLAUDE/go/CLAUDE-core.md`, `/prompts/CLAUDE/go/CLAUDE-tooling.md`
- **User Personas:** PRD-006 §User Personas & Use Cases - Persona 1: Enterprise Development Team Lead
- **Dependency:** HLS-006 (MCP Resources Migration), HLS-008 (MCP Tools - add_task tool)

## Version History
- **v2 (2025-10-18):** Applied feedback - Added "Happy Path (Sub-artifact Task Addition)" flow showing how Claude Code adds new tasks to queue after artifact generation. Added Criterion 3 for batch task addition. Added POST /tasks/batch endpoint to Task endpoints. Updated dependencies to include HLS-008 (add_task tool). Updated backlog story counts (US-047 through US-054).
- **v1 (2025-10-18):** Initial version
