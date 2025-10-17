# PRD: MCP Server SDLC Framework Integration

## Metadata
- **PRD ID:** PRD-006
- **Author:** Product Manager + Tech Lead
- **Date:** 2025-10-17
- **Version:** 1.0
- **Status:** Draft
- **Parent Epic:** EPIC-006
- **Informed By Business Research:** /artifacts/research/AI_Agent_MCP_Server_business_research.md

## Parent Artifact Context

**Parent Epic:** [EPIC-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md`
- **Epic Scope Coverage:** This PRD addresses the complete epic scope - migration of SDLC framework components (CLAUDE.md files, artifacts, generators, templates) to MCP resources and tools, establishing the AI Agent MCP Server as a centralized framework infrastructure provider
- **Epic Acceptance Criteria Mapping:**
  - **Criterion 1** (MCP Resources Migration): Covered by Features 1-3, FR-01 through FR-12
  - **Criterion 2** (MCP Tools Functional Equivalence): Covered by Features 4-6, FR-13 through FR-24
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

This PRD defines requirements for migrating the SDLC framework to MCP-native architecture using resources (CLAUDE.md files, generators, templates, shared artifacts), prompts (Claude commands), and deterministic Python/Go tools (validation, path resolution, task tracking, ID management). The solution eliminates framework duplication, reduces token consumption by 40-60%, and enables multi-language/multi-project scalability while maintaining zero functionality loss compared to local file approach.

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

- **MCP Resources:** CLAUDE.md files, generators, templates, shared artifacts served by MCP Server (zero local duplication)
- **MCP Prompts:** Claude commands (`/generate`, `/refine`) migrated to MCP prompts
- **MCP Tools:** Deterministic Python/Go scripts for validation (checklist evaluation), path resolution (pattern→file), task tracking (database-backed API), and ID management (reserve/allocate)
- **Main CLAUDE.md:** Refactored as pure orchestrator directing to MCP resources and tools

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
| **FR-01** | MCP Server SHALL expose all CLAUDE.md files (sdlc, core, tooling, testing, typing, validation, architecture) as named MCP resources | Must-have | ✅ Client can request `mcp://resources/claude/sdlc` and receive CLAUDE-sdlc.md content<br>✅ Client can request `mcp://resources/claude/python/core` and receive CLAUDE-core.md for Python projects<br>✅ Resource list includes all CLAUDE-*.md files with language-specific subdirectories |
| **FR-02** | MCP Server SHALL expose all artifact generators (prompts/*.xml) as named MCP resources | Must-have | ✅ Client can request `mcp://resources/generators/prd-generator` and receive prd-generator.xml content<br>✅ Resource list includes all 10 generator types (product-vision, initiative, epic, prd, hls, backlog-story, spike, adr, tech-spec, implementation-task) |
| **FR-03** | MCP Server SHALL expose all artifact templates (prompts/templates/*.xml) as named MCP resources | Must-have | ✅ Client can request `mcp://resources/templates/prd-template` and receive prd-template.xml content<br>✅ Resource list includes all 10 template types matching generators |
| **FR-04** | MCP Server SHALL expose shared artifacts (artifacts/**/*) as queryable MCP resources with filters by artifact type, status, and parent relationship | Should-have | ✅ Client can request `mcp://resources/artifacts/epic/006` and receive EPIC-006 content<br>✅ Client can query `mcp://resources/artifacts?type=epic&status=Approved` and receive list of approved epics<br>✅ Client can query `mcp://resources/artifacts?parent=EPIC-006` and receive all PRD/HLS children |
| **FR-05** | MCP Server SHALL refactor main CLAUDE.md into orchestrator (remains local) + SDLC workflow instructions (new prompts/CLAUDE/CLAUDE-sdlc.md served as MCP resource) | Must-have | ✅ Local CLAUDE.md reduced to <200 lines (orchestration only, no SDLC content)<br>✅ CLAUDE-sdlc.md contains all artifact dependency flow, generator execution, refinement workflow instructions<br>✅ Functionality equivalent pre/post split (validation test suite) |
| **FR-06** | MCP Server SHALL expose `/generate` and `/refine` commands as MCP prompts with parameter validation | Must-have | ✅ Client can execute `mcp://prompts/generate` with `generator_name` parameter<br>✅ Client can execute `mcp://prompts/refine` with `artifact_type` parameter<br>✅ Prompt execution validates parameters before execution (fail fast on invalid generator name) |
| **FR-07** | MCP Server SHALL provide `validate_artifact` tool that accepts artifact content and validation checklist ID, returning pass/fail results with criterion-level details | Must-have | ✅ Tool accepts artifact text + checklist ID (e.g., "prd_validation_v1")<br>✅ Returns JSON: `{passed: true/false, results: [{id: "CQ-01", passed: true, details: "..."}]}`<br>✅ Validation logic deterministic (same input → same output, no AI inference) |
| **FR-08** | MCP Server SHALL provide `resolve_artifact_path` tool that accepts path pattern with variables and returns exact file path or error if not found | Must-have | ✅ Input: `{pattern: "artifacts/epics/EPIC-{id}*v{version}.md", id: "006", version: 1}`<br>✅ Output: `{path: "artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md"}`<br>✅ Error if multiple matches or no match: `{error: "Multiple files match pattern", candidates: [...]}`<br>✅ Supports all artifact path patterns from CLAUDE.md Folder Structure section |
| **FR-09** | MCP Server SHALL provide `get_next_task` tool (Go microservice) that queries task tracking database and returns next pending task with context (ID, description, dependencies, inputs, expected outputs) | Must-have | ✅ Input: `{project_id: "ai-agent-mcp-server", status_filter: "pending"}`<br>✅ Output: `{task_id: "TASK-051", description: "Generate PRD-006", generator: "prd-generator", inputs: ["EPIC-006"], context: "New session CX required"}`<br>✅ Returns empty if no pending tasks: `{task_id: null, message: "No pending tasks"}`<br>✅ Tool exposed via MCP Server REST API integration |
| **FR-10** | MCP Server SHALL provide `update_task_status` tool (Go microservice) that updates task status (pending→in_progress→completed) and logs completion timestamp | Must-have | ✅ Input: `{task_id: "TASK-051", status: "completed", completion_notes: "PRD-006 v1 generated, 26/26 validation criteria passed"}`<br>✅ Updates database record with status, timestamp, notes<br>✅ Returns confirmation: `{success: true, updated_task: {...}}`<br>✅ Validates state transitions (cannot go completed→pending without explicit reset) |
| **FR-11** | MCP Server SHALL provide `get_next_available_id` tool (Go microservice) that queries ID registry database and returns next sequential ID for artifact type | Must-have | ✅ Input: `{artifact_type: "US"}`<br>✅ Output: `{artifact_type: "US", next_id: "US-028", last_assigned: "US-027"}`<br>✅ Guarantees uniqueness across concurrent requests (database transaction isolation)<br>✅ Supports all artifact types: VIS, INIT, EPIC, PRD, HLS, US, SPIKE, ADR, SPEC, TASK |
| **FR-12** | MCP Server SHALL provide `reserve_id_range` tool (Go microservice) that reserves contiguous ID range for batch artifact generation (e.g., HLS decomposition generating 6 backlog stories) | Must-have | ✅ Input: `{artifact_type: "US", count: 6}`<br>✅ Output: `{artifact_type: "US", reserved_ids: ["US-028", "US-029", "US-030", "US-031", "US-032", "US-033"], expires_at: "2025-10-17T14:30:00Z"}`<br>✅ IDs locked in database with expiration (15 min default, configurable)<br>✅ Expired reservations released for reuse if not confirmed within timeout |
| **FR-13** | Main CLAUDE.md SHALL be refactored to orchestrate MCP Server integration, directing Claude Code to use MCP resources/prompts/tools instead of local file access | Must-have | ✅ CLAUDE.md instructions reference MCP resources for SDLC workflow (not local file paths)<br>✅ Generator execution instructions call MCP prompts (not local .claude/commands/*.md)<br>✅ Validation instructions call `validate_artifact` MCP tool (not AI inference)<br>✅ Path resolution instructions call `resolve_artifact_path` MCP tool (not manual file search) |
| **FR-14** | MCP Server SHALL maintain backward compatibility mode allowing projects to opt-in to MCP framework incrementally (coexist with local file approach during transition) | Should-have | ✅ Configuration flag `use_mcp_framework: true/false` in project config<br>✅ When false, fall back to local file access (CLAUDE.md, generators, templates)<br>✅ When true, use MCP resources/tools exclusively<br>✅ Validation test suite passes in both modes (functional equivalence) |
| **FR-15** | Task tracking microservice SHALL provide REST API with endpoints: `GET /tasks/next`, `PUT /tasks/{id}/status`, `GET /tasks?project={id}&status={filter}` | Must-have | ✅ `GET /tasks/next?project=ai-agent-mcp-server&status=pending` returns next pending task<br>✅ `PUT /tasks/TASK-051/status` with body `{status: "completed", notes: "..."}` updates task<br>✅ `GET /tasks?project=ai-agent-mcp-server&status=completed` returns list of completed tasks<br>✅ API authenticated via API key or JWT token |
| **FR-16** | ID management microservice SHALL provide REST API with endpoints: `GET /ids/next?type={artifact_type}`, `POST /ids/reserve` with body `{type, count}` | Must-have | ✅ `GET /ids/next?type=US` returns `{next_id: "US-028"}`<br>✅ `POST /ids/reserve` with body `{type: "US", count: 6}` returns `{reserved_ids: ["US-028"...], expires_at: "..."}`<br>✅ `POST /ids/confirm` with body `{reservation_id: "abc123"}` confirms reservation and prevents expiration<br>✅ API authenticated via API key or JWT token |
| **FR-17** | ID management microservice SHALL ensure global uniqueness across concurrent requests from multiple projects using database transaction isolation (SERIALIZABLE level) | Must-have | ✅ Stress test: 10 concurrent `get_next_available_id` requests for same artifact type return unique IDs (no duplicates)<br>✅ Stress test: 5 concurrent `reserve_id_range` requests with overlapping ranges return non-overlapping ID sets<br>✅ Database transaction log shows SERIALIZABLE isolation level enforcement |
| **FR-18** | MCP Server SHALL expose validation checklists as structured data resources (JSON format) allowing dynamic checklist updates without MCP Server code changes | Should-have | ✅ Client can request `mcp://resources/validation/prd_checklist_v1` and receive JSON: `[{id: "CQ-01", category: "content", description: "...", validation_type: "manual/auto"}]`<br>✅ `validate_artifact` tool loads checklist from resource (not hardcoded)<br>✅ Checklist updates deployed via resource file change (no code deployment) |
| **FR-19** | MCP Server SHALL log all tool invocations (validation, path resolution, task tracking, ID management) with timestamp, input parameters, execution duration, and result status for observability | Should-have | ✅ Logs include: `{timestamp, tool_name, input_params, duration_ms, success: true/false, error_message}`<br>✅ Logs queryable via API or log aggregation system (structured JSON format)<br>✅ Logs retained for ≥30 days for error analysis and performance monitoring |
| **FR-20** | Task tracking microservice SHALL support multiple independent project databases (project-specific isolation) with project_id parameter for all API calls | Must-have | ✅ `GET /tasks/next?project=ai-agent-mcp-server` queries ai-agent-mcp-server database<br>✅ `GET /tasks/next?project=other-project` queries other-project database (isolated data)<br>✅ Database schema includes project_id foreign key with strict isolation enforcement |
| **FR-21** | ID management microservice SHALL support multiple independent project ID registries (project-specific isolation) with project_id parameter for all API calls | Must-have | ✅ `GET /ids/next?project=ai-agent-mcp-server&type=US` queries ai-agent-mcp-server ID registry<br>✅ `GET /ids/next?project=other-project&type=US` queries other-project ID registry (independent sequences)<br>✅ Projects can have overlapping artifact IDs (US-001 in both projects) without conflicts |
| **FR-22** | MCP Server SHALL implement resource caching with TTL (time-to-live) to reduce repeated file I/O for frequently accessed CLAUDE.md files and generators | Should-have | ✅ First request for `mcp://resources/claude/sdlc` loads from disk and caches (TTL: 5 minutes)<br>✅ Subsequent requests within 5 minutes served from cache (latency <10ms vs. 50ms disk I/O)<br>✅ Cache invalidation on TTL expiration or explicit invalidation API call |
| **FR-23** | MCP Server SHALL expose artifact metadata (ID, type, status, parent_id, created_at, updated_at) as queryable resources separate from full artifact content for efficient filtering and discovery | Should-have | ✅ Client can request `mcp://resources/artifacts/metadata?type=epic&status=Approved` and receive lightweight metadata list (no full content)<br>✅ Metadata includes: `{id: "EPIC-006", type: "epic", title: "...", status: "Draft", parent_id: "INIT-001", created_at: "2025-10-16", file_path: "artifacts/epics/EPIC-006_..._v1.md"}`<br>✅ Metadata loading ≥10x faster than full artifact loading (benchmark validation) |
| **FR-24** | Validation tool SHALL support both automated validation (deterministic rules: template sections present, ID format correct) and manual validation flags (readability, clarity requiring human judgment) | Must-have | ✅ Automated criteria (e.g., "CQ-01: All template sections present") evaluated by script with pass/fail result<br>✅ Manual criteria (e.g., "CQ-12: Readability accessible to cross-functional team") flagged as `{passed: null, requires_manual_review: true}`<br>✅ Validation summary shows automated pass rate and list of manual review items |

### Non-Functional Requirements

#### Performance
- **NFR-Performance-01:** MCP resource loading latency SHALL be <100ms for 95th percentile requests (p95 <100ms) for CLAUDE.md files and generators (typical size: 10-50KB)
- **NFR-Performance-02:** MCP tool execution latency SHALL be <500ms for 95th percentile (p95 <500ms) for all tools (validation, path resolution, task tracking API calls, ID management API calls)
- **NFR-Performance-03:** Token consumption for typical SDLC workflow (epic generation, PRD creation, backlog story breakdown - 10 workflows) SHALL be reduced by ≥40% vs. baseline local file approach
- **NFR-Performance-04:** Task tracking microservice SHALL support ≥100 requests/second (RPS) with p99 latency <200ms
- **NFR-Performance-05:** ID management microservice SHALL support ≥50 concurrent reservation requests with zero ID collisions (validated via stress test)

#### Scalability
- **NFR-Scalability-01:** System SHALL support ≥5 concurrent projects using shared MCP framework with zero resource conflicts, ID collisions, or performance degradation >10% vs. single-project baseline
- **NFR-Scalability-02:** Task tracking microservice SHALL scale horizontally (add instances) to support ≥20 concurrent projects without database bottleneck (validated via load test)
- **NFR-Scalability-03:** MCP Server resource cache SHALL support ≥1000 cached resources (CLAUDE.md files, generators, templates, artifacts) with memory consumption <2GB

#### Availability
- **NFR-Availability-01:** MCP Server SHALL maintain ≥99.5% uptime during business hours (8am-6pm weekdays) measured over 30-day rolling window
- **NFR-Availability-02:** Task tracking and ID management microservices SHALL implement health check endpoints (`/health`) returning status within 100ms
- **NFR-Availability-03:** MCP Server SHALL implement graceful degradation: if microservices (task tracking, ID management) unavailable, fall back to local file approach with warning message (no hard failure)

#### Security
- **NFR-Security-01:** Task tracking and ID management microservice REST APIs SHALL require authentication via API key or JWT token (no unauthenticated access)
- **NFR-Security-02:** MCP Server SHALL validate all tool inputs against defined schemas (reject malformed requests with clear error messages)
- **NFR-Security-03:** ID management SHALL prevent ID exhaustion attacks by rate-limiting reservation requests to ≤10 per minute per project (configurable)
- **NFR-Security-04:** Database credentials for task tracking and ID management SHALL be stored in environment variables or secret management system (never hardcoded)

#### Observability
- **NFR-Observability-01:** MCP Server SHALL log all tool invocations with structured JSON format including timestamp, tool name, input parameters, duration, result status
- **NFR-Observability-02:** Task tracking and ID management microservices SHALL expose metrics endpoints (`/metrics`) in Prometheus format including request count, latency histogram, error rate
- **NFR-Observability-03:** MCP Server SHALL provide dashboard showing: resource cache hit rate, tool execution success rate, average latency per tool, active projects count (updated every 60 seconds)
- **NFR-Observability-04:** Validation tool SHALL log all failed validation criteria with artifact ID, criterion ID, failure reason for debugging and framework improvement

#### Reliability
- **NFR-Reliability-01:** MCP Server SHALL implement retry logic for transient microservice failures (3 retries with exponential backoff: 100ms, 200ms, 400ms)
- **NFR-Reliability-02:** Database operations (task tracking, ID management) SHALL use transactions with rollback on failure (ACID compliance)
- **NFR-Reliability-03:** ID reservation expiration SHALL automatically release unused IDs after timeout (default: 15 minutes, configurable) to prevent ID exhaustion from abandoned workflows

#### Maintainability
- **NFR-Maintainability-01:** All MCP tools (validation, path resolution) SHALL have unit test coverage ≥80% and integration test coverage ≥60%
- **NFR-Maintainability-02:** Task tracking and ID management microservices (Go) SHALL follow CLAUDE-core.md and CLAUDE-tooling.md standards for Go projects (when created) including linting (golangci-lint), testing (go test), and type safety
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
   └─ Claude Code calls MCP prompt `mcp://prompts/generate` with parameter `generator=epic-generator`
   └─ MCP Server loads generator from `mcp://resources/generators/epic-generator`
   └─ MCP Server calls `resolve_artifact_path` tool to locate input artifacts
   └─ MCP Server returns generated epic artifact
5. Claude Code calls `validate_artifact` tool with epic content + validation checklist
   └─ Tool returns validation results: 25/25 criteria passed
6. Developer confirms artifact looks correct
7. Claude Code calls `update_task_status` tool to mark task completed

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
│ - Directs to MCP prompts for /generate and /refine commands       │
│ - Directs to MCP tools for validation, path resolution, tasks, IDs │
└─────────────────────────────────────────────────────────────────────┘
                              ↓ MCP Protocol (stdio/HTTP)
┌─────────────────────────────────────────────────────────────────────┐
│ MCP Server (Python)                                                │
├─────────────────────────────────────────────────────────────────────┤
│ MCP Resources Layer                                                │
│ - CLAUDE.md files (sdlc, core, tooling, testing, typing, etc.)    │
│ - Generators (product-vision, epic, prd, hls, backlog-story, etc.) │
│ - Templates (all artifact templates)                                │
│ - Artifacts (shared/reference artifacts, queryable by type/status) │
│                                                                     │
│ MCP Prompts Layer                                                  │
│ - /generate command (parameter: generator_name)                    │
│ - /refine command (parameter: artifact_type)                       │
│                                                                     │
│ MCP Tools Layer (Python)                                           │
│ - validate_artifact (input: artifact content + checklist ID)       │
│ - resolve_artifact_path (input: pattern + variables)               │
│ - Integration with microservices (REST API calls):                 │
│   └─ Task tracking microservice (Go)                               │
│   └─ ID management microservice (Go)                               │
└─────────────────────────────────────────────────────────────────────┘
                              ↓ REST API (HTTP/JSON)
┌──────────────────────────────────┬──────────────────────────────────┐
│ Task Tracking Microservice (Go)  │ ID Management Microservice (Go)  │
├──────────────────────────────────┼──────────────────────────────────┤
│ REST API:                        │ REST API:                        │
│ - GET /tasks/next                │ - GET /ids/next?type={type}      │
│ - PUT /tasks/{id}/status         │ - POST /ids/reserve              │
│ - GET /tasks?project={id}        │ - POST /ids/confirm              │
│                                  │                                  │
│ Database: PostgreSQL             │ Database: PostgreSQL             │
│ - Schema: tasks table            │ - Schema: id_registry table      │
│   (task_id, project_id,          │   (artifact_type, project_id,    │
│    status, inputs, outputs)      │    last_id, reservations)        │
└──────────────────────────────────┴──────────────────────────────────┘
```

**Key Architectural Decisions:**
1. **Hybrid CLAUDE.md:** Main CLAUDE.md remains local (orchestration) but SDLC content migrated to MCP resource (CLAUDE-sdlc.md)
2. **Microservices for State:** Task tracking and ID management as separate Go microservices (not embedded in MCP Server) enables independent deployment, scaling, and multi-language demonstration (PoC for Go Lang support per EPIC-006 Decisions Made §4)
3. **Deterministic Tools in Python:** Validation and path resolution as Python scripts (not Go) to minimize language context switching for MCP Server development (Python-first, add Go incrementally)
4. **REST API Integration:** MCP tools call microservices via REST API (not direct database access) for clean separation of concerns and protocol-agnostic integration

**Alignment with CLAUDE.md Standards:**
- **CLAUDE-architecture.md:** Follow established project structure for MCP Server (src/mcp_server/, src/tools/, src/resources/, tests/)
- **CLAUDE-core.md:** Core development philosophy applies to all Python and Go components
- **Go microservices:** Will reference Go-specific CLAUDE-core.md and CLAUDE-tooling.md when created (currently Python-focused framework)

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

- **ID Management Microservice (Go):**
  - Go 1.21+ runtime
  - PostgreSQL client library (pgx or similar)
  - HTTP router (chi, gin, or similar)

- **Database:**
  - PostgreSQL 15+ (task tracking and ID management databases)
  - Database migration tool (goose, migrate, or similar)

#### External Dependencies
- **MCP Protocol:** Compliance with MCP specification version (check mcp-sdk compatibility)
- **Claude Code CLI:** Client must support MCP resource/prompt/tool protocol (stdio or HTTP transport)
- **Containerization (for deployment):** Docker/Podman for MCP Server and microservices (EPIC-000 established container infrastructure)

#### Implementation Standards (Reference CLAUDE.md Files)

**Python Components (MCP Server, validation tool, path resolution tool):**
- **CLAUDE-tooling.md:** UV for dependency management, Ruff for linting/formatting, MyPy for type checking, pytest for testing, Taskfile for unified CLI
- **CLAUDE-testing.md:** Testing strategy with ≥80% unit test coverage, integration tests for MCP resource/tool workflows, fixture patterns
- **CLAUDE-typing.md:** Full type hints with mypy strict mode, Pydantic models for tool input/output schemas
- **CLAUDE-validation.md:** Pydantic models for input validation, security patterns for file path sanitization
- **CLAUDE-architecture.md:** Project structure following established patterns (src/, tests/, docs/)

**Go Components (task tracking microservice, ID management microservice):**
- **CLAUDE-core.md (Go):** To be created during implementation (reference Go best practices, similar philosophy to Python CLAUDE-core.md)
- **CLAUDE-tooling.md (Go):** To be created (golangci-lint for linting, go test for testing, Taskfile integration, module management)

**Note:** Language-specific CLAUDE.md files located in `prompts/CLAUDE/{language}/` subdirectories. Go-specific files will be created as part of this PRD's implementation, establishing framework's multi-language capability.

**Treating CLAUDE.md as "Decisions Made":**
All Technical Considerations in this PRD supplement (not duplicate) CLAUDE.md standards. Implementation phase SHALL reference CLAUDE-*.md files as authoritative for tooling, testing, typing, validation, and architecture patterns.

### Technical Constraints

1. **MCP Protocol Compatibility:** Must remain compatible with MCP SDK version used by Claude Code CLI (version validation required during implementation)
2. **File System Access:** MCP Server requires read access to local Git repository for artifacts, generators, templates (migration to database-backed storage deferred to future phase)
3. **Database Hosting:** PostgreSQL databases for task tracking and ID management can be containerized (Docker Compose or Podman) or cloud-hosted (AWS RDS, GCP Cloud SQL) - deployment model TBD in Tech Spec phase
4. **Backward Compatibility Window:** Must maintain local file approach compatibility for ≥3 months during transition period (dual-mode operation)
5. **Token Budget:** MCP resource content must fit within Claude Code context window (200k tokens) - large artifacts may require chunking or summarization (deferred to implementation if needed)
6. **Language-Specific Resources:** CLAUDE.md files organized by language subdirectory (prompts/CLAUDE/python/, prompts/CLAUDE/go/) - MCP resource URIs must support language-specific paths

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
| **Go Microservice Development Complexity** | Medium (delays implementation) | Medium (new language for framework) | Start with Python prototypes for task tracking/ID management, migrate to Go incrementally, recruit Go expertise (contractor or upskill team member), reuse established patterns from Python CLAUDE.md standards |
| **ID Collision in Concurrent Requests** | High (data corruption, duplicate IDs) | Low (database transactions prevent this) | Database SERIALIZABLE isolation level for ID allocation queries, stress testing with 50 concurrent requests, automated testing in CI/CD pipeline, monitoring for collision events (should be zero) |
| **MCP Server Single Point of Failure** | High (blocks all projects if server down) | Medium (deployment/infrastructure risk) | Graceful degradation (fall back to local file approach with warning), health check monitoring with alerts, implement MCP Server redundancy (load balancer + 2 instances) in production, clear runbook for MCP Server recovery |

## Timeline & Milestones

### Phase 1: MCP Resources Migration (Weeks 1-2)
**Deliverables:**
- Refactor main CLAUDE.md into orchestrator (local) + CLAUDE-sdlc.md (MCP resource)
- Migrate all CLAUDE-*.md files to MCP resources with language-specific subdirectory structure
- Migrate generators and templates to MCP resources
- Implement MCP resource caching with TTL
- Validation: Resource loading latency <100ms (p95), cache hit rate >70%

**Success Criteria:**
- ✅ 15+ CLAUDE.md resources accessible via MCP protocol
- ✅ 10 generator resources + 10 template resources accessible
- ✅ Resource loading latency meets NFR-Performance-01 target
- ✅ Unit tests passing for resource loading and caching logic

### Phase 2: MCP Tools - Validation and Path Resolution (Weeks 3-4)
**Deliverables:**
- Implement `validate_artifact` tool (Python) with deterministic validation logic
- Implement `resolve_artifact_path` tool (Python) with pattern matching and variable substitution
- Migrate validation checklists to JSON resources (dynamic loading)
- Implement tool invocation logging for observability
- Validation: Error rate <5% vs. AI inference baseline, tool execution <500ms (p95)

**Success Criteria:**
- ✅ Validation tool evaluates 25-criterion PRD checklist with 100% accuracy on 10 test artifacts
- ✅ Path resolution tool resolves all 10 artifact path patterns from CLAUDE.md Folder Structure section
- ✅ Tool execution latency meets NFR-Performance-02 target
- ✅ Integration tests passing for MCP tool workflows

### Phase 3: MCP Tools - Task Tracking and ID Management Microservices (Weeks 5-6)
**Deliverables:**
- Implement task tracking microservice (Go) with REST API and PostgreSQL database
- Implement ID management microservice (Go) with REST API and PostgreSQL database
- Integrate microservices with MCP Server tools (`get_next_task`, `update_task_status`, `get_next_available_id`, `reserve_id_range`)
- Database migration scripts and schema validation
- Validation: Multi-project scalability (5 concurrent projects), zero ID collisions in stress test

**Success Criteria:**
- ✅ Task tracking API supports 100 RPS with p99 <200ms (NFR-Performance-04)
- ✅ ID management API handles 50 concurrent reservations with zero collisions (NFR-Performance-05)
- ✅ Multi-project isolation validated (5 projects with independent task/ID databases)
- ✅ API authentication implemented (API key or JWT)

### Phase 4: MCP Prompts and CLAUDE.md Orchestration Update (Weeks 7-8)
**Deliverables:**
- Migrate `/generate` and `/refine` commands to MCP prompts
- Update main CLAUDE.md orchestrator to direct to MCP resources/prompts/tools
- Implement backward compatibility mode (local file approach as fallback)
- End-to-end integration testing (epic generation, PRD creation, backlog story breakdown)
- Documentation: Migration guide, MCP tool API reference, troubleshooting guide

**Success Criteria:**
- ✅ 10 representative workflows execute successfully using MCP approach
- ✅ Token cost reduction ≥40% validated vs. baseline (NFR-Performance-03)
- ✅ Backward compatibility mode functional (regression tests passing)
- ✅ Internal pilot completed with AI Agent MCP Server project (self-hosting validation)

### Phase 5: Production Readiness and Pilot (Week 8+)
**Deliverables:**
- Performance benchmarking report (resource loading, tool execution, API latency)
- Security review and hardening (input validation, authentication, rate limiting)
- Observability dashboard (Grafana or similar) with key metrics
- Production deployment guide and runbook
- Feedback collection from pilot project

**Success Criteria:**
- ✅ All success metrics from Goals & Success Metrics section met or exceeded
- ✅ Zero high-severity bugs from pilot project
- ✅ Documentation complete (migration guide, API reference, troubleshooting, deployment guide)
- ✅ Performance benchmarks meet all NFRs (availability, latency, scalability)

## Open Questions

**PRD is a BRIDGE ARTIFACT: Including both business and strategic technical questions, deferring implementation details to ADR/Tech Spec phases.**

### Business Questions

[BUSINESS] **Question 1: Pilot Project Expansion Timeline**
- Should we expand to second pilot project immediately after AI Agent MCP Server validation (week 9), or wait for 30-day stability period?
- **Impact:** Affects resource allocation and risk exposure (early expansion validates multi-project scalability faster but increases support burden)
- **Stakeholders:** Tech Lead, Product Manager

[BUSINESS] **Question 2: Open Source Timing for Go Microservices**
- Should task tracking and ID management microservices be open-sourced immediately (part of MCP Server repo), or kept private until after production validation (3 months)?
- **Impact:** Open source builds community credibility (per Business Research §5.1 - "first-mover advantage") but exposes immature code to external scrutiny
- **Stakeholders:** Tech Lead, Product Manager, Legal (if applicable)

### Product/Technical Trade-offs

[TECHNICAL] **Question 3: Database Hosting Model for Pilot Phase**
- Should we use containerized PostgreSQL (Docker Compose/Podman) or cloud-hosted database (AWS RDS, GCP Cloud SQL) for task tracking and ID management in pilot phase?
- **Trade-off:** Containerized = simpler setup, lower cost, sufficient for pilot vs. Cloud-hosted = production-grade reliability, managed backups, higher operational maturity
- **Impact on Requirements:** Affects deployment guide (FR-20, FR-21), availability NFRs (NFR-Availability-02), and operational complexity
- **Recommendation Needed From:** Tech Lead (infrastructure experience) + Product Manager (budget/timeline)

[TECHNICAL] **Question 4: MCP Resource Granularity for Artifacts**
- Should shared artifacts (e.g., EPIC-000, PRD-000) be exposed as individual resources (`mcp://resources/artifacts/epic/000`) or collections (`mcp://resources/artifacts/epics` with filtering)?
- **Trade-off:** Individual = simpler client requests, higher resource count vs. Collection = flexible filtering, fewer resources, requires query parameter parsing
- **Impact on Requirements:** Affects FR-04 implementation complexity and client usage patterns
- **Recommendation Needed From:** Tech Lead + UX consideration (which approach feels more natural for Claude Code interactions?)

[TECHNICAL] **Question 5: Validation Checklist Versioning Strategy**
- How should validation checklists handle backward compatibility when criteria are added/modified (e.g., PRD checklist v1 → v2 with new security criterion)?
- **Options:** (A) Immutable versions (prd_checklist_v1, prd_checklist_v2 - artifacts specify version), (B) Single evolving checklist (all artifacts use latest), (C) Hybrid (default to latest, override with explicit version)
- **Trade-off:** Immutable = predictable validation but fragmented checklists vs. Evolving = simpler but may break old artifacts vs. Hybrid = flexible but complex
- **Impact on Requirements:** Affects FR-18 (validation checklist resources) and FR-07 (validate_artifact tool)
- **Recommendation Needed From:** Tech Lead + Product Manager (governance preference)

---

**Deferred to ADR/Tech Spec Phases:**

- Specific HTTP framework choice for microservices (chi vs. gin vs. gorilla/mux) - **ADR**
- Exact caching implementation (in-memory dict vs. Redis vs. memcached) - **Tech Spec**
- Database migration tool selection (goose vs. migrate vs. custom) - **Tech Spec**
- Logging library choice (structured logging: logrus vs. zap vs. zerolog) - **Tech Spec**
- MCP transport protocol (stdio vs. HTTP) - **Tech Spec** (may use both, client-dependent)

## Related Documents
- **Parent Epic:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md`
- **Business Research:** `/artifacts/research/AI_Agent_MCP_Server_business_research.md`
- **Parent Initiative:** `/artifacts/initiatives/INIT-001_ai_agent_mcp_infrastructure_v4.md`
- **Parent Product Vision:** `/artifacts/product_visions/VIS-001_AI_Agent_MCP_Server_v1.md`
- **Prerequisite Epic:** `/artifacts/epics/EPIC-000_project_foundation_bootstrap_v2.md` (completed)

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
| CQ-01 | Content | FR-07, FR-18 | Automated (objective present?) |
| CQ-02 | Content | FR-07 | Automated (scope section present?) |
| CQ-03 | Content | FR-07 | Automated (10-20 user stories?) |
| CQ-04 | Content | FR-07 | Automated (NFRs separated?) |
| CQ-05 | Content | FR-07 | Automated (technical NFRs have targets?) |
| CQ-06 | Content | FR-07 | Automated (dependencies documented?) |
| CQ-07 | Content | FR-07 | Automated (success metrics defined?) |
| CQ-08 | Content | FR-07 | Automated (user personas present?) |
| CQ-09 | Content | FR-07 | Automated (user journeys present?) |
| CQ-10 | Content | FR-07 | Automated (risks present?) |
| CQ-11 | Content | FR-07, FR-24 | Manual (open questions appropriate?) |
| CQ-12 | Content | FR-24 | Manual (readability check) |
| CQ-13 | Content | FR-07 | Automated (bridge artifact structure?) |
| CQ-14 | Content | FR-07 | Automated (CLAUDE.md references?) |
| UT-01 | Traceability | FR-07 | Automated (parent epic ID present?) |
| UT-02 | Traceability | FR-08, FR-23 | Automated (parent epic status check) |
| UT-03 | Traceability | FR-07 | Automated (parent context present?) |
| UT-04 | Traceability | FR-07 | Automated (research fields present?) |
| UT-05 | Traceability | FR-08, FR-23 | Automated (business research status) |
| UT-06 | Traceability | FR-08, FR-23 | Automated (implementation research status) |
| UT-07 | Traceability | FR-07 | Automated (research references valid?) |
| UT-08 | Traceability | FR-07 | Automated (traceability references present?) |
| CC-01 | Consistency | FR-07 | Automated (status value format) |
| CC-02 | Consistency | FR-07 | Automated (PRD ID format) |
| CC-03 | Consistency | FR-07 | Automated (no placeholder brackets) |
| CC-04 | Consistency | FR-07 | Automated (FR-XX identifiers unique?) |
| CC-05 | Consistency | FR-07 | Automated (metrics SMART?) |
| CC-06 | Consistency | FR-07 | Automated (acceptance criteria testable?) |

**Automated Validation Coverage:** 24/26 criteria (92%)
**Manual Review Required:** 2/26 criteria (8% - CQ-11 appropriateness, CQ-12 readability)
