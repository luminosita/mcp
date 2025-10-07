# Master Plan - Context Engineering PoC

**Document Version**: 1.1
**Status**: Active - Phase 1 (PoC)
**Last Updated**: 2025-10-07

---

## Current Phase: Phase 1 - Bootstrap & Foundation

**Current Status**: Bootstrap completed, ready for generator execution
**Last Completed**: TASK-000 (Templates extracted and generated)
**Next Task**: TASK-001 (Regenerate Product Idea from IDEA.md)
**Completion**: 1/15 tasks (7%)

---

## Phase 1: Bootstrap & Foundation (PoC)

### TASK-000: Extract & Generate Templates
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

### TASK-001: Regenerate Product Idea from IDEA.md
**Priority**: High
**Dependencies**: None
**Estimated Time**: 10 minutes
**Status**: ⏳ Pending

**Description**:
Regenerate product idea document using the concept outlined in `/IDEA.md`. Replace existing `/docs/product-idea.md` with new content.

**Success Criteria**:
- [ ] Document describes product from IDEA.md
- [ ] Includes problem statement (high-level)
- [ ] Identifies target user persona
- [ ] Lists 3-5 key capabilities
- [ ] Readable and concise (<500 words)

**Output Artifacts**:
- `/docs/product-idea.md` (regenerated)

**Note**: DO NOT execute until explicitly requested by user

---

### TASK-002: Generate Product Vision Generator Prompt
**Priority**: Critical
**Dependencies**: TASK-000 (product-vision-template.xml must exist)
**Estimated Time**: 45 minutes
**Status**: ✅ Completed

**Description**:
Create the first generator prompt that will produce Product Vision documents and Epic Generator prompts.

**Success Criteria**:
- [x] Follows generator prompt XML schema template
- [x] References correct template path
- [x] Includes validation checklist in generator (not template)
- [x] Specifies dual outputs (vision doc + epic generator)
- [x] Contains research step for competitive analysis
- [x] Constraints marked as [CUSTOMIZE PER PRODUCT]
- [x] Valid XML syntax

**Output Artifacts**:
- `/prompts/product_vision_generator.xml` ✅

---

### TASK-003: Update Framework Files per Critique
**Priority**: Critical
**Dependencies**: TASK-002
**Estimated Time**: 60 minutes
**Status**: ✅ Completed

**Description**:
Apply all updates from feedback/context_engineering_strategy_v1_critique.md:
- Remove validation checklists from templates
- Add research instructions to generators
- Create generator schema template
- Update command files
- Update CLAUDE.md
- Update strategy document with phase reorganization

**Success Criteria**:
- [x] Validation checklists removed from all templates
- [x] Research steps added to Product Vision generator
- [x] Generator schema template created
- [x] Command files updated (remove /kickoff, fix references)
- [x] CLAUDE.md updated (remove Current Phase section, fix commands)
- [x] Strategy document updated with 5-phase model including MCP Server phase

**Output Artifacts**:
- Updated templates (6 files) ✅
- `/prompts/templates/generator-schema-template.xml` ✅
- Updated command files ✅
- Updated `/CLAUDE.md` ✅
- Updated `/docs/context_engineering_strategy_v1.md` ✅

---

## Phase 1: Generator Execution & Iteration

### TASK-004: Execute Product Vision Generator v1
**Priority**: Critical
**Dependencies**: TASK-001 (product-idea.md must exist), TASK-003
**Estimated Time**: 20 minutes
**Status**: ⏳ Pending
**Context**: New session C1 required
**Task Type**: product-vision

**Description**:
Execute Product Vision Generator in standalone context to produce first iteration of Product Vision document.

**Command**: `/execute-generator TASK-004`

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
- [ ] 3-5 key capabilities listed
- [ ] Competitive analysis includes research findings
- [ ] Alignment with product-idea.md
- [ ] Epic generator prompt is syntactically valid XML
- [ ] Readability: Accessible to non-expert (manual Flesch >60)

**Output Artifacts**:
- `/artifacts/product_vision_v1.md`
- `/prompts/epic_generator.xml`

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

**Command**: `/refine-generator product_vision_generator`

**Context Requirements**:
- All from TASK-004
- `/feedback/product_vision_v1_critique.md`

**Success Criteria**:
- [ ] Generator prompt updated with improvements
- [ ] Changes address critique points
- [ ] Version incremented (1.0 → 1.1)
- [ ] Vision v2 shows measurable improvement
- [ ] Epic generator prompt refined (if issues noted)

**Output Artifacts**:
- `/prompts/product_vision_generator.xml` (updated)
- `/artifacts/product_vision_v2.md`
- `/prompts/epic_generator.xml` (updated)

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

**Description**:
Apply final refinements, execute generator for v3, and **HUMAN manually updates** strategy document with lessons learned.

**Command**: `/refine-generator product_vision_generator`

**Context Requirements**:
- All from TASK-006
- `/feedback/product_vision_v2_critique.md`
- `/docs/context_engineering_strategy_v1.md`

**Success Criteria**:
- [ ] Generator prompt finalized (version 1.2)
- [ ] Vision v3 meets all validation criteria
- [ ] Epic generator prompt production-ready
- [ ] **HUMAN**: Strategy doc Section 8.2 manually updated with patterns
- [ ] Human approval obtained for v3

**Output Artifacts**:
- `/prompts/product_vision_generator.xml` (final)
- `/artifacts/product_vision_v3.md` (approved)
- `/prompts/epic_generator.xml` (final)
- `/docs/context_engineering_strategy_v1.md` (manually updated by human)

---

## Phase 1: Cascade to Epic Generation

### TASK-009: Execute Epic Generator v1
**Priority**: Critical
**Dependencies**: TASK-008
**Estimated Time**: 30 minutes
**Status**: ⏳ Pending
**Context**: New session C2 required
**Task Type**: epic

**Description**:
Execute Epic Generator in standalone context to decompose Product Vision into Epic documents.

**Command**: `/execute-generator TASK-009`

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

## Phase 1: PRD Generation

### TASK-012: Execute PRD Generator v1 (Epic 001)
**Priority**: Critical
**Dependencies**: TASK-011
**Estimated Time**: 25 minutes
**Status**: ⏳ Pending
**Context**: New session C3 required
**Task Type**: prd

**Description**:
Execute PRD Generator for first epic in standalone context.

**Command**: `/execute-generator TASK-012`

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
- [ ] PRD v2 critique created and refinements applied
- [ ] PRD v3 critique created and final refinements applied
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
**Task Type**: backlog-story

**Description**:
Execute Backlog Story Generator for first high-level story from PRD.

**Command**: `/execute-generator TASK-014`

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
- [ ] **HUMAN**: Final strategy document update with Phase 1 summary

**Output Artifacts**:
- `/docs/phase1_completion_report.md`
- `/docs/context_engineering_strategy_v1.md` (final Phase 1 update by human)

**Phase 1 Completion Gate**: After this task, Phase 1 (PoC) is complete

---

## Phase 2: MCP Server Extraction & Productization

### TASK-016: Plan MCP Server Architecture
**Priority**: High
**Dependencies**: TASK-015 (Phase 1 complete)
**Estimated Time**: 45 minutes
**Status**: ⏳ Pending

**Description**:
Design MCP Server architecture for hosting prompts and templates as reusable resources.

**Success Criteria**:
- [ ] MCP Server framework selected (Python/FastMCP or alternative - TBD)
- [ ] Architecture document created
- [ ] API/resource structure defined
- [ ] Integration patterns documented
- [ ] Migration plan from PoC to MCP Server defined

**Output Artifacts**:
- `/docs/mcp_server_architecture.md`
- `/docs/mcp_server_migration_plan.md`

---

### TASK-017: Create MCP Server Project Repository
**Priority**: Critical
**Dependencies**: TASK-016
**Estimated Time**: 30 minutes
**Status**: ⏳ Pending

**Description**:
Create new repository for MCP Server project following context engineering strategy.

**Success Criteria**:
- [ ] New repository created
- [ ] Initial project structure set up
- [ ] README with project overview
- [ ] CLAUDE.md for MCP Server project created
- [ ] TODO.md for MCP Server development created

**Output Artifacts**:
- New repository: `context-engineering-mcp-server/`
- Repository structure following strategy

**Note**: This task creates a new product that will be developed using the same context engineering framework (meta!)

---

### TASK-018: Extract and Clean Prompts/Templates
**Priority**: Critical
**Dependencies**: TASK-017
**Estimated Time**: 60 minutes
**Status**: ⏳ Pending

**Description**:
Extract all prompts and templates from PoC, remove PoC-specific references, generalize for reuse.

**Success Criteria**:
- [ ] All templates extracted and cleaned
- [ ] Generator schema template extracted
- [ ] All PoC-specific references removed
- [ ] Generic [CUSTOMIZE PER PRODUCT] placeholders added where needed
- [ ] Documentation updated
- [ ] Templates validated for XML correctness

**Output Artifacts**:
- Clean templates in MCP Server repository
- Migration log documenting changes

---

### TASK-019: Implement MCP Server
**Priority**: Critical
**Dependencies**: TASK-018
**Estimated Time**: TBD (requires product vision/epic/PRD from MCP Server project)
**Status**: ⏳ Pending

**Description**:
Implement MCP Server following architecture. Use context engineering framework to generate product vision, epics, PRDs, and implementation specs for the MCP Server itself.

**Success Criteria**:
- [ ] MCP Server product vision created (using framework!)
- [ ] Epics defined
- [ ] PRDs created
- [ ] Implementation complete
- [ ] Tests passing
- [ ] Documentation complete

**Output Artifacts**:
- Functional MCP Server
- MCP Server project artifacts (vision, epics, PRDs, code, tests)

**Note**: Time estimate TBD - depends on scope defined during vision/epic phases

---

### TASK-020: Test MCP Server with New Project
**Priority**: Critical
**Dependencies**: TASK-019
**Estimated Time**: 45 minutes
**Status**: ⏳ Pending

**Description**:
Validate MCP Server by creating a new test project that uses prompts/templates from the MCP Server.

**Success Criteria**:
- [ ] Test project created
- [ ] MCP Server integration successful
- [ ] Prompts/templates loaded from MCP Server
- [ ] Product vision generated using MCP-served resources
- [ ] No PoC-specific coupling detected
- [ ] Integration documented

**Output Artifacts**:
- Test project demonstrating MCP Server usage
- Integration guide
- Lessons learned document

**Phase 2 Completion Gate**: After this task, Phase 2 (MCP Server) is complete

---

## Phase 3: Semi-Automated Execution (Future)

### TASK-021: Implement Automated Self-Critique
**Priority**: Medium
**Dependencies**: TASK-020 (Phase 2 complete)
**Estimated Time**: 60 minutes
**Status**: ⏳ Pending

**Description**:
Implement Chain-of-Verification pattern for automated artifact critique.

**Success Criteria**:
- [ ] Critique agent prompt created
- [ ] Auto-generates structured feedback
- [ ] Integrates with refine-generator command
- [ ] Human approval at 80% threshold
- [ ] Documented in strategy

**Output Artifacts**:
- Critique agent implementation
- Updated refine-generator command
- Strategy document update

---

### TASK-022: Implement Script-Assisted Execution
**Priority**: Medium
**Dependencies**: TASK-021
**Estimated Time**: 45 minutes
**Status**: ⏳ Pending

**Description**:
Create automation scripts for generator execution from TODO.md.

**Success Criteria**:
- [ ] Script parses TODO.md
- [ ] Loads correct generator + context for task ID
- [ ] Handles versioning (v1, v2, v3)
- [ ] Provides human approval checkpoints
- [ ] Documented in strategy

**Output Artifacts**:
- Execution automation scripts
- Strategy document update

**Phase 3 Completion Gate**: After this task, semi-automation is complete

---

## Summary Statistics

**Total Tasks**: 22
**Completed**: 3 (14%)
**Pending**: 19 (86%)

**By Phase**:
- **Phase 1 (PoC)**: 15 tasks, 3 completed, 12 pending
- **Phase 2 (MCP Server)**: 5 tasks, 0 completed, 5 pending
- **Phase 3 (Semi-Automated)**: 2 tasks, 0 completed, 2 pending

**By Priority**:
- **Critical**: 14 tasks
- **High**: 6 tasks
- **Medium**: 2 tasks

**Estimated Remaining Time**: ~10-12 hours (Phase 1 only)

---

## Task Status Legend

- ✅ Completed
- ⏳ Pending
- 🔄 In Progress
- ⏸️ Blocked
- ⚠️ Issues Found

---

**Last Updated**: 2025-10-07
**Current Phase**: Phase 1 - Bootstrap & Foundation
**Next Task**: TASK-001 (Regenerate Product Idea from IDEA.md)
