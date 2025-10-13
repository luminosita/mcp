# Master Plan - Context Engineering PoC

**Document Version**: 1.1
**Status**: Active - Phase 1 (PoC)
**Last Updated**: 2025-10-07

---

## Current Phase: Phase 1 - Bootstrap & Foundation

**Current Status**: PRD-000 v1 generated, Generator architecture refined for INIT-000
**Last Completed**: TASK-015: Refactor Initiative Generator to Handle INIT-000 (Foundation Initiative)
**Next Task**: TASK-013 (Execute High-Level User Story Generator) or create INIT-000
**Completion**: 8/16 tasks (50%)

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
**Status**: ⏳ Pending
**Context**: New session C3 required
**Generator Name**: high-level-user-story

**Description**:
Execute PRD Generator for first epic in standalone context.

**Command**: `/generate TASK-013`

**Input Data:**
- PRD-000

---

## Phase 1.5: Backlog User Story Generation

### TASK-014: Execute Backlog User Story Generator v1 (HLS-001)
**Priority**: Critical
**Dependencies**: TASK-012
**Estimated Time**: 25 minutes
**Status**: ⏳ Pending
**Context**: New session C3 required
**Generator Name**: high-level-user-story

**Description**:
Execute PRD Generator for first epic in standalone context.

**Command**: `/generate TASK-014`

**Input Data:**
- HLS-001

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

## Task Status Legend

- ✅ Completed
- ⏳ Pending
- 🔄 In Progress
- ⏸️ Blocked
- ⚠️ Issues Found

---
