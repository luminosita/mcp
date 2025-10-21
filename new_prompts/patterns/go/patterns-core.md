# CLAUDE.md - Core Go Development Guide

> **Hybrid Approach**: This is the lean core configuration. For detailed examples and specialized guidance, see the specialized configuration files linked below.
>
> **Taskfile Interface**: Use `task <command>` for all development operations. Taskfile provides a unified CLI interface across all projects, abstracting underlying tools (go, golangci-lint, gosec, govulncheck) for consistency. Use **Taskfile.yml** for Go projects.

## 📚 Specialized Configuration Files

### Development Tools & Practices
- **[patterns-tooling]mcp://resources/patterns/go/patterns-tooling** - Development tools: Taskfile, Go toolchain, golangci-lint, gosec, govulncheck, staticcheck, Wire, Swagger, golang-migrate, testify, gomock, NuShell, Devbox, Podman, Trivy container security scanning
- **[patterns-testing]mcp://resources/patterns/go/patterns-testing** - Testing strategy: table-driven tests, testify/mock, gomock, race detection, benchmarks, integration tests with build tags
- **[patterns-error-handling]mcp://resources/patterns/go/patterns-error-handling** - Error patterns: custom errors, wrapping, errors.Is/As, HTTP error mapping, context handling, panic recovery

### Architecture & Design
- **[patterns-architecture]mcp://resources/patterns/go/patterns-architecture** - Clean Architecture: Domain/Application/Infrastructure/Interface layers, Wire dependency injection, CQRS pattern, project structure
- **[patterns-http-frameworks]mcp://resources/patterns/go/patterns-http-frameworks** - HTTP framework comparison: Gin vs Chi vs Fiber, selection criteria, performance benchmarks, observability integration, migration paths
- **[patterns-concurrency]mcp://resources/patterns/go/patterns-concurrency** - Concurrency patterns: goroutines, channels, worker pools, fan-out/fan-in, errgroup, graceful shutdown, race condition prevention
- **[patterns-database]mcp://resources/patterns/go/patterns-database** - Database patterns: Repository pattern, connection pooling, GORM/sqlx examples, golang-migrate setup, transaction patterns

### Validation & Security
- **[patterns-validation]mcp://resources/patterns/go/patterns-validation** - Input validation: struct tags, sanitization, SQL injection prevention, path traversal protection, request/response DTOs
- **[patterns-security]mcp://resources/patterns/go/patterns-security** - Security patterns: authentication (JWT, OAuth2, PKCE), authorization (RBAC), CSRF protection, rate limiting, encryption
- **[patterns-api]mcp://resources/patterns/go/patterns-api** - REST API design: RESTful patterns, API versioning strategies, Swagger annotations, API key management, request/response handling

---

## 🎯 Core Development Philosophy

### KISS (Keep It Simple, Stupid)
Simplicity is a key design goal. Choose straightforward solutions over complex ones. Simple solutions are easier to understand, maintain, and debug.

### YAGNI (You Aren't Gonna Need It)
Implement features only when needed, not when anticipated for future use. Avoid speculative development.

### Go Proverbs (Guiding Principles)
Follow Go's philosophy:
- Clear is better than clever
- Don't communicate by sharing memory, share memory by communicating
- Concurrency is not parallelism
- Errors are values
- Don't just check errors, handle them gracefully
- Make the zero value useful
- Interface{} says nothing
- A little copying is better than a little dependency

### SOLID Principles
- **Single Responsibility**: Each package, struct, and function has one clear purpose
- **Open/Closed Principle**: Open for extension, closed for modification
- **Liskov Substitution**: Interfaces replaceable with implementations
- **Interface Segregation**: No forced dependencies on unused interfaces - keep interfaces small
- **Dependency Inversion**: Depend on abstractions (interfaces), not concretions (structs)

---

## 🧱 Code Structure & Modularity

### File and Function Limits
- **Files**: Maximum 200-400 lines - refactor by extracting packages if approaching this limit
- **Functions**: Maximum 50 lines for better AI comprehension and maintainability
- **Packages**: Focus on single responsibility, one clear concept
- **Cyclomatic complexity**: Maximum 10 per function

### Project Structure (Clean Architecture)
```
project-root/
├── go.mod                  # Module definition
├── go.sum                  # Dependency checksums
├── Taskfile.yml         # Task automation (Go version)
├── .golangci.yml           # Linter configuration
├── CLAUDE.md               # This file
├── cmd/                    # Application entry points (one per executable)
│   ├── api/main.go        # HTTP API server
│   ├── worker/main.go     # Background worker
│   └── migrate/main.go    # Database migrations
├── internal/              # Private application code
│   ├── domain/            # Business entities and rules (NO external dependencies)
│   │   ├── entities/      # Core business entities
│   │   ├── repositories/  # Repository interfaces (defined here)
│   │   └── services/      # Domain services
│   ├── application/       # Use cases and orchestration
│   │   ├── usecases/      # Application use cases
│   │   ├── commands/      # Command objects and DTOs
│   │   └── queries/       # Query objects and read models
│   ├── infrastructure/    # External concerns
│   │   ├── persistence/   # Database implementations
│   │   └── external/      # External service integrations
│   └── interfaces/        # Interface adapters
│       ├── http/          # HTTP handlers and middleware
│       ├── grpc/          # gRPC implementations
│       └── cli/           # CLI interfaces
├── pkg/                   # Public libraries (if any)
├── api/                   # API definitions (OpenAPI, protobuf)
├── configs/              # Configuration files
├── scripts/              # Build and deployment scripts
├── migrations/           # Database migrations
└── tests/                # Integration/E2E tests (optional)
    └── integration/
```

**See [patterns-architecture]mcp://resources/patterns/go/patterns-architecture for detailed Clean Architecture patterns and Wire DI setup**

---

### HTTP Framework Selection

**Recommended: Gin (stdlib-compatible, largest community)**

Go offers several HTTP framework options. Choose based on your priorities:

**Gin** (Recommended for most projects)
- ✅ stdlib-compatible (works with net/http middleware)
- ✅ Largest community (81k+ GitHub stars)
- ✅ HTTP/2 & HTTP/3 support
- ✅ Full observability ecosystem (OpenTelemetry, Prometheus)
- ✅ Mature middleware ecosystem (auth, rate limiting, CORS)
- ✅ Express.js-like API (familiar for Node.js developers)
- Performance: Excellent (slight overhead vs fasthttp)

**See [patterns-http-frameworks]mcp://resources/patterns/go/patterns-http-frameworks for detailed framework comparison, benchmarks, and migration paths**

---

## 📋 Code Style & Conventions

### Go Style Guide (Effective Go + Google/Uber)
- **Line length**: 80-100 characters (soft limit)
- **Indentation**: Tabs (gofmt default)
- **Braces**: K&R style (same line)
- **Formatting**: Use `gofmt` and `goimports` for ALL code (non-negotiable)

### Naming Conventions
- **Packages**: lowercase, single word (e.g., `user`, `payment`)
- **Exported**: PascalCase (e.g., `UserService`, `CreateOrder`)
- **Unexported**: camelCase (e.g., `userRepository`, `validateInput`)
- **Constants**: PascalCase or camelCase (not UPPER_SNAKE_CASE)
- **Interfaces**: Behavior-based, often `-er` suffix (e.g., `Reader`, `Writer`, `UserFinder`)
- **Acronyms**: Consistent case (e.g., `HTTP`, `URL`, `ID` not `Http`, `Url`, `Id`)
- **No "Get" prefix**: If field is `owner`, getter is `Owner()`
- **Avoid stuttering**: `user.ID` not `user.UserID` in user package

---

## 🎯 Type Safety & Interfaces

### Interface Design Principles
- **Keep interfaces small** - prefer single-method interfaces
- **Define at point of use** - not at implementation (interfaces belong where consumed)
- **Accept interfaces, return structs** - functions accept interfaces, return concrete types
- Use interface composition for complex contracts
- Repository interfaces MUST be in domain layer

```go
// Good: Small, focused interface defined where used
type UserFinder interface {
    FindByID(ctx context.Context, id string) (*User, error)
}

// Good: Accept interface, return struct
func GetUser(ctx context.Context, finder UserFinder, id string) (*User, error) {
    return finder.FindByID(ctx, id)
}
```

**See [patterns-architecture]mcp://resources/patterns/go/patterns-architecture for comprehensive interface and dependency inversion patterns**

---

## 📖 Documentation Standards

### Godoc Requirements
Every exported identifier MUST have a godoc comment:

```go
// UserService handles user-related business operations.
// It coordinates between user repository and business rules.
type UserService struct {
    repo UserRepository
}

// CreateUser creates a new user with validation.
// It returns an error if the email is already registered or validation fails.
//
// Parameters:
//   - ctx: Request context for cancellation
//   - req: User creation request with validated fields
//
// Returns:
//   - *User: Created user with generated ID
//   - error: Validation or persistence error
func (s *UserService) CreateUser(ctx context.Context, req CreateUserRequest) (*User, error) {
    // Implementation
}
```

**See [patterns-api]mcp://resources/patterns/go/patterns-api for Swagger/OpenAPI documentation patterns**

---

## 🧪 Testing Strategy

### Test Requirements
- Place tests alongside code with `_test.go` suffix
- Use table-driven tests for multiple scenarios
- Group related tests with `t.Run()` subtests
- Mark helpers with `t.Helper()`
- Use build tags for integration tests: `//go:build integration`
- **ALWAYS run with race detector**: `go test -race ./...`
- Minimum 80% coverage, 100% for critical business logic

### Basic Test Structure (Table-Driven)
```go
func TestUserService_CreateUser(t *testing.T) {
    tests := []struct {
        name    string
        req     CreateUserRequest
        wantErr bool
    }{
        {
            name: "valid user creation",
            req:  CreateUserRequest{Email: "test@example.com", Name: "Test User"},
            wantErr: false,
        },
        {
            name: "duplicate email",
            req:  CreateUserRequest{Email: "existing@example.com", Name: "Test User"},
            wantErr: true,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // Arrange, Act, Assert
        })
    }
}
```

**See [patterns-testing]mcp://resources/patterns/go/patterns-testing for comprehensive testing patterns with testify/mock and gomock**

---

## 🛠️ Development Tools

### Taskfile (Primary Interface)
```bash
# Essential commands - use Taskfile.yml for ALL operations
task --list                # Show all available tasks
task setup                 # Initial project setup (install tools)
task check                 # Run all quality checks
```

### Dependency Management (via Taskfile)
```bash
task deps:tidy             # Tidy go.mod and go.sum
task deps:download         # Download dependencies
task deps:verify           # Verify dependency checksums
task deps:update           # Update dependencies to latest
```

### Code Quality (via Taskfile)
```bash
# Linting and formatting
task lint:fix              # Run golangci-lint with auto-fix
task format                # Format with gofmt + goimports
task lint:all              # Lint + format

# Security scanning
task security:all          # Run gosec, govulncheck, staticcheck

# Testing
task test                  # Run tests with race detection and coverage
task test:coverage         # Run tests with 80%+ enforcement
```

### Code Generation (via Taskfile)
```bash
task generate:wire         # Generate Wire DI code
task generate:mocks        # Generate gomock mocks
task generate:swagger      # Generate Swagger/OpenAPI docs
task generate:all          # Run all generators
```

**See [patterns-tooling]mcp://resources/patterns/go/patterns-tooling for comprehensive Taskfile commands and tool configuration**

---

## 🔐 Error Handling & Security

### Error Handling (Critical)
- **ALWAYS check errors** - never ignore with `_`
- **Handle errors once** - log OR return, not both
- **Wrap with context**: `fmt.Errorf("context: %w", err)`
- **Return errors, don't panic** - reserve `panic` for exceptional cases
- Use `errors.Is()` and `errors.As()` for error inspection
- Create custom error types for domain-specific errors

```go
// Good: Wrap errors with context
if err := repo.Save(ctx, user); err != nil {
    return fmt.Errorf("failed to save user %s: %w", user.ID, err)
}

// Good: Custom domain errors
var ErrUserNotFound = errors.New("user not found")

// Check with errors.Is
if errors.Is(err, ErrUserNotFound) {
    // Handle specifically
}
```

### Security Best Practices
- Never log sensitive data (passwords, tokens, PII)
- Use parameterized queries for database operations
- Validate all user input at boundaries
- Keep dependencies updated with `govulncheck`
- Use `crypto/rand` for security (never `math/rand`)
- Enforce HTTPS/TLS 1.2+

**See [patterns-error-handling]mcp://resources/patterns/go/patterns-error-handling for comprehensive error patterns**
**See [patterns-security]mcp://resources/patterns/go/patterns-security for comprehensive security patterns**

---

## 🔄 Git Workflow

### Commit Message Format
**Never include "claude code" or "written by claude code" in commit messages**

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: feat, fix, docs, style, refactor, test, chore

Example:
```
feat(auth): add JWT token validation

- Implement JWT token validation middleware
- Add token refresh endpoint
- Update user authentication flow

Closes #156
```

---

## 🚨 CRITICAL ARCHITECTURE RULES

### Dependency Direction (STRICTLY ENFORCED)
- **Domain layer**: NO external dependencies (no database, HTTP, etc.)
- **Application layer**: Can import Domain only
- **Infrastructure layer**: Can import Domain and Application interfaces only
- **Interfaces layer**: Can import Application and Domain only
- **NEVER** import from outer to inner layers - **VIOLATION IS FORBIDDEN**

### Interface Definition
- Define interfaces where CONSUMED, not where implemented
- Repository interfaces MUST be in domain layer
- Service interfaces MUST be in domain or application layer
- Keep interfaces small and focused (Interface Segregation Principle)

**See [patterns-architecture]mcp://resources/patterns/go/patterns-architecture for detailed Clean Architecture implementation**

---

## ⚠️ Critical Guidelines

1. **Always use gofmt/goimports** - Non-negotiable formatting standard
2. **Check all errors** - Never use `_` to ignore errors
3. **Use context.Context** - First parameter for cancellation/timeouts
4. **Define interfaces at consumption** - Not at implementation
5. **Test with race detector** - Always run `go test -race ./...`
6. **Document all exports** - Complete godoc comments mandatory
7. **Minimum 80% coverage** - 100% for critical business logic
8. **Run all linters** - golangci-lint, gosec, govulncheck before commit
9. **Follow Clean Architecture** - Respect layer boundaries strictly
10. **Secure by default** - No hardcoded secrets, validate all inputs

---

## 📋 Pre-commit Checklist

Run `task check` to verify all requirements:

- [ ] All code formatted (`gofmt` + `goimports`)
- [ ] Godoc for all exported identifiers
- [ ] Tests written with 80%+ coverage (`task test:coverage` passes)
- [ ] Linting passes (`task lint` passes)
- [ ] Security scans pass (`task security:all` passes)
- [ ] Race detector passes (`go test -race ./...`)
- [ ] No vulnerable dependencies (`govulncheck`)
- [ ] Dependencies tidied (`go mod tidy`)
- [ ] Documentation updated if needed

**Quick command**: `task check` runs all quality checks

---

## 🚀 Quick Reference

### Development Setup
```bash
task setup                 # Install Go tools and dependencies
task info                  # Show environment information
```

### Quality Checks
```bash
task check                 # Run all checks (lint, security, test)
task lint:fix              # Fix linting issues
task format                # Format code
task security:all          # Run all security scans
task test:coverage         # Run tests with coverage enforcement
```

### Development Workflow
```bash
task run                   # Run application
task dev                   # Start with hot-reload (air)
task db:start              # Start PostgreSQL database
task container:build       # Build container image
task generate:all          # Run all code generators
```

### Show All Commands
```bash
task --list                # List all available tasks (use Taskfile.yml)
```

---

## 🧭 When to Use Each File

### Starting a New Go Project?
1. **mcp://resources/patterns/go/patterns-tooling** - Set up development tools (golangci-lint, wire, air, etc.)
2. **mcp://resources/patterns/go/patterns-architecture** - Structure your project with Clean Architecture

### Implementing Features?

**Need to validate input?**
→ **mcp://resources/patterns/go/patterns-validation** - Struct validation, request/response models, sanitization

**Building REST API?**
→ **mcp://resources/patterns/go/patterns-api** - RESTful design, versioning, Swagger documentation

**Database operations?**
→ **mcp://resources/patterns/go/patterns-database** - Repository pattern, migrations, connection pooling

**Background jobs or concurrent operations?**
→ **mcp://resources/patterns/go/patterns-concurrency** - Goroutines, channels, worker pools, graceful shutdown

**Handling errors?**
→ **mcp://resources/patterns/go/patterns-error-handling** - Custom errors, wrapping, context, HTTP mapping

### Adding Authentication/Security?
→ **mcp://resources/patterns/go/patterns-security** - JWT, OAuth2, PKCE, CSRF protection, rate limiting, encryption

### Writing Tests?
→ **mcp://resources/patterns/go/patterns-testing** - Table-driven tests, testify/mock, gomock, benchmarks, race detection

### Specialized Domains?

**gRPC service?**
→ **mcp://resources/patterns/go/patterns-grpc** - Proto definitions, server/client implementation, streaming

**WebSocket server?**
→ **mcp://resources/patterns/go/patterns-websockets** - Connection handling, broadcast patterns, room management

**Message queues (RabbitMQ, Kafka, NATS)?**
→ **mcp://resources/patterns/go/patterns-messaging** - Producer/consumer patterns, error handling, retries

**Caching layer (Redis, in-memory)?**
→ **mcp://resources/patterns/go/patterns-caching** - Cache-aside, write-through, TTL strategies

**CLI tool (Cobra)?**
→ **mcp://resources/patterns/go/patterns-cli** - Command structure, flags, configuration, subcommands

**Observability (logging, metrics, tracing)?**
→ **mcp://resources/patterns/go/patterns-observability** - Structured logging, Prometheus, OpenTelemetry, health checks

---

## Anti-Patterns (Do NOT Do)

### Architecture Violations
- ❌ Import from outer to inner layers
- ❌ Create circular dependencies
- ❌ Implement repositories in domain layer
- ❌ Put business logic in HTTP handlers or main
- ❌ Mix infrastructure with business logic

### Code Quality Violations
- ❌ Ignore errors with `_`
- ❌ Use `panic()` for normal error handling
- ❌ Create large, monolithic interfaces
- ❌ Use reflection in business logic (unless necessary)
- ❌ Skip input validation at boundaries
- ❌ Use global variables for dependency management

### Performance Violations
- ❌ Optimize without profiling first
- ❌ Create unnecessary goroutines for simple tasks
- ❌ Use mutexes when channels are more appropriate
- ❌ Ignore memory allocations in hot paths

---

## External Resources

- **Effective Go**: https://go.dev/doc/effective_go
- **Google Go Style Guide**: https://google.github.io/styleguide/go/
- **Uber Go Style Guide**: https://github.com/uber-go/guide/blob/master/style.md
- **Go Code Review Comments**: https://go.dev/wiki/CodeReviewComments
- **Go Proverbs**: https://go-proverbs.github.io/
- **OWASP Go Security**: https://github.com/OWASP/Go-SCP

---

**For detailed examples, patterns, and advanced configurations, refer to the specialized CLAUDE-*.md files organized by category at the top of this document.**
