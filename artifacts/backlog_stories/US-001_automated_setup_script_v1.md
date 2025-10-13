# User Story: Automated Setup Script with Interactive Prompts

## Metadata
- **Story ID:** US-001
- **Title:** Create Automated Setup Script (NuShell) with Interactive Prompts
- **Type:** Feature
- **Status:** Backlog
- **Priority:** Critical - Foundation enabler blocking all feature development
- **Parent PRD:** PRD-000
- **Parent High-Level Story:** HLS-001
- **Functional Requirements Covered:** FR-01, FR-03, FR-19, FR-20
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** PRD-000: Project Foundation & Bootstrap Infrastructure
- **Link:** /artifacts/prds/PRD-000_project_foundation_bootstrap_v2.md
- **PRD Section:** Section 6.1 - User Flows (Flow 1: New Developer Environment Setup)
- **Functional Requirements Coverage:**
  - **FR-01:** Automated environment setup script supporting macOS, Linux, and Windows (WSL2)
  - **FR-03:** Python 3.11+ virtual environment with automated dependency management via uv
  - **FR-19:** Cross-platform scripting with NuShell
  - **FR-20:** Isolated dev environments with Devbox

**Parent High-Level Story:** HLS-001: Automated Development Environment Setup
- **Link:** /artifacts/hls/HLS-001_automated_dev_environment_setup_v2.md
- **HLS Section:** Section 8 - Decomposition into Backlog Stories (Story #1)

## User Story

As a developer joining the project, I want to run a single automated setup script that handles all environment configuration, so that I can achieve a working development environment in under 30 minutes without manual troubleshooting.

## Description

This story implements the core automation script (`scripts/setup.nu`) that orchestrates complete development environment setup within a Devbox isolated environment. The script performs operating system detection, prerequisite validation, dependency installation, virtual environment configuration, and environment health checks—all through an interactive command-line interface with sensible defaults for automation scenarios.

The script bridges the gap between "repository cloned" and "environment ready for development" states, eliminating multi-hour manual configuration processes and "works on my machine" failures through reproducible, automated setup within Devbox containers.

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
- Validate prerequisites within Devbox environment (Python 3.11+, Podman, Git, uv)
- Install uv package manager if not present in Devbox environment
- Create Python virtual environment at `.venv/` using Python 3.11+
- Install all dependencies from `pyproject.toml` using uv for reproducible builds
- Configure pre-commit hooks for automated code quality checks
- Copy `.env.example` to `.env` with default environment variable values
- Validate environment health through automated checks (Python version, dependency installation, file permissions)

### Interactive Configuration
- Prompt user for configuration options (IDE setup preference, verbose/silent mode, database setup)
- Provide sensible defaults for all prompts enabling quick setup via Enter key
- Support `--silent` flag for non-interactive mode using all defaults (CI/automation scenarios)
- Display clear help text for each configuration option

### Progress Feedback
- Display verbose output showing detailed step information (what's being installed, where files are written)
- Show progress indicators (progress bars or percentage complete) for long-running operations
- Provide estimated time remaining for multi-minute operations
- Output success message with clear next steps upon completion

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
  - Dependency installation
  - Environment configuration
  - Health check validation

### NuShell Implementation
- Use NuShell built-in commands for cross-platform file operations
- Leverage NuShell's structured data types for progress tracking
- Implement error handling using NuShell's `try-catch` pattern
- Use NuShell pipes for chaining operations efficiently

### uv Package Manager Integration
- Install uv if not present: Check system PATH, download via curl/wget, verify installation
- Create virtual environment: `uv venv .venv --python 3.11`
- Install dependencies: `uv pip install -r pyproject.toml --no-cache`
- Lock dependencies: `uv pip freeze > uv.lock`

### Environment Validation Checks
- Python version check: `python --version` >= 3.11
- uv installation check: `uv --version`
- Podman availability check: `podman --version`
- Git installation check: `git --version`
- Virtual environment activation test: Source `.venv/bin/activate` and verify
- Dependency import test: `python -c "import fastapi; import pydantic"` within venv
- File permission check: Write test file to verify `.venv/` permissions

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
**And** all dependencies from `pyproject.toml` are installed
**And** the `.env` file exists with default values
**And** the success message displays next steps (run server, review docs)

### Scenario 2: Successful setup on Linux
**Given** a developer with Ubuntu 22.04+ and Devbox preinstalled
**When** they run `devbox shell` and then `scripts/setup.nu` in interactive mode
**Then** the script completes successfully with identical behavior to macOS
**And** all validation checks pass

### Scenario 3: Successful setup on Windows WSL2
**Given** a developer with Windows 11 WSL2 (Ubuntu distribution) and Devbox preinstalled
**When** they run `devbox shell` and then `scripts/setup.nu` in interactive mode
**Then** the script completes successfully with identical behavior to Linux
**And** all validation checks pass

### Scenario 4: Silent mode for CI/automation
**Given** a CI/CD pipeline or developer running setup in automation
**When** they run `scripts/setup.nu --silent` within Devbox shell
**Then** the script executes without prompts
**And** all configuration options use sensible defaults
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
**Then** the script detects existing setup
**And** skips already-completed steps
**And** completes successfully without errors
**And** execution time <2 minutes (validation only)

### Scenario 10: Environment health validation
**Given** the setup script completes all installation steps
**When** the validation phase executes
**Then** the script verifies Python version >= 3.11
**And** verifies all dependencies importable in virtual environment
**And** verifies `.env` file exists with required keys
**And** verifies pre-commit hooks installed
**And** displays validation report showing all checks passed

## Definition of Done

- [ ] Code implemented in `scripts/setup.nu` using NuShell
- [ ] Separate NuShell modules for OS detection, prerequisite checking, dependency installation, configuration, validation
- [ ] Unit tests written for testable NuShell functions (80% coverage minimum)
- [ ] Integration test validates complete setup flow on all supported platforms (macOS, Linux, WSL2)
- [ ] Documentation added to `docs/SETUP.md` covering usage, flags, troubleshooting
- [ ] All 10 acceptance criteria scenarios validated manually on each platform
- [ ] Code review completed with no unresolved comments
- [ ] Pre-commit hooks pass (Ruff, mypy, tests)
- [ ] CI/CD pipeline validates script execution in GitHub Actions Ubuntu runner
- [ ] Product owner (Tech Lead) approval obtained

## Additional Information

**Suggested Labels:** setup, automation, devops, foundation, cross-platform

**Estimated Story Points:** 6 (High complexity due to cross-platform requirements and comprehensive error handling)

**Dependencies:**
- **Story Dependencies:** US-002 (Repository Directory Structure) must complete first - setup script populates structure
- **Technical Dependencies:**
  - Devbox installed on developer machine (prerequisite)
  - NuShell available in Devbox environment (configured via devbox.json)
  - uv available or installable via curl/wget
  - Internet connectivity for dependency downloads

**Related PRD Sections:**
- PRD-000 Section 6.1: User Flows - Flow 1 (New Developer Environment Setup)
- PRD-000 Section 8: Technical Considerations - Dependencies

## Open Questions & Implementation Uncertainties

No open implementation questions. All technical approaches clear from Implementation Research and PRD-000 v2.

The following implementation decisions have been made in PRD-000 v2 Decisions section:
- **D3:** Sensible defaults with interactive prompts confirmed
- **D4:** uv package manager confirmed for dependency management
- **D7:** Podman container approach for database (handled in separate story)

All prerequisite decisions documented. Implementation path is clear.

---

## Traceability

### Source Documents
- **Parent HLS:** HLS-001 v2 - Automated Development Environment Setup (Story #1 in Decomposition)
- **Parent PRD:** PRD-000 v2 - Section 6.1 User Flow 1 (Environment Setup)
- **Implementation Research:** §2.1 (Python 3.11+), §2.2 (FastAPI), §7.1 (Testing), §8.1-8.2 (Pitfalls/Anti-patterns)

### Requirements Mapping
- HLS-001 AC1 (Rapid Setup <30min) → This story's performance NFR
- HLS-001 AC2 (Cross-Platform Compatibility) → Scenarios 1-3 (macOS, Linux, WSL2)
- HLS-001 AC3 (Verbose Progress Feedback) → Scenario 8
- HLS-001 AC4 (Interactive Prompts with Defaults) → Scenario 7
- HLS-001 AC5 (Silent Mode) → Scenario 4
- HLS-001 AC7 (Effective Error Handling) → Scenarios 5-6

### Implementation Decisions Applied
- **PRD-000 D3:** Interactive prompts with sensible defaults implemented
- **PRD-000 D4:** uv package manager integrated
- **HLS-001 D2:** Verbose output with progress indicators implemented
- **HLS-001 D3:** Silent mode with --silent flag supported

---

**Document Version:** v1.0
**Generated By:** Backlog Story Generator v1.3
**Generation Date:** 2025-10-13

---
