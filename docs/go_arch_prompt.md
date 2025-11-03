# Go Microservice Architecture Research Prompt

## Context

Establish architectural standards for scalable Go microservice implementations. The research will inform the creation of implementation guides for future Go-based microservices in the organization.

**Target Framework:** Standard library + popular community packages

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
   - **Configuration loading patterns** (viper, envconfig, custom loaders)
   - **Configuration struct patterns** (nested configs, validation tags)
   - **Hot reload capabilities** (when to use, when to avoid)
   - **Configuration initialization patterns** (global with init, dependency injection, lazy with sync.Once, environment-specific with Viper)
   - **Common configuration mistakes** (reading config in init(), missing validation, no environment defaults)
   - **Verification and troubleshooting** (health check endpoints for config status, Kubernetes health probes)

2. **Structured Logging**
   - JSON-structured logging for machine parsing
   - Log levels and filtering strategies
   - Request ID tracing across services
   - Integration with log aggregation systems (ELK, CloudWatch, etc.)
   - **Logger initialization patterns** (global logger, contextual logger, logger middleware)
   - **Common initialization mistakes** (global state misuse, missing context propagation, logger configuration ordering)
   - **Verification and troubleshooting** (health check endpoints, log format verification)

3. **Caching Strategies**
   - In-memory vs. distributed caching (Redis, Memcached)
   - Cache invalidation patterns
   - TTL strategies and cache warming
   - Integration with HTTP handlers
   - **Cache client initialization patterns** (singleton, dependency injection, connection pooling)
   - **Connection pool configuration** (max connections, timeouts, health checks, keepalive settings)
   - **Monitoring connection pool health** (health check endpoints, pool stats)

4. **Data Access Patterns**
   - Repository pattern implementation
   - ORM vs. raw SQL trade-offs (GORM, sqlx, database/sql)
   - Connection pooling and database access
   - Database migration strategies (golang-migrate, goose)
   - **Database connection initialization** (singleton pattern, connection pool lifecycle)
   - **Repository pattern implementation** (domain layer interfaces, infrastructure layer implementations, model mapping)
   - **Repository dependency injection** (constructor injection, dependency chains, handler integration)
   - **Testing with mocked repositories** (interface-based mocks, testify/mock, test fixtures)
   - **Connection pool configuration** (MaxOpenConns, MaxIdleConns, ConnMaxLifetime, ConnMaxIdleTime)

5. **External Service Integration**
   - HTTP client patterns (net/http, resty)
   - Circuit breaker and retry patterns
   - Service discovery and health checks
   - API versioning strategies
   - **HTTP client lifecycle** (singleton vs. per-request, connection pooling, timeout configuration)
   - **Middleware patterns** (request logging, authentication, retry logic)

6. **Dependency Injection in Go**
   - Constructor injection patterns
   - Service lifecycle management (singleton, request-scoped, transient)
   - Testing with dependency injection
   - DI frameworks vs. manual injection (wire, dig, fx)

7. **Clean Architecture Layers**
   - Domain layer (entities, value objects, domain services)
   - Application layer (use cases, DTOs, ports/interfaces)
   - Infrastructure layer (repositories, external services, frameworks)
   - Presentation layer (HTTP handlers, request/response models, middleware)

### Secondary Research Areas

8. **Testing Strategies**
   - Unit testing with testing package
   - Integration testing patterns
   - Mocking external dependencies (testify, gomock, mockery)
   - Test fixtures and factories
   - Coverage targets and quality gates
   - Table-driven tests
   - Subtests and test parallelization

9. **Error Handling and Validation**
   - Error wrapping and unwrapping (errors.Is, errors.As)
   - Custom error types and error hierarchies
   - Validation libraries (validator, ozzo-validation)
   - Standardized error response formats
   - **Type safety with custom types** (semantic types, validation methods)
   - **Struct tag validation** (validate, required, min, max)
   - **Error correlation with distributed tracing** (trace context in errors, error sampling)

10. **Telemetry and Observability**
   - OpenTelemetry with Go net/http integration
   - Prometheus metrics with promhttp
   - Distributed tracing (Jaeger/Zipkin)
   - Health check patterns (Kubernetes liveness/readiness)
   - Custom metrics and spans
   - Context propagation across goroutines

11. **Audit Logging**
   - Structured audit events (Go structs with JSON encoding)
   - Immutable audit trail (append-only storage)
   - Audit context propagation (userID, tenantID, requestID via context.Context)
   - Compliance requirements (GDPR, SOC 2, HIPAA)
   - Audit middleware patterns
   - Audit repository and query patterns

10. **Project Structure**
    - Directory organization (by layer vs. by feature)
    - Package naming conventions
    - Package organization for monorepo vs. multi-repo
    - Internal packages and encapsulation

## Research Scope and Guardrails

### In Scope
- **Production-ready patterns** with real-world adoption (not experimental libraries)
- **Go idiomatic approaches** (leverage Go's strengths: interfaces, goroutines, channels)
- **Concurrency patterns** (goroutines, channels, sync primitives, context cancellation)
- **Type-safe patterns** (leverage Go's type system and interfaces)
- **Examples from established projects** (open-source Go projects with >1000 stars, official docs)
- **Trade-off analysis** (when to use pattern A vs. pattern B)

### Out of Scope
- Frontend frameworks (React, Vue, etc.)
- Deployment and infrastructure (Docker, Kubernetes) - focus on application code
- Authentication/Authorization libraries (OAuth, JWT) - unless part of Clean Architecture example
- Specific business domain logic - use generic examples (e.g., user management, product catalog)
- Performance benchmarking - cite existing benchmarks, don't create new ones

### Constraints
- **Minimum Go version:** 1.21+ (for modern generics and standard library features)
- **Focus on concurrency safety** (goroutine-safe patterns, race condition prevention)
- **Prioritize stdlib when possible** (minimize external dependencies)
- **Standard library first** (use stdlib net/http, database/sql unless clear advantage from external library)

## Research Methodology

1. **Literature Review**
   - Official Go documentation and blog posts
   - Go GitHub discussions and issues (architectural patterns)
   - Published articles and blog posts from credible sources
   - Open-source Go projects with >1000 stars (GitHub)
   - Books: "Let's Go" (Alex Edwards), "Go in Action" (Kennedy, et al.), "Clean Architecture" (Robert Martin)

2. **Pattern Analysis**
   - Identify 3-5 alternative approaches per research area
   - Document pros/cons for each approach
   - Provide decision criteria (when to use which pattern)
   - Include code examples (10-30 lines, simplified but realistic)

3. **Source Quality Criteria**
   - **Authoritative sources:** Official docs, Go team blog posts, published books
   - **Community validation:** High-engagement GitHub repos, Stack Overflow answers with 50+ votes
   - **Recency:** Prefer sources from last 2 years (Go evolves with generics, workspace mode, etc.)
   - **Production evidence:** Patterns used in production systems, not just theoretical

## Output Format Requirements

### Document Structure

```markdown
# Go Microservice Architecture Research Report

**Document Version:** 1.0
**Research Date:** [YYYY-MM-DD]
**Researcher:** [Name/Team]
**Target Go Version:** 1.21+

## Executive Summary
[2-3 paragraphs: Key findings, recommended patterns, critical decisions]

## 1. Configuration Management
### 1.1 Recommended Approach
[Detailed explanation with rationale]

### 1.2 Implementation Example
[Code example with inline comments]

### 1.2.1 Configuration Initialization Patterns
[Multiple initialization patterns with benefits/drawbacks]
- Pattern 1: Global Config with Init Function (Recommended)
- Pattern 2: Config as Dependency Injection (Testing-Friendly)
- Pattern 3: Lazy Initialization with sync.Once (Goroutine-Safe)
- Pattern 4: Environment-Specific Config with Viper (Multi-Source)

### 1.2.2 Common Configuration Mistakes
[Anti-patterns and fixes]
- Mistake 1: Reading config in init() instead of main()
- Mistake 2: Not validating required fields
- Mistake 3: Missing environment variable defaults

### 1.2.3 Verification and Troubleshooting
[Health check endpoints and troubleshooting examples]
- Health check endpoint showing config status
- Kubernetes liveness/readiness probe configuration
- Troubleshooting commands with curl/jq

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

### 2.2.1 Logger Initialization Patterns
[Multiple initialization patterns with benefits/drawbacks]
- Pattern 1: Global Logger with Initialization Function (Common)
- Pattern 2: Contextual Logger with Dependency Injection (Recommended)
- Pattern 3: Logger Middleware for HTTP Handlers
- Pattern 4: Environment-Specific Logger Configuration

### 2.2.2 Common Initialization Mistakes
[Anti-patterns and fixes]
- Mistake 1: Using global logger without initialization
- Mistake 2: Missing context propagation in goroutines
- Mistake 3: Logger configuration ordering issues

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

### 3.2.1 Cache Client Initialization Patterns
[Multiple initialization patterns with benefits/drawbacks]
- Pattern 1: Singleton Cache Client with Initialization (Recommended)
- Pattern 2: Dependency Injection with Interface Abstraction
- Pattern 3: Hybrid Approach with Test Override

### 3.2.2 Connection Pool Configuration Best Practices
[Detailed Redis/cache connection pool settings with guidelines]

### 3.3 Alternative Approaches
[Compare 2-3 alternatives with pros/cons]

### 3.4 Decision Criteria
[When to use this pattern vs. alternatives]

## 4. Data Access Patterns
### 4.1 Recommended Approach
[Detailed explanation with rationale]

### 4.2 Database Connection Initialization
[Multiple initialization patterns]
- Pattern 1: Singleton DB Connection with Init Function (Recommended)
- Pattern 2: Per-Request Connection (Testing Only)

### 4.3 Repository Pattern Implementation
[Complete implementation with domain/infrastructure layers]
- Repository Interface (Domain Layer)
- Repository Implementation (Infrastructure Layer)
- Model Mapping (Domain ↔ Database)

### 4.4 Repository Dependency Injection
[Dependency chain setup and usage]
- Constructor Injection Pattern
- Usage in HTTP Handlers

### 4.5 Testing with Mocked Repositories
[Complete test examples with mocks]

### 4.6 Connection Pool Configuration Best Practices
[database/sql pool settings with guidelines]

### 4.7 Decision Criteria
[When to use different patterns]

[Repeat structure for remaining research areas: 5. External Service Integration, etc.]

## 9. Error Handling and Validation
### 9.1 Recommended Approach
[Detailed explanation with rationale]

### 9.2 Implementation Example
[Code example with inline comments]

### 9.3 Error Wrapping and Unwrapping
[errors.Is, errors.As patterns]

### 9.4 Custom Error Types
[Sentinel errors, error hierarchies]

### 9.5 Type Safety with Custom Types
[Semantic types with validation methods]

### 9.6 Struct Tag Validation
[validate library, custom validation]

### 9.7 Error Correlation with Distributed Tracing
[Link errors to traces]
- Propagating trace context in error wrapping
- OpenTelemetry span.RecordError
- Error sampling strategies

## 10. Telemetry and Observability
### 10.1 Recommended Approach
[OpenTelemetry + Prometheus + Jaeger/Zipkin]

### 10.2 Implementation Examples
[Complete code examples]

### 10.2.1 Telemetry Initialization Patterns
- Pattern 1: OpenTelemetry Auto-Instrumentation (Recommended)
- Pattern 2: Manual Instrumentation with Custom Spans
- Pattern 3: Prometheus Metrics with Registry
- Pattern 4: Hybrid Approach (OpenTelemetry + Prometheus)

### 10.2.2 Common Telemetry Mistakes
- Mistake 1: Not propagating context.Context across goroutines
- Mistake 2: Creating metrics in request handlers (use global registry)
- Mistake 3: Missing span.End() calls (resource leaks)

### 10.2.3 Verification and Troubleshooting
[Health check endpoints, metrics endpoint, trace debugging]

### 10.3 Alternative Approaches
[OpenTelemetry vs. Prometheus vs. StatsD, Jaeger vs. Zipkin vs. AWS X-Ray]

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
- Pattern 2: Event Stream (Kafka, NATS)
- Pattern 3: Hybrid Approach (Database + Event Stream)
- Pattern 4: Centralized Audit Service (gRPC)

### 11.2.2 Common Audit Mistakes
- Mistake 1: Not capturing user context from context.Context
- Mistake 2: Mutable audit records (allowing updates/deletes)
- Mistake 3: Missing critical events (auth failures, privilege escalation)

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
Go's interface-based design enables repository abstraction without runtime overhead[^1],
which aligns with Clean Architecture principles by inverting control flow[^2].

[^1]: Go Documentation, "Effective Go - Interfaces,"
https://go.dev/doc/effective_go#interfaces, accessed 2025-11-01.

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
- Be **syntactically valid Go 1.21+** (can be compiled)
- Include **inline comments** explaining key concepts
- Show **complete imports** (don't assume context)
- Use **realistic names** (not foo/bar, use domain examples like UserRepository, ProductService)
- Be **10-30 lines** (simplified but demonstrative)
- Follow **Go conventions** (error handling, exported vs. unexported identifiers)
- Show **interface usage** where appropriate (demonstrate dependency inversion)

**Example:**

```go
// File: internal/domain/repository/user_repository.go
package repository

import (
	"context"
	"github.com/example/project/internal/domain/entity"
)

// UserRepository defines the interface for user persistence (port).
// Domain layer defines WHAT operations needed, infrastructure defines HOW.
type UserRepository interface {
	GetByID(ctx context.Context, userID int64) (*entity.User, error)
	Save(ctx context.Context, user *entity.User) error
}

// File: internal/infrastructure/postgres/user_repository.go
package postgres

import (
	"context"
	"database/sql"
	"github.com/example/project/internal/domain/entity"
	"github.com/example/project/internal/domain/repository"
)

// UserRepo is the PostgreSQL implementation of UserRepository (adapter).
type UserRepo struct {
	db *sql.DB
}

// NewUserRepository creates a new PostgreSQL user repository.
func NewUserRepository(db *sql.DB) repository.UserRepository {
	return &UserRepo{db: db}
}

// GetByID retrieves a user by ID.
func (r *UserRepo) GetByID(ctx context.Context, userID int64) (*entity.User, error) {
	var user entity.User
	query := `SELECT id, email, name FROM users WHERE id = $1`

	err := r.db.QueryRowContext(ctx, query, userID).Scan(&user.ID, &user.Email, &user.Name)
	if err == sql.ErrNoRows {
		return nil, nil // User not found
	}
	if err != nil {
		return nil, err
	}

	return &user, nil
}
```

**Citation for example:** `[^5]: Adapted from "Go Clean Architecture" repository pattern example,
https://github.com/bxcodec/go-clean-arch`

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
- [ ] Trade-off analysis for major decisions (ORM vs. raw SQL, stdlib vs. external packages, etc.)
- [ ] Examples demonstrate SOLID, Clean Architecture, DI principles
- [ ] Markdown footnotes used consistently throughout
- [ ] Document is actionable (developer can use it to structure new Go microservice)
- [ ] Concurrency patterns addressed (goroutine safety, context propagation, cancellation)
- [ ] Error handling patterns follow Go idioms (errors.Is/As, error wrapping)

## Timeline Estimate

- **Research Phase:** 8-12 hours (literature review, pattern analysis)
- **Synthesis Phase:** 6-8 hours (writing report, code examples)
- **Review Phase:** 2-3 hours (citation verification, example testing/compilation)
- **Total:** 16-23 hours

## Notes

- Prioritize **clarity over completeness** - better to deeply cover 7 areas than superficially cover 10
- Include **anti-patterns** where relevant (common mistakes to avoid)
- Focus on **maintainability and testability** - not just "cool" patterns
- Cite **real-world production examples** when available (e.g., "Company X uses pattern Y for Z")
- If pattern has **no consensus**, document the debate and provide balanced view
- **Go-specific considerations:**
  - Emphasize **interface-based design** (small interfaces, dependency inversion)
  - Address **goroutine safety** (data races, sync primitives, channel patterns)
  - Show **idiomatic error handling** (errors.Is/As, error wrapping, sentinel errors)
  - Demonstrate **context propagation** (cancellation, timeouts, request-scoped values)
  - Use **standard library first** (justify external dependencies explicitly)

## Additional Requirements for Subsections

For areas with initialization patterns (Configuration, Logging, Caching, Data Access):
- Provide **3-4 alternative initialization patterns** with complete code examples
- Compare **benefits/drawbacks** for each pattern (production vs. testing use cases)
- Document **common mistakes** with anti-patterns and fixes (3 mistakes minimum)
- Include **verification/troubleshooting** guidance (health check endpoints, diagnostics)
- Provide **configuration best practices** (validation, goroutine safety, environment handling)
- Show **complete working examples** (60-100 lines) demonstrating pattern in context
- Address **goroutine safety** (initialization order, concurrent access patterns, sync primitives)

For Configuration Management:
- Show **global config with init function** pattern with sync.RWMutex for goroutine safety
- Demonstrate **dependency injection** pattern for testing-friendly configs
- Provide **lazy initialization with sync.Once** for on-demand loading
- Include **environment-specific patterns** with Viper for multi-source configs
- Document **validation best practices** (required tags, custom Validate() methods)
- Show **health check endpoints** with Kubernetes probe configuration
- Address **common mistakes** (init() usage, missing defaults, no validation)

For Repository Pattern (Data Access):
- Show **complete layer separation** (domain interfaces, infrastructure implementations)
- Demonstrate **dependency injection chain** (constructor injection, handler wiring)
- Provide **testing examples** with mocked implementations (testify/mock or interface-based)
- Include **model mapping** (domain entity ↔ database model conversion)
- Document **transaction management** (context-based, sql.Tx patterns)
- Show **error handling** (sql.ErrNoRows, context.Canceled, proper error wrapping)

For Concurrency Patterns:
- Show **safe concurrent initialization** (sync.Once, initialization functions)
- Demonstrate **context propagation** (request cancellation, timeout handling)
- Document **channel patterns** (when to use, when to avoid)
- Include **sync primitives usage** (Mutex, RWMutex, WaitGroup patterns)

For Error Handling and Validation (Section 9):
- Show **error wrapping patterns** (errors.Is, errors.As, error chains)
- Demonstrate **custom error types** (sentinel errors, error hierarchies)
- Include **type safety with custom types** (semantic types, validation methods)
- Document **struct tag validation** (validate library, custom validators)
- Show **error correlation with distributed tracing** (trace context propagation)

For Telemetry and Observability (Section 10):
- Show **OpenTelemetry SDK initialization** (tracer provider, metrics provider)
- Demonstrate **HTTP middleware** (automatic tracing, context propagation)
- Include **custom metrics** (Prometheus registry, business metrics)
- Document **health check handlers** (Kubernetes liveness/readiness probes)
- Show **goroutine-safe patterns** (context propagation, span lifecycle)

For Audit Logging (Section 11):
- Show **structured audit events** (Go structs with JSON encoding, validation tags)
- Demonstrate **audit middleware** (HTTP handler with context capture)
- Include **immutable storage** (append-only database, event streaming)
- Document **compliance requirements** (GDPR, SOC 2, HIPAA patterns)
- Show **audit query patterns** (SQL queries, reporting, integrity checks)
