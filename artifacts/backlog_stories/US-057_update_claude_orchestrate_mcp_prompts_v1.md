# User Story: Update CLAUDE.md to Orchestrate MCP Prompts

## Metadata
- **Story ID:** US-057
- **Title:** Update CLAUDE.md to Orchestrate MCP Prompts
- **Type:** Feature
- **Status:** Backlog
- **Priority:** High - Enables MCP-native generator execution and token-efficient prompt loading
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-010
- **Functional Requirements Covered:** FR-05, FR-12
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Requirements - FR-05, FR-12; §Timeline & Milestones - Phase 2 (Week 3)
- **Functional Requirements Coverage:**
  - **FR-05:** MCP Server SHALL expose all artifact generators (prompts/*-generator.xml) as MCP prompts using URL pattern `mcp://prompts/generator/{artifact_name}`
  - **FR-12:** Main CLAUDE.md SHALL be refactored to orchestrate MCP Server integration, directing Claude Code to use MCP resources/prompts/tools instead of local file access

**Parent High-Level Story:** [HLS-010: CLAUDE.md Orchestration Update & Integration Testing]
- **Link:** `/artifacts/hls/HLS-010_claude_orchestration_integration_testing_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 2

## User Story
As a Framework Maintainer, I want CLAUDE.md /generate command instructions updated to call MCP prompts instead of reading local generator XML files, so that Claude Code executes generators via MCP protocol with centralized prompt management.

## Description

The current /generate command workflow (defined in `.claude/commands/generate.md` and orchestrated by CLAUDE.md) reads generator XML files from local `prompts/*-generator.xml` paths. This approach requires every project to maintain local copies of all 10 generator files (epic-generator.xml, prd-generator.xml, etc.), creating synchronization overhead when generators are updated.

This story updates CLAUDE.md orchestration instructions to direct Claude Code to call MCP prompts using the URL pattern `mcp://prompts/generator/{artifact_name}` (e.g., `mcp://prompts/generator/epic` for epic-generator.xml). The local `/generate` command in `.claude/commands/generate.md` remains as the orchestration layer, but CLAUDE.md instructions change to reference MCP prompts instead of local file paths.

**Key Changes:**
1. Update CLAUDE.md §Generate Command Instructions to reference MCP prompt URLs
2. Document MCP prompt URL pattern: `mcp://prompts/generator/{artifact_name}`
3. Update generator execution workflow to call MCP prompts
4. Maintain functional equivalence (same generator outputs, different loading mechanism)

**Scope:**
- In Scope: CLAUDE.md orchestration instructions only
- Out of Scope: Changes to `.claude/commands/generate.md` local command file (remains unchanged)
- Out of Scope: MCP Server prompt implementation (covered by US-035 - Expose Generators as MCP Prompts)

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§4.3: MCP Prompts Pattern:** Generators exposed as MCP prompts, callable via URL scheme `mcp://prompts/generator/{artifact_name}`
  - **Example:** `mcp://prompts/generator/epic` → epic-generator.xml content
- **§4.1: Resource Caching:** MCP Server caches generator XML content with 5-minute TTL (FR-20)
  - **Performance Target:** First request 50ms (disk I/O), subsequent requests <10ms (cache hit)
- **§5.2: Orchestration Patterns:** CLAUDE.md directs Claude Code to call MCP prompts; local `/generate` command orchestrates workflow but delegates prompt loading to MCP Server

**Anti-Patterns Avoided:**
- **§6.2: Hardcoded File Paths:** Avoid hardcoded local generator file paths in orchestration logic (prevents centralized framework updates)

**Performance Considerations:**
- **§8.1: Token Optimization:** MCP prompt loading only fetches generator content when needed (not entire prompts/ directory), reducing token consumption for generator execution
- **§8.2: Resource Caching:** Generator XML caching reduces latency for repeated generator calls (e.g., generating multiple backlog stories from same HLS uses cached prompt)

## Functional Requirements
- Update CLAUDE.md §Generate Command Instructions to reference MCP prompt URL pattern
- Document MCP prompt URL pattern: `mcp://prompts/generator/{artifact_name}` with mapping examples
- Update generator execution workflow to call MCP prompts instead of reading local files
- Maintain functional equivalence (validation test suite passes pre/post changes)
- Document all 10 generator types with MCP prompt URLs (product-vision, initiative, epic, prd, hls, backlog-story, spike, adr, tech-spec, implementation-task)

## Non-Functional Requirements
- **Performance:** Generator prompt loading latency <100ms (p95) per NFR-Performance-01
- **Maintainability:** Clear documentation of MCP prompt URL mapping for all generator types
- **Compatibility:** Functional equivalence validated via test suite (same generator outputs pre/post changes)
- **Backward Compatibility:** Graceful degradation to local files when MCP Server unavailable (implementation in US-059)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story updates CLAUDE.md orchestration instructions only, not implementation code.

### Implementation Guidance

**Step 1: Update CLAUDE.md §Generate Command Instructions**

Replace current generator execution instructions with MCP prompt references:

**Before (Local File Approach):**
```markdown
### Step 3: Execute Generator
1. Read generator XML content from `prompts/{generator_name}-generator.xml`
2. Substitute placeholders:
   - `{UPSTREAM_ARTIFACT}` → content from input file
   - `{TEMPLATE}` → content from template file
3. Run generator
```

**After (MCP Prompt Approach):**
```markdown
### Step 3: Execute Generator
1. Call MCP prompt using URL pattern: `mcp://prompts/generator/{artifact_name}`
   - Example: For epic generation, call `mcp://prompts/generator/epic`
   - MCP Server returns epic-generator.xml content with placeholders substituted
2. Generator content loaded from MCP Server (cached, <100ms p95 latency)
3. Run generator with substituted content
```

**Step 2: Document MCP Prompt URL Pattern**

Add mapping table to CLAUDE.md §Generate Command Instructions:

```markdown
## MCP Prompt URL Mapping

| Generator Type | Artifact Name | MCP Prompt URL |
|----------------|---------------|----------------|
| Product Vision | product-vision | mcp://prompts/generator/product-vision |
| Initiative | initiative | mcp://prompts/generator/initiative |
| Epic | epic | mcp://prompts/generator/epic |
| PRD | prd | mcp://prompts/generator/prd |
| High-Level Story | hls | mcp://prompts/generator/hls |
| Backlog Story | backlog-story | mcp://prompts/generator/backlog-story |
| Spike | spike | mcp://prompts/generator/spike |
| ADR | adr | mcp://prompts/generator/adr |
| Tech Spec | tech-spec | mcp://prompts/generator/tech-spec |
| Implementation Task | implementation-task | mcp://prompts/generator/implementation-task |

**Pattern:** `mcp://prompts/generator/{artifact_name}` where `{artifact_name}` is derived from generator filename (`{artifact_name}-generator.xml`)
```

**Step 3: Update Generator Execution Workflow**

Modify CLAUDE.md instructions for generator execution:
- Replace local file path references (`prompts/{generator_name}-generator.xml`) with MCP prompt URLs
- Add note: "MCP Server handles placeholder substitution and returns ready-to-execute prompt content"
- Add fallback reference: "See US-059 for backward compatibility mode (local file approach when MCP Server unavailable)"

**Step 4: Validation**

- Compare CLAUDE.md generator execution instructions pre/post changes
- Verify all 10 generator types documented in MCP prompt URL mapping table
- Test MCP prompt execution (requires US-035 completion for MCP Server prompt endpoints)
- Run validation test suite (if available) to confirm functional equivalence

**References to Implementation Standards:**
- patterns-core.md: Core development philosophy applies to orchestration instruction updates
- patterns-architecture.md: Follow established documentation patterns for CLAUDE.md updates

### Technical Tasks
- [ ] Update CLAUDE.md §Generate Command Instructions with MCP prompt references
- [ ] Add MCP prompt URL mapping table to CLAUDE.md
- [ ] Replace local file path references with `mcp://prompts/generator/{artifact_name}` pattern
- [ ] Document all 10 generator types with MCP prompt URLs
- [ ] Update generator execution workflow instructions
- [ ] Add backward compatibility note (reference US-059)
- [ ] Validate functional equivalence (comparison test)
- [ ] Update `.claude/commands/generate.md` documentation to reference MCP prompt approach (documentation only, no logic changes)

## Acceptance Criteria

### Scenario 1: MCP Prompt URL Pattern Documented
**Given** CLAUDE.md §Generate Command Instructions updated
**When** Framework Maintainer reviews orchestration instructions
**Then** MCP prompt URL pattern is documented: `mcp://prompts/generator/{artifact_name}` with mapping table for all 10 generator types

### Scenario 2: Generator Execution Workflow Updated
**Given** CLAUDE.md generator execution workflow section
**When** refactoring is complete
**Then** workflow references MCP prompt URLs (e.g., `mcp://prompts/generator/epic`) instead of local file paths (`prompts/epic-generator.xml`)

### Scenario 3: All Generator Types Mapped
**Given** MCP prompt URL mapping table added to CLAUDE.md
**When** mapping table reviewed
**Then** all 10 generator types documented with MCP prompt URLs (product-vision, initiative, epic, prd, hls, backlog-story, spike, adr, tech-spec, implementation-task)

### Scenario 4: Functional Equivalence Validated
**Given** CLAUDE.md updated with MCP prompt references
**When** validation test suite executes
**Then** all tests pass (same generator outputs as pre-refactoring baseline)

### Scenario 5: Backward Compatibility Noted
**Given** CLAUDE.md orchestration instructions
**When** MCP Server unavailable scenario documented
**Then** backward compatibility note added with reference to US-059 (fallback to local files)

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 3 SP (CONSIDER threshold, below DON'T SKIP at 8+ SP)
- **Developer Count:** Single developer (documentation updates only)
- **Domain Span:** Single domain (documentation/orchestration instructions only, no code changes)
- **Complexity:** Low - Well-defined updates to CLAUDE.md instructions and URL mapping table
- **Uncertainty:** Low - Clear pattern defined in PRD-006 v3 FR-05
- **Override Factors:** None - No cross-domain dependencies, no security-critical changes, no unfamiliar technology

**Conclusion:** Documentation-only story with straightforward pattern updates does not warrant task decomposition. Implementation can proceed as a single cohesive unit of work within one sprint.

## Definition of Done
- [ ] CLAUDE.md §Generate Command Instructions updated with MCP prompt URL references
- [ ] MCP prompt URL mapping table added to CLAUDE.md with all 10 generator types
- [ ] Local file path references replaced with `mcp://prompts/generator/{artifact_name}` pattern
- [ ] Generator execution workflow instructions updated
- [ ] Backward compatibility note added (reference US-059)
- [ ] Functional equivalence validated (comparison test passes)
- [ ] Code reviewed and approved
- [ ] Documentation updated (CHANGELOG or migration notes)
- [ ] Product Owner acceptance obtained

## Additional Information
**Suggested Labels:** refactoring, infrastructure, mcp-prompts, documentation
**Estimated Story Points:** 3
**Dependencies:**
- **Depends On:** US-056 (Update CLAUDE.md to Orchestrate MCP Resources) - establishes orchestrator structure
- **Blocks:** US-060 (Integration Testing) - requires MCP prompt orchestration for end-to-end testing
- **Related:** US-035 (Expose Generators as MCP Prompts) - implements MCP Server prompt endpoints
- **Related:** US-036 (Update /generate Command to Call MCP Prompts) - implements command logic changes

## Decisions Made

**All technical approaches clear from PRD-006 v3 §Requirements (FR-05, FR-12).**

**Key Decisions Already Made:**
- MCP prompt URL pattern: `mcp://prompts/generator/{artifact_name}` per FR-05
- Artifact name derivation: Remove `-generator.xml` suffix from filename (e.g., `epic-generator.xml` → `epic`)
- Backward compatibility approach: Fall back to local files when MCP Server unavailable (US-059)
- Local `/generate` command remains unchanged (orchestration only, no logic changes)

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-010_claude_orchestration_integration_testing_v2.md`
- **Parent Epic:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`
- **Related Stories:** US-035 (Expose Generators as MCP Prompts), US-036 (Update /generate Command to Call MCP Prompts), US-056 (Update CLAUDE.md to Orchestrate MCP Resources)

## Version History
- **v1 (2025-10-18):** Initial version
