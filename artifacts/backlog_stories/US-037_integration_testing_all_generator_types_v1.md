# User Story: Integration Testing for All Generator Types

## Metadata
- **Story ID:** US-037
- **Title:** Integration Testing for All Generator Types
- **Type:** Quality Assurance
- **Status:** Backlog
- **Priority:** High - validates functional equivalence of MCP vs. local file approach
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-007 (MCP Prompts - Generators Migration)
- **Functional Requirements Covered:** FR-05 (validation), NFR-Compatibility-02
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration v3]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Requirements - FR-05 (validation), NFR-Compatibility-02, NFR-Performance-01, NFR-Performance-02
- **Functional Requirements Coverage:**
  - **FR-05:** MCP Server SHALL expose all artifact generators as MCP prompts - validation required
  - **NFR-Compatibility-02:** Generated artifacts using MCP approach SHALL be byte-identical to artifacts generated with local file approach (verified via diff on 10 sample artifacts)
  - **NFR-Performance-01:** MCP resource loading latency SHALL be <100ms for 95th percentile (p95 <100ms)
  - **NFR-Performance-02:** MCP tool execution latency SHALL be <500ms for 95th percentile (p95 <500ms)

**Parent High-Level Story:** [HLS-007: MCP Prompts - Generators Migration]
- **Link:** `/artifacts/hls/HLS-007_mcp_prompts_generators_migration_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 3

## User Story
As a QA Engineer, I want comprehensive integration tests for all 10 generator types via MCP prompts, validating byte-identical output to local file approach and performance targets, so that we can confidently deploy MCP prompts to production.

## Description
This story implements end-to-end integration testing for the MCP prompt migration. Tests validate that all 10 generator types (product-vision, initiative, epic, prd, hls, backlog-story, spike, adr, tech-spec, implementation-task) produce identical artifacts whether executed via MCP prompts or local files, and meet performance targets.

**Current State:** No automated integration tests exist for MCP prompt execution. Migration validation is manual.

**Desired State:** Automated integration test suite validates all 10 generators via MCP prompts, with byte-identical artifact comparison, performance benchmarks, and CI/CD integration.

**Business Value:** Provides confidence for production deployment, prevents regressions, validates NFR-Compatibility-02 requirement (byte-identical outputs), enables continuous validation of generator updates.

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§7.1: Unit Testing:** Tool logic testing patterns with AsyncMock for MCP client (ref: Implementation Research §7.1 lines 947-988)
- **§7.2: Integration Testing:** MCP protocol testing with real MCP client and server (ref: Implementation Research §7.2 lines 990-1024)
- **§6.2: Prometheus Metrics:** Instrument tests to collect latency metrics for performance validation

**Anti-Patterns Avoided:**
- **§8.1 Pitfall 1: Treating MCP as Stateless REST:** Integration tests use proper MCP client lifecycle (initialize → call → cleanup), not raw HTTP assertions

**Performance Considerations:**
- **Target:** p95 latency <500ms for MCP prompt calls (per PRD-006 NFR-Performance-02)
- **Measurement:** Collect latency percentiles (p50, p95, p99) across 100+ test runs per generator

## Functional Requirements
- Implement integration tests for all 10 generator types via MCP prompts
- Validate byte-identical artifacts between MCP and local file approaches
- Measure and validate performance targets (p95 latency <500ms)
- Test error scenarios (missing prompt, malformed XML, MCP Server unavailable)
- Automate tests in CI/CD pipeline (run on every commit to main branch)
- Generate test report with pass/fail status, performance metrics, artifact diffs (if not byte-identical)
- Validate all 10 generators with representative input artifacts

## Non-Functional Requirements
- **Reliability:** Tests must be deterministic (no flaky failures)
- **Performance:** Test suite completes in <10 minutes for all 10 generators
- **Maintainability:** Tests use shared fixtures for input artifacts, easy to add new generator types
- **Observability:** Test reports include detailed failure information (which criterion failed, actual vs. expected diff)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story implements integration tests for MCP Server. Reference Python testing patterns.

### Implementation Guidance

**Integration Test Structure:**
- Use pytest with async support (`pytest-asyncio` plugin)
- Implement fixture for MCP Server startup/shutdown (`@pytest.fixture(scope="session")`)
- Implement fixture for MCP client initialization
- Create parameterized test function for all 10 generator types (`@pytest.mark.parametrize`)
- Generate artifacts using both MCP and local file approaches
- Compare outputs using byte-level diff (hashlib.md5 or filecmp.cmp)
- Collect latency metrics using pytest-benchmark plugin (optional) or custom timing

**Test Data Setup:**
- Use representative input artifacts for each generator type (e.g., EPIC-006 for prd-generator)
- Store input artifacts in `tests/fixtures/artifacts/` directory
- Expected output artifacts in `tests/fixtures/expected_outputs/` directory

**Byte-Identical Comparison:**
- Generate artifact via MCP prompt → save to temp file
- Generate artifact via local file → save to temp file
- Compare files using `filecmp.cmp(shallow=False)` for byte-identical check
- If diff detected: log diff output using `difflib.unified_diff()` for debugging

**References to Implementation Standards:**
- **CLAUDE-testing.md (Python):** Testing strategy with ≥80% unit test coverage, integration tests for MCP resource/tool workflows, fixture patterns
- **CLAUDE-tooling.md (Python):** Use pytest for testing, Taskfile commands (`task test`, `task test-integration`)

**Note:** Treat CLAUDE.md content as authoritative - supplement with story-specific context, don't duplicate.

### Technical Tasks
- **Test Infrastructure:** Implement pytest fixtures for MCP Server and client setup/teardown
- **Test Data:** Create representative input artifacts for all 10 generator types in `tests/fixtures/`
- **Parameterized Tests:** Implement single parameterized test function covering all 10 generators
- **Byte-Identical Validation:** Implement artifact comparison logic with diff output on failure
- **Performance Measurement:** Collect and validate latency metrics (p50, p95, p99)
- **Error Scenario Tests:** Test missing prompt, malformed XML, MCP Server unavailable scenarios
- **CI/CD Integration:** Add integration test job to GitHub Actions workflow
- **Test Report:** Generate test report with summary (pass/fail count, performance metrics, diffs)

## Acceptance Criteria

**Format Guidance:** Gherkin format (Given-When-Then) for scenario-based validation.

### Scenario 1: All 10 generators produce byte-identical artifacts
**Given** MCP Server is running with all 10 generator prompts exposed
**When** integration test suite executes all 10 generators via MCP prompts
**And** same generators executed via local file reading
**Then** all 10 artifacts generated via MCP are byte-identical to local file artifacts
**And** byte-level comparison passes for all 10 generator types (no diffs detected)

### Scenario 2: Performance targets met for all generators
**Given** integration tests collect latency metrics for each generator
**When** test suite executes each generator 100 times via MCP prompt
**Then** p95 latency is <500ms for all 10 generator types
**And** p99 latency is <1000ms for all 10 generator types
**And** average latency delta between MCP and local file is <10%

### Scenario 3: Test suite runs in CI/CD pipeline
**Given** integration tests added to GitHub Actions workflow
**When** developer pushes commit to main branch
**Then** CI/CD pipeline triggers integration test job
**And** test job starts MCP Server, runs all 10 generator tests
**And** test job reports pass/fail status to GitHub PR checks
**And** test job completes in <10 minutes

### Scenario 4: Detailed failure reporting for non-identical artifacts
**Given** generator produces non-identical artifact (e.g., timestamp difference)
**When** byte-identical comparison fails
**Then** test report includes unified diff output showing exact differences
**And** diff highlights lines with mismatches (expected vs. actual)
**And** test fails with clear error message indicating which generator failed

### Scenario 5: Error scenario - missing prompt handling
**Given** MCP Server is running but `mcp://prompts/generator/invalid` does not exist
**When** integration test attempts to call missing prompt
**Then** test validates error response (404 Not Found)
**And** test validates error message format: "Prompt not found: mcp://prompts/generator/invalid"
**And** test passes if error handling matches expected behavior

### Scenario 6: Error scenario - MCP Server unavailable
**Given** MCP Server is stopped or unreachable
**When** integration test attempts to call generator prompt
**Then** test validates connection error or timeout
**And** test validates fallback to local file approach works correctly
**And** test passes if graceful degradation behavior matches specification

### Scenario 7: Test fixtures reusable for new generator types
**Given** new generator type added (e.g., `deployment-plan-generator`)
**When** test engineer adds new generator to parameterized test list
**And** provides input artifact fixture and expected output
**Then** test suite automatically includes new generator in integration tests
**And** no code changes required beyond fixture data and parameter list update

### Scenario 8: Test report includes performance metrics summary
**Given** integration tests collect latency metrics for all generators
**When** test suite completes
**Then** test report includes performance summary table:
- Generator name | p50 latency | p95 latency | p99 latency | Pass/Fail
- Summary row: Average latency, slowest generator, pass rate
**And** report indicates whether all generators meet NFR-Performance-02 target

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Consider Tasks

**Rationale:**
- **Story Points:** 5 SP (CONSIDER per SDLC Section 11.6 - 3-5 SP depends on complexity)
- **Developer Count:** Single developer (QA Engineer)
- **Domain Span:** Single domain (testing infrastructure)
- **Complexity:** Medium - requires pytest fixtures, parameterized tests, byte-identical comparison, CI/CD integration
- **Uncertainty:** Low - testing patterns well-documented in Implementation Research
- **Override Factors:** None (no cross-domain changes, not security-critical)

**Decision:** No Tasks Needed for this story.

**Justification:** Story is focused testing work with clear test cases. Single QA Engineer can implement fixtures and parameterized tests in 1-2 days. Decomposition overhead not justified for 5 SP story with clear scope.

## Definition of Done
- [ ] Code implemented and reviewed
- [ ] Integration tests implemented for all 10 generator types
- [ ] Byte-identical validation passing for all 10 generators (100% match)
- [ ] Performance targets validated (p95 <500ms for all generators)
- [ ] Error scenario tests passing (missing prompt, MCP Server unavailable)
- [ ] CI/CD integration complete (tests run on every commit to main)
- [ ] Test report generated with performance metrics and pass/fail summary
- [ ] Test suite executes in <10 minutes
- [ ] Documentation updated (integration test README, how to add new generator tests)
- [ ] Acceptance criteria validated (all 8 scenarios passing)
- [ ] Product owner approval obtained

## Additional Information
**Suggested Labels:** testing, integration-tests, qa, ci-cd
**Estimated Story Points:** 5
**Dependencies:**
- **Story Dependencies:**
  - US-035 (Expose Generators as MCP Prompts) - must complete first
  - US-036 (Update /generate Command to Call MCP Prompts) - must complete first
- **Technical Dependencies:**
  - MCP Server running with all 10 generators exposed
  - pytest with pytest-asyncio plugin
  - Representative input artifacts for each generator type
  - CI/CD infrastructure (GitHub Actions or similar)
- **Team Dependencies:** None

**Related PRD Section:** PRD-006 §Timeline & Milestones - Phase 2: MCP Prompts - Generators Migration (Week 3)

## Open Questions & Implementation Uncertainties

**No open implementation questions.** All technical approaches clear from Implementation Research and PRD-006.

Implementation path is well-defined:
1. pytest fixtures for MCP Server setup (ref: Implementation Research §7.2 - integration testing patterns)
2. Parameterized tests covering all 10 generators (standard pytest pattern)
3. Byte-identical comparison using filecmp.cmp() or hashlib (Python stdlib)
4. CI/CD integration via GitHub Actions workflow (standard DevOps practice)
5. Performance metrics collection via pytest-benchmark or custom timing

All patterns validated in similar MCP integration test suites per Implementation Research §7.2.
