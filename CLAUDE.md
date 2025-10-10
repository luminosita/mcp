# Context Engineering Framework - Root Orchestration

## Folder Structure

```
/
   .claude/
      commands/
         generate.md       # Universal executor
         refine.md        # Iteration orchestrator

   docs/
      context_engineering_strategy_v1.md           # Comprehensive methodology
      sdlc_artifacts_comprehensive_guideline.md    # SDLC artifacts guideline               
   prompts/
      templates/                          # XML-formatted templates
         {phase}-template_v{1-3}.md       ## SDLC artifacts templates 
      {phase}_generator_v{1-3}.xml               # Generator prompts

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
- Feedback folder supports human-in-loop refinement
- TODO.md files track progress without modifying frozen artifacts

---

## Generate Command Instructions

### Start New Context (if required)**
- Most tasks require fresh Claude Code session
- Check task `Context:` field in TODO.md
- If "New session CX required", start clean session

## Commands Reference

### Primary Commands
- `/generate TASK-XXX` - Execute a generator from TODO.md
- `/refine {name}_generator` - Iterate based on feedback

---

**Versioning Convention**:
- Artifacts: `{name}_v{1-3}.md` (3 iterations max per refinement cycle)
- Generator prompts: Metadata `<version>1.{iteration}</version>`
- Strategy document: Semantic versioning `vX.Y`

**File Naming Conventions**:
- Generators: `{phase}_generator.xml` (e.g., `product_vision_generator.xml`)
- Templates: `{artifact-type}-template.xml` (e.g., `prd-template.xml`)
- Artifacts: `{artifact}_v{N}.md` or `{epic_id}_{artifact}_v{N}.md`
- Backlog Stories: `US-{prd_id}-{story_id}_{feature_name}/` subfolders

---

**Document Version**: 1.0
**Last Updated**: 2025-10-07
**Maintained By**: Context Engineering PoC Team
**Next Review**: n/a
