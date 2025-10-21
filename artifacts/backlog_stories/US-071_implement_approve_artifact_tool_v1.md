# User Story: Implement approve_artifact Tool

## Metadata
- **Story ID:** US-071
- **Title:** Implement approve_artifact Tool
- **Type:** Feature
- **Status:** Draft (v1)
- **Priority:** Must-have (enables automated approval workflow with placeholder ID resolution, replaces manual approval and US-042 resolve_artifact_path)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-008 (MCP Tools - Validation and Path Resolution)
- **Functional Requirements Covered:** FR-26 (new requirement for approval workflow automation)
- **Informed By Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Functional Requirements - FR-26 (new requirement)
- **Functional Requirements Coverage:**
  - **FR-26 (NEW):** MCP Server SHALL provide `approve_artifact` tool that approves Draft artifacts, resolves placeholder IDs via ID Management API, updates artifacts with final IDs, resolves ALL generator inputs for sub-artifacts, and creates tasks via add_task tool

**Parent High-Level Story:** [HLS-008: MCP Tools - Validation and Path Resolution]
- **Link:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 9: Implement approve_artifact Tool (NEW)

## User Story
As Claude Code, I want a tool that orchestrates the complete artifact approval workflow (validate prerequisites → reserve IDs → replace placeholders → resolve inputs → create tasks), so that I can approve artifacts and automatically initiate sub-artifact workflows without manual intervention.

## Description
Currently, artifact approval is a manual multi-step process:
1. Human verifies artifact quality (validation passed)
2. Human updates artifact status from "Draft" to "Approved"
3. Human manually assigns IDs to placeholder sub-artifacts (HLS-AAA → HLS-012)
4. Human updates TODO.md to add sub-artifact generation tasks
5. Human ensures parent artifacts are approved before approving children

This creates:
1. **Manual Overhead:** 5-step approval process requiring human intervention
2. **Error Risk:** Placeholder IDs may be forgotten or incorrectly replaced
3. **ID Collision Risk:** Manual ID assignment can create duplicates
4. **Workflow Fragmentation:** No automatic sub-artifact task creation
5. **Resolution Failures:** Tasks created without validated inputs fail during execution

This story implements a deterministic Python tool (`approve_artifact`) that:
1. **Validates approval prerequisites** (4 checks):
   - Artifact exists in filesystem
   - Current status = "Draft" (not already approved)
   - Parent artifact approved (if parent exists)
   - No blocking Open Questions ([REQUIRES SPIKE] or [REQUIRES ADR] markers)
2. **Parses artifact** to detect sub-artifacts and placeholder IDs
3. **Reserves ID range** via ID Management API (reserve_id_range)
4. **Replaces placeholder IDs** in artifact content (HLS-AAA → HLS-012)
5. **Updates artifact status** from "Draft" to "Approved"
6. **Resolves ALL generator inputs** for sub-artifact tasks (MCP resource URIs)
7. **Creates tasks** via add_task tool with resolved inputs
8. **Confirms ID reservation** to prevent expiration

The tool eliminates manual approval overhead, prevents ID collisions, ensures sub-artifact tasks created with validated inputs, and guarantees workflow integrity.

**Key Innovation:** Replaces US-042 (resolve_artifact_path) by embedding path resolution in approval workflow.

## Implementation Research References

**Primary Research Document:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

**Technical Patterns Applied:**
- **§2.1: Python 3.11+ with Type Safety:** Use Pydantic models for input/output validation with full type hints
- **§2.2: FastAPI Integration:** Expose approve_artifact tool as MCP tool via FastAPI
- **§5.3: Input Validation:** Validate approval prerequisites before proceeding
- **§6.1: Structured Logging:** Log approval workflow stages with task_id correlation

**Anti-Patterns Avoided:**
- **§8.1: Poor Error Handling:** Return structured error responses for each prerequisite validation failure
- **§8.2: Synchronous Blocking Calls in Async Context:** Use async HTTP client for ID Management API and Task Tracking API calls

## Functional Requirements
1. Tool accepts two parameters:
   - `artifact_id`: Full artifact ID to approve (e.g., "PRD-006", "EPIC-006")
   - `task_id` (string, mandatory): Task tracking ID for log correlation
2. **Step 1: Validate Approval Prerequisites (4 checks)**
   - Check 1: Artifact file exists in filesystem
   - Check 2: Artifact status = "Draft" (not already "Approved")
   - Check 3: Parent artifact approved (if parent_id exists in metadata)
   - Check 4: No blocking Open Questions ([REQUIRES SPIKE], [REQUIRES ADR] markers in Open Questions section)
   - If any check fails → return error with clear message (do NOT proceed)
3. **Step 2: Parse Artifact for Sub-artifacts**
   - Read artifact content
   - Detect sub-artifact type based on artifact type:
     - Epic → 1 PRD (same ID: EPIC-006 → PRD-006)
     - PRD → N HLS (parse §High-Level User Stories section for HLS-XXX subsections)
     - HLS → N US (parse §Decomposition section for backlog stories)
     - US → Tech Spec + Tasks (if marked [REQUIRES TECH SPEC])
   - Extract placeholder IDs (HLS-AAA, HLS-BBB, HLS-CCC, etc.)
   - Count sub-artifacts needed
4. **Step 3: Reserve ID Range**
   - Call ID Management API: `reserve_id_range(type, count)`
   - Receive reserved IDs (e.g., ["HLS-012", "HLS-013", "HLS-014"])
   - Store reservation_id for later confirmation
5. **Step 4: Replace Placeholder IDs in Artifact**
   - Map placeholders to reserved IDs (HLS-AAA → HLS-012)
   - Replace all placeholder references in artifact content
   - Write corrected artifact atomically (temp file + rename)
6. **Step 5: Update Artifact Status**
   - Update metadata: Status = "Draft" → "Approved"
   - Write metadata JSON atomically
7. **Step 6: Resolve Generator Inputs for Sub-artifacts**
   - For each sub-artifact (e.g., HLS-012, HLS-013, HLS-014):
     - Read generator input requirements (from pre-configured mappings, NOT dynamic XML parsing)
     - Resolve mandatory inputs (parent artifact now Approved)
     - Resolve recommended inputs (Business Research, Implementation Research)
     - Construct GeneratorInput objects with MCP resource URIs
     - Build TaskMetadata with complete inputs list
8. **Step 7: Create Tasks via add_task**
   - Call add_task tool with list of TaskMetadata (all inputs resolved)
   - Receive task_ids from Task Tracking API
9. **Step 8: Confirm ID Reservation**
   - Call ID Management API: `confirm_reservation(reservation_id)`
   - Prevent reservation expiration
10. Tool returns structured JSON response:
   ```json
   {
     "success": true,
     "artifact_id": "PRD-006",
     "old_status": "Draft",
     "new_status": "Approved",
     "artifact_path": "artifacts/prds/PRD-006_v3.md",
     "placeholder_ids_replaced": 3,
     "id_mapping": {
       "HLS-AAA": "HLS-012",
       "HLS-BBB": "HLS-013",
       "HLS-CCC": "HLS-014"
     },
     "sub_artifacts_detected": ["HLS-012", "HLS-013", "HLS-014"],
     "tasks_created": 3,
     "task_ids": ["TASK-012", "TASK-013", "TASK-014"]
   }
   ```
11. Tool execution completes in <2000ms p95 (approval workflow more complex than simple tool calls)
12. Tool logs approval workflow with timestamp, task_id, artifact_id, old_status, new_status, placeholder IDs replaced, sub-artifacts detected, tasks created, duration

## Non-Functional Requirements
- **Performance:** Approval workflow latency <2000ms p95 (includes ID reservation, file I/O, task creation)
- **Reliability:** Atomic operations (artifact updates use temp file + rename), ID reservation confirmed only after success
- **Security:** Approval prerequisites validated before ANY modifications
- **Observability:** Structured logging captures approval workflow stages for audit trail
- **Maintainability:** Clear separation between prerequisite validation, ID resolution, input resolution, and task creation

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** Follow established implementation patterns for MCP tools. Supplement with story-specific approval workflow orchestration.

**References to Implementation Standards:**
- **prompts/CLAUDE/python/patterns-tooling.md:** Use Taskfile commands
- **prompts/CLAUDE/python/patterns-testing.md:** Testing patterns (80% coverage, async tests, mock API calls)
- **prompts/CLAUDE/python/patterns-typing.md:** Type hints with mypy strict mode, Pydantic models
- **prompts/CLAUDE/python/patterns-architecture.md:** Project structure following established patterns

### Implementation Guidance

**Story-Specific Technical Approach:**

1. **Pydantic Models for Tool Input/Output:**
   ```python
   from pydantic import BaseModel, Field
   from typing import List, Dict, Optional

   class ApproveArtifactInput(BaseModel):
       """Input schema for approve_artifact tool"""
       artifact_id: str = Field(..., pattern=r'^[A-Z]+-\d{3,}$', description="Artifact ID to approve")
       task_id: str = Field(..., description="Task tracking ID for log correlation")

   class ApprovalResult(BaseModel):
       """Approval workflow result"""
       success: bool
       artifact_id: str
       old_status: str
       new_status: str
       artifact_path: str
       placeholder_ids_replaced: int = 0
       id_mapping: Dict[str, str] = {}  # {"HLS-AAA": "HLS-012", ...}
       sub_artifacts_detected: List[str] = []
       tasks_created: int = 0
       task_ids: List[str] = []
       error: Optional[str] = None
   ```

2. **Approval Workflow Orchestrator:**
   ```python
   from pathlib import Path
   import re
   from typing import List, Dict, Tuple
   import structlog

   logger = structlog.get_logger()

   class ApprovalWorkflow:
       def __init__(self, id_management_client, task_tracking_client, artifacts_base_dir: str):
           self.id_client = id_management_client
           self.task_client = task_tracking_client
           self.artifacts_base_dir = Path(artifacts_base_dir)

       async def execute_approval(self, artifact_id: str, task_id: str) -> ApprovalResult:
           """Orchestrates complete approval workflow"""
           try:
               # Step 1: Validate prerequisites
               artifact_path = await self._validate_prerequisites(artifact_id)
               logger.info("approval_prerequisites_validated", task_id=task_id, artifact_id=artifact_id)

               # Step 2: Parse artifact for sub-artifacts
               artifact_content, metadata = await self._load_artifact(artifact_path)
               sub_artifact_type, placeholders = await self._detect_sub_artifacts(artifact_content, artifact_id)
               logger.info("sub_artifacts_detected", task_id=task_id, artifact_id=artifact_id,
                          count=len(placeholders), type=sub_artifact_type)

               # Step 3: Reserve ID range (if placeholders exist)
               id_mapping = {}
               reservation_id = None
               if placeholders:
                   reserved_ids, reservation_id = await self._reserve_id_range(sub_artifact_type, len(placeholders))
                   id_mapping = dict(zip(placeholders, reserved_ids))
                   logger.info("id_range_reserved", task_id=task_id, count=len(reserved_ids),
                              id_mapping=id_mapping)

               # Step 4: Replace placeholder IDs in artifact
               if id_mapping:
                   corrected_content = await self._replace_placeholders(artifact_content, id_mapping)
                   await self._write_artifact_atomically(artifact_path, corrected_content)
                   logger.info("placeholders_replaced", task_id=task_id, count=len(id_mapping))

               # Step 5: Update artifact status
               await self._update_artifact_status(artifact_path, "Approved")
               logger.info("artifact_status_updated", task_id=task_id, artifact_id=artifact_id,
                          new_status="Approved")

               # Step 6: Resolve generator inputs for sub-artifacts
               tasks_metadata = await self._resolve_generator_inputs(
                   list(id_mapping.values()) if id_mapping else [],
                   artifact_id,
                   sub_artifact_type
               )
               logger.info("generator_inputs_resolved", task_id=task_id, tasks_count=len(tasks_metadata))

               # Step 7: Create tasks via add_task
               task_ids = []
               if tasks_metadata:
                   add_task_result = await self.task_client.add_tasks(tasks_metadata, task_id)
                   task_ids = add_task_result.task_ids
                   logger.info("tasks_created", task_id=task_id, tasks_count=len(task_ids))

               # Step 8: Confirm ID reservation
               if reservation_id:
                   await self.id_client.confirm_reservation(reservation_id)
                   logger.info("id_reservation_confirmed", task_id=task_id, reservation_id=reservation_id)

               return ApprovalResult(
                   success=True,
                   artifact_id=artifact_id,
                   old_status="Draft",
                   new_status="Approved",
                   artifact_path=str(artifact_path),
                   placeholder_ids_replaced=len(id_mapping),
                   id_mapping=id_mapping,
                   sub_artifacts_detected=list(id_mapping.values()) if id_mapping else [],
                   tasks_created=len(task_ids),
                   task_ids=task_ids
               )

           except Exception as e:
               logger.error("approval_workflow_failed", task_id=task_id, artifact_id=artifact_id, error=str(e))
               return ApprovalResult(
                   success=False,
                   artifact_id=artifact_id,
                   old_status="Draft",
                   new_status="Draft",
                   artifact_path="",
                   error=str(e)
               )

       async def _validate_prerequisites(self, artifact_id: str) -> Path:
           """Validates 4 approval prerequisites"""
           # Check 1: Artifact exists
           artifact_path = self._find_artifact_path(artifact_id)
           if not artifact_path.exists():
               raise FileNotFoundError(f"Artifact {artifact_id} not found")

           # Check 2: Status = Draft
           metadata = self._read_artifact_metadata(artifact_path)
           if metadata.get("status") != "Draft":
               raise ValueError(f"Artifact {artifact_id} already approved (status: {metadata.get('status')})")

           # Check 3: Parent approved (if parent exists)
           parent_id = metadata.get("parent_id")
           if parent_id:
               parent_metadata = self._read_artifact_metadata(self._find_artifact_path(parent_id))
               if parent_metadata.get("status") != "Approved":
                   raise ValueError(f"Parent artifact {parent_id} must be approved first")

           # Check 4: No blocking Open Questions
           artifact_content = artifact_path.read_text()
           if self._has_blocking_open_questions(artifact_content):
               raise ValueError(f"Artifact {artifact_id} has blocking open questions requiring resolution")

           return artifact_path

       async def _detect_sub_artifacts(self, content: str, artifact_id: str) -> Tuple[str, List[str]]:
           """Detects sub-artifact type and placeholder IDs"""
           artifact_type = artifact_id.split('-')[0]

           if artifact_type == "EPIC":
               # Epic → 1 PRD (no placeholders, use same numeric ID)
               return "prd", []
           elif artifact_type == "PRD":
               # PRD → N HLS (parse §High-Level User Stories)
               placeholders = re.findall(r'HLS-[A-Z]{3}', content)
               return "hls", list(set(placeholders))  # Deduplicate
           elif artifact_type == "HLS":
               # HLS → N US (parse §Decomposition)
               placeholders = re.findall(r'US-[A-Z]{3}', content)
               return "backlog_story", list(set(placeholders))
           else:
               return "unknown", []

       async def _reserve_id_range(self, artifact_type: str, count: int) -> Tuple[List[str], str]:
           """Reserves ID range via ID Management API"""
           response = await self.id_client.reserve_id_range(artifact_type, count)
           return response['reserved_ids'], response['reservation_id']

       async def _replace_placeholders(self, content: str, id_mapping: Dict[str, str]) -> str:
           """Replaces placeholder IDs with final IDs"""
           corrected_content = content
           for placeholder, final_id in id_mapping.items():
               corrected_content = corrected_content.replace(placeholder, final_id)
           return corrected_content

       async def _write_artifact_atomically(self, path: Path, content: str):
           """Writes artifact atomically (temp file + rename)"""
           temp_path = path.with_suffix('.tmp')
           temp_path.write_text(content)
           temp_path.rename(path)  # Atomic on POSIX systems

       async def _update_artifact_status(self, path: Path, new_status: str):
           """Updates artifact metadata status"""
           metadata_path = path.with_suffix('.json')
           metadata = json.loads(metadata_path.read_text())
           metadata['status'] = new_status
           metadata_path.write_text(json.dumps(metadata, indent=2))

       async def _resolve_generator_inputs(self, artifact_ids: List[str], parent_id: str,
                                          generator_type: str) -> List[TaskMetadata]:
           """Resolves ALL generator inputs for sub-artifact tasks"""
           tasks = []
           for artifact_id in artifact_ids:
               # Read pre-configured input requirements (NOT dynamic XML parsing)
               input_config = self._get_generator_input_config(generator_type)

               # Resolve inputs
               inputs = []
               for inp_req in input_config:
                   if inp_req['name'] == 'parent':
                       # Mandatory parent input
                       parent_path = self._find_artifact_path(parent_id)
                       inputs.append(GeneratorInput(
                           name=inp_req['name'],
                           classification='mandatory',
                           artifact_type=parent_id.split('-')[0].lower(),
                           artifact_id=parent_id,
                           resource_path=str(parent_path),
                           mcp_resource_uri=f"file://{parent_path.absolute()}",
                           status="Approved"
                       ))
                   elif inp_req['name'] == 'business_research':
                       # Recommended research input
                       research_path = Path(f"{self.artifacts_base_dir}/research/AI_Agent_MCP_Server_business_research.md")
                       if research_path.exists():
                           inputs.append(GeneratorInput(
                               name='business_research',
                               classification='recommended',
                               artifact_type='research',
                               artifact_id='N/A',
                               resource_path=str(research_path),
                               mcp_resource_uri=f"file://{research_path.absolute()}",
                               status="Finalized"
                           ))

               # Construct TaskMetadata
               tasks.append(TaskMetadata(
                   artifact_id=artifact_id,
                   generator=f"{generator_type}-generator",
                   task_id=f"gen-{artifact_id}",
                   inputs=inputs
               ))

           return tasks

       def _get_generator_input_config(self, generator_type: str) -> List[Dict]:
           """Returns pre-configured generator input requirements"""
           # Pre-configured mappings (prepared during migration, NOT dynamic XML parsing)
           configs = {
               "prd": [
                   {"name": "epic", "classification": "mandatory"},
                   {"name": "business_research", "classification": "recommended"},
                   {"name": "implementation_research", "classification": "recommended"}
               ],
               "hls": [
                   {"name": "prd", "classification": "mandatory"},
                   {"name": "business_research", "classification": "recommended"}
               ],
               "backlog_story": [
                   {"name": "hls", "classification": "mandatory"},
                   {"name": "implementation_research", "classification": "recommended"}
               ]
           }
           return configs.get(generator_type, [])
   ```

3. **MCP Tool Implementation:**
   ```python
   from mcp.server.fastmcp import FastMCP
   import structlog
   import time

   mcp = FastMCP(name="MCPServer", version="1.0.0")
   logger = structlog.get_logger()

   approval_workflow = ApprovalWorkflow(
       id_management_client=id_client,
       task_tracking_client=task_client,
       artifacts_base_dir=settings.ARTIFACTS_BASE_DIR
   )

   @mcp.tool(
       name="approve_artifact",
       description="""
       Approves Draft artifacts with complete workflow orchestration.

       Use this tool when:
       - You have generated and validated an artifact (status: Draft)
       - Artifact contains placeholder IDs that need final ID assignment
       - You want to automatically create sub-artifact tasks with resolved inputs
       - You want to update artifact status to Approved

       Workflow (8 steps):
       1. Validate prerequisites (artifact exists, status=Draft, parent approved, no blocking questions)
       2. Parse artifact to detect sub-artifacts and placeholder IDs
       3. Reserve ID range via ID Management API
       4. Replace placeholder IDs in artifact with final IDs
       5. Update artifact status to Approved
       6. Resolve ALL generator inputs for sub-artifact tasks
       7. Create tasks via add_task tool (with resolved inputs)
       8. Confirm ID reservation

       Input:
       - artifact_id: Artifact to approve (e.g., "PRD-006")
       - task_id: Task tracking ID for log correlation

       Eliminates manual approval overhead.
       Prevents ID collisions.
       Ensures sub-artifact tasks created with validated inputs.
       """
   )
   async def approve_artifact(params: ApproveArtifactInput) -> ApprovalResult:
       """Approves artifact with complete workflow orchestration"""
       start_time = time.time()

       logger.info("approval_workflow_started", task_id=params.task_id, artifact_id=params.artifact_id)

       try:
           result = await approval_workflow.execute_approval(params.artifact_id, params.task_id)

           duration_ms = (time.time() - start_time) * 1000
           logger.info(
               "approval_workflow_completed",
               task_id=params.task_id,
               artifact_id=params.artifact_id,
               success=result.success,
               old_status=result.old_status,
               new_status=result.new_status,
               placeholder_ids_replaced=result.placeholder_ids_replaced,
               sub_artifacts_detected=len(result.sub_artifacts_detected),
               tasks_created=result.tasks_created,
               duration_ms=duration_ms
           )

           return result

       except Exception as e:
           logger.error("approval_workflow_error", task_id=params.task_id,
                       artifact_id=params.artifact_id, error=str(e))
           raise  # Re-raise for FastMCP ErrorHandlingMiddleware (→ JSON-RPC -32603)
   ```

4. **Testing Strategy:**
   - Unit tests: Validate ApprovalWorkflow prerequisite checks (4 checks)
   - Unit tests: Test sub-artifact detection (Epic → PRD, PRD → HLS, HLS → US)
   - Unit tests: Test placeholder ID replacement logic
   - Integration tests: Mock ID Management API and Task Tracking API
   - Integration tests: End-to-end approval workflow (Draft → Approved with tasks created)
   - Error handling tests: Test each prerequisite failure (artifact not found, already approved, parent not approved, blocking questions)
   - Performance tests: Verify <2000ms p95 latency for approval workflow

### Technical Tasks
- [ ] Implement ApprovalWorkflow class with 8-step orchestration
- [ ] Implement prerequisite validation (4 checks)
- [ ] Implement sub-artifact detection logic (parse for placeholder IDs)
- [ ] Implement ID Management API client integration (reserve_id_range, confirm_reservation)
- [ ] Implement placeholder ID replacement logic
- [ ] Implement atomic artifact write (temp file + rename)
- [ ] Implement generator input resolution (pre-configured mappings)
- [ ] Implement add_task integration for task creation
- [ ] Implement MCP tool endpoint with FastMCP
- [ ] Add structured logging for approval workflow stages
- [ ] Write unit tests for prerequisite validation (80% coverage)
- [ ] Write unit tests for sub-artifact detection
- [ ] Write integration tests with mocked APIs
- [ ] Write end-to-end approval workflow tests
- [ ] Write error handling tests (prerequisite failures)
- [ ] Write performance tests (<2000ms p95 latency)

## Acceptance Criteria

### Scenario 1: PRD approval with 3 HLS placeholder IDs
**Given** PRD-006 artifact generated with status="Draft"
**And** PRD-006 contains placeholder IDs: HLS-AAA, HLS-BBB, HLS-CCC
**And** Parent EPIC-006 has status="Approved"
**When** Claude Code calls `approve_artifact(artifact_id="PRD-006", task_id="task-123")`
**Then** tool validates prerequisites (all pass)
**And** tool detects 3 HLS placeholders
**And** tool calls `reserve_id_range(type="HLS", count=3)`
**And** receives reserved IDs: HLS-012, HLS-013, HLS-014
**And** tool replaces placeholders in artifact: HLS-AAA → HLS-012, HLS-BBB → HLS-013, HLS-CCC → HLS-014
**And** tool updates artifact status to "Approved"
**And** tool resolves generator inputs for 3 HLS tasks (parent PRD-006, business research, implementation research)
**And** tool calls `add_task` with 3 TaskMetadata objects (resolved inputs)
**And** tool confirms ID reservation
**And** returns `{success: true, artifact_id: "PRD-006", old_status: "Draft", new_status: "Approved", placeholder_ids_replaced: 3, id_mapping: {...}, sub_artifacts_detected: ["HLS-012", "HLS-013", "HLS-014"], tasks_created: 3, task_ids: [...]}`
**And** execution completes in <2000ms

### Scenario 2: Approval blocked - artifact already approved
**Given** PRD-006 artifact with status="Approved"
**When** Claude Code calls `approve_artifact(artifact_id="PRD-006", task_id="task-123")`
**Then** tool validates prerequisites
**And** prerequisite check 2 fails (status != Draft)
**And** tool returns error: "Artifact PRD-006 already approved (status: Approved)"
**And** no ID reservation made
**And** no artifact modifications made

### Scenario 3: Approval blocked - parent not approved
**Given** PRD-006 artifact with status="Draft"
**And** Parent EPIC-006 has status="Draft" (not approved)
**When** Claude Code calls `approve_artifact(artifact_id="PRD-006", task_id="task-123")`
**Then** tool validates prerequisites
**And** prerequisite check 3 fails (parent not approved)
**And** tool returns error: "Parent artifact EPIC-006 must be approved first"
**And** no ID reservation made
**And** no artifact modifications made

### Scenario 4: Approval blocked - blocking Open Questions
**Given** PRD-006 artifact with status="Draft"
**And** PRD-006 has Open Questions section with marker: [REQUIRES SPIKE]
**When** Claude Code calls `approve_artifact(artifact_id="PRD-006", task_id="task-123")`
**Then** tool validates prerequisites
**And** prerequisite check 4 fails (blocking open questions)
**And** tool returns error: "Artifact PRD-006 has blocking open questions requiring resolution"
**And** no ID reservation made
**And** no artifact modifications made

### Scenario 5: Epic approval (no placeholders, single PRD task)
**Given** EPIC-006 artifact with status="Draft"
**And** EPIC-006 has no parent
**And** EPIC-006 specifies 1 PRD as sub-artifact (no placeholder, uses same numeric ID)
**When** Claude Code calls `approve_artifact(artifact_id="EPIC-006", task_id="task-123")`
**Then** tool validates prerequisites (all pass, no parent check)
**And** tool detects 1 PRD sub-artifact (PRD-006)
**And** tool does NOT call reserve_id_range (no placeholders, uses same numeric ID)
**And** tool updates artifact status to "Approved"
**And** tool resolves generator inputs for 1 PRD task (parent EPIC-006, business research, implementation research)
**And** tool calls `add_task` with 1 TaskMetadata (PRD-006)
**And** returns `{success: true, artifact_id: "EPIC-006", old_status: "Draft", new_status: "Approved", placeholder_ids_replaced: 0, sub_artifacts_detected: ["PRD-006"], tasks_created: 1, task_ids: [...]}`

### Scenario 6: Approval workflow logged with task_id
**Given** Claude Code calls approve_artifact tool
**When** Approval workflow completes
**Then** tool logs structured events for each stage:
  - approval_workflow_started
  - approval_prerequisites_validated
  - sub_artifacts_detected
  - id_range_reserved
  - placeholders_replaced
  - artifact_status_updated
  - generator_inputs_resolved
  - tasks_created
  - id_reservation_confirmed
  - approval_workflow_completed
**And** all log entries include task_id for correlation

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Not Needed (Single Sprint-Ready Task)

**Rationale:**
- **Story Points:** 13 SP (high complexity due to 8-step orchestration, API integration, file I/O)
- **Developer Count:** Single developer (workflow orchestration with existing API clients)
- **Domain Span:** 2 domains (filesystem operations + API integration)
- **Complexity:** High - complex workflow with multiple stages, error handling at each stage
- **Uncertainty:** Low-moderate - clear workflow steps, existing API contracts, file I/O patterns established
- **Override Factors:** Complexity high but workflow is linear (no parallel decomposition benefit)

Per SDLC Section 11.6 Decision Matrix: "13 SP, single developer, high complexity → CONSIDER DECOMPOSITION if parallel work possible".

**Decision:** Skip decomposition. Workflow is linear (each step depends on previous). Single developer can complete in 5-7 days. Decomposition would fragment cohesive workflow logic.

## Definition of Done
- [ ] ApprovalWorkflow class implemented with 8-step orchestration
- [ ] Prerequisite validation implemented (4 checks)
- [ ] Sub-artifact detection implemented (Epic → PRD, PRD → HLS, HLS → US)
- [ ] ID Management API client integration implemented
- [ ] Placeholder ID replacement implemented
- [ ] Atomic artifact write implemented
- [ ] Generator input resolution implemented (pre-configured mappings)
- [ ] add_task integration implemented
- [ ] MCP tool endpoint implemented with FastMCP
- [ ] Structured logging for approval workflow stages
- [ ] Unit tests passing (80% coverage, includes prerequisite validation, sub-artifact detection)
- [ ] Integration tests passing (mocked APIs, end-to-end workflow)
- [ ] Error handling tests passing (prerequisite failures)
- [ ] Performance tests passing (<2000ms p95 latency)
- [ ] Manual testing: Approve PRD with placeholder IDs, verify final IDs replaced and tasks created
- [ ] Product Owner approval obtained

## Additional Information
**Suggested Labels:** mcp-tools, approval-workflow, orchestration
**Estimated Story Points:** 13
**Dependencies:**
- **Depends On:** US-051 (ID Management API - reserve_id_range, confirm_reservation), US-044 v3 (add_task with resolved inputs)
- **Replaces:** US-042 (resolve_artifact_path - deprecated, path resolution now embedded in approval workflow)
- **Blocks:** None (enables workflow automation, doesn't block other features)

**Related PRD Section:** PRD-006 §Functional Requirements - FR-26 (new requirement)

## Decisions Made

**Decision 1: Use pre-configured generator input mappings (NOT dynamic XML parsing)**
- **Made:** During v1 design (2025-10-20)
- **Rationale:** Dynamic XML parsing adds complexity and runtime overhead. Pre-configured mappings prepared during migration provide same functionality with simpler implementation. Generator input requirements are stable (change infrequently)
- **Impact:**
  - approve_artifact reads input configs from dict (not XML files)
  - Requires migration step to prepare input configs
  - Simpler runtime (no XML parser dependency)
  - Trade-off: Config updates require code change (not just XML update)
  - Decision can be revisited if dynamic requirements emerge

**Decision 2: Atomic artifact writes use temp file + rename pattern**
- **Made:** During v1 design (2025-10-20)
- **Rationale:** POSIX atomic rename guarantees no partial writes visible. Prevents corruption if process crashes mid-write
- **Impact:**
  - Write to temp file (.tmp suffix)
  - Rename temp → final (atomic operation)
  - No partial artifact content visible to readers
  - Crash-safe writes

**Decision 3: ID reservation confirmed AFTER tasks created (not before)**
- **Made:** During v1 design (2025-10-20)
- **Rationale:** If task creation fails, ID reservation can expire without consequence. Confirming before task creation risks using reserved IDs without corresponding tasks
- **Impact:**
  - Task creation failure allows ID reservation to expire (IDs returned to pool)
  - Success path confirms reservation after tasks committed
  - Prevents orphaned ID reservations

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`
- **Related Stories:** US-044 v3 (add_task with resolved inputs), US-051 (ID Management API), US-042 (resolve_artifact_path - DEPRECATED)
- **Feedback:** `/feedback/new_work_feedback.md` (approve_artifact requirements)
- **Sequence Diagram:** `/docs/mcp_tools_sequence_diagram_v3.md` (approve_artifact workflow)
