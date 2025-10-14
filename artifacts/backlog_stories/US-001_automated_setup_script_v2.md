# User Story: Automated Setup Script with Interactive Prompts

## Metadata
- **Story ID:** US-001
- **Title:** Create Automated Setup Script (NuShell) with Interactive Prompts
- **Type:** Feature
- **Status:** Backlog
- **Priority:** Critical - Foundation enabler blocking all feature development
- **Parent PRD:** PRD-000
- **Parent High-Level Story:** HLS-001
- **Functional Requirements Covered:** FR-01, FR-03, FR-19, FR-20, FR-22
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md
- **Version:** v2.0

## Parent Artifact Context

**Parent PRD:** PRD-000: Project Foundation & Bootstrap Infrastructure
- **Link:** /artifacts/prds/PRD-000_project_foundation_bootstrap_v3.md
- **PRD Section:** Section 6.1 - User Flows (Flow 1: New Developer Environment Setup)
- **Functional Requirements Coverage:**
  - **FR-01:** Automated environment setup script supporting macOS, Linux, and Windows (WSL2)
  - **FR-03:** Python 3.11+ virtual environment with automated dependency management via uv
  - **FR-19:** Cross-platform scripting with NuShell
  - **FR-20:** Isolated dev environments with Devbox
  - **FR-22:** Unified CLI interface via Taskfile for all development operations

**Parent High-Level Story:** HLS-001: Automated Development Environment Setup
- **Link:** /artifacts/hls/HLS-001_automated_dev_environment_setup_v2.md
- **HLS Section:** Section 8 - Decomposition into Backlog Stories (Story #1)

## User Story

As a developer joining the project, I want to run a single automated setup script that handles all environment configuration including Taskfile installation, so that I can achieve a working development environment in under 30 minutes with unified CLI access to all development operations.

## Description

This story implements the core automation script (`scripts/setup.nu`) that orchestrates complete development environment setup within a Devbox isolated environment. The script performs operating system detection, prerequisite validation (including Taskfile), dependency installation, virtual environment configuration, and environment health checks—all through an interactive command-line interface with sensible defaults for automation scenarios.

The script bridges the gap between "repository cloned" and "environment ready for development" states, eliminating multi-hour manual configuration processes and "works on my machine" failures through reproducible, automated setup within Devbox containers. Taskfile installation ensures developers have unified CLI access to all development operations via `task <command>` interface.

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§2.1: Python 3.11+ Technology Stack:** Script validates Python 3.11+ availability and uses uv package manager for dependency management
  - **Performance Target:** Setup script execution <30 minutes end-to-end
- **§2.2: FastAPI Framework:** Script installs FastAPI and dependencies via uv from pyproject.toml
- **§7.1: Testing Implementation:** Script validates environment health through automated checks after setup

**Anti-Patterns Avoided:**
- **§8.1 Pitfall 1: Synchronous Blocking Calls:** Script uses NuShell's async capabilities for parallel downloads where possible
- **§8.2 Anti-Pattern 2: Poor Error Handling:** Script provides structured error messages with suggested remediation (ref: §8.1 Pitfall 3)

**Performance Considerations:**
- **§2.1 Language Runtime:** Python 3.11+ required for async performance and modern type hints
- **Target Metrics:** Setup execution <30 minutes, uv dependency installation ~2-3 minutes typical

## Functional Requirements

### Core Setup Capabilities
- Detect operating system (macOS, Linux, Windows WSL2) and adapt setup steps accordingly
- Validate prerequisites within Devbox environment (Python 3.11+, Podman, Git, uv, Taskfile)
- Install Taskfile 3.0+ if not present in Devbox environment (unified CLI interface)
- Install uv package manager if not present in Devbox environment
- Create Python virtual environment at `.venv/` using Python 3.11+
- Install all dependencies from `pyproject.toml` using uv for reproducible builds
- Configure pre-commit hooks for automated code quality checks
- Copy `.env.example` to `.env` with default environment variable values
- Validate environment health through automated checks (Python version, dependency installation, Taskfile availability, file permissions)

### Interactive Configuration
- Prompt user for configuration options (IDE setup preference, verbose/silent mode, database setup)
- Provide sensible defaults for all prompts enabling quick setup via Enter key
- Support `--silent` flag for non-interactive mode using all defaults (CI/automation scenarios)
- Display clear help text for each configuration option

### Progress Feedback
- Display verbose output showing detailed step information (what's being installed, where files are written)
- Show progress indicators (progress bars or percentage complete) for long-running operations
- Provide estimated time remaining for multi-minute operations
- Output success message with clear next steps upon completion (including `task --list` for command discovery)

### Error Handling
- Detect and report missing prerequisites with installation instructions
- Handle network failures with retry logic (3 attempts with exponential backoff)
- Detect file system permission issues and provide resolution guidance
- Provide actionable error messages with specific troubleshooting steps

## Non-Functional Requirements

- **Performance:** Script execution time <30 minutes end-to-end on typical developer machine with stable internet
- **Reliability:** >98% success rate on supported platforms (macOS, Linux, Windows WSL2) within Devbox
- **Usability:** Error messages must be actionable with specific resolution steps (no generic "setup failed" messages)
- **Maintainability:** Script must be modular with clearly separated functions for each setup phase
- **Cross-Platform Compatibility:** Single NuShell script works identically on macOS, Linux, BSD, and Windows (WSL2)
- **Idempotency:** Running script multiple times produces same result without side effects

## Technical Requirements

### Script Structure
- Main setup script: `scripts/setup.nu` (NuShell for cross-platform compatibility)
- Separate NuShell modules for:
  - OS detection and validation
  - Prerequisite checking
  - Dependency installation (including Taskfile)
  - Environment configuration
  - Health check validation

### NuShell Implementation
- Use NuShell built-in commands for cross-platform file operations
- Leverage NuShell's structured data types for progress tracking
- Implement error handling using NuShell's `try-catch` pattern
- Use NuShell pipes for chaining operations efficiently

### Taskfile Installation
- Check if Taskfile installed: `task --version`
- If not installed, detect OS and install appropriate version:
  - macOS: `brew install go-task` or download binary
  - Linux: Download binary from GitHub releases or use package manager
  - Windows WSL2: Download binary or use package manager
- Verify installation: `task --version >= 3.0`
- Add to Devbox packages if possible for better reproducibility

### uv Package Manager Integration
- Install uv if not present: Check system PATH, download via curl/wget, verify installation
- Create virtual environment: `uv venv .venv --python 3.11`
- Install dependencies: `uv pip install -r pyproject.toml --no-cache`
- Lock dependencies: `uv pip freeze > uv.lock`

### Environment Validation Checks
- Python version check: `python --version` >= 3.11
- Taskfile installation check: `task --version` >= 3.0
- uv installation check: `uv --version`
- Podman availability check: `podman --version`
- Git installation check: `git --version`
- Virtual environment activation test: Source `.venv/bin/activate` and verify
- Dependency import test: `python -c "import fastapi; import pydantic"` within venv
- File permission check: Write test file to verify `.venv/` permissions
- Taskfile functionality test: `task --list` displays available tasks

### Configuration Management
- Read `.env.example` template
- Parse key-value pairs
- Generate `.env` with defaults
- Preserve any existing `.env` values (merge, don't overwrite)

## Acceptance Criteria

**Format:** Gherkin (Given-When-Then)

### Scenario 1: Successful setup on macOS
**Given** a developer with macOS Sonoma+ and Devbox preinstalled
**When** they run `devbox shell` and then `scripts/setup.nu` in interactive mode
**Then** the script completes successfully in <30 minutes
**And** the virtual environment exists at `.venv/`
**And** Taskfile 3.0+ is installed and functional
**And** all dependencies from `pyproject.toml` are installed
**And** the `.env` file exists with default values
**And** the success message displays next steps (run `task setup` for future runs, use `task --list` to see commands)

### Scenario 2: Successful setup on Linux
**Given** a developer with Ubuntu 22.04+ and Devbox preinstalled
**When** they run `devbox shell` and then `scripts/setup.nu` in interactive mode
**Then** the script completes successfully with identical behavior to macOS
**And** all validation checks pass including Taskfile availability

### Scenario 3: Successful setup on Windows WSL2
**Given** a developer with Windows 11 WSL2 (Ubuntu distribution) and Devbox preinstalled
**When** they run `devbox shell` and then `scripts/setup.nu` in interactive mode
**Then** the script completes successfully with identical behavior to Linux
**And** all validation checks pass including Taskfile availability

### Scenario 4: Silent mode for CI/automation
**Given** a CI/CD pipeline or developer running setup in automation
**When** they run `scripts/setup.nu --silent` within Devbox shell
**Then** the script executes without prompts
**And** all configuration options use sensible defaults
**And** Taskfile is installed if not present
**And** the setup completes successfully with return code 0

### Scenario 5: Missing prerequisite detection
**Given** Python 3.11+ is not available in Devbox environment
**When** developer runs `scripts/setup.nu`
**Then** the script detects missing prerequisite
**And** displays error message: "Python 3.11+ not found. Please check devbox.json configuration."
**And** provides link to Devbox documentation for adding Python
**And** script exits with return code 1

### Scenario 6: Network failure handling
**Given** network connection fails during dependency download
**When** uv dependency installation encounters network error
**Then** the script retries up to 3 times with exponential backoff (1s, 2s, 4s)
**And** if retries exhausted, displays error with offline installation guidance
**And** script exits with return code 1

### Scenario 7: Interactive prompts with defaults
**Given** a developer runs `scripts/setup.nu` in interactive mode
**When** the script prompts for IDE setup preference
**Then** the prompt displays: "Configure VS Code with standard extensions? [Y/n] (default: Y)"
**And** pressing Enter accepts default (Y)
**And** entering "n" skips IDE setup
**And** the chosen preference is applied correctly

### Scenario 8: Progress indicators
**Given** a developer runs `scripts/setup.nu`
**When** long-running operations execute (dependency installation)
**Then** the script displays verbose output showing each package being installed
**And** displays progress indicator showing overall completion percentage
**And** provides estimated time remaining for operation

### Scenario 9: Idempotent execution
**Given** a developer has already run `scripts/setup.nu` successfully
**When** they run the script again
**Then** the script detects existing setup (including Taskfile)
**And** skips already-completed steps
**And** completes successfully without errors
**And** execution time <2 minutes (validation only)

### Scenario 10: Environment health validation
**Given** the setup script completes all installation steps
**When** the validation phase executes
**Then** the script verifies Python version >= 3.11
**And** verifies Taskfile installed and functional (`task --version` >= 3.0)
**And** verifies all dependencies importable in virtual environment
**And** verifies `.env` file exists with required keys
**And** verifies pre-commit hooks installed
**And** runs `task --list` to validate Taskfile configuration
**And** displays validation report showing all checks passed

### Scenario 11: Taskfile not available
**Given** Taskfile is not installed and cannot be downloaded (e.g., network failure)
**When** developer runs `scripts/setup.nu`
**Then** the script detects Taskfile unavailability
**And** displays error message: "Taskfile installation failed. Please install manually: [installation instructions]"
**And** provides link to Taskfile installation documentation
**And** script continues with other setup steps (degraded mode)
**And** displays warning in final output: "⚠️ Taskfile not available - use direct tool commands (see CLAUDE-tooling.md)"

## Definition of Done

- [ ] Code implemented in `scripts/setup.nu` using NuShell
- [ ] Separate NuShell modules for OS detection, prerequisite checking (including Taskfile), dependency installation, configuration, validation
- [ ] Taskfile installation logic implemented with cross-platform support (macOS, Linux, WSL2)
- [ ] Unit tests written for testable NuShell functions (80% coverage minimum)
- [ ] Integration test validates complete setup flow on all supported platforms (macOS, Linux, WSL2)
- [ ] Integration test validates Taskfile installation and functionality
- [ ] Documentation added to `docs/SETUP.md` covering usage, flags, troubleshooting (including Taskfile installation)
- [ ] All 11 acceptance criteria scenarios validated manually on each platform
- [ ] Code review completed with no unresolved comments
- [ ] Pre-commit hooks pass (Ruff, mypy, tests)
- [ ] CI/CD pipeline validates script execution in GitHub Actions Ubuntu runner
- [ ] Taskfile validation added to CI/CD pipeline health checks
- [ ] Product owner (Tech Lead) approval obtained

## Additional Information

**Suggested Labels:** setup, automation, devops, foundation, cross-platform, taskfile

**Estimated Story Points:** 6 (High complexity due to cross-platform requirements, comprehensive error handling, and Taskfile integration)

**Dependencies:**
- **Story Dependencies:** US-002 (Repository Directory Structure) must complete first - setup script populates structure and Taskfile.yml must exist
- **Technical Dependencies:**
  - Devbox installed on developer machine (prerequisite)
  - NuShell available in Devbox environment (configured via devbox.json)
  - Taskfile 3.0+ available or installable (will be installed by script)
  - uv available or installable via curl/wget
  - Internet connectivity for dependency downloads

**Related PRD Sections:**
- PRD-000 v3 Section 6.1: User Flows - Flow 1 (New Developer Environment Setup)
- PRD-000 v3 Section 8: Technical Considerations - Dependencies
- PRD-000 v3 FR-22: Unified CLI interface via Taskfile

## Open Questions & Implementation Uncertainties

No open implementation questions. All technical approaches clear from Implementation Research and PRD-000 v3.

The following implementation decisions have been made in PRD-000 v3 Decisions section:
- **D3:** Sensible defaults with interactive prompts confirmed
- **D8:** Taskfile as unified CLI interface - must be installed during setup

## Changes from v1

**Version 2.0 Changes (Taskfile Integration):**

**Functional Requirements:**
- Added Taskfile 3.0+ to prerequisite validation list
- Added Taskfile installation to core setup capabilities
- Added Taskfile functionality test to environment validation checks
- Updated success message to mention `task --list` for command discovery

**Technical Requirements:**
- Added "Taskfile Installation" section with cross-platform installation logic
- Updated "Environment Validation Checks" to include Taskfile verification
- Updated "Technical Dependencies" to include Taskfile 3.0+

**Acceptance Criteria:**
- Updated Scenario 1, 2, 3 to verify Taskfile 3.0+ installed and functional
- Updated Scenario 4 to ensure Taskfile installed in silent mode
- Updated Scenario 9 to check existing Taskfile during idempotent execution
- Updated Scenario 10 to validate Taskfile with `task --version` and `task --list`
- Added Scenario 11 for Taskfile installation failure handling

**Definition of Done:**
- Added Taskfile installation logic requirement
- Added Taskfile integration tests requirement
- Added Taskfile validation to CI/CD pipeline
- Added Taskfile documentation to SETUP.md

**Parent PRD:**
- Updated link from PRD-000 v2 to PRD-000 v3
- Added FR-22 to functional requirements coverage

**Estimated Story Points:**
- Unchanged at 6 SP (Taskfile installation adds minimal complexity - similar to uv installation)

**Rationale for Changes:**
- Addresses PRD-000 v3 FR-22 requirement for unified CLI interface
- Ensures developers have `task` commands available immediately after setup
- Aligns with CLAUDE-tooling.md standards documenting Taskfile as primary interface
- Eliminates manual Taskfile installation step, maintaining <30 minute setup target
- Supports degraded mode if Taskfile unavailable (script continues, warns user)

---

**Version History:**
- v1.0 (2025-10-13): Initial version with NuShell setup script, interactive prompts
- v2.0 (2025-10-14): Added Taskfile integration - installation, validation, documentation
