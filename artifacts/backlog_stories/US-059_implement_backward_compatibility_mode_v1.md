# User Story: Implement Backward Compatibility Mode

## Metadata
- **Story ID:** US-059
- **Title:** Implement Backward Compatibility Mode
- **Type:** Feature
- **Status:** Backlog
- **Priority:** High - Critical for zero-disruption migration, prevents breaking existing projects during MCP framework rollout
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-010
- **Functional Requirements Covered:** FR-13
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Requirements - FR-13; §Non-Functional Requirements - NFR-Compatibility-01, NFR-Compatibility-02, NFR-Compatibility-03; §Timeline & Milestones - Phase 5 (Week 7)
- **Functional Requirements Coverage:**
  - **FR-13:** MCP Server SHALL maintain backward compatibility mode allowing projects to opt-in to MCP framework incrementally (coexist with local file approach during transition)

**Parent High-Level Story:** [HLS-010: CLAUDE.md Orchestration Update & Integration Testing]
- **Link:** `/artifacts/hls/HLS-010_claude_orchestration_integration_testing_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 4

## User Story
As a Framework Maintainer, I want projects to detect `use_mcp_framework` configuration flag and gracefully fall back to local file approach when false or MCP Server unavailable, so that existing projects continue functioning without disruption during MCP migration.

## Description

The MCP framework migration introduces a risk of breaking existing projects that rely on local file access for CLAUDE.md, generators, templates, and artifacts. To enable zero-disruption migration, projects must support two modes:

1. **MCP Mode (`use_mcp_framework: true`):**
   - Load SDLC instructions from `mcp://resources/sdlc/core`
   - Load implementation patterns from `mcp://resources/patterns/{language}/*`
   - Load templates from `mcp://resources/templates/*`
   - Call generators via `mcp://prompts/generator/{artifact_name}`
   - Call tools via MCP protocol (validate_artifact, resolve_artifact_path, etc.)

2. **Local File Mode (`use_mcp_framework: false` or MCP Server unavailable):**
   - Load SDLC instructions from local `CLAUDE.md` file (pre-refactoring content)
   - Load implementation patterns from local `prompts/CLAUDE/{language}/*.md` files
   - Load templates from local `prompts/templates/*.xml` files
   - Read generators from local `prompts/*-generator.xml` files
   - Use AI inference for validation and path resolution (fallback behavior)

This story implements backward compatibility detection and graceful degradation logic in CLAUDE.md orchestration instructions. When `use_mcp_framework: false` or MCP Server unreachable, Claude Code automatically falls back to local file approach with warning message (no hard failure).

**Scope:**
- In Scope: Configuration detection logic, fallback instructions, graceful degradation workflow
- In Scope: Warning messages for fallback scenarios
- Out of Scope: MCP Server health check implementation (assumed available via MCP protocol)
- Out of Scope: Regression testing validation (covered by US-062)

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§5.5: Configuration Management:** Detect `use_mcp_framework` flag from `.mcp/config.json` or environment variable
  - **Default Behavior:** If config file not found or flag not set, default to `false` (local file approach, safe fallback)
- **§5.6: Graceful Degradation:** When MCP Server unavailable (connection timeout, HTTP 503), fall back to local files with warning
  - **Error Detection:** MCP resource request timeout (>5 seconds) or explicit error response
- **§8.5: Resilience Patterns:** Retry logic for transient MCP Server failures (3 retries with exponential backoff: 100ms, 200ms, 400ms) per NFR-Reliability-01

**Anti-Patterns Avoided:**
- **§6.6: Hard Failures on Infrastructure Unavailability:** Avoid blocking workflow execution when MCP Server unavailable (graceful degradation prevents hard failures)
- **§6.7: Silent Fallbacks:** Avoid silent fallback behavior without user notification (transparency required for debugging)

**Performance Considerations:**
- **§8.6: Fallback Latency:** Local file approach should have similar latency to MCP approach (both <100ms for file loading)
- **§8.7: Retry Overhead:** Retry logic adds maximum 700ms latency (100+200+400) for transient failures before fallback

## Functional Requirements
- Detect `use_mcp_framework` configuration flag from `.mcp/config.json` or environment variable
- When `use_mcp_framework: false`, use local file approach (read CLAUDE.md, prompts/*, templates/*)
- When `use_mcp_framework: true` but MCP Server unavailable, fall back to local files with warning
- Display warning message when fallback occurs: "⚠️ MCP Server unavailable, using local files"
- Implement retry logic for transient MCP Server failures (3 retries, exponential backoff)
- Maintain functional equivalence (same artifact outputs in both modes) per NFR-Compatibility-02
- Document configuration file schema (`.mcp/config.json`)

## Non-Functional Requirements
- **Compatibility:** Functional equivalence validated via test suite (same outputs in MCP and local modes) per NFR-Compatibility-02
- **Reliability:** Retry logic for transient failures (3 retries, exponential backoff) per NFR-Reliability-01
- **Usability:** Clear warning messages when fallback occurs (no silent failures)
- **Maintainability:** Backward compatibility maintained for ≥3 months during transition period per NFR-Compatibility-01
- **Documentation:** Configuration schema and fallback behavior documented in CLAUDE.md

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story implements backward compatibility logic in CLAUDE.md orchestration instructions.

### Implementation Guidance

**Step 1: Define Configuration File Schema**

Create `.mcp/config.json` schema for project-level configuration:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "use_mcp_framework": {
      "type": "boolean",
      "description": "Enable MCP framework for resources, prompts, and tools. Default: false (local file approach).",
      "default": false
    },
    "mcp_server_url": {
      "type": "string",
      "description": "MCP Server URL (e.g., http://localhost:3000). Required when use_mcp_framework: true.",
      "format": "uri"
    },
    "retry_policy": {
      "type": "object",
      "properties": {
        "max_retries": {
          "type": "integer",
          "description": "Maximum retry attempts for transient MCP Server failures. Default: 3.",
          "default": 3
        },
        "initial_backoff_ms": {
          "type": "integer",
          "description": "Initial backoff duration in milliseconds. Default: 100ms.",
          "default": 100
        }
      }
    }
  },
  "required": ["use_mcp_framework"]
}
```

**Example Configuration File:**

```json
{
  "use_mcp_framework": true,
  "mcp_server_url": "http://localhost:3000",
  "retry_policy": {
    "max_retries": 3,
    "initial_backoff_ms": 100
  }
}
```

**Step 2: Add Configuration Detection Logic to CLAUDE.md**

Add new section to CLAUDE.md:

```markdown
## Configuration Detection (Backward Compatibility Mode)

**Purpose:** Support incremental MCP migration by allowing projects to opt-in via configuration flag.

### Configuration Loading

1. Check for `.mcp/config.json` file in project root
2. If file exists, parse JSON and read `use_mcp_framework` flag
3. If file not found or flag not set, default to `false` (local file approach)
4. If environment variable `USE_MCP_FRAMEWORK` set, override config file value

**Configuration Priority:**
1. Environment variable `USE_MCP_FRAMEWORK` (highest priority)
2. `.mcp/config.json` file `use_mcp_framework` field
3. Default: `false` (local file approach, safe fallback)

### Mode Selection

**MCP Mode (`use_mcp_framework: true`):**
- Load SDLC instructions from `mcp://resources/sdlc/core`
- Load implementation patterns from `mcp://resources/patterns/{language}/*`
- Load templates from `mcp://resources/templates/*`
- Call generators via `mcp://prompts/generator/{artifact_name}`
- Call tools via MCP protocol (validate_artifact, resolve_artifact_path, etc.)

**Local File Mode (`use_mcp_framework: false` or MCP Server unavailable):**
- Load SDLC instructions from local `CLAUDE.md` file (embedded content or separate file)
- Load implementation patterns from local `prompts/CLAUDE/{language}/*.md` or `prompts/CLAUDE/{language}/patterns-*.md`
- Load templates from local `prompts/templates/*.xml`
- Read generators from local `prompts/*-generator.xml`
- Use AI inference for validation and path resolution (fallback behavior)
```

**Step 3: Add Graceful Degradation Logic to CLAUDE.md**

Add graceful degradation workflow:

```markdown
### Graceful Degradation (MCP Server Unavailable)

**When:** `use_mcp_framework: true` but MCP Server unreachable or returns error

**Retry Policy (per NFR-Reliability-01):**
1. Attempt MCP resource request
2. If timeout (>5 seconds) or HTTP error (503, 500), retry with exponential backoff:
   - Retry 1: Wait 100ms, retry request
   - Retry 2: Wait 200ms, retry request
   - Retry 3: Wait 400ms, retry request
3. If all retries fail, fall back to local file approach

**Fallback Workflow:**
1. Log warning: "⚠️ MCP Server unavailable (URL: {mcp_server_url}), falling back to local files"
2. Switch to Local File Mode for current session
3. Continue workflow execution without hard failure
4. Notify user at end of task: "⚠️ MCP Server was unavailable during this task. Local file approach used. Check MCP Server status."

**Error Scenarios:**
- **Connection Timeout (>5 seconds):** Fall back to local files
- **HTTP 503 Service Unavailable:** Fall back to local files
- **HTTP 500 Internal Server Error:** Fall back to local files
- **Invalid MCP Response (malformed JSON):** Fall back to local files
- **Resource Not Found (404):** Hard failure (misconfiguration, not transient error)
```

**Step 4: Update Resource/Prompt/Tool Loading Instructions**

Update CLAUDE.md orchestration instructions to include mode detection:

```markdown
## Resource Loading (Mode-Aware)

**If `use_mcp_framework: true`:**
1. Request resource from MCP Server: `mcp://resources/sdlc/core`
2. If successful, use MCP resource content
3. If failed (after retries), fall back to local file: `CLAUDE.md` (embedded SDLC content or separate `prompts/CLAUDE/sdlc-core.md`)

**If `use_mcp_framework: false`:**
1. Read local file: `CLAUDE.md` (embedded SDLC content) or `prompts/CLAUDE/sdlc-core.md`
2. No MCP Server requests made

## Generator Execution (Mode-Aware)

**If `use_mcp_framework: true`:**
1. Call MCP prompt: `mcp://prompts/generator/{artifact_name}`
2. If successful, use MCP prompt content
3. If failed (after retries), fall back to local file: `prompts/{artifact_name}-generator.xml`

**If `use_mcp_framework: false`:**
1. Read local file: `prompts/{artifact_name}-generator.xml`
2. No MCP Server requests made

## Tool Execution (Mode-Aware)

**If `use_mcp_framework: true`:**
1. Call MCP tool: `validate_artifact`, `resolve_artifact_path`, etc.
2. If successful, use tool result
3. If failed (after retries), fall back to AI inference with warning: "⚠️ MCP tools unavailable, using AI inference (error rate may increase to 20-30%)"

**If `use_mcp_framework: false`:**
1. Use AI inference for validation and path resolution
2. No MCP Server requests made
```

**Step 5: Validation**

- Test configuration detection (`.mcp/config.json` parsing, environment variable override)
- Test MCP mode with MCP Server running (resources, prompts, tools load successfully)
- Test local file mode (use_mcp_framework: false, all local files load successfully)
- Test graceful degradation (simulate MCP Server unavailability, verify fallback to local files)
- Test retry logic (simulate transient MCP Server failures, verify exponential backoff)
- Validate functional equivalence (US-062 regression testing)

**References to Implementation Standards:**
- patterns-core.md: Core development philosophy applies to backward compatibility approach
- patterns-validation.md: Validate configuration file schema (JSON validation)

### Technical Tasks
- [ ] Define `.mcp/config.json` schema with `use_mcp_framework` flag
- [ ] Add configuration detection logic to CLAUDE.md
- [ ] Add mode selection logic (MCP vs. Local File)
- [ ] Add graceful degradation workflow with retry logic
- [ ] Update resource loading instructions for mode-aware behavior
- [ ] Update prompt loading instructions for mode-aware behavior
- [ ] Update tool execution instructions for mode-aware behavior
- [ ] Add warning messages for fallback scenarios
- [ ] Document configuration file schema in CLAUDE.md
- [ ] Test configuration detection and mode selection
- [ ] Test graceful degradation (simulate MCP Server unavailability)
- [ ] Test retry logic (simulate transient failures)
- [ ] Validate functional equivalence (both modes produce same outputs)

## Acceptance Criteria

### Scenario 1: Configuration Detection
**Given** project contains `.mcp/config.json` with `use_mcp_framework: true`
**When** Claude Code reads CLAUDE.md
**Then** configuration flag detected and MCP mode enabled

### Scenario 2: MCP Mode (Server Available)
**Given** `use_mcp_framework: true` and MCP Server running
**When** Claude Code executes workflow
**Then** resources, prompts, and tools loaded from MCP Server successfully

### Scenario 3: Local File Mode (Explicit Opt-Out)
**Given** `use_mcp_framework: false` in configuration
**When** Claude Code executes workflow
**Then** local files loaded (CLAUDE.md, prompts/*, templates/*), no MCP Server requests made

### Scenario 4: Graceful Degradation (MCP Server Unavailable)
**Given** `use_mcp_framework: true` but MCP Server unreachable
**When** Claude Code attempts MCP resource request
**Then** retry logic executes (3 retries, exponential backoff), falls back to local files, warning message displayed

### Scenario 5: Functional Equivalence
**Given** same generator executed in MCP mode and Local File mode
**When** artifacts generated in both modes
**Then** artifacts are byte-identical (NFR-Compatibility-02)

### Scenario 6: Retry Logic
**Given** MCP Server returns transient error (HTTP 503)
**When** Claude Code requests resource
**Then** retry logic executes (100ms, 200ms, 400ms backoff), succeeds on retry or falls back to local files after max retries

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 5 SP (CONSIDER threshold but below DON'T SKIP at 8+ SP)
- **Developer Count:** Single developer (CLAUDE.md orchestration instructions + configuration schema)
- **Domain Span:** Single domain (documentation/configuration only, no code implementation)
- **Complexity:** Medium - Configuration detection and fallback logic well-defined, no complex algorithms
- **Uncertainty:** Low - Clear requirements from PRD-006 v3 FR-13 and NFR-Compatibility requirements
- **Override Factors:** None - No cross-domain dependencies, no security-critical changes, no unfamiliar technology

**Conclusion:** While 5 SP is at CONSIDER threshold, the documentation-focused nature of the work (CLAUDE.md updates, configuration schema definition) with clear requirements does not warrant task decomposition. Implementation can proceed as a single cohesive unit of work within one sprint.

## Definition of Done
- [ ] `.mcp/config.json` schema defined with `use_mcp_framework` flag
- [ ] Configuration detection logic added to CLAUDE.md
- [ ] Mode selection logic documented (MCP vs. Local File)
- [ ] Graceful degradation workflow documented with retry logic
- [ ] Resource loading instructions updated for mode-aware behavior
- [ ] Prompt loading instructions updated for mode-aware behavior
- [ ] Tool execution instructions updated for mode-aware behavior
- [ ] Warning messages added for fallback scenarios
- [ ] Configuration schema documented in CLAUDE.md
- [ ] Configuration detection tested (parsing, environment variable override)
- [ ] Graceful degradation tested (simulated MCP Server unavailability)
- [ ] Retry logic tested (simulated transient failures)
- [ ] Functional equivalence validated (US-062 regression testing)
- [ ] Code reviewed and approved
- [ ] Documentation updated (CHANGELOG or migration notes)
- [ ] Product Owner acceptance obtained

## Additional Information
**Suggested Labels:** infrastructure, backward-compatibility, configuration, resilience
**Estimated Story Points:** 5
**Dependencies:**
- **Depends On:** US-056, US-057, US-058 (CLAUDE.md orchestration updates for MCP mode)
- **Blocks:** US-060 (Integration Testing) - requires backward compatibility for testing both modes
- **Blocks:** US-062 (Regression Testing) - validates functional equivalence between modes
- **Related:** All HLS-006 through HLS-009 stories (US-028 through US-055) - provide MCP Server implementation

## Open Questions & Implementation Uncertainties

**No open implementation questions. All technical approaches clear from PRD-006 v3 §Requirements (FR-13) and §Non-Functional Requirements (NFR-Compatibility-01, NFR-Reliability-01).**

**Key Decisions Already Made:**
- Configuration file location: `.mcp/config.json` in project root
- Configuration schema: JSON with `use_mcp_framework` boolean flag
- Default behavior: `false` (local file approach, safe fallback)
- Retry policy: 3 retries, exponential backoff (100ms, 200ms, 400ms) per NFR-Reliability-01
- Fallback behavior: Graceful degradation with warning message (no hard failure)
- Transition period: ≥3 months backward compatibility maintenance per NFR-Compatibility-01

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-010_claude_orchestration_integration_testing_v2.md`
- **Parent Epic:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`
- **Related Stories:** US-056 (MCP Resources), US-057 (MCP Prompts), US-058 (MCP Tools), US-060 (Integration Testing), US-062 (Regression Testing)

## Version History
- **v1 (2025-10-18):** Initial version
