# CLAUDE.md - API Patterns & Versioning

**← [Back to Go Development Guide](./CLAUDE-core.md)**

## Overview

This document covers RESTful API design patterns, versioning strategies, API documentation, and best practices for building scalable HTTP APIs in Go.

**Framework Recommendation**: This guide uses **Gin** (stdlib-compatible) for examples. See main [CLAUDE.md](../CLAUDE.md) for framework selection guidance.

## API Design Principles

### RESTful Resource Design

```
GET    /api/v1/users              # List users
POST   /api/v1/users              # Create user
GET    /api/v1/users/:id          # Get user by ID
PUT    /api/v1/users/:id          # Update user (full)
PATCH  /api/v1/users/:id          # Update user (partial)
DELETE /api/v1/users/:id          # Delete user

GET    /api/v1/users/:id/posts    # List user's posts
POST   /api/v1/users/:id/posts    # Create post for user
```

### HTTP Handler Pattern (Gin)

```go
package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/go-playground/validator/v10"
)

type UserHandler struct {
	userUseCase application.UserUseCase
	validator   *validator.Validate
	logger      *logger.Logger
}

func NewUserHandler(
	userUseCase application.UserUseCase,
	validator *validator.Validate,
	logger *logger.Logger,
) *UserHandler {
	return &UserHandler{
		userUseCase: userUseCase,
		validator:   validator,
		logger:      logger,
	}
}

// Create godoc
// @Summary Create a new user
// @Tags users
// @Accept json
// @Produce json
// @Param user body CreateUserRequest true "User creation request"
// @Success 201 {object} UserResponse
// @Failure 400 {object} ErrorResponse
// @Failure 409 {object} ErrorResponse
// @Router /api/v1/users [post]
func (h *UserHandler) Create(c *gin.Context) {
	var req CreateUserRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "Bad Request",
			Message: "Invalid request body",
		})
		return
	}

	if err := h.validator.Struct(req); err != nil {
		h.respondValidationError(c, err)
		return
	}

	user, err := h.userUseCase.Create(c.Request.Context(), req.ToDTO())
	if err != nil {
		h.handleError(c, err)
		return
	}

	c.JSON(http.StatusCreated, user)
}

// GetByID godoc
// @Summary Get user by ID
// @Tags users
// @Produce json
// @Param id path string true "User ID"
// @Success 200 {object} UserResponse
// @Failure 404 {object} ErrorResponse
// @Router /api/v1/users/{id} [get]
func (h *UserHandler) GetByID(c *gin.Context) {
	id := c.Param("id")

	user, err := h.userUseCase.GetByID(c.Request.Context(), id)
	if err != nil {
		h.handleError(c, err)
		return
	}

	c.JSON(http.StatusOK, user)
}

// List godoc
// @Summary List users with pagination
// @Tags users
// @Produce json
// @Param page query int false "Page number" default(1)
// @Param limit query int false "Items per page" default(10)
// @Success 200 {object} UserListResponse
// @Router /api/v1/users [get]
func (h *UserHandler) List(c *gin.Context) {
	filter := ParseListFilter(c.Request.URL.Query())

	result, err := h.userUseCase.List(c.Request.Context(), filter)
	if err != nil {
		h.handleError(c, err)
		return
	}

	c.JSON(http.StatusOK, result)
}

func (h *UserHandler) handleError(c *gin.Context, err error) {
	switch {
	case errors.Is(err, domain.ErrUserNotFound):
		c.JSON(http.StatusNotFound, ErrorResponse{
			Error:   "Not Found",
			Message: err.Error(),
		})
	case errors.Is(err, domain.ErrUserAlreadyExists):
		c.JSON(http.StatusConflict, ErrorResponse{
			Error:   "Conflict",
			Message: err.Error(),
		})
	case errors.Is(err, domain.ErrInvalidInput):
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "Bad Request",
			Message: err.Error(),
		})
	default:
		h.logger.Errorw("Internal server error", "error", err)
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "Internal Server Error",
			Message: "An unexpected error occurred",
		})
	}
}

func (h *UserHandler) respondValidationError(c *gin.Context, err error) {
	if validationErrs, ok := err.(validator.ValidationErrors); ok {
		errors := make([]string, 0, len(validationErrs))
		for _, e := range validationErrs {
			errors = append(errors, fmt.Sprintf("%s: %s", e.Field(), e.Tag()))
		}
		c.JSON(http.StatusBadRequest, ValidationErrorResponse{
			Error:   "Validation Failed",
			Message: "Input validation failed",
			Errors:  errors,
		})
		return
	}
	c.JSON(http.StatusBadRequest, ErrorResponse{
		Error:   "Bad Request",
		Message: err.Error(),
	})
}
```

## Request/Response DTOs

### Request DTOs

```go
package handlers

import (
	"time"
)

type CreateUserRequest struct {
	Email    string `json:"email" validate:"required,email"`
	Username string `json:"username" validate:"required,min=3,max=50"`
	Password string `json:"password" validate:"required,min=8"`
}

func (r CreateUserRequest) ToDTO() *application.CreateUserDTO {
	return &application.CreateUserDTO{
		Email:    r.Email,
		Username: r.Username,
		Password: r.Password,
	}
}

type UpdateUserRequest struct {
	Email    *string `json:"email,omitempty" validate:"omitempty,email"`
	Username *string `json:"username,omitempty" validate:"omitempty,min=3,max=50"`
}

type ListUsersQuery struct {
	Page     int    `json:"page" validate:"omitempty,min=1"`
	PageSize int    `json:"page_size" validate:"omitempty,min=1,max=100"`
	SortBy   string `json:"sort_by" validate:"omitempty,oneof=created_at email username"`
	SortDir  string `json:"sort_dir" validate:"omitempty,oneof=asc desc"`
}
```

### Response DTOs

```go
type UserResponse struct {
	ID        string    `json:"id"`
	Email     string    `json:"email"`
	Username  string    `json:"username"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

type PaginatedResponse struct {
	Items      interface{} `json:"items"`
	Total      int64       `json:"total"`
	Page       int         `json:"page"`
	PageSize   int         `json:"page_size"`
	TotalPages int         `json:"total_pages"`
}

type ErrorResponse struct {
	Error   string            `json:"error"`
	Message string            `json:"message"`
	Details map[string]string `json:"details,omitempty"`
}
```

## API Versioning Strategies

### 1. URL Path Versioning (Recommended)

```go
package main

import (
	"github.com/gorilla/mux"
)

func SetupRoutes() *mux.Router {
	r := mux.NewRouter()

	v1 := r.PathPrefix("/api/v1").Subrouter()
	registerV1Routes(v1)

	v2 := r.PathPrefix("/api/v2").Subrouter()
	registerV2Routes(v2)

	return r
}

func registerV1Routes(r *mux.Router) {
	r.HandleFunc("/users", userHandlerV1.List).Methods("GET")
	r.HandleFunc("/users", userHandlerV1.Create).Methods("POST")
	r.HandleFunc("/users/{id}", userHandlerV1.GetByID).Methods("GET")
	r.HandleFunc("/users/{id}", userHandlerV1.Update).Methods("PUT")
	r.HandleFunc("/users/{id}", userHandlerV1.Delete).Methods("DELETE")
}

func registerV2Routes(r *mux.Router) {
	r.HandleFunc("/users", userHandlerV2.List).Methods("GET")
	r.HandleFunc("/users", userHandlerV2.Create).Methods("POST")
	r.HandleFunc("/users/{id}", userHandlerV2.GetByID).Methods("GET")
}
```

### 2. Header Versioning

```go
type VersionMiddleware struct {
	v1Handler http.Handler
	v2Handler http.Handler
}

func (vm *VersionMiddleware) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	version := r.Header.Get("API-Version")

	switch version {
	case "v2", "2":
		vm.v2Handler.ServeHTTP(w, r)
	default:
		vm.v1Handler.ServeHTTP(w, r)
	}
}
```

### 3. Content Negotiation (Accept Header)

```go
func (h *UserHandler) GetByID(w http.ResponseWriter, r *http.Request) {
	acceptHeader := r.Header.Get("Accept")

	user, err := h.userUseCase.GetByID(r.Context(), id)
	if err != nil {
		h.handleError(w, err)
		return
	}

	switch {
	case strings.Contains(acceptHeader, "application/vnd.myapp.v2+json"):
		h.respondJSON(w, http.StatusOK, h.toV2Response(user))
	default:
		h.respondJSON(w, http.StatusOK, h.toV1Response(user))
	}
}
```

### Deprecation Strategy

```go
func DeprecationMiddleware(version string, sunsetDate time.Time) mux.MiddlewareFunc {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("Deprecation", "true")
			w.Header().Set("Sunset", sunsetDate.Format(time.RFC1123))
			w.Header().Set("Link", fmt.Sprintf(`</api/%s/migration-guide>; rel="deprecation"`, version))

			next.ServeHTTP(w, r)
		})
	}
}

v1Router.Use(DeprecationMiddleware("v1", time.Date(2024, 12, 31, 0, 0, 0, 0, time.UTC)))
```

## API Documentation with Swagger

### Setup Swagger

```go
package main

import (
	"github.com/swaggo/http-swagger"
	_ "yourapp/docs"
)

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
	r := mux.NewRouter()

	r.PathPrefix("/swagger/").Handler(httpSwagger.WrapHandler)

	http.ListenAndServe(":8080", r)
}
```

### Swagger Annotations

```go
// CreateUser godoc
// @Summary Create a new user
// @Description Create a new user with the provided details
// @Tags users
// @Accept json
// @Produce json
// @Param user body CreateUserRequest true "User details"
// @Success 201 {object} UserResponse
// @Failure 400 {object} ErrorResponse
// @Failure 409 {object} ErrorResponse
// @Failure 500 {object} ErrorResponse
// @Router /users [post]
func (h *UserHandler) Create(w http.ResponseWriter, r *http.Request) {
}

// GetUser godoc
// @Summary Get user by ID
// @Description Get detailed information about a user
// @Tags users
// @Accept json
// @Produce json
// @Param id path string true "User ID"
// @Success 200 {object} UserResponse
// @Failure 404 {object} ErrorResponse
// @Failure 500 {object} ErrorResponse
// @Security BearerAuth
// @Router /users/{id} [get]
func (h *UserHandler) GetByID(w http.ResponseWriter, r *http.Request) {
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
func (h *UserHandler) List(w http.ResponseWriter, r *http.Request) {
}
```

### Generate Swagger Docs

```bash
# Install swag
go install github.com/swaggo/swag/cmd/swag@latest

# Generate docs
swag init -g cmd/api/main.go

# View docs at http://localhost:8080/swagger/index.html
```

## API Key Management

### API Key Model

```go
package domain

import (
	"crypto/rand"
	"encoding/base64"
	"time"
)

type APIKey struct {
	ID        string
	UserID    string
	Key       string
	Name      string
	Scopes    []string
	ExpiresAt *time.Time
	CreatedAt time.Time
	LastUsed  *time.Time
}

func GenerateAPIKey() (string, error) {
	b := make([]byte, 32)
	if _, err := rand.Read(b); err != nil {
		return "", err
	}
	return base64.URLEncoding.EncodeToString(b), nil
}
```

### API Key Middleware

```go
type APIKeyMiddleware struct {
	apiKeyService application.APIKeyService
}

func (m *APIKeyMiddleware) Authenticate(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		apiKey := r.Header.Get("X-API-Key")
		if apiKey == "" {
			http.Error(w, "API key required", http.StatusUnauthorized)
			return
		}

		key, err := m.apiKeyService.Validate(r.Context(), apiKey)
		if err != nil {
			http.Error(w, "Invalid API key", http.StatusUnauthorized)
			return
		}

		if key.ExpiresAt != nil && key.ExpiresAt.Before(time.Now()) {
			http.Error(w, "API key expired", http.StatusUnauthorized)
			return
		}

		ctx := context.WithValue(r.Context(), "api_key", key)
		ctx = context.WithValue(ctx, "user_id", key.UserID)

		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

func (m *APIKeyMiddleware) RequireScope(scope string) mux.MiddlewareFunc {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			key := r.Context().Value("api_key").(*domain.APIKey)

			if !contains(key.Scopes, scope) {
				http.Error(w, "Insufficient permissions", http.StatusForbidden)
				return
			}

			next.ServeHTTP(w, r)
		})
	}
}
```

### API Key Repository

```go
package repositories

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
)

type APIKeyRepository interface {
	Create(ctx context.Context, key *domain.APIKey) error
	FindByKey(ctx context.Context, key string) (*domain.APIKey, error)
	UpdateLastUsed(ctx context.Context, id string) error
	Revoke(ctx context.Context, id string) error
}

type postgresAPIKeyRepository struct {
	db *sql.DB
}

func (r *postgresAPIKeyRepository) Create(ctx context.Context, key *domain.APIKey) error {
	hashedKey := hashAPIKey(key.Key)

	query := `
		INSERT INTO api_keys (id, user_id, key_hash, name, scopes, expires_at, created_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
	`

	_, err := r.db.ExecContext(
		ctx,
		query,
		key.ID,
		key.UserID,
		hashedKey,
		key.Name,
		pq.Array(key.Scopes),
		key.ExpiresAt,
		key.CreatedAt,
	)

	return err
}

func (r *postgresAPIKeyRepository) FindByKey(ctx context.Context, key string) (*domain.APIKey, error) {
	hashedKey := hashAPIKey(key)

	query := `
		SELECT id, user_id, name, scopes, expires_at, created_at, last_used
		FROM api_keys
		WHERE key_hash = $1 AND revoked_at IS NULL
	`

	apiKey := &domain.APIKey{}
	err := r.db.QueryRowContext(ctx, query, hashedKey).Scan(
		&apiKey.ID,
		&apiKey.UserID,
		&apiKey.Name,
		pq.Array(&apiKey.Scopes),
		&apiKey.ExpiresAt,
		&apiKey.CreatedAt,
		&apiKey.LastUsed,
	)

	if err == sql.ErrNoRows {
		return nil, domain.ErrAPIKeyNotFound
	}

	return apiKey, err
}

func hashAPIKey(key string) string {
	hash := sha256.Sum256([]byte(key))
	return hex.EncodeToString(hash[:])
}
```

## Rate Limiting per API Key

```go
package middleware

import (
	"net/http"
	"sync"
	"time"

	"golang.org/x/time/rate"
)

type APIKeyRateLimiter struct {
	limiters map[string]*rate.Limiter
	mu       sync.RWMutex
	rps      rate.Limit
	burst    int
}

func NewAPIKeyRateLimiter(rps rate.Limit, burst int) *APIKeyRateLimiter {
	return &APIKeyRateLimiter{
		limiters: make(map[string]*rate.Limiter),
		rps:      rps,
		burst:    burst,
	}
}

func (rl *APIKeyRateLimiter) getLimiter(apiKeyID string) *rate.Limiter {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	limiter, exists := rl.limiters[apiKeyID]
	if !exists {
		limiter = rate.NewLimiter(rl.rps, rl.burst)
		rl.limiters[apiKeyID] = limiter
	}

	return limiter
}

func (rl *APIKeyRateLimiter) Middleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		apiKey := r.Context().Value("api_key").(*domain.APIKey)

		limiter := rl.getLimiter(apiKey.ID)

		if !limiter.Allow() {
			w.Header().Set("Retry-After", "60")
			http.Error(w, "Rate limit exceeded", http.StatusTooManyRequests)
			return
		}

		next.ServeHTTP(w, r)
	})
}
```

## Best Practices

### ✅ DO

- **Use URL versioning** for clear API version management
- **Provide deprecation notices** well in advance (6-12 months)
- **Document all endpoints** with Swagger/OpenAPI
- **Use proper HTTP status codes** for different scenarios
- **Implement pagination** for list endpoints
- **Use ETags** for cache validation
- **Support partial updates** with PATCH
- **Validate input** at the handler level
- **Use DTOs** to decouple API from domain models
- **Implement rate limiting** per API key
- **Hash API keys** before storing in database
- **Support API key scopes** for fine-grained permissions
- **Log API key usage** for audit trails
- **Provide API key rotation** mechanism

### ❌ DON'T

- **Don't break backward compatibility** without versioning
- **Don't expose internal errors** to clients
- **Don't return database entities** directly
- **Don't forget to validate** query parameters
- **Don't use GET** for operations that modify data
- **Don't hardcode** version numbers throughout codebase
- **Don't store API keys** in plain text
- **Don't allow unlimited** API requests
- **Don't reuse API keys** across users
- **Don't skip audit logging** for API key operations

## Versioning Migration Guide

### Breaking vs Non-Breaking Changes

**Non-Breaking (Safe in same version):**
- Adding new endpoints
- Adding optional fields to requests
- Adding new fields to responses
- Adding new query parameters (optional)
- Relaxing validation rules

**Breaking (Requires new version):**
- Removing or renaming endpoints
- Removing fields from responses
- Changing field types
- Making optional fields required
- Changing authentication methods
- Modifying URL structure

### Migration Example: V1 to V2

```go
type UserHandlerV1 struct {
	userUseCase application.UserUseCase
}

func (h *UserHandlerV1) toV1Response(user *domain.User) *UserResponseV1 {
	return &UserResponseV1{
		ID:       user.ID,
		Email:    user.Email,
		Username: user.Username,
	}
}

type UserHandlerV2 struct {
	userUseCase application.UserUseCase
}

func (h *UserHandlerV2) toV2Response(user *domain.User) *UserResponseV2 {
	return &UserResponseV2{
		ID:    user.ID,
		Email: user.Email,
		Profile: ProfileV2{
			Username:  user.Username,
			FirstName: user.FirstName,
			LastName:  user.LastName,
		},
	}
}
```

## Related Files

- **[CLAUDE-validation.md](./CLAUDE-validation.md)** - Input validation, request/response DTOs, sanitization patterns
- **[CLAUDE-error-handling.md](./CLAUDE-error-handling.md)** - HTTP error responses, status code mapping, error wrapping
- **[CLAUDE-security.md](./CLAUDE-security.md)** - API authentication (JWT, OAuth2), rate limiting, CSRF protection
- **[CLAUDE-testing.md](./CLAUDE-testing.md)** - API endpoint testing, integration tests, table-driven test patterns
- **[CLAUDE-database.md](./CLAUDE-database.md)** - Repository pattern, database integration in handlers
- **[CLAUDE-tooling.md](./CLAUDE-tooling.md)** - Swagger generation with swaggo, API documentation workflow

---

## External References

- [REST API Tutorial](https://restfulapi.net/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [API Versioning Best Practices](https://www.baeldung.com/rest-versioning)
- [gorilla/mux Documentation](https://github.com/gorilla/mux)
- [swaggo Documentation](https://github.com/swaggo/swag)
