# CLAUDE-tooling.md - Development Tools & Configuration

> **Specialized Guide**: Comprehensive tooling setup for Python development with UV, Ruff, MyPy, and pytest.
>
> **Taskfile Interface**: All CLI commands are consolidated in `/Taskfile.yml` for consistent cross-platform execution. Use `task <command>` as the primary interface; individual tool commands documented below for understanding and configuration.

---

## 🎯 Taskfile - Unified CLI Interface

### Why Taskfile?
Taskfile provides a unified interface for all development operations:
- **Cross-platform consistency** - Same commands work on macOS, Linux, Windows
- **Self-documenting** - `task --list` shows all available commands
- **Language-agnostic** - Works across Python, Go, Rust, or any future tech stack
- **Simple YAML** - Easy to read, extend, and maintain
- **No dependencies** - Single binary, no runtime requirements

**Philosophy**: Taskfile is the common facade for ALL CLI operations. Individual tools (uv, ruff, mypy, pytest) are implementation details abstracted behind Taskfile tasks.

### Installation

```bash
# macOS
brew install go-task

# Linux (via snap)
snap install task --classic

# Linux (via sh script)
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin

# Windows (via Scoop)
scoop install task

# Or add to Devbox (recommended)
devbox add go-task
```

### Essential Commands

```bash
# Show all available tasks
task --list

# Show detailed task information
task --list-all

# Run specific task
task <task-name>

# Pass arguments to task
task deps:add -- PKG=requests
```

### Common Development Tasks

#### Code Quality
```bash
# Run linter (check only)
task lint

# Run linter with auto-fix
task lint:fix

# Run linter in watch mode
task lint:watch

# Format code
task format

# Check formatting without changes
task format:check

# Run both linting and formatting
task lint:all
```

#### Type Checking
```bash
# Run MyPy type checker (strict mode)
task type-check

# Generate type coverage report
task type-check:report

# Install missing type stubs
task type-check:install
```

#### Testing
```bash
# Run all tests with coverage
task test

# Run unit tests only
task test:unit

# Run integration tests only
task test:integration

# Run e2e tests only
task test:e2e

# Run tests in watch mode
task test:watch

# Run only last failed tests
task test:failed

# Run tests with coverage enforcement (80%+)
task test:coverage

# Run tests in parallel
task test:parallel
```

#### Quality Checks (All)
```bash
# Run all quality checks (lint, format, type, test)
task check

# Run CI/CD pipeline checks
task check:ci
```

#### Dependency Management
```bash
# Install dependencies
task deps:install

# Install all dependencies including extras
task deps:install:all

# Add new dependency
task deps:add -- PKG=requests

# Add dev dependency
task deps:add:dev -- PKG=pytest-watch

# Remove dependency
task deps:remove -- PKG=requests

# Update dependencies
task deps:update

# Export to requirements.txt
task deps:export
```

#### Pre-commit Hooks
```bash
# Install pre-commit hooks
task hooks:install

# Run hooks on all files
task hooks:run

# Update hook versions
task hooks:update
```

#### Build & Run
```bash
# Build Python package
task build

# Run application
task run -- SCRIPT=main.py

# Start development server
task dev

# Start Python REPL
task shell
```

#### Container Operations (Podman)
```bash
# Build container image
task container:build

# Run application container
task container:run

# Stop container
task container:stop

# View container logs
task container:logs

# Execute shell in container
task container:shell

# Clean containers and images
task container:clean

# Scan container for security vulnerabilities (all severities)
task container:scan

# Scan for critical and high severity vulnerabilities only
task container:scan:critical

# Generate SARIF report for GitHub Security tab
task container:scan:sarif

# Generate JSON report for programmatic analysis
task container:scan:json
```

#### Container Security Scanning

**Scanner:** Trivy (Aqua Security)
**Purpose:** Detect vulnerabilities in container images before deployment

**Installation:**
```bash
# macOS
brew install aquasecurity/trivy/trivy

# Linux (Ubuntu/Debian)
sudo apt-get install wget apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy

# Docker/Podman (no installation)
alias trivy="docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy"
```

**Scanning Workflow:**
1. Build container image: `task container:build`
2. Scan for vulnerabilities: `task container:scan`
3. Review findings and remediate critical/high CVEs
4. Re-scan to verify fixes: `task container:scan:critical`

**Severity Policy (CI/CD):**
- **CRITICAL/HIGH:** Blocks deployment (build fails)
- **MEDIUM/LOW:** Logged as warnings, deployment continues
- **Unfixed vulnerabilities:** Ignored (no remediation available)

**Scan Scope:**
- OS packages (Alpine APK, Debian/Ubuntu APT, Red Hat RPM)
- Application dependencies (Python, Node.js, Go, Rust)
- Base image vulnerabilities
- Known CVEs from NVD, Red Hat, Debian, Alpine databases

**Local Development:**
```bash
# Full scan (all severities)
task container:scan

# Production-ready check (critical/high only)
task container:scan:critical

# Generate SARIF for GitHub Security tab
task container:scan:sarif

# Generate JSON for CI/CD integration
task container:scan:json OUTPUT_FILE=scan-results.json

# Scan specific tag
task container:scan TAG=v1.0.0
```

**CI/CD Integration:**
Container images are automatically scanned in GitHub Actions on every build. Scan results uploaded to **Repository → Security → Code Scanning**.

**Vulnerability Database:**
Trivy updates its vulnerability database daily. Force manual update:
```bash
trivy image --download-db-only
```

**Common Remediation Patterns:**
- **OS packages:** Update base image (`FROM python:3.11-alpine` → `FROM python:3.11-alpine3.19`)
- **Python dependencies:** Update in `pyproject.toml`, run `uv lock`, rebuild image
- **Unfixed CVEs:** Document as accepted risk or use alternative package

#### Database Operations (Podman)
```bash
# Start PostgreSQL database
task db:start

# Stop database
task db:stop

# Connect to database shell
task db:shell

# View database logs
task db:logs

# Restart database
task db:restart
```

#### Devbox Integration
```bash
# Enter Devbox shell
task devbox:shell

# Run command in Devbox
task devbox:run -- CMD=pytest

# Update Devbox packages
task devbox:update

# Show Devbox info
task devbox:info
```

#### Utilities
```bash
# Clean build artifacts and caches
task clean

# Clean everything including venv
task clean:all

# Initial project setup
task setup

# Show project environment info
task info

# Show help
task help
```

### Taskfile Structure

The Taskfile is organized into logical sections:
1. **Code Quality Tasks** - Linting and formatting
2. **Type Checking Tasks** - MyPy operations
3. **Testing Tasks** - All test operations
4. **Quality Check Tasks** - Combined checks
5. **Dependency Management** - UV operations
6. **Pre-commit Hooks** - Git hook operations
7. **Build & Run Tasks** - Application execution
8. **Container Tasks** - Podman build, run, and security scanning
9. **Database Tasks** - Database management
10. **Devbox Tasks** - Environment management
11. **Documentation Tasks** - Docs generation (placeholder)
12. **Utility Tasks** - Cleanup and setup

### Extending Taskfile

To add new tasks, edit `/Taskfile.yml`:

```yaml
tasks:
  my-task:
    desc: Description of what this task does
    cmds:
      - command to run
      - another command
    deps:
      - other-task  # Run this task first
```

**Best Practices**:
- Keep tasks focused (single responsibility)
- Use descriptive names with `:` separators (e.g., `test:unit`, `db:start`)
- Add `desc` field for `task --list` output
- Use variables for repeated values (defined in `vars:` section)
- Document complex tasks in comments

---

## 📦 UV Package Manager

### Why UV?
UV is a modern Python package manager written in Rust that offers:
- **10-100x faster** than pip and other traditional tools
- Drop-in replacement for pip, virtualenv, pyenv, poetry, and pipx
- Built-in Python version management
- Universal lock files for reproducible builds
- Workspace support for monorepos

### Essential pyproject.toml Configuration

```toml
[project]
name = "project-name"
version = "0.1.0"
description = "Project description"
readme = "README.md"
requires-python = ">=3.9"
license = { text = "MIT" }
authors = [
    { name = "Your Name", email = "you@example.com" }
]
keywords = ["python", "project"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "pydantic>=2.0.0",
    "click>=8.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-mock>=3.10.0",
    "mypy>=1.8.0",
    "ruff>=0.3.0",
    "pre-commit>=3.0.0",
]
test = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.10.0",
    "httpx>=0.24.0",
]
docs = [
    "mkdocs>=1.4.0",
    "mkdocs-material>=9.0.0",
    "sphinx>=7.0.0",
]

[project.scripts]
project-cli = "project_name.main:cli"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.version]
path = "src/project_name/__init__.py"

[tool.hatch.build.targets.wheel]
packages = ["src/project_name"]

[tool.uv]
managed = true
dev-dependencies = [
    "pytest>=8.0.0",
    "mypy>=1.8.0",
    "ruff>=0.3.0",
]
```

### UV Commands Reference

#### Installation
```bash
# Install UV (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install UV (with pipx)
pipx install uv
```

#### Project Initialization
```bash
# Create new project
uv init project-name
cd project-name

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # bash/zsh
.venv\Scripts\activate     # Windows
```

#### Dependency Management
```bash
# Install dependencies from pyproject.toml
uv sync

# Install with all extras
uv sync --all-extras

# Add production dependency
uv add requests

# Add development dependency
uv add --dev pytest

# Add optional dependency group
uv add --optional docs sphinx

# Remove dependency
uv remove requests

# Update lock file
uv lock

# Export requirements
uv export --format requirements-txt --output-file requirements.txt
```

#### Python Version Management
```bash
# Install Python version
uv python install 3.12

# List installed Python versions
uv python list

# Pin Python version for project
uv python pin 3.12

# Create venv with specific Python
uv venv --python 3.12
```

#### Running Code
```bash
# Run script with project dependencies
uv run python script.py

# Run tests
uv run pytest

# Run with specific Python version
uv run --python 3.12 script.py

# Run tools (like pipx)
uvx ruff check .           # Run tool without installing
uv tool install black      # Install tool globally
uv tool run black .        # Run installed tool
```

---

## 🔧 Ruff - Fast Linting & Formatting

### Why Ruff?
- **10-100x faster** than Black, isort, and Flake8 combined
- Written in Rust for maximum performance
- Replaces multiple tools: Black, isort, Flake8, pyupgrade, etc.

### Ruff Configuration

```toml
[tool.ruff]
target-version = "py39"
line-length = 88
fix = true
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
    "N",    # pep8-naming
    "S",    # flake8-bandit (security)
    "T20",  # flake8-print
    "SIM",  # flake8-simplify
    "ARG",  # flake8-unused-arguments
    "PTH",  # flake8-use-pathlib
    "RUF",  # Ruff-specific rules
]
ignore = [
    "E501",  # line-too-long (handled by formatter)
    "S101",  # use of assert (okay in tests)
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"

[tool.ruff.per-file-ignores]
"tests/**/*" = ["S101", "ARG", "FBT"]
"scripts/**/*" = ["T20"]

[tool.ruff.isort]
known-first-party = ["project_name"]

[tool.ruff.mccabe]
max-complexity = 10
```

### Ruff Commands

```bash
# Check for linting issues
ruff check .

# Check specific files
ruff check src/module.py

# Auto-fix issues
ruff check --fix .

# Watch mode (auto-fix on save)
ruff check --watch .

# Format code
ruff format .

# Check formatting without changes
ruff format --check .

# Combined workflow (recommended)
ruff check --fix . && ruff format .

# Show rule documentation
ruff rule E501

# Generate configuration
ruff config
```

---

## 🔍 MyPy - Static Type Checking

### Why MyPy?
- Catches type-related errors before runtime
- Improves code documentation and IDE support
- Enforces type safety across the codebase

### MyPy Configuration

```toml
[tool.mypy]
python_version = "3.9"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

# Allow untyped calls for specific libraries
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[[tool.mypy.overrides]]
module = "third_party_without_types.*"
ignore_missing_imports = true
```

### MyPy Commands

```bash
# Type check entire project
mypy src/

# Type check with strict mode
mypy src/ --strict

# Type check specific files
mypy src/module.py

# Show error codes
mypy src/ --show-error-codes

# Generate coverage report
mypy src/ --html-report ./mypy-report

# Check for unused type ignores
mypy src/ --warn-unused-ignores

# Install type stubs
mypy --install-types
```

---

## 🧪 pytest - Testing Framework

### pytest Configuration

```toml
[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
pythonpath = ["src"]
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "--cov=src",
    "--cov-branch",
    "--cov-report=term-missing:skip-covered",
    "--cov-report=html",
    "--cov-report=xml",
    "--cov-fail-under=80",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/migrations/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

### pytest Commands

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_module.py

# Run specific test
uv run pytest tests/test_module.py::test_function

# Run tests matching pattern
uv run pytest -k "test_user"

# Run tests with markers
uv run pytest -m "not slow"

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run with parallel execution
uv run pytest -n auto

# Run and stop on first failure
uv run pytest -x

# Show local variables in traceback
uv run pytest -l

# Show print statements
uv run pytest -s
```

---

## 🔗 Pre-commit Hooks

### Pre-commit Configuration

**CRITICAL**: Pre-commit hooks run in isolated environments without access to project dependencies. For type checking with dependencies (like FastMCP SDK), use local hooks that run via Taskfile.

```yaml
# .pre-commit-config.yaml
repos:
  # Ruff - Fast Python linter and formatter
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  # General file checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: [--maxkb=1000]
      - id: check-json
      - id: check-toml
      - id: check-merge-conflict
      - id: detect-private-key

  # Local hooks - Run project tasks with full dependencies
  - repo: local
    hooks:
      # Run type checking via task (uses uv with full dependencies)
      - id: type-check
        name: Type checking (mypy via task)
        entry: task type-check
        language: system
        types: [python]
        pass_filenames: false
        always_run: true
```

### Why Local Hook for MyPy?

**Problem**: Pre-commit's mypy hook runs in isolated environment:
```yaml
# ❌ THIS PATTERN HAS ISSUES
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.14.1
  hooks:
    - id: mypy
      additional_dependencies: [pydantic, fastapi]  # Hard to maintain!
      args: [--strict]
```

**Issues with Isolated MyPy:**
1. Doesn't have access to project dependencies (mcp, httpx, sqlalchemy, etc.)
2. Decorators from external packages appear untyped
3. Must manually list all type stub packages in `additional_dependencies`
4. Inconsistent with local type checking via `task type-check`

**Solution**: Use local hook that runs `task type-check`:
```yaml
# ✅ CORRECT PATTERN
- repo: local
  hooks:
    - id: type-check
      name: Type checking (mypy via task)
      entry: task type-check      # Uses project's uv environment
      language: system             # Runs in project environment
      types: [python]
      pass_filenames: false        # Check entire codebase
      always_run: true             # Run even if no Python files changed
```

**Benefits:**
- ✅ Full access to all project dependencies
- ✅ Consistent behavior (local = pre-commit = CI)
- ✅ No need to maintain `additional_dependencies`
- ✅ Uses same mypy configuration (pyproject.toml)

**When This Matters:**
- Projects with external package type hints (FastMCP, SQLAlchemy, etc.)
- Decorators from external packages that need type information
- Complex dependency graphs where listing all stubs is impractical

**Real Example from US-011:**
```python
# With isolated mypy: decorator appears untyped
@mcp.tool(name="example")  # ❌ Error: Untyped decorator
async def tool(params: Input) -> Output:
    pass

# With task type-check: decorator properly typed
@mcp.tool(name="example")  # ✅ Typed correctly
async def tool(params: Input) -> Output:
    pass
```

### Pre-commit Commands

```bash
# Install pre-commit
uv add --dev pre-commit

# Install hooks (done automatically by task setup)
task hooks:install
# Or manually:
uv run pre-commit install

# Run hooks manually on all files
task hooks:run
# Or manually:
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run ruff --all-files
uv run pre-commit run type-check --all-files

# Update hooks to latest version
task hooks:update
# Or manually:
uv run pre-commit autoupdate

# Skip hooks for a commit (use sparingly!)
git commit --no-verify
```

---

## 🔄 Renovate - Automated Dependency Updates

### Why Renovate?
Renovate automates dependency updates with:
- **Automatic PRs** for dependency updates
- **Security vulnerability detection** and automatic fixes
- **Configurable update schedules** (daily, weekly, monthly)
- **Automatic test validation** before merging
- **Grouped updates** to reduce PR noise
- **Support for Python, Node.js, Docker, GitHub Actions**, and more

### Renovate Configuration

```json
// renovate.json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "config:recommended"
  ],
  "schedule": ["before 6am on Monday"],
  "timezone": "America/New_York",
  "prConcurrentLimit": 3,
  "labels": ["dependencies"],
  "packageRules": [
    {
      "matchManagers": ["pip_requirements", "pip_setup", "poetry"],
      "matchUpdateTypes": ["minor", "patch"],
      "groupName": "Python dependencies"
    },
    {
      "matchManagers": ["github-actions"],
      "groupName": "GitHub Actions",
      "pinDigests": true
    },
    {
      "matchUpdateTypes": ["major"],
      "labels": ["major-update"],
      "automerge": false
    },
    {
      "matchUpdateTypes": ["minor", "patch"],
      "matchCurrentVersion": ">=1.0.0",
      "automerge": true,
      "automergeType": "pr",
      "automergeStrategy": "squash"
    },
    {
      "matchPackagePatterns": ["^pytest", "^ruff", "^mypy"],
      "groupName": "dev tools"
    }
  ],
  "vulnerabilityAlerts": {
    "enabled": true,
    "labels": ["security"],
    "assignees": ["@team-security"]
  },
  "python": {
    "enabled": true
  },
  "pip_requirements": {
    "fileMatch": ["(^|/)([\\w-]*)requirements\\.txt$", "(^|/)requirements/.*\\.txt$"]
  },
  "pip_setup": {
    "fileMatch": ["(^|/)setup\\.py$"]
  }
}
```

### Renovate Setup

```bash
# Enable Renovate for your repository
# 1. Install Renovate GitHub App: https://github.com/apps/renovate
# 2. Create renovate.json in repository root
# 3. Renovate will automatically create PRs for dependency updates

# Local testing (optional)
npm install -g renovate
renovate --platform github --token YOUR_TOKEN

# Validate configuration
renovate-config-validator
```

### Renovate Best Practices

- **Group related updates** to reduce PR noise (dev tools, test dependencies, etc.)
- **Schedule updates** during off-hours to avoid disrupting work
- **Enable automerge** for minor/patch updates after CI passes
- **Keep major updates manual** to review breaking changes
- **Use security alerts** to prioritize vulnerability fixes
- **Pin digests** for Docker images and GitHub Actions for security

---

## 🐚 NuShell - Cross-Platform Shell

### Why NuShell?
NuShell provides cross-platform shell scripting with:
- **Works on macOS, Linux, BSD, and Windows** natively
- **Structured data pipelines** (like JSON, CSV, tables)
- **Type-safe** shell scripting
- **Modern syntax** with improved error messages
- **Replaces Bash** for cross-platform compatibility
- **Built-in commands** for common operations

### NuShell Installation

```bash
# Install NuShell (macOS)
brew install nushell

# Install NuShell (Linux - cargo)
cargo install nu

# Install NuShell (Windows)
winget install nushell

# Or via Devbox (recommended - see Devbox section)
devbox add nushell
```

### NuShell Basic Syntax

```nu
# Variables
let name = "John"
let age = 30
let is_active = true

# Lists
let fruits = ["apple" "banana" "orange"]
let numbers = [1 2 3 4 5]

# Records (like objects/dicts)
let user = {
    name: "John"
    age: 30
    email: "john@example.com"
}

# Conditionals
if $age > 18 {
    print "Adult"
} else {
    print "Minor"
}

# Loops
for fruit in $fruits {
    print $fruit
}

# Pipelines (structured data)
ls | where size > 1kb | select name size | sort-by size

# Error handling
try {
    open file.txt
} catch {
    print "File not found"
}
```

### NuShell Script Example (setup.nu)

```nu
#!/usr/bin/env nu

# Automated environment setup script
# Usage: nu setup.nu [--silent]

def main [--silent] {
    print "🚀 Starting environment setup..."

    # Detect OS (sys requires subcommand)
    let os = (sys host | get name)
    print $"Detected OS: ($os)"

    # Check prerequisites
    check_prerequisites

    # Install uv if not present
    if (which uv | is-empty) {
        print "Installing uv package manager..."
        install_uv
    }

    # Create virtual environment
    print "Creating virtual environment..."
    ^uv venv .venv

    # Install dependencies
    print "Installing dependencies..."
    ^uv sync --all-extras

    # Configure pre-commit
    print "Configuring pre-commit hooks..."
    ^uv run pre-commit install

    # Copy .env.example if needed
    if not (".env" | path exists) {
        ^cp .env.example .env
        print "✅ Created .env file from template"
    }

    # Validate environment
    validate_environment

    print "✅ Setup complete! Run 'uv run uvicorn main:app --reload' to start server"
}

def check_prerequisites [] {
    print "Checking prerequisites..."

    # Check Python version
    let python_version = (python --version | parse "Python {version}" | get version.0)
    if ($python_version < "3.11") {
        error make {msg: "Python 3.11+ required"}
    }
    print $"✅ Python ($python_version)"

    # Check git
    if (which git | is-empty) {
        error make {msg: "Git is required"}
    }
    print "✅ Git installed"

    # Check podman
    if (which podman | is-empty) {
        print "⚠️  Podman not found (optional)"
    } else {
        print "✅ Podman installed"
    }
}

def install_uv [] {
    # Install uv via curl
    http get https://astral.sh/uv/install.sh | bash
}

def validate_environment [] {
    print "Validating environment..."

    # Test imports
    uv run python -c "import fastapi; import pydantic"
    print "✅ All dependencies importable"

    # Check .venv exists
    if (".venv" | path exists) {
        print "✅ Virtual environment created"
    }
}
```

### NuShell Module Organization

**CRITICAL: Use explicit exports for all modules (Decision D1 from SPEC-001 v1)**

NuShell supports module-based code organization for better maintainability and reusability. Follow these guidelines:

#### Module Structure Pattern

```
scripts/
├── setup.nu                 # Main entry point (orchestrator)
├── lib/
│   ├── os_detection.nu      # Module: OS detection (export def detect_os)
│   ├── prerequisites.nu     # Module: Prerequisites validation (export def check_prerequisites)
│   ├── validation.nu        # Module: Environment validation (export def validate_environment)
│   └── error_handler.nu     # Module: Error handling (export def retry_with_backoff)
└── tests/                   # NuShell tests

```

#### Import Strategy: `use` vs `source`

**✅ ALWAYS use `use` with explicit imports (Decision D1)**
- Provides namespace isolation
- Better IDE support and autocomplete
- Clear function dependencies
- Prevents namespace pollution

**❌ NEVER use `source`**
- Pollutes namespace with all functions
- No explicit dependency management
- Harder to track function origins

#### Explicit Exports (REQUIRED)

All public functions must use `export def`:

```nu
# ✅ CORRECT: Explicit export
# scripts/lib/os_detection.nu

# Detect operating system, architecture, and version
# Returns: record {os: string, arch: string, version: string}
# NOTE: Detailed type annotations (-> record<...>) not supported in NuShell 0.106+
export def detect_os [] {
    # Use sys host subcommand (sys requires a subcommand)
    let sys_info = (sys host)

    let os_name = $sys_info.name
    # sys host doesn't provide arch field, use external uname command
    let arch = (^uname -m | str trim)

    return {
        os: $os_name,
        arch: $arch,
        version: $sys_info.kernel_version
    }
}

# ❌ WRONG: Plain def (not exported, cannot be imported)
def detect_os [] {
    # ... implementation
}
```

#### Module Import Pattern

```nu
# ✅ CORRECT: Explicit function import
use scripts/lib/os_detection.nu detect_os
use scripts/lib/prerequisites.nu check_prerequisites
use scripts/lib/validation.nu validate_environment

# Call imported functions
let os_info = (detect_os)
let prereqs = (check_prerequisites)
let validation = (validate_environment)

# ❌ WRONG: source (pollutes namespace)
source scripts/lib/os_detection.nu
source scripts/lib/prerequisites.nu
```

#### Helper Functions (Private)

Helper functions that should NOT be exported use plain `def`:

```nu
# scripts/lib/prerequisites.nu

# Public function (exported)
export def check_prerequisites [] -> record {
    let python_check = check_python  # Call private helper

    return {
        python: $python_check.ok,
        python_version: $python_check.version
    }
}

# Private helper function (NOT exported)
def check_python [] -> record {
    let version_output = (python --version | complete)

    if $version_output.exit_code != 0 {
        return {ok: false, version: ""}
    }

    return {ok: true, version: $version_output.stdout}
}
```

#### Complete Module Example

**scripts/lib/validation.nu:**
```nu
# Environment validation module
# Provides comprehensive health checks for development environment

# Public function: Validate entire environment
# NOTE: Type annotations (-> record) not supported in detail, use comment documentation
export def validate_environment [] {
    print "Validating environment..."

    mut checks = []

    # Run all validation checks
    $checks = ($checks | append (check_python_version))
    $checks = ($checks | append (check_venv_exists))
    $checks = ($checks | append (check_dependencies_importable))

    let passed = ($checks | where passed == true | length)
    let failed = ($checks | where passed == false | length)

    return {
        passed: $passed,
        failed: $failed,
        checks: $checks
    }
}

# Private helper: Check Python version
def check_python_version [] {
    let version = (python --version | parse "Python {version}" | get version.0)

    if ($version >= "3.11") {
        return {name: "Python version", passed: true, message: $"Python ($version)"}
    } else {
        return {name: "Python version", passed: false, message: $"Python ($version) < 3.11"}
    }
}

# Private helper: Check venv exists
def check_venv_exists [] {
    if (".venv" | path exists) {
        return {name: "Virtual environment", passed: true, message: ".venv directory exists"}
    } else {
        return {name: "Virtual environment", passed: false, message: ".venv directory missing"}
    }
}

# Private helper: Check dependencies importable
def check_dependencies_importable [] {
    let result = (^uv run python -c "import fastapi; import pydantic" | complete)

    if $result.exit_code == 0 {
        return {name: "Dependencies", passed: true, message: "All dependencies importable"}
    } else {
        return {name: "Dependencies", passed: false, message: "Import failed"}
    }
}
```

**scripts/setup.nu:**
```nu
#!/usr/bin/env nu

# Main setup script (orchestrator)
# Usage: nu setup.nu [--silent]

# Import modules with explicit function imports (per Decision D1)
use scripts/lib/os_detection.nu detect_os
use scripts/lib/prerequisites.nu check_prerequisites
use scripts/lib/validation.nu validate_environment

def main [--silent] {
    print "🚀 Starting environment setup..."

    # Use imported functions
    let os_info = (detect_os)
    print $"Detected OS: ($os_info.os) ($os_info.arch)"

    let prereqs = (check_prerequisites)
    if ($prereqs.errors | length) > 0 {
        print "❌ Prerequisites check failed:"
        $prereqs.errors | each { |err| print $"  - ($err)" }
        exit 1
    }

    # ... rest of setup logic

    let validation = (validate_environment)
    print $"Validation: ($validation.passed)/($validation.passed + $validation.failed) checks passed"

    if $validation.failed > 0 {
        print "❌ Environment validation failed"
        exit 1
    }

    print "✅ Setup complete!"
}
```

#### Best Practices

1. **One module per responsibility** - Each .nu file should have a single, clear purpose
2. **Use explicit exports** - Always use `export def` for public functions
3. **Document function signatures** - Include parameter and return types
4. **Keep modules focused** - Avoid large, multi-purpose modules
5. **Use helper functions** - Private helpers (plain `def`) for internal logic
6. **Import explicitly** - Use `use module.nu function_name`, not `use module.nu *`
7. **Test modules independently** - Each module should be unit-testable

#### Module Import Examples

```nu
# ✅ CORRECT: Import specific functions
use scripts/lib/os_detection.nu detect_os
use scripts/lib/prerequisites.nu [check_prerequisites check_python]

# ✅ CORRECT: Import all exports from module (when needed)
use scripts/lib/validation.nu *

# ❌ WRONG: source pollutes namespace
source scripts/lib/os_detection.nu

# ❌ WRONG: Plain def without export (cannot be imported)
# In module:
def my_function [] {  # Missing 'export'
    print "This cannot be imported!"
}
```

#### References

- **NuShell Modules Documentation:** https://www.nushell.sh/book/modules.html
- **SPEC-001 v2 Decision D1:** Use `use` with explicit exports for maintainability
- **Implementation Guide:** See `/artifacts/tech_specs/SPEC-001_automated_setup_script_v2.md`

### Common NuShell Pitfalls & Solutions

**IMPORTANT**: Real issues encountered during implementation (NuShell 0.106.1). Follow these patterns to avoid syntax errors.

#### 1. Type Annotations Not Supported

**❌ WRONG:**
```nu
export def detect_os [] -> record<os: string, arch: string, version: string> {
    # Error: Parse mismatch, detailed type annotations not supported
}
```

**✅ CORRECT:**
```nu
# Use comment documentation for type information
# Returns: record {os: string, arch: string, version: string}
export def detect_os [] {
    return {os: "macos", arch: "arm64", version: "14.5"}
}
```

#### 2. sys Command Requires Subcommand

**❌ WRONG:**
```nu
let sys_info = (sys | get host)  # Error: sys doesn't support piping
```

**✅ CORRECT:**
```nu
let sys_info = (sys host)  # Use sys host subcommand directly
```

#### 3. sys host Doesn't Provide Architecture

**❌ WRONG:**
```nu
let sys_info = (sys host)
let arch = $sys_info.arch  # Error: Column 'arch' not found
```

**✅ CORRECT:**
```nu
let sys_info = (sys host)
let arch = (^uname -m | str trim)  # Use external uname with ^ prefix
```

#### 4. External Commands Need ^ Prefix

**❌ WRONG:**
```nu
uv venv .venv           # May conflict with NuShell builtins
tar -xzf file.tar.gz    # Error: NuShell tries to parse flags
```

**✅ CORRECT:**
```nu
^uv venv .venv          # ^ prefix ensures external command
^tar -xzf file.tar.gz   # Prevents NuShell flag parsing
^chmod +x script.sh
^mv source dest
```

#### 5. Mutable Variables in Catch Blocks

**❌ WRONG:**
```nu
mut error_msg = ""
try {
    # ... code
} catch { |err|
    $error_msg = $"Failed: ($err)"  # Error: Capture of mutable variable
}
```

**✅ CORRECT:**
```nu
let result = (try {
    # ... code
    {success: true, error: ""}
} catch { |err|
    {success: false, error: $"Failed: ($err)"}
})

if not $result.success {
    print $result.error
}
```

#### 6. String Interpolation with Parentheses

**❌ WRONG:**
```nu
print $"Detected: ($result.os)"  # Error: Shell tries to execute 'detected:' command
```

**✅ CORRECT - Option 1: Extract variable**
```nu
let detected_os = $result.os
print $"Detected: ($detected_os)"
```

**✅ CORRECT - Option 2: Escape parentheses**
```nu
print $"Detected: \(($result.os)\)"
```

#### 7. Shell Redirection (Bash-style Not Supported)

**❌ WRONG:**
```nu
let output = (command 2>&1 | complete)  # Error: Use out+err> not 2>&1
```

**✅ CORRECT:**
```nu
let output = (^command | complete)  # complete captures stdout + stderr
```

#### 8. Test Assertions with Comparisons

**❌ WRONG:**
```nu
assert ($result.arch | str length) > 0  # Error: Extra positional argument
```

**✅ CORRECT:**
```nu
assert (($result.arch | str length) > 0)  # Wrap comparison in extra parentheses
```

#### 9. Version Parsing Edge Cases

**❌ FRAGILE:**
```nu
let version = ($output | split row " " | get 1)
# Breaks on "Python 3.11.5+" or "Python 3.11.5rc1"
```

**✅ ROBUST:**
```nu
let version_str = ($output | str trim | split row " " | get 1)
let clean_version = ($version_str | split row "+" | get 0 | split row "rc" | get 0)
let parts = ($clean_version | split row ".")
let major = ($parts | get 0 | into int)
let minor = ($parts | get 1 | into int)
```

#### 10. Error Handling Best Practices

**❌ WRONG:**
```nu
def check_tool [] {
    if (which tool | is-empty) {
        error make {msg: "Tool not found"}  # Abrupt exit
    }
}
```

**✅ CORRECT:**
```nu
def check_tool [] {
    if (which tool | is-empty) {
        return {ok: false, error: "Tool not found. Install: devbox add tool"}
    }
    return {ok: true, error: ""}
}
```

### NuShell vs Bash Comparison

| Feature | Bash | NuShell |
|---------|------|---------|
| **Cross-platform** | ❌ (macOS/Linux only) | ✅ (macOS/Linux/Windows) |
| **Structured data** | ❌ (text-based) | ✅ (JSON, CSV, tables) |
| **Type safety** | ❌ | ✅ |
| **Error messages** | Poor | Excellent |
| **Modern syntax** | ❌ | ✅ |
| **Learning curve** | Medium | Medium |

### NuShell Commands Reference

```bash
# File operations
ls                    # List files (returns table)
open file.txt         # Read file
save file.txt         # Write file
cp source dest        # Copy
mv source dest        # Move
rm file.txt           # Remove

# Data manipulation
ls | where size > 1mb                    # Filter
ls | select name size                    # Select columns
ls | sort-by size                        # Sort
ls | first 5                             # Limit
open data.json | get users | length      # JSON operations

# System operations
sys                   # System information
ps                    # Process list
which python          # Find command
env                   # Environment variables

# String operations
"hello world" | str upcase               # Uppercase
"  text  " | str trim                    # Trim whitespace
"hello,world" | split row ","            # Split string

# HTTP operations
http get https://api.github.com/repos/nushell/nushell
http post https://api.example.com/data { key: "value" }
```

**NuShell Scripting Conventions:**
- **Location:** All NuShell scripts in `scripts/` directory
- **Module Library:** Reusable modules in `scripts/lib/` with explicit exports (`export def`)
- **Testing:** NuShell module tests in `scripts/tests/` (NOT in `tests/` directory)
- **Import Pattern:** Use `use ../lib/module.nu function_name` for explicit imports (per SPEC-001 D1)
- **Test Execution:** Run tests with `nu scripts/tests/test_module_name.nu`
- **Naming Convention:** Test files named `test_module_name.nu` matching module being tested

**Directory Separation:**
- `scripts/` - NuShell setup scripts and automation (DevOps/Infrastructure)
- `tests/` - Python application tests (unit, integration, e2e)
- `src/` - Python application source code

---

## 📦 Devbox - Portable Isolated Environments

### Why Devbox?
Devbox creates isolated, reproducible development environments with:
- **Eliminates "works on my machine" issues**
- **No Docker required** for dev environment isolation
- **Fast shell activation** (<1 second)
- **Reproducible environments** via `devbox.json` lockfile
- **Per-project tool versions** without conflicts
- **Portable across machines** - commit devbox.json to git

### Devbox Installation

```bash
# Install Devbox (macOS/Linux)
curl -fsSL https://get.jetpack.io/devbox | bash

# Or via Homebrew (macOS)
brew install jetpack-io/devbox/devbox

# Verify installation
devbox version
```

### Devbox Configuration (devbox.json)

```json
{
  "$schema": "https://jetpack.io/devbox/schema.json",
  "packages": [
    "python@3.11",
    "uv",
    "podman",
    "git",
    "nushell",
    "postgresql@15"
  ],
  "shell": {
    "init_hook": [
      "echo 'Welcome to AI Agent MCP Server development environment'",
      "python --version",
      "uv --version"
    ],
    "scripts": {
      "setup": "nu scripts/setup.nu",
      "test": "uv run pytest",
      "lint": "ruff check --fix . && ruff format .",
      "typecheck": "mypy src/ --strict",
      "dev": "uv run uvicorn main:app --reload",
      "db:start": "podman run -d --name mcp-db -e POSTGRES_PASSWORD=dev -p 5432:5432 postgres:15"
    }
  },
  "env": {
    "PYTHONPATH": "src",
    "DATABASE_URL": "postgresql://postgres:dev@localhost:5432/mcp"
  }
}
```

### Devbox Commands

```bash
# Initialize devbox in project
devbox init

# Add packages
devbox add python@3.11
devbox add uv
devbox add podman
devbox add nushell

# Remove packages
devbox remove python

# Enter devbox shell
devbox shell

# Run commands in devbox environment (without entering shell)
devbox run python script.py
devbox run uv sync

# Run defined scripts from devbox.json
devbox run setup        # Runs scripts/setup.nu
devbox run test         # Runs uv run pytest
devbox run dev          # Starts dev server

# Update packages
devbox update

# Show package information
devbox info python

# Generate shell script (for CI)
devbox generate direnv
```

### Devbox Best Practices

1. **Commit `devbox.json` and `devbox.lock` to git** - ensures reproducibility
2. **Pin major versions** - `python@3.11` not `python@latest`
3. **Use shell scripts** - define common tasks in `devbox.json` `shell.scripts`
4. **Set environment variables** - use `env` section for project-specific vars
5. **Init hook** - display helpful info when entering shell (versions, commands)
6. **Fast activation** - devbox shell starts in <1 second (vs Docker ~10 seconds)

### Devbox vs Docker Comparison

| Feature | Docker | Devbox |
|---------|--------|--------|
| **Purpose** | Container runtime | Dev environment manager |
| **Isolation** | Full OS isolation | Process isolation |
| **Performance** | Slower (VM overhead) | Fast (native binaries) |
| **Startup time** | ~10 seconds | <1 second |
| **Disk usage** | High (images) | Low (nix store) |
| **Best for** | Production deployment | Local development |
| **Learning curve** | High | Low |

**Use Devbox for**: Local development environments
**Use Docker/Podman for**: Production deployment, integration tests, database containers

---

## 🐳 Podman - Daemonless Container Runtime

### Why Podman?
Podman is a Docker-compatible container runtime with:
- **Daemonless architecture** - no background daemon required
- **Rootless containers** - run as non-root user for security
- **Docker-compatible** - uses same commands and Containerfile format
- **Drop-in replacement** - alias podman=docker works seamlessly
- **Organizational standard** per PRD-000 Decision D2
- **Secure by default** - better security model than Docker

### Podman Installation

```bash
# Install Podman (macOS)
brew install podman

# Initialize Podman machine (macOS only)
podman machine init
podman machine start

# Install Podman (Linux - Ubuntu/Debian)
sudo apt-get update
sudo apt-get -y install podman

# Install Podman (Linux - Fedora/RHEL)
sudo dnf -y install podman

# Or via Devbox (recommended)
devbox add podman

# Verify installation
podman --version
podman info
```

### Containerfile (Multi-Stage Build)

```dockerfile
# Containerfile (identical to Dockerfile)
# Multi-stage build for optimized production image

# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src/ /app/src/
COPY README.md /app/

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Podman Commands

```bash
# Build image
podman build -t mcp-server:latest .

# Build with specific Containerfile
podman build -f Containerfile.prod -t mcp-server:prod .

# Run container
podman run -d --name mcp-server -p 8000:8000 mcp-server:latest

# Run with environment variables
podman run -d --name mcp-server \
  -e DATABASE_URL=postgresql://localhost/mcp \
  -e LOG_LEVEL=info \
  -p 8000:8000 \
  mcp-server:latest

# Run with volume mount
podman run -d --name mcp-server \
  -v ./data:/app/data:Z \
  -p 8000:8000 \
  mcp-server:latest

# View logs
podman logs mcp-server
podman logs -f mcp-server  # Follow logs

# Execute command in container
podman exec -it mcp-server bash
podman exec mcp-server python -c "print('Hello')"

# Stop and remove
podman stop mcp-server
podman rm mcp-server

# List containers
podman ps           # Running containers
podman ps -a        # All containers

# List images
podman images

# Remove image
podman rmi mcp-server:latest

# Prune unused resources
podman system prune -a
```

### Podman Compose (docker-compose equivalent)

```yaml
# compose.yaml
version: '3'

services:
  app:
    build:
      context: .
      dockerfile: Containerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:dev@db:5432/mcp
      LOG_LEVEL: info
    depends_on:
      - db
    volumes:
      - ./src:/app/src:Z  # For development hot-reload
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: docker.io/library/postgres:15
    environment:
      POSTGRES_PASSWORD: dev
      POSTGRES_DB: mcp
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

```bash
# Run with podman-compose
podman-compose up -d

# View logs
podman-compose logs -f

# Stop all services
podman-compose down
```

### Podman vs Docker Commands

| Operation | Docker | Podman |
|-----------|--------|--------|
| **Build** | `docker build -t name .` | `podman build -t name .` |
| **Run** | `docker run -d name` | `podman run -d name` |
| **Logs** | `docker logs name` | `podman logs name` |
| **Exec** | `docker exec -it name bash` | `podman exec -it name bash` |
| **Compose** | `docker-compose up` | `podman-compose up` |
| **Stop** | `docker stop name` | `podman stop name` |

**Podman is 100% Docker-compatible** - just replace `docker` with `podman`

### Podman Best Practices

1. **Multi-stage builds** - separate builder and runtime stages for smaller images
2. **Non-root user** - always run containers as non-root for security
3. **Layer caching** - copy dependency files before code for efficient caching
4. **Health checks** - include HEALTHCHECK for production deployments
5. **Pin base images** - use `python:3.11-slim` not `python:latest`
6. **Minimal base images** - use `-slim` or `-alpine` variants
7. **.dockerignore** - exclude unnecessary files from build context

### Docker Compatibility Notes

- **Containerfile = Dockerfile** - syntax is identical
- **Docker Hub images work** - prefix with `docker.io/` if needed
- **Alias command** - add `alias docker=podman` to shell profile for seamless migration
- **compose support** - install `podman-compose` for docker-compose compatibility
- **Socket compatibility** - podman can expose Docker-compatible socket if needed

---

## 🔄 Complete Development Workflow

> **Note**: All commands use Taskfile interface for consistency. Individual tool commands are abstracted behind `task` commands.

### Initial Setup

```bash
# 1. Install Taskfile (if not already installed)
# macOS: brew install go-task
# Linux: See Taskfile section above

# 2. Clone repository
git clone https://github.com/your-org/project.git
cd project

# 3. Run initial project setup
task setup
# This installs dependencies and sets up pre-commit hooks

# 4. Verify environment
task info
# Shows project info, tool versions, and environment status
```

### Daily Development Workflow

```bash
# 1. Pull latest changes
git pull origin main

# 2. Create feature branch
git checkout -b feature/new-feature

# 3. Add dependencies if needed
task deps:add -- PKG=requests
task deps:add:dev -- PKG=pytest-watch

# 4. Make code changes
# ... edit files ...

# 5. Run quality checks before committing
task lint:fix      # Auto-fix linting issues
task format        # Format code
task type-check    # Check types
task test          # Run tests with coverage

# Or run all checks at once
task check

# 6. Commit changes (pre-commit hooks run automatically)
git add .
git commit -m "feat: add new feature"

# 7. Push changes
git push origin feature/new-feature
```

### Test-Driven Development Workflow

```bash
# 1. Start test watch mode
task test:watch

# 2. Make changes in another terminal
# Tests automatically re-run on file changes

# 3. Run specific test file
task test -- ARGS="tests/test_module.py"

# 4. Run only failed tests
task test:failed

# 5. Check test coverage
task test:coverage
```

### Database Development

```bash
# 1. Start PostgreSQL database
task db:start

# 2. Connect to database shell
task db:shell

# 3. View database logs
task db:logs

# 4. Restart database
task db:restart

# 5. Stop database when done
task db:stop
```

### Container Development

```bash
# 1. Build container image
task container:build

# 2. Run application container
task container:run

# 3. View container logs
task container:logs

# 4. Execute shell in container
task container:shell

# 5. Stop and remove container
task container:stop

# 6. Clean all containers and images
task container:clean
```

### Devbox Workflow (Recommended)

```bash
# 1. Enter Devbox shell (installs all tools automatically)
task devbox:shell

# 2. All Taskfile commands work inside Devbox
task test
task lint
task dev

# 3. Show Devbox environment info
task devbox:info

# 4. Update Devbox packages
task devbox:update
```

### CI/CD Pipeline

**Pipeline Triggers:**
- **Feature/Bugfix/Chore branches** (`feature/*`, `bugfix/*`, `chore/*`): Run all validation jobs + container build (no push)
- **Release branches** (`release/*`): Run all validation jobs + container build + push to registry
- **Pull Requests to main**: Run all validation jobs + container build (no push)
- **Main branch pushes**: NO automated container builds (documentation/TODO updates should not trigger builds)

**Container Build Strategy:**
- ✅ **Builds on ALL branches** - Validates Containerfile changes early
- ✅ **Pushes ONLY on release branches** - Clean, intentional releases
- ❌ **NO builds on main branch pushes** - Avoids unnecessary builds for docs/TODO updates

**Release Process:**
1. Create release branch: `git checkout -b release/v0.1.0`
2. Update version in `pyproject.toml` to match release tag
3. Push to trigger automated build and push: `git push -u origin release/v0.1.0`
4. Container image automatically pushed to `ghcr.io` with tags: `latest`, `v0.1.0`, `<commit-sha>`

```bash
# Run all CI checks (uses frozen lockfile)
task check:ci

# Individual CI steps
task deps:install              # Install from lockfile
task lint                      # Check linting
task type-check                # Check types
task test:coverage             # Run tests with coverage enforcement
task build                     # Build package
task container:build           # Build container (local only - CI handles push)
```

**CI/CD Jobs:**
1. **Containerfile Validation** - Hadolint linter for Dockerfile best practices
2. **Code Quality Checks** - Ruff linting and formatting
3. **Type Safety Validation** - MyPy strict mode type checking
4. **Test Execution and Coverage** - pytest with 80% coverage requirement
5. **Container Build** - Builds on all branches, pushes only on release branches
6. **Build Status Report** - Aggregates results, posts PR comment with status table

### Pre-commit Workflow

**Pre-commit Hooks:**
- **Ruff** - Linting with auto-fix
- **Ruff Format** - Code formatting
- **YAML/JSON/TOML checks** - Syntax validation
- **Hadolint** - Containerfile linting for best practices
- **Type checking** - MyPy strict mode via Taskfile
- **Security checks** - Detect private keys, large files

```bash
# Install pre-commit hooks (done automatically in task setup)
task hooks:install

# Run hooks manually on all files
task hooks:run

# Update hook versions
task hooks:update
```

### Development Server

```bash
# Start development server with hot-reload
task dev

# Run in background and view logs
task dev &
tail -f logs/dev.log
```

---

## 🚀 Performance Optimization

### UV Performance Tips
- Use `uv sync --frozen` in CI to skip lock file updates
- Use `uv cache` commands to manage cache
- Leverage parallel installation with `--no-deps` when appropriate

### Ruff Performance Tips
- Use `--fix` flag to auto-fix issues
- Run in watch mode during development: `ruff check --watch .`
- Configure per-file-ignores to skip unnecessary checks

### pytest Performance Tips
- Use `-n auto` for parallel test execution (requires pytest-xdist)
- Mark slow tests with `@pytest.mark.slow` and skip with `-m "not slow"`
- Use `--lf` to run only last failed tests
- Use `--ff` to run failed tests first

---

## 📊 Monitoring & Reporting

### Coverage Reports
```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Generate XML coverage (for CI)
pytest --cov=src --cov-report=xml
```

### Type Coverage Reports
```bash
# Generate MyPy HTML report
mypy src/ --html-report ./mypy-report

# View type coverage
open mypy-report/index.html
```

### Code Quality Metrics
```bash
# Show Ruff statistics
ruff check --statistics .

# Show complexity metrics
ruff check --select C90 .
```

---

## ⚠️ Critical Tool Requirements

### CLI Interface (Primary)
1. **Use Taskfile for all operations** - `task <command>` is the primary interface
2. **Never use direct tool commands in docs** - Always reference Taskfile tasks
3. **Extend Taskfile for new operations** - Add new tasks to `/Taskfile.yml`

### Core Development Tools
4. **Always use UV** for dependency management - never use pip directly (via `task deps:*`)
5. **Never manually edit uv.lock** - always use `task deps:add/remove`
6. **Run quality checks before commits** - `task check` or `task lint:fix && task format && task type-check && task test`
7. **Maintain 80%+ test coverage** - `task test:coverage` enforces this
8. **Use pre-commit hooks** - `task hooks:install` (done automatically in `task setup`)

### Environment & Deployment Tools (PRD-000 v2)
9. **Use Devbox for development** - Eliminates "works on my machine" issues (`task devbox:shell`)
10. **Use NuShell for cross-platform scripts** - Replaces Bash for macOS/Linux/Windows compatibility
11. **Use Podman for containers** - Organizational standard per PRD-000 Decision D2 (`task container:*`)
12. **Enable Renovate** - Automate dependency updates and security vulnerability fixes
13. **Pin dependencies** - Ensure reproducible builds via uv.lock
14. **Commit devbox.json and devbox.lock** - Ensures reproducible environments across team

---

**Back to [Core Guide](./CLAUDE-core.md)**
