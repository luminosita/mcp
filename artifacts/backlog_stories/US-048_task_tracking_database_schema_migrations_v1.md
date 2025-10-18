# User Story: Task Tracking Database Schema and Migrations

## Metadata
- **Story ID:** US-048
- **Title:** Task Tracking Database Schema and Migrations
- **Type:** Feature
- **Status:** Backlog
- **Priority:** High - Foundation for Task Tracking microservice (blocks all other HLS-009 stories)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-009
- **Functional Requirements Covered:** FR-08, FR-09, FR-14, FR-18
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration v3]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Technical Considerations - Data Model - Task Tracking Database Schema
- **Functional Requirements Coverage:**
  - **FR-08:** get_next_task tool (requires tasks table)
  - **FR-09:** update_task_status tool (requires tasks table with status tracking)
  - **FR-14:** Task Tracking microservice REST API (requires database schema)
  - **FR-18:** Multi-project task tracking isolation (requires project_id column and indexes)

**Parent High-Level Story:** [HLS-009: Task Tracking Microservice]
- **Link:** `/artifacts/hls/HLS-009_task_tracking_microservice_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 1: Task Tracking Database Schema and Migrations

## User Story
As a Task Tracking microservice developer, I want a PostgreSQL database schema for task tracking with proper indexes and project isolation, so that the microservice can persist task state, support multi-project isolation, and query tasks efficiently.

## Description
The Task Tracking microservice requires a PostgreSQL database to persist task state across Claude Code sessions, eliminating the need for TODO.md file growth. This story implements the database schema for the `tasks` table, including all required columns for task metadata (task_id, project_id, description, generator_name, status, inputs, outputs, context_notes), timestamps for created/updated/completed tracking, and database constraints for status validation.

The schema must support multi-project isolation (project_id filtering), efficient queries by status (indexes on project_id + status), and ACID compliance for task state transitions. Migration scripts will use Go migration tooling (goose or migrate) to enable versioned schema deployment.

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **Database Schema Design:** PostgreSQL table design with proper data types, constraints, and indexes
  - **Constraint Validation:** CHECK constraint for valid status values (pending | in_progress | completed)
  - **Multi-Project Isolation:** project_id column with composite index (project_id, status) for efficient filtering
  - **JSONB Storage:** Use JSONB columns for inputs/expected_outputs arrays (flexible, queryable)

**Anti-Patterns Avoided:**
- **Avoid String Status Values Without Constraints:** Use CHECK constraint to prevent invalid status values from application layer bugs
- **Avoid Missing Indexes:** Create indexes on frequently queried columns (project_id, status) to prevent full table scans

**Performance Considerations:**
- **Index Strategy:** Composite index on (project_id, status) supports common query pattern `GET /tasks/next?project=X&status=pending`
- **JSONB Performance:** JSONB columns enable array storage without separate join tables while maintaining query performance

## Functional Requirements
- PostgreSQL table `tasks` with columns: task_id (PK), project_id, description, generator_name, status, inputs (JSONB), expected_outputs (JSONB), context_notes, created_at, updated_at, completed_at, completion_notes
- CHECK constraint on status column: values must be one of {pending, in_progress, completed}
- Composite index on (project_id, status) for efficient task filtering
- Index on status column for global status queries
- Migration scripts using Go migration tool (goose or migrate) for versioned schema deployment
- Database initialization script for local development (creates database if not exists)

## Non-Functional Requirements
- **Performance:** Task queries filtered by project_id + status must return results in <50ms for databases with ≤10,000 tasks
- **Scalability:** Schema must support ≥5 concurrent projects with independent project_id namespaces
- **Reliability:** Constraints enforced at database level (not application only) to prevent data corruption
- **Maintainability:** Migration scripts versioned and idempotent (safe to re-run)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story implements database layer for Go microservice. Reference Go implementation standards for migration tooling and database client selection.

### Implementation Guidance

**Database Schema (PostgreSQL):**
- Table: `tasks`
- Primary Key: `task_id` (VARCHAR(20), format: TASK-051)
- Columns:
  - `project_id` VARCHAR(100) NOT NULL - Project identifier for isolation
  - `description` TEXT NOT NULL - Human-readable task description
  - `generator_name` VARCHAR(50) NULL - Generator type (prd-generator, epic-generator, etc.) or NULL for non-generator tasks
  - `status` VARCHAR(20) NOT NULL - Task status (pending | in_progress | completed)
  - `inputs` JSONB - Array of input artifact IDs (e.g., ["EPIC-006", "PRD-006"])
  - `expected_outputs` JSONB - Array of expected output artifact IDs (e.g., ["PRD-006"])
  - `context_notes` TEXT - Additional context (e.g., "New session CX required")
  - `created_at` TIMESTAMP DEFAULT NOW()
  - `updated_at` TIMESTAMP DEFAULT NOW()
  - `completed_at` TIMESTAMP NULL - Set when status transitions to completed
  - `completion_notes` TEXT - Notes from completion (e.g., "PRD-006 v1 generated, 26/26 validation passed")

**Constraints:**
- CHECK constraint: `status IN ('pending', 'in_progress', 'completed')`

**Indexes:**
- `idx_tasks_project_status` on (project_id, status) - Supports `GET /tasks/next?project=X&status=Y`
- `idx_tasks_status` on (status) - Supports global status queries

**Migration Tooling:**
- Use goose or migrate (Go migration libraries) - deferred to Tech Spec/implementation
- Migration files: `001_create_tasks_table.sql`, `002_add_indexes.sql` (example naming)
- Idempotent migrations: Safe to re-run (IF NOT EXISTS checks where applicable)

**References to Implementation Standards:**
- **CLAUDE-tooling.md (Go):** Migration tool selection, Taskfile integration for database commands
- **CLAUDE-architecture.md (Go):** Database migration directory structure (db/migrations/, db/schema.sql)
- **CLAUDE-validation.md (Go):** Input validation patterns (validate project_id format, task_id format before database insertion)

**Note:** Treat CLAUDE.md (Go) files as authoritative for tooling choices and project structure.

### Technical Tasks
- Create PostgreSQL migration script: `001_create_tasks_table.sql`
  - Define tasks table with all columns
  - Add CHECK constraint for status values
- Create PostgreSQL migration script: `002_create_tasks_indexes.sql`
  - Add composite index (project_id, status)
  - Add index on status column
- Integrate migration tool (goose or migrate) into Go project
  - Add migration library to go.mod dependencies
  - Create Taskfile commands: `task db-migrate-up`, `task db-migrate-down`
- Create database initialization script for local development
  - Script creates `mcp_dev` database if not exists
  - Script runs migrations automatically
- Document database setup in README or deployment guide

## Acceptance Criteria

### Scenario 1: Create tasks table via migration
**Given** PostgreSQL database is running and empty
**When** developer runs `task db-migrate-up` (or equivalent migration command)
**Then** tasks table is created with all required columns
**And** CHECK constraint enforces valid status values
**And** indexes are created on (project_id, status) and (status)

### Scenario 2: Insert task with valid status
**Given** tasks table exists
**When** application inserts task with status = "pending"
**Then** insert succeeds and task is persisted
**And** created_at timestamp is automatically set to current time

### Scenario 3: Reject task with invalid status
**Given** tasks table exists
**When** application attempts to insert task with status = "invalid_status"
**Then** database rejects insert with CHECK constraint violation error
**And** no row is inserted into tasks table

### Scenario 4: Query tasks by project_id and status (performance)
**Given** tasks table contains 1,000 tasks across 5 projects
**When** application queries `SELECT * FROM tasks WHERE project_id = 'project-alpha' AND status = 'pending'`
**Then** query completes in <50ms
**And** query uses idx_tasks_project_status index (verified via EXPLAIN ANALYZE)

### Scenario 5: Migration idempotency
**Given** migration has already been applied to database
**When** developer re-runs `task db-migrate-up`
**Then** migration tool detects already-applied migration and skips it
**And** no database errors occur
**And** schema remains unchanged

### Scenario 6: Multi-project isolation (data integrity)
**Given** tasks table contains tasks for project-alpha and project-beta
**When** application queries `SELECT * FROM tasks WHERE project_id = 'project-alpha'`
**Then** only project-alpha tasks are returned
**And** project-beta tasks are not included in result set

### Scenario 7: JSONB column storage for inputs/outputs
**Given** tasks table exists
**When** application inserts task with inputs = `["EPIC-006", "PRD-006"]` as JSONB array
**Then** insert succeeds and JSONB array is persisted
**And** application can query JSONB column: `SELECT inputs FROM tasks WHERE task_id = 'TASK-051'`

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 5 SP - CONSIDER threshold, but below 5+ SP (DON'T SKIP) threshold
- **Developer Count:** Single developer (database engineer or backend developer)
- **Domain Span:** Single domain (database/infrastructure only - no frontend, no backend application logic)
- **Complexity:** Low - straightforward SQL schema definition and migration setup (no complex business logic)
- **Uncertainty:** Low - clear database design from PRD §Data Model, standard PostgreSQL migration patterns
- **Override Factors:** None apply (not cross-domain, not unfamiliar tech, not security-critical beyond standard database constraints, not multi-system integration)

**Conclusion:** Story is within single developer capacity with straightforward implementation (SQL DDL + migration tool setup). Task decomposition overhead not justified. Implementation can proceed directly from this backlog story.

## Definition of Done
- [ ] Migration scripts created and committed to repository
- [ ] Migration tool (goose or migrate) integrated into Go project with Taskfile commands
- [ ] Database initialization script created for local development
- [ ] All acceptance criteria validated (manual testing or automated integration tests)
- [ ] Unit tests passing (if applicable - migration tool integration tests)
- [ ] Integration tests passing (apply migration to test database, verify schema)
- [ ] Code review completed
- [ ] Documentation updated (database setup instructions in README or deployment guide)
- [ ] Product Owner acceptance obtained

## Additional Information
**Suggested Labels:** backend, database, infrastructure, migration
**Estimated Story Points:** 5
**Dependencies:**
- PostgreSQL 15+ database running (local or containerized)
- Go migration tool decision (goose or migrate) - can be made during implementation

**Related PRD Section:** PRD-006 §Technical Considerations - Data Model - Task Tracking Database Schema (lines 419-441)

## Open Questions & Implementation Uncertainties

**No open implementation questions. All technical approaches clear from Implementation Research and PRD.**

Database schema fully specified in PRD-006 §Data Model. Migration tool selection (goose vs. migrate) is a minor implementation detail that can be decided during story execution based on Go community recommendations and CLAUDE-tooling.md (Go) standards.
