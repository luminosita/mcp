# High-Level User Story: CLAUDE.md Orchestration Update & Integration Testing

## Metadata
- **Story ID:** HLS-010
- **Status:** Draft
- **Priority:** Critical
- **Parent Epic:** EPIC-006
- **Parent PRD:** PRD-006
- **PRD Section:** Phase 5: CLAUDE.md Orchestration Update & Integration Testing (Week 7)
- **Functional Requirements:** FR-12, FR-13
- **Owner:** Product Manager + Tech Lead
- **Target Release:** Phase 5 (Week 7)

## Parent Artifact Context

**Parent Epic:** [EPIC-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md`
- **Epic Contribution:** Integrates all MCP components (resources, prompts, tools) through updated CLAUDE.md orchestration, enabling end-to-end SDLC workflows with 40-60% token reduction (addresses Epic Acceptance Criteria 2 & 3)

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md`
- **PRD Section:** §Timeline & Milestones - Phase 5: CLAUDE.md Orchestration Update & Integration Testing (Week 7)
- **Functional Requirements Coverage:**
  - **FR-12:** Main CLAUDE.md SHALL orchestrate MCP Server integration (resources/prompts/tools)
  - **FR-13:** MCP Server SHALL maintain backward compatibility (local file fallback)

**User Persona Source:** PRD-006 §User Personas - Persona 2: Framework Maintainer + Persona 3: AI Agent

## User Story Statement

**As a** Framework Maintainer,
**I want** main CLAUDE.md to orchestrate MCP resources/prompts/tools instead of local file access,
**So that** all projects automatically use centralized framework infrastructure while maintaining backward compatibility.

## User Context

### Target Persona
**Framework Maintainer (Alex) + AI Agent (Claude Code)**
- Alex updates CLAUDE.md orchestration to reference MCP components
- Claude Code executes SDLC workflows using MCP Server

**User Characteristics:**
- Alex needs confidence that MCP migration doesn't break existing projects
- Claude Code requires seamless transition (same commands, better performance)
- Both need validation that end-to-end workflows function correctly
- Pain point: Risk of breaking changes during infrastructure migration

### User Journey Context
**Before this story:** CLAUDE.md references local files. Claude Code reads implementation pattern files, generators, and templates from local Git repository.

**After this story:** CLAUDE.md orchestrates MCP Server. Claude Code requests resources from `mcp://resources/*`, executes prompts from `mcp://prompts/generator/*`, calls tools via MCP protocol. Local file approach available as fallback.

**Downstream impact:** Enables production pilot (HLS-011) by completing MCP migration. All framework components now MCP-native.

## Business Value

### User Value
- **Zero Breaking Changes:** Existing projects continue functioning with local file approach
- **Gradual Migration:** Projects opt-in to MCP framework incrementally (`use_mcp_framework: true/false`)
- **Performance Improvement:** Token consumption reduced by 40-60% for projects using MCP approach
- **Confidence:** End-to-end testing validates all 10 generator workflows

### Business Value
- **Token Cost Reduction:** Achieves 40-60% token reduction target (per PRD-006 §Executive Summary)
- **Risk Mitigation:** Backward compatibility prevents disruption to existing projects
- **Quality Assurance:** End-to-end testing prevents regression bugs
- **Pilot Readiness:** Validates MCP framework for production use (enables HLS-011)

### Success Criteria
- 10 representative workflows execute successfully using MCP approach (per PRD-006 Phase 5 Success Criteria)
- Token cost reduction ≥40% validated vs. baseline (NFR-Performance-03)
- Backward compatibility mode functional (regression tests passing)
- Internal pilot completed with AI Agent MCP Server project

## Functional Requirements (High-Level)

### Primary User Flow

**Happy Path (MCP Mode):**
1. Developer configures project with MCP framework: `.mcp/config.json` → `{use_mcp_framework: true}`
2. Developer runs `/generate epic-generator`
3. Claude Code reads local CLAUDE.md orchestrator
4. CLAUDE.md instructs: "Load SDLC workflow from `mcp://resources/sdlc/core`"
5. Claude Code requests `mcp://resources/sdlc/core` from MCP Server
6. MCP Server returns sdlc-core.md content (cached, <10ms)
7. Claude Code reads SDLC instructions: "Call `mcp://prompts/generator/epic`"
8. Claude Code calls MCP prompt `mcp://prompts/generator/epic`
9. MCP Server returns epic-generator.xml content
10. Claude Code executes generator, calls `validate_artifact` MCP tool
11. MCP Server validates artifact, returns pass/fail results
12. Claude Code calls `update_task_status` MCP tool to mark task completed
13. Epic artifact generated successfully with 40-60% fewer tokens consumed

**Alternative Flow (Backward Compatibility Mode):**
1. Developer configures project: `.mcp/config.json` → `{use_mcp_framework: false}`
2. Developer runs `/generate epic-generator`
3. Claude Code reads local CLAUDE.md
4. CLAUDE.md detects `use_mcp_framework: false`, falls back to local file reading
5. Claude Code reads local epic-generator.xml from `prompts/epic-generator.xml`
6. Claude Code executes generator using local files
7. Epic artifact generated successfully (same output, local approach)

**Alternative Flow (MCP Server Unavailable):**
1. Claude Code requests `mcp://resources/sdlc/core` but MCP Server unreachable
2. CLAUDE.md detects MCP Server failure (per NFR-Availability-03)
3. CLAUDE.md gracefully degrades to local file approach with warning
4. Developer notified: "⚠️ MCP Server unavailable, using local files"
5. Workflow continues without hard failure

### User Interactions
- Developer configures MCP framework opt-in/opt-out in project config
- Developer runs standard commands (`/generate`, `/refine`) - no syntax changes
- Framework Maintainer updates CLAUDE.md orchestration logic
- Framework Maintainer runs end-to-end integration tests (10 workflows)

### System Behaviors (User Perspective)
- CLAUDE.md detects `use_mcp_framework` configuration flag
- CLAUDE.md orchestrates MCP resources/prompts/tools when enabled
- CLAUDE.md falls back to local files when disabled or MCP Server unavailable
- System logs all MCP requests for observability
- Token usage metrics captured pre/post migration for comparison

## Acceptance Criteria (High-Level)

### Criterion 1: CLAUDE.md Orchestrates MCP Resources
**Given** project configured with `use_mcp_framework: true`
**When** Claude Code reads CLAUDE.md
**Then** CLAUDE.md instructs loading resources from `mcp://resources/sdlc/core` and `mcp://resources/patterns/*` instead of local files

### Criterion 2: CLAUDE.md Orchestrates MCP Prompts
**Given** developer runs `/generate epic-generator`
**When** CLAUDE.md orchestrates generator execution
**Then** CLAUDE.md calls `mcp://prompts/generator/epic` instead of reading local file

### Criterion 3: CLAUDE.md Orchestrates MCP Tools
**Given** Claude Code needs to validate artifact
**When** CLAUDE.md instructions executed
**Then** CLAUDE.md calls `validate_artifact` MCP tool instead of AI inference

### Criterion 4: Backward Compatibility Functional
**Given** project configured with `use_mcp_framework: false`
**When** developer runs workflows
**Then** CLAUDE.md uses local file approach successfully

### Criterion 5: End-to-End Workflows Pass
**Given** 10 representative workflows (epic generation, PRD creation, story breakdown)
**When** workflows executed using MCP approach
**Then** all workflows complete successfully with expected outputs

### Criterion 6: Token Reduction Validated
**Given** same 10 workflows executed with local vs. MCP approach
**When** token usage measured
**Then** MCP approach consumes ≥40% fewer tokens (per NFR-Performance-03)

### Edge Cases & Error Conditions
- **MCP Server Unavailable:** Fall back to local files with warning (no hard failure)
- **Invalid Config:** If `use_mcp_framework` malformed, default to local files
- **Resource Not Found:** Clear error message with fallback guidance

## Scope & Boundaries

### In Scope
- Update main CLAUDE.md to orchestrate MCP resources/prompts/tools
- Update references to use new naming conventions (patterns-*.md, sdlc-core.md)
- Update prompt URLs to use `mcp://prompts/generator/{artifact_name}` pattern
- Backward compatibility mode implementation (`use_mcp_framework` flag)
- Graceful degradation when MCP Server unavailable
- End-to-end integration testing (10 workflows)
- Token usage measurement (pre/post migration comparison)
- Regression testing (local file approach validation)

### Out of Scope (Deferred to Future Stories)
- Production deployment guide (HLS-011)
- Observability dashboard (HLS-011)
- Multi-project pilot expansion (HLS-011 + Decision D1 - 30-day stability period)
- `/refine` command optimization (future enhancement)

## Decomposition into Backlog Stories

### Estimated Backlog Stories (Not Yet Detailed)

1. **Update CLAUDE.md to Orchestrate MCP Resources** (~5 SP)
   - Brief: Refactor CLAUDE.md to reference `mcp://resources/sdlc/core` and `mcp://resources/patterns/*` and `mcp://resources/templates/*`

2. **Update CLAUDE.md to Orchestrate MCP Prompts** (~3 SP)
   - Brief: Update /generate command instructions to call `mcp://prompts/generator/{generator_name}`

3. **Update CLAUDE.md to Orchestrate MCP Tools** (~3 SP)
   - Brief: Update validation/path resolution instructions to call MCP tools instead of AI inference

4. **Implement Backward Compatibility Mode** (~5 SP)
   - Brief: Detect `use_mcp_framework` flag, fall back to local files when false or MCP Server unavailable

5. **End-to-End Integration Testing (10 Workflows)** (~8 SP)
   - Brief: Test epic generation, PRD creation, HLS decomposition, backlog story generation, refinement cycles

6. **Token Usage Measurement and Validation** (~3 SP)
   - Brief: Measure token consumption for 10 workflows (local vs. MCP), validate ≥40% reduction

7. **Regression Testing (Local File Approach)** (~5 SP)
   - Brief: Validate local file approach still functional (backward compatibility validation)

**Total Estimated Story Points:** ~32 SP
**Estimated Sprints:** 1 sprint (Week 7 per PRD-006 timeline)

### Decomposition Strategy
**By Integration Layer:**
- Stories 1-3: Orchestration updates (resources, prompts, tools)
- Story 4: Compatibility layer (fallback logic)
- Stories 5-6: Quality assurance (end-to-end testing, performance validation)
- Story 7: Regression validation (backward compatibility)

**Priority Order:** 1 → 2 → 3 → 4 → 5 → 6 → 7 (sequential for 1-4, parallel for 5-7)

## Dependencies

### User Story Dependencies
- **Depends On:** HLS-006 (MCP Resources), HLS-007 (MCP Prompts), HLS-008 (MCP Tools), HLS-009 (Task Tracking)
- **Blocks:** HLS-011 (Production Readiness - requires integrated system)

### External Dependencies
- All previous HLS stories (HLS-006 through HLS-009) must be complete
- MCP Server deployed and accessible (containerized or cloud-hosted)

## Non-Functional Requirements (User-Facing Only)

- **Reliability:** Graceful degradation when MCP Server unavailable (no hard failures)
- **Performance:** Token consumption reduced by ≥40% (NFR-Performance-03)
- **Compatibility:** Existing projects continue functioning with local file approach
- **Usability:** Developer uses same commands (`/generate`, `/refine`) - transparent migration

## Risks & Open Questions

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| **Backward Compatibility Breaks Projects** | High - blocks existing users | Comprehensive regression testing (50+ test cases), phased rollout |
| **Token Reduction Target Not Met** | Medium - business case weakened | Incremental optimization, profile token-heavy operations |
| **End-to-End Testing Gaps** | Medium - bugs in production | Test all 10 generator types, diverse input scenarios |

### Open Questions

**No open UX or functional questions at this time. Implementation uncertainties will be captured during backlog refinement.**

## Definition of Ready (Before Backlog Refinement)

- [x] User story statement complete
- [x] User personas identified (Framework Maintainer + AI Agent)
- [x] Business value articulated (40-60% token reduction)
- [x] High-level acceptance criteria defined (6 criteria)
- [x] Dependencies identified (depends on HLS-006/007/008/009, blocks HLS-011)
- [ ] Product Owner approval obtained

## Definition of Done (High-Level Story Complete)

- [ ] All 7 decomposed backlog stories completed (US-055 through US-061)
- [ ] All acceptance criteria met and validated
- [ ] 10 representative workflows execute successfully (MCP approach)
- [ ] Token cost reduction ≥40% validated (NFR-Performance-03)
- [ ] Backward compatibility functional (regression tests passing)
- [ ] Internal pilot completed (AI Agent MCP Server project)
- [ ] Unit test coverage ≥80%, integration tests passing
- [ ] Product Owner acceptance obtained

## Related Documents
- **Parent Epic:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md`
- **PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md` (§Timeline & Milestones - Phase 5)
- **Dependencies:** HLS-006, HLS-007, HLS-008, HLS-009 (all must complete first)
- **User Personas:** PRD-006 §User Personas - Persona 2 (Framework Maintainer), Persona 3 (AI Agent)

## Version History
- **v2 (2025-10-18):** Applied feedback - Updated references to new naming conventions (patterns-*.md, sdlc-core.md instead of CLAUDE-*.md). Updated prompt URLs to `mcp://prompts/generator/{artifact_name}` pattern. Updated Criterion 1 to reference mcp://resources/sdlc/core and mcp://resources/patterns/*. Updated backlog story counts (US-055 through US-061).
- **v1 (2025-10-18):** Initial version
