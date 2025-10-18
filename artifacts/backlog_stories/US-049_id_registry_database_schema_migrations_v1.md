# User Story: ID Registry Database Schema and Migrations

## Metadata
- **Story ID:** US-049
- **Title:** ID Registry Database Schema and Migrations
- **Type:** Feature
- **Status:** Backlog
- **Priority:** High - Foundation for ID management (blocks US-051, critical for FR-15 uniqueness guarantee)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-009
- **Functional Requirements Covered:** FR-10, FR-11, FR-14, FR-15, FR-19
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration v3]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Technical Considerations - Data Model - ID Registry Database Schema
- **Functional Requirements Coverage:**
  - **FR-10:** get_next_available_id tool (requires id_registry table)
  - **FR-11:** reserve_id_range tool (requires id_reservations table with expiration logic)
  - **FR-14:** Task Tracking microservice REST API ID endpoints (requires database schema)
  - **FR-15:** Global ID uniqueness across concurrent requests (requires SERIALIZABLE isolation)
  - **FR-19:** Multi-project ID registry isolation (requires project_id column and UNIQUE constraint)

**Parent High-Level Story:** [HLS-009: Task Tracking Microservice]
- **Link:** `/artifacts/hls/HLS-009_task_tracking_microservice_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 2: ID Registry Database Schema and Migrations

## User Story
As a Task Tracking microservice developer, I want PostgreSQL database schemas for ID registry and ID reservations with SERIALIZABLE transaction isolation, so that the microservice can guarantee globally unique artifact IDs across concurrent requests with zero collisions.

## Description
The Task Tracking microservice must eliminate manual artifact ID tracking by providing database-backed ID management with guaranteed uniqueness. This story implements two PostgreSQL tables:

1. **id_registry:** Tracks the last assigned ID per artifact type per project (e.g., US-027 for ai-agent-mcp-server project)
2. **id_reservations:** Manages temporary ID reservations with 15-minute expiration for batch artifact generation workflows

The schema must enforce UNIQUE constraint on (artifact_type, project_id) to prevent duplicate registry entries, support SERIALIZABLE transaction isolation to guarantee zero ID collisions during concurrent `reserve_id_range` calls, and provide automatic reservation expiration cleanup via database-level checks.

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **Database Transaction Isolation:** SERIALIZABLE isolation level for ID allocation queries to prevent race conditions
  - **Concurrent Safety:** Two transactions requesting next US ID will serialize - first gets US-028, second gets US-029 (no overlap)
  - **Performance Trade-off:** SERIALIZABLE adds latency (~10-20ms) but guarantees correctness
- **UUID Primary Keys:** Use UUID for reservation_id to prevent collision across distributed systems
- **JSONB Array Storage:** Store reserved_ids as JSONB array (e.g., ["US-028", "US-029", "US-030"]) for flexible range representation
- **Temporal Data Management:** expires_at timestamp with partial index for efficient cleanup query (`WHERE confirmed = FALSE`)

**Anti-Patterns Avoided:**
- **Avoid Application-Level ID Generation:** Database enforces uniqueness via transaction isolation (not application logic)
- **Avoid Unbounded Reservations:** Expiration mechanism prevents ID exhaustion from abandoned workflows
- **Avoid Full Table Scans:** Partial index on (expires_at) WHERE confirmed = FALSE limits index size to active reservations only

**Performance Considerations:**
- **Transaction Isolation Cost:** SERIALIZABLE isolation adds ~10-20ms per transaction but eliminates retry logic complexity
- **Reservation Expiration Query:** Partial index on (expires_at, confirmed) enables fast expired reservation cleanup without scanning confirmed reservations

## Functional Requirements
- PostgreSQL table `id_registry` with columns: id (SERIAL PK), artifact_type, project_id, last_assigned_id, created_at, updated_at
- UNIQUE constraint on (artifact_type, project_id) to prevent duplicate registry entries
- PostgreSQL table `id_reservations` with columns: reservation_id (UUID PK), artifact_type, project_id, reserved_ids (JSONB), reserved_at, expires_at, confirmed
- CHECK constraint on id_reservations: expires_at > reserved_at (prevent invalid expiration)
- Partial index on id_reservations (expires_at) WHERE confirmed = FALSE for efficient expiration cleanup
- Index on id_reservations (project_id, artifact_type) for project-specific reservation queries
- Migration scripts using Go migration tool (goose or migrate) for versioned schema deployment
- Database initialization script for local development (populates initial id_registry rows for all artifact types if empty)

## Non-Functional Requirements
- **Performance:** ID allocation queries with SERIALIZABLE isolation must complete in <100ms (p95) under 50 concurrent requests
- **Scalability:** Schema must support ≥10 artifact types × ≥5 projects = 50 id_registry rows
- **Reliability:** UNIQUE constraint enforced at database level prevents duplicate registry entries (not application-level validation)
- **Reliability:** SERIALIZABLE isolation guarantees zero ID collisions (validated via stress test in US-054)
- **Maintainability:** Migration scripts versioned and idempotent (safe to re-run)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story implements database layer for Go microservice. Reference Go implementation standards for migration tooling and transaction isolation configuration.

### Implementation Guidance

**Database Schema 1: id_registry**
- Table: `id_registry`
- Primary Key: `id` (SERIAL)
- Columns:
  - `artifact_type` VARCHAR(10) NOT NULL - Artifact type (US, SPEC, TASK, EPIC, PRD, HLS, etc.)
  - `project_id` VARCHAR(100) NOT NULL - Project identifier for isolation
  - `last_assigned_id` INTEGER NOT NULL - Last assigned numeric ID (27 for US-027)
  - `created_at` TIMESTAMP DEFAULT NOW()
  - `updated_at` TIMESTAMP DEFAULT NOW()
- Constraints:
  - UNIQUE (artifact_type, project_id) - Ensures single registry entry per type per project

**Database Schema 2: id_reservations**
- Table: `id_reservations`
- Primary Key: `reservation_id` (UUID)
- Columns:
  - `artifact_type` VARCHAR(10) NOT NULL - Artifact type (US, SPEC, TASK, etc.)
  - `project_id` VARCHAR(100) NOT NULL - Project identifier
  - `reserved_ids` JSONB NOT NULL - Array of reserved IDs (["US-028", "US-029", "US-030"])
  - `reserved_at` TIMESTAMP DEFAULT NOW()
  - `expires_at` TIMESTAMP NOT NULL - Expiration timestamp (reserved_at + 15 minutes default)
  - `confirmed` BOOLEAN DEFAULT FALSE - TRUE if client confirmed reservation, FALSE if pending
- Constraints:
  - CHECK (expires_at > reserved_at) - Prevent invalid expiration timestamps

**Indexes:**
- `idx_reservations_expiry` on (expires_at) WHERE confirmed = FALSE - Partial index for expired reservation cleanup
- `idx_reservations_project` on (project_id, artifact_type) - Supports project-specific reservation queries

**Transaction Isolation:**
- ID allocation queries (UPDATE id_registry SET last_assigned_id = ...) MUST run in SERIALIZABLE isolation
- Configuration: PostgreSQL connection string or BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE
- Implementation detail: US-051 (ID Management REST API) will configure isolation level

**Migration Tooling:**
- Use goose or migrate (Go migration libraries) - deferred to Tech Spec/implementation
- Migration files: `003_create_id_registry_table.sql`, `004_create_id_reservations_table.sql`, `005_add_id_indexes.sql`
- Idempotent migrations: Safe to re-run (IF NOT EXISTS checks where applicable)

**Database Initialization:**
- Seed script populates id_registry with initial rows for all artifact types (US, SPEC, TASK, EPIC, PRD, HLS, VIS, INIT, SPIKE, ADR) with last_assigned_id = 0
- Run seed script as part of local development setup (not production - production starts empty)

**References to Implementation Standards:**
- **CLAUDE-tooling.md (Go):** Migration tool selection, Taskfile integration for database commands
- **CLAUDE-architecture.md (Go):** Database migration directory structure (db/migrations/, db/schema.sql)
- **CLAUDE-validation.md (Go):** Input validation patterns (validate artifact_type enum, validate UUID format)

**Note:** Treat CLAUDE.md (Go) files as authoritative for tooling choices and project structure.

### Technical Tasks
- Create PostgreSQL migration script: `003_create_id_registry_table.sql`
  - Define id_registry table with all columns
  - Add UNIQUE constraint on (artifact_type, project_id)
- Create PostgreSQL migration script: `004_create_id_reservations_table.sql`
  - Define id_reservations table with all columns (UUID primary key, JSONB reserved_ids)
  - Add CHECK constraint: expires_at > reserved_at
- Create PostgreSQL migration script: `005_create_id_indexes.sql`
  - Add partial index on (expires_at) WHERE confirmed = FALSE
  - Add index on (project_id, artifact_type)
- Create database seed script for local development
  - Insert id_registry rows for all 10 artifact types with last_assigned_id = 0
  - Script idempotent (INSERT ... ON CONFLICT DO NOTHING)
- Document SERIALIZABLE isolation requirement in migration notes or code comments

## Acceptance Criteria

### Scenario 1: Create id_registry table via migration
**Given** PostgreSQL database is running and migration 002 (tasks indexes) is applied
**When** developer runs `task db-migrate-up` to apply migration 003
**Then** id_registry table is created with all required columns
**And** UNIQUE constraint enforces single registry entry per (artifact_type, project_id)
**And** migration completes without errors

### Scenario 2: Enforce UNIQUE constraint on id_registry
**Given** id_registry table contains row (artifact_type="US", project_id="project-alpha", last_assigned_id=10)
**When** application attempts to insert duplicate row (artifact_type="US", project_id="project-alpha", last_assigned_id=20)
**Then** database rejects insert with UNIQUE constraint violation error
**And** original row remains unchanged

### Scenario 3: Create id_reservations table via migration
**Given** PostgreSQL database is running and migration 003 (id_registry table) is applied
**When** developer runs `task db-migrate-up` to apply migration 004
**Then** id_reservations table is created with all required columns
**And** CHECK constraint enforces expires_at > reserved_at
**And** migration completes without errors

### Scenario 4: Reject id_reservations with invalid expiration
**Given** id_reservations table exists
**When** application attempts to insert reservation with expires_at = '2025-10-18T10:00:00Z' and reserved_at = '2025-10-18T12:00:00Z' (expires before reserved)
**Then** database rejects insert with CHECK constraint violation error
**And** no row is inserted into id_reservations table

### Scenario 5: JSONB storage for reserved_ids array
**Given** id_reservations table exists
**When** application inserts reservation with reserved_ids = `["US-028", "US-029", "US-030"]` as JSONB array
**Then** insert succeeds and JSONB array is persisted
**And** application can query JSONB column: `SELECT reserved_ids FROM id_reservations WHERE reservation_id = <UUID>`
**And** JSONB array can be queried: `SELECT * FROM id_reservations WHERE reserved_ids @> '["US-028"]'`

### Scenario 6: Partial index improves expiration cleanup performance
**Given** id_reservations table contains 100 reservations (50 confirmed = TRUE, 50 confirmed = FALSE)
**When** application queries `SELECT * FROM id_reservations WHERE expires_at < NOW() AND confirmed = FALSE`
**Then** query uses idx_reservations_expiry partial index (verified via EXPLAIN ANALYZE)
**And** query does not scan confirmed = TRUE rows

### Scenario 7: Database seed script populates initial id_registry
**Given** id_registry table is empty
**When** developer runs database seed script
**Then** 10 rows are inserted (one per artifact type: US, SPEC, TASK, EPIC, PRD, HLS, VIS, INIT, SPIKE, ADR)
**And** all rows have last_assigned_id = 0 and project_id = 'ai-agent-mcp-server' (default project)
**And** re-running seed script is idempotent (no duplicate inserts)

### Scenario 8: Multi-project isolation (data integrity)
**Given** id_registry contains rows for project-alpha (US last_assigned_id = 10) and project-beta (US last_assigned_id = 20)
**When** application queries `SELECT last_assigned_id FROM id_registry WHERE artifact_type = 'US' AND project_id = 'project-alpha'`
**Then** query returns 10 (not 20)
**And** project-beta data is not included in result set

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 5 SP - CONSIDER threshold, but below 5+ SP (DON'T SKIP) threshold
- **Developer Count:** Single developer (database engineer or backend developer)
- **Domain Span:** Single domain (database/infrastructure only - no frontend, no backend application logic)
- **Complexity:** Low - straightforward SQL schema definition with standard constraints (UNIQUE, CHECK) and indexes (partial, composite)
- **Uncertainty:** Low - clear database design from PRD §Data Model, standard PostgreSQL transaction isolation patterns
- **Override Factors:** None apply (not cross-domain, not unfamiliar tech, not security-critical beyond standard database constraints, not multi-system integration)

**Conclusion:** Story is within single developer capacity with straightforward implementation (SQL DDL + migration tool setup + seed script). Similar complexity to US-048 (tasks table). Task decomposition overhead not justified. Implementation can proceed directly from this backlog story.

## Definition of Done
- [ ] Migration scripts created and committed to repository (003, 004, 005)
- [ ] Database seed script created for local development
- [ ] All acceptance criteria validated (manual testing or automated integration tests)
- [ ] Unit tests passing (if applicable - migration tool integration tests)
- [ ] Integration tests passing (apply migrations to test database, verify schema and constraints)
- [ ] Code review completed
- [ ] Documentation updated (database setup instructions, SERIALIZABLE isolation requirement noted)
- [ ] Product Owner acceptance obtained

## Additional Information
**Suggested Labels:** backend, database, infrastructure, migration, concurrency
**Estimated Story Points:** 5
**Dependencies:**
- US-048 completed (tasks table migrations as prerequisite)
- PostgreSQL 15+ database running (local or containerized)
- Go migration tool decision (goose or migrate) - should be consistent with US-048

**Related PRD Section:** PRD-006 §Technical Considerations - Data Model - ID Registry Database Schema (lines 443-471)

## Decisions Made

**All technical approaches clear from Implementation Research and PRD.**

Database schema fully specified in PRD-006 §Data Model. SERIALIZABLE isolation level is standard PostgreSQL transaction isolation (no custom implementation required - configured via connection string or BEGIN TRANSACTION statement). UUID generation handled by PostgreSQL or Go libraries (standard approach).
