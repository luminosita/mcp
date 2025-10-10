# Specialized Context: {Task Name}

**Document Version**: 1.0
**SDLC Phase**: {Vision|Epic|PRD|Backlog_Story|ADR|Tech_Spec|Code|Test}
**Parent Document**: `/CLAUDE.md`

---

## Purpose

This specialized context provides task-specific guidance for the **{Task Name}** phase of the SDLC. It supplements the root `/CLAUDE.md` with domain expertise, validation rules, and examples specific to this phase.

---

## Task-Specific Guidelines

### Domain Expertise for This Phase

{Describe what expertise is needed for this phase. Examples:}
- Product strategy and market analysis (for Vision)
- Epic decomposition and feature prioritization (for Epic)
- Requirements engineering and stakeholder alignment (for PRD)
- User story decomposition and acceptance criteria (for Backlog Story)
- Architecture decision documentation (for ADR)
- Technical design and API specification (for Tech Spec)

### Key Deliverables

**Primary Output**: {Description of main artifact}
**Secondary Output**: {Next-level generator prompt}

### Quality Standards for This Phase

- **Completeness**: {Phase-specific completeness criteria}
- **Clarity**: {Target audience and readability standards}
- **Actionability**: {What downstream consumers need}
- **Traceability**: {How to link to upstream artifacts}

---

## Template Location

**Path**: `/prompts/templates/{task}-template.xml`

**Template Sections**:
{List key sections from the template, e.g.:}
- Document Metadata
- Executive Summary / Overview
- {Section 1}
- {Section 2}
- {Section 3}
- Validation Checklist (in generator, not template)

**Validation Criteria**:
{Reference the validation checklist from the generator prompt}
- [ ] {Criterion 1}
- [ ] {Criterion 2}
- [ ] {Criterion 3}

---

## Input Requirements

### Required Files

**Mandatory Inputs**:
- `/CLAUDE.md` (root orchestration)
- `/prompts/{task}_generator.xml` (generator prompt)
- `/prompts/templates/{task}-template.xml` (output structure)
- `{upstream artifact path}` (dependency from prior phase)

**Optional Inputs**:
- `{additional context file 1}`
- `{additional context file 2}`

### Context Size Management

Target: <50% of Claude's context window (< 100k tokens)

If context exceeds target:
- Verify only immediate upstream artifact is loaded (not entire history)
- Check template size - consider splitting large templates
- Remove unnecessary historical context

---

## Output Specifications

### Terminal Artifact

**Path**: `/artifacts/{path}/{artifact}_v{N}.md`
**Format**: Markdown following template structure
**Versioning**: v1 (initial), v2 (first refinement), v3 (final)

### Next-Level Generator

**Path**: `/prompts/{next_task}_generator.xml`
**Format**: Valid XML following generator schema template
**Purpose**: Enable cascade to next SDLC phase

---

## Common Pitfalls

### Pitfall 1: {Common Issue}
**Problem**: {Description of what goes wrong}
**Solution**: {How to avoid it}
**Example**: {Concrete example}

### Pitfall 2: {Common Issue}
**Problem**: {Description}
**Solution**: {How to avoid it}
**Example**: {Concrete example}

### Pitfall 3: {Common Issue}
**Problem**: {Description}
**Solution**: {How to avoid it}
**Example**: {Concrete example}

---

## Example Outputs

### Example 1: {Scenario}

**Context**: {Brief description of input conditions}

**Good Output**:
```
{Example of high-quality output for this phase}
```

**Why It's Good**:
- {Reason 1}
- {Reason 2}
- {Reason 3}

**Bad Output**:
```
{Example of poor output}
```

**Why It's Bad**:
- {Problem 1}
- {Problem 2}
- {Problem 3}

### Example 2: {Another Scenario}
{Repeat format above}

---

## Research Document References

**Note**: These references are for documentation purposes only. Do NOT load these documents into context during execution.

- **Section {X.Y}**: {Topic} - {Brief description of relevant content}
- **Section {X.Z}**: {Topic} - {Brief description}
- **Lines {NNN-MMM}**: {Specific guidance or examples}

---

## Phase-Specific Anti-Hallucination Guidelines

### For This Phase, Ensure You:

1. **Ground in Input Artifacts**:
   - {Phase-specific grounding instruction}
   - Quote or reference specific sections from upstream artifacts
   - Don't fabricate details not present in inputs

2. **Mark Assumptions Explicitly**:
   - {Phase-specific assumption handling}
   - Use `[ASSUMPTION]` tag for inferences
   - Explain reasoning for assumptions

3. **Distinguish Facts from Inferences**:
   - {Phase-specific fact vs. inference guidance}
   - Be explicit about what's derived vs. what's in source material

4. **Request Clarification When Needed**:
   - {Phase-specific clarification scenarios}
   - If upstream artifact is ambiguous, note in output
   - Don't guess - ask or document uncertainty

---

## Iteration and Refinement

### Typical Issues in v1 → v2

**Common Critique Points**:
- {Issue 1 typically found in first iteration}
- {Issue 2}
- {Issue 3}

**How to Address**:
- {Solution pattern 1}
- {Solution pattern 2}
- {Solution pattern 3}

### v2 → v3 Focus Areas

**Polish and Finalize**:
- {Refinement focus 1}
- {Refinement focus 2}
- {Refinement focus 3}

**Strategy Document Update**:
Remember: At v3, HUMAN must manually update `/docs/context_engineering_strategy_v1.md` Section 8.2 with lessons learned from this phase.

---

## Related Commands

- `/generate {TASK-ID}` - Execute this generator
- `/refine {task}_generator` - Refine based on critique

---

## Validation Before Proceeding

Before marking this task complete, verify:
- [ ] All template sections are complete
- [ ] Validation checklist criteria met (from generator)
- [ ] Traceability to upstream artifacts established
- [ ] Next-level generator is valid XML
- [ ] Readability appropriate for target audience
- [ ] No critical issues in output

---

**Template Version**: 1.0
**Last Updated**: 2025-10-07
**Maintained By**: Context Engineering Framework
