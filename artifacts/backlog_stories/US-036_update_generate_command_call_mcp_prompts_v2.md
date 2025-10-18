# User Story: Update /generate Command to Call MCP Prompts

## Metadata
- **Story ID:** US-036
- **Title:** Update /generate Command to Call MCP Prompts
- **Type:** Feature
- **Status:** Draft
- **Version:** v2 (Applied feedback from US-036_v1_comments.md)
- **Priority:** Critical - enables generator execution via MCP protocol
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-007 (MCP Prompts - Generators Migration)
- **Functional Requirements Covered:** FR-05, FR-12
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration v3]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Requirements - FR-05, FR-12
- **Functional Requirements Coverage:**
  - **FR-05:** MCP Server SHALL expose all artifact generators as MCP prompts using URL pattern `mcp://prompts/generator/{artifact_name}`
  - **FR-12:** Main CLAUDE.md SHALL be refactored to orchestrate MCP Server integration, directing Claude Code to use MCP prompts instead of local file access

**Parent High-Level Story:** [HLS-007: MCP Prompts - Generators Migration]
- **Link:** `/artifacts/hls/HLS-007_mcp_prompts_generators_migration_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 2

## User Story
As a Developer, I want the `/generate` command to call MCP prompts (`mcp://prompts/generator/{generator_name}`) instead of reading local generator files, so that I automatically use the latest generator versions without manual Git pulls.

## Description
The `/generate` command (in `.claude/commands/generate.md`) currently reads generator XML files from local filesystem (`prompts/*-generator.xml`). This story refactors the command to call MCP prompts exposed by MCP Server (US-035), enabling transparent migration from local files to centralized generator management.

**Current State:** `/generate` command reads generator content from local file path `prompts/{generator_name}-generator.xml` using Claude Code's Read tool.

**Desired State:** `/generate` command calls MCP prompt `mcp://prompts/generator/{generator_name}` to retrieve generator content from MCP Server, with fallback to local files if MCP Server unavailable.

**Business Value:** Eliminates manual "git pull generators" workflow, ensures all developers use same generator version, enables instant propagation of generator updates across all projects.

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§8.1: Pitfall 1 - MCP Protocol Lifecycle:** Proper MCP client initialization with handshake before calling prompts (ref: Implementation Research §8.1 lines 1032-1064)
- **§8.2 Anti-Pattern 3: Overly Broad Tool Scope:** Keep `/generate` command focused on single purpose (generator orchestration), no unrelated operations
- **§6.2: Prometheus Metrics:** Instrument MCP prompt calls with success/failure metrics for observability

**Anti-Patterns Avoided:**
- **§8.1 Pitfall 1: Treating MCP as Stateless REST:** Use official MCP client with proper lifecycle (initialize → call prompt → cleanup), not raw HTTP requests
  - **Example Code:** Implementation Research §8.1 lines 1054-1064 (correct MCP client usage)

**Performance Considerations:**
- **Target:** MCP prompt call latency <500ms p95 (includes network + MCP Server response, per PRD-006 NFR-Performance-02)
- **Graceful Degradation:** Fall back to local file reading if MCP Server unavailable (per PRD-006 NFR-Availability-03)

## Functional Requirements
- Refactor `/generate` command to call MCP prompts instead of local file reading
- Construct MCP prompt URI from generator name: `{generator_name}` → `mcp://prompts/generator/{generator_name}`
- Retrieve generator content from MCP Server via MCP prompt call
- Parse returned XML content and execute generator logic (existing behavior unchanged)
- Implement fallback to local file reading if MCP Server unavailable or prompt call fails
- Maintain same command syntax for users: `/generate {generator_name}` (transparent change)
- Log MCP prompt calls with success/failure status for observability

## Non-Functional Requirements
- **Usability:** Developer uses same `/generate` command syntax (transparent MCP vs. local file)
- **Reliability:** Graceful degradation to local file approach if MCP Server unavailable (per PRD-006 NFR-Availability-03)
- **Performance:** MCP prompt call latency p95 <500ms (per PRD-006 NFR-Performance-02)
- **Observability:** Log all MCP prompt calls with timestamp, generator name, execution duration, success/failure status

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story updates client-side command orchestration. Reference Claude Code command patterns.

### Implementation Guidance

**MCP Prompt Call Pattern:**
- Update `.claude/commands/generate.md` to call MCP prompt before executing generator
- Use Claude Code's built-in MCP client capabilities (if available) or implement MCP client call
- Construct prompt URI: `mcp://prompts/generator/{generator_name}` where `{generator_name}` derived from command argument
- Handle MCP client initialization (if not already initialized by Claude Code)
- Parse MCP prompt response to extract generator XML content
- Execute generator logic with retrieved content (reuse existing template substitution and execution logic)

**Fallback Strategy:**
- Try MCP prompt call first (primary path)
- If MCP Server unavailable or prompt call fails: log warning + fall back to local file reading
- Fallback path: Read from `prompts/{generator_name}-generator.xml` using existing Read tool
- Warn user: "Using local generator file (MCP Server unavailable)"

**References to Implementation Standards:**
- **CLAUDE-core.md:** Command orchestration patterns (how /generate command structures execution flow)
- **CLAUDE-testing.md:** Integration testing for command workflows (test both MCP and fallback paths)

**Note:** Treat CLAUDE.md content as authoritative - supplement with story-specific context, don't duplicate.

### Technical Tasks
- **Command Update:** Refactor `.claude/commands/generate.md` to add MCP prompt call step
- **MCP Client Integration:** Implement MCP prompt call logic (or leverage Claude Code's built-in MCP client)
- **Fallback Logic:** Implement graceful degradation to local file reading on MCP Server failure
- **Error Handling:** Add clear error messages for MCP connection failures, prompt not found, malformed responses
- **Logging:** Add structured logging for MCP prompt calls (timestamp, generator name, duration, status)
- **Testing:** Integration tests for MCP path, fallback path, error scenarios

## Acceptance Criteria

**Format Guidance:** Gherkin format (Given-When-Then) for scenario-based validation.

### Scenario 1: Successful generator execution via MCP prompt
**Given** MCP Server is running and `mcp://prompts/generator/epic` is accessible
**When** developer runs `/generate epic-generator` command
**Then** command calls MCP prompt `mcp://prompts/generator/epic`
**And** generator XML content retrieved from MCP Server
**And** generator executes successfully with retrieved content
**And** output artifact generated (e.g., `EPIC-XXX_v1.md`)
**And** user sees no difference vs. local file approach (transparent change)

### Scenario 2: All 10 generator types work via MCP prompts
**Given** MCP Server exposes all 10 generator prompts
**When** developer iterates through generators (epic, prd, hls, backlog-story, etc.)
**Then** all 10 generator types execute successfully via MCP prompts
**And** generated artifacts are byte-identical to local file approach (per PRD-006 NFR-Compatibility-02)

### Scenario 3: Fallback to local file when MCP Server unavailable
**Given** MCP Server is not running or unreachable
**When** developer runs `/generate prd-generator` command
**Then** MCP prompt call fails (connection error or timeout)
**And** command logs warning: "MCP Server unavailable, falling back to local generator file"
**And** command reads generator content from local file `prompts/prd-generator.xml`
**And** generator executes successfully with local file content
**And** output artifact generated successfully

### Scenario 4: Error handling for missing prompt
**Given** MCP Server is running but prompt `mcp://prompts/generator/invalid` does not exist
**When** developer runs `/generate invalid-generator` command
**Then** MCP Server returns 404 Not Found
**And** command logs error: "Prompt not found: mcp://prompts/generator/invalid"
**And** command attempts fallback to local file `prompts/invalid-generator.xml`
**And** if local file also missing: command displays clear error message to user

### Scenario 5: MCP prompt call latency meets performance target
**Given** MCP Server is running with prompt caching enabled
**When** developer runs `/generate hls-generator` command (warm cache)
**Then** MCP prompt call completes in <500ms (p95)
**And** total command execution time similar to local file approach (<5% delta)

### Scenario 6: Logging captures MCP prompt calls
**Given** MCP Server is running
**When** developer runs `/generate backlog-story-generator` command
**Then** command logs structured entry: `{"timestamp": "2025-10-18T12:00:00Z", "command": "/generate", "generator": "backlog-story", "mcp_prompt_uri": "mcp://prompts/generator/backlog-story", "duration_ms": 250, "status": "success"}`
**And** log entry includes MCP Server response status (200 OK)

### Scenario 7: Command syntax unchanged (backward compatibility)
**Given** user familiar with existing `/generate` command syntax
**When** user runs `/generate epic-generator` (same syntax as before)
**Then** command executes without syntax changes
**And** user experience identical to local file approach (transparent migration)

### Scenario 8: Malformed MCP response handling
**Given** MCP Server returns invalid XML content for prompt
**When** developer runs `/generate spike-generator` command
**Then** command detects malformed XML (parsing error)
**And** command logs error with details: "Invalid generator XML received from MCP Server"
**And** command falls back to local file reading
**And** if local file valid: execution continues with fallback content

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Consider Tasks

**Rationale:**
- **Story Points:** 5 SP (CONSIDER per SDLC Section 11.6 - 3-5 SP depends on complexity)
- **Developer Count:** Single developer (command orchestration update)
- **Domain Span:** Single domain (client-side command layer)
- **Complexity:** Medium - requires MCP client integration and fallback logic, but well-defined patterns from Implementation Research
- **Uncertainty:** Low - MCP protocol and fallback patterns documented
- **Override Factors:** None (no cross-domain changes, not security-critical, no multi-system integration)

**Decision:** No Tasks Needed for this story.

**Justification:** Story is straightforward command refactoring with clear implementation path. Single developer can complete in 1-2 days. Decomposition overhead not justified for 5 SP story with low complexity.

## Definition of Done
- [ ] Code implemented and reviewed
- [ ] `/generate` command calls MCP prompts for all 10 generator types
- [ ] Fallback to local files functional when MCP Server unavailable
- [ ] Unit tests written and passing (MCP prompt call logic, fallback logic)
- [ ] Integration tests passing (all 10 generators via MCP, fallback scenarios, error handling)
- [ ] Performance target met (MCP prompt call latency p95 <500ms validated)
- [ ] Logging implemented (structured logs for all MCP prompt calls)
- [ ] Documentation updated (command usage guide notes transparent MCP migration)
- [ ] Acceptance criteria validated (all 8 scenarios passing)
- [ ] Backward compatibility validated (command syntax unchanged)
- [ ] Product owner approval obtained

## Additional Information
**Suggested Labels:** command-orchestration, mcp-client, client-side, critical-path
**Estimated Story Points:** 5
**Dependencies:**
- **Story Dependencies:** US-035 (Expose Generators as MCP Prompts) - must complete first
- **Technical Dependencies:**
  - MCP Server running with generators exposed (US-035 deliverable)
  - Claude Code MCP client capabilities (built-in or custom implementation)
  - Local generator files present for fallback (current state)
- **Team Dependencies:** None

**Related PRD Section:** PRD-006 §Timeline & Milestones - Phase 2: MCP Prompts - Generators Migration (Week 3)

## Decisions Made

### D1: MCP Client Implementation in Claude Code
**Decision:** Claude Code provides command script with built-in MCP client capabilities for calling prompts from `.claude/commands/*.md` files.

**Context:** Implementation path depends on whether Claude Code natively supports MCP prompt calls from command scripts. This decision confirms that Claude Code provides the necessary MCP client API.

**Rationale:** Leverages Claude Code's built-in MCP capabilities instead of implementing custom HTTP client, reducing complexity and maintaining consistency with Claude Code's MCP integration patterns.

**Impact:**
- Implementation uses Claude Code's native MCP prompt call API
- No custom HTTP client or subprocess calls required
- Command script remains declarative and simple
- Testing can rely on Claude Code's MCP client mocking capabilities

**Stakeholders:** Tech Lead, Development Team

### D2: Fallback Path Testing Strategy
**Decision:** Mock MCP client responses to simulate unavailability in integration tests.

**Context:** Fallback logic is critical for reliability (NFR-Availability-03 graceful degradation). Need reliable test strategy that validates fallback without flaky "stop server" tests.

**Rationale:**
- Mocking MCP client provides deterministic test behavior (no race conditions or timing issues)
- Avoids infrastructure complexity of starting/stopping MCP Server in CI/CD
- More reliable than "intentionally break server" tests
- Can simulate specific failure modes (connection timeout, 404 Not Found, malformed response)

**Impact:**
- Integration tests use mocked MCP client responses
- Can simulate all failure scenarios: unavailable server, prompt not found, malformed XML
- Tests run faster (no actual server start/stop)
- CI/CD pipeline remains simple

**Stakeholders:** Tech Lead, QA Team

---

**All technical approaches clear from Implementation Research:**
- MCP client initialization pattern documented (§8.1)
- Fallback strategy defined (graceful degradation per PRD-006 NFR-Availability-03)
- Logging pattern documented (structured JSON logs per §6.1)
