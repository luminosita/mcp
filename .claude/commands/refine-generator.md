---
name: refine-generator
description: Refine generator prompt based on critique feedback and re-execute
args:
  - name: generator_name
    description: Generator name without .xml extension (e.g., product_vision_generator)
    required: true
---

# Refine Generator Command

This command implements the Self-Refine pattern (research Section 2.4) to improve generator prompts based on human critique feedback.

## Usage

```bash
/kickoff refine-generator product_vision_generator
```

## Workflow

### Step 1: Identify Current Iteration
- Locate generator: `/prompts/{generator_name}.xml`
- Read `<version>` metadata tag
- Determine current version (e.g., `1.1`)
- Calculate next version (e.g., `1.2`)
- Identify current artifact version (v1 or v2) based on generator version

### Step 2: Load Critique Feedback
- Determine critique file path: `/feedback/{artifact}_v{N}_critique.md`
- Example: `/feedback/product_vision_v1_critique.md`
- If file not found:
  - **Prompt human**: "Critique file not found. Create `/feedback/{artifact}_v{N}_critique.md` with feedback before refining."
  - Exit

### Step 3: Analyze Critique
Parse critique file for:
- **Completeness Issues**: Missing sections, incomplete information
- **Clarity Issues**: Confusing language, jargon, poor structure
- **Actionability Issues**: Vague next steps, missing details
- **Traceability Issues**: Missing references, unclear connections
- **Severity Ratings**: Critical, Major, Minor

**Prioritization**:
1. Critical issues (blockers)
2. Major issues (significant quality impact)
3. Minor issues (nice-to-have improvements)

### Step 4: Generate Refinement Plan
Create structured plan addressing each issue:

```markdown
## Refinement Plan for {generator_name} v{next_version}

### Issue 1: [Description from critique]
**Severity**: Critical
**Current Behavior**: [What generator does now]
**Proposed Fix**: [Specific change to generator prompt]
**Expected Improvement**: [How artifact v{N+1} will be better]

### Issue 2: [Description]
...
```

**Prompt human for approval**:
```
Refinement Plan Generated
-----------------------
Found 5 issues: 2 Critical, 2 Major, 1 Minor

Proposed changes to {generator_name}:
1. Add explicit instruction for quantified pain points in problem statement
2. Include SMART criteria validation checklist in output_format section
3. Enhance examples with concrete metrics
4. Add traceability prompt: "Reference product-idea.md using [source] notation"
5. Fix typo in template path reference

Proceed with these refinements? (y/n)
```

### Step 5: Apply Refinements
Update generator XML:

**Updated Sections**:
- `<metadata><version>`: Increment to next version
- `<instructions>`: Add/modify steps based on refinement plan
- `<output_format><validation_checklist>`: Add new validation criteria
- `<examples>` (if applicable): Enhance with better exemplars

**Preserve**:
- Original template references
- Core structure and logic
- Existing validations (don't remove, only add)

### Step 6: Re-Execute Generator
Run the refined generator (same as execute-generator command):
1. Load updated generator + all required context
2. Execute generation
3. Save new version artifact: `{artifact}_v{N+1}.md`
4. Save updated next-level generator (if applicable)

### Step 7: Compare Versions
Generate comparison report:

```markdown
## Artifact Comparison: v{N} → v{N+1}

### Improvements
✅ Problem statement now includes 3 quantified pain points (was 0)
✅ Success metrics follow SMART format (Specific, Measurable, Achievable, Relevant, Time-bound)
✅ Added 5 traceability references to product-idea.md

### Remaining Issues
⚠️  Readability: Still somewhat technical (manual Flesch check recommended)
⚠️  Epic generator: Missing error handling instructions (minor)

### Validation Checklist
✅ All template sections present (8/8) - IMPROVED from 6/8
✅ Quantified metrics present
✅ Traceability present
⚠️  Readability: Manual check required

Next Steps:
1. Review /artifacts/{artifact}_v{N+1}.md
2. If issues remain: Create /feedback/{artifact}_v{N+1}_critique.md
3. If acceptable: Proceed to next task or finalize as v3
```

### Step 8: Update Strategy Document (v2 → v3 only)
If refining from v2 to v3 (final iteration):
- Open `/docs/context_engineering_strategy_v1.md`
- Navigate to Section 8.2 "Generator Refinement Patterns"
- Add entry documenting lessons learned:

```markdown
#### Pattern: {Generator_Type} Refinement
**Issue Pattern**: [Common issues encountered across v1/v2]
**Solution**: [Effective refinement strategy]
**Applicability**: [When to apply this pattern to future generators]
**Evidence**: Improved validation score from X% to Y%
```

## Iteration Limits

**Standard Cycle**: 3 iterations (v1 → v2 → v3)
- **v1**: Initial generation
- **v2**: First refinement (addresses major issues)
- **v3**: Final refinement (polish + strategy update)

**Exceptional Cases** (requires human approval):
- If v3 still has critical issues: Discuss root cause (template? generator logic? input quality?)
- Consider template refinement or restructuring approach
- Document exception in strategy Section 8.4

## Self-Refine Pattern Application

Based on research Section 2.4, implement three-step workflow:

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
ERROR: Generator /prompts/{generator_name}.xml does not exist
Available generators:
- product_vision_generator.xml
- epic_generator.xml
```

### Error: Critique File Missing
```
ERROR: Critique file not found
Expected path: /feedback/{artifact}_v{N}_critique.md

Please create critique file with the following structure:
## Completeness
[Issues with missing/incomplete sections]

## Clarity
[Issues with readability/understanding]

## Actionability
[Issues with vague/unclear next steps]

## Traceability
[Issues with missing references]

## Severity
Critical | Major | Minor
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

## Implementation Notes

**For Current PoC (Phase 1)**:
- Human performs all steps manually following this guide
- Judgment required for refinement plan approval
- Human writes updated generator XML

**For Phase 2 (Semi-Automated)**:
- Automated critique parsing
- AI-generated refinement plan
- Human approves plan before application
- Automated re-execution and comparison

**For Phase 3 (Fully Automated)**:
- Chain-of-Verification self-critique (research Section 2.4)
- Automated refinement with threshold-based approval
- Human intervention only on quality failures (<80% checklist pass rate)

---

**Related Commands**:
- `/kickoff execute-generator` - Initial generator execution
- `/kickoff validate-artifact` - Quality assessment

**See Also**:
- `/docs/context_engineering_strategy_v1.md` - Section 6.3
- Research document - Section 2.4 (Self-Correction Frameworks)
