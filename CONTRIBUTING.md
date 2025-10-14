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

**Tool**: Ruff (replaces Black, isort, Flake8)
**Configuration**: `pyproject.toml`
**Enforcement**: Automatically checked in CI pipeline

Ruff is a fast Python linter and formatter (10-100x faster than alternatives) that enforces consistent code style and catches common errors.

**Enabled Rule Categories**:
- `E`, `W` - pycodestyle errors and warnings
- `F` - Pyflakes (unused imports, undefined variables)
- `I` - isort (import sorting)
- `B` - flake8-bugbear (common bugs and design problems)
- `C4` - flake8-comprehensions (better list/set/dict comprehensions)
- `UP` - pyupgrade (modern Python syntax)
- `N` - pep8-naming (naming conventions)
- `S` - flake8-bandit (security issues)
- `T20` - flake8-print (print statements)
- `SIM` - flake8-simplify (code simplification)
- `ARG` - flake8-unused-arguments (unused function arguments)
- `PTH` - flake8-use-pathlib (prefer pathlib over os.path)
- `RUF` - Ruff-specific rules

**Commands**:
```bash
# Check for linting issues
task lint

# Auto-fix linting issues
task lint:fix

# Check formatting
task format:check

# Auto-format code
task format

# Run both lint and format together
task lint:all
```

**Error Message Format**:
```
F401 [*] `os` imported but unused
 --> src/module.py:3:8
  |
3 | import os
  |        ^^
  |
help: Remove unused import: `os`
```

Each error includes:
- **Rule Code** (e.g., `F401`) - Look up with `ruff rule F401`
- **File Path** - Exact location of the issue
- **Line Number** - Specific line with the problem
- **Code Snippet** - Visual context
- **Help Message** - Suggested fix

**Per-File Ignores**:
- Test files: Allow `assert`, unused arguments, and `print` statements
- Scripts: Allow `print` statements

**Suppressing Warnings**:
When a rule violation is intentional (e.g., binding to `0.0.0.0` for a server), add inline comments:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104
```

### Type Safety

**Tool**: MyPy (strict mode)
**Configuration**: `pyproject.toml`
**Enforcement**: Automatically checked in CI pipeline

MyPy is a static type checker that catches type-related errors before runtime, improves code documentation, and enables better IDE support through comprehensive type annotations.

**Strict Mode Checks Enabled**:
- `disallow_untyped_defs` - All functions must have type hints
- `disallow_incomplete_defs` - Functions with some typed params must have all typed
- `check_untyped_defs` - Check bodies of untyped functions
- `disallow_untyped_decorators` - Decorators must preserve type information
- `no_implicit_optional` - Require explicit `Optional[T]` (use `T | None` in Python 3.10+)
- `warn_redundant_casts` - Warn about unnecessary type casts
- `warn_unused_ignores` - Warn about unused `# type: ignore` comments
- `warn_no_return` - Warn about functions that don't return
- `warn_unreachable` - Warn about unreachable code
- `strict_equality` - Prohibit equality checks between incompatible types
- `warn_return_any` - Warn about returning `Any` from typed function
- `disallow_any_generics` - Require type parameters for generic types

**Type Hint Requirements**:
- **All production code** (`src/` directory) must pass strict type checking
- **Test code** (`tests/` directory) exempt from strict checks for testing flexibility
- Use modern Python 3.11+ syntax:
  - `list[str]` instead of `typing.List[str]`
  - `dict[str, int]` instead of `typing.Dict[str, int]`
  - `str | None` instead of `Optional[str]`
  - `str | int` instead of `Union[str, int]`

**Commands**:
```bash
# Run type checking
task type-check

# Generate HTML coverage report
task type-check:report

# Install missing type stubs
task type-check:install
```

**Error Message Format**:
```
src/module.py:13: error: "int" has no attribute "upper"  [attr-defined]
src/module.py:18: error: Incompatible types in assignment (expression has type "int", variable has type "str")  [assignment]
```

Each error includes:
- **File Path** - Exact location of the issue (e.g., `src/module.py:13`)
- **Error Type** - Clear description of the problem
- **Error Code** - Reference code in brackets (e.g., `[attr-defined]`)

**Common Type Hints**:
```python
# Function signatures
def greet(name: str) -> str:
    return f"Hello, {name}"

# Optional parameters (use | None for Python 3.10+)
def find_user(user_id: int) -> User | None:
    return database.get_user(user_id)

# Lists, dicts, sets
def process_items(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

# Async functions
async def fetch_data(url: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Generic types
from typing import TypeVar

T = TypeVar('T')

def first_item(items: list[T]) -> T | None:
    return items[0] if items else None
```

**Suppressing Type Errors**:
When type errors are unavoidable (e.g., interacting with untyped third-party libraries):
```python
result = untyped_library_call()  # type: ignore[no-untyped-call]
```

**Test Code Exemption**:
Test files automatically exempt from strict type checking but encouraged to use type hints where practical:
```python
# tests/test_example.py - type hints optional but recommended
def test_greet():
    result = greet("Alice")  # Type hints inferred from source
    assert result == "Hello, Alice"
```

### Testing and Coverage

**Framework**: pytest with pytest-cov and pytest-asyncio
**Configuration**: `pyproject.toml`
**Enforcement**: Automatically checked in CI pipeline

pytest is our testing framework with support for async tests, fixtures, and coverage reporting. All code must include comprehensive tests to maintain >80% coverage threshold.

**Testing Philosophy**:
- **Test-Driven Development**: Write tests first, then implementation
- **Testing Pyramid**: 70% unit tests, 20% integration tests, 10% end-to-end tests
- **Deterministic Tests**: No flaky tests - all tests must be reproducible
- **Async Support**: Full support for testing async/await patterns with pytest-asyncio

**Test Categories (pytest markers)**:
- `@pytest.mark.unit` - Unit tests (test individual functions/methods in isolation)
- `@pytest.mark.integration` - Integration tests (test component interactions)
- `@pytest.mark.e2e` - End-to-end tests (test complete user workflows)
- `@pytest.mark.slow` - Slow tests (>1 second, run selectively)
- `@pytest.mark.asyncio` - Async tests (automatically handled by pytest-asyncio)

**Commands**:
```bash
# Run all tests with coverage
task test

# Run tests and enforce 80% coverage threshold
task test:coverage

# Run specific test categories
task test:unit           # Unit tests only
task test:integration    # Integration tests only
task test:e2e            # End-to-end tests only

# Run tests by marker
pytest -m "not slow"     # Skip slow tests
pytest -m "unit"         # Only unit tests
pytest -m "integration"  # Only integration tests

# Useful test commands
task test:verbose        # Verbose output
task test:failed         # Re-run only failed tests
task test:watch          # Watch mode (re-run on file changes)
```

**Coverage Requirements**:
- **Minimum threshold**: 80% line coverage (enforced by `--cov-fail-under=80`)
- **Coverage reports**: Generated in 3 formats:
  - Terminal summary (shown after test run)
  - HTML report (browsable at `htmlcov/index.html`)
  - XML report (for CI/CD integration)
- **Excluded from coverage**:
  - Test files (`tests/*`)
  - `__init__.py` files
  - `__main__.py` files
  - Lines marked with `# pragma: no cover`

**Test Organization**:
```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests (70% of tests)
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/             # Integration tests (20% of tests)
│   ├── test_api_endpoints.py
│   └── test_database.py
└── e2e/                     # End-to-end tests (10% of tests)
    └── test_workflows.py
```

**Test Fixtures**:
All tests have access to comprehensive fixtures defined in `tests/conftest.py`:

**FastAPI Test Clients**:
```python
def test_endpoint(client):
    """Synchronous TestClient for sync endpoints."""
    response = client.get("/api/endpoint")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_async_endpoint(async_client):
    """Async client for async endpoints, SSE, WebSockets."""
    response = await async_client.get("/api/endpoint")
    assert response.status_code == 200
```

**Database Fixtures**:
```python
def test_repository(db_session):
    """Mocked database session for unit tests."""
    db_session.query.return_value.filter.return_value.first.return_value = User(id=1)
    user = repo.get_by_id(db_session, 1)
    assert user.id == 1

@pytest.mark.asyncio
async def test_async_repository(async_db_session):
    """Mocked async database session."""
    async_db_session.execute.return_value.scalar.return_value = User(id=1)
    user = await repo.get_by_id(async_db_session, 1)
    assert user.id == 1
```

**Mock External Services**:
```python
def test_external_api(mock_http_client):
    """Mocked HTTP client for external APIs."""
    mock_http_client.get.return_value.json.return_value = {"data": "value"}
    result = service.fetch_data(mock_http_client)
    assert result["data"] == "value"

def test_jira_integration(mock_jira_client):
    """Pre-configured JIRA client mock."""
    issue = mock_jira_client.create_issue(fields={...})
    assert issue["key"] == "PROJ-123"

def test_ci_cd_integration(mock_ci_cd_client):
    """Pre-configured CI/CD client mock."""
    run = mock_ci_cd_client.trigger_workflow(workflow_id="ci.yml")
    assert run["run_id"] == 123
```

**Sample Data Fixtures**:
```python
def test_with_sample_data(sample_user_data, sample_tool_request):
    """Pre-configured sample data for testing."""
    user = User(**sample_user_data)
    assert user.email == "test@example.com"

    result = tool.execute(sample_tool_request)
    assert result["status"] == "success"
```

**Fixture Factories**:
```python
def test_multiple_instances(user_factory):
    """Factory function to create multiple instances with custom data."""
    user1 = user_factory(email="user1@example.com")
    user2 = user_factory(email="user2@example.com")
    assert user1["email"] != user2["email"]
```

**Test Naming Convention**:
```python
# Format: test_should_<expected_behavior>_when_<condition>
def test_should_return_user_when_id_exists():
    """Test retrieves user successfully when ID exists in database."""
    pass

def test_should_raise_error_when_id_invalid():
    """Test raises ValueError when user ID is negative."""
    pass

def test_should_filter_active_users_when_status_active():
    """Test filters only active users when status parameter is 'active'."""
    pass
```

**Arrange-Act-Assert Pattern**:
```python
def test_user_email_update(sample_user_data):
    """Test user email update with valid input."""
    # Arrange - set up test data and preconditions
    user = User(**sample_user_data)
    new_email = "newemail@example.com"

    # Act - execute the code under test
    user.update_email(new_email)

    # Assert - verify expected outcomes
    assert user.email == new_email
    assert user.email_verified is False  # Email change resets verification
```

**Parametrized Tests**:
```python
@pytest.mark.parametrize("age,expected_eligible", [
    (17, False),  # Below minimum
    (18, True),   # At minimum
    (65, True),   # Within range
    (66, False),  # Above maximum
])
def test_age_eligibility(age, expected_eligible):
    """Test age eligibility validation for different ages."""
    result = is_eligible(age)
    assert result == expected_eligible
```

**Exception Testing**:
```python
def test_invalid_user_id_raises_error():
    """Test ValueError raised when user ID is negative."""
    with pytest.raises(ValueError, match="User ID must be positive"):
        get_user(-1)
```

**Async Test Patterns**:
```python
@pytest.mark.asyncio
async def test_async_function():
    """Test async function execution."""
    result = await async_process_data(["item1", "item2"])
    assert len(result) == 2

@pytest.mark.asyncio
async def test_concurrent_processing():
    """Test concurrent task processing."""
    tasks = [process_item(1), process_item(2), process_item(3)]
    results = await asyncio.gather(*tasks)
    assert len(results) == 3
```

**Coverage Enforcement**:
The test suite automatically enforces the 80% coverage threshold:
```bash
$ task test:coverage
============================= test session starts ==============================
...
---------- coverage: platform darwin, python 3.11.13-final-0 -----------
Name                Stmts   Miss  Cover   Missing
-------------------------------------------------
src/module.py          50      2    96%   23, 45
-------------------------------------------------
TOTAL                 200     10    95%

Required test coverage of 80% reached. Total coverage: 95.00%
============================== 33 passed in 0.15s ===============================
```

If coverage falls below 80%, the build fails:
```bash
ERROR: Coverage failure: total of 75 is less than fail-under=80
FAIL Required test coverage of 80% not reached. Total coverage: 75.00%
```

**Viewing Coverage Reports**:
```bash
# Generate and view HTML coverage report
task test:coverage
open htmlcov/index.html

# The HTML report shows:
# - Coverage percentage per file
# - Highlighted uncovered lines in source code
# - Branch coverage details
# - Links to source files
```

**Writing Good Tests**:
1. **One assertion per test** (when possible) - Makes failures easier to diagnose
2. **Test one thing** - Each test should validate a single behavior
3. **Use descriptive names** - Test name should describe what it tests and when
4. **Avoid test interdependence** - Tests should run in any order
5. **Use fixtures for setup** - Don't duplicate setup code across tests
6. **Test edge cases** - Empty lists, None values, boundary conditions
7. **Test error paths** - Verify error handling works correctly
8. **Mock external dependencies** - Tests should not require network, database, or file system

**Common Testing Patterns**:

See `tests/unit/test_example_fixtures.py` and `tests/integration/test_api_endpoints.py` for comprehensive examples demonstrating:
- Fixture usage patterns
- FastAPI endpoint testing
- Async test patterns
- Mock service configuration
- Parametrized tests
- Exception testing
- Coverage strategies

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

**Symptoms**: `lint-and-format` job fails with exit code 1

**Diagnosis**:
```bash
# Run locally to reproduce
task lint           # Check for linting issues
task format:check   # Check for formatting issues
```

**Common Issues**:

1. **Unused Imports** (F401)
   ```bash
   task lint:fix  # Auto-removes unused imports
   ```

2. **Formatting Issues** (line length, quotes, spacing)
   ```bash
   task format  # Auto-formats all files
   ```

3. **Naming Violations** (N801, N802, N803)
   - Fix manually: Use `PascalCase` for classes, `snake_case` for functions/variables

4. **Security Issues** (S104, S105, S106)
   - Review the violation and suppress if intentional:
     ```python
     host: str = "0.0.0.0"  # noqa: S104
     ```

5. **Print Statements** (T20)
   - Replace `print()` with proper logging:
     ```python
     import logging
     logger = logging.getLogger(__name__)
     logger.info("Message")
     ```

**Quick Fix Workflow**:
```bash
# Fix most issues automatically
task lint:fix && task format

# Re-run checks
task lint && task format:check

# If any issues remain, fix manually and re-run
```

### Pipeline Failure: Type Safety Validation

**Symptoms**: `type-check` job fails with exit code 1

**Diagnosis**:
```bash
# Run locally to reproduce
task type-check

# Generate HTML report for detailed analysis
task type-check:report
# Open mypy-report/index.html in browser
```

**Common Issues**:

1. **Missing Type Hints** (no-untyped-def)
   ```python
   # Bad
   def calculate(x, y):
       return x + y

   # Good
   def calculate(x: int, y: int) -> int:
       return x + y
   ```

2. **Incompatible Types** (assignment, return-value)
   ```python
   # Bad
   result: str = 42  # Type error: int assigned to str

   # Good
   result: int = 42
   ```

3. **Missing Return Type**
   ```python
   # Bad
   def greet(name: str):
       return f"Hello, {name}"

   # Good
   def greet(name: str) -> str:
       return f"Hello, {name}"
   ```

4. **Optional Values** (arg-type, union-attr)
   ```python
   # Bad
   def get_length(value: str | None) -> int:
       return len(value)  # Error: value might be None

   # Good
   def get_length(value: str | None) -> int:
       return len(value) if value is not None else 0
   ```

5. **Third-Party Library Missing Stubs**
   ```bash
   # Install type stubs
   task type-check:install

   # Or suppress for specific library
   # Add to pyproject.toml:
   # [[tool.mypy.overrides]]
   # module = "library_name.*"
   # ignore_missing_imports = true
   ```

6. **Generic Types** (type-arg)
   ```python
   # Bad
   items: list = [1, 2, 3]

   # Good
   items: list[int] = [1, 2, 3]
   ```

**Quick Fix Workflow**:
```bash
# Check errors
task type-check

# For detailed analysis with line-by-line coverage
task type-check:report

# Fix errors in code, then re-run
task type-check

# If stuck, suppress specific errors (last resort)
# Add: # type: ignore[error-code]
```

### Pipeline Failure: Test Execution and Coverage

**Symptoms**: `test-and-coverage` job fails with exit code 1

**Diagnosis**:
```bash
# Run locally to reproduce
task test:coverage

# Run tests with verbose output
task test:verbose

# Run only failed tests
task test:failed
```

**Common Issues**:

1. **Test Failures** (assertion errors, exceptions)
   ```bash
   # Run failed tests with full traceback
   task test:verbose --tb=long

   # Common causes:
   # - Assertions that don't match expected values
   # - Exceptions raised during test execution
   # - Fixture configuration issues
   # - Mock return values not configured correctly
   ```

2. **Coverage Below 80% Threshold**
   ```bash
   # Check which files need more coverage
   task test:coverage

   # View detailed HTML coverage report
   open htmlcov/index.html

   # The report shows:
   # - Files with low coverage (red highlighting)
   # - Uncovered lines (line numbers listed in Missing column)
   # - Branch coverage details

   # Add tests for uncovered code paths:
   # 1. Identify uncovered lines in HTML report
   # 2. Write tests that execute those lines
   # 3. Re-run coverage to verify improvement
   ```

3. **Import Errors** (module not found, circular imports)
   ```bash
   # Check Python path configuration
   # pyproject.toml should have: pythonpath = ["src"]

   # Verify test file imports:
   from mcp_server.module import function  # Correct (uses package name)
   # NOT: from src.mcp_server.module import function
   ```

4. **Fixture Not Found** (fixture 'name' not found)
   ```bash
   # Verify fixture defined in conftest.py
   # Check fixture scope (function, class, module, session)
   # Ensure conftest.py is in correct directory

   # Fixture resolution order:
   # 1. Test file's conftest.py
   # 2. Parent directory's conftest.py
   # 3. Root tests/ conftest.py
   ```

5. **Async Tests Not Running** (@pytest.mark.asyncio)
   ```bash
   # Verify pytest-asyncio installed:
   uv add --dev pytest-asyncio

   # Check pyproject.toml configuration:
   # [tool.pytest.ini_options]
   # asyncio_mode = "auto"

   # Async test example:
   @pytest.mark.asyncio
   async def test_async_function():
       result = await async_function()
       assert result is not None
   ```

6. **Flaky Tests** (intermittent failures)
   ```bash
   # Run test multiple times to reproduce:
   pytest tests/test_flaky.py::test_name -x --count=10

   # Common causes:
   # - Relying on timing/sleep (use proper async patterns)
   # - Shared state between tests (use isolated fixtures)
   # - Non-deterministic random values (use fixed seeds)
   # - External service dependencies (use mocks)

   # Fix patterns:
   # - Use fixtures with autouse=True to reset state
   # - Use pytest-mock for deterministic mocking
   # - Use asyncio.wait_for() for timeout handling
   ```

7. **Slow Tests** (timeout exceeded)
   ```bash
   # Mark slow tests with @pytest.mark.slow
   # Run without slow tests locally:
   pytest -m "not slow"

   # Optimize test performance:
   # - Use mocks instead of real I/O
   # - Minimize fixture setup/teardown
   # - Run tests in parallel: task test:parallel
   ```

**Quick Fix Workflow**:
```bash
# 1. Run tests and identify failures
task test:verbose

# 2. Check coverage report
task test:coverage
open htmlcov/index.html

# 3. Fix failing tests and add missing coverage

# 4. Re-run specific test
pytest tests/path/to/test_file.py::test_name -v

# 5. Re-run full suite
task test:coverage

# 6. Verify coverage ≥80%
# Output should show: "Required test coverage of 80% reached"
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
