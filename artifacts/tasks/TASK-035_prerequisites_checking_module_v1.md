# Implementation Task: Implement Prerequisites Checking Module

## Metadata
- **Task ID:** TASK-035
- **Parent Story ID:** US-001
- **Status:** To Do
- **Priority:** Critical
- **Assigned To:** [Unassigned]
- **Sprint:** Sprint 1
- **Domain:** DevOps/Infrastructure
- **Estimated Hours:** 4 hours
- **Related Tech Spec:** SPEC-001 (Phase 1: Core Infrastructure)

## Task Description

**Objective:**
Implement the `prerequisites.nu` module that validates the presence and versions of required tools (Python 3.11+, Podman, Git) within the Devbox environment, returning a structured report of validation results with actionable error messages.

**Technical Context:**
Per US-001 Scenario 5, the setup script must detect missing prerequisites and provide clear error messages with installation instructions. This module provides early validation before attempting installation steps, preventing confusing mid-setup failures. Per SPEC-001 §2.2, this module is called after OS detection and before any installation logic.

## Technical Specifications

### Implementation Approach
1. Implement `check_prerequisites` function in `prerequisites.nu`
2. Check each prerequisite (Python, Podman, Git) using `which` command
3. Validate version requirements using version comparison logic
4. Return structured record with validation results and error messages
5. Write unit tests with mocked commands

### Code Changes Required

**New Files to Create:**
- `scripts/lib/prerequisites.nu` - Prerequisites validation module
- `tests/unit/test_prerequisites.nu` - Unit tests for validation logic

###Technical Details

#### DevOps/Infrastructure Task
- **Module:** prerequisites.nu
- **Public Functions:** `check_prerequisites() -> record`
- **Validation Logic:**
  - Python: `python --version` >= 3.11 (parse "Python 3.11.5" format)
  - Podman: `podman --version` (any version acceptable)
  - Git: `git --version` (any version acceptable)
- **Error Handling:** Collect all failures, return complete report (don't fail-fast)

## Acceptance Criteria (Task Level)

- [ ] `scripts/lib/prerequisites.nu` module implemented with `check_prerequisites` function
- [ ] Function validates Python 3.11+ availability and version
- [ ] Function validates Podman availability
- [ ] Function validates Git availability
- [ ] Returns structured record with validation results
- [ ] Error messages include Devbox configuration guidance (e.g., "Add python311 to devbox.json")
- [ ] Unit tests pass with mocked commands (simulate missing/present tools)
- [ ] Code handles edge cases (command not found, version parsing failures)

## Implementation Guidance

### Code Example / Pseudo-code

```nushell
# scripts/lib/prerequisites.nu

# Check if all prerequisites are available and meet version requirements
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

### Unit Tests Example

```nushell
# tests/unit/test_prerequisites.nu
use std assert
use scripts/lib/prerequisites.nu

# Mock test: Simulate all prerequisites present
def test_all_prerequisites_present [] {
    # In real test, would mock `which` and version commands
    let result = (check_prerequisites)

    assert ($result.python == true)
    assert ($result.podman == true)
    assert ($result.git == true)
    assert (($result.errors | length) == 0)
}

# Mock test: Simulate Python missing
def test_python_missing [] {
    # Mock `which python` to return empty
    # let result = check_prerequisites with mocked environment

    # assert ($result.python == false)
    # assert (($result.errors | length) > 0)
    # assert ($result.errors | str contains "Python not found")
}
```

### Reference Implementation
- Version parsing pattern from Taskfile version checks
- Error message format consistent with US-001 Scenario 5 requirements

### Implementation Research Reference
- **Primary Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md
- **§2.1 - Python 3.11+ Technology Stack:** Validates Python 3.11+ availability before setup proceeds
- **§8.2 - Anti-Pattern: Poor Error Handling:** Provide actionable error messages with Devbox configuration guidance

## Dependencies

### Technical Dependencies
- NuShell `which` command
- Python, Podman, Git (for testing)

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

## Testing Requirements

### Unit Tests
- [ ] Test all prerequisites present (Python 3.11+, Podman, Git)
- [ ] Test Python missing
- [ ] Test Python too old (< 3.11)
- [ ] Test Podman missing
- [ ] Test Git missing
- [ ] Test version parsing edge cases (malformed version strings)

### Manual Testing Steps
1. Run `devbox shell` with all tools installed
2. Execute `use scripts/lib/prerequisites.nu; check_prerequisites`
3. Verify all checks pass
4. Remove Python from devbox.json, restart shell
5. Execute check again, verify error message includes Devbox guidance

## Non-Functional Requirements

### Performance
- Prerequisite checks must complete in <2 seconds

### Security
- No security concerns (read-only validation)

### Observability
- Log validation results for debugging

## Risk & Complexity Notes

**Technical Risks:**
- Python version string format may vary (Python 3.11.5+ vs 3.11.5rc1)
- Different Python distributions may report versions differently

**Mitigation Strategies:**
- Robust version parsing with regex fallback
- Test with multiple Python installations (CPython, PyPy if relevant)

**Task-Level Uncertainties & Blockers:**

No task-level uncertainties. Implementation approach clear from Tech Spec SPEC-001 §2.2 (prerequisites.nu module interface).

## Definition of Done (Task Level)

- [ ] Implementation complete and functionally correct
- [ ] Code follows NuShell coding standards
- [ ] All unit tests written and passing
- [ ] Code reviewed and approved by 1 reviewer
- [ ] No NuShell analyzer warnings
- [ ] Inline comments added explaining version parsing logic
- [ ] Merged to main branch
- [ ] Task status updated to Done

## Code Review Checklist

**For Reviewer:**
- [ ] Version parsing handles edge cases (rc versions, patch versions)
- [ ] Error messages are actionable and include Devbox guidance
- [ ] Logic collects all errors (doesn't fail-fast on first failure)
- [ ] Unit tests cover all validation scenarios
- [ ] Code is readable with clear variable names
- [ ] Structured data returned correctly

## Related Links
- **Parent Story:** /artifacts/backlog_stories/US-001_automated_setup_script_v2.md (Scenario 5)
- **Tech Spec:** /artifacts/tech_specs/SPEC-001_automated_setup_script_v1.md (§2.2 - prerequisites.nu)
- **Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Notes & Comments

**Implementation Notes:**
- Use `complete` command for version checks to capture exit codes and stderr
- Collect all validation failures to provide complete picture to user
- Include Devbox configuration guidance in error messages (per US-001 requirements)

**Blockers/Issues Encountered:**
[To be filled during implementation if issues arise]
