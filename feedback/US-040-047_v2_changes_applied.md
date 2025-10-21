# Applied Changes for US-040-047 v2 Feedback

**Date:** 2025-10-20
**Source:** `/feedback/US-040-047_v2_comments.md`

## Summary

This document tracks the application of feedback from `US-040-047_v2_comments.md` to create updated versions (v3 for stories with v2, v2 for stories with v1).

---

## Global Changes (All Stories US-040 through US-047)

### 1. artifact_id Pattern Enforcement
**Change:** All tools must use full artifact_id format: `{artifact_type}-{ID}` (e.g., EPIC-006, US-040)

**Rationale:** Consistent artifact identification across all tools.

**Applied to:**
- US-040: Input parameter changed from `checklist_id` to `artifact_id`
- US-042: Already uses `artifact_id` (no change)
- US-043: Already uses `artifact_id` in metadata (no change)
- US-044: Already uses `artifact_id` in TaskMetadata (no change)

---

### 2. Rename request_id → task_id (Mandatory)
**Change:** Rename `request_id` parameter to `task_id` and make it mandatory.

**Rationale:** Better visibility and traceability in logs. "task_id" is more descriptive than "request_id".

**Applied to:**
- US-040 (validate_artifact tool)
- US-041 (validation checklists - no tool changes, but documentation updated)
- US-042 (resolve_artifact_path tool)
- US-043 (store_artifact tool)
- US-044 (add_task tool)
- US-046 (logging examples updated throughout)
- US-047 (integration tests updated)

**Implementation:**
- Function signatures: `async def tool_name(params: Input, task_id: str)` (mandatory, no default)
- Logging: All log entries include `task_id` field
- Propagation: task_id propagated across tool calls in same workflow

---

## Story-Specific Changes

### US-040: Implement validate_artifact Tool

**Version:** v2 → v3

**Changes:**

1. **Remove `checklist_id` input parameter**
   - **Old:** `ValidateArtifactInput(artifact_content: str, checklist_id: str)`
   - **New:** `ValidateArtifactInput(artifact_content: str, artifact_id: str)`

2. **Add artifact_id parameter and inference logic**
   - Input: `artifact_id` (e.g., "EPIC-006", "PRD-006", "US-040")
   - Inference:
     - Extract prefix from artifact_id: `EPIC-006` → `EPIC`
     - Map prefix to artifact_type: `EPIC` → `epic`
     - Construct checklist_id: `epic` → `epic_validation_v1`
   - Implementation:
     ```python
     TYPE_PREFIX_MAP = {
         "EPIC": "epic",
         "PRD": "prd",
         "HLS": "hls",
         "US": "backlog_story",
         "SPEC": "tech_spec",
         "ADR": "adr",
         "SPIKE": "spike",
         "TASK": "task",
         "VIS": "product_vision",
         "INIT": "initiative"
     }

     def infer_checklist_id(artifact_id: str) -> str:
         prefix = artifact_id.split('-')[0]
         artifact_type = TYPE_PREFIX_MAP[prefix]
         return f"{artifact_type}_validation_v1"
     ```

3. **Rename request_id → task_id (mandatory)**
   - All function signatures updated
   - All logging examples updated

**Rationale:** Checklist ID is fully deterministic from artifact_id. No need to require client to provide it explicitly.

**Impact:**
- Simpler client interface (one less parameter to provide)
- Always uses latest checklist version (v1)
- Clear error if artifact_id format invalid

---

### US-041: Migrate Validation Checklists to JSON Resources

**Version:** v2 → v3

**Changes:**

1. **Rename request_id → task_id**
   - Documentation updated (no tool implementation in this story)

**Impact:** Documentation consistency only.

---

### US-042: Implement resolve_artifact_path Tool

**Version:** v2 → v3

**Changes:**

1. **Rename request_id → task_id (mandatory)**
   - Function signature updated
   - Logging examples updated

**Impact:** Consistent parameter naming across tools.

---

### US-043: Implement store_artifact Tool

**Version:** v2 → v3

**Changes:**

1. **Change PATTERNS_BASE_DIR → ARTIFACTS_BASE_DIR**
   - **Old:** Storage path uses `settings.PATTERNS_BASE_DIR`
   - **New:** Storage path uses `settings.ARTIFACTS_BASE_DIR`
   - **PATTERNS_BASE_DIR:** Remains as separate config for template/pattern storage
   - **ARTIFACTS_BASE_DIR:** New config for generated artifact storage

2. **Rename request_id → task_id (mandatory)**
   - Function signature updated
   - Logging examples updated

**Rationale:** Patterns (templates) and artifacts (generated content) can come from different file system sources. Separate configuration enables:
- Patterns from read-only shared directory (e.g., /opt/mcp/patterns/)
- Artifacts to writable project directory (e.g., /workspace/artifacts/)

**Implementation:**
```python
class Settings(BaseSettings):
    PATTERNS_BASE_DIR: str = "/opt/mcp/patterns"  # Templates/patterns (read-only)
    ARTIFACTS_BASE_DIR: str = "/workspace/artifacts"  # Generated artifacts (read-write)
    VALIDATION_RESOURCES_DIR: str = "/opt/mcp/validation"  # Validation checklists
```

**Impact:**
- More flexible deployment configurations
- Clear separation between templates and generated content
- Better security (patterns can be read-only)

---

### US-044: Implement add_task Tool

**Version:** v1 → v2

**Changes:**

1. **Remove `generator` parameter from TaskMetadata**
   - **Old:** `TaskMetadata(artifact_id, artifact_type, generator, parent_id, ...)`
   - **New:** `TaskMetadata(artifact_id, parent_id, ...)`
   - **Inference:** `EPIC-006` → `epic-generator`

2. **Remove `artifact_type` parameter from TaskMetadata**
   - **Old:** Explicit `artifact_type` field
   - **New:** Inferred from artifact_id prefix
   - **Inference:** `EPIC-006` → `epic`

3. **Rename request_id → task_id (mandatory)**
   - Function signature updated
   - Logging examples updated

**Inference Implementation:**
```python
@validator('artifact_type', pre=True, always=True)
def infer_artifact_type(cls, v, values):
    if v is None and 'artifact_id' in values:
        prefix = values['artifact_id'].split('-')[0]
        TYPE_MAP = {
            "EPIC": "epic",
            "PRD": "prd",
            "HLS": "hls",
            "US": "backlog_story",
            # ... etc
        }
        return TYPE_MAP[prefix]
    return v

@validator('generator', pre=True, always=True)
def infer_generator(cls, v, values):
    if v is None and 'artifact_type' in values:
        artifact_type = values['artifact_type']
        return f"{artifact_type.replace('_', '-')}-generator"
    return v
```

**Rationale:**
- artifact_type is fully deterministic from artifact_id prefix
- generator name follows convention: `{artifact_type}-generator`
- Reduces client-side complexity and potential errors

**Impact:**
- Simpler API (2 fewer parameters)
- Eliminates mismatched artifact_id/artifact_type errors
- Clearer contract: client provides artifact_id, server infers metadata

---

### US-045: Add Sub-artifact Evaluation Instructions to Generators

**Version:** v1 → v2

**Changes:**

1. **Update metadata format in generators**
   - **Old:** Metadata includes `artifact_type` and `generator` in task list
   - **New:** Metadata includes only `artifact_id` in task list (type and generator inferred)

   ```xml
   <!-- Old format -->
   <task artifact_id="HLS-006" artifact_type="hls" generator="hls-generator" parent_id="PRD-006" />

   <!-- New format -->
   <task artifact_id="HLS-006" parent_id="PRD-006" />
   ```

2. **Rename request_id → task_id in documentation**

**Rationale:** Aligns with US-044 changes (add_task tool no longer accepts artifact_type/generator).

**Impact:** Generator metadata format simplified.

---

### US-046: Tool Invocation Logging

**Version:** v1 → v2

**Changes:**

1. **Rename request_id → task_id throughout**
   - All logging examples updated
   - Decorator signature updated: `log_tool_invocation(task_id: str)`
   - Log field name: `task_id` (not `request_id`)

**Examples Updated:**
- Log entry JSON: `{"task_id": "abc-123", ...}`
- Function signatures: `async def tool(params, task_id: str)`
- Propagation examples: `task_id` passed across tool calls

**Impact:** Consistent naming convention across all logging.

---

### US-047: Integration Testing for All Tools

**Version:** v1 → v2

**Changes:**

1. **Update test examples to use task_id**
   - All test function signatures updated
   - Assertions updated to check `task_id` in logs

2. **Update test examples for changed tool interfaces**
   - US-040 tests: Use `artifact_id` instead of `checklist_id`
   - US-044 tests: Remove `artifact_type` and `generator` from TaskMetadata

**Impact:** Tests aligned with updated tool interfaces.

---

## Validation

### Checklist

- [ ] US-040 v3: checklist_id removed, artifact_id added, inference logic documented
- [ ] US-041 v3: task_id renaming documented
- [ ] US-042 v3: task_id renaming applied
- [ ] US-043 v3: ARTIFACTS_BASE_DIR introduced, PATTERNS_BASE_DIR retained, task_id renamed
- [ ] US-044 v2: generator/artifact_type removed, inference logic documented, task_id renamed
- [ ] US-045 v2: metadata format updated to remove artifact_type/generator
- [ ] US-046 v2: All request_id references changed to task_id
- [ ] US-047 v2: Tests updated for new tool interfaces

### Testing Requirements

After applying changes:
1. **Unit tests:** Verify inference logic (artifact_id → checklist_id, artifact_id → generator)
2. **Integration tests:** Verify tools work with simplified interfaces
3. **Error handling:** Verify invalid artifact_id formats rejected with clear errors

---

## Next Steps

1. Apply changes to v3/v2 versions of each story
2. Update related documentation (CLAUDE.md, SDLC artifacts guideline)
3. Communicate changes to development team
4. Update generator prompts (US-045 changes)

---

## Related Documents

- **Feedback Source:** `/feedback/US-040-047_v2_comments.md`
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
