# Master Plan - Context Engineering PoC

**Document Version**: 1.1
**Status**: Active - Phase 1 (PoC)
**Last Updated**: 2025-10-07

---

## Current Phase: Phase 1 - Bootstrap & Foundation

**Current Status**: Bootstrap completed, ready for generator execution
**Last Completed**: TASK-003: Convert Research Templates into XML format
**Next Task**: TASK-004: Execute Product Vision Generator v1
**Completion**: 3/15 tasks (20%)

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
**Status**: ⏳ Pending
**Context**: New session C1 required

**Description**:
Execute Product Vision Generator in standalone context to produce first iteration of Product Vision document.

**Command**: `/generate TASK-004`

**Input artifacts**:
- Business Research - `docs/research/mcp/AI_Agent_MCP_Server_business_research.md`

---

### TASK-005: Critique Product Vision v1
**Priority**: High
**Dependencies**: TASK-004
**Estimated Time**: 15 minutes
**Status**: ⏳ Pending

**Description**:
Human review of Product Vision v1 with structured critique focusing on completeness, clarity, actionability, traceability.

**Success Criteria**:
- [ ] Critique document created
- [ ] Covers all 4 quality dimensions
- [ ] Identifies specific improvement areas
- [ ] Rates severity (minor/major/critical)
- [ ] Provides actionable suggestions

**Output Artifacts**:
- `/feedback/product_vision_v1_critique.md`

---

### TASK-006: Refine Product Vision Generator & Execute v2
**Priority**: Critical
**Dependencies**: TASK-005
**Estimated Time**: 30 minutes
**Status**: ⏳ Pending
**Context**: Can reuse C1 or start new session

**Description**:
Apply Self-Refine pattern to update generator based on critique, then re-execute.

**Command**: `/refine product_vision_generator`

**Context Requirements**:
- All from TASK-004
- `/feedback/product_vision_v1_critique.md`

**Success Criteria**:
- [ ] Generator prompt updated with improvements
- [ ] Changes address critique points
- [ ] Version incremented (1.0 → 1.1)
- [ ] Vision v2 shows measurable improvement

**Output Artifacts**:
- `/prompts/product_vision_generator_v2.xml` (updated)
- `/artifacts/product_vision_v2.md`

---

### TASK-007: Critique Product Vision v2
**Priority**: High
**Dependencies**: TASK-006
**Estimated Time**: 15 minutes
**Status**: ⏳ Pending

**Description**:
Second human review focusing on whether v1 critiques were addressed and identifying remaining gaps.

**Success Criteria**:
- [ ] Critique document created
- [ ] Compares v1 vs v2 improvements
- [ ] Identifies remaining issues
- [ ] Notes patterns for strategy doc update

**Output Artifacts**:
- `/feedback/product_vision_v2_critique.md`

---

### TASK-008: Final Refinement & Execute v3 + Update Strategy
**Priority**: Critical
**Dependencies**: TASK-007
**Estimated Time**: 45 minutes
**Status**: ⏳ Pending
**Context**: Can reuse C1 or start new session

**Description**:
Apply final refinements, execute generator for v3, and **HUMAN manually updates** strategy document with lessons learned.

**Command**: `/refine product_vision_generator`

**Context Requirements**:
- All from TASK-006
- `/feedback/product_vision_v2_critique.md`

**Success Criteria**:
- [ ] Generator prompt finalized (version 1.2)
- [ ] Vision v3 meets all validation criteria
- [ ] Human approval obtained for v3

**Output Artifacts**:
- `/prompts/product_vision_generator_v3.xml` (final)
- `/artifacts/product_vision_v3.md` (approved)

---

## Phase 1.2: Cascade to Epic Generation

### TASK-009: Execute Epic Generator v1
**Priority**: Critical
**Dependencies**: TASK-008
**Estimated Time**: 30 minutes
**Status**: ⏳ Pending
**Context**: New session C2 required

**Description**:
Execute Epic Generator in standalone context to decompose Product Vision into Epic documents.

**Command**: `/generate TASK-009`

**Context Requirements**:
- `/CLAUDE.md`
- `/prompts/CLAUDE-epic.md` (lazy-generate if missing)
- `/prompts/epic_generator.xml` 
- `/prompts/templates/epic-template.xml`
- `/artifacts/product_vision_v3.md`

**Success Criteria**:
- [ ] 3-5 epic documents generated
- [ ] Each epic follows template structure
- [ ] Epics decompose vision completely (no gaps)
- [ ] Epics are non-overlapping
- [ ] Each epic is independently valuable
- [ ] Feature-specific research conducted
- [ ] PRD generator prompt is valid XML
- [ ] Clear dependency order between epics

**Output Artifacts**:
- `/artifacts/epics/epic_001_v1.md` through `epic_00N_v1.md`
- `/prompts/prd_generator.xml`

---

### TASK-010: Critique Epics v1 & Refine to v2
**Priority**: High
**Dependencies**: TASK-009
**Estimated Time**: 45 minutes
**Status**: ⏳ Pending

**Description**:
Human review of Epic documents, create critique, refine and execute v2.

**Success Criteria**:
- [ ] Critique document created
- [ ] Validates epic decomposition logic
- [ ] Checks for gaps/overlaps
- [ ] Assesses priority ordering
- [ ] Reviews PRD generator quality
- [ ] Generator refined and v2 generated

**Output Artifacts**:
- `/feedback/epics_v1_critique.md`
- `/prompts/epic_generator.xml` (updated)
- `/artifacts/epics/epic_001_v2.md` through `epic_00N_v2.md`
- `/prompts/prd_generator.xml` (updated)

---

### TASK-011: Critique Epics v2 & Final Refinement
**Priority**: High
**Dependencies**: TASK-010
**Estimated Time**: 30 minutes
**Status**: ⏳ Pending

**Description**:
Final critique and refinement cycle for Epic Generator, **HUMAN manually updates** strategy document.

**Success Criteria**:
- [ ] Critique document created
- [ ] Epic v3 approved
- [ ] **HUMAN**: Strategy doc manually updated with Epic-specific patterns
- [ ] PRD generator ready for next phase

**Output Artifacts**:
- `/feedback/epics_v2_critique.md`
- `/artifacts/epics/epic_001_v3.md` through `epic_00N_v3.md` (approved)
- `/prompts/prd_generator.xml` (final)
- `/docs/context_engineering_strategy_v1.md` (manually updated by human)

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
