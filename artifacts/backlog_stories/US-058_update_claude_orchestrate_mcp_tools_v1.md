# User Story: Update CLAUDE.md to Orchestrate MCP Tools

## Metadata
- **Story ID:** US-058
- **Title:** Update CLAUDE.md to Orchestrate MCP Tools
- **Type:** Feature
- **Status:** Backlog
- **Priority:** High - Enables deterministic validation and path resolution, reducing AI inference errors from 20-30% to <5%
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-010
- **Functional Requirements Covered:** FR-06, FR-07, FR-08, FR-09, FR-10, FR-11, FR-12, FR-23, FR-24
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Requirements - FR-06 through FR-11, FR-12, FR-23, FR-24; §Timeline & Milestones - Phase 3 (Week 4)
- **Functional Requirements Coverage:**
  - **FR-06:** MCP Server SHALL provide `validate_artifact` tool (deterministic validation, not AI inference)
  - **FR-07:** MCP Server SHALL provide `resolve_artifact_path` tool (pattern matching with variables)
  - **FR-08:** MCP Server SHALL provide `get_next_task` tool (integrated with Task Tracking microservice)
  - **FR-09:** MCP Server SHALL provide `update_task_status` tool (task status updates)
  - **FR-10:** MCP Server SHALL provide `get_next_available_id` tool (ID registry integration)
  - **FR-11:** MCP Server SHALL provide `reserve_id_range` tool (batch ID allocation)
  - **FR-12:** Main CLAUDE.md SHALL be refactored to orchestrate MCP Server integration, directing Claude Code to use MCP tools
  - **FR-23:** MCP Server SHALL provide `store_artifact` tool (centralized artifact storage)
  - **FR-24:** MCP Server SHALL provide `add_task` tool (automatic sub-artifact workflow initiation)

**Parent High-Level Story:** [HLS-010: CLAUDE.md Orchestration Update & Integration Testing]
- **Link:** `/artifacts/hls/HLS-010_claude_orchestration_integration_testing_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 3

## User Story
As a Framework Maintainer, I want CLAUDE.md validation and path resolution instructions updated to call MCP tools instead of AI inference, so that Claude Code uses deterministic validation with <5% error rate (vs. 20-30% AI inference baseline).

## Description

The current CLAUDE.md orchestration relies on AI inference for critical operations:
1. **Artifact Validation:** Claude Code subjectively evaluates if artifacts meet quality criteria (e.g., "Does PRD have clear objectives?") with 20-30% inconsistency rate
2. **Path Resolution:** Claude Code infers file paths from patterns like `artifacts/epics/EPIC-{id}_{slug}_v{version}.md` with frequent errors (wrong version, wrong slug, file not found)
3. **Task Management:** TODO.md file grows unbounded with completed tasks, consuming 5-10k tokens on every interaction
4. **ID Assignment:** Claude Code manually tracks next available IDs (US-XXX, SPEC-XXX) with risk of collisions

This story updates CLAUDE.md orchestration instructions to call MCP tools for these operations:
- `validate_artifact`: Deterministic validation against checklist (24/26 criteria automated)
- `resolve_artifact_path`: Pattern matching with variable substitution (exact file path returned)
- `get_next_task`: Query Task Tracking microservice for next pending task
- `update_task_status`: Update task status (pending→in_progress→completed)
- `get_next_available_id`: Query ID registry for next sequential ID
- `reserve_id_range`: Reserve contiguous ID range for batch generation
- `store_artifact`: Upload generated artifacts to centralized storage
- `add_task`: Add new tasks to queue after artifact generation

**Key Changes:**
1. Update CLAUDE.md §Generate Command Instructions to call `validate_artifact` tool instead of AI inference
2. Update CLAUDE.md §Artifact Path Resolution Algorithm to call `resolve_artifact_path` tool
3. Add CLAUDE.md §Task Management instructions to call `get_next_task` and `update_task_status` tools
4. Add CLAUDE.md §ID Management instructions to call `get_next_available_id` and `reserve_id_range` tools
5. Document all 8 MCP tools with input/output schemas and usage examples

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§4.4: MCP Tools Pattern:** Deterministic Python scripts exposed as MCP tools, callable by Claude Code
  - **Example:** `validate_artifact(content, checklist_id)` → `{passed: true/false, results: [{id: "CQ-01", passed: true}]}`
- **§5.3: Validation Patterns:** Automated validation for objective criteria (template sections present, ID format correct), manual review flags for subjective criteria (readability, clarity)
  - **Error Rate Target:** <5% (vs. 20-30% AI inference baseline)
- **§5.4: Path Resolution Patterns:** Pattern matching with variable substitution (`artifacts/epics/EPIC-{id}_*_v{version}.md` + `id=006, version=1` → exact file path)
  - **Performance Target:** <500ms p95 latency for path resolution

**Anti-Patterns Avoided:**
- **§6.4: AI Inference for Deterministic Operations:** Avoid using AI inference for validation rules that can be objectively evaluated (e.g., "All template sections present?" is objective, not subjective)
- **§6.5: Manual ID Tracking:** Avoid manual ID assignment in TODO.md (causes collisions, human error, unbounded file growth)

**Performance Considerations:**
- **§8.3: Tool Execution Latency:** MCP tools execute in <500ms p95 (vs. 2-5 seconds for AI inference)
- **§8.4: Token Optimization:** Task tracking via database API eliminates TODO.md file growth (saves 5-10k tokens per task execution)

## Functional Requirements
- Update CLAUDE.md §Generate Command Instructions to call `validate_artifact` tool
- Update CLAUDE.md §Artifact Path Resolution Algorithm to call `resolve_artifact_path` tool
- Add CLAUDE.md §Task Management instructions with `get_next_task` and `update_task_status` tools
- Add CLAUDE.md §ID Management instructions with `get_next_available_id` and `reserve_id_range` tools
- Document all 8 MCP tools (validate_artifact, resolve_artifact_path, get_next_task, update_task_status, get_next_available_id, reserve_id_range, store_artifact, add_task)
- Provide input/output schemas and usage examples for each tool
- Maintain functional equivalence (validation test suite passes pre/post changes)

## Non-Functional Requirements
- **Performance:** Tool execution latency <500ms p95 per NFR-Performance-02
- **Accuracy:** Validation error rate <5% (vs. 20-30% AI inference baseline) per PRD-006 §Goals & Success Metrics
- **Maintainability:** Clear documentation of tool input/output schemas for all 8 tools
- **Compatibility:** Functional equivalence validated via test suite (same validation results pre/post changes)
- **Backward Compatibility:** Graceful degradation to AI inference when MCP Server unavailable (implementation in US-059)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story updates CLAUDE.md orchestration instructions only, not implementation code.

### Implementation Guidance

**Step 1: Update CLAUDE.md §Generate Command Instructions - Validation**

Replace AI inference validation instructions with `validate_artifact` tool call:

**Before (AI Inference Approach):**
```markdown
### Step 4: Validate Generated Artifact
1. Review artifact against validation checklist
2. Evaluate content quality criteria (CQ-01 through CQ-14)
3. Evaluate traceability criteria (UT-01 through UT-08)
4. Evaluate consistency criteria (CC-01 through CC-06)
5. Report validation results
```

**After (MCP Tool Approach):**
```markdown
### Step 4: Validate Generated Artifact
1. Call MCP tool `validate_artifact` with inputs:
   - `artifact_content`: Generated artifact markdown content
   - `checklist_id`: Validation checklist identifier (e.g., "prd_validation_v1")
2. MCP Server returns validation results:
   - `{passed: true/false, results: [{id: "CQ-01", passed: true, details: "..."}]}`
3. Report validation results with criterion-level details
4. Manual review required for subjective criteria (CQ-11 appropriateness, CQ-12 readability)

**Tool Input Schema:**
```json
{
  "artifact_content": "string (markdown)",
  "checklist_id": "string (e.g., prd_validation_v1)"
}
```

**Tool Output Schema:**
```json
{
  "passed": "boolean",
  "results": [
    {"id": "CQ-01", "category": "content", "passed": true, "details": "All template sections present (8/8)"},
    {"id": "CQ-11", "category": "content", "passed": null, "requires_manual_review": true}
  ],
  "summary": {
    "total": 26,
    "automated_passed": 24,
    "automated_failed": 0,
    "manual_review_required": 2
  }
}
```
```

**Step 2: Update CLAUDE.md §Artifact Path Resolution Algorithm**

Replace AI inference path resolution with `resolve_artifact_path` tool call:

**Before (AI Inference Approach):**
```markdown
### Path Resolution
1. Identify path pattern from CLAUDE.md Folder Structure section
2. Substitute variables (e.g., {id}=006, {version}=1)
3. Use glob pattern to find matching file
4. Verify file exists
```

**After (MCP Tool Approach):**
```markdown
### Path Resolution
1. Call MCP tool `resolve_artifact_path` with inputs:
   - `pattern`: Path pattern from Folder Structure section (e.g., "artifacts/epics/EPIC-{id}_*_v{version}.md")
   - `variables`: Variable substitutions (e.g., {"id": "006", "version": 1})
2. MCP Server returns exact file path or error:
   - Success: `{path: "artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md"}`
   - Error (not found): `{error: "No files match pattern", candidates: []}`
   - Error (multiple matches): `{error: "Multiple files match pattern", candidates: ["...", "..."]}`

**Tool Input Schema:**
```json
{
  "pattern": "string (path pattern with {variables})",
  "variables": {
    "id": "string or integer",
    "version": "integer",
    "slug": "string (optional)"
  }
}
```

**Tool Output Schema:**
```json
{
  "path": "string (exact file path)" || null,
  "error": "string (error message)" || null,
  "candidates": ["array of matching paths (if multiple)"]
}
```
```

**Step 3: Add CLAUDE.md §Task Management Instructions**

Add new section for task management tool calls:

```markdown
## Task Management via MCP Tools

**Purpose:** Replace TODO.md file-based task tracking with database-backed Task Tracking microservice.

### Get Next Task

**When:** At start of work session or when previous task completed

**Tool:** `get_next_task`

**Input:**
```json
{
  "project_id": "ai-agent-mcp-server",
  "status_filter": "pending"
}
```

**Output:**
```json
{
  "task_id": "TASK-051",
  "description": "Generate PRD-006",
  "generator": "prd-generator",
  "inputs": ["EPIC-006"],
  "expected_outputs": ["PRD-006"],
  "context_notes": "New session CX required"
}
```

### Update Task Status

**When:** After completing task or transitioning status (pending→in_progress→completed)

**Tool:** `update_task_status`

**Input:**
```json
{
  "task_id": "TASK-051",
  "status": "completed",
  "completion_notes": "PRD-006 v1 generated, 26/26 validation criteria passed"
}
```

**Output:**
```json
{
  "success": true,
  "updated_task": {
    "task_id": "TASK-051",
    "status": "completed",
    "completed_at": "2025-10-17T14:30:00Z"
  }
}
```

### Add Task

**When:** After generating artifact that requires sub-artifacts (e.g., Epic requires PRD, PRD requires HLS)

**Tool:** `add_task`

**Input:**
```json
{
  "tasks": [
    {
      "artifact_id": "HLS-006",
      "artifact_type": "hls",
      "generator": "hls-generator",
      "parent_id": "PRD-006",
      "status": "pending"
    }
  ]
}
```

**Output:**
```json
{
  "success": true,
  "tasks_added": 6,
  "task_ids": ["TASK-046", "TASK-047", "TASK-048", "TASK-049", "TASK-050", "TASK-051"]
}
```
```

**Step 4: Add CLAUDE.md §ID Management Instructions**

Add new section for ID management tool calls:

```markdown
## ID Management via MCP Tools

**Purpose:** Replace manual ID tracking in TODO.md with database-backed ID registry.

### Get Next Available ID

**When:** Planning new artifact generation (single artifact)

**Tool:** `get_next_available_id`

**Input:**
```json
{
  "artifact_type": "US",
  "project_id": "ai-agent-mcp-server"
}
```

**Output:**
```json
{
  "artifact_type": "US",
  "next_id": "US-028",
  "last_assigned": "US-027"
}
```

### Reserve ID Range

**When:** Planning batch artifact generation (e.g., HLS decomposition generating 6 backlog stories)

**Tool:** `reserve_id_range`

**Input:**
```json
{
  "artifact_type": "US",
  "count": 6,
  "project_id": "ai-agent-mcp-server"
}
```

**Output:**
```json
{
  "artifact_type": "US",
  "reserved_ids": ["US-028", "US-029", "US-030", "US-031", "US-032", "US-033"],
  "reservation_id": "abc-123-def-456",
  "expires_at": "2025-10-17T14:30:00Z"
}
```

**Note:** Reservations expire after 15 minutes (default, configurable). Confirm reservation with `confirm_reservation` tool (implementation detail, not documented in CLAUDE.md orchestration instructions).
```

**Step 5: Document store_artifact Tool**

Add section for centralized artifact storage:

```markdown
### Store Artifact

**When:** After generating artifact with successful validation

**Tool:** `store_artifact`

**Input:**
```json
{
  "artifact_type": "epic",
  "artifact_id": "EPIC-006",
  "content": "[full artifact markdown content]",
  "metadata": {
    "status": "Draft",
    "parent_id": "INIT-001",
    "created_at": "2025-10-16T10:00:00Z"
  }
}
```

**Output:**
```json
{
  "success": true,
  "uri": "mcp://resources/artifacts/epic/006"
}
```
```

**Step 6: Validation**

- Compare CLAUDE.md tool orchestration instructions pre/post changes
- Verify all 8 tools documented with input/output schemas
- Test MCP tool execution (requires US-040/042/043/044 completion for tool implementations)
- Run validation test suite (if available) to confirm functional equivalence

**References to Implementation Standards:**
- patterns-core.md: Core development philosophy applies to orchestration instruction updates
- patterns-architecture.md: Follow established documentation patterns for CLAUDE.md updates

### Technical Tasks
- [ ] Update CLAUDE.md §Generate Command Instructions with `validate_artifact` tool call
- [ ] Update CLAUDE.md §Artifact Path Resolution Algorithm with `resolve_artifact_path` tool call
- [ ] Add CLAUDE.md §Task Management section with `get_next_task`, `update_task_status`, `add_task` tools
- [ ] Add CLAUDE.md §ID Management section with `get_next_available_id`, `reserve_id_range` tools
- [ ] Document `store_artifact` tool
- [ ] Provide input/output schemas for all 8 tools
- [ ] Add usage examples for each tool
- [ ] Add backward compatibility note (reference US-059)
- [ ] Validate functional equivalence (comparison test)

## Acceptance Criteria

### Scenario 1: Validation Tool Documented
**Given** CLAUDE.md §Generate Command Instructions updated
**When** Framework Maintainer reviews validation workflow
**Then** `validate_artifact` tool is documented with input/output schema and replaces AI inference instructions

### Scenario 2: Path Resolution Tool Documented
**Given** CLAUDE.md §Artifact Path Resolution Algorithm updated
**When** Framework Maintainer reviews path resolution workflow
**Then** `resolve_artifact_path` tool is documented with input/output schema and replaces AI inference instructions

### Scenario 3: Task Management Tools Documented
**Given** CLAUDE.md §Task Management section added
**When** Framework Maintainer reviews task management workflow
**Then** `get_next_task`, `update_task_status`, and `add_task` tools are documented with input/output schemas

### Scenario 4: ID Management Tools Documented
**Given** CLAUDE.md §ID Management section added
**When** Framework Maintainer reviews ID management workflow
**Then** `get_next_available_id` and `reserve_id_range` tools are documented with input/output schemas

### Scenario 5: All 8 Tools Documented
**Given** CLAUDE.md updated with MCP tool references
**When** all tool sections reviewed
**Then** all 8 tools documented (validate_artifact, resolve_artifact_path, get_next_task, update_task_status, get_next_available_id, reserve_id_range, store_artifact, add_task)

### Scenario 6: Functional Equivalence Validated
**Given** CLAUDE.md updated with MCP tool instructions
**When** validation test suite executes
**Then** all tests pass (same validation results as pre-refactoring baseline)

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 3 SP (CONSIDER threshold, below DON'T SKIP at 8+ SP)
- **Developer Count:** Single developer (documentation updates only)
- **Domain Span:** Single domain (documentation/orchestration instructions only, no code changes)
- **Complexity:** Low - Well-defined tool documentation with input/output schemas
- **Uncertainty:** Low - Clear tool specifications defined in PRD-006 v3 FR-06 through FR-11, FR-23, FR-24
- **Override Factors:** None - No cross-domain dependencies, no security-critical changes, no unfamiliar technology

**Conclusion:** Documentation-only story with straightforward tool schema documentation does not warrant task decomposition. Implementation can proceed as a single cohesive unit of work within one sprint.

## Definition of Done
- [ ] CLAUDE.md §Generate Command Instructions updated with `validate_artifact` tool call
- [ ] CLAUDE.md §Artifact Path Resolution Algorithm updated with `resolve_artifact_path` tool call
- [ ] CLAUDE.md §Task Management section added with `get_next_task`, `update_task_status`, `add_task` tools
- [ ] CLAUDE.md §ID Management section added with `get_next_available_id`, `reserve_id_range` tools
- [ ] `store_artifact` tool documented
- [ ] Input/output schemas provided for all 8 tools
- [ ] Usage examples provided for each tool
- [ ] Backward compatibility note added (reference US-059)
- [ ] Functional equivalence validated (comparison test passes)
- [ ] Code reviewed and approved
- [ ] Documentation updated (CHANGELOG or migration notes)
- [ ] Product Owner acceptance obtained

## Additional Information
**Suggested Labels:** refactoring, infrastructure, mcp-tools, documentation
**Estimated Story Points:** 3
**Dependencies:**
- **Depends On:** US-056 (Update CLAUDE.md to Orchestrate MCP Resources) - establishes orchestrator structure
- **Blocks:** US-060 (Integration Testing) - requires MCP tool orchestration for end-to-end testing
- **Related:** US-040 (Implement validate_artifact Tool), US-042 (Implement resolve_artifact_path Tool), US-043 (Implement store_artifact Tool), US-044 (Implement add_task Tool)
- **Related:** US-048/049/050/051 (Task Tracking and ID Management REST API) - provides microservice backend for task/ID tools

## Open Questions & Implementation Uncertainties

**No open implementation questions. All technical approaches clear from PRD-006 v3 §Requirements (FR-06 through FR-11, FR-12, FR-23, FR-24).**

**Key Decisions Already Made:**
- Tool input/output schemas: Defined in PRD-006 v3 FR-06 through FR-11, FR-23, FR-24
- Validation approach: Automated criteria (24/26) + manual review flags (2/26) per FR-22
- Path resolution approach: Pattern matching with variable substitution per FR-07
- Task management approach: Database-backed via Task Tracking microservice per FR-08, FR-09, FR-24
- ID management approach: Database-backed ID registry per FR-10, FR-11
- Backward compatibility approach: Fall back to AI inference when MCP Server unavailable (US-059)

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-010_claude_orchestration_integration_testing_v2.md`
- **Parent Epic:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`
- **Related Stories:** US-040 (validate_artifact Tool), US-042 (resolve_artifact_path Tool), US-043 (store_artifact Tool), US-044 (add_task Tool), US-048/049/050/051 (Task Tracking Microservice)

## Version History
- **v1 (2025-10-18):** Initial version
