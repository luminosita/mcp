# Context Engineering Framework - Root Orchestration

## Project Overview

**Name**: Context Engineering Proof-of-Concept
**Purpose**: Demonstrate recursive prompt generation following SDLC phases
**Target Product**: CLI tool (specifics in `/docs/product-idea.md`)
**Framework Version**: 1.0
**Status**: Bootstrap Phase

### Core Innovation
Prompts generate prompts in a self-propagating chain:
- Each generator produces both a **terminal artifact** (document/code) and the **next-level generator prompt**
- Creates SDLC-aligned cascade: Vision > Epic > PRD > Backlog Story > ADR/Spec > Code > Test
- Each generation happens in **standalone context** to prevent pollution

---

## Folder Structure

```
/
   .claude/
      commands/
          execute-generator.md       # Universal executor
          refine-generator.md        # Iteration orchestrator

   docs/
      advanced_prompt_engineering_software_docs_code_final.md  # Research (immutable)
      context_engineering_strategy_v1.md  # Comprehensive methodology
      product-idea.md                     # CLI tool initial concept

   prompts/
      CLAUDE-{task}.md                    # Specialized contexts (lazy-generated)
      templates/                          # XML-formatted templates
         product-vision-template.xml
         epic-template.xml
         prd-template.xml
         backlog-story-template.xml
         adr-template.xml
         tech-spec-template.xml
         user-story-template.xml

      {phase}_generator.xml               # Generator prompts (created by cascade)

   artifacts/                              # All generated deliverables
      product_vision_v{1-3}.md
      epics/
      prds/
         prd_{id}/
            prd_v{1-3}.md
            TODO.md                        # High-level story tracking
      backlog_stories/
         US-{prd_id}-{story_id}_{feature_name}/
            backlog_story_v{1-3}.md
            TODO.md                        # Implementation task tracking
      specs/
      code/
      tests/

   feedback/                               # Human critique logs
      {artifact}_v{N}_critique.md

   CLAUDE.md                               # This file
   TODO.md                                 # Master Plan (single source of truth)
```

**Design Rationale**:
- Max 3 levels deep (prevents navigation complexity)
- Versioned outputs (v1, v2, v3) prevent overwriting during iterations
- Specialized CLAUDE.md files co-located with prompts directory
- Feedback folder supports human-in-loop refinement
- TODO.md files track progress without modifying frozen artifacts

---

## Execution Instructions

### How to Execute a Generator

**Step 1: Identify Task**
- Open `/TODO.md`
- Find task ID (e.g., `TASK-003: Execute Product Vision Generator v1`)
- Check dependencies are completed
- Note required context files

**Step 2: Start New Context (if required)**
- Most tasks require fresh Claude Code session
- Check task `Context:` field in TODO.md
- If "New session CX required", start clean session

**Step 3: Execute Generator**
```bash
/execute-generator TASK-003
```

**Step 4: System Actions**
The executor will:
1. Parse task details from `/TODO.md`
2. Check for specialized CLAUDE.md (e.g., `/prompts/CLAUDE-product-vision.md`)
   - If missing: Prompt human for confirmation > Generate from guidelines in "Specialized CLAUDE.md Files" section
   - If exists: Load directly
3. Load required context:
   - `/CLAUDE.md` (this file)
   - `/prompts/CLAUDE-{task}.md` (specialized)
   - `/prompts/{task}_generator.xml`
   - `/prompts/templates/{task}-template.xml`
   - Input artifacts (from prior tasks)
4. Execute generator prompt
5. Save outputs to `/artifacts/`
6. Update `/TODO.md` task status
7. Report validation checklist status

**Step 5: Review Output**
- Check `/artifacts/{output}_v1.md`
- Evaluate against validation criteria in TODO.md

**Step 6: Provide Feedback**
- Create `/feedback/{artifact}_v1_critique.md`
- Use structured format:
  - **Completeness**: All sections present?
  - **Clarity**: Readable by non-expert?
  - **Actionability**: Clear next steps?
  - **Traceability**: Links to upstream artifacts?
  - **Severity**: Minor/Major/Critical issues

**Step 7: Iterate (if needed)**
```bash
/refine-generator {task}_generator
```
- System loads generator + critique
- Applies Self-Refine pattern
- Re-executes > produces v2
- Repeat for v3 if necessary

**Step 8: Approve Final Version**
- Confirm v3 meets all validation criteria
- Update TODO.md task status to Completed
- Proceed to next task in dependency chain

---

## TODO.md Tracking Files

The framework uses separate TODO.md files to track status without cluttering frozen artifacts:

### PRD Level (`/artifacts/prds/prd_XXX/TODO.md`)
Tracks high-level user stories:
- [ ] = Not yet sent to Backlog Story Generator
- [x] = Sent to Backlog Story Generator, backlog stories created

### Backlog Story Level (`/artifacts/backlog_stories/US-XX-YY/TODO.md`)
Tracks implementation tasks with estimates, dependencies, assignments.

### Why Separate Files?
- Preserves artifact immutability after approval
- Allows dynamic status updates without re-generating documents
- Clear separation: specifications (frozen) vs. progress tracking (dynamic)

---

## Quality Standards

### Documentation Quality
- **Flesch Readability**: >60 (accessible to non-experts)
- **Completeness**: All template sections filled
- **Traceability**: References to upstream artifacts/decisions
- **Actionability**: Each section has clear next steps

### Code Quality
- **Test Coverage**: 80% minimum
- **Security**: Zero critical vulnerabilities (OWASP Top 10)
- **Style**: Follows language-specific conventions
- **Documentation**: Inline comments for complex logic

### Prompt Quality
- **Valid XML**: No syntax errors
- **Validation Checklists**: Included in all generators
- **Versioning**: Metadata tracks iteration number
- **Self-Contained**: Includes all necessary context

---

## Specialized CLAUDE.md Files

### What Are They?
Task-specific context files that provide:
- Domain expertise for specific SDLC phase
- Template usage instructions
- Common pitfalls and lessons learned
- Example outputs from research

### When Are They Created?
**Lazy Generation**: Created on-demand during first generator execution
- Executor checks if `/prompts/CLAUDE-{task}.md` exists
- If missing: Prompts human > Generates from template
- If exists: Load directly

### Current Specialized Files:
- None yet (will be created as tasks execute)

---

## Key Research References

This framework is based on:
- **Document**: `/docs/advanced_prompt_engineering_software_docs_code_final.md`
- **Section 1.1**: Anatomy of Effective Prompt (lines 49-92)
- **Section 2.4**: Self-Refine Pattern (lines 176-184)
- **Section 5.1**: Claude Optimization (lines 456-465)
- **Section 6.1-6.4**: Documentation Templates (lines 620-1117)

For detailed methodology, see:
- **Strategy Document**: `/docs/context_engineering_strategy_v1.md`

---

## Troubleshooting

### Issue: Specialized CLAUDE.md Missing
**Symptom**: Executor prompts for file generation
**Resolution**: Confirm generation when prompted (recommended) or create manually

### Issue: Context Window Overflow
**Symptom**: Token limit warnings
**Resolution**:
- Check that only immediate inputs are loaded (not entire history)
- Consider splitting large templates into sub-sections
- Target: <50% context window usage per task

### Issue: Validation Checklist Failure
**Symptom**: Generated artifact missing required sections
**Resolution**:
- Review template structure
- Check if generator correctly references template
- Iterate using refine-generator command

### Issue: Generator Produces Invalid XML
**Symptom**: Next-level generator fails to parse
**Resolution**:
- Validate XML syntax using online validator
- Check for unescaped special characters
- Ensure CDATA sections are properly closed

---

## Human Approval Checkpoints

Tasks requiring explicit human approval before proceeding:

1. **After TASK-007**: Product Vision v3 final approval
2. **After TASK-011**: Epic set v3 final approval
3. **After TASK-013**: PRD v3 final approval
4. **After TASK-014**: Backlog Story v3 final approval
5. **After TASK-015**: Phase 2 graduation decision
6. **Before any code generation**: Security and architecture review

**Approval Checklist**:
```
[ ] All template sections complete
[ ] Readable by non-expert (subjective Flesch >60)
[ ] Actionable (clear next steps)
[ ] Traceable (links to upstream artifacts)
[ ] Next generator is valid XML
[ ] No critical issues in feedback
```

---

## Maturity Progression

### Current: Phase 1 (Manual)
- Human triggers all executions via slash commands
- Manual critique files with human-written feedback
- Subjective quality assessment using checklists

### Target: Phase 2 (Semi-Automated)
**Graduation Criteria** (see TASK-015):
- Complete >= 3 generator types through 3-iteration cycles
- Document >= 5 patterns in strategy
- Validate execution script functionality

**Enhancements**:
- Script-assisted execution from TODO.md
- Automated self-critique using Chain-of-Verification
- Human approval only on threshold failures (80% pass rate)

### Future: Phase 3 (Fully Automated)
- Agentic workflow reads TODO.md > spawns contexts > validates
- Multi-agent critique (separate generator/reviewer)
- ML-based quality prediction
- Live strategy document updates

---

## Commands Reference

### Primary Commands
- `/execute-generator TASK-XXX` - Execute a generator from TODO.md
- `/refine-generator {name}_generator` - Iterate based on feedback

---

## Notes for Future Sessions

**Context Isolation Reminder**:
- Each task in new session should load ONLY:
  - This file (`/CLAUDE.md`)
  - Specialized CLAUDE.md for task
  - Generator prompt for task
  - Template(s) required
  - Immediate input artifacts (not entire history)

**Versioning Convention**:
- Artifacts: `{name}_v{1-3}.md` (3 iterations max per refinement cycle)
- Generator prompts: Metadata `<version>1.{iteration}</version>`
- Strategy document: Semantic versioning `vX.Y`

**File Naming Conventions**:
- Generators: `{phase}_generator.xml` (e.g., `product_vision_generator.xml`)
- Templates: `{artifact-type}-template.xml` (e.g., `prd-template.xml`)
- Specialized contexts: `CLAUDE-{phase}.md` (e.g., `CLAUDE-product-vision.md`)
- Artifacts: `{artifact}_v{N}.md` or `{epic_id}_{artifact}_v{N}.md`
- Backlog Stories: `US-{prd_id}-{story_id}_{feature_name}/` subfolders

---

**Document Version**: 1.0
**Last Updated**: 2025-10-07
**Maintained By**: Context Engineering PoC Team
**Next Review**: After TASK-015 (Phase 2 graduation assessment)
