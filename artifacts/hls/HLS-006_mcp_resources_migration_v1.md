# High-Level User Story: MCP Resources Migration

## Metadata
- **Story ID:** HLS-006
- **Status:** Draft
- **Priority:** Critical
- **Parent Epic:** EPIC-006
- **Parent PRD:** PRD-006
- **PRD Section:** Phase 1: MCP Resources Migration (Weeks 1-2)
- **Functional Requirements:** FR-01, FR-02, FR-04, FR-20
- **Owner:** Product Manager + Tech Lead
- **Target Release:** Phase 1 (Weeks 1-2)

## Parent Artifact Context

**Parent Epic:** [EPIC-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md`
- **Epic Contribution:** Establishes foundational MCP resources infrastructure, enabling framework centralization and eliminating per-project duplication (addresses Epic Acceptance Criterion 1 - MCP Resources Migration)

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md`
- **PRD Section:** §Timeline & Milestones - Phase 1: MCP Resources Migration (Weeks 1-2)
- **Functional Requirements Coverage:**
  - **FR-01:** MCP Server SHALL expose all CLAUDE.md files as named MCP resources
  - **FR-02:** MCP Server SHALL expose all artifact templates as named MCP resources
  - **FR-04:** MCP Server SHALL refactor main CLAUDE.md into orchestrator + SDLC workflow resource
  - **FR-20:** MCP Server SHALL implement resource caching with TTL

**User Persona Source:** PRD-006 §User Personas - Persona 2: Framework Maintainer (Core Team)

## User Story Statement

**As a** Framework Maintainer,
**I want** SDLC framework components (CLAUDE.md files, templates) accessible through MCP resources instead of local Git files,
**So that** I can maintain a single source of truth that automatically propagates to all projects without manual synchronization.

## User Context

### Target Persona
**Framework Maintainer (Core Team) - "Alex"**
- Senior engineer responsible for evolving SDLC framework based on team feedback
- 10+ years experience with enterprise development processes
- Manages framework updates across multiple concurrent projects

**User Characteristics:**
- Frustrated by manual file synchronization across N project repositories
- Values single source of truth eliminating version drift
- Needs confidence that updates won't break existing projects
- Pain point: Currently spends 4-6 hours/month manually syncing framework changes across 5+ projects

### User Journey Context
**Before this story:** Framework updates require manually copying CLAUDE.md files and templates to each project repository, leading to version drift and inconsistent practices.

**After this story:** Framework components served via MCP resources enable instant propagation of updates to all projects, eliminating manual synchronization overhead.

**Downstream impact:** Enables subsequent stories (HLS-007 through HLS-011) by establishing MCP resources infrastructure.

## Business Value

### User Value
- **Time Savings:** Eliminates 4-6 hours/month manual synchronization effort (>80% reduction)
- **Consistency:** Single source of truth prevents version drift across projects
- **Confidence:** Changes propagate automatically without risk of missed updates
- **Reduced Cognitive Load:** No need to track which projects have which framework versions

### Business Value
- **Operational Efficiency:** Reduces framework maintenance time from 6 hours/month to <1 hour (per PRD-006 §Goals - Centralize Maintenance)
- **Quality Improvement:** Eliminates version drift reducing framework-related bugs by ~30%
- **Scalability:** Enables support for 5+ concurrent projects without proportional maintenance burden increase
- **Strategic Positioning:** Demonstrates production-ready MCP infrastructure capabilities (per PRD-006 §Executive Summary)

### Success Criteria
- 15+ CLAUDE.md resources accessible via MCP protocol (per PRD-006 Phase 1 Success Criteria)
- 10 template resources accessible via MCP protocol
- Resource loading latency <100ms for p95 requests (per NFR-Performance-01)
- Cache hit rate >70% for frequently accessed resources
- Framework update propagation time <1 minute (vs. hours/days baseline)

## Functional Requirements (High-Level)

### Primary User Flow

**Happy Path:**
1. Framework Maintainer updates CLAUDE-sdlc.md content in MCP Server repository
2. Framework Maintainer commits and deploys updated MCP Server
3. MCP Server invalidates cached resource automatically
4. Developer in Project-Alpha runs `/generate epic-generator` command
5. Claude Code requests `mcp://resources/claude/sdlc` from MCP Server
6. MCP Server loads updated CLAUDE-sdlc.md from disk and caches (TTL: 5 minutes)
7. Claude Code receives updated framework instructions
8. Developer in Project-Beta runs `/generate prd-generator` later same day
9. MCP Server serves cached CLAUDE-sdlc.md (latency <10ms vs. 50ms disk I/O)
10. Both projects now using identical framework version - no manual sync required

**Alternative Flows:**
- **Alt Flow 1: Language-Specific Resource:** If developer requests Python-specific resource (`mcp://resources/claude/python/core`), MCP Server loads from `prompts/CLAUDE/python/CLAUDE-core.md`
- **Alt Flow 2: Cache Expiration:** If resource cached >5 minutes ago, MCP Server reloads from disk before serving
- **Alt Flow 3: Initial Setup:** If new project connects to MCP Server for first time, receives same resources as existing projects (immediate consistency)

### User Interactions
- Framework Maintainer edits CLAUDE.md files in MCP Server repository (not in individual project repos)
- Framework Maintainer deploys updated MCP Server
- Developer requests resources via Claude Code (transparent - no awareness of MCP vs. local file)
- Framework Maintainer monitors resource loading metrics via observability dashboard

### System Behaviors (User Perspective)
- MCP Server automatically detects CLAUDE.md file changes on deployment
- MCP Server caches frequently accessed resources to reduce latency
- MCP Server invalidates cache on TTL expiration or explicit invalidation call
- MCP Server serves resources to all connected projects with consistent content
- System logs resource access patterns for optimization

## Acceptance Criteria (High-Level)

### Criterion 1: CLAUDE.md Resources Accessible
**Given** MCP Server is deployed with CLAUDE.md files in `prompts/CLAUDE/` directory
**When** Claude Code requests `mcp://resources/claude/sdlc`
**Then** MCP Server returns CLAUDE-sdlc.md content within 100ms (p95)

### Criterion 2: Language-Specific Resources Accessible
**Given** MCP Server has Python-specific CLAUDE files at `prompts/CLAUDE/python/`
**When** Claude Code requests `mcp://resources/claude/python/core`
**Then** MCP Server returns CLAUDE-core.md content for Python projects

### Criterion 3: Template Resources Accessible
**Given** MCP Server has templates at `prompts/templates/`
**When** Claude Code requests `mcp://resources/templates/prd-template`
**Then** MCP Server returns prd-template.xml content

### Criterion 4: Resource Caching Functional
**Given** resource requested once and cached (TTL: 5 minutes)
**When** same resource requested within TTL window
**Then** MCP Server serves from cache with latency <10ms

### Criterion 5: Cache Invalidation Works
**Given** resource cached from previous request
**When** 5 minutes elapse (TTL expiration)
**Then** MCP Server reloads from disk on next request

### Criterion 6: Main CLAUDE.md Refactored
**Given** main CLAUDE.md file split into orchestrator (local) + SDLC content (MCP resource)
**When** developer reads local CLAUDE.md
**Then** file contains <200 lines with references to MCP resources

### Edge Cases & Error Conditions
- **Missing Resource File:** If requested CLAUDE.md file doesn't exist, return clear error: "Resource not found: mcp://resources/claude/sdlc"
- **Disk I/O Error:** If file read fails, retry once, then return error with diagnostic info
- **Cache Corruption:** If cached content appears corrupted (e.g., truncated), reload from disk and log warning

## Scope & Boundaries

### In Scope
- Migration of all CLAUDE-*.md files to MCP resources (sdlc, core, tooling, testing, typing, validation, architecture)
- Migration of all 10 artifact templates to MCP resources
- Refactoring main CLAUDE.md into local orchestrator + MCP resource
- Resource caching implementation with TTL
- Cache invalidation mechanism (TTL-based and explicit)
- Resource loading latency optimization (<100ms p95)
- Language-specific resource subdirectories (Python, Go)

### Out of Scope (Deferred to Future Stories)
- Artifact migration (HLS-011 - FR-03, FR-21)
- Generator migration (HLS-007 - FR-05)
- MCP tool implementation (HLS-008, HLS-009)
- CLAUDE.md orchestration update (HLS-010)
- Authentication/authorization for resource access (assumed trusted environment for pilot)
- Database-backed resource storage (file-based only in Phase 1)

## Decomposition into Backlog Stories

### Estimated Backlog Stories (Not Yet Detailed)

1. **Refactor Main CLAUDE.md into Orchestrator + SDLC Resource** (~5 SP)
   - Brief: Split CLAUDE.md into local orchestrator (<200 lines) and prompts/CLAUDE/CLAUDE-sdlc.md (served as MCP resource)

2. **Implement MCP Resource Server for CLAUDE.md Files** (~8 SP)
   - Brief: MCP Server exposes CLAUDE-*.md files as named resources with language-specific subdirectory support

3. **Implement MCP Resource Server for Templates** (~5 SP)
   - Brief: MCP Server exposes all 10 artifact templates (prompts/templates/*.xml) as named resources

4. **Implement Resource Caching with TTL** (~5 SP)
   - Brief: In-memory cache for resources with 5-minute TTL and explicit invalidation API

5. **Resource Loading Performance Optimization** (~3 SP)
   - Brief: Profile and optimize resource loading to meet <100ms p95 latency target

6. **Unit and Integration Testing for Resource Server** (~5 SP)
   - Brief: Test resource loading, caching, invalidation, and error handling

**Total Estimated Story Points:** ~31 SP
**Estimated Sprints:** 2 sprints (Weeks 1-2 per PRD-006 timeline)

### Decomposition Strategy
**By Feature Area:**
- Stories 1-3: Core resource migration (CLAUDE.md refactor, resource server implementation)
- Story 4: Performance optimization (caching)
- Story 5: Performance validation (latency optimization)
- Story 6: Quality assurance (testing)

**Priority Order:** 1 → 2 → 3 → 4 → 5 → 6 (sequential dependencies)

## Dependencies

### User Story Dependencies
- **Depends On:** None (foundational story for EPIC-006)
- **Blocks:** HLS-007 (MCP Prompts migration depends on resource infrastructure)
- **Blocks:** HLS-008 (MCP Tools migration depends on resource infrastructure)
- **Blocks:** HLS-010 (CLAUDE.md orchestration update depends on resource availability)

### External Dependencies
- MCP SDK (Python package) - must support resource protocol
- Claude Code CLI - must support MCP resource requests (stdio/HTTP transport)

## Non-Functional Requirements (User-Facing Only)

- **Usability:** Framework Maintainer can deploy resource updates via standard Git workflow (commit → push → deploy)
- **Reliability:** Resource loading failures gracefully degrade to local file fallback (per NFR-Availability-03)
- **Observability:** Framework Maintainer can view resource access logs showing cache hit rate and latency percentiles
- **Backward Compatibility:** Projects using local file approach continue functioning during MCP migration (per FR-13)

## Risks & Open Questions

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| **MCP SDK Breaking Changes** | High - could block resource serving | Pin MCP SDK version, monitor changelog, implement compatibility layer |
| **Cache Memory Consumption** | Medium - could affect MCP Server performance | Monitor memory usage, limit cache size to 1000 resources (NFR-Scalability-03) |
| **Resource Loading Latency** | Medium - could slow generator execution | Profile and optimize file I/O, validate <100ms p95 target early |

### Open Questions

**No open UX or functional questions at this time. Implementation uncertainties will be captured during backlog refinement.**

Technical implementation questions (HTTP framework choice, exact caching library) deferred to backlog stories and tech specs per PRD-006 §Decisions Made.

## Definition of Ready (Before Backlog Refinement)

- [x] User story statement complete and validated
- [x] User persona identified and documented (Framework Maintainer - Alex)
- [x] Business value articulated and quantified (6 hours/month → <1 hour)
- [x] High-level acceptance criteria defined (6 criteria)
- [x] Dependencies identified (blocks HLS-007, HLS-008, HLS-010)
- [ ] Product Owner approval obtained

## Definition of Done (High-Level Story Complete)

- [ ] All 6 decomposed backlog stories completed (US-028 through US-033)
- [ ] All acceptance criteria met and validated
- [ ] 15+ CLAUDE.md resources accessible via MCP protocol
- [ ] 10 template resources accessible via MCP protocol
- [ ] Resource loading latency <100ms p95 (NFR-Performance-01)
- [ ] Cache hit rate >70% validated
- [ ] Unit test coverage ≥80% (NFR-Maintainability-01)
- [ ] Integration tests passing (resource loading, caching, error handling)
- [ ] Product Owner acceptance obtained

## Related Documents
- **Parent Epic:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md`
- **PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md` (§Timeline & Milestones - Phase 1)
- **Business Research:** `/artifacts/research/AI_Agent_MCP_Server_business_research.md` (§1.1 - Integration Fragmentation)
- **User Personas:** PRD-006 §User Personas & Use Cases - Persona 2: Framework Maintainer
