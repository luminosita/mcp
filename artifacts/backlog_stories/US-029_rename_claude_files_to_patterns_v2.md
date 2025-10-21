# User Story: Rename CLAUDE.md Files to Patterns

## Metadata
- **Story ID:** US-029
- **Title:** Rename CLAUDE.md Files to AI-Agent-Agnostic Pattern Names
- **Type:** Feature
- **Status:** Draft
- **Version:** v2 (Applied feedback from US-028-033_v1_comments.md)
- **Priority:** High (unblocks MCP resource server implementation with clear naming)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-006 (MCP Resources Migration)
- **Functional Requirements Covered:** FR-01 (partially - establishes naming for pattern resources)
- **Informed By Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Functional Requirements - FR-01: MCP Server SHALL expose all implementation pattern files as named MCP resources
- **Functional Requirements Coverage:**
  - **FR-01 (partial):** Establishes AI-agent-agnostic file naming (patterns-*.md, sdlc-core.md) before exposing as MCP resources

**Parent High-Level Story:** [HLS-006: MCP Resources Migration]
- **Link:** `/artifacts/hls/HLS-006_mcp_resources_migration_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 2: Rename CLAUDE-*.md Files to patterns-*.md and sdlc-core.md

## User Story
As a Framework Maintainer, I want to rename CLAUDE-*.md files to AI-agent-agnostic names (patterns-*.md, sdlc-core.md), so that the framework is not tied to a specific AI agent platform and can be reused across different AI development tools.

## Description
Current implementation pattern files use "CLAUDE" prefix (CLAUDE-core.md, CLAUDE-tooling.md, CLAUDE-testing.md, etc.), which creates vendor lock-in perception and limits framework reusability across AI agent platforms beyond Claude Code.

This story renames all implementation pattern files to AI-agent-agnostic names following a consistent naming convention:
- **CLAUDE-core.md** → **patterns-core.md** (core development philosophy and orchestration)
- **CLAUDE-tooling.md** → **patterns-tooling.md** (build tools, linters, formatters)
- **CLAUDE-testing.md** → **patterns-testing.md** (testing strategy, fixtures)
- **CLAUDE-typing.md** → **patterns-typing.md** (type system patterns)
- **CLAUDE-validation.md** → **patterns-validation.md** (input validation, security)
- **CLAUDE-architecture.md** → **patterns-architecture.md** (project structure, modularity)
- **CLAUDE-security.md** (if exists) → **patterns-security.md**
- **CLAUDE-auth.md** (if exists) → **patterns-auth.md**
- Main CLAUDE.md SDLC content (from US-028) → **sdlc-core.md**

After renaming, file references in all documents (main CLAUDE.md, generators, templates) must be updated to use new names. This establishes consistent naming before exposing files as MCP resources in US-030.

## Implementation Research References

**Primary Research Document:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

**Technical Patterns Applied:**
- **§2.2: FastAPI Backend Framework:** Resource naming conventions inform MCP resource URI design (`mcp://resources/patterns/core` maps to `patterns-core.md`) - ref: Implementation Research §2.2

**Note:** This is a documentation refactoring task, not a code implementation task. No direct code patterns from Implementation Research apply. The naming convention supports future MCP resource URI design.

## Functional Requirements
1. Rename all CLAUDE-*.md files in `new_prompts/CLAUDE/python/` directory to patterns-*.md
2. Rename main SDLC content file (created in US-028) from tentative name to sdlc-core.md
3. Update all file references in main CLAUDE.md orchestrator
4. Update all file references in generator XML files (if any CLAUDE-*.md files referenced)
5. Update all file references in template XML files (if any CLAUDE-*.md files referenced)
6. Update folder structure documentation in sdlc-core.md to reflect new naming
7. Preserve all file content (rename only, no content changes)
8. Language-specific subdirectory structure unchanged (new_prompts/CLAUDE/python/, new_prompts/CLAUDE/go/)

## Non-Functional Requirements
- **Consistency:** All pattern files use "patterns-" prefix consistently
- **Traceability:** Version history updated in renamed files documenting the change
- **Maintainability:** Clear naming convention documented in sdlc-core.md
- **Backward Compatibility:** Reference update ensures no broken links (deferred orchestration logic to US-056)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story renames CLAUDE-*.md files themselves. No specialized implementation standards apply (documentation refactoring only).

### Implementation Guidance
This is a manual file renaming and reference update task. Approach:

1. **Inventory Current Files:**
   - List all CLAUDE-*.md files in `new_prompts/CLAUDE/python/`
   - Document current file names and line counts
   - Example inventory:
     ```
     new_prompts/CLAUDE/python/CLAUDE-core.md (250 lines)
     new_prompts/CLAUDE/python/CLAUDE-tooling.md (180 lines)
     new_prompts/CLAUDE/python/CLAUDE-testing.md (220 lines)
     new_prompts/CLAUDE/python/CLAUDE-typing.md (150 lines)
     new_prompts/CLAUDE/python/CLAUDE-validation.md (200 lines)
     new_prompts/CLAUDE/python/CLAUDE-architecture.md (170 lines)
     ```

2. **Execute Renaming:**
   - Use `git mv` to preserve version history:
     ```bash
     git mv new_prompts/CLAUDE/python/CLAUDE-core.md new_prompts/CLAUDE/python/patterns-core.md
     git mv new_prompts/CLAUDE/python/CLAUDE-tooling.md new_prompts/CLAUDE/python/patterns-tooling.md
     git mv new_prompts/CLAUDE/python/CLAUDE-testing.md new_prompts/CLAUDE/python/patterns-testing.md
     git mv new_prompts/CLAUDE/python/CLAUDE-typing.md new_prompts/CLAUDE/python/patterns-typing.md
     git mv new_prompts/CLAUDE/python/CLAUDE-validation.md new_prompts/CLAUDE/python/patterns-validation.md
     git mv new_prompts/CLAUDE/python/CLAUDE-architecture.md new_prompts/CLAUDE/python/patterns-architecture.md
     ```
   - Rename main SDLC file (if not already named):
     ```bash
     git mv new_prompts/CLAUDE/sdlc-content.md new_prompts/CLAUDE/sdlc-core.md
     ```

3. **Update File References:**
   - Search and replace in main CLAUDE.md:
     - "CLAUDE-core.md" → "patterns-core.md"
     - "CLAUDE-tooling.md" → "patterns-tooling.md"
     - (continue for all files)
   - Search and replace in all generator XML files (`new_prompts/*-generator.xml`)
   - Search and replace in all template XML files (`new_prompts/templates/*-template.xml`)
   - Use case-sensitive search to avoid false matches

4. **Update Documentation:**
   - Update Folder Structure section in sdlc-core.md documenting new naming convention
   - Add version history entry to all renamed files
   - Document naming rationale: "Renamed from CLAUDE-*.md to patterns-*.md for AI-agent-agnostic framework design"

5. **Validate References:**
   - Grep for remaining "CLAUDE-" references (should only find "CLAUDE.md" and historical version notes)
   - Test that all file references resolve correctly

### Technical Tasks
- [ ] Inventory current CLAUDE-*.md files
- [ ] Rename files using `git mv` (preserves history)
- [ ] Update references in main CLAUDE.md
- [ ] Update references in generator XML files
- [ ] Update references in template XML files
- [ ] Update Folder Structure documentation in sdlc-core.md
- [ ] Add version history entries to renamed files
- [ ] Validate no broken references remain

## Acceptance Criteria

### Scenario 1: All pattern files renamed successfully
**Given** CLAUDE-*.md files exist in `new_prompts/CLAUDE/python/`
**When** renaming is complete
**Then** all files use "patterns-" prefix: patterns-core.md, patterns-tooling.md, patterns-testing.md, patterns-typing.md, patterns-validation.md, patterns-architecture.md
**And** main SDLC file named sdlc-core.md
**And** no CLAUDE-*.md files remain in new_prompts/CLAUDE/ directory (excluding main CLAUDE.md orchestrator)

### Scenario 2: Git history preserved
**Given** files renamed using `git mv`
**When** I run `git log --follow new_prompts/CLAUDE/python/patterns-core.md`
**Then** Git history shows original CLAUDE-core.md commits
**And** rename operation visible in Git history

### Scenario 3: File references updated in CLAUDE.md
**Given** main CLAUDE.md references pattern files
**When** I search for "CLAUDE-" in CLAUDE.md
**Then** only "CLAUDE.md" itself appears (no CLAUDE-*.md references)
**And** all references use patterns-*.md naming

### Scenario 4: File references updated in generators and templates
**Given** generators and templates reference pattern files
**When** I grep for "CLAUDE-" in `new_prompts/*.xml` and `new_prompts/templates/*.xml`
**Then** no CLAUDE-*.md references found (only CLAUDE.md orchestrator if applicable)
**And** all pattern file references use patterns-*.md naming

### Scenario 5: Documentation updated
**Given** sdlc-core.md documents folder structure
**When** I read Folder Structure section
**Then** naming convention documented: "new_prompts/CLAUDE/python/patterns-*.md"
**And** AI-agent-agnostic naming rationale explained
**And** version history includes rename entry with date

### Scenario 6: No broken references
**Given** all file references updated
**When** Claude Code reads CLAUDE.md and follows references
**Then** all pattern file references resolve successfully
**And** no file-not-found errors occur

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 3 SP (below 5 SP threshold - CONSIDER territory)
- **Developer Count:** Single developer (solo work)
- **Domain Span:** Single domain (documentation refactoring only, no code)
- **Complexity:** Low - straightforward file renaming and reference updates (scripted or manual)
- **Uncertainty:** Low - clear renaming instructions, no technical decisions
- **Override Factors:** None - simple documentation refactoring, not cross-domain, not security-critical, no system integration

Per SDLC Section 11.6 Decision Matrix: "1-2 SP, single dev, single domain → SKIP (Overhead not justified)". This 3 SP story with single developer and straightforward file renaming falls into "overhead not justified" category.

## Definition of Done
- [ ] All CLAUDE-*.md files renamed to patterns-*.md
- [ ] Main SDLC file renamed to sdlc-core.md
- [ ] File references updated in CLAUDE.md
- [ ] File references updated in all generator XML files
- [ ] File references updated in all template XML files
- [ ] Folder Structure documentation updated in sdlc-core.md
- [ ] Version history updated in all renamed files
- [ ] Git history preserved (verified with `git log --follow`)
- [ ] Validation: No broken references (grep confirms)
- [ ] Product Owner approval obtained

## Additional Information
**Suggested Labels:** documentation, refactoring, mcp-resources, naming-convention
**Estimated Story Points:** 3
**Dependencies:**
- **Depends On:** US-028 (refactor must complete before renaming sdlc-core.md)
- **Blocks:** US-030 (MCP resource server implementation depends on final file names)

**Related PRD Section:** PRD-006 §Functional Requirements - FR-01

## Decisions Made

**D1: No Technical Decisions Required**
- Renaming strategy is straightforward: Use `git mv` to preserve history, update references with search-and-replace, validate with grep
- All technical approaches clear from HLS-006 decomposition plan
- No implementation uncertainties identified

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-006_mcp_resources_migration_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`
