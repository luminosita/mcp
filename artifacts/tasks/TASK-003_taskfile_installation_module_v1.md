# Implementation Task: Implement Taskfile Detection and Installation Module

## Metadata
- **Task ID:** TASK-003
- **Parent Story ID:** US-001
- **Status:** To Do
- **Priority:** Critical
- **Assigned To:** [Unassigned]
- **Sprint:** Sprint 1
- **Domain:** DevOps/Infrastructure
- **Estimated Hours:** 6 hours
- **Related Tech Spec:** SPEC-001 (Phase 2: Installation Logic)
- **Version:** v1

## Decisions Incorporated from SPEC-001 v1 Feedback

**D1 - NuShell Module Import Strategy:**
- Use `use lib/module.nu` with explicit exports (NOT `source`)
- Provides better maintainability and clear module boundaries
- **Impact:** All modules must use `export def` for public functions

**D2 - Taskfile Binary Location:**
- Prefer devbox packages for isolation
- Fallback to `~/.local/bin` (no sudo required)
- **Impact:** Installation logic tries devbox first, then local bin
- **Rationale:** Avoid sudo requirements, maintain isolation

**D3 - Progress Indicator Implementation:**
- Use gum (https://github.com/charmbracelet/gum) for terminal UX/UI
- **Impact:** Progress display via gum for long-running downloads

**D5 - Taskfile Installation Retry:**
- Retry 3 times for network errors
- Fail immediately for platform/permission errors
- Continue in degraded mode if retries exhausted
- **Impact:** Module implements retry logic for downloads, warns on final failure

## Task Description

**Objective:**
Implement the `taskfile_install.nu` module that detects existing Taskfile installations and performs cross-platform installation (macOS, Linux, WSL2) with automatic retry logic for network failures, returning structured installation status. Module must use explicit exports per Decision D1 and implement degraded mode per Decision D5.

**Technical Context:**
Per US-001 v2 FR-22, Taskfile 3.0+ provides unified CLI interface (`task <command>`) for all development operations. This module bridges the gap between "Taskfile missing" and "Taskfile available" states. Per SPEC-001 §4.2, this module is called after prerequisite validation and before dependency installation. Per Decision D5, if installation fails after retries, setup continues in degraded mode with warning.

**Architecture Decision:**
Per SPEC-001 v1 Decision D1, all NuShell modules use `use` with explicit exports (NOT `source`).

## Technical Specifications

### Implementation Approach
1. Implement `ensure_taskfile` function in `taskfile_install.nu` with explicit export
2. Check if Taskfile already installed using `task --version`
3. If not installed, detect installation method based on OS:
   - macOS: Try `brew install go-task`, fallback to binary download
   - Linux: Download binary from GitHub releases with checksum verification
   - WSL2: Try `apt` (if available), fallback to binary download
4. Implement retry logic (3 attempts) for network operations with exponential backoff
5. Verify installation success after each attempt
6. Return structured record with installation status
7. Write unit tests with mocked commands

### Code Changes Required

**New Files to Create:**
- `scripts/lib/taskfile_install.nu` - Taskfile installation module (explicit exports per D1)
- `tests/unit/test_taskfile_install.nu` - Unit tests for installation logic

### Technical Details

#### DevOps/Infrastructure Task
- **Module:** taskfile_install.nu
- **Public Functions:** `ensure_taskfile(os_info: record) -> record`
- **Export Pattern:** Explicit exports using `export def` (per D1)
- **Import Pattern:** Main script will use `use scripts/lib/taskfile_install.nu ensure_taskfile`
- **Installation Logic:**
  - **Detection:** `task --version` (exit code 0 = installed)
  - **macOS:**
    1. Check if `brew` available: `which brew`
    2. If yes: `brew install go-task`
    3. If no: Download binary from GitHub releases to `~/.local/bin`
  - **Linux:**
    1. Download binary from GitHub releases: `https://github.com/go-task/task/releases/latest/download/task_linux_amd64.tar.gz`
    2. Verify checksum (optional but recommended)
    3. Extract to `~/.local/bin`
    4. Make executable: `chmod +x`
  - **WSL2:**
    1. Check if `apt` available: `which apt`
    2. If yes: `sudo apt install task` (may require user confirmation)
    3. If no: Download binary (same as Linux)
- **Retry Logic:** 3 attempts with exponential backoff (1s, 2s, 4s) for network operations
- **Degraded Mode:** If all retries fail, return `{installed: false, degraded: true, warning: "..."}` and continue setup

## Acceptance Criteria (Task Level)

- [ ] `scripts/lib/taskfile_install.nu` module implemented with **explicitly exported** `ensure_taskfile` function
- [ ] Module uses `export def` (NOT plain `def`) per Decision D1
- [ ] Function detects existing Taskfile installations (3.0+ only)
- [ ] Function installs Taskfile on macOS (brew + binary fallback)
- [ ] Function installs Taskfile on Linux (binary download with checksum)
- [ ] Function installs Taskfile on WSL2 (apt + binary fallback)
- [ ] Implements retry logic (3 attempts) with exponential backoff for network failures
- [ ] Binary installation uses `~/.local/bin` (per Decision D2)
- [ ] Returns structured record with installation status and source
- [ ] Supports degraded mode (continues with warning if installation fails per Decision D5)
- [ ] Unit tests pass with mocked commands (simulate existing/missing Taskfile, network failures)
- [ ] Unit tests demonstrate proper `use` import pattern
- [ ] Code handles edge cases (network timeout, permission errors, unsupported platforms)

## Implementation Guidance

### Code Example / Pseudo-code

```nushell
# scripts/lib/taskfile_install.nu
# NuShell module for Taskfile installation with explicit exports (per SPEC-001 D1)

# Ensure Taskfile 3.0+ is installed, install if missing
# Arguments:
#   os_info: record - OS detection result from os_detection.nu
# Returns:
#   record - Installation status {installed: bool, version: string, source: string, degraded: bool?, warning: string?}
# Degraded mode: If installation fails after retries, returns degraded=true with warning (per D5)
export def ensure_taskfile [os_info: record] -> record {
    # Check if Taskfile already installed
    let existing = (check_taskfile_version)

    if $existing.installed {
        return {
            installed: true,
            version: $existing.version,
            source: "existing",
            degraded: false
        }
    }

    # Attempt installation based on OS
    print "Taskfile not found. Installing..."

    let install_result = match $os_info.os {
        "macos" => { install_taskfile_macos },
        "linux" => { install_taskfile_linux $os_info.arch },
        "wsl2" => { install_taskfile_wsl2 $os_info.arch },
        _ => { {success: false, error: $"Unsupported OS: ($os_info.os)"} }
    }

    if not $install_result.success {
        # Degraded mode per Decision D5
        return {
            installed: false,
            version: "",
            source: "none",
            degraded: true,
            warning: $"Taskfile installation failed: ($install_result.error). Setup will continue. Install manually: https://taskfile.dev/installation/"
        }
    }

    # Verify installation
    let final_check = (check_taskfile_version)

    return {
        installed: $final_check.installed,
        version: $final_check.version,
        source: $install_result.source,
        degraded: (not $final_check.installed)
    }
}

# Check if Taskfile installed and get version
# Helper function (not exported - private to module)
def check_taskfile_version [] -> record {
    let version_output = (task --version | complete)

    if $version_output.exit_code != 0 {
        return {installed: false, version: ""}
    }

    let version_str = ($version_output.stdout | str trim)

    # Parse version (format: "Task version: v3.39.0")
    let version = ($version_str | parse "Task version: {version}" | get version.0?)

    return {installed: true, version: ($version | default "")}
}

# Install Taskfile on macOS
# Helper function (not exported - private to module)
def install_taskfile_macos [] -> record {
    # Try brew first
    if (which brew | length) > 0 {
        print "Installing Taskfile via Homebrew..."
        let brew_result = (brew install go-task | complete)

        if $brew_result.exit_code == 0 {
            return {success: true, source: "brew"}
        }

        print "Homebrew installation failed, falling back to binary download..."
    }

    # Fallback to binary download
    return (install_taskfile_binary "darwin" "amd64")  # TODO: detect arm64 vs amd64
}

# Install Taskfile on Linux
# Helper function (not exported - private to module)
def install_taskfile_linux [arch: string] -> record {
    return (install_taskfile_binary "linux" $arch)
}

# Install Taskfile on WSL2
# Helper function (not exported - private to module)
def install_taskfile_wsl2 [arch: string] -> record {
    # Try apt first
    if (which apt | length) > 0 {
        print "Installing Taskfile via apt..."
        let apt_result = (sudo apt install -y task | complete)

        if $apt_result.exit_code == 0 {
            return {success: true, source: "apt"}
        }

        print "apt installation failed, falling back to binary download..."
    }

    # Fallback to binary download
    return (install_taskfile_binary "linux" $arch)
}

# Download and install Taskfile binary
# Helper function (not exported - private to module)
# Implements retry logic per Decision D5 (3 attempts, exponential backoff)
def install_taskfile_binary [os: string, arch: string] -> record {
    let binary_dir = ([$env.HOME, ".local", "bin"] | path join)
    let url = $"https://github.com/go-task/task/releases/latest/download/task_($os)_($arch).tar.gz"
    let temp_file = "/tmp/task.tar.gz"

    # Ensure ~/.local/bin exists
    mkdir $binary_dir

    # Retry logic (3 attempts with exponential backoff)
    let max_attempts = 3
    let backoff = [1sec, 2sec, 4sec]

    for attempt in 0..<$max_attempts {
        print $"Downloading Taskfile (attempt ($attempt + 1)/($max_attempts))..."

        # Download with timeout
        let download_result = (http get --max-time 30 $url | save -f $temp_file | complete)

        if $download_result.exit_code == 0 {
            # Extract tarball
            let extract_result = (tar -xzf $temp_file -C $binary_dir task | complete)

            if $extract_result.exit_code == 0 {
                # Make executable
                chmod +x ([$binary_dir, "task"] | path join)

                # Cleanup
                rm $temp_file

                return {success: true, source: "binary"}
            } else {
                print $"Extraction failed: ($extract_result.stderr)"
            }
        } else {
            print $"Download failed: ($download_result.stderr)"
        }

        # Retry with backoff (unless last attempt)
        if $attempt < ($max_attempts - 1) {
            let wait_time = ($backoff | get $attempt)
            print $"Retrying in ($wait_time)..."
            sleep $wait_time
        }
    }

    # All retries exhausted
    return {
        success: false,
        error: "Failed to download Taskfile after 3 attempts. Check network connectivity."
    }
}
```

### Usage Example (for documentation)

```nushell
# Import modules using `use` with explicit function import (per D1)
use scripts/lib/os_detection.nu detect_os
use scripts/lib/taskfile_install.nu ensure_taskfile

# Detect OS
let os_info = (detect_os)

# Ensure Taskfile installed
let taskfile_result = (ensure_taskfile $os_info)

if $taskfile_result.degraded {
    # Degraded mode per Decision D5 - warn but continue
    gum style --foreground 214 $"⚠️ WARNING: ($taskfile_result.warning)"
    gum style --foreground 214 "Setup will continue, but you must use direct tool commands (see CLAUDE-tooling.md)"
} else if $taskfile_result.installed {
    gum style --foreground 2 $"✓ Taskfile ($taskfile_result.version) ready (source: ($taskfile_result.source))"
}

# Continue with setup...
```

### Unit Tests Example

```nushell
# tests/unit/test_taskfile_install.nu
use std assert
use scripts/lib/taskfile_install.nu ensure_taskfile  # Explicit import per D1

# Test: Taskfile already installed
def test_taskfile_already_installed [] {
    # Mock: task --version returns success
    # let result = (ensure_taskfile {os: "macos", arch: "arm64"})

    # assert ($result.installed == true)
    # assert ($result.source == "existing")
    # assert ($result.degraded == false)
}

# Test: Install on macOS via brew
def test_install_macos_brew [] {
    # Mock: which brew returns success, brew install succeeds
    # let result = (ensure_taskfile {os: "macos", arch: "arm64"})

    # assert ($result.installed == true)
    # assert ($result.source == "brew")
}

# Test: Retry logic on network failure
def test_retry_logic_network_failure [] {
    # Mock: first 2 download attempts fail, 3rd succeeds
    # Verify exponential backoff timing (1s, 2s)
    # let result = (ensure_taskfile {os: "linux", arch: "amd64"})

    # assert ($result.installed == true)
    # assert ($result.source == "binary")
}

# Test: Degraded mode after all retries fail
def test_degraded_mode_all_retries_fail [] {
    # Mock: all 3 download attempts fail
    # let result = (ensure_taskfile {os: "linux", arch: "amd64"})

    # assert ($result.installed == false)
    # assert ($result.degraded == true)
    # assert ($result.warning | str contains "failed after 3 attempts")
}

# Run tests
test_taskfile_already_installed
```

### Reference Implementation
- Binary download pattern from uv installation examples
- Retry logic pattern from SPEC-001 §4.2 (deps_install.nu)
- Homebrew check pattern from common dev environment scripts
- gum integration example: https://github.com/charmbracelet/gum

### Implementation Research Reference
- **Primary Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md
- **§8.2 - Anti-Pattern: Poor Error Handling:** Implement retry logic with clear error messages and degraded mode support
- **Taskfile Documentation:** https://taskfile.dev/installation/

## Dependencies

### Technical Dependencies
- NuShell `which` command
- NuShell `http get` for downloads
- NuShell `complete` for command execution with error handling
- `tar` command for extracting binary
- `chmod` for file permissions
- gum (for progress display in main setup script)

### Task Dependencies
- **Blocked By:** TASK-001 (OS detection provides OS info input)
- **Blocked By:** TASK-002 (Prerequisites check must pass before installation)
- **Blocks:** TASK-004 (uv installation follows similar pattern)
- **Blocks:** TASK-005 (Virtual environment setup requires Taskfile for task commands)

### Environment Requirements
- Devbox shell environment active
- Network connectivity for binary downloads
- Write permissions to `~/.local/bin`

## Estimation

- **Estimated Hours:** 6 hours
- **Complexity:** Medium-High
- **Uncertainty Level:** Medium

**Complexity Factors:**
- Cross-platform installation logic (high - 3 different OS paths)
- Network retry logic with exponential backoff (medium)
- Binary download and extraction (medium)
- Degraded mode support (low)
- Unit test mocking for multiple platforms (medium)

## Testing Requirements

### Unit Tests
- [ ] Test Taskfile already installed (returns existing)
- [ ] Test macOS installation via brew (success)
- [ ] Test macOS installation binary fallback (brew fails)
- [ ] Test Linux installation via binary download
- [ ] Test WSL2 installation via apt (success)
- [ ] Test WSL2 installation binary fallback (apt fails)
- [ ] Test retry logic on network failure (1st attempt fails, 2nd succeeds)
- [ ] Test retry logic exhaustion (all 3 attempts fail)
- [ ] Test degraded mode activation (installation fails, returns degraded=true)
- [ ] Test binary extraction failure handling
- [ ] Test unsupported OS error handling
- [ ] Test module import using `use` pattern (verify explicit export works)

### Manual Testing Steps
1. Run `devbox shell` without Taskfile installed
2. Test explicit import: `use scripts/lib/taskfile_install.nu ensure_taskfile`
3. Execute function: `let result = (ensure_taskfile {os: "macos", arch: "arm64"}); print $result`
4. Verify Taskfile installed to `~/.local/bin/task` (or via brew)
5. Run `task --version` to confirm installation
6. Test idempotency: Run function again, verify returns "existing"
7. Test degraded mode: Simulate network failure (disconnect network), verify warning displayed
8. Test on all supported platforms (macOS, Linux, WSL2)

## Non-Functional Requirements

### Performance
- Detection check must complete in <1 second
- Binary download with retries must complete in <60 seconds (typical)
- Degraded mode activation must not block setup (continue immediately with warning)

### Security
- Download binaries over HTTPS only
- Verify checksums if available (optional for v1, recommended for future)
- Install to user directory (`~/.local/bin`) to avoid sudo

### Observability
- Log installation attempts and results
- Progress indicators during download (via gum in main setup script)
- Clear warning messages in degraded mode

## Risk & Complexity Notes

**Technical Risks:**
- Network failures during binary download (high probability in poor connectivity)
- GitHub releases API rate limiting (low probability)
- Platform detection may not cover all Linux distributions
- `~/.local/bin` may not be in PATH (user configuration issue)
- Binary architecture mismatch (arm64 vs amd64 on macOS)

**Mitigation Strategies:**
- Retry logic with exponential backoff for network failures
- Degraded mode allows setup to continue without Taskfile
- Fallback to binary download if package managers fail
- Include PATH setup guidance in warning messages
- Detect architecture from OS info (from TASK-001)

**Task-Level Uncertainties & Blockers:**

1. **Architecture Detection for macOS:** Should we detect arm64 vs amd64 dynamically, or use `os_info.arch` from TASK-001? [CLARIFY BEFORE START]
   - **Recommendation:** Use `os_info.arch` from TASK-001 for consistency

2. **Checksum Verification:** Should we verify binary checksums in v1, or defer to future enhancement? [CLARIFY BEFORE START]
   - **Trade-off:** Security vs implementation complexity
   - **Recommendation:** Skip checksum in v1 (use HTTPS), add in future iteration

3. **PATH Addition:** Should this module add `~/.local/bin` to PATH if missing, or just warn user? [CLARIFY BEFORE START]
   - **Trade-off:** Automatic PATH modification may surprise users vs manual step required
   - **Recommendation:** Warn user with instructions (less invasive)

4. **Homebrew Installation Timeout:** What timeout should we use for `brew install go-task`? Homebrew can be slow. [CLARIFY BEFORE START]
   - **Recommendation:** 120 seconds timeout (brew can be slow on first run)

## Definition of Done (Task Level)

- [ ] Implementation complete and functionally correct
- [ ] Code follows NuShell coding standards
- [ ] Module uses explicit exports (`export def`) per Decision D1
- [ ] All unit tests written and passing
- [ ] Unit tests demonstrate `use` import pattern
- [ ] Code reviewed and approved by 1 reviewer
- [ ] No NuShell analyzer warnings
- [ ] Inline comments added explaining installation logic per platform
- [ ] Module header includes usage example with `use` import and degraded mode handling
- [ ] Tested manually on at least 2 platforms (macOS + Linux or WSL2)
- [ ] Degraded mode tested with network failure simulation
- [ ] Merged to main branch
- [ ] Task status updated to Done

## Code Review Checklist

**For Reviewer:**
- [ ] Installation logic handles all 3 platforms (macOS, Linux, WSL2)
- [ ] Retry logic implements exponential backoff correctly (1s, 2s, 4s)
- [ ] Degraded mode activated after retry exhaustion
- [ ] Binary installation uses `~/.local/bin` (per Decision D2)
- [ ] Error messages are actionable and include installation URL
- [ ] Unit tests cover all platforms and failure scenarios
- [ ] Code is readable with clear variable names
- [ ] Structured data returned correctly
- [ ] **Module uses `export def` (NOT plain `def`) per Decision D1**
- [ ] **Helper functions are NOT exported (private to module)**
- [ ] **Unit tests demonstrate correct `use` import pattern**
- [ ] **Module header documents degraded mode behavior (per D5)**
- [ ] Binary download uses HTTPS (security requirement)
- [ ] Extraction handles tar command failures gracefully

## Related Links
- **Parent Story:** /artifacts/backlog_stories/US-001_automated_setup_script_v2.md (FR-22, Scenario 11)
- **Tech Spec:** /artifacts/tech_specs/SPEC-001_automated_setup_script_v1.md (§4.2 - taskfile_install.nu, Phase 2)
- **Tech Spec API:** /artifacts/tech_specs/SPEC-001_automated_setup_script_v1.md (lines 284-352 - taskfile_install.nu interface)
- **Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md
- **Taskfile Installation Docs:** https://taskfile.dev/installation/

## Notes & Comments

**Implementation Notes:**
- Use `complete` command for all external command execution to capture exit codes and stderr
- Implement retry logic in reusable helper function for future use (uv installation will use similar pattern)
- Include platform-specific troubleshooting guidance in error messages
- **CRITICAL:** Public function uses `export def`, helper functions use plain `def` (private)
- Include usage example in module header comments showing degraded mode handling
- Verify `~/.local/bin` exists before binary installation (create if needed)
- Use gum for progress display in main setup script (not this module's responsibility)

**Blockers/Issues Encountered:**
[To be filled during implementation if issues arise]
