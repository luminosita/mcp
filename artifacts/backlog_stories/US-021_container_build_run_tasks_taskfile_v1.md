# User Story: Configure Container Build and Run Tasks in Taskfile

## Metadata
- **Story ID:** US-021
- **Title:** Configure Container Build and Run Tasks in Taskfile
- **Type:** Feature
- **Status:** Draft
- **Priority:** High - Provides unified CLI interface for container operations, enables developer self-service
- **Parent PRD:** PRD-000
- **Parent High-Level Story:** HLS-005 (Containerized Deployment Enabling Production Readiness)
- **Functional Requirements Covered:** FR-13, FR-22
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** PRD-000: Project Foundation & Bootstrap Infrastructure
- **Link:** /artifacts/prds/PRD-000_project_foundation_bootstrap_v3.md
- **PRD Section:** Section 5.1 - Functional Requirements
- **Functional Requirements Coverage:**
  - **FR-13:** Containerized deployment configuration with Podman (Docker alternative)
  - **FR-22:** Unified CLI interface via Taskfile for all development operations

**Parent High-Level Story:** HLS-005: Containerized Deployment Enabling Production Readiness
- **Link:** /artifacts/hls/HLS-005_containerized_deployment_configuration_v1.md
- **HLS Section:** Section "Decomposition into Backlog Stories" - Story 2

## User Story
As a software engineer building or deploying the AI Agent MCP Server,
I want unified Taskfile commands for container operations,
So that I can build and run containers without memorizing Podman/Docker CLI syntax.

## Description
Integrate container operations into the project's unified Taskfile interface by adding `task container:build` and `task container:run` commands. These tasks abstract Podman/Docker CLI complexity, provide sensible defaults, and enable self-discovery via `task --list`. The Taskfile tasks use the Containerfile created in US-020, providing a developer-friendly CLI for container workflows.

This story completes the container foundation by making container operations accessible through the project's standard CLI interface, reducing cognitive load and enabling consistent workflows across development and deployment.

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§2.1: Python 3.11+ Technology Stack:** Tasks execute container builds for Python 3.11+ application
- **§2.2: FastAPI Framework:** Container runs FastAPI application, tasks configure appropriate port mapping and environment variables

**Performance Considerations:**
- **Build Speed:** Tasks leverage Podman/Docker layer caching for fast rebuilds
- **Task Overhead:** Taskfile adds <2 seconds overhead per PRD-000 NFR requirement

## Functional Requirements
- Add `task container:build` command to Taskfile building container image using Containerfile from US-020
- Add `task container:run` command to Taskfile running container with appropriate port mapping and environment configuration
- Tasks support both Podman (primary) and Docker (alternative) runtimes via environment variable or auto-detection
- Tasks provide clear output indicating build progress and container runtime status
- Tasks include help text describing purpose and usage (accessible via `task --list`)
- Container build task accepts optional tag parameter (default: `latest`)
- Container run task maps application port (8000) to host
- Container run task mounts environment variables from `.env` file if present
- Tasks handle common error scenarios with actionable error messages
- Documentation updated to reference Taskfile commands (CONTRIBUTING.md or DEPLOYMENT.md)

## Non-Functional Requirements
- **Performance:** Task execution overhead <2 seconds per PRD-000 NFR
- **Usability:**
  - Commands discoverable via `task --list`
  - Clear help text for each task
  - Error messages actionable with resolution guidance
- **Reliability:**
  - Tasks idempotent (safe to run multiple times)
  - Proper error handling prevents incomplete builds
- **Maintainability:**
  - Tasks include inline comments explaining purpose
  - Uses Taskfile best practices (variables, dependencies)
- **Portability:** Tasks work on macOS, Linux, Windows WSL2 within Devbox environment

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story references established implementation standards from specialized CLAUDE.md files, supplementing with story-specific technical guidance.

### Implementation Guidance

Add container tasks to `Taskfile.yml` under new `container:` namespace:

**Task: container:build**
- Command: `podman build -t {{.IMAGE_NAME}}:{{.TAG}} -f Containerfile .`
- Variables:
  - `IMAGE_NAME`: Default `ai-agent-mcp-server`
  - `TAG`: Parameter with default `latest`
  - `CONTAINER_RUNTIME`: Auto-detect Podman (primary) or fall back to Docker
- Description: "Build production container image using multi-stage Containerfile"
- Features:
  - Accepts optional tag parameter: `task container:build TAG=v1.0.0`
  - Detects container runtime (Podman primary, Docker fallback)
  - Displays build progress to stdout
  - Returns non-zero exit code on build failure

**Task: container:run**
- Command: `podman run -p 8000:8000 --env-file .env {{.IMAGE_NAME}}:{{.TAG}}`
- Variables:
  - `IMAGE_NAME`: Default `ai-agent-mcp-server`
  - `TAG`: Parameter with default `latest`
  - `CONTAINER_RUNTIME`: Auto-detect Podman/Docker
- Description: "Run production container locally with port mapping"
- Features:
  - Maps port 8000 (container) to 8000 (host)
  - Loads environment variables from `.env` file if present
  - Runs in foreground (Ctrl+C to stop)
  - Accepts optional tag parameter: `task container:run TAG=v1.0.0`

**Optional Helper Tasks:**
- `task container:stop`: Stop running container
- `task container:logs`: View container logs
- `task container:shell`: Open shell in running container for debugging

**References to Implementation Standards:**
- **CLAUDE-tooling.md:** Follow Taskfile organization patterns, use consistent naming conventions (`namespace:action` format)
- **CLAUDE-architecture.md:** Tasks integrate with project structure (Containerfile at root, src/ layout)

**Note:** Treat CLAUDE.md content as authoritative - Taskfile tasks supplement with container-specific commands.

### Technical Tasks
- Add `container:build` task to Taskfile.yml with Podman/Docker runtime detection
- Add `container:run` task to Taskfile.yml with port mapping and environment configuration
- Define Taskfile variables for image name and tag with sensible defaults
- Implement container runtime auto-detection (check for Podman, fall back to Docker)
- Add task descriptions visible in `task --list` output
- Add inline comments in Taskfile explaining task purpose
- Test tasks with both Podman and Docker runtimes
- Update documentation (CONTRIBUTING.md or DEPLOYMENT.md) with Taskfile command examples
- Verify tasks work in Devbox environment on macOS, Linux, Windows WSL2

## Acceptance Criteria

**Format:** Gherkin (Given-When-Then) for scenario-based validation

### Scenario 1: Container build task succeeds with default tag
**Given** Containerfile exists from US-020 at project root
**When** developer executes `task container:build`
**Then** container image builds successfully using Podman (or Docker fallback)
**And** image is tagged as `ai-agent-mcp-server:latest`
**And** build output displays progress to terminal
**And** task completes with exit code 0

### Scenario 2: Container build task accepts custom tag
**Given** Containerfile exists at project root
**When** developer executes `task container:build TAG=v1.0.0`
**Then** container image builds successfully
**And** image is tagged as `ai-agent-mcp-server:v1.0.0`
**And** custom tag is reflected in build output

### Scenario 3: Container run task starts application successfully
**Given** container image `ai-agent-mcp-server:latest` has been built
**When** developer executes `task container:run`
**Then** container starts successfully using Podman (or Docker fallback)
**And** application is accessible on http://localhost:8000
**And** health check endpoint responds within 10 seconds
**And** container logs display in terminal

### Scenario 4: Container run task loads environment variables
**Given** container image has been built
**And** `.env` file exists at project root with configuration
**When** developer executes `task container:run`
**Then** container starts with environment variables loaded from `.env`
**And** application uses configuration from environment variables

### Scenario 5: Tasks discoverable via task --list
**Given** container tasks have been added to Taskfile
**When** developer executes `task --list`
**Then** output includes `container:build` with description
**And** output includes `container:run` with description
**And** descriptions clearly explain task purpose

### Scenario 6: Docker fallback works when Podman unavailable
**Given** Podman is not installed on system
**And** Docker is installed as alternative
**When** developer executes `task container:build`
**Then** task detects Docker as fallback runtime
**And** build succeeds using Docker
**And** output indicates Docker is being used

### Scenario 7: Error handling provides actionable messages
**Given** Containerfile does not exist at project root
**When** developer executes `task container:build`
**Then** task fails with clear error message
**And** error message indicates Containerfile is missing
**And** error message suggests resolution (e.g., "Run task container:build after completing US-020")

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 2 SP - Low complexity, straightforward implementation
- **Developer Count:** Single developer - No coordination overhead
- **Domain Span:** Single domain (Taskfile configuration) - No cross-domain complexity
- **Complexity:** Low - Adding tasks to existing Taskfile using established patterns, standard Podman/Docker commands
- **Uncertainty:** Low - Clear path, Taskfile syntax well-documented, container commands standard
- **Override Factors:** None applicable
  - Not cross-domain (single Taskfile configuration)
  - Not high uncertainty (standard task definition)
  - Not unfamiliar technology (Taskfile and Podman/Docker standard tools)
  - Not security-critical (executing container commands, no secrets handling)
  - Not multi-system integration (local container operations)

**Conclusion:** This is a straightforward 2 SP story adding 2-3 tasks to an existing Taskfile. Developer can complete in <1 day following established Taskfile patterns. Creating separate TASK-XXX artifacts would add overhead without coordination benefit.

## Definition of Done
- [ ] `container:build` task added to Taskfile.yml with Podman/Docker runtime detection
- [ ] `container:run` task added to Taskfile.yml with port mapping and environment configuration
- [ ] Taskfile variables defined for image name and tag with defaults
- [ ] Container runtime auto-detection implemented (Podman primary, Docker fallback)
- [ ] Task descriptions added and visible in `task --list` output
- [ ] Tasks tested successfully with Podman runtime
- [ ] Tasks tested successfully with Docker runtime (compatibility verified)
- [ ] Environment variable loading from `.env` verified
- [ ] Error handling tested (missing Containerfile, no runtime available)
- [ ] Documentation updated (CONTRIBUTING.md or DEPLOYMENT.md) with Taskfile command examples
- [ ] Tasks verified in Devbox environment on at least 2 platforms (macOS, Linux, or WSL2)
- [ ] Code reviewed following project review checklist
- [ ] Acceptance criteria validated manually
- [ ] Product owner approval obtained

## Additional Information
**Suggested Labels:** infrastructure, container, taskfile, cli, developer-experience
**Estimated Story Points:** 2 (Fibonacci scale)
**Dependencies:**
- US-020 (Create Production Containerfile) completed - **MUST** complete first, provides Containerfile
- Taskfile.yml exists from HLS-001 (Development Environment Setup) - Foundation established

**Related PRD Section:**
- PRD-000 Section 5.1 Functional Requirements (FR-13: Containerized deployment, FR-22: Unified CLI via Taskfile)
- PRD-000 Section 4.2 Problem Statement (Tool Command Fragmentation pain point)
- PRD-000 Decision D8: Unified CLI Interface (Taskfile standardization)

## Open Questions & Implementation Uncertainties

**No open implementation questions.** All technical approaches clear from PRD-000 and CLAUDE-tooling.md.

Taskfile syntax for container operations is straightforward. Podman/Docker runtime detection can use simple shell command checks (`which podman` or `which docker`). Port mapping and environment variable loading are standard container runtime features with well-documented syntax.

Implementation can proceed directly following Taskfile best practices from CLAUDE-tooling.md without requiring spike investigation or tech lead consultation.

---

**Document Version:** v1.0
**Generated By:** Backlog Story Generator v1.5
**Generation Date:** 2025-10-15
**Parent:** HLS-005 Containerized Deployment Enabling Production Readiness v1.0
**Story Sequence:** 2 of 6 in HLS-005 decomposition

---

## Traceability Notes

**Source Artifacts:**
- **Parent HLS:** HLS-005 Containerized Deployment Enabling Production Readiness v1.0
  - Decomposition Plan: Story 2 (lines 294-296)
  - Primary User Flow: Developer Builds and Runs Application in Production Container (lines 121-143, mentions `task container:build` and `task container:run`)
  - User Interactions: "Builds production container images using `task container:build` command" (line 180)
- **Parent PRD:** PRD-000 Project Foundation & Bootstrap Infrastructure v3.0
  - FR-13: Containerized deployment configuration with Podman (line 182)
  - FR-22: Unified CLI interface via Taskfile for all development operations (line 191)
  - Problem Statement: Tool Command Fragmentation pain point (line 93)
  - Decision D8: Unified CLI Interface - Taskfile standardization (lines 637-642)
- **Implementation Research:** AI_Agent_MCP_Server_implementation_research.md
  - §2.1: Python 3.11+ Technology Stack (container runtime context)
  - §2.2: FastAPI Framework (container configuration for FastAPI application)

**Quality Validation:**
- ✅ Story title action-oriented and specific ("Configure Container Build and Run Tasks in Taskfile")
- ✅ Detailed requirements clearly stated (2 primary tasks with runtime detection, environment handling)
- ✅ Acceptance criteria highly specific and testable (7 scenarios covering build, run, discovery, fallback, errors)
- ✅ Technical notes reference Implementation Research sections (§2.1, §2.2)
- ✅ Technical specifications include Taskfile task definitions (commands, variables, features)
- ✅ Story points estimated (2 SP)
- ✅ Testing strategy defined (manual validation via acceptance criteria, cross-platform testing)
- ✅ Dependencies identified (US-020 must complete first, Taskfile from HLS-001)
- ✅ Open Questions capture implementation uncertainties (none - all approaches clear)
- ✅ Implementation-adjacent: Describes task structure without prescribing exact Taskfile.yml syntax
- ✅ Sprint-ready: Can be completed in <1 day by single developer
- ✅ CLAUDE.md Alignment: References CLAUDE-tooling.md and CLAUDE-architecture.md appropriately
- ✅ Implementation Tasks Evaluation: Clear decision (No Tasks Needed) with rationale based on SDLC Section 11 criteria
