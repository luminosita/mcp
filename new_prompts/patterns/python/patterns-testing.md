# patterns-testing - Testing Strategy & Best Practices

> **Specialized Guide**: Comprehensive testing patterns, fixtures, and coverage requirements for Python projects.

## 🧪 Testing Philosophy

### Test-Driven Development (TDD)
1. **Write the test first** - Define expected behavior before implementation
2. **Watch it fail** - Ensure the test actually tests something
3. **Write minimal code** - Just enough to make the test pass
4. **Refactor** - Improve code while keeping tests green
5. **Repeat** - One test at a time

### Testing Pyramid
- **Unit Tests (70%)**: Test individual functions/methods in isolation
- **Integration Tests (20%)**: Test component interactions
- **End-to-End Tests (10%)**: Test complete user workflows

---

## 📁 Test Organization

### Directory Structure
```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/             # Integration tests
│   ├── __init__.py
│   ├── test_database.py
│   └── test_api.py
└── e2e/                     # End-to-end tests
    ├── __init__.py
    └── test_workflows.py
```

### Test File Naming
- Test files: `test_*.py` or `*_test.py`
- Test classes: `Test*` (e.g., `TestUserService`)
- Test functions: `test_should_expected_behavior_when_condition`

---

## 🔧 pytest Fixtures

### Basic Fixtures

```python
# tests/conftest.py
import pytest
from typing import Generator
from datetime import datetime, UTC
from mcp_server.models import User
from mcp_server.database import DatabaseConnection

@pytest.fixture
def sample_user() -> User:
    """Provide a sample user for testing."""
    return User(
        id=1,
        name="Test User",
        email="test@example.com",
        created_at=datetime.now(UTC),
        is_active=True
    )

@pytest.fixture
def user_list() -> list[User]:
    """Provide a list of sample users."""
    return [
        User(id=1, name="User 1", email="user1@example.com"),
        User(id=2, name="User 2", email="user2@example.com"),
        User(id=3, name="User 3", email="user3@example.com"),
    ]

@pytest.fixture
def db_connection() -> Generator[DatabaseConnection, None, None]:
    """Provide a database connection with cleanup."""
    connection = DatabaseConnection(":memory:")
    connection.connect()
    yield connection
    connection.close()
```

### Fixture Scopes

```python
import pytest

# Function scope (default) - run for each test
@pytest.fixture
def function_fixture():
    return "new instance per test"

# Class scope - run once per test class
@pytest.fixture(scope="class")
def class_fixture():
    return "shared within class"

# Module scope - run once per module
@pytest.fixture(scope="module")
def module_fixture():
    return "shared within module"

# Session scope - run once per test session
@pytest.fixture(scope="session")
def session_fixture():
    return "shared across all tests"
```

### Fixture Factories

```python
import pytest
from typing import Callable

@pytest.fixture
def user_factory() -> Callable:
    """Factory to create multiple users with different data."""
    def _create_user(name: str = "Test User", email: str | None = None):
        if email is None:
            email = f"{name.lower().replace(' ', '.')}@example.com"
        return User(name=name, email=email)
    return _create_user

def test_multiple_users(user_factory):
    """Test with multiple users created by factory."""
    user1 = user_factory("Alice")
    user2 = user_factory("Bob")
    assert user1.email == "alice@example.com"
    assert user2.email == "bob@example.com"
```

### Auto-use Fixtures

```python
import pytest

@pytest.fixture(autouse=True)
def reset_database():
    """Automatically reset database before each test."""
    Database.reset()
    yield
    Database.cleanup()

@pytest.fixture(autouse=True, scope="function")
def setup_logging(caplog):
    """Automatically configure logging for each test."""
    caplog.set_level(logging.DEBUG)
```

---

## 🎯 Test Patterns

### Arrange-Act-Assert (AAA) Pattern

```python
def test_should_update_user_email_when_valid(sample_user):
    """Test user email update with valid input."""
    # Arrange
    new_email = "newemail@example.com"

    # Act
    sample_user.update_email(new_email)

    # Assert
    assert sample_user.email == new_email
```

### Parametrized Tests

```python
import pytest

@pytest.mark.parametrize("age,expected", [
    (17, False),  # Below minimum
    (18, True),   # At minimum
    (65, True),   # Within range
    (66, False),  # Above maximum
])
def test_should_validate_age_correctly(age: int, expected: bool):
    """Test age validation for different values."""
    result = is_eligible_for_service(age)
    assert result == expected

@pytest.mark.parametrize("input_email,is_valid", [
    ("valid@example.com", True),
    ("invalid.email", False),
    ("@example.com", False),
    ("user@", False),
    ("", False),
])
def test_email_validation(input_email: str, is_valid: bool):
    """Test email validation with various formats."""
    if is_valid:
        assert validate_email(input_email) == input_email
    else:
        with pytest.raises(ValueError):
            validate_email(input_email)
```

### Exception Testing

```python
import pytest

def test_should_raise_error_when_invalid_id():
    """Test error handling for invalid user ID."""
    with pytest.raises(ValueError, match="User ID must be positive"):
        get_user(-1)

def test_should_raise_error_with_specific_message():
    """Test exception message content."""
    with pytest.raises(ValidationError) as exc_info:
        validate_user_data({"email": "invalid"})

    assert "Invalid email format" in str(exc_info.value)
    assert exc_info.value.field_name == "email"
```

---

## 🧩 Mocking & Patching

### Using unittest.mock

```python
import pytest
from unittest.mock import Mock, patch, MagicMock, call

def test_should_call_api_with_correct_params():
    """Test API call with mocked HTTP client."""
    # Create mock
    mock_client = Mock()
    mock_client.get.return_value = {"status": "success", "data": []}

    # Use mock
    service = UserService(client=mock_client)
    result = service.fetch_users()

    # Verify
    mock_client.get.assert_called_once_with("/users")
    assert result == []

def test_should_handle_api_error():
    """Test error handling with mocked exception."""
    mock_client = Mock()
    mock_client.get.side_effect = ConnectionError("Network error")

    service = UserService(client=mock_client)

    with pytest.raises(ServiceError):
        service.fetch_users()
```

### Using pytest-mock

```python
def test_should_send_notification(mocker):
    """Test notification sending with pytest-mock."""
    # Mock external dependency
    mock_email = mocker.patch('mcp_server.notifications.send_email')

    # Execute code
    notify_user("user@example.com", "Welcome!")

    # Verify
    mock_email.assert_called_once_with(
        to="user@example.com",
        subject="Welcome!",
        body=mocker.ANY
    )

def test_should_log_on_error(mocker):
    """Test logging with mocked logger."""
    mock_logger = mocker.patch('mcp_server.services.logger')

    service = UserService()
    service.process_invalid_data({})

    mock_logger.error.assert_called_once()
```

### Patch Decorators

```python
from unittest.mock import patch

@patch('mcp_server.services.ExternalAPI')
def test_with_patched_api(mock_api_class):
    """Test with patched API class."""
    # Configure mock
    mock_api_instance = mock_api_class.return_value
    mock_api_instance.fetch.return_value = {"data": "test"}

    # Test code that uses ExternalAPI
    result = process_external_data()

    assert result == {"data": "test"}
    mock_api_instance.fetch.assert_called_once()

@patch.object(UserRepository, 'find_by_id')
def test_with_patched_method(mock_find):
    """Test with patched repository method."""
    mock_find.return_value = User(id=1, name="Test")

    service = UserService()
    user = service.get_user(1)

    assert user.name == "Test"
```

---

## 🔄 Async Testing

### Testing Async Functions

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    """Test async function execution."""
    result = await async_process_data(["item1", "item2"])
    assert len(result) == 2

@pytest.mark.asyncio
async def test_async_context_manager():
    """Test async context manager."""
    async with AsyncDatabaseConnection() as db:
        result = await db.query("SELECT * FROM users")
        assert result is not None
```

### Testing Concurrent Operations

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_concurrent_processing():
    """Test concurrent task processing."""
    tasks = [
        process_item(1),
        process_item(2),
        process_item(3),
    ]
    results = await asyncio.gather(*tasks)
    assert len(results) == 3

@pytest.mark.asyncio
async def test_timeout_handling():
    """Test async timeout handling."""
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_operation(), timeout=1.0)
```

---

## 📊 Test Coverage

### Coverage Requirements
- **Minimum coverage**: 80% line coverage
- **Branch coverage**: 80% branch coverage
- **Critical business logic**: 90%+ coverage
- **All public APIs**: Must have tests

### Coverage Configuration

```toml
[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/__init__.py",
]
branch = true

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "def __str__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]

[tool.coverage.html]
directory = "htmlcov"
```

### Coverage Commands

```bash
# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Fail if coverage below threshold
pytest --cov=src --cov-fail-under=80

# Show only uncovered code
pytest --cov=src --cov-report=term-missing:skip-covered
```

---

## 🏷️ Test Markers

### Built-in Markers

```python
import pytest

@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    """Test for future feature."""
    pass

@pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires Python 3.10+")
def test_python_310_feature():
    """Test requiring Python 3.10+."""
    pass

@pytest.mark.xfail(reason="Known bug #123")
def test_known_issue():
    """Test with known failure."""
    assert False
```

### Custom Markers

```python
# tests/conftest.py
import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "unit: unit tests")

# tests/test_module.py
import pytest

@pytest.mark.slow
def test_slow_operation():
    """Test that takes a long time."""
    pass

@pytest.mark.integration
def test_database_integration():
    """Integration test with database."""
    pass

# Run tests with markers
# pytest -m "not slow"           # Skip slow tests
# pytest -m "integration"        # Run only integration tests
# pytest -m "unit and not slow"  # Run unit tests except slow ones
```

---

## 🔍 Advanced Testing Patterns

### Class-based Tests

```python
import pytest

class TestUserService:
    """Test suite for UserService."""

    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        """Set up test dependencies."""
        self.mock_repo = mocker.Mock()
        self.service = UserService(self.mock_repo)

    def test_get_user_success(self):
        """Test successful user retrieval."""
        expected_user = User(id=1, name="John")
        self.mock_repo.find_by_id.return_value = expected_user

        result = self.service.get_user(1)

        assert result == expected_user
        self.mock_repo.find_by_id.assert_called_once_with(1)

    def test_get_user_not_found(self):
        """Test user not found scenario."""
        self.mock_repo.find_by_id.return_value = None

        with pytest.raises(ValueError, match="User not found"):
            self.service.get_user(999)
```

### Property-based Testing (Hypothesis)

```python
from hypothesis import given, strategies as st
import pytest

@given(st.integers(min_value=0, max_value=150))
def test_age_validation_property(age):
    """Property-based test for age validation."""
    if 18 <= age <= 65:
        assert is_valid_age(age)
    else:
        assert not is_valid_age(age)

@given(st.text(min_size=1))
def test_string_processing_property(text):
    """Test string processing with any non-empty string."""
    result = process_string(text)
    assert isinstance(result, str)
    assert len(result) >= 0
```

### Snapshot Testing

```python
import pytest
from syrupy.assertion import SnapshotAssertion

def test_user_serialization(snapshot: SnapshotAssertion):
    """Test user serialization output."""
    user = User(id=1, name="Test", email="test@example.com")
    result = user.to_dict()
    assert result == snapshot

def test_api_response(snapshot: SnapshotAssertion):
    """Test API response structure."""
    response = get_user_profile(1)
    assert response == snapshot
```

---

## 🐛 Debugging Tests

### Using pytest Debug Features

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger at start of each test
pytest --trace

# Show local variables in traceback
pytest -l

# Verbose output with full diffs
pytest -vv

# Show print statements
pytest -s

# Run last failed tests only
pytest --lf

# Run failed tests first
pytest --ff
```

### Using Fixtures for Debugging

```python
import pytest

@pytest.fixture
def debug_fixture(request):
    """Fixture for debugging test context."""
    print(f"\nTest: {request.node.name}")
    yield
    print(f"Test completed: {request.node.name}")

def test_with_debug(debug_fixture):
    """Test with debug output."""
    # Test code here
    pass
```

---

## ⚡ Parallel Testing with pytest-xdist

### Installation and Basic Setup

```bash
# Install pytest-xdist
uv add --dev pytest-xdist

# Run tests in parallel (auto-detect CPU count)
pytest -n auto

# Run tests with specific number of workers
pytest -n 4

# Run tests with load balancing
pytest -n auto --dist loadscope
```

### Configuration in pyproject.toml

```toml
[tool.pytest.ini_options]
# Basic parallel configuration
addopts = [
    "-n", "auto",              # Auto-detect CPU count
    "--dist", "loadscope",     # Distribution strategy
    "--maxfail", "5",          # Stop after 5 failures
]

# Parallel test markers
markers = [
    "serial: marks tests that must run serially (not in parallel)",
    "parallel: marks tests that can run in parallel",
]
```

### Distribution Strategies

```python
"""
pytest-xdist Distribution Strategies:

1. load (default)
   - Distributes tests evenly across workers
   - Best for tests of similar duration
   - Command: pytest -n auto --dist load

2. loadscope
   - Distributes test classes/modules together
   - Keeps related tests on same worker
   - Better for tests with expensive fixtures
   - Command: pytest -n auto --dist loadscope

3. loadfile
   - Distributes entire test files to workers
   - All tests in file run on same worker
   - Good for file-scoped fixtures
   - Command: pytest -n auto --dist loadfile

4. loadgroup
   - Distributes tests by xdist_group marker
   - Manual control over test grouping
   - Command: pytest -n auto --dist loadgroup

5. each
   - Runs all tests on each worker
   - Used for cross-platform testing
   - Command: pytest -n 3 --dist each
"""

# Example: Grouping related tests
import pytest

@pytest.mark.xdist_group(name="database")
def test_user_creation():
    """Runs in same group as other database tests."""
    pass

@pytest.mark.xdist_group(name="database")
def test_user_query():
    """Runs in same group as other database tests."""
    pass

@pytest.mark.xdist_group(name="api")
def test_api_endpoint():
    """Runs in different group."""
    pass
```

### Fixture Scope with Parallel Tests

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Session-scoped fixture (shared across worker)
@pytest.fixture(scope="session")
def event_loop():
    """
    Create event loop for entire test session.

    Each worker gets its own event loop.
    """
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# Worker-scoped database engine
@pytest.fixture(scope="session")
def db_engine(worker_id):
    """
    Create separate database per worker.

    Prevents database conflicts in parallel tests.
    """
    # Use worker_id to create unique database
    if worker_id == "master":
        db_url = "postgresql+asyncpg://localhost/test_db"
    else:
        db_url = f"postgresql+asyncpg://localhost/test_db_{worker_id}"

    engine = create_async_engine(db_url)
    yield engine
    engine.sync_engine.dispose()

# Session factory per worker
@pytest.fixture(scope="session")
def session_factory(db_engine):
    """Create session factory for worker."""
    return sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

# Function-scoped session
@pytest.fixture
async def db_session(session_factory):
    """Create fresh session for each test."""
    async with session_factory() as session:
        yield session
```

### Database Isolation Per Worker

```python
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine

@pytest.fixture(scope="session")
def worker_db_url(worker_id):
    """
    Generate unique database URL per worker.

    Pattern: test_db_gw0, test_db_gw1, etc.
    """
    if worker_id == "master":
        return "postgresql+asyncpg://localhost/test_db"
    return f"postgresql+asyncpg://localhost/test_db_{worker_id}"

@pytest.fixture(scope="session", autouse=True)
async def setup_worker_database(worker_db_url, worker_id):
    """
    Create and setup database for worker.

    Runs once per worker at session start.
    """
    if worker_id == "master":
        yield
        return

    # Extract database name
    db_name = worker_db_url.split("/")[-1]

    # Create database
    admin_engine = create_async_engine(
        "postgresql+asyncpg://localhost/postgres"
    )

    async with admin_engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")

        # Drop existing database
        await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))

        # Create new database
        await conn.execute(text(f"CREATE DATABASE {db_name}"))

    await admin_engine.dispose()

    # Run migrations on worker database
    worker_engine = create_async_engine(worker_db_url)
    async with worker_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await worker_engine.dispose()

    yield

    # Cleanup: Drop database after tests
    async with admin_engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))

    await admin_engine.dispose()
```

### Test Data Management for Parallel Runs

```python
import pytest
from typing import Generator

# Shared test data (read-only)
@pytest.fixture(scope="session")
def reference_data():
    """
    Reference data shared across all workers.

    Should be read-only to avoid conflicts.
    """
    return {
        "countries": ["USA", "UK", "Canada"],
        "currencies": ["USD", "GBP", "CAD"],
    }

# Worker-specific test data
@pytest.fixture(scope="session")
def worker_test_data(worker_id):
    """
    Generate unique test data per worker.

    Prevents ID conflicts in parallel tests.
    """
    base_id = 0 if worker_id == "master" else int(worker_id.replace("gw", "")) + 1
    offset = base_id * 1000

    return {
        "user_id_start": 1000 + offset,
        "order_id_start": 5000 + offset,
        "product_id_start": 10000 + offset,
    }

# Function-scoped unique IDs
@pytest.fixture
def unique_user_id(worker_test_data) -> Generator[int, None, None]:
    """
    Generate unique user ID for test.

    Uses worker offset + counter to ensure uniqueness.
    """
    import itertools
    counter = itertools.count(start=worker_test_data["user_id_start"])
    yield next(counter)

# Usage
def test_create_user(db_session, unique_user_id):
    """Test user creation with unique ID."""
    user = User(id=unique_user_id, name=f"User_{unique_user_id}")
    db_session.add(user)
    # No ID conflicts with other workers
```

### Marking Tests for Serial Execution

```python
import pytest

# Mark test to run serially (not in parallel)
@pytest.mark.serial
def test_global_state_modification():
    """
    Test that modifies global state.

    Must run serially to avoid conflicts.
    """
    import os
    os.environ["GLOBAL_CONFIG"] = "test_value"
    # Test logic
    del os.environ["GLOBAL_CONFIG"]

# Configure pytest to run serial tests separately
# In pyproject.toml:
"""
[tool.pytest.ini_options]
markers = [
    "serial: marks tests that must run serially",
]
"""

# Run parallel tests excluding serial
# pytest -n auto -m "not serial"

# Then run serial tests alone
# pytest -m serial
```

### Handling Shared Resources

```python
import pytest
import filelock
from pathlib import Path

@pytest.fixture(scope="session")
def shared_file_lock(tmp_path_factory):
    """
    Create file lock for shared resource access.

    Prevents race conditions when accessing shared files.
    """
    lockfile = tmp_path_factory.getbasetemp().parent / "shared.lock"
    return filelock.FileLock(str(lockfile))

def test_shared_resource_access(shared_file_lock, tmp_path):
    """
    Test that safely accesses shared resource.

    Uses lock to prevent parallel access conflicts.
    """
    shared_file = tmp_path.parent / "shared_data.json"

    with shared_file_lock:
        # Critical section - only one worker at a time
        data = {}
        if shared_file.exists():
            data = json.loads(shared_file.read_text())

        data["test_run"] = datetime.now().isoformat()

        shared_file.write_text(json.dumps(data))
```

### Troubleshooting Parallel Tests

```python
"""
Common Issues and Solutions:

1. Flaky Tests (Pass/Fail Randomly)
   Issue: Race conditions, shared state
   Solution:
   - Use worker-specific test data
   - Ensure test independence
   - Use locks for shared resources

   # Debug flaky tests
   pytest -n auto --looponfail  # Repeat failing tests

2. Fixture Scope Issues
   Issue: Session fixtures not working
   Solution:
   - Check fixture scope compatibility
   - Use pytest-xdist compatible scopes
   - Avoid module-scoped fixtures with parallel tests

3. Database Conflicts
   Issue: Multiple workers accessing same DB
   Solution:
   - Create separate DB per worker
   - Use worker_id in database name
   - Implement setup_worker_database fixture

4. Port Conflicts
   Issue: Tests binding to same port
   Solution:
   # Generate unique port per worker
   @pytest.fixture
   def worker_port(worker_id):
       if worker_id == "master":
           return 8000
       return 8000 + int(worker_id.replace("gw", ""))

5. File System Conflicts
   Issue: Tests writing to same files
   Solution:
   - Use tmp_path fixture (unique per test)
   - Add worker_id to filenames
   - Use file locks for shared files

6. Slower Than Expected
   Issue: Parallel tests not faster
   Solution:
   - Check distribution strategy (try loadscope)
   - Profile tests to find bottlenecks
   - Ensure tests are truly independent

   # Profile test duration
   pytest -n auto --durations=10
"""

# Debugging helper
@pytest.fixture
def worker_info(worker_id, request):
    """Print worker information for debugging."""
    print(f"\nWorker: {worker_id}")
    print(f"Test: {request.node.name}")
    return worker_id
```

### Performance Optimization

```python
"""
Optimizing Parallel Test Performance:

1. Choose Right Distribution Strategy
   - loadscope: For tests with expensive fixtures
   - loadfile: For file-scoped fixtures
   - load: For uniform test duration

2. Balance Test Duration
   - Avoid mix of fast and slow tests
   - Consider splitting slow test files

   # Check test duration distribution
   pytest --durations=20

3. Minimize Fixture Overhead
   - Use appropriate scope (session > module > function)
   - Cache expensive operations
   - Lazy initialization when possible

4. Optimize Worker Count
   # Test different worker counts
   pytest -n 2  # Start conservative
   pytest -n 4
   pytest -n auto  # Usually optimal

5. Use Test Grouping
   # Group related tests for better caching
   @pytest.mark.xdist_group(name="heavy_fixtures")
   def test_with_expensive_setup():
       pass
"""

# Example: Cached expensive fixture
@pytest.fixture(scope="session")
def ml_model(worker_id):
    """
    Load ML model once per worker.

    Expensive operation cached at session level.
    """
    import joblib
    cache_key = f"model_{worker_id}"

    # Check cache
    if cache_key in pytest.cache:
        return pytest.cache.get(cache_key)

    # Load model (expensive)
    model = joblib.load("model.pkl")

    # Cache for session
    pytest.cache.set(cache_key, model)
    return model
```

### Integration with CI/CD

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - uses: astral-sh/setup-uv@v1

      - name: Install dependencies
        run: |
          uv sync --frozen
          uv add --dev pytest-xdist

      - name: Run parallel tests
        run: |
          # Run with parallel workers
          uv run pytest -n auto --dist loadscope \
            --maxfail=5 \
            --tb=short \
            --cov=src \
            --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

### Complete Example Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
# Parallel test configuration
addopts = [
    "-n", "auto",                    # Auto-detect CPU count
    "--dist", "loadscope",           # Keep related tests together
    "--maxfail", "5",                # Stop after 5 failures
    "--tb", "short",                 # Shorter traceback format
    "--strict-markers",              # Enforce marker registration
    "-v",                            # Verbose output
]

# Test markers
markers = [
    "serial: marks tests that must run serially (not in parallel)",
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "database: marks tests that require database",
    "integration: marks integration tests",
]

# Test discovery
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

# Parallel test specific
asyncio_mode = "auto"  # Auto-detect async tests
```

---

## ⚠️ Testing Best Practices

1. **Test one thing at a time** - Single assertion per test when possible
2. **Use descriptive test names** - Follow `test_should_behavior_when_condition` pattern
3. **Follow AAA pattern** - Arrange, Act, Assert
4. **Use fixtures for reusable data** - Don't repeat setup code
5. **Mock external dependencies** - Keep tests fast and isolated
6. **Maintain test independence** - Tests should not depend on each other
7. **Keep tests fast** - Mock I/O operations
8. **Test edge cases** - Empty inputs, null values, boundaries
9. **Test error conditions** - Validate exception handling
10. **Update tests with code** - Tests are part of the codebase

---

## 📋 Testing Checklist

- [ ] All public functions have unit tests
- [ ] Edge cases and error conditions tested
- [ ] Integration tests for component interactions
- [ ] Async functions tested with pytest.mark.asyncio
- [ ] External dependencies properly mocked
- [ ] Test coverage meets minimum threshold (80%)
- [ ] Tests follow naming conventions
- [ ] Fixtures used for common setup
- [ ] Tests are independent and isolated
- [ ] Tests run quickly (< 1 second per unit test)

---

**Back to [Core Guide]mcp://resources/patterns/python/patterns-core**
