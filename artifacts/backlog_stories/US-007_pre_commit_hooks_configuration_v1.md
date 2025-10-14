# User Story: Configure Pre-commit Hooks for Local Validation

## Metadata
- **Story ID:** US-007
- **Title:** Configure Pre-commit Hooks for Local Validation
- **Type:** Feature
- **Status:** Draft
- **Priority:** Medium (Improves developer experience and reduces CI/CD failures)
- **Parent PRD:** PRD-000
- **Parent High-Level Story:** HLS-002 (Automated Build Validation with CI/CD Pipeline)
- **Functional Requirements Covered:** FR-15
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** PRD-000: Project Foundation & Bootstrap Infrastructure
- **Link:** /artifacts/prds/PRD-000_project_foundation_bootstrap_v3.md
- **PRD Section:** Section 5.1 (Functional Requirements)
- **Functional Requirements Coverage:**
  - **FR-15:** Pre-commit hooks for automated code quality checks

**Parent High-Level Story:** HLS-002: Automated Build Validation with CI/CD Pipeline
- **Link:** /artifacts/hls/HLS-002_ci_cd_pipeline_setup_v1.md
- **HLS Section:** Decomposition Story 5 (Configure Pre-commit Hooks for Local Validation)

## User Story
As a software engineer contributing code to the AI Agent MCP Server project, I want pre-commit hooks to run quality checks locally before my commits are finalized, so that I catch code quality issues immediately while context is fresh and avoid wasting CI/CD build time on preventable failures.

## Description
This story implements pre-commit hooks that automatically execute on every local commit, running lightweight quality checks (linting, formatting, type checking) before the commit is finalized. The hooks provide immediate feedback within seconds, allowing developers to fix issues while code changes are still in working memory. This "shift-left" approach catches problems at the earliest possible stage, reducing CI/CD pipeline failures and accelerating the development feedback loop.

Pre-commit hooks complement the CI/CD pipeline (US-003) by providing a first line of defense locally. Developers receive instant feedback (<10 seconds) rather than waiting for CI/CD pipeline execution (minutes). This reduces the "commit → push → wait for CI → fix → repeat" cycle time significantly.

Hooks are configured to allow bypass via --no-verify flag for exceptional cases (e.g., work-in-progress commits, urgent hotfixes) while defaulting to mandatory enforcement.

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§2.1: Python 3.11+ Type Safety:** Pre-commit hooks run mypy type checking to catch type errors at development time
  - Early type error detection prevents runtime failures
- **§6.1: Slow Feedback Loops Anti-pattern:** Pre-commit hooks provide <10 second feedback vs. 5 minute CI/CD pipeline
  - Catches issues while developer context is fresh (code still in working memory)

**Anti-Patterns Avoided:**
- **§6.1: Slow Feedback Loops:** Pre-commit hooks eliminate waiting for CI/CD to discover fixable quality issues
  - Developer receives immediate actionable feedback before push
  - Reduces "commit → CI failure → context switch" cycle waste

**Performance Considerations:**
- Pre-commit hook execution target: <10 seconds for changed files only
- Hooks run only on staged files (not entire codebase) for fast feedback
- Heavy validation (full test suite) deferred to CI/CD pipeline

## Functional Requirements
- Pre-commit framework installed and configured in .pre-commit-config.yaml
- Ruff linting hook validates code style on staged Python files
- Ruff formatting hook checks code formatting on staged Python files
- MyPy type checking hook validates type hints on staged Python files
- Hooks run automatically on every git commit
- Hooks only check staged files (not entire codebase) for performance
- Clear error messages with file paths and line numbers when hooks fail
- Commit blocked if hooks fail (unless --no-verify flag used)
- Hooks can be manually run via `pre-commit run --all-files`
- Setup script installs pre-commit hooks automatically during environment setup

## Non-Functional Requirements
- **Performance:** Pre-commit hook execution <10 seconds for typical commit (1-10 changed files)
- **Developer Experience:** Error messages must be actionable with suggested fixes
- **Reliability:** Hooks run consistently across macOS, Linux, Windows WSL2
- **Flexibility:** Bypass mechanism (--no-verify) available for exceptional cases without removing enforcement
- **Maintainability:** Hook configuration synchronized with CI/CD pipeline checks

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** References specialized CLAUDE-tooling.md standards for pre-commit configuration. Story supplements with US-007-specific setup details.

### Implementation Guidance
Configure pre-commit framework in .pre-commit-config.yaml with hooks mirroring CI/CD pipeline checks (Ruff linting, Ruff formatting, MyPy type checking). Install hooks automatically during environment setup via Taskfile. Configure hooks to run only on staged files for fast feedback.

**References to Implementation Standards:**
- CLAUDE-tooling.md: Pre-commit hooks configuration (Ruff, MyPy integration), Taskfile commands (`task hooks:install`, `task hooks:run`)
- CLAUDE-testing.md: Testing strategy (pre-commit hooks run lightweight checks only; full test suite in CI/CD)
- CLAUDE-typing.md: MyPy strict mode enforcement in pre-commit hooks
- CLAUDE-architecture.md: .pre-commit-config.yaml location in repository root

**Note:** Treat CLAUDE.md content as authoritative - supplement with story-specific context, don't duplicate.

### Technical Tasks
1. Install pre-commit framework: `uv add --dev pre-commit`
2. Create .pre-commit-config.yaml configuration file
   - Add Ruff linting hook (mirrors `task lint` behavior)
   - Add Ruff formatting hook (mirrors `task format:check` behavior)
   - Add MyPy type checking hook (mirrors `task type-check` behavior on staged files only)
   - Configure hooks to run only on Python files (*.py)
   - Set fail_fast: false (run all hooks even if early hook fails)
3. Add Taskfile commands: `task hooks:install`, `task hooks:run`, `task hooks:update`
4. Update setup script (scripts/setup.nu) to run `pre-commit install` automatically
5. Configure pre-commit cache strategy (.cache/pre-commit)
6. Test hooks with intentional violations (linting error, formatting issue, type error)
7. Verify hooks block commit on failure
8. Verify hooks can be bypassed with `git commit --no-verify`
9. Verify hooks run only on staged files (not entire codebase)
10. Document pre-commit hooks usage in CONTRIBUTING.md

## Acceptance Criteria

**Format Guidance:** Gherkin format (Given-When-Then) for scenario-based validation

### Scenario 1: Hooks run automatically on every commit
**Given** pre-commit hooks are installed via `task hooks:install`
**When** a developer runs `git commit -m "message"`
**Then** pre-commit hooks execute automatically before commit is finalized
**And** hooks run Ruff linting, Ruff formatting, and MyPy type checking on staged files
**And** developer sees hook execution output in terminal

### Scenario 2: Linting violation blocks commit
**Given** staged code contains linting violations (unused import, unused variable)
**When** a developer attempts to commit
**Then** Ruff linting hook fails with clear error message
**And** error message includes file path, line number, and rule ID
**And** commit is blocked until violation is fixed
**And** developer can run `task lint:fix` to auto-fix issues

### Scenario 3: Formatting violation blocks commit
**Given** staged code contains formatting violations (inconsistent indentation, missing trailing newline)
**When** a developer attempts to commit
**Then** Ruff formatting hook fails with clear error message
**And** error message indicates which files need formatting
**And** commit is blocked until formatting is applied
**And** developer can run `task format` to auto-fix formatting

### Scenario 4: Type checking violation blocks commit
**Given** staged code contains type errors (missing type hints, type mismatches)
**When** a developer attempts to commit
**Then** MyPy hook fails with clear error message
**And** error message includes file path, line number, and type error description
**And** commit is blocked until type errors are resolved

### Scenario 5: Clean code allows commit
**Given** staged code passes all quality checks (linting, formatting, type checking)
**When** a developer runs `git commit -m "message"`
**Then** all pre-commit hooks pass
**And** commit is finalized successfully
**And** hook execution time is <10 seconds

### Scenario 6: Hooks can be bypassed for exceptional cases
**Given** a developer needs to commit work-in-progress code with known quality issues
**When** they run `git commit --no-verify -m "WIP: message"`
**Then** pre-commit hooks are skipped
**And** commit is finalized without running quality checks
**And** developer is responsible for fixing issues before PR

### Scenario 7: Hooks run only on staged files for performance
**Given** repository contains 100+ Python files
**When** a developer commits changes to 3 files
**Then** pre-commit hooks run only on those 3 staged files
**And** hooks do not check the entire codebase
**And** execution time remains <10 seconds

### Scenario 8: Manual hook execution for all files
**Given** a developer wants to validate entire codebase locally
**When** they run `task hooks:run` (executes `pre-commit run --all-files`)
**Then** hooks execute on all Python files in repository
**And** results show which files pass/fail quality checks
**And** developer can fix issues before pushing

## Definition of Done
- [ ] Pre-commit framework installed via uv (--dev dependency)
- [ ] .pre-commit-config.yaml configured with Ruff linting, Ruff formatting, MyPy hooks
- [ ] Hooks run only on Python files (*.py)
- [ ] Hooks run only on staged files by default (not entire codebase)
- [ ] Taskfile commands work: `task hooks:install`, `task hooks:run`, `task hooks:update`
- [ ] Setup script runs `pre-commit install` automatically
- [ ] Pre-commit cache configured (.cache/pre-commit)
- [ ] Hooks block commit on linting violations with clear error messages
- [ ] Hooks block commit on formatting violations with clear error messages
- [ ] Hooks block commit on type checking violations with clear error messages
- [ ] Clean code passes all hooks and commits successfully
- [ ] Hooks can be bypassed via `git commit --no-verify`
- [ ] Hook execution time <10 seconds for typical commit (1-10 changed files)
- [ ] Documentation updated in CONTRIBUTING.md with pre-commit hooks usage

## Additional Information
**Suggested Labels:** developer-experience, quality, tooling, local-validation
**Estimated Story Points:** 2 SP (Low complexity - straightforward configuration)
**Dependencies:**
- US-004 (Automated Code Quality Checks) - Ruff configuration must exist first
- US-005 (Automated Type Safety Validation) - MyPy configuration must exist first
- CLAUDE-tooling.md - Pre-commit hooks and Taskfile standards

**Related PRD Section:** /artifacts/prds/PRD-000_project_foundation_bootstrap_v3.md Section 5.1 (FR-15)

## Open Questions & Implementation Uncertainties

**Note:** No open implementation questions at this time. Pre-commit framework is well-established standard with clear configuration patterns. Hooks mirror CI/CD pipeline checks (Ruff, MyPy) from US-004 and US-005.

**Resolved during planning:**
- ~~"Should hooks run entire test suite?"~~ → No, only lightweight checks (linting, formatting, type checking). Full tests run in CI/CD (too slow for pre-commit)
- ~~"Should hooks be optional or mandatory?"~~ → Mandatory by default, bypassable via --no-verify (per PRD-000 Decision D3)
- ~~"Should hooks check entire codebase or only staged files?"~~ → Only staged files for performance (<10 second target)
- ~~"Which quality checks should run in hooks?"~~ → Ruff linting + formatting + MyPy (mirrors CI/CD pipeline checks)

---
