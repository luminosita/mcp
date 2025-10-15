# User Story: Create Production Containerfile with Multi-Stage Build

## Metadata
- **Story ID:** US-020
- **Title:** Create Production Containerfile with Multi-Stage Build
- **Type:** Feature
- **Status:** Draft
- **Priority:** High - Foundation story, must complete first to establish container deployment capability
- **Parent PRD:** PRD-000
- **Parent High-Level Story:** HLS-005 (Containerized Deployment Enabling Production Readiness)
- **Functional Requirements Covered:** FR-13
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** PRD-000: Project Foundation & Bootstrap Infrastructure
- **Link:** /artifacts/prds/PRD-000_project_foundation_bootstrap_v3.md
- **PRD Section:** Section 5.1 - Functional Requirements
- **Functional Requirements Coverage:**
  - **FR-13:** Containerized deployment configuration with Podman (Docker alternative)

**Parent High-Level Story:** HLS-005: Containerized Deployment Enabling Production Readiness
- **Link:** /artifacts/hls/HLS-005_containerized_deployment_configuration_v1.md
- **HLS Section:** Section "Decomposition into Backlog Stories" - Story 1

## User Story
As a software engineer deploying the AI Agent MCP Server to production,
I want an optimized production Containerfile with multi-stage build,
So that I can build minimal, secure container images for production deployment.

## Description
Create a production-ready Containerfile (Dockerfile-compatible) that uses multi-stage build pattern to produce an optimized container image. The Containerfile must follow security best practices including non-root user execution and minimal base image selection. The final production image should be optimized for size (<500MB target) and security, containing only runtime dependencies required for the application.

This is the foundational story for HLS-005, establishing the container image that enables all subsequent containerized deployment workflows.

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§2.1: Python 3.11+ Technology Stack:** Container uses Python 3.11+ as base runtime for modern type hints and async improvements
  - **Implementation:** Use `python:3.11-slim` as minimal base image providing Python runtime without unnecessary packages
- **§2.2: FastAPI Framework:** Container configured for FastAPI application deployment with Uvicorn ASGI server
  - **Implementation:** Include uvicorn[standard] in production dependencies for optimal async performance

**Anti-Patterns Avoided:**
- **Bloated Container Images:** Multi-stage build separates build-time dependencies from runtime, preventing inclusion of unnecessary packages in production image
- **Root User Execution:** Production stage runs as non-root user reducing attack surface if container compromised

**Performance Considerations:**
- **Image Size Optimization:** Target <500MB final image size through multi-stage build and minimal base image selection
- **Build Speed:** Leverage layer caching by ordering Containerfile instructions from least to most frequently changed

## Functional Requirements
- Containerfile creates production-ready image using multi-stage build pattern
- Build stage installs all build-time dependencies (compilers, build tools)
- Production stage contains only runtime dependencies and application code
- Final image size optimized to <500MB (typical for Python applications)
- Container runs application as non-root user for security
- Container uses minimal base image (python:3.11-slim) reducing attack surface
- Containerfile compatible with both Podman and Docker runtimes
- Application entry point configured as container CMD/ENTRYPOINT
- Health check configuration included in Containerfile

## Non-Functional Requirements
- **Performance:** Container image build completes in <5 minutes on standard development hardware
- **Security:**
  - Non-root user execution (application runs as UID 1000)
  - Minimal base image reduces vulnerability surface
  - No secrets embedded in image layers
- **Reliability:**
  - Deterministic builds (same input produces identical image)
  - Layer caching optimizes rebuild performance
- **Maintainability:**
  - Containerfile includes comments explaining build stages
  - Follows standard multi-stage build conventions
- **Portability:** Compatible with Podman 4.0+ (primary) and Docker 20.10+ (alternative)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story references established implementation standards from specialized CLAUDE.md files, supplementing with story-specific technical guidance.

### Implementation Guidance

Create Containerfile at project root with multi-stage build structure:

**Stage 1: Builder (Build-time dependencies)**
- Base: `python:3.11-slim` as builder stage
- Install build dependencies: gcc, build-essential for compiling Python packages
- Copy `pyproject.toml` and `uv.lock` for dependency installation
- Install all dependencies including build requirements using uv
- Copy application source code (`src/`)

**Stage 2: Production (Runtime only)**
- Base: `python:3.11-slim` as production stage
- Create non-root user (appuser, UID 1000)
- Copy only installed Python packages from builder stage (virtual environment)
- Copy application source code from builder stage
- Set working directory to `/app`
- Switch to non-root user
- Configure health check endpoint
- Set CMD to run application: `CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]`

**References to Implementation Standards:**
- **CLAUDE-tooling.md:** Containerfile will integrate with Taskfile commands (`task container:build`, `task container:run`) - Task implementation in US-021
- **CLAUDE-architecture.md:** Follow project structure with `src/` layout for application code
- **CLAUDE-typing.md:** Application code uses Python 3.11+ type hints, no impact on Containerfile but validates runtime compatibility

**Note:** Treat CLAUDE.md content as authoritative - Containerfile supplements with container-specific implementation details.

### Technical Tasks
- Create `Containerfile` at project root following multi-stage build pattern
- Define builder stage with build-time dependencies (gcc, build-essential, uv)
- Define production stage with minimal runtime dependencies
- Configure non-root user (appuser, UID 1000) for production stage
- Copy only necessary artifacts from builder to production (Python packages, application code)
- Configure application entry point (CMD) to run FastAPI with Uvicorn
- Add HEALTHCHECK instruction for container health monitoring
- Document Containerfile with inline comments explaining each stage
- Test build with both Podman and Docker to verify compatibility

## Acceptance Criteria

**Format:** Gherkin (Given-When-Then) for scenario-based validation

### Scenario 1: Containerfile builds successfully with multi-stage pattern
**Given** project repository contains Containerfile at root
**When** developer executes `podman build -t ai-agent-mcp-server:latest .`
**Then** build completes successfully without errors
**And** build uses two stages (builder and production)
**And** build completes within 5 minutes

### Scenario 2: Production image size optimized
**Given** container image has been built
**When** developer checks image size with `podman images ai-agent-mcp-server:latest`
**Then** image size is less than 500MB
**And** production stage contains only runtime dependencies (no build tools)

### Scenario 3: Container runs as non-root user
**Given** container image has been built
**When** developer inspects container with `podman inspect ai-agent-mcp-server:latest`
**Then** container USER is configured as non-root (appuser, UID 1000)
**And** container does not run as root (UID 0)

### Scenario 4: Container application starts successfully
**Given** container image has been built
**When** developer runs container with `podman run -p 8000:8000 ai-agent-mcp-server:latest`
**Then** application starts without errors
**And** application listens on port 8000
**And** health check endpoint responds within 10 seconds

### Scenario 5: Containerfile compatible with Docker alternative
**Given** project repository contains Containerfile
**When** developer executes `docker build -t ai-agent-mcp-server:latest .`
**Then** build completes successfully using Docker runtime
**And** resulting image functions identically to Podman-built image

### Scenario 6: Container layer caching optimized
**Given** container has been built once
**When** developer makes minor code change and rebuilds
**Then** build reuses cached layers for dependency installation
**And** rebuild completes faster than initial build (<2 minutes)

### Scenario 7: No secrets embedded in image
**Given** container image has been built
**When** developer inspects image layers with `podman history ai-agent-mcp-server:latest`
**Then** no environment variables contain secrets
**And** no secret files are embedded in layers
**And** `.env` files are not copied to image

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 5 SP - At threshold but straightforward implementation
- **Developer Count:** Single developer - No coordination overhead
- **Domain Span:** Single domain (container configuration) - No cross-domain complexity
- **Complexity:** Medium - Multi-stage Containerfile is standard pattern with established practices, not novel architecture
- **Uncertainty:** Low - Clear path using well-documented multi-stage build pattern per Implementation Research §2.1-2.2
- **Override Factors:** None applicable
  - Not cross-domain (single Containerfile)
  - Not high uncertainty (standard pattern)
  - Not unfamiliar technology (Docker/Podman standard tools)
  - Not security-critical at file level (security requirements clear and standard)
  - Not multi-system integration (single artifact)

**Conclusion:** This is a straightforward 5 SP story with a single developer implementing a well-understood multi-stage build pattern. Creating separate TASK-XXX artifacts would add overhead without coordination benefit. Developer can complete story in 1-2 days following standard Containerfile best practices.

## Definition of Done
- [ ] Containerfile created at project root with multi-stage build (builder + production stages)
- [ ] Containerfile builds successfully with Podman without errors
- [ ] Containerfile builds successfully with Docker without errors (compatibility verified)
- [ ] Production image size < 500MB validated
- [ ] Non-root user configured (appuser, UID 1000) verified with `podman inspect`
- [ ] Application starts successfully in container and listens on port 8000
- [ ] Health check endpoint responds correctly within 10 seconds
- [ ] Containerfile includes inline comments documenting each stage
- [ ] Build layer caching tested (rebuild after minor change completes in <2 minutes)
- [ ] No secrets embedded in image layers verified
- [ ] Code reviewed following project review checklist
- [ ] Unit tests written for container build process validation (if applicable)
- [ ] Documentation updated (CONTRIBUTING.md or DEPLOYMENT.md references Containerfile)
- [ ] Acceptance criteria validated manually
- [ ] Product owner approval obtained

## Additional Information
**Suggested Labels:** infrastructure, container, docker, podman, deployment, foundation
**Estimated Story Points:** 5 (Fibonacci scale)
**Dependencies:**
- HLS-001 (Development Environment Setup) completed - Provides Taskfile foundation for container tasks (US-021)
- HLS-003 (Application Skeleton Implementation) completed - Provides application code to containerize

**Related PRD Section:**
- PRD-000 Section 5.1 Functional Requirements (FR-13: Containerized deployment configuration)
- PRD-000 Section 6 Technical Considerations - Architecture (Container workflow diagram)

## Open Questions & Implementation Uncertainties

**No open implementation questions.** All technical approaches clear from Implementation Research and PRD-000.

The multi-stage build pattern for Python containers is well-established with extensive documentation. Security best practices (non-root user, minimal base image) are standard. Podman/Docker compatibility is straightforward as Podman is Docker-compatible by design.

Implementation can proceed directly following standard patterns without requiring spike investigation or tech lead consultation.

---

**Document Version:** v1.0
**Generated By:** Backlog Story Generator v1.5
**Generation Date:** 2025-10-15
**Parent:** HLS-005 Containerized Deployment Enabling Production Readiness v1.0
**Story Sequence:** 1 of 6 in HLS-005 decomposition

---

## Traceability Notes

**Source Artifacts:**
- **Parent HLS:** HLS-005 Containerized Deployment Enabling Production Readiness v1.0
  - Decomposition Plan: Story 1 (lines 290-293)
  - Primary User Flow: Developer Builds and Runs Application in Production Container (lines 121-143)
  - Acceptance Criterion 1: Production Container Image Builds Successfully (lines 207-214)
- **Parent PRD:** PRD-000 Project Foundation & Bootstrap Infrastructure v3.0
  - FR-13: Containerized deployment configuration with Podman (line 182)
  - Technical Constraints: Podman primary runtime, Docker alternative (line 540)
- **Implementation Research:** AI_Agent_MCP_Server_implementation_research.md
  - §2.1: Python 3.11+ Technology Stack (minimal base image guidance)
  - §2.2: FastAPI Framework (Uvicorn configuration for container)

**Quality Validation:**
- ✅ Story title action-oriented and specific ("Create Production Containerfile with Multi-Stage Build")
- ✅ Detailed requirements clearly stated (multi-stage build, non-root user, <500MB target)
- ✅ Acceptance criteria highly specific and testable (7 scenarios covering build, size, security, compatibility)
- ✅ Technical notes reference Implementation Research sections (§2.1, §2.2)
- ✅ Technical specifications include container configuration details (stages, user, entry point)
- ✅ Story points estimated (5 SP)
- ✅ Testing strategy defined (manual validation of container build and runtime)
- ✅ Dependencies identified (HLS-001, HLS-003)
- ✅ Open Questions capture implementation uncertainties (none - all approaches clear)
- ✅ Implementation-adjacent: Hints at multi-stage approach without prescribing exact Containerfile syntax
- ✅ Sprint-ready: Can be completed in 1 sprint (1-2 days for single developer)
- ✅ CLAUDE.md Alignment: References CLAUDE-tooling.md, CLAUDE-architecture.md, CLAUDE-typing.md appropriately
- ✅ Implementation Tasks Evaluation: Clear decision (No Tasks Needed) with rationale based on SDLC Section 11 criteria
