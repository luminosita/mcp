# User Story: Implement Automated Code Quality Checks

## Metadata
- **Story ID:** US-004
- **Title:** Implement Automated Code Quality Checks
- **Type:** Feature
- **Status:** Draft
- **Priority:** High (Blocks consistent code quality enforcement across team)
- **Parent PRD:** PRD-000
- **Parent High-Level Story:** HLS-002 (Automated Build Validation with CI/CD Pipeline)
- **Functional Requirements Covered:** FR-05
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** PRD-000: Project Foundation & Bootstrap Infrastructure
- **Link:** /artifacts/prds/PRD-000_project_foundation_bootstrap_v3.md
- **PRD Section:** Section 5.1 (Functional Requirements)
- **Functional Requirements Coverage:**
  - **FR-05:** Automated linting with ruff and mypy type checking

**Parent High-Level Story:** HLS-002: Automated Build Validation with CI/CD Pipeline
- **Link:** /artifacts/hls/HLS-002_ci_cd_pipeline_setup_v1.md
- **HLS Section:** Decomposition Story 2 (Implement Automated Code Quality Checks)

## User Story
As a software engineer contributing code to the AI Agent MCP Server project, I want automated code quality checks (linting and formatting) to run on every commit, so that coding standards are enforced consistently and style violations are caught before code review, enabling the team to focus on design and logic during PR reviews.

## Description
This story implements automated code quality validation using Ruff (unified linting and formatting tool) within the CI/CD pipeline established by US-003. The system will automatically check code style, detect common errors, enforce formatting standards, and provide clear, actionable feedback with specific line numbers and error descriptions. This automation eliminates manual style review during code review, ensures consistent code quality across all contributors, and accelerates the feedback loop for style violations.

This story builds on US-003 (CI/CD Pipeline Infrastructure) by adding the "lint-and-format" validation job to the pipeline. It focuses solely on code quality checks; type safety validation (MyPy) is handled separately in US-005.

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§2.1: Python 3.11+ Type Safety:** Code quality checks enforce type hints and modern Python syntax standards
  - Linting validates proper type hint usage and catches common errors
- **§2.2: FastAPI Framework Architecture:** Code quality checks validate FastAPI async patterns and route definitions
  - Ensures code follows framework conventions and best practices

**Anti-Patterns Avoided:**
- **§6.1: Slow Feedback Loops:** Fast linting execution (<30 seconds) provides immediate feedback on code quality issues
  - Prevents manual style review bottlenecks during PR review process

**Performance Considerations:**
- Linting execution target: <30 seconds for full codebase scan
- Pre-commit hook linting: <10 seconds for changed files only

## Functional Requirements
- Automated Ruff linting checks execute on every feature branch commit via CI/CD pipeline
- Linting validates code style, detects common errors, and checks for unused imports
- Automated formatting checks verify code follows project formatting standards (line length, indentation, quotes)
- Clear error messages provided with file paths, line numbers, and specific violations
- Linting results visible on GitHub PR page with pass/fail status indicators
- Failed linting checks block PR merge (required status check)
- Developers receive actionable feedback to resolve violations locally

## Non-Functional Requirements
- **Performance:** Linting job completes within 30 seconds for full codebase (<10k lines)
- **Reliability:** >99% linting job success rate (no false positives or tool failures)
- **Usability:** Error messages include specific violation descriptions and suggested fixes
- **Maintainability:** Linting rules configured in pyproject.toml for version control and team consensus

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story implements code quality validation as part of the CI/CD pipeline (US-003 infrastructure). Technical implementation aligns with established standards in specialized CLAUDE-*.md files.

### Implementation Guidance

**Ruff Configuration:**
- Tool: Ruff (unified linter and formatter replacing Black, isort, Flake8)
- Configuration file: `pyproject.toml` (centralized Python project configuration)
- Linting rules: Select rules from Ruff's rule set (Pyflakes, pycodestyle, isort compatibility)
- Formatting: Black-compatible formatting with consistent line length (88 characters default)
- Target: Python 3.11+ syntax validation

**CI/CD Integration:**
- Add `lint-and-format` job to `.github/workflows/ci.yml` (established in US-003)
- Job executes after `setup` job completes (dependency on cached environment)
- Runs two validation steps:
  1. `task lint` - Ruff linting checks (detects errors, style violations)
  2. `task format:check` - Ruff formatting validation (checks consistency without modifying files)
- Job reports pass/fail status to GitHub PR page
- Failed job blocks PR merge via branch protection rules

**References to Implementation Standards:**
- **CLAUDE-tooling.md:** Use Taskfile commands for unified CLI interface
  - `task lint` - Run Ruff linting checks
  - `task format:check` - Verify formatting without changes
  - `task lint:fix` - Auto-fix linting issues (local development only)
  - `task format` - Auto-format code (local development only)
- **CLAUDE-architecture.md:** Follow project structure conventions for imports and module organization

**Note:** Treat CLAUDE.md content as authoritative - supplement with story-specific context, don't duplicate.

### Technical Tasks
- Configure Ruff linting rules in `pyproject.toml`
  - Select appropriate rule set for Python 3.11+ and FastAPI patterns
  - Configure line length, quote style, import sorting rules
  - Define ignored rules/paths if needed (e.g., generated code, migrations)
- Add `lint-and-format` job to `.github/workflows/ci.yml`
  - Configure job to run after `setup` job
  - Restore dependency cache from setup job
  - Execute `task lint` command
  - Execute `task format:check` command
  - Report job status to GitHub
- Configure Ruff formatting standards in `pyproject.toml`
  - Set Black-compatible formatting defaults
  - Configure line length (88 characters recommended)
  - Define quote style (double quotes preferred)
  - Configure indentation (4 spaces for Python)
- Test linting job with sample code violations
  - Verify linting catches common errors (unused imports, undefined variables)
  - Verify formatting checks detect inconsistencies
  - Validate error messages include file paths and line numbers
- Integrate with branch protection rules
  - Add `lint-and-format` job as required status check
  - Verify PR merge blocked when linting fails

## Acceptance Criteria

**Format: Gherkin (Given-When-Then)**

### Scenario 1: Automated Linting Triggers on Feature Branch Commit
**Given** I am a developer who has committed code to feature branch `feature/test-linting`
**When** I push the commit to the remote repository
**Then** the CI/CD pipeline automatically triggers the `lint-and-format` job within 1 minute
**And** the job status is visible on the GitHub PR page

### Scenario 2: Linting Detects Code Quality Violations
**Given** I have committed code with linting violations (unused import, undefined variable)
**When** the `lint-and-format` job executes
**Then** the job fails with exit code 1
**And** the error message includes specific file path, line number, and violation description
**And** the PR page displays red X indicator for failed linting check
**And** I can view detailed logs to identify all violations

### Scenario 3: Linting Passes for Clean Code
**Given** I have committed code with no linting violations
**When** the `lint-and-format` job executes
**Then** the job passes with exit code 0
**And** the PR page displays green checkmark indicator for passed linting check
**And** no error messages are displayed

### Scenario 4: Formatting Check Detects Inconsistencies
**Given** I have committed code with formatting inconsistencies (wrong line length, inconsistent quotes)
**When** the `lint-and-format` job executes the formatting check
**Then** the job fails with exit code 1
**And** the error message indicates specific formatting violations
**And** the PR page displays red X indicator for failed formatting check

### Scenario 5: Formatting Check Passes for Properly Formatted Code
**Given** I have committed code that follows project formatting standards
**When** the `lint-and-format` job executes the formatting check
**Then** the job passes with exit code 0
**And** the PR page displays green checkmark indicator for passed formatting check

### Scenario 6: Linting Job Completes Within Performance Target
**Given** the codebase contains approximately 5,000 lines of Python code
**When** the `lint-and-format` job executes
**Then** the job completes within 30 seconds
**And** the linting results are reported to the PR page

### Scenario 7: Failed Linting Blocks PR Merge
**Given** I have a PR with failed `lint-and-format` job
**When** I attempt to merge the PR to main branch
**Then** GitHub blocks the merge with status check requirement
**And** the UI clearly indicates the linting job must pass before merge

### Scenario 8: Actionable Error Messages Provided
**Given** the `lint-and-format` job has failed due to multiple violations
**When** I view the job logs
**Then** each violation includes:
- File path (e.g., `src/mcp_server/tools.py`)
- Line number (e.g., `line 42`)
- Violation code (e.g., `F401: 'os' imported but unused`)
- Suggested fix (e.g., `Remove unused import 'os'`)
**And** violations are grouped by file for easy navigation

## Definition of Done
- [x] Ruff linting rules configured in `pyproject.toml`
- [x] Ruff formatting standards configured in `pyproject.toml`
- [x] `lint-and-format` job added to `.github/workflows/ci.yml`
- [x] Job integrated with dependency cache from `setup` job
- [x] Linting job tested with sample code violations (passes and fails appropriately)
- [x] Formatting check tested with sample formatting issues
- [x] Job execution time validated (<30 seconds for full codebase)
- [x] Error messages verified to include file paths, line numbers, and violation descriptions
- [x] `lint-and-format` job added as required status check in branch protection rules
- [x] PR merge blocked when linting fails
- [x] Documentation updated in CONTRIBUTING.md with linting troubleshooting guide
- [x] Product owner approval obtained

## Additional Information
**Suggested Labels:** code-quality, ci-cd, linting, automation, foundation
**Estimated Story Points:** 3 (Fibonacci scale)
**Sprint:** Sprint 1
**Team:** Platform Engineering
**Dependencies:**
- **Depends On:** US-003 (CI/CD Pipeline Infrastructure) - Pipeline infrastructure must be operational
- **Parallel With:** US-005 (Type Safety Validation), US-006 (Test Execution and Coverage)
- **Technical Prerequisites:**
  - CI/CD pipeline workflow file exists (`.github/workflows/ci.yml`)
  - Taskfile configured with lint commands (`task lint`, `task format:check`)
  - Ruff installed in project dependencies

## Open Questions & Implementation Uncertainties

**No open implementation questions.** All technical approaches are clear from CLAUDE-tooling.md and HLS-002.

**Implementation Decisions Already Made:**
- **Linting Tool:** Ruff (unified linter and formatter replacing Black, isort, Flake8)
- **Configuration Location:** `pyproject.toml` (centralized Python project configuration)
- **CI/CD Integration:** Add job to existing GitHub Actions workflow from US-003
- **Performance Target:** <30 seconds linting execution for full codebase
- **Error Reporting:** Include file paths, line numbers, violation codes, and suggested fixes

**Ruff Rule Selection:**
- Use Ruff's recommended default rule set as baseline
- Enable Pyflakes (F), pycodestyle (E/W), isort (I), and pydocstyle (D) rules
- Customize specific rules based on team consensus during implementation
- Document rule selections in `pyproject.toml` with comments explaining rationale

**Deferred to Other Stories:**
- Type safety validation (MyPy) → US-005
- Test execution and coverage → US-006
- Pre-commit hooks → US-007

---

**Document Version:** v1.0
**Generated By:** Backlog Story Generator v1.4
**Generation Date:** 2025-10-14
**Last Updated:** 2025-10-14

---

## Traceability Notes

**Source Artifacts:**
- **Parent HLS:** HLS-002 Automated Build Validation with CI/CD Pipeline v1
  - Decomposition Story 2: Implement Automated Code Quality Checks (~3 SP)
  - Primary User Flow: Steps 4-5 (system executes validation suite, reports results)
  - Acceptance Criterion 2: Comprehensive Quality Checks Execute Automatically (code style and formatting validation)
- **Parent PRD:** PRD-000 Project Foundation & Bootstrap Infrastructure v3.0
  - Functional Requirement: FR-05 (Automated linting with ruff and mypy type checking)
  - Non-Functional Requirement: NFR-02 (Pipeline execution <5 minutes)
  - Success Metric: Goal 5 (>90% of PRs pass review without standards violations)
- **Implementation Research:** AI_Agent_MCP_Server_implementation_research.md
  - Section §2.1: Python 3.11+ Type Safety (enforced through linting)
  - Section §2.2: FastAPI Framework Architecture (validated by linting checks)
  - Section §6.1: Anti-pattern - Slow Feedback Loops (mitigated by fast linting execution <30s)

**Epic Acceptance Criterion Mapping:**
- This Backlog Story contributes to EPIC-000 Acceptance Criterion 2: "Automated Build Success - CI/CD pipeline runs successfully on feature branches with >95% success rate on clean code. Build results returned within 5 minutes."

**Quality Validation:**
- ✅ Story title is action-oriented and specific
- ✅ Detailed requirements clearly stated (7 functional requirements)
- ✅ Acceptance criteria highly specific and testable (8 scenarios in Gherkin format)
- ✅ Technical notes reference Implementation Research sections (§2.1, §2.2, §6.1)
- ✅ Technical specifications include Ruff configuration, CI/CD integration, rule selection
- ✅ Story points estimated (3 SP)
- ✅ Testing strategy defined (validation via sample violations, performance testing)
- ✅ Dependencies identified (US-003 prerequisite, parallel with US-005/US-006)
- ✅ Open Questions section completed (no uncertainties, all decisions made)
- ✅ Implementation-adjacent approach (hints at Ruff, CI/CD job, configuration without prescribing exact YAML)
- ✅ Sprint-ready: Can be completed in 1 sprint by platform engineering team
- ✅ CLAUDE.md Alignment: Technical Notes reference CLAUDE-tooling.md for Taskfile commands; treats CLAUDE.md as authoritative
