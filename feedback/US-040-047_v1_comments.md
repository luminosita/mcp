# Feedback for Backlog Stories US-040 thru US-047

## General for all stories

### Open Questions
Convert Open Questions section into Decision Made section

### Hardcoded Paths in code snippets

**Issue:**

Paths must not be hardcoded. Examples of hardcoded paths

1.
```python
checklist_path = Path(f"resources/validation/{checklist_id}.json")
```

**Allowed URIs:**
1.
```python
return {"uri": f"mcp://resources/patterns/{name}", "content": content}
```
2.
```python
detail=f"Resource not found: mcp://resources/templates/{artifact_type}"
```

**Solution:**
Externalize all paths to configuration

**Rationale:**
Location of resource files can be changed and should not be hardcoded but configurable. URIs can remain in code since the actual routing path at the top of the corresponding method as a decorator (e.g., @app.get("/mcp/resources/templates/{artifact_type}")
)

---

## US-040

### Require Manual Review

**Issue:**

`requires_manual_review` flag should be `requires_agent_review`

Functional Requirements 4.
Tool flags manual criteria with `requires_manual_review: true`:
   - Readability checks
   - Appropriateness of content

**Solution:**

Convert recurrence of `requires_manual_review` into `requires_agent_review`

**Rationale:**
Readability checks and appropriateness of content should be done by AI Agent first. AI Agent can flag for further human review. We should first perform deterministic validation via script (tool), then AI Agent content review and finally human review only if needed.

---

## US-041

### Validation Extraction From Generators

**Issue:**

Functional Requirements, Step 1:

1. Extract validation criteria from 6 generator prompts:
   - epic-generator.xml
   - prd-generator.xml
   - hls-generator.xml (high-level-user-story-generator.xml)
   - backlog-story-generator.xml
   - tech-spec-generator.xml
   - adr-generator.xml

**Solution:**

All generators should be considered from validation checklists extraction:
   - product-vision-generator.xml
   - initiative-generator.xml
   - epic-generator.xml
   - prd-generator.xml
   - high-level-user-story-generator.xml
   - backlog-story-generator.xml
   - tech-spec-generator.xml
   - adr-generator.xml
   - spike-generator.xml
   - implementation-task-generator.xml
   - business-research-generator.xml
   - implementation-research-generator.xml

### Validation Category Type

**Issue:**

Functional Requirements, Step 2:

`validation_type`: "automated" or "manual", should be "automated", "agent", or "manual"

**Solution:**

Update `validation_type` -> "automated", "agent", or "manual"

---
pattern (string): Path pattern with variable placeholders (e.g., artifacts/epics/EPIC-{id}*_v{version}.md)
variables (dict): Variable substitutions (e.g., {id: "006", version: 1})

## US-042 - Needs rewrite (complex issues, changes the whole story)

### Input Pattern

**Issue:**

Input for the tool is wrong

Functional Requirements, step 1:
pattern (string): Path pattern with variable placeholders (e.g., artifacts/epics/EPIC-{id}*_v{version}.md)
variables (dict): Variable substitutions (e.g., {id: "006", version: 1})

Should be artifact_type, artifact_id, version (e.g., {type: "epic", id: "006", version: 1})

**Solution:**

Much simpler approach. No parsing of input is required

### Tool Response

**Issue:**

Response is wrong.

Functional Requirements, step 5:
Tool returns structured JSON response:
// Success (single match)
{
  "success": true,
  "path": "artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md",
  "match_count": 1
}

Should return MCP resource path (e.g., mcp://resources/artifacts/epic/006)

**Solution:**

Correct response to return MCP resource path

---

## US-043

### Metadata and File Path

**Issue:**

Functional Requirements, step 1:

```
Tool accepts three parameters:
   - `artifact_content` (string): Full artifact markdown text
   - `metadata` (dict): Artifact metadata including:
     - `artifact_id`: Artifact ID (e.g., "EPIC-006", "PRD-006")
     - `artifact_type`: Artifact type (e.g., "epic", "prd", "hls", "backlog_story")
     - `version`: Version number (integer, e.g., 1, 2, 3)
     - `status`: Artifact status (e.g., "Draft", "Approved", "Planned")
     - `parent_id`: Optional parent artifact ID (e.g., "INIT-001" for Epic-006)
     - `title`: Artifact title (for metadata indexing)
   - `file_path` (optional string): Override default file path for storage location
```

This is wrong. It should accept only one, artifact_content

**Solution:**
Run evaluation with other stories in HLS-008 and identify, if generator prompt can return metadata as JSON. If no, change requirements that tool should accept only one paramenter, artifact_content, and it should extract metadata out of the content, by parsing Markdown section "Metadata". If yes, keep second parameter (metadata) and pass the result from generator prompt

**Rationale:**
If we force AI Agent to provide tool with metadata we are not really helping AI Agent, rather making additional problem. We can change generators to return metadata as JSON. In that case we could pass second (metadata parameter).
`file_path` cannot be sent from AI Agent (client). This belong in main configuration and it is fixed

### Metadata and File Path

**Issue:**

Functional Requirements, step 3:

```
Tool generates storage path if not provided:
   - Default: `shared_artifacts/{artifact_type}/{artifact_id}_v{version}.md`
   - Example: `shared_artifacts/epics/EPIC-006_v1.md`
```

It should incorporate configured base_path from configuration and append `/{artifact_type}/{artifact_id}_v{version}.md` (e.g., {PATTERNS_BASE_DIR}/epic/006_v1.md)

**Solution:**

Make PATTERNS_BASE_DIR in configuration

### Metadata and File Path

**Issue:**

Functional Requirements, step 3:

Tool returns structured JSON response:
```json
{
    "success": true,
    "artifact_id": "EPIC-006",
    "artifact_type": "epic",
    "version": 1,
    "storage_path": "shared_artifacts/epics/EPIC-006_v1.md",
    "resource_uri": "mcp://resources/artifacts/epic/006",
    "metadata_path": "shared_artifacts/epics/EPIC-006_v1_metadata.json"
}
```

Too much information in response

**Solution:**
Only return `success` and `resource_uri`

---
