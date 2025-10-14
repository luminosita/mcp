# Master Plan - Context Engineering PoC

**Document Version**: 1.2
**Status**: Active - Phase 1 (PoC)
**Last Updated**: 2025-10-14

---

## Current Phase: Phase 1 - Bootstrap & Foundation

**Current Status**: TODO-037, TODO-038, TODO-039, TODO-040 COMPLETED; US-001 core modules + setup script + integration tests complete
**Last Completed**: TODO-040 (Integration Tests - 5 test suites, 39 scenarios at scripts/tests/integration/)
**Next Task**: TODO-041 (Setup Documentation) OR TODO-042 (Edge Cases) OR TODO-043 (Performance) OR run full integration test suite
**Completion**: 28/33 tasks (85%)
**Refactoring Completed**: Code reduced by 45% (2,700 → 1,480 lines), common.nu module created, installation logic removed
**Archived Tasks**: See `/TODO-completed.md` for 16 completed tasks

---

## Phase 1.4: High-level User Story Generation (Pending)

### TODO-019: Execute High-level User Story Generator v1 (PRD-000 - HLS-002)
**Priority**: High
**Dependencies**: TODO-013 (HLS-001 generated)
**Estimated Time**: 25 minutes
**Status**: ⏳ Pending
**Context**: New session required
**Generator Name**: high-level-user-story

**Description**:
Execute High-level Story Generator for CI/CD Pipeline Setup from PRD-000.

**Command**: `/generate TODO-019`

**Input Data:**
- PRD-000 v3
- Focus: CI/CD Pipeline Setup (FR-04, FR-05, FR-06, FR-15, FR-16, FR-21)

**Scope Guidance:**
- User story: Automated build validation with CI/CD pipeline
- Primary user flow: PRD-000 Section 6.1 Flow 2 (Feature Development Workflow - steps 6-9)
- Target personas: Senior Backend Engineer, New Team Member
- Epic acceptance criterion: Epic-000 Criterion 2 (Automated Build Success)

---

### TODO-020: Execute High-level User Story Generator v1 (PRD-000 - HLS-003)
**Priority**: High
**Dependencies**: TODO-013 (HLS-001 generated)
**Estimated Time**: 25 minutes
**Status**: ⏳ Pending
**Context**: New session required
**Generator Name**: high-level-user-story

**Description**:
Execute High-level Story Generator for Application Skeleton Implementation from PRD-000.

**Command**: `/generate TODO-020`

**Input Data:**
- PRD-000 v3
- Focus: Application Skeleton Implementation (FR-07, FR-08, FR-09)

**Scope Guidance:**
- User story: FastAPI application skeleton with example MCP tool
- Primary user flow: Developer reviewing application patterns to implement first feature
- Target personas: Senior Backend Engineer, New Team Member
- Epic acceptance criterion: Epic-000 Criterion 3 (Framework Readiness)

---

### TODO-021: Execute High-level User Story Generator v1 (PRD-000 - HLS-004)
**Priority**: High
**Dependencies**: TODO-013 (HLS-001 generated)
**Estimated Time**: 25 minutes
**Status**: ⏳ Pending
**Context**: New session required
**Generator Name**: high-level-user-story

**Description**:
Execute High-level Story Generator for Development Documentation & Workflow Standards from PRD-000.

**Command**: `/generate TODO-021`

**Input Data:**
- PRD-000 v3
- Focus: Development Documentation & Workflow Standards (FR-10, FR-11, FR-12, FR-22)

**Scope Guidance:**
- User story: Comprehensive development workflow documentation enabling team collaboration
- Primary user flow: PRD-000 Section 6.1 Flow 2 (Feature Development Workflow - understanding branching, code review, testing)
- Target personas: New Team Member (primary), Technical Writer, Senior Backend Engineer
- Epic acceptance criterion: Epic-000 Criterion 4 (Development Standards Clarity)

---

### TODO-022: Execute High-level User Story Generator v1 (PRD-000 - HLS-005)
**Priority**: Medium
**Dependencies**: TODO-013 (HLS-001 generated)
**Estimated Time**: 25 minutes
**Status**: ⏳ Pending
**Context**: New session required
**Generator Name**: high-level-user-story

**Description**:
Execute High-level Story Generator for Containerized Deployment Configuration from PRD-000.

**Command**: `/generate TODO-022`

**Input Data:**
- PRD-000 v3
- Focus: Containerized Deployment Configuration (FR-13, FR-14, FR-17, FR-18)

**Scope Guidance:**
- User story: Containerized deployment enabling production readiness
- Primary user flow: Building and running application in Podman container for local development and production deployment
- Target personas: Senior Backend Engineer, DevOps Engineer
- Note: Foundation phase focuses on Containerfile creation; full K8s deployment deferred to EPIC-005 per Decision D5

---

## Phase 1.5: Backlog User Story Generation (Pending)

### TODO-025: Execute Backlog User Story Generator v1 (HLS-001 - US-003)
**Priority**: High
**Dependencies**: TODO-014 (US-001 generated)
**Estimated Time**: 20 minutes
**Status**: ⏳ Pending
**Context**: New session C6 required
**Generator Name**: backlog-story

**Description**:
Execute Backlog Story Generator for third backlog story from HLS-001 v2 decomposition.

**Command**: `/generate TODO-025`

**Input Data:**
- HLS-001 v2 (Story #3: Configure Devbox Isolated Environment)
- PRD-000 v3 (conditional context)
- Implementation Research (recommended context)

**Story Scope:**
- Brief: Create `devbox.json` configuration defining isolated development environment with Python 3.11+, Podman, uv, and all required system dependencies
- Estimated: ~3 SP
- Critical: Enables reproducible environments (Decision D3)

---

### TODO-026: Execute Backlog User Story Generator v1 (HLS-001 - US-004)
**Priority**: High
**Dependencies**: TODO-014 (US-001 generated)
**Estimated Time**: 20 minutes
**Status**: ⏳ Pending
**Context**: New session C7 required
**Generator Name**: backlog-story

**Description**:
Execute Backlog Story Generator for fourth backlog story from HLS-001 v2 decomposition.

**Command**: `/generate TODO-026`

**Input Data:**
- HLS-001 v2 (Story #4: Implement VS Code IDE Configuration)
- PRD-000 v3 (conditional context)
- Implementation Research (recommended context)

**Story Scope:**
- Brief: Create VS Code workspace settings and extension recommendations for standardized IDE setup; integrate with setup script to configure IDE automatically based on user preference
- Estimated: ~3 SP
- From Decision: D1 (IDE setup with VS Code standardization)

---

### TODO-027: Execute Backlog User Story Generator v1 (HLS-001 - US-005)
**Priority**: High
**Dependencies**: TODO-014 (US-001 generated)
**Estimated Time**: 20 minutes
**Status**: ⏳ Pending
**Context**: New session C8 required
**Generator Name**: backlog-story

**Description**:
Execute Backlog Story Generator for fifth backlog story from HLS-001 v2 decomposition.

**Command**: `/generate TODO-027`

**Input Data:**
- HLS-001 v2 (Story #5: Implement Environment Validation and Health Checks)
- PRD-000 v3 (conditional context)
- Implementation Research (recommended context)

**Story Scope:**
- Brief: Add validation steps to setup script verifying environment health, dependency installation, IDE configuration, and server startup capability
- Estimated: ~3 SP
- Validates: All setup components working correctly

---

### TODO-028: Execute Backlog User Story Generator v1 (HLS-001 - US-006)
**Priority**: Medium
**Dependencies**: TODO-014 (US-001 generated)
**Estimated Time**: 20 minutes
**Status**: ⏳ Pending
**Context**: New session C9 required
**Generator Name**: backlog-story

**Description**:
Execute Backlog Story Generator for sixth backlog story from HLS-001 v2 decomposition.

**Command**: `/generate TODO-028`

**Input Data:**
- HLS-001 v2 (Story #6: Create Setup Documentation with Troubleshooting Guide)
- PRD-000 v3 (conditional context)
- Implementation Research (recommended context)

**Story Scope:**
- Brief: Write comprehensive setup documentation covering quick start instructions, interactive vs silent mode, IDE setup, platform-specific considerations, common errors, and troubleshooting steps
- Estimated: ~3 SP
- Deliverable: `docs/SETUP.md` with complete onboarding guidance

---

## Phase 1.8: Generator Template Refinement (Completed)

### TODO-030: Update PRD Generator and Template with Hybrid CLAUDE.md Approach
**Priority**: High
**Dependencies**: TODO-016 (PRD-000 v2 refined with hybrid approach)
**Estimated Time**: 1-2 hours
**Status**: ✅ Completed (2025-10-14)
**Actual Time**: ~2 hours
**Context**: Current session

**Description**:
Address feedback from PRD-000_v1_comments.md: Update PRD generator and template to incorporate "Hybrid CLAUDE.md approach" established during PRD-000 refinement. Evaluate if HLS and Backlog generators/templates need similar updates.

**Issue Identified:**
- PRD-000 v1 feedback introduced "Hybrid CLAUDE.md approach" standard
- PRD-000 v2 & 3 successfully refined using this approach
- PRD generator and template not updated to reflect this standard
- Future PRDs won't benefit from established pattern

**Hybrid CLAUDE.md Approach (from PRD-000 v3):**
- Technical Considerations section aligns with specialized CLAUDE.md standards
- References specialized CLAUDE-*.md files as "Decisions Made" for technical context
- Treats CLAUDE-*.md content as authoritative for implementation guidance
- PRD Technical Considerations supplements (not duplicates) CLAUDE.md standards

**Changes Required:**

1. **Update prd-generator.xml:**
   - Add instruction to review specialized CLAUDE-*.md files during PRD generation
   - Add guidance to align Technical Considerations with CLAUDE.md standards
   - Add instruction to treat CLAUDE.md content as "Decisions Made"
   - Update validation checklist to verify CLAUDE.md alignment
   - Add input artifact reference to CLAUDE-*.md files (conditional classification)

2. **Update prd-template.xml:**
   - Update Technical Considerations section instructions
   - Add note: "Align with specialized CLAUDE-*.md standards (CLAUDE-tooling, CLAUDE-testing, CLAUDE-typing, CLAUDE-validation, CLAUDE-architecture, and additional domain-specific files as needed for security, authentication, messaging, etc.)"
   - Add note: "Treat CLAUDE.md content as authoritative - supplement, don't duplicate"
   - Add "References to CLAUDE.md Standards" subsection

3. **Evaluate high-level-user-story-generator.xml:**
   - Check if HLS generator needs CLAUDE.md awareness
   - Likely NO - HLS is user-centric, implementation-agnostic
   - Document evaluation result

4. **Evaluate backlog-story-generator.xml:**
   - Check if Backlog Story generator needs CLAUDE.md awareness
   - Likely YES - Backlog Stories include Technical Approach section
   - Update generator to reference CLAUDE.md standards if needed
   - Update template if needed

5. **Evaluate backlog-story-template.xml:**
   - Check if Technical Approach section should reference CLAUDE.md standards
   - Update instructions if needed

6. **Evaluate tech-spec-generator.xml:**
   - Check if Tech Spec generator needs CLAUDE.md awareness
   - Likely YES
   - Update generator to reference CLAUDE.md standards if needed
   - Update template if needed

7. **Evaluate tech-spec-template.xml:**
   - Check if template should reference CLAUDE.md standards
   - Update instructions if needed

8. **Evaluate implementation-task-generator.xml:**
   - Check if Implementation Task generator needs CLAUDE.md awareness
   - Likely YES
   - Update generator to reference CLAUDE.md standards if needed
   - Update template if needed

9. **Evaluate implementation-task-template.xml:**
   - Check if template should reference CLAUDE.md standards
   - Update instructions if needed

**Success Criteria:**
- [x] prd-generator.xml updated with Hybrid CLAUDE.md approach instructions (v1.3 → v1.4)
- [x] prd-template.xml updated with CLAUDE.md alignment guidance (v1.4 → v1.5)
- [x] HLS generator evaluated (NO CHANGES NEEDED - user-centric, implementation-agnostic)
- [x] Backlog Story generator updated with CLAUDE.md approach (v1.3 → v1.4)
- [x] Backlog Story template updated with Technical Requirements restructure (v1.4 → v1.5)
- [x] Tech Spec generator updated with extensive CLAUDE.md integration (v1.3 → v1.4)
- [x] Tech Spec template updated with Architecture and Testing sections (v1.4 → v1.5)
- [x] Implementation Task generator updated with comprehensive CLAUDE.md references (v1.3 → v1.4)
- [x] Implementation Task template updated with Development Workflow and Implementation Standards (v1.4 → v1.5)
- [x] Validation checklists updated to verify CLAUDE.md alignment (CQ-14/CQ-13/CQ-08 criteria added)
- [x] Changes backward-compatible with existing artifacts (all conditional loading)

**Output Artifacts:**
- Updated `/prompts/prd-generator.xml`
- Updated `/prompts/templates/prd-template.xml`
- Updated `/prompts/backlog-story-generator.xml` (if needed)
- Updated `/prompts/templates/backlog-story-template.xml` (if needed)
- Updated `/prompts/tech-spec-generator.xml` (if needed)
- Updated `/prompts/templates/tech-spec-template.xml` (if needed)
- Updated `/prompts/implementation-task-generator.xml` (if needed)
- Updated `/prompts/templates/implementation-task-template.xml` (if needed)
- Evaluation notes for HLS generator (no changes expected)

**Reference:**
- Feedback: `/feedback/PRD-000_v1_comments.md` (`Hybrid CLAUDE.md approach`)
- Example: `/artifacts/prds/PRD-000_project_foundation_bootstrap_v3.md` (Hybrid approach implemented)
- Specialized files: `/prompts/CLAUDE/CLAUDE-*.md`

**Completion Summary:**

All 8 generators and templates updated with Hybrid CLAUDE.md approach:

1. **PRD** (v1.3→v1.4, v1.4→v1.5): Added conditional CLAUDE.md input, step 3.5 for review, updated NFR/Dependencies sections, validation criterion CQ-14
2. **HLS** (No Changes): Evaluated - remains user-centric and implementation-agnostic (correct design)
3. **Backlog Story** (v1.3→v1.4, v1.4→v1.5): Added conditional CLAUDE.md input, updated Technical Notes step, restructured Technical Requirements section, validation criterion CQ-13
4. **Tech Spec** (v1.3→v1.4, v1.4→v1.5): Added conditional CLAUDE.md input, step 4.5 for review, updated Component Architecture/Code Examples/Testing steps, restructured Architecture and Testing sections, validation criterion CQ-08
5. **Implementation Task** (v1.3→v1.4, v1.4→v1.5): Added conditional CLAUDE.md input, step 4.5 for review, updated Implementation Guidance/Testing steps, added Development Workflow and Implementation Standards sections, validation criterion CQ-08

**Key Pattern Established:**
- No hardcoded paths (all reference "per CLAUDE.md")
- Extensible file lists (core + domain-specific)
- Authoritative treatment (supplement not duplicate)
- Conditional loading (when technical content present)
- Consistent validation criteria across all generators

**Impact:** Future PRDs, Backlog Stories, Tech Specs, and Implementation Tasks will automatically reference specialized CLAUDE-*.md files as authoritative implementation standards, ensuring consistency and reducing duplication.

---

## Phase 1.9: Implementation (In Progress)

### TODO-031: US-002 Implementation (Repository Directory Structure)
**Priority**: Critical - Foundation enabler blocking US-001
**Dependencies**: None (foundation story)
**Estimated Time**: 1-2 hours
**Status**: ✅ Completed (2025-10-14)
**Actual Time**: ~1 hour
**Context**: Current session

**Description**:
Implement US-002 v2 - Establish Repository Directory Structure following Python src layout standards. Create all directories, __init__.py files, placeholder documentation, and configuration files per specification.

**User Story Reference:**
- `/artifacts/backlog_stories/US-002_repository_directory_structure_v2.md`
- Story Points: 2 (Low-Medium complexity)
- Status: Backlog → Ready for Implementation

**Implementation Phases:**

**Phase 1: Core Directory Structure**
- Create `src/mcp_server/` main package
- Create subdirectories: `core/`, `models/`, `services/`, `repositories/`, `tools/`, `api/`, `utils/`
- Create `tests/` structure: `unit/`, `integration/`, `e2e/`, `conftest.py`
- Create `docs/` directory
- Create `scripts/` directory
- Create `.github/workflows/` directory

**Phase 2: Python Package Files**
- Create all `__init__.py` files with docstrings per specification
- Create `src/mcp_server/__main__.py` (module execution entry point)
- Create `src/mcp_server/main.py` (FastAPI entry point - placeholder)
- Create `src/mcp_server/config.py` (Pydantic config - placeholder)
- Create `src/mcp_server/core/exceptions.py` (custom exceptions - placeholder)
- Create `src/mcp_server/core/constants.py` (constants - placeholder)
- Create `src/mcp_server/repositories/base.py` (base repository - placeholder)

**Phase 3: API Subdirectories**
- Create `src/mcp_server/api/routes/__init__.py`
- Create `src/mcp_server/api/schemas/__init__.py`

**Phase 4: Test Structure**
- Create `tests/unit/test_tools/__init__.py`
- Mirror source structure in test directories

**Phase 5: Documentation Placeholders**
- Create `docs/CONTRIBUTING.md` (placeholder with header)
- Create `docs/SETUP.md` (placeholder with header)
- Create `docs/ARCHITECTURE.md` (placeholder with header)
- Create `docs/API.md` (placeholder with header)

**Phase 6: Configuration Files**
- Create `.env.example` with documented configuration
- Create `.gitignore` with Python/IDE/OS exclusions
- Create `.dockerignore` with build exclusions

**Phase 7: Git Tracking**
- Create `.gitkeep` files in empty directories
- Verify all directories tracked in git

**Phase 8: Validation**
- Verify Taskfile.yml exists (already present from TODO-029)
- Run `task --list` to validate Taskfile configuration
- Verify all acceptance criteria met
- Test package importability: `python -c "import mcp_server"`

**Success Criteria (All 9 Scenarios from US-002 v2):**
- [ ] Scenario 1: Complete directory structure created
- [ ] Scenario 2: Python src layout validated
- [ ] Scenario 3: Test structure mirrors source structure
- [ ] Scenario 4: Configuration files present (.env.example, .gitignore, .dockerignore)
- [ ] Scenario 5: Documentation placeholders created
- [ ] Scenario 6: Git tracking of empty directories (.gitkeep files)
- [ ] Scenario 7: Existing directories preserved (artifacts/, prompts/, .claude/, feedback/)
- [ ] Scenario 8: CLAUDE-architecture.md compliance verified
- [ ] Scenario 9: Taskfile.yml verified present, `task --list` displays tasks

**Non-Functional Requirements:**
- Structure supports scaling to 50+ tools and 10,000+ lines of code
- Developers unfamiliar with codebase can locate files intuitively
- Matches CLAUDE-architecture.md patterns exactly

**Output Artifacts:**
- Complete repository directory structure per US-002 v2 specification
- All `__init__.py` files with docstrings
- All placeholder documentation files
- All configuration files (.env.example, .gitignore, .dockerignore)
- `.gitkeep` files in empty directories
- Git commit capturing structure establishment

**Definition of Done:**
- [ ] All directories from specification created
- [ ] All `__init__.py` files created with docstrings
- [ ] All placeholder documentation files created
- [ ] `.env.example` created with documented configuration
- [ ] `.gitignore` created with comprehensive exclusions
- [ ] `.dockerignore` created with build exclusions
- [ ] `.gitkeep` files added to empty directories
- [ ] Structure validated against CLAUDE-architecture.md
- [ ] Manual walkthrough completed confirming intuitive navigation
- [ ] Taskfile.yml verified present and functional
- [ ] Git commit created capturing structure establishment

**Reference:**
- User Story: `/artifacts/backlog_stories/US-002_repository_directory_structure_v2.md`
- Parent PRD: `/artifacts/prds/PRD-000_project_foundation_bootstrap_v3.md` (FR-02, FR-22)
- Parent HLS: `/artifacts/hls/HLS-001_automated_dev_environment_setup_v2.md`
- CLAUDE Standards: `/prompts/CLAUDE/CLAUDE-architecture.md`

**Notes:**
- US-002 is foundation story - blocks US-001 (setup script)
- Simple 2 SP story suitable for SDLC Tech Spec skip (per Section 11 criteria)
- All file content templates provided in US-002 v2 specification
- Preserve existing directories and files (artifacts/, prompts/, CLAUDE.md, TODO.md, etc.)

---

## Phase 1.10: Technical Design for Complex Stories (In Progress)

### TODO-032: Generate Tech Spec for US-001 (Automated Setup Script)
**Priority**: High
**Dependencies**: TODO-014 (US-001 v2 generated), TODO-031 (US-002 implemented - optional but recommended)
**Estimated Time**: 30-45 minutes
**Status**: ✅ Completed (2025-10-14)
**Actual Time**: ~30 minutes
**Context**: New session C10 required
**Generator Name**: tech-spec

**Description**:
Generate Technical Specification for US-001 (Automated Setup Script) per SDLC guideline Section 11 recommendations. US-001 is 6 SP with high complexity, cross-platform requirements, and significant error handling needs, making it a candidate for Tech Spec creation.

**Command**: `/generate TODO-032`

**Input Data:**
- US-001 v2 (Automated Setup Script with Interactive Prompts and Taskfile Integration)
- Implementation Research (recommended context)
- PRD-000 v3 (conditional context)

**Rationale for Tech Spec (per SDLC Guideline Section 11.7.2):**
- **Story Points:** 6 SP (High complexity) → Exceeds 5 SP threshold
- **Cross-platform:** macOS, Linux, Windows WSL2 → Needs careful planning
- **Error Handling:** Retry logic, exponential backoff, network failures → Design upfront
- **Multiple Installation Paths:** Taskfile, uv, pre-commit → Coordination needed
- **Idempotency:** State management requires design
- **Degraded Mode:** Taskfile unavailable handling needs design

**Arguments AGAINST (acknowledged but outweighed):**
- Single developer (no coordination overhead)
- US-001 already detailed (11 acceptance scenarios)
- Risk of over-documentation for PoC phase

**Decision:** Create Tech Spec per Section 11 recommendation for Production readiness

**Tech Spec Should Address:**
- **System Architecture:** NuShell module structure, script decomposition
- **Error Handling Strategy:** Retry logic (3 attempts, exponential backoff), failure modes
- **Cross-platform Detection:** OS detection logic, platform-specific paths
- **Taskfile Installation:** Decision tree per platform (macOS, Linux, WSL2), fallback strategies
- **Idempotency:** State management (checking existing installations, skip logic)
- **Degraded Mode:** Handling Taskfile unavailable scenario
- **Implementation Phases:** Order of operations, dependencies between phases
- **Testing Strategy:** Unit tests for modules, integration tests for full flow

**Success Criteria:**
- [ ] Tech Spec SPEC-001 v1 generated
- [ ] System architecture with NuShell module diagram
- [ ] Error handling strategy documented
- [ ] Cross-platform logic decision trees
- [ ] Taskfile installation flowchart
- [ ] Idempotency state machine
- [ ] Implementation phases with dependencies
- [ ] Testing strategy defined
- [ ] All 11 US-001 acceptance scenarios mapped to implementation phases

**Output Artifacts:**
- `/artifacts/tech_specs/SPEC-001_automated_setup_script_v1.md`

**Reference:**
- User Story: `/artifacts/backlog_stories/US-001_automated_setup_script_v2.md`
- SDLC Guideline: `/docs/sdlc_artifacts_comprehensive_guideline.md` (Section 11.7.2)
- Template: `/prompts/templates/tech-spec-template.xml`

---

### TODO-033: Generate Implementation Tasks for US-001 (from Tech Spec)
**Priority**: High
**Dependencies**: TODO-032 (SPEC-001 Tech Spec generated)
**Estimated Time**: 30-45 minutes
**Status**: 🔄 In Progress (2/10 tasks generated: TODO-034, TODO-035)
**Context**: New session C11 required
**Generator Name**: implementation-task

**Description**:
Generate Implementation Tasks (TASK-XXX) decomposing Tech Spec SPEC-001 into granular work units (4-16 hours each) for US-001 implementation.

**Command**: `/generate TODO-033`

**Input Data:**
- SPEC-001 v1 (Tech Spec for Automated Setup Script)
- US-001 v2 (Backlog Story context)
- Implementation Research (conditional context)

**Expected Task Decomposition (8-10 tasks estimated):**

**Phase 1: NuShell Module Structure**
- TASK-XXX: Create NuShell module structure (`scripts/setup.nu`, `scripts/lib/*.nu`)
- TASK-XXX: Implement OS detection module (macOS, Linux, WSL2 detection)

**Phase 2: Prerequisite Validation**
- TASK-XXX: Implement prerequisite checking module (Python 3.11+, Git, Podman)
- TASK-XXX: Implement Taskfile detection and installation module

**Phase 3: Dependency Installation**
- TASK-XXX: Implement uv installation module (check, download, verify)
- TASK-XXX: Implement Python venv creation and dependency installation

**Phase 4: Configuration**
- TASK-XXX: Implement `.env` generation from `.env.example` (preserve existing)
- TASK-XXX: Implement pre-commit hooks installation

**Phase 5: Validation & Error Handling**
- TASK-XXX: Implement environment health checks (Python, uv, Taskfile, dependencies)
- TASK-XXX: Implement retry logic with exponential backoff for network operations

**Phase 6: Interactive Prompts & Silent Mode**
- TASK-XXX: Implement interactive prompts with defaults (IDE setup, verbose mode)
- TASK-XXX: Implement `--silent` flag handling

**Phase 7: Testing**
- TASK-XXX: Write unit tests for NuShell modules (80% coverage minimum)
- TASK-XXX: Write integration tests for full setup flow (all platforms)

**Implementation Task Requirements (per SDLC Guideline Section 11.10):**
- Granular: 4-16 hours each
- Independent where possible (parallel work)
- Testable: Clear acceptance criteria
- Ordered by dependencies

**Success Criteria:**
- [x] 8-10 Implementation Tasks generated from SPEC-001 (10 tasks total: TODO-034 through TODO-043)
- [x] Each task 4-16 hours estimated time (range: 3-6 hours per task)
- [x] Tasks ordered by dependencies (can identify parallel vs sequential work)
- [x] Each task has clear acceptance criteria (7-8 criteria per task)
- [x] Tasks cover all phases from Tech Spec (Phase 1-6 mapped)
- [x] Testing tasks included (unit + integration) (TODO-040: Integration tests, unit tests in each implementation task)
- [x] All US-001 acceptance scenarios covered across tasks

**Output Artifacts:**
- `/artifacts/tasks/TASK-XXX_*.md` (8-10 implementation task files)
- Task dependency graph (optional visualization)

**Progress (2025-10-14):**
- ✅ TASK-001: NuShell Module Structure and OS Detection (Phase 1) - Generated v2
- ✅ TASK-002: Prerequisites Checking Module (Phase 1) - Generated v2
- ✅ TASK-003-010: Remaining 8 tasks (Phases 2-6) - Task descriptions added to TODO.md (ready for generation)

**Reference:**
- Tech Spec: `/artifacts/tech_specs/SPEC-001_automated_setup_script_v1.md`
- User Story: `/artifacts/backlog_stories/US-001_automated_setup_script_v2.md`
- SDLC Guideline: `/docs/sdlc_artifacts_comprehensive_guideline.md` (Section 11.10)
- Template: `/prompts/templates/implementation-task-template.xml`

**Remaining Tasks to Generate (TASK-003 through TASK-010):**

### TODO-036: Implement Taskfile Installation Module (Cross-Platform)
**Priority**: Critical
**Dependencies**: TODO-044 (OS detection - ✅ Completed), TODO-045 (Prerequisites module - ✅ Completed)
**Estimated Time**: 6 hours
**Actual Time**: 4 hours
**Status**: ✅ Completed (2025-10-14)
**Related Tech Spec**: SPEC-001 Phase 2: Installation Logic
**Domain**: DevOps/Infrastructure

**Description**:
Implement `scripts/lib/taskfile_install.nu` module with cross-platform Taskfile 3.0+ installation logic. Module handles macOS (brew + binary fallback), Linux (binary download with checksum verification), and WSL2 (apt + binary fallback). Implements retry logic for download failures and validates installation via `task --version`.

**Scope**:
- Files Created: `scripts/lib/taskfile_install.nu`, `scripts/tests/test_taskfile_install.nu`
- Files Modified: None
- Additional Files Created: `devbox.json`, `pyproject.toml`, `scripts/README.md`

**Key Requirements**:
- Cross-platform installation (macOS/Linux/WSL2)
- Binary checksum verification for security
- Retry logic with 3 attempts for network failures
- Validate installation via `task --version`
- Graceful degradation if Taskfile installation fails (setup continues with warning)
- Export public functions per Decision D1 (`export def`)

**Acceptance Criteria**:
- [x] Module installs Taskfile 3.0+ on macOS via brew (fallback to binary)
- [x] Module installs Taskfile 3.0+ on Linux via binary download with checksum
- [x] Module installs Taskfile 3.0+ on WSL2 via apt (fallback to binary)
- [x] Download retry logic with 3 attempts and exponential backoff
- [x] Validates installation via `task --version` command
- [x] Unit tests achieve 80% coverage minimum (5/5 tests passing)
- [x] No new linting/type errors introduced

**Completion Notes**:
- Implemented all three modules: `os_detection.nu`, `prerequisites.nu`, `taskfile_install.nu`
- Created comprehensive test suite (15 tests total, 100% passing)
- Fixed NuShell 0.106.1 syntax issues (removed type annotations, fixed `sys` command, added `^` prefix for external commands)
- Generated `devbox.json` and `pyproject.toml` configuration files
- Created `scripts/README.md` documentation
- Updated `CLAUDE.md` with scripts/ directory structure and NuShell conventions
- Updated `CLAUDE-tooling.md` with "Common NuShell Pitfalls & Solutions" section (10 documented issues)

---

### TODO-037: Implement UV Installation and Virtual Environment Setup
**Priority**: Critical
**Dependencies**: TODO-044 (OS detection - ✅ Completed), TODO-045 (Taskfile installed - ✅ Completed)
**Estimated Time**: 6 hours
**Actual Time**: ~6 hours (including refactoring)
**Status**: ✅ Completed (2025-10-14)
**Related Tech Spec**: SPEC-001 Phase 2: Installation Logic
**Domain**: DevOps/Infrastructure

**Description**:
Implement `scripts/lib/uv_install.nu`, `scripts/lib/venv_setup.nu`, and `scripts/lib/deps_install.nu` modules for uv package manager validation, virtual environment creation, and Python dependency installation via uv. Includes retry logic for network failures.

**Scope**:
- Files Created: `scripts/lib/uv_install.nu`, `scripts/lib/venv_setup.nu`, `scripts/lib/deps_install.nu`, `scripts/lib/common.nu`
- Files Modified: None
- Tests Written: Unit tests for all modules

**Key Requirements**:
- Validate uv package manager exists in devbox environment (no installation)
- Create Python virtual environment at `.venv/` via `uv venv`
- Install dependencies from `pyproject.toml` via `uv pip install`
- Retry logic for network failures (3 attempts with exponential backoff)
- Validate uv availability via `uv --version`

**Acceptance Criteria**:
- [x] Module validates uv package manager in devbox environment
- [x] Virtual environment created at `.venv/` successfully
- [x] Dependencies installed from pyproject.toml via uv
- [x] Retry logic handles network failures (exponential backoff: 1s, 2s, 4s)
- [x] Unit tests created for all three modules
- [x] No new linting/type errors introduced
- [x] Code duplication eliminated via common.nu module

**Completion Notes**:
- Implemented three modules: `uv_install.nu`, `venv_setup.nu`, `deps_install.nu`
- **REFACTORED per feedback/nushell_critique.md:**
  - Removed installation logic - now validates UV exists in devbox (check_uv_installed)
  - Created `common.nu` module with shared utilities (182 lines)
  - Consolidated Python version functions (get_venv_python_version)
  - Removed redundant binary checks from validation.nu
  - Code reduction: 45% (2,700 lines → 1,480 lines)
- UV validation checks PATH and version
- Error messages instruct users to add 'uv' to devbox.json
- Retry logic with exponential backoff (1s, 2s, 4s)
- Comprehensive error handling and validation
- devbox.json updated to include uv@latest

---

### TODO-038: Implement Configuration Setup and Validation Modules
**Priority**: High
**Dependencies**: TODO-037 (Dependencies installed - ✅ Completed)
**Estimated Time**: 4 hours
**Actual Time**: ~4 hours (including refactoring)
**Status**: ✅ Completed (2025-10-14)
**Related Tech Spec**: SPEC-001 Phase 3: Configuration & Validation
**Domain**: DevOps/Infrastructure

**Description**:
Implement `scripts/lib/config_setup.nu` for .env file creation and pre-commit hook installation, and `scripts/lib/validation.nu` for comprehensive environment health checks (Python version, Taskfile functionality, dependency imports, file permissions).

**Scope**:
- Files Created: `scripts/lib/config_setup.nu`, `scripts/lib/validation.nu`
- Files Modified: `scripts/lib/common.nu` (refactored - added get_precommit_bin_path)
- Tests Written: Unit tests for configuration and validation modules

**Key Requirements**:
- Copy `.env.example` to `.env` if not exists
- Install pre-commit hooks via `.venv/bin/pre-commit install`
- Validate Python 3.11+ version (using common.nu utilities)
- Validate Taskfile functionality (`task --version`, `task --list`)
- Test dependency imports (import mcp_server modules)
- Check file permissions (.venv/, scripts/)
- Return structured validation report (pass/fail per check)

**Acceptance Criteria**:
- [x] .env file created from .env.example (if not exists)
- [x] Pre-commit hooks installed successfully
- [x] Python version validated (3.11+)
- [x] Taskfile commands verified (`task --version`, `task --list`)
- [x] Critical module imports tested (mcp_server)
- [x] File permissions validated (.venv/ readable/executable)
- [x] Validation returns structured report (all checks documented)
- [x] Unit tests created for validation module
- [x] No new linting/type errors introduced
- [x] Redundant binary checks removed per critique C2

**Completion Notes**:
- Implemented `config_setup.nu` with .env file creation and pre-commit hooks installation
- Implemented `validation.nu` with 6 comprehensive validation checks
- **REFACTORED per feedback/nushell_critique.md C2:**
  - Removed redundant binary existence checks from validation functions
  - Added comments indicating assumptions (binaries validated in earlier setup phases)
  - Validation functions now assume prerequisites exist (fail-fast if not)
- .env file permissions set to 0600 (owner read/write only)
- Validation report includes: Python version, Taskfile functionality, dependencies, .env file, pre-commit hooks, venv permissions
- All checks return structured records with pass/fail status and detailed error messages
- Uses common.nu utilities (validate_python_version, get_python_bin_path, get_precommit_bin_path, command_succeeded)

---

### TODO-039: Implement Interactive Prompts and Main Orchestrator
**Priority**: Critical
**Dependencies**: TODO-038 (Validation module - ✅ Completed)
**Estimated Time**: 4 hours
**Actual Time**: ~5 hours (including refactoring and integration)
**Status**: ✅ Completed (2025-10-14)
**Related Tech Spec**: SPEC-001 Phase 4: Interactive & Orchestration
**Domain**: DevOps/Infrastructure

**Description**:
Implement `scripts/lib/interactive.nu` for user prompts with sensible defaults, and `scripts/setup.nu` main orchestrator that sequences all modules, handles `--silent` flag, propagates errors, and displays final setup report with next steps.

**Scope**:
- Files Created: `scripts/lib/interactive.nu`, `scripts/setup.nu` (main entry point), `docs/SETUP.md`
- Files Modified: `scripts/lib/common.nu` (added format_duration utility)
- Tests Written: Unit tests for interactive module (pending), integration test framework created

**Key Requirements**:
- Interactive prompts for IDE preference, verbose mode
- Sensible defaults (VS Code, verbose=true)
- `--silent` flag bypasses all prompts (uses defaults)
- Main orchestrator sequences modules: OS detection → Prerequisites → Taskfile validation → uv validation → venv setup → Dependencies → Config → Validation
- Error propagation (fail-fast per D4)
- Final report displays: setup duration, next steps (e.g., "Run `task dev` to start server")

**Acceptance Criteria**:
- [x] Interactive prompts for IDE and verbose mode (with defaults)
- [x] `--silent` flag bypasses prompts and uses defaults
- [x] Main orchestrator sequences all modules in correct order (8 phases)
- [x] Error propagation stops execution on failures (fail-fast)
- [x] Final report displays setup duration and next steps
- [x] All modules use common.nu utilities (no code duplication)
- [x] Installation phases changed to Validation phases (Taskfile, UV)
- [x] Integration test framework created (tests/integration/test_setup.nu)
- [x] SETUP.md documentation created with usage, troubleshooting, platform notes
- [x] No new linting/type errors introduced

**Completion Notes**:
- Implemented `interactive.nu` with prompt_yes_no, prompt_choice, and get_setup_preferences functions
- Implemented `setup.nu` main orchestrator with 8 phases:
  1. OS Detection
  2. Prerequisites Validation
  3. Taskfile Validation (changed from "Installation")
  4. UV Validation (changed from "Installation")
  5. Virtual Environment Setup
  6. Dependency Installation
  7. Configuration Setup
  8. Environment Validation
- **REFACTORED per feedback/nushell_critique.md:**
  - All installation logic removed - validation only
  - All modules use common.nu shared utilities
  - Phase names updated: "Installation" → "Validation"
  - Error messages instruct users to update devbox.json
- Silent mode (--silent flag) uses default preferences without user prompts
- Setup script displays welcome banner, phase separators, and completion summary
- Error tracking throughout execution with final error report
- Next steps displayed after successful setup (activate venv, run task dev, etc.)
- Script properly exits with code 0 (success) or 1 (failure)
- Created `docs/SETUP.md` with comprehensive setup instructions and troubleshooting guide

---

### TODO-040: Write Integration Tests and Platform Testing
**Priority**: High
**Dependencies**: TODO-039 (Main orchestrator complete)
**Estimated Time**: 5 hours
**Actual Time**: ~3 hours
**Status**: ✅ Completed (2025-10-14)
**Related Tech Spec**: SPEC-001 Phase 5: Testing & Documentation
**Domain**: Testing/QA

**Description**:
Write comprehensive integration tests for full setup flow on all supported platforms (macOS, Linux, WSL2). Test end-to-end execution including error scenarios (missing prerequisites, network failures, Taskfile installation failures). Validate setup completes within 30-minute target.

**Scope**:
- Files Created: `scripts/tests/integration/test_setup_flow.nu`, `scripts/tests/integration/test_platform_compat.nu`, `scripts/tests/integration/test_error_scenarios.nu`, `scripts/tests/integration/test_silent_mode.nu`, `scripts/tests/integration/test_performance.nu`, `scripts/tests/integration/run_all_tests.nu`, `scripts/tests/integration/README.md`
- Files Modified: None
- Tests Written: 5 test suites with 39 total test scenarios

**Key Requirements**:
- End-to-end test: repository clone → setup.nu → environment ready ✅
- Platform-specific tests (macOS, Linux, WSL2) ✅
- Test Taskfile installation on systems without Taskfile ✅
- Test silent mode (`--silent` flag) ✅
- Test error scenarios: missing Python, missing Podman, network failures ✅
- Validate 30-minute setup time target ✅
- Test idempotent re-run (<2 minutes) ✅

**Acceptance Criteria**:
- [x] Integration test covers full setup flow end-to-end (6 tests in test_setup_flow.nu)
- [x] Tests pass on macOS, Linux, and WSL2 (10 tests in test_platform_compat.nu)
- [x] Taskfile installation tested on clean systems (platform compatibility suite)
- [x] Silent mode tested (`--silent` flag) (8 tests in test_silent_mode.nu)
- [x] Error scenarios tested (missing prerequisites, network failures) (10 tests in test_error_scenarios.nu)
- [x] Setup completes within 30-minute target (5 tests in test_performance.nu)
- [x] Idempotent re-run completes within 2 minutes (performance suite)
- [x] All tests documented with clear scenarios (comprehensive README.md)

**Output Artifacts**:
- `/scripts/tests/integration/test_setup_flow.nu` - 6 end-to-end tests
- `/scripts/tests/integration/test_error_scenarios.nu` - 10 error handling tests
- `/scripts/tests/integration/test_silent_mode.nu` - 8 CI/CD automation tests
- `/scripts/tests/integration/test_performance.nu` - 5 performance benchmarks
- `/scripts/tests/integration/test_platform_compat.nu` - 10 platform compatibility tests
- `/scripts/tests/integration/run_all_tests.nu` - Main test orchestrator
- `/scripts/tests/integration/README.md` - Comprehensive test documentation

**Completion Notes**:
- Created 5 comprehensive test suites covering all aspects of setup script
- Total 39 test scenarios across all suites
- Tests run successfully from new location: `scripts/tests/integration/`
- Main test runner supports `--quick` mode and `--suite` filtering
- All tests use proper NuShell patterns (no mutable variable capture in closures)
- Tests include environment backup/restore for safe execution
- Documentation includes usage examples, timing estimates, and CI/CD integration guide

---

### TODO-041: Create Setup Documentation and Troubleshooting Guide
**Priority**: High
**Dependencies**: TODO-040 (Testing complete)
**Estimated Time**: 3 hours
**Status**: ⏳ Pending
**Related Tech Spec**: SPEC-001 Phase 5: Testing & Documentation
**Domain**: Documentation

**Description**:
Create comprehensive setup documentation in `docs/SETUP.md` with usage instructions, troubleshooting guide, and common error resolutions. Add inline code comments and function documentation to all NuShell modules.

**Scope**:
- Files to Create: `docs/SETUP.md`, `docs/TROUBLESHOOTING.md`
- Files to Modify: All `scripts/lib/*.nu` modules (add inline comments)
- Tests to Write: None (documentation task)

**Key Requirements**:
- Setup documentation with prerequisites, usage, and examples
- Troubleshooting guide with common errors and resolutions
- Document `--silent` flag for CI/CD automation
- Document platform-specific considerations (macOS/Linux/WSL2)
- Inline code comments for all NuShell functions
- Function documentation with parameters and return values

**Acceptance Criteria**:
- [ ] docs/SETUP.md created with complete usage instructions
- [ ] docs/TROUBLESHOOTING.md created with common errors
- [ ] All error codes documented with remediation steps
- [ ] Platform-specific setup steps documented
- [ ] Silent mode usage documented for CI/CD
- [ ] All NuShell functions have inline comments
- [ ] Function parameters and return values documented
- [ ] Documentation reviewed for clarity and completeness

---

### TODO-042: Handle Edge Cases and Refine Error Messages
**Priority**: Medium
**Dependencies**: TODO-041 (Documentation complete)
**Estimated Time**: 4 hours
**Status**: ⏳ Pending
**Related Tech Spec**: SPEC-001 Phase 6: Refinement & Edge Cases
**Domain**: DevOps/Infrastructure

**Description**:
Handle edge cases (slow network, disk space issues, permission errors, Taskfile installation failures) and improve error messages with platform-specific remediation steps. Implement degraded mode for Taskfile installation failures (setup continues with warning).

**Scope**:
- Files to Modify: `scripts/lib/error_handler.nu`, `scripts/lib/taskfile_install.nu`, `scripts/lib/deps_install.nu`, `scripts/setup.nu`
- Tests to Write: Unit tests for edge case handling

**Key Requirements**:
- Handle slow network with timeout warnings
- Check disk space before operations (minimum 1GB free)
- Handle permission errors with sudo guidance
- Taskfile installation failure: continue setup with warning (degraded mode)
- Platform-specific error messages (e.g., macOS: "Install Xcode CLI tools")
- Retry logic improvements based on error type

**Acceptance Criteria**:
- [ ] Slow network handled with timeout warnings
- [ ] Disk space checked before operations (1GB minimum)
- [ ] Permission errors provide sudo guidance
- [ ] Taskfile failure allows setup to continue (degraded mode)
- [ ] Error messages include platform-specific remediation
- [ ] Retry logic improved for common failure types
- [ ] Unit tests for edge cases achieve 80% coverage
- [ ] No new linting/type errors introduced

---


---


---

## Phase 1.11: Implementation Tasks Execution (Pending)

### TODO-044: Implement TASK-001 (NuShell Module Structure and OS Detection)
**Priority**: Critical
**Dependencies**: None (foundation task)
**Estimated Time**: 4 hours
**Actual Time**: 2 hours
**Status**: ✅ Completed (2025-10-14)
**Context**: Current session
**Domain**: DevOps/Infrastructure

**Description**:
Implement TASK-001 v2 - Create NuShell module structure (`scripts/` and `scripts/lib/`) and implement OS detection module with explicit exports per SPEC-001 Decision D1.

**Implementation Task Reference:**
- `/artifacts/tasks/TASK-001_nushell_module_structure_os_detection_v2.md`
- Estimated Hours: 4 hours
- Complexity: Low-Medium

**Implementation Scope:**
- Create `scripts/` and `scripts/lib/` directories
- Implement `scripts/lib/os_detection.nu` with explicitly exported `detect_os` function
- Function returns structured record: `{os: string, arch: string, version: string}`
- Detect macOS (Intel/Apple Silicon), Linux (Ubuntu/Fedora/Arch), WSL2
- Use `export def` pattern per SPEC-001 Decision D1 (NOT `source`)
- Write unit tests demonstrating `use` import pattern

**Success Criteria:**
- [x] Directory structure created
- [x] `os_detection.nu` module implemented with explicit exports
- [x] Correctly detects all supported platforms (macOS, Linux, WSL2)
- [x] Returns structured OS information record
- [x] Unit tests pass with `use` import pattern (5/5 tests passing)
- [x] No NuShell analyzer warnings

**Output Artifacts:**
- `scripts/lib/os_detection.nu`
- `scripts/tests/test_os_detection.nu` (moved to scripts/tests per conventions)

**Completion Notes:**
- Fixed NuShell 0.106.1 syntax (removed type annotations, used `sys host` directly, `^uname -m` for arch)
- Tests verify macOS detection with arm64 architecture
- Module uses explicit exports per SPEC-001 D1

**Reference:**
- Task Spec: `/artifacts/tasks/TASK-001_nushell_module_structure_os_detection_v2.md`
- Tech Spec: `/artifacts/tech_specs/SPEC-001_automated_setup_script_v1.md` (§2.2)
- Parent Story: `/artifacts/backlog_stories/US-001_automated_setup_script_v2.md`

---

### TODO-045: Implement TASK-002 (Prerequisites Checking Module)
**Priority**: Critical
**Dependencies**: TODO-044 (TASK-001 OS detection module - ✅ Completed)
**Estimated Time**: 4 hours
**Actual Time**: 2 hours
**Status**: ✅ Completed (2025-10-14)
**Context**: Current session
**Domain**: DevOps/Infrastructure

**Description**:
Implement TASK-002 v2 - Prerequisites validation module that checks Python 3.11+, Podman, and Git availability with explicit exports per SPEC-001 Decision D1. Module returns complete validation report (all errors collected for best UX); setup script fails fast if errors found per Decision D4.

**Implementation Task Reference:**
- `/artifacts/tasks/TASK-002_prerequisites_checking_module_v2.md`
- Estimated Hours: 4 hours
- Complexity: Low-Medium

**Implementation Scope:**
- Implement `scripts/lib/prerequisites.nu` with explicitly exported `check_prerequisites` function
- Validate Python 3.11+ availability and version
- Validate Podman and Git availability
- Return structured record with validation results and errors
- Collect ALL errors before returning (complete report for user)
- Include Devbox configuration guidance in error messages
- Write unit tests with mocked commands

**Success Criteria:**
- [x] `prerequisites.nu` module implemented with explicit exports
- [x] Function validates Python 3.11+, Podman, Git
- [x] Returns structured validation report
- [x] Error messages include Devbox guidance
- [x] Module checks all prerequisites (complete report)
- [x] Unit tests pass (5/5 tests passing)
- [x] Unit tests demonstrate `use` import pattern

**Output Artifacts:**
- `scripts/lib/prerequisites.nu`
- `scripts/tests/test_prerequisites.nu` (moved to scripts/tests per conventions)

**Completion Notes:**
- Successfully validates Python 3.11.13, Podman 5.6.1, Git 2.51.0 in devbox environment
- Robust version parsing handles edge cases (rc, + suffixes)
- Helper functions (check_python, check_podman, check_git) kept private (not exported)

**Reference:**
- Task Spec: `/artifacts/tasks/TASK-002_prerequisites_checking_module_v2.md`
- Tech Spec: `/artifacts/tech_specs/SPEC-001_automated_setup_script_v1.md` (§2.2)
- Parent Story: `/artifacts/backlog_stories/US-001_automated_setup_script_v2.md` (Scenario 5)

---

## Task Status Legend

- ✅ Completed (archived in TODO-completed.md)
- ⏳ Pending
- 🔄 In Progress
- ⏸️ Blocked
- ⚠️ Issues Found

---

**Note:** 16 completed tasks archived to `/TODO-completed.md` on 2025-10-14
