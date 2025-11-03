# Java Microservice Architecture Research Prompt

## Context

Establish architectural standards for scalable Java microservice implementations using Spring Boot. The research will inform the creation of implementation guides for future Java-based microservices in the organization.

**Target Framework:** Spring Boot 3.x with Spring Framework 6.x

**Core Architecture Principles:**
- **SOLID Principles** - Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **YAGNI** (You Aren't Gonna Need It) - Build only what's needed, avoid speculative features
- **Clean Architecture** - Separation of concerns with dependency rule (outer layers depend on inner layers)
- **Dependency Injection** - Decouple components, improve testability (Spring IoC container)
- **DDD** (Domain-Driven Design) - Model business domain, bounded contexts, ubiquitous language
- **TDD** (Test-Driven Development) - Write tests first, red-green-refactor cycle

## Research Objectives

### Primary Research Areas

1. **Configuration Management**
   - Environment-based settings (dev, staging, production)
   - Secrets management (API keys, database credentials)
   - Configuration validation and type safety
   - 12-factor app compliance
   - **Spring Boot configuration** (application.yml, @ConfigurationProperties, profiles)
   - **External configuration** (Spring Cloud Config, environment variables, Vault integration)
   - **Configuration validation** (JSR-303/JSR-380 Bean Validation)
   - **Configuration initialization patterns** (auto-configuration with @ConfigurationPropertiesScan, programmatic @Bean, @Profile files, Spring Cloud Config)
   - **Common configuration mistakes** (using @Value instead of @ConfigurationProperties, missing validation, not using profiles)
   - **Verification and troubleshooting** (Spring Boot Actuator /configprops endpoint, configuration debugging)

2. **Structured Logging**
   - JSON-structured logging for machine parsing
   - Log levels and filtering strategies
   - Request ID tracing across services (MDC/Sleuth)
   - Integration with log aggregation systems (ELK, CloudWatch, etc.)
   - **Logger initialization patterns** (Logback configuration, SLF4J facade, structured logging with Logstash encoder)
   - **MDC (Mapped Diagnostic Context)** for request correlation
   - **Common initialization mistakes** (logger configuration ordering, MDC cleanup, async logging issues)
   - **Verification and troubleshooting** (actuator endpoints, log format verification)

3. **Caching Strategies**
   - In-memory vs. distributed caching (Redis, Hazelcast, Ehcache)
   - Cache invalidation patterns
   - TTL strategies and cache warming
   - Integration with Spring Cache abstraction
   - **Cache initialization patterns** (@EnableCaching, CacheManager configuration, custom cache resolvers)
   - **Connection pool configuration** (Lettuce/Jedis for Redis, connection pool sizing)
   - **Monitoring cache health** (Spring Boot Actuator, cache metrics, cache hit/miss ratio)

4. **Data Access Patterns**
   - Repository pattern implementation (Spring Data JPA)
   - ORM vs. raw SQL trade-offs (JPA/Hibernate, MyBatis, JdbcTemplate)
   - Connection pooling and database access (HikariCP)
   - Database migration strategies (Flyway, Liquibase)
   - **Database connection initialization** (DataSource configuration, HikariCP settings, connection pool lifecycle)
   - **Repository pattern implementation** (domain layer interfaces, infrastructure layer implementations, entity mapping)
   - **Repository dependency injection** (constructor injection, @Repository annotation, transaction boundaries)
   - **Testing with mocked repositories** (Mockito, Spring Boot Test slices, @DataJpaTest)
   - **Connection pool configuration** (maximumPoolSize, minimumIdle, maxLifetime, connectionTimeout)

5. **External Service Integration**
   - HTTP client patterns (RestTemplate, WebClient, Feign)
   - Circuit breaker and retry patterns (Resilience4j, Spring Retry)
   - Service discovery and health checks
   - API versioning strategies
   - **HTTP client lifecycle** (RestTemplate beans, WebClient configuration, connection pooling)
   - **Resilience patterns** (circuit breakers, bulkheads, rate limiters, retry with exponential backoff)

6. **Dependency Injection in Spring**
   - Bean scopes (singleton, prototype, request, session)
   - Constructor vs. field vs. setter injection
   - Bean lifecycle and initialization callbacks
   - Conditional bean registration (@ConditionalOnProperty, @Profile)
   - Testing with dependency injection (@MockBean, @SpyBean)

7. **Clean Architecture Layers**
   - Domain layer (entities, value objects, domain services)
   - Application layer (use cases, DTOs, ports/interfaces)
   - Infrastructure layer (repositories, external services, Spring configuration)
   - Presentation layer (REST controllers, request/response models, exception handlers)

### Secondary Research Areas

8. **Testing Strategies**
   - Unit testing with JUnit 5 and Mockito
   - Integration testing with Spring Boot Test
   - Test slices (@WebMvcTest, @DataJpaTest, @RestClientTest)
   - Mocking external dependencies (Mockito, WireMock, Testcontainers)
   - Test fixtures and factories
   - Coverage targets and quality gates
   - Parameterized tests and test templates

9. **Error Handling and Validation**
   - Bean Validation (JSR-303/JSR-380)
   - Custom validation constraints
   - Global exception handlers (@ControllerAdvice, @ExceptionHandler)
   - Standardized error response formats (RFC 7807 Problem Details)
   - Custom exception hierarchies
   - **Type safety with Records and generics** (Java 17+ sealed classes, Optional)
   - **Advanced validation patterns** (cross-field validation, custom annotations)
   - **Error correlation with distributed tracing** (trace context in exceptions, error sampling)

10. **Telemetry and Observability**
   - Spring Boot Actuator with Micrometer
   - OpenTelemetry with Spring Boot integration
   - Prometheus metrics endpoint
   - Distributed tracing (Zipkin/Jaeger via Spring Cloud Sleuth)
   - Health indicators (liveness/readiness)
   - Custom metrics and spans

11. **Audit Logging**
   - Spring Data JPA Auditing (@CreatedBy, @CreatedDate, @LastModifiedBy, @LastModifiedDate)
   - Custom audit event publishing (ApplicationEventPublisher)
   - Immutable audit trail storage (append-only tables)
   - Audit context from Spring Security (authentication, authorization)
   - Compliance requirements (GDPR, SOC 2, HIPAA)
   - Audit middleware and repository patterns

10. **Project Structure**
    - Directory organization (by layer vs. by feature)
    - Package naming conventions
    - Maven/Gradle multi-module projects
    - Clean separation of concerns (domain, application, infrastructure, presentation)

## Research Scope and Guardrails

### In Scope
- **Production-ready patterns** with real-world adoption (not experimental libraries)
- **Spring Boot best practices** (leverage Spring's capabilities while avoiding over-configuration)
- **Reactive patterns** (WebFlux, reactive repositories, Project Reactor - when appropriate)
- **Type-safe patterns** (leverage Java's type system, generics, Optional)
- **Examples from established projects** (open-source Spring Boot projects with >1000 stars, official Spring guides)
- **Trade-off analysis** (when to use pattern A vs. pattern B)

### Out of Scope
- Frontend frameworks (React, Vue, Thymeleaf)
- Deployment and infrastructure (Docker, Kubernetes) - focus on application code
- Authentication/Authorization libraries (Spring Security, OAuth 2.0) - unless part of Clean Architecture example
- Specific business domain logic - use generic examples (e.g., user management, product catalog)
- Performance benchmarking - cite existing benchmarks, don't create new ones

### Constraints
- **Minimum Java version:** Java 17+ (LTS version with modern features)
- **Minimum Spring Boot version:** 3.0+ (Spring Framework 6.x)
- **Focus on reactive patterns** when appropriate (Project Reactor, WebFlux)
- **Prioritize Spring ecosystem** (Spring Data, Spring Cloud, Spring Security)
- **Convention over configuration** (use Spring Boot defaults, customize when needed)

## Research Methodology

1. **Literature Review**
   - Official Spring documentation and guides (spring.io)
   - Spring Boot and Spring Framework GitHub discussions
   - Published articles and blog posts from credible sources (Baeldung, Spring blog)
   - Open-source Spring Boot projects with >1000 stars (GitHub)
   - Books: "Spring Boot in Action" (Craig Walls), "Cloud Native Java" (Long & Bastani), "Clean Architecture" (Robert Martin)

2. **Pattern Analysis**
   - Identify 3-5 alternative approaches per research area
   - Document pros/cons for each approach
   - Provide decision criteria (when to use which pattern)
   - Include code examples (10-30 lines, simplified but realistic)

3. **Source Quality Criteria**
   - **Authoritative sources:** Official Spring docs, Spring team blog posts, published books
   - **Community validation:** High-engagement GitHub repos, Stack Overflow answers with 50+ votes
   - **Recency:** Prefer sources from last 2 years (Spring Boot 3.x, Java 17+)
   - **Production evidence:** Patterns used in production systems, not just theoretical

## Output Format Requirements

### Document Structure

```markdown
# Java Microservice Architecture Research Report

**Document Version:** 1.0
**Research Date:** [YYYY-MM-DD]
**Researcher:** [Name/Team]
**Target Framework:** Spring Boot 3.x, Java 17+

## Executive Summary
[2-3 paragraphs: Key findings, recommended patterns, critical decisions]

## 1. Configuration Management
### 1.1 Recommended Approach
[Detailed explanation with rationale]

### 1.2 Implementation Example
[Code example with inline comments]

### 1.2.1 Configuration Initialization Patterns
[Multiple initialization patterns with benefits/drawbacks]
- Pattern 1: Spring Boot Auto-Configuration with @ConfigurationPropertiesScan (Recommended)
- Pattern 2: Programmatic Configuration with @Bean
- Pattern 3: Multiple Configuration Files with @Profile
- Pattern 4: External Configuration with Spring Cloud Config

### 1.2.2 Common Configuration Mistakes
[Anti-patterns and fixes]
- Mistake 1: Using @Value instead of @ConfigurationProperties for grouped config
- Mistake 2: Missing validation on configuration properties
- Mistake 3: Not using profiles for environment-specific configuration

### 1.2.3 Verification and Troubleshooting
[Actuator endpoints and troubleshooting examples]
- Spring Boot Actuator /configprops endpoint
- Configuration debugging checklist
- Common property binding issues

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
- Pattern 1: Logback Configuration with Application Startup (Recommended)
- Pattern 2: Programmatic Logback Configuration
- Pattern 3: MDC Configuration with Filter/Interceptor
- Pattern 4: Environment-Specific Logging Configuration

### 2.2.2 Common Initialization Mistakes
[Anti-patterns and fixes]
- Mistake 1: Missing MDC cleanup in async processing
- Mistake 2: Logger configuration ordering issues
- Mistake 3: Not configuring logging in tests

### 2.2.3 Verification and Troubleshooting
[Actuator endpoints and verification examples]

### 2.3 Alternative Approaches
[Compare 2-3 alternatives with pros/cons]

### 2.4 Decision Criteria
[When to use this pattern vs. alternatives]

## 3. Caching Strategies
### 3.1 Recommended Approach
[Detailed explanation with rationale]

### 3.2 Implementation Example
[Code example with inline comments]

### 3.2.1 Cache Initialization Patterns
[Multiple initialization patterns with benefits/drawbacks]
- Pattern 1: Spring Cache Abstraction with @EnableCaching (Recommended)
- Pattern 2: Programmatic CacheManager Configuration
- Pattern 3: Multiple Cache Managers (Redis + Local)
- Pattern 4: Custom Cache Resolver

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
- Pattern 1: Auto-configured DataSource (Recommended for most cases)
- Pattern 2: Programmatic DataSource Configuration (Advanced scenarios)

### 4.3 Repository Pattern Implementation
[Complete implementation with domain/infrastructure layers]
- Repository Interface (Domain Layer)
- JPA Repository Implementation (Infrastructure Layer)
- Entity Mapping (Domain ↔ JPA Entity)

### 4.4 Repository Dependency Injection
[Dependency chain setup and usage]
- Constructor Injection Pattern
- Usage in Service Layer and Controllers

### 4.5 Testing with Mocked Repositories
[Complete test examples with mocks]

### 4.6 Connection Pool Configuration Best Practices
[HikariCP settings with guidelines]

### 4.7 Decision Criteria
[When to use different patterns]

[Repeat structure for remaining research areas: 5. External Service Integration, etc.]

## 9. Error Handling and Validation
### 9.1 Recommended Approach
[Detailed explanation with rationale]

### 9.2 Implementation Example
[Code example with inline comments]

### 9.3 Bean Validation
[JSR-303/JSR-380 patterns]

### 9.4 Custom Validation Constraints
[Custom annotations, validators]

### 9.5 Global Exception Handlers
[@ControllerAdvice, @ExceptionHandler patterns]

### 9.6 RFC 7807 Problem Details
[Standardized error responses]

### 9.7 Error Correlation with Distributed Tracing
[Link errors to traces]
- Propagating trace context in exceptions (Sleuth/OpenTelemetry)
- Span.current().recordException patterns
- Error sampling strategies

## 10. Telemetry and Observability
### 10.1 Recommended Approach
[Spring Boot Actuator + Micrometer + OpenTelemetry]

### 10.2 Implementation Examples
[Complete code examples]

### 10.2.1 Telemetry Initialization Patterns
- Pattern 1: Spring Boot Actuator with Micrometer (Recommended)
- Pattern 2: OpenTelemetry Java Agent Auto-Instrumentation
- Pattern 3: Manual Instrumentation with @Observed/@Timed
- Pattern 4: Hybrid Approach (Actuator + OpenTelemetry)

### 10.2.2 Common Telemetry Mistakes
- Mistake 1: Not configuring MDC for async/reactive operations
- Mistake 2: Creating too many custom metrics (cardinality explosion)
- Mistake 3: Missing trace context propagation in @Async methods

### 10.2.3 Verification and Troubleshooting
[Actuator endpoints, Prometheus scraping, trace debugging]

### 10.3 Alternative Approaches
[Micrometer vs. OpenTelemetry, Sleuth vs. OTel Agent, Prometheus vs. InfluxDB vs. Datadog]

### 10.4 Decision Criteria
[When to use each approach]

### 10.5 References
[Numbered references as footnotes]

## 11. Audit Logging
### 11.1 Recommended Approach
[Event-driven audit with Spring Data JPA]

### 11.2 Implementation Examples
[Complete code examples]

### 11.2.1 Audit Logging Patterns
- Pattern 1: JPA Auditing with Spring Data (Simple, entity-level)
- Pattern 2: Event-Driven Audit with ApplicationEventPublisher (Recommended)
- Pattern 3: AOP-Based Audit with @Aspect
- Pattern 4: Centralized Audit Service (Microservices)

### 11.2.2 Common Audit Mistakes
- Mistake 1: Not capturing SecurityContext user details
- Mistake 2: Mutable audit records (allow updates/deletes)
- Mistake 3: Audit logging in same transaction (rollback loses audit)

### 11.2.3 Verification and Troubleshooting
[Audit event verification, completeness checks, compliance queries]

### 11.3 Alternative Approaches
[Database vs. Kafka, sync vs. async, self-managed vs. AWS CloudTrail]

### 11.4 Decision Criteria
[Compliance requirements, query patterns, transaction boundaries]

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
Spring's dependency injection enables repository abstraction through interfaces[^1],
which aligns with Clean Architecture principles by inverting control flow[^2].

[^1]: Spring Framework Documentation, "Core Technologies - The IoC Container,"
https://docs.spring.io/spring-framework/reference/core/beans.html, accessed 2025-11-01.

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
- Be **syntactically valid Java 17+** (can be compiled)
- Include **inline comments** explaining key concepts
- Show **complete imports** (don't assume context)
- Use **realistic names** (not foo/bar, use domain examples like UserRepository, ProductService)
- Be **10-30 lines** (simplified but demonstrative)
- Follow **Spring conventions** (@Component, @Service, @Repository annotations)
- Show **dependency injection** (constructor injection preferred)

**Example:**

```java
// File: src/main/java/com/example/project/domain/repository/UserRepository.java
package com.example.project.domain.repository;

import com.example.project.domain.entity.User;
import java.util.Optional;

/**
 * Repository interface (port) defined in domain layer.
 * Domain defines WHAT operations needed, infrastructure defines HOW.
 * This achieves Dependency Inversion Principle (DIP).
 */
public interface UserRepository {
    Optional<User> findById(Long userId);
    User save(User user);
    void deleteById(Long userId);
}

// File: src/main/java/com/example/project/infrastructure/persistence/JpaUserRepository.java
package com.example.project.infrastructure.persistence;

import com.example.project.domain.entity.User;
import com.example.project.domain.repository.UserRepository;
import com.example.project.infrastructure.persistence.entity.UserEntity;
import org.springframework.stereotype.Repository;
import java.util.Optional;

/**
 * JPA implementation of UserRepository (adapter).
 * Infrastructure layer - knows about JPA, Spring Data.
 */
@Repository
public class JpaUserRepository implements UserRepository {

    private final SpringDataUserRepository jpaRepository;

    public JpaUserRepository(SpringDataUserRepository jpaRepository) {
        this.jpaRepository = jpaRepository;
    }

    @Override
    public Optional<User> findById(Long userId) {
        return jpaRepository.findById(userId)
            .map(UserEntity::toDomain); // Map JPA entity → domain entity
    }

    @Override
    public User save(User user) {
        UserEntity entity = UserEntity.fromDomain(user);
        UserEntity saved = jpaRepository.save(entity);
        return saved.toDomain();
    }

    @Override
    public void deleteById(Long userId) {
        jpaRepository.deleteById(userId);
    }
}
```

**Citation for example:** `[^5]: Adapted from "Spring Boot Clean Architecture" repository pattern example,
https://github.com/mattia-battiston/clean-architecture-example`

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
- [ ] Trade-off analysis for major decisions (JPA vs. MyBatis, blocking vs. reactive, etc.)
- [ ] Examples demonstrate SOLID, Clean Architecture, DI principles
- [ ] Markdown footnotes used consistently throughout
- [ ] Document is actionable (developer can use it to structure new Spring Boot microservice)
- [ ] Spring Boot best practices followed (convention over configuration)
- [ ] Exception handling and validation patterns included

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
- **Spring Boot-specific considerations:**
  - Emphasize **convention over configuration** (leverage auto-configuration, customize when needed)
  - Show **dependency injection patterns** (constructor injection, @Autowired alternatives)
  - Demonstrate **Spring Boot Test slices** (@WebMvcTest, @DataJpaTest, @SpringBootTest)
  - Address **bean scopes** (singleton by default, prototype when needed, request/session for web)
  - Use **Spring Boot Actuator** for observability (health checks, metrics, info endpoints)

## Additional Requirements for Subsections

For areas with initialization patterns (Configuration, Logging, Caching, Data Access):
- Provide **3-4 alternative initialization patterns** with complete code examples
- Compare **benefits/drawbacks** for each pattern (production vs. testing use cases)
- Document **common mistakes** with anti-patterns and fixes (3 mistakes minimum)
- Include **verification/troubleshooting** guidance (actuator endpoints, diagnostics)
- Provide **configuration best practices** (validation, security, environment handling)
- Show **complete working examples** (60-100 lines) demonstrating pattern in context
- Address **Spring Boot auto-configuration** (when to use, when to customize)

For Configuration Management:
- Show **@ConfigurationProperties with Java Records** (Spring Boot 3.x with implicit constructor binding)
- Demonstrate **programmatic @Bean configuration** for complex initialization logic
- Provide **@Profile-based configuration** for environment-specific beans and properties
- Include **Spring Cloud Config** integration for centralized configuration
- Document **JSR-303 validation** with @Validated and custom constraints
- Show **Actuator /configprops endpoint** for runtime configuration inspection
- Address **common mistakes** (@Value overuse, missing validation, no profiles)

For Repository Pattern (Data Access):
- Show **complete layer separation** (domain interfaces, infrastructure implementations)
- Demonstrate **dependency injection chain** (repository → service → controller)
- Provide **testing examples** with mocked implementations (@MockBean, Mockito)
- Include **entity mapping** (domain entity ↔ JPA entity conversion)
- Document **transaction management** (@Transactional, propagation levels, rollback rules)
- Show **exception handling** (DataAccessException hierarchy, custom exceptions)

For Spring-Specific Patterns:
- Show **bean lifecycle** (initialization callbacks, destruction callbacks)
- Demonstrate **conditional configuration** (@ConditionalOnProperty, @Profile)
- Document **externalized configuration** (application.yml, environment variables, Spring Cloud Config)
- Include **aspect-oriented programming** (for cross-cutting concerns like logging, caching)
- Show **event-driven patterns** (ApplicationEvent, @EventListener, async event handling)

For Error Handling and Validation (Section 9):
- Show **Bean Validation** (JSR-303/JSR-380, @Valid, @Validated)
- Demonstrate **custom validation constraints** (custom annotations, validators)
- Include **global exception handlers** (@ControllerAdvice, @ExceptionHandler)
- Document **RFC 7807 Problem Details** (standardized error responses)
- Show **error correlation with distributed tracing** (Sleuth/OpenTelemetry integration)

For Telemetry and Observability (Section 10):
- Show **Spring Boot Actuator configuration** (endpoints, security)
- Demonstrate **Micrometer custom metrics** (@Timed, @Counted, custom meters)
- Include **OpenTelemetry auto-instrumentation** (Java agent, manual spans)
- Document **health indicators** (liveness, readiness, custom health checks)
- Show **MDC propagation** (async methods, reactive streams)

### 10.6 OpenTelemetry SDK Manual Instrumentation
[Manual SDK integration alongside agent]
- Complete OpenTelemetry dependencies (API, SDK, exporters)
- Full SDK initialization with OTLP/Zipkin/Jaeger exporters
- Manual span creation with proper resource management
- Async context propagation with TaskDecorator
- OpenTelemetry metrics (counters, histograms, gauges)

### 10.7 Logback MDC Integration with OpenTelemetry
[Trace context in logs]
- Logback XML configuration with trace context injection
- Spring Boot Starter auto-configuration for MDC
- Manual MDC injection with HandlerInterceptor
- JSON logs with trace IDs (correlation)
- Filtering logs by trace ID in Jaeger/Grafana

### 10.8 Common OpenTelemetry Mistakes and Solutions
[Production anti-patterns]
- Async context propagation failures (TaskDecorator fix)
- Span memory leaks (try-finally patterns)
- High-cardinality attribute explosion (guidelines table)
- Span sampling configuration (environment-based)

### 10.9 OpenTelemetry Verification and Troubleshooting
[Production debugging guide]
- OTLP export verification to Collector
- Docker Compose setup (Collector, Jaeger, Prometheus)
- Debug controller for trace verification
- Common troubleshooting scenarios with solutions

For Audit Logging (Section 11):
- Show **Spring Data JPA Auditing** (@EntityListeners, @CreatedBy, @CreatedDate)
- Demonstrate **event-driven audit** (ApplicationEventPublisher, @EventListener)
- Include **AOP-based audit** (@Aspect, @AfterReturning, @AfterThrowing)
- Document **compliance requirements** (GDPR, SOC 2, HIPAA patterns)
- Show **audit query patterns** (Spring Data JPA queries, reporting)
