# User Story: Update CLAUDE.md to Orchestrate MCP Resources

## Metadata
- **Story ID:** US-056
- **Title:** Update CLAUDE.md to Orchestrate MCP Resources
- **Type:** Feature
- **Status:** Backlog
- **Priority:** High - Critical infrastructure refactoring that enables MCP-native architecture and 40-60% token reduction
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-010
- **Functional Requirements Covered:** FR-01, FR-02, FR-04, FR-12, FR-20
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Requirements - FR-01, FR-02, FR-04, FR-12; §Timeline & Milestones - Phase 1 (Weeks 1-2)
- **Functional Requirements Coverage:**
  - **FR-01:** MCP Server SHALL expose all implementation pattern files (sdlc-core.md, patterns-*.md) as named MCP resources with AI-agent-agnostic naming
  - **FR-02:** MCP Server SHALL expose all artifact templates (prompts/templates/*.xml) as named MCP resources
  - **FR-04:** MCP Server SHALL refactor main CLAUDE.md into orchestrator (remains local) + SDLC workflow instructions (new prompts/CLAUDE/sdlc-core.md served as MCP resource)
  - **FR-12:** Main CLAUDE.md SHALL be refactored to orchestrate MCP Server integration, directing Claude Code to use MCP resources/prompts/tools instead of local file access
  - **FR-20:** MCP Server SHALL implement resource caching with TTL to reduce repeated file I/O

**Parent High-Level Story:** [HLS-010: CLAUDE.md Orchestration Update & Integration Testing]
- **Link:** `/artifacts/hls/HLS-010_claude_orchestration_integration_testing_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 1

## User Story
As a Framework Maintainer, I want main CLAUDE.md refactored to orchestrate MCP resources instead of containing SDLC content directly, so that all projects automatically load framework components from centralized MCP Server with 40-60% token reduction.

## Description

The current main CLAUDE.md file contains 800+ lines of SDLC workflow instructions, artifact dependency flows, folder structures, and orchestration logic. When Claude Code reads this file on every task execution, it consumes significant tokens for content that rarely changes. Additionally, updating framework components requires modifying CLAUDE.md directly, making it difficult to version SDLC instructions separately from orchestration logic.

This story refactors CLAUDE.md into two components:
1. **Local CLAUDE.md (Orchestrator):** Remains in project repository (~200 lines), directs Claude Code to load SDLC instructions from MCP resources
2. **sdlc-core.md (MCP Resource):** Migrated SDLC workflow content, served by MCP Server as `mcp://resources/sdlc/core`

Additionally, all implementation pattern files (CLAUDE-*.md → patterns-*.md) and templates will be referenced via MCP resources instead of local file paths. This enables token-efficient loading (only load resources when needed), centralized framework updates (update MCP Server once, all projects benefit), and multi-language support (language-specific pattern files organized by subdirectory).

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§4.2: MCP Resources Pattern:** CLAUDE.md references MCP resources using URI scheme `mcp://resources/sdlc/core`, `mcp://resources/patterns/python/core`, etc.
  - **Example:** Replace local file references with MCP resource URIs in orchestration instructions
- **§4.1: Resource Caching:** MCP Server caches frequently accessed resources (sdlc-core.md, patterns-*.md) with 5-minute TTL per FR-20
  - **Performance Target:** First request 50ms (disk I/O), subsequent requests <10ms (cache hit)
- **§6.3: Configuration Management:** Projects configure MCP framework opt-in via `.mcp/config.json` with `use_mcp_framework: true/false` flag
  - **Backward Compatibility:** When false, fall back to local file approach (addressed in US-059)

**Anti-Patterns Avoided:**
- **§6.1: Monolithic Configuration Files:** Avoid bundling all SDLC content in single CLAUDE.md (current approach causes token waste and difficult versioning)
- **§6.2: Hardcoded File Paths:** Avoid hardcoded local file paths in orchestration logic (prevents centralized framework updates)

**Performance Considerations:**
- **§8.1: Token Optimization:** Reducing CLAUDE.md from 800+ lines to ~200 lines saves ~15-20k tokens per task execution (assuming Claude Code reads CLAUDE.md on every task)
- **§8.2: Resource Caching:** MCP Server caching reduces latency from 50ms (disk I/O) to <10ms (cache hit) for frequently accessed resources

## Functional Requirements
- Refactor main CLAUDE.md to orchestrator-only (~200 lines maximum)
- Extract SDLC workflow instructions to new sdlc-core.md file
- Update all CLAUDE-*.md file references to patterns-*.md naming convention
- Update CLAUDE.md to reference MCP resources using URI scheme (mcp://resources/sdlc/core, mcp://resources/patterns/*, mcp://resources/templates/*)
- Update folder structure section to reference MCP resource paths instead of local file paths
- Maintain functional equivalence (validation test suite passes pre/post refactoring)
- Document MCP resource URI patterns for templates and pattern files

## Non-Functional Requirements
- **Performance:** Token consumption reduced by 15-20k tokens per CLAUDE.md load (measured via Claude API telemetry)
- **Maintainability:** CLAUDE.md reduced to <200 lines for clarity and easier orchestration updates
- **Compatibility:** Functional equivalence validated via test suite (same outputs pre/post refactoring)
- **Documentation:** Clear comments explaining MCP resource loading logic and fallback behavior

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story implements the hybrid approach defined in CLAUDE.md and PRD-006 v3 Decision D1.

### Implementation Guidance

**Step 1: Create sdlc-core.md from CLAUDE.md Content**
- Extract SDLC Artifact Dependency Flow section → sdlc-core.md
- Extract Input Classification System section → sdlc-core.md
- Extract Spike Workflow section → sdlc-core.md
- Extract Open Questions Marker System section → sdlc-core.md
- Extract Generate Command Instructions section → sdlc-core.md
- Extract ID Assignment Strategy section → sdlc-core.md
- Extract artifact path patterns table → sdlc-core.md
- Save as: `prompts/CLAUDE/sdlc-core.md`

**Step 2: Rename CLAUDE-*.md Files to patterns-*.md (AI-Agent-Agnostic Naming)**

Per PRD-006 v3 Decision and Epic feedback, rename implementation pattern files for AI-agent-agnostic naming:

**Python Implementation Patterns:**
```
prompts/CLAUDE/python/CLAUDE-core.md        → prompts/CLAUDE/python/patterns-core.md
prompts/CLAUDE/python/CLAUDE-tooling.md     → prompts/CLAUDE/python/patterns-tooling.md
prompts/CLAUDE/python/CLAUDE-testing.md     → prompts/CLAUDE/python/patterns-testing.md
prompts/CLAUDE/python/CLAUDE-typing.md      → prompts/CLAUDE/python/patterns-typing.md
prompts/CLAUDE/python/CLAUDE-validation.md  → prompts/CLAUDE/python/patterns-validation.md
prompts/CLAUDE/python/CLAUDE-architecture.md → prompts/CLAUDE/python/patterns-architecture.md
```

**Go Implementation Patterns:**
```
prompts/CLAUDE/go/CLAUDE-core.md        → prompts/CLAUDE/go/patterns-core.md
prompts/CLAUDE/go/CLAUDE-tooling.md     → prompts/CLAUDE/go/patterns-tooling.md
(Additional Go pattern files as needed)
```

**Rationale:** Supports multiple AI agents (not just Claude), enables language-agnostic framework reuse.

**Step 3: Refactor Main CLAUDE.md to Orchestrator**
- Reduce CLAUDE.md to orchestration logic only (~200 lines max):
  - General section (product name, package name)
  - Folder structure reference: "See mcp://resources/sdlc/core for SDLC folder structure"
  - Implementation Phase section: "For implementation work, see mcp://resources/patterns/{language}/*"
  - MCP resource loading instructions
  - Configuration detection logic (`use_mcp_framework` flag)
- Add MCP resource URI references:
  - SDLC core: `mcp://resources/sdlc/core`
  - Implementation patterns: `mcp://resources/patterns/{language}/{pattern_name}` (e.g., `mcp://resources/patterns/python/core`)
  - Templates: `mcp://resources/templates/{template_name}` (e.g., `mcp://resources/templates/prd-template`)
- Add backward compatibility notes (fallback to local files when MCP unavailable - implementation in US-059)

**Step 4: Update Folder Structure Section**
- Replace inline folder structure with reference: "See mcp://resources/sdlc/core §Folder Structure for complete hierarchy and naming conventions"
- Keep only essential project-specific paths in local CLAUDE.md (if any)
- Update artifact path resolution algorithm to reference MCP resource paths

**Step 5: Validation**
- Compare CLAUDE.md content pre/post refactoring (line count reduced from 800+ to ~200)
- Verify sdlc-core.md contains all extracted SDLC sections
- Verify all pattern files renamed with patterns-* convention
- Run validation test suite (if available) to confirm functional equivalence
- Test MCP resource loading (requires US-030/031 completion for MCP Server resource endpoints)

**References to Implementation Standards:**
- patterns-architecture.md: Follow established project structure for file organization
- patterns-core.md: Core development philosophy applies to refactoring approach
- patterns-validation.md: Validate CLAUDE.md orchestration logic with schema validation (future enhancement)

### Technical Tasks
- [ ] Create `prompts/CLAUDE/sdlc-core.md` with extracted SDLC workflow content
- [ ] Rename `CLAUDE-*.md` files to `patterns-*.md` across all language subdirectories
- [ ] Refactor main CLAUDE.md to orchestrator-only (~200 lines)
- [ ] Add MCP resource URI references to CLAUDE.md
- [ ] Update folder structure section to reference sdlc-core.md
- [ ] Update artifact path resolution algorithm section
- [ ] Add MCP resource loading instructions to CLAUDE.md
- [ ] Document backward compatibility approach (reference US-059)
- [ ] Validate functional equivalence (comparison test)
- [ ] Update all artifact templates to reference patterns-*.md naming convention (ensure consistency)

## Acceptance Criteria

### Scenario 1: CLAUDE.md Reduced to Orchestrator
**Given** main CLAUDE.md contains 800+ lines of SDLC content
**When** refactoring is complete
**Then** main CLAUDE.md is <200 lines (orchestration only, no inline SDLC content)

### Scenario 2: SDLC Content Migrated to sdlc-core.md
**Given** SDLC workflow sections extracted from CLAUDE.md
**When** sdlc-core.md is created at `prompts/CLAUDE/sdlc-core.md`
**Then** sdlc-core.md contains all extracted sections (Artifact Dependency Flow, Input Classification, Spike Workflow, Open Questions, Generate Command Instructions, ID Assignment Strategy, Artifact Path Patterns)

### Scenario 3: Implementation Pattern Files Renamed
**Given** implementation pattern files named CLAUDE-*.md in language subdirectories
**When** renaming is complete
**Then** all files use patterns-*.md naming convention (e.g., patterns-core.md, patterns-tooling.md, patterns-testing.md, etc.) across Python and Go subdirectories

### Scenario 4: MCP Resource URIs Referenced in CLAUDE.md
**Given** CLAUDE.md orchestrator refactored
**When** framework components referenced
**Then** CLAUDE.md uses MCP resource URIs:
- `mcp://resources/sdlc/core` for SDLC workflow instructions
- `mcp://resources/patterns/{language}/{pattern_name}` for implementation patterns
- `mcp://resources/templates/{template_name}` for artifact templates

### Scenario 5: Functional Equivalence Validated
**Given** CLAUDE.md refactored with MCP resource references
**When** validation test suite executes
**Then** all tests pass (same behavior as pre-refactoring baseline)

### Scenario 6: Folder Structure References Updated
**Given** Folder Structure section previously inline in CLAUDE.md
**When** refactoring complete
**Then** Folder Structure section replaced with reference: "See mcp://resources/sdlc/core §Folder Structure for complete hierarchy"

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 5 SP (CONSIDER threshold but below DON'T SKIP at 8+ SP)
- **Developer Count:** Single developer (straightforward refactoring work)
- **Domain Span:** Single domain (documentation/configuration refactoring only, no code changes)
- **Complexity:** Low - Well-defined refactoring (extract sections, rename files, update references)
- **Uncertainty:** Low - Clear transformation path defined in technical requirements
- **Override Factors:** None - No cross-domain dependencies, no security-critical changes, no unfamiliar technology

**Conclusion:** While 5 SP is at CONSIDER threshold, the straightforward nature of the refactoring (single developer, single domain, low complexity, clear path) does not warrant task decomposition. Implementation can proceed as a single cohesive unit of work within one sprint.

## Definition of Done
- [ ] sdlc-core.md created at `prompts/CLAUDE/sdlc-core.md` with all extracted SDLC sections
- [ ] All CLAUDE-*.md files renamed to patterns-*.md across Python and Go subdirectories
- [ ] Main CLAUDE.md refactored to <200 lines (orchestration only)
- [ ] MCP resource URI references added to CLAUDE.md for sdlc-core, patterns-*, and templates
- [ ] Folder Structure section updated to reference sdlc-core.md
- [ ] Functional equivalence validated (comparison test passes)
- [ ] Code reviewed and approved
- [ ] Documentation updated (CHANGELOG or migration notes)
- [ ] Product Owner acceptance obtained

## Additional Information
**Suggested Labels:** refactoring, infrastructure, mcp-resources, documentation
**Estimated Story Points:** 5
**Dependencies:**
- **Blocks:** US-057 (MCP Prompts), US-058 (MCP Tools), US-059 (Backward Compatibility) - all depend on CLAUDE.md orchestrator structure
- **Enables:** US-060 (Integration Testing) - requires refactored CLAUDE.md to test MCP resource loading
- **Related:** US-029 (Rename CLAUDE Files to Patterns) - This story implements the renaming as part of the refactoring

## Decisions Made

**All technical approaches clear from PRD-006 v3 §Requirements and §Technical Considerations.**

**Key Decisions Already Made:**
- File naming convention: patterns-*.md per PRD-006 v3 Decision and Epic feedback
- MCP resource URI scheme: `mcp://resources/{type}/{name}` per FR-01, FR-02, FR-04
- CLAUDE.md size target: <200 lines per FR-04
- Language subdirectory structure: `prompts/CLAUDE/{language}/` per existing folder structure

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-010_claude_orchestration_integration_testing_v2.md`
- **Parent Epic:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`
- **Related Stories:** US-029 (Rename CLAUDE Files to Patterns), US-030 (MCP Resource Server Implementation), US-031 (MCP Resource Server for Templates)

## Version History
- **v1 (2025-10-18):** Initial version
