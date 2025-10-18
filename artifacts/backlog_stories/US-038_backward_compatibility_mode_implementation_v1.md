# User Story: Backward Compatibility Mode Implementation

## Metadata
- **Story ID:** US-038
- **Title:** Backward Compatibility Mode Implementation
- **Type:** Feature
- **Status:** Backlog
- **Priority:** High - enables incremental adoption without breaking existing projects
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-007 (MCP Prompts - Generators Migration)
- **Functional Requirements Covered:** FR-13, NFR-Compatibility-01
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration v3]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Requirements - FR-13, NFR-Compatibility-01
- **Functional Requirements Coverage:**
  - **FR-13:** MCP Server SHALL maintain backward compatibility mode allowing projects to opt-in to MCP framework incrementally (coexist with local file approach during transition)
  - **NFR-Compatibility-01:** MCP Server SHALL maintain backward compatibility with local file approach during transition period (3 months minimum) allowing projects to opt-in incrementally

**Parent High-Level Story:** [HLS-007: MCP Prompts - Generators Migration]
- **Link:** `/artifacts/hls/HLS-007_mcp_prompts_generators_migration_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 4

## User Story
As a Project Maintainer, I want a backward compatibility mode that allows my project to use local generator files while other projects migrate to MCP prompts, so that I can adopt MCP framework at my own pace without forced migration.

## Description
The MCP prompt migration must not force all projects to migrate simultaneously. This story implements a configuration-driven backward compatibility mode where projects can opt-in to MCP prompts via config flag (`use_mcp_prompts: true/false`). When disabled, `/generate` command falls back to local file reading, allowing coexistence during 3-month transition period.

**Current State:** Migration plan assumes all projects switch to MCP prompts simultaneously (risky, disruptive).

**Desired State:** Projects configure opt-in flag in `.mcp/config.json`. MCP-enabled projects use prompts; legacy projects use local files. Both approaches work simultaneously without interference.

**Business Value:** De-risks migration by allowing gradual rollout (pilot → early adopters → full adoption), reduces support burden (no "big bang" migration), respects team autonomy (migrate when ready).

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§4.2: Environment Variables and Secrets Management:** Store feature flags in .env configuration (ref: Implementation Research §4.2 lines 635-678)
- **§6.2: Prometheus Metrics:** Track adoption metrics (% of requests using MCP vs. local files)

**Anti-Patterns Avoided:**
- **§8.2 Anti-Pattern 4: Proliferation Without Lifecycle Plan:** Clearly define deprecation timeline (3 months), communicate sunsetting plan for local file approach

**Performance Considerations:**
- Minimal performance impact (single boolean check per generator execution)
- No dual code paths that complicate maintenance (fallback already exists for error handling per US-036)

## Functional Requirements
- Add configuration flag `use_mcp_prompts` to project config (`.mcp/config.json`)
- `/generate` command checks config flag before deciding MCP vs. local file approach
- Default value: `false` (backward compatible - use local files unless explicitly opted in)
- Configuration documented in migration guide with opt-in instructions
- MCP Server logs track adoption metrics (count of MCP vs. local file generator executions)
- Validation test suite passes in both modes (MCP and local file)

## Non-Functional Requirements
- **Backward Compatibility:** Projects without `.mcp/config.json` default to local file approach (zero breaking changes)
- **Performance:** Config flag check adds <1ms overhead per generator execution
- **Usability:** Clear migration guide with step-by-step opt-in instructions
- **Observability:** Adoption metrics tracked (% of generator executions using MCP prompts)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story implements configuration-driven feature flagging. Reference config management patterns.

### Implementation Guidance

**Configuration Schema (.mcp/config.json):**
```json
{
  "server_url": "http://localhost:3000",
  "use_mcp_prompts": false,
  "use_mcp_resources": false,
  "use_mcp_tools": false,
  "timeout_ms": 5000,
  "retry_attempts": 3
}
```

**Feature Flag Check in /generate Command:**
```python
# .claude/commands/generate.md (pseudocode)
config = load_config(".mcp/config.json")

if config.get("use_mcp_prompts", False):
    # New path: Call MCP prompt
    generator_content = call_mcp_prompt(f"mcp://prompts/generator/{generator_name}")
else:
    # Legacy path: Read local file
    generator_content = read_local_file(f"prompts/{generator_name}-generator.xml")

# Execute generator (same logic for both paths)
execute_generator(generator_content, inputs)
```

**Default Behavior (no config file):**
```python
def load_config(config_path):
    """Loads config with backward-compatible defaults"""
    if not os.path.exists(config_path):
        # No config file → default to local file approach
        return {"use_mcp_prompts": False}

    with open(config_path) as f:
        return json.load(f)
```

**Adoption Metrics Logging:**
```python
# Log generator execution with mode
logger.info(
    "Generator executed",
    extra={
        "generator": generator_name,
        "mode": "mcp_prompt" if use_mcp_prompts else "local_file",
        "duration_ms": execution_duration,
        "project_id": project_id
    }
)
```

**References to Implementation Standards:**
- **CLAUDE-tooling.md (Python):** Configuration management patterns (environment variables, .env files)
- **CLAUDE-testing.md (Python):** Test both modes (MCP and local file) in CI/CD
- **CLAUDE-architecture.md (Python):** Config loading module design (`src/mcp_server/config.py`)

**Note:** Treat CLAUDE.md content as authoritative - supplement with story-specific context, don't duplicate.

### Technical Tasks
- **Config Schema:** Define `.mcp/config.json` schema with `use_mcp_prompts` flag
- **Config Loading:** Implement config loader with backward-compatible defaults (no file → local mode)
- **Command Update:** Update `/generate` command to check config flag before choosing execution path
- **Logging:** Add adoption metrics logging (mode field: "mcp_prompt" or "local_file")
- **Testing:** Test suite validates both modes (MCP and local file execution)
- **Documentation:** Migration guide with opt-in instructions and .mcp/config.json example
- **Validation:** Regression test suite passes in both modes (NFR-Compatibility-01)

## Acceptance Criteria

**Format Guidance:** Gherkin format (Given-When-Then) for scenario-based validation.

### Scenario 1: Default behavior is local file (backward compatible)
**Given** project does not have `.mcp/config.json` file
**When** developer runs `/generate epic-generator` command
**Then** command uses local file approach (reads `prompts/epic-generator.xml`)
**And** command executes successfully with local file content
**And** no errors or warnings about missing MCP Server

### Scenario 2: Opt-in to MCP prompts via config
**Given** project has `.mcp/config.json` with `"use_mcp_prompts": true`
**When** developer runs `/generate epic-generator` command
**Then** command uses MCP prompt approach (calls `mcp://prompts/generator/epic`)
**And** command executes successfully with MCP prompt content
**And** generated artifact identical to local file approach (per NFR-Compatibility-02)

### Scenario 3: Explicit opt-out to local files
**Given** project has `.mcp/config.json` with `"use_mcp_prompts": false`
**When** developer runs `/generate prd-generator` command
**Then** command uses local file approach (reads `prompts/prd-generator.xml`)
**And** command logs mode: "local_file" for adoption metrics

### Scenario 4: Config validation handles invalid values
**Given** project has `.mcp/config.json` with `"use_mcp_prompts": "yes"` (invalid type - string instead of boolean)
**When** developer runs `/generate hls-generator` command
**Then** config loader validates type and logs warning: "Invalid use_mcp_prompts value, defaulting to false"
**And** command uses local file approach (safe fallback)

### Scenario 5: Both modes tested in CI/CD
**Given** test suite includes tests for MCP and local file modes
**When** CI/CD pipeline runs on pull request
**Then** tests execute generators in both modes (use_mcp_prompts: true and false)
**And** all tests pass in both modes (100% pass rate)
**And** byte-identical artifacts validated (NFR-Compatibility-02)

### Scenario 6: Adoption metrics tracked
**Given** 3 projects configured: 2 use MCP prompts, 1 uses local files
**When** all 3 projects execute generators over 1 week
**Then** adoption metrics show: 67% MCP prompts, 33% local files
**And** metrics queryable via log aggregation (e.g., "mode=mcp_prompt" filter)

### Scenario 7: Migration guide available
**Given** developer wants to opt-in to MCP prompts
**When** developer reads migration guide in documentation
**Then** guide provides step-by-step instructions:
  1. Create `.mcp/config.json` file
  2. Set `"use_mcp_prompts": true`
  3. Ensure MCP Server running and accessible
  4. Test generator execution with `/generate epic-generator`
  5. Validate generated artifacts match local file approach
**And** guide includes troubleshooting section (MCP Server unreachable, config syntax errors)

### Scenario 8: Deprecation timeline communicated
**Given** backward compatibility mode is 3-month transition period
**When** developer checks migration guide or release notes
**Then** documentation clearly states:
  - Transition period: 3 months from MCP prompts release (e.g., 2025-10-18 to 2026-01-18)
  - After transition: Local file approach deprecated, use_mcp_prompts=true becomes mandatory
  - Sunsetting plan: Warning logs added 1 month before deprecation, hard failure after deprecation
**And** timeline allows reasonable migration window for all projects

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 3 SP (DON'T SPLIT per SDLC Section 11.6 - <3 SP rarely benefits from decomposition)
- **Developer Count:** Single developer (config management + command update)
- **Domain Span:** Single domain (client-side command layer + config loading)
- **Complexity:** Low - simple boolean flag check, config loading with defaults
- **Uncertainty:** Low - standard feature flag pattern
- **Override Factors:** None (not cross-domain, not security-critical, straightforward implementation)

Per SDLC Section 11.6 Decision Matrix: "<3 SP → DON'T SPLIT". Implementation is simple config flag with fallback logic (already exists per US-036). Decomposition overhead not justified.

## Definition of Done
- [ ] Code implemented and reviewed
- [ ] `.mcp/config.json` schema defined with `use_mcp_prompts` flag
- [ ] Config loader implemented with backward-compatible defaults
- [ ] `/generate` command updated to check config flag
- [ ] Adoption metrics logging implemented
- [ ] Test suite validates both modes (MCP and local file)
- [ ] Regression tests pass in both modes (NFR-Compatibility-01)
- [ ] Migration guide written with opt-in instructions
- [ ] Deprecation timeline documented (3-month transition period)
- [ ] Acceptance criteria validated (all 8 scenarios passing)
- [ ] Product owner approval obtained

## Additional Information
**Suggested Labels:** backward-compatibility, config-management, migration, technical-debt
**Estimated Story Points:** 3
**Dependencies:**
- **Story Dependencies:**
  - US-035 (Expose Generators as MCP Prompts) - must complete first
  - US-036 (Update /generate Command to Call MCP Prompts) - must complete first (provides fallback logic)
- **Technical Dependencies:**
  - `.mcp/config.json` configuration file (new file, created by this story)
  - MCP Server running with generators exposed (US-035 deliverable)
- **Team Dependencies:** None

**Related PRD Section:** PRD-006 §Requirements - FR-13, NFR-Compatibility-01; §Risks & Mitigations - "Backward Compatibility Breaks Existing Projects"

## Decisions Made

**All technical approaches resolved.**

**D1: Default Behavior**
- **Decision:** Default to local file approach (`use_mcp_prompts: false`) when config file missing
- **Rationale:** Backward compatible - existing projects without config file continue working without changes
- **Impact:** Zero breaking changes, projects opt-in when ready

**D2: Configuration Location**
- **Decision:** Store feature flags in `.mcp/config.json` (project root)
- **Rationale:** Aligns with MCP-specific settings (server URL, timeout, etc.), clear separation from application config
- **Alternative Considered:** `.env` file - rejected because feature flags are project-level decisions (not environment-specific like credentials)

**D3: Transition Period Duration**
- **Decision:** 3-month transition period before deprecating local file approach
- **Rationale:** Per PRD-006 NFR-Compatibility-01 requirement, provides reasonable time for 5+ projects to migrate at their own pace
- **Validation:** Survey projects at 6-week mark, extend if <80% adoption

**D4: Adoption Metrics Tracking**
- **Decision:** Log generator executions with mode field ("mcp_prompt" or "local_file")
- **Rationale:** Enables data-driven decision making (when to deprecate local file approach based on actual adoption)
- **Observability:** Queryable via log aggregation (Grafana, CloudWatch, etc.)

**D5: Validation Strategy**
- **Decision:** CI/CD runs test suite in both modes (use_mcp_prompts: true and false)
- **Rationale:** Ensures functional equivalence, prevents regressions in either mode during transition period
- **Implementation:** Parameterized tests with mode fixture (pytest)
