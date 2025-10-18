# User Story: Refactor Main CLAUDE.md into Orchestrator + SDLC Resource

## Metadata
- **Story ID:** US-028
- **Title:** Refactor Main CLAUDE.md into Orchestrator + SDLC Resource
- **Type:** Feature
- **Status:** Draft
- **Priority:** Critical (foundational for MCP resources migration - blocks all downstream stories)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-006 (MCP Resources Migration)
- **Functional Requirements Covered:** FR-04
- **Informed By Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Functional Requirements - FR-04: MCP Server SHALL refactor main CLAUDE.md into orchestrator + SDLC workflow resource
- **Functional Requirements Coverage:**
  - **FR-04:** MCP Server SHALL refactor main CLAUDE.md into orchestrator + SDLC workflow resource containing folder structure, ID assignment, artifact paths, dependency flow, markers

**Parent High-Level Story:** [HLS-006: MCP Resources Migration]
- **Link:** `/artifacts/hls/HLS-006_mcp_resources_migration_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 1: Refactor Main CLAUDE.md into Orchestrator + SDLC Resource

## User Story
As a Framework Maintainer, I want to split main CLAUDE.md into a local orchestrator (<200 lines) and an MCP-served SDLC resource, so that SDLC framework content can be centralized in the MCP server while project-specific orchestration remains local.

## Description
Currently, CLAUDE.md (~1900 lines) contains both project-specific orchestration instructions AND framework-wide SDLC content (folder structure, ID assignment, artifact paths, dependency flow, markers). This creates duplication across projects and manual synchronization overhead.

This story refactors CLAUDE.md into two components:
1. **Local Orchestrator (CLAUDE.md):** ~200 lines containing project-specific metadata (product name, package name), references to MCP resources, and implementation phase delegation to language-specific patterns
2. **SDLC Resource (sdlc-core.md):** ~1700 lines containing all framework-wide SDLC content, served as `mcp://resources/sdlc/core` via MCP Server

After this refactor, the local CLAUDE.md acts as a lightweight "pointer" to centralized MCP resources, enabling single-source-of-truth maintenance.

## Implementation Research References

**Primary Research Document:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

**Technical Patterns Applied:**
- **§3.1: Microservices with Sidecar Pattern:** MCP Server serves resources via FastAPI, enabling centralized framework content distribution (ref: Implementation Research §3.1 - Overall Architecture Pattern)
- **§2.2: FastAPI Backend Framework:** Resource serving implemented with FastAPI's static file serving or custom resource endpoint (ref: Implementation Research §2.2 - Backend Framework: FastAPI 0.100+)
- **§2.4: Caching Layer (Redis):** Resource caching with TTL to reduce disk I/O latency (deferred to US-032)

**Anti-Patterns Avoided:**
- **§8.2: Synchronous Blocking Calls in Async Context:** If resource endpoint implemented, use async file I/O (aiofiles) to avoid blocking event loop (ref: Implementation Research §8.2 - Anti-Pattern 1)

## Functional Requirements
1. Split CLAUDE.md into local orchestrator and SDLC resource file
2. Local CLAUDE.md retains project-specific metadata (product name, package name, general section)
3. Local CLAUDE.md references MCP resource for SDLC content (folder structure, ID assignment, etc.)
4. SDLC resource (sdlc-core.md) created at `prompts/CLAUDE/sdlc-core.md` containing all framework-wide sections
5. SDLC resource includes all sections: Folder Structure, Artifact Path Resolution, Dependency Flow, Input Classification, Markers, ID Assignment, Version History
6. Local CLAUDE.md reduced to <200 lines (target: ~150 lines)
7. No functionality loss - all information remains accessible

## Non-Functional Requirements
- **Readability:** Local CLAUDE.md must be clear and concise, with obvious references to MCP resources
- **Maintainability:** Clear separation of concerns between project-specific and framework-wide content
- **Traceability:** Version history preserved in both files documenting the split
- **Backward Compatibility:** Maintain same information architecture (deferred orchestration update to US-056)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story refactors CLAUDE.md itself, establishing the pattern for MCP resource references. Supplement with story-specific technical guidance.

### Implementation Guidance
This is a manual refactoring task (not code implementation). Approach:

1. **Analyze Current CLAUDE.md Structure:**
   - Identify project-specific sections (General, Implementation Phase Instructions)
   - Identify framework-wide sections (Folder Structure through Version History)
   - Map line ranges to new file locations

2. **Create SDLC Resource File:**
   - Create `/prompts/CLAUDE/sdlc-core.md` as new file
   - Extract framework-wide sections from CLAUDE.md (preserve exact content)
   - Add document header with metadata (name, version, last updated, purpose)
   - Add reference back to orchestrator CLAUDE.md for context

3. **Refactor Local CLAUDE.md:**
   - Retain General section (lines 1-7: product name, package name)
   - Replace framework sections with MCP resource reference: `See: mcp://resources/sdlc/core (provided by MCP Server)`
   - Retain Implementation Phase Instructions section with reference to language-specific patterns
   - Add version note documenting the split

4. **Validate Content Preservation:**
   - Confirm all original content exists in either local or resource file
   - Verify line count: local <200 lines, resource ~1700 lines
   - Check that all section cross-references remain valid

5. **Update Documentation:**
   - Add version history entry to both files
   - Document new file structure in README (if applicable)

### Technical Tasks
- [ ] Create `/prompts/CLAUDE/sdlc-core.md` file
- [ ] Extract framework-wide sections from CLAUDE.md to sdlc-core.md
- [ ] Refactor local CLAUDE.md to reference MCP resource
- [ ] Validate content preservation (no information loss)
- [ ] Update version history in both files

## Acceptance Criteria

### Scenario 1: Local CLAUDE.md reduced to orchestrator role
**Given** CLAUDE.md has been refactored
**When** I read `/CLAUDE.md`
**Then** the file is <200 lines
**And** it contains General section with product name and package name
**And** it references `mcp://resources/sdlc/core` for SDLC framework content
**And** it contains Implementation Phase Instructions section

### Scenario 2: SDLC resource file created with framework content
**Given** CLAUDE.md refactoring is complete
**When** I read `/prompts/CLAUDE/sdlc-core.md`
**Then** the file contains all framework-wide SDLC sections
**And** it includes: Folder Structure, Artifact Path Resolution, Dependency Flow, Input Classification, Markers, ID Assignment
**And** total line count is ~1700 lines
**And** file includes metadata header (name, version, purpose)

### Scenario 3: No information loss
**Given** original CLAUDE.md content documented
**When** I compare original CLAUDE.md to (new CLAUDE.md + sdlc-core.md)
**Then** all original sections exist in one of the two files
**And** all original content preserved (no deletions except for refactoring structure)
**And** section cross-references remain valid

### Scenario 4: Clear MCP resource reference
**Given** local CLAUDE.md references MCP resource
**When** Claude Code reads CLAUDE.md and encounters `mcp://resources/sdlc/core`
**Then** reference format is clear and unambiguous
**And** includes note: "(provided by MCP Server)" for human readers

### Scenario 5: Version history updated
**Given** refactoring complete
**When** I read version history in both files
**Then** local CLAUDE.md version history documents the split with date
**And** sdlc-core.md version history documents file creation from CLAUDE.md split
**And** both files reference v1.10 or later as split version

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 3 SP (below 5 SP threshold - CONSIDER territory)
- **Developer Count:** Single developer (solo work)
- **Domain Span:** Single domain (documentation refactoring only, no code)
- **Complexity:** Low - straightforward file split and content reorganization
- **Uncertainty:** Low - clear refactoring instructions, no technical unknowns
- **Override Factors:** None - simple documentation refactoring, not cross-domain, not security-critical, no system integration

Per SDLC Section 11.6 Decision Matrix: "1-2 SP, single dev, single domain → SKIP (Overhead not justified)". This 3 SP story with single developer and straightforward documentation refactoring falls into "overhead not justified" category.

## Definition of Done
- [ ] `/prompts/CLAUDE/sdlc-core.md` file created with all framework-wide sections
- [ ] Local `/CLAUDE.md` refactored to <200 lines with MCP resource references
- [ ] Content validation complete (no information loss)
- [ ] Version history updated in both files
- [ ] Manual testing: Verify Claude Code can still read both files without errors
- [ ] Product Owner approval obtained

## Additional Information
**Suggested Labels:** documentation, refactoring, mcp-resources, foundational
**Estimated Story Points:** 3
**Dependencies:**
- **Blocks:** US-029 (file renaming depends on this refactor completing)
- **Blocks:** US-030 (MCP resource server implementation depends on sdlc-core.md file existing)

**Related PRD Section:** PRD-006 §Functional Requirements - FR-04

## Open Questions & Implementation Uncertainties

No open implementation questions. All technical approaches clear from HLS-006 decomposition plan and Implementation Research.

**Refactoring strategy is straightforward:** Manual file split with content preservation validation. No technical decisions required.

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-006_mcp_resources_migration_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`
