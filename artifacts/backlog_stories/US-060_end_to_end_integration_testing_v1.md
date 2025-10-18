# User Story: End-to-End Integration Testing (10 Workflows)

## Metadata
- **Story ID:** US-060
- **Title:** End-to-End Integration Testing (10 Workflows)
- **Type:** Feature
- **Status:** Backlog
- **Priority:** Critical - Validates complete MCP framework integration before production pilot, prevents regression bugs
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-010
- **Functional Requirements Covered:** All FR-01 through FR-24 (validation via integration testing)
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Goals & Success Metrics, §Timeline & Milestones - Phase 5 (Week 7), §Appendix A: Token Cost Baseline Measurement Plan
- **Functional Requirements Coverage:**
  - **All FR-01 through FR-24:** Integration testing validates end-to-end functionality of all functional requirements (resources, prompts, tools, orchestration, task tracking, ID management)

**Parent High-Level Story:** [HLS-010: CLAUDE.md Orchestration Update & Integration Testing]
- **Link:** `/artifacts/hls/HLS-010_claude_orchestration_integration_testing_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 5

## User Story
As a Framework Maintainer, I want comprehensive end-to-end integration tests for 10 representative SDLC workflows using MCP approach, so that all framework components (resources, prompts, tools, orchestration) are validated before production pilot.

## Description

The MCP framework migration involves multiple integrated components (MCP Server resources/prompts/tools, Task Tracking microservice, updated CLAUDE.md orchestration, backward compatibility mode). Unit tests validate individual components, but end-to-end integration tests are required to validate that the complete system functions correctly for real SDLC workflows.

This story implements automated integration tests for 10 representative workflows (per PRD-006 Appendix A):

1. **Generate Product Vision (VIS-001) from business research**
2. **Generate Initiative (INIT-001) from Product Vision**
3. **Generate Epic (EPIC-000) from Initiative**
4. **Generate PRD (PRD-000) from Epic**
5. **Generate High-Level Story (HLS-001) from PRD**
6. **Generate Backlog Story (US-001) from HLS + PRD**
7. **Generate Tech Spec (SPEC-001) from Backlog Story**
8. **Refine Epic (EPIC-000 v1 → v2) based on critique**
9. **Refine PRD (PRD-000 v1 → v2) based on critique**
10. **Validate PRD-000 against 26-criterion checklist**

Each workflow exercises multiple framework components:
- **Resources:** Load sdlc-core.md, patterns-*.md, templates from MCP Server
- **Prompts:** Call MCP prompts for generators (epic-generator, prd-generator, etc.)
- **Tools:** Call validate_artifact, resolve_artifact_path, get_next_task, update_task_status, get_next_available_id, reserve_id_range
- **Orchestration:** CLAUDE.md directs Claude Code through workflow steps
- **Backward Compatibility:** Test graceful degradation when MCP Server unavailable

**Scope:**
- In Scope: Automated integration tests for 10 workflows
- In Scope: Test execution in MCP mode (`use_mcp_framework: true`)
- In Scope: Test data setup (input artifacts, configuration files)
- In Scope: Assertion validation (artifacts generated, validation passed, IDs assigned)
- Out of Scope: Token usage measurement (covered by US-061)
- Out of Scope: Backward compatibility regression testing (covered by US-062)

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§7.1: Integration Testing Patterns:** End-to-end workflow tests covering multiple components (resources, prompts, tools, database)
  - **Test Structure:** Setup (create test data) → Execute (run workflow) → Assert (validate outputs) → Cleanup (delete test data)
- **§7.2: Test Data Management:** Isolated test database for Task Tracking microservice, test artifacts in temporary directory
  - **Isolation:** Each test workflow uses unique artifact IDs to prevent collisions (e.g., TEST-VIS-001, TEST-INIT-001)
- **§7.3: Mocking vs. Real Dependencies:** Use real MCP Server and Task Tracking microservice (not mocks) for integration tests
  - **Rationale:** Validates actual integration behavior, not mocked behavior

**Anti-Patterns Avoided:**
- **§6.8: Unit Tests Only:** Avoid relying solely on unit tests for complex integrated system (miss integration bugs)
- **§6.9: Manual Testing Only:** Avoid manual workflow execution for regression validation (time-consuming, error-prone, not repeatable)

**Performance Considerations:**
- **§8.8: Test Execution Time:** Integration test suite should complete in <10 minutes (10 workflows × ~1 minute per workflow)
- **§8.9: Parallel Test Execution:** Run independent workflows in parallel to reduce total execution time (if test infrastructure supports parallelization)

## Functional Requirements
- Implement automated integration tests for 10 representative workflows
- Test MCP mode (`use_mcp_framework: true`) for all workflows
- Validate artifact generation (correct content, ID, status, parent references)
- Validate MCP resource loading (sdlc-core.md, patterns-*.md, templates)
- Validate MCP prompt execution (epic-generator, prd-generator, etc.)
- Validate MCP tool execution (validate_artifact, resolve_artifact_path, task tracking, ID management)
- Test data setup (input artifacts, configuration files, test database)
- Assertion validation (artifacts generated, validation passed, IDs assigned correctly)
- Test cleanup (delete test artifacts, reset test database)
- Integration test suite completes in <10 minutes

## Non-Functional Requirements
- **Reliability:** Integration tests pass consistently (>95% pass rate, flaky tests debugged)
- **Performance:** Test suite execution <10 minutes total
- **Maintainability:** Clear test structure (setup, execute, assert, cleanup), test data reusable across workflows
- **Documentation:** Test execution instructions, test data setup guide, troubleshooting common failures

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story implements integration tests for CLAUDE.md orchestration workflows.

### Implementation Guidance

**Step 1: Test Infrastructure Setup**

Create test environment:
- **MCP Server:** Start MCP Server with test configuration (test resource paths, test database)
- **Task Tracking Microservice:** Start microservice with test database (isolated from production data)
- **Test Configuration:** Create `.mcp/config.test.json` with `use_mcp_framework: true` and test MCP Server URL
- **Test Data Directory:** Create `tests/integration/test_data/` for test artifacts

**Test Database Setup:**
```sql
-- Create test database
CREATE DATABASE mcp_test;

-- Initialize schemas (tasks, id_registry, id_reservations)
-- Use same schema as production but isolated database
```

**Step 2: Implement Test Framework**

Use pytest for integration test framework:

```python
# tests/integration/test_e2e_workflows.py

import pytest
from pathlib import Path
import requests

# Test configuration
MCP_SERVER_URL = "http://localhost:3000"
TEST_DATA_DIR = Path("tests/integration/test_data")
TEST_CONFIG_FILE = ".mcp/config.test.json"

@pytest.fixture(scope="session")
def mcp_server():
    """Ensure MCP Server running before tests"""
    response = requests.get(f"{MCP_SERVER_URL}/health")
    assert response.status_code == 200, "MCP Server not running"
    yield MCP_SERVER_URL

@pytest.fixture(scope="session")
def test_database():
    """Setup test database, yield, cleanup after tests"""
    # Setup: Create test database, initialize schemas
    # Yield: Provide database connection
    # Cleanup: Drop test database
    pass

@pytest.fixture(scope="function")
def test_config():
    """Create test configuration file for each test"""
    config = {
        "use_mcp_framework": True,
        "mcp_server_url": MCP_SERVER_URL
    }
    with open(TEST_CONFIG_FILE, "w") as f:
        json.dump(config, f)
    yield config
    # Cleanup: Remove test config file
    os.remove(TEST_CONFIG_FILE)
```

**Step 3: Implement 10 Integration Test Workflows**

**Workflow 1: Generate Product Vision from Business Research**

```python
def test_workflow_01_generate_product_vision(mcp_server, test_database, test_config):
    """
    Test: Generate Product Vision (VIS-001) from business research
    Validates: MCP resources (templates), MCP prompts (product-vision-generator),
               MCP tools (validate_artifact, store_artifact)
    """
    # Setup: Create test business research artifact
    business_research = TEST_DATA_DIR / "test_business_research.md"
    assert business_research.exists()

    # Execute: Call product-vision-generator via MCP prompt
    # (Simulated execution - actual test would invoke Claude Code with test inputs)
    response = requests.post(
        f"{MCP_SERVER_URL}/prompts/generator/product-vision",
        json={"inputs": {"business_research": business_research.read_text()}}
    )
    assert response.status_code == 200
    vision_content = response.json()["output"]

    # Execute: Validate artifact via MCP tool
    validation_response = requests.post(
        f"{MCP_SERVER_URL}/tools/validate_artifact",
        json={
            "artifact_content": vision_content,
            "checklist_id": "product_vision_validation_v1"
        }
    )
    assert validation_response.status_code == 200
    validation_result = validation_response.json()
    assert validation_result["passed"] == True

    # Assert: Product Vision artifact contains required sections
    assert "## Metadata" in vision_content
    assert "## Vision Statement" in vision_content
    assert "VIS-001" in vision_content  # Artifact ID

    # Cleanup: Delete test artifact
```

**Workflow 2: Generate Initiative from Product Vision**

```python
def test_workflow_02_generate_initiative(mcp_server, test_database, test_config):
    """
    Test: Generate Initiative (INIT-001) from Product Vision
    Validates: MCP resources (templates), MCP prompts (initiative-generator),
               MCP tools (resolve_artifact_path, get_next_available_id, validate_artifact)
    """
    # Setup: Create test Product Vision artifact
    product_vision = TEST_DATA_DIR / "VIS-001_test_vision_v1.md"
    assert product_vision.exists()

    # Execute: Get next available Initiative ID
    id_response = requests.get(
        f"{MCP_SERVER_URL}/tools/get_next_available_id",
        params={"artifact_type": "INIT", "project_id": "test-project"}
    )
    assert id_response.status_code == 200
    next_id = id_response.json()["next_id"]
    assert next_id == "INIT-001"

    # Execute: Call initiative-generator via MCP prompt
    response = requests.post(
        f"{MCP_SERVER_URL}/prompts/generator/initiative",
        json={"inputs": {"product_vision": product_vision.read_text()}}
    )
    assert response.status_code == 200
    initiative_content = response.json()["output"]

    # Execute: Validate artifact
    validation_response = requests.post(
        f"{MCP_SERVER_URL}/tools/validate_artifact",
        json={
            "artifact_content": initiative_content,
            "checklist_id": "initiative_validation_v1"
        }
    )
    assert validation_response.status_code == 200
    assert validation_response.json()["passed"] == True

    # Assert: Initiative artifact contains required metadata
    assert "INIT-001" in initiative_content
    assert "Parent Vision: VIS-001" in initiative_content

    # Cleanup: Delete test artifact
```

**Workflow 3-7:** Similar structure for Epic, PRD, HLS, Backlog Story, Tech Spec generation

**Workflow 8: Refine Epic (v1 → v2) based on critique**

```python
def test_workflow_08_refine_epic(mcp_server, test_database, test_config):
    """
    Test: Refine Epic (EPIC-000 v1 → v2) based on critique
    Validates: MCP prompts (epic-generator with refinement mode),
               MCP tools (validate_artifact for v2)
    """
    # Setup: Create test Epic v1 and critique file
    epic_v1 = TEST_DATA_DIR / "EPIC-000_test_epic_v1.md"
    critique = TEST_DATA_DIR / "EPIC-000_v1_critique.md"
    assert epic_v1.exists() and critique.exists()

    # Execute: Call epic-generator with refinement inputs (v1 + critique)
    response = requests.post(
        f"{MCP_SERVER_URL}/prompts/generator/epic",
        json={
            "inputs": {
                "epic_v1": epic_v1.read_text(),
                "critique": critique.read_text()
            },
            "mode": "refine",
            "version": 2
        }
    )
    assert response.status_code == 200
    epic_v2_content = response.json()["output"]

    # Execute: Validate Epic v2
    validation_response = requests.post(
        f"{MCP_SERVER_URL}/tools/validate_artifact",
        json={
            "artifact_content": epic_v2_content,
            "checklist_id": "epic_validation_v1"
        }
    )
    assert validation_response.status_code == 200
    assert validation_response.json()["passed"] == True

    # Assert: v2 artifact references v1 and incorporates critique feedback
    assert "v2" in epic_v2_content
    assert "Based on critique feedback" in epic_v2_content or "Version History" in epic_v2_content

    # Cleanup: Delete test artifacts
```

**Workflow 9-10:** Similar structure for PRD refinement and PRD validation

**Step 4: Integration Test Execution**

Run integration tests:

```bash
# Start MCP Server and Task Tracking microservice with test configuration
task mcp-server-start-test
task task-tracking-start-test

# Run integration tests
pytest tests/integration/test_e2e_workflows.py -v

# Cleanup
task mcp-server-stop-test
task task-tracking-stop-test
```

**Step 5: Continuous Integration (CI) Setup**

Add integration tests to CI pipeline (GitHub Actions or similar):

```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests

on: [push, pull_request]

jobs:
  integration-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: uv sync

      - name: Start MCP Server (test mode)
        run: task mcp-server-start-test

      - name: Start Task Tracking microservice (test mode)
        run: task task-tracking-start-test

      - name: Run integration tests
        run: pytest tests/integration/test_e2e_workflows.py -v

      - name: Cleanup
        if: always()
        run: |
          task mcp-server-stop-test
          task task-tracking-stop-test
```

**References to Implementation Standards:**
- patterns-testing.md: Follow testing patterns (pytest fixtures, test data management, assertion patterns)
- patterns-tooling.md: Use Taskfile commands for test execution (`task test-integration`)

### Technical Tasks
- [ ] Create test infrastructure (test database, test configuration, test data directory)
- [ ] Implement pytest fixtures (mcp_server, test_database, test_config)
- [ ] Implement Workflow 1: Generate Product Vision
- [ ] Implement Workflow 2: Generate Initiative
- [ ] Implement Workflow 3: Generate Epic
- [ ] Implement Workflow 4: Generate PRD
- [ ] Implement Workflow 5: Generate High-Level Story
- [ ] Implement Workflow 6: Generate Backlog Story
- [ ] Implement Workflow 7: Generate Tech Spec
- [ ] Implement Workflow 8: Refine Epic (v1 → v2)
- [ ] Implement Workflow 9: Refine PRD (v1 → v2)
- [ ] Implement Workflow 10: Validate PRD (26-criterion checklist)
- [ ] Create test data artifacts (business research, Product Vision v1, Epic v1, critique files)
- [ ] Add integration tests to CI pipeline (GitHub Actions)
- [ ] Document test execution instructions
- [ ] Validate test suite execution time (<10 minutes)

## Acceptance Criteria

### Scenario 1: All 10 Workflows Pass
**Given** MCP Server and Task Tracking microservice running with test configuration
**When** integration test suite executes
**Then** all 10 workflow tests pass (100% pass rate)

### Scenario 2: MCP Resources Loaded Successfully
**Given** Workflow 1 (Product Vision generation) executes
**When** MCP resource requested (product-vision-template)
**Then** MCP Server returns template content, artifact generated with required sections

### Scenario 3: MCP Prompts Executed Successfully
**Given** Workflow 3 (Epic generation) executes
**When** MCP prompt `mcp://prompts/generator/epic` called
**Then** MCP Server returns epic-generator.xml content, artifact generated successfully

### Scenario 4: MCP Tools Executed Successfully
**Given** Workflow 10 (PRD validation) executes
**When** `validate_artifact` tool called with PRD content and checklist ID
**Then** MCP tool returns validation results (24/26 automated criteria evaluated, 2/26 manual review flags)

### Scenario 5: Task Tracking Integration Validated
**Given** Workflow 2 (Initiative generation) executes
**When** `get_next_available_id` tool called for artifact type INIT
**Then** Task Tracking microservice returns next ID (INIT-001), ID recorded in database

### Scenario 6: Test Suite Execution Time <10 Minutes
**Given** All 10 workflows implemented
**When** integration test suite executes
**Then** total execution time <10 minutes (average ~1 minute per workflow)

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Needed

**Rationale:**
- **Story Points:** 8 SP (DON'T SKIP threshold - exceeds 5 SP guideline)
- **Developer Count:** Single developer (test implementation focused)
- **Domain Span:** Cross-domain (testing infrastructure, MCP Server integration, Task Tracking microservice integration, test data management)
- **Complexity:** High - 10 separate workflow tests, each exercising multiple components (resources, prompts, tools, database)
- **Uncertainty:** Medium - Integration test behavior predictable but test data setup and fixture management adds complexity
- **Override Factors:** Cross-domain (multiple systems integrated), high story points (8 SP)

**Proposed Implementation Tasks:**

- **TASK-XXX:** Create test infrastructure and pytest fixtures (4-6 hours)
  - Setup test database, test configuration, pytest fixtures (mcp_server, test_database, test_config)
  - Create test data directory structure

- **TASK-YYY:** Implement Workflows 1-5 (artifact generation tests) (6-8 hours)
  - Test workflows: Product Vision, Initiative, Epic, PRD, High-Level Story generation
  - Validate MCP resources, prompts, tools for each workflow

- **TASK-ZZZ:** Implement Workflows 6-10 (advanced workflows - Tech Spec, refinement, validation) (6-8 hours)
  - Test workflows: Backlog Story, Tech Spec, Epic refinement, PRD refinement, PRD validation
  - Validate refinement mode and validation tool execution

- **TASK-AAA:** CI integration and documentation (2-4 hours)
  - Add integration tests to CI pipeline (GitHub Actions)
  - Document test execution instructions, troubleshooting guide
  - Validate test suite execution time (<10 minutes)

**Total Estimated Hours:** 18-26 hours (consistent with 8 SP estimate)

**Note:** TASK-XXX IDs should be pre-allocated in TODO.md during story planning. If no IDs allocated, list task descriptions only.

## Definition of Done
- [ ] Test infrastructure created (test database, test configuration, test data directory)
- [ ] Pytest fixtures implemented (mcp_server, test_database, test_config)
- [ ] All 10 workflow tests implemented and passing
- [ ] Test data artifacts created (business research, Product Vision v1, Epic v1, critique files)
- [ ] Integration tests added to CI pipeline (GitHub Actions)
- [ ] Test execution instructions documented
- [ ] Test suite execution time <10 minutes validated
- [ ] Code reviewed and approved
- [ ] Unit test coverage ≥80% for test fixtures and utilities
- [ ] Product Owner acceptance obtained

## Additional Information
**Suggested Labels:** testing, integration-testing, quality-assurance, ci-cd
**Estimated Story Points:** 8
**Dependencies:**
- **Depends On:** US-056 (MCP Resources), US-057 (MCP Prompts), US-058 (MCP Tools), US-059 (Backward Compatibility) - all orchestration components required
- **Depends On:** US-030 (MCP Resource Server), US-035 (Generators as MCP Prompts), US-040/042/043/044 (MCP Tools), US-050/051 (Task Tracking API) - all implementation components required
- **Blocks:** HLS-011 (Production Readiness) - integration testing validation required before production pilot
- **Related:** US-061 (Token Usage Measurement) - both validate MCP approach

## Open Questions & Implementation Uncertainties

**Q1: Should integration tests use real Claude Code CLI or simulate workflow execution?** [REQUIRES TECH LEAD]
- **Option A:** Use real Claude Code CLI (full integration, slower execution, harder to automate)
- **Option B:** Simulate workflow execution (call MCP Server APIs directly, faster, easier CI integration)
- **Recommendation:** Start with Option B (simulated execution) for faster iteration, add Option A (real CLI) for final validation before production pilot

**Q2: Should test database be ephemeral (created/destroyed per test run) or persistent?** [REQUIRES TECH LEAD]
- **Option A:** Ephemeral database (clean state per run, slower setup)
- **Option B:** Persistent database (faster setup, requires cleanup logic)
- **Recommendation:** Option A (ephemeral) for CI environment, Option B (persistent) for local development

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md` (§Appendix A: Token Cost Baseline Measurement Plan)
- **Parent HLS:** `/artifacts/hls/HLS-010_claude_orchestration_integration_testing_v2.md`
- **Parent Epic:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`
- **Related Stories:** US-056/057/058/059 (CLAUDE.md Orchestration), US-030 (MCP Resources), US-035 (MCP Prompts), US-040/042/043/044 (MCP Tools), US-050/051 (Task Tracking API), US-061 (Token Usage Measurement), US-062 (Regression Testing)

## Version History
- **v1 (2025-10-18):** Initial version
