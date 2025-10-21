# Feedback for Backlog Stories US-040 thru US-047 (version 2)

## General for all stories

artifact_id for all tools must have full pattern: {artifact_id} = {artifact_type} + {ID} (e.g., EPIC-006)

### Validate Tool

**Issue:**

Checklist ID as an input parameter is invalid.

**Solution:**
Remove Checklist ID as an input parameter

**Rationale:**
Checklist ID is inferred from articfact_type, which is inferred from artifact_id. Validation Tool should always use the latest version
---

### Request ID

**Issue:**

Every MCP tool call has request_id as an optional parameter.

**Solution:**
request_id must be mandatory and renamed to task_id

**Rationale:**
If we call it task_id we will have better visibility and traceability in logs
---

### Store Artifact Tool

**Issue:**
PATTERNS_BASE_DIR

**Solution:**
Should use ARTIFACTS_BASE_DIR. Do not rename PATTERNS_BASE_DIR. Introduce new configuration field

**Rationale:**
Patterns and artifacts can easily come from two separate file system sources and need to maintain separate base directory

---

### Add Task

**Issue:**
add_task has generator and artifact_type as input parameters

**Solution:**
Remove both

**Rationale:**
artifact_type is inferred from artifact_id (EPIC-006 -> epic), generator_name is inferred from artifact_id (EPIC-006 -> epic-generator)
