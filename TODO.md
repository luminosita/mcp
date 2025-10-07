# Master Plan - Context Engineering PoC

**Document Version**: 1.0
**Status**: Active
**Last Updated**: 2025-10-07

---

## Phase 1: Bootstrap & Foundation

### TASK-000: Extract & Generate Templates
**Priority**: Critical
**Dependencies**: None
**Estimated Time**: 30 minutes
**Status**: ⏳ Pending

**Description**:
Extract templates from research document (Section 6.1-6.4) and convert to XML format. Generate missing templates not explicitly defined in research.

**Required Templates**:
1. Product Vision Template (generate - not in research)
2. Epic Template (generate - not in research)
3. PRD Template (extract from Section 6.1, lines 630-728)
4. ADR Template (extract from Section 6.2, lines 773-849)
5. Technical Specification Template (extract from Section 6.3, lines 905-1016)
6. User Story Template (extract from Section 6.4, lines 1063-1108)

**Success Criteria**:
- [ ] All 6 templates exist in `/prompts/templates/*.xml`
- [ ] Each template is valid XML with proper CDATA sections
- [ ] Templates include validation checklists from research
- [ ] Metadata references source sections (where applicable)
- [ ] Instructions are clear and actionable

**Output Artifacts**:
- `/prompts/templates/product-vision-template.xml`
- `/prompts/templates/epic-template.xml`
- `/prompts/templates/prd-template.xml`
- `/prompts/templates/adr-template.xml`
- `/prompts/templates/tech-spec-template.xml`
- `/prompts/templates/user-story-template.xml`

---

### TASK-001: Create Product Idea Stub
**Priority**: High
**Dependencies**: None
**Estimated Time**: 10 minutes
**Status**: ⏳ Pending

**Description**:
Create initial product idea document for CLI tool that will serve as input to Product Vision Generator.

**Success Criteria**:
- [ ] Document describes CLI tool purpose
- [ ] Includes problem statement (high-level)
- [ ] Identifies target user persona
- [ ] Lists 3-5 key capabilities
- [ ] Readable and concise (<500 words)

**Output Artifacts**:
- `/docs/product-idea.md`

---

### TASK-002: Generate Product Vision Generator Prompt
**Priority**: Critical
**Dependencies**: TASK-000 (product-vision-template.xml must exist)
**Estimated Time**: 45 minutes
**Status**: ⏳ Pending

**Description**:
Create the first generator prompt that will produce Product Vision documents and Epic Generator prompts.

**Success Criteria**:
- [ ] Follows generator prompt XML schema (Section 5.1 of strategy)
- [ ] References correct template path
- [ ] Includes validation checklist
- [ ] Specifies dual outputs (vision doc + epic generator)
- [ ] Contains relevant guidance from research Section 6.1
- [ ] Valid XML syntax

**Output Artifacts**:
- `/prompts/product_vision_generator.xml`

---

## Phase 2: First Generator Execution & Iteration

### TASK-003: Execute Product Vision Generator v1
**Priority**: Critical
**Dependencies**: TASK-001, TASK-002
**Estimated Time**: 20 minutes
**Status**: ⏳ Pending
**Context**: New session C1 required

**Description**:
Execute Product Vision Generator in standalone context to produce first iteration of Product Vision document.

**Context Requirements**:
- `/CLAUDE.md`
- `/prompts/CLAUDE-product-vision.md` (lazy-generate if missing)
- `/prompts/product_vision_generator.xml`
- `/prompts/templates/product-vision-template.xml`
- `/docs/product-idea.md`

**Success Criteria**:
- [ ] Vision document contains all required sections (per template)
- [ ] Problem statement includes quantified pain points
- [ ] Success metrics are SMART-compliant
- [ ] Target users clearly defined
- [ ] 3-5 key features listed
- [ ] Alignment with product-idea.md
- [ ] Epic generator prompt is syntactically valid XML
- [ ] Readability: Accessible to non-expert (manual Flesch >60)

**Output Artifacts**:
- `/artifacts/product_vision_v1.md`
- `/prompts/epic_generator.xml`

---

### TASK-004: Critique Product Vision v1
**Priority**: High
**Dependencies**: TASK-003
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

### TASK-005: Refine Product Vision Generator & Execute v2
**Priority**: Critical
**Dependencies**: TASK-004
**Estimated Time**: 30 minutes
**Status**: ⏳ Pending
**Context**: Can reuse C1 or start new session

**Description**:
Apply Self-Refine pattern (research Section 2.4) to update generator based on critique, then re-execute.

**Context Requirements**:
- All from TASK-003
- `/feedback/product_vision_v1_critique.md`

**Success Criteria**:
- [ ] Generator prompt updated with improvements
- [ ] Changes address critique points
- [ ] Version incremented (1.1 → 1.2)
- [ ] Vision v2 shows measurable improvement
- [ ] Epic generator prompt refined (if issues noted)

**Output Artifacts**:
- `/prompts/product_vision_generator.xml` (updated)
- `/artifacts/product_vision_v2.md`
- `/prompts/epic_generator.xml` (updated)

---

### TASK-006: Critique Product Vision v2
**Priority**: High
**Dependencies**: TASK-005
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

### TASK-007: Final Refinement & Execute v3 + Update Strategy
**Priority**: Critical
**Dependencies**: TASK-006
**Estimated Time**: 45 minutes
**Status**: ⏳ Pending

**Description**:
Apply final refinements, execute generator for v3, and update strategy document with lessons learned.

**Context Requirements**:
- All from TASK-005
- `/feedback/product_vision_v2_critique.md`
- `/docs/context_engineering_strategy_v1.md`

**Success Criteria**:
- [ ] Generator prompt finalized (version 1.3)
- [ ] Vision v3 meets all validation criteria
- [ ] Epic generator prompt production-ready
- [ ] Strategy doc Section 8.2 updated with patterns
- [ ] Human approval obtained

**Output Artifacts**:
- `/prompts/product_vision_generator.xml` (final)
- `/artifacts/product_vision_v3.md` (approved)
- `/prompts/epic_generator.xml` (final)
- `/docs/context_engineering_strategy_v1.md` (updated)

---

## Phase 3: Cascade to Epic Generation

### TASK-008: Execute Epic Generator v1
**Priority**: Critical
**Dependencies**: TASK-007
**Estimated Time**: 30 minutes
**Status**: ⏳ Pending
**Context**: New session C2 required

**Description**:
Execute Epic Generator in standalone context to decompose Product Vision into Epic documents.

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
- [ ] PRD generator prompt is valid XML
- [ ] Clear dependency order between epics

**Output Artifacts**:
- `/artifacts/epics/epic_001_v1.md` through `epic_00N_v1.md`
- `/prompts/prd_generator.xml`

---

### TASK-009: Critique Epics v1
**Priority**: High
**Dependencies**: TASK-008
**Estimated Time**: 20 minutes
**Status**: ⏳ Pending

**Description**:
Human review of Epic documents focusing on completeness of vision decomposition and independence.

**Success Criteria**:
- [ ] Critique document created
- [ ] Validates epic decomposition logic
- [ ] Checks for gaps/overlaps
- [ ] Assesses priority ordering
- [ ] Reviews PRD generator quality

**Output Artifacts**:
- `/feedback/epics_v1_critique.md`

---

### TASK-010: Refine Epic Generator & Execute v2
**Priority**: Critical
**Dependencies**: TASK-009
**Estimated Time**: 30 minutes
**Status**: ⏳ Pending

**Description**:
Refine Epic Generator based on critique and re-execute for improved epic set.

**Success Criteria**:
- [ ] Generator updated with improvements
- [ ] Epic v2 set addresses critique issues
- [ ] Decomposition logic refined
- [ ] PRD generator improved

**Output Artifacts**:
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
Final critique and refinement cycle for Epic Generator, update strategy document.

**Success Criteria**:
- [ ] Critique document created
- [ ] Epic v3 approved
- [ ] Strategy doc updated with Epic-specific patterns
- [ ] PRD generator ready for next phase

**Output Artifacts**:
- `/feedback/epics_v2_critique.md`
- `/artifacts/epics/epic_001_v3.md` through `epic_00N_v3.md` (approved)
- `/prompts/prd_generator.xml` (final)
- `/docs/context_engineering_strategy_v1.md` (updated)

---

## Phase 4: PRD Generation

### TASK-012: Execute PRD Generator v1 (Epic 001)
**Priority**: Critical
**Dependencies**: TASK-011
**Estimated Time**: 25 minutes
**Status**: ⏳ Pending
**Context**: New session C3 required

**Description**:
Execute PRD Generator for first epic in standalone context.

**Context Requirements**:
- `/CLAUDE.md`
- `/prompts/CLAUDE-prd.md` (lazy-generate if missing)
- `/prompts/prd_generator.xml`
- `/prompts/templates/prd-template.xml`
- `/artifacts/epics/epic_001_v3.md`

**Success Criteria**:
- [ ] PRD follows template from research Section 6.1
- [ ] All required sections complete
- [ ] Success metrics are SMART
- [ ] Requirements traceable to epic
- [ ] User stories generator is valid XML
- [ ] Technical feasibility addressed

**Output Artifacts**:
- `/artifacts/prds/epic_001_prd_v1.md`
- `/prompts/user_story_generator.xml`

---

### TASK-013: Iterate PRD (3 cycles) & Update Strategy
**Priority**: Critical
**Dependencies**: TASK-012
**Estimated Time**: 60 minutes
**Status**: ⏳ Pending

**Description**:
Complete 3-iteration refinement cycle for PRD, update strategy document with lessons.

**Success Criteria**:
- [ ] PRD v3 approved
- [ ] Backlog story generator finalized
- [ ] Strategy doc updated
- [ ] Patterns documented
- [ ] PRD/TODO.md created with high-level story tracking

**Output Artifacts**:
- `/feedback/epic_001_prd_v1_critique.md`
- `/feedback/epic_001_prd_v2_critique.md`
- `/artifacts/prds/prd_001/prd_v3.md` (approved)
- `/artifacts/prds/prd_001/TODO.md` (high-level story tracking)
- `/prompts/backlog_story_generator.xml` (final)
- `/docs/context_engineering_strategy_v1.md` (updated)

---

### TASK-014: Execute Backlog Story Generator v1 (US-01 from PRD)
**Priority**: Critical
**Dependencies**: TASK-013 (PRD v3 approved)
**Estimated Time**: 25 minutes
**Status**: ⏳ Pending
**Context**: New session C4 required

**Description**:
Execute Backlog Story Generator for first high-level story from PRD.

**Command**: `/kickoff execute-generator TASK-014 --story-id=US-01`

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
- `/artifacts/backlog_stories/US-01-01_feature/backlog_story_v1.md`
- `/artifacts/backlog_stories/US-01-01_feature/TODO.md`
- `/prompts/adr_generator.xml`

---

## Phase 5: Framework Validation & Graduation

### TASK-015: Validate Automation Graduation Criteria
**Priority**: High
**Dependencies**: TASK-013
**Estimated Time**: 45 minutes
**Status**: ⏳ Pending

**Description**:
Assess readiness to graduate from Phase 1 (manual) to Phase 2 (semi-automated) execution and iteration triggers.

**Validation Areas**:
1. **Task Execution Trigger**: Can we script generator execution?
2. **Iteration Trigger**: Can we implement self-critique loops?
3. **Quality Assessment**: Can we automate checklist validation?

**Success Criteria**:
- [ ] Completed ≥3 different generator types (Vision, Epic, PRD)
- [ ] Each validated through 3-iteration cycle
- [ ] ≥5 patterns documented in strategy
- [ ] Graduation criteria assessment document created
- [ ] Recommendations for Phase 2 enhancements

**Output Artifacts**:
- `/docs/phase2_graduation_assessment.md`
- `/docs/context_engineering_strategy_v1.md` (updated Section 9)

---

### TASK-016: Create Execution Script (Semi-Automation)
**Priority**: Medium
**Dependencies**: TASK-015
**Estimated Time**: 30 minutes
**Status**: ⏳ Pending

**Description**:
Create script that automates generator execution based on TODO.md task IDs (Phase 2 enhancement).

**Success Criteria**:
- [ ] Script parses TODO.md
- [ ] Loads correct generator + context for task ID
- [ ] Handles versioning (v1, v2, v3)
- [ ] Provides human approval checkpoints
- [ ] Documents usage in strategy

**Output Artifacts**:
- `/.claude/commands/execute-task-script.sh`
- `/docs/context_engineering_strategy_v1.md` (updated Section 6)

---

### TASK-017: Implement Self-Critique Loop (Semi-Automation)
**Priority**: Medium
**Dependencies**: TASK-015
**Estimated Time**: 45 minutes
**Status**: ⏳ Pending

**Description**:
Implement automated Chain-of-Verification (research Section 2.4) for artifact critique.

**Success Criteria**:
- [ ] Critique prompt created
- [ ] Auto-generates structured feedback
- [ ] Integrates with refine-generator command
- [ ] Human approval at 80% threshold
- [ ] Documented in strategy

**Output Artifacts**:
- `/prompts/artifact_critique_agent.xml`
- `/.claude/commands/refine-generator.xml` (updated)
- `/docs/context_engineering_strategy_v1.md` (updated Section 6.3)

---

## Phase 6: Extended SDLC Cascade (Optional)

### TASK-018: Additional Backlog Story Generation
**Priority**: Low
**Dependencies**: TASK-014
**Estimated Time**: 45 minutes
**Status**: ⏳ Pending

**Description**:
Execute Backlog Story Generator for remaining high-level stories from PRD.

**Output Artifacts**:
- `/artifacts/backlog_stories/US-01-02_feature/` through `/US-01-0N_feature/`
- Updated `/artifacts/prds/prd_001/TODO.md`

---

### TASK-019: ADR & Technical Specification Generation
**Priority**: Low
**Dependencies**: TASK-014
**Estimated Time**: 45 minutes
**Status**: ⏳ Pending

**Description**:
Execute User Story Generator to decompose PRD into actionable stories.

**Output Artifacts**:
- `/artifacts/user_stories/epic_001_story_001_v3.md` through `story_00N_v3.md`
- `/prompts/adr_generator.xml` (or spec_generator.xml)

---

### TASK-020: Code Generation
**Priority**: Low
**Dependencies**: TASK-019
**Estimated Time**: 60 minutes
**Status**: ⏳ Pending

**Description**:
Generate implementation code from technical specifications.

**Output Artifacts**:
- `/artifacts/code/` (source files)
- `/prompts/test_generator.xml`

---

### TASK-021: Test Generation
**Priority**: Low
**Dependencies**: TASK-020
**Estimated Time**: 45 minutes
**Status**: ⏳ Pending

**Description**:
Generate unit and integration tests for implementation code.

**Output Artifacts**:
- `/artifacts/tests/` (test files)
- Complete SDLC cascade demonstration

---

## Summary Statistics

**Total Tasks**: 22 (21 active + 1 completed)
**Critical Priority**: 12 tasks
**High Priority**: 6 tasks
**Medium Priority**: 2 tasks
**Low Priority**: 4 tasks

**Estimated Total Time**: ~12-15 hours

**Phase Breakdown**:
- Phase 1 (Bootstrap): 3 tasks, ~90 minutes
- Phase 2 (First Generator): 5 tasks, ~165 minutes
- Phase 3 (Epic Cascade): 4 tasks, ~110 minutes
- Phase 4 (PRD): 2 tasks, ~85 minutes
- Phase 5 (Validation): 3 tasks, ~120 minutes
- Phase 6 (Extended): 5 tasks, ~195 minutes (optional)

---

## Task Status Legend

- ⏳ Pending
- 🔄 In Progress
- ✅ Completed
- ⏸️ Blocked
- ⚠️ Issues Found

---

**Last Updated**: 2025-10-07
**Current Phase**: Phase 1 - Bootstrap
**Next Task**: TASK-000 (Extract & Generate Templates)
