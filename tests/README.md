# MCP Server Test Suite

Comprehensive unit and integration tests for the MCP Resource Server.

## Test Coverage

**Total Coverage:** 89.47% (exceeds 80% target)
**Total Tests:** 201 tests
**Execution Time:** ~1.15 seconds (well under 2-minute target)

## Test Structure

```
tests/
├── unit/                              # Unit tests (isolated component testing)
│   ├── test_cache_service.py          # Cache service tests (14 tests)
│   ├── test_resource_error_handling.py # Resource error handling tests (13 tests)
│   ├── test_resource_schemas.py        # Pydantic schema validation tests (12 tests)
│   ├── test_health_check.py            # Health check endpoint tests
│   ├── test_config.py                  # Configuration tests
│   ├── test_dependencies.py            # Dependency injection tests
│   ├── test_example_tool.py            # Example tool tests
│   └── test_example_fixtures.py        # Example fixture tests
│
├── integration/                       # Integration tests (end-to-end flows)
│   ├── test_resource_endpoints.py      # Resource endpoint integration tests (27 tests)
│   ├── test_generator_byte_identity.py # Generator byte-identical tests (47 tests) - US-037
│   ├── test_prompts.py                 # MCP prompt integration tests - TASK-011
│   ├── test_generate_command_mcp.py    # /generate command MCP integration - US-036
│   ├── test_api_endpoints.py           # API endpoint tests
│   ├── test_dependency_injection.py    # Dependency injection integration tests
│   └── test_mcp_example_tool.py        # MCP tool integration tests
│
├── e2e/                               # End-to-end tests (placeholder)
│   └── __init__.py
│
└── conftest.py                        # Shared fixtures and test configuration
```

## Running Tests

### Run all tests with coverage
```bash
uv run pytest tests/ --cov=src/mcp_server --cov-report=term --cov-report=html
```

### Run specific test categories
```bash
# Unit tests only
uv run pytest tests/unit/

# Integration tests only
uv run pytest tests/integration/

# Specific test file
uv run pytest tests/unit/test_cache_service.py -v

# Specific test class
uv run pytest tests/unit/test_cache_service.py::TestGetOrFetch -v
```

### Run with coverage report
```bash
# Terminal report with HTML output
uv run pytest tests/ --cov=src/mcp_server --cov-report=term --cov-report=html

# View HTML coverage report (opens in browser)
open htmlcov/index.html
```

### Run with test timings
```bash
# Show slowest 10 tests
uv run pytest tests/ --durations=10
```

## Test Categories

### 1. Cache Service Tests (`test_cache_service.py`)

Tests for `ResourceCacheService` class:

- **Initialization tests**: Default/custom configuration, connection lifecycle
- **Cache hit/miss tests**: Verify cache-aside pattern implementation
- **Error handling tests**: Redis connection errors, graceful degradation
- **Invalidation tests**: Pattern-based cache invalidation
- **Cache size tests**: Monitor cache growth

**Coverage:** 100% for `src/mcp_server/services/cache.py`

### 2. Resource Error Handling Tests (`test_resource_error_handling.py`)

Tests for error scenarios in resource loading:

- **File not found**: 404 errors for missing resources
- **Permission errors**: 403 errors for unreadable files
- **Path traversal protection**: Security validation
- **I/O errors**: Disk read failures
- **Cache service errors**: Error propagation and handling

**Coverage:** Covers error paths in `src/mcp_server/api/routes/resources.py`

### 3. Resource Schema Tests (`test_resource_schemas.py`)

Tests for Pydantic models and input validation:

- **ResourceNameValidator**: Path traversal protection, invalid characters
- **PatternResourceRequest**: Language parameter validation
- **ResourceResponse**: Response structure validation

**Coverage:** 97% for `src/mcp_server/api/schemas/resources.py`

### 4. Resource Endpoint Integration Tests (`test_resource_endpoints.py`)

End-to-end tests for resource loading:

- **Pattern resources**: Python/Go pattern file loading
- **SDLC core**: Framework core content loading
- **Template resources**: All 10 template types
- **Security tests**: Path traversal attack prevention
- **Error handling**: Missing files, permission errors
- **Response format**: URI, content, size_bytes validation

**Coverage:** Validates full request → response flow

### 5. Generator Byte Identity Tests (`test_generator_byte_identity.py`) - US-037

End-to-end integration tests for all 10 generator types via MCP prompts:

- **Byte-identical comparison**: MCP vs local file approach produce identical generator XML
- **Performance benchmarks**: Collect p50, p95, p99 latencies across 100+ iterations
- **Error scenarios**: Missing prompts, path traversal attacks, malformed XML handling
- **Test reporting**: Comprehensive performance summary with pass/fail status
- **CI/CD integration**: Automated tests run on every commit

**Test Classes:**
- `TestByteIdenticalGeneration`: Validates MCP and local file content are byte-identical (30 tests)
- `TestPerformanceTargets`: Validates p95 <500ms for all generators (11 tests)
- `TestErrorScenarios`: Validates error handling (3 tests)
- `TestFixtureReusability`: Validates extensible test design (1 test)
- `TestCICDIntegration`: Validates CI/CD execution (2 tests)

**Performance Targets (US-037 NFR-Performance-02):**
- p95 latency <500ms for all 10 generator types
- p99 latency <1000ms for all 10 generator types
- Test suite completes in <10 minutes

**Total Tests:** 47 tests covering all 10 generator types
**Generators Tested:** product-vision, initiative, epic, prd, high-level-user-story, backlog-story, spike, adr, tech-spec, implementation-task

**Coverage:** Validates generator loading, caching, security, and performance

## Coverage Details

| Module | Coverage | Missing Lines |
|--------|----------|--------------|
| `services/cache.py` | 100% | None |
| `core/constants.py` | 100% | None |
| `core/exceptions.py` | 100% | None |
| `tools/example_tool.py` | 98% | 181 |
| `api/schemas/resources.py` | 97% | 126 |
| `config.py` | 96% | 125 |
| `core/dependencies.py` | 94% | 90, 135-137 |
| `main.py` | 94% | 87, 239-245 |
| `api/routes/resources.py` | 78% | Error handling paths (tested in unit tests) |

**Overall:** 89.47% coverage across 513 statements

## Security Testing

Security tests validate:

1. **Path traversal protection**: `../etc/passwd`, `../../etc/passwd`, `foo/../bar`
2. **Absolute path rejection**: `/etc/passwd`, `/core`
3. **Invalid characters**: Dots, semicolons, pipes, uppercase
4. **Base directory restriction**: Files outside configured base directory
5. **Language parameter validation**: Only lowercase alphabetic characters

All security tests pass with 100% success rate.

## Performance

- **Full suite execution**: ~1.15 seconds
- **Slowest test**: 0.11s (health check uptime test)
- **Average test time**: <0.01s per test
- **Target**: <2 minutes (achieved: 1.15s = 58x faster than target)

## Test Execution in CI/CD

Tests are executed automatically on every commit via GitHub Actions:

```yaml
- name: Run tests
  run: uv run pytest tests/ --cov=src/mcp_server --cov-fail-under=80
```

Pipeline blocks merge if coverage drops below 80%.

## Acceptance Criteria Status

| Scenario | Status | Details |
|----------|--------|---------|
| Unit tests for resource handlers | ✅ Pass | All resource handlers tested |
| Unit tests for cache service | ✅ Pass | 14 tests, 100% coverage |
| Integration tests for end-to-end flows | ✅ Pass | 27 integration tests |
| Security tests validate path traversal | ✅ Pass | All attack vectors blocked |
| Error handling tests | ✅ Pass | 404, 403, 500 scenarios covered |
| Test coverage ≥80% | ✅ Pass | 89.47% coverage achieved |
| All tests pass in CI/CD | ✅ Pass | 201/201 tests passing |
| Test execution time <2 minutes | ✅ Pass | 1.15 seconds (58x faster) |

## Completed User Stories

### US-034: Unit and Integration Testing for Resource Server

**Status:** ✅ Complete
**Date Completed:** 2025-10-21

All acceptance criteria met:
- ✅ 89.47% test coverage (exceeds 80% target)
- ✅ 201 tests passing (100% pass rate)
- ✅ 1.15s execution time (under 2-minute target)
- ✅ Comprehensive security testing
- ✅ Error handling coverage
- ✅ Cache service fully tested

### US-037: Integration Testing for All Generator Types

**Status:** ✅ Complete
**Date Completed:** 2025-10-21

All acceptance criteria met:
- ✅ All 10 generator types produce byte-identical artifacts (MCP vs local file)
- ✅ Performance targets met: p95 <500ms for all generators
- ✅ Test suite runs in CI/CD pipeline (<10 minute budget)
- ✅ Detailed failure reporting with unified diffs
- ✅ Error scenarios tested (missing prompt, MCP Server unavailable, path traversal)
- ✅ Test fixtures reusable for new generator types
- ✅ Performance report generated with pass/fail status

**Test Implementation:**
- File: `tests/integration/test_generator_byte_identity.py`
- Total Tests: 47 tests
- Generators Covered: 10 types (product-vision, initiative, epic, prd, hls, backlog-story, spike, adr, tech-spec, implementation-task)
- Performance Tracking: Custom `PerformanceTracker` class with percentile calculation
- Fixtures: Extensible fixture structure in `tests/fixtures/`
