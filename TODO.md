# Master Plan - Context Engineering PoC

**Document Version**: 1.1
**Status**: Active - Phase 1 (PoC)
**Last Updated**: 2025-10-07

---

## Current Phase: Phase 1 - Bootstrap & Foundation

**Current Status**: 5 Epics v1 generated, ready for human critique
**Last Completed**: TASK-009: Execute Epic Generator v1
**Next Task**: TASK-010: Critique Epics v1 & Refine to v2 (or TASK-005: Critique Product Vision v1)
**Completion**: 6/15 tasks (40%)

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
- `/prompts/templates/generator-schema-template.xml` ✅

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
- `/prompts/product_vision_generator.xml` ✅

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

**Description**:
Execute Product Vision Generator in standalone context to produce first iteration of Product Vision document.

**Command**: `/generate TASK-004`

**Input artifacts**:
- Business Research - `docs/research/mcp/AI_Agent_MCP_Server_business_research.md`

**Completion Notes**:
- Product Vision v1 generated: `/artifacts/product_vision_v1.md`
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

**Description**:
Execute Initiative Generator in standalone context to decompose Product Vision into Initiative documents.

**Production Requirement**: Should use approved Product Vision v3 as input
**Current State**: Executed with Product Vision v1 (Draft) - acceptable for PoC, risk of rework if Vision changes in v2/v3

**Command**: `/generate TASK-008`

**Input Artifacts:**
- Primary: `/artifacts/product_vision_v3.md` (approved) - **Production requirement**
- Primary (Current): `/artifacts/product_vision_v1.md` (Draft) - **Used for PoC**
- Secondary (optional): `/docs/research/mcp/AI_Agent_MCP_Server_business_research.md`

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

**Description**:
Execute Epic Generator in standalone context to decompose Product Vision into Epic documents.

**Production Requirement**: Should use approved Product Vision v3 as input
**Current State**: Executed with Product Vision v1 (Draft) - acceptable for PoC, risk of rework if Vision changes in v2/v3

**Command**: `/generate TASK-009`

**Input Artifacts:**
- Primary: `/artifacts/product_vision_v3.md` (approved) - **Production requirement**
- Primary (Current): `/artifacts/product_vision_v1.md` (Draft) - **Used for PoC**
- Secondary (optional): `/docs/research/mcp/AI_Agent_MCP_Server_business_research.md`

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

### TASK-012: Execute PRD Generator v1 (Epic 001)
**Priority**: Critical
**Dependencies**: TASK-011
**Estimated Time**: 25 minutes
**Status**: ⏳ Pending
**Context**: New session C3 required

**Description**:
Execute PRD Generator for first epic in standalone context.

**Command**: `/generate TASK-012`

**Context Requirements**:
- `/CLAUDE.md`
- `/prompts/CLAUDE-prd.md` (lazy-generate if missing)
- `/prompts/prd_generator.xml`
- `/prompts/templates/prd-template.xml`
- `/artifacts/epics/epic_001_v3.md`

**Success Criteria**:
- [ ] PRD follows template structure
- [ ] All required sections complete
- [ ] Success metrics are SMART
- [ ] Requirements traceable to epic
- [ ] Technical approaches researched
- [ ] Backlog story generator is valid XML
- [ ] Technical feasibility addressed

**Output Artifacts**:
- `/artifacts/prds/prd_001/prd_v1.md`
- `/artifacts/prds/prd_001/TODO.md` (high-level story tracking)
- `/prompts/backlog_story_generator.xml`

---

### TASK-013: Iterate PRD (3 cycles) & Update Strategy
**Priority**: Critical
**Dependencies**: TASK-012
**Estimated Time**: 60 minutes
**Status**: ⏳ Pending

**Description**:
Complete 3-iteration refinement cycle for PRD, **HUMAN manually updates** strategy document with lessons.

**Success Criteria**:
- [ ] PRD v1 critique created and refinements applied
- [ ] PRD v2 critique created and final refinements applied
- [ ] PRD v3 approved
- [ ] Backlog story generator finalized
- [ ] **HUMAN**: Strategy doc manually updated with PRD patterns
- [ ] PRD/TODO.md tracking high-level stories

**Output Artifacts**:
- `/feedback/prd_001_v1_critique.md`
- `/feedback/prd_001_v2_critique.md`
- `/artifacts/prds/prd_001/prd_v2.md`
- `/artifacts/prds/prd_001/prd_v3.md` (approved)
- `/artifacts/prds/prd_001/TODO.md` (updated with stories)
- `/prompts/backlog_story_generator.xml` (final)
- `/docs/context_engineering_strategy_v1.md` (manually updated by human)

---

### TASK-014: Execute Backlog Story Generator v1 (US-01 from PRD)
**Priority**: Critical
**Dependencies**: TASK-013 (PRD v3 approved)
**Estimated Time**: 25 minutes
**Status**: ⏳ Pending
**Context**: New session C4 required

**Description**:
Execute Backlog Story Generator for first high-level story from PRD.

**Command**: `/generate TASK-014`

**Context Requirements**:
- `/CLAUDE.md`
- `/prompts/CLAUDE-backlog-story.md` (lazy-generate if missing)
- `/prompts/backlog_story_generator.xml`
- `/prompts/templates/backlog-story-template.xml`
- `/artifacts/prds/prd_001/prd_v3.md`
- `/artifacts/prds/prd_001/TODO.md`

**Success Criteria**:
- [ ] Backlog story follows template structure
- [ ] Related PRD section populated (PRD ID, high-level story, FRs)
- [ ] Functional requirements listed
- [ ] Non-functional requirements defined (all 6 dimensions)
- [ ] Technical requirements cover all layers
- [ ] Acceptance criteria in Given-When-Then format
- [ ] TODO.md file created with implementation tasks
- [ ] ADR generator prompt is valid XML
- [ ] Traceability to PRD established

**Output Artifacts**:
- `/artifacts/backlog_stories/US-01-01_{feature}/backlog_story_v1.md`
- `/artifacts/backlog_stories/US-01-01_{feature}/TODO.md`
- `/prompts/adr_generator.xml`

---

### TASK-015: Generate Phase 1 Completion Report
**Priority**: High
**Dependencies**: TASK-014
**Estimated Time**: 30 minutes
**Status**: ⏳ Pending

**Description**:
Generate comprehensive Phase 1 completion report documenting framework viability, lessons learned, and recommendations for Phase 2 (MCP Server extraction).

**Success Criteria**:
- [ ] Report documents all completed generators (Vision, Epic, PRD, Backlog Story)
- [ ] 3-iteration cycles validated for each generator type
- [ ] At least 5 patterns documented
- [ ] Framework viability assessment complete
- [ ] Recommendations for Phase 2 MCP Server project
- [ ] All templates from final strategy document removed and replaced with extracted file references (e.g., prompts/templates/generator-schema-template.xml, prompts/templates/specialized-claude-template.md)
- [ ] Section 6 of final strategy document Synced with TODO.md file
- [ ] **HUMAN**: Final strategy document update with Phase 1 summary

**Output Artifacts**:
- `/docs/phase1_completion_report.md`
- `/docs/context_engineering_strategy_v1.md` (final Phase 1 update by human)

**Phase 1 Completion Gate**: After this task, Phase 1 (PoC) is complete

---

## Task Status Legend

- ✅ Completed
- ⏳ Pending
- 🔄 In Progress
- ⏸️ Blocked
- ⚠️ Issues Found

---
