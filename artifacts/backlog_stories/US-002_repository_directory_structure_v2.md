# User Story: Establish Repository Directory Structure

## Metadata
- **Story ID:** US-002
- **Title:** Establish Repository Directory Structure
- **Type:** Technical Foundation
- **Status:** Backlog
- **Priority:** Critical - Blocks US-001 (setup script requires structure to populate)
- **Parent PRD:** PRD-000
- **Parent High-Level Story:** HLS-001
- **Functional Requirements Covered:** FR-02, FR-22 (reference only)
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md
- **Version:** v2.0

## Parent Artifact Context

**Parent PRD:** PRD-000: Project Foundation & Bootstrap Infrastructure
- **Link:** /artifacts/prds/PRD-000_project_foundation_bootstrap_v3.md
- **PRD Section:** Section 8 - Technical Considerations (Repository Structure)
- **Functional Requirements Coverage:**
  - **FR-02:** Standardized repository directory structure following Python src layout
  - **FR-22:** Unified CLI interface via Taskfile (reference only)

**Parent High-Level Story:** HLS-001: Automated Development Environment Setup
- **Link:** /artifacts/hls/HLS-001_automated_dev_environment_setup_v2.md
- **HLS Section:** Section 8 - Decomposition into Backlog Stories (Story #2)

## User Story

As a developer setting up the project, I want a well-organized repository directory structure following Python src layout standards including the Taskfile.yml for unified CLI access, so that I can easily navigate the codebase and the setup script can populate directories correctly.

## Description

This story establishes the foundational repository directory structure that all subsequent development work will build upon. The structure follows Python src layout best practices as documented in CLAUDE-architecture.md, providing clear separation between source code, tests, documentation, configuration, and project artifacts.

The directory structure serves multiple purposes: (1) enables the automated setup script (US-001) to populate directories correctly, (2) provides intuitive navigation for developers at all experience levels, (3) establishes conventions that scale as the project grows, (4) aligns with industry-standard Python project organization patterns, and (5) includes the Taskfile.yml unified CLI interface.

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§2.1: Python 3.11+ Technology Stack:** Structure supports Python package management with src layout preventing common import issues
- **§2.2: FastAPI Framework:** Directory structure accommodates FastAPI application organization (api/, models/, services/)
- **§3.1: Microservices Architecture:** Structure supports service-oriented decomposition with clear module boundaries

**Project Structure Alignment:**
- **CLAUDE-architecture.md:** Repository structure follows documented src layout pattern with standardized subdirectory organization
- **CLAUDE-tooling.md:** Taskfile.yml provides unified CLI interface for all development operations

## Functional Requirements

### Directory Structure Creation
- Create root-level directories: `src/`, `tests/`, `docs/`, `scripts/`, `.github/workflows/`
- Create Python package structure under `src/` with proper `__init__.py` files
- Create test organization under `tests/` with subdirectories for unit, integration, and e2e tests
- Create documentation structure under `docs/` for setup guides, architecture docs, and API references
- Create scripts directory for automation scripts (NuShell setup scripts, deployment scripts)
- Preserve existing directories: `artifacts/`, `prompts/`, `.claude/`, `feedback/`
- **Note:** Taskfile.yml already exists - verify presence and document in structure

### Python Package Structure (src/ layout)
- Create `src/ai_agent_mcp_server/` as main package directory
- Create subdirectories with appropriate `__init__.py` files:
  - `src/ai_agent_mcp_server/core/` - Core business logic and constants
  - `src/ai_agent_mcp_server/models/` - Data models (SQLAlchemy, Pydantic)
  - `src/ai_agent_mcp_server/services/` - Business services layer
  - `src/ai_agent_mcp_server/repositories/` - Data access layer (Repository pattern)
  - `src/ai_agent_mcp_server/tools/` - MCP tool implementations
  - `src/ai_agent_mcp_server/api/` - API endpoints and routes
  - `src/ai_agent_mcp_server/utils/` - Shared utilities
- Create `src/ai_agent_mcp_server/__main__.py` for module execution support
- Create `src/ai_agent_mcp_server/main.py` as FastAPI application entry point
- Create `src/ai_agent_mcp_server/config.py` for configuration management

### Test Structure
- Create `tests/conftest.py` for pytest fixtures
- Create `tests/unit/` for unit tests
- Create `tests/integration/` for integration tests
- Create `tests/e2e/` for end-to-end tests
- Mirror source structure in test directories (e.g., `tests/unit/test_tools/`)

### Documentation Structure
- Create `docs/CONTRIBUTING.md` placeholder for development workflow guide
- Create `docs/SETUP.md` placeholder for environment setup guide
- Create `docs/ARCHITECTURE.md` placeholder for system architecture documentation
- Create `docs/API.md` placeholder for API documentation

### Configuration Files Structure
- Create `.env.example` template for environment variables
- Create `.gitignore` with Python, IDE, and OS-specific exclusions
- Create `.dockerignore` (mapped to Containerfile) with build exclusions
- Preserve existing files: `pyproject.toml`, `CLAUDE.md`, `TODO.md`, `README.md`, `Taskfile.yml`

### Placeholder Files
- Create `.gitkeep` files in empty directories to preserve structure in git
- Create placeholder `__init__.py` files with docstrings indicating module purpose
- Create placeholder `README.md` files in major directories explaining contents

## Non-Functional Requirements

- **Maintainability:** Structure must accommodate growth to 50+ tools and 10,000+ lines of code without requiring reorganization
- **Navigability:** Developers unfamiliar with codebase should locate files intuitively following standard Python conventions
- **Scalability:** Directory organization must support future modularization and potential service extraction
- **Standards Compliance:** Structure must match CLAUDE-architecture.md documented patterns exactly
- **CLI Consistency:** Taskfile.yml presence enables unified `task <command>` interface per CLAUDE-tooling.md

## Technical Requirements

### Directory Tree Structure

```
ai-agent-mcp-server/
├── .github/
│   └── workflows/              # GitHub Actions CI/CD pipelines
│       └── .gitkeep
├── .claude/                    # Existing - Claude Code configuration
├── src/
│   └── ai_agent_mcp_server/
│       ├── __init__.py         # Package root
│       ├── __main__.py         # Entry point for -m execution
│       ├── main.py             # FastAPI application entry point
│       ├── config.py           # Configuration management (Pydantic)
│       ├── core/               # Core business logic
│       │   ├── __init__.py
│       │   ├── exceptions.py   # Custom exception classes
│       │   └── constants.py    # Application constants
│       ├── models/             # Data models (SQLAlchemy)
│       │   └── __init__.py
│       ├── services/           # Business services layer
│       │   └── __init__.py
│       ├── repositories/       # Data access layer (Repository pattern)
│       │   ├── __init__.py
│       │   └── base.py         # Base repository interface
│       ├── tools/              # MCP tool implementations
│       │   ├── __init__.py
│       │   └── .gitkeep
│       ├── api/                # API endpoints
│       │   ├── __init__.py
│       │   ├── routes/         # Route handlers
│       │   │   └── __init__.py
│       │   └── schemas/        # Pydantic schemas
│       │       └── __init__.py
│       └── utils/              # Shared utilities
│           └── __init__.py
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   ├── unit/                   # Unit tests
│   │   ├── __init__.py
│   │   └── test_tools/
│   │       └── __init__.py
│   ├── integration/            # Integration tests
│   │   └── __init__.py
│   └── e2e/                    # End-to-end tests
│       └── __init__.py
├── docs/
│   ├── CONTRIBUTING.md         # Development workflow guide (placeholder)
│   ├── SETUP.md                # Environment setup guide (placeholder)
│   ├── ARCHITECTURE.md         # System architecture documentation (placeholder)
│   └── API.md                  # API documentation (placeholder)
├── scripts/
│   ├── setup.nu                # NuShell setup script (to be created in US-001)
│   └── .gitkeep
├── prompts/                    # Existing - MCP server prompts
│   └── CLAUDE/                 # Existing - Specialized CLAUDE.md files
├── artifacts/                  # Existing - Generated SDLC artifacts
├── feedback/                   # Existing - Human critique logs
├── Taskfile.yml                # Existing - Unified CLI interface (60+ tasks)
├── .env.example                # Environment variable template
├── .gitignore                  # Git exclusions
├── .dockerignore               # Containerfile build exclusions
├── devbox.json                 # Devbox configuration (to be created in US-003)
├── devbox.lock                 # Devbox locked dependencies (generated)
├── pyproject.toml              # Existing - Python dependencies and metadata
├── uv.lock                     # Existing - UV locked dependencies
├── Containerfile               # Podman/Docker image definition (to be created)
├── .pre-commit-config.yaml     # Pre-commit hooks configuration (to be created)
├── renovate.json               # Renovate dependency automation config (to be created)
├── README.md                   # Existing - Project overview
├── CLAUDE.md                   # Existing - Core CLAUDE configuration
└── TODO.md                     # Existing - Master plan
```

### File Content Templates

#### __init__.py (Package Root)
```python
"""
AI Agent MCP Server

A production-ready Model Context Protocol (MCP) server providing AI agents
with comprehensive tool access for project management, code analysis, and
development workflow automation.
"""

__version__ = "0.1.0"
```

#### __init__.py (Subdirectory Example - core/)
```python
"""
Core business logic module.

Contains application constants, custom exceptions, and fundamental business rules.
"""
```

#### .gitignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/
env/

# UV
uv.lock
.uv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json

# Ruff
.ruff_cache/

# Logs
*.log
```

#### .dockerignore
```
# Development files
.venv/
venv/
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Documentation
docs/
*.md

# Git
.git/
.gitignore

# IDE
.vscode/
.idea/

# CI/CD
.github/

# Project artifacts
artifacts/
feedback/

# Environment
.env
.env.*
!.env.example

# Tests
tests/
```

#### .env.example
```
# Application Configuration
APP_NAME="AI Agent MCP Server"
APP_VERSION="0.1.0"
DEBUG=false

# Server Configuration
HOST="0.0.0.0"
PORT=8000

# Database Configuration (Future use)
DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/mcp"

# Logging Configuration
LOG_LEVEL="INFO"
LOG_FORMAT="json"

# Security (Replace with actual values)
SECRET_KEY="change-me-in-production"
```

## Acceptance Criteria

**Format:** Gherkin (Given-When-Then)

### Scenario 1: Complete directory structure created
**Given** a fresh repository clone
**When** the repository structure is established
**Then** all directories from the specification exist
**And** all `__init__.py` files exist in Python packages
**And** all placeholder documentation files exist

### Scenario 2: Python src layout validated
**Given** the repository structure is established
**When** a developer examines the `src/` directory
**Then** the structure follows Python src layout with `src/ai_agent_mcp_server/` as the main package
**And** all subdirectories under `ai_agent_mcp_server/` have `__init__.py` files
**And** the package is importable without issues

### Scenario 3: Test structure mirrors source structure
**Given** the repository structure is established
**When** a developer examines the `tests/` directory
**Then** subdirectories exist for unit, integration, and e2e tests
**And** `tests/conftest.py` exists for shared fixtures
**And** test directories mirror the source structure (e.g., `tests/unit/test_tools/` mirrors `src/ai_agent_mcp_server/tools/`)

### Scenario 4: Configuration files present
**Given** the repository structure is established
**When** a developer examines the root directory
**Then** `.env.example` exists with documented configuration options
**And** `.gitignore` exists with Python, IDE, and OS exclusions
**And** `.dockerignore` exists with build exclusions

### Scenario 5: Documentation placeholders created
**Given** the repository structure is established
**When** a developer examines the `docs/` directory
**Then** placeholder files exist for CONTRIBUTING.md, SETUP.md, ARCHITECTURE.md, and API.md
**And** each placeholder contains a header and brief description of planned content

### Scenario 6: Git tracking of empty directories
**Given** the repository structure is established
**When** the repository is committed to git
**Then** empty directories are preserved via `.gitkeep` files
**And** all directories are tracked in version control

### Scenario 7: Existing directories preserved
**Given** the repository structure is established
**When** a developer examines the repository
**Then** existing directories (`artifacts/`, `prompts/`, `.claude/`, `feedback/`) are preserved
**And** existing files (`CLAUDE.md`, `TODO.md`, `README.md`, `pyproject.toml`, `Taskfile.yml`) are unchanged

### Scenario 8: CLAUDE-architecture.md compliance
**Given** the repository structure is established
**When** a developer compares the structure to CLAUDE-architecture.md
**Then** the directory organization matches the documented src layout pattern
**And** all subdirectory purposes align with documented conventions

### Scenario 9: Taskfile.yml verified present
**Given** the repository structure is established
**When** a developer examines the root directory
**Then** Taskfile.yml exists
**And** running `task --list` displays available development tasks
**And** Taskfile.yml is documented as part of the standard repository structure

## Definition of Done

- [ ] All directories from specification created
- [ ] All `__init__.py` files created with docstrings
- [ ] All placeholder documentation files created
- [ ] `.env.example` created with documented configuration
- [ ] `.gitignore` created with comprehensive exclusions
- [ ] `.dockerignore` created with build exclusions
- [ ] `.gitkeep` files added to empty directories
- [ ] Taskfile.yml presence verified
- [ ] Structure validated against CLAUDE-architecture.md
- [ ] Structure validated against PRD-000 v3 repository structure diagram
- [ ] Manual walkthrough completed confirming intuitive navigation
- [ ] Git commit created capturing structure establishment
- [ ] Code review completed with no unresolved comments
- [ ] Product owner (Tech Lead) approval obtained

## Additional Information

**Suggested Labels:** foundation, infrastructure, project-structure, python, taskfile

**Estimated Story Points:** 2 (Low-Medium complexity - straightforward directory creation with attention to detail)

**Dependencies:**
- **Story Dependencies:** None - This is the foundation story that other stories depend on
- **Blocked Stories:** US-001 (Automated Setup Script) requires this structure
- **Technical Dependencies:** None - Pure filesystem operations
- **Pre-existing:** Taskfile.yml previously created

**Related PRD Sections:**
- PRD-000 v3 Section 8: Technical Considerations - Repository Structure
- PRD-000 v3 FR-22: Unified CLI interface via Taskfile
- CLAUDE-architecture.md: Project Structure Philosophy
- CLAUDE-tooling.md: Taskfile documentation

## Open Questions & Implementation Uncertainties

No open implementation questions. Directory structure is fully specified in PRD-000 v3 Section 8 and CLAUDE-architecture.md.

**Implementation Notes:**
- Use `mkdir -p` for nested directory creation
- Python `pathlib` library recommended for cross-platform path handling if scripting
- Preserve existing directories and files (including Taskfile.yml)
- Focus on creating structure; content creation deferred to subsequent stories
- Taskfile.yml already exists - verify presence and functionality as part of acceptance criteria

---

## Traceability

### Source Documents
- **Parent HLS:** HLS-001 v2 - Automated Development Environment Setup (Story #2 in Decomposition)
- **Parent PRD:** PRD-000 v3 - Section 8 Technical Considerations (Repository Structure diagram)
- **CLAUDE-architecture.md:** Standard Project Structure section
- **CLAUDE-tooling.md:** Taskfile unified CLI interface documentation

### Requirements Mapping
- HLS-001 In Scope → FR-02 (Standardized repository directory structure)
- PRD-000 v3 FR-02 → This story's directory structure specification
- PRD-000 v3 FR-22 → Taskfile.yml presence verification (reference only)
- CLAUDE-architecture.md src layout → This story's Python package structure
- CLAUDE-tooling.md Taskfile → Unified CLI interface

### Implementation Decisions Applied
- **PRD-000 v3 Technical Constraints:** Python 3.11+ with src layout
- **PRD-000 v3 Decision D8:** Taskfile as unified CLI interface
- **CLAUDE-architecture.md:** Standard src layout with service-oriented subdirectories
- **CLAUDE-tooling.md:** Taskfile provides language-agnostic CLI facade

---

## Changes from v1

**Version 2.0 Changes (PRD-000 v3 Alignment and Taskfile Integration):**

**Parent PRD:**
- Updated link from PRD-000 v2 to PRD-000 v3

**Functional Requirements Coverage:**
- Added FR-22 (Unified CLI interface via Taskfile) as reference-only coverage

**User Story:**
- Added mention of Taskfile.yml for unified CLI access

**Description:**
- Added note that Taskfile.yml is included in structure

**Functional Requirements:**
- Added note that Taskfile.yml already exists
- Added Taskfile.yml to preserved files list

**Directory Tree Structure:**
- Added Taskfile.yml with note "Existing - Unified CLI interface (60+ tasks)"

**Acceptance Criteria:**
- Added Scenario 9: Taskfile.yml verified present (with `task --list` validation)
- Updated Scenario 7 to include Taskfile.yml in preserved files list

**Definition of Done:**
- Added "Taskfile.yml presence verified"
- Added "Structure validated against PRD-000 v3 repository structure diagram"

**Additional Information:**
- Added "taskfile" to suggested labels
- Added note about Taskfile.yml pre-existing

**Related PRD Sections:**
- Updated references from PRD-000 v2 to PRD-000 v3
- Added reference to PRD-000 v3 FR-22
- Added reference to CLAUDE-tooling.md Taskfile documentation

**Open Questions:**
- Updated reference from "PRD-000 v2" to "PRD-000 v3"

**Implementation Notes:**
- Added note about preserving Taskfile.yml
- Added note about verifying Taskfile.yml functionality

**Traceability:**
- Updated Parent PRD reference from v2 to v3
- Added FR-22 to Requirements Mapping
- Added CLAUDE-tooling.md to Source Documents
- Added PRD-000 v3 Decision D8 to Implementation Decisions

**Rationale for Changes:**
- Aligns US-002 with PRD-000 v3 which includes Taskfile.yml in repository structure
- Documents that Taskfile.yml already exists (no creation work needed)
- Ensures story verifies presence and functionality of unified CLI interface
- Maintains story as lightweight (2 SP) - no Taskfile creation, just verification

---

**Document Version:** v2.0
**Generated By:** Manual update from US-002 v1.0
**Update Date:** 2025-10-14

---
