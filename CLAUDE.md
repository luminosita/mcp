# Context Engineering Framework - Root Orchestration

## General

**Product Name:** AI_Agent_MCP_Server
**Documentation Product Name:** AI Agent MCP Server

## Folder Structure

```
/
   .claude/
      commands/
         generate.md       # Universal executor
         refine.md         # Iteration orchestrator

   docs/
      sdlc_artifacts_comprehensive_guideline.md       # SDLC artifacts guideline               
      refinements/                                    # Refinement plans
   prompts/
      templates/                                # XML-formatted templates
         {artifact-type}-template_v{N}.md       # SDLC artifacts templates 
      {artifact-type}_generator_v{N}.xml        # Generator prompts

   artifacts/                                         # All generated deliverables
      research/                                       # Research artifacts
         {product_name}_business_research.md          # Business Research
         {product_name}_implementation_research.md    # Implementation Research
      product_visions/                                # Product Visions
         VIS-{XXX}_product_vision_v{N}.md
      initiatives/                                    # Initiatives
         INIT-{XXX}_initiative_v{N}.md
      epics/                                          # Epics
         EPIC-{XXX}_epic_v{N}.md
      prds/                                           # PRDs
         PRD-{XXX}_prd_v{N}.md
      hls/                                            # High-level user stories  
         HLS-{XXX}_story_v{N}.md                      
      backlog_stories/                                # Backlog user stories  
         US-{XXX}_story_v{N}.md
      spikes/                                         # Time-boxed technical investigations
         SPIKE-{XXX}_v{N}.md
      adrs/                                           # Architecture Decision Records
         ADR-{XXX}_v{N}.md
      tech_specs/                                     # Technical Specifications
         SPEC-{XXX}_v{N}.md
      tasks/                                          # Implementation Tasks
         TASK-{XXX}_v{N}.md

   feedback/                               # Human critique logs
      {artifact}_v{N}_critique.md

   CLAUDE.md                               # This file
   TODO.md                                 # Master Plan (single source of truth)
```

**Design Rationale**:
- Max 3 levels deep (prevents navigation complexity)
- Versioned outputs (v1, v2, v3) prevent overwriting during iterations
- Feedback folder supports human-in-loop refinement

---

## SDLC Generators Input Dependency Tree

```
Research Phase (Root)
├── Business Research
│   └── artifacts/research/{product_name}_business_research.md
└── Implementation Research
    └── artifacts/research/{product_name}_implementation_research.md

↓

Vision Phase
└── Product Vision Generator
    ├── Input: artifacts/research/{product_name}_business_research.md
    └── Output: artifacts/product_visions/VIS-{XXX}_product_vision_v{N}.md

↓

Strategic Phase
├── Initiative Generator
│   ├── Primary Input: artifacts/product_visions/VIS-{XXX}_product_vision_v{N}.md (approved)
│   ├── Secondary Input: artifacts/research/{product_name}_business_research.md (optional)
│   └── Output: artifacts/initiatives/INIT-{XXX}_initiative_v{N}.md
│
└── Epic Generator
    ├── Primary Input: artifacts/product_visions/VIS-{XXX}_product_vision_v{N}.md (approved)
    ├── Secondary Input: artifacts/research/{product_name}_business_research.md (optional)
    └── Output: artifacts/epics/EPIC-{XXX}_epic_v{N}.md

↓

Requirements Phase (Transition - bridges business and technical)
└── PRD Generator
    ├── Primary Input: artifacts/epics/EPIC-{XXX}_epic_v{N}.md (approved)
    ├── Secondary Input 1: artifacts/research/{product_name}_business_research.md (optional - market validation)
    ├── Secondary Input 2: artifacts/research/{product_name}_implementation_research.md (optional - technical feasibility)
    └── Output: artifacts/prds/PRD-{XXX}_prd_v{N}.md
└── High-level Story Generator
    ├── Primary Input: artifacts/prds/PRD-{XXX}_prd_v{N}.md (approved)
    ├── Secondary Input: artifacts/research/{product_name}_business_research.md (optional)
    └── Output: artifacts/hls/HLS-{XXX}_story_v{N}.md
↓

Story Phase
└── Backlog Story Generator
    ├── Primary Input: artifacts/prds/PRD-{XXX}_prd_v{N}.md (approved)
    ├── Secondary Input: artifacts/research/{product_name}_implementation_research.md (optional)
    └── Output: artifacts/backlog_stories/US-{XXX}_story_v{N}.md

↓

Technical Phase
├── Spike Generator (Optional - triggered by [REQUIRES SPIKE] marker)
│   ├── Primary Input: artifacts/backlog_stories/US-{XXX}_story_v{N}.md (question marked [REQUIRES SPIKE])
│   ├── Alternative Input: artifacts/specs/tech_specs/SPEC-{XXX}_v{N}.md (Open Questions)
│   ├── Secondary Input: artifacts/research/{product_name}_implementation_research.md (optional - baseline data)
│   ├── Output: artifacts/spikes/SPIKE-{XXX}_v1.md
│   ├── Time Box: 1-3 days maximum (strictly enforced)
│   └── Purpose: Time-boxed investigation to reduce technical uncertainty before implementation
│
├── ADR Generator
│   ├── Primary Input: artifacts/backlog_stories/US-{XXX}_story_v{N}.md
│   ├── Optional Input: artifacts/spikes/SPIKE-{XXX}_v1.md (if spike completed - provides findings and evidence)
│   ├── Secondary Input: artifacts/research/{product_name}_implementation_research.md
│   └── Output: artifacts/specs/adrs/ADR-{XXX}_v{N}.md
│
└── Technical Spec Generator
    ├── Primary Input: artifacts/backlog_stories/US-{XXX}_story_v{N}.md
    ├── Optional Input: artifacts/spikes/SPIKE-{XXX}_v1.md (if spike completed - provides implementation details)
    ├── Secondary Input: artifacts/research/{product_name}_implementation_research.md
    └── Output: artifacts/specs/tech_specs/SPEC-{XXX}_v{N}.md
```

**Key Principles:**
- **Business Research** flows into all business-phase artifacts (Vision, Initiative, Epic)
- **Implementation Research** flows into technical-phase artifacts (Backlog Story, Spike, ADR, Tech Spec)
- **PRD is unique**: Transition phase artifact that may use BOTH research documents
- **Spike is optional**: Only created when Backlog Story or Tech Spec has [REQUIRES SPIKE] marker
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

### Migration from `required` Attribute

**Old System (deprecated):**
- `required="true"` - must load (ambiguous: includes both mandatory and recommended)
- `required="false"` - optional (ambiguous: includes recommended, conditional, and truly optional)

**New System (Issue #3):**
- `classification="mandatory"` - must load (clear: generator fails without it)
- `classification="recommended"` - should load (clear: warns but continues without it)
- `classification="conditional"` - maybe load (clear: only loads if condition met)
- `mutually_exclusive_group="name"` - one of N required (clear: validates exactly one)

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

**File Naming Conventions**:
- Generators: `{artifact-type}-generator.xml` (e.g., `product-vision-generator.xml`, `spike-generator.xml`)
- Templates: `{artifact-type}-template.xml` (e.g., `prd-template.xml`, `spike-template.xml`)
- Artifacts (artifact types):
   - Business Research: `{product_name}_business_research.md`
   - Implementation Research: `{product_name}_implementation_research.md`
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

**Artifact Path Patterns**:

All generators reference paths from this section. Paths are relative to repository root.

**Path Variables:**
- `{id}` - Artifact ID (e.g., 005, 042, 123)
- `{version}` - Version number (1, 2, 3)
- `{product_name}` - Product name for research documents
- `{feature_name}` - Feature name for backlog stories

**Input Artifact Paths:**
- Business Research: `artifacts/research/{product_name}_business_research.md`
- Implementation Research: `artifacts/research/{product_name}_implementation_research.md`
- Product Vision: `artifacts/product_visions/VIS-{id}_product_vision_v{version}.md`
- Initiative: `artifacts/initiatives/INIT-{id}_initiative_v{version}.md`
- Epic: `artifacts/epics/EPIC-{id}_epic_v{version}.md`
- PRD: `artifacts/prds/PRD-{id}_prd_v{version}.md`
- High-Level Story: `artifacts/hls/HLS-{id}_story_v{version}.md`
- Backlog Story: `artifacts/backlog_stories/US-{id}_story_v{version}.md`
- Spike: `artifacts/spikes/SPIKE-{id}_v{version}.md`
- ADR: `artifacts/adrs/ADR-{id}_v{version}.md`
- Tech Spec: `artifacts/tech_specs/SPEC-{id}_v{version}.md`
- Implementation Task: `artifacts/tasks/TASK-{id}_v{version}.md`

**Template Paths:**
- Business Research: `prompts/templates/business-research-template.md`
- Implementation Research: `prompts/templates/implementation-research-template.md`
- Product Vision: `prompts/templates/product-vision-template.xml`
- Initiative: `prompts/templates/initiative-template.xml`
- Epic: `prompts/templates/epic-template.xml`
- PRD: `prompts/templates/prd-template.xml`
- High-Level Story: `prompts/templates/high-level-user-story-template.xml`
- Backlog Story: `prompts/templates/backlog-story-template.xml`
- Spike: `prompts/templates/spike-template.xml`
- ADR: `prompts/templates/adr-template.xml`
- Tech Spec: `prompts/templates/tech-spec-template.xml`
- Implementation Task: `prompts/templates/implementation-task-template.xml`

**Generator Paths:**
- Business Research: `prompts/business-research-generator.xml`
- Implementation Research: `prompts/implementation-research-generator.xml`
- Product Vision: `prompts/product-vision-generator.xml`
- Initiative: `prompts/initiative-generator.xml`
- Epic: `prompts/epic-generator.xml`
- PRD: `prompts/prd-generator.xml`
- High-Level Story: `prompts/high-level-user-story-generator.xml`
- Backlog Story: `prompts/backlog-story-generator.xml`
- Spike: `prompts/spike-generator.xml`
- ADR: `prompts/adr-generator.xml`
- Tech Spec: `prompts/tech-spec-generator.xml`
- Implementation Task: `prompts/implementation-task-generator.xml`

**Usage in Generators:**
Generators reference these paths using the artifact type name (e.g., "Load template from path defined in CLAUDE.md for PRD"). All paths are defined once here and referenced by all generators.

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
