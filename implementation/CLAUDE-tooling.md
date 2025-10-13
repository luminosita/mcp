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

## 🔄 Complete Development Workflow

### Initial Setup
```bash
# 1. Create project structure
uv init my-project
cd my-project

# 2. Create virtual environment
uv venv

# 3. Activate environment
source .venv/bin/activate

# 4. Install dependencies
uv sync --all-extras

# 5. Install pre-commit hooks
uv run pre-commit install
```

### Daily Development
```bash
# 1. Pull latest changes
git pull origin main

# 2. Create feature branch
git checkout -b feature/new-feature

# 3. Add dependencies if needed
uv add new-package

# 4. Run quality checks before committing
ruff check --fix . && ruff format .
mypy src/ --strict
pytest --cov

# 5. Commit changes (pre-commit runs automatically)
git add .
git commit -m "feat: add new feature"

# 6. Push changes
git push origin feature/new-feature
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

1. **Always use UV** for dependency management
2. **Never manually edit uv.lock** - always use `uv add/remove`
3. **Run Ruff before commits** - `ruff check --fix . && ruff format .`
4. **Type check with MyPy strict mode** - `mypy src/ --strict`
5. **Maintain 80%+ test coverage** - `pytest --cov-fail-under=80`
6. **Use pre-commit hooks** - Automate quality checks
7. **Pin dependencies** - Ensure reproducible builds

---

**Back to [Core Guide](./CLAUDE-core.md)**