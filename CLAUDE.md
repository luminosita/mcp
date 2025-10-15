# Context Engineering Framework - Root Orchestration

## General

**Product Name:** AI_Agent_MCP_Server
**Documentation Product Name:** AI Agent MCP Server
**Package Name:** mcp_server (alias: ai_agent_mcp_server)

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

## Artifact Path Resolution Algorithm

**Purpose:** Resolve path patterns from Folder Structure section to actual file paths during generator execution.

### Variable Substitution Rules

**Step 1: Extract Context Variables**

From CLAUDE.md General section (lines 5-7):
```
product_name = "AI_Agent_MCP_Server"  (from line 5: **Product Name:** AI_Agent_MCP_Server)
package_name = "mcp_server"            (from line 7: **Package Name:** mcp_server)
```

**Step 2: Apply Substitution**

```
Pattern: artifacts/research/{product_name}_implementation_research.md
Substitute: {product_name} → AI_Agent_MCP_Server
Result: artifacts/research/AI_Agent_MCP_Server_implementation_research.md
```

**Step 3: Validate File Exists**

```bash
# Method 1: Check resolved path directly
ls artifacts/research/AI_Agent_MCP_Server_implementation_research.md

# Method 2: Use glob pattern for fuzzy matching
ls artifacts/research/*_implementation_research.md
```

**Step 4: Apply Input Classification Rules**

Based on generator's `<input_artifacts>` section:
- **MANDATORY** (`classification="mandatory"`): File MUST exist → EXIT with error code 1 if missing
- **RECOMMENDED** (`classification="recommended"`): File SHOULD exist → WARN + confirm if missing (exit code 2 if user declines)
- **CONDITIONAL** (`classification="conditional"`): File loaded only if condition met → No error if missing

### Common Path Patterns

| Artifact Type | Pattern | Resolved Example |
|---------------|---------|------------------|
| Business Research | `artifacts/research/{product_name}_business_research.md` | `artifacts/research/AI_Agent_MCP_Server_business_research.md` |
| Implementation Research | `artifacts/research/{product_name}_implementation_research.md` | `artifacts/research/AI_Agent_MCP_Server_implementation_research.md` |
| Product Vision | `artifacts/product_visions/VIS-{XXX}_product_vision_v{N}.md` | `artifacts/product_visions/VIS-001_product_vision_v1.md` |
| Epic | `artifacts/epics/EPIC-{XXX}_epic_v{N}.md` | `artifacts/epics/EPIC-000_project_foundation_bootstrap_v2.md` |
| PRD | `artifacts/prds/PRD-{XXX}_prd_v{N}.md` | `artifacts/prds/PRD-000_project_foundation_bootstrap_v3.md` |
| High-Level Story | `artifacts/hls/HLS-{XXX}_story_v{N}.md` | `artifacts/hls/HLS-003_application_skeleton_implementation_v1.md` |
| Backlog Story | `artifacts/backlog_stories/US-{XXX}_story_v{N}.md` | `artifacts/backlog_stories/US-009_story_v1.md` |
| Spike | `artifacts/spikes/SPIKE-{XXX}_v{N}.md` | `artifacts/spikes/SPIKE-001_v1.md` |
| ADR | `artifacts/adrs/ADR-{XXX}_v{N}.md` | `artifacts/adrs/ADR-001_v1.md` |
| Tech Spec | `artifacts/tech_specs/SPEC-{XXX}_v{N}.md` | `artifacts/tech_specs/SPEC-001_v1.md` |
| Implementation Task | `artifacts/tasks/TASK-{XXX}_v{N}.md` | `artifacts/tasks/TASK-001_v1.md` |

### Glob Pattern Strategies

```bash
# Strategy 1: Specific artifact by ID and version (most precise)
ls artifacts/hls/HLS-003_story_v1.md

# Strategy 2: Latest version of specific artifact
ls artifacts/hls/HLS-003_*.md | sort | tail -1

# Strategy 3: All versions of specific artifact
ls artifacts/hls/HLS-003_*.md

# Strategy 4: All artifacts of type
ls artifacts/hls/HLS-*.md

# Strategy 5: Research by product name (when product_name known)
ls artifacts/research/AI_Agent_MCP_Server_*.md

# Strategy 6: Research by type suffix (when product_name unknown)
ls artifacts/research/*_implementation_research.md
ls artifacts/research/*_business_research.md

# Strategy 7: Wildcard search across all artifact directories
find artifacts -name "*HLS-003*"
```

### Error Message Formats

**MANDATORY Input Missing (Exit Code 1):**

```
❌ ERROR: Mandatory input artifact not found

Input Type: High-Level Story
Expected Path: artifacts/hls/HLS-003_story_v1.md
Classification: MANDATORY
Status Requirement: Approved

Generator cannot proceed without mandatory input.

Action Required:
1. Verify HLS-003 exists at expected path
2. Ensure Status field = "Approved" in artifact metadata
3. Retry generator execution

Search Patterns Tried:
- artifacts/hls/HLS-003_story_v1.md (exact path)
- artifacts/hls/HLS-003_*.md (glob pattern)

Exit Code: 1
```

**RECOMMENDED Input Missing (Warning + Confirmation):**

```
⚠️  WARNING: Recommended input artifact not found

Input Type: Implementation Research
Expected Path: artifacts/research/AI_Agent_MCP_Server_implementation_research.md
Classification: RECOMMENDED
Quality Impact: ~20-30% reduction in output quality without technical patterns and code examples

Resolution Details:
- Pattern: artifacts/research/{product_name}_implementation_research.md
- Substituted: {product_name} → AI_Agent_MCP_Server
- Resolved Path: artifacts/research/AI_Agent_MCP_Server_implementation_research.md

Search Patterns Tried:
- artifacts/research/AI_Agent_MCP_Server_implementation_research.md (exact)
- artifacts/research/*_implementation_research.md (glob)

Files Found: (none)

Proceed without recommended input? (y/n)
- If 'n': Exit Code 2
- If 'y': Continue with quality degradation documented in generated artifact
```

**CONDITIONAL Input Skipped (No Error):**

```
ℹ️  INFO: Conditional input not loaded

Input Type: Spike Findings
Expected Path: artifacts/spikes/SPIKE-{id}_v{version}.md
Classification: CONDITIONAL
Condition: Story has [REQUIRES SPIKE] marker in Open Questions
Condition Met: No

Skipping conditional input (no error).
```

### Path Resolution Implementation Checklist

For generator implementations:

- [ ] Extract `product_name` from CLAUDE.md General section
- [ ] Substitute `{product_name}` in research artifact paths
- [ ] Substitute `{XXX}` artifact IDs from TODO.md task specification
- [ ] Substitute `{N}` version numbers from TODO.md or latest available
- [ ] Validate resolved paths before generator execution
- [ ] Apply classification rules (MANDATORY, RECOMMENDED, CONDITIONAL)
- [ ] Exit with appropriate error code:
  - `0` - Success, all required inputs validated
  - `1` - Error, mandatory input missing
  - `2` - Warning, user declined to proceed without recommended input
- [ ] Document quality degradation when RECOMMENDED inputs unavailable
- [ ] Log all search patterns attempted for debugging

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
├── INIT-000: Foundation Initiative (greenfield projects only)
│   ├── Requires: Product Vision (mandatory)
│   ├── + Business Research (recommended)
│   └── Contains: EPIC-000 (Project Foundation & Bootstrap)
│
├── INIT-001+: Feature Initiatives
│   ├── Requires: Product Vision (mandatory)
│   ├── + Business Research (recommended)
│   ├── Dependencies: INIT-000 (must complete first - for greenfield projects)
│   └── Contains: EPIC-001, EPIC-002, EPIC-003, etc.
│
└── Epic (can be generated from Product Vision OR Initiative)
    ├── Path A: Requires Product Vision (mandatory) + Business Research (recommended)
    └── Path B: Requires Initiative (mandatory) + Business Research (recommended)

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
- **INIT-000 (Foundation Initiative)**: For greenfield/new projects only. Contains EPIC-000 (Project Foundation & Bootstrap). Establishes infrastructure before feature development. No dependencies.
- **INIT-001+ (Feature Initiatives)**: For feature delivery. Depends on INIT-000 (if greenfield). Contains EPIC-001, EPIC-002, etc.
- **Epic Generation**: Can be generated from Product Vision (direct) OR Initiative (decomposition). Use mutually exclusive input selection.
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

## ID Assignment Strategy

**Global Sequential Numbering:** All artifact IDs within a type (US, SPEC, ADR, TASK, SPIKE) are globally unique and sequential across the entire project.

**Purpose:** Prevents ID clashing when multiple HLS stories generate backlog stories. Ensures unique identification across all artifacts.

**Assignment Process:**
1. **Planning Phase:** Assign IDs in TODO.md when creating generator tasks
2. **Registry:** TODO.md acts as the authoritative ID registry
3. **Immutability:** Once assigned, IDs never change (even if artifact deleted)
4. **Sequence:** Next available ID = (last assigned ID + 1)

**ID Allocation Example:**

| HLS | Backlog Stories | US IDs Assigned |
|-----|-----------------|-----------------|
| HLS-001 | 2 stories | US-001, US-002 |
| HLS-002 | 6 stories | US-003 → US-008 |
| HLS-003 | 5 stories | US-009 → US-013 |
| HLS-004 | 6 stories | US-014 → US-019 |
| HLS-005 | 6 stories | US-020 → US-025 |

**Next Available IDs (as of 2025-10-14):**
- US: US-009 (HLS-002 in progress through US-008, US-003 generated)
- SPEC: SPEC-002 (SPEC-001 used by US-001)
- TASK: TASK-004 (TASK-001/002/003 used by US-001)
- ADR: ADR-001 (none assigned yet)
- SPIKE: SPIKE-001 (none assigned yet)

**Note:** TODO.md tracks only active/upcoming work. Completed work archived to TODO-completed.md.

**Checking Next Available ID:**
```bash
# Find last assigned US ID in TODO.md
grep -oE "US-[0-9]+" TODO.md | sort -t- -k2 -n | tail -1

# Find last assigned SPEC ID in TODO.md
grep -oE "SPEC-[0-9]+" TODO.md | sort -t- -k2 -n | tail -1

# Find last assigned TASK ID in TODO.md
grep -oE "TASK-[0-9]+" TODO.md | sort -t- -k2 -n | tail -1

# Check for duplicate US IDs in artifacts (should return nothing)
find artifacts/backlog_stories -name "US-*.md" | sed 's/.*US-/US-/' | sed 's/_.*//' | sort | uniq -d
```

**Parent Relationship Tracking:**
Parent tracked in artifact metadata (not in ID):

```markdown
## Metadata
- **Story ID:** US-002
- **Parent HLS:** HLS-002 (CI/CD Pipeline)
- **Parent PRD:** PRD-000
```

**Child Artifact ID Assignment:**
- **Tech Spec:** One SPEC per complex US (typically 5+ SP or marked [REQUIRES TECH SPEC])
- **Spike:** One SPIKE per investigation (US with [REQUIRES SPIKE] marker)
- **ADR:** One ADR per major technical decision ([REQUIRES ADR] marker)
- **Task:** Multiple TASKs per US (decomposed from Tech Spec, typically 4-16 hours each)

**Example Lineage:**
```
PRD-000 (Project Foundation)
  └─ HLS-002 (CI/CD Pipeline)
       ├─ US-002 (Pipeline Infrastructure, 5 SP)
       │    ├─ SPEC-XXX (Pipeline Architecture) [if needed]
       │    ├─ TASK-XXX (Create workflow YAML)
       │    └─ TASK-YYY (Configure branch protection)
       ├─ US-003 (Code Quality Checks, 3 SP)
       │    └─ TASK-ZZZ (Configure Ruff)
       └─ US-004 (Type Safety, 3 SP)
            ├─ SPIKE-XXX (MyPy strict mode impact)
            ├─ ADR-XXX (Type checking strategy)
            └─ SPEC-YYY (MyPy configuration)
```

**Generator Guidance:**
- **Backlog Story Generator:** Receives explicit US-XXX ID as input parameter from TODO.md (never auto-generates IDs)
- **Tech Spec Generator:** Receives explicit SPEC-XXX ID as input parameter from TODO.md
- **Task Generator:** Receives range of TASK-XXX IDs as input parameter from TODO.md

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

**Document Version**: 1.7
**Last Updated**: 2025-10-15
**Maintained By**: Context Engineering PoC Team
**Next Review**: End of Phase 1

**Version History:**
- v1.7 (2025-10-15): Added Artifact Path Resolution Algorithm section - explicit rules for resolving path patterns with variable substitution, glob strategies, error message formats, and implementation checklist (Issue #5 - Path Resolution Failures)
- v1.6 (2025-10-14): Added ID Assignment Strategy section - documents global sequential numbering to prevent ID clashing across HLS stories (Issue #4 - ID Management)
- v1.5 (2025-10-13): Added Input Classification System - replaced ambiguous `required` attribute with clear `classification` tiers (Issue #3 - Input Classification)
- v1.4 (2025-10-13): Added centralized Artifact Path Patterns section (Issue #2 - Path Consolidation)
- v1.3 (2025-10-12): Standardized artifact IDs, file naming conventions, and status values across all templates
- v1.2 (2025-10-11): Added Spike artifact to framework (time-boxed technical investigations)
- v1.1 (2025-10-11): Initial comprehensive version

**Related Documents:**
- `/docs/framework_validation_gaps.md` - Known validation gaps and production requirements
- `/docs/sdlc_artifacts_comprehensive_guideline.md` - Section 1.10 covers Metadata Standards and Traceability

---

## Implementation Phase Instructions

**When to use Implementation Phase instructions:**
- Writing Python code, tests, documentation
- Setting up development environment, CI/CD, tooling
- Implementing features from PRDs/Backlog Stories
- Coding tasks after planning phase completes

**Unified CLI Interface:**
- **Use `task <command>` for all development operations** - Taskfile provides language-agnostic interface
- **Run `task --list` to discover available commands** - Self-documenting workflow
- **See [CLAUDE-tooling.md](prompts/CLAUDE/CLAUDE-tooling.md) for complete Taskfile reference**

**Implementation Configuration Files:**
- **[CLAUDE-core.md](prompts/CLAUDE/CLAUDE-core.md)** - Main implementation guide and orchestration (includes Taskfile usage)
- **[CLAUDE-tooling.md](prompts/CLAUDE/CLAUDE-tooling.md)** - Taskfile (unified CLI), UV, Ruff, MyPy, pytest configuration
- **[CLAUDE-testing.md](prompts/CLAUDE/CLAUDE-testing.md)** - Testing strategy, fixtures, coverage
- **[CLAUDE-typing.md](prompts/CLAUDE/CLAUDE-typing.md)** - Type hints, annotations, type safety
- **[CLAUDE-validation.md](prompts/CLAUDE/CLAUDE-validation.md)** - Pydantic models, input validation, security
- **[CLAUDE-architecture.md](prompts/CLAUDE/CLAUDE-architecture.md)** - Project structure, modularity, design patterns

**→ For implementation work, see [CLAUDE-core.md](prompts/CLAUDE/CLAUDE-core.md) which orchestrates all specialized configs.**
