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

## SDLC Generators Input Dependency Tree

**Root Product:** AI Agent MCP Server

```
Research Phase (Root)
├── Business Research
│   └── docs/research/mcp/AI_Agent_MCP_Server_business_research.md
└── Implementation Research
    └── docs/research/mcp/AI_Agent_MCP_Server_implementation_research.md

↓

Vision Phase
└── Product Vision Generator
    ├── Input: docs/research/mcp/AI_Agent_MCP_Server_business_research.md
    └── Output: artifacts/product_vision_v{1-3}.md

↓

Strategic Phase
├── Initiative Generator
│   ├── Primary Input: artifacts/product_vision_v{N}.md (approved)
│   ├── Secondary Input: docs/research/mcp/AI_Agent_MCP_Server_business_research.md (optional)
│   └── Output: artifacts/initiatives/initiative_{id}_v{1-3}.md
│
└── Epic Generator
    ├── Primary Input: artifacts/product_vision_v{N}.md (approved)
    ├── Secondary Input: docs/research/mcp/AI_Agent_MCP_Server_business_research.md (optional)
    └── Output: artifacts/epics/epic_{id}_v{1-3}.md

↓

Requirements Phase (Transition - bridges business and technical)
└── PRD Generator
    ├── Primary Input: artifacts/epics/epic_{id}_v3.md (approved)
    ├── Secondary Input 1: docs/research/mcp/AI_Agent_MCP_Server_business_research.md (optional - market validation)
    ├── Secondary Input 2: docs/research/mcp/AI_Agent_MCP_Server_implementation_research.md (optional - technical feasibility)
    └── Output: artifacts/prds/prd_{id}/prd_v{1-3}.md

↓

Story Phase
└── Backlog Story Generator
    ├── Primary Input: artifacts/prds/prd_{id}/prd_v3.md (approved)
    ├── Secondary Input: docs/research/mcp/AI_Agent_MCP_Server_implementation_research.md (optional)
    └── Output: artifacts/backlog_stories/US-{prd_id}-{story_id}_{feature}/backlog_story_v{1-3}.md

↓

Technical Phase
├── ADR Generator
│   ├── Primary Input: artifacts/backlog_stories/US-{prd_id}-{story_id}_{feature}/backlog_story_v3.md (approved)
│   ├── Secondary Input: docs/research/mcp/AI_Agent_MCP_Server_implementation_research.md
│   └── Output: artifacts/specs/adr_{id}_v{1-3}.md
│
└── Technical Spec Generator
    ├── Primary Input: artifacts/backlog_stories/US-{prd_id}-{story_id}_{feature}/backlog_story_v3.md (approved)
    ├── Secondary Input: docs/research/mcp/AI_Agent_MCP_Server_implementation_research.md
    └── Output: artifacts/specs/tech_spec_{id}_v{1-3}.md
```

**Key Principles:**
- **Business Research** flows into all business-phase artifacts (Vision, Initiative, Epic)
- **Implementation Research** flows into technical-phase artifacts (Backlog Story, ADR, Tech Spec)
- **PRD is unique**: Transition phase artifact that may use BOTH research documents:
  - Business Research (optional): Market validation, competitive positioning, business metrics
  - Implementation Research (optional): Technical feasibility, architecture constraints, NFRs
- Each generator produces v1, v2, v3 iterations through feedback cycles
- Approved v3 artifacts become inputs to downstream generators
- Generators are stateless; all context from input artifacts only
- Secondary inputs are OPTIONAL: Load when enrichment needed, not by default

---

## Generate Command Instructions

### Start New Context (if required)**
- Most tasks require fresh Claude Code session
- Check task `Context:` field in TODO.md
- If "New session CX required", start clean session

## Instructions for TODO.md Tasks
Upon completion, update relevant task status in `/TODO.md`:
- Mark current task checkbox as complete
- Update task status notes
- Add entry to task completion log if applicable

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
- Generators: `{phase}-generator.xml` (e.g., `product-vision-generator.xml`)
- Templates: `{artifact-type}-template.xml` (e.g., `prd-template.xml`)
- Artifacts: `{artifact}_v{N}.md` or `{epic_id}_{artifact}_v{N}.md`
- Backlog Stories: `US-{prd_id}-{story_id}_{feature_name}/` subfolders

---

**Document Version**: 1.1
**Last Updated**: 2025-10-11
**Maintained By**: Context Engineering PoC Team
**Next Review**: End of Phase 1

**Related Documents:**
- `/docs/framework_validation_gaps.md` - Known validation gaps and production requirements
