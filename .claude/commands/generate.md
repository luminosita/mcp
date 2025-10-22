---
name: generate
description: Execute a generator prompt from TODO.md task list
args:
  - name: task_id
    description: Task ID from TODO.md (e.g., TODO-003)
    required: true
---

# Execute Generator Command

This command executes a generator prompt based on the task ID specified in `/TODO.md`.

## Usage

```bash
/generate TODO-003
```

## Workflow

### Step 1: Parse Task from TODO.md
- Locate task by ID in `/TODO.md`
- Extract task metadata:
  - Generator name
  - Input artifacts (dependencies)

### Step 2: Load Generator Content (MCP-First with Fallback)

**MCP Prompt Strategy (US-036):**
1. **Primary path**: Call MCP prompt `mcp://prompts/generator/{artifact_name}`
   - Derive `artifact_name` from generator name (e.g., "epic-generator" → "epic")
   - MCP prompt returns generator XML content
   - Log MCP prompt call with timestamp, artifact_name, duration, status

2. **Fallback path**: If MCP Server unavailable or prompt call fails:
   - Log warning: "MCP Server unavailable, falling back to local generator file"
   - Read generator from local file: `/prompts/{generator_name}-generator.xml`
   - Continue execution with local file content

**Implementation:**
```
# Try MCP prompt first
TRY:
  generator_content = call_mcp_prompt("mcp://prompts/generator/{artifact_name}")
  log_info({"mcp_prompt_call": "success", "artifact_name": artifact_name, "duration_ms": duration})
EXCEPT MCP_UNAVAILABLE or PROMPT_NOT_FOUND:
  log_warning({"mcp_prompt_call": "failed", "artifact_name": artifact_name, "fallback": "local_file"})
  generator_content = read_file("/prompts/{generator_name}-generator.xml")
```

### Step 3: Load Context & Validate Inputs
Required files for execution:
1. `/CLAUDE.md` (root orchestration)
2. Generator XML content (from Step 2: MCP prompt or local file)
3. Input artifacts

**Path Resolution**:
- All artifact paths defined in CLAUDE.md Artifact Path Patterns section
- Use path patterns like: artifacts/product_visions/VIS-{id}_product_vision_v{version}.md
- For links/URLs in artifacts, use {SDLC_DOCUMENTS_URL} placeholder format

**Context Validation**:
- Verify all files exist and check sizes (<50% context window)
- **Input Classification Handling** (see CLAUDE.md Input Classification System):
  - **Mandatory inputs**: Must exist. Generator FAILS if missing. Status must be "Approved" (production).
  - **Recommended inputs**: WARN if missing. Quality reduced by ~20-30% without. Status should be "Approved".
  - **Conditional inputs**: Load only if condition met. No warning if not loaded.
  - **Mutually Exclusive inputs**: Exactly ONE of group required. FAIL if none or multiple provided.
- **Status Validation (Production)**:
  - Mandatory/Recommended inputs should have Status = "Approved"
  - Exception: Research artifacts (business_research.md, implementation_research.md) always approved
  - Exception: PoC/development may proceed with "Draft" status (risk of rework)

### Step 4: Execute Generator
1. Use generator XML content from Step 2 (MCP prompt or local file)
2. Substitute placeholders:
   - `{UPSTREAM_ARTIFACT}` → content from input file
   - `{TEMPLATE}` → content from template file
   - `{ITERATION}` → version number (v1, v2, or v3)
3. Run generator
4. **IMPORTANT: Set artifact Status to "Draft"**
   - All newly generated artifacts MUST have `Status: Draft` in metadata section
   - Status lifecycle: Draft → Review → Approved → Planned → In Progress → Completed
   - Only human approval can change Status from "Draft" to "Approved"
   - Never generate artifacts with Status: Planned, Approved, or any other non-Draft status
5. If generator succesfully created artifact, update `TODO.md`

**Report Results**:
```
✅ Terminal Artifact: artifacts/product_visions/VIS-001_product_vision_v1.md
(Path pattern: artifacts/product_visions/VIS-{id}_product_vision_v{version}.md - see CLAUDE.md)

Generator Source: MCP Prompt (mcp://prompts/generator/product-vision) ✅
└─ Latency: 245ms (p95 target: <500ms) ✅
└─ Fallback Used: No

MCP Prompt Call Log:
{
  "timestamp": "2025-10-21T12:00:00Z",
  "command": "/generate",
  "task_id": "TODO-003",
  "generator_name": "product-vision",
  "artifact_name": "product-vision",
  "mcp_prompt_uri": "mcp://prompts/generator/product-vision",
  "mcp_call_status": "success",
  "mcp_duration_ms": 245,
  "fallback_used": false,
  "generator_content_length": 15234
}

Validation Status:
✅ CQ-01: Status set to "Draft" in metadata (content quality)
✅ CQ-02: All template sections present (8/8) (content quality)
⚠️  CC-03: Readability: Manual check required (consistency)
✅ TR-01: Traceability: 3 references to product-idea.md (traceability)

Note: Criterion IDs help identify specific validation failures. See validation_checklist in generator XML.

AI Context Report:
[RUN `/context` COMMAND AND PASTE OUTPUT HERE]

Action Required:
1. Review artifact at artifacts/product_visions/VIS-001_product_vision_v1.md
2. Create critique file: /feedback/product_vision_v1_critique.md
3. If refinement needed, run: /refine product-vision
```

**Report Results (Fallback Used)**:
```
✅ Terminal Artifact: artifacts/epics/EPIC-001_user_management_v1.md

Generator Source: Local File (fallback) ⚠️
└─ MCP Server: Unavailable (connection timeout)
└─ Fallback File: /prompts/epic-generator.xml ✅

MCP Prompt Call Log:
{
  "timestamp": "2025-10-21T12:05:00Z",
  "command": "/generate",
  "task_id": "TODO-050",
  "generator_name": "epic-generator",
  "artifact_name": "epic",
  "mcp_prompt_uri": "mcp://prompts/generator/epic",
  "mcp_call_status": "failed",
  "mcp_error": "Connection timeout",
  "fallback_used": true,
  "fallback_path": "/prompts/epic-generator.xml",
  "fallback_status": "success",
  "generator_content_length": 12876
}

Validation Status:
[... validation results ...]

Action Required:
1. ⚠️  Check MCP Server availability (MCP prompt call failed)
2. Review artifact at artifacts/epics/EPIC-001_user_management_v1.md
3. Create critique file if needed
```

## Error Handling

### Error: Task ID Not Found
```
ERROR: Task TODO-999 not found in /TODO.md
Please verify task ID and try again.
```

### Error: Missing Dependency
```
ERROR: Task TODO-003 depends on TODO-001 (not completed)
Complete prerequisite tasks first:
- TODO-001: Create Product Idea Stub [Status: ⏳ Pending]
```

### Error: Input Artifact Not Approved
```
ERROR: Input artifact has invalid status for production use
Required: Status = "Approved"
Found: Status = "Draft" in /artifacts/product_visions/VIS-001_AI_Agent_MCP_Server_v1.md

This artifact requires critique and refinement before use as input.

Action Required:
1. Complete critique cycle (e.g., TODO-005: Critique Product Vision v1)
2. Refine artifact based on feedback (e.g., TODO-006: Refine to v2)
3. Obtain approval after final refinement (v3)
4. Update artifact status to "Approved"
5. Retry generator execution

Note: For PoC/development, you may proceed with Draft status at risk of rework
if upstream artifact changes significantly during refinement.
```

### Error: Recommended Input Missing
```
⚠️ WARNING: Recommended input artifact not found
Input: Business Research (artifacts/research/{product_name}_business_research.md)
Classification: RECOMMENDED
Impact: Output quality reduced by ~25% without market context and user personas

Proceed without recommended input? (y/n)
Note: Generated artifact will be based solely on mandatory inputs.
```

### Error: MCP Prompt Not Found (with Fallback)
```
⚠️  WARNING: MCP prompt not found, attempting fallback
MCP Prompt: mcp://prompts/generator/product-vision
MCP Server Response: 404 Not Found
Fallback: Reading local file /prompts/product-vision-generator.xml
Status: Fallback successful, continuing execution
```

### Error: MCP Server Unavailable (with Fallback)
```
⚠️  WARNING: MCP Server unavailable, falling back to local generator file
MCP Prompt: mcp://prompts/generator/epic
Error: Connection refused or timeout
Fallback: Reading local file /prompts/epic-generator.xml
Status: Fallback successful, continuing execution
```

### Error: Generator File Not Found (After Fallback Failed)
```
ERROR: Generator not available via MCP or local file
MCP Prompt: mcp://prompts/generator/product-vision (404 Not Found)
Local File: /prompts/product-vision-generator.xml (File not found)
This generator should be created by TODO-002.
Complete TODO-002 first or create generator manually.
```

### Error: Malformed Generator XML from MCP
```
⚠️  WARNING: Invalid generator XML from MCP Server, attempting fallback
MCP Prompt: mcp://prompts/generator/spike
Error: XML parsing failed (malformed content)
Fallback: Reading local file /prompts/spike-generator.xml
Status: Fallback successful, continuing execution
```

### Error: Context Window Overflow
```
WARNING: Context size exceeds 50% threshold
Current: 105k tokens / 200k limit (52.5%)
Recommendation: Split large templates or reduce input artifact size
Proceed anyway? (y/n)
```
---

**Related Commands**:
- `/refine` - Iterate based on feedback

**See Also**:
- `/TODO.md` - Master task list
- `/CLAUDE.md` - Root orchestration guide
