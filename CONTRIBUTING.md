# Contributing to AI Agent MCP Server

Thank you for your interest in contributing to the AI Agent MCP Server project! This guide will help you understand our development workflow and CI/CD pipeline.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [CI/CD Pipeline](#cicd-pipeline)
- [Code Quality Standards](#code-quality-standards)
- [Pull Request Process](#pull-request-process)

## Getting Started

### Prerequisites

- Python 3.11+
- UV package manager
- Task (Taskfile CLI)
- Git

### Initial Setup

```bash
# Run automated setup script
nu scripts/setup.nu

# Or install dependencies manually
uv sync --all-extras
task hooks:install
```

## Development Workflow

### Creating a Feature Branch

All development work should be done on feature branches. Branch naming conventions:

- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `chore/*` - Maintenance tasks

```bash
# Create and checkout a new feature branch
git checkout -b feature/my-new-feature

# Make your changes
# ...

# Run local validation before committing
task check
```

### Local Quality Checks

Before pushing your changes, run the following commands to ensure code quality:

```bash
# Run all quality checks (recommended)
task check

# Or run individual checks
task lint              # Ruff linting
task format:check      # Code formatting validation
task type-check        # MyPy type checking
task test:coverage     # Tests with coverage (80% minimum)
```

## CI/CD Pipeline

### Pipeline Architecture

Our CI/CD pipeline is built with GitHub Actions and automatically triggers on:
- Pushes to feature branches (`feature/*`, `bugfix/*`, `chore/*`)
- Pull requests to `main` branch

The pipeline consists of **5 jobs** organized into 3 stages:

#### Stage 1: Setup (30 seconds)
- **setup**: Installs dependencies and caches artifacts for downstream jobs
  - Sets up Python 3.11
  - Installs UV package manager
  - Caches UV dependencies (`~/.cache/uv`)
  - Caches pytest cache (`.pytest_cache`)
  - Caches mypy cache (`.mypy_cache`)

#### Stage 2: Validation (2-3 minutes, runs in parallel)
- **lint-and-format**: Code quality checks with Ruff
  - Runs `task lint` (linting checks)
  - Runs `task format:check` (formatting validation)
- **type-check**: Type safety validation with MyPy
  - Runs `task type-check` (strict mode type checking)
- **test-and-coverage**: Test execution with coverage reporting
  - Runs `task test:coverage` (80% minimum coverage)
  - Uploads coverage reports as artifacts

#### Stage 3: Report (30 seconds)
- **report**: Aggregates results and posts build status to PR
  - Checks all validation job results
  - Posts summary comment to PR with status indicators
  - Uploads coverage reports

### Performance Targets

- **Total execution time**: <5 minutes (95th percentile)
- **Pipeline trigger**: <1 minute after push
- **Setup with cache hit**: <30 seconds
- **Concurrent builds**: Supports 10+ simultaneous builds

### Caching Strategy

The pipeline implements aggressive caching to minimize build times:

1. **UV Dependency Cache**: Cached by `pyproject.toml` and `uv.lock` hashes
2. **Pytest Cache**: Cached by commit SHA for test result reuse
3. **MyPy Cache**: Cached by Python file hashes for incremental type checking

**Cache Invalidation**:
- UV cache: Automatic on `pyproject.toml` or `uv.lock` changes
- Pytest cache: Per-commit (ensures fresh test runs)
- MyPy cache: When Python files change

### Concurrency Management

The pipeline uses GitHub Actions concurrency groups to:
- Allow parallel builds across different branches
- Cancel in-progress builds when new commits are pushed to the same branch
- Prevent resource contention and queue delays

## Code Quality Standards

All code contributions must meet the following standards:

### Linting and Formatting
- **Tool**: Ruff (replaces Black, isort, Flake8)
- **Configuration**: `pyproject.toml`
- **Enforcement**: Automatically checked in CI pipeline

### Type Safety
- **Tool**: MyPy (strict mode)
- **Requirement**: All code must include type hints
- **Configuration**: `pyproject.toml`
- **Enforcement**: Automatically checked in CI pipeline

### Testing and Coverage
- **Framework**: pytest
- **Minimum Coverage**: 80%
- **Test Types**: Unit, integration, and end-to-end tests
- **Enforcement**: Automatically checked in CI pipeline

### Pre-commit Hooks

We use pre-commit hooks to catch issues before they reach CI:

```bash
# Install hooks (one-time setup)
task hooks:install

# Run hooks manually
task hooks:run

# Update hook versions
task hooks:update
```

**Note**: You can bypass hooks in exceptional cases with `git commit --no-verify`, but this is discouraged.

## Pull Request Process

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes and Commit

```bash
# Make your changes
# ...

# Run local checks
task check

# Commit changes
git add .
git commit -m "feat: Add new feature"
```

### 3. Push to Remote

```bash
git push origin feature/my-feature
```

### 4. Create Pull Request

1. Navigate to the GitHub repository
2. Click "New Pull Request"
3. Select your feature branch
4. Fill in the PR template with:
   - Summary of changes
   - Related issues
   - Testing notes
   - Screenshots (if applicable)

### 5. Wait for CI/CD Validation

The CI/CD pipeline will automatically:
- Trigger within 1 minute of push
- Run all validation jobs in parallel
- Post build status to PR page
- Upload coverage reports

**Build Status Indicators**:
- ✅ Green checkmark: All checks passed
- ❌ Red X: One or more checks failed
- 🟡 Yellow dot: Checks in progress

### 6. Address Review Feedback

- Respond to code review comments
- Make requested changes
- Push updates (pipeline automatically re-runs)
- Request re-review when ready

### 7. Merge

Once approved and all checks pass:
- Squash and merge (recommended for feature branches)
- Merge commit (for complex features with logical commits)
- Rebase and merge (for clean linear history)

## Branch Protection Rules

The `main` branch is protected with the following rules:

- ✅ Require status checks to pass before merging
  - Code Quality Checks (lint-and-format)
  - Type Safety Validation (type-check)
  - Test Execution and Coverage (test-and-coverage)
- ✅ Require at least 1 approving review
- ✅ Require branch to be up to date with base
- ✅ No direct pushes (all changes via PR)

## Troubleshooting

### Pipeline Failure: Code Quality Checks

```bash
# Run locally to reproduce
task lint
task format:check

# Auto-fix linting issues
task lint:fix

# Auto-fix formatting issues
task format
```

### Pipeline Failure: Type Safety Validation

```bash
# Run locally to reproduce
task type-check

# Generate HTML report for detailed analysis
task type-check:report
# Open mypy-report/index.html
```

### Pipeline Failure: Test Execution and Coverage

```bash
# Run locally to reproduce
task test:coverage

# Run tests with verbose output
task test:verbose

# Run only failed tests
task test:failed
```

### Slow Pipeline Execution

If pipeline execution exceeds 5 minutes:
- Check if caches are being restored (look for "Cache restored" in logs)
- Verify dependency changes (new dependencies may require re-download)
- Check for slow tests (consider parallelization with `pytest-xdist`)

### Cache Issues

If caches are not working correctly:
- Clear caches from GitHub repository settings
- Check cache key format in `.github/workflows/ci.yml`
- Verify cache paths match actual file locations

## Getting Help

- **Documentation**: Check the `/docs` directory for detailed guides
- **Issues**: Search existing GitHub issues or create a new one
- **Discussions**: Use GitHub Discussions for questions and proposals

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/).

---

**Last Updated**: 2025-10-14
**Pipeline Version**: v1.0
