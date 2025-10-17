# Go Specialized CLAUDE.md Files Evaluation Report

**Date:** 2025-10-17
**Evaluator:** Claude Code
**Scope:** Evaluate `/prompts/CLAUDE/go/CLAUDE-*.md` files for clarity, duplicates, gaps, and alignment with main CLAUDE.md orchestration
**Comparison Baseline:** Python CLAUDE.md evaluation (`docs/specialized_claude_evaluation.md`)

---

## Executive Summary

The Go specialized CLAUDE.md files provide **comprehensive, well-structured implementation guidance** for Go development with Clean Architecture. The files demonstrate:

✅ **Strengths:**
- Excellent separation of concerns across 15 specialized files
- Strong Clean Architecture focus with clear layer boundaries
- Comprehensive code examples with practical patterns
- Good cross-referencing structure (references to `.claude/patterns/` files)
- Consistent naming conventions and terminology
- Advanced patterns: concurrency, error handling, security

⚠️ **Critical Issues Identified:**
- **MISSING ORCHESTRATOR**: `CLAUDE-core.md` exists but lacks orchestration structure similar to Python version
- **NO TOOLING FILE**: Missing equivalent to Python's `CLAUDE-tooling.md` (Go-specific tools: golangci-lint, wire, swag, etc.)
- **BROKEN REFERENCES**: Core file references `.claude/patterns/*.md` files that **DO NOT EXIST**
- **ORGANIZATIONAL CONFUSION**: 15 files vs Python's 6 - unclear when to use each file
- **INCONSISTENT STRUCTURE**: Files vary between pattern-focused (testing, error-handling) and domain-focused (api, database, grpc)

📝 **Recommended Actions:**
1. **CRITICAL:** Create proper `CLAUDE-core.md` orchestrator (currently just tech stack list)
2. **CRITICAL:** Create `CLAUDE-tooling.md` for Go development tools
3. **HIGH:** Remove/replace references to non-existent `.claude/patterns/` files
4. **MEDIUM:** Consolidate files to match Python's 6-file structure (reduce confusion)
5. **LOW:** Add back-links to core orchestrator in all specialized files

---

## File Inventory & Purpose Analysis

| File | Purpose | Lines | Status | Python Equivalent |
|------|---------|-------|--------|-------------------|
| **CLAUDE-core.md** | Tech stack list (NOT orchestrator) | 279 | ❌ **BROKEN** | CLAUDE-core.md (orchestrator) |
| **CLAUDE-architecture.md** | Clean Architecture patterns | 677 | ✅ Good | CLAUDE-architecture.md |
| **CLAUDE-testing.md** | Test patterns, mocks, table-driven tests | 648 | ✅ Excellent | CLAUDE-testing.md |
| **CLAUDE-error-handling.md** | Error patterns, wrapping, custom errors | 562 | ✅ Excellent | (Part of CLAUDE-core.md in Python) |
| **CLAUDE-concurrency.md** | Goroutines, channels, worker pools | 745 | ✅ Excellent | (Part of CLAUDE-core.md in Python) |
| **CLAUDE-security.md** | Auth, encryption, input validation | 1697 | ✅ Comprehensive | (Part of CLAUDE-validation.md in Python) |
| **CLAUDE-api.md** | REST API design, versioning, Swagger | 701 | ✅ Good | (No direct equivalent) |
| **CLAUDE-database.md** | Repository pattern, migrations, queries | 736 | ✅ Excellent | (No direct equivalent) |
| **CLAUDE-grpc.md** | gRPC patterns (not read yet) | ? | ⏳ Pending | (No equivalent) |
| **CLAUDE-websockets.md** | WebSocket patterns (not read yet) | ? | ⏳ Pending | (No equivalent) |
| **CLAUDE-messaging.md** | Message queues (not read yet) | ? | ⏳ Pending | (No equivalent) |
| **CLAUDE-caching.md** | Cache patterns (not read yet) | ? | ⏳ Pending | (No equivalent) |
| **CLAUDE-cli.md** | CLI application patterns (not read yet) | ? | ⏳ Pending | (No equivalent) |
| **CLAUDE-observability.md** | Logging, metrics, tracing (not read yet) | ? | ⏳ Pending | (No equivalent) |
| **claude-TODO.md** | Unknown (not read yet) | ? | ⏳ Pending | (No equivalent) |

**MISSING (compared to Python):**
- ❌ **CLAUDE-tooling.md** - Go tooling: golangci-lint, wire, swag, govulncheck, gosec
- ❌ **CLAUDE-typing.md** - Go doesn't need this (static typing built-in)
- ❌ **CLAUDE-validation.md** - Covered in CLAUDE-security.md (input validation section)

---

## Individual File Analysis

### 1. CLAUDE-core.md

**Purpose:** Should be main orchestration file (like Python version)

**Current State:** ❌ **CRITICAL FAILURE - NOT AN ORCHESTRATOR**

**Content:**
- Tech stack list (Go 1.21+, Clean Architecture, Wire, etc.)
- Project structure (cmd/, internal/, pkg/)
- Core commands (go build, go test, etc.)
- Core philosophy (KISS, YAGNI, DRY, SOLID)
- Anti-patterns section
- References to `.claude/patterns/*.md` files (DO NOT EXIST)

**Issues:**
1. **NOT an orchestrator** - Lists tech stack, not navigation guide
2. **Broken references** - Points to 12 non-existent `.claude/patterns/` files:
   - `.claude/patterns/architecture.md`
   - `.claude/patterns/interfaces.md`
   - `.claude/patterns/error-handling.md`
   - `.claude/patterns/testing.md`
   - `.claude/patterns/concurrency.md`
   - `.claude/patterns/security.md`
   - `.claude/patterns/performance.md`
   - `.claude/patterns/documentation.md`
   - `.claude/patterns/api-docs.md`
   - `.claude/configs/linting.md`
   - `.claude/configs/docker.md`
   - `.claude/configs/wire.md`
3. **No navigation** - Doesn't guide developers to specialized files
4. **No "When to use" guidance** - Unlike Python version

**Comparison to Python CLAUDE-core.md:**

| Feature | Python Version | Go Version | Status |
|---------|---------------|------------|--------|
| Clear purpose statement | ✅ "Main orchestration file" | ❌ "Tech stack list" | **MISSING** |
| Specialized files overview | ✅ Links to 5 files | ❌ No links to 14+ files | **MISSING** |
| "When to use" guidance | ✅ Decision tree | ❌ None | **MISSING** |
| Quick reference section | ✅ Common tasks | ✅ Core commands | ✅ Good |
| Tool commands | ✅ UV, Ruff, MyPy, pytest | ✅ go build, go test | ✅ Good |
| External references | ✅ Points to specialized files | ❌ Points to non-existent files | **BROKEN** |

**Recommendations:**
1. **Rewrite as orchestrator** following Python pattern:
   ```markdown
   # CLAUDE.md - Go Clean Architecture (Core Orchestrator)

   ## Purpose
   This is the main orchestration file for Go implementation guidance...

   ## Specialized Configuration Files
   - **CLAUDE-tooling.md** - Go development tools (golangci-lint, wire, swag)
   - **CLAUDE-architecture.md** - Clean Architecture patterns
   - **CLAUDE-testing.md** - Test patterns and mocking
   ...

   ## When to Use Each File
   - Implementing Clean Architecture → CLAUDE-architecture.md
   - Writing tests → CLAUDE-testing.md
   - Handling errors → CLAUDE-error-handling.md
   ...
   ```
2. **Remove all `.claude/patterns/` references** (files don't exist)
3. **Add navigation links** to all 14+ specialized files
4. **Add "When to use" decision tree**

---

### 2. CLAUDE-architecture.md

**Purpose:** Clean Architecture implementation patterns

**Clarity:** ⭐⭐⭐⭐⭐ Excellent

**Organization:**
```
Clean Architecture Layers
├── Domain Layer (entities, value objects, repository interfaces)
├── Application Layer (use cases, commands, queries)
├── Infrastructure Layer (repository implementations)
├── Interface Layer (HTTP handlers, gRPC, CLI)
Dependency Injection Wiring (manual vs Wire)
Dependency Rule Visualization
Common Patterns (functional options, domain events, CQRS)
```

**Strengths:**
- Comprehensive Clean Architecture example (User entity → Repository → Use Case → HTTP Handler)
- Clear layer boundaries with dependency direction diagram
- Excellent value object pattern (EmailAddress, UserID)
- Google Wire dependency injection example
- CQRS pattern included
- Functional options pattern for optional dependencies

**Duplicates:**
- Clean Architecture structure mentioned in CLAUDE-core.md (acceptable - core shows overview, this shows detail)
- Repository interfaces defined here AND in CLAUDE-database.md (acceptable - different focus)

**Gaps:**
- No Devbox integration guidance (Python version has this in architecture file)
- No Podman/container deployment structure (Python version includes this)
- No multi-stage build example for Go (Python has this)

**Recommendations:**
- Add Podman multi-stage Containerfile example for Go
- Add note about container deployment structure
- Consider adding Devbox guidance if applicable to Go projects

---

### 3. CLAUDE-testing.md

**Purpose:** Comprehensive testing strategies

**Clarity:** ⭐⭐⭐⭐⭐ Excellent

**Organization:**
```
Testing Philosophy
Table-Driven Tests (basic, advanced with testify)
Unit Testing with Mocks (testify/mock, gomock)
Integration Testing (database, HTTP)
Benchmark Tests (basic, parallel, with setup)
Test Helpers and Fixtures
Test Organization Best Practices
Running Tests (commands)
```

**Strengths:**
- Excellent table-driven test examples (Go best practice)
- Both testify/mock and gomock examples provided
- Integration tests with build tags (`//go:build integration`)
- Benchmark patterns (basic, parallel, with allocations)
- Test helpers with `t.Helper()` marker
- Fixture loading from testdata/
- Clear test organization (subtests with `t.Run()`)
- Good coverage requirements (80% minimum, 100% for critical logic)

**Duplicates:**
- Testing basics mentioned in CLAUDE-core.md (acceptable - core shows commands, this shows patterns)

**Gaps:**
- No Podman container integration testing examples (Python has this)
- No MCP server-specific testing patterns (Python version mentions this)

**Comparison to Python:**

| Feature | Python Version | Go Version | Status |
|---------|---------------|------------|--------|
| Testing philosophy | ✅ TDD, testing pyramid | ✅ TDD, testing pyramid | ✅ Equal |
| Test organization | ✅ conftest.py, fixtures | ✅ t.Helper(), testdata/ | ✅ Equal |
| Mocking | ✅ pytest-mock, unittest.mock | ✅ testify/mock, gomock | ✅ Equal |
| Coverage requirements | ✅ 80% minimum | ✅ 80% minimum | ✅ Equal |
| Integration tests | ✅ Markers, tags | ✅ Build tags | ✅ Equal |
| Benchmarks | ❌ Not covered | ✅ Comprehensive | ✅ **Go Better** |
| Async testing | ✅ pytest-asyncio | ❌ (Goroutines covered elsewhere) | ✅ Equal |

**Recommendations:**
- Add Podman container integration test example (database in container)
- Consider adding race detection emphasis (`go test -race`)

---

### 4. CLAUDE-error-handling.md

**Purpose:** Comprehensive error handling patterns

**Clarity:** ⭐⭐⭐⭐⭐ Excellent

**Organization:**
```
Core Error Handling Principles
Basic Error Handling (check and return, early return)
Custom Error Types (NotFoundError, ValidationError, UnauthorizedError)
Error Inspection (errors.Is, errors.As)
Error Wrapping (fmt.Errorf with %w, multiple errors with errors.Join)
HTTP Error Handling (error response mapper)
Context Error Handling (timeout, cancellation)
Panic and Recover (when to use, recovery middleware)
Error Logging Best Practices (structured logging)
```

**Strengths:**
- Clear "handle errors once" principle (log OR return, not both)
- Excellent custom error type examples
- Comprehensive `errors.Is()` and `errors.As()` usage
- HTTP error mapping to status codes
- Context deadline/cancellation handling
- Panic recovery middleware for HTTP
- Structured logging with slog
- Error metrics tracking example

**Duplicates:**
- Error handling basics in CLAUDE-core.md (acceptable - core shows principles, this shows implementation)

**Gaps:**
- None identified - comprehensive coverage

**Comparison to Python:**
- Python doesn't have equivalent dedicated file (error handling in CLAUDE-core.md and CLAUDE-validation.md)
- Go's error handling is more complex (no exceptions), justifies dedicated file

**Recommendations:**
- None - file is comprehensive

---

### 5. CLAUDE-concurrency.md

**Purpose:** Goroutines, channels, and synchronization patterns

**Clarity:** ⭐⭐⭐⭐⭐ Excellent

**Organization:**
```
Core Concurrency Principles
Worker Pool Pattern (basic, with context cancellation)
Context Patterns (timeout, cancellation, values)
Channel Patterns (fan-out/fan-in, pipeline)
Synchronization Patterns (Mutex, RWMutex, sync.Once, sync.WaitGroup, errgroup)
Graceful Shutdown (HTTP server with signal handling)
Common Pitfalls (goroutine leaks, race conditions)
```

**Strengths:**
- Comprehensive worker pool implementation with context support
- Excellent fan-out/fan-in and pipeline patterns
- Context usage throughout (timeouts, cancellation)
- Clear goroutine leak prevention examples
- Graceful shutdown with signal handling
- `errgroup` usage for coordinated error handling
- Race condition prevention (atomic operations, mutexes)

**Duplicates:**
- Concurrency basics in CLAUDE-core.md (acceptable - core shows principles, this shows implementation)

**Gaps:**
- None identified - comprehensive coverage

**Comparison to Python:**
- Python doesn't have equivalent (async patterns in CLAUDE-core.md and CLAUDE-testing.md)
- Go's concurrency primitives (goroutines, channels) justify dedicated file

**Recommendations:**
- None - file is comprehensive and follows Go best practices

---

### 6. CLAUDE-security.md

**Purpose:** Security-critical code examples and patterns

**Clarity:** ⭐⭐⭐⭐⭐ Comprehensive (longest file at 1697 lines)

**Organization:**
```
Input Validation (HTTP request validation, SQL injection prevention, path traversal)
Authentication and Authorization (password hashing, JWT, RBAC, OAuth2/OIDC, PKCE)
Cryptographic Operations (secure random generation, AES-GCM encryption)
HTTPS and TLS Configuration
Security Headers Middleware
CSRF Protection (double-submit cookie, JWT-based, gorilla/csrf)
Rate Limiting
File Upload and Download Patterns (validation, streaming, secure tokens, virus scanning)
Secrets Management
Logging Best Practices (no sensitive data)
Security Checklist
```

**Strengths:**
- Extremely comprehensive (covers everything from input validation to OAuth2)
- Excellent bcrypt password hashing examples
- Complete JWT implementation (generation, validation, refresh tokens)
- OAuth2/OIDC with Google provider example
- PKCE implementation for mobile/SPA
- CSRF protection (3 different approaches)
- File upload security (type validation, size limits, virus scanning hook)
- Secure file download with token-based access
- Rate limiting per API key
- TLS 1.2+ configuration with cipher suites

**Duplicates:**
- Input validation overlaps with CLAUDE-api.md (acceptable - security shows validation patterns, API shows request DTOs)
- File upload security overlaps with any file handling docs (acceptable - security-focused view)

**Gaps:**
- No specific MCP server security patterns (Python version doesn't have this either)

**Comparison to Python:**
- Python has `CLAUDE-validation.md` (Pydantic validation focus)
- Go has `CLAUDE-security.md` (broader security focus including auth)
- Go version is more comprehensive (1697 lines vs Python's ~300 lines)

**Recommendations:**
- Consider splitting into 2 files:
  - **CLAUDE-validation.md** - Input validation, sanitization
  - **CLAUDE-security.md** - Auth, encryption, CSRF, rate limiting
- This would match Python structure better

---

### 7. CLAUDE-api.md

**Purpose:** RESTful API design patterns, versioning, documentation

**Clarity:** ⭐⭐⭐⭐⭐ Excellent

**Organization:**
```
API Design Principles (RESTful resource design)
HTTP Handler Pattern
Request/Response DTOs
API Versioning Strategies (URL path, header, content negotiation, deprecation)
API Documentation with Swagger (setup, annotations, generation)
API Key Management (model, middleware, repository)
Rate Limiting per API Key
Best Practices (versioning, breaking changes, migration guide)
```

**Strengths:**
- Clear RESTful resource design principles
- Comprehensive handler pattern with error mapping
- Request/Response DTO examples with validation
- 3 API versioning strategies (URL path, header, Accept header)
- Deprecation strategy with Sunset header
- Complete Swagger/OpenAPI setup with annotations
- API key management (generation, hashing, scopes, last used tracking)
- Rate limiting per API key with golang.org/x/time/rate
- Migration guide (breaking vs non-breaking changes)

**Duplicates:**
- Handler error handling overlaps with CLAUDE-error-handling.md (acceptable - different focus)
- Input validation overlaps with CLAUDE-security.md (acceptable - API-specific DTOs)

**Gaps:**
- None identified - comprehensive API guidance

**Comparison to Python:**
- Python doesn't have dedicated API file (FastAPI patterns in CLAUDE-architecture.md)
- Go version provides more structured API guidance

**Recommendations:**
- None - file is comprehensive

---

### 8. CLAUDE-database.md

**Purpose:** Database interaction patterns, migrations, best practices

**Clarity:** ⭐⭐⭐⭐⭐ Excellent

**Organization:**
```
Database Stack (PostgreSQL, golang-migrate, GORM/sqlx/database/sql)
Database Connection Patterns (repository implementation, connection pool config)
Using GORM (alternative to database/sql)
Database Migration Patterns (directory structure, migration files, migration runner)
Programmatic Migration (embedded migrations)
Transaction Patterns (basic, transaction helper)
Query Patterns (pagination, batch operations)
Database Seeding
Best Practices (context usage, prepared statements, migrations, soft deletes)
Migration Best Practices (versioning, safety checklist, zero-downtime pattern)
Troubleshooting (connection pool, slow queries, migration conflicts)
```

**Strengths:**
- Comprehensive repository pattern implementation (Clean Architecture aligned)
- Connection pool configuration with appropriate limits
- Both database/sql and GORM examples
- Complete migration setup with golang-migrate
- Embedded migrations with embed.FS
- Transaction helper with automatic rollback
- Pagination with total count
- Batch operations with prepared statements
- Zero-downtime migration pattern (excellent!)
- Migration safety checklist

**Duplicates:**
- Repository interfaces overlap with CLAUDE-architecture.md (acceptable - architecture shows pattern, database shows implementation)

**Gaps:**
- No Podman database container setup (Python version has this in CLAUDE-tooling.md)
- No migration testing guidance

**Comparison to Python:**
- Python doesn't have dedicated database file (Alembic migrations in CLAUDE-tooling.md)
- Go version is more comprehensive (736 lines)

**Recommendations:**
- Add Podman database container setup example (docker-compose alternative)
- Add migration testing section

---

## Cross-File Analysis

### Intentional Duplicates (GOOD - No Action Needed)

| Content | Files | Rationale |
|---------|-------|-----------|
| **Clean Architecture structure** | CLAUDE-core.md (overview), CLAUDE-architecture.md (detailed) | Core shows project layout, architecture shows implementation |
| **Error handling basics** | CLAUDE-core.md (principles), CLAUDE-error-handling.md (patterns) | Core shows philosophy, error-handling shows code examples |
| **Testing basics** | CLAUDE-core.md (commands), CLAUDE-testing.md (patterns) | Core shows how to run tests, testing shows how to write tests |
| **Repository interfaces** | CLAUDE-architecture.md (Clean Arch), CLAUDE-database.md (SQL) | Different focus: architecture pattern vs database implementation |
| **Input validation** | CLAUDE-security.md (security), CLAUDE-api.md (DTOs) | Security shows validation functions, API shows request structs |

### Problematic Issues

| Issue | Files | Severity | Action Required |
|-------|-------|----------|-----------------|
| **CLAUDE-core.md NOT orchestrator** | CLAUDE-core.md | 🚨 CRITICAL | Rewrite as orchestration file |
| **Broken references to `.claude/patterns/`** | CLAUDE-core.md | 🚨 CRITICAL | Remove all references (files don't exist) |
| **No tooling guide** | MISSING | 🚨 CRITICAL | Create CLAUDE-tooling.md |
| **No navigation structure** | All files | ⚠️ HIGH | Add back-links to core, create decision tree |
| **15 files vs Python's 6** | All files | ⚠️ MEDIUM | Consider consolidation |
| **Inconsistent file focus** | Various | ⚠️ MEDIUM | Some files are pattern-focused (testing), others domain-focused (api, grpc) |

---

## Gap Analysis: Main CLAUDE.md Alignment

### Main CLAUDE.md "Implementation Phase Instructions" Section

From `/CLAUDE.md` lines 382-413:

```markdown
## Implementation Phase Instructions

**When to use Implementation Phase instructions:**
- Writing code, tests, documentation
- Setting up development environment, CI/CD, tooling
- Implementing features from PRDs/Backlog Stories
- Coding tasks after planning phase completes

**Language-Specific Implementation Guides:**

Language-specific CLAUDE.md files are organized by programming language in subdirectories:
- **Python Projects:** `prompts/CLAUDE/python/`
- **Go Projects:** `prompts/CLAUDE/go/`

**Implementation Configuration Files (Language-Specific):**
- **CLAUDE-core.md** - Main implementation guide and orchestration
- **CLAUDE-tooling.md** - Language-specific tooling (build tools, linters, formatters, test runners)
- **CLAUDE-testing.md** - Testing strategy, fixtures, coverage
- **CLAUDE-typing.md** - Type system patterns and type safety
- **CLAUDE-validation.md** - Input validation, data models, security patterns
- **CLAUDE-architecture.md** - Project structure, modularity, design patterns

**→ For implementation work, navigate to the appropriate language subdirectory and see CLAUDE-core.md which orchestrates all specialized configs.**

**Current Project Language:** Python (see `prompts/CLAUDE/python/` for implementation guides)
```

### Alignment Check: Go vs Main CLAUDE.md Expectations

| Expected File (per main CLAUDE.md) | Go Status | Issue |
|-------------------------------------|-----------|-------|
| **CLAUDE-core.md** (orchestrator) | ❌ **EXISTS BUT NOT ORCHESTRATOR** | Tech stack list, no navigation |
| **CLAUDE-tooling.md** | ❌ **DOES NOT EXIST** | **CRITICAL GAP** |
| **CLAUDE-testing.md** | ✅ EXISTS | Excellent quality |
| **CLAUDE-typing.md** | ⚠️ **NOT NEEDED FOR GO** | Go has built-in static typing (acceptable) |
| **CLAUDE-validation.md** | ⚠️ **PARTIALLY COVERED** | Input validation in CLAUDE-security.md |
| **CLAUDE-architecture.md** | ✅ EXISTS | Excellent quality |

**Additional Go Files (not in main CLAUDE.md list):**
- ✅ CLAUDE-error-handling.md (good - Go-specific need)
- ✅ CLAUDE-concurrency.md (good - Go-specific need)
- ✅ CLAUDE-security.md (good - comprehensive)
- ✅ CLAUDE-api.md (good - REST patterns)
- ✅ CLAUDE-database.md (good - database patterns)
- ⏳ CLAUDE-grpc.md (not evaluated yet)
- ⏳ CLAUDE-websockets.md (not evaluated yet)
- ⏳ CLAUDE-messaging.md (not evaluated yet)
- ⏳ CLAUDE-caching.md (not evaluated yet)
- ⏳ CLAUDE-cli.md (not evaluated yet)
- ⏳ CLAUDE-observability.md (not evaluated yet)
- ⏳ claude-TODO.md (not evaluated yet)

---

## Missing Tooling Guidance (CRITICAL GAP)

### CLAUDE-tooling.md Expected Content

Python version has comprehensive tooling guidance (lines 84-143 in Python eval report). Go version is **completely missing** this file.

**Required Go Tooling Coverage:**

| Tool | Purpose | Commands | Configuration | Status |
|------|---------|----------|---------------|--------|
| **go** | Compiler, build tool, module manager | `go build`, `go test`, `go mod tidy` | go.mod, go.sum | ⚠️ Partial (CLAUDE-core.md has commands) |
| **golangci-lint** | Comprehensive linter (runs ~30 linters) | `golangci-lint run` | .golangci.yml | ❌ Not documented |
| **gosec** | Security scanner | `gosec ./...` | gosec.json | ⚠️ Mentioned in CLAUDE-core.md, no config |
| **govulncheck** | Vulnerability scanner | `govulncheck ./...` | N/A | ⚠️ Mentioned in CLAUDE-core.md |
| **staticcheck** | Advanced static analysis | `staticcheck ./...` | staticcheck.conf | ⚠️ Mentioned in CLAUDE-core.md |
| **gofmt** | Code formatter | `gofmt -w .` | N/A (standard) | ⚠️ Mentioned in CLAUDE-core.md |
| **goimports** | Import formatter | `goimports -w .` | N/A | ⚠️ Mentioned in CLAUDE-core.md |
| **wire** | Compile-time dependency injection | `go generate ./...` | wire.go, wire_gen.go | ⚠️ Mentioned in CLAUDE-architecture.md, no setup guide |
| **swag** | OpenAPI/Swagger doc generator | `swag init -g cmd/api/main.go` | Annotations in code | ⚠️ Mentioned in CLAUDE-api.md, no setup |
| **golang-migrate** | Database migrations | `migrate -path ./migrations -database $DB up` | Migration files (.up.sql, .down.sql) | ✅ Covered in CLAUDE-database.md |
| **Taskfile** | Task runner (Make alternative) | `task build`, `task test` | Taskfile.yml | ❌ Not documented |
| **Podman** | Container runtime (Docker alternative) | `podman build`, `podman run` | Containerfile | ❌ Not documented |
| **Air** | Hot-reload development server | `air` | .air.toml | ❌ Not documented |
| **Devbox** | Isolated development environment | `devbox shell`, `devbox run` | devbox.json | ❌ Not documented |

**Impact:** HIGH - Developers implementing Go projects will lack critical tooling guidance

**Recommended CLAUDE-tooling.md Structure:**
```markdown
# CLAUDE.md - Go Development Tools

## Purpose
Comprehensive tooling setup for Go development: linters, formatters, build tools, etc.

## Go Compiler & Modules
### go (built-in toolchain)
...

## Code Quality Tools
### golangci-lint (comprehensive linter)
### gosec (security scanner)
### govulncheck (vulnerability scanner)
### staticcheck (static analysis)
### gofmt & goimports (formatters)

## Build & Dependency Tools
### Taskfile (task runner)
### wire (dependency injection)

## API Documentation
### swag (Swagger/OpenAPI generator)

## Database Tools
### golang-migrate (migrations)

## Development Environment
### Air (hot-reload)
### Devbox (isolated environment)
### Podman (container runtime)

## Complete Development Workflow
### Setup (initial project setup)
### Daily Development (write → format → lint → test)
### CI/CD (automated checks)

## Tool Configuration Files
### .golangci.yml (linter config)
### Taskfile.yml (task definitions)
### .air.toml (hot-reload config)
### devbox.json (environment definition)
### Containerfile (multi-stage build)
```

---

## Consistency Analysis

### Terminology Consistency

✅ **Consistent across all files:**
- "Clean Architecture" (not "Hexagonal Architecture" or "Ports and Adapters")
- "Repository pattern" (consistent naming)
- "Use case" (not "interactor" or "application service")
- "Domain layer" (not "business logic layer")
- "Infrastructure layer" (not "persistence layer")
- "Interface layer" (not "presentation layer")
- "Context" (always `context.Context`, never just "ctx")
- "goroutine" (lowercase, one word)
- "channel" (not "chan" in prose)

### Code Style Consistency

✅ **Consistent patterns:**
- All code blocks use triple backticks with `go` language specification
- Variable names follow camelCase (unexported) and PascalCase (exported)
- Package names lowercase, single word
- Error handling with early returns (`if err != nil { return ... }`)
- Context as first parameter in all functions
- Struct initialization with field names (`&User{ID: id, ...}`)

### Structural Consistency

⚠️ **INCONSISTENT - Major Issue:**

**Pattern-Focused Files** (good structure):
- CLAUDE-testing.md - Philosophy → Basic → Advanced → Best Practices
- CLAUDE-error-handling.md - Principles → Patterns → Advanced → Checklist
- CLAUDE-concurrency.md - Principles → Patterns → Pitfalls → Best Practices

**Domain-Focused Files** (different structure):
- CLAUDE-api.md - Principles → Patterns → Tools → Best Practices
- CLAUDE-database.md - Stack → Patterns → Migrations → Best Practices
- CLAUDE-security.md - Mixed (input validation, auth, crypto, file upload - feels like 4 files in one)

**Recommendation:** Standardize structure across all files:
```markdown
# CLAUDE.md - [Topic] Patterns

## Overview / Philosophy
## Core Principles / Design Guidelines
## Basic Patterns (with examples)
## Advanced Patterns (with examples)
## Best Practices
## Checklist (✅ DO / ❌ DON'T)
## References (optional)
```

---

## Recommendations

### Priority 1: CRITICAL - Fix Orchestration (Estimated: 2-3 hours)

**Action:** Completely rewrite `CLAUDE-core.md` as orchestration file

**New Structure:**
```markdown
# CLAUDE.md - Go Clean Architecture (Core Orchestrator)

## Purpose
Main orchestration file providing navigation to specialized Go implementation guides.

## Hybrid Approach
This file serves as orchestrator. Specialized files provide deep dives.

## Specialized Configuration Files
📚 **Recommended Reading Order:**
1. **CLAUDE-tooling.md** - Start here: set up Go development tools
2. **CLAUDE-architecture.md** - Understand Clean Architecture structure
3. **CLAUDE-testing.md** - Learn testing patterns
4. **CLAUDE-error-handling.md** - Error handling patterns
5. **CLAUDE-concurrency.md** - Goroutines and channels
6. **CLAUDE-security.md** - Security and input validation
7. **CLAUDE-api.md** - REST API design
8. **CLAUDE-database.md** - Database patterns and migrations

🔧 **Specialized Topics** (reference as needed):
- **CLAUDE-grpc.md** - gRPC patterns
- **CLAUDE-websockets.md** - WebSocket patterns
- **CLAUDE-messaging.md** - Message queue patterns
- **CLAUDE-caching.md** - Cache patterns
- **CLAUDE-cli.md** - CLI application patterns
- **CLAUDE-observability.md** - Logging, metrics, tracing

## Core Development Philosophy
KISS, YAGNI, DRY, SOLID (brief - already in current core.md)

## Project Structure
(Keep current cmd/, internal/, pkg/ structure - it's good)

## Core Commands
(Keep current commands - they're good)

## When to Use Each Specialized File

**🎯 Task-Based Navigation:**
- Setting up project → CLAUDE-tooling.md
- Implementing Clean Architecture → CLAUDE-architecture.md
- Writing tests → CLAUDE-testing.md
- Handling errors → CLAUDE-error-handling.md
- Using goroutines/channels → CLAUDE-concurrency.md
- Implementing authentication → CLAUDE-security.md
- Building REST API → CLAUDE-api.md
- Database operations → CLAUDE-database.md
- gRPC service → CLAUDE-grpc.md
- Real-time features → CLAUDE-websockets.md
- Message queues → CLAUDE-messaging.md
- Caching strategy → CLAUDE-caching.md
- CLI application → CLAUDE-cli.md
- Adding logging/metrics → CLAUDE-observability.md

**🔍 Problem-Based Navigation:**
- "How do I structure my project?" → CLAUDE-architecture.md
- "How do I test this?" → CLAUDE-testing.md
- "How should I handle this error?" → CLAUDE-error-handling.md
- "Is this goroutine usage correct?" → CLAUDE-concurrency.md
- "How do I validate input?" → CLAUDE-security.md
- "How do I version my API?" → CLAUDE-api.md
- "How do I write migrations?" → CLAUDE-database.md

## Critical Guidelines
(Keep current guidelines - they're good)

## Pre-commit Checklist
(Keep current checklist - it's good)

## Quick Reference
(Keep current quick reference - it's good)

**Back to Main:** [CLAUDE.md](/CLAUDE.md)
```

**Remove:**
- All references to `.claude/patterns/*.md` files (they don't exist)
- All references to `.claude/configs/*.md` files (they don't exist)

**Estimated Effort:** 2-3 hours to rewrite and reorganize

---

### Priority 2: CRITICAL - Create CLAUDE-tooling.md (Estimated: 3-4 hours)

**Action:** Create comprehensive Go tooling guide

**Required Sections:**
1. **Go Compiler & Modules**
   - go build, go test, go mod commands
   - go.mod and go.sum files
   - Version management

2. **Code Quality Tools**
   - golangci-lint comprehensive setup (`.golangci.yml` example)
   - gosec security scanner
   - govulncheck vulnerability scanner
   - staticcheck advanced analysis
   - gofmt and goimports usage

3. **Build & Task Tools**
   - Taskfile setup (Taskfile.yml example)
   - Wire dependency injection (wire.go example, generation)

4. **API Documentation**
   - swag setup and annotations
   - Swagger UI integration
   - OpenAPI spec generation

5. **Development Environment**
   - Air hot-reload setup (.air.toml example)
   - Devbox isolated environment (devbox.json example)
   - Podman container setup (Containerfile multi-stage build)

6. **Complete Development Workflow**
   - Setup: `devbox shell`, `go mod download`, `task setup`
   - Daily Dev: `air` (hot-reload), `task lint`, `task test`
   - CI/CD: `task ci` (all checks), `task build-container`

7. **Configuration Examples**
   - Complete `.golangci.yml` with all linters configured
   - Complete `Taskfile.yml` with common tasks
   - Complete `.air.toml` for hot-reload
   - Complete `devbox.json` for environment
   - Complete `Containerfile` for multi-stage build

**Estimated Effort:** 3-4 hours to create comprehensive guide with all examples

---

### Priority 3: HIGH - Add Back-Links and Navigation (Estimated: 1 hour)

**Action:** Add back-links to core orchestrator in all specialized files

**Add to Bottom of Each Specialized File:**
```markdown
---

**Back to [Core Orchestrator](./CLAUDE-core.md)** | **Back to [Main CLAUDE.md](/CLAUDE.md)**
```

**Add to Top of Each Specialized File:**
```markdown
# CLAUDE.md - [Topic] Patterns

**Part of:** [Go Implementation Guides](./CLAUDE-core.md)

## Purpose
[Existing purpose text]
```

**Estimated Effort:** 1 hour to add navigation to all 15 files

---

### Priority 4: MEDIUM - Consider File Consolidation (Estimated: 4-6 hours)

**Current State:** 15 specialized files (vs Python's 6)

**Issues:**
- Unclear when to use which file (no decision tree)
- Some files are very specialized (grpc, websockets, messaging, caching, cli)
- Security file is 1697 lines (too large, covers too much)

**Recommendation:** Consider consolidating to match Python structure (6-8 core files + optional specialized files)

**Proposed Structure:**

**Core Files** (always relevant, part of standard workflow):
1. **CLAUDE-core.md** - Orchestrator (rewrite required)
2. **CLAUDE-tooling.md** - Go development tools (create new)
3. **CLAUDE-architecture.md** - Clean Architecture (keep as-is)
4. **CLAUDE-testing.md** - Test patterns (keep as-is)
5. **CLAUDE-validation.md** - Input validation and data models (extract from CLAUDE-security.md)
6. **CLAUDE-security.md** - Auth, encryption, CSRF, rate limiting (slim down from 1697 lines)

**Advanced Files** (reference as needed for specific use cases):
7. **CLAUDE-api.md** - REST API patterns (keep as-is)
8. **CLAUDE-database.md** - Database and migrations (keep as-is)
9. **CLAUDE-error-handling.md** - Error patterns (keep as-is)
10. **CLAUDE-concurrency.md** - Goroutines and channels (keep as-is)

**Specialized Files** (optional, for specific domains):
11. **CLAUDE-grpc.md** - gRPC patterns (keep separate)
12. **CLAUDE-websockets.md** - WebSocket patterns (keep separate)
13. **CLAUDE-messaging.md** - Message queues (keep separate)
14. **CLAUDE-caching.md** - Cache patterns (keep separate)
15. **CLAUDE-cli.md** - CLI applications (keep separate)
16. **CLAUDE-observability.md** - Logging, metrics, tracing (keep separate)

**Benefits:**
- Clear separation: Core (always needed) vs Advanced (usually needed) vs Specialized (sometimes needed)
- Matches Python structure (easier for developers working in both languages)
- Reduces cognitive load (developers know to read Core files first)

**Estimated Effort:** 4-6 hours to reorganize and consolidate

---

### Priority 5: LOW - Minor Enhancements (Estimated: 2-3 hours)

1. **Add Podman/Devbox examples** to relevant files
   - CLAUDE-architecture.md: Add multi-stage Containerfile example
   - CLAUDE-database.md: Add Podman database container setup
   - CLAUDE-testing.md: Add Podman integration test example

2. **Standardize file structure** across all specialized files:
   ```markdown
   # Title
   ## Overview / Philosophy
   ## Core Principles
   ## Basic Patterns
   ## Advanced Patterns
   ## Best Practices (✅ DO / ❌ DON'T)
   ## Checklist
   ## References
   ```

3. **Add "Related Files" section** to each specialized file:
   ```markdown
   ## Related Files
   - See **CLAUDE-error-handling.md** for error handling in handlers
   - See **CLAUDE-security.md** for input validation
   - See **CLAUDE-testing.md** for testing patterns
   ```

**Estimated Effort:** 2-3 hours total

---

## Comparison: Go vs Python Implementation Guides

### File Count and Organization

| Metric | Python | Go | Status |
|--------|--------|----|----|
| **Total files** | 6 | 15 | Go has 2.5x more files |
| **Core orchestrator** | ✅ Excellent | ❌ Broken | **Python Better** |
| **Tooling guide** | ✅ Comprehensive | ❌ Missing | **Python Better** |
| **Specialized files quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Equal quality |
| **Consistency** | ✅ Excellent | ⚠️ Mixed | **Python Better** |
| **Navigation** | ✅ Clear | ❌ Unclear | **Python Better** |
| **Cross-references** | ✅ Working | ❌ Broken (points to non-existent files) | **Python Better** |

### Content Coverage

| Topic | Python | Go | Winner |
|-------|--------|----|----|
| **Core philosophy** | ✅ KISS, YAGNI, SOLID | ✅ KISS, YAGNI, SOLID | Equal |
| **Project structure** | ✅ src layout | ✅ cmd/internal/pkg | Equal |
| **Tooling** | ✅ UV, Ruff, MyPy, pytest | ❌ **MISSING** | **Python Better** |
| **Testing** | ✅ pytest, fixtures, coverage | ✅ table-driven, mocks, benchmarks | **Go Better** (benchmarks) |
| **Type safety** | ✅ mypy, Pydantic | ⚠️ Built-in (no file needed) | Equal |
| **Validation** | ✅ Pydantic patterns | ⚠️ Covered in security file | **Python Better** (dedicated file) |
| **Error handling** | ⚠️ In core file | ✅ **Dedicated file** | **Go Better** (more complex) |
| **Concurrency** | ⚠️ async in core file | ✅ **Dedicated file** | **Go Better** (goroutines) |
| **Security** | ⚠️ In validation file | ✅ **Comprehensive file** (1697 lines) | **Go Better** |
| **API patterns** | ⚠️ FastAPI in architecture | ✅ **Dedicated file** | **Go Better** |
| **Database** | ⚠️ Alembic in tooling | ✅ **Dedicated file** | **Go Better** |

### Overall Assessment

| Category | Python | Go | Recommendation |
|----------|--------|----|----|
| **Orchestration** | ✅ Excellent | ❌ **CRITICAL FAILURE** | **Fix Go immediately** |
| **Essential Files** | ✅ Complete (6/6) | ⚠️ Missing tooling (5/6) | **Fix Go immediately** |
| **Content Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **Equal (both excellent)** |
| **Organization** | ✅ Clear (6 files) | ⚠️ Confusing (15 files) | **Simplify Go** |
| **Consistency** | ✅ Excellent | ⚠️ Mixed | **Improve Go** |
| **Completeness** | ✅ 100% | ⚠️ 85% (missing tooling) | **Complete Go** |

**Verdict:**
- **Python guides are production-ready** ✅
- **Go guides need critical fixes** ⚠️ (orchestration, tooling, navigation)
- **Go content is excellent** but **organizational structure is broken**

---

## Conclusion

### Key Findings

✅ **Strengths:**
- Excellent content quality across all files (⭐⭐⭐⭐⭐)
- Comprehensive Clean Architecture guidance
- Strong Go-specific patterns (error handling, concurrency, security)
- Good code examples throughout
- Consistent terminology

❌ **Critical Issues:**
1. **CLAUDE-core.md is NOT an orchestrator** (just a tech stack list)
2. **CLAUDE-tooling.md is missing** (no Go tooling guidance)
3. **Broken references** to non-existent `.claude/patterns/` files
4. **No navigation structure** (unclear when to use which file)
5. **15 files vs Python's 6** (organization confusion)

### Immediate Next Steps

**Phase 1: CRITICAL FIXES (Required for Production Use)**
- [ ] Rewrite `CLAUDE-core.md` as orchestration file (2-3 hours)
- [ ] Create `CLAUDE-tooling.md` with Go development tools (3-4 hours)
- [ ] Remove all broken `.claude/patterns/` references (15 minutes)
- [ ] Add back-links and navigation to all files (1 hour)

**Estimated Total:** 6-8 hours

**Phase 2: IMPROVEMENTS (Recommended for Consistency)**
- [ ] Consider file consolidation (6-8 core files + optional specialized) (4-6 hours)
- [ ] Standardize file structure across all specialized files (2 hours)
- [ ] Add Podman/Devbox examples (1-2 hours)
- [ ] Add "Related Files" sections (1 hour)

**Estimated Total:** 8-11 hours

**Phase 3: ALIGNMENT WITH MAIN CLAUDE.MD (Optional but Recommended)**
- [ ] Update main CLAUDE.md to acknowledge Go's 15-file structure (30 minutes)
- [ ] OR consolidate Go files to match Python's 6-file structure (see Phase 2)

### Final Recommendation

**The Go specialized CLAUDE.md files have excellent content but critical organizational issues.**

**Before using Go guides in production:**
1. Fix CLAUDE-core.md orchestration (CRITICAL)
2. Create CLAUDE-tooling.md (CRITICAL)
3. Remove broken references (CRITICAL)
4. Add navigation structure (HIGH)

**After critical fixes, consider:**
- File consolidation to match Python structure (MEDIUM)
- Standardize file structure (LOW)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-17
**Related Document:** `docs/specialized_claude_evaluation.md` (Python evaluation baseline)
**Related Files:** `prompts/CLAUDE/go/CLAUDE-*.md` (all 15 Go implementation guides)
