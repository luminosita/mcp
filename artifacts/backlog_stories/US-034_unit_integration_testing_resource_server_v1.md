# User Story: Unit and Integration Testing for Resource Server

## Metadata
- **Story ID:** US-034
- **Title:** Comprehensive Unit and Integration Testing for Resource Server
- **Type:** Feature
- **Status:** Draft
- **Priority:** High (quality assurance - ensures resource server reliability before pilot deployment)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-006 (MCP Resources Migration)
- **Functional Requirements Covered:** NFR-Maintainability-01 (Test coverage ≥80%)
- **Informed By Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Non-Functional Requirements - NFR-Maintainability-01: Test coverage ≥80%
- **Functional Requirements Coverage:**
  - **NFR-Maintainability-01:** Unit test coverage SHALL be ≥80% for all Python modules

**Parent High-Level Story:** [HLS-006: MCP Resources Migration]
- **Link:** `/artifacts/hls/HLS-006_mcp_resources_migration_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 7: Unit and Integration Testing for Resource Server

## User Story
As a Framework Maintainer, I want comprehensive unit and integration tests for the resource server, so that I can deploy with confidence knowing resource loading, caching, and error handling work correctly.

## Description
Resource server implementation (US-030, US-031, US-032, US-033) provides core MCP resources functionality, but systematic test coverage is needed to ensure reliability before pilot deployment.

This story implements comprehensive testing suite covering:
1. **Unit Tests:** Test individual components in isolation (resource handlers, cache service, validation logic)
2. **Integration Tests:** Test end-to-end resource loading flows (MCP client → server → file system → cache)
3. **Security Tests:** Validate path traversal protection, input sanitization
4. **Error Handling Tests:** Verify graceful handling of missing files, I/O errors, cache failures
5. **Cache Behavior Tests:** Validate TTL expiration, cache hit/miss, invalidation

Target: ≥80% code coverage per PRD-006 NFR-Maintainability-01.

## Implementation Research References

**Primary Research Document:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

**Technical Patterns Applied:**
- **§7.1: Unit Testing:** Test tool logic with pytest, AsyncMock for async functions (ref: Implementation Research §7.1 - Unit Testing, lines 947-988)
- **§7.2: Integration Testing:** Test MCP protocol communication end-to-end using MCP client (ref: Implementation Research §7.2 - Integration Testing, lines 992-1024)
- **§5.3: Input Validation Testing:** Test path traversal attack prevention (ref: Implementation Research §5.3 - Input Validation and Command Injection Prevention, lines 736-762)

**Testing Strategy:**
- pytest for test framework with async support (pytest-asyncio)
- pytest-cov for coverage reporting
- AsyncMock for mocking async dependencies (Redis, file I/O)
- httpx.AsyncClient for integration testing (FastAPI test client)

## Functional Requirements
1. Unit tests cover all resource handler functions (patterns, templates, SDLC core)
2. Unit tests cover cache service (get_or_fetch, invalidation, TTL expiration)
3. Unit tests cover input validation (resource name sanitization, path traversal protection)
4. Integration tests cover end-to-end resource loading (request → response)
5. Integration tests cover caching behavior (cache hit, cache miss, TTL expiration)
6. Security tests validate path traversal attack prevention
7. Error handling tests cover missing files, disk I/O errors, cache failures
8. Test coverage ≥80% measured by pytest-cov
9. All tests pass in CI/CD pipeline
10. Test execution time <2 minutes for full suite

## Non-Functional Requirements
- **Test Coverage:** ≥80% line coverage (per PRD-006 NFR-Maintainability-01)
- **Test Execution Time:** Full test suite completes <2 minutes (fast feedback)
- **Test Reliability:** Tests deterministic, no flaky tests (retry until stable)
- **Maintainability:** Tests follow patterns-testing.md standards (fixtures, parametrization)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** When implementing tests, follow established implementation standards. Supplement with story-specific technical guidance.

**References to Implementation Standards:**
- **prompts/CLAUDE/python/patterns-testing.md:** Follow testing patterns (80% coverage minimum, async test support with pytest-asyncio, fixtures for database/cache access)
- **prompts/CLAUDE/python/patterns-tooling.md:** Use Taskfile commands (`task test`, `task test:cov`, `task test:watch`)
- **prompts/CLAUDE/python/patterns-typing.md:** Apply type hints to test functions for clarity

### Implementation Guidance

**Story-Specific Technical Approach:**

1. **Unit Tests for Resource Handlers:**
   ```python
   import pytest
   from unittest.mock import AsyncMock, patch
   from httpx import AsyncClient
   from mcp_server.main import app

   @pytest.mark.asyncio
   async def test_get_pattern_resource_success():
       """Tests successful pattern resource retrieval"""
       async with AsyncClient(app=app, base_url="http://test") as client:
           response = await client.get("/mcp/resources/patterns/core")

       assert response.status_code == 200
       assert response.json()["uri"] == "mcp://resources/patterns/core"
       assert "content" in response.json()
       assert len(response.json()["content"]) > 0

   @pytest.mark.asyncio
   async def test_get_pattern_resource_not_found():
       """Tests 404 error for missing pattern resource"""
       async with AsyncClient(app=app, base_url="http://test") as client:
           response = await client.get("/mcp/resources/patterns/nonexistent")

       assert response.status_code == 404
       assert "Resource not found" in response.json()["detail"]

   @pytest.mark.asyncio
   async def test_get_pattern_resource_path_traversal():
       """Tests path traversal attack prevention"""
       async with AsyncClient(app=app, base_url="http://test") as client:
           response = await client.get("/mcp/resources/patterns/../../../etc/passwd")

       assert response.status_code == 400
       assert "Invalid resource name" in response.json()["detail"]
   ```

2. **Unit Tests for Cache Service:**
   ```python
   import pytest
   from unittest.mock import AsyncMock
   from mcp_server.cache import ResourceCacheService

   @pytest.mark.asyncio
   async def test_cache_get_or_fetch_cache_hit(mock_redis):
       """Tests cache hit returns cached content immediately"""
       mock_redis.get = AsyncMock(return_value='{"content": "cached data"}')
       cache = ResourceCacheService(mock_redis)

       result = await cache.get_or_fetch("resource:patterns:core", None, None)

       assert result == "cached data"
       mock_redis.get.assert_called_once_with("resource:patterns:core")

   @pytest.mark.asyncio
   async def test_cache_get_or_fetch_cache_miss(mock_redis):
       """Tests cache miss loads from source and caches"""
       mock_redis.get = AsyncMock(return_value=None)
       mock_redis.setex = AsyncMock()
       fetch_func = AsyncMock(return_value="fresh data")
       cache = ResourceCacheService(mock_redis)

       result = await cache.get_or_fetch("resource:patterns:core", fetch_func, "path.md")

       assert result == "fresh data"
       fetch_func.assert_called_once_with("path.md")
       mock_redis.setex.assert_called_once()
   ```

3. **Integration Tests for End-to-End Flows:**
   ```python
   import pytest
   from httpx import AsyncClient
   from mcp_server.main import app

   @pytest.mark.asyncio
   async def test_resource_loading_end_to_end():
       """Tests full resource loading flow: request → file load → response"""
       async with AsyncClient(app=app, base_url="http://test") as client:
           # First request - cache miss (loads from disk)
           response1 = await client.get("/mcp/resources/sdlc/core")
           assert response1.status_code == 200
           content1 = response1.json()["content"]

           # Second request - cache hit (returns cached)
           response2 = await client.get("/mcp/resources/sdlc/core")
           assert response2.status_code == 200
           content2 = response2.json()["content"]

           # Content should be identical
           assert content1 == content2
   ```

4. **Test Fixtures:**
   ```python
   import pytest
   from unittest.mock import AsyncMock

   @pytest.fixture
   def mock_redis():
       """Provides mock Redis client for testing"""
       mock = AsyncMock()
       mock.get = AsyncMock(return_value=None)
       mock.setex = AsyncMock()
       mock.delete = AsyncMock()
       return mock

   @pytest.fixture
   async def test_client():
       """Provides test HTTP client for FastAPI app"""
       async with AsyncClient(app=app, base_url="http://test") as client:
           yield client
   ```

5. **Coverage Configuration (pytest.ini):**
   ```ini
   [pytest]
   testpaths = tests
   asyncio_mode = auto
   addopts = --cov=mcp_server --cov-report=term --cov-report=html --cov-fail-under=80
   ```

### Technical Tasks
- [ ] Create test directory structure (`tests/unit/`, `tests/integration/`)
- [ ] Write unit tests for pattern resource handler (success, not found, path traversal)
- [ ] Write unit tests for template resource handler (success, not found, whitelist validation)
- [ ] Write unit tests for SDLC core resource handler
- [ ] Write unit tests for cache service (get_or_fetch, cache hit, cache miss, TTL expiration)
- [ ] Write unit tests for input validation (path traversal, invalid characters)
- [ ] Write integration tests for end-to-end resource loading (cache hit/miss scenarios)
- [ ] Write security tests for path traversal attacks
- [ ] Write error handling tests (missing files, I/O errors, cache failures)
- [ ] Create test fixtures (mock Redis, test HTTP client)
- [ ] Configure pytest.ini with coverage settings (≥80%)
- [ ] Add Taskfile commands for testing (`task test`, `task test:cov`, `task test:watch`)
- [ ] Validate all tests pass and coverage ≥80%

## Acceptance Criteria

### Scenario 1: Unit tests for resource handlers pass
**Given** resource handler unit tests implemented
**When** I run `task test tests/unit/test_resource_handlers.py`
**Then** all tests pass (100% pass rate)
**And** tests cover: success cases, 404 errors, 400 errors (path traversal)
**And** test execution time <30 seconds

### Scenario 2: Unit tests for cache service pass
**Given** cache service unit tests implemented
**When** I run `task test tests/unit/test_cache_service.py`
**Then** all tests pass (100% pass rate)
**And** tests cover: cache hit, cache miss, TTL expiration, invalidation
**And** tests use AsyncMock for Redis client

### Scenario 3: Integration tests for end-to-end flows pass
**Given** integration tests implemented
**When** I run `task test tests/integration/test_resource_loading.py`
**Then** all tests pass (100% pass rate)
**And** tests cover: full request → response flow, cache hit/miss behavior
**And** tests use real FastAPI test client (httpx.AsyncClient)

### Scenario 4: Security tests validate path traversal protection
**Given** security tests implemented
**When** I run `task test tests/security/test_path_traversal.py`
**Then** all tests pass (100% pass rate)
**And** tests attempt path traversal attacks (../, absolute paths, etc.)
**And** all attacks return 400 error (Bad Request)

### Scenario 5: Error handling tests pass
**Given** error handling tests implemented
**When** I run `task test tests/unit/test_error_handling.py`
**Then** all tests pass (100% pass rate)
**And** tests cover: missing files (404), disk I/O errors (500), cache failures (graceful degradation)

### Scenario 6: Test coverage ≥80%
**Given** comprehensive test suite implemented
**When** I run `task test:cov`
**Then** pytest-cov reports coverage ≥80%
**And** coverage report shows line coverage per module
**And** uncovered lines identified for investigation

### Scenario 7: All tests pass in CI/CD pipeline
**Given** test suite integrated into CI/CD (GitHub Actions or similar)
**When** pull request submitted with resource server changes
**Then** CI/CD runs full test suite automatically
**And** all tests pass (100% pass rate)
**And** CI/CD blocks merge if coverage <80%

### Scenario 8: Test execution time <2 minutes
**Given** full test suite implemented
**When** I run `task test` (all tests)
**Then** test execution completes <2 minutes
**And** fast feedback for developers during TDD workflow

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 5 SP (at threshold - CONSIDER territory)
- **Developer Count:** Single developer (test implementation)
- **Domain Span:** Single domain (testing infrastructure for existing code)
- **Complexity:** Low-moderate - well-defined testing patterns from Implementation Research §7.1 and patterns-testing.md
- **Uncertainty:** Low - clear testing strategy (unit, integration, security tests), pytest framework standard
- **Override Factors:** None - not cross-domain, not security-critical (testing security features, not implementing them)

Per SDLC Section 11.6 Decision Matrix: "3-5 SP, single dev, familiar domain → CONSIDER". Since testing patterns are well-defined in Implementation Research §7.1-7.2 and patterns-testing.md provides clear standards, overhead of task decomposition is not justified.

**Note:** If test implementation uncovers significant bugs requiring refactoring, track those as separate bugs/stories.

## Definition of Done
- [ ] Unit tests implemented for all resource handlers (patterns, templates, SDLC core)
- [ ] Unit tests implemented for cache service
- [ ] Unit tests implemented for input validation
- [ ] Integration tests implemented for end-to-end resource loading
- [ ] Security tests implemented for path traversal protection
- [ ] Error handling tests implemented (404, 500, cache failures)
- [ ] Test fixtures created (mock Redis, test HTTP client)
- [ ] pytest.ini configured with coverage settings
- [ ] Taskfile commands added (`task test`, `task test:cov`, `task test:watch`)
- [ ] All tests pass (100% pass rate)
- [ ] Test coverage ≥80% (validated by pytest-cov)
- [ ] Tests integrated into CI/CD pipeline
- [ ] Test execution time <2 minutes (full suite)
- [ ] Product Owner approval obtained

## Additional Information
**Suggested Labels:** testing, quality-assurance, ci-cd, maintainability
**Estimated Story Points:** 5
**Dependencies:**
- **Depends On:** US-030 (patterns resource server must exist)
- **Depends On:** US-031 (templates resource server must exist)
- **Depends On:** US-032 (cache service must exist)
- **Depends On:** US-033 (performance optimization complete - stable codebase for testing)

**Related PRD Section:** PRD-006 §Non-Functional Requirements - NFR-Maintainability-01

## Decisions Made

**All technical approaches resolved.**

**D1: Testing Framework**
- **Decision:** Use pytest with pytest-asyncio for async test support
- **Rationale:** Standard Python testing framework, excellent async support, mature ecosystem (pytest-cov, pytest-asyncio, AsyncMock)
- **Source:** Implementation Research §7.1-7.2, patterns-testing.md standards

**D2: Test Coverage Target**
- **Decision:** ≥80% line coverage (per PRD-006 NFR-Maintainability-01)
- **Rationale:** PRD requirement, industry standard for production code quality
- **Validation:** pytest-cov with --cov-fail-under=80 flag

**D3: Mock Strategy for External Dependencies**
- **Decision:** Use AsyncMock for Redis and file I/O in unit tests
- **Rationale:** Isolates unit tests from external dependencies, enables fast test execution (<30 seconds per module)
- **Source:** Implementation Research §7.1 lines 952-970

**D4: Integration Test Client**
- **Decision:** Use httpx.AsyncClient for FastAPI integration tests
- **Rationale:** Official FastAPI test client, supports async operations, realistic HTTP testing
- **Source:** Implementation Research §7.2 lines 996-1004

**D5: Test Execution Time Budget**
- **Decision:** Full test suite must complete <2 minutes
- **Rationale:** Enables fast TDD feedback loops, supports pre-commit hooks
- **Validation:** Measure actual execution time, optimize if threshold exceeded

Testing strategy is straightforward: pytest + pytest-asyncio + AsyncMock + httpx.AsyncClient. Follow patterns-testing.md standards (80% coverage, fixtures, parametrization).

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-006_mcp_resources_migration_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md` (§7.1 Unit Testing, §7.2 Integration Testing, §5.3 Input Validation Testing)
- **Testing Standards:** `prompts/CLAUDE/python/patterns-testing.md`
