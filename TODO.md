# Master Plan - Context Engineering PoC

**Document Version**: 1.3
**Last Updated**: 2025-10-14

---

## Current Phase: Phase 1.6 - Implementation (HLS-002 Stories)

**Current Status**: Parallel track - 3/6 stories implemented (US-003, US-004, US-005), backlog story generation in progress
**Last Completed**: TODO-031 (US-005 Automated Type Safety Validation implemented)
**Next Task**: TODO-026 (Generate US-006: Test Execution and Coverage Reporting)
**Implementation**: 3/6 stories implemented (US-003, US-004, US-005 complete)
**Generation**: 3/6 stories generated (US-003, US-004, US-005 complete)

**Parallel Track**: Continue backlog story generation (TODO-024 through TODO-028) while implementation begins

---

## Completed Work Summary (Phase 1.0 - Phase 1.5)

### Phase 1.0: Foundation (HLS-001 - Development Environment Setup)
**Status**: ✅ Completed

**Artifacts:**
- ✅ HLS-001: Development Environment Setup (Approved)
  - ✅ US-001: Automated Setup Script (v1, v2 - Done)
    - ✅ SPEC-001: Setup Script Technical Specification (Completed)
    - ✅ TASK-001: Core setup script implementation (Completed)
    - ✅ TASK-002: Interactive prompts and validation (Completed)
    - ✅ TASK-003: Error handling and recovery (Completed)
  - ✅ US-002: Repository Directory Structure (v1, v2 - Done)

**Summary**: Development environment foundation complete. Setup automation, repository structure, and core tooling (UV, Taskfile, testing frameworks) operational.

### Phase 1.5: Backlog Story Generation (HLS-002)
**Status**: 🔄 In Progress (2/6 stories generated)

**Artifacts:**
- ✅ US-003: CI/CD Pipeline Infrastructure (Generated, Draft)
- ✅ US-004: Automated Code Quality Checks (Generated, Draft)

---

## Phase 1.5: Backlog Story Generation - HLS-002 (CI/CD Pipeline Setup)

### TODO-023: Generate Backlog Story US-003 - CI/CD Pipeline Infrastructure
**Priority**: High
**Dependencies**: TODO-019 (HLS-002 generated)
**Estimated Time**: 30 minutes
**Status**: ✅ Completed (2025-10-14)
**Context**: New session recommended
**Generator Name**: backlog-story
**ID Assignment**: US-003 (HLS-001 used US-001, US-002)

**Description**:
Generate detailed backlog story for CI/CD Pipeline Infrastructure configuration from HLS-002.

**Command**: `/generate TODO-023`

**Input Data:**
- HLS-002 v1 (CI/CD Pipeline Setup)
- Backlog Story 1: Configure CI/CD Pipeline Infrastructure (~5 SP)

**Scope Guidance:**
- Set up GitHub Actions workflow configuration
- Trigger builds on feature branch commits
- Execute validation suite within 5-minute target
- Configure build status reporting to PR

**Completion Notes:**
- ✅ Generated US-003 v1 at /artifacts/backlog_stories/US-003_ci_cd_pipeline_infrastructure_v1.md
- ✅ All 27 validation criteria passed (Content Quality: 13/13, Upstream Traceability: 8/8, Consistency: 6/6)
- ✅ Status set to Draft, ready for Product Owner review

---

### TODO-024: Generate Backlog Story US-004 - Automated Code Quality Checks
**Priority**: High
**Dependencies**: TODO-019 (HLS-002 generated)
**Estimated Time**: 25 minutes
**Status**: ✅ Completed (2025-10-14)
**Context**: New session recommended
**Generator Name**: backlog-story
**ID Assignment**: US-004 (next after US-003)

**Description**:
Generate detailed backlog story for Automated Code Quality Checks from HLS-002.

**Command**: `/generate TODO-024`

**Input Data:**
- HLS-002 v1 (CI/CD Pipeline Setup)
- Backlog Story 2: Implement Automated Code Quality Checks (~3 SP)

**Scope Guidance:**
- Configure Ruff linting and formatting validation
- Provide clear error reporting with line numbers
- Enforce project coding standards
- Integrate with CI/CD pipeline

**Completion Notes:**
- ✅ Generated US-004 v1 at /artifacts/backlog_stories/US-004_automated_code_quality_checks_v1.md
- ✅ All 27 validation criteria passed (Content Quality: 13/13, Upstream Traceability: 8/8, Consistency: 6/6)
- ⚠️ Parent PRD-000 v3 status is "Draft" (acceptable for PoC phase, may require rework if PRD changes)
- ✅ Status set to Draft, ready for Product Owner review

---

### TODO-025: Generate Backlog Story US-005 - Automated Type Safety Validation
**Priority**: High
**Dependencies**: TODO-019 (HLS-002 generated)
**Estimated Time**: 25 minutes
**Status**: ✅ Completed (2025-10-14)
**Context**: New session recommended
**Generator Name**: backlog-story
**ID Assignment**: US-005 (next after US-004)

**Description**:
Generate detailed backlog story for Automated Type Safety Validation from HLS-002.

**Command**: `/generate TODO-025`

**Input Data:**
- HLS-002 v1 (CI/CD Pipeline Setup)
- Backlog Story 3: Implement Automated Type Safety Validation (~3 SP)

**Scope Guidance:**
- Configure mypy type checking with strict mode enforcement
- Catch type errors before code review
- Integrate with CI/CD pipeline
- Provide actionable error messages

**Completion Notes:**
- ✅ Generated US-005 v1 at /artifacts/backlog_stories/US-005_automated_type_safety_validation_v1.md
- ✅ All 27 validation criteria passed (Content Quality: 13/13, Upstream Traceability: 8/8, Consistency: 6/6)
- ⚠️ Parent PRD-000 v3 status is "Draft" (acceptable for PoC phase, may require rework if PRD changes)
- ✅ Implementation Research referenced: §2.1 (Type Safety), §2.2 (FastAPI + Pydantic)
- ✅ CLAUDE.md standards referenced: CLAUDE-typing.md (Type hints), CLAUDE-tooling.md (MyPy config, Taskfile)
- ✅ 7 Gherkin acceptance criteria scenarios defined
- ✅ Story points: 3 SP (Medium complexity)
- ✅ Status set to Draft, ready for Product Owner review

---

### TODO-026: Generate Backlog Story US-006 - Test Execution and Coverage Reporting
**Priority**: High
**Dependencies**: TODO-019 (HLS-002 generated)
**Estimated Time**: 30 minutes
**Status**: ⏳ Pending
**Context**: New session recommended
**Generator Name**: backlog-story
**ID Assignment**: US-006 (next after US-005)

**Description**:
Generate detailed backlog story for Automated Test Execution and Coverage Reporting from HLS-002.

**Command**: `/generate TODO-026`

**Input Data:**
- HLS-002 v1 (CI/CD Pipeline Setup)
- Backlog Story 4: Implement Automated Test Execution and Coverage Reporting (~5 SP)

**Scope Guidance:**
- Configure pytest test suite execution
- Enforce >80% coverage threshold
- Generate detailed coverage reports
- Integrate with CI/CD pipeline

---

### TODO-027: Generate Backlog Story US-007 - Pre-commit Hooks Configuration
**Priority**: High
**Dependencies**: TODO-019 (HLS-002 generated)
**Estimated Time**: 20 minutes
**Status**: ⏳ Pending
**Context**: New session recommended
**Generator Name**: backlog-story
**ID Assignment**: US-007 (next after US-006)

**Description**:
Generate detailed backlog story for Pre-commit Hooks Configuration from HLS-002.

**Command**: `/generate TODO-027`

**Input Data:**
- HLS-002 v1 (CI/CD Pipeline Setup)
- Backlog Story 5: Configure Pre-commit Hooks for Local Validation (~2 SP)

**Scope Guidance:**
- Set up pre-commit hooks for local validation
- Run quality checks before commit
- Provide immediate feedback on quality issues
- Allow bypass with --no-verify for exceptional cases

---

### TODO-028: Generate Backlog Story US-008 - Automated Dependency Management
**Priority**: High
**Dependencies**: TODO-019 (HLS-002 generated)
**Estimated Time**: 25 minutes
**Status**: ⏳ Pending
**Context**: New session recommended
**Generator Name**: backlog-story
**ID Assignment**: US-008 (next after US-007)

**Description**:
Generate detailed backlog story for Automated Dependency Management from HLS-002.

**Command**: `/generate TODO-028`

**Input Data:**
- HLS-002 v1 (CI/CD Pipeline Setup)
- Backlog Story 6: Implement Automated Dependency Management (~3 SP)

**Scope Guidance:**
- Configure Renovate bot for dependency scanning
- Automate dependency update PRs
- Security vulnerability detection
- Batch minor updates, prioritize security updates

---

## Phase 1.6: Implementation - HLS-002 Stories

### TODO-029: Implement US-003 - CI/CD Pipeline Infrastructure
**Priority**: Critical
**Dependencies**: TODO-023 (US-003 generated)
**Estimated Time**: 4-6 hours (5 SP)
**Status**: ✅ Completed (2025-10-14)
**Context**: Current session OK
**Type**: Implementation

**Description**:
Implement CI/CD pipeline infrastructure for the AI Agent MCP Server project using GitHub Actions. Create workflow configuration, set up parallel validation jobs, configure caching strategy, and establish branch protection rules.

**User Story**: `/artifacts/backlog_stories/US-003_ci_cd_pipeline_infrastructure_v1.md`

**Implementation Tasks** (from US-003 Definition of Done):
1. Create `.github/workflows/ci.yml` workflow configuration file
2. Configure workflow triggers (feature branch pushes, PR events)
3. Implement setup job with dependency caching (UV cache, pytest cache, mypy cache)
4. Define job dependencies and parallel execution strategy
5. Configure branch protection rules on main branch via GitHub repository settings
6. Add build status badge to README.md
7. Test workflow with sample commit to feature branch
8. Validate concurrent build handling with multiple test commits
9. Verify cache effectiveness (second build should be significantly faster)
10. Document workflow architecture and job purpose in CONTRIBUTING.md

**Acceptance Criteria** (7 Gherkin scenarios in US-003):
- Scenario 1: Automatic pipeline trigger on feature branch commit (within 1 minute)
- Scenario 2: Pipeline execution completes within 5 minutes (p95 target)
- Scenario 3: Build status visibility on PR page
- Scenario 4: Main branch protection enforcement
- Scenario 5: Concurrent build handling (3+ simultaneous builds)
- Scenario 6: Pipeline failure provides actionable feedback
- Scenario 7: Dependency caching effectiveness (<30 seconds setup on cache hit)

**Technical References**:
- Implementation Research §2.8: UV package manager (fast dependency installation)
- CLAUDE-tooling.md: Taskfile commands (pipeline will invoke `task test`, `task lint`, `task type-check`)
- CLAUDE-testing.md: 80% coverage minimum
- CLAUDE-typing.md: Strict mypy mode

**Performance Targets**:
- Pipeline execution: <5 minutes (p95)
- Pipeline trigger: <1 minute after push
- Setup job with cache: <30 seconds
- Pipeline success rate: >95% on clean branches

**Validation**:
- [x] Workflow file created at `.github/workflows/ci.yml`
- [x] Pipeline triggers on feature branch push (configured)
- [x] Build status visible on PR page (report job configured)
- [ ] Main branch protected (requires GitHub repository setup)
- [ ] Pipeline completes within 5 minutes (requires testing on GitHub)
- [ ] Concurrent builds handled (requires testing on GitHub)
- [ ] Dependency caching working (requires testing on GitHub)
- [x] Documentation updated in CONTRIBUTING.md

**Completion Notes**:
- ✅ Created `.github/workflows/ci.yml` with complete 5-job pipeline (setup, lint-and-format, type-check, test-and-coverage, report)
- ✅ Configured workflow triggers: feature branches (feature/*, bugfix/*, chore/*) and PRs to main
- ✅ Implemented caching strategy for UV dependencies (~/.cache/uv), pytest cache (.pytest_cache), and mypy cache (.mypy_cache)
- ✅ Configured parallel validation jobs with proper dependencies
- ✅ Added build status badge to README.md (placeholder URLs - update when GitHub repo connected)
- ✅ Created comprehensive CONTRIBUTING.md with workflow architecture, development workflow, troubleshooting guide
- ✅ Committed changes to feature branch `feature/us-003-ci-cd-pipeline`
- ✅ YAML syntax validated by pre-commit hooks
- ⚠️ Branch protection rules require GitHub repository admin access (document configuration steps in CONTRIBUTING.md)
- ⚠️ Full pipeline testing requires pushing to GitHub remote (local repository only)

**Next Steps**:
- Connect repository to GitHub remote
- Configure branch protection rules via GitHub repository settings
- Push feature branch to test pipeline execution
- Validate performance targets (<5 min execution, <30s cache hit)
- Test concurrent build handling

**Notes**:
- No Tech Spec or Implementation Tasks needed (configuration work, clear scope)
- Implement directly from backlog story
- Subsequent stories (US-004, US-005, US-006) will add specific validation stages to this pipeline
- This story establishes the infrastructure; validation configs come in later stories

---

### TODO-030: Implement US-004 - Automated Code Quality Checks
**Priority**: High
**Dependencies**: TODO-024 (US-004 generated), TODO-029 (US-003 CI/CD pipeline infrastructure)
**Estimated Time**: 2-3 hours (3 SP)
**Status**: ✅ Completed (2025-10-14)
**Context**: Current session OK
**Type**: Implementation

**Description**:
Implement automated code quality checks with Ruff linting and formatting validation integrated into the CI/CD pipeline. Configure Ruff in pyproject.toml, add lint-and-format job to GitHub Actions workflow, and enforce project coding standards on every commit.

**User Story**: `/artifacts/backlog_stories/US-004_automated_code_quality_checks_v1.md`

**Implementation Tasks** (from US-004 Definition of Done):
1. Configure Ruff in pyproject.toml with project-specific rule set
   - Enable rules: E (pycodestyle errors), W (warnings), F (pyflakes), I (isort), B (bugbear), C4 (comprehensions), UP (pyupgrade), N (naming), S (security), T20 (print), SIM (simplify), ARG (unused args), PTH (pathlib), RUF (ruff-specific)
   - Configure per-file-ignores for tests/ directory
   - Set line length: 100, target version: py311
2. Update .github/workflows/ci.yml with lint-and-format job
   - Run `ruff check .` for linting (via `task lint`)
   - Run `ruff format --check .` for formatting validation (via `task format:check`)
   - Configure job to run in parallel with type-check job
   - Add dependency on setup job for cache restoration
3. Configure Ruff cache caching strategy (.ruff_cache)
4. Add local Taskfile commands: `task lint`, `task lint:fix`, `task format`, `task format:check`
5. Test linting job with intentional violations (unused import, formatting issue)
6. Verify error messages are actionable with file paths and line numbers
7. Validate GitHub Actions annotations display correctly on PR
8. Document code quality standards in CONTRIBUTING.md

**Acceptance Criteria** (7 Gherkin scenarios in US-004):
- Scenario 1: Linting executes on feature branch commit
- Scenario 2: Linting error fails build with actionable feedback
- Scenario 3: Valid code passes linting checks
- Scenario 4: Formatting validation detects unformatted code
- Scenario 5: Auto-fix mode available locally (`task lint:fix`)
- Scenario 6: Cache improves subsequent run performance
- Scenario 7: Local linting matches CI/CD behavior

**Technical References**:
- CLAUDE-tooling.md: Ruff configuration (lines 457-538), Taskfile commands (lines 59-77)
- Implementation Research §2.2: FastAPI development workflow
- US-004 v1: Complete acceptance criteria and technical specifications

**Performance Targets**:
- Lint job execution: <30 seconds for codebase <5,000 LOC
- Format check: <10 seconds
- Cache hit reduces runtime by >50%

**Validation**:
- [x] Ruff configured in pyproject.toml with project rule set (added N, S, T20, SIM, ARG, PTH, RUF)
- [x] lint-and-format job exists in .github/workflows/ci.yml (from US-003)
- [x] Ruff cache added to CI/CD workflow setup and lint-and-format jobs
- [x] Local Taskfile commands work: `task lint`, `task lint:fix`, `task format`, `task format:check`
- [x] Linting errors detected and reported with detailed messages
- [x] Error messages include file path, line number, rule ID, and suggested fixes
- [x] Test code has appropriate per-file-ignores (S101, ARG, T20)
- [x] Documentation updated in CONTRIBUTING.md with comprehensive Ruff guide
- [x] All acceptance criteria validated locally

**Completion Notes**:
- ✅ Extended Ruff configuration in pyproject.toml with 8 additional rule categories (N, S, T20, SIM, ARG, PTH, RUF)
- ✅ Added per-file-ignores for tests/ and scripts/ directories
- ✅ Configured Ruff cache (.ruff_cache) in both setup and lint-and-format jobs
- ✅ Updated Taskfile.yml to use `uv run` for all Ruff commands
- ✅ Fixed existing linting violations in codebase (import sorting, security warnings)
- ✅ Tested linting with intentional violations - verified comprehensive error reporting with:
  - Rule codes (F401, F841, N801, T201)
  - File paths and line numbers
  - Code snippets with visual indicators
  - Helpful suggestions and auto-fix availability
- ✅ Updated CONTRIBUTING.md with:
  - Complete Ruff rule category documentation
  - Command reference for all linting/formatting tasks
  - Error message format explanation
  - Common issues and troubleshooting guide
  - Per-file ignore documentation
  - Warning suppression examples
- ✅ All local validation passing: `task lint && task format:check` returns clean
- ⚠️ GitHub-dependent validations require remote repository:
  - Performance target validation (<30 seconds)
  - GitHub Actions annotations display
  - Branch protection rule configuration

**Next Steps**:
- Push to GitHub remote to test full CI/CD integration
- Configure branch protection rules to require lint-and-format status check
- Validate performance targets on GitHub Actions runners

**Notes**:
- Ruff replaces multiple tools: Black (formatter), isort (import sorting), Flake8 (linting)
- 10-100x faster than traditional Python linters
- lint-and-format job already existed from US-003, enhanced with Ruff cache and extended rule set

---

### TODO-031: Implement US-005 - Automated Type Safety Validation
**Priority**: High
**Dependencies**: TODO-025 (US-005 generated), TODO-029 (US-003 CI/CD pipeline infrastructure)
**Estimated Time**: 2-3 hours (3 SP)
**Status**: ✅ Completed (2025-10-14)
**Context**: Current session OK
**Type**: Implementation

**Description**:
Implement automated type safety validation with mypy strict mode integrated into the CI/CD pipeline. Configure mypy in pyproject.toml, add type-check job to GitHub Actions workflow, and enforce comprehensive type checking on all production code.

**User Story**: `/artifacts/backlog_stories/US-005_automated_type_safety_validation_v1.md`

**Implementation Tasks** (from US-005 Definition of Done):
1. Configure mypy in pyproject.toml with strict mode
   - Enable strict mode: disallow_untyped_defs, disallow_incomplete_defs, check_untyped_defs, disallow_untyped_decorators, no_implicit_optional, warn_redundant_casts, warn_unused_ignores, warn_no_return, warn_unreachable, strict_equality
   - Set Python version: 3.11
   - Configure test directory exemption: [[tool.mypy.overrides]] for tests.* (disallow_untyped_defs = false)
   - Configure third-party library overrides: ignore_missing_imports for libraries without type stubs
2. Update .github/workflows/ci.yml with type-check job
   - Run `mypy src/ --strict`
   - Configure job to run in parallel with lint-and-format job
   - Add dependency on setup job for cache restoration
   - Format output for GitHub Actions annotations
3. Configure mypy cache caching strategy (~/.mypy_cache)
4. Add local Taskfile commands: `task type-check`, `task type-check:report`, `task type-check:install`
5. Add type hints to existing code in src/ directory (if not already present)
6. Test type-check job with intentional type error (e.g., calling .upper() on int)
7. Verify error messages include file path, line number, and clear description
8. Validate test code remains exempt from strict type checking
9. Install missing type stubs: `mypy --install-types`
10. Document type checking standards in CONTRIBUTING.md

**Acceptance Criteria** (7 Gherkin scenarios in US-005):
- Scenario 1: Type checking executes on feature branch commit
- Scenario 2: Type error fails build with actionable feedback
- Scenario 3: Valid type annotations pass type checking
- Scenario 4: Test code exempt from strict type checking
- Scenario 5: Third-party libraries without stubs don't block build
- Scenario 6: Mypy cache improves subsequent run performance
- Scenario 7: Local type checking matches CI/CD behavior

**Technical References**:
- CLAUDE-tooling.md: MyPy configuration (lines 542-602), Taskfile commands (lines 79-89)
- CLAUDE-typing.md: Type hints philosophy, patterns, best practices (entire document)
- Implementation Research §2.1: Python 3.11+ type safety benefits
- US-005 v1: Complete acceptance criteria and technical specifications

**Performance Targets**:
- Type-check job execution: <30 seconds for codebase <10,000 LOC
- Cache hit reduces runtime to <15 seconds
- First run (cold cache): <60 seconds

**Validation**:
- [x] Mypy configured in pyproject.toml with strict mode enabled
- [x] Test directory exempt from strict checking via overrides
- [x] Third-party libraries configured (ignore_missing_imports = false by default)
- [x] type-check job exists in .github/workflows/ci.yml (from US-003)
- [x] Mypy cache cached in CI/CD workflow (from US-003)
- [x] Local Taskfile commands work: `task type-check`, `task type-check:report`, `task type-check:install`
- [x] Type errors detected and reported with actionable error messages
- [x] Error messages include file path, line number, error description, and error codes
- [x] All src/ code passes strict type checking (16 source files, 0 errors)
- [x] Test code exempt from strict checks (validated via overrides)
- [x] Documentation updated in CONTRIBUTING.md
- [x] All acceptance criteria validated locally

**Completion Notes**:
- ✅ MyPy already configured in pyproject.toml with comprehensive strict mode settings:
  - All strict checks enabled (disallow_untyped_defs, no_implicit_optional, etc.)
  - Python version 3.11
  - Test directory exempt via [[tool.mypy.overrides]]
- ✅ CI/CD integration already complete from US-003:
  - type-check job runs in parallel with lint-and-format
  - MyPy cache configured and cached
  - Job uses `task type-check` command
- ✅ Updated Taskfile.yml to use `uv run` for all MyPy commands (type-check, type-check:report, type-check:install)
- ✅ All existing code passes strict type checking:
  - 16 source files checked
  - 0 type errors found
  - Code already has proper type hints
- ✅ Tested type checking with intentional errors - verified comprehensive error reporting:
  - Error codes: no-any-return, attr-defined, assignment, return-value, no-untyped-def
  - Clear file paths and line numbers
  - Descriptive error messages
- ✅ Updated CONTRIBUTING.md with comprehensive type checking guide:
  - All strict mode checks explained
  - Type hint requirements and modern Python 3.11+ syntax
  - Command reference
  - Error message format explanation
  - Common type hints examples (functions, optionals, async, generics)
  - Troubleshooting guide with 6 common issues and fixes
  - Test code exemption explanation
- ✅ All local validation passing: `task type-check` returns "Success: no issues found"
- ⚠️ GitHub-dependent validations require remote repository:
  - Performance target validation (<30 seconds)
  - GitHub Actions annotations display
  - Branch protection rule configuration

**Next Steps**:
- Push to GitHub remote to test full CI/CD integration
- Configure branch protection rules to require type-check status check
- Validate performance targets on GitHub Actions runners

**Notes**:
- MyPy strict mode enforces comprehensive type safety across entire codebase
- Type hints serve dual purpose: static analysis + inline documentation
- All infrastructure already in place from US-003 - only needed Taskfile updates and documentation

---

## Task Status Legend

- ✅ Completed (archived in TODO-completed.md)
- ⏳ Pending
- 🔄 In Progress
- ⏸️ Blocked
- ⚠️ Issues Found

---

**Note:** 16 completed tasks archived to `/TODO-completed.md` on 2025-10-14
