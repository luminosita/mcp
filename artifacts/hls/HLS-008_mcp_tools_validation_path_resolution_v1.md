# High-Level User Story: MCP Tools - Validation and Path Resolution

## Metadata
- **Story ID:** HLS-008
- **Status:** Draft
- **Priority:** Critical
- **Parent Epic:** EPIC-006
- **Parent PRD:** PRD-006
- **PRD Section:** Phase 3: MCP Tools - Validation and Path Resolution (Week 4)
- **Functional Requirements:** FR-06, FR-07, FR-16, FR-17, FR-22, FR-23
- **Owner:** Product Manager + Tech Lead
- **Target Release:** Phase 3 (Week 4)

## Parent Artifact Context

**Parent Epic:** [EPIC-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md`
- **Epic Contribution:** Replaces AI inference for validation and path resolution with deterministic tools, reducing error rate from 20-30% to <5% (addresses Epic Acceptance Criterion 2 - MCP Tools Functional Equivalence)

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md`
- **PRD Section:** §Timeline & Milestones - Phase 3: MCP Tools - Validation and Path Resolution (Week 4)
- **Functional Requirements Coverage:**
  - **FR-06:** validate_artifact tool with deterministic checklist evaluation
  - **FR-07:** resolve_artifact_path tool with pattern matching
  - **FR-16:** Validation checklists as structured JSON resources
  - **FR-17:** Tool invocation logging for observability
  - **FR-22:** Automated + manual validation flag support
  - **FR-23:** store_artifact tool for centralized storage

**User Persona Source:** PRD-006 §User Personas - Persona 3: AI Agent (Claude Code Orchestrating SDLC)

## User Story Statement

**As an** AI Agent (Claude Code),
**I want** deterministic validation and path resolution tools instead of AI inference,
**So that** I can validate artifacts and locate files with <5% error rate and predictable execution time.

## User Context

### Target Persona
**AI Agent (Claude Code Orchestrating SDLC)**
- Executes SDLC workflows (generate epic, create PRD, break down stories)
- Currently uses AI inference for validation and path resolution
- Requires deterministic operations and minimal token consumption

**User Characteristics:**
- Currently spends ~500ms+ inferring artifact paths from patterns
- Error-prone: 20-30% error rate in path resolution and validation (per PRD-006 §Problem Statement)
- Token-heavy: Burns ~2-5k tokens on validation inference per artifact
- Pain point: Validation errors discovered late (after artifact generated), requiring regeneration

### User Journey Context
**Before this story:** Claude Code infers validation criteria from generator prompts and manually searches filesystem for artifact paths, causing 20-30% errors and excessive token consumption.

**After this story:** Claude Code calls deterministic MCP tools (`validate_artifact`, `resolve_artifact_path`, `store_artifact`) with <5% error rate and <500ms execution time, reducing token consumption by ~40%.

**Downstream impact:** Enables reliable artifact validation and path resolution for all generators. Required for HLS-009 (Task Tracking microservice) to store artifact metadata.

## Business Value

### User Value (AI Agent Perspective)
- **Accuracy:** Path resolution error rate reduced from 20-30% to <5% (per PRD-006 §Goals)
- **Speed:** Validation execution time reduced from ~2 seconds (AI inference) to <500ms (deterministic tool)
- **Predictability:** Deterministic tool returns same result for same input (no AI variability)
- **Token Efficiency:** Validation no longer requires ~2-5k tokens per artifact

### Business Value
- **Quality Improvement:** Artifact validation errors reduced by ~80% (30% → <5%)
- **Cost Reduction:** Token consumption reduced by ~40-60% per PRD-006 §Executive Summary
- **Time Savings:** Faster validation enables faster artifact generation cycles
- **Operational Efficiency:** Deterministic tools easier to debug and maintain vs. AI inference

### Success Criteria
- Validation tool evaluates 25-criterion PRD checklist with 100% accuracy on 10 test artifacts (per PRD-006 Phase 3 Success Criteria)
- Path resolution tool resolves all 10 artifact path patterns from CLAUDE.md
- Tool execution latency <500ms for p95 requests (per NFR-Performance-02)
- Error rate <5% vs. 20-30% AI inference baseline

## Functional Requirements (High-Level)

### Primary User Flow

**Happy Path (Validation):**
1. Claude Code generates PRD-006 artifact
2. Claude Code calls MCP tool `validate_artifact(content=prd_text, checklist_id="prd_validation_v1")`
3. MCP Server loads validation checklist from `mcp://resources/validation/prd_checklist_v1` (JSON)
4. MCP Server evaluates 26 automated criteria deterministically (sections present, ID format, references valid)
5. MCP Server flags 2 manual criteria as `requires_manual_review: true` (readability, appropriateness)
6. MCP Server returns JSON: `{passed: 24/26 automated, manual_review: 2 criteria}`
7. Claude Code presents validation report to developer
8. Developer confirms manual criteria satisfied
9. Claude Code proceeds with artifact finalization

**Happy Path (Path Resolution):**
1. Claude Code needs to locate EPIC-006 artifact for PRD generation
2. Claude Code calls MCP tool `resolve_artifact_path(pattern="artifacts/epics/EPIC-{id}*v{version}.md", id="006", version=1)`
3. MCP Server searches filesystem using glob pattern
4. MCP Server finds exact match: `artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md`
5. MCP Server returns JSON: `{path: "artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md"}`
6. Claude Code reads artifact from resolved path
7. Claude Code executes PRD generator with EPIC-006 as input

**Happy Path (Artifact Storage):**
1. Claude Code generates HLS-006 artifact
2. Claude Code calls MCP tool `store_artifact(artifact_type="hls", artifact_id="HLS-006", content="...", metadata={...})`
3. MCP Server stores artifact in centralized repository (filesystem or database)
4. MCP Server returns confirmation: `{success: true, uri: "mcp://resources/artifacts/hls/006"}`
5. Artifact now queryable via MCP resources (FR-03)

**Alternative Flows:**
- **Alt Flow 1: Path Not Found:** If pattern matches zero files, return error: `{error: "No files match pattern", pattern: "..."}`
- **Alt Flow 2: Multiple Matches:** If pattern matches >1 file, return error: `{error: "Multiple files match pattern", candidates: [path1, path2]}`
- **Alt Flow 3: Validation Failure:** If <90% automated criteria pass, flag artifact for regeneration

### User Interactions
- Claude Code calls `validate_artifact` tool with artifact content + checklist ID
- Claude Code calls `resolve_artifact_path` tool with path pattern + variables
- Claude Code calls `store_artifact` tool with artifact content + metadata
- Claude Code receives structured JSON responses (no natural language parsing required)

### System Behaviors (User Perspective)
- MCP Server loads validation checklists from JSON resources (dynamic updates)
- MCP Server evaluates automated criteria deterministically (same input → same output)
- MCP Server searches filesystem using glob patterns for path resolution
- MCP Server logs all tool invocations for observability (timestamp, duration, result)
- MCP Server stores artifacts in centralized location accessible across projects

## Acceptance Criteria (High-Level)

### Criterion 1: Validation Tool Functional
**Given** PRD artifact generated with all required sections
**When** Claude Code calls `validate_artifact(content=prd_text, checklist_id="prd_validation_v1")`
**Then** tool returns pass/fail results for all 26 criteria with criterion-level details

### Criterion 2: Path Resolution Tool Functional
**Given** EPIC-006 artifact exists at `artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md`
**When** Claude Code calls `resolve_artifact_path(pattern="artifacts/epics/EPIC-{id}*v{version}.md", id="006", version=1)`
**Then** tool returns exact path in <500ms

### Criterion 3: Validation Checklists as JSON Resources
**Given** validation checklist stored as JSON at `mcp://resources/validation/prd_checklist_v1`
**When** `validate_artifact` tool executes
**Then** tool loads checklist from resource (not hardcoded)

### Criterion 4: Automated vs. Manual Validation Flags
**Given** PRD checklist has 24 automated criteria + 2 manual criteria
**When** `validate_artifact` tool evaluates PRD
**Then** tool returns automated pass/fail results + flags 2 manual criteria for human review

### Criterion 5: Tool Invocation Logging
**Given** Claude Code calls `validate_artifact` tool
**When** tool execution completes
**Then** MCP Server logs invocation with timestamp, input params, duration, result status

### Criterion 6: Store Artifact Tool Functional
**Given** Claude Code generates HLS-006 artifact
**When** Claude Code calls `store_artifact(artifact_type="hls", artifact_id="HLS-006", content="...")`
**Then** artifact stored and returns URI `mcp://resources/artifacts/hls/006`

### Edge Cases & Error Conditions
- **Pattern Matches Zero Files:** Return error: `{error: "No files match pattern", pattern: "..."}`
- **Pattern Matches Multiple Files:** Return error: `{error: "Multiple files match pattern", candidates: [...]}`
- **Malformed Checklist JSON:** Return error: `{error: "Invalid checklist format", checklist_id: "..."}`
- **Validation Failure:** Return detailed failure report with failed criteria IDs

## Scope & Boundaries

### In Scope
- `validate_artifact` tool implementation (Python)
- `resolve_artifact_path` tool implementation (Python)
- `store_artifact` tool implementation (Python)
- Validation checklists as JSON resources (10 types)
- Tool invocation logging for observability
- Automated + manual validation flag support
- All 10 artifact path patterns from CLAUDE.md

### Out of Scope (Deferred to Future Stories)
- Task tracking tools (HLS-009 - get_next_task, update_task_status)
- ID management tools (HLS-009 - get_next_available_id, reserve_id_range)
- AI-powered validation (remain deterministic rule-based)
- Database-backed artifact storage (file-based in Phase 3, database in HLS-011)

## Decomposition into Backlog Stories

### Estimated Backlog Stories (Not Yet Detailed)

1. **Implement validate_artifact Tool** (~8 SP)
   - Brief: Python script accepting artifact content + checklist ID, returning pass/fail results with criterion-level details

2. **Migrate Validation Checklists to JSON Resources** (~3 SP)
   - Brief: Convert 10 validation checklists (PRD, Epic, HLS, etc.) from XML to JSON format, expose as MCP resources

3. **Implement resolve_artifact_path Tool** (~5 SP)
   - Brief: Python script accepting path pattern + variables, returning exact file path using glob search

4. **Implement store_artifact Tool** (~5 SP)
   - Brief: Python script accepting artifact content + metadata, storing in centralized location and returning URI

5. **Tool Invocation Logging** (~3 SP)
   - Brief: Log all tool calls with timestamp, input params, duration, result status (structured JSON format)

6. **Integration Testing for All Tools** (~5 SP)
   - Brief: Test validate_artifact with 10 artifact types, resolve_artifact_path with 10 patterns, store_artifact with sample artifacts

**Total Estimated Story Points:** ~29 SP
**Estimated Sprints:** 1 sprint (Week 4 per PRD-006 timeline)

### Decomposition Strategy
**By Tool:**
- Stories 1-2: Validation tool + checklists
- Story 3: Path resolution tool
- Story 4: Artifact storage tool
- Story 5: Cross-cutting observability
- Story 6: Quality assurance

**Priority Order:** 1 → 2 → 3 → 4 → 5 → 6 (parallel possible for 1-4)

## Dependencies

### User Story Dependencies
- **Depends On:** HLS-006 (MCP Resources Migration - resource infrastructure for checklists)
- **Blocks:** HLS-009 (Task Tracking microservice uses artifact metadata)
- **Blocks:** HLS-010 (CLAUDE.md orchestration references MCP tools)

### External Dependencies
- MCP SDK (Python package) - must support tool protocol
- Claude Code CLI - must support MCP tool calls (stdio/HTTP transport)

## Non-Functional Requirements (User-Facing Only)

- **Reliability:** Tool execution deterministic (same input → same output, no variability)
- **Performance:** Tool execution latency <500ms p95 (per NFR-Performance-02)
- **Observability:** All tool invocations logged with structured JSON format
- **Maintainability:** Validation checklists updatable via JSON file change (no code deployment)

## Risks & Open Questions

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| **Tool Execution Latency Exceeds Target** | Medium - slows artifact generation | Profile and optimize filesystem search, validate <500ms p95 early |
| **Validation Logic Bugs** | High - incorrect pass/fail results | Comprehensive test coverage (≥80%), test with diverse artifact samples |
| **Path Resolution Edge Cases** | Medium - fails to find artifacts | Extensive testing with all 10 path patterns, clear error messages |

### Open Questions

**No open UX or functional questions at this time. Implementation uncertainties will be captured during backlog refinement.**

Technical implementation questions (validation rule logic, glob pattern optimization) deferred to backlog stories and tech specs per PRD-006 §Decisions Made.

## Definition of Ready (Before Backlog Refinement)

- [x] User story statement complete and validated
- [x] User persona identified and documented (AI Agent - Claude Code)
- [x] Business value articulated and quantified (20-30% → <5% error rate)
- [x] High-level acceptance criteria defined (6 criteria)
- [x] Dependencies identified (depends on HLS-006, blocks HLS-009/HLS-010)
- [ ] Product Owner approval obtained

## Definition of Done (High-Level Story Complete)

- [ ] All 6 decomposed backlog stories completed (US-039 through US-044)
- [ ] All acceptance criteria met and validated
- [ ] Validation tool evaluates 25-criterion PRD checklist with 100% accuracy (10 test artifacts)
- [ ] Path resolution tool resolves all 10 artifact path patterns
- [ ] Tool execution latency <500ms p95 (NFR-Performance-02)
- [ ] Error rate <5% validated (vs. 20-30% baseline)
- [ ] Unit test coverage ≥80% (NFR-Maintainability-01)
- [ ] Integration tests passing for all tools
- [ ] Product Owner acceptance obtained

## Related Documents
- **Parent Epic:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md`
- **PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md` (§Timeline & Milestones - Phase 3)
- **Business Research:** `/artifacts/research/AI_Agent_MCP_Server_business_research.md` (§1.1 - Integration Fragmentation, §Token Overhead)
- **User Personas:** PRD-006 §User Personas & Use Cases - Persona 3: AI Agent (Claude Code)
- **Dependency:** HLS-006 (MCP Resources Migration) - resource infrastructure required
