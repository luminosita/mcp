# Implementation Task: Implement Prerequisites Checking Module

## Metadata
- **Task ID:** TASK-002
- **Parent Story ID:** US-001
- **Status:** To Do
- **Priority:** Critical
- **Assigned To:** [Unassigned]
- **Sprint:** Sprint 1
- **Domain:** DevOps/Infrastructure
- **Estimated Hours:** 4 hours
- **Related Tech Spec:** SPEC-001 (Phase 1: Core Infrastructure)
- **Version:** v2
- **Change Summary:** Incorporated SPEC-001 v1 feedback decisions (D1: explicit exports, D4: fail-fast clarification, D3: gum for terminal UX)

## Decisions Incorporated from SPEC-001 v1 Feedback

**D1 - NuShell Module Import Strategy:**
- Use `use lib/module.nu` with explicit exports (NOT `source`)
- Provides better maintainability and clear module boundaries
- **Impact:** All modules must use `export def` for public functions

**D3 - Progress Indicator Implementation:**
- Use gum (https://github.com/charmbracelet/gum) for terminal UX/UI
- **Impact:** Error display via gum (handled in main setup.nu, not this module)

**D4 - Validation Failure Handling:**
- Fail-fast on validation failures (setup script fails immediately if prerequisites check returns errors)
- **Impact:** Module returns complete validation report; setup script exits immediately if any errors found
- **Clarification:** Module still checks ALL prerequisites and returns complete report for best user experience (user sees all missing items at once), but setup script will not proceed if any failures detected

## Task Description

**Objective:**
Implement the `prerequisites.nu` module that validates the presence and versions of required tools (Python 3.11+, Podman, Git) within the Devbox environment, returning a structured report of validation results with actionable error messages. Module must use explicit exports per Decision D1. Setup script will fail-fast if this module reports any errors (per Decision D4).

**Technical Context:**
Per US-001 Scenario 5, the setup script must detect missing prerequisites and provide clear error messages with installation instructions. This module provides early validation before attempting installation steps, preventing confusing mid-setup failures. Per SPEC-001 §2.2, this module is called after OS detection and before any installation logic. Per Decision D4, if this check fails, setup script terminates immediately with error report.

**Architecture Decision:**
Per SPEC-001 v1 Decision D1, all NuShell modules use `use` with explicit exports (NOT `source`).

## Technical Specifications

### Implementation Approach
1. Implement `check_prerequisites` function in `prerequisites.nu` with explicit export
2. Check each prerequisite (Python, Podman, Git) using `which` command
3. Validate version requirements using version comparison logic
4. Return structured record with validation results and error messages (check ALL prerequisites for complete user feedback)
5. Setup script will fail-fast if errors found (caller's responsibility, not this module's)
6. Write unit tests with mocked commands

### Code Changes Required

**New Files to Create:**
- `scripts/lib/prerequisites.nu` - Prerequisites validation module (explicit exports per D1)
- `tests/unit/test_prerequisites.nu` - Unit tests for validation logic

### Technical Details

#### DevOps/Infrastructure Task
- **Module:** prerequisites.nu
- **Public Functions:** `check_prerequisites() -> record`
- **Export Pattern:** Explicit exports using `export def` (per D1)
- **Import Pattern:** Main script will use `use scripts/lib/prerequisites.nu check_prerequisites`
- **Validation Logic:**
  - Python: `python --version` >= 3.11 (parse "Python 3.11.5" format)
  - Podman: `podman --version` (any version acceptable)
  - Git: `git --version` (any version acceptable)
- **Error Handling:** Collect all failures, return complete report (provides best UX - user sees all missing items)
- **Fail-Fast Integration:** Setup script (caller) will check if errors exist and exit immediately (per D4)

## Acceptance Criteria (Task Level)

- [ ] `scripts/lib/prerequisites.nu` module implemented with **explicitly exported** `check_prerequisites` function
- [ ] Module uses `export def` (NOT plain `def`) per Decision D1
- [ ] Function validates Python 3.11+ availability and version
- [ ] Function validates Podman availability
- [ ] Function validates Git availability
- [ ] Returns structured record with validation results
- [ ] Error messages include Devbox configuration guidance (e.g., "Add python311 to devbox.json")
- [ ] Module checks ALL prerequisites before returning (complete report for user)
- [ ] Unit tests pass with mocked commands (simulate missing/present tools)
- [ ] Unit tests demonstrate proper `use` import pattern
- [ ] Code handles edge cases (command not found, version parsing failures)

## Implementation Guidance

### Code Example / Pseudo-code

```nushell
# scripts/lib/prerequisites.nu
# NuShell module for prerequisite validation with explicit exports (per SPEC-001 D1)

# Check if all prerequisites are available and meet version requirements
# Returns structured record with validation results and errors
# NOTE: Checks ALL prerequisites before returning (complete report)
# Setup script will fail-fast if errors exist (per SPEC-001 D4)
export def check_prerequisites [] -> record {
    mut errors = []

    # Check Python 3.11+
    let python_check = check_python
    let python_ok = $python_check.ok
    let python_version = $python_check.version

    if not $python_ok {
        $errors = ($errors | append $python_check.error)
    }

    # Check Podman
    let podman_ok = (which podman | length) > 0
    if not $podman_ok {
        $errors = ($errors | append "Podman not found. Add 'podman' to devbox.json packages.")
    }

    # Check Git
    let git_ok = (which git | length) > 0
    if not $git_ok {
        $errors = ($errors | append "Git not found. Add 'git' to devbox.json packages.")
    }

    return {
        python: $python_ok,
        python_version: $python_version,
        podman: $podman_ok,
        git: $git_ok,
        errors: $errors
    }
}

# Check Python version (3.11+)
# Helper function (not exported - private to module)
def check_python [] -> record {
    let python_path = (which python | get path.0?)

    if ($python_path | is-empty) {
        return {ok: false, version: "", error: "Python not found. Add 'python311' to devbox.json packages."}
    }

    let version_output = (python --version | complete)

    if $version_output.exit_code != 0 {
        return {ok: false, version: "", error: "Python version check failed"}
    }

    # Parse version (format: "Python 3.11.5")
    let version_str = ($version_output.stdout | str trim | split row " " | get 1)
    let version_parts = ($version_str | split row ".")
    let major = ($version_parts | get 0 | into int)
    let minor = ($version_parts | get 1 | into int)

    if $major < 3 or ($major == 3 and $minor < 11) {
        return {
            ok: false,
            version: $version_str,
            error: $"Python ($version_str) is too old. Python 3.11+ required. Update devbox.json to use python311."
        }
    }

    return {ok: true, version: $version_str, error: ""}
}
```

### Usage Example (for documentation)

```nushell
# Import module using `use` with explicit function import (per D1)
use scripts/lib/prerequisites.nu check_prerequisites

# Call function
let prereq_result = (check_prerequisites)

# Setup script will fail-fast if errors found (per D4)
if ($prereq_result.errors | length) > 0 {
    # Display errors using gum (per D3)
    gum style --foreground 196 "Prerequisites check failed:"
    $prereq_result.errors | each { |err| gum style --foreground 196 $"  - ($err)" }
    exit 1  # Fail-fast
}

# Continue with setup if no errors
print "All prerequisites satisfied. Continuing setup..."
```

### Unit Tests Example

```nushell
# tests/unit/test_prerequisites.nu
use std assert
use scripts/lib/prerequisites.nu check_prerequisites  # Explicit import per D1

# Test: All prerequisites present
def test_all_prerequisites_present [] {
    # In real test, would mock `which` and version commands
    let result = (check_prerequisites)

    assert ($result.python == true)
    assert ($result.podman == true)
    assert ($result.git == true)
    assert (($result.errors | length) == 0)
}

# Test: Verify module returns complete report (checks all prerequisites)
def test_complete_report_multiple_failures [] {
    # Mock scenario: Python and Git missing
    # Verify function checks ALL prerequisites before returning
    # let result = check_prerequisites with mocked environment

    # assert ($result.python == false)
    # assert ($result.git == false)
    # assert ($result.podman == true)
    # assert (($result.errors | length) == 2)  # Both errors collected
}

# Run tests
test_all_prerequisites_present
```

### Reference Implementation
- Version parsing pattern from Taskfile version checks
- Error message format consistent with US-001 Scenario 5 requirements
- gum integration example: https://github.com/charmbracelet/gum

### Implementation Research Reference
- **Primary Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md
- **§2.1 - Python 3.11+ Technology Stack:** Validates Python 3.11+ availability before setup proceeds
- **§8.2 - Anti-Pattern: Poor Error Handling:** Provide actionable error messages with Devbox configuration guidance

## Dependencies

### Technical Dependencies
- NuShell `which` command
- Python, Podman, Git (for testing)
- gum (for setup script error display - not this module's dependency)

### Task Dependencies
- **Blocked By:** TASK-034 (OS detection module provides context for error messages)
- **Blocks:** TASK-036 (Taskfile installation requires prerequisites to be validated first)

### Environment Requirements
- Devbox shell environment active

## Estimation

- **Estimated Hours:** 4 hours
- **Complexity:** Low-Medium
- **Uncertainty Level:** Low

**Complexity Factors:**
- Version parsing logic (medium - handle multiple version formats)
- Error message clarity (low - straightforward)
- Unit test mocking (low - NuShell provides test utilities)
- Module export pattern enforcement (low - simple syntax change)

## Testing Requirements

### Unit Tests
- [ ] Test all prerequisites present (Python 3.11+, Podman, Git)
- [ ] Test Python missing
- [ ] Test Python too old (< 3.11)
- [ ] Test Podman missing
- [ ] Test Git missing
- [ ] Test version parsing edge cases (malformed version strings)
- [ ] Test complete report generation (multiple failures collected)
- [ ] Test module import using `use` pattern (verify explicit export works)

### Manual Testing Steps
1. Run `devbox shell` with all tools installed
2. Test explicit import: `use scripts/lib/prerequisites.nu check_prerequisites`
3. Execute function: `let result = (check_prerequisites); print $result`
4. Verify all checks pass
5. Remove Python from devbox.json, restart shell
6. Execute check again, verify error message includes Devbox guidance
7. Test fail-fast integration in main setup script

## Non-Functional Requirements

### Performance
- Prerequisite checks must complete in <2 seconds

### Security
- No security concerns (read-only validation)

### Observability
- Log validation results for debugging
- Error messages displayed via gum in setup script (per D3)

## Risk & Complexity Notes

**Technical Risks:**
- Python version string format may vary (Python 3.11.5+ vs 3.11.5rc1)
- Different Python distributions may report versions differently
- Module import failures if `export def` not used correctly

**Mitigation Strategies:**
- Robust version parsing with regex fallback
- Test with multiple Python installations (CPython, PyPy if relevant)
- Include import examples in module header comments
- Validate explicit exports with unit tests

**Task-Level Uncertainties & Blockers:**

No task-level uncertainties. Implementation approach clear from Tech Spec SPEC-001 §2.2 (prerequisites.nu module interface) and SPEC-001 v2 Decisions D1 (explicit exports) and D4 (fail-fast behavior).

## Definition of Done (Task Level)

- [ ] Implementation complete and functionally correct
- [ ] Code follows NuShell coding standards
- [ ] Module uses explicit exports (`export def`) per Decision D1
- [ ] All unit tests written and passing
- [ ] Unit tests demonstrate `use` import pattern
- [ ] Code reviewed and approved by 1 reviewer
- [ ] No NuShell analyzer warnings
- [ ] Inline comments added explaining version parsing logic
- [ ] Module header includes usage example with `use` import and fail-fast integration
- [ ] Merged to main branch
- [ ] Task status updated to Done

## Code Review Checklist

**For Reviewer:**
- [ ] Version parsing handles edge cases (rc versions, patch versions)
- [ ] Error messages are actionable and include Devbox guidance
- [ ] Logic collects all errors (provides complete report to user)
- [ ] Unit tests cover all validation scenarios
- [ ] Code is readable with clear variable names
- [ ] Structured data returned correctly
- [ ] **Module uses `export def` (NOT plain `def`) per Decision D1**
- [ ] **Unit tests demonstrate correct `use` import pattern**
- [ ] **Module header documents fail-fast integration (per D4)**
- [ ] Helper functions (check_python) are NOT exported (private to module)

## Related Links
- **Parent Story:** /artifacts/backlog_stories/US-001_automated_setup_script_v2.md (Scenario 5)
- **Tech Spec:** /artifacts/tech_specs/SPEC-001_automated_setup_script_v1.md (§2.2 - prerequisites.nu)
- **Tech Spec Feedback:** /feedback/SPEC-001_v1_comments.md (Decisions D1, D3, D4)
- **Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Notes & Comments

**Implementation Notes:**
- Use `complete` command for version checks to capture exit codes and stderr
- Collect all validation failures to provide complete picture to user (better UX than failing on first error)
- Include Devbox configuration guidance in error messages (per US-001 requirements)
- **CRITICAL:** Public function uses `export def`, helper functions use plain `def` (private)
- Include usage example in module header comments showing fail-fast integration
- Setup script (not this module) handles fail-fast exit on validation failure (per D4)

**Changes from v1:**
- Added explicit reference to Decision D1 (use `use` with explicit exports)
- Added explicit reference to Decision D3 (gum for terminal UX)
- Added explicit reference to Decision D4 (fail-fast behavior) with clarification on module vs. script responsibility
- Updated code examples to emphasize `export def` usage for public function
- Added usage example demonstrating `use` import pattern and fail-fast integration
- Enhanced acceptance criteria to verify explicit export pattern
- Updated code review checklist to enforce explicit exports and fail-fast documentation
- Added testing requirement for verifying `use` import pattern
- Clarified that helper functions (check_python) should NOT be exported
- Added note that module collects all errors (complete report) but setup script fails fast

**Blockers/Issues Encountered:**
[To be filled during implementation if issues arise]
