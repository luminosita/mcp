# Clean Architecture Patterns

This file provides detailed Clean Architecture implementation patterns with comprehensive code examples.

**← [Back to Go Development Guide](./CLAUDE-core.md)**

## Clean Architecture Layers

### Domain Layer (Innermost - No Dependencies)

**Purpose**: Contains business entities, domain logic, and repository interfaces.

```go
// internal/domain/entities/user.go
package entities

import (
    "errors"
    "time"
)

// User represents a user entity with encapsulated business logic
type User struct {
    id        UserID
    email     EmailAddress  // Value object
    name      string
    active    bool
    createdAt time.Time
}

// Constructor ensures valid state
func NewUser(email EmailAddress, name string) (*User, error) {
    if name == "" {
        return nil, ValidationError{Field: "name", Message: "required"}
    }

    return &User{
        id:        NewUserID(),
        email:     email,
        name:      name,
        active:    true,
        createdAt: time.Now(),
    }, nil
}

// Business logic as methods
func (u *User) Deactivate() error {
    if !u.active {
        return errors.New("user already inactive")
    }
    u.active = false
    return nil
}

func (u *User) Activate() error {
    if u.active {
        return errors.New("user already active")
    }
    u.active = true
    return nil
}

// Getters for accessing private fields
func (u *User) ID() UserID           { return u.id }
func (u *User) Email() EmailAddress  { return u.email }
func (u *User) Name() string         { return u.name }
func (u *User) IsActive() bool       { return u.active }
func (u *User) CreatedAt() time.Time { return u.createdAt }
```

### Value Objects

```go
// internal/domain/entities/email.go
package entities

import (
    "errors"
    "regexp"
    "strings"
)

// EmailAddress is a value object ensuring valid email format
type EmailAddress struct {
    value string
}

var emailRegex = regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)

func NewEmailAddress(email string) (EmailAddress, error) {
    normalized := strings.ToLower(strings.TrimSpace(email))

    if !emailRegex.MatchString(normalized) {
        return EmailAddress{}, errors.New("invalid email format")
    }

    return EmailAddress{value: normalized}, nil
}

func (e EmailAddress) String() string {
    return e.value
}

// UserID is a strongly-typed identifier
type UserID string

func NewUserID() UserID {
    // Generate unique ID (UUID, ULID, etc.)
    return UserID("usr_" + generateUniqueID())
}
```

### Repository Interfaces (Defined in Domain)

```go
// internal/domain/repositories/user_repository.go
package repositories

import (
    "context"
    "myapp/internal/domain/entities"
)

// UserRepository defines data access operations for User entity
// Interface is defined in domain but implemented in infrastructure
type UserRepository interface {
    Save(ctx context.Context, user *entities.User) error
    FindByID(ctx context.Context, id entities.UserID) (*entities.User, error)
    FindByEmail(ctx context.Context, email entities.EmailAddress) (*entities.User, error)
    Delete(ctx context.Context, id entities.UserID) error
}

// Smaller, focused interfaces following ISP
type UserFinder interface {
    FindByID(ctx context.Context, id entities.UserID) (*entities.User, error)
}

type UserPersister interface {
    Save(ctx context.Context, user *entities.User) error
}
```

### Application Layer (Use Cases)

```go
// internal/application/usecases/create_user.go
package usecases

import (
    "context"
    "fmt"
    "myapp/internal/domain/entities"
    "myapp/internal/domain/repositories"
)

// CreateUserCommand is a DTO for user creation
type CreateUserCommand struct {
    Email string
    Name  string
}

// CreateUserUseCase orchestrates user creation
type CreateUserUseCase struct {
    userRepo repositories.UserRepository
    // Could also inject domain services here
}

func NewCreateUserUseCase(repo repositories.UserRepository) *CreateUserUseCase {
    return &CreateUserUseCase{
        userRepo: repo,
    }
}

func (uc *CreateUserUseCase) Execute(ctx context.Context, cmd CreateUserCommand) (*entities.User, error) {
    // Validate input
    email, err := entities.NewEmailAddress(cmd.Email)
    if err != nil {
        return nil, fmt.Errorf("invalid email: %w", err)
    }

    // Check if user already exists
    existing, err := uc.userRepo.FindByEmail(ctx, email)
    if err == nil && existing != nil {
        return nil, fmt.Errorf("user with email %s already exists", email)
    }

    // Create domain entity
    user, err := entities.NewUser(email, cmd.Name)
    if err != nil {
        return nil, fmt.Errorf("failed to create user: %w", err)
    }

    // Persist
    if err := uc.userRepo.Save(ctx, user); err != nil {
        return nil, fmt.Errorf("failed to save user: %w", err)
    }

    return user, nil
}
```

### Infrastructure Layer (Repository Implementation)

```go
// internal/infrastructure/persistence/postgres/user_repository.go
package postgres

import (
    "context"
    "database/sql"
    "fmt"
    "myapp/internal/domain/entities"
    "myapp/internal/domain/repositories"
)

// UserRepository implements repositories.UserRepository for PostgreSQL
type UserRepository struct {
    db *sql.DB
}

func NewUserRepository(db *sql.DB) repositories.UserRepository {
    return &UserRepository{db: db}
}

func (r *UserRepository) Save(ctx context.Context, user *entities.User) error {
    query := `
        INSERT INTO users (id, email, name, active, created_at)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (id) DO UPDATE SET
            email = EXCLUDED.email,
            name = EXCLUDED.name,
            active = EXCLUDED.active
    `

    _, err := r.db.ExecContext(ctx, query,
        user.ID(),
        user.Email().String(),
        user.Name(),
        user.IsActive(),
        user.CreatedAt(),
    )

    if err != nil {
        return fmt.Errorf("save user: %w", err)
    }

    return nil
}

func (r *UserRepository) FindByID(ctx context.Context, id entities.UserID) (*entities.User, error) {
    query := `
        SELECT id, email, name, active, created_at
        FROM users
        WHERE id = $1
    `

    var (
        userID    string
        email     string
        name      string
        active    bool
        createdAt time.Time
    )

    err := r.db.QueryRowContext(ctx, query, id).Scan(
        &userID, &email, &name, &active, &createdAt,
    )

    if err == sql.ErrNoRows {
        return nil, fmt.Errorf("user not found: %s", id)
    }
    if err != nil {
        return nil, fmt.Errorf("find user: %w", err)
    }

    emailAddr, _ := entities.NewEmailAddress(email)

    // Reconstruct entity (would need to expose constructor or use reflection)
    // In practice, you might need a factory method in domain
    user := entities.ReconstructUser(
        entities.UserID(userID),
        emailAddr,
        name,
        active,
        createdAt,
    )

    return user, nil
}

func (r *UserRepository) FindByEmail(ctx context.Context, email entities.EmailAddress) (*entities.User, error) {
    // Similar implementation
    return nil, nil
}

func (r *UserRepository) Delete(ctx context.Context, id entities.UserID) error {
    query := `DELETE FROM users WHERE id = $1`

    result, err := r.db.ExecContext(ctx, query, id)
    if err != nil {
        return fmt.Errorf("delete user: %w", err)
    }

    rows, _ := result.RowsAffected()
    if rows == 0 {
        return fmt.Errorf("user not found: %s", id)
    }

    return nil
}
```

### Interface Layer (HTTP Handlers)

```go
// internal/interfaces/http/user_handler.go
package http

import (
    "encoding/json"
    "net/http"
    "myapp/internal/application/usecases"
)

type UserHandler struct {
    createUserUC *usecases.CreateUserUseCase
}

func NewUserHandler(createUC *usecases.CreateUserUseCase) *UserHandler {
    return &UserHandler{
        createUserUC: createUC,
    }
}

type CreateUserRequest struct {
    Email string `json:"email" validate:"required,email"`
    Name  string `json:"name" validate:"required,min=1,max=100"`
}

type UserResponse struct {
    ID     string `json:"id"`
    Email  string `json:"email"`
    Name   string `json:"name"`
    Active bool   `json:"active"`
}

func (h *UserHandler) CreateUser(w http.ResponseWriter, r *http.Request) {
    var req CreateUserRequest

    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        h.respondError(w, "invalid JSON", http.StatusBadRequest)
        return
    }

    // Execute use case
    cmd := usecases.CreateUserCommand{
        Email: req.Email,
        Name:  req.Name,
    }

    user, err := h.createUserUC.Execute(r.Context(), cmd)
    if err != nil {
        h.respondError(w, err.Error(), http.StatusBadRequest)
        return
    }

    // Map to response DTO
    resp := UserResponse{
        ID:     string(user.ID()),
        Email:  user.Email().String(),
        Name:   user.Name(),
        Active: user.IsActive(),
    }

    h.respondJSON(w, resp, http.StatusCreated)
}

func (h *UserHandler) respondJSON(w http.ResponseWriter, data interface{}, status int) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(data)
}

func (h *UserHandler) respondError(w http.ResponseWriter, message string, status int) {
    h.respondJSON(w, map[string]string{"error": message}, status)
}
```

## Dependency Injection Wiring

### Manual Wiring in main.go

```go
// cmd/api/main.go
package main

import (
    "database/sql"
    "log"
    "net/http"

    "myapp/internal/application/usecases"
    "myapp/internal/infrastructure/persistence/postgres"
    httphandlers "myapp/internal/interfaces/http"

    _ "github.com/lib/pq"
)

func main() {
    // Infrastructure setup
    db, err := sql.Open("postgres", "postgres://user:pass@localhost/dbname?sslmode=disable")
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    // Repository implementations (Infrastructure layer)
    userRepo := postgres.NewUserRepository(db)

    // Use cases (Application layer)
    createUserUC := usecases.NewCreateUserUseCase(userRepo)

    // Handlers (Interface layer)
    userHandler := httphandlers.NewUserHandler(createUserUC)

    // Route setup
    mux := http.NewServeMux()
    mux.HandleFunc("/users", userHandler.CreateUser)

    // Start server
    log.Println("Server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", mux))
}
```

### Google Wire Setup

```go
// internal/di/wire.go
//go:build wireinject

package di

import (
    "database/sql"

    "github.com/google/wire"

    "myapp/internal/application/usecases"
    "myapp/internal/infrastructure/persistence/postgres"
    httphandlers "myapp/internal/interfaces/http"
)

// Repository providers
var repositorySet = wire.NewSet(
    postgres.NewUserRepository,
    wire.Bind(new(repositories.UserRepository), new(*postgres.UserRepository)),
)

// Use case providers
var usecaseSet = wire.NewSet(
    usecases.NewCreateUserUseCase,
)

// Handler providers
var handlerSet = wire.NewSet(
    httphandlers.NewUserHandler,
)

// InitializeUserHandler wires up all dependencies for UserHandler
func InitializeUserHandler(db *sql.DB) (*httphandlers.UserHandler, error) {
    wire.Build(
        repositorySet,
        usecaseSet,
        handlerSet,
    )
    return nil, nil
}
```

```bash
# Generate wire code
cd internal/di && wire
```

```go
// cmd/api/main.go (with Wire)
package main

import (
    "database/sql"
    "log"
    "net/http"

    "myapp/internal/di"

    _ "github.com/lib/pq"
)

func main() {
    db, err := sql.Open("postgres", "postgres://user:pass@localhost/dbname?sslmode=disable")
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    // Wire handles all dependency injection
    userHandler, err := di.InitializeUserHandler(db)
    if err != nil {
        log.Fatal(err)
    }

    mux := http.NewServeMux()
    mux.HandleFunc("/users", userHandler.CreateUser)

    log.Println("Server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", mux))
}
```

## Dependency Rule Visualization

```
┌─────────────────────────────────────────┐
│         Domain Layer (Core)             │
│  ┌─────────────┐    ┌─────────────┐     │
│  │  Entities   │    │ Repository  │     │
│  │             │    │ Interfaces  │     │
│  └─────────────┘    └─────────────┘     │
│         ▲                   ▲            │
└─────────┼───────────────────┼────────────┘
          │                   │
┌─────────┼───────────────────┼────────────┐
│         │   Application Layer            │
│  ┌──────┴──────┐    ┌──────┴──────┐      │
│  │  Use Cases  │    │  Commands   │      │
│  │             │    │  Queries    │      │
│  └─────────────┘    └─────────────┘      │
│         ▲                   ▲            │
└─────────┼───────────────────┼────────────┘
          │                   │
┌─────────┼───────────────────┼────────────┐
│    Infrastructure & Interface Layers     │
│  ┌──────┴──────┐    ┌──────┴──────┐      │
│  │   Postgres  │    │    HTTP     │      │
│  │   (Impl)    │    │  Handlers   │      │
│  └─────────────┘    └─────────────┘      │
└──────────────────────────────────────────┘

Dependencies flow INWARD (↑)
Outer layers depend on inner layers
Inner layers are independent
```

## Common Patterns

### Functional Options for Optional Dependencies

```go
type UserService struct {
    repo    repositories.UserRepository
    logger  Logger
    cache   Cache
    timeout time.Duration
}

type Option func(*UserService)

func WithCache(cache Cache) Option {
    return func(s *UserService) {
        s.cache = cache
    }
}

func WithLogger(logger Logger) Option {
    return func(s *UserService) {
        s.logger = logger
    }
}

func WithTimeout(timeout time.Duration) Option {
    return func(s *UserService) {
        s.timeout = timeout
    }
}

func NewUserService(repo repositories.UserRepository, opts ...Option) *UserService {
    s := &UserService{
        repo:    repo,
        timeout: 30 * time.Second, // default
    }

    for _, opt := range opts {
        opt(s)
    }

    return s
}

// Usage
service := NewUserService(
    repo,
    WithCache(redisCache),
    WithLogger(logger),
    WithTimeout(60*time.Second),
)
```

### Domain Events

```go
// internal/domain/events/user_events.go
package events

import "myapp/internal/domain/entities"

type UserCreatedEvent struct {
    UserID entities.UserID
    Email  entities.EmailAddress
}

type UserDeactivatedEvent struct {
    UserID entities.UserID
}

// Event publisher interface (defined in domain)
type EventPublisher interface {
    Publish(event interface{}) error
}
```

### CQRS Pattern (Command Query Separation)

```go
// internal/application/queries/user_queries.go
package queries

import (
    "context"
    "myapp/internal/domain/entities"
)

// Read model - optimized for queries
type UserReadModel struct {
    ID     string
    Email  string
    Name   string
    Active bool
}

type UserQueryService interface {
    GetUserByID(ctx context.Context, id string) (*UserReadModel, error)
    ListActiveUsers(ctx context.Context, limit, offset int) ([]UserReadModel, error)
}

// Implementation uses read-optimized queries, possibly different DB or cache
```

## Best Practices

### ✅ DO
- Keep domain layer pure with no external dependencies
- Define interfaces where they're used (consumer defines interface)
- Use dependency injection for all external dependencies
- Return domain entities from use cases
- Map domain entities to DTOs at the interface layer
- Use value objects for domain concepts (Email, UserID, Money, etc.)
- Keep use cases focused on single responsibility
- Test each layer independently with mocks

### ❌ DON'T
- Don't import infrastructure in domain layer
- Don't implement repositories in domain layer
- Don't let domain entities know about persistence
- Don't pass HTTP requests/responses to use cases
- Don't put business logic in handlers or infrastructure
- Don't create circular dependencies between layers
- Don't skip the application layer (handlers shouldn't call repos directly)
