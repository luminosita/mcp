# PRD: MCP Server SDLC Framework Integration

## Metadata
- **PRD ID:** PRD-006
- **Author:** Product Manager + Tech Lead
- **Date:** 2025-10-18
- **Version:** 3.0
- **Status:** Draft
- **Parent Epic:** EPIC-006
- **Informed By Business Research:** /artifacts/research/AI_Agent_MCP_Server_business_research.md

## Parent Artifact Context

**Parent Epic:** [EPIC-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v2.md`
- **Epic Scope Coverage:** This PRD addresses the complete epic scope - migration of SDLC framework components (CLAUDE.md files, artifacts, generators, templates) to MCP resources and tools, establishing the AI Agent MCP Server as a centralized framework infrastructure provider
- **Epic Acceptance Criteria Mapping:**
  - **Criterion 1** (MCP Resources Migration): Covered by Features 1-3, FR-01 through FR-12
  - **Criterion 2** (MCP Tools Functional Equivalence): Covered by Features 4-6, FR-13 through FR-25
  - **Criterion 3** (Token Cost Reduction): Measured via NFR-Performance-02
  - **Criterion 4** (Multi-Project Validation): Covered by NFR-Scalability-01 and FR-17, FR-21

## Research References

### Business Research
**Document:** /artifacts/research/AI_Agent_MCP_Server_business_research.md

**Applied Insights:**
- **§1.1: Integration Fragmentation:** Addresses M×N scaling problem by centralizing SDLC framework as MCP resources, reducing per-project setup from 2-3 days to <4 hours
- **§3.1: Production Deployment Guides:** Gap in production patterns directly addressed by establishing reference architecture for MCP framework infrastructure
- **§4.1: Project Management Integration:** Demonstrates MCP capabilities (resources, tools, prompts) that will enable EPIC-001 (Project Management Integration)
- **§5.1: Market Positioning:** Positions product as "Production-Ready AI Agent Infrastructure" through practical demonstration of advanced MCP usage beyond basic protocol compliance

## Executive Summary

The AI Agent MCP Server currently implements MCP protocol basics (EPIC-000 established foundation), but the SDLC planning framework remains entirely file-based with local Git repository access. This creates framework duplication across projects, AI inference overhead for path resolution and validation, unbounded TODO.md file growth, and maintenance fragmentation across repositories.

This PRD defines requirements for migrating the SDLC framework to MCP-native architecture using resources (CLAUDE.md files, templates, shared artifacts), prompts (artifact generators), and deterministic Python/Go tools (validation, path resolution, task tracking, ID management). The solution eliminates framework duplication, reduces token consumption by 40-60%, and enables multi-language/multi-project scalability while maintaining zero functionality loss compared to local file approach.

**Business Impact:** Reduces new project setup time from 2-3 days to <4 hours (>80% reduction), centralizes framework maintenance to single update point instead of N×M repository synchronization, and enables framework reuse across Python, Go, and future language projects. Validates MCP Server's production readiness as infrastructure platform (critical step between EPIC-000 foundation and EPIC-001 external integration).

## Background & Context

### Business Context
The AI Agent MCP Server project has completed EPIC-000 (Project Foundation & Bootstrap), establishing functional MCP Server infrastructure with example tool implementation. EPIC-001 (Project Management Integration) is planned next to integrate with external systems (JIRA, Linear). However, the current SDLC framework architecture creates a critical gap:

- **Current State:** Framework components (CLAUDE.md orchestration, artifact generators, templates, validation) live as local files in Git repository, accessed via Claude Code's Read tool
- **Problem:** New projects must duplicate all framework files, creating synchronization overhead, version drift, and manual ID tracking across repositories
- **Blocking Issue:** Cannot efficiently scale to multiple projects or languages with current file-based approach

EPIC-006 bridges the foundation (EPIC-000) and integration (EPIC-001) phases by refactoring the framework into MCP-native architecture, validating that the infrastructure can support production-grade framework capabilities before adding external system complexity.

### User Research
**Primary Persona (from Business Research §Appendix A):** Enterprise Development Team Lead
- **Pain Point:** Must maintain consistent SDLC practices across 5-10 concurrent projects
- **Current Friction:** Manually syncs framework updates across project repositories, leading to version drift and inconsistent practices
- **Desired Outcome:** Single source of truth for framework components with automatic propagation to all projects

### Market Analysis
Per Business Research §2.3, competitive MCP implementations focus on protocol compliance with basic tool examples. This PRD differentiates through "advanced MCP usage demonstration":
- **Reference implementations:** Protocol mechanics only, minimal production features
- **Enterprise platforms:** Full-stack solutions but costly and opaque
- **This solution:** Production-ready framework infrastructure showcasing MCP resources, prompts, and deterministic tools for quantifiable business value (time savings, cost reduction)

## Problem Statement

### Current State
The SDLC framework operates entirely on local file access with AI inference for critical operations:

1. **Framework Duplication:** Each project copies 30+ CLAUDE.md files, generators, templates from reference repository
2. **AI Inference Overhead:** Path resolution (`artifacts/epics/EPIC-{XXX}_{slug}_v{N}.md`), validation rules (25-criterion checklists), and artifact ID assignment rely on AI inference, consuming excessive tokens and introducing 20-30% error rates
3. **TODO.md Growth:** Task tracking file grows with every completed task, burning ~5-10k tokens on every Claude Code interaction as historical data accumulates
4. **Maintenance Fragmentation:** Framework updates require synchronizing N project repositories × M framework files
5. **Language Lock-In:** Python-specific CLAUDE.md files cannot be reused for Go/Rust projects without significant rework

**Quantified Pain Points (from EPIC-006):**
- Setup Time: 2-3 days per new project to copy and configure framework
- Token Overhead: 40-60% token waste on repeated file parsing and inference
- Error Rate: 20-30% errors in path resolution and validation due to AI inference
- Maintenance: N×M update operations for framework changes (N=projects, M=files)

### Desired State
SDLC framework components accessible through MCP protocol:

- **MCP Resources:** CLAUDE.md files, templates, shared artifacts served by MCP Server (zero local duplication)
- **MCP Prompts:** Artifact generators (epic-generator, prd-generator, backlog-story-generator, etc.) exposed as MCP prompts
- **MCP Tools:** Deterministic Python/Go scripts for validation (checklist evaluation), path resolution (pattern→file), task tracking (database-backed API), and ID management (reserve/allocate)
- **Main CLAUDE.md:** Refactored as pure orchestrator directing to MCP resources and tools
- **Local Commands:** `/generate` and `/refine` commands remain in `.claude/commands/` as local orchestration layer

**Benefits:**
- Setup: <4 hours per project (>80% reduction)
- Token Cost: 40-60% reduction through optimized MCP resource loading
- Error Rate: <5% through deterministic tool validation
- Maintenance: Single central update propagates automatically

### Impact if Not Solved
**User Impact:**
- Development teams cannot efficiently scale to 5+ concurrent projects (synchronization overhead becomes unmanageable)
- Framework version drift causes inconsistent practices, compliance risks, and quality degradation across projects
- Excessive token consumption on repeated framework file loading impacts AI API budgets and interaction latency

**Business Impact:**
- Cannot credibly position as "production-ready infrastructure" if own framework doesn't use MCP capabilities
- Blocks EPIC-001 (Project Management Integration) adoption by teams with multiple concurrent projects
- Limits market opportunity to single-project/single-language teams, missing enterprise segment (primary target market per Business Research §2.1)

## Goals & Success Metrics

| Goal | Metric | Target | Measurement Method |
|------|---------|--------|-------------------|
| **Reduce Framework Setup Time** | Time from repository creation to first artifact generation | <4 hours (baseline: 2-3 days) | Project onboarding survey tracking setup duration per new project |
| **Reduce Token Cost** | AI API token consumption for typical workflows | ≥40% reduction vs. baseline | Token usage telemetry for 10 representative workflows (epic generation, PRD creation, story breakdown) measured pre/post migration |
| **Improve Validation Accuracy** | Error rate for path resolution and validation | <5% (baseline: 20-30% AI inference errors) | MCP tool execution logs tracking validation failures (30-day rolling average) |
| **Centralize Maintenance** | Framework update propagation | Single central update vs. N repository updates | Measure time to propagate framework change (e.g., new validation rule) to all active projects |
| **Multi-Project Scalability** | Concurrent projects using shared framework | Support ≥5 concurrent projects without resource conflicts | Stress test with 5 parallel workflows, monitor for ID collisions, resource contention, error rate <1% |

## User Personas & Use Cases

### Persona 1: Enterprise Development Team Lead
- **Description:** Tech Lead managing 5-10 concurrent Python/Go microservice projects, each using SDLC framework for planning and implementation. 8+ years experience, values consistency, automation, and operational simplicity.
- **Needs:**
  - Consistent SDLC practices across all projects (same generators, templates, validation)
  - Minimal overhead for framework updates (no manual synchronization)
  - Visibility into task status across projects (centralized tracking)
- **Use Case:** Sarah leads 7 microservice projects. When EPIC-006 framework is updated with new validation rule for security compliance, she wants all 7 projects to automatically use updated rule without manual Git pulls or file copying. She runs `task tracking-status --project all` to see combined task progress across projects.

### Persona 2: Framework Maintainer (Core Team)
- **Description:** Senior engineer responsible for evolving SDLC framework based on team feedback and production learnings. 10+ years experience with enterprise development processes.
- **Needs:**
  - Single source of truth for framework components (eliminates version drift)
  - Ability to extend framework with new languages (Go, Rust) without duplicating Python-specific logic
  - Confidence that updates won't break existing projects (backward compatibility validation)
- **Use Case:** Alex receives feedback that generator validation checklists should include security criteria. He updates validation tool logic (Python script), deploys updated MCP Server, and immediately all projects use enhanced validation on next generator execution—zero client-side changes required.

### Persona 3: AI Agent (Claude Code Orchestrating SDLC)
- **Description:** AI agent executing SDLC workflows (generate epic, create PRD, break down stories). Requires deterministic operations and minimal token consumption.
- **Needs:**
  - Reliable path resolution without inference errors (path patterns→actual files)
  - Fast validation with clear pass/fail results (not subjective AI judgment)
  - Efficient context loading (load only necessary framework components, not entire file history)
- **Use Case:** Claude Code executes `/generate prd-generator` for PRD-006. It calls MCP tool `resolve_artifact_path(pattern="artifacts/epics/EPIC-{id}_*_v{version}.md", id=006, version=1)` which returns exact path `artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md` in 20ms (vs. 500ms+ for AI inference with potential errors). Loads only required EPIC-006 artifact via MCP resource (10k tokens) instead of full local file with Git history (25k tokens).

## Requirements

### Functional Requirements

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|-------------------|
| **FR-01** | MCP Server SHALL expose all implementation pattern files (sdlc-core.md, patterns-*.md) as named MCP resources with AI-agent-agnostic naming | Must-have | ✅ Client can request `mcp://resources/sdlc/core` and receive sdlc-core.md content<br>✅ Client can request `mcp://resources/patterns/python/core` and receive patterns-core.md for Python projects<br>✅ Client can request `mcp://resources/patterns/python/tooling` and receive patterns-tooling.md<br>✅ Resource list includes all pattern files: sdlc-core.md, patterns-core.md, patterns-tooling.md, patterns-testing.md, patterns-typing.md, patterns-validation.md, patterns-architecture.md (with language-specific subdirectories) |
| **FR-02** | MCP Server SHALL expose all artifact templates (prompts/templates/*.xml) as named MCP resources | Must-have | ✅ Client can request `mcp://resources/templates/prd-template` and receive prd-template.xml content<br>✅ Resource list includes all 10 template types (product-vision, initiative, epic, prd, hls, backlog-story, spike, adr, tech-spec, implementation-task) |
| **FR-03** | MCP Server SHALL expose shared artifacts (artifacts/**/*) as queryable MCP resources with filters by artifact type, status, and parent relationship | Should-have | ✅ Client can request `mcp://resources/artifacts/epic/006` and receive EPIC-006 content<br>✅ Client can query `mcp://resources/artifacts?type=epic&status=Approved` and receive list of approved epics<br>✅ Client can query `mcp://resources/artifacts?parent=EPIC-006` and receive all PRD/HLS children |
| **FR-04** | MCP Server SHALL refactor main CLAUDE.md into orchestrator (remains local) + SDLC workflow instructions (new prompts/CLAUDE/sdlc-core.md served as MCP resource) | Must-have | ✅ Local CLAUDE.md reduced to <200 lines (orchestration only, no SDLC content)<br>✅ sdlc-core.md contains all artifact dependency flow, generator execution, refinement workflow instructions<br>✅ Functionality equivalent pre/post split (validation test suite) |
| **FR-05** | MCP Server SHALL expose all artifact generators (prompts/*-generator.xml) as MCP prompts using URL pattern `mcp://prompts/generator/{artifact_name}` | Must-have | ✅ Client can execute MCP prompt `mcp://prompts/generator/epic` (maps to epic-generator.xml)<br>✅ Client can execute MCP prompt `mcp://prompts/generator/prd` (maps to prd-generator.xml)<br>✅ All 10 generator types exposed: product-vision, initiative, epic, prd, hls, backlog-story, spike, adr, tech-spec, implementation-task |
| **FR-06** | MCP Server SHALL provide `validate_artifact` tool that accepts artifact content and validation checklist ID, returning pass/fail results with criterion-level details | Must-have | ✅ Tool accepts artifact text + checklist ID (e.g., "prd_validation_v1")<br>✅ Returns JSON: `{passed: true/false, results: [{id: "CQ-01", passed: true, details: "..."}]}`<br>✅ Validation logic deterministic (same input → same output, no AI inference) |
| **FR-07** | MCP Server SHALL provide `resolve_artifact_path` tool that accepts path pattern with variables and returns exact file path or error if not found | Must-have | ✅ Input: `{pattern: "artifacts/epics/EPIC-{id}*v{version}.md", id: "006", version: 1}`<br>✅ Output: `{path: "artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md"}`<br>✅ Error if multiple matches or no match: `{error: "Multiple files match pattern", candidates: [...]}`<br>✅ Supports all artifact path patterns from CLAUDE.md Folder Structure section |
| **FR-08** | MCP Server SHALL provide `get_next_task` tool (integrated with Task Tracking microservice) that queries task tracking database and returns next pending task with context (ID, description, dependencies, inputs, expected outputs) | Must-have | ✅ Input: `{project_id: "ai-agent-mcp-server", status_filter: "pending"}`<br>✅ Output: `{task_id: "TASK-051", description: "Generate PRD-006", generator: "prd-generator", inputs: ["EPIC-006"], context: "New session CX required"}`<br>✅ Returns empty if no pending tasks: `{task_id: null, message: "No pending tasks"}`<br>✅ Tool exposed via MCP Server REST API integration |
| **FR-09** | MCP Server SHALL provide `update_task_status` tool (integrated with Task Tracking microservice) that updates task status (pending→in_progress→completed) and logs completion timestamp | Must-have | ✅ Input: `{task_id: "TASK-051", status: "completed", completion_notes: "PRD-006 v1 generated, 26/26 validation criteria passed"}`<br>✅ Updates database record with status, timestamp, notes<br>✅ Returns confirmation: `{success: true, updated_task: {...}}`<br>✅ Validates state transitions (cannot go completed→pending without explicit reset) |
| **FR-10** | MCP Server SHALL provide `get_next_available_id` tool (integrated with Task Tracking microservice) that queries ID registry database and returns next sequential ID for artifact type | Must-have | ✅ Input: `{artifact_type: "US"}`<br>✅ Output: `{artifact_type: "US", next_id: "US-028", last_assigned: "US-027"}`<br>✅ Guarantees uniqueness across concurrent requests (database transaction isolation)<br>✅ Supports all artifact types: VIS, INIT, EPIC, PRD, HLS, US, SPIKE, ADR, SPEC, TASK |
| **FR-11** | MCP Server SHALL provide `reserve_id_range` tool (integrated with Task Tracking microservice) that reserves contiguous ID range for batch artifact generation (e.g., HLS decomposition generating 6 backlog stories) | Must-have | ✅ Input: `{artifact_type: "US", count: 6}`<br>✅ Output: `{artifact_type: "US", reserved_ids: ["US-028", "US-029", "US-030", "US-031", "US-032", "US-033"], expires_at: "2025-10-17T14:30:00Z"}`<br>✅ IDs locked in database with expiration (15 min default, configurable)<br>✅ Expired reservations released for reuse if not confirmed within timeout |
| **FR-12** | Main CLAUDE.md SHALL be refactored to orchestrate MCP Server integration, directing Claude Code to use MCP resources/prompts/tools instead of local file access | Must-have | ✅ CLAUDE.md instructions reference MCP resources for SDLC workflow (not local file paths)<br>✅ Generator execution instructions call MCP prompts (epic-generator, prd-generator, etc.)<br>✅ Validation instructions call `validate_artifact` MCP tool (not AI inference)<br>✅ Path resolution instructions call `resolve_artifact_path` MCP tool (not manual file search) |
| **FR-13** | MCP Server SHALL maintain backward compatibility mode allowing projects to opt-in to MCP framework incrementally (coexist with local file approach during transition) | Should-have | ✅ Configuration flag `use_mcp_framework: true/false` in project config<br>✅ When false, fall back to local file access (CLAUDE.md, generators, templates)<br>✅ When true, use MCP resources/tools exclusively<br>✅ Validation test suite passes in both modes (functional equivalence) |
| **FR-14** | Task Tracking microservice SHALL provide REST API with endpoints: `GET /tasks/next`, `PUT /tasks/{id}/status`, `GET /tasks?project={id}&status={filter}`, `GET /ids/next?type={artifact_type}`, `POST /ids/reserve` | Must-have | ✅ `GET /tasks/next?project=ai-agent-mcp-server&status=pending` returns next pending task<br>✅ `PUT /tasks/TASK-051/status` with body `{status: "completed", notes: "..."}` updates task<br>✅ `GET /tasks?project=ai-agent-mcp-server&status=completed` returns list of completed tasks<br>✅ `GET /ids/next?type=US` returns `{next_id: "US-028"}`<br>✅ `POST /ids/reserve` with body `{type: "US", count: 6}` returns `{reserved_ids: ["US-028"...], expires_at: "..."}`<br>✅ `POST /ids/confirm` with body `{reservation_id: "abc123"}` confirms reservation<br>✅ API authenticated via API key or JWT token |
| **FR-15** | Task Tracking microservice SHALL ensure global ID uniqueness across concurrent requests from multiple projects using database transaction isolation (SERIALIZABLE level) | Must-have | ✅ Stress test: 10 concurrent `get_next_available_id` requests for same artifact type return unique IDs (no duplicates)<br>✅ Stress test: 5 concurrent `reserve_id_range` requests with overlapping ranges return non-overlapping ID sets<br>✅ Database transaction log shows SERIALIZABLE isolation level enforcement |
| **FR-16** | MCP Server SHALL expose validation checklists as structured data resources (JSON format) allowing dynamic checklist updates without MCP Server code changes | Should-have | ✅ Client can request `mcp://resources/validation/prd_checklist_v1` and receive JSON: `[{id: "CQ-01", category: "content", description: "...", validation_type: "manual/auto"}]`<br>✅ `validate_artifact` tool loads checklist from resource (not hardcoded)<br>✅ Checklist updates deployed via resource file change (no code deployment) |
| **FR-17** | MCP Server SHALL log all tool invocations (validation, path resolution, task tracking, ID management) with timestamp, input parameters, execution duration, and result status for observability | Should-have | ✅ Logs include: `{timestamp, tool_name, input_params, duration_ms, success: true/false, error_message}`<br>✅ Logs queryable via API or log aggregation system (structured JSON format)<br>✅ Logs retained for ≥30 days for error analysis and performance monitoring |
| **FR-18** | Task Tracking microservice SHALL support multiple independent project databases (project-specific isolation) with project_id parameter for all API calls | Must-have | ✅ `GET /tasks/next?project=ai-agent-mcp-server` queries ai-agent-mcp-server database<br>✅ `GET /tasks/next?project=other-project` queries other-project database (isolated data)<br>✅ Database schema includes project_id foreign key with strict isolation enforcement |
| **FR-19** | Task Tracking microservice SHALL support multiple independent project ID registries (project-specific isolation) with project_id parameter for all API calls | Must-have | ✅ `GET /ids/next?project=ai-agent-mcp-server&type=US` queries ai-agent-mcp-server ID registry<br>✅ `GET /ids/next?project=other-project&type=US` queries other-project ID registry (independent sequences)<br>✅ Projects can have overlapping artifact IDs (US-001 in both projects) without conflicts |
| **FR-20** | MCP Server SHALL implement resource caching with TTL (time-to-live) to reduce repeated file I/O for frequently accessed CLAUDE.md files and generators | Should-have | ✅ First request for `mcp://resources/claude/sdlc` loads from disk and caches (TTL: 5 minutes)<br>✅ Subsequent requests within 5 minutes served from cache (latency <10ms vs. 50ms disk I/O)<br>✅ Cache invalidation on TTL expiration or explicit invalidation API call |
| **FR-21** | MCP Server SHALL expose artifact metadata (ID, type, status, parent_id, created_at, updated_at) as queryable resources separate from full artifact content for efficient filtering and discovery | Should-have | ✅ Client can request `mcp://resources/artifacts/metadata?type=epic&status=Approved` and receive lightweight metadata list (no full content)<br>✅ Metadata includes: `{id: "EPIC-006", type: "epic", title: "...", status: "Draft", parent_id: "INIT-001", created_at: "2025-10-16", file_path: "artifacts/epics/EPIC-006_..._v1.md"}`<br>✅ Metadata loading ≥10x faster than full artifact loading (benchmark validation) |
| **FR-22** | Validation tool SHALL support both automated validation (deterministic rules: template sections present, ID format correct) and manual validation flags (readability, clarity requiring human judgment) | Must-have | ✅ Automated criteria (e.g., "CQ-01: All template sections present") evaluated by script with pass/fail result<br>✅ Manual criteria (e.g., "CQ-12: Readability accessible to cross-functional team") flagged as `{passed: null, requires_manual_review: true}`<br>✅ Validation summary shows automated pass rate and list of manual review items |
| **FR-23** | MCP Server SHALL provide `store_artifact` tool that uploads generated artifacts to centralized storage accessible across projects | Should-have | ✅ Input: `{artifact_type: "epic", artifact_id: "EPIC-006", content: "...", metadata: {...}}`<br>✅ Stores artifact in shared repository or database<br>✅ Returns confirmation: `{success: true, uri: "mcp://resources/artifacts/epic/006"}`<br>✅ Stored artifacts queryable via FR-03 resource filters |
| **FR-24** | MCP Server SHALL provide `add_task` tool (integrated with Task Tracking microservice) that adds new tasks to queue after artifact generation, enabling automatic sub-artifact workflow initiation | Must-have | ✅ Input: `{tasks: [{artifact_id: "HLS-006", artifact_type: "hls", generator: "hls-generator", parent_id: "PRD-006", status: "pending"}]}`<br>✅ Calls Task Tracking microservice REST API `POST /tasks/batch`<br>✅ Returns confirmation: `{success: true, tasks_added: 6, task_ids: ["TASK-046", "TASK-047", ...]}`<br>✅ Tool exposed via MCP Server REST API integration |
| **FR-25** | All artifact generators SHALL evaluate whether sub-artifacts are required after generation and return appropriate metadata flags for automatic task queue population | Must-have | ✅ Generator output includes: `{requires_sub_artifacts: true/false, open_questions: true/false, required_artifacts_ids: ["HLS-006", "HLS-007", ...]}`<br>✅ Initiative generator evaluates Epic requirements<br>✅ Epic generator evaluates HLS requirements<br>✅ PRD generator evaluates HLS requirements<br>✅ HLS generator evaluates Backlog Story requirements<br>✅ Backlog Story generator evaluates Tech Spec/ADR/Spike requirements (case-by-case basis) |

### Non-Functional Requirements

#### Performance
- **NFR-Performance-01:** MCP resource loading latency SHALL be <100ms for 95th percentile requests (p95 <100ms) for CLAUDE.md files and generators (typical size: 10-50KB)
- **NFR-Performance-02:** MCP tool execution latency SHALL be <500ms for 95th percentile (p95 <500ms) for all tools (validation, path resolution, task tracking API calls, ID management API calls)
- **NFR-Performance-03:** Token consumption for typical SDLC workflow (epic generation, PRD creation, backlog story breakdown - 10 workflows) SHALL be reduced by ≥40% vs. baseline local file approach
- **NFR-Performance-04:** Task Tracking microservice SHALL support ≥100 requests/second (RPS) with p99 latency <200ms
- **NFR-Performance-05:** Task Tracking microservice ID management SHALL support ≥50 concurrent reservation requests with zero ID collisions (validated via stress test)

#### Scalability
- **NFR-Scalability-01:** System SHALL support ≥5 concurrent projects using shared MCP framework with zero resource conflicts, ID collisions, or performance degradation >10% vs. single-project baseline
- **NFR-Scalability-02:** Task Tracking microservice SHALL scale horizontally (add instances) to support ≥20 concurrent projects without database bottleneck (validated via load test)
- **NFR-Scalability-03:** MCP Server resource cache SHALL support ≥1000 cached resources (CLAUDE.md files, generators, templates, artifacts) with memory consumption <2GB

#### Availability
- **NFR-Availability-01:** MCP Server SHALL maintain ≥99.5% uptime during business hours (8am-6pm weekdays) measured over 30-day rolling window
- **NFR-Availability-02:** Task Tracking microservice SHALL implement health check endpoint (`/health`) returning status within 100ms
- **NFR-Availability-03:** MCP Server SHALL implement graceful degradation: if Task Tracking microservice unavailable, fall back to local file approach with warning message (no hard failure)

#### Security
- **NFR-Security-01:** Task Tracking microservice REST API SHALL require authentication via API key or JWT token (no unauthenticated access)
- **NFR-Security-02:** MCP Server SHALL validate all tool inputs against defined schemas (reject malformed requests with clear error messages)
- **NFR-Security-03:** Task Tracking microservice ID management SHALL prevent ID exhaustion attacks by rate-limiting reservation requests to ≤10 per minute per project (configurable)
- **NFR-Security-04:** Database credentials for Task Tracking microservice SHALL be stored in environment variables or secret management system (never hardcoded)

#### Observability
- **NFR-Observability-01:** MCP Server SHALL log all tool invocations with structured JSON format including timestamp, tool name, input parameters, duration, result status
- **NFR-Observability-02:** Task Tracking microservice SHALL expose metrics endpoint (`/metrics`) in Prometheus format including request count, latency histogram, error rate
- **NFR-Observability-03:** MCP Server SHALL provide dashboard showing: resource cache hit rate, tool execution success rate, average latency per tool, active projects count (updated every 60 seconds)
- **NFR-Observability-04:** Validation tool SHALL log all failed validation criteria with artifact ID, criterion ID, failure reason for debugging and framework improvement

#### Reliability
- **NFR-Reliability-01:** MCP Server SHALL implement retry logic for transient Task Tracking microservice failures (3 retries with exponential backoff: 100ms, 200ms, 400ms)
- **NFR-Reliability-02:** Database operations (task tracking, ID management) SHALL use transactions with rollback on failure (ACID compliance)
- **NFR-Reliability-03:** ID reservation expiration SHALL automatically release unused IDs after timeout (default: 15 minutes, configurable) to prevent ID exhaustion from abandoned workflows

#### Maintainability
- **NFR-Maintainability-01:** All MCP tools (validation, path resolution) SHALL have unit test coverage ≥80% and integration test coverage ≥60%
- **NFR-Maintainability-02:** Task Tracking microservice (Go) SHALL follow CLAUDE-core.md and CLAUDE-tooling.md standards for Go projects including linting (golangci-lint), testing (go test), and type safety
- **NFR-Maintainability-03:** MCP Server SHALL expose API documentation (OpenAPI/Swagger format) for all tools and resources auto-generated from code annotations

#### Compatibility
- **NFR-Compatibility-01:** MCP Server SHALL maintain backward compatibility with local file approach during transition period (3 months minimum) allowing projects to opt-in incrementally
- **NFR-Compatibility-02:** Generated artifacts using MCP approach SHALL be byte-identical to artifacts generated with local file approach (verified via diff on 10 sample artifacts)
- **NFR-Compatibility-03:** Main CLAUDE.md orchestration updates SHALL not break existing projects using local file approach (validated via regression test suite)

## User Experience

### User Flows

#### Flow 1: New Project Setup Using MCP Framework

```
1. Developer creates new project repository
2. Developer adds MCP Server connection configuration (server URL, authentication)
   └─ Config file: `.mcp/config.json` with `{server_url: "http://localhost:3000", use_mcp_framework: true}`
3. Developer creates minimal local CLAUDE.md orchestrator (50 lines)
   └─ References MCP resources: "See mcp://resources/claude/sdlc for SDLC workflow instructions"
4. Developer runs first generator: `claude-code "/generate epic-generator"`
   └─ AI Agent calls MCP prompt `mcp://prompts/epic-generator`
   └─ AI Agent calls MCP Server tool `resolve_artifact_path` to locate input artifacts
   └─ AI Agent fetches input artifacts from MCP resources
   └─ AI Agent executes prompt with input artifacts and generates epic artifact
5. AI Agent calls `validate_artifact` tool with epic content + validation checklist
   └─ Tool returns validation results: 25/25 criteria passed
6. Developer confirms artifact looks correct
7. AI Agent calls `update_task_status` tool to mark task completed
8. AI Agent calls MCP Server tool `store_artifact` to upload new epic artifact

**Time to first artifact:** <1 hour (vs. 2-3 days with local file setup)
```

#### Flow 2: Framework Maintainer Updates Validation Rules

```
1. Framework maintainer identifies new validation requirement (e.g., security compliance check)
2. Maintainer updates validation checklist JSON resource file
   └─ Adds new criterion: `{id: "SEC-01", category: "security", description: "Artifact references security review requirement if handling sensitive data"}`
3. Maintainer updates validation tool logic (Python script) to evaluate SEC-01
   └─ Deterministic rule: Check if artifact contains "[REQUIRES SECURITY REVIEW]" marker when data classification = sensitive
4. Maintainer deploys updated MCP Server with new validation logic
5. **All projects automatically use updated validation on next generator execution**
   └─ No client-side changes required
   └─ No Git pull/sync across N project repositories
6. Maintainer monitors validation logs to confirm new criterion evaluates correctly across projects

**Propagation time:** <1 minute (instant for all projects vs. hours/days for N repository synchronization)
```

#### Flow 3: Multi-Project Task Tracking

```
1. Tech Lead manages 5 concurrent projects (project-alpha, project-beta, project-gamma, project-delta, project-epsilon)
2. Each project configured with MCP task tracking: `{task_tracking_enabled: true, project_id: "project-alpha"}`
3. Claude Code calls `get_next_task` with project_id filter
   └─ For project-alpha: Returns `{task_id: "TASK-010", description: "Generate HLS-003"}`
   └─ For project-beta: Returns `{task_id: "TASK-005", description: "Implement authentication middleware"}`
4. Tech Lead runs `task tracking-status --project all` (custom CLI tool)
   └─ Queries task tracking API for all 5 projects
   └─ Returns consolidated view: "18 pending tasks across 5 projects, 42 completed this week"
5. Tech Lead identifies bottleneck: project-gamma has 8 pending tasks, all blocked
6. Tech Lead resolves blocker, updates task dependencies in database
7. Claude Code resumes workflow for project-gamma using `get_next_task`

**Visibility improvement:** Real-time cross-project status vs. manual TODO.md file review per project
```

### Wireframes/Mockups

**Note:** This is a backend infrastructure feature with CLI/API interactions (no GUI). User experience manifests through:
1. **Claude Code CLI:** Users interact via existing Claude Code interface (no new UI)
2. **MCP Server Logs:** Observability dashboard showing tool execution metrics (Grafana/similar - implementation detail for Tech Spec phase)
3. **Task Tracking CLI:** Optional CLI tool for tech leads (`task tracking-status --project all`) - future enhancement

## Technical Considerations

**HYBRID CLAUDE.md APPROACH:** This PRD references specialized CLAUDE-*.md standards as authoritative for implementation. Technical Considerations align with established patterns.

### Architecture

**High-Level Architecture:**

```
┌─────────────────────────────────────────────────────────────────────┐
│ Client Layer (Claude Code CLI)                                     │
├─────────────────────────────────────────────────────────────────────┤
│ Local CLAUDE.md (Orchestrator)                                     │
│ - Directs to MCP resources for SDLC workflow instructions          │
│ - Local commands: /generate, /refine (in .claude/commands/)        │
│ - Directs to MCP tools for validation, path resolution, tasks, IDs │
└─────────────────────────────────────────────────────────────────────┘
                              ↓ MCP Protocol (stdio/HTTP)
┌─────────────────────────────────────────────────────────────────────┐
│ MCP Server (Python)                                                │
├─────────────────────────────────────────────────────────────────────┤
│ MCP Resources Layer                                                │
│ - Implementation pattern files (sdlc-core.md, patterns-*.md)       │
│   └─ URLs: mcp://resources/sdlc/core, mcp://resources/patterns/*   │
│ - Templates (all artifact templates)                                │
│ - Artifacts (shared/reference artifacts, queryable by type/status) │
│                                                                     │
│ MCP Prompts Layer                                                  │
│ - Generators: epic, prd, hls, backlog-story, etc.                  │
│   └─ URL pattern: mcp://prompts/generator/{artifact_name}          │
│                                                                     │
│ MCP Tools Layer (Python)                                           │
│ - validate_artifact (input: artifact content + checklist ID)       │
│ - resolve_artifact_path (input: pattern + variables)               │
│ - store_artifact (input: artifact content + metadata)              │
│ - Integration with Task Tracking microservice (REST API calls):    │
│   └─ get_next_task, update_task_status, add_task                   │
│   └─ get_next_available_id, reserve_id_range                       │
└─────────────────────────────────────────────────────────────────────┘
                              ↓ REST API (HTTP/JSON)
┌─────────────────────────────────────────────────────────────────────┐
│ Task Tracking Microservice (Go)                                    │
├─────────────────────────────────────────────────────────────────────┤
│ REST API:                                                          │
│ - GET /tasks/next                                                  │
│ - PUT /tasks/{id}/status                                           │
│ - GET /tasks?project={id}&status={filter}                          │
│ - GET /ids/next?type={type}&project={id}                           │
│ - POST /ids/reserve                                                │
│ - POST /ids/confirm                                                │
│                                                                     │
│ Database: PostgreSQL                                               │
│ - Schema: tasks table                                              │
│   (task_id, project_id, status, inputs, outputs)                   │
│ - Schema: id_registry table                                        │
│   (artifact_type, project_id, last_id, reservations)               │
└─────────────────────────────────────────────────────────────────────┘
```

**Key Architectural Decisions:**
1. **AI-Agent-Agnostic Naming:** Implementation pattern files use generic names (sdlc-core.md, patterns-*.md) instead of Claude-specific names (CLAUDE-*.md) to support multiple AI agents
2. **Hybrid CLAUDE.md:** Main CLAUDE.md remains local (orchestration) but SDLC content migrated to MCP resource (sdlc-core.md)
3. **Single Microservice for State:** Task Tracking microservice (Go) handles both task tracking and ID management as a unified service, enabling independent deployment, scaling, and multi-language demonstration
4. **Deterministic Tools in Python:** Validation and path resolution as Python scripts (not Go) to minimize language context switching for MCP Server development (Python-first, add Go incrementally)
5. **REST API Integration:** MCP tools call Task Tracking microservice via REST API (not direct database access) for clean separation of concerns and protocol-agnostic integration
6. **Generators as MCP Prompts:** Artifact generators exposed as MCP prompts using URL pattern `mcp://prompts/generator/{artifact_name}`; local `/generate` and `/refine` commands remain in `.claude/commands/` as orchestration layer
7. **Sub-Artifact Evaluation:** All generators evaluate sub-artifact requirements and return metadata flags to enable automatic task queue population via `add_task` tool

**Alignment with Implementation Pattern Standards:**
- **patterns-architecture.md:** Follow established project structure for MCP Server (src/mcp_server/, src/tools/, src/resources/, tests/)
- **patterns-core.md:** Core development philosophy applies to all Python and Go components
- **Go microservice:** References Go-specific patterns-core.md and patterns-*.md (already available in `prompts/CLAUDE/go/`, to be renamed to patterns-*.md)

### Dependencies

#### System Dependencies
- **MCP Server (Python):**
  - Python 3.11+ runtime
  - MCP SDK (mcp-sdk package)
  - HTTP server framework (FastAPI or similar) for REST API endpoints
  - File system access for loading resources (CLAUDE.md files, generators, templates, artifacts)

- **Task Tracking Microservice (Go):**
  - Go 1.21+ runtime
  - PostgreSQL client library (pgx or similar)
  - HTTP router (chi, gin, or similar)

- **Database:**
  - PostgreSQL 15+ (task tracking and ID management schemas)
  - Database migration tool (goose, migrate, or similar)

#### External Dependencies
- **MCP Protocol:** Compliance with MCP specification version (check mcp-sdk compatibility)
- **Claude Code CLI:** Client must support MCP resource/prompt/tool protocol (stdio or HTTP transport)
- **Containerization (for deployment):** Docker/Podman for MCP Server and microservices (EPIC-000 established container infrastructure)

#### Implementation Standards (Reference CLAUDE.md Files)

**Python Components (MCP Server, validation tool, path resolution tool):**
- **CLAUDE-tooling.md (Python):** UV for dependency management, Ruff for linting/formatting, MyPy for type checking, pytest for testing, Taskfile for unified CLI
- **CLAUDE-testing.md (Python):** Testing strategy with ≥80% unit test coverage, integration tests for MCP resource/tool workflows, fixture patterns
- **CLAUDE-typing.md (Python):** Full type hints with mypy strict mode, Pydantic models for tool input/output schemas
- **CLAUDE-validation.md (Python):** Pydantic models for input validation, security patterns for file path sanitization
- **CLAUDE-architecture.md (Python):** Project structure following established patterns (src/, tests/, docs/)

**Go Components (Task Tracking microservice):**
- **CLAUDE-core.md (Go):** Available at `prompts/CLAUDE/go/CLAUDE-core.md` - provides Go best practices, project structure, and development philosophy
- **CLAUDE-tooling.md (Go):** Available at `prompts/CLAUDE/go/CLAUDE-tooling.md` - covers golangci-lint for linting, go test for testing, Taskfile integration, module management
- **CLAUDE-validation.md (Go):** Input validation, security patterns for file path sanitization
- **CLAUDE-architecture.md (Go):** Project structure following established patterns

**Note:** Language-specific CLAUDE.md files located in `prompts/CLAUDE/{language}/` subdirectories. Go-specific files are already available and ready for implementation phase.

**Treating CLAUDE.md as "Decisions Made":**
All Technical Considerations in this PRD supplement (not duplicate) CLAUDE.md standards. Implementation phase SHALL reference CLAUDE-*.md files as authoritative for tooling, testing, typing, validation, and architecture patterns.

### Technical Constraints

1. **MCP Protocol Compatibility:** Must remain compatible with MCP SDK version used by Claude Code CLI (version validation required during implementation)
2. **File System Access:** MCP Server requires read access to local Git repository for artifacts, generators, templates (migration to database-backed storage deferred to future phase)
3. **Database Hosting:** PostgreSQL database for Task Tracking microservice using containerized PostgreSQL (Docker Compose or Podman) per Decision D3
4. **Backward Compatibility Window:** Must maintain local file approach compatibility for ≥3 months during transition period (dual-mode operation)
5. **Token Budget:** MCP resource content must fit within Claude Code context window (200k tokens) - large artifacts may require chunking or summarization (deferred to implementation if needed)
6. **Language-Specific Resources:** CLAUDE.md files organized by language subdirectory (prompts/CLAUDE/python/, prompts/CLAUDE/go/) - MCP resource URIs must support language-specific paths
7. **Artifact Storage:** Individual resources approach per Decision D4 (`mcp://resources/artifacts/epic/000`)
8. **Checklist Versioning:** Hybrid approach per Decision D5 (default to latest, override with explicit version)

### Data Model

#### Task Tracking Database Schema (PostgreSQL)

```sql
-- Tasks table
CREATE TABLE tasks (
  task_id VARCHAR(20) PRIMARY KEY,        -- TASK-051
  project_id VARCHAR(100) NOT NULL,       -- ai-agent-mcp-server
  description TEXT NOT NULL,              -- Generate PRD-006
  generator_name VARCHAR(50),             -- prd-generator (NULL for non-generator tasks)
  status VARCHAR(20) NOT NULL,            -- pending | in_progress | completed
  inputs JSONB,                           -- ["EPIC-006"] (input artifact IDs)
  expected_outputs JSONB,                 -- ["PRD-006"] (output artifact IDs)
  context_notes TEXT,                     -- New session CX required
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,
  completion_notes TEXT,
  CONSTRAINT valid_status CHECK (status IN ('pending', 'in_progress', 'completed'))
);

CREATE INDEX idx_tasks_project_status ON tasks(project_id, status);
CREATE INDEX idx_tasks_status ON tasks(status);
```

#### ID Registry Database Schema (PostgreSQL)

```sql
-- ID registry table
CREATE TABLE id_registry (
  id SERIAL PRIMARY KEY,
  artifact_type VARCHAR(10) NOT NULL,     -- US, SPEC, TASK, etc.
  project_id VARCHAR(100) NOT NULL,       -- ai-agent-mcp-server
  last_assigned_id INTEGER NOT NULL,      -- 27 (for US-027)
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(artifact_type, project_id)
);

-- ID reservations table
CREATE TABLE id_reservations (
  reservation_id UUID PRIMARY KEY,
  artifact_type VARCHAR(10) NOT NULL,
  project_id VARCHAR(100) NOT NULL,
  reserved_ids JSONB NOT NULL,            -- ["US-028", "US-029", "US-030"]
  reserved_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP NOT NULL,
  confirmed BOOLEAN DEFAULT FALSE,
  CONSTRAINT valid_expiration CHECK (expires_at > reserved_at)
);

CREATE INDEX idx_reservations_expiry ON id_reservations(expires_at) WHERE confirmed = FALSE;
CREATE INDEX idx_reservations_project ON id_reservations(project_id, artifact_type);
```

#### MCP Resource Metadata (In-Memory Cache)

```python
@dataclass
class ResourceMetadata:
    uri: str                          # mcp://resources/claude/sdlc
    type: str                         # claude_md | generator | template | artifact
    file_path: str                    # prompts/CLAUDE/CLAUDE-sdlc.md
    size_bytes: int                   # 45000
    last_modified: datetime           # 2025-10-17T10:00:00Z
    cache_ttl_seconds: int            # 300 (5 minutes)
    cached_content: Optional[str]     # Cached file content (NULL if not cached)
    cache_expiry: Optional[datetime]  # When cache expires
```

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **MCP Protocol Version Incompatibility** | High (breaking change blocks all workflows) | Medium (protocol still evolving) | Pin MCP SDK version in requirements, monitor protocol changelog, implement version negotiation in MCP Server handshake, maintain compatibility layer for protocol updates |
| **Database Performance Bottleneck** | Medium (slows task tracking/ID management) | Low (simple queries, low volume) | Implement database connection pooling, add query performance monitoring, database indexes on frequently queried columns (project_id, status), load testing with 5 concurrent projects |
| **Token Cost Reduction Target Not Met** | Medium (business case weakened) | Low (deterministic loading reduces overhead significantly) | Baseline measurement before migration (10 workflows, record token usage), incremental optimization (profile token-heavy operations), revise targets if necessary based on real data |
| **Backward Compatibility Breaks Existing Projects** | High (blocks existing users) | Medium (refactoring risk) | Comprehensive regression test suite (50+ test cases covering all generator types), dual-mode operation (local file + MCP), phased rollout (internal project first, then expand), explicit opt-in flag (use_mcp_framework: true) |
| **Go Microservice Development Complexity** | Medium (delays implementation) | Low (Go-specific CLAUDE.md files already available) | Reference existing Go CLAUDE-core.md and CLAUDE-*.md standards at `prompts/CLAUDE/go/`, start with simple REST API implementation, expand incrementally |
| **ID Collision in Concurrent Requests** | High (data corruption, duplicate IDs) | Low (database transactions prevent this) | Database SERIALIZABLE isolation level for ID allocation queries, stress testing with 50 concurrent requests, automated testing in CI/CD pipeline, monitoring for collision events (should be zero) |
| **MCP Server Single Point of Failure** | High (blocks all projects if server down) | Medium (deployment/infrastructure risk) | Graceful degradation (fall back to local file approach with warning), health check monitoring with alerts, implement MCP Server redundancy (load balancer + 2 instances) in production, clear runbook for MCP Server recovery |

## Timeline & Milestones

### Phase 1: MCP Resources Migration (Weeks 1-2)
**Deliverables:**
- Refactor main CLAUDE.md into orchestrator (local) + CLAUDE-sdlc.md (MCP resource)
- Migrate all CLAUDE-*.md files to MCP resources with language-specific subdirectory structure
- Migrate templates to MCP resources
- Implement MCP resource caching with TTL
- Validation: Resource loading latency <100ms (p95), cache hit rate >70%

**Success Criteria:**
- ✅ 15+ CLAUDE.md resources accessible via MCP protocol
- ✅ 10 template resources accessible
- ✅ Resource loading latency meets NFR-Performance-01 target
- ✅ Unit tests passing for resource loading and caching logic

### Phase 2: MCP Prompts - Generators Migration (Week 3)
**Deliverables:**
- Migrate all 10 artifact generators to MCP prompts (epic-generator, prd-generator, etc.)
- Update local `/generate` command to call MCP prompts
- Integration testing for generator execution via MCP prompts
- Validation: Generator prompts execute successfully with same outputs as local file approach

**Success Criteria:**
- ✅ 10 generator prompts accessible via MCP protocol
- ✅ `/generate` command successfully orchestrates MCP prompt calls
- ✅ Generated artifacts byte-identical to local file approach (NFR-Compatibility-02)

### Phase 3: MCP Tools - Validation and Path Resolution (Week 4)
**Deliverables:**
- Implement `validate_artifact` tool (Python) with deterministic validation logic
- Implement `resolve_artifact_path` tool (Python) with pattern matching and variable substitution
- Implement `store_artifact` tool (Python) for centralized artifact storage
- Migrate validation checklists to JSON resources (dynamic loading)
- Implement tool invocation logging for observability
- Validation: Error rate <5% vs. AI inference baseline, tool execution <500ms (p95)

**Success Criteria:**
- ✅ Validation tool evaluates 25-criterion PRD checklist with 100% accuracy on 10 test artifacts
- ✅ Path resolution tool resolves all 10 artifact path patterns from CLAUDE.md Folder Structure section
- ✅ Tool execution latency meets NFR-Performance-02 target
- ✅ Integration tests passing for MCP tool workflows

### Phase 4: Task Tracking Microservice (Weeks 5-6)
**Deliverables:**
- Implement Task Tracking microservice (Go) with REST API and PostgreSQL database
- Integrate task tracking and ID management endpoints into single service
- Integrate microservice with MCP Server tools (`get_next_task`, `update_task_status`, `get_next_available_id`, `reserve_id_range`)
- Database migration scripts and schema validation
- Validation: Multi-project scalability (5 concurrent projects), zero ID collisions in stress test

**Success Criteria:**
- ✅ Task Tracking API supports 100 RPS with p99 <200ms (NFR-Performance-04)
- ✅ ID management API handles 50 concurrent reservations with zero collisions (NFR-Performance-05)
- ✅ Multi-project isolation validated (5 projects with independent task/ID databases)
- ✅ API authentication implemented (API key or JWT)

### Phase 5: CLAUDE.md Orchestration Update & Integration Testing (Week 7)
**Deliverables:**
- Update main CLAUDE.md orchestrator to direct to MCP resources/prompts/tools
- Implement backward compatibility mode (local file approach as fallback)
- End-to-end integration testing (epic generation, PRD creation, backlog story breakdown)
- Documentation: Migration guide, MCP tool API reference, troubleshooting guide

**Success Criteria:**
- ✅ 10 representative workflows execute successfully using MCP approach
- ✅ Token cost reduction ≥40% validated vs. baseline (NFR-Performance-03)
- ✅ Backward compatibility mode functional (regression tests passing)
- ✅ Internal pilot completed with AI Agent MCP Server project (self-hosting validation)

### Phase 6: Production Readiness and Pilot (Week 8+)
**Deliverables:**
- Performance benchmarking report (resource loading, tool execution, API latency)
- Security review and hardening (input validation, authentication, rate limiting)
- Observability dashboard (Grafana or similar) with key metrics
- Production deployment guide and runbook
- Feedback collection from pilot project
- 30-day stability period per Decision D1

**Success Criteria:**
- ✅ All success metrics from Goals & Success Metrics section met or exceeded
- ✅ Zero high-severity bugs from pilot project
- ✅ Documentation complete (migration guide, API reference, troubleshooting, deployment guide)
- ✅ Performance benchmarks meet all NFRs (availability, latency, scalability)
- ✅ 30-day stability period completed before second pilot expansion

## Decisions Made

**PRD is a BRIDGE ARTIFACT: Including both business and strategic technical decisions, with implementation details deferred to ADR/Tech Spec phases.**

### Business Decisions

**D1: Pilot Project Expansion Timeline**
- **Decision:** Wait for 30-day stability period after initial AI Agent MCP Server validation before expanding to second pilot project
- **Rationale:** Reduces risk exposure and allows thorough monitoring of production stability before scaling
- **Impact:** Affects resource allocation timeline; validation period extends before multi-project rollout (Week 8+ → Week 12+)
- **Stakeholders:** Tech Lead, Product Manager

**D2: Open Source Timing for Go Microservices**
- **Decision:** Keep Task Tracking microservice private until after production validation (3 months minimum)
- **Rationale:** Avoids exposing immature code to external scrutiny; allows refinement based on production learnings before community release
- **Impact:** Delays community credibility benefits but reduces risk of negative perception from early-stage code quality
- **Stakeholders:** Tech Lead, Product Manager

### Technical Decisions

**D3: Database Hosting Model for Pilot Phase**
- **Decision:** Use containerized PostgreSQL (Docker Compose/Podman) for Task Tracking microservice in pilot phase
- **Rationale:** Simpler setup, lower cost, sufficient reliability for pilot validation; can migrate to cloud-hosted (AWS RDS, GCP Cloud SQL) for production scale if needed
- **Impact:** Affects deployment guide (FR-14, FR-18, FR-19), operational complexity (lower during pilot), migration path defined for production scale
- **Stakeholders:** Tech Lead

**D4: MCP Resource Granularity for Artifacts**
- **Decision:** Expose shared artifacts as individual resources (`mcp://resources/artifacts/epic/000`) rather than collections
- **Rationale:** Simpler client requests, clearer resource URIs, aligns with MCP protocol design patterns for resource addressability
- **Impact:** Affects FR-03 implementation; higher resource count but better client ergonomics
- **Stakeholders:** Tech Lead

**D5: Validation Checklist Versioning Strategy**
- **Decision:** Hybrid approach - default to latest checklist version, allow explicit version override in artifact metadata
- **Rationale:** Balances flexibility (projects can pin to specific checklist version) with simplicity (most projects use latest automatically)
- **Impact:** Affects FR-16 (validation checklist resources) and FR-06 (validate_artifact tool); requires version resolution logic in validation tool
- **Implementation:** Artifact metadata includes optional `validation_checklist_version` field; if absent, use latest; if present, load specified version
- **Stakeholders:** Tech Lead, Product Manager

---

**Deferred to ADR/Tech Spec Phases:**

- Specific HTTP framework choice for microservice (chi vs. gin vs. gorilla/mux) - **ADR**
- Exact caching implementation (in-memory dict vs. Redis vs. memcached) - **Tech Spec**
- Database migration tool selection (goose vs. migrate vs. custom) - **Tech Spec**
- Logging library choice (structured logging: logrus vs. zap vs. zerolog) - **Tech Spec**
- MCP transport protocol (stdio vs. HTTP) - **Tech Spec** (may use both, client-dependent)

## Related Documents
- **Parent Epic:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v2.md`
- **Business Research:** `/artifacts/research/AI_Agent_MCP_Server_business_research.md`
- **Parent Initiative:** `/artifacts/initiatives/INIT-001_ai_agent_mcp_infrastructure_v4.md`
- **Parent Product Vision:** `/artifacts/product_visions/VIS-001_AI_Agent_MCP_Server_v1.md`
- **Prerequisite Epic:** `/artifacts/epics/EPIC-000_project_foundation_bootstrap_v2.md` (completed)

## Version History
- **v3.0 (2025-10-18):** Applied feedback - Renamed CLAUDE-*.md to patterns-*.md and sdlc-core.md for AI-agent-agnostic naming. Updated FR-01 to reflect new resource URLs (mcp://resources/sdlc/core, mcp://resources/patterns/*). Updated FR-04 to reference sdlc-core.md. Updated FR-05 to use mcp://prompts/generator/{artifact_name} URL pattern. Added FR-24 (add_task tool) and FR-25 (generator sub-artifact evaluation). Updated architecture diagrams and Key Architectural Decisions to reflect new naming and sub-artifact evaluation. Updated Alignment section to reference patterns-*.md files. Updated Epic link to v2.
- **v2.0 (2025-10-18):** Comprehensive refinement based on Epic and HLS feedback iterations. Updated functional requirements FR-01 through FR-23, refined NFRs, clarified architecture, added detailed appendices with validation criteria cross-reference.
- **v1.0 (2025-10-17):** Initial version

## Appendix

### Appendix A: Token Cost Baseline Measurement Plan

**Baseline Workflows (10 representative scenarios):**
1. Generate Product Vision (VIS-001) from business research
2. Generate Initiative (INIT-001) from Product Vision
3. Generate Epic (EPIC-000) from Initiative
4. Generate PRD (PRD-000) from Epic
5. Generate High-Level Story (HLS-001) from PRD
6. Generate Backlog Story (US-001) from HLS + PRD
7. Generate Tech Spec (SPEC-001) from Backlog Story
8. Refine Epic (EPIC-000 v1 → v2) based on critique
9. Refine PRD (PRD-000 v1 → v2) based on critique
10. Validate PRD-000 against 26-criterion checklist

**Measurement Method:**
- **Baseline (Local File Approach):** Record token usage from Claude API telemetry for each workflow (input tokens + output tokens)
- **MCP Approach:** Record token usage for same workflows using MCP resources/tools
- **Comparison:** Calculate % reduction per workflow and aggregate average
- **Target:** ≥40% aggregate reduction (per NFR-Performance-03)

### Appendix B: Multi-Project Validation Test Plan

**Test Scenario:** 5 concurrent projects using shared MCP framework

**Projects:**
1. ai-agent-mcp-server (Python, current project)
2. project-alpha (Python REST API)
3. project-beta (Python CLI tool)
4. project-gamma (Go microservice)
5. project-delta (Python data pipeline)

**Test Cases:**
1. **Concurrent ID Reservation:** All 5 projects request US IDs simultaneously (10 requests/project = 50 total)
   - **Expected:** 50 unique IDs assigned with zero collisions, latency <500ms per request
2. **Concurrent Task Retrieval:** All 5 projects query `get_next_task` simultaneously
   - **Expected:** Each project receives correct next task for their project_id, zero cross-project leakage
3. **Resource Loading Contention:** All 5 projects load `mcp://resources/claude/sdlc` simultaneously
   - **Expected:** Cache hit rate >80% after first request, latency <100ms for all requests
4. **Database Isolation:** Verify task and ID databases correctly isolate data per project_id
   - **Expected:** Zero data leakage between projects, queries correctly filtered by project_id
5. **Performance Degradation:** Measure latency/throughput with 1 project vs. 5 concurrent projects
   - **Expected:** <10% degradation in latency for 5 concurrent projects vs. single-project baseline

### Appendix C: Validation Criteria Cross-Reference

**PRD Validation Checklist (26 criteria) mapped to requirements:**

| Criterion ID | Category | Requirement ID | Validation Type |
|--------------|----------|----------------|-----------------|
| CQ-01 | Content | FR-06, FR-16 | Automated (objective present?) |
| CQ-02 | Content | FR-06 | Automated (scope section present?) |
| CQ-03 | Content | FR-06 | Automated (10-20 user stories?) |
| CQ-04 | Content | FR-06 | Automated (NFRs separated?) |
| CQ-05 | Content | FR-06 | Automated (technical NFRs have targets?) |
| CQ-06 | Content | FR-06 | Automated (dependencies documented?) |
| CQ-07 | Content | FR-06 | Automated (success metrics defined?) |
| CQ-08 | Content | FR-06 | Automated (user personas present?) |
| CQ-09 | Content | FR-06 | Automated (user journeys present?) |
| CQ-10 | Content | FR-06 | Automated (risks present?) |
| CQ-11 | Content | FR-06, FR-22 | Manual (open questions appropriate?) |
| CQ-12 | Content | FR-22 | Manual (readability check) |
| CQ-13 | Content | FR-06 | Automated (bridge artifact structure?) |
| CQ-14 | Content | FR-06 | Automated (CLAUDE.md references?) |
| UT-01 | Traceability | FR-06 | Automated (parent epic ID present?) |
| UT-02 | Traceability | FR-07, FR-21 | Automated (parent epic status check) |
| UT-03 | Traceability | FR-06 | Automated (parent context present?) |
| UT-04 | Traceability | FR-06 | Automated (research fields present?) |
| UT-05 | Traceability | FR-07, FR-21 | Automated (business research status) |
| UT-06 | Traceability | FR-07, FR-21 | Automated (implementation research status) |
| UT-07 | Traceability | FR-06 | Automated (research references valid?) |
| UT-08 | Traceability | FR-06 | Automated (traceability references present?) |
| CC-01 | Consistency | FR-06 | Automated (status value format) |
| CC-02 | Consistency | FR-06 | Automated (PRD ID format) |
| CC-03 | Consistency | FR-06 | Automated (no placeholder brackets) |
| CC-04 | Consistency | FR-06 | Automated (FR-XX identifiers unique?) |
| CC-05 | Consistency | FR-06 | Automated (metrics SMART?) |
| CC-06 | Consistency | FR-06 | Automated (acceptance criteria testable?) |

**Automated Validation Coverage:** 24/26 criteria (92%)
**Manual Review Required:** 2/26 criteria (8% - CQ-11 appropriateness, CQ-12 readability)
