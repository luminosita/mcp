---
name: generate
description: Execute a generator prompt from TODO.md task list
args:
  - name: task_id
    description: Task ID from TODO.md (e.g., TASK-003)
    required: true
---

# Execute Generator Command

This command executes a generator prompt based on the task ID specified in `/TODO.md`.

## Usage

```bash
/generate TASK-003
```

## Workflow

### Step 1: Parse Task from TODO.md
- Locate task by ID in `/TODO.md`
- Extract task metadata:
  - Generator prompt path
  - Input artifacts (dependencies)

### Step 2: Load Context & Validate Inputs
Required files for execution:
1. `/CLAUDE.md` (root orchestration)
2. `/prompts/{task_name}_generator.xml` (the generator to execute)
  - Derive task_name from generator prompt filename (e.g., product_vision_generator.xml → product-vision)
3. Input artifacts (from task dependencies, e.g., `/artifacts/product_vision_v3.md`)

**Context Validation**:
- Verify all required files exist
- Check file sizes to ensure <50% context window usage
- **Validate input artifact status (production requirement)**:
  - Parse artifact metadata section for Status field
  - Primary input artifacts should have Status = "Approved"
  - Exception: Research phase artifacts (business_research.md, implementation_research.md) are always approved sources
  - Exception: PoC/development mode may proceed with "Draft" status at risk of rework
- If any file missing: Prompt human with clear error message

### Step 3: Execute Generator
1. Read generator XML content
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

**Report Results**:
```
✅ Terminal Artifact: /artifacts/product_vision_v1.md

Validation Status:
✅ Status set to "Draft" in metadata
✅ All template sections present (8/8)
⚠️  Readability: Manual check required
✅ Traceability: 3 references to product-idea.md

AI Context Report:
[RUN `/context` COMMAND AND PASTE OUTPUT HERE]

Action Required:
1. Review artifact at /artifacts/product_vision_v1.md
2. Create critique file: /feedback/product_vision_v1_critique.md
3. If refinement needed, run: /refine product_vision_generator
```

## Error Handling

### Error: Task ID Not Found
```
ERROR: Task TASK-999 not found in /TODO.md
Please verify task ID and try again.
```

### Error: Missing Dependency
```
ERROR: Task TASK-003 depends on TASK-001 (not completed)
Complete prerequisite tasks first:
- TASK-001: Create Product Idea Stub [Status: ⏳ Pending]
```

### Error: Input Artifact Not Approved
```
ERROR: Input artifact has invalid status for production use
Required: Status = "Approved"
Found: Status = "Draft" in /artifacts/product_vision_v1.md

This artifact requires critique and refinement before use as input.

Action Required:
1. Complete critique cycle (e.g., TASK-005: Critique Product Vision v1)
2. Refine artifact based on feedback (e.g., TASK-006: Refine to v2)
3. Obtain approval after final refinement (v3)
4. Update artifact status to "Approved"
5. Retry generator execution

Note: For PoC/development, you may proceed with Draft status at risk of rework
if upstream artifact changes significantly during refinement.
```

### Error: Generator File Not Found
```
ERROR: Generator /prompts/product_vision_generator.xml does not exist
This generator should be created by TASK-002.
Complete TASK-002 first or create generator manually.
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
