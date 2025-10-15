# User Story: Create Database Container Configuration

## Metadata
- **Story ID:** US-023
- **Title:** Create Database Container Configuration
- **Type:** Feature
- **Status:** Draft
- **Priority:** Medium - Enables local development with containerized database, can implement in parallel with US-022/US-024
- **Parent PRD:** PRD-000
- **Parent High-Level Story:** HLS-005 (Containerized Deployment Enabling Production Readiness)
- **Functional Requirements Covered:** FR-17
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** PRD-000: Project Foundation & Bootstrap Infrastructure
- **Link:** /artifacts/prds/PRD-000_project_foundation_bootstrap_v3.md
- **PRD Section:** Section 5.1 - Functional Requirements
- **Functional Requirements Coverage:**
  - **FR-17:** Development environment database running in Podman container

**Parent High-Level Story:** HLS-005: Containerized Deployment Enabling Production Readiness
- **Link:** /artifacts/hls/HLS-005_containerized_deployment_configuration_v1.md
- **HLS Section:** Section "Decomposition into Backlog Stories" - Story 4

## User Story
As a software engineer developing the AI Agent MCP Server locally,
I want a containerized PostgreSQL + pgvector database for local development,
So that I can develop and test database features without installing PostgreSQL natively on my machine.

## Description
Configure a PostgreSQL + pgvector container for local development use, accessible through unified Taskfile commands (`task db:start`, `task db:stop`). The database container eliminates the need for native PostgreSQL installation (per PRD-000 Decision D7), runs in Podman (or Docker alternative), and provides a consistent database environment across all development machines. The container should be ready for connections within 10 seconds and persist data between restarts by default.

This story addresses the database component of local development containerization, enabling developers to work with a production-like database locally without complex native installation.

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§2.3: Database & Storage - PostgreSQL 15+ with pgvector 0.5+:** Container runs PostgreSQL 15+ with pgvector extension for vector embedding storage
  - **Implementation:** Use official PostgreSQL image with pgvector extension pre-installed or install during initialization
- **§2.3: Schema Design Example:** Container initializes with schema supporting document metadata and vector embeddings per research guidance

**Performance Considerations:**
- **Startup Time:** Target <10 seconds from container start to database ready for connections
- **Development Performance:** Container performance acceptable for local development workloads (PRD-000 Decision D7 assumption)

## Functional Requirements
- PostgreSQL 15+ container with pgvector extension enabled
- Database container runs using Podman (primary) or Docker (alternative)
- Add `task db:start` command to Taskfile starting database container
- Add `task db:stop` command to Taskfile stopping database container gracefully
- Database ready for connections within 10 seconds of start
- Data persists between container restarts by default (volume mounted)
- Database accessible on localhost:5432 (standard PostgreSQL port)
- Default database created automatically on first run
- Environment variables configure database credentials (DATABASE_URL in .env)
- `.env.example` updated with database connection string template
- Database container logs accessible for debugging
- Add optional `task db:reset` command for clean slate (drops data)

## Non-Functional Requirements
- **Performance:**
  - Container startup: <10 seconds to ready state
  - Query performance acceptable for development workloads (no production optimization required)
- **Usability:**
  - Database starts with single command (`task db:start`)
  - No manual configuration required for basic usage
  - Clear error messages if port already in use
- **Reliability:**
  - Data persistence maintained across container restarts
  - Graceful shutdown on `task db:stop`
  - Container restarts automatically if crashes (configurable)
- **Portability:**
  - Works with Podman (primary) and Docker (alternative)
  - Consistent behavior across macOS, Linux, Windows WSL2
  - Works within Devbox environment

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story references established implementation standards from specialized CLAUDE.md files, supplementing with story-specific technical guidance.

### Implementation Guidance

Configure PostgreSQL + pgvector container for local development:

**Container Configuration:**
- Base image: `postgres:15` or `ankane/pgvector:latest` (PostgreSQL with pgvector pre-installed)
- Extension: Enable pgvector extension during initialization
- Port mapping: 5432 (container) → 5432 (host)
- Volume: Mount persistent volume for database data (`pgdata:/var/lib/postgresql/data`)
- Environment variables:
  - `POSTGRES_USER`: Default user (e.g., `mcp_user`)
  - `POSTGRES_PASSWORD`: Default password (e.g., `dev_password_change_in_production`)
  - `POSTGRES_DB`: Default database (e.g., `mcp_dev`)

**Taskfile Integration:**
Add database tasks to Taskfile under `db:` namespace:

```yaml
db:start:
  desc: "Start PostgreSQL + pgvector container for local development"
  cmds:
    - |
      podman run -d \
        --name mcp-postgres \
        -e POSTGRES_USER={{.DB_USER}} \
        -e POSTGRES_PASSWORD={{.DB_PASSWORD}} \
        -e POSTGRES_DB={{.DB_NAME}} \
        -p 5432:5432 \
        -v pgdata:/var/lib/postgresql/data \
        ankane/pgvector:latest

db:stop:
  desc: "Stop database container gracefully"
  cmds:
    - podman stop mcp-postgres
    - podman rm mcp-postgres

db:reset:
  desc: "Reset database to clean state (WARNING: destroys data)"
  cmds:
    - task db:stop
    - podman volume rm pgdata
    - task db:start

db:logs:
  desc: "View database container logs"
  cmds:
    - podman logs mcp-postgres -f
```

**Initialization Script (Optional):**
- Create `scripts/init-db.sql` with initial schema (pgvector extension, basic tables)
- Mount script as volume: `-v ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql`
- PostgreSQL executes scripts in `/docker-entrypoint-initdb.d/` on first run

**Connection Configuration:**
Update `.env.example` with database connection string:
```
DATABASE_URL=postgresql+asyncpg://mcp_user:dev_password_change_in_production@localhost:5432/mcp_dev
```

**References to Implementation Standards:**
- **CLAUDE-tooling.md:** Follow Taskfile patterns for database tasks, use consistent naming (`db:action` format)
- **CLAUDE-architecture.md:** Database configuration integrates with project structure (initialization scripts in `scripts/` directory)

**Note:** Treat CLAUDE.md content as authoritative - database container configuration supplements with container-specific commands.

### Technical Tasks
- Select PostgreSQL + pgvector container image (ankane/pgvector or postgres:15 with manual extension)
- Add `task db:start` command to Taskfile with Podman/Docker runtime detection
- Add `task db:stop` command to Taskfile
- Add optional `task db:reset` and `task db:logs` commands
- Configure persistent volume for database data
- Define Taskfile variables for database credentials with defaults
- Create `scripts/init-db.sql` initialization script enabling pgvector extension
- Update `.env.example` with DATABASE_URL template
- Test database startup time (<10 seconds)
- Test data persistence across container restarts
- Test database connectivity from application
- Verify tasks work with both Podman and Docker runtimes
- Document database commands in CONTRIBUTING.md or SETUP.md

## Acceptance Criteria

**Format:** Gherkin (Given-When-Then) for scenario-based validation

### Scenario 1: Database container starts successfully
**Given** developer is in project directory with Taskfile configured
**When** developer executes `task db:start`
**Then** PostgreSQL + pgvector container starts using Podman (or Docker fallback)
**And** database is ready for connections within 10 seconds
**And** pgvector extension is enabled
**And** default database `mcp_dev` is created

### Scenario 2: Application connects to containerized database
**Given** database container is running
**And** `.env` file contains DATABASE_URL
**When** application starts and attempts database connection
**Then** connection succeeds using credentials from .env
**And** application can query database successfully

### Scenario 3: Data persists across container restarts
**Given** database container is running
**And** developer creates test table with data
**When** developer executes `task db:stop` and then `task db:start`
**Then** database restarts successfully
**And** test table and data still exist (persistence verified)

### Scenario 4: Database logs accessible for debugging
**Given** database container is running
**When** developer executes `task db:logs`
**Then** container logs display in terminal
**And** logs show database initialization and query activity

### Scenario 5: Database reset clears all data
**Given** database container is running with test data
**When** developer executes `task db:reset` and confirms
**Then** database container stops
**And** data volume is removed
**And** new clean database starts
**And** test data no longer exists

### Scenario 6: Port conflict handled gracefully
**Given** port 5432 is already in use by another process
**When** developer executes `task db:start`
**Then** command fails with clear error message
**And** error indicates port conflict
**And** error suggests resolution (stop conflicting process or change port)

### Scenario 7: Docker fallback works when Podman unavailable
**Given** Podman is not installed on system
**And** Docker is installed as alternative
**When** developer executes `task db:start`
**Then** database container starts using Docker runtime
**And** all functionality works identically to Podman

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 3 SP - Medium complexity, straightforward container configuration
- **Developer Count:** Single developer - No coordination overhead
- **Domain Span:** Single domain (database container configuration) - No cross-domain complexity
- **Complexity:** Low-Medium - Using pre-built PostgreSQL container image, standard Taskfile commands, well-documented container patterns
- **Uncertainty:** Low - PostgreSQL containers are standard practice, pgvector extension available in pre-built images
- **Override Factors:** None applicable
  - Not cross-domain (database container only)
  - Not high uncertainty (standard PostgreSQL containerization)
  - Not unfamiliar technology (PostgreSQL and container runtimes standard tools)
  - Not security-critical at configuration level (development database with default credentials acceptable)
  - Not multi-system integration (local database container)

**Conclusion:** This is a straightforward 3 SP story configuring a standard PostgreSQL container with pgvector and adding Taskfile commands. Developer can complete in 1 day following established containerization patterns. Creating separate TASK-XXX artifacts would add overhead without coordination benefit.

## Definition of Done
- [ ] PostgreSQL + pgvector container image selected (ankane/pgvector or postgres:15)
- [ ] `task db:start` command added to Taskfile with Podman/Docker runtime detection
- [ ] `task db:stop` command added to Taskfile
- [ ] `task db:reset` and `task db:logs` commands added (optional but recommended)
- [ ] Persistent volume configured for database data (`pgdata` volume)
- [ ] Taskfile variables defined for database credentials with defaults
- [ ] `scripts/init-db.sql` initialization script created enabling pgvector extension
- [ ] `.env.example` updated with DATABASE_URL template
- [ ] Database startup time verified (<10 seconds)
- [ ] Data persistence verified across container restarts
- [ ] Database connectivity tested from application
- [ ] Port conflict error handling tested
- [ ] Tasks tested with both Podman and Docker runtimes
- [ ] Tasks verified in Devbox environment on at least 2 platforms
- [ ] Documentation updated (CONTRIBUTING.md or SETUP.md) with database commands
- [ ] Code reviewed following project review checklist
- [ ] Acceptance criteria validated manually
- [ ] Product owner approval obtained

## Additional Information
**Suggested Labels:** infrastructure, database, container, podman, postgresql, pgvector
**Estimated Story Points:** 3 (Fibonacci scale)
**Dependencies:**
- HLS-001 (Development Environment Setup) completed - Provides Taskfile and Devbox foundation
- US-020 (Create Production Containerfile) completed - Establishes container patterns (not blocking but provides context)

**Related PRD Section:**
- PRD-000 Section 5.1 Functional Requirements (FR-17: Development environment database in Podman container)
- PRD-000 Section 8 Technical Considerations - Dependencies (PostgreSQL 15+ with pgvector 0.5+)
- PRD-000 Decision D7: Development Environment Database (Podman container only, no native installation)

## Open Questions & Implementation Uncertainties

**No open implementation questions.** All technical approaches clear from Implementation Research and PRD-000.

PostgreSQL containerization is standard practice with extensive documentation. Pre-built images with pgvector extension are available (ankane/pgvector). Volume mounting for data persistence is standard Docker/Podman feature. Taskfile command structure follows established patterns from US-021.

Implementation can proceed directly following standard container patterns without requiring spike investigation or tech lead consultation.

---

**Document Version:** v1.0
**Generated By:** Backlog Story Generator v1.5
**Generation Date:** 2025-10-15
**Parent:** HLS-005 Containerized Deployment Enabling Production Readiness v1.0
**Story Sequence:** 4 of 6 in HLS-005 decomposition

---

## Traceability Notes

**Source Artifacts:**
- **Parent HLS:** HLS-005 Containerized Deployment Enabling Production Readiness v1.0
  - Decomposition Plan: Story 4 (lines 303-306)
  - Alternative Flow B: Local Database Setup with Container (lines 160-176)
  - User Interactions: "Manages database container using `task db:*` commands" (line 183)
  - Acceptance Criterion 4: Database Container Operational for Development (lines 234-242)
- **Parent PRD:** PRD-000 Project Foundation & Bootstrap Infrastructure v3.0
  - FR-17: Development environment database running in Podman container (line 186)
  - Technical Constraints: PostgreSQL 15+ with pgvector 0.5+ (line 546)
  - Decision D7: Development Environment Database - Podman container only (lines 631-635)
- **Implementation Research:** AI_Agent_MCP_Server_implementation_research.md
  - §2.3: Database & Storage - PostgreSQL 15+ with pgvector 0.5+ (lines 154-199 excerpt)
  - Schema Design Example: Document metadata and embeddings tables

**Quality Validation:**
- ✅ Story title action-oriented and specific ("Create Database Container Configuration")
- ✅ Detailed requirements clearly stated (PostgreSQL + pgvector container with Taskfile commands)
- ✅ Acceptance criteria highly specific and testable (7 scenarios covering startup, persistence, logs, reset, errors)
- ✅ Technical notes reference Implementation Research sections (§2.3)
- ✅ Technical specifications include container configuration (image, volumes, Taskfile commands)
- ✅ Story points estimated (3 SP)
- ✅ Testing strategy defined (manual validation via acceptance criteria, startup time measurement)
- ✅ Dependencies identified (HLS-001, US-020 for context)
- ✅ Open Questions capture implementation uncertainties (none - all approaches clear)
- ✅ Implementation-adjacent: Describes container approach without prescribing exact Taskfile.yml syntax
- ✅ Sprint-ready: Can be completed in 1 day by single developer
- ✅ CLAUDE.md Alignment: References CLAUDE-tooling.md and CLAUDE-architecture.md appropriately
- ✅ Implementation Tasks Evaluation: Clear decision (No Tasks Needed) with rationale based on SDLC Section 11 criteria
