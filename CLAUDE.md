# Context Engineering Framework - Root Orchestration

## Folder Structure

```
/
   .claude/
      commands/
         generate.md       # Universal executor
         refine.md        # Iteration orchestrator

   docs/
      context_engineering_strategy_v{1-3}.md           # Comprehensive methodology
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
      spikes/                              # Time-boxed technical investigations
         SPIKE-{XXX}_v{1-3}.md
      specs/
         adrs/                             # Architecture Decision Records
         tech_specs/                       # Technical Specifications
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
    └── Output: artifacts/product_vision_v{N}.md

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
    ├── Primary Input: artifacts/epics/epic_{id}_v{N}.md (approved)
    ├── Secondary Input 1: docs/research/mcp/AI_Agent_MCP_Server_business_research.md (optional - market validation)
    ├── Secondary Input 2: docs/research/mcp/AI_Agent_MCP_Server_implementation_research.md (optional - technical feasibility)
    └── Output: artifacts/prds/prd_{id}/prd_v{1-3}.md

↓

Story Phase
└── Backlog Story Generator
    ├── Primary Input: artifacts/prds/prd_{id}/prd_v{N}.md (approved)
    ├── Secondary Input: docs/research/mcp/AI_Agent_MCP_Server_implementation_research.md (optional)
    └── Output: artifacts/backlog_stories/US-{prd_id}-{story_id}_{feature}/backlog_story_v{1-3}.md

↓

Technical Phase
├── Spike Generator (Optional - triggered by [REQUIRES SPIKE] marker)
│   ├── Primary Input: artifacts/backlog_stories/US-{prd_id}-{story_id}_{feature}/backlog_story_v{N}.md (question marked [REQUIRES SPIKE])
│   ├── Alternative Input: artifacts/specs/tech_specs/SPEC-{XXX}_v{N}.md (Open Questions)
│   ├── Secondary Input: docs/research/mcp/AI_Agent_MCP_Server_implementation_research.md (optional - baseline data)
│   ├── Output: artifacts/spikes/SPIKE-{XXX}_v1.md
│   ├── Time Box: 1-3 days maximum (strictly enforced)
│   └── Purpose: Time-boxed investigation to reduce technical uncertainty before implementation
│
├── ADR Generator
│   ├── Primary Input: artifacts/backlog_stories/US-{prd_id}-{story_id}_{feature}/backlog_story_v{N}.md (approved)
│   ├── Optional Input: artifacts/spikes/SPIKE-{XXX}_v1.md (if spike completed - provides findings and evidence)
│   ├── Secondary Input: docs/research/mcp/AI_Agent_MCP_Server_implementation_research.md
│   └── Output: artifacts/specs/adrs/ADR-{XXX}_v{1-3}.md
│
└── Technical Spec Generator
    ├── Primary Input: artifacts/backlog_stories/US-{prd_id}-{story_id}_{feature}/backlog_story_v{N}.md (approved)
    ├── Optional Input: artifacts/spikes/SPIKE-{XXX}_v1.md (if spike completed - provides implementation details)
    ├── Secondary Input: docs/research/mcp/AI_Agent_MCP_Server_implementation_research.md
    └── Output: artifacts/specs/tech_specs/SPEC-{XXX}_v{1-3}.md
```

**Key Principles:**
- **Business Research** flows into all business-phase artifacts (Vision, Initiative, Epic)
- **Implementation Research** flows into technical-phase artifacts (Backlog Story, Spike, ADR, Tech Spec)
- **PRD is unique**: Transition phase artifact that may use BOTH research documents:
  - Business Research (optional): Market validation, competitive positioning, business metrics
  - Implementation Research (optional): Technical feasibility, architecture constraints, NFRs
- **Spike is optional**: Only created when Backlog Story or Tech Spec has [REQUIRES SPIKE] marker
  - Time-boxed investigation (1-3 days max) to reduce technical uncertainty
  - Produces findings and recommendation (NOT production code)
  - Informs ADR (if major decision) or Tech Spec (if implementation detail)
  - Always updates parent Backlog Story with findings and revised estimate
- Each generator produces v1, v2, v3 iterations through feedback cycles
- Approved v3 artifacts become inputs to downstream generators
- Generators are stateless; all context from input artifacts only
- Secondary inputs are OPTIONAL: Load when enrichment needed, not by default

---

## Spike Workflow (Technical Investigations)

**When to Create Spike:**
- Backlog Story Open Question marked `[REQUIRES SPIKE]`
- Tech Spec has technical uncertainty requiring investigation
- Need evidence (benchmarks, prototypes, documentation) before committing to approach

**Spike Execution Flow:**
```
1. Backlog Story identifies uncertainty
   └─ Mark question as [REQUIRES SPIKE] in Open Questions section

2. Create Spike artifact at /artifacts/spikes/SPIKE-{XXX}_v1.md
   ├─ Define investigation goal (specific question to answer)
   ├─ Set time box (1-3 days maximum - HARD LIMIT)
   ├─ Design investigation approach (prototype, benchmark, documentation review)
   └─ Define success criteria (what evidence needed to decide)

3. Execute time-boxed investigation
   ├─ Collect evidence (benchmark data, code samples, documentation)
   ├─ Document findings with data (no speculation, only measured results)
   └─ Provide clear recommendation based on findings

4. Create downstream artifacts based on spike outcome:
   ├─ If major decision → Create ADR at /artifacts/specs/adrs/ADR-{XXX}_v1.md
   ├─ If implementation detail → Update Tech Spec
   └─ Always → Update parent Backlog Story with findings and revised estimate
```

**Time-Box Enforcement:**
- Spike MUST NOT exceed 3 days
- If incomplete at time box expiration: Document current findings, state unknowns, recommend follow-up if needed
- Do NOT extend time box without Tech Lead approval

**Spike Markers:**
- `[REQUIRES SPIKE]` - In Backlog Story/Tech Spec Open Questions
- No markers in spike itself (spike documents findings, not questions)

---

## Open Questions Marker System

All SDLC artifacts use a consistent marker system to classify uncertainties and route them to appropriate resolution paths:

**Strategic/Resource Level (Initiative):**
- `[REQUIRES EXECUTIVE DECISION]` - C-level or VP approval needed
- `[REQUIRES PORTFOLIO PLANNING]` - Affects multiple initiatives or roadmap
- `[REQUIRES RESOURCE PLANNING]` - FTE, budget, or team allocation
- `[REQUIRES ORGANIZATIONAL ALIGNMENT]` - Stakeholder consensus needed

**Business Level (Epic):**
- Business questions only (market, business model, compliance)
- No technical markers at Epic phase

**Bridge Level (PRD):**
- `[REQUIRES PM + TECH LEAD]` - Product/technical trade-offs requiring collaboration

**User/UX Level (High-Level Story):**
- `[REQUIRES UX RESEARCH]` - User behavior validation
- `[REQUIRES UX DESIGN]` - Design input or usability testing
- `[REQUIRES PRODUCT OWNER]` - Feature scope or priority decisions

**Implementation Level (Backlog Story):**
- `[REQUIRES SPIKE]` - Time-boxed investigation (1-3 days) → Creates spike artifact
- `[REQUIRES ADR]` - Major architectural decision → Creates ADR artifact
- `[REQUIRES TECH LEAD]` - Senior technical input (no artifact needed)
- `[BLOCKED BY]` - External dependency

**Technical Detail Level (Tech Spec, Implementation Task):**
- `[REQUIRES TECH LEAD]` - Senior technical input
- `[CLARIFY BEFORE START]` - Must resolve before beginning task
- `[BLOCKED BY]` - External dependency
- `[NEEDS PAIR PROGRAMMING]` - Complex area requiring collaboration
- `[TECH DEBT]` - Workaround needed due to existing code constraints

**Workflow:**
```
Question marked [REQUIRES SPIKE] in Backlog Story
    ↓
Spike Generator creates investigation plan
    ↓
Spike executed (1-3 days, time-boxed)
    ↓
Spike findings documented at /artifacts/spikes/SPIKE-XXX_v1.md
    ↓
Based on findings:
    ├─ If major decision needed → [REQUIRES ADR] → Create ADR
    ├─ If implementation detail → Update Tech Spec
    └─ Always → Update Backlog Story with findings and revised estimate
```

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

**Standardized Artifact IDs**:
| Artifact Type | ID Format | Example |
|---------------|-----------|---------|
| Product Vision | VIS-XXX | VIS-001 |
| Initiative | INIT-XXX | INIT-042 |
| Epic | EPIC-XXX | EPIC-123 |
| PRD | PRD-XXX | PRD-005 |
| High-Level Story | HLS-XXX | HLS-078 |
| Backlog Story | US-XXX | US-234 |
| Spike | SPIKE-XXX | SPIKE-042 |
| ADR | ADR-XXX | ADR-008 |
| Tech Spec | SPEC-XXX | SPEC-015 |
| Implementation Task | TASK-XXX | TASK-567 |

**File Naming Conventions**:
- Generators: `{phase}-generator.xml` (e.g., `product-vision-generator.xml`, `spike-generator.xml`)
- Templates: `{artifact-type}-template.xml` (e.g., `prd-template.xml`, `spike-template.xml`)
- Artifacts: `{artifact}_v{N}.md` or `{epic_id}_{artifact}_v{N}.md`
- Product Vision: `VIS-{XXX}_product_vision_v{N}.md`
- Initiatives: `INIT-{XXX}_initiative_v{N}.md`
- Epics: `EPIC-{XXX}_epic_v{N}.md`
- PRDs: `PRD-{XXX}_prd_v{N}.md` in `prds/prd_{XXX}/` subfolder
- High-Level Stories: `HLS-{XXX}_story_v{N}.md`
- Backlog Stories: `US-{XXX}_story_v{N}.md` in `backlog_stories/US-{XXX}_{feature_name}/` subfolder
- Spikes: `SPIKE-{XXX}_v{N}.md` (e.g., `SPIKE-042_v1.md`)
- ADRs: `ADR-{XXX}_v{N}.md` (e.g., `ADR-008_v1.md`)
- Tech Specs: `SPEC-{XXX}_v{N}.md` (e.g., `SPEC-015_v1.md`)
- Implementation Tasks: `TASK-{XXX}_v{N}.md`

**Status Value Standards**:
- Research (Business/Implementation): Draft → In Review → Finalized
- Strategic (Vision/Initiative/Epic): Draft → In Review → Approved → Planned/Active → In Progress → Completed
- Requirements (PRD/HLS): Draft → In Review → Approved → Ready → In Progress → Completed
- Implementation (Backlog Story): Backlog → Ready → In Progress → In Review → Done
- Implementation (Task): To Do → In Progress → In Review → Done
- Spike: Planned → In Progress → Completed
- Architecture (ADR/Tech Spec): Proposed → Accepted → Active → Deprecated/Superseded

---

**Document Version**: 1.3
**Last Updated**: 2025-10-12
**Maintained By**: Context Engineering PoC Team
**Next Review**: End of Phase 1

**Version History:**
- v1.3 (2025-10-12): Standardized artifact IDs, file naming conventions, and status values across all templates
- v1.2 (2025-10-11): Added Spike artifact to framework (time-boxed technical investigations)
- v1.1 (2025-10-11): Initial comprehensive version

**Related Documents:**
- `/docs/framework_validation_gaps.md` - Known validation gaps and production requirements
- `/docs/sdlc_artifacts_comprehensive_guideline.md` - Section 1.10 covers Metadata Standards and Traceability
