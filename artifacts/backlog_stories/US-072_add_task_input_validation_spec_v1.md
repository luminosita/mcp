# User Story: add_task Input Validation Test Specification

## Metadata
- **Story ID:** US-072
- **Title:** add_task Input Validation Test Specification
- **Type:** Documentation / Test Specification
- **Status:** Draft (v1)
- **Priority:** Should-have (documents validation requirements for US-044 v3, ensures comprehensive test coverage)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-008 (MCP Tools - Validation and Path Resolution)
- **Functional Requirements Covered:** FR-24 (validation requirements)
- **Informed By Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Functional Requirements - FR-24 (task validation requirements)

**Parent High-Level Story:** [HLS-008: MCP Tools - Validation and Path Resolution]
- **Link:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 10: add_task Input Validation Specification (NEW)

## User Story
As a QA Engineer, I want comprehensive test cases documenting add_task input validation requirements, so that I can verify all validation rules are correctly implemented and tested.

## Description
US-044 v3 implements comprehensive input validation for add_task tool with 5 Pydantic validators. This story documents validation requirements and test cases to ensure complete test coverage.

**Implementation Note:** Input validation logic is implemented in US-044 v3 (`TaskMetadata` and `AddTaskInput` Pydantic models). This story provides test specification only.

**Validation Rules Implemented in US-044 v3:**
1. **validate_inputs_non_empty:** Inputs list must contain at least one GeneratorInput
2. **validate_mandatory_inputs_present:** At least one mandatory input required
3. **validate_resource_uris_format:** All MCP resource URIs must match `file:///workspace/...` pattern
4. **validate_resource_paths_exist:** All resource paths must exist in filesystem
5. **validate_artifact_inputs_approved:** Artifact inputs must have status="Approved", research inputs status="Finalized"
6. **validate_no_duplicate_artifact_ids:** No duplicate artifact_id in batch (AddTaskInput validator)

This story documents:
1. Test cases for each validation rule (happy path + error cases)
2. Edge cases (e.g., mixed mandatory/recommended inputs, partial file system availability)
3. Performance test requirements (validation must not significantly impact <500ms p95 latency target)

## Functional Requirements
1. Document 30+ test cases covering all validation rules
2. For each validation rule, specify:
   - Happy path test case (validation passes)
   - Error path test cases (validation fails with expected error message)
   - Edge cases (boundary conditions, unusual but valid inputs)
3. Document expected error messages for each validation failure
4. Document performance requirements (validation overhead <50ms per task)
5. Document integration test requirements (validation with real filesystem, mocked filesystem)

## Test Cases Specification

### Test Group 1: validate_inputs_non_empty

**TC-1.1: Happy Path - Single input present**
- **Input:** TaskMetadata with 1 GeneratorInput
- **Expected:** Validation passes
- **Error:** None

**TC-1.2: Error Path - Empty inputs list**
- **Input:** TaskMetadata with `inputs=[]`
- **Expected:** ValidationError
- **Error Message:** "inputs list must contain at least one GeneratorInput"

### Test Group 2: validate_mandatory_inputs_present

**TC-2.1: Happy Path - Mandatory input present**
- **Input:** TaskMetadata with 1 mandatory input (classification="mandatory")
- **Expected:** Validation passes
- **Error:** None

**TC-2.2: Happy Path - Multiple mandatory inputs**
- **Input:** TaskMetadata with 2 mandatory inputs, 1 recommended input
- **Expected:** Validation passes
- **Error:** None

**TC-2.3: Error Path - No mandatory inputs**
- **Input:** TaskMetadata with only recommended inputs (classification="recommended")
- **Expected:** ValidationError
- **Error Message:** "At least one mandatory input required"

**TC-2.4: Edge Case - Conditional inputs only**
- **Input:** TaskMetadata with only conditional inputs (classification="conditional")
- **Expected:** ValidationError
- **Error Message:** "At least one mandatory input required"

### Test Group 3: validate_resource_uris_format

**TC-3.1: Happy Path - Valid file:/// URI**
- **Input:** GeneratorInput with `mcp_resource_uri="file:///workspace/artifacts/prds/PRD-006_v3.md"`
- **Expected:** Validation passes
- **Error:** None

**TC-3.2: Error Path - Invalid URI scheme (http)**
- **Input:** GeneratorInput with `mcp_resource_uri="http://localhost/artifacts/PRD-006.md"`
- **Expected:** ValidationError
- **Error Message:** "Invalid MCP resource URI format: http://localhost/artifacts/PRD-006.md. Expected: file:///workspace/..."

**TC-3.3: Error Path - Relative path (no scheme)**
- **Input:** GeneratorInput with `mcp_resource_uri="artifacts/prds/PRD-006_v3.md"`
- **Expected:** ValidationError
- **Error Message:** "Invalid MCP resource URI format: artifacts/prds/PRD-006_v3.md. Expected: file:///workspace/..."

**TC-3.4: Edge Case - file:// (missing third slash)**
- **Input:** GeneratorInput with `mcp_resource_uri="file://workspace/artifacts/PRD-006.md"`
- **Expected:** ValidationError
- **Error Message:** "Invalid MCP resource URI format: file://workspace/artifacts/PRD-006.md. Expected: file:///workspace/..."

### Test Group 4: validate_resource_paths_exist

**TC-4.1: Happy Path - File exists**
- **Input:** GeneratorInput with `resource_path="artifacts/prds/PRD-006_v3.md"` (file exists)
- **Expected:** Validation passes
- **Error:** None

**TC-4.2: Error Path - File not found**
- **Input:** GeneratorInput with `resource_path="artifacts/prds/PRD-999_v1.md"` (file does not exist)
- **Expected:** ValidationError
- **Error Message:** "Input file not found: artifacts/prds/PRD-999_v1.md (input name: prd, artifact_id: PRD-999)"

**TC-4.3: Error Path - Directory instead of file**
- **Input:** GeneratorInput with `resource_path="artifacts/prds/"` (directory, not file)
- **Expected:** ValidationError
- **Error Message:** "Input file not found: artifacts/prds/ (input name: prd, artifact_id: N/A)"

**TC-4.4: Edge Case - Symbolic link to file**
- **Input:** GeneratorInput with `resource_path="artifacts/prds/PRD-006_latest.md"` (symlink to PRD-006_v3.md)
- **Expected:** Validation passes (symlinks resolved by pathlib.Path.exists())
- **Error:** None

### Test Group 5: validate_artifact_inputs_approved

**TC-5.1: Happy Path - Artifact input approved**
- **Input:** GeneratorInput with `artifact_id="PRD-006"`, `status="Approved"`
- **Expected:** Validation passes
- **Error:** None

**TC-5.2: Happy Path - Research input finalized**
- **Input:** GeneratorInput with `artifact_id="N/A"` (research), `status="Finalized"`
- **Expected:** Validation passes
- **Error:** None

**TC-5.3: Error Path - Artifact input not approved (Draft)**
- **Input:** GeneratorInput with `artifact_id="PRD-006"`, `status="Draft"`
- **Expected:** ValidationError
- **Error Message:** "Input artifact PRD-006 must be Approved (current status: Draft)"

**TC-5.4: Error Path - Research input not finalized**
- **Input:** GeneratorInput with `artifact_id="N/A"` (research), `status="Draft"`
- **Expected:** ValidationError
- **Error Message:** "Research input 'business_research' must have status='Finalized' (current status: Draft)"

**TC-5.5: Edge Case - Mixed statuses (Approved + Draft)**
- **Input:** TaskMetadata with 2 inputs: PRD-006 (Approved), EPIC-006 (Draft)
- **Expected:** ValidationError (fails on second input)
- **Error Message:** "Input artifact EPIC-006 must be Approved (current status: Draft)"

### Test Group 6: validate_no_duplicate_artifact_ids

**TC-6.1: Happy Path - Unique artifact_ids**
- **Input:** AddTaskInput with tasks=[HLS-012, HLS-013, HLS-014]
- **Expected:** Validation passes
- **Error:** None

**TC-6.2: Error Path - Duplicate artifact_id**
- **Input:** AddTaskInput with tasks=[HLS-012, HLS-013, HLS-012]
- **Expected:** ValidationError
- **Error Message:** "Duplicate artifact_id in batch: HLS-012"

**TC-6.3: Error Path - Multiple duplicates**
- **Input:** AddTaskInput with tasks=[HLS-012, HLS-013, HLS-012, HLS-013]
- **Expected:** ValidationError
- **Error Message:** "Duplicate artifact_id in batch: HLS-012, HLS-013"

### Test Group 7: Performance Requirements

**TC-7.1: Validation overhead - Single task**
- **Input:** AddTaskInput with 1 task (3 inputs: mandatory parent + 2 recommended research)
- **Expected:** Validation completes in <50ms
- **Measurement:** Time validation execution, assert duration < 50ms

**TC-7.2: Validation overhead - Batch (10 tasks)**
- **Input:** AddTaskInput with 10 tasks (each with 3 inputs)
- **Expected:** Validation completes in <200ms (<20ms per task)
- **Measurement:** Time validation execution, assert duration < 200ms

**TC-7.3: Validation overhead - Large batch (100 tasks)**
- **Input:** AddTaskInput with 100 tasks (each with 3 inputs)
- **Expected:** Validation completes in <1000ms (<10ms per task)
- **Measurement:** Time validation execution, assert duration < 1000ms

### Test Group 8: Integration Tests with Filesystem

**TC-8.1: Real filesystem - All files exist**
- **Setup:** Create temp directory with PRD-006_v3.md, business_research.md, implementation_research.md
- **Input:** TaskMetadata with inputs referencing temp directory files
- **Expected:** Validation passes
- **Teardown:** Remove temp directory

**TC-8.2: Real filesystem - Missing file**
- **Setup:** Create temp directory with only PRD-006_v3.md (missing research files)
- **Input:** TaskMetadata with inputs referencing missing files
- **Expected:** ValidationError ("Input file not found: ...")
- **Teardown:** Remove temp directory

**TC-8.3: Mocked filesystem - All files exist**
- **Setup:** Mock pathlib.Path.exists() to return True for all paths
- **Input:** TaskMetadata with inputs
- **Expected:** Validation passes
- **Teardown:** Unmock Path.exists()

**TC-8.4: Mocked filesystem - Selective file existence**
- **Setup:** Mock Path.exists() to return True for PRD-006, False for research files
- **Input:** TaskMetadata with inputs (PRD + research)
- **Expected:** ValidationError on research file check
- **Teardown:** Unmock Path.exists()

## Acceptance Criteria

### Scenario 1: All 30+ test cases documented
**Given** Test specification complete
**When** QA Engineer reviews document
**Then** 30+ test cases documented covering all 6 validation rules
**And** Each test case specifies: input, expected result, error message (if applicable)

### Scenario 2: Test cases implemented and passing
**Given** Test specification complete
**When** Developer implements test cases in pytest
**Then** All test cases passing
**And** Test coverage ≥95% for validation code (US-044 v3 TaskMetadata validators)

### Scenario 3: Performance tests validate overhead <50ms per task
**Given** Performance test cases TC-7.1, TC-7.2, TC-7.3 implemented
**When** Performance tests executed on CI/CD
**Then** All performance tests pass
**And** Validation overhead <50ms for single task, <20ms per task for batch

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Not Needed (Documentation Story)

**Rationale:**
- **Story Points:** 2 SP (documentation + test case writing, no implementation)
- **Developer Count:** Single QA engineer or developer
- **Domain Span:** Single domain (testing)
- **Complexity:** Low - document test cases, implement tests following specification
- **Uncertainty:** None - validation logic already implemented in US-044 v3

Per SDLC Section 11.6 Decision Matrix: "2 SP, single developer, low complexity → SKIP".

**No task decomposition needed.** Story can be completed as single unit of work in 1 day.

## Definition of Done
- [ ] 30+ test cases documented (all validation rules covered)
- [ ] Test case format: TC-X.Y with input, expected result, error message
- [ ] Performance test requirements documented (overhead <50ms per task)
- [ ] Integration test requirements documented (real filesystem + mocked filesystem)
- [ ] Test cases implemented in pytest (references US-044 v3 code)
- [ ] All test cases passing
- [ ] Test coverage ≥95% for validation code
- [ ] Performance tests passing (<50ms overhead)
- [ ] QA Engineer approval obtained

## Additional Information
**Suggested Labels:** testing, validation, documentation, quality-assurance
**Estimated Story Points:** 2 (documentation + test implementation)
**Dependencies:**
- **Depends On:** US-044 v3 (add_task implementation with validation logic)
- **Blocks:** None (quality assurance, doesn't block other features)

**Related PRD Section:** PRD-006 §Functional Requirements - FR-24 (task validation requirements)

## Decisions Made

**Decision 1: Document test specification separately from implementation (US-044 v3)**
- **Made:** During v1 planning (2025-10-20)
- **Rationale:** Separating test specification from implementation ensures comprehensive test coverage is explicitly documented and reviewed. Validates that US-044 v3 validators meet all requirements
- **Impact:**
  - US-044 v3 contains implementation (Pydantic validators)
  - US-072 contains test specification (test cases, acceptance criteria)
  - Clear separation of concerns (implementation vs. testing)
  - QA Engineer can review test spec independently

**Decision 2: Include performance test requirements (validation overhead <50ms)**
- **Made:** During v1 planning (2025-10-20)
- **Rationale:** Validation must not significantly impact add_task latency target (<500ms p95). Overhead <50ms ensures validation is <10% of total latency budget
- **Impact:**
  - Performance test cases TC-7.1, TC-7.2, TC-7.3 specify overhead limits
  - CI/CD must run performance tests to catch regressions
  - Validation code must be optimized (e.g., batch file existence checks)

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`
- **Implementation Story:** US-044 v3 (add_task with input validation - implementation)
- **Related Stories:** US-071 (approve_artifact - generates tasks with resolved inputs that must pass validation)
- **Feedback:** `/feedback/new_work_feedback.md` (validation requirements)
