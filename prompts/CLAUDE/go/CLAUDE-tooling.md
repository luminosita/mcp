# CLAUDE-tooling.md - Go Development Tools & Configuration

> **Specialized Guide**: Comprehensive tooling setup for Go development with golangci-lint, wire, swag, and testing frameworks.
>
> **Taskfile Interface**: All CLI commands are consolidated in `/Taskfile-go.yml` for consistent cross-platform execution. Use `task <command>` as the primary interface; individual tool commands documented below for understanding and configuration.

**← [Back to Go Development Guide](./CLAUDE-core.md)**

---

## 🎯 Taskfile - Unified CLI Interface

### Why Taskfile?
Taskfile provides a unified interface for all development operations:
- **Cross-platform consistency** - Same commands work on macOS, Linux, Windows
- **Self-documenting** - `task --list` shows all available commands
- **Language-agnostic** - Works across Python, Go, Rust, or any future tech stack
- **Simple YAML** - Easy to read, extend, and maintain
- **No dependencies** - Single binary, no runtime requirements

**Philosophy**: Taskfile is the common facade for ALL CLI operations. Individual tools (go, golangci-lint, wire, swag) are implementation details abstracted behind Taskfile tasks.

### Installation

```bash
# macOS
brew install go-task

# Linux (via snap)
snap install task --classic

# Linux (via sh script)
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin

# Windows (via Scoop)
scoop install task

# Or add to Devbox (recommended)
devbox add go-task
```

### Essential Commands

```bash
# Show all available tasks (Go project)
task --list

# Show detailed task information
task --list-all

# Run specific task
task <task-name>

# Pass arguments to task
task test:run -- PKG=./internal/...
```

### Common Development Tasks

#### Code Quality
```bash
# Run linter (golangci-lint)
task lint

# Run linter with auto-fix
task lint:fix

# Run specific linter
task lint:specific -- LINTER=gosec

# Format code
task format

# Check formatting without changes
task format:check

# Run all code quality checks
task quality
```

#### Testing
```bash
# Run all tests with coverage
task test

# Run tests with race detection
task test:race

# Run specific package tests
task test:pkg -- PKG=./internal/domain

# Run integration tests
task test:integration

# Run benchmarks
task bench

# Generate coverage report
task coverage

# Generate HTML coverage report
task coverage:html
```

#### Quality Checks (All)
```bash
# Run all quality checks (format, lint, test)
task check

# Run CI/CD pipeline checks
task check:ci
```

#### Dependency Management
```bash
# Tidy dependencies
task deps:tidy

# Vendor dependencies
task deps:vendor

# Update dependencies
task deps:update

# Show dependency graph
task deps:graph

# Check for vulnerabilities
task deps:vuln
```

#### Build & Run
```bash
# Build application
task build

# Build for production (optimized)
task build:prod

# Build for all platforms
task build:all

# Run application
task run

# Start development server with hot-reload
task dev

# Generate wire dependency injection
task generate:wire

# Generate all code (wire, swagger, mocks)
task generate
```

#### API Documentation
```bash
# Generate Swagger documentation
task docs:swagger

# Serve Swagger docs locally
task docs:serve

# Validate Swagger spec
task docs:validate
```

#### Container Operations (Podman)
```bash
# Build container image
task container:build

# Run application container
task container:run

# Stop container
task container:stop

# View container logs
task container:logs

# Execute shell in container
task container:shell

# Clean containers and images
task container:clean

# Scan container for vulnerabilities (all severities)
task container:scan

# Scan for critical/high vulnerabilities
task container:scan:critical

# Generate SARIF report
task container:scan:sarif

# Generate JSON report
task container:scan:json
```

#### Database Operations (Podman)
```bash
# Start PostgreSQL database
task db:start

# Stop database
task db:stop

# Connect to database shell
task db:shell

# View database logs
task db:logs

# Restart database
task db:restart

# Apply migrations
task db:migrate

# Rollback last migration
task db:migrate:down

# Create new migration
task db:migrate:create -- NAME=add_users_table
```

#### Utilities
```bash
# Clean build artifacts
task clean

# Clean everything including vendor
task clean:all

# Initial project setup
task setup

# Show project environment info
task info

# Show help
task help
```

---

## 🛠️ Go Toolchain

### Why Go?
Go provides:
- **Fast compilation** - Build times measured in seconds
- **Built-in tooling** - go fmt, go test, go build all included
- **Static typing** - Catch errors at compile time
- **Concurrency primitives** - Goroutines and channels built-in
- **Single binary deployment** - No runtime dependencies
- **Cross-platform** - Compile for any OS/arch combination

### Go Installation

```bash
# macOS
brew install go

# Linux (via snap)
snap install go --classic

# Linux (manual)
wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin

# Windows (via Scoop)
scoop install go

# Or via Devbox (recommended)
devbox add go@1.21

# Verify installation
go version
```

### Go Project Initialization

```bash
# Create new module
go mod init github.com/user/project

# Initialize project structure
mkdir -p cmd/api internal/domain pkg

# Create main.go
cat > cmd/api/main.go <<EOF
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
EOF

# Run application
go run cmd/api/main.go
```

### Essential go.mod Configuration

```go
module github.com/user/project

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/lib/pq v1.10.9
    github.com/google/wire v0.5.0
    github.com/swaggo/gin-swagger v1.6.0
)

require (
    // Indirect dependencies managed automatically
)
```

### Go Commands Reference

#### Module Management
```bash
# Initialize module
go mod init github.com/user/project

# Add dependency
go get github.com/gin-gonic/gin@latest

# Add specific version
go get github.com/gin-gonic/gin@v1.9.1

# Remove unused dependencies
go mod tidy

# Vendor dependencies
go mod vendor

# Verify dependencies
go mod verify

# Show dependency graph
go mod graph

# Update dependencies
go get -u ./...

# Update specific dependency
go get -u github.com/gin-gonic/gin
```

#### Building
```bash
# Build current package
go build

# Build specific package
go build ./cmd/api

# Build with output name
go build -o bin/api ./cmd/api

# Build for production (optimized, stripped)
CGO_ENABLED=0 go build -ldflags="-s -w" -o bin/api ./cmd/api

# Build for multiple platforms
GOOS=linux GOARCH=amd64 go build -o bin/api-linux-amd64 ./cmd/api
GOOS=darwin GOARCH=arm64 go build -o bin/api-darwin-arm64 ./cmd/api
GOOS=windows GOARCH=amd64 go build -o bin/api-windows-amd64.exe ./cmd/api

# Show build info
go version -m bin/api
```

#### Testing
```bash
# Run all tests
go test ./...

# Run tests with verbose output
go test -v ./...

# Run tests with race detection (ALWAYS use for concurrent code)
go test -race ./...

# Run tests with coverage
go test -cover ./...

# Generate coverage report
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out

# Run specific package tests
go test ./internal/domain

# Run specific test
go test -run TestUserCreate ./internal/domain

# Run benchmarks
go test -bench=. ./...

# Run benchmarks with memory stats
go test -bench=. -benchmem ./...

# Run tests in parallel
go test -p 4 ./...
```

#### Code Quality
```bash
# Format code (required before commit)
go fmt ./...

# Organize imports
goimports -w .

# Lint code (basic)
go vet ./...

# Show compilation errors
go build ./...

# Clean build cache
go clean -cache
```

---

## 🔍 golangci-lint - Comprehensive Linter

### Why golangci-lint?
golangci-lint runs ~50+ linters in parallel:
- **Fast** - Runs multiple linters concurrently
- **Comprehensive** - Includes gosec, staticcheck, govet, errcheck, and more
- **Configurable** - Enable/disable linters per project
- **IDE integration** - Works with VS Code, GoLand, Vim
- **CI/CD ready** - Exit codes, JSON output for automation

### Installation

```bash
# macOS
brew install golangci-lint

# Linux (via binary)
curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(go env GOPATH)/bin

# Or via Devbox (recommended)
devbox add golangci-lint

# Verify installation
golangci-lint version
```

### Configuration (.golangci.yml)

```yaml
# .golangci.yml
run:
  timeout: 5m
  modules-download-mode: readonly
  skip-dirs:
    - vendor
    - third_party
  skip-files:
    - ".*\\.pb\\.go$"
    - ".*_gen\\.go$"

output:
  format: colored-line-number
  print-issued-lines: true
  print-linter-name: true

linters:
  enable:
    - errcheck      # Check unchecked errors
    - gosimple      # Simplify code
    - govet         # Go vet (official)
    - ineffassign   # Detect ineffectual assignments
    - staticcheck   # Advanced static analysis
    - typecheck     # Type checking
    - unused        # Find unused code
    - gosec         # Security issues
    - gocyclo       # Cyclomatic complexity
    - gofmt         # Check formatting
    - goimports     # Check import organization
    - goconst       # Find repeated strings (constants)
    - misspell      # Spelling mistakes
    - revive        # Fast linter (replaces golint)
    - unconvert     # Unnecessary type conversions
    - unparam       # Unused function parameters
    - bodyclose     # HTTP response body closed
    - noctx         # HTTP requests without context
    - errname       # Error naming conventions
    - errorlint     # Error wrapping issues
    - exportloopref # Loop variable captured by func literal
    - gocritic      # Comprehensive diagnostic checks
    - gocognit      # Cognitive complexity
    - nestif        # Deeply nested if statements
    - prealloc      # Slice preallocation
  disable:
    - deadcode      # Deprecated (use unused instead)
    - varcheck      # Deprecated (use unused instead)
    - structcheck   # Deprecated (use unused instead)

linters-settings:
  errcheck:
    check-type-assertions: true
    check-blank: true

  govet:
    check-shadowing: true
    settings:
      printf:
        funcs:
          - (github.com/sirupsen/logrus.FieldLogger).Infof
          - (github.com/sirupsen/logrus.FieldLogger).Warnf

  gocyclo:
    min-complexity: 15

  gocognit:
    min-complexity: 20

  revive:
    rules:
      - name: exported
        severity: warning
      - name: unexported-return
      - name: var-naming
      - name: package-comments
      - name: indent-error-flow
      - name: errorf
      - name: empty-block
      - name: superfluous-else
      - name: unreachable-code
      - name: redefines-builtin-id

  gosec:
    severity: medium
    confidence: medium
    excludes:
      - G104  # Audit errors not checked (use errcheck instead)
      - G304  # File path from variable (valid in many cases)

  staticcheck:
    go: "1.21"
    checks:
      - "all"
      - "-SA1019" # Allow deprecated packages (for gradual migration)

  goconst:
    min-len: 3
    min-occurrences: 3

  misspell:
    locale: US

issues:
  exclude-rules:
    # Exclude some linters from test files
    - path: _test\.go
      linters:
        - gocyclo
        - gosec
        - errcheck
        - goconst
        - unparam

    # Exclude known false positives
    - linters:
        - staticcheck
      text: "SA9003:"  # Empty branch

  max-issues-per-linter: 0
  max-same-issues: 0
  new: false
```

### golangci-lint Commands

```bash
# Run all enabled linters
golangci-lint run

# Run on specific directory
golangci-lint run ./internal/...

# Run with auto-fix (where possible)
golangci-lint run --fix

# Run specific linters
golangci-lint run --enable-only=gosec,errcheck

# Disable specific linters
golangci-lint run --disable=gocyclo

# Show enabled linters
golangci-lint linters

# Run with verbose output
golangci-lint run -v

# Generate configuration
golangci-lint config

# Print statistics
golangci-lint run --issues-exit-code=0 | grep -E '^(internal|cmd)'
```

---

## 🔐 gosec - Security Scanner

### Why gosec?
gosec inspects Go code for security issues:
- **CWE database** - Maps findings to Common Weakness Enumeration
- **Rule-based** - 30+ security rules (SQL injection, XSS, crypto misuse, etc.)
- **Configurable** - Exclude rules, paths, or specific issues
- **Fast** - Analyzes entire codebase in seconds
- **CI/CD ready** - JSON/SARIF output for automation

### gosec Configuration

```go
// gosec.json (optional - use .golangci.yml instead)
{
  "tests": false,
  "exclude": [
    "G104",  // Audit errors not checked (use errcheck)
    "G304"   // File path from variable (valid in many cases)
  ],
  "exclude-dirs": [
    "vendor",
    "testdata"
  ],
  "severity": "medium",
  "confidence": "medium"
}
```

### gosec Commands

```bash
# Install gosec
go install github.com/securego/gosec/v2/cmd/gosec@latest

# Run security scan
gosec ./...

# Run with detailed output
gosec -fmt=json ./... > gosec-report.json

# Scan specific directory
gosec ./internal/...

# Exclude specific rules
gosec -exclude=G104,G304 ./...

# Show all available rules
gosec -help rules

# Generate SARIF report (for GitHub Security)
gosec -fmt=sarif -out=gosec.sarif ./...
```

---

## 🛡️ govulncheck - Vulnerability Scanner

### Why govulncheck?
govulncheck checks for known vulnerabilities in dependencies:
- **Official Go tool** - Maintained by Go team
- **Go vulnerability database** - Curated vulnerability data
- **Call graph analysis** - Only reports if vulnerable code is actually called
- **Fast** - Analyzes dependencies in seconds
- **CI/CD ready** - Exit codes for blocking builds

### Installation

```bash
# Install govulncheck
go install golang.org/x/vuln/cmd/govulncheck@latest

# Verify installation
govulncheck -version
```

### govulncheck Commands

```bash
# Check for vulnerabilities
govulncheck ./...

# Check with verbose output
govulncheck -v ./...

# Check with JSON output
govulncheck -json ./...

# Scan binary (production validation)
govulncheck -mode=binary ./bin/api

# Update vulnerability database
govulncheck -db=https://vuln.go.dev ./...
```

---

## 📊 staticcheck - Advanced Static Analysis

### Why staticcheck?
staticcheck provides advanced static analysis:
- **Go-specific** - Understands Go idioms and patterns
- **Comprehensive** - Checks for bugs, performance issues, and style
- **Fast** - Runs in parallel, caches results
- **Precise** - Low false positive rate
- **Actively maintained** - Regular updates for new Go versions

### Installation

```bash
# Install staticcheck
go install honnef.co/go/tools/cmd/staticcheck@latest

# Or via Devbox
devbox add staticcheck

# Verify installation
staticcheck -version
```

### staticcheck Configuration

```toml
# staticcheck.conf
checks = ["all", "-SA1019"]  # Enable all, disable deprecated warnings

[[formatters]]
formatter = "text"
```

### staticcheck Commands

```bash
# Run static analysis
staticcheck ./...

# Run on specific package
staticcheck ./internal/domain

# Show all available checks
staticcheck -list-checks

# Run with specific checks
staticcheck -checks=SA1000,SA1001 ./...

# Disable specific checks
staticcheck -checks=all,-SA1019 ./...

# Generate machine-readable output
staticcheck -f=json ./...
```

---

## 🔗 Google Wire - Dependency Injection

### Why Wire?
Wire generates dependency injection code at compile time:
- **Compile-time safety** - Catches missing dependencies before runtime
- **No reflection** - Generated code is plain Go, no runtime overhead
- **Explicit dependencies** - Clear dependency graph
- **Type-safe** - Full type checking by Go compiler
- **Easy debugging** - Generated code is readable and debuggable

### Installation

```bash
# Install wire
go install github.com/google/wire/cmd/wire@latest

# Or via Devbox
devbox add wire

# Verify installation
wire version
```

### Wire Setup

#### 1. Define Providers

```go
// internal/di/providers.go
//go:build wireinject

package di

import (
    "database/sql"
    "github.com/google/wire"
    "myapp/internal/application/usecases"
    "myapp/internal/infrastructure/persistence/postgres"
    httphandlers "myapp/internal/interfaces/http"
)

// RepositorySet provides all repository implementations
var RepositorySet = wire.NewSet(
    postgres.NewUserRepository,
    wire.Bind(new(repositories.UserRepository), new(*postgres.UserRepository)),
)

// UseCaseSet provides all use cases
var UseCaseSet = wire.NewSet(
    usecases.NewCreateUserUseCase,
    usecases.NewGetUserUseCase,
    usecases.NewListUsersUseCase,
)

// HandlerSet provides all HTTP handlers
var HandlerSet = wire.NewSet(
    httphandlers.NewUserHandler,
)

// InitializeUserHandler wires up UserHandler with all dependencies
func InitializeUserHandler(db *sql.DB) (*httphandlers.UserHandler, error) {
    wire.Build(
        RepositorySet,
        UseCaseSet,
        HandlerSet,
    )
    return nil, nil
}

// InitializeApplication wires up entire application
func InitializeApplication(db *sql.DB) (*Application, error) {
    wire.Build(
        RepositorySet,
        UseCaseSet,
        HandlerSet,
        NewApplication,
    )
    return nil, nil
}

type Application struct {
    UserHandler *httphandlers.UserHandler
    // Add more handlers as needed
}

func NewApplication(userHandler *httphandlers.UserHandler) *Application {
    return &Application{
        UserHandler: userHandler,
    }
}
```

#### 2. Generate Wire Code

```bash
# Generate wire code (creates wire_gen.go)
cd internal/di && wire

# Or use task command
task generate:wire

# The generated file wire_gen.go should be committed to git
```

#### 3. Use Generated Code

```go
// cmd/api/main.go
package main

import (
    "database/sql"
    "log"
    "myapp/internal/di"
    _ "github.com/lib/pq"
)

func main() {
    // Initialize database
    db, err := sql.Open("postgres", "postgresql://localhost/myapp")
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    // Wire handles all dependency injection
    app, err := di.InitializeApplication(db)
    if err != nil {
        log.Fatal(err)
    }

    // Use injected dependencies
    router := setupRouter(app.UserHandler)
    log.Fatal(router.Run(":8080"))
}
```

### Wire Commands

```bash
# Generate wire code
wire

# Generate wire code with verbose output
wire -v

# Show wire dependencies graph
wire show

# Clean generated files
rm wire_gen.go
```

### Wire Best Practices

1. **One provider per file** - Keep providers.go focused
2. **Group related providers** - Use wire.NewSet for logical groups
3. **Use interfaces** - Bind implementations to interfaces with wire.Bind
4. **Commit generated code** - wire_gen.go should be in version control
5. **Run wire in CI** - Verify generated code is up-to-date
6. **Use build tags** - `//go:build wireinject` prevents import cycles

---

## 📚 swaggo - OpenAPI/Swagger Documentation

### Why swaggo?
swaggo generates OpenAPI documentation from Go comments:
- **Annotation-based** - Documents API alongside code
- **Auto-generated** - Regenerates docs from code changes
- **Swagger UI integration** - Interactive API documentation
- **Type-safe** - Validates against Go types
- **Multiple formats** - JSON, YAML, HTML

### Installation

```bash
# Install swag
go install github.com/swaggo/swag/cmd/swag@latest

# Or via Devbox
devbox add swag

# Verify installation
swag version
```

### Swagger Setup

#### 1. Add General API Information

```go
// cmd/api/main.go

// @title User Management API
// @version 2.0
// @description API for managing users and authentication
// @termsOfService http://swagger.io/terms/

// @contact.name API Support
// @contact.url http://www.swagger.io/support
// @contact.email support@swagger.io

// @license.name Apache 2.0
// @license.url http://www.apache.org/licenses/LICENSE-2.0.html

// @host localhost:8080
// @BasePath /api/v1

// @securityDefinitions.apikey BearerAuth
// @in header
// @name Authorization
// @description Type "Bearer" followed by a space and JWT token

func main() {
    // Application setup
}
```

#### 2. Annotate Handlers

```go
// internal/interfaces/http/user_handler.go

// CreateUser godoc
// @Summary Create a new user
// @Description Create a new user with the provided details
// @Tags users
// @Accept json
// @Produce json
// @Param user body CreateUserRequest true "User details"
// @Success 201 {object} UserResponse
// @Failure 400 {object} ErrorResponse
// @Failure 409 {object} ErrorResponse "User already exists"
// @Failure 500 {object} ErrorResponse
// @Router /users [post]
func (h *UserHandler) CreateUser(c *gin.Context) {
    // Handler implementation
}

// GetUser godoc
// @Summary Get user by ID
// @Description Get detailed information about a user
// @Tags users
// @Accept json
// @Produce json
// @Param id path string true "User ID"
// @Success 200 {object} UserResponse
// @Failure 404 {object} ErrorResponse "User not found"
// @Failure 500 {object} ErrorResponse
// @Security BearerAuth
// @Router /users/{id} [get]
func (h *UserHandler) GetUser(c *gin.Context) {
    // Handler implementation
}

// ListUsers godoc
// @Summary List all users
// @Description Get a paginated list of users
// @Tags users
// @Accept json
// @Produce json
// @Param page query int false "Page number" default(1)
// @Param page_size query int false "Page size" default(10)
// @Param sort_by query string false "Sort field" Enums(created_at, email, username)
// @Param sort_dir query string false "Sort direction" Enums(asc, desc)
// @Success 200 {object} PaginatedResponse
// @Failure 400 {object} ErrorResponse
// @Failure 500 {object} ErrorResponse
// @Security BearerAuth
// @Router /users [get]
func (h *UserHandler) ListUsers(c *gin.Context) {
    // Handler implementation
}
```

#### 3. Generate Swagger Docs

```bash
# Generate swagger docs (creates docs/ directory)
swag init -g cmd/api/main.go

# Or use task command
task docs:swagger

# Files generated:
# - docs/docs.go
# - docs/swagger.json
# - docs/swagger.yaml
```

#### 4. Integrate Swagger UI

```go
// cmd/api/main.go
import (
    "github.com/gin-gonic/gin"
    swaggerFiles "github.com/swaggo/files"
    ginSwagger "github.com/swaggo/gin-swagger"
    _ "myapp/docs"  // Import generated docs
)

func main() {
    router := gin.Default()

    // Swagger UI endpoint
    router.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

    // API routes
    v1 := router.Group("/api/v1")
    {
        v1.POST("/users", userHandler.CreateUser)
        v1.GET("/users/:id", userHandler.GetUser)
        v1.GET("/users", userHandler.ListUsers)
    }

    router.Run(":8080")
}
```

#### 5. View Documentation

```bash
# Start server
go run cmd/api/main.go

# Open browser to Swagger UI
open http://localhost:8080/swagger/index.html
```

### swag Commands

```bash
# Generate swagger docs
swag init -g cmd/api/main.go

# Generate with custom output directory
swag init -g cmd/api/main.go -o ./api/docs

# Generate with specific API version
swag init -g cmd/api/main.go --instanceName v1

# Validate swagger spec
swag fmt

# Show swag version
swag version
```

### Swagger Annotation Reference

```go
// API Metadata
// @title API Title
// @version 1.0
// @description API Description
// @host localhost:8080
// @BasePath /api/v1

// Endpoint Documentation
// @Summary Short summary
// @Description Detailed description
// @Tags tag1,tag2
// @Accept json
// @Produce json
// @Param name query string false "Description"
// @Success 200 {object} ResponseType
// @Failure 400 {object} ErrorType
// @Router /endpoint [get]

// Security
// @securityDefinitions.apikey BearerAuth
// @in header
// @name Authorization
// @Security BearerAuth

// Request Body
// @Param body body RequestType true "Description"

// Path Parameters
// @Param id path string true "User ID"

// Query Parameters
// @Param page query int false "Page number" default(1)
// @Param sort query string false "Sort" Enums(asc, desc)
```

---

## 🧪 Testing Tools

### testify - Testing Toolkit

```bash
# Install testify
go get github.com/stretchr/testify
```

#### testify/assert Example

```go
import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestUserCreate(t *testing.T) {
    user := &User{Email: "test@example.com"}

    assert.NotNil(t, user)
    assert.Equal(t, "test@example.com", user.Email)
    assert.True(t, user.IsValid())
}
```

#### testify/require Example (stops test on failure)

```go
import (
    "testing"
    "github.com/stretchr/testify/require"
)

func TestUserRepository(t *testing.T) {
    db := setupTestDB(t)
    require.NotNil(t, db, "Database connection required")

    user, err := CreateUser(db, "test@example.com")
    require.NoError(t, err, "User creation should not fail")
    require.NotNil(t, user)
}
```

#### testify/mock Example

```go
import (
    "testing"
    "github.com/stretchr/testify/mock"
)

type MockUserRepository struct {
    mock.Mock
}

func (m *MockUserRepository) FindByID(id string) (*User, error) {
    args := m.Called(id)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*User), args.Error(1)
}

func TestUserService(t *testing.T) {
    mockRepo := new(MockUserRepository)
    mockRepo.On("FindByID", "123").Return(&User{ID: "123"}, nil)

    service := NewUserService(mockRepo)
    user, err := service.GetUser("123")

    assert.NoError(t, err)
    assert.Equal(t, "123", user.ID)
    mockRepo.AssertExpectations(t)
}
```

### gomock - Official Mock Generator

```bash
# Install gomock
go install github.com/golang/mock/mockgen@latest
```

#### Generate Mocks

```go
//go:generate mockgen -destination=mocks/user_repository_mock.go -package=mocks myapp/internal/domain/repositories UserRepository

// Generate mocks
go generate ./...
```

#### Use Generated Mocks

```go
import (
    gomock "github.com/golang/mock/gomock"
    "myapp/internal/domain/repositories/mocks"
)

func TestUserService(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockRepo := mocks.NewMockUserRepository(ctrl)
    mockRepo.EXPECT().FindByID("123").Return(&User{ID: "123"}, nil)

    service := NewUserService(mockRepo)
    user, err := service.GetUser("123")

    assert.NoError(t, err)
    assert.Equal(t, "123", user.ID)
}
```

---

## 🐚 NuShell - Cross-Platform Shell (same as Python)

See Python CLAUDE-tooling.md for comprehensive NuShell documentation. All NuShell patterns apply equally to Go projects.

---

## 📦 Devbox - Portable Isolated Environments (same as Python)

See Python CLAUDE-tooling.md for comprehensive Devbox documentation. Devbox works identically for Go projects.

### Go-Specific Devbox Configuration

```json
{
  "$schema": "https://jetpack.io/devbox/schema.json",
  "packages": [
    "go@1.21",
    "golangci-lint",
    "wire",
    "swag",
    "podman",
    "git",
    "nushell",
    "postgresql@15",
    "go-task"
  ],
  "shell": {
    "init_hook": [
      "echo 'Welcome to Go development environment'",
      "go version",
      "golangci-lint version"
    ],
    "scripts": {
      "setup": "nu scripts/setup.nu",
      "test": "go test -race ./...",
      "lint": "golangci-lint run --fix",
      "build": "go build -o bin/api ./cmd/api",
      "dev": "air",
      "wire": "cd internal/di && wire",
      "swagger": "swag init -g cmd/api/main.go",
      "db:start": "podman run -d --name go-db -e POSTGRES_PASSWORD=dev -p 5432:5432 postgres:15"
    }
  },
  "env": {
    "GOPATH": "$HOME/go",
    "GOBIN": "$HOME/go/bin",
    "DATABASE_URL": "postgresql://postgres:dev@localhost:5432/myapp"
  }
}
```

---

## 🐳 Podman - Daemonless Container Runtime (same as Python)

See Python CLAUDE-tooling.md for comprehensive Podman documentation. All Podman patterns apply equally to Go projects.

### Go-Specific Containerfile (Multi-Stage Build)

```dockerfile
# Containerfile for Go application
# Multi-stage build for optimized production image

# Stage 1: Builder
FROM golang:1.21-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git ca-certificates

WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build application (static binary)
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags="-s -w" \
    -o /app/bin/api \
    ./cmd/api

# Stage 2: Runtime
FROM alpine:latest

# Install runtime dependencies
RUN apk --no-cache add ca-certificates

# Create non-root user
RUN adduser -D -u 1000 appuser

WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/bin/api /app/api

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Run application
CMD ["/app/api"]
```

---

## 🔄 golang-migrate - Database Migrations

### Why golang-migrate?
golang-migrate manages database schema migrations:
- **Version control** - Track schema changes over time
- **Up/Down migrations** - Roll forward and back
- **Multiple databases** - PostgreSQL, MySQL, SQLite, MongoDB
- **CLI and library** - Use as tool or import as package
- **Atomic migrations** - Transaction support

### Installation

```bash
# Install migrate CLI
go install -tags 'postgres' github.com/golang-migrate/migrate/v4/cmd/migrate@latest

# Or via Devbox
devbox add migrate

# Verify installation
migrate -version
```

### Migration Files

```
migrations/
├── 000001_create_users_table.up.sql
├── 000001_create_users_table.down.sql
├── 000002_create_posts_table.up.sql
├── 000002_create_posts_table.down.sql
└── ...
```

#### Example Migration

```sql
-- migrations/000001_create_users_table.up.sql
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_username ON users(username) WHERE deleted_at IS NULL;
```

```sql
-- migrations/000001_create_users_table.down.sql
DROP TABLE IF EXISTS users;
```

### migrate Commands

```bash
# Create new migration
migrate create -ext sql -dir migrations -seq create_users_table

# Apply all up migrations
migrate -path migrations -database "postgresql://localhost/myapp?sslmode=disable" up

# Apply N migrations
migrate -path migrations -database "postgresql://localhost/myapp?sslmode=disable" up 2

# Rollback last migration
migrate -path migrations -database "postgresql://localhost/myapp?sslmode=disable" down 1

# Rollback all migrations
migrate -path migrations -database "postgresql://localhost/myapp?sslmode=disable" down

# Show current migration version
migrate -path migrations -database "postgresql://localhost/myapp?sslmode=disable" version

# Force set version (recovery)
migrate -path migrations -database "postgresql://localhost/myapp?sslmode=disable" force 1
```

---

## 🔄 Complete Development Workflow

### Initial Setup

```bash
# 1. Install Go and tools
brew install go go-task golangci-lint

# 2. Clone repository
git clone https://github.com/user/project.git
cd project

# 3. Run initial setup
task setup

# 4. Enter Devbox shell (optional but recommended)
devbox shell

# 5. Verify environment
task info
```

### Daily Development Workflow

```bash
# 1. Pull latest changes
git pull origin main

# 2. Create feature branch
git checkout -b feature/new-feature

# 3. Add dependencies if needed
go get github.com/gin-gonic/gin@latest
go mod tidy

# 4. Make code changes
# ... edit files ...

# 5. Generate code (if needed)
task generate

# 6. Run quality checks
task format     # Format code
task lint       # Run linters
task test       # Run tests

# Or run all checks
task check

# 7. Commit changes
git add .
git commit -m "feat: add new feature"

# 8. Push changes
git push origin feature/new-feature
```

### Test-Driven Development Workflow

```bash
# 1. Write test
vim internal/domain/user_test.go

# 2. Run tests in watch mode (using air or similar)
task test:watch

# 3. Implement feature
vim internal/domain/user.go

# 4. Tests automatically re-run

# 5. Check coverage
task coverage:html
open coverage.html
```

### CI/CD Pipeline

```bash
# Run all CI checks
task check:ci

# Individual CI steps
task deps:tidy          # Verify dependencies
task format:check       # Check formatting
task lint               # Run linters
task test:race          # Run tests with race detection
task test:coverage      # Check coverage
task build              # Build application
task container:build    # Build container
```

---

## ⚠️ Critical Tool Requirements

### CLI Interface (Primary)
1. **Use Taskfile for all operations** - `task <command>` is the primary interface
2. **Never use direct tool commands in docs** - Always reference Taskfile tasks
3. **Extend Taskfile for new operations** - Add new tasks to `/Taskfile-go.yml`

### Core Development Tools
4. **Always use go modules** - never use GOPATH or vendor manually
5. **Run tests with -race** - concurrency bugs are hard to find
6. **Use golangci-lint** - comprehensive linting before commits
7. **Generate wire code** - commit wire_gen.go to version control
8. **Document APIs with swag** - keep Swagger docs in sync with code
9. **Check vulnerabilities** - run govulncheck regularly

### Environment & Deployment Tools
10. **Use Devbox for development** - Eliminates "works on my machine" issues
11. **Use NuShell for scripts** - Cross-platform compatibility
12. **Use Podman for containers** - Organizational standard per PRD-000 Decision D2
13. **Pin dependencies** - Use go.sum for reproducible builds
14. **Multi-stage Containerfiles** - Separate builder and runtime stages

---

**Back to [Core Orchestrator](./CLAUDE-core.md)** | **Back to [Main CLAUDE.md](/CLAUDE.md)**
