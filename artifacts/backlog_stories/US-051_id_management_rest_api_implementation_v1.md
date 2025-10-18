# User Story: ID Management REST API Implementation (Go)

## Metadata
- **Story ID:** US-051
- **Title:** ID Management REST API Implementation (Go)
- **Type:** Feature
- **Status:** Backlog
- **Priority:** High - Critical for artifact ID uniqueness guarantee (blocks US-053 MCP integration)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-009
- **Functional Requirements Covered:** FR-10, FR-11, FR-14, FR-15, FR-19
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration v3]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Technical Considerations - Architecture - Task Tracking Microservice REST API
- **Functional Requirements Coverage:**
  - **FR-10:** get_next_available_id tool (requires GET /ids/next endpoint)
  - **FR-11:** reserve_id_range tool (requires POST /ids/reserve and POST /ids/confirm endpoints)
  - **FR-14:** Task Tracking microservice REST API ID endpoints specification
  - **FR-15:** Global ID uniqueness across concurrent requests (requires SERIALIZABLE isolation)
  - **FR-19:** Multi-project ID registry isolation (requires project_id query parameter filtering)

**Parent High-Level Story:** [HLS-009: Task Tracking Microservice]
- **Link:** `/artifacts/hls/HLS-009_task_tracking_microservice_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 4: ID Management REST API Implementation (Go)

## User Story
As an MCP Server developer, I want a Go REST API for artifact ID management with endpoints for retrieving next available ID, reserving ID ranges, and confirming reservations, so that MCP tools can guarantee globally unique artifact IDs across concurrent requests with zero collisions.

## Description
The Task Tracking microservice provides centralized artifact ID management to eliminate manual ID tracking and prevent collisions. This story implements three core ID management endpoints:

1. **GET /ids/next?type={artifact_type}&project={project_id}** - Returns next sequential ID for artifact type (e.g., US-028)
2. **POST /ids/reserve** - Reserves contiguous ID range for batch generation with 15-minute expiration (e.g., US-028 through US-033)
3. **POST /ids/confirm** - Confirms reservation to prevent expiration (client successfully generated all artifacts)

The API must use SERIALIZABLE transaction isolation to guarantee zero ID collisions during concurrent requests, enforce project-specific ID sequences (project-alpha US-001 is independent from project-beta US-001), handle reservation expiration cleanup (release unused IDs after 15 minutes), and return atomic ID allocations (single transaction for entire range).

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **Database Transaction Isolation:** SERIALIZABLE isolation level for ID allocation queries
  - **Concurrency Safety:** Prevent race conditions where two requests get overlapping ID ranges
  - **Example:** Request A allocates US-028-033, Request B (concurrent) allocates US-034-039 (no overlap)
  - **Performance Trade-off:** SERIALIZABLE adds ~10-20ms latency but eliminates retry complexity
- **Optimistic Locking Alternative (Not Used):** Version-based locking with retry logic rejected in favor of SERIALIZABLE for simplicity
- **Temporal Reservations:** Expiration mechanism with partial index for efficient cleanup query
- **Atomic Range Allocation:** Single transaction updates id_registry.last_assigned_id AND creates id_reservations row

**Anti-Patterns Avoided:**
- **Avoid Application-Level Retry for ID Conflicts:** Database handles serialization (no application retry needed)
- **Avoid Unbounded Reservations:** 15-minute expiration prevents ID exhaustion from abandoned workflows
- **Avoid Cross-Project ID Sequences:** Each project maintains independent ID counters (last_assigned_id per project_id)

**Performance Considerations:**
- **SERIALIZABLE Overhead:** ~10-20ms per transaction vs. READ COMMITTED, but eliminates collision risk
- **Connection Pool Sizing:** Separate connection pool for SERIALIZABLE transactions (avoid mixing isolation levels)
- **Reservation Cleanup:** Background job (or explicit API call) to delete expired reservations (expires_at < NOW() AND confirmed = FALSE)

## Functional Requirements
- Endpoint: `GET /ids/next?type={artifact_type}&project={project_id}` - Returns next available ID for type+project
- Endpoint: `POST /ids/reserve` with JSON body `{type: string, count: int, project_id: string}` - Reserves ID range, returns reservation_id and reserved_ids array
- Endpoint: `POST /ids/confirm` with JSON body `{reservation_id: UUID}` - Marks reservation as confirmed (prevents expiration)
- Endpoint: `DELETE /ids/reservations/expired` - Cleanup endpoint to delete expired reservations (internal use, cron job trigger)
- SERIALIZABLE transaction isolation for all ID allocation queries (GET /ids/next, POST /ids/reserve)
- Request validation: Validate artifact_type enum (US, SPEC, TASK, EPIC, PRD, HLS, VIS, INIT, SPIKE, ADR), validate count > 0, validate project_id format
- Multi-project isolation: Query filters by project_id (project-alpha US sequence independent from project-beta)
- Reservation expiration: Default 15 minutes (configurable via environment variable)
- Atomic ID range allocation: Single transaction updates id_registry AND inserts id_reservations row
- Response format: JSON with consistent structure `{success: bool, data: object, error: string}`

## Non-Functional Requirements
- **Performance:** ID allocation queries with SERIALIZABLE isolation must complete in <100ms (p95) under 50 concurrent requests (per NFR-Performance-05)
- **Scalability:** Support ≥50 concurrent ID reservation requests with zero collisions
- **Reliability:** Database SERIALIZABLE isolation guarantees zero ID collisions (validated via stress test in US-054)
- **Reliability:** Reservation expiration cleanup prevents ID exhaustion (automated cleanup job or manual API call)
- **Observability:** Log all ID allocation requests with timestamp, artifact_type, project_id, reserved_ids, duration

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story implements Go REST API. Reference Go implementation standards (CLAUDE-core.md, CLAUDE-tooling.md, CLAUDE-architecture.md) for transaction isolation configuration, logging, and testing.

### Implementation Guidance

**API Endpoints Specification:**

**1. GET /ids/next**
- Query Parameters:
  - `type` (required): Artifact type (US, SPEC, TASK, etc.)
  - `project` (required): Project ID (e.g., "ai-agent-mcp-server")
- Response 200 OK:
  ```json
  {
    "success": true,
    "artifact_type": "US",
    "next_id": "US-028",
    "last_assigned": "US-027"
  }
  ```
- Response 400 Bad Request: Invalid artifact_type or missing parameters
- Implementation:
  - Start SERIALIZABLE transaction
  - Query: `SELECT last_assigned_id FROM id_registry WHERE artifact_type = $1 AND project_id = $2 FOR UPDATE`
  - Increment: `next_id = last_assigned_id + 1`
  - Update: `UPDATE id_registry SET last_assigned_id = $1, updated_at = NOW() WHERE artifact_type = $2 AND project_id = $3`
  - Commit transaction
  - Return next_id formatted (e.g., "US-028")

**2. POST /ids/reserve**
- Request Body:
  ```json
  {
    "type": "US",
    "count": 6,
    "project_id": "ai-agent-mcp-server"
  }
  ```
- Response 200 OK:
  ```json
  {
    "success": true,
    "reservation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "artifact_type": "US",
    "reserved_ids": ["US-028", "US-029", "US-030", "US-031", "US-032", "US-033"],
    "expires_at": "2025-10-18T14:30:00Z"
  }
  ```
- Response 400 Bad Request: Invalid count (≤0 or >100), invalid artifact_type
- Implementation:
  - Start SERIALIZABLE transaction
  - Query: `SELECT last_assigned_id FROM id_registry WHERE artifact_type = $1 AND project_id = $2 FOR UPDATE`
  - Calculate range: `start = last_assigned_id + 1, end = last_assigned_id + count`
  - Generate reserved_ids array: `["US-028", "US-029", ..., "US-033"]`
  - Update: `UPDATE id_registry SET last_assigned_id = $1, updated_at = NOW() WHERE artifact_type = $2 AND project_id = $3`
  - Insert: `INSERT INTO id_reservations (reservation_id, artifact_type, project_id, reserved_ids, expires_at) VALUES ($1, $2, $3, $4, NOW() + INTERVAL '15 minutes')`
  - Commit transaction
  - Return reservation_id and reserved_ids

**3. POST /ids/confirm**
- Request Body:
  ```json
  {
    "reservation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
  ```
- Response 200 OK:
  ```json
  {
    "success": true,
    "reservation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "confirmed": true
  }
  ```
- Response 404 Not Found: Reservation ID not found or already expired
- Implementation:
  - Update: `UPDATE id_reservations SET confirmed = TRUE WHERE reservation_id = $1 AND expires_at > NOW()`
  - Check rows affected: If 0, return 404

**4. DELETE /ids/reservations/expired** (Internal cleanup endpoint)
- Response 200 OK:
  ```json
  {
    "success": true,
    "deleted_count": 5
  }
  ```
- Implementation:
  - Delete: `DELETE FROM id_reservations WHERE expires_at < NOW() AND confirmed = FALSE`
  - Return count of deleted rows

**SERIALIZABLE Transaction Configuration:**
- PostgreSQL connection: Set isolation level per transaction
- pgx example: `tx, err := pool.BeginTx(ctx, pgx.TxOptions{IsoLevel: pgx.Serializable})`
- Note: SERIALIZABLE transactions may fail with serialization error (retry logic not needed - database handles serialization)

**Error Handling:**
- SERIALIZABLE serialization failure (rare): Retry transaction once, then return 500 if fails again
- Database connection failure: Retry 3 times with exponential backoff (100ms, 200ms, 400ms)
- Validation errors: Return 400 Bad Request with specific error message

**Logging:**
- Structured logging (JSON format): `{"timestamp": "...", "method": "POST", "path": "/ids/reserve", "artifact_type": "US", "count": 6, "reserved_ids": ["US-028", ...], "duration_ms": 45}`
- Log level: INFO for successful allocations, ERROR for 500 responses, WARN for 400 responses

**References to Implementation Standards:**
- **CLAUDE-core.md (Go):** Transaction isolation configuration, error handling patterns
- **CLAUDE-tooling.md (Go):** Database client (pgx), Taskfile integration (`task id-api-run`, `task id-api-test`)
- **CLAUDE-architecture.md (Go):** Project structure (internal/handlers/ids.go, internal/db/id_registry.go)
- **CLAUDE-validation.md (Go):** Input validation patterns (validate artifact_type enum, validate UUID format)

**Note:** Treat CLAUDE.md (Go) files as authoritative for framework choices and code organization.

### Technical Tasks
- Implement GET /ids/next endpoint with SERIALIZABLE transaction
- Implement POST /ids/reserve endpoint with atomic range allocation
- Implement POST /ids/confirm endpoint for reservation confirmation
- Implement DELETE /ids/reservations/expired cleanup endpoint
- Configure pgx connection pool with SERIALIZABLE transaction support
- Add input validation for artifact_type enum, count bounds, UUID format
- Add structured logging for all ID allocation requests
- Add error handling for serialization failures and database errors
- Write unit tests for endpoint handlers (mock database)
- Write integration tests for concurrent ID allocation (50 concurrent requests, zero collisions)

## Acceptance Criteria

### Scenario 1: Retrieve next available ID
**Given** id_registry contains row (artifact_type="US", project_id="ai-agent-mcp-server", last_assigned_id=27)
**When** client sends GET /ids/next?type=US&project=ai-agent-mcp-server
**Then** API returns 200 OK with next_id = "US-028" and last_assigned = "US-027"
**And** id_registry updated with last_assigned_id = 28
**And** response completes in <100ms (p95)

### Scenario 2: Reserve ID range for batch generation
**Given** id_registry contains row (artifact_type="US", project_id="ai-agent-mcp-server", last_assigned_id=27)
**When** client sends POST /ids/reserve with body `{type: "US", count: 6, project_id: "ai-agent-mcp-server"}`
**Then** API returns 200 OK with reserved_ids = ["US-028", "US-029", "US-030", "US-031", "US-032", "US-033"]
**And** id_registry updated with last_assigned_id = 33
**And** id_reservations table contains new row with reservation_id, reserved_ids, expires_at (15 minutes from now)
**And** response completes in <100ms (p95)

### Scenario 3: Confirm reservation before expiration
**Given** id_reservations contains reservation with expires_at = 10 minutes from now, confirmed = FALSE
**When** client sends POST /ids/confirm with body `{reservation_id: "<UUID>"}`
**Then** API returns 200 OK with confirmed = TRUE
**And** id_reservations row updated with confirmed = TRUE

### Scenario 4: Reject confirmation of expired reservation
**Given** id_reservations contains reservation with expires_at = 5 minutes ago, confirmed = FALSE
**When** client sends POST /ids/confirm with body `{reservation_id: "<UUID>"}`
**Then** API returns 404 Not Found with error message "Reservation expired or not found"
**And** id_reservations row remains unchanged (confirmed = FALSE)

### Scenario 5: Concurrent ID allocation with zero collisions
**Given** id_registry contains row (artifact_type="US", project_id="ai-agent-mcp-server", last_assigned_id=0)
**When** 10 clients send concurrent GET /ids/next?type=US&project=ai-agent-mcp-server requests
**Then** all 10 requests return unique IDs (US-001, US-002, ..., US-010)
**And** zero ID collisions (all IDs distinct)
**And** id_registry final state: last_assigned_id = 10
**And** SERIALIZABLE isolation enforced (verified via database transaction logs)

### Scenario 6: Concurrent range reservation with zero overlap
**Given** id_registry contains row (artifact_type="US", project_id="ai-agent-mcp-server", last_assigned_id=0)
**When** 5 clients send concurrent POST /ids/reserve requests with count=6 each
**Then** all 5 requests return non-overlapping ID ranges (US-001-006, US-007-012, US-013-018, US-019-024, US-025-030)
**And** zero ID overlap between reservations
**And** id_registry final state: last_assigned_id = 30

### Scenario 7: Multi-project isolation enforced
**Given** id_registry contains two rows (artifact_type="US", project_id="project-alpha", last_assigned_id=10) and (artifact_type="US", project_id="project-beta", last_assigned_id=20)
**When** client sends GET /ids/next?type=US&project=project-alpha
**Then** API returns next_id = "US-011" (not "US-021")
**And** project-beta registry remains unchanged (last_assigned_id=20)

### Scenario 8: Cleanup expired reservations
**Given** id_reservations contains 5 expired reservations (expires_at < NOW(), confirmed = FALSE)
**And** id_reservations contains 3 confirmed reservations (confirmed = TRUE)
**When** client sends DELETE /ids/reservations/expired
**Then** API returns 200 OK with deleted_count = 5
**And** 5 expired rows deleted from id_reservations
**And** 3 confirmed rows remain in id_reservations

### Scenario 9: Validate artifact_type enum
**Given** API is running
**When** client sends GET /ids/next?type=INVALID&project=ai-agent-mcp-server
**Then** API returns 400 Bad Request with error message "Invalid artifact_type: INVALID. Valid types: US, SPEC, TASK, EPIC, PRD, HLS, VIS, INIT, SPIKE, ADR"

### Scenario 10: Performance under concurrent load
**Given** API is running with id_registry populated
**When** 50 concurrent POST /ids/reserve requests are sent (stress test)
**Then** p95 response time <100ms (per NFR-Performance-05)
**And** zero ID collisions (all reservations have unique, non-overlapping ranges)
**And** no database connection pool exhaustion errors

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Needed

**Rationale:**
- **Story Points:** 8 SP - EXCEEDS 5+ SP threshold (DON'T SKIP per SDLC Section 11.6)
- **Developer Count:** Single backend developer, but significant complexity
- **Domain Span:** Single domain (backend only), but critical concurrency requirements
- **Complexity:** High - SERIALIZABLE transaction isolation, atomic range allocation, reservation expiration logic, concurrent request handling
- **Uncertainty:** Medium - SERIALIZABLE isolation standard but less common than READ COMMITTED (requires careful testing)
- **Override Factors:** Performance-critical (50 concurrent requests must have zero collisions)

**Conclusion:** Story exceeds 5 SP threshold. Complexity (SERIALIZABLE transactions, concurrent safety) and performance criticality warrant decomposition into focused tasks (4-8 hours each).

**Proposed Implementation Tasks:**
- **TASK-XXX:** Implement GET /ids/next endpoint with SERIALIZABLE transaction (4-6 hours)
  - Brief: Database query with FOR UPDATE lock, transaction isolation configuration, ID increment logic, formatted response
- **TASK-XXX:** Implement POST /ids/reserve endpoint with atomic range allocation (6-8 hours)
  - Brief: SERIALIZABLE transaction, range calculation, id_registry update + id_reservations insert in single transaction, expiration timestamp
- **TASK-XXX:** Implement POST /ids/confirm and DELETE /ids/reservations/expired endpoints (3-4 hours)
  - Brief: Confirmation update logic, expired reservation cleanup query, response formatting
- **TASK-XXX:** Input validation and error handling (3-4 hours)
  - Brief: Artifact_type enum validation, count bounds check, UUID format validation, serialization failure retry logic
- **TASK-XXX:** Structured logging for ID allocation (2-3 hours)
  - Brief: JSON logging middleware, log all ID allocation requests with parameters and duration
- **TASK-XXX:** Concurrency stress testing (50 concurrent requests) (4-6 hours)
  - Brief: Integration test suite with 50 concurrent GET /ids/next and POST /ids/reserve requests, validate zero collisions, measure p95 latency

**Note:** TASK IDs to be allocated by Tech Lead during sprint planning.

## Definition of Done
- [ ] All 4 API endpoints implemented and functional
- [ ] SERIALIZABLE transaction isolation configured for ID allocation queries
- [ ] Input validation implemented (artifact_type enum, count bounds, UUID format)
- [ ] Structured logging implemented for all ID allocation requests
- [ ] Error handling implemented (serialization failures, database errors)
- [ ] Unit tests written and passing (80% coverage minimum)
- [ ] Integration tests passing (all 10 acceptance criteria validated)
- [ ] Concurrency stress test validates zero collisions with 50 concurrent requests
- [ ] Performance test validates p95 <100ms under 50 concurrent requests
- [ ] Code review completed
- [ ] Documentation updated (API endpoint documentation, SERIALIZABLE isolation configuration notes)
- [ ] Product Owner acceptance obtained

## Additional Information
**Suggested Labels:** backend, go, rest-api, concurrency, database, critical
**Estimated Story Points:** 8
**Dependencies:**
- US-049 completed (id_registry and id_reservations tables)
- PostgreSQL 15+ database running (supports SERIALIZABLE isolation)
- Go 1.21+ runtime with pgx library

**Related PRD Section:** PRD-006 §Technical Considerations - Architecture (lines 296-347), §Requirements - FR-15 (lines 164)

## Open Questions & Implementation Uncertainties

**Q1: Should we implement automatic reservation expiration cleanup (cron job) or manual API call?**
- **Type:** [REQUIRES TECH LEAD] - Operational decision
- **Context:** Expired reservations waste database space. Options: (1) Cron job runs DELETE /ids/reservations/expired every 30 minutes, (2) Manual API call triggered by ops team, (3) Lazy cleanup (delete on next ID allocation query).
- **Recommendation:** Start with manual API call endpoint (DELETE /ids/reservations/expired). Add cron job if expired reservations accumulate (>1000 rows). Lazy cleanup adds complexity to ID allocation queries (avoid).

**Q2: Should reservation expiration be configurable per request or global?**
- **Type:** [REQUIRES TECH LEAD] - Design decision
- **Context:** Current requirement: 15 minutes default. Some batch operations may need longer expiration (e.g., 30 minutes).
- **Recommendation:** Start with global configuration (environment variable RESERVATION_EXPIRATION_MINUTES=15). Add per-request override (`{type: "US", count: 6, expiration_minutes: 30}`) only if business case emerges (YAGNI principle).

All other technical approaches clear from PRD and Implementation Research. SERIALIZABLE isolation level standard PostgreSQL feature (no custom implementation). UUID generation handled by database (gen_random_uuid()) or Go libraries (google/uuid).
