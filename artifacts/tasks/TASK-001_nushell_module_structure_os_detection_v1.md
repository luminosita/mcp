# Implementation Task: Create NuShell Module Structure and OS Detection

## Metadata
- **Task ID:** TASK-001
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
Create the foundational NuShell directory structure (`scripts/` and `scripts/lib/`) and implement the OS detection module that identifies macOS, Linux, and WSL2 environments with architecture and version information.

**Technical Context:**
This task establishes the foundational module architecture for the automated setup script. The OS detection module is critical as all subsequent modules make platform-specific decisions based on its output. Per SPEC-001 §2 (Component Diagram), this module is the first step in the setup orchestration flow.

## Technical Specifications

### Implementation Approach
1. Create `scripts/` and `scripts/lib/` directory structure
2. Implement `os_detection.nu` module with `detect_os` function
3. Use NuShell built-in commands (`sys`, `uname`) for cross-platform detection
4. Return structured record with OS type, architecture, and version
5. Write unit tests for all supported platforms

### Code Changes Required

**Directories to Create:**
- `scripts/` - Main scripts directory
- `scripts/lib/` - NuShell module library

**New Files to Create:**
- `scripts/lib/os_detection.nu` - OS detection module (export `detect_os` function)
- `tests/unit/test_os_detection.nu` - Unit tests for OS detection

### Technical Details

#### DevOps/Infrastructure Task
- **Module:** os_detection.nu
- **Public Functions:** `detect_os() -> record<os: string, arch: string, version: string>`
- **Platform Support:** macOS, Linux (Ubuntu/Debian/Fedora/Arch), Windows WSL2
- **Detection Strategy:**
  - Use `sys | get host` for structured system information
  - Fall back to `uname -s` and `uname -m` for compatibility
  - Detect WSL2 via `/proc/version` containing "microsoft" or "WSL"
  - Parse version strings from `sw_vers`, `lsb_release`, or `/etc/os-release`

## Acceptance Criteria (Task Level)

- [ ] `scripts/` and `scripts/lib/` directories created
- [ ] `scripts/lib/os_detection.nu` module implemented with `detect_os` function
- [ ] Function returns structured record: `{os: string, arch: string, version: string}`
- [ ] Correctly detects macOS (both Intel and Apple Silicon)
- [ ] Correctly detects Linux distributions (Ubuntu, Fedora, Arch)
- [ ] Correctly detects Windows WSL2 (Ubuntu distribution)
- [ ] Unit tests pass for all supported platforms
- [ ] Code follows NuShell best practices (use structured data, avoid string parsing where possible)
- [ ] No linting errors from NuShell analyzer

## Implementation Guidance

### Code Example / Pseudo-code

```nushell
# scripts/lib/os_detection.nu

# Detect operating system, architecture, and version
export def detect_os [] -> record<os: string, arch: string, version: string> {
    # Get system info using NuShell's built-in sys command
    let sys_info = (sys | get host)

    let os_name = $sys_info.name
    let arch = $sys_info.arch

    # Determine OS type
    let os_type = match $os_name {
        "Darwin" => "macos",
        "Linux" => {
            # Check if WSL2
            let is_wsl = (if ("/proc/version" | path exists) {
                (open /proc/version | str contains "microsoft" or (open /proc/version | str contains "WSL"))
            } else {
                false
            })

            if $is_wsl {
                "wsl2"
            } else {
                "linux"
            }
        },
        _ => "unknown"
    }

    # Get version information
    let version = match $os_type {
        "macos" => {
            # Use sw_vers to get macOS version
            (sw_vers -productVersion | str trim)
        },
        "linux" | "wsl2" => {
            # Try lsb_release first
            if (which lsb_release | length) > 0 {
                (lsb_release -rs | str trim)
            } else if ("/etc/os-release" | path exists) {
                # Parse /etc/os-release file
                (open /etc/os-release | lines | find VERSION_ID | first | split row "=" | get 1 | str trim --char '"')
            } else {
                "unknown"
            }
        },
        _ => "unknown"
    }

    return {
        os: $os_type,
        arch: $arch,
        version: $version
    }
}
```

### Unit Tests Example

```nushell
# tests/unit/test_os_detection.nu
use std assert
use scripts/lib/os_detection.nu

def test_detect_os [] {
    let result = (detect_os)

    # Verify return structure
    assert ($result | get os | describe) == "string"
    assert ($result | get arch | describe) == "string"
    assert ($result | get version | describe) == "string"

    # Verify OS is one of supported types
    assert ($result.os in ["macos", "linux", "wsl2"])

    # Verify arch is valid
    assert ($result.arch in ["x86_64", "arm64", "aarch64", "amd64"])
}

# Run test
test_detect_os
```

### Reference Implementation
- NuShell `sys` command documentation: https://www.nushell.sh/commands/docs/sys.html
- Similar pattern in Devbox: https://github.com/jetpack-io/devbox

### Implementation Research Reference
- **Primary Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md
- **§2.1 - Python 3.11+ Technology Stack:** This module enables cross-platform validation of Python availability
- **§8.1 - Anti-Pattern: Poor Error Handling:** Provide structured error messages if OS detection fails

## Dependencies

### Technical Dependencies
- NuShell 0.80+ installed in Devbox environment

### Task Dependencies
- **Blocked By:** None (foundation task)
- **Blocks:** TASK-002 (Prerequisites module needs OS detection)

### Environment Requirements
- Devbox shell environment active
- Access to test environments: macOS, Linux, WSL2 (for manual testing)

## Estimation

- **Estimated Hours:** 4 hours
- **Complexity:** Low-Medium
- **Uncertainty Level:** Low

**Complexity Factors:**
- NuShell structured data handling (low - well-documented)
- Cross-platform testing (medium - requires multiple environments)
- WSL2 detection logic (low - straightforward file check)

## Testing Requirements

### Unit Tests
- [ ] Test `detect_os` returns correct structure
- [ ] Test OS type detection (macos/linux/wsl2)
- [ ] Test architecture detection (x86_64/arm64/amd64)
- [ ] Test version string parsing
- [ ] Test WSL2 detection via /proc/version

### Integration Tests (if applicable)
- [ ] Manual test on macOS (Intel and Apple Silicon if available)
- [ ] Manual test on Ubuntu 22.04+
- [ ] Manual test on Windows 11 WSL2 (Ubuntu distribution)

### Manual Testing Steps
1. Run `devbox shell` to enter isolated environment
2. Execute `use scripts/lib/os_detection.nu; detect_os`
3. Verify output structure matches: `{os: "macos", arch: "arm64", version: "14.5"}`
4. Repeat on all supported platforms

## Non-Functional Requirements

### Performance
- OS detection must complete in <1 second

### Security
- No sensitive system information exposed beyond OS type, arch, version

### Observability
- Log detected OS information for debugging setup issues

## Risk & Complexity Notes

**Technical Risks:**
- Different Linux distributions may have varying version file formats (/etc/os-release variations)
- WSL2 detection may fail on older WSL versions

**Mitigation Strategies:**
- Provide fallback logic if primary detection methods fail
- Test on multiple Linux distributions (Ubuntu, Fedora, Arch)
- Document known limitations in code comments

**Task-Level Uncertainties & Blockers:**

No task-level uncertainties. Implementation approach clear from Tech Spec SPEC-001 §2.2 (os_detection.nu module interface).

## Definition of Done (Task Level)

- [ ] Implementation complete and functionally correct
- [ ] Code follows NuShell coding standards
- [ ] All unit tests written and passing
- [ ] Code reviewed and approved by 1 reviewer
- [ ] No NuShell analyzer warnings
- [ ] Inline comments added explaining detection logic
- [ ] Merged to main branch
- [ ] Task status updated to Done

## Code Review Checklist

**For Reviewer:**
- [ ] NuShell structured data used correctly (no string parsing where avoidable)
- [ ] Logic handles all supported platforms (macOS, Linux, WSL2)
- [ ] Unit tests adequately cover detection scenarios
- [ ] Error handling for unknown platforms
- [ ] Version parsing handles edge cases (missing files, malformed data)
- [ ] Code is readable with clear variable names
- [ ] Inline comments explain complex logic (e.g., WSL2 detection)

## Related Links
- **Parent Story:** /artifacts/backlog_stories/US-001_automated_setup_script_v2.md
- **Tech Spec:** /artifacts/tech_specs/SPEC-001_automated_setup_script_v1.md (§2.2 - os_detection.nu)
- **Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Notes & Comments

**Implementation Notes:**
- Use NuShell's `sys` command for primary detection (cleaner than parsing `uname` output)
- WSL2 detection via `/proc/version` is reliable across WSL versions
- Version parsing may vary by distribution - prioritize Ubuntu/Debian (most common)

**Blockers/Issues Encountered:**
[To be filled during implementation if issues arise]
