# User Story: Regression Testing (Local File Approach)

## Metadata
- **Story ID:** US-062
- **Title:** Regression Testing (Local File Approach)
- **Type:** Feature
- **Status:** Backlog
- **Priority:** Critical - Validates zero breaking changes for existing projects, critical for safe migration rollout
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-010
- **Functional Requirements Covered:** NFR-Compatibility-01, NFR-Compatibility-02, NFR-Compatibility-03 (validation via regression testing)
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Non-Functional Requirements - NFR-Compatibility-01, NFR-Compatibility-02, NFR-Compatibility-03; §Timeline & Milestones - Phase 5 (Week 7)
- **Functional Requirements Coverage:**
  - **NFR-Compatibility-01:** MCP Server SHALL maintain backward compatibility with local file approach during transition period (3 months minimum) allowing projects to opt-in incrementally
  - **NFR-Compatibility-02:** Generated artifacts using MCP approach SHALL be byte-identical to artifacts generated with local file approach (verified via diff on 10 sample artifacts)
  - **NFR-Compatibility-03:** Main CLAUDE.md orchestration updates SHALL not break existing projects using local file approach (validated via regression test suite)

**Parent High-Level Story:** [HLS-010: CLAUDE.md Orchestration Update & Integration Testing]
- **Link:** `/artifacts/hls/HLS-010_claude_orchestration_integration_testing_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 7

## User Story
As a Framework Maintainer, I want comprehensive regression tests validating that local file approach (`use_mcp_framework: false`) still functions correctly after CLAUDE.md refactoring, so that existing projects continue working without disruption during MCP migration rollout.

## Description

The MCP framework migration introduces significant changes to CLAUDE.md orchestration (US-056, US-057, US-058) and backward compatibility mode (US-059). While integration testing (US-060) validates MCP mode functionality, regression testing is required to ensure that **existing projects using local file approach are not broken** by these changes.

This story implements automated regression tests to validate:

1. **Local File Mode Functional Equivalence:**
   - All 10 representative workflows execute successfully with `use_mcp_framework: false`
   - Generated artifacts match pre-refactoring baseline (byte-identical per NFR-Compatibility-02)

2. **CLAUDE.md Orchestration Updates Don't Break Local Mode:**
   - Refactored CLAUDE.md orchestrator correctly detects local file mode and skips MCP requests
   - Local file loading still works for CLAUDE.md (or sdlc-core.md), prompts/*, templates/*
   - AI inference fallback works for validation and path resolution

3. **Zero Breaking Changes for Existing Projects:**
   - Projects without `.mcp/config.json` default to local file mode (safe fallback)
   - Projects with `use_mcp_framework: false` continue functioning without MCP Server dependency
   - No hard failures when MCP Server unavailable

**Regression Test Scope (50+ Test Cases):**
- **Workflow Tests (10 workflows × 2 scenarios = 20 tests):** Execute 10 workflows with local file mode, compare outputs to baseline
- **Configuration Tests (5 tests):** Test config detection (missing config, explicit false, environment variable override)
- **Fallback Tests (10 tests):** Test graceful degradation (MCP Server unavailable, invalid MCP response)
- **File Loading Tests (10 tests):** Test local file loading (CLAUDE.md, generators, templates, artifacts)
- **AI Inference Tests (5 tests):** Test validation and path resolution fallback to AI inference

**Scope:**
- In Scope: Automated regression tests for local file approach
- In Scope: Functional equivalence validation (compare outputs to baseline)
- In Scope: Byte-identical artifact comparison for 10 sample workflows
- Out of Scope: MCP mode testing (covered by US-060 integration testing)
- Out of Scope: Performance benchmarking (covered by US-061 token usage measurement)

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§7.4: Regression Testing Patterns:** Validate that refactoring does not break existing functionality
  - **Golden Master Testing:** Compare generated artifacts to known-good baseline (byte-identical)
- **§7.5: Backward Compatibility Testing:** Test all configuration scenarios (missing config, explicit false, default behavior)
  - **Safe Fallback Validation:** Verify graceful degradation when MCP unavailable
- **§7.6: Test Data Management:** Baseline artifacts from pre-refactoring commit tagged as "golden master"

**Anti-Patterns Avoided:**
- **§6.12: Breaking Changes Without Warning:** Avoid silent breaking changes to existing projects (regression tests catch unintended breaks)
- **§6.13: Insufficient Fallback Testing:** Avoid assuming fallback mode works without explicit testing (test all degradation scenarios)

**Performance Considerations:**
- **§8.14: Regression Test Execution Time:** Regression test suite should complete in <15 minutes (50+ tests)

## Functional Requirements
- Implement automated regression tests for local file approach (50+ test cases)
- Test 10 representative workflows with `use_mcp_framework: false`
- Compare generated artifacts to baseline (byte-identical validation)
- Test configuration detection scenarios (missing config, explicit false, environment variable override)
- Test graceful degradation (MCP Server unavailable, invalid MCP response)
- Test local file loading (CLAUDE.md, generators, templates, artifacts)
- Test AI inference fallback (validation, path resolution)
- Regression test suite completes in <15 minutes
- All tests pass with ≥95% pass rate (flaky tests debugged)

## Non-Functional Requirements
- **Reliability:** Regression tests pass consistently (≥95% pass rate)
- **Performance:** Test suite execution <15 minutes total
- **Maintainability:** Clear test structure, baseline artifacts version-controlled
- **Documentation:** Test execution instructions, baseline artifact update procedure

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story implements regression tests for backward compatibility validation.

### Implementation Guidance

**Step 1: Baseline Artifact Collection**

Capture baseline artifacts from pre-refactoring commit:

```bash
# Checkout commit before CLAUDE.md refactoring (before US-056)
git checkout <pre-refactoring-commit>

# Execute 10 workflows with local file approach
# Save generated artifacts to tests/regression/baseline/
pytest tests/regression/generate_baseline_artifacts.py

# Tag baseline artifacts as golden master
git tag golden-master-baseline

# Return to current branch
git checkout main
```

Baseline directory structure:
```
tests/regression/baseline/
├── VIS-001_product_vision_v1.md
├── INIT-001_initiative_v1.md
├── EPIC-000_epic_v1.md
├── PRD-000_prd_v1.md
├── HLS-001_hls_v1.md
├── US-001_backlog_story_v1.md
├── SPEC-001_tech_spec_v1.md
├── EPIC-000_epic_v2.md  # Refinement test
├── PRD-000_prd_v2.md    # Refinement test
└── PRD-000_validation_results.json
```

**Step 2: Regression Test Framework**

Implement regression test framework with pytest:

```python
# tests/regression/test_local_file_approach.py

import pytest
from pathlib import Path
import filecmp
import json

BASELINE_DIR = Path("tests/regression/baseline")
OUTPUT_DIR = Path("tests/regression/output")

@pytest.fixture(scope="session")
def local_file_config():
    """Configure local file mode for all regression tests"""
    config = {"use_mcp_framework": False}
    config_file = Path(".mcp/config.test.json")
    with open(config_file, "w") as f:
        json.dump(config, f)
    yield config
    # Cleanup: Remove test config
    config_file.unlink()

@pytest.fixture(scope="function")
def output_dir():
    """Create clean output directory for each test"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    yield OUTPUT_DIR
    # Cleanup: Remove test outputs after test
    for file in OUTPUT_DIR.iterdir():
        file.unlink()
```

**Step 3: Workflow Regression Tests (20 tests)**

Test 10 workflows with local file approach, compare outputs to baseline:

```python
def test_workflow_01_product_vision_local_mode(local_file_config, output_dir):
    """
    Test: Generate Product Vision (VIS-001) with local file approach
    Validates: Local file mode generates same artifact as baseline
    """
    # Execute: Run workflow with local file mode
    # (Simulated execution - actual test would invoke Claude Code)
    response = execute_workflow_local(
        workflow_id="WF-01",
        config=local_file_config
    )
    output_file = output_dir / "VIS-001_product_vision_v1.md"
    output_file.write_text(response.artifact_content)

    # Assert: Compare to baseline (byte-identical)
    baseline_file = BASELINE_DIR / "VIS-001_product_vision_v1.md"
    assert filecmp.cmp(output_file, baseline_file, shallow=False), \
        f"Artifact mismatch: {output_file} != {baseline_file}"

def test_workflow_02_initiative_local_mode(local_file_config, output_dir):
    """Test: Generate Initiative (INIT-001) with local file approach"""
    # Similar structure to test_workflow_01
    pass

# ... Similar tests for workflows 3-10 (EPIC, PRD, HLS, US, SPEC, refinements, validation)
```

**Step 4: Configuration Detection Tests (5 tests)**

Test configuration scenarios:

```python
def test_config_missing_defaults_to_local_mode():
    """
    Test: Missing .mcp/config.json defaults to local file approach
    Validates: Safe fallback behavior (no MCP Server dependency)
    """
    # Remove config file if exists
    config_file = Path(".mcp/config.json")
    if config_file.exists():
        config_file.unlink()

    # Execute: Read CLAUDE.md orchestration instructions
    # Assert: Detects missing config, defaults to use_mcp_framework: false
    detected_mode = detect_configuration_mode()
    assert detected_mode == "local", \
        "Missing config should default to local file mode"

def test_config_explicit_false():
    """Test: Explicit use_mcp_framework: false uses local file approach"""
    config_file = Path(".mcp/config.json")
    config_file.write_text('{"use_mcp_framework": false}')

    detected_mode = detect_configuration_mode()
    assert detected_mode == "local"

def test_config_env_variable_override():
    """Test: Environment variable USE_MCP_FRAMEWORK overrides config file"""
    # Set environment variable
    os.environ["USE_MCP_FRAMEWORK"] = "false"

    # Create config with true (should be overridden)
    config_file = Path(".mcp/config.json")
    config_file.write_text('{"use_mcp_framework": true}')

    detected_mode = detect_configuration_mode()
    assert detected_mode == "local", \
        "Environment variable should override config file"

    # Cleanup
    del os.environ["USE_MCP_FRAMEWORK"]

# ... Additional config tests (invalid JSON, malformed config)
```

**Step 5: Graceful Degradation Tests (10 tests)**

Test fallback scenarios:

```python
def test_fallback_mcp_server_unavailable():
    """
    Test: MCP Server unavailable triggers fallback to local files
    Validates: Graceful degradation per NFR-Compatibility-03
    """
    # Setup: Configure MCP mode with invalid server URL
    config = {"use_mcp_framework": True, "mcp_server_url": "http://localhost:9999"}

    # Execute: Attempt workflow execution
    # Assert: Falls back to local file mode with warning
    result = execute_workflow_with_fallback("WF-01", config)
    assert result.mode == "local", "Should fall back to local mode"
    assert "MCP Server unavailable" in result.warnings

def test_fallback_mcp_invalid_response():
    """Test: Invalid MCP response (malformed JSON) triggers fallback"""
    # Similar structure to test_fallback_mcp_server_unavailable
    pass

# ... Additional fallback tests (timeout, HTTP 500, HTTP 503, resource not found)
```

**Step 6: File Loading Tests (10 tests)**

Test local file loading:

```python
def test_load_local_claude_md():
    """Test: CLAUDE.md (or sdlc-core.md) loads successfully in local mode"""
    config = {"use_mcp_framework": False}

    # Execute: Load CLAUDE.md content
    content = load_sdlc_instructions(config)

    # Assert: Content loaded from local file
    assert content is not None
    assert "Artifact Dependency Flow" in content

def test_load_local_generator():
    """Test: Generator XML loads from local prompts/*-generator.xml"""
    config = {"use_mcp_framework": False}

    # Execute: Load epic-generator.xml
    generator_content = load_generator("epic", config)

    # Assert: Content loaded from local file
    assert generator_content is not None
    assert "epic-generator" in generator_content.lower()

# ... Additional file loading tests (templates, artifacts, patterns-*.md files)
```

**Step 7: AI Inference Fallback Tests (5 tests)**

Test validation and path resolution fallback:

```python
def test_validation_fallback_ai_inference():
    """
    Test: Validation falls back to AI inference in local mode
    Validates: AI inference used when validate_artifact tool unavailable
    """
    config = {"use_mcp_framework": False}

    # Execute: Validate artifact (should use AI inference, not MCP tool)
    result = validate_artifact_local_mode(
        artifact_content=sample_prd_content,
        config=config
    )

    # Assert: Validation completed (AI inference)
    assert result.validation_method == "ai_inference"
    assert result.passed is not None  # Result available (true or false)

def test_path_resolution_fallback_ai_inference():
    """Test: Path resolution falls back to AI inference in local mode"""
    # Similar structure to test_validation_fallback_ai_inference
    pass

# ... Additional AI inference tests (edge cases, error handling)
```

**Step 8: Regression Test Execution**

Run regression tests:

```bash
# Generate baseline artifacts (one-time, on pre-refactoring commit)
git checkout <pre-refactoring-commit>
pytest tests/regression/generate_baseline_artifacts.py
git checkout main

# Run regression test suite
pytest tests/regression/ -v

# Expected output: 50+ tests passing, <15 minutes execution time
```

**References to Implementation Standards:**
- patterns-testing.md: Follow testing patterns (pytest fixtures, golden master testing)
- patterns-tooling.md: Use Taskfile commands for regression test execution

### Technical Tasks
- [ ] Capture baseline artifacts from pre-refactoring commit (10 workflows)
- [ ] Tag baseline artifacts as golden master (git tag)
- [ ] Implement regression test framework (pytest fixtures, output directory)
- [ ] Implement workflow regression tests (20 tests: 10 workflows × 2 scenarios)
- [ ] Implement configuration detection tests (5 tests)
- [ ] Implement graceful degradation tests (10 tests)
- [ ] Implement file loading tests (10 tests)
- [ ] Implement AI inference fallback tests (5 tests)
- [ ] Add regression tests to CI pipeline (GitHub Actions)
- [ ] Document test execution instructions
- [ ] Document baseline artifact update procedure
- [ ] Validate test suite execution time (<15 minutes)

## Acceptance Criteria

### Scenario 1: All Workflow Regression Tests Pass
**Given** 10 workflows executed with local file approach (`use_mcp_framework: false`)
**When** regression test suite executes
**Then** all 10 workflow tests pass, generated artifacts byte-identical to baseline

### Scenario 2: Configuration Detection Tests Pass
**Given** configuration scenarios tested (missing config, explicit false, environment variable override)
**When** configuration detection tests execute
**Then** all 5 tests pass, local file mode correctly detected in all scenarios

### Scenario 3: Graceful Degradation Tests Pass
**Given** MCP Server unavailable scenarios tested (timeout, HTTP 500, invalid response)
**When** graceful degradation tests execute
**Then** all 10 tests pass, fallback to local file mode succeeds with warning messages

### Scenario 4: File Loading Tests Pass
**Given** local file loading tested (CLAUDE.md, generators, templates, artifacts)
**When** file loading tests execute
**Then** all 10 tests pass, files load successfully from local paths

### Scenario 5: AI Inference Fallback Tests Pass
**Given** validation and path resolution tested with local file mode
**When** AI inference fallback tests execute
**Then** all 5 tests pass, AI inference used correctly when MCP tools unavailable

### Scenario 6: Regression Test Suite Execution Time <15 Minutes
**Given** All 50+ regression tests implemented
**When** regression test suite executes
**Then** total execution time <15 minutes

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 5 SP (CONSIDER threshold but below DON'T SKIP at 8+ SP)
- **Developer Count:** Single developer (regression test implementation focused)
- **Domain Span:** Single domain (testing only, no production code changes)
- **Complexity:** Medium - Straightforward regression testing with golden master comparison, well-defined scenarios
- **Uncertainty:** Low - Clear test cases defined, baseline artifacts available from pre-refactoring commit
- **Override Factors:** None - No cross-domain dependencies, no security-critical changes, no unfamiliar technology

**Conclusion:** While 5 SP is at CONSIDER threshold, the focused nature of the work (regression testing with golden master comparison) with clear test scenarios does not warrant task decomposition. Implementation can proceed as a single cohesive unit of work within one sprint.

## Definition of Done
- [ ] Baseline artifacts captured from pre-refactoring commit (10 workflows)
- [ ] Baseline artifacts tagged as golden master (git tag)
- [ ] Regression test framework implemented (pytest fixtures, output directory)
- [ ] Workflow regression tests implemented (20 tests: 10 workflows × 2 scenarios)
- [ ] Configuration detection tests implemented (5 tests)
- [ ] Graceful degradation tests implemented (10 tests)
- [ ] File loading tests implemented (10 tests)
- [ ] AI inference fallback tests implemented (5 tests)
- [ ] All regression tests passing (≥95% pass rate)
- [ ] Regression tests added to CI pipeline (GitHub Actions)
- [ ] Test execution instructions documented
- [ ] Baseline artifact update procedure documented
- [ ] Test suite execution time <15 minutes validated
- [ ] Code reviewed and approved
- [ ] Product Owner acceptance obtained

## Additional Information
**Suggested Labels:** testing, regression-testing, backward-compatibility, quality-assurance
**Estimated Story Points:** 5
**Dependencies:**
- **Depends On:** US-056/057/058 (CLAUDE.md Orchestration) - refactoring to be validated
- **Depends On:** US-059 (Backward Compatibility Mode) - fallback logic to be tested
- **Related:** US-060 (Integration Testing) - complementary testing (MCP mode vs. local mode)
- **Related:** US-061 (Token Usage Measurement) - validates functional equivalence and performance

## Decisions Made

**All technical approaches clear from PRD-006 v3 §Non-Functional Requirements (NFR-Compatibility-01, NFR-Compatibility-02, NFR-Compatibility-03).**

**Key Decisions Already Made:**
- Baseline artifacts: Captured from pre-refactoring commit (before US-056)
- Comparison method: Byte-identical comparison (filecmp.cmp) per NFR-Compatibility-02
- Test scenarios: 50+ test cases covering workflow execution, configuration detection, graceful degradation, file loading, AI inference fallback
- Pass criteria: ≥95% pass rate, all workflow artifacts byte-identical to baseline
- Execution time target: <15 minutes for full regression suite

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-010_claude_orchestration_integration_testing_v2.md`
- **Parent Epic:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`
- **Related Stories:** US-056/057/058 (CLAUDE.md Orchestration), US-059 (Backward Compatibility), US-060 (Integration Testing), US-061 (Token Usage Measurement)

## Version History
- **v1 (2025-10-18):** Initial version
