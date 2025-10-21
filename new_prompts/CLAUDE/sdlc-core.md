# SDLC Framework Core Resource

**Resource Name:** sdlc-core
**Resource URI:** mcp://resources/sdlc/core
**Document Version:** 1.0 (Split from CLAUDE.md v2.4)
**Last Updated:** 2025-10-21
**Purpose:** Centralized SDLC framework content including folder structure, dependency flow, markers, ID assignment, and artifact patterns
**Maintained By:** Context Engineering PoC Team
**Parent Document:** CLAUDE.md (Root Orchestrator)

**Usage:** This resource is served by MCP Server and referenced by local CLAUDE.md files across all projects using the Context Engineering Framework.

---

## Framework Design Principles

### Template vs Generator Responsibility

**Single Responsibility Separation:**

**Templates** (`new_prompts/templates/*.xml`):
- **Purpose:** Define artifact structure and content requirements
- **Responsibility:** Specify WHAT sections exist and WHAT format to use
- **Example:** Define that Open Questions must use standardized markers `[REQUIRES SPIKE]`, `[REQUIRES ADR]`, etc.
- **Does NOT:** Contain validation checklists or enforcement logic
- **Audience:** Human reviewers and generators (as structural reference)

**Generators** (`new_prompts/*-generator.xml`):
- **Purpose:** Produce artifacts conforming to template structure
- **Responsibility:** Implement validation logic to enforce template requirements
- **Example:** Validate that Open Questions in v2+ artifacts use markers with required sub-fields
- **Does:** Programmatically check compliance and reject non-conforming artifacts
- **Audience:** Automated artifact generation system

**Validation Specification** (`docs/generator_validation_spec.md`):
- **Purpose:** Define HOW generators should validate artifacts
- **Responsibility:** Provide comprehensive validation rules, error messages, test cases
- **Example:** Specify that `[REQUIRES SPIKE]` must include "Investigation Needed", "Spike Scope", "Time Box", "Blocking" sub-fields
- **Audience:** Generator developers implementing validation logic

**Rationale:**
- **Separation of concerns:** Templates define structure (declarative), generators enforce compliance (imperative)
- **Maintainability:** Validation logic updates don't require template changes
- **Testability:** Generators can be unit tested against validation spec
- **Single source of truth:** Validation spec is authoritative for enforcement logic

**When Updating Templates or Generators:**
1. **Template changes** → Update structural requirements (sections, markers, format)
2. **Validation changes** → Update `docs/generator_validation_spec.md` first, then implement in generators
3. **Never add validation checklists to templates** → Document in generator validation spec instead

**Example (Open Questions Marker System):**
- **Template:** Specifies that v2+ artifacts must use `[REQUIRES SPIKE]` marker with sub-fields
- **Generator:** Validates that marker exists and includes "Investigation Needed", "Spike Scope", "Time Box", "Blocking"
- **Validation Spec:** Documents exact validation rules, error messages, and test cases

---

## Decision Hierarchy for Technical Guidance

**Purpose:** Establish authoritative precedence when multiple sources provide technical guidance. Prevents architectural decision conflicts and generator hallucination for already-decided patterns.

**Problem Addressed:** CLAUDE.md architectural decisions ignored or contradicted by Implementation Research recommendations, causing duplicate decision-making and documentation inconsistency (Lean Analysis Report v1.4 Recommendation 2).

### Three-Tier Precedence System

**Tier 1: CLAUDE.md Files (Authoritative - Decisions Made)**
- **Location:** `new_prompts/CLAUDE/{language}/CLAUDE-*.md` files
- **Content:** Finalized architectural decisions, technology choices, patterns, standards
- **Status:** **Default authoritative** - use unless explicit override justified
- **Override Allowed:** YES - with documented justification and approval (see override process below)
- **Examples:**
  - HTTP framework choice (e.g., Gin for Go REST APIs - `CLAUDE-http-frameworks.md`)
  - Database ORM (e.g., SQLAlchemy async for Python - `CLAUDE-database.md`)
  - Logging library (e.g., structlog for Python - `CLAUDE-logging.md`)
  - Testing framework (e.g., pytest for Python, testify for Go - `CLAUDE-testing.md`)

**Tier 2: Implementation Research (Exploratory - Recommendations)**
- **Location:** `artifacts/research/{product_name}_implementation_research.md`
- **Content:** Exploration of patterns, alternatives analysis, recommendations when CLAUDE.md doesn't cover topic
- **Status:** **Advisory** - used only when CLAUDE.md has no decision on topic
- **Usage Rule:** `IF CLAUDE.md covers topic THEN ignore Implementation Research ELSE use Implementation Research`
- **Examples:**
  - Cache invalidation strategies (when `CLAUDE-caching.md` doesn't exist)
  - Error handling patterns for specific domain (when not standardized in CLAUDE.md)
  - Third-party library selection (when no standard exists)

**Tier 3: Artifact-Specific Decisions (Supplements)**
- **Location:** PRD, US, Tech Spec Open Questions → triggers ADR creation
- **Content:** Product-specific decisions not covered by CLAUDE.md or Implementation Research
- **Status:** **New decisions** - may trigger CLAUDE.md updates if pattern generalizes across project
- **Examples:**
  - Product-specific data model constraints
  - Integration-specific error handling
  - Feature-specific algorithm selection

### CLAUDE.md Override Process

**When Override Justified:**
Artifact-specific context requires deviating from CLAUDE.md decision (rare - requires strong technical justification).

**Required Documentation:**
```markdown
[CLAUDE.md OVERRIDE] {Alternative approach}
- **Original Decision:** CLAUDE-{file}.md:{line} "{decision}"
- **Override Rationale:** {Technical justification specific to this artifact}
- **Approval Status:** [APPROVED BY: {Tech Lead Name} - {Date}] or [REQUIRES TECH LEAD APPROVAL]

Example:
[CLAUDE.md OVERRIDE] Use Chi instead of Gin for this microservice
- **Original Decision:** CLAUDE-http-frameworks.md:238 "Default: Use Gin"
- **Override Rationale:** Client mandate requires stdlib-only dependencies for security audit compliance
- **Approval Status:** [APPROVED BY: Tech Lead John - 2025-10-20]
```

### CLAUDE.md Gap Flagging

**When Implementation Research suggests pattern worth standardizing:**
```markdown
[EXTEND CLAUDE.md]
- **Pattern from Research:** §X.Y {Pattern name from Implementation Research}
- **Generalization Opportunity:** {Why this should become project standard}
- **Proposed File:** CLAUDE-{domain}.md
- **Action:** Tech Lead review for standardization

Example:
[EXTEND CLAUDE.md]
- **Pattern from Research:** §5.3 Cache invalidation with TTL expiration
- **Generalization Opportunity:** Used across 3 services, should standardize TTL values and invalidation strategy
- **Proposed File:** CLAUDE-caching.md
- **Action:** Tech Lead review for standardization (create new CLAUDE file)
```

### Conflict Resolution Examples

**Scenario 1: CLAUDE.md has decision, Implementation Research contradicts**
- **Resolution:** Use CLAUDE.md decision (Tier 1 precedence)
- **Generator Behavior:** Reference CLAUDE.md, ignore Implementation Research recommendation
- **Example:** CLAUDE-http-frameworks.md says "Gin", Implementation Research suggests "chi or gin" → Use Gin

**Scenario 2: CLAUDE.md silent, Implementation Research has recommendation**
- **Resolution:** Use Implementation Research (Tier 2 applies when Tier 1 absent)
- **Generator Behavior:** Reference Implementation Research with `[CLAUDE.md GAP]` marker
- **Example:** No CLAUDE-caching.md, Implementation Research §5.3 recommends TTL strategy → Use §5.3

**Scenario 3: Neither CLAUDE.md nor Implementation Research covers topic**
- **Resolution:** Create artifact-specific decision (Tier 3), document in Open Questions
- **Generator Behavior:** Mark with `[NEW DECISION REQUIRED]` or appropriate marker (`[REQUIRES TECH LEAD]`, `[REQUIRES ADR]`)
- **Example:** Product-specific algorithm choice → Document decision rationale, consider ADR

### Template and Generator Enforcement

**Templates include Decision Hierarchy guidance:**
- PRD Template (lines 118-163): Explicit hierarchy with examples
- Backlog Story Template: References to CLAUDE.md standards
- Tech Spec Template: CLAUDE.md precedence for implementation patterns

**Generators enforce precedence:**
- Check CLAUDE.md files before referencing Implementation Research
- Validate that CLAUDE.md decisions are not contradicted
- Flag conflicts during generation (validation criteria)

**Related Documents:**
- PRD Template: Lines 118-163 (Technical Considerations section)
- Lean Analysis Report v1.4: Recommendation 2 (lines 726-875)
- Generator Validation Spec: Precedence validation rules (if applicable)

---

## Folder Structure

**Single source for directory hierarchy and file naming conventions.**

**Naming Variables:**
- `{XXX}` = Artifact ID (e.g., 005, 042, 123)
- `{N}` = Version number (1, 2, 3)
- `{product_name}` = Product name for research documents
- `{artifact-type}` = Artifact type name (e.g., product-vision, epic, prd)
- `{descriptive-slug}` = Lowercase, underscore-separated slug derived from artifact title (e.g., "Create Production Containerfile" → "production_containerfile")

```
/
   .claude/
      commands/
         generate.md                              # Universal executor
         refine.md                                # Iteration orchestrator

   docs/
      sdlc_artifacts_comprehensive_guideline.md  # SDLC artifacts guideline
      refinements/                               # Refinement plans

   new_prompts/                                  # Generators (XML-formatted)
      CLAUDE/                                    # SDLC framework resources
         sdlc-core.md                            # SDLC framework core (this file)
         python/                                 # Python-specific implementation guides
            CLAUDE-core.md                       # Main implementation orchestrator
            CLAUDE-tooling.md                    # UV, Ruff, MyPy, pytest config
            CLAUDE-*.md                          # Other Python-specific guides
         go/                                     # Go-specific CLAUDE.md files
            CLAUDE-core.md                       # Main implementation orchestrator
            CLAUDE-*.md                          # Go-specific guides
      templates/                                 # Artifact templates (XML-formatted)
         {artifact-type}-template.xml            # Format: prd-template.xml, spike-template.xml
      {artifact-type}-generator.xml              # Format: product-vision-generator.xml, epic-generator.xml

   artifacts/                                    # All generated deliverables
      research/                                  # Research artifacts
         {product_name}_business_research.md     # Format: ai_agent_mcp_server_business_research.md
         {product_name}_implementation_research.md
      product_visions/                           # Product Visions
         VIS-{XXX}_{descriptive-slug}_v{N}.md    # Format: VIS-001_ai_agent_mcp_server_v1.md
      initiatives/                               # Initiatives
         INIT-{XXX}_{descriptive-slug}_v{N}.md   # Format: INIT-001_ai_agent_mcp_infrastructure_v1.md
      epics/                                     # Epics
         EPIC-{XXX}_{descriptive-slug}_v{N}.md   # Format: EPIC-000_project_foundation_bootstrap_v2.md
      prds/                                      # PRDs (CONSOLIDATED - includes HLS-XXX subsections within PRD)
         PRD-{XXX}_{descriptive-slug}_v{N}.md    # Format: PRD-000_project_foundation_bootstrap_v3.md
                                                 # Note: HLS-XXX are subsections within PRD (Lean Analysis v1.4 Strategic Rec - Option 2)
      hls/                                       # High-level user stories (LEGACY - being migrated to PRD subsections)
         HLS-{XXX}_{descriptive-slug}_v{N}.md    # Format: HLS-078_user_authentication_flow_v1.md
                                                 # Note: Existing HLS artifacts pending migration to PRD §HLS-XXX subsections
      funcspecs/                                 # Functional Specifications (detailed behavior specs)
         FS-{XXX}_{descriptive-slug}_v{N}.md     # Format: FS-001_user_login_flow_v1.md
      backlog_stories/                           # Backlog user stories
         US-{XXX}_{descriptive-slug}_v{N}.md     # Format: US-234_implement_user_authentication_v1.md
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
- Language-specific implementation guides organized by subdirectory (Python, Go, etc.) enable multi-language project support
- **HLS Consolidation (v2.2):** High-Level Stories consolidated as subsections within PRD (reduces artifact count from 7 to 6, eliminates navigation overhead) - Lean Analysis v1.4 Strategic Recommendation - Option 2

**Descriptive Slug Derivation Rules:**

For artifacts that include `{descriptive-slug}` (Product Vision, Initiative, Epic, PRD, HLS, and US backlog stories), derive the slug from the artifact title:

1. **Extract key words from title** (typically 2-5 words that capture essence)
2. **Convert to lowercase**
3. **Replace spaces with underscores**
4. **Remove special characters** (parentheses, hyphens become underscores)
5. **Keep concise** (aim for 20-40 characters)

**Examples:**
- Title: "Create Production Containerfile with Multi-Stage Build" → Slug: `production_containerfile_multi_stage_build`
- Title: "Configure Container Build and Run Tasks in Taskfile" → Slug: `container_build_run_tasks_taskfile`
- Title: "Automated Setup Script with Interactive Prompts" → Slug: `automated_setup_script`
- Title: "Implement User Authentication (OAuth 2.0)" → Slug: `implement_user_authentication_oauth`

**Purpose:** Descriptive slugs enable file identification without opening files, improve codebase navigation, and maintain consistency with existing artifacts (US-001 to US-008 pattern).

**Note on Historical Naming:**
- **Current standard (recommended)**: lowercase_with_underscores (e.g., `ai_agent_mcp_server`, `project_foundation_bootstrap`)
- **Legacy artifacts**: Some Initiative and Product Vision files use Title_Case_With_Underscores (e.g., `AI_Agent_MCP_Infrastructure`)
- **For new artifacts**: Always use lowercase_with_underscores for consistency
- **For existing artifacts**: Maintain current format unless performing systematic rename

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
| Product Vision | `artifacts/product_visions/VIS-{XXX}_{descriptive-slug}_v{N}.md` | `artifacts/product_visions/VIS-001_ai_agent_mcp_server_v1.md` |
| Initiative | `artifacts/initiatives/INIT-{XXX}_{descriptive-slug}_v{N}.md` | `artifacts/initiatives/INIT-001_ai_agent_mcp_infrastructure_v4.md` |
| Epic | `artifacts/epics/EPIC-{XXX}_{descriptive-slug}_v{N}.md` | `artifacts/epics/EPIC-000_project_foundation_bootstrap_v2.md` |
| PRD | `artifacts/prds/PRD-{XXX}_{descriptive-slug}_v{N}.md` | `artifacts/prds/PRD-000_project_foundation_bootstrap_v3.md` |
| High-Level Story | `artifacts/hls/HLS-{XXX}_{descriptive-slug}_v{N}.md` | `artifacts/hls/HLS-003_application_skeleton_implementation_v1.md` |
| Functional Spec | `artifacts/funcspecs/FS-{XXX}_{descriptive-slug}_v{N}.md` | `artifacts/funcspecs/FS-001_user_login_flow_v1.md` |
| Backlog Story | `artifacts/backlog_stories/US-{XXX}_{descriptive-slug}_v{N}.md` | `artifacts/backlog_stories/US-001_automated_setup_script_v1.md` |
| Spike | `artifacts/spikes/SPIKE-{XXX}_v{N}.md` | `artifacts/spikes/SPIKE-001_v1.md` |
| ADR | `artifacts/adrs/ADR-{XXX}_v{N}.md` | `artifacts/adrs/ADR-001_v1.md` |
| Tech Spec | `artifacts/tech_specs/SPEC-{XXX}_v{N}.md` | `artifacts/tech_specs/SPEC-001_v1.md` |
| Implementation Task | `artifacts/tasks/TASK-{XXX}_v{N}.md` | `artifacts/tasks/TASK-001_v1.md` |

### Glob Pattern Strategies

```bash
# Strategy 1: Specific artifact by ID and version (most precise)
ls artifacts/hls/HLS-003_application_skeleton_implementation_v1.md
ls artifacts/backlog_stories/US-001_automated_setup_script_v1.md

# Strategy 2: Latest version of specific artifact
ls artifacts/hls/HLS-003_*.md | sort | tail -1
ls artifacts/backlog_stories/US-001_*.md | sort | tail -1

# Strategy 3: All versions of specific artifact
ls artifacts/hls/HLS-003_*.md
ls artifacts/backlog_stories/US-001_*.md

# Strategy 4: All artifacts of type
ls artifacts/hls/HLS-*.md
ls artifacts/backlog_stories/US-*.md

# Strategy 5: Research by product name (when product_name known)
ls artifacts/research/AI_Agent_MCP_Server_*.md

# Strategy 6: Research by type suffix (when product_name unknown)
ls artifacts/research/*_implementation_research.md
ls artifacts/research/*_business_research.md

# Strategy 7: Wildcard search across all artifact directories
find artifacts -name "*HLS-003*"
find artifacts -name "*US-001*"
```

### Error Message Formats

**MANDATORY Input Missing (Exit Code 1):**

```
❌ ERROR: Mandatory input artifact not found

Input Type: High-Level Story
Expected Path: artifacts/hls/HLS-003_application_skeleton_implementation_v1.md
Classification: MANDATORY
Status Requirement: Approved

Generator cannot proceed without mandatory input.

Action Required:
1. Verify HLS-003 exists at expected path
2. Ensure Status field = "Approved" in artifact metadata
3. Retry generator execution

Search Patterns Tried:
- artifacts/hls/HLS-003_application_skeleton_implementation_v1.md (exact path)
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
└── PRD (CONSOLIDATED - includes HLS subsections)
    ├── Requires: Epic (mandatory)
    ├── + Business Research (recommended - market validation)
    ├── + Implementation Research (recommended - technical feasibility)
    ├── Contains: Requirements (FR-XX, NFR-XX) + High-Level User Stories (HLS-XXX subsections)
    └── **HLS Consolidation:** High-Level Stories now subsections within PRD (Lean Analysis v1.4 Strategic Recommendation - Option 2)

↓

Story Phase
├── Functional Specification (FuncSpec) - NEW (Lean Analysis Recommendation 1)
│   ├── Requires: PRD (mandatory - single document with multiple sections)
│   │   ├── §HLS-XXX subsection (parent high-level story)
│   │   └── Referenced FR-XX requirements (traceability)
│   ├── + Implementation Research (recommended - for I/O schema examples)
│   ├── Purpose: Detailed functional behavior (WHAT system does) with explicit I/O contracts, Happy Paths, Alternative Flows, Error Handling
│   ├── **Role:** REFERENCE artifact (not decomposition artifact)
│   └── **§Implementation Scope:** References parent HLS decomposition (US-AAA, US-BBB, US-CCC) for traceability
│
└── Backlog Story
    ├── **Source:** Decomposed from PRD §HLS-XXX §Decomposition (US-AAA, US-BBB, US-CCC)
    ├── Requires: PRD (mandatory - single document with multiple sections)
    │   ├── §HLS-XXX subsection (parent high-level story with decomposition)
    │   └── Referenced FR-XX requirements (for context, if needed)
    ├── + FuncSpec (recommended - eliminates 60-80% of I/O schema errors, used as reference)
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
│   ├── + Implementation Research (recommended)
│   ├── + CLAUDE-*.md files (conditional - check existing architectural decisions, Tier 1 precedence)
│   └── + Spike findings (conditional - if spike completed)
│
└── Tech Spec
    ├── Requires: Backlog Story (mandatory)
    ├── + Implementation Research (mandatory)
    ├── + CLAUDE-*.md files (conditional - implementation standards, Tier 1 precedence per Decision Hierarchy)
    ├── + Spike findings (conditional - if spike completed)
    ├── + ADR (conditional - architectural decisions)
    └── Decomposes into: Implementation Tasks (TASK-AAA, TASK-BBB, TASK-CCC placeholders, always)

↓

Implementation Phase
└── Implementation Task
    ├── Generated from: Backlog Story (optional) OR Tech Spec (always)
    ├── Requires: Tech Spec (if complex story) OR Backlog Story (if simple story)
    └── Unit of work: 4-16 hours (sprint-ready task)
```

**Key Principles:**
- **INIT-000 (Foundation Initiative)**: For greenfield/new projects only. Contains EPIC-000 (Project Foundation & Bootstrap). Establishes infrastructure before feature development. No dependencies.
- **INIT-001+ (Feature Initiatives)**: For feature delivery. Depends on INIT-000 (if greenfield). Contains EPIC-001, EPIC-002, etc.
- **Epic Generation**: Can be generated from Product Vision (direct) OR Initiative (decomposition). Use mutually exclusive input selection.
- **Business Research** flows into all business-phase artifacts (Vision, Initiative, Epic, PRD with HLS subsections)
- **Implementation Research** flows into technical-phase artifacts (PRD, FuncSpec, Backlog Story, Spike, ADR, Tech Spec)
- **CLAUDE-*.md files** provide implementation standards for technical artifacts (ADR, Tech Spec). Per Decision Hierarchy: CLAUDE.md (Tier 1 - authoritative) takes precedence over Implementation Research (Tier 2 - exploratory)
- **PRD is unique**: Transition phase artifact that may use BOTH research documents AND contains consolidated HLS-XXX subsections (Lean Analysis v1.4 Strategic Recommendation - Option 2)
- **HLS Consolidation**: High-Level Stories are subsections within PRD (not separate artifacts). Artifact count: 6 types (Epic, PRD+HLS, FuncSpec, US, Tech Spec, Task)
- **Spike is optional**: Only created when Backlog Story or Tech Spec has [REQUIRES SPIKE] marker
- **Decomposition Chain**:
  - Initiative → Epics (EPIC-AAA, EPIC-BBB, EPIC-CCC)
  - PRD §HLS-XXX → Backlog Stories (US-AAA, US-BBB, US-CCC in §Decomposition)
  - Backlog Story (simple) → Direct implementation (no tasks)
  - Backlog Story (medium) → Tasks (optional: TASK-AAA, TASK-BBB, TASK-CCC)
  - Backlog Story (complex) → Tech Spec → Tasks (ALWAYS: TASK-AAA, TASK-BBB, TASK-CCC)
  - **FuncSpec does NOT decompose** - it's a REFERENCE artifact for I/O details
- **Placeholder IDs**: All sub-artifacts use standardized AAA/BBB/CCC alphabetic sequence. Resolved to final IDs during approval workflow (US-071).
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

All SDLC artifacts use a consistent marker system to classify uncertainties and route them to appropriate resolution paths.

### Version Lifecycle (v1 → v2+)

**Version 1 Artifacts (Initial Generation):**
- Open Questions should include **Recommendations** for each question (exploratory, not yet decided)
- Include alternatives, context, decision criteria
- No markers required in v1 (questions are exploratory)
- Example format:
  ```markdown
  ## Open Questions

  - How should error responses be structured to match MCP SDK expectations?
    - **Recommendation:** Review MCP SDK documentation for error response schema patterns
    - **Alternatives:**
      - Option A: Mirror HTTP status code structure (400/500 codes)
      - Option B: Custom error object with code/message/details fields
      - Option C: Follow MCP protocol error conventions
    - **Decision Needed By:** Product Owner + Tech Lead
  ```

**After Feedback (Version 2+):**
- Answered questions MUST move to **"Decisions Made"** section
- Remaining unresolved questions MUST use standardized markers
- Format for Decisions Made:
  ```markdown
  ## Decisions Made

  **Q1: How should error responses be structured?**
  - **Decision:** Follow MCP protocol error conventions (Option C)
  - **Rationale:** Ensures compatibility with MCP clients, standard error handling
  - **Decided By:** Tech Lead John (2025-10-20)
  ```

**PROHIBITED in v2+ artifacts:**
- ❌ Free-form text: "Decision: Spike needed for this"
- ❌ Generic actions: "Action Required: Create spike to investigate..."
- ✅ Use standardized markers with required sub-fields instead

**Exception - Meta-instruction Only:**
"Action Required:" text may be used ONLY for strong emphasis when markers are missing:
```markdown
⚠️ **ACTION REQUIRED:** This artifact has 3 open questions without markers.
Add [REQUIRES SPIKE] or [REQUIRES TECH LEAD] markers before finalization. ⚠️
```
(This is a meta-instruction about the artifact itself, not the actual question documentation)

---

### Standardized Marker Formats with Required Sub-fields

**Strategic/Resource Level (Initiative):**

```markdown
[REQUIRES EXECUTIVE DECISION]
- **Decision Needed:** {What needs executive approval}
- **Options Considered:** {List alternatives}
- **Business Impact:** {Revenue, risk, resource implications}
- **Decision Deadline:** {Date by which decision needed}
```

```markdown
[REQUIRES PORTFOLIO PLANNING]
- **Impact:** {Affects which initiatives or roadmap items}
- **Timeline Dependencies:** {When this needs to be decided}
- **Resource Impact:** {Teams or budgets affected}
```

```markdown
[REQUIRES RESOURCE PLANNING]
- **Resource Type:** {FTE, budget, infrastructure}
- **Quantity Needed:** {Number of people, dollar amount, capacity}
- **Duration:** {Timeline for resource need}
- **Blocking:** {What's blocked without resources}
```

```markdown
[REQUIRES ORGANIZATIONAL ALIGNMENT]
- **Stakeholders:** {List departments/teams requiring alignment}
- **Alignment Topic:** {What needs consensus}
- **Impact Without Alignment:** {Risk of proceeding without consensus}
- **Decision Deadline:** {Date}
```

**Business Level (Epic):**

Business questions only (market, business model, compliance). No technical markers at Epic phase.

```markdown
[REQUIRES EXECUTIVE DECISION]
- **Decision Needed:** {Business strategy or investment decision}
- **Options Considered:** {Strategic alternatives}
- **Business Impact:** {Revenue, market position, risk}
- **Decision Deadline:** {Date}
```

**Bridge Level (PRD):**

```markdown
[REQUIRES PM + TECH LEAD]
- **Trade-off:** {Product vs. technical tension}
- **PM Perspective:** {User experience, business value considerations}
- **Tech Perspective:** {Implementation complexity, technical debt considerations}
- **Decision Needed By:** {Date}
```

**User/UX Level (High-Level Story):**

```markdown
[REQUIRES UX RESEARCH]
- **Research Question:** {User behavior to validate}
- **Research Method:** {Survey, usability test, A/B test}
- **Timeline:** {Duration}
- **Blocking:** {What's blocked until research complete}
```

```markdown
[REQUIRES UX DESIGN]
- **Design Scope:** {What needs design input}
- **Design Deliverables:** {Mockups, prototypes, design system components}
- **Timeline:** {When design needed}
- **Blocking:** {What's blocked without design}
```

```markdown
[REQUIRES PRODUCT OWNER]
- **Decision Needed:** {Scope, priority, feature clarification}
- **Context:** {Why this decision matters}
- **Impact:** {What's affected by decision}
```

**Implementation Level (Backlog Story):**

```markdown
[REQUIRES SPIKE]
- **Investigation Needed:** {Technical uncertainty to resolve}
- **Spike Scope:** {What to research/prototype}
- **Time Box:** {1-3 days maximum}
- **Blocking:** {What implementation steps blocked}
```

```markdown
[REQUIRES ADR]
- **Decision Topic:** {Architectural decision needed}
- **Alternatives:** {Options to evaluate in ADR}
- **Impact Scope:** {What components/systems affected}
- **Decision Deadline:** {Date}
```

```markdown
[REQUIRES TECH LEAD]
- **Technical Question:** {Senior input needed on what}
- **Context:** {Why this needs tech lead review}
- **Blocking:** {What's blocked}
```

```markdown
[BLOCKED BY]
- **Dependency:** {External system, team, decision}
- **Expected Resolution:** {Date/milestone when unblocked}
- **Workaround Available:** {Yes/No, if yes describe}
```

**Technical Detail Level (Tech Spec, Implementation Task):**

```markdown
[REQUIRES TECH LEAD]
- **Technical Question:** {Senior input needed on what}
- **Context:** {Why this needs tech lead review}
- **Blocking:** {What's blocked}
```

```markdown
[CLARIFY BEFORE START]
- **Clarification Needed:** {Ambiguity to resolve}
- **Stakeholder:** {Who can clarify}
- **Blocking:** {Can't start task until clarified}
```

```markdown
[BLOCKED BY]
- **Dependency:** {External system, team, decision}
- **Expected Resolution:** {Date/milestone when unblocked}
- **Workaround Available:** {Yes/No, if yes describe}
```

```markdown
[NEEDS PAIR PROGRAMMING]
- **Complexity Area:** {What's complex requiring collaboration}
- **Skills Needed:** {Expertise required}
- **Duration:** {Estimated pairing time}
```

```markdown
[TECH DEBT]
- **Tech Debt Description:** {Existing constraint}
- **Workaround:** {How to work around constraint}
- **Future Resolution:** {When/how to address properly}
```

---

### Spike Workflow Example

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

## Placeholder ID Conventions

**Purpose:** Generators use placeholder IDs for sub-artifacts to enable automated approval workflow and prevent ID collisions.

**Workflow:**
1. **Generation Phase:** Generators create artifacts with placeholder IDs (e.g., HLS-AAA, HLS-BBB, US-XXX)
2. **Storage Phase:** Artifacts stored in Draft status with placeholders intact
3. **Approval Phase:** `approve_artifact` tool (US-071) resolves placeholders to final IDs via `reserve_id_range` API
4. **Task Creation Phase:** Sub-artifact tasks created with final IDs and resolved inputs

**Placeholder Format:**

**STANDARDIZED SEQUENCE:** All sub-artifacts use alphabetic sequence: AAA, BBB, CCC, DDD, EEE, FFF, GGG, HHH, III, JJJ, KKK, LLL, MMM, NNN, OOO, PPP, QQQ, RRR, SSS, TTT, UUU, VVV, WWW, XXX, YYY, ZZZ

| Artifact Type | Placeholder Format | Example | Final ID Format |
|---------------|-------------------|---------|-----------------|
| Epic | EPIC-AAA, EPIC-BBB, EPIC-CCC | EPIC-AAA → EPIC-001 | EPIC-001, EPIC-002 |
| HLS (PRD subsections) | HLS-AAA, HLS-BBB, HLS-CCC | HLS-AAA → HLS-012 | HLS-012, HLS-013 |
| Backlog Story | US-AAA, US-BBB, US-CCC | US-AAA → US-073 | US-073, US-074 |
| Task | TASK-AAA, TASK-BBB, TASK-CCC | TASK-AAA → TASK-012 | TASK-012, TASK-013 |

**Generator Usage:**

| Generator | Creates Sub-Artifacts | Placeholder IDs Used |
|-----------|----------------------|---------------------|
| `initiative-generator.xml` | Epics | EPIC-AAA, EPIC-BBB, EPIC-CCC (for INIT-001+) |
| `epic-generator.xml` | 1 PRD | No placeholder (uses same numeric ID: EPIC-006 → PRD-006) |
| `prd-generator.xml` | HLS subsections + US decomposition | HLS-AAA, HLS-BBB, HLS-CCC (within PRD §High-Level User Stories)<br>US-AAA, US-BBB, US-CCC (in §Decomposition) |
| `funcspec-generator.xml` | *(none - reference artifact)* | US-AAA, US-BBB, US-CCC (REFERENCES parent PRD §HLS-XXX decomposition)<br>Documented in §Implementation Scope for traceability only |
| `backlog-story-generator.xml` | Tasks (optional) | TASK-AAA, TASK-BBB, TASK-CCC (if not pre-allocated in TODO.md) |
| `tech-spec-generator.xml` | Tasks (always) | TASK-AAA, TASK-BBB, TASK-CCC (if not pre-allocated in TODO.md) |

**Alphabetic Sequence:**
- Use 3-letter alphabetic suffixes: AAA, BBB, CCC, DDD, EEE, FFF, GGG, HHH, III, JJJ, KKK, LLL, MMM, NNN, OOO, PPP, QQQ, RRR, SSS, TTT, UUU, VVV, WWW, XXX, YYY, ZZZ
- For >26 sub-artifacts (rare): Use AAAA, BBBB, CCCC, etc.

**Examples:**

**Initiative with 4 Epics:**
```markdown
## Supporting Epics
1. **EPIC-AAA:** User Authentication & Authorization
2. **EPIC-BBB:** Dashboard & Analytics
3. **EPIC-CCC:** Data Management
4. **EPIC-DDD:** Reporting System
```

**PRD with 6 HLS Subsections:**
```markdown
## High-Level User Stories

### HLS-AAA: User Registration Flow
...

### HLS-BBB: Login & Session Management
...

### HLS-CCC: Profile Management
...
```

**Backlog Story with 3 Tasks:**
```markdown
## Implementation Tasks Evaluation
**Decision:** Tasks Needed
**Rationale:** 8 SP story with 3 distinct integration points
**Proposed Tasks:**
1. **TASK-AAA:** Implement authentication API client (6 hours)
2. **TASK-BBB:** Add session management middleware (4 hours)
3. **TASK-CCC:** Update UI components for auth state (6 hours)
```

**Tech Spec with 6 Tasks:**
```markdown
## Implementation Tasks
**Total Tasks:** 6 tasks (estimated 42 hours)

1. **TASK-AAA:** Implement database schema and migrations - Data Layer - 6 hours
2. **TASK-BBB:** Create user repository with CRUD operations - Data Layer - 8 hours
3. **TASK-CCC:** Implement authentication service - Business Logic - 10 hours
4. **TASK-DDD:** Build login/logout API endpoints - API Layer - 8 hours
5. **TASK-EEE:** Write unit tests for auth service - Testing - 6 hours
6. **TASK-FFF:** Add integration tests for auth flow - Testing - 4 hours

**Task Dependencies:**
- TASK-BBB depends on TASK-AAA (schema must exist)
- TASK-CCC depends on TASK-BBB (needs repository)
- TASK-DDD depends on TASK-CCC (needs service)
- TASK-EEE, TASK-FFF can run in parallel after TASK-DDD
```

**Special Cases:**
- **EPIC-000:** Reserved for Foundation Initiative (INIT-000). Uses final ID, not placeholder.
- **Pre-allocated IDs:** If TODO.md pre-allocates IDs (e.g., TASK-012, TASK-013), use those instead of placeholders.

**Reference:** See US-071 (approve_artifact tool) for placeholder resolution workflow.

---

## ID Assignment Strategy

**Global Sequential Numbering:** All artifact IDs within a type (US, SPEC, ADR, TASK, SPIKE) are globally unique and sequential across the entire project.

**Purpose:** Prevents ID clashing when multiple HLS stories generate backlog stories. Ensures unique identification across all artifacts.

**Assignment Process:**
1. **Planning Phase:** Assign IDs in TODO.md when creating generator tasks
2. **Registry:** TODO.md acts as the authoritative ID registry
3. **Immutability:** Once assigned, IDs never change (even if artifact deleted)
4. **Sequence:** Next available ID = (last assigned ID + 1)

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
| Functional Spec | FS-XXX | FS-001 |
| Backlog Story | US-XXX | US-234 |
| Spike | SPIKE-XXX | SPIKE-042 |
| ADR | ADR-XXX | ADR-008 |
| Tech Spec | SPEC-XXX | SPEC-015 |
| Implementation Task | TASK-XXX | TASK-567 |

**Status Value Standards**:
- Research (Business/Implementation): Draft → In Review → Finalized
- Strategic (Vision/Initiative/Epic): Draft → In Review → Approved → Planned/Active → In Progress → Completed
- Requirements (PRD/HLS): Draft → In Review → Approved → Ready → In Progress → Completed
- Implementation (Backlog Story): Backlog → Ready → In Progress → In Review → Done
- Implementation (Task): To Do → In Progress → In Review → Done
- Spike: Planned → In Progress → Completed
- Architecture (ADR/Tech Spec): Proposed → Accepted → Active → Deprecated/Superseded

---

## Strategic SDLC Decisions

### HLS Consolidation Decision (Lean Analysis Strategic Recommendation)

**Decision Date:** 2025-10-20

**Question:** Should we consolidate High-Level Story (HLS) into PRD or keep HLS as separate artifact?

**Options Evaluated:**
- **Option 1:** Keep all artifacts + Add FuncSpec (7 artifact types total)
  - Flow: Epic → PRD → HLS → FuncSpec → US → Tech Spec → Task
  - Strategy: Make existing artifacts LEANER (reduce business overlap 50%), ADD FuncSpec to fill functional gap
  - Trade-off: More artifacts to manage, but clear separation of concerns

- **Option 2:** Merge HLS into PRD + Add FuncSpec (6 artifact types total)
  - Flow: Epic → PRD (includes HLS subsections) → FuncSpec → US → Tech Spec → Task
  - Strategy: Consolidate HLS as subsection within PRD, eliminate artifact navigation overhead
  - Trade-off: Single artifact contains both requirements and user stories, reduces navigation

**Decision:** **Option 2 - Merge HLS into PRD (Consolidation)**

**Rationale:**
1. **Eliminates artifact navigation overhead:** Single PRD contains requirements (FR-XX) AND high-level user stories
2. **Reduces artifact count:** 6 artifact types instead of 7 (Epic, PRD+HLS, FuncSpec, US, Tech Spec, Task)
3. **Aligns with "consolidation" terminology:** Merging artifacts, not expanding them
4. **Maintains user story structure:** HLS becomes dedicated section within PRD ("High-Level User Stories")
5. **Preserves FuncSpec value:** Detailed functional specs still bridge gap between HLS (in PRD) and US

**Trade-offs Accepted:**
- ✅ **Pro:** Reduced artifact count (6 vs 7 types)
- ✅ **Pro:** Single source for requirements AND user stories (eliminates PRD ↔ HLS navigation)
- ✅ **Pro:** Clear precedence: Epic business context → PRD requirements + user stories → FuncSpec detailed behavior → US implementation
- ❌ **Con:** Larger PRD documents (includes HLS content as subsections)
- ❌ **Con:** PRD serves dual purpose (requirements definition + user story organization)

**Mitigation:**
- PRD structured with clear sections: Executive Summary, Requirements (FR-XX, NFR-XX), High-Level User Stories (HLS-XXX subsections), Technical Considerations
- Each HLS subsection within PRD follows standard user story format: "As a [user], I want...", Acceptance Criteria, Decomposition into Backlog Stories
- FuncSpec references PRD §High-Level User Stories for detailed functional specification
- Business overlap still reduced 50% via Epic Context cross-referencing

**Artifact Count:** 6 types (Epic, PRD+HLS, FuncSpec, US, Tech Spec, Task)

**Artifact Flow:**
```
Epic (Business goals, success metrics)
  └─ PRD (Requirements: FR-XX, NFR-XX + High-Level User Stories: HLS-XXX)
      └─ FuncSpec (Detailed functional behavior with I/O schemas)
          └─ US (Implementation-ready backlog stories)
              ├─ Tech Spec (Technical design)
              └─ Task (4-16 hour work items)
```

**Implementation Status:** **Decision made, PARTIALLY IMPLEMENTED (Core generators complete, migration pending)**

**Completed Implementation Tasks (2025-10-20):**
1. ✅ **PRD Template Updated (v1.9 → v2.0):** Added "High-Level User Stories" section with complete HLS subsection structure
   - Location: `new_prompts/templates/prd-template.xml`
   - Structure: HLS-XXX subsections with User Story Statement, Value Contribution, Primary User Flow, Acceptance Criteria, Decomposition, Dependencies
   - Preserves HLS-XXX ID format for traceability

2. ✅ **PRD Generator Updated (v1.7 → v2.0):** Generates 3-8 HLS subsections within PRD
   - Location: `new_prompts/prd-generator.xml`
   - Step 7 replaced: "Define User Stories" → "Generate High-Level User Stories Subsections"
   - Validation: Added 16 HLS-XX validation criteria (HLS-01 to HLS-16) covering structure, format, completeness
   - Total validation criteria: 53 (CQ: 14, UT: 8, CC: 6, HLS: 16, OQ: 9)

3. ✅ **FuncSpec Generator Updated (v1.1 → v2.0):** References PRD §HLS-XXX subsections instead of separate HLS artifacts
   - Location: `new_prompts/funcspec-generator.xml`
   - Input: Loads PRD, navigates to §High-Level User Stories, extracts specific HLS-XXX subsection
   - Traceability: References both PRD FR-XX requirements AND PRD §HLS-XXX subsections

4. ✅ **Backlog Story Generator Updated (v1.7 → v2.0):** References parent PRD §HLS-XXX subsections for decomposition
   - Location: `new_prompts/backlog-story-generator.xml`
   - Input: Loads PRD, navigates to §HLS-XXX subsection, extracts decomposition plan
   - Traceability: US-XXX metadata includes both "Parent HLS: PRD §HLS-YYY" and "Parent PRD: PRD-XXX"

**Pending Implementation Tasks:**
5. ⏳ **Migrate existing HLS artifacts to PRD subsections** (one-time data migration)
   - Action: Move content from `artifacts/hls/HLS-XXX_v*.md` files into corresponding PRD §High-Level User Stories subsections
   - Scope: HLS-001 through HLS-011 (11 artifacts)
   - Timing: Before generating new PRDs with consolidated structure

6. ⏳ **Archive HLS template and generator** (no longer needed as separate artifacts)
   - Action: Move to archive folder or mark as deprecated
   - Files: `new_prompts/templates/high-level-user-story-template.xml`, `new_prompts/high-level-user-story-generator.xml`
   - Timing: After migration complete and tested

**Current State (as of 2025-10-20):**
- ✅ PRD template v2.0 includes HLS subsection structure (consolidated)
- ✅ PRD generator v2.0 generates HLS subsections within PRD (ready for use)
- ✅ FuncSpec generator v2.0 references PRD §HLS-XXX (ready for use)
- ✅ Backlog Story generator v2.0 references PRD §HLS-XXX (ready for use)
- ⏳ Separate HLS template still exists (pending archive)
- ⏳ Separate HLS generator still exists (pending archive)
- ⏳ Existing HLS artifacts in `artifacts/hls/` (pending migration to PRD subsections)
- **New PRDs generated with v2.0 will include HLS subsections** (consolidated structure operational)

**Related Recommendations:**
- **Recommendation 1 (Implemented):** FuncSpec artifact added to fill Happy Path/I/O gap
- **Recommendation 3 (Implemented):** Business overlap reduced 50% through cross-referencing
- **Recommendation 4 (Implemented):** Happy Path format standardized in FuncSpec template

**Reference:** Lean Analysis Report v1.4 lines 1746-1845 (Strategic Recommendation: Artifact Consolidation - Option 2)

---

**Document Version**: 1.0
**Last Updated**: 2025-10-21
**Maintained By**: Context Engineering PoC Team
**Source**: Split from CLAUDE.md v2.4 (US-028: Refactor Main CLAUDE.md into Orchestrator + SDLC Resource)

**Version History:**
- v1.0 (2025-10-21): Initial version created by extracting framework-wide sections from CLAUDE.md v2.4. Contains Framework Design Principles, Decision Hierarchy, Folder Structure, Artifact Path Resolution, SDLC Dependency Flow, Input Classification, Spike Workflow, Open Questions Markers, Placeholder IDs, ID Assignment Strategy, and Strategic SDLC Decisions. Served as MCP resource at mcp://resources/sdlc/core.

**Related Documents:**
- `/CLAUDE.md` - Root orchestrator (references this resource)
- `/docs/framework_validation_gaps.md` - Known validation gaps and production requirements
- `/docs/sdlc_artifacts_comprehensive_guideline.md` - Section 1.10 covers Metadata Standards and Traceability
- `/docs/generator_validation_spec.md` - Generator validation specification for enforcing standardized marker system (implementation guide for generators)
- `/docs/lean/report.md` - SDLC Documentation Optimization Report (Lean Analysis v1.4 with 5 tactical recommendations)
