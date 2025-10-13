# CLAUDE-tooling.md - Development Tools & Configuration

> **Specialized Guide**: Comprehensive tooling setup for Python development with UV, Ruff, MyPy, and pytest.

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

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, pydantic]
        args: [--strict]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: check-json
      - id: check-toml

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, src, -ll]
```

### Pre-commit Commands

```bash
# Install pre-commit
uv add --dev pre-commit

# Install hooks
uv run pre-commit install

# Run hooks manually on all files
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run ruff --all-files

# Update hooks to latest version
uv run pre-commit autoupdate

# Skip hooks for a commit
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

    # Detect OS
    let os = (sys | get host.name)
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
    uv venv .venv

    # Install dependencies
    print "Installing dependencies..."
    uv sync --all-extras

    # Configure pre-commit
    print "Configuring pre-commit hooks..."
    uv run pre-commit install

    # Copy .env.example if needed
    if not (".env" | path exists) {
        cp .env.example .env
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

### Initial Setup (with Devbox)

```bash
# 1. Install Devbox (if not already installed)
curl -fsSL https://get.jetpack.io/devbox | bash

# 2. Clone repository
git clone https://github.com/your-org/project.git
cd project

# 3. Enter Devbox shell (installs all dependencies automatically)
devbox shell

# 4. Run setup script (NuShell)
devbox run setup
# Or manually: nu scripts/setup.nu

# 5. Verify environment
uv run python -c "import fastapi; print('✅ Environment ready')"
```

### Daily Development (with Devbox)

```bash
# 1. Enter Devbox shell
devbox shell

# 2. Pull latest changes
git pull origin main

# 3. Create feature branch
git checkout -b feature/new-feature

# 4. Add dependencies if needed
uv add new-package

# 5. Run quality checks before committing
devbox run lint        # Ruff check + format
devbox run typecheck   # MyPy strict
devbox run test        # pytest with coverage

# 6. Commit changes (pre-commit hooks run automatically)
git add .
git commit -m "feat: add new feature"

# 7. Push changes
git push origin feature/new-feature
```

### Database Development (with Podman)

```bash
# Start PostgreSQL in Podman container
podman run -d --name mcp-db \
  -e POSTGRES_PASSWORD=dev \
  -e POSTGRES_DB=mcp \
  -p 5432:5432 \
  postgres:15

# Or use devbox script
devbox run db:start

# Connect to database
podman exec -it mcp-db psql -U postgres -d mcp

# Stop database
podman stop mcp-db
podman rm mcp-db
```

### Container Development (with Podman)

```bash
# Build container image
podman build -t mcp-server:dev .

# Run container locally
podman run -d --name mcp-server \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://postgres:dev@localhost:5432/mcp \
  mcp-server:dev

# View logs
podman logs -f mcp-server

# Test endpoints
curl http://localhost:8000/health

# Stop and remove
podman stop mcp-server && podman rm mcp-server
```

### CI/CD Pipeline Commands
```bash
# Install dependencies
uv sync --frozen

# Run linting
ruff check .

# Run type checking
mypy src/ --strict

# Run tests with coverage
pytest --cov=src --cov-report=xml --cov-fail-under=80

# Build package
uv build

# Publish to PyPI
uv publish
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

### Core Development Tools
1. **Always use UV** for dependency management - never use pip directly
2. **Never manually edit uv.lock** - always use `uv add/remove`
3. **Run Ruff before commits** - `ruff check --fix . && ruff format .`
4. **Type check with MyPy strict mode** - `mypy src/ --strict`
5. **Maintain 80%+ test coverage** - `pytest --cov-fail-under=80`
6. **Use pre-commit hooks** - Automate quality checks before commits

### Environment & Deployment Tools (PRD-000 v2)
7. **Use Devbox for development** - Eliminates "works on my machine" issues
8. **Use NuShell for cross-platform scripts** - Replaces Bash for macOS/Linux/Windows compatibility
9. **Use Podman for containers** - Organizational standard per PRD-000 Decision D2
10. **Enable Renovate** - Automate dependency updates and security vulnerability fixes
11. **Pin dependencies** - Ensure reproducible builds via uv.lock
12. **Commit devbox.json and devbox.lock** - Ensures reproducible environments across team

---

**Back to [Core Guide](./CLAUDE-core.md)**