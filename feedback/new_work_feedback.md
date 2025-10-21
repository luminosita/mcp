  Understanding of Request

  1. Enhance add_task Tool: Input Parameter Validation

  The add_task tool (US-044) must validate that input parameters in TaskMetadata satisfy the input requirements for the specific generator that will execute the task.

  Example:
  - Task to generate PRD-007 must include parent Epic ID (required input for PRD generator)
  - Task to generate US-040 must include parent HLS ID (required input for Backlog Story generator)

  ---
  2. New Tool: approve_artifact

  Create a new MCP tool that orchestrates the approval workflow:

  Input: artifact_id (e.g., "EPIC-006")

  Function:
  1. Load artifact from filesystem
  2. Update status: "Draft" → "Approved"
  3. Analyze artifact to determine required sub-artifacts
  4. Call add_task to create generation tasks for sub-artifacts
  5. Return approval result with list of tasks created

  Example Workflow:
  - Approve EPIC-006 → Detect PRD needed → Create task to generate PRD-007
  - Approve PRD-006 → Detect HLS subsections → Create tasks to generate FuncSpec + Backlog Stories

  ---
  3. Remove resolve_artifact_path Tool

  - US-042 (resolve_artifact_path tool) is obsolete
  - approve_artifact handles artifact path resolution internally
  - Update or remove related stories (US-047 integration tests)

  ---
  Assumptions (Please Confirm)

  A1: Artifact Status Lifecycle

  Correct

  ---

  A2: Sub-artifact Determination Rules

  Correct

  ---
  A3: HLS Consolidation Impact (CRITICAL)

  Depends on complexity. If FuncSpec required then Option A, if not then Option B

  ---
  A4: Version Handling

  Option A, approve latest version

  ---
  A5: Sub-artifact ID Assignment

  All sub-artifacts must be generated at the same time because of mutual dependencies and order of priority. Generated artifact does not have final IDs (EPIC-004, PRD-003), it only has placeholders (US-AAA, US-BBB, US-CCC). When artifact is approved, reserve_id_range is called, artifact is corrected with the proper sub-artifact IDs to reflect dependencies betweem sub-artifacts within parent artifact. Last step is to generate tasks (add_task) with those sub-artifact IDs

  ---
  A6: add_task Validation Scope

  All assumptions are correct. In addition, add_task has all inputs for a particular generator as MCP resource paths. That include business/implementation research, patterns (ex-`CLAUDE.md` files), HLS-XXX IDs (in case of FuncSpec or Backlog Story PRD is mandatory input, but HLS section ID must be also specified)

  ---
  A7: approve_artifact Output Schema

  Correct.

  ---
  A8: Approval Prerequisites

  No, all 4 steps need to be fullfiled.

  ---
  A9: Error Handling

  Correct

  ---
  A10: US-042 Removal Strategy

  Option B

  ---
  A11: New Stories to Create

  1. correct. It will be US-071 (US-048 id already used)
  2. correct. It will be US-072 (US-049 id already used)
  3. v3
  4. v3
  5. correct

  ---
  A12: Validation Against Generator Input Requirements

  Correct

  ---
  A13: Task Metadata Must Include Resolved Input Paths

  Each task created by add_task (or approve_artifact → add_task) must contain:

  1. All generator inputs (mandatory + recommended + conditional if applicable)
  2. Paths already resolved (not patterns, actual file paths)
  3. MCP resource URIs for each input

  Current TaskMetadata (US-044 v2):

  class TaskMetadata(BaseModel):
      artifact_id: str      # "PRD-006"
      parent_id: str        # "EPIC-006" (simple reference)
      task_id: str

  NEW TaskMetadata (with resolved inputs):

  class TaskMetadata(BaseModel):
      artifact_id: str              # "PRD-006" (output to generate)
      generator: str                # "prd-generator"
      task_id: str                  # "task-123"
      inputs: List[GeneratorInput]  # ALL resolved inputs

  class GeneratorInput(BaseModel):
      name: str                     # "epic" (from generator XML)
      classification: str           # "mandatory" | "recommended" | "conditional"
      artifact_type: str            # "epic"
      artifact_id: str             # "EPIC-006"
      resource_path: str           # RESOLVED: "artifacts/epics/EPIC-006_project_foundation_bootstrap_v2.md"
      mcp_resource_uri: str        # "file:///workspace/artifacts/epics/EPIC-006_project_foundation_bootstrap_v2.md"
      status: str                  # "Approved"

  ---
  Path Resolution Process (add_task or approve_artifact)

  When creating task to generate PRD-006:

  Step 1: Read PRD generator <input_artifacts> section:
  <input_artifacts>
    <input classification="mandatory" name="epic">
      <artifact_type>epic</artifact_type>
      <path>artifacts/epics/EPIC-{id}_*_v{version}.md</path>
    </input>
    <input classification="recommended" name="business_research">
      <path>artifacts/research/{product_name}_business_research.md</path>
    </input>
    <input classification="recommended" name="implementation_research">
      <path>artifacts/research/{product_name}_implementation_research.md</path>
    </input>
  </input_artifacts>

  Step 2: Resolve each input path:

  Input 1 (epic - mandatory):
  - Pattern: artifacts/epics/EPIC-{id}_*_v{version}.md
  - Substitute: {id}=006 → artifacts/epics/EPIC-006_*_v*.md
  - Glob/Find: artifacts/epics/EPIC-006_project_foundation_bootstrap_v2.md
  - Verify: File exists, status = "Approved"
  - MCP URI: file:///workspace/artifacts/epics/EPIC-006_project_foundation_bootstrap_v2.md

  Input 2 (business_research - recommended):
  - Pattern: artifacts/research/{product_name}_business_research.md
  - Substitute: {product_name}=AI_Agent_MCP_Server (from CLAUDE.md)
  - Resolve: artifacts/research/AI_Agent_MCP_Server_business_research.md
  - Verify: File exists, status = "Finalized"
  - MCP URI: file:///workspace/artifacts/research/AI_Agent_MCP_Server_business_research.md

  Input 3 (implementation_research - recommended):
  - Same process as Input 2

  Step 3: Create TaskMetadata with ALL resolved inputs:
  TaskMetadata(
      artifact_id="PRD-006",
      generator="prd-generator",
      task_id="task-123",
      inputs=[
          GeneratorInput(
              name="epic",
              classification="mandatory",
              artifact_type="epic",
              artifact_id="EPIC-006",
              resource_path="artifacts/epics/EPIC-006_project_foundation_bootstrap_v2.md",
              mcp_resource_uri="file:///workspace/artifacts/epics/EPIC-006_project_foundation_bootstrap_v2.md",
              status="Approved"
          ),
          GeneratorInput(
              name="business_research",
              classification="recommended",
              artifact_type="research",
              artifact_id="N/A",
              resource_path="artifacts/research/AI_Agent_MCP_Server_business_research.md",
              mcp_resource_uri="file:///workspace/artifacts/research/AI_Agent_MCP_Server_business_research.md",
              status="Finalized"
          ),
          GeneratorInput(
              name="implementation_research",
              classification="recommended",
              artifact_type="research",
              artifact_id="N/A",
              resource_path="artifacts/research/AI_Agent_MCP_Server_implementation_research.md",
              mcp_resource_uri="file:///workspace/artifacts/research/AI_Agent_MCP_Server_implementation_research.md",
              status="Finalized"
          )
      ]
  )

  ---
  Benefits of Resolved Paths in Tasks

  1. Self-contained tasks: All inputs validated and resolved at task creation time
  2. No runtime path resolution: Generator just reads MCP URIs from task metadata
  3. Validation at creation: Ensures all mandatory inputs exist and approved BEFORE task created
  4. Audit trail: Task contains snapshot of input artifacts at creation time
  5. Eliminates resolve_artifact_path tool: Path resolution happens during task creation

  ---
  Updated add_task Validation Logic (US-049)

  New validation requirements:

  1. ✅ Read generator XML: Parse <input_artifacts> section to get input requirements
  2. ✅ Resolve all paths: For each mandatory/recommended input, resolve path pattern to actual file
  3. ✅ Verify file exists: Glob pattern, find file, fail if not found (mandatory) or warn (recommended)
  4. ✅ Verify status: For artifact inputs (non-research), verify status = "Approved"
  5. ✅ Construct MCP URIs: Convert file paths to file:///workspace/... format
  6. ✅ Validate completeness: All mandatory inputs resolved and included in TaskMetadata
  7. ✅ Validate no duplicates: Task for same artifact_id not already in queue

  Error handling:
  - Mandatory input not found → Fail task creation with error: "Cannot create task PRD-006: mandatory input 'epic' not found"
  - Mandatory input not approved → Fail with error: "Cannot create task PRD-006: parent artifact EPIC-006 status is Draft (must be Approved)"
  - Recommended input not found → Warn and continue: "Task PRD-006 created without recommended input 'business_research'"

  ---
  Updated approve_artifact Logic (US-048)

  When approve_artifact calls add_task to create sub-artifact tasks:

  1. ✅ Determine sub-artifacts: Parse approved artifact to identify required sub-artifacts
  2. ✅ For each sub-artifact:
    - Read generator XML for sub-artifact type
    - Resolve all input paths (approved artifact becomes input for sub-artifact generator)
    - Create TaskMetadata with resolved inputs
    - Call add_task with complete TaskMetadata

  Example: Approve EPIC-006 → Generate PRD-006
  # Step 1: Approve EPIC-006 (update status)
  # Step 2: Determine sub-artifact: PRD-006
  # Step 3: Read prd-generator.xml inputs
  # Step 4: Resolve paths (epic input = EPIC-006)
  # Step 5: Create task with resolved inputs

  task = TaskMetadata(
      artifact_id="PRD-006",
      generator="prd-generator",
      task_id="generated-task-001",
      inputs=[
          GeneratorInput(
              name="epic",
              classification="mandatory",
              artifact_id="EPIC-006",
              resource_path="artifacts/epics/EPIC-006_project_foundation_bootstrap_v2.md",
              mcp_resource_uri="file:///workspace/artifacts/epics/EPIC-006_project_foundation_bootstrap_v2.md",
              status="Approved"
          ),
          # ... other inputs
      ]
  )

  add_task_result = await add_task(AddTaskInput(tasks=[task]))

  ---
  Updated Assumptions (with A13 added)

  A13: Task Input Resolution Strategy

  Tasks are self-contained with pre-resolved MCP resource paths.

  add_task responsibilities:
  1. Read generator XML <input_artifacts> section
  2. Resolve all path patterns to actual files (glob + find)
  3. Verify mandatory inputs exist and approved
  4. Construct MCP resource URIs for all inputs
  5. Include all resolved inputs in TaskMetadata.inputs
  6. Validate completeness before creating task

  Generator execution (when task runs):
  1. Read TaskMetadata.inputs from task
  2. Load each MCP resource URI directly
  3. No path resolution needed (already done)

  Correct?

  ---
  A14: Generator XML Parsing

  No, this is all prepared during migration process. No need for dynamic parsing when calling add_task

  ---
  A15: Version Selection for Input Artifacts

  Correct, highest version number

  ---
  Questions for Confirmation

  Critical Questions:

  1. A13 Confirmation: Yes
  2. A14 Confirmation: No, it is fixed during migration process
  3. A15 Confirmation: Correct
  4. Schema Confirmation: Yes
  5. Scope Confirmation: No parsing

  Original Questions (A1-A12):

  6. A3: PRD approval → Depends on complexity and requirement for FuncSpec
  7. A4: Yes
  8. A5: See response for A5 for details
  9. A8: No, must all be answered
