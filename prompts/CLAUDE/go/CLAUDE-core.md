# CLAUDE.md - Go Clean Architecture

## Tech Stack
- **Language**: Go 1.21+
- **Architecture**: Clean Architecture with Domain-Driven Design
- **Build Tool**: Go modules (go.mod/go.sum)
- **Dependency Injection**: Google Wire (compile-time DI, preferred)
- **Testing**: Standard library testing + testify + gomock
- **HTTP Framework**: Standard library net/http, Gin, or Echo
- **Database**: PostgreSQL with database/sql or GORM
- **Documentation**: godoc + OpenAPI (swaggo)
- **Quality Control**: golangci-lint + staticcheck + gosec + govulncheck

## Project Structure

```
cmd/                    # Application entry points (one per executable)
├── api/main.go        # HTTP API server
├── worker/main.go     # Background worker
├── migrate/main.go    # Database migrations

internal/              # Private application code
├── domain/            # Business entities and rules (NO external dependencies)
│   ├── entities/      # Core business entities
│   ├── repositories/  # Repository interfaces (defined here)
│   └── services/      # Domain services
├── application/       # Use cases and orchestration
│   ├── usecases/      # Application use cases
│   ├── commands/      # Command objects and DTOs
│   └── queries/       # Query objects and read models
├── infrastructure/    # External concerns
│   ├── persistence/   # Database implementations
│   └── external/      # External service integrations
└── interfaces/        # Interface adapters
    ├── http/          # HTTP handlers and middleware
    ├── grpc/          # gRPC implementations
    └── cli/           # CLI interfaces

pkg/                   # Public libraries (if any)
api/                   # API definitions (OpenAPI, protobuf)
configs/              # Configuration files
scripts/              # Build and deployment scripts
```

## Core Commands

```bash
# Module management
go mod tidy                                      # Clean dependencies
go mod vendor                                    # Vendor dependencies

# Build
go build -o bin/api ./cmd/api                   # Development build
CGO_ENABLED=0 go build -ldflags="-s -w" ./cmd/api  # Production build

# Testing (ALWAYS with race detection)
go test -race -cover ./...                      # All tests with race detection
go test -race -coverprofile=coverage.out ./...  # Generate coverage
go tool cover -html=coverage.out                # View coverage report

# Code quality (MUST pass before commit)
golangci-lint run                               # Comprehensive linting
go vet ./...                                    # Static analysis
staticcheck ./...                               # Advanced analysis
gosec ./...                                     # Security scanning
govulncheck ./...                               # Vulnerability check

# Documentation
godoc -http=:6060                               # Local docs server
swag init -g cmd/api/main.go                   # Generate OpenAPI docs

# Dependency injection (if using Wire)
go generate ./...                               # Generate wire dependencies
```

## Core Development Philosophy

### Design Principles
- **KISS**: Keep It Simple - choose straightforward solutions over complex ones
- **YAGNI**: You Aren't Gonna Need It - implement only what's needed now
- **DRY**: Don't Repeat Yourself - reuse through functions and packages
- **SOLID**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **Fail Fast**: Validate early, return errors immediately
- **Composition Over Inheritance**: Use embedding and interfaces

### File and Function Limits
- **Files**: 200-400 lines, focused on related functionality
- **Functions**: Under 50 lines for better comprehension
- **Cyclomatic Complexity**: Maximum 10 per function
- **Packages**: Single responsibility, one clear concept

## 🚨 CRITICAL ARCHITECTURE RULES

### Dependency Direction (STRICTLY ENFORCED)
- **Domain layer**: NO external dependencies
- **Application layer**: Can import Domain only
- **Infrastructure layer**: Can import Domain and Application interfaces only
- **Interfaces layer**: Can import Application and Domain only
- **NEVER** import from outer to inner layers - **VIOLATION IS FORBIDDEN**

### Interface Definition
- Define interfaces where CONSUMED, not where implemented
- Repository interfaces MUST be in domain layer
- Service interfaces MUST be in domain or application layer
- Keep interfaces small and focused (Interface Segregation Principle)

## Code Style & Conventions

### Formatting (Non-negotiable)
- Use `gofmt` and `goimports` for ALL code
- Line length: 80-100 characters (soft limit)
- Indent: Tabs (gofmt default)
- Braces: K&R style (same line)

### Naming Conventions
- **Packages**: lowercase, single word (e.g., `user`, `payment`)
- **Exported**: PascalCase (e.g., `UserService`, `CreateOrder`)
- **Unexported**: camelCase (e.g., `userRepository`, `validateInput`)
- **Constants**: PascalCase or camelCase (not UPPER_SNAKE_CASE)
- **Interfaces**: Behavior-based, often `-er` suffix (e.g., `Reader`, `Writer`, `UserFinder`)
- **Acronyms**: Consistent case (e.g., `HTTP`, `URL`, `ID` not `Http`, `Url`, `Id`)
- **No "Get" prefix**: If field is `owner`, getter is `Owner()`
- **Avoid stuttering**: `user.ID` not `user.UserID` in user package

### Error Handling (Critical)
- **ALWAYS check errors** - never ignore with `_`
- **Handle errors once** - log OR return, not both
- **Wrap with context**: `fmt.Errorf("context: %w", err)`
- **Return errors, don't panic** - reserve `panic` for exceptional cases
- Use `errors.Is()` and `errors.As()` for error inspection
- Create custom error types for domain-specific errors
- For detailed patterns, see `.claude/patterns/error-handling.md`

### Interface Design
- **Keep interfaces small** - prefer single-method interfaces
- **Define at point of use** - not at implementation
- **Accept interfaces, return structs** - functions accept interfaces, return concrete types
- Use interface composition for complex contracts
- For detailed patterns, see `.claude/patterns/interfaces.md`

### Concurrency
- Use `context.Context` as first parameter for cancellation/timeouts
- Prefer channels for communication over mutexes
- Make goroutine lifetimes obvious, prevent leaks
- Use `sync.WaitGroup` for coordination
- Implement graceful shutdown with context cancellation
- For detailed patterns, see `.claude/patterns/concurrency.md`

## Testing Guidelines

### Test Organization
- Place tests alongside code with `_test.go` suffix
- Use table-driven tests for multiple scenarios
- Group related tests with `t.Run()` subtests
- Mark helpers with `t.Helper()`
- Use build tags for integration tests: `//go:build integration`

### Test Quality Standards
- Test behavior, not implementation
- Use descriptive names explaining the scenario
- Follow AAA pattern: Arrange, Act, Assert
- Test both success and error cases
- Mock external dependencies using interfaces
- **Minimum 80% coverage** for production code
- **100% coverage** for critical business logic
- For detailed patterns, see `.claude/patterns/testing.md`

## Documentation Standards

### Godoc Requirements
- Every exported identifier MUST have a godoc comment
- First sentence is summary, starting with identifier name
- Use complete sentences with proper capitalization
- Explain the "why", not just the "what"
- Document parameters and return values clearly
- For detailed patterns, see `.claude/patterns/documentation.md`

### API Documentation
- Use OpenAPI 3.0 specifications for HTTP APIs
- Use swaggo annotations for generating docs
- Keep specs in sync with code changes
- For detailed patterns, see `.claude/patterns/api-docs.md`

## Security Best Practices

### Critical Security Rules
- **Never log sensitive data** - no passwords, tokens, or PII
- **Use parameterized queries** - prevent SQL injection
- **Validate all inputs** - sanitize user data at boundaries
- **Use HTTPS only** - enforce TLS 1.2+
- **Keep dependencies updated** - run `govulncheck` regularly
- **Use crypto/rand** - never math/rand for security
- For detailed patterns, see `.claude/patterns/security.md`

## Performance Guidelines

### Optimization Strategy
- **Profile before optimizing** - measure, don't guess
- Use `pprof` for CPU and memory profiling
- Preallocate slices when size known: `make([]T, 0, capacity)`
- Use `sync.Pool` for frequently allocated objects
- Use `strings.Builder` for concatenation
- For detailed patterns, see `.claude/patterns/performance.md`

## Pre-commit Checklist

- [ ] All code formatted with `gofmt` and `goimports`
- [ ] No `golangci-lint` warnings
- [ ] All tests passing with race detection: `go test -race ./...`
- [ ] Coverage above 80% for business logic
- [ ] Godoc for all exported identifiers
- [ ] No security issues: `gosec ./...`
- [ ] `go mod tidy` executed
- [ ] No vulnerable dependencies: `govulncheck ./...`

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

## Specialized Pattern References

For detailed code examples and advanced patterns, see:

- **`.claude/patterns/architecture.md`** - Clean Architecture implementation examples
- **`.claude/patterns/interfaces.md`** - Interface design patterns with code examples
- **`.claude/patterns/error-handling.md`** - Comprehensive error handling patterns
- **`.claude/patterns/testing.md`** - Test patterns with mocks and table-driven tests
- **`.claude/patterns/concurrency.md`** - Goroutines, channels, and worker pools
- **`.claude/patterns/security.md`** - Security-critical code examples
- **`.claude/patterns/performance.md`** - Performance optimization patterns
- **`.claude/patterns/documentation.md`** - Documentation examples and standards
- **`.claude/patterns/api-docs.md`** - OpenAPI/Swagger documentation patterns
- **`.claude/configs/linting.md`** - golangci-lint configuration
- **`.claude/configs/docker.md`** - Dockerfile and Docker Compose templates
- **`.claude/configs/wire.md`** - Wire dependency injection setup

## Context Triggers

**When working on specific tasks, reference specialized patterns**:

- Implementing authentication → `.claude/patterns/security.md`
- Setting up DI → `.claude/configs/wire.md`
- Writing tests → `.claude/patterns/testing.md`
- Refactoring to Clean Architecture → `.claude/patterns/architecture.md`
- Performance issues → `.claude/patterns/performance.md`
- API documentation → `.claude/patterns/api-docs.md`

## External Resources

- **Effective Go**: https://go.dev/doc/effective_go
- **Google Go Style Guide**: https://google.github.io/styleguide/go/
- **Uber Go Style Guide**: https://github.com/uber-go/guide/blob/master/style.md
- **Go Code Review Comments**: https://go.dev/wiki/CodeReviewComments
- **Go Proverbs**: https://go-proverbs.github.io/
- **OWASP Go Security**: https://github.com/OWASP/Go-SCP

---

*This is the lean core CLAUDE.md. For detailed examples and patterns, always reference the specialized files in `.claude/patterns/` and `.claude/configs/`*
