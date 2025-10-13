---
name: refine
description: Refine generator prompt based on critique feedback and re-execute
args:
  - name: generator_name
    description: Generator name without "-generator.xml" suffix (e.g., product-vision)
    required: true
---

# Refine Generator Command

This command implements the Self-Refine pattern (research Section 2.4) to improve generator prompts based on human critique feedback.

## Usage

```bash
/refine product-vision
```

## Workflow

### Step 1: Identify Current Iteration
- Locate generator: `/prompts/{generator_name}-generator.xml`
- Locate artifact template: `/prompts/templates/{artifact}-template.xml`
  - Artifact is the same as generator_name (e.g., product-vision -> product-vision)
- Read generator `<version>` metadata tag
- Read artifact template `<version>` metadata tag
- Determine current versions (e.g., `1.1`)
- Calculate next versions (e.g., `1.2`)

### Step 2: Load Critique Feedback
- Determine critique file path: `/feedback/{artifact}_v{N}_critique.md`
- Example: `/feedback/product_vision_v1_critique.md`
- If file not found:
  - **Prompt human**: "Critique file not found. Create `/feedback/{artifact}_v{N}_critique.md` with feedback before refining."
  - Exit

### Step 3: Analyze Critique
Parse critique file for validation categories:
- **Content Quality (CQ-##)**: Missing sections, incomplete information, unclear explanations
- **Traceability (TR-##)**: Missing references, unclear connections to input artifacts
- **Consistency (CC-##)**: Terminology inconsistencies, formatting issues, readability problems
- **Severity Ratings**: Critical, Major, Minor

Note: Validation criterion IDs (e.g., CQ-03, TR-01) align with generator validation_checklist.
Reference specific IDs in critique to pinpoint failures.

**Prioritization**:
1. Critical issues (blockers)
2. Major issues (significant quality impact)
3. Minor issues (nice-to-have improvements)

### Step 4: Generate Refinement Plan

**IMPORTANT** Refinement plan must include generator AND optional artifact template refinements

Create structured plan addressing each issue:

```markdown
## Refinement Plan for {generator_name} v{generator_next_version}

### Issue 1: [Description from critique]
**Severity**: Critical
**Current Behavior**: [What generator does now]
**Proposed Fix**: [Specific change to generator prompt]
**Expected Improvement**: [How artifact v{N+1} will be better]

### Issue 2: [Description]
...

## Refinement Plan for {artifact} Template v{artifact_template_next_version}

### Issue 1: [Description from critique]
**Severity**: Critical
**Current Behavior**: [What artifact template defines now]
**Proposed Fix**: [Specific change to artifact template]
**Expected Improvement**: [How artifact v{N+1} will be better]

### Issue 2: [Description]
...
```

**Prompt human for approval**:
```
Refinement Plan Generated
-----------------------
Found 5 issues: 2 Critical, 2 Major, 1 Minor

Proposed changes to {generator_name} and {artifact} template:
1. Add explicit instruction for quantified pain points in problem statement
2. Include SMART criteria validation checklist in output_format section
3. Enhance examples with concrete metrics
4. Add traceability prompt: "Reference product-idea.md using [source] notation"
5. Fix typo in template path reference

Proceed with these refinements? (y/n)
```

### Step 5: Apply Generator Refinements
Update generator XML:

**Updated Sections**:
- `<metadata><version>`: Increment to next generator version
- `<instructions>`: Add/modify steps based on generator refinement plan
- `<output_format><validation_checklist>`: Add new validation criteria
- `<examples>` (if applicable): Enhance with better exemplars

**Preserve**:
- Original template references
- Core structure and logic
- Existing validations (don't remove, only add)

### Step 6: Apply Template Refinements
Update artifact template XML:

**Updated Sections**:
- `<metadata><version>`: Increment to next artifact template version
- `<instructions>`: Add/modify steps based on template refinement plan
- `<output_format><validation_checklist>`: Add new validation criteria
- `<examples>` (if applicable): Enhance with better exemplars

**Preserve**:
- Core structure and logic
- Existing validations (don't remove, only add)

### Step 7: Re-Execute Generator
Evaluate refinements impact on the generated artifact, present the artifact refinement report to human and ASK human to decide to simply apply refinements to the artifact directly, or to regenerate the entire artifact

If human decides to simply apply refinements, proceed to apply refinements, ignore the steps to regenerate artifact:
1. Save new version artifact: `{artifact}_v{N+1}.md`

If human decides to regenerate, only then run the refined generator (/generate command):
1. Load updated generator + all required context
2. Load updated artifact template
3. Execute generation
4. Save new version artifact: `{artifact}_v{N+1}.md`

Note: Artifact paths follow patterns defined in CLAUDE.md Artifact Path Patterns section.

### Step 8: Compare Versions
Generate comparison report:

```markdown
## Artifact Comparison: v{N} → v{N+1}

### Improvements
✅ CQ-01: Problem statement now includes 3 quantified pain points (was 0) (content quality)
✅ CQ-02: Success metrics follow SMART format (Specific, Measurable, Achievable, Relevant, Time-bound) (content quality)
✅ TR-01: Added 5 traceability references to product-idea.md (traceability)

### Remaining Issues
⚠️  CC-03: Readability: Still somewhat technical (manual Flesch check recommended) (consistency)
⚠️  CQ-05: Epic generator: Missing error handling instructions (minor) (content quality)

### Validation Checklist
✅ CQ-01-CQ-08: All template sections present (8/8) - IMPROVED from 6/8
✅ CQ-03: Quantified metrics present
✅ TR-01-TR-02: Traceability present
⚠️  CC-03: Readability: Manual check required

Note: Criterion IDs (CQ-##, TR-##, CC-##) help trace specific validation failures.

Next Steps:
1. Review artifacts/{artifact}_v{N+1}.md
2. If issues remain: Create /feedback/{artifact}_v{N+1}_critique.md
3. If acceptable: Proceed to next task or finalize as v3
```

## Iteration Limits

**Standard Cycle**: 3 iterations (v1 → v2 → v3)
- **v1**: Initial generation
- **v2**: First refinement (addresses major issues)
- **v3**: Final refinement (polish + human strategy update required)

**Exceptional Cases** (requires human approval):
- If v3 still has critical issues: Discuss root cause (template? generator logic? input quality?)
- Consider template refinement or restructuring approach
- Document exception in strategy Section 8.4

## Self-Refine Pattern Application

Implement three-step workflow:

### Generate Initial Output (already done in previous execution)
- v1 artifact exists

### Provide Constructive Feedback
- Human creates critique with specific criteria
- Focuses on: completeness, clarity, actionability, traceability

### Refine Based on Feedback
- Update generator prompt (this command)
- Re-execute
- Compare results

## Error Handling

### Error: Generator Not Found
```
ERROR: Generator /prompts/{generator_name}-generator.xml does not exist
Available generators:
- product-vision-generator.xml
- epic-generator.xml
```

### Error: Artifact Template Not Found
```
ERROR: Generator /prompts/{artifact}-template.xml does not exist
Available artifact templates:
- product-vision-template.xml
- epic-template.xml
```

### Error: Critique File Missing
```
ERROR: Critique file not found
Expected path: /feedback/{artifact}_v{N}_critique.md

Please create critique file with the following structure:

## Content Quality (CQ-##)
[Issues with missing/incomplete sections, unclear explanations]
- Reference specific criterion IDs from generator validation_checklist (e.g., CQ-03)

## Traceability (TR-##)
[Issues with missing references to input artifacts, unclear connections]
- Reference specific criterion IDs (e.g., TR-01, TR-02)

## Consistency (CC-##)
[Issues with terminology inconsistencies, formatting problems, readability]
- Reference specific criterion IDs (e.g., CC-03)

## Severity
Critical | Major | Minor

Note: Criterion IDs help trace specific validation failures in generator validation_checklist.
```

### Error: Maximum Iterations Reached
```
WARNING: Generator already at v3 (maximum iterations)
If quality issues remain, consider:
1. Review template structure (may need fundamental changes)
2. Check input artifact quality
3. Consult strategy document Section 8 for patterns
4. Document exception case

Proceed with v4 anyway? (requires justification)
```

---

**Related Commands**:
- `/generate` - Initial generator execution

**See Also**:
- `/TODO.md` - Master task list
- `/CLAUDE.md` - Root orchestration guide
