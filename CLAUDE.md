# Context Engineering Framework - Root Orchestration

## General

**Product Name:** AI_Agent_MCP_Server
**Documentation Product Name:** AI Agent MCP Server

## Folder Structure

**Single source for directory hierarchy and file naming conventions.**

**Naming Variables:**
- `{XXX}` = Artifact ID (e.g., 005, 042, 123)
- `{N}` = Version number (1, 2, 3)
- `{product_name}` = Product name for research documents
- `{artifact-type}` = Artifact type name (e.g., product-vision, epic, prd)

```
/
   .claude/
      commands/
         generate.md                              # Universal executor
         refine.md                                # Iteration orchestrator

   docs/
      sdlc_artifacts_comprehensive_guideline.md  # SDLC artifacts guideline
      refinements/                               # Refinement plans

   prompts/                                      # Generators (XML-formatted)
      templates/                                 # Artifact templates (XML-formatted)
         {artifact-type}-template.xml            # Format: prd-template.xml, spike-template.xml
      {artifact-type}-generator.xml              # Format: product-vision-generator.xml, epic-generator.xml

   artifacts/                                    # All generated deliverables
      research/                                  # Research artifacts
         {product_name}_business_research.md     # Format: ai_agent_mcp_server_business_research.md
         {product_name}_implementation_research.md
      product_visions/                           # Product Visions
         VIS-{XXX}_product_vision_v{N}.md        # Format: VIS-001_product_vision_v1.md
      initiatives/                               # Initiatives
         INIT-{XXX}_initiative_v{N}.md           # Format: INIT-042_initiative_v1.md
      epics/                                     # Epics
         EPIC-{XXX}_epic_v{N}.md                 # Format: EPIC-123_epic_v1.md
      prds/                                      # PRDs
         PRD-{XXX}_prd_v{N}.md                   # Format: PRD-005_prd_v1.md
      hls/                                       # High-level user stories
         HLS-{XXX}_story_v{N}.md                 # Format: HLS-078_story_v1.md
      backlog_stories/                           # Backlog user stories
         US-{XXX}_story_v{N}.md                  # Format: US-234_story_v1.md
      spikes/                                    # Time-boxed technical investigations (1-3 days)
         SPIKE-{XXX}_v{N}.md                     # Format: SPIKE-042_v1.md
      adrs/                                      # Architecture Decision Records
         ADR-{XXX}_v{N}.md                       # Format: ADR-008_v1.md
      tech_specs/                                # Technical Specifications
         SPEC-{XXX}_v{N}.md                      # Format: SPEC-015_v1.md
      tasks/                                     # Implementation Tasks
         TASK-{XXX}_v{N}.md                      # Format: TASK-567_v1.md

   feedback/                                     # Human critique logs
      {artifact}_v{N}_critique.md                # Format: US-234_v1_critique.md

   CLAUDE.md                                     # This file (root orchestration)
   TODO.md                                       # Master Plan (single source of truth)
```

**Design Rationale**:
- Max 3 levels deep (prevents navigation complexity)
- Versioned outputs (v1, v2, v3) prevent overwriting during iterations
- Feedback folder supports human-in-loop refinement
- Consistent ID prefixes enable artifact type identification (VIS, EPIC, PRD, US, SPIKE, etc.)
- File naming conventions inline with structure (single reference point)

---

## SDLC Artifact Dependency Flow

**Purpose**: High-level view of artifact relationships and SDLC flow.

**For detailed information, see:**
- Paths and naming: "Folder Structure" section (lines ~8-72)
- Classification rules: "Input Classification System" section (lines ~148-200)
- Detailed inputs: Each generator's `<input_artifacts>` section

```
Research Phase (Root)
├── Business Research
└── Implementation Research

↓

Vision Phase
└── Product Vision
    └── Requires: Business Research (mandatory)

↓

Strategic Phase
├── Initiative
│   ├── Requires: Product Vision (mandatory)
│   └── + Business Research (recommended)
│
└── Epic
    ├── Requires: Product Vision (mandatory)
    └── + Business Research (recommended)

↓

Requirements Phase (Transition - bridges business and technical)
├── PRD
│   ├── Requires: Epic (mandatory)
│   ├── + Business Research (recommended - market validation)
│   └── + Implementation Research (recommended - technical feasibility)
│
└── High-Level Story
    ├── Requires: PRD (mandatory)
    └── + Business Research (recommended)

↓

Story Phase
└── Backlog Story
    ├── Requires: PRD (mandatory)
    └── + Implementation Research (recommended)

↓

Technical Phase
├── Spike (Optional - triggered by [REQUIRES SPIKE] marker)
│   ├── Requires: Backlog Story OR Tech Spec (mandatory, mutually exclusive)
│   ├── + Implementation Research (recommended)
│   ├── Time Box: 1-3 days maximum (strictly enforced)
│   └── Purpose: Time-boxed investigation to reduce technical uncertainty
│
├── ADR
│   ├── Requires: Backlog Story (mandatory)
│   ├── + Spike findings (conditional - if spike completed)
│   └── + Implementation Research (recommended)
│
└── Tech Spec
    ├── Requires: Backlog Story (mandatory)
    ├── + Spike findings (conditional - if spike completed)
    └── + Implementation Research (recommended)
```

**Key Principles:**
- **Business Research** flows into all business-phase artifacts (Vision, Initiative, Epic, PRD, HLS)
- **Implementation Research** flows into technical-phase artifacts (PRD, Backlog Story, Spike, ADR, Tech Spec)
- **PRD is unique**: Transition phase artifact that may use BOTH research documents
- **Spike is optional**: Only created when Backlog Story or Tech Spec has [REQUIRES SPIKE] marker
- **Classification system**: mandatory (must load), recommended (should load), conditional (load if condition met)
- Each generator produces v1, v2, v3 iterations through feedback cycles
- Approved v3 artifacts become inputs to downstream generators
- Generators are stateless; all context from input artifacts only

---

## Input Classification System

All generator input artifacts use a `classification` attribute that defines loading behavior and quality impact.

### Classification Tiers

**MANDATORY** (`classification="mandatory"`):
- **Definition**: Artifact MUST be loaded. Generator cannot proceed without it.
- **Characteristics**:
  - Direct parent in dependency chain (Primary Input)
  - Contains core requirements for output artifact
  - Blocking: Generator fails with error if not provided
- **Load Behavior**: Load immediately, fail if not found
- **Examples**: Epic for PRD, Product Vision for Initiative, High-Level Story for Backlog Story

**RECOMMENDED** (`classification="recommended"`):
- **Definition**: Artifact SHOULD be loaded to produce high-quality output, but generator can function without it.
- **Characteristics**:
  - Enriches output with additional context (Secondary Input)
  - Absence causes quality degradation but not failure
  - Generator notes when not loaded: "[WARN] Business Research not available - recommendations based on Epic only"
  - Standard workflow includes these inputs; skipped only when explicitly unavailable
- **Load Behavior**: Attempt to load, warn if not found, continue execution
- **Quality Impact**: Output quality reduced by ~20-30% without recommended inputs
- **Examples**: Business Research for PRD, Implementation Research for Backlog Story

**CONDITIONAL** (`classification="conditional"`):
- **Definition**: Artifact is loaded ONLY under specific conditions or when explicitly requested.
- **Characteristics**:
  - Loaded conditionally based on markers, flags, or specific scenarios
  - Not loaded by default in standard workflow
  - Presence/absence doesn't affect quality (provides alternative information path)
- **Load Behavior**: Check condition first, load only if condition met, no warning if not loaded
- **Conditions**:
  - Spike results available → ADR/Tech Spec may load Spike findings
  - Additional context needed → Backlog Story may load PRD (parent is HLS)
  - Explicit marker in parent artifact (e.g., [LOAD_RESEARCH])
- **Examples**: Spike for ADR (if spike completed), PRD for Backlog Story (if additional context needed)

**MUTUALLY_EXCLUSIVE** (Special case):
- **Definition**: Exactly ONE of N inputs must be provided.
- **Attributes**: `classification="mandatory" mutually_exclusive_group="[group_name]"`
- **Characteristics**:
  - Generator validates exactly one input from group is provided
  - Dependency tree shows "OR" relationship in metadata
  - Fail if zero or multiple inputs from same group
- **Validation**: At least one required, only one allowed per group
- **Examples**:
  - Epic accepts Product Vision OR Initiative (group="parent")
  - High-Level Story accepts Epic OR PRD (group="parent")
  - Spike accepts Backlog Story OR Tech Spec (group="source")

All generators updated to use `classification` attribute exclusively.

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

---

**Status Value Standards**:
- Research (Business/Implementation): Draft → In Review → Finalized
- Strategic (Vision/Initiative/Epic): Draft → In Review → Approved → Planned/Active → In Progress → Completed
- Requirements (PRD/HLS): Draft → In Review → Approved → Ready → In Progress → Completed
- Implementation (Backlog Story): Backlog → Ready → In Progress → In Review → Done
- Implementation (Task): To Do → In Progress → In Review → Done
- Spike: Planned → In Progress → Completed
- Architecture (ADR/Tech Spec): Proposed → Accepted → Active → Deprecated/Superseded

---

**Document Version**: 1.5
**Last Updated**: 2025-10-13
**Maintained By**: Context Engineering PoC Team
**Next Review**: End of Phase 1

**Version History:**
- v1.5 (2025-10-13): Added Input Classification System - replaced ambiguous `required` attribute with clear `classification` tiers (Issue #3 - Input Classification)
- v1.4 (2025-10-13): Added centralized Artifact Path Patterns section (Issue #2 - Path Consolidation)
- v1.3 (2025-10-12): Standardized artifact IDs, file naming conventions, and status values across all templates
- v1.2 (2025-10-11): Added Spike artifact to framework (time-boxed technical investigations)
- v1.1 (2025-10-11): Initial comprehensive version

**Related Documents:**
- `/docs/framework_validation_gaps.md` - Known validation gaps and production requirements
- `/docs/sdlc_artifacts_comprehensive_guideline.md` - Section 1.10 covers Metadata Standards and Traceability
