# Master Plan - Context Engineering PoC

**Document Version**: 1.1
**Status**: Active - Phase 1 (PoC)
**Last Updated**: 2025-10-13

---

## Current Phase: Phase 1 - Bootstrap & Foundation

**Current Status**: HLS-001 v2 created with feedback decisions; 4 additional HLS tasks added for complete PRD-000 coverage
**Last Completed**: TASK-013: Execute High-level User Story Generator v1 (PRD-000 - HLS-001)
**Next Task**: TASK-014 (Generate backlog stories from HLS-001) OR TASK-019/020/021/022 (Generate additional HLS stories) OR Update CLAUDE-tooling.md (critical gap from TASK-018)
**Completion**: 12/22 tasks (55%)

---

## Phase 1: Bootstrap & Foundation (PoC)

### TASK-001: Extract & Generate Templates
**Priority**: Critical
**Dependencies**: None
**Estimated Time**: 30 minutes
**Status**: ✅ Completed

**Description**:
Extract templates from research document (Section 6.1-6.4) and convert to XML format. Generate missing templates not explicitly defined in research.

**Required Templates**:
1. Product Vision Template (generate - not in research)
2. Epic Template (generate - not in research)
3. PRD Template (extract from Section 6.1, lines 630-728)
4. ADR Template (extract from Section 6.2, lines 773-849)
5. Technical Specification Template (extract from Section 6.3, lines 905-1016)
6. Backlog Story Template (extract from Section 6.4, lines 1063-1108)
7. Generator Schema Template (create for consistency)

**Success Criteria**:
- [x] All 7 templates exist in `/prompts/templates/*.xml`
- [x] Each template is valid XML with proper CDATA sections
- [x] Validation checklists removed from templates (moved to generators)
- [x] Metadata references source sections (where applicable)
- [x] Instructions are clear and actionable
- [x] Generator schema template created

**Output Artifacts**:
- `/prompts/templates/product-vision-template.xml` ✅
- `/prompts/templates/epic-template.xml` ✅
- `/prompts/templates/prd-template.xml` ✅
- `/prompts/templates/adr-template.xml` ✅
- `/prompts/templates/tech-spec-template.xml` ✅
- `/prompts/templates/backlog-story-template.xml` ✅
- `/prompts/templates/generator-schema.xml` ✅

---

### TASK-002: Generate Product Vision Generator Prompt
**Priority**: Critical
**Dependencies**: TASK-001 (product-vision-template.xml must exist)
**Estimated Time**: 45 minutes
**Status**: ✅ Completed

**Description**:
Create the first generator prompt that will produce Product Vision documents.

**Success Criteria**:
- [x] Follows generator prompt XML schema template
- [x] References correct template path
- [x] Includes validation checklist in generator (not template)
- [x] Specifies dual outputs (vision doc)
- [x] Contains research step for competitive analysis
- [x] Constraints marked as [CUSTOMIZE PER PRODUCT]
- [x] Valid XML syntax

**Output Artifacts**:
- `/prompts/product-vision-generator.xml` ✅

---
### TASK-003: Convert Research Templates into XML format
**Priority**: Critical
**Dependencies**: none
**Estimated Time**: 45 minutes
**Status**: ✅ Completed

**Description**:
Convert Input Templates from Markdown into XML format. Use referenced file as an example

**Input Templates**:
- `prompts/templates/business_research_template.md`
- `prompts/templates/implementation_research_template.md`
- `prompts/templates/research-artifact-template.md`

**References**:
- `prompts/templates/adr-template.xml` (ADR Template)

**Success Criteria**:
- [x] business_research_template converted into a valid XML file format
- [x] implementation_research_template converted into a valid XML file format
- [x] research-artifact-template converted into a valid XML file format

**Output Artifacts**:
- `prompts/templates/business_research_template.xml` ✅
- `prompts/templates/implementation_research_template.xml` ✅
- `prompts/templates/research-artifact-template.xml` ✅
---

## Phase 1.1: Generator Execution & Iteration

### TASK-004: Execute Product Vision Generator v1
**Priority**: Critical
**Dependencies**: None
**Estimated Time**: 20 minutes
**Status**: ✅ Completed
**Context**: New session C1 required
**Generator Name**: product-vision

**Description**:
Execute Product Vision Generator in standalone context to produce first iteration of Product Vision document.

**Command**: `/generate TASK-004`

**Input artifacts**:
- Business Research - `artifacts/research/AI_Agent_MCP_Server_business_research.md`

**Completion Notes**:
- Product Vision v1 generated: `/artifacts/product_visions/VIS-001_AI_Agent_MCP_Server_v1.md`
- All template sections populated with content extracted from business research
- Traceability maintained with §X section references throughout
- Business-focused (WHAT/WHY), implementation-agnostic per guidelines
- Ready for human critique (TASK-005)

---

## Phase 1.2: Cascade to Initiative Generation

### TASK-008: Execute Initiative Generator v1
**Priority**: Critical
**Dependencies**: None
**Estimated Time**: 20 minutes
**Status**: ✅ Completed
**Context**: New session C2 required
**Generator Name**: initiative

**Description**:
Execute Initiative Generator in standalone context to decompose Product Vision into Initiative documents.

**Production Requirement**: Should use approved Product Vision v3 as input
**Current State**: Executed with Product Vision v1 (Draft) - acceptable for PoC, risk of rework if Vision changes in v2/v3

**Command**: `/generate TASK-008`

**Input Artifacts:**
- Primary: `/artifacts/product_vision_v3.md` (approved) - **Production requirement**
- Primary (Current): `/artifacts/product_visions/VIS-001_AI_Agent_MCP_Server_v1.md` (Draft) - **Used for PoC**
- Secondary (optional): `/artifacts/research/AI_Agent_MCP_Server_business_research.md`

**Completion Notes:**
- Initiative INIT-001 generated: `/artifacts/initiatives/INIT-001_AI_Agent_MCP_Infrastructure_v1.md`
- Strategic objective and 5 Key Results derived from Product Vision success metrics
- 5 supporting epics mapped from Product Vision key capabilities
- Budget estimated at $800K-$1.2M with detailed breakdown
- 12-month timeline across 3 phases aligned with Product Vision roadmap
- All template sections populated with executive-level content
- Ready for human critique and executive review

---

### TASK-009: Execute Epic Generator v1
**Priority**: Critical
**Dependencies**: None
**Estimated Time**: 20 minutes
**Status**: ✅ Completed
**Context**: New session C3 required
**Generator Name**: epic

**Description**:
Execute Epic Generator in standalone context to decompose Product Vision into Epic documents.

**Production Requirement**: Should use approved Product Vision v3 as input
**Current State**: Executed with Product Vision v1 (Draft) - acceptable for PoC, risk of rework if Vision changes in v2/v3

**Command**: `/generate TASK-009`

**Input Artifacts:**
- Primary: `/artifacts/product_vision_v3.md` (approved) - **Production requirement**
- Primary (Current): `/artifacts/product_visions/VIS-001_AI_Agent_MCP_Server_v1.md` (Draft) - **Used for PoC**
- Secondary (optional): `/artifacts/research/AI_Agent_MCP_Server_business_research.md`

**Completion Notes:**
- 5 epics generated from Product Vision key capabilities
- EPIC-001: Project Management Integration (Q1-Q2, 60-80 SP, 6-8 weeks)
- EPIC-002: Organizational Knowledge Access (Q1-Q2, 80-100 SP, 8-10 weeks, HIGH complexity)
- EPIC-003: Secure Authentication & Authorization (Q2, 70-90 SP, 8-10 weeks, blocks EPIC-001/002)
- EPIC-004: Production-Ready Observability (Q2-Q3, 60-75 SP, 6-8 weeks)
- EPIC-005: Automated Deployment Configuration (Q3, 50-65 SP, 6-7 weeks)
- All epics have complete scope, success metrics, user stories, acceptance criteria
- Epic dependencies mapped (EPIC-003 blocks EPIC-001, EPIC-002)
- Ready for human critique and PRD generation

---

## Phase 1.3: PRD Generation

### TASK-012: Execute PRD Generator v1 (Epic 000)
**Priority**: Critical
**Dependencies**: TASK-011
**Estimated Time**: 25 minutes
**Status**: ✅ Completed
**Context**: New session C3 required
**Generator Name**: prd

**Description**:
Execute PRD Generator for first epic in standalone context.

**Command**: `/generate TASK-012`

**Input Data:**
- EPIC-000

**Completion Notes:**
- PRD-000 v1 generated: `/artifacts/prds/PRD-000_project_foundation_bootstrap_v1.md`
- All template sections populated from EPIC-000, Business Research, Implementation Research
- 18 functional requirements (FR-01 to FR-18) with detailed acceptance criteria
- NFRs separated: Business-level (accessibility, maintainability) + Technical (performance, security, observability)
- 3 user personas with detailed use cases and user journeys
- Validation: 26/27 criteria passed (1 warning: parent epic in Draft status - acceptable for PoC)
- Ready for human critique (TASK-013 or proceed to High-Level Story generation)

---

## Phase 1.4: High-level User Story Generation

### TASK-013: Execute High-level User Story Generator v1 (PRD-000)
**Priority**: Critical
**Dependencies**: TASK-012
**Estimated Time**: 25 minutes
**Status**: ✅ Completed
**Context**: New session C3 required
**Generator Name**: high-level-user-story

**Description**:
Execute High-level Story Generator for first PRD in standalone context.

**Command**: `/generate TASK-013`

**Input Data:**
- PRD-000

**Completion Notes:**
- HLS-001 v1 generated: `/artifacts/hls/HLS-001_automated_dev_environment_setup_v1.md`
- HLS-001 v2 generated: `/artifacts/hls/HLS-001_automated_dev_environment_setup_v2.md` (incorporated feedback decisions)
- Story focuses on automated development environment setup (PRD-000 User Flow 1)
- Addresses Epic EPIC-000 Acceptance Criterion 1 (Rapid Environment Setup)
- Functional requirements covered: FR-01, FR-02, FR-03, FR-20
- Primary persona: Senior Backend Engineer; Secondary: New Team Member
- User journey: Repository clone to working environment in <30 minutes
- v1: 5 acceptance criteria, 5 stories, ~16 SP, 3 open questions
- v2: 7 acceptance criteria, 6 stories, ~20 SP, all questions resolved via Decisions D1-D3
- Decisions incorporated: IDE setup (VS Code), verbose output with progress indicators, interactive prompts with silent mode
- Validation: 16/16 criteria passed (100%) - fully user-centric, implementation-agnostic
- Traceability maintained to PRD-000, Business Research, and feedback decisions
- Ready for backlog story generation (TASK-014)

---

## Phase 1.5: Backlog User Story Generation

### TASK-014: Execute Backlog User Story Generator v1 (HLS-001)
**Priority**: Critical
**Dependencies**: TASK-013
**Estimated Time**: 25 minutes
**Status**: ⏳ Pending
**Context**: New session C3 required
**Generator Name**: high-level-user-story

**Description**:
Execute Backlog Story Generator for first HLS in standalone context.

**Command**: `/generate TASK-014`

**Input Data:**
- HLS-001

---

### TASK-019: Execute High-level User Story Generator v1 (PRD-000 - HLS-002)
**Priority**: High
**Dependencies**: TASK-013 (HLS-001 generated)
**Estimated Time**: 25 minutes
**Status**: ⏳ Pending
**Context**: New session required
**Generator Name**: high-level-user-story

**Description**:
Execute High-level Story Generator for CI/CD Pipeline Setup from PRD-000.

**Command**: `/generate TASK-019`

**Input Data:**
- PRD-000
- Focus: CI/CD Pipeline Setup (FR-04, FR-05, FR-06, FR-15, FR-16, FR-21)

**Scope Guidance:**
- User story: Automated build validation with CI/CD pipeline
- Primary user flow: PRD-000 Section 6.1 Flow 2 (Feature Development Workflow - steps 6-9)
- Target personas: Senior Backend Engineer, New Team Member
- Epic acceptance criterion: Epic-000 Criterion 2 (Automated Build Success)

---

### TASK-020: Execute High-level User Story Generator v1 (PRD-000 - HLS-003)
**Priority**: High
**Dependencies**: TASK-013 (HLS-001 generated)
**Estimated Time**: 25 minutes
**Status**: ⏳ Pending
**Context**: New session required
**Generator Name**: high-level-user-story

**Description**:
Execute High-level Story Generator for Application Skeleton Implementation from PRD-000.

**Command**: `/generate TASK-020`

**Input Data:**
- PRD-000
- Focus: Application Skeleton Implementation (FR-07, FR-08, FR-09)

**Scope Guidance:**
- User story: FastAPI application skeleton with example MCP tool
- Primary user flow: Developer reviewing application patterns to implement first feature
- Target personas: Senior Backend Engineer, New Team Member
- Epic acceptance criterion: Epic-000 Criterion 3 (Framework Readiness)

---

### TASK-021: Execute High-level User Story Generator v1 (PRD-000 - HLS-004)
**Priority**: High
**Dependencies**: TASK-013 (HLS-001 generated)
**Estimated Time**: 25 minutes
**Status**: ⏳ Pending
**Context**: New session required
**Generator Name**: high-level-user-story

**Description**:
Execute High-level Story Generator for Development Documentation & Workflow Standards from PRD-000.

**Command**: `/generate TASK-021`

**Input Data:**
- PRD-000
- Focus: Development Documentation & Workflow Standards (FR-10, FR-11, FR-12, FR-19)

**Scope Guidance:**
- User story: Comprehensive development workflow documentation enabling team collaboration
- Primary user flow: PRD-000 Section 6.1 Flow 2 (Feature Development Workflow - understanding branching, code review, testing)
- Target personas: New Team Member (primary), Technical Writer, Senior Backend Engineer
- Epic acceptance criterion: Epic-000 Criterion 4 (Development Standards Clarity)

---

### TASK-022: Execute High-level User Story Generator v1 (PRD-000 - HLS-005)
**Priority**: Medium
**Dependencies**: TASK-013 (HLS-001 generated)
**Estimated Time**: 25 minutes
**Status**: ⏳ Pending
**Context**: New session required
**Generator Name**: high-level-user-story

**Description**:
Execute High-level Story Generator for Containerized Deployment Configuration from PRD-000.

**Command**: `/generate TASK-022`

**Input Data:**
- PRD-000
- Focus: Containerized Deployment Configuration (FR-13, FR-14, FR-17, FR-18)

**Scope Guidance:**
- User story: Containerized deployment enabling production readiness
- Primary user flow: Building and running application in Podman container for local development and production deployment
- Target personas: Senior Backend Engineer, DevOps Engineer
- Note: Foundation phase focuses on Containerfile creation; full K8s deployment deferred to EPIC-005 per Decision D5

---

## Phase 1.6: Generator Architecture Refinement

### TASK-015: Refactor Initiative Generator to Handle INIT-000 (Foundation Initiative)
**Priority**: High
**Dependencies**: None (architectural improvement)
**Estimated Time**: 30 minutes
**Status**: ✅ Completed
**Context**: Current session

**Description**:
Refactor initiative-generator to convert existing EPIC-000 instructions into INIT-000 (Foundation Initiative) instructions. The initiative generator should check if INIT-000 exists before generating feature initiatives (INIT-001+), and recommend creating INIT-000 first if it doesn't exist.

**Completion Notes:**
- ✅ Updated initiative-generator.xml (v1.5 → v1.8)
  - v1.6: Added Step 1 INIT-000 detection, split Step 6 into 6A/6B routing
  - v1.7: Removed redundant Step 2 routing logic, cleaned up step sequence
  - v1.8: Made Step 6A fully tech-agnostic (CRITICAL architectural refinement)
    - Removed specific technologies (FastAPI, PostgreSQL, Python, pytest)
    - Added tech-agnostic language guidance and examples
    - Added anti-hallucination guideline for maintaining tech-agnostic language
    - **Rationale:** Initiatives/Epics are STRATEGIC PHASE (business-focused, tech-agnostic). Technical decisions belong in PRD phase where Implementation Research is available.
- ✅ Updated CLAUDE.md SDLC Artifact Dependency Flow diagram
  - Explicitly shows INIT-000 (Foundation Initiative) with EPIC-000
  - Shows INIT-001+ (Feature Initiatives) with EPIC-001+ and INIT-000 dependency
  - Added Key Principles clarifying INIT-000 vs INIT-001+ distinction
- ✅ Verified epic-generator.xml handles INIT-000 correctly (no changes needed)
  - Already supports Initiative as parent via mutually exclusive inputs
- ✅ Created INIT-000 artifact (needs regeneration with tech-agnostic language)
- Generator architecture now clean: Product Vision → INIT-000 (foundation) & INIT-001+ (features)
- **Architectural Decision:** Strategic Phase = Tech-Agnostic, PRD = Tech-Aware Bridge

**Architectural Rationale:**
- Product Vision remains initiative-agnostic (strategic, no initiatives generated)
- Initiative Generator handles ALL initiative creation (foundation + features)
- INIT-000 (Foundation Initiative) contains EPIC-000 as single supporting epic
- INIT-001+ (Feature Initiatives) depend on INIT-000 as prerequisite
- Clean separation at initiative level: foundation bootstrap vs. feature delivery
- Aligns with decision to create separate INIT-000 for foundation/bootstrap work

**Generation Flow:**
```
Product Vision (initiative-agnostic)
    ↓
Initiative Generator:
    ├─ Check: Does INIT-000 exist?
    │  ├─ NO → Generate INIT-000 (Foundation Initiative with EPIC-000)
    │  └─ YES → Proceed to feature initiatives
    ↓
    └─ Generate INIT-001+ (Feature Initiatives)
       └─ Reference INIT-000 as prerequisite/dependency
```

**Changes Required:**

1. **Update initiative-generator.xml:**

   **A. Add INIT-000 Detection Step (Priority 1):**
   - Before generating feature initiatives, check if INIT-000 exists in `/artifacts/initiatives/`
   - If INIT-000 NOT found:
     - Recommend creating INIT-000 first as foundation prerequisite
     - Provide instructions: "Before generating feature initiatives, create INIT-000 (Foundation Initiative)"
   - If INIT-000 found:
     - Proceed with feature initiative generation (INIT-001+)
     - Reference INIT-000 as prerequisite in dependencies section

   **B. Convert EPIC-000 Instructions into INIT-000 Instructions:**
   - Remove embedded EPIC-000 generation instructions from feature initiative flow
   - Create dedicated INIT-000 generation section with:
     - Strategic Objective: "Establish production-ready development infrastructure enabling rapid, confident feature development"
     - Duration: 1 month (Q1, Weeks 1-4)
     - Supporting Epics: EPIC-000 (Project Foundation & Bootstrap) - single epic
     - Key Results focused on infrastructure readiness (environment setup, CI/CD, framework readiness)
     - Budget: Extract foundation portion (~$200K-$300K for 2 engineers × 4 weeks)

   **C. Update Feature Initiative Instructions (INIT-001+):**
   - Add prerequisite: "This initiative depends on INIT-000 (Foundation Initiative)"
   - Adjust timeline: Start after INIT-000 completion (Week 5+, not Week 1)
   - Adjust budget: Exclude foundation costs (already in INIT-000)
   - Add dependency metadata: "Dependencies: INIT-000 (must complete first)"

2. **Update epic-generator.xml (if needed):**
   - Verify EPIC-000 generation correctly references parent initiative INIT-000
   - Verify EPIC-001+ generation correctly references parent initiative INIT-001+
   - Ensure mutually_exclusive_group handles INIT-000 vs INIT-001+ correctly for parent selection

3. **Update CLAUDE.md (if needed):**
   - Update SDLC Artifact Dependency Flow diagram to show INIT-000 explicitly
   - Clarify initiative generation flow: INIT-000 (foundation) first, then INIT-001+ (features)

**Success Criteria:**
- [ ] initiative-generator.xml checks for INIT-000 existence before generating feature initiatives
- [ ] initiative-generator.xml can generate INIT-000 (Foundation Initiative) with EPIC-000 as supporting epic
- [ ] initiative-generator.xml generates INIT-001+ (Feature Initiatives) with INIT-000 dependency
- [ ] EPIC-000 instructions converted from epic-level to initiative-level (INIT-000)
- [ ] Feature initiatives (INIT-001+) reference INIT-000 as prerequisite
- [ ] Generators maintain backward compatibility with existing artifacts
- [ ] CLAUDE.md updated if dependency flow documentation needs clarification
- [ ] Architecture documentation clarifies: INIT-000 (foundation) blocks INIT-001+ (features)

**Output Artifacts:**
- Updated `/prompts/initiative-generator.xml`
- Updated `/prompts/epic-generator.xml` (if changes needed)
- Updated `/CLAUDE.md` (if dependency flow needs clarification)

---

## Phase 1.7: PRD Refinement & Implementation Setup

### TASK-016: Refine PRD-000 Based on Feedback
**Priority**: High
**Dependencies**: TASK-012 (PRD-000 v1 must exist)
**Estimated Time**: 45 minutes
**Status**: ✅ Completed
**Context**: Current session

**Description**:
Incorporate feedback from `/feedback/PRD-000_v1_comments.md` into PRD-000 v2. Update Technical Considerations section to align with specialized CLAUDE.md standards and incorporate additional tooling requirements and answered Open Questions.

**Feedback Summary:**
1. **Alignment with Hybrid CLAUDE.md Approach:**
   - Technical Considerations section must align with established standards in specialized CLAUDE.md files (@implementation/CLAUDE-*.md)
   - Specialized files cover: tooling, testing, typing, validation, architecture

2. **Additional PRD Requirements (New Tools):**
   - Renovate (dependency automation) - keep library versions up-to-date
   - NuShell (cross-platform shell) - replacement for Bash
   - Devbox (portable isolated dev environments) - reduce "works on my machine" issues
   - Podman (container runtime) - instead of Docker

3. **Open Questions - Answers Provided:**
   - **Business Q1:** Comprehensive foundation (4-5 weeks, not minimal)
   - **Business Q2:** Platform standards confirmed:
     - CI/CD: GitHub Actions
     - Container registry: DockerHub
     - Deployment: Podman, Kubernetes Manifests
     - Secret management: HashiCorp Vault
   - **Business Q3:** Optimize for experienced team productivity (automation, advanced tooling)
   - **Tech Q4:** Package manager = uv (confirmed)
   - **Tech Q5:** K8s deployment = defer to EPIC-005; MVP = Dockerfile + Podman instructions
   - **Tech Q6:** Observability = defer to EPIC-004
   - **Tech Q7:** Dev environment database = Podman alternative only (no native PostgreSQL install)

**Changes Required:**

1. **Update Technical Considerations Section:**
   - Review alignment with specialized CLAUDE.md standards
   - **Treat CLAUDE-*.md file context as "Decisions Made"** for Technical Considerations
   - Add Renovate for dependency management
   - Add NuShell for cross-platform shell scripting
   - Add Devbox for isolated development environments
   - Add Podman as primary container runtime (**keep Docker as alternative**)

2. **Update Dependencies Section:**
   - Add Renovate as system dependency
   - Add NuShell as system dependency
   - Add Devbox as system dependency
   - Add Podman as primary container runtime (keep Docker as alternative option)

3. **Create "Decisions Made" Section:**
   - **Move all 7 answered Open Questions to new "Decisions Made" section**
   - Document answers as decisions with rationale
   - Include decision date and decision makers (based on feedback)

4. **Update Functional Requirements (if needed):**
   - FR-13: Update to reference Podman as primary (Docker as alternative)
   - FR-14: Clarify hot-reload works with Devbox
   - FR-17: Update to reference Podman for database container (Docker alternative)
   - Add new FR for Renovate integration (dependency automation)
   - Add new FR for NuShell scripting support
   - Add new FR for Devbox isolated environments

5. **Update Technology Stack Appendix:**
   - Add Renovate, NuShell, Devbox, Podman to stack
   - Document Docker as alternative to Podman (compatibility option)
   - Update justifications based on feedback and specialized CLAUDE.md standards

**Success Criteria:**
- [x] All feedback incorporated into PRD-000 v2
- [x] Technical Considerations aligned with specialized CLAUDE.md files
- [x] New tooling requirements (Renovate, NuShell, Devbox, Podman) documented
- [x] Open Questions answered and documented as decisions
- [x] Functional Requirements updated to reflect tooling changes
- [x] PRD-000 v2 generated at `/artifacts/prds/PRD-000_project_foundation_bootstrap_v2.md`
- [x] **EPIC-000 evaluated for alignment** - verify if parent epic needs updates based on PRD changes

**Completion Notes:**
- PRD-000 v2 generated with all feedback incorporated
- Added "Decisions Made" section documenting all 7 stakeholder decisions (D1-D7)
- Removed "Open Questions" section (all questions answered and documented)
- Updated Technical Considerations to align with specialized CLAUDE.md standards (CLAUDE-core, CLAUDE-tooling, CLAUDE-testing, CLAUDE-typing, CLAUDE-validation, CLAUDE-architecture)
- Added new tooling: Renovate (FR-16, FR-21), NuShell (FR-19), Devbox (FR-20)
- Updated FR-13, FR-14, FR-17 to reference Podman as primary (Docker alternative)
- Updated Dependencies section with new tooling
- Updated Technology Stack Appendix with new tools and rationale
- Updated Timeline to 5 weeks (comprehensive foundation per Decision D1)
- EPIC-000 evaluation: Minor alignment needed (duration 4→5 weeks, milestones, open questions resolved) but strategic scope remains valid and tech-agnostic ✅

**EPIC-000 Evaluation Criteria:**
- Does EPIC-000 scope need updates for new tooling? (Likely NO - epic is strategic/tech-agnostic)
- Do EPIC-000 acceptance criteria still align with PRD requirements? (Verify)
- Does EPIC-000 business value section need updates? (Verify)
- If changes needed: Update EPIC-000 and document as v3
- If no changes needed: Document evaluation result (no updates required, epic remains tech-agnostic)

**Output Artifacts:**
- `/artifacts/prds/PRD-000_project_foundation_bootstrap_v2.md`
- EPIC-000 evaluation report (changes needed or no changes required with rationale)
- `/artifacts/epics/EPIC-000_project_foundation_bootstrap_v3.md` (only if changes needed)

---

### TASK-017: Add Implementation Routing to CLAUDE.md
**Priority**: High
**Dependencies**: None (architectural improvement)
**Estimated Time**: 30 minutes
**Status**: ✅ Completed
**Context**: Current session

**Description**:
Add implementation-phase routing instructions to existing CLAUDE.md and move implementation configuration files from `/implementation/` to `/prompts/CLAUDE/`. Main CLAUDE.md stays intact with planning-phase instructions, just adds routing to implementation configs.

**Current State:**
- Main `/CLAUDE.md`: Planning phase instructions (Product Vision → Epic → PRD → Stories → Spikes/ADRs/Tech Specs)
- Implementation folder `/implementation/*.md`: Implementation phase configs (Python tooling, testing, typing, validation, architecture)
- **Problem:** No connection between planning instructions and implementation configs

**Target State:**
```
/CLAUDE.md (planning instructions + implementation routing)
    └─ Implementation Phase → /prompts/CLAUDE/CLAUDE-core.md
        ├─ Tooling → /prompts/CLAUDE/CLAUDE-tooling.md
        ├─ Testing → /prompts/CLAUDE/CLAUDE-testing.md
        ├─ Typing → /prompts/CLAUDE/CLAUDE-typing.md
        ├─ Validation → /prompts/CLAUDE/CLAUDE-validation.md
        └─ Architecture → /prompts/CLAUDE/CLAUDE-architecture.md
```

**Changes Required:**

**Step 1: Create Folder Structure**
- Create `/prompts/CLAUDE/` directory

**Step 2: Move Implementation Files (CLAUDE-*.md only from /implementation/)**
- Move `/implementation/CLAUDE-core.md` → `/prompts/CLAUDE/CLAUDE-core.md`
- Move `/implementation/CLAUDE-tooling.md` → `/prompts/CLAUDE/CLAUDE-tooling.md`
- Move `/implementation/CLAUDE-testing.md` → `/prompts/CLAUDE/CLAUDE-testing.md`
- Move `/implementation/CLAUDE-typing.md` → `/prompts/CLAUDE/CLAUDE-typing.md`
- Move `/implementation/CLAUDE-validation.md` → `/prompts/CLAUDE/CLAUDE-validation.md`
- Move `/implementation/CLAUDE-architecture.md` → `/prompts/CLAUDE/CLAUDE-architecture.md`
- **Do NOT move** `/implementation/TODO.md` (stays for implementation-specific tracking)
- **Do NOT move** `/CLAUDE.md` (stays at root, gets augmented only)

**Step 3: Add Implementation Routing to Existing CLAUDE.md**
At the **end** of existing `/CLAUDE.md`, add new section:
```markdown
---

## Implementation Phase Instructions

**When to use Implementation Phase instructions:**
- Writing Python code, tests, documentation
- Setting up development environment, CI/CD, tooling
- Implementing features from PRDs/Backlog Stories
- Coding tasks after planning phase completes

**Implementation Configuration Files:**
- **[CLAUDE-core.md](prompts/CLAUDE/CLAUDE-core.md)** - Main implementation guide and orchestration
- **[CLAUDE-tooling.md](prompts/CLAUDE/CLAUDE-tooling.md)** - UV, Ruff, MyPy, pytest configuration
- **[CLAUDE-testing.md](prompts/CLAUDE/CLAUDE-testing.md)** - Testing strategy, fixtures, coverage
- **[CLAUDE-typing.md](prompts/CLAUDE/CLAUDE-typing.md)** - Type hints, annotations, type safety
- **[CLAUDE-validation.md](prompts/CLAUDE/CLAUDE-validation.md)** - Pydantic models, input validation, security
- **[CLAUDE-architecture.md](prompts/CLAUDE/CLAUDE-architecture.md)** - Project structure, modularity, design patterns

**→ For implementation work, see [CLAUDE-core.md](prompts/CLAUDE/CLAUDE-core.md) which orchestrates all specialized configs.**
```

**Step 4: Update Cross-References in Moved Files**
- Update all `@implementation/` references → `/prompts/CLAUDE/` in moved files
- Update feedback file references if needed (e.g., PRD-000_v1_comments.md)

**Step 5: Validate**
- Verify generators can still load CLAUDE.md (planning instructions unaffected)
- Verify cross-references resolve correctly
- Test `/generate` command still works
- Verify implementation files accessible from new location

**Success Criteria:**
- [x] `/prompts/CLAUDE/` folder created
- [x] 6 implementation CLAUDE-*.md files moved to new location
- [x] Main `/CLAUDE.md` augmented with implementation routing (planning content unchanged)
- [x] All cross-references verified (all use relative paths, no updates needed)
- [x] Generators validated (input_artifacts resolve without issues)
- [x] `/generate` command tested successfully

**Completion Notes:**
- Created `/prompts/CLAUDE/` directory
- Moved 6 CLAUDE-*.md files from `/implementation/` to `/prompts/CLAUDE/`:
  - CLAUDE-core.md
  - CLAUDE-tooling.md
  - CLAUDE-testing.md
  - CLAUDE-typing.md
  - CLAUDE-validation.md
  - CLAUDE-architecture.md
- Added "Implementation Phase Instructions" section to main `/CLAUDE.md` at end
- Cross-references use relative paths (`./CLAUDE-*.md`) - no updates needed
- Implementation TODO.md stays in `/implementation/` for implementation-specific tracking
- Main CLAUDE.md retains all planning instructions, now includes routing to implementation configs

**Output Artifacts:**
- Updated `/CLAUDE.md` (existing planning content + new implementation routing section)
- `/prompts/CLAUDE/CLAUDE-core.md` (moved from /implementation/)
- `/prompts/CLAUDE/CLAUDE-tooling.md` (moved)
- `/prompts/CLAUDE/CLAUDE-testing.md` (moved)
- `/prompts/CLAUDE/CLAUDE-typing.md` (moved)
- `/prompts/CLAUDE/CLAUDE-validation.md` (moved)
- `/prompts/CLAUDE/CLAUDE-architecture.md` (moved)

**Notes:**
- Main CLAUDE.md stays at root with all planning instructions intact
- Only adds implementation routing section at the end
- Implementation TODO.md stays in `/implementation/` for implementation-specific tracking
- Simpler than creating separate CLAUDE-planning.md - avoids splitting planning content

---

### TASK-018: Evaluate specialized CLAUDE.md files
**Priority**: High
**Dependencies**: TASK-017 (CLAUDE-*.md files moved to /prompts/CLAUDE/)
**Estimated Time**: 30 minutes
**Status**: ✅ Completed
**Context**: Current session

**Description**:
Systematic evaluation of specialized `/prompts/CLAUDE/CLAUDE-*.md` files to ensure they provide clear, non-redundant implementation guidance aligned with PRD-000 requirements.

**Evaluation Criteria:**
1. **Clarity**: Each file has clear purpose, organization, and actionable guidance
2. **Duplicated Instructions**: Identify and flag redundant content across files
3. **Gaps**: Identify missing guidance needed for PRD-000 implementation
4. **Consistency**: Cross-references work correctly, terminology consistent
5. **Completeness**: Coverage of all PRD-000 technical requirements

**Files to Evaluate:**
- `/prompts/CLAUDE/CLAUDE-core.md` - Core development philosophy
- `/prompts/CLAUDE/CLAUDE-tooling.md` - UV, Ruff, MyPy, pytest
- `/prompts/CLAUDE/CLAUDE-testing.md` - Testing strategy, coverage
- `/prompts/CLAUDE/CLAUDE-typing.md` - Type hints, annotations
- `/prompts/CLAUDE/CLAUDE-validation.md` - Pydantic, security
- `/prompts/CLAUDE/CLAUDE-architecture.md` - Project structure, patterns

**Success Criteria:**
- [x] Each file evaluated for clarity and organization
- [x] Duplicated content identified and documented
- [x] Gaps identified relative to PRD-000 requirements
- [x] Cross-references verified
- [x] Evaluation report created with findings and recommendations

**Completion Notes:**
- **Evaluation report:** `/docs/specialized_claude_evaluation.md`
- **Overall assessment:** Excellent foundational guidance, well-organized, minimal problematic duplication
- **Critical finding:** CLAUDE-tooling.md missing 4 new tools from PRD-000 v2:
  - ❌ Renovate (dependency automation) - FR-16, FR-21
  - ❌ NuShell (cross-platform scripting) - FR-19
  - ❌ Devbox (isolated environments) - FR-20, Decision D3
  - ❌ Podman (container runtime) - FR-13, FR-17, Decision D2, D7
- **Coverage:** 11/21 PRD-000 v2 requirements fully covered (52%)
- **Cross-references:** All verified working, no broken links
- **Consistency:** Excellent - terminology, code style, structure consistent across all files
- **Recommended actions:**
  - **Priority 1 (CRITICAL):** Update CLAUDE-tooling.md with 4 missing tools (~2-3 hours)
  - **Priority 2 (MEDIUM):** Add Devbox/Podman context to CLAUDE-architecture.md (~1 hour)
  - **Priority 3 (LOW):** Minor enhancements across files (~1-2 hours)

**Output Artifacts:**
- `/docs/specialized_claude_evaluation.md` - Comprehensive evaluation report

## Task Status Legend

- ✅ Completed
- ⏳ Pending
- 🔄 In Progress
- ⏸️ Blocked
- ⚠️ Issues Found

---
