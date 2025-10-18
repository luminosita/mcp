# User Story: Integration Testing for All Tools

## Metadata
- **Story ID:** US-047
- **Title:** Integration Testing for All Tools
- **Type:** Feature
- **Status:** Draft
- **Priority:** Must-have (validates all MCP tools work correctly together, critical for quality)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-008 (MCP Tools - Validation and Path Resolution)
- **Functional Requirements Covered:** NFR-Maintainability-01
- **Informed By Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Non-Functional Requirements - NFR-Maintainability-01
- **Functional Requirements Coverage:**
  - **NFR-Maintainability-01:** All MCP tools (validation, path resolution) SHALL have unit test coverage ≥80% and integration test coverage ≥60%

**Parent High-Level Story:** [HLS-008: MCP Tools - Validation and Path Resolution]
- **Link:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 8: Integration Testing for All Tools

## User Story
As a Framework Maintainer, I want comprehensive integration tests for all MCP tools, so that I have confidence that tools work correctly together in real-world workflows.

## Description
MCP tools (validate_artifact, resolve_artifact_path, store_artifact, add_task) will have unit tests (≥80% coverage per NFR-Maintainability-01), but unit tests cannot validate:
1. **Tool Integration:** Tools called in sequence work correctly together (e.g., generate artifact → validate → store → add tasks)
2. **End-to-End Workflows:** Complete SDLC workflows execute successfully (e.g., generate PRD → validate → decompose to HLS → add HLS tasks)
3. **Error Propagation:** Errors in upstream tools handled gracefully by downstream tools
4. **Performance:** Tool execution meets latency targets in realistic scenarios (not just isolated unit tests)

This story implements integration test suite covering:
1. **Single Tool Integration Tests:** Each tool tested with real dependencies (e.g., validate_artifact with real JSON checklist files, resolve_artifact_path with real artifact directory structure)
2. **Multi-Tool Workflow Tests:** Tools called in sequence to validate end-to-end scenarios:
   - **Workflow 1:** validate_artifact → (if passed) store_artifact
   - **Workflow 2:** resolve_artifact_path → (load artifact) → validate_artifact
   - **Workflow 3:** validate_artifact → (if sub-artifacts required) add_task
3. **Error Handling Tests:** Simulate failures and verify graceful error handling:
   - Validation failure → do not store artifact
   - Path resolution failure → return clear error (not found vs. multiple matches)
   - API failure (add_task) → retry logic works correctly
4. **Performance Tests:** Verify all tools meet NFR-Performance-02 (<500ms p95 latency) in realistic scenarios

Integration test coverage target: ≥60% (per NFR-Maintainability-01).

## Implementation Research References

**Primary Research Document:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

**Technical Patterns Applied:**
- **§Testing Strategy:** Integration tests with pytest-asyncio for async tool testing (ref: Implementation Research - testing patterns)
- **§Fixture Patterns:** Use pytest fixtures for test data (sample artifacts, checklists, etc.)

No direct reference to integration testing in Implementation Research (general testing patterns apply).

## Functional Requirements
1. Implement integration tests for 4 MCP tools:
   - `validate_artifact`
   - `resolve_artifact_path`
   - `store_artifact`
   - `add_task`
2. Single tool integration tests (with real dependencies):
   - **validate_artifact:** Load real JSON checklist from `resources/validation/`, validate sample PRD artifact
   - **resolve_artifact_path:** Use real artifact directory structure, resolve paths for Epic, PRD, HLS, US
   - **store_artifact:** Write artifact to temp directory, verify file created with correct content
   - **add_task:** Mock Task Tracking API, verify API called with correct payload
3. Multi-tool workflow tests:
   - **Workflow 1 (Validate + Store):** Generate artifact → validate → if passed, store → verify storage successful
   - **Workflow 2 (Resolve + Validate):** Resolve artifact path → load artifact → validate → verify validation results
   - **Workflow 3 (Validate + Add Tasks):** Validate artifact with sub-artifact requirements → add tasks → verify tasks added to queue
4. Error handling tests:
   - Validation failure → store_artifact not called
   - Path resolution not_found error → downstream tool receives error, handles gracefully
   - add_task API failure → retry logic executes (3 retries with exponential backoff)
5. Performance tests:
   - Validate all tools meet <500ms p95 latency target (run 100 iterations, measure p95)
   - Workflow tests meet combined latency targets (e.g., validate + store <1000ms)
6. Integration test coverage:
   - Measure coverage with pytest-cov
   - Target: ≥60% integration test coverage (per NFR-Maintainability-01)

## Non-Functional Requirements
- **Coverage:** Integration test coverage ≥60% (per NFR-Maintainability-01)
- **Reliability:** Tests pass consistently (no flaky tests due to timing issues)
- **Maintainability:** Tests use fixtures for test data (easy to add new test cases)
- **Performance:** Test suite executes in <5 minutes (fast enough for CI/CD pipeline)
- **Clarity:** Test names clearly describe scenario (e.g., `test_validate_then_store_successful_workflow`)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** Follow established testing patterns from Implementation Research. Supplement with story-specific integration test structure.

**References to Implementation Standards:**
- **prompts/CLAUDE/python/patterns-tooling.md:** Use Taskfile commands (`task test`, `task test-integration`, `task coverage`)
- **prompts/CLAUDE/python/patterns-testing.md:** Testing patterns (pytest, pytest-asyncio, fixtures, 80% unit coverage, 60% integration coverage)
- **prompts/CLAUDE/python/patterns-typing.md:** Type hints in tests for clarity

### Implementation Guidance

**Story-Specific Technical Approach:**

1. **Integration Test Structure:**
   ```
   tests/
     integration/
       test_validate_artifact_integration.py      # validate_artifact with real checklists
       test_resolve_artifact_path_integration.py   # resolve_artifact_path with real artifacts
       test_store_artifact_integration.py          # store_artifact with real file I/O
       test_add_task_integration.py                # add_task with mocked API
       test_multi_tool_workflows.py                # Combined tool workflows
       test_error_handling.py                      # Error scenarios
       test_performance.py                         # Performance benchmarks
       fixtures/
         sample_artifacts/                         # Sample Epic, PRD, HLS artifacts
         validation_checklists/                    # Sample JSON checklists
         conftest.py                               # Shared fixtures
   ```

2. **Single Tool Integration Tests (Examples):**
   ```python
   # tests/integration/test_validate_artifact_integration.py
   import pytest
   from src.mcp_server.tools.validate_artifact import validate_artifact, ValidateArtifactInput

   @pytest.mark.asyncio
   async def test_validate_prd_with_real_checklist(prd_sample_artifact, prd_checklist_path):
       """Validates PRD artifact using real JSON checklist from resources/"""
       # Arrange
       input_params = ValidateArtifactInput(
           artifact_content=prd_sample_artifact,
           checklist_id="prd_validation_v1"
       )

       # Act
       result = await validate_artifact(input_params)

       # Assert
       assert result.passed is True
       assert result.automated_pass_rate == "24/24"
       assert result.manual_review_required == 2
       assert len(result.results) == 26

   @pytest.mark.asyncio
   async def test_validate_epic_missing_section_fails(epic_sample_artifact_missing_risks):
       """Validates Epic artifact with missing Risks section (should fail)"""
       # Arrange
       input_params = ValidateArtifactInput(
           artifact_content=epic_sample_artifact_missing_risks,
           checklist_id="epic_validation_v1"
       )

       # Act
       result = await validate_artifact(input_params)

       # Assert
       assert result.passed is False
       assert any(
           r.id == "CQ-02" and r.passed is False and "Missing sections: Risks" in r.details
           for r in result.results
       )
   ```

3. **Multi-Tool Workflow Tests:**
   ```python
   # tests/integration/test_multi_tool_workflows.py
   import pytest
   from src.mcp_server.tools import validate_artifact, store_artifact

   @pytest.mark.asyncio
   async def test_validate_then_store_successful_workflow(prd_sample_artifact, prd_metadata):
       """Workflow: Generate artifact → Validate → Store (happy path)"""
       # Step 1: Validate artifact
       validation_input = ValidateArtifactInput(
           artifact_content=prd_sample_artifact,
           checklist_id="prd_validation_v1"
       )
       validation_result = await validate_artifact(validation_input)

       assert validation_result.passed is True, "Validation should pass before storage"

       # Step 2: Store artifact (only if validation passed)
       storage_input = StoreArtifactInput(
           artifact_content=prd_sample_artifact,
           metadata=prd_metadata
       )
       storage_result = await store_artifact(storage_input)

       # Assert storage successful
       assert storage_result.success is True
       assert storage_result.artifact_id == "PRD-006"
       assert Path(storage_result.storage_path).exists()

   @pytest.mark.asyncio
   async def test_validation_failure_prevents_storage(invalid_prd_artifact, prd_metadata):
       """Workflow: Validate (fails) → Do NOT store artifact"""
       # Step 1: Validate artifact (expect failure)
       validation_input = ValidateArtifactInput(
           artifact_content=invalid_prd_artifact,
           checklist_id="prd_validation_v1"
       )
       validation_result = await validate_artifact(validation_input)

       assert validation_result.passed is False, "Validation should fail for invalid artifact"

       # Step 2: Do NOT call store_artifact (conditional logic in workflow)
       # Verify: No storage occurred
       assert not Path("shared_artifacts/prds/PRD-006_v1.md").exists()
   ```

4. **Error Handling Tests:**
   ```python
   # tests/integration/test_error_handling.py
   import pytest
   from src.mcp_server.tools import resolve_artifact_path, add_task

   @pytest.mark.asyncio
   async def test_resolve_artifact_path_not_found_error():
       """Path resolution returns not_found error for non-existent artifact"""
       # Arrange
       input_params = ResolveArtifactPathInput(
           pattern="artifacts/epics/EPIC-{id}*_v{version}.md",
           variables={"id": "999", "version": "1"}
       )

       # Act
       result = await resolve_artifact_path(input_params)

       # Assert
       assert result.success is False
       assert result.error == "not_found"
       assert "No files match pattern" in result.message
       assert result.pattern_resolved == "artifacts/epics/EPIC-999*_v1.md"

   @pytest.mark.asyncio
   async def test_add_task_api_retry_on_transient_failure(mock_task_api_transient_failure):
       """add_task tool retries on transient API failure (503 error)"""
       # Arrange: Mock API returns 503 twice, then succeeds
       mock_task_api_transient_failure.configure_responses([503, 503, 201])

       input_params = AddTaskInput(
           tasks=[TaskMetadata(artifact_id="HLS-006", artifact_type="hls", ...)]
       )

       # Act
       result = await add_task(input_params)

       # Assert
       assert result.success is True
       assert result.tasks_added == 1
       assert mock_task_api_transient_failure.call_count == 3  # 2 retries + success
   ```

5. **Performance Tests:**
   ```python
   # tests/integration/test_performance.py
   import pytest
   import time
   import statistics

   @pytest.mark.asyncio
   async def test_validate_artifact_latency_p95_target(prd_sample_artifact):
       """Validates validate_artifact meets <500ms p95 latency target"""
       # Run tool 100 times
       latencies = []
       for _ in range(100):
           start_time = time.time()
           await validate_artifact(ValidateArtifactInput(
               artifact_content=prd_sample_artifact,
               checklist_id="prd_validation_v1"
           ))
           latencies.append((time.time() - start_time) * 1000)  # ms

       # Calculate p95 latency
       p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile

       # Assert meets target
       assert p95_latency < 500, f"p95 latency ({p95_latency}ms) exceeds 500ms target"

   @pytest.mark.asyncio
   async def test_multi_tool_workflow_combined_latency(prd_sample_artifact, prd_metadata):
       """Validates validate + store workflow meets combined latency target <1000ms"""
       start_time = time.time()

       # Validate
       validation_result = await validate_artifact(ValidateArtifactInput(
           artifact_content=prd_sample_artifact,
           checklist_id="prd_validation_v1"
       ))

       # Store
       if validation_result.passed:
           storage_result = await store_artifact(StoreArtifactInput(
               artifact_content=prd_sample_artifact,
               metadata=prd_metadata
           ))

       duration_ms = (time.time() - start_time) * 1000

       assert duration_ms < 1000, f"Combined workflow latency ({duration_ms}ms) exceeds 1000ms target"
   ```

6. **Fixtures (Sample Artifacts and Checklists):**
   ```python
   # tests/integration/fixtures/conftest.py
   import pytest
   from pathlib import Path

   @pytest.fixture
   def prd_sample_artifact():
       """Sample PRD artifact with all required sections"""
       artifact_path = Path(__file__).parent / "sample_artifacts" / "PRD-006_v1.md"
       return artifact_path.read_text()

   @pytest.fixture
   def epic_sample_artifact_missing_risks():
       """Sample Epic artifact missing Risks section (for failure testing)"""
       artifact_path = Path(__file__).parent / "sample_artifacts" / "EPIC-006_missing_risks.md"
       return artifact_path.read_text()

   @pytest.fixture
   def prd_metadata():
       """Sample PRD artifact metadata"""
       return ArtifactMetadata(
           artifact_id="PRD-006",
           artifact_type="prd",
           version=1,
           status="Draft",
           parent_id="EPIC-006",
           title="MCP Server SDLC Framework Integration"
       )

   @pytest.fixture
   def prd_checklist_path():
       """Path to PRD validation checklist JSON"""
       return Path("resources/validation/prd_validation_v1.json")
   ```

7. **Running Integration Tests:**
   ```bash
   # Run all integration tests
   task test-integration

   # Run with coverage
   task coverage-integration

   # Run specific test file
   pytest tests/integration/test_validate_artifact_integration.py -v

   # Run performance tests only
   pytest tests/integration/test_performance.py -v -m performance
   ```

8. **Testing Strategy:**
   - Unit tests: Each tool's internal logic (80% coverage minimum)
   - Integration tests: Tools with real dependencies and multi-tool workflows (60% coverage minimum)
   - Performance tests: Verify latency targets met in realistic scenarios
   - Regression tests: Prevent future changes from breaking existing functionality

### Technical Tasks
- [ ] Create integration test directory structure
- [ ] Implement validate_artifact integration tests (with real checklists)
- [ ] Implement resolve_artifact_path integration tests (with real artifacts)
- [ ] Implement store_artifact integration tests (with real file I/O)
- [ ] Implement add_task integration tests (with mocked API)
- [ ] Implement multi-tool workflow tests (3 workflows)
- [ ] Implement error handling tests (3 error scenarios)
- [ ] Implement performance tests (validate latency targets)
- [ ] Create fixtures for sample artifacts and checklists
- [ ] Configure pytest-cov for coverage measurement
- [ ] Add Taskfile commands for integration tests
- [ ] Document integration test patterns and conventions

## Acceptance Criteria

### Scenario 1: validate_artifact integration test with real checklist passes
**Given** Sample PRD artifact with all required sections
**When** Integration test runs validate_artifact with real `prd_validation_v1.json` checklist
**Then** Test passes (artifact validates successfully)
**And** Coverage report shows validate_artifact integration coverage ≥60%

### Scenario 2: Multi-tool workflow test (validate + store) passes
**Given** Sample PRD artifact
**When** Integration test runs validate → store workflow
**Then** Validation passes
**And** Artifact stored to `shared_artifacts/prds/PRD-006_v1.md`
**And** Storage path confirmed in result
**And** Test passes

### Scenario 3: Error handling test (validation failure prevents storage) passes
**Given** Invalid PRD artifact (missing required section)
**When** Integration test runs validate → (conditional) store workflow
**Then** Validation fails
**And** store_artifact NOT called (conditional logic prevents storage)
**And** No artifact file created
**And** Test passes

### Scenario 4: Performance test validates <500ms p95 latency
**Given** Sample PRD artifact
**When** Performance test runs validate_artifact 100 times
**Then** p95 latency calculated
**And** p95 latency <500ms
**And** Test passes

### Scenario 5: Integration test coverage ≥60%
**Given** All integration tests implemented
**When** Coverage measured with pytest-cov
**Then** Integration test coverage ≥60% (per NFR-Maintainability-01)
**And** Coverage report generated in HTML format

### Scenario 6: All integration tests pass in CI/CD pipeline
**Given** Integration test suite implemented
**When** CI/CD pipeline runs tests
**Then** All tests pass (no flaky tests)
**And** Test execution completes in <5 minutes
**And** Coverage thresholds met (unit ≥80%, integration ≥60%)

### Scenario 7: Integration tests use fixtures for test data
**Given** Sample artifacts and checklists needed for tests
**When** Tests reference fixtures (e.g., `prd_sample_artifact` fixture)
**Then** Fixtures loaded from `tests/integration/fixtures/`
**And** New test cases easily added by reusing fixtures

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Not Needed (Single Sprint-Ready Task)

**Rationale:**
- **Story Points:** 5 SP (at threshold - CONSIDER SKIPPING per decision matrix)
- **Developer Count:** Single developer (QA engineer or developer writing tests)
- **Domain Span:** Single domain (testing/QA)
- **Complexity:** Low-moderate - writing integration tests with pytest, well-defined test scenarios
- **Uncertainty:** Low - clear test cases, existing tools to test against
- **Override Factors:** None (testing is straightforward, not complex enough to require decomposition)

Per SDLC Section 11.6 Decision Matrix: "5 SP, single developer, low-moderate complexity → SKIP (Straightforward test implementation)".

**No task decomposition needed.** Story can be completed as single unit of work in 2-3 days.

## Definition of Done
- [ ] Integration test directory structure created
- [ ] validate_artifact integration tests implemented (real checklists)
- [ ] resolve_artifact_path integration tests implemented (real artifacts)
- [ ] store_artifact integration tests implemented (real file I/O)
- [ ] add_task integration tests implemented (mocked API)
- [ ] Multi-tool workflow tests implemented (3 workflows)
- [ ] Error handling tests implemented (3 error scenarios)
- [ ] Performance tests implemented (validate latency targets)
- [ ] Fixtures created for sample artifacts and checklists
- [ ] pytest-cov configured for coverage measurement
- [ ] Taskfile commands added for integration tests
- [ ] Integration test coverage ≥60% (measured with pytest-cov)
- [ ] All integration tests passing in local environment
- [ ] All integration tests passing in CI/CD pipeline
- [ ] Integration test patterns and conventions documented
- [ ] Product Owner approval obtained

## Additional Information
**Suggested Labels:** testing, integration-tests, quality
**Estimated Story Points:** 5
**Dependencies:**
- **Depends On:** US-040, US-041, US-042, US-043, US-044 (all 5 MCP tools must exist)
- **Blocks:** None (quality validation, does not block other features)
- **Related:** NFR-Maintainability-01 (unit test coverage ≥80%, integration test coverage ≥60%)

**Related PRD Section:** PRD-006 §Non-Functional Requirements - NFR-Maintainability-01

## Open Questions & Implementation Uncertainties

**No open implementation questions.** Integration test approach and coverage targets clearly defined.

Technical implementation details (pytest structure, fixtures, multi-tool workflows, performance tests) defined in Implementation Guidance section above.

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md` (testing patterns)
- **Related Stories:** US-040, US-041, US-042, US-043, US-044 (all 5 MCP tools)
