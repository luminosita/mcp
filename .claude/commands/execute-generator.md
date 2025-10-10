---
name: execute-generator
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
/execute-generator TASK-003
```

## Workflow

### Step 1: Parse Task from TODO.md
- Locate task by ID in `/TODO.md`
- Extract task metadata:
  - Generator prompt path
  - Required context files
  - Input artifacts (dependencies)
  - Validation criteria
  - Output paths

### Step 2: Check Specialized CLAUDE.md
- Determine specialized context file: `/prompts/CLAUDE-{task_name}.md`
  - Derive task_name from generator prompt filename (e.g., product_vision_generator.xml → product-vision)
- If file exists: Load it
- If missing:
  - **Prompt human**: "Specialized context `/prompts/CLAUDE-{task_name}.md` not found. Generate it now? (y/n)"
  - **If approved**: Generate from guidelines in main `/CLAUDE.md` "Specialized CLAUDE.md Files" section
  - **If declined**: Exit with error

### Step 3: Load Context
Required files for execution:
1. `/CLAUDE.md` (root orchestration)
2. `/prompts/CLAUDE-{task_name}.md` (specialized, from Step 2)
3. `/prompts/{task_name}_generator.xml` (the generator to execute)
4. `/prompts/templates/{artifact}-template.xml` (template referenced by generator)
5. Input artifacts (from task dependencies, e.g., `/artifacts/product_vision_v3.md`)

**Context Validation**:
- Verify all required files exist
- Check file sizes to ensure <50% context window usage
- If any file missing: Prompt human with clear error message

### Step 4: Execute Generator
1. Read generator XML content
2. Substitute placeholders:
   - `{UPSTREAM_ARTIFACT}` → content from input file
   - `{TEMPLATE}` → content from template file
   - `{ITERATION}` → version number (v1, v2, or v3)
3. Process generator instructions step-by-step
4. Generate outputs:
   - **Terminal artifact**: Primary deliverable (e.g., `/artifacts/product_vision_v1.md`)
   - **Next-level generator**: Prompt for next SDLC phase (e.g., `/prompts/epic_generator.xml`)

### Step 5: Save Outputs
- Write terminal artifact to path specified in generator `<output_format>`
- Write next-level generator to `/prompts/` directory
- Ensure proper file naming with version suffix

### Step 6: Validate Outputs
Run validation checklist from generator XML:
- [ ] Terminal artifact has all required template sections
- [ ] Readability check (manual Flesch >60 assessment)
- [ ] Traceability: References to upstream artifacts present
- [ ] Next generator: Valid XML syntax

**Report Results**:
```
✅ Terminal Artifact: /artifacts/product_vision_v1.md
✅ Next Generator: /prompts/epic_generator.xml

Validation Status:
✅ All template sections present (8/8)
⚠️  Readability: Manual check required
✅ Traceability: 3 references to product-idea.md
✅ Next generator: Valid XML

AI Context Report:
[RUN `/context` COMMAND AND PASTE OUTPUT HERE] 

Action Required:
1. Review artifact at /artifacts/product_vision_v1.md
2. Create critique file: /feedback/product_vision_v1_critique.md
3. If refinement needed, run: /refine-generator product_vision_generator
```

### Step 7: Update TODO.md
Update relevant task status in `/TODO.md`:
- Mark current task checkbox as complete (if final version v3)
- Update task status notes
- Add entry to task completion log if applicable

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
- `/refine-generator` - Iterate based on feedback

**See Also**:
- `/TODO.md` - Master task list
- `/CLAUDE.md` - Root orchestration guide
