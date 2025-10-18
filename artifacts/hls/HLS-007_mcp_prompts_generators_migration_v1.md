# High-Level User Story: MCP Prompts - Generators Migration

## Metadata
- **Story ID:** HLS-007
- **Status:** Draft
- **Priority:** Critical
- **Parent Epic:** EPIC-006
- **Parent PRD:** PRD-006
- **PRD Section:** Phase 2: MCP Prompts - Generators Migration (Week 3)
- **Functional Requirements:** FR-05
- **Owner:** Product Manager + Tech Lead
- **Target Release:** Phase 2 (Week 3)

## Parent Artifact Context

**Parent Epic:** [EPIC-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md`
- **Epic Contribution:** Migrates artifact generators to MCP prompts, enabling centralized generator management and automatic updates across all projects (addresses Epic Acceptance Criterion 1 - MCP Resources Migration)

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md`
- **PRD Section:** §Timeline & Milestones - Phase 2: MCP Prompts - Generators Migration (Week 3)
- **Functional Requirements Coverage:**
  - **FR-05:** MCP Server SHALL expose all artifact generators (prompts/*-generator.xml) as MCP prompts

**User Persona Source:** PRD-006 §User Personas - Persona 2: Framework Maintainer (Core Team)

## User Story Statement

**As a** Framework Maintainer,
**I want** artifact generators (epic-generator, prd-generator, etc.) accessible through MCP prompts instead of local Git files,
**So that** generator updates propagate instantly to all projects without requiring manual file synchronization.

## User Context

### Target Persona
**Framework Maintainer (Core Team) - "Alex"**
- Senior engineer maintaining SDLC artifact generators
- Receives feedback from teams on generator quality and needs to iterate
- Manages 10+ generator types across Python, Go, and future language projects

**User Characteristics:**
- Currently maintains generators in local Git repository, manually copied to each project
- Frustrated by version drift where projects use different generator versions
- Values instant propagation of generator improvements
- Pain point: Generator bug fixes take hours/days to propagate across all projects (manual Git pull required)

### User Journey Context
**Before this story:** Generators stored as local files (prompts/*.xml) requiring manual synchronization. When Alex fixes a bug in prd-generator.xml, must notify all teams to `git pull` latest version.

**After this story:** Generators exposed as MCP prompts. When Alex updates prd-generator.xml and deploys MCP Server, all projects automatically use updated generator on next execution - zero client-side action required.

**Downstream impact:** Enables consistent generator execution across all projects. Required for HLS-010 (CLAUDE.md orchestration update) to reference MCP prompts instead of local files.

## Business Value

### User Value
- **Instant Propagation:** Generator updates available immediately to all projects (vs. hours/days manual sync)
- **Consistency:** Eliminates version drift ensuring all projects use same generator versions
- **Simplified Workflow:** No need to coordinate "please pull latest generators" messages to teams
- **Confidence:** Generator improvements automatically benefit all projects

### Business Value
- **Quality Improvement:** Generator bug fixes propagate instantly, reducing artifact quality issues by ~40%
- **Maintenance Efficiency:** Reduces generator update overhead from 2-4 hours to <10 minutes (per PRD-006 §Goals)
- **Scalability:** Supports 5+ concurrent projects without proportional generator maintenance burden
- **Consistency Guarantee:** 100% of projects using same generator version at any given time (vs. 60-70% with manual sync)

### Success Criteria
- 10 generator prompts accessible via MCP protocol (per PRD-006 Phase 2 Success Criteria)
- `/generate` command successfully orchestrates MCP prompt calls
- Generated artifacts byte-identical to local file approach (per NFR-Compatibility-02)
- Generator update propagation time <1 minute (vs. hours/days baseline)

## Functional Requirements (High-Level)

### Primary User Flow

**Happy Path:**
1. Framework Maintainer identifies bug in prd-generator.xml (e.g., validation criteria inconsistency)
2. Framework Maintainer edits prompts/prd-generator.xml in MCP Server repository
3. Framework Maintainer commits and deploys updated MCP Server
4. Developer in Project-Alpha runs `/generate prd-generator` command
5. Local `/generate` command (in .claude/commands/generate.md) calls MCP prompt `mcp://prompts/prd-generator`
6. MCP Server loads prd-generator.xml from disk
7. MCP Server returns generator prompt content to Claude Code
8. Claude Code executes generator with PRD-006 parent epic as input
9. PRD-006 v3 generated with corrected validation criteria
10. Developer in Project-Beta runs `/generate prd-generator` later same day
11. Automatically receives same updated generator (no manual sync required)

**Alternative Flows:**
- **Alt Flow 1: Different Generator Type:** If developer runs `/generate epic-generator`, MCP Server loads epic-generator.xml instead
- **Alt Flow 2: Generator Not Found:** If developer requests non-existent generator, MCP Server returns clear error: "Prompt not found: mcp://prompts/invalid-generator"
- **Alt Flow 3: Backward Compatibility:** If project uses local generators (opt-out mode), `/generate` command falls back to local file reading (per FR-13)

### User Interactions
- Framework Maintainer edits generator XML files in MCP Server repository (not in individual projects)
- Framework Maintainer deploys updated MCP Server
- Developer runs `/generate` command (same command syntax, transparent MCP vs. local file)
- Framework Maintainer monitors generator execution success rate via observability dashboard

### System Behaviors (User Perspective)
- MCP Server detects generator file changes on deployment
- MCP Server loads generator content from disk when requested
- MCP Server returns generator prompt to Claude Code for execution
- Local `/generate` command orchestrates MCP prompt call (references mcp://prompts/{generator_name})
- All projects receive same generator version automatically

## Acceptance Criteria (High-Level)

### Criterion 1: All Generators Accessible as MCP Prompts
**Given** MCP Server deployed with 10 generators at `prompts/*-generator.xml`
**When** Claude Code requests `mcp://prompts/prd-generator`
**Then** MCP Server returns prd-generator.xml content

### Criterion 2: /generate Command Orchestrates MCP Prompt Calls
**Given** `/generate` command updated to reference MCP prompts
**When** developer runs `/generate epic-generator`
**Then** command calls `mcp://prompts/epic-generator` and executes successfully

### Criterion 3: Generated Artifacts Byte-Identical
**Given** same input artifacts (parent epic, business research)
**When** generator executed via MCP prompt vs. local file
**Then** output artifacts are byte-identical (per NFR-Compatibility-02)

### Criterion 4: All 10 Generator Types Supported
**Given** 10 generator types (product-vision, initiative, epic, prd, hls, backlog-story, spike, adr, tech-spec, implementation-task)
**When** each generator requested as MCP prompt
**Then** all 10 generators accessible and functional

### Criterion 5: Generator Update Propagation Instant
**Given** Framework Maintainer deploys updated prd-generator.xml
**When** developer runs `/generate prd-generator` 1 minute later
**Then** updated generator version used automatically

### Edge Cases & Error Conditions
- **Generator Not Found:** If requested generator doesn't exist, return error: "Prompt not found: mcp://prompts/{name}"
- **Malformed Generator XML:** If generator XML parsing fails, return error with line number and issue details
- **Backward Compatibility:** If project uses local generators (use_mcp_framework: false), fall back to local file reading without error

## Scope & Boundaries

### In Scope
- Migration of all 10 artifact generators to MCP prompts
- Update `/generate` command to call MCP prompts instead of local files
- Integration testing for all 10 generator types
- Validation that output artifacts byte-identical (local vs. MCP approach)
- Backward compatibility support (local file fallback)

### Out of Scope (Deferred to Future Stories)
- `/refine` command update (deferred to HLS-010 - CLAUDE.md orchestration)
- Generator parameter validation (deferred to backlog stories)
- Generator versioning strategy (e.g., prd-generator-v1, prd-generator-v2) - future enhancement
- Generator execution caching (optimization for future phase)

## Decomposition into Backlog Stories

### Estimated Backlog Stories (Not Yet Detailed)

1. **Expose Generators as MCP Prompts** (~8 SP)
   - Brief: MCP Server exposes all 10 generators (prompts/*-generator.xml) as MCP prompts with prompt protocol support

2. **Update /generate Command to Call MCP Prompts** (~5 SP)
   - Brief: Refactor .claude/commands/generate.md to call `mcp://prompts/{generator_name}` instead of local file reading

3. **Integration Testing for All Generator Types** (~5 SP)
   - Brief: Test all 10 generators via MCP prompts, validate output artifacts byte-identical to local file approach

4. **Backward Compatibility Mode Implementation** (~3 SP)
   - Brief: Implement fallback to local file reading when `use_mcp_framework: false` in project config

5. **Error Handling and User Messaging** (~2 SP)
   - Brief: Clear error messages for missing generators, malformed XML, MCP Server unavailable

**Total Estimated Story Points:** ~23 SP
**Estimated Sprints:** 1 sprint (Week 3 per PRD-006 timeline)

### Decomposition Strategy
**By Feature Area:**
- Story 1: Core generator migration (MCP prompt exposure)
- Story 2: Client-side orchestration (update /generate command)
- Story 3: Quality assurance (integration testing)
- Story 4: Compatibility (backward compatibility mode)
- Story 5: User experience (error handling)

**Priority Order:** 1 → 2 → 3 → 4 → 5 (sequential dependencies)

## Dependencies

### User Story Dependencies
- **Depends On:** HLS-006 (MCP Resources Migration - infrastructure must exist for prompts)
- **Blocks:** HLS-010 (CLAUDE.md orchestration update references MCP prompts)

### External Dependencies
- MCP SDK (Python package) - must support prompt protocol
- Claude Code CLI - must support MCP prompt execution (stdio/HTTP transport)

## Non-Functional Requirements (User-Facing Only)

- **Usability:** Developer uses same `/generate` command syntax (transparent MCP vs. local file)
- **Reliability:** Generator loading failures gracefully degrade to local file fallback (per NFR-Availability-03)
- **Consistency:** All projects use same generator version at any given time (100% consistency vs. 60-70% with manual sync)
- **Backward Compatibility:** Projects using local generators continue functioning during migration (per FR-13)

## Risks & Open Questions

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| **MCP Prompt Protocol Breaking Changes** | High - could block generator execution | Pin MCP SDK version, monitor protocol changelog |
| **Generator Execution Failures** | High - blocks artifact generation | Comprehensive integration testing for all 10 generators, rollback plan |
| **Backward Compatibility Breaks Projects** | High - blocks local file users | Extensive regression testing with both modes, phased rollout |

### Open Questions

**No open UX or functional questions at this time. Implementation uncertainties will be captured during backlog refinement.**

Technical implementation questions (MCP prompt protocol details, error handling strategies) deferred to backlog stories and tech specs per PRD-006 §Decisions Made.

## Definition of Ready (Before Backlog Refinement)

- [x] User story statement complete and validated
- [x] User persona identified and documented (Framework Maintainer - Alex)
- [x] Business value articulated and quantified (2-4 hours → <10 minutes)
- [x] High-level acceptance criteria defined (5 criteria)
- [x] Dependencies identified (depends on HLS-006, blocks HLS-010)
- [ ] Product Owner approval obtained

## Definition of Done (High-Level Story Complete)

- [ ] All 5 decomposed backlog stories completed (US-034 through US-038)
- [ ] All acceptance criteria met and validated
- [ ] 10 generator prompts accessible via MCP protocol
- [ ] `/generate` command successfully orchestrates MCP prompt calls
- [ ] Generated artifacts byte-identical (local vs. MCP) - validated with 10 sample artifacts
- [ ] Backward compatibility mode functional (regression tests passing)
- [ ] Unit test coverage ≥80% (NFR-Maintainability-01)
- [ ] Integration tests passing for all 10 generator types
- [ ] Product Owner acceptance obtained

## Related Documents
- **Parent Epic:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md`
- **PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md` (§Timeline & Milestones - Phase 2)
- **Business Research:** `/artifacts/research/AI_Agent_MCP_Server_business_research.md` (§1.1 - Integration Fragmentation)
- **User Personas:** PRD-006 §User Personas & Use Cases - Persona 2: Framework Maintainer
- **Dependency:** HLS-006 (MCP Resources Migration) - must complete first
