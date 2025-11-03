# Python Microservice Architecture Research Prompt

## Context

Establish architectural standards for scalable Python microservice implementations using FastAPI. The research will inform the creation of implementation guides for the AI Agent MCP Server project and future Python-based microservices.

**Target Framework:** FastAPI (async Python web framework)

**Core Architecture Principles:**
- **SOLID Principles** - Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **YAGNI** (You Aren't Gonna Need It) - Build only what's needed, avoid speculative features
- **Clean Architecture** - Separation of concerns with dependency rule (outer layers depend on inner layers)
- **Dependency Injection** - Decouple components, improve testability
- **DDD** (Domain-Driven Design) - Model business domain, bounded contexts, ubiquitous language
- **TDD** (Test-Driven Development) - Write tests first, red-green-refactor cycle

## Research Objectives

### Primary Research Areas

1. **Configuration Management**
   - Environment-based settings (dev, staging, production)
   - Secrets management (API keys, database credentials)
   - Configuration validation and type safety
   - 12-factor app compliance
   - **Configuration initialization patterns** (lifespan-based singleton, module-level, lazy with singleton, environment-specific factory)
   - **Common configuration mistakes** (missing startup validation, exposing secrets in health endpoints, weak default secrets)
   - **Verification and troubleshooting** (health check endpoints for config status, production safety checks)

2. **Structured Logging**
   - JSON-structured logging for machine parsing
   - Log levels and filtering strategies
   - Request ID tracing across services
   - Integration with log aggregation systems (ELK, CloudWatch, etc.)
   - **Logging initialization patterns** (lifespan, module-level, lazy, environment-specific)
   - **Common initialization mistakes** (creating loggers before configuration, multiple configurations, missing test configuration)
   - **Verification and troubleshooting** (health check endpoints, processor verification)

3. **Caching Strategies**
   - In-memory vs. distributed caching (Redis, Memcached)
   - Cache invalidation patterns
   - TTL strategies and cache warming
   - Integration with FastAPI routes
   - **CacheService initialization patterns** (lifespan with singleton, request-scoped, hybrid with dependency override)
   - **Connection pool configuration** (max connections, timeouts, health checks, keepalive settings)
   - **Monitoring connection pool health** (health check endpoints, pool stats)

4. **Data Access Patterns**
   - Repository pattern implementation
   - ORM vs. raw SQL trade-offs (SQLAlchemy, asyncpg, etc.)
   - Connection pooling and async database access
   - Database migration strategies (Alembic)
   - **Database engine and session initialization** (lifespan with singleton engine, per-request engine for testing)
   - **Repository pattern implementation** (domain layer interfaces/ports, infrastructure layer adapters, ORM model mapping)
   - **Repository dependency injection** (dependency chain setup, usage in API routes, automatic transaction management)
   - **Testing with mocked repositories** (in-memory mock implementations, dependency overrides, unit test examples)
   - **Connection pool configuration** (pool_size, max_overflow, pool_recycle, pool_pre_ping, expire_on_commit settings)

5. **External Service Integration**
   - HTTP client patterns (httpx, aiohttp)
   - Circuit breaker and retry patterns
   - Service discovery and health checks
   - API versioning strategies

6. **Dependency Injection in FastAPI**
   - FastAPI's `Depends()` system
   - Service lifecycle management (singleton, request-scoped, transient)
   - Testing with dependency overrides
   - Integration with DI containers (dependency-injector, etc.)

7. **Clean Architecture Layers**
   - Domain layer (entities, value objects, domain services)
   - Application layer (use cases, DTOs, ports)
   - Infrastructure layer (repositories, external services, frameworks)
   - Presentation layer (API routes, request/response models)

### Secondary Research Areas

8. **Testing Strategies**
   - Unit testing with pytest
   - Integration testing with TestClient
   - Mocking external dependencies
   - Test fixtures and factories
   - Coverage targets and quality gates

9. **Error Handling and Validation**
   - Pydantic models for request/response validation
   - Custom exception hierarchies
   - Global exception handlers
   - Standardized error response formats
   - **Type safety patterns** (Pydantic BaseModel, TypedDict, Protocol, Literal types)
   - **Validation patterns** (field validators, model validators, custom validation logic)
   - **Error correlation with distributed tracing** (trace context in exceptions, error sampling)

10. **Telemetry and Observability**
   - OpenTelemetry integration with FastAPI
   - Prometheus metrics exposition
   - Distributed tracing (Jaeger/Zipkin)
   - Health check patterns (liveness/readiness/startup)
   - Custom metrics and spans
   - Trace context propagation

11. **Audit Logging**
   - Structured audit events (Pydantic models)
   - Immutable audit trail storage
   - Audit context propagation (user ID, tenant ID, request ID)
   - Compliance requirements (GDPR, SOC 2, HIPAA)
   - Audit middleware patterns
   - Audit repository and query patterns

10. **Project Structure**
    - Directory organization (by layer vs. by feature)
    - Module naming conventions
    - Package organization for monorepo vs. multi-repo

## Research Scope and Guardrails

### In Scope
- **Production-ready patterns** with real-world adoption (not experimental libraries)
- **FastAPI-specific implementations** (not generic Python patterns)
- **Async-first approaches** (FastAPI's async capabilities)
- **Type-safe patterns** (leverage Python 3.10+ type hints)
- **Examples from established projects** (open-source FastAPI projects, official docs)
- **Trade-off analysis** (when to use pattern A vs. pattern B)

### Out of Scope
- Frontend frameworks (React, Vue, etc.)
- Deployment and infrastructure (Docker, Kubernetes) - focus on application code
- Authentication/Authorization libraries (OAuth, JWT) - unless part of Clean Architecture example
- Specific business domain logic - use generic examples (e.g., user management, product catalog)
- Performance benchmarking - cite existing benchmarks, don't create new ones

### Constraints
- **Minimum Python version:** 3.10+ (for modern type hints)
- **Minimum FastAPI version:** 0.100+ (current stable features)
- **Focus on async patterns** (async/await, not synchronous alternatives)
- **Prioritize stdlib and well-maintained libraries** (avoid unmaintained dependencies)

## Research Methodology

1. **Literature Review**
   - Official FastAPI documentation and tutorials
   - FastAPI GitHub discussions and issues (architectural patterns)
   - Published articles and blog posts from credible sources
   - Open-source FastAPI projects with >1000 stars (GitHub)
   - Books: "Architecture Patterns with Python" (Percival & Gregory), "Clean Architecture" (Robert Martin)

2. **Pattern Analysis**
   - Identify 3-5 alternative approaches per research area
   - Document pros/cons for each approach
   - Provide decision criteria (when to use which pattern)
   - Include code examples (10-30 lines, simplified but realistic)

3. **Source Quality Criteria**
   - **Authoritative sources:** Official docs, framework maintainers, published books
   - **Community validation:** High-engagement GitHub repos, Stack Overflow answers with 50+ votes
   - **Recency:** Prefer sources from last 2 years (Python/FastAPI evolve rapidly)
   - **Production evidence:** Patterns used in production systems, not just theoretical

## Output Format Requirements

### Document Structure

```markdown
# Python Microservice Architecture Research Report

**Document Version:** 1.0
**Research Date:** [YYYY-MM-DD]
**Researcher:** [Name/Team]
**Target Framework:** FastAPI 0.100+, Python 3.10+

## Executive Summary
[2-3 paragraphs: Key findings, recommended patterns, critical decisions]

## 1. Configuration Management
### 1.1 Recommended Approach
[Detailed explanation with rationale]

### 1.2 Implementation Example
[Code example with inline comments]

### 1.2.1 Configuration Initialization Patterns
[Multiple initialization patterns with benefits/drawbacks]
- Pattern 1: Lifespan-Based Initialization with Singleton (Recommended)
- Pattern 2: Module-Level Initialization (Simple Applications)
- Pattern 3: Lazy Initialization with Singleton (Test-Friendly)
- Pattern 4: Environment-Specific Configuration Loading (Multi-Environment)

### 1.2.2 Common Configuration Mistakes
[Anti-patterns and fixes]
- Mistake 1: Not validating configuration at startup
- Mistake 2: Exposing sensitive configuration in health endpoints
- Mistake 3: Using weak or default secrets

### 1.2.3 Verification and Troubleshooting
[Health check endpoints and troubleshooting examples]
- /health/config endpoint (non-sensitive config display)
- /health/config/validation endpoint (production safety checks)
- Troubleshooting guide (configuration not loading, validation errors, etc.)

### 1.3 Alternative Approaches
[Compare 2-3 alternatives with pros/cons]

### 1.4 Decision Criteria
[When to use this pattern vs. alternatives]

### 1.2.4 Type Safety Patterns
[Type safety with Pydantic Settings]
- Pattern 1: Pydantic BaseSettings with type hints
- Pattern 2: Field validators for type constraints
- Pattern 3: Custom types with validators

### 1.2.5 Validation Patterns
[Configuration validation]
- Pattern 1: Field-level validation (min/max, regex)
- Pattern 2: Model-level validation (cross-field constraints)
- Pattern 3: Custom validation logic

### 1.2.6 Best Practices
[Configuration security and validation]

### 1.3 Alternative Approaches
[Compare 2-3 alternatives with pros/cons]

### 1.4 Decision Criteria
[When to use this pattern vs. alternatives]

### 1.5 References
[Numbered references as footnotes - see Citation Format below]

## 2. Structured Logging
### 2.1 Recommended Approach
[Detailed explanation with rationale]

### 2.2 Implementation Example
[Code example with inline comments]

### 2.2.1 Logging Initialization Patterns
[Multiple initialization patterns with benefits/drawbacks]
- Pattern 1: Initialization in Application Lifespan (Recommended)
- Pattern 2: Initialization in main.py Module Level (Alternative)
- Pattern 3: Lazy Initialization with Singleton (Testing-Friendly)
- Pattern 4: Environment-Specific Configuration Files

### 2.2.2 Common Initialization Mistakes
[Anti-patterns and fixes]
- Mistake 1: Creating loggers before configuration
- Mistake 2: Configuring logging multiple times
- Mistake 3: Not configuring logging in tests

### 2.2.3 Verification and Troubleshooting
[Health check endpoints and verification examples]

### 2.3 Alternative Approaches
[Compare 2-3 alternatives with pros/cons]

### 2.4 Decision Criteria
[When to use this pattern vs. alternatives]

## 3. Caching Strategies
### 3.1 Recommended Approach
[Detailed explanation with rationale]

### 3.2 Implementation Example
[Code example with inline comments]

### 3.2.1 CacheService Initialization Patterns
[Multiple initialization patterns with benefits/drawbacks]
- Pattern 1: Application Lifespan with Singleton Redis Client (Recommended)
- Pattern 2: Request-Scoped Redis Client (For Testing)
- Pattern 3: Hybrid Approach with Dependency Override

### 3.2.2 Connection Pool Configuration Best Practices
[Detailed Redis connection pool settings with guidelines]

### 3.3 Alternative Approaches
[Compare 2-3 alternatives with pros/cons]

### 3.4 Decision Criteria
[When to use this pattern vs. alternatives]

## 4. Data Access Patterns
### 4.1 Recommended Approach
[Detailed explanation with rationale]

### 4.2 Database Engine and Session Initialization
[Multiple initialization patterns]
- Pattern 1: Lifespan with Singleton Engine (Recommended)
- Pattern 2: Direct Engine Per Request (Testing Only)

### 4.3 Repository Pattern Implementation
[Complete implementation with domain/infrastructure layers]
- Repository Interface (Domain Layer)
- Repository Implementation (Infrastructure Layer)
- ORM Model Mapping

### 4.4 Repository Dependency Injection
[Dependency chain setup and usage]
- Dependency Chain Setup
- Usage in API Routes

### 4.5 Testing with Mocked Repositories
[Complete test examples with mocks]

### 4.6 Connection Pool Configuration Best Practices
[SQLAlchemy pool settings with guidelines]

### 4.7 Decision Criteria
[When to use different patterns]

### 4.8 SQLAlchemy Type Safety
[Type safety with Mapped[] annotations]
- SQLAlchemy 2.0+ typed mappings
- Relationship type hints
- Query result typing

### 4.9 Domain Model Validation
[Entity validation patterns]
- Pydantic domain models
- to_domain/from_domain mapping with validation

[Repeat structure for remaining research areas: 5. External Service Integration, etc.]

## 9. Error Handling and Validation
### 9.1 Recommended Approach
[Detailed explanation with rationale]

### 9.2 Implementation Example
[Code example with inline comments]

### 9.3 Type Safety Patterns
[Type-safe error handling]
- Custom exception hierarchies with type hints
- Result types (Success/Failure pattern)
- Optional vs. exceptions

### 9.4 Validation Patterns
[Comprehensive validation]
- Pydantic field validators
- Model validators (cross-field)
- Custom validation logic

### 9.5 Global Exception Handlers
[FastAPI exception handlers]

### 9.6 RFC 7807 Problem Details
[Standardized error responses]

### 9.7 Error Correlation with Distributed Tracing
[Link errors to traces]
- Trace context in exceptions
- Error sampling strategies
- Span error recording

## 10. Telemetry and Observability
### 10.1 Recommended Approach
[OpenTelemetry + Prometheus + Jaeger/Zipkin]

### 10.2 Implementation Examples
[Complete code examples]

### 10.2.1 Telemetry Initialization Patterns
- Pattern 1: OpenTelemetry Auto-Instrumentation (Recommended)
- Pattern 2: Manual Instrumentation with Custom Spans
- Pattern 3: Prometheus Metrics Export
- Pattern 4: Hybrid Approach (OpenTelemetry + Prometheus)

### 10.2.2 Common Telemetry Mistakes
- Mistake 1: Not propagating trace context across async boundaries
- Mistake 2: Creating too many custom metrics (cardinality explosion)
- Mistake 3: Missing correlation IDs in logs and traces

### 10.2.3 Verification and Troubleshooting
[Health checks, metrics endpoints, trace debugging]

### 10.3 Alternative Approaches
[OpenTelemetry vs. Datadog vs. New Relic vs. AWS CloudWatch]

### 10.4 Decision Criteria
[When to use each approach]

### 10.5 References
[Numbered references as footnotes]

## 11. Audit Logging
### 11.1 Recommended Approach
[Structured audit events with immutable storage]

### 11.2 Implementation Examples
[Complete code examples]

### 11.2.1 Audit Logging Patterns
- Pattern 1: Database Audit Trail (Recommended for compliance)
- Pattern 2: Event Stream (Kafka, AWS Kinesis)
- Pattern 3: Hybrid Approach (Database + Event Stream)
- Pattern 4: Centralized Audit Service

### 11.2.2 Common Audit Mistakes
- Mistake 1: Not capturing user context (who performed action)
- Mistake 2: Mutable audit records (allow updates/deletes)
- Mistake 3: Missing critical events (authorization failures, data exports)

### 11.2.3 Verification and Troubleshooting
[Audit completeness, integrity verification, compliance reporting]

### 11.3 Alternative Approaches
[Database vs. event streaming vs. managed services]

### 11.4 Decision Criteria
[Compliance requirements, query patterns, retention policies]

### 11.5 References
[Numbered references as footnotes]

## Appendix A: Example Project Structure
[Complete directory tree with explanations]

## Appendix B: Recommended Libraries
[Curated list with version constraints and justifications]

## References
[All footnotes collected here in numeric order]
```

### Citation Format

**Use Markdown footnotes for all citations:**

```markdown
FastAPI's dependency injection system provides request-scoped dependencies by default[^1],
which aligns with Clean Architecture principles by inverting control flow[^2].

[^1]: FastAPI Documentation, "Dependencies - First Steps,"
https://fastapi.tiangolo.com/tutorial/dependencies/, accessed 2025-10-20.

[^2]: Robert C. Martin, *Clean Architecture: A Craftsman's Guide to Software Structure
and Design* (Boston: Prentice Hall, 2017), 87-94.
```

**Citation Requirements:**
- **Every claim** must have a citation (no unsupported assertions)
- **Code examples** must cite source (official docs, GitHub repo, book)
- **Footnote format:** `[^1]`, `[^2]`, etc. (numbered sequentially)
- **Reference section:** Collect all footnotes at end of document
- **Include access dates** for web sources
- **Include page numbers** for books (if applicable)

### Code Example Format

**All code examples must:**
- Be **syntactically valid Python 3.10+** (can be tested)
- Include **inline comments** explaining key concepts
- Show **complete imports** (don't assume context)
- Use **realistic names** (not foo/bar, use domain examples like UserRepository, ProductService)
- Be **10-30 lines** (simplified but demonstrative)
- Include **type hints** (leverage Python's type system)

**Example:**

```python
# File: src/infrastructure/repositories/user_repository.py
from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.user import User

class UserRepositoryProtocol(Protocol):
    """Repository interface (port) - domain layer doesn't depend on SQLAlchemy."""
    async def get_by_id(self, user_id: int) -> User | None: ...
    async def save(self, user: User) -> User: ...

class SQLAlchemyUserRepository:
    """Repository implementation (adapter) - infrastructure layer."""
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user_model = result.scalar_one_or_none()
        return user_model.to_domain() if user_model else None  # Map ORM → domain
```

**Citation for example:** `[^5]: Adapted from "Cosmic Python" repository pattern example,
https://github.com/cosmicpython/book/tree/master/chapter_02_repository`

## Deliverables

1. **Research Report** (Markdown file, 15-25 pages)
   - Follows structure defined in "Output Format Requirements"
   - Includes 30-50 citations (footnotes)
   - Contains 15-25 code examples
   - Provides decision trees for key architectural choices

2. **Quick Reference Guide** (Optional, 2-3 pages)
   - Summarizes recommended patterns in table format
   - Lists "golden path" technology choices
   - Provides project structure template

## Success Criteria

- [ ] All 11 research areas addressed with recommended approach + alternatives (Configuration, Logging, Caching, Data Access, External Services, Dependency Injection, Clean Architecture, Testing, Error Handling & Validation, Telemetry & Observability, Audit Logging)
- [ ] Minimum 30 citations from authoritative sources
- [ ] Minimum 15 code examples (syntactically valid, well-commented)
- [ ] Decision criteria provided for each pattern (when to use vs. alternatives)
- [ ] Trade-off analysis for major decisions (ORM vs. raw SQL, sync vs. async, etc.)
- [ ] Examples demonstrate SOLID, Clean Architecture, DI principles
- [ ] Markdown footnotes used consistently throughout
- [ ] Document is actionable (developer can use it to structure new FastAPI project)

## Timeline Estimate

- **Research Phase:** 8-12 hours (literature review, pattern analysis)
- **Synthesis Phase:** 6-8 hours (writing report, code examples)
- **Review Phase:** 2-3 hours (citation verification, example testing)
- **Total:** 16-23 hours

## Notes

- Prioritize **clarity over completeness** - better to deeply cover 7 areas than superficially cover 10
- Include **anti-patterns** where relevant (common mistakes to avoid)
- Focus on **maintainability and testability** - not just "cool" patterns
- Cite **real-world production examples** when available (e.g., "Company X uses pattern Y for Z")
- If pattern has **no consensus**, document the debate and provide balanced view

## Additional Requirements for Subsections

For areas with initialization patterns (Configuration, Logging, Caching, Data Access):
- Provide **3-4 alternative initialization patterns** with complete code examples
- Compare **benefits/drawbacks** for each pattern (production vs. testing use cases)
- Document **common mistakes** with anti-patterns and fixes (3 mistakes minimum)
- Include **verification/troubleshooting** guidance (health check endpoints, diagnostics)
- Provide **configuration best practices** (validation, security, environment handling)
- Show **complete working examples** (60-100 lines) demonstrating pattern in context

For Configuration Management:
- Show **lifespan-based initialization** with FastAPI startup/shutdown
- Demonstrate **Pydantic Settings with validators** (field validation, custom validators)
- Provide **environment-specific patterns** (dev/staging/production configs)
- Include **security best practices** (secret management, no sensitive data in health endpoints)
- Document **startup validation** (fail-fast on missing/invalid config)
- Show **health check endpoints** for configuration status

For Repository Pattern (Data Access):
- Show **complete layer separation** (domain interfaces, infrastructure implementations)
- Demonstrate **dependency injection chain** (session → repository → route)
- Provide **testing examples** with mocked implementations
- Include **ORM model mapping** (to_domain/from_domain methods)
- Document **transaction management** (automatic commit/rollback)
- Show **SQLAlchemy type safety** (Mapped[] annotations, relationship typing)
- Include **domain model validation** (Pydantic models, validation in mapping)

For Error Handling and Validation (Section 9):
- Show **type safety patterns** (typed exceptions, Result types, Optional)
- Demonstrate **Pydantic validation** (field validators, model validators, custom logic)
- Include **global exception handlers** (FastAPI @exception_handler)
- Document **RFC 7807 Problem Details** (standardized error responses)
- Show **error correlation with distributed tracing** (trace context propagation)

For Telemetry and Observability (Section 10):
- Show **OpenTelemetry initialization** (SDK setup, auto-instrumentation)
- Demonstrate **custom metrics** (Prometheus client, business metrics)
- Include **distributed tracing** (manual spans, context propagation)
- Document **health check patterns** (liveness, readiness, startup probes)
- Show **trace context in logs** (correlation IDs, structured logging integration)

For Audit Logging (Section 11):
- Show **structured audit events** (Pydantic models with schema validation)
- Demonstrate **audit middleware** (FastAPI middleware with context capture)
- Include **immutable storage** (append-only database, event streaming)
- Document **compliance requirements** (GDPR, SOC 2, HIPAA patterns)
- Show **audit query patterns** (reporting, integrity verification)
