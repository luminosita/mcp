# Go Microservice Architecture Research Report

**Document Version:** 1.0 (Starter - Sections 1-4)
**Research Date:** 2025-11-01
**Researcher:** Context Engineering PoC Team
**Target Go Version:** 1.21+

## Executive Summary

This research report establishes architectural standards for scalable Go microservice implementations, focusing on production-ready patterns that leverage Go's strengths: interfaces, goroutines, channels, and a powerful standard library. Based on analysis of official documentation, established open-source projects, and community best practices, this report provides actionable guidance across critical architectural areas.

**Key Findings:**
1. **Configuration Management:** Environment variables with struct tags (envconfig) provide the simplest twelve-factor compliant approach, while Viper offers flexibility for complex scenarios requiring multiple config sources[^1]
2. **Structured Logging:** slog (Go 1.21+) as the standard library option with structured logging, or zerolog/zap for high-performance scenarios requiring allocation-free logging[^2]
3. **Caching:** Redis with go-redis/redis client using connection pooling provides production-grade distributed caching with goroutine-safe operations[^3]
4. **Data Access:** database/sql with sqlx for enhanced scanning, or GORM for rapid development with ORM convenience - both patterns require repository abstraction for Clean Architecture compliance[^4]

**Critical Architectural Decision:** Embrace Go's interface-based design for dependency inversion, leverage standard library when sufficient (slog, database/sql), and add external libraries only when they provide clear value (redis client, migration tools).

---

## 1. Configuration Management

### 1.1 Recommended Approach: Environment Variables with envconfig

For microservices deployed in containerized environments, reading configuration from environment variables using struct tags provides the simplest twelve-factor app compliant approach[^1][^5]. The `kelseyhightower/envconfig` library enables declarative configuration mapping with minimal boilerplate.

**Core Benefits:**
- **Twelve-Factor Compliance:** Strict separation of config from code, environment-specific without code changes[^5]
- **Type Safety:** Struct tags provide compile-time type checking and automatic conversion
- **Simplicity:** No file parsing, no dependencies on filesystem layout
- **Container-Native:** Perfect for Kubernetes, Docker, cloud platforms where env vars are first-class

### 1.2 Implementation Example

```go
// File: internal/config/config.go
package config

import (
	"fmt"
	"time"

	"github.com/kelseyhightower/envconfig"
)

// Config holds all application configuration loaded from environment variables.
// Struct tags define environment variable names and default values.
type Config struct {
	// Application metadata
	AppName string `envconfig:"APP_NAME" default:"go-microservice"`
	Debug   bool   `envconfig:"DEBUG" default:"false"`

	// Server configuration
	ServerPort    int           `envconfig:"SERVER_PORT" default:"8080"`
	ReadTimeout   time.Duration `envconfig:"READ_TIMEOUT" default:"10s"`
	WriteTimeout  time.Duration `envconfig:"WRITE_TIMEOUT" default:"10s"`
	IdleTimeout   time.Duration `envconfig:"IDLE_TIMEOUT" default:"60s"`

	// Database configuration
	DatabaseURL      string        `envconfig:"DATABASE_URL" required:"true"`
	DBMaxOpenConns   int           `envconfig:"DB_MAX_OPEN_CONNS" default:"25"`
	DBMaxIdleConns   int           `envconfig:"DB_MAX_IDLE_CONNS" default:"5"`
	DBConnMaxLifetime time.Duration `envconfig:"DB_CONN_MAX_LIFETIME" default:"5m"`

	// Redis configuration
	RedisAddr     string        `envconfig:"REDIS_ADDR" required:"true"`
	RedisPassword string        `envconfig:"REDIS_PASSWORD"`
	RedisDB       int           `envconfig:"REDIS_DB" default:"0"`
	RedisPoolSize int           `envconfig:"REDIS_POOL_SIZE" default:"10"`

	// Security
	JWTSecret string `envconfig:"JWT_SECRET" required:"true"`
}

// Load reads configuration from environment variables and returns Config.
// Returns error if required variables missing or type conversion fails.
func Load() (*Config, error) {
	var cfg Config

	// Process environment variables into Config struct
	if err := envconfig.Process("", &cfg); err != nil {
		return nil, fmt.Errorf("failed to process config: %w", err)
	}

	return &cfg, nil
}

// MustLoad loads configuration or panics if it fails.
// Use during application initialization when config is required.
func MustLoad() *Config {
	cfg, err := Load()
	if err != nil {
		panic(fmt.Sprintf("failed to load configuration: %v", err))
	}
	return cfg
}
```

**Usage in main.go:**

```go
// File: cmd/server/main.go
package main

import (
	"log"
	"github.com/example/project/internal/config"
)

func main() {
	// Load configuration from environment variables
	cfg := config.MustLoad()

	log.Printf("Starting %s on port %d", cfg.AppName, cfg.ServerPort)

	// Initialize application with config
	// app := NewApplication(cfg)
	// app.Run()
}
```

### 1.2.1 Configuration Initialization Patterns

#### Pattern 1: Global Config with Init Function (Recommended)

Load configuration once at application startup in `main()`, store in package-level variable, access throughout application[^5][^18]. This pattern provides simplicity while maintaining testability through explicit initialization.

```go
// File: internal/config/config.go
package config

import (
	"fmt"
	"sync"
	"time"

	"github.com/kelseyhightower/envconfig"
)

// Config holds all application configuration loaded from environment variables.
type Config struct {
	// Application metadata
	AppName string `envconfig:"APP_NAME" default:"go-microservice"`
	Debug   bool   `envconfig:"DEBUG" default:"false"`

	// Server configuration
	ServerPort    int           `envconfig:"SERVER_PORT" default:"8080"`
	ReadTimeout   time.Duration `envconfig:"READ_TIMEOUT" default:"10s"`
	WriteTimeout  time.Duration `envconfig:"WRITE_TIMEOUT" default:"10s"`
	IdleTimeout   time.Duration `envconfig:"IDLE_TIMEOUT" default:"60s"`

	// Database configuration
	DatabaseURL      string        `envconfig:"DATABASE_URL" required:"true"`
	DBMaxOpenConns   int           `envconfig:"DB_MAX_OPEN_CONNS" default:"25"`
	DBMaxIdleConns   int           `envconfig:"DB_MAX_IDLE_CONNS" default:"5"`
	DBConnMaxLifetime time.Duration `envconfig:"DB_CONN_MAX_LIFETIME" default:"5m"`

	// Redis configuration
	RedisAddr     string        `envconfig:"REDIS_ADDR" required:"true"`
	RedisPassword string        `envconfig:"REDIS_PASSWORD"`
	RedisDB       int           `envconfig:"REDIS_DB" default:"0"`
	RedisPoolSize int           `envconfig:"REDIS_POOL_SIZE" default:"10"`

	// Security
	JWTSecret string `envconfig:"JWT_SECRET" required:"true"`
}

var (
	// Global configuration instance (package-level, not exported)
	globalConfig *Config
	configMu     sync.RWMutex
)

// Init initializes the global configuration from environment variables.
// Call this once during application startup in main() before accessing config.
// Returns error if required variables missing or type conversion fails.
func Init() error {
	configMu.Lock()
	defer configMu.Unlock()

	if globalConfig != nil {
		return fmt.Errorf("config already initialized")
	}

	var cfg Config
	if err := envconfig.Process("", &cfg); err != nil {
		return fmt.Errorf("failed to process config: %w", err)
	}

	globalConfig = &cfg
	return nil
}

// MustInit initializes configuration or panics if it fails.
// Use during application initialization when config is required.
func MustInit() {
	if err := Init(); err != nil {
		panic(fmt.Sprintf("failed to initialize configuration: %v", err))
	}
}

// Get returns the global configuration instance.
// Panics if configuration not initialized (fail-fast for misconfiguration).
func Get() *Config {
	configMu.RLock()
	defer configMu.RUnlock()

	if globalConfig == nil {
		panic("config not initialized - call config.Init() in main() before using")
	}

	return globalConfig
}

// Reset clears the global configuration (for testing only).
// NEVER call this in production code.
func Reset() {
	configMu.Lock()
	defer configMu.Unlock()
	globalConfig = nil
}
```

**Usage in application:**

```go
// File: cmd/server/main.go
package main

import (
	"log/slog"
	"github.com/example/project/internal/config"
	"github.com/example/project/internal/database"
	"github.com/example/project/internal/server"
)

func main() {
	// Step 1: Initialize configuration FIRST (before any code uses it)
	config.MustInit()
	cfg := config.Get()

	// Step 2: Initialize logger with config values
	initLogger(cfg.Debug)

	slog.Info("application starting",
		"app_name", cfg.AppName,
		"port", cfg.ServerPort,
		"debug", cfg.Debug,
	)

	// Step 3: Initialize database with config values
	db, err := database.NewPostgresDB(database.Config{
		URL:              cfg.DatabaseURL,
		MaxOpenConns:     cfg.DBMaxOpenConns,
		MaxIdleConns:     cfg.DBMaxIdleConns,
		ConnMaxLifetime:  cfg.DBConnMaxLifetime,
	})
	if err != nil {
		slog.Error("failed to connect to database", "error", err)
		panic(err)
	}
	defer db.Close()

	// Step 4: Start server (accesses config internally via config.Get())
	srv := server.New(db)
	if err := srv.Start(cfg.ServerPort); err != nil {
		slog.Error("server failed", "error", err)
	}
}
```

**Usage in service layers:**

```go
// File: internal/service/auth_service.go
package service

import (
	"context"
	"fmt"
	"time"

	"github.com/example/project/internal/config"
	"github.com/golang-jwt/jwt/v5"
)

type AuthService struct {
	repo UserRepository
}

func NewAuthService(repo UserRepository) *AuthService {
	return &AuthService{repo: repo}
}

// GenerateToken creates a JWT token using configuration.
func (s *AuthService) GenerateToken(ctx context.Context, userID int64) (string, error) {
	// Access global config (no need to pass as parameter)
	cfg := config.Get()

	claims := jwt.MapClaims{
		"user_id": userID,
		"exp":     time.Now().Add(24 * time.Hour).Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	signed, err := token.SignedString([]byte(cfg.JWTSecret))
	if err != nil {
		return "", fmt.Errorf("failed to sign token: %w", err)
	}

	return signed, nil
}
```

**Testing with global config:**

```go
// File: internal/service/auth_service_test.go
package service

import (
	"context"
	"os"
	"testing"

	"github.com/example/project/internal/config"
	"github.com/stretchr/testify/assert"
)

func TestAuthService_GenerateToken(t *testing.T) {
	// Setup: Initialize config for test environment
	os.Setenv("DATABASE_URL", "postgres://test")
	os.Setenv("REDIS_ADDR", "localhost:6379")
	os.Setenv("JWT_SECRET", "test-secret-key")

	// Reset config before test (ensures clean state)
	config.Reset()
	config.MustInit()

	// Cleanup after test
	defer config.Reset()

	// Test with real config
	mockRepo := &MockUserRepository{}
	service := NewAuthService(mockRepo)

	token, err := service.GenerateToken(context.Background(), 123)

	assert.NoError(t, err)
	assert.NotEmpty(t, token)
}
```

**Benefits:**
- ✅ **Simple API:** Single `Get()` call anywhere in codebase, no parameter passing
- ✅ **Type-Safe:** Compile-time guarantees on config field access
- ✅ **Goroutine-Safe:** `sync.RWMutex` protects concurrent access (though config read-only after init)
- ✅ **Fail-Fast:** Panics if config accessed before initialization (catches bugs early)
- ✅ **Testable:** `Reset()` enables test isolation without global state pollution

**Drawbacks:**
- ❌ **Global State:** Package-level variable (violates pure dependency injection)
- ❌ **Test Complexity:** Requires explicit `Reset()` in test setup/teardown
- ❌ **Hidden Dependency:** Not obvious from function signatures that config is used

**Goroutine Safety:**
- ✅ **Read-Safe:** `sync.RWMutex` allows concurrent reads after initialization
- ✅ **Write-Protected:** `configMu.Lock()` prevents concurrent initialization
- ✅ **Panic-Safe:** Panics if accessed before init (prevents race conditions)

**Use When:**
- Standard microservice applications requiring config across many layers
- Team prefers simplicity over strict dependency injection
- Configuration is read-only after initialization (most common case)

#### Pattern 2: Config as Dependency Injection (Testing-Friendly)

Pass `*Config` as explicit dependency to constructors instead of using global state[^18][^19]. This pattern provides maximum testability and makes dependencies explicit at the cost of more boilerplate.

```go
// File: internal/config/config.go
package config

import (
	"fmt"
	"time"

	"github.com/kelseyhightower/envconfig"
)

// Config holds all application configuration loaded from environment variables.
type Config struct {
	// Application metadata
	AppName string `envconfig:"APP_NAME" default:"go-microservice"`
	Debug   bool   `envconfig:"DEBUG" default:"false"`

	// Server configuration
	ServerPort    int           `envconfig:"SERVER_PORT" default:"8080"`
	ReadTimeout   time.Duration `envconfig:"READ_TIMEOUT" default:"10s"`
	WriteTimeout  time.Duration `envconfig:"WRITE_TIMEOUT" default:"10s"`
	IdleTimeout   time.Duration `envconfig:"IDLE_TIMEOUT" default:"60s"`

	// Database configuration
	DatabaseURL      string        `envconfig:"DATABASE_URL" required:"true"`
	DBMaxOpenConns   int           `envconfig:"DB_MAX_OPEN_CONNS" default:"25"`
	DBMaxIdleConns   int           `envconfig:"DB_MAX_IDLE_CONNS" default:"5"`
	DBConnMaxLifetime time.Duration `envconfig:"DB_CONN_MAX_LIFETIME" default:"5m"`

	// Redis configuration
	RedisAddr     string        `envconfig:"REDIS_ADDR" required:"true"`
	RedisPassword string        `envconfig:"REDIS_PASSWORD"`
	RedisDB       int           `envconfig:"REDIS_DB" default:"0"`
	RedisPoolSize int           `envconfig:"REDIS_POOL_SIZE" default:"10"`

	// Security
	JWTSecret string `envconfig:"JWT_SECRET" required:"true"`
}

// Load reads configuration from environment variables and returns Config.
// Returns error if required variables missing or type conversion fails.
func Load() (*Config, error) {
	var cfg Config
	if err := envconfig.Process("", &cfg); err != nil {
		return nil, fmt.Errorf("failed to process config: %w", err)
	}

	// Validate configuration (optional but recommended)
	if err := cfg.Validate(); err != nil {
		return nil, fmt.Errorf("config validation failed: %w", err)
	}

	return &cfg, nil
}

// MustLoad loads configuration or panics if it fails.
// Use during application initialization when config is required.
func MustLoad() *Config {
	cfg, err := Load()
	if err != nil {
		panic(fmt.Sprintf("failed to load configuration: %v", err))
	}
	return cfg
}

// Validate checks configuration for logical errors (beyond envconfig validation).
func (c *Config) Validate() error {
	if c.ServerPort < 1 || c.ServerPort > 65535 {
		return fmt.Errorf("invalid server port: %d (must be 1-65535)", c.ServerPort)
	}

	if c.ReadTimeout < 1*time.Second {
		return fmt.Errorf("read timeout too low: %v (must be >= 1s)", c.ReadTimeout)
	}

	if c.DBMaxOpenConns < c.DBMaxIdleConns {
		return fmt.Errorf("max open conns (%d) must be >= max idle conns (%d)",
			c.DBMaxOpenConns, c.DBMaxIdleConns)
	}

	return nil
}
```

**Usage in application services:**

```go
// File: internal/service/auth_service.go
package service

import (
	"context"
	"fmt"
	"time"

	"github.com/example/project/internal/config"
	"github.com/golang-jwt/jwt/v5"
)

type AuthService struct {
	repo   UserRepository
	config *config.Config  // Config as explicit dependency
}

// NewAuthService creates a new auth service with config dependency.
func NewAuthService(repo UserRepository, cfg *config.Config) *AuthService {
	return &AuthService{
		repo:   repo,
		config: cfg,
	}
}

// GenerateToken creates a JWT token using injected configuration.
func (s *AuthService) GenerateToken(ctx context.Context, userID int64) (string, error) {
	claims := jwt.MapClaims{
		"user_id": userID,
		"exp":     time.Now().Add(24 * time.Hour).Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	signed, err := token.SignedString([]byte(s.config.JWTSecret))
	if err != nil {
		return "", fmt.Errorf("failed to sign token: %w", err)
	}

	return signed, nil
}
```

**Dependency wiring in main.go:**

```go
// File: cmd/server/main.go
package main

import (
	"log/slog"

	"github.com/example/project/internal/config"
	"github.com/example/project/internal/database"
	"github.com/example/project/internal/repository"
	"github.com/example/project/internal/service"
	"github.com/example/project/internal/server"
)

func main() {
	// Step 1: Load configuration
	cfg := config.MustLoad()

	// Step 2: Initialize logger
	initLogger(cfg.Debug)

	slog.Info("application starting",
		"app_name", cfg.AppName,
		"port", cfg.ServerPort,
	)

	// Step 3: Initialize database
	db, err := database.NewPostgresDB(database.Config{
		URL:              cfg.DatabaseURL,
		MaxOpenConns:     cfg.DBMaxOpenConns,
		MaxIdleConns:     cfg.DBMaxIdleConns,
		ConnMaxLifetime:  cfg.DBConnMaxLifetime,
	})
	if err != nil {
		slog.Error("failed to connect to database", "error", err)
		panic(err)
	}
	defer db.Close()

	// Step 4: Wire dependencies (manual dependency injection)
	userRepo := repository.NewUserRepository(db)
	authService := service.NewAuthService(userRepo, cfg)  // Pass config explicitly

	// Step 5: Start server (pass config to server constructor)
	srv := server.New(cfg, db, authService)
	if err := srv.Start(); err != nil {
		slog.Error("server failed", "error", err)
	}
}
```

**Testing with dependency injection:**

```go
// File: internal/service/auth_service_test.go
package service

import (
	"context"
	"testing"
	"time"

	"github.com/example/project/internal/config"
	"github.com/stretchr/testify/assert"
)

func TestAuthService_GenerateToken(t *testing.T) {
	// Create test config (no environment variables needed)
	testConfig := &config.Config{
		AppName:   "test-app",
		JWTSecret: "test-secret-key",
		Debug:     true,
	}

	mockRepo := &MockUserRepository{}
	service := NewAuthService(mockRepo, testConfig)

	token, err := service.GenerateToken(context.Background(), 123)

	assert.NoError(t, err)
	assert.NotEmpty(t, token)
}

func TestAuthService_GenerateToken_MultipleSecrets(t *testing.T) {
	tests := []struct {
		name      string
		jwtSecret string
		wantError bool
	}{
		{
			name:      "valid secret",
			jwtSecret: "valid-secret-key-123",
			wantError: false,
		},
		{
			name:      "another valid secret",
			jwtSecret: "different-secret-456",
			wantError: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Each test gets isolated config
			testConfig := &config.Config{
				JWTSecret: tt.jwtSecret,
			}

			mockRepo := &MockUserRepository{}
			service := NewAuthService(mockRepo, testConfig)

			token, err := service.GenerateToken(context.Background(), 123)

			if tt.wantError {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
				assert.NotEmpty(t, token)
			}
		})
	}
}
```

**Benefits:**
- ✅ **Explicit Dependencies:** Function signatures show config requirement (no hidden globals)
- ✅ **Easy Testing:** Pass custom config to constructors, no environment setup needed
- ✅ **Multiple Configs:** Support different configs per component (e.g., per-tenant settings)
- ✅ **No Global State:** Pure dependency injection (functional programming friendly)
- ✅ **Refactoring-Friendly:** IDE can trace config usage via constructor parameters

**Drawbacks:**
- ❌ **Boilerplate:** Pass config to every constructor that needs it
- ❌ **Verbose:** Constructor parameter lists grow longer with more dependencies
- ❌ **Propagation:** Config must be passed through all layers (handler → service → repository)

**Goroutine Safety:**
- ✅ **Immutable After Init:** Config loaded once, never modified (read-only safe)
- ✅ **No Locking Needed:** Each goroutine receives same pointer, no mutations
- ⚠️ **Copy-Safe:** If config copied by value, each goroutine has independent copy

**Use When:**
- Applications requiring extensive unit testing (test-driven development)
- Team follows strict no-globals policy (Clean Architecture purists)
- Multi-tenant applications needing per-tenant configuration
- Configuration changes at runtime (e.g., feature flags, A/B testing)

#### Pattern 3: Lazy Initialization with sync.Once (Goroutine-Safe)

Load configuration on-demand with `sync.Once` to ensure single initialization across concurrent goroutines[^20][^21]. This pattern defers config loading until first use, useful for libraries or packages that may not always need config.

```go
// File: internal/config/config.go
package config

import (
	"fmt"
	"sync"
	"time"

	"github.com/kelseyhightower/envconfig"
)

// Config holds all application configuration loaded from environment variables.
type Config struct {
	// Application metadata
	AppName string `envconfig:"APP_NAME" default:"go-microservice"`
	Debug   bool   `envconfig:"DEBUG" default:"false"`

	// Server configuration
	ServerPort    int           `envconfig:"SERVER_PORT" default:"8080"`
	ReadTimeout   time.Duration `envconfig:"READ_TIMEOUT" default:"10s"`
	WriteTimeout  time.Duration `envconfig:"WRITE_TIMEOUT" default:"10s"`
	IdleTimeout   time.Duration `envconfig:"IDLE_TIMEOUT" default:"60s"`

	// Database configuration
	DatabaseURL      string        `envconfig:"DATABASE_URL" required:"true"`
	DBMaxOpenConns   int           `envconfig:"DB_MAX_OPEN_CONNS" default:"25"`
	DBMaxIdleConns   int           `envconfig:"DB_MAX_IDLE_CONNS" default:"5"`
	DBConnMaxLifetime time.Duration `envconfig:"DB_CONN_MAX_LIFETIME" default:"5m"`

	// Redis configuration
	RedisAddr     string        `envconfig:"REDIS_ADDR" required:"true"`
	RedisPassword string        `envconfig:"REDIS_PASSWORD"`
	RedisDB       int           `envconfig:"REDIS_DB" default:"0"`
	RedisPoolSize int           `envconfig:"REDIS_POOL_SIZE" default:"10"`

	// Security
	JWTSecret string `envconfig:"JWT_SECRET" required:"true"`
}

var (
	// Global configuration instance (lazy-loaded)
	instance *Config

	// Initialization error (captured during first load)
	initErr error

	// sync.Once ensures load runs exactly once across all goroutines
	once sync.Once
)

// Get returns the global configuration instance, initializing on first call.
// Uses sync.Once to ensure goroutine-safe initialization.
// Returns error if config loading fails (e.g., missing required env vars).
func Get() (*Config, error) {
	// once.Do() ensures this function runs exactly once, even with concurrent calls
	// Subsequent calls to Get() return the cached instance immediately
	once.Do(func() {
		var cfg Config
		if err := envconfig.Process("", &cfg); err != nil {
			initErr = fmt.Errorf("failed to process config: %w", err)
			return
		}

		instance = &cfg
		initErr = nil
	})

	// All goroutines receive the same instance and error
	return instance, initErr
}

// MustGet returns the global configuration instance or panics if loading fails.
// Convenient for application code that cannot handle config errors.
func MustGet() *Config {
	cfg, err := Get()
	if err != nil {
		panic(fmt.Sprintf("failed to get configuration: %v", err))
	}
	return cfg
}

// Reset clears the global configuration (for testing only).
// NEVER call this in production code.
// CAUTION: Not goroutine-safe, call only when no other goroutines are running.
func Reset() {
	instance = nil
	initErr = nil
	once = sync.Once{}
}
```

**Usage in application:**

```go
// File: cmd/server/main.go
package main

import (
	"log/slog"
	"github.com/example/project/internal/config"
	"github.com/example/project/internal/database"
	"github.com/example/project/internal/server"
)

func main() {
	// Config loaded automatically on first call to config.MustGet()
	// No explicit Init() required
	cfg := config.MustGet()

	initLogger(cfg.Debug)

	slog.Info("application starting",
		"app_name", cfg.AppName,
		"port", cfg.ServerPort,
	)

	db, err := database.NewPostgresDB(database.Config{
		URL:              cfg.DatabaseURL,
		MaxOpenConns:     cfg.DBMaxOpenConns,
		MaxIdleConns:     cfg.DBMaxIdleConns,
		ConnMaxLifetime:  cfg.DBConnMaxLifetime,
	})
	if err != nil {
		slog.Error("failed to connect to database", "error", err)
		panic(err)
	}
	defer db.Close()

	srv := server.New(db)
	if err := srv.Start(cfg.ServerPort); err != nil {
		slog.Error("server failed", "error", err)
	}
}
```

**Usage in concurrent goroutines:**

```go
// File: internal/worker/background_worker.go
package worker

import (
	"context"
	"log/slog"
	"sync"
	"time"

	"github.com/example/project/internal/config"
)

// BackgroundWorker processes tasks concurrently.
type BackgroundWorker struct {
	wg sync.WaitGroup
}

// Start launches N worker goroutines, each accessing config safely.
func (w *BackgroundWorker) Start(ctx context.Context, numWorkers int) {
	for i := 0; i < numWorkers; i++ {
		w.wg.Add(1)

		// Launch goroutine - config loaded lazily but safely
		go func(workerID int) {
			defer w.wg.Done()

			// Multiple goroutines can call MustGet() concurrently
			// sync.Once ensures config loaded exactly once
			cfg := config.MustGet()

			slog.Info("worker started",
				"worker_id", workerID,
				"app_name", cfg.AppName,
			)

			// Worker processing loop
			ticker := time.NewTicker(10 * time.Second)
			defer ticker.Stop()

			for {
				select {
				case <-ctx.Done():
					slog.Info("worker shutting down", "worker_id", workerID)
					return
				case <-ticker.C:
					w.processTask(cfg)
				}
			}
		}(i)
	}
}

func (w *BackgroundWorker) processTask(cfg *config.Config) {
	// Use config for task processing
	slog.Debug("processing task", "debug", cfg.Debug)
}

func (w *BackgroundWorker) Stop() {
	w.wg.Wait()
}
```

**Testing with lazy initialization:**

```go
// File: internal/config/config_test.go
package config

import (
	"os"
	"sync"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestGet_ConcurrentAccess(t *testing.T) {
	// Setup: Set environment variables
	os.Setenv("DATABASE_URL", "postgres://test")
	os.Setenv("REDIS_ADDR", "localhost:6379")
	os.Setenv("JWT_SECRET", "test-secret")
	defer func() {
		os.Unsetenv("DATABASE_URL")
		os.Unsetenv("REDIS_ADDR")
		os.Unsetenv("JWT_SECRET")
	}()

	// Reset config before test
	Reset()

	// Test: Multiple goroutines access config concurrently
	var wg sync.WaitGroup
	results := make([]*Config, 100)

	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(index int) {
			defer wg.Done()
			cfg, err := Get()
			assert.NoError(t, err)
			results[index] = cfg
		}(i)
	}

	wg.Wait()

	// Assert: All goroutines received the same instance
	firstInstance := results[0]
	for i, cfg := range results {
		assert.Same(t, firstInstance, cfg, "instance %d should be same pointer", i)
	}
}

func TestGet_InitializationError(t *testing.T) {
	// Setup: Missing required environment variable
	os.Unsetenv("DATABASE_URL")
	os.Unsetenv("REDIS_ADDR")
	os.Unsetenv("JWT_SECRET")

	// Reset config before test
	Reset()

	// Test: Get() returns error when config invalid
	cfg, err := Get()

	assert.Error(t, err)
	assert.Nil(t, cfg)
	assert.Contains(t, err.Error(), "failed to process config")
}

func TestMustGet_Panics(t *testing.T) {
	// Setup: Missing required environment variable
	os.Unsetenv("DATABASE_URL")
	Reset()

	// Test: MustGet() panics when config invalid
	assert.Panics(t, func() {
		MustGet()
	})
}
```

**Benefits:**
- ✅ **Lazy Loading:** Config loaded only when first needed (defers initialization cost)
- ✅ **Goroutine-Safe:** `sync.Once` guarantees single initialization across concurrent calls
- ✅ **No Explicit Init:** No need to call `Init()` or `MustInit()` in `main()`
- ✅ **Error Handling:** Captures initialization errors for all callers
- ✅ **Automatic:** Works transparently, no setup code required

**Drawbacks:**
- ❌ **Unpredictable Timing:** Config loaded at first use, not startup (harder to debug failures)
- ❌ **Error Discovery Delay:** Config errors not discovered until first call (could be deep in execution)
- ❌ **Testing Complexity:** Must call `Reset()` between tests to clear cached instance
- ❌ **Global State:** Still uses package-level variable (same issues as Pattern 1)

**Goroutine Safety:**
- ✅ **Thread-Safe Init:** `sync.Once` uses mutex internally, guarantees single execution
- ✅ **Read-Safe:** Config immutable after init, safe for concurrent reads
- ✅ **No Race Conditions:** All goroutines block until initialization completes
- ⚠️ **Reset Not Safe:** `Reset()` is NOT goroutine-safe, use only in test setup

**Use When:**
- Library packages that may not always need config (optional initialization)
- Applications where config needed deep in call stack (not at startup)
- Want goroutine-safe initialization without explicit `Init()` call
- Prefer automatic initialization over explicit control

#### Pattern 4: Environment-Specific Config with Viper (Multi-Source)

Use Viper to load configuration from multiple sources (files, env vars, remote config) with environment-specific overrides[^1][^6]. This pattern provides maximum flexibility for complex deployment scenarios (dev, staging, prod).

```go
// File: internal/config/config.go
package config

import (
	"fmt"
	"strings"
	"time"

	"github.com/spf13/viper"
)

// Config holds all application configuration from multiple sources.
type Config struct {
	// Application metadata
	AppName string
	Debug   bool

	// Server configuration
	ServerPort   int
	ReadTimeout  time.Duration
	WriteTimeout time.Duration
	IdleTimeout  time.Duration

	// Database configuration
	DatabaseURL       string
	DBMaxOpenConns    int
	DBMaxIdleConns    int
	DBConnMaxLifetime time.Duration

	// Redis configuration
	RedisAddr     string
	RedisPassword string
	RedisDB       int
	RedisPoolSize int

	// Security
	JWTSecret string
}

// LoadWithViper loads configuration using Viper (multi-source).
// Priority (highest to lowest):
//  1. Environment variables (APP_DATABASE_URL)
//  2. Config file for environment (config.{env}.yaml)
//  3. Base config file (config.yaml)
//  4. Default values
func LoadWithViper(env string) (*Config, error) {
	v := viper.New()

	// Set config file paths (multiple config directories)
	v.SetConfigName("config")        // Base config: config.yaml
	v.SetConfigType("yaml")
	v.AddConfigPath("./configs")     // Look in ./configs directory
	v.AddConfigPath("./config")      // Look in ./config directory
	v.AddConfigPath("/etc/app/")     // Look in /etc/app/ (production)
	v.AddConfigPath(".")             // Look in current directory

	// Read base configuration file (optional - don't fail if missing)
	if err := v.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			return nil, fmt.Errorf("failed to read base config: %w", err)
		}
		// Config file not found - acceptable, will use env vars + defaults
	}

	// Merge environment-specific config (config.dev.yaml, config.prod.yaml)
	if env != "" {
		v.SetConfigName(fmt.Sprintf("config.%s", env))
		if err := v.MergeInConfig(); err != nil {
			if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
				return nil, fmt.Errorf("failed to read %s config: %w", env, err)
			}
			// Environment-specific config not found - acceptable
		}
	}

	// Environment variables take precedence over config files
	v.SetEnvPrefix("APP")                            // APP_DATABASE_URL
	v.SetEnvKeyReplacer(strings.NewReplacer(".", "_")) // database.url → DATABASE_URL
	v.AutomaticEnv()                                 // Read all env vars with APP_ prefix

	// Set default values (lowest priority)
	setDefaults(v)

	// Unmarshal into Config struct
	var cfg Config
	if err := v.Unmarshal(&cfg); err != nil {
		return nil, fmt.Errorf("failed to unmarshal config: %w", err)
	}

	// Validate configuration
	if err := cfg.Validate(); err != nil {
		return nil, fmt.Errorf("config validation failed: %w", err)
	}

	return &cfg, nil
}

// setDefaults configures default values for all settings.
func setDefaults(v *viper.Viper) {
	// Application defaults
	v.SetDefault("AppName", "go-microservice")
	v.SetDefault("Debug", false)

	// Server defaults
	v.SetDefault("ServerPort", 8080)
	v.SetDefault("ReadTimeout", "10s")
	v.SetDefault("WriteTimeout", "10s")
	v.SetDefault("IdleTimeout", "60s")

	// Database defaults
	v.SetDefault("DBMaxOpenConns", 25)
	v.SetDefault("DBMaxIdleConns", 5)
	v.SetDefault("DBConnMaxLifetime", "5m")

	// Redis defaults
	v.SetDefault("RedisDB", 0)
	v.SetDefault("RedisPoolSize", 10)
}

// Validate checks configuration for logical errors.
func (c *Config) Validate() error {
	// Validate required fields
	if c.DatabaseURL == "" {
		return fmt.Errorf("DatabaseURL is required")
	}
	if c.RedisAddr == "" {
		return fmt.Errorf("RedisAddr is required")
	}
	if c.JWTSecret == "" {
		return fmt.Errorf("JWTSecret is required")
	}

	// Validate ranges
	if c.ServerPort < 1 || c.ServerPort > 65535 {
		return fmt.Errorf("invalid ServerPort: %d (must be 1-65535)", c.ServerPort)
	}

	if c.DBMaxOpenConns < c.DBMaxIdleConns {
		return fmt.Errorf("DBMaxOpenConns (%d) must be >= DBMaxIdleConns (%d)",
			c.DBMaxOpenConns, c.DBMaxIdleConns)
	}

	return nil
}
```

**Config files for different environments:**

```yaml
# File: configs/config.yaml (base configuration)
app_name: go-microservice
debug: false

server_port: 8080
read_timeout: 10s
write_timeout: 10s
idle_timeout: 60s

database_url: postgres://user:pass@localhost:5432/dbname
db_max_open_conns: 25
db_max_idle_conns: 5
db_conn_max_lifetime: 5m

redis_addr: localhost:6379
redis_db: 0
redis_pool_size: 10

jwt_secret: default-secret-change-in-production
```

```yaml
# File: configs/config.dev.yaml (development overrides)
debug: true

database_url: postgres://dev:dev@localhost:5432/dev_db
redis_addr: localhost:6379

jwt_secret: dev-secret-key
```

```yaml
# File: configs/config.prod.yaml (production overrides)
debug: false

# Production values overridden by environment variables
database_url: ${APP_DATABASE_URL}
redis_addr: ${APP_REDIS_ADDR}
jwt_secret: ${APP_JWT_SECRET}

# Production-tuned settings
db_max_open_conns: 50
db_max_idle_conns: 10
db_conn_max_lifetime: 10m

redis_pool_size: 20
```

**Usage in main.go:**

```go
// File: cmd/server/main.go
package main

import (
	"flag"
	"log/slog"
	"os"

	"github.com/example/project/internal/config"
	"github.com/example/project/internal/database"
	"github.com/example/project/internal/server"
)

func main() {
	// Read environment from flag or environment variable
	env := flag.String("env", os.Getenv("APP_ENV"), "Environment: dev, staging, prod")
	flag.Parse()

	if *env == "" {
		*env = "dev" // Default to development
	}

	// Load configuration for environment
	cfg, err := config.LoadWithViper(*env)
	if err != nil {
		slog.Error("failed to load configuration", "error", err)
		panic(err)
	}

	initLogger(cfg.Debug)

	slog.Info("application starting",
		"app_name", cfg.AppName,
		"environment", *env,
		"port", cfg.ServerPort,
		"debug", cfg.Debug,
	)

	db, err := database.NewPostgresDB(database.Config{
		URL:              cfg.DatabaseURL,
		MaxOpenConns:     cfg.DBMaxOpenConns,
		MaxIdleConns:     cfg.DBMaxIdleConns,
		ConnMaxLifetime:  cfg.DBConnMaxLifetime,
	})
	if err != nil {
		slog.Error("failed to connect to database", "error", err)
		panic(err)
	}
	defer db.Close()

	srv := server.New(db)
	if err := srv.Start(cfg.ServerPort); err != nil {
		slog.Error("server failed", "error", err)
	}
}
```

**Running with different environments:**

```bash
# Development (uses config.dev.yaml + defaults)
./app -env dev

# Production (uses config.prod.yaml + env vars override)
export APP_DATABASE_URL="postgres://prod:secret@prod-db:5432/prod_db"
export APP_REDIS_ADDR="redis-cluster:6379"
export APP_JWT_SECRET="prod-secret-key-abc123"
./app -env prod

# Staging (uses config.yaml + env vars, no config.staging.yaml)
export APP_DATABASE_URL="postgres://staging:pass@staging-db:5432/staging_db"
./app -env staging
```

**Benefits:**
- ✅ **Multi-Source Config:** Combine files, env vars, command-line flags, remote config
- ✅ **Environment-Specific:** Different settings per environment (dev/staging/prod)
- ✅ **Flexible Overrides:** Environment variables override file values (twelve-factor)
- ✅ **Hot Reload:** Viper supports watching config file changes (optional)
- ✅ **Gradual Migration:** Start with files in dev, move to env vars in prod

**Drawbacks:**
- ❌ **Complexity:** More complex than envconfig (multiple config sources to manage)
- ❌ **File Management:** Requires managing config files across environments
- ❌ **External Dependency:** Adds Viper dependency (envconfig simpler for env-only)
- ❌ **Testing Overhead:** Tests must set up config files or use test fixtures

**Goroutine Safety:**
- ✅ **Read-Safe:** Viper is safe for concurrent reads after initial load
- ⚠️ **Write-Not-Safe:** Viper's `Set()` not goroutine-safe (don't modify after load)
- ✅ **Watch-Safe:** `WatchConfig()` uses callbacks, safe for hot reload

**Use When:**
- Applications deployed across multiple environments (dev/staging/prod)
- Need file-based config for local development, env vars for production
- Require remote config integration (etcd, Consul, AWS Parameter Store)
- Team prefers config files over environment variables for readability

### 1.2.2 Common Configuration Mistakes

#### Mistake 1: Reading Config in init() Instead of main()

**Problem:** Go's `init()` functions run before `main()`, making it difficult to control initialization order, handle errors gracefully, or set up test environments[^22][^23].

**❌ Bad Example:**

```go
// File: internal/config/config.go
package config

import (
	"log"
	"github.com/kelseyhightower/envconfig"
)

var GlobalConfig Config

// init() runs automatically before main() - BAD PRACTICE
func init() {
	if err := envconfig.Process("", &GlobalConfig); err != nil {
		// Can't return error from init(), forced to panic or ignore
		log.Fatal("failed to load config:", err)
	}
}
```

**Why This Is Bad:**
- ❌ **No Error Handling:** Cannot return error from `init()`, forced to panic or log.Fatal
- ❌ **Unpredictable Order:** Multiple `init()` functions run in undefined order
- ❌ **Testing Nightmare:** Tests cannot control when config loads or inject test values
- ❌ **Hidden Dependencies:** Not obvious that importing package triggers config loading
- ❌ **Environment Setup:** Cannot set environment variables before `init()` runs

**✅ Good Example:**

```go
// File: internal/config/config.go
package config

import (
	"fmt"
	"github.com/kelseyhightower/envconfig"
)

type Config struct {
	DatabaseURL string `envconfig:"DATABASE_URL" required:"true"`
	RedisAddr   string `envconfig:"REDIS_ADDR" required:"true"`
	JWTSecret   string `envconfig:"JWT_SECRET" required:"true"`
}

// Load reads configuration from environment variables.
// Call explicitly in main() to control initialization order and handle errors.
func Load() (*Config, error) {
	var cfg Config
	if err := envconfig.Process("", &cfg); err != nil {
		return nil, fmt.Errorf("failed to process config: %w", err)
	}
	return &cfg, nil
}

// MustLoad loads configuration or panics (for application startup).
func MustLoad() *Config {
	cfg, err := Load()
	if err != nil {
		panic(fmt.Sprintf("failed to load configuration: %v", err))
	}
	return cfg
}
```

**Usage in main.go:**

```go
// File: cmd/server/main.go
package main

import (
	"log/slog"
	"github.com/example/project/internal/config"
)

func main() {
	// Step 1: Load config FIRST (explicit, controllable)
	cfg := config.MustLoad()

	// Step 2: Initialize logger (depends on config.Debug)
	initLogger(cfg.Debug)

	// Step 3: Initialize other resources in known order
	slog.Info("application starting", "app", cfg.AppName)
	// ...
}
```

**Testing with explicit initialization:**

```go
// File: internal/service/user_service_test.go
package service

import (
	"os"
	"testing"
	"github.com/example/project/internal/config"
)

func TestUserService_WithTestConfig(t *testing.T) {
	// Setup: Configure test environment BEFORE loading config
	os.Setenv("DATABASE_URL", "postgres://test")
	os.Setenv("REDIS_ADDR", "localhost:6379")
	os.Setenv("JWT_SECRET", "test-secret")
	defer func() {
		os.Unsetenv("DATABASE_URL")
		os.Unsetenv("REDIS_ADDR")
		os.Unsetenv("JWT_SECRET")
	}()

	// Load config explicitly (not in init())
	cfg := config.MustLoad()

	// Test with controlled config
	service := NewUserService(cfg)
	// ... test assertions ...
}
```

**Best Practice:**
- ✅ Load configuration explicitly in `main()` as first step
- ✅ Use `Load()` function that returns error (not `init()`)
- ✅ Control initialization order: config → logger → database → server
- ✅ Handle errors gracefully (log and exit, or return to caller)

#### Mistake 2: Not Validating Required Fields

**Problem:** Using default values for critical configuration (database URLs, secrets) can lead to production failures or security issues[^18][^24].

**❌ Bad Example:**

```go
// File: internal/config/config.go
package config

import "github.com/kelseyhightower/envconfig"

type Config struct {
	// No "required" tag - silently uses empty string if missing!
	DatabaseURL string `envconfig:"DATABASE_URL"`
	JWTSecret   string `envconfig:"JWT_SECRET"`
	RedisAddr   string `envconfig:"REDIS_ADDR"`
}

func Load() (*Config, error) {
	var cfg Config
	// Missing DATABASE_URL? No error, empty string returned!
	if err := envconfig.Process("", &cfg); err != nil {
		return nil, err
	}
	return &cfg, nil
}
```

**Why This Is Bad:**
- ❌ **Silent Failures:** Missing environment variables result in empty strings, not errors
- ❌ **Runtime Errors:** Database connection fails at runtime, not during config load
- ❌ **Security Risk:** Empty JWT secret or weak defaults compromise security
- ❌ **Hard to Debug:** Error occurs far from config loading, unclear root cause

**✅ Good Example:**

```go
// File: internal/config/config.go
package config

import (
	"fmt"
	"net/url"
	"time"

	"github.com/kelseyhightower/envconfig"
)

type Config struct {
	// Use "required" tag for critical fields
	DatabaseURL string `envconfig:"DATABASE_URL" required:"true"`
	RedisAddr   string `envconfig:"REDIS_ADDR" required:"true"`
	JWTSecret   string `envconfig:"JWT_SECRET" required:"true"`

	// Optional fields with sensible defaults
	ServerPort    int           `envconfig:"SERVER_PORT" default:"8080"`
	Debug         bool          `envconfig:"DEBUG" default:"false"`
	ReadTimeout   time.Duration `envconfig:"READ_TIMEOUT" default:"10s"`
	DBMaxOpenConns int          `envconfig:"DB_MAX_OPEN_CONNS" default:"25"`
}

// Load reads and validates configuration.
func Load() (*Config, error) {
	var cfg Config

	// envconfig checks "required" tags automatically
	if err := envconfig.Process("", &cfg); err != nil {
		return nil, fmt.Errorf("failed to process config: %w", err)
	}

	// Additional validation beyond envconfig
	if err := cfg.Validate(); err != nil {
		return nil, fmt.Errorf("config validation failed: %w", err)
	}

	return &cfg, nil
}

// Validate performs custom validation logic.
func (c *Config) Validate() error {
	// Validate database URL format
	if _, err := url.Parse(c.DatabaseURL); err != nil {
		return fmt.Errorf("invalid DATABASE_URL: %w", err)
	}

	// Validate JWT secret strength
	if len(c.JWTSecret) < 32 {
		return fmt.Errorf("JWT_SECRET must be at least 32 characters (got %d)", len(c.JWTSecret))
	}

	// Validate port range
	if c.ServerPort < 1 || c.ServerPort > 65535 {
		return fmt.Errorf("invalid SERVER_PORT: %d (must be 1-65535)", c.ServerPort)
	}

	// Validate database connection pool settings
	if c.DBMaxOpenConns < 1 {
		return fmt.Errorf("DB_MAX_OPEN_CONNS must be at least 1 (got %d)", c.DBMaxOpenConns)
	}

	return nil
}
```

**Usage in main.go:**

```go
// File: cmd/server/main.go
package main

import (
	"log/slog"
	"os"
	"github.com/example/project/internal/config"
)

func main() {
	// Config validation fails fast with clear error message
	cfg, err := config.Load()
	if err != nil {
		// Log error and exit gracefully (don't start with invalid config)
		slog.Error("configuration error", "error", err)
		os.Exit(1)
	}

	// Config validated - safe to proceed
	slog.Info("configuration loaded successfully")
	// ...
}
```

**Example validation errors:**

```bash
# Missing required field
$ ./app
configuration error: required key DATABASE_URL missing value

# Invalid database URL
$ export DATABASE_URL="not-a-valid-url"
$ ./app
configuration error: config validation failed: invalid DATABASE_URL: parse "not-a-valid-url": invalid URI for request

# Weak JWT secret
$ export DATABASE_URL="postgres://localhost/db"
$ export REDIS_ADDR="localhost:6379"
$ export JWT_SECRET="weak"
$ ./app
configuration error: config validation failed: JWT_SECRET must be at least 32 characters (got 4)

# Invalid port
$ export SERVER_PORT="99999"
$ ./app
configuration error: config validation failed: invalid SERVER_PORT: 99999 (must be 1-65535)
```

**Best Practice:**
- ✅ Use `required:"true"` tag for critical configuration (database, secrets, APIs)
- ✅ Implement custom `Validate()` method for complex validation logic
- ✅ Fail fast during startup if config invalid (don't start with bad config)
- ✅ Provide clear error messages indicating which field failed and why
- ✅ Validate format (URLs, ports, durations) not just presence

#### Mistake 3: Missing Environment Variable Defaults

**Problem:** Not providing sensible defaults for optional configuration forces users to set every environment variable, even for standard values[^5][^18].

**❌ Bad Example:**

```go
// File: internal/config/config.go
package config

import "github.com/kelseyhightower/envconfig"

type Config struct {
	// No defaults - user must set EVERY variable!
	ServerPort       int           `envconfig:"SERVER_PORT"`
	ReadTimeout      time.Duration `envconfig:"READ_TIMEOUT"`
	WriteTimeout     time.Duration `envconfig:"WRITE_TIMEOUT"`
	DBMaxOpenConns   int           `envconfig:"DB_MAX_OPEN_CONNS"`
	DBMaxIdleConns   int           `envconfig:"DB_MAX_IDLE_CONNS"`
	LogLevel         string        `envconfig:"LOG_LEVEL"`
	EnableProfiling  bool          `envconfig:"ENABLE_PROFILING"`
}

func Load() (*Config, error) {
	var cfg Config
	if err := envconfig.Process("", &cfg); err != nil {
		return nil, err
	}
	return &cfg, nil
}
```

**Why This Is Bad:**
- ❌ **User Burden:** Forces users to set 20+ environment variables for basic operation
- ❌ **Boilerplate:** Deployment configs (Docker, K8s) become verbose with every variable
- ❌ **Error-Prone:** Easy to forget a variable, leading to zero values (port 0, timeout 0)
- ❌ **Poor DX:** Developer experience suffers from excessive configuration

**✅ Good Example:**

```go
// File: internal/config/config.go
package config

import (
	"time"
	"github.com/kelseyhightower/envconfig"
)

type Config struct {
	// Required fields (no defaults)
	DatabaseURL string `envconfig:"DATABASE_URL" required:"true"`
	RedisAddr   string `envconfig:"REDIS_ADDR" required:"true"`
	JWTSecret   string `envconfig:"JWT_SECRET" required:"true"`

	// Optional fields with sensible defaults
	AppName       string        `envconfig:"APP_NAME" default:"go-microservice"`
	ServerPort    int           `envconfig:"SERVER_PORT" default:"8080"`
	ReadTimeout   time.Duration `envconfig:"READ_TIMEOUT" default:"10s"`
	WriteTimeout  time.Duration `envconfig:"WRITE_TIMEOUT" default:"10s"`
	IdleTimeout   time.Duration `envconfig:"IDLE_TIMEOUT" default:"60s"`

	// Database connection pool defaults (tuned for typical workloads)
	DBMaxOpenConns    int           `envconfig:"DB_MAX_OPEN_CONNS" default:"25"`
	DBMaxIdleConns    int           `envconfig:"DB_MAX_IDLE_CONNS" default:"5"`
	DBConnMaxLifetime time.Duration `envconfig:"DB_CONN_MAX_LIFETIME" default:"5m"`

	// Redis connection pool defaults
	RedisPassword string `envconfig:"REDIS_PASSWORD"`  // Empty by default (no auth)
	RedisDB       int    `envconfig:"REDIS_DB" default:"0"`
	RedisPoolSize int    `envconfig:"REDIS_POOL_SIZE" default:"10"`

	// Logging defaults
	LogLevel string `envconfig:"LOG_LEVEL" default:"info"`
	Debug    bool   `envconfig:"DEBUG" default:"false"`

	// Feature flags (off by default)
	EnableProfiling bool `envconfig:"ENABLE_PROFILING" default:"false"`
	EnableMetrics   bool `envconfig:"ENABLE_METRICS" default:"true"`
}

func Load() (*Config, error) {
	var cfg Config
	if err := envconfig.Process("", &cfg); err != nil {
		return nil, err
	}
	return &cfg, nil
}
```

**Minimal environment variables for startup:**

```bash
# Only 3 required variables - everything else has defaults!
export DATABASE_URL="postgres://user:pass@localhost:5432/mydb"
export REDIS_ADDR="localhost:6379"
export JWT_SECRET="your-secret-key-here-min-32-chars"

./app
# Runs with defaults: port 8080, 25 DB connections, 10s timeout, info logging
```

**Override defaults when needed:**

```bash
# Production: Override specific values
export DATABASE_URL="postgres://prod:secret@prod-db:5432/prod"
export REDIS_ADDR="redis-cluster:6379"
export JWT_SECRET="prod-secret"
export SERVER_PORT="3000"              # Override default 8080
export DB_MAX_OPEN_CONNS="50"          # Override default 25
export LOG_LEVEL="warn"                # Override default "info"
export ENABLE_PROFILING="true"         # Override default false

./app
```

**Docker Compose example (minimal config):**

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    image: myapp:latest
    environment:
      # Only required variables - rest use defaults
      DATABASE_URL: postgres://user:pass@db:5432/mydb
      REDIS_ADDR: redis:6379
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "8080:8080"  # Uses default SERVER_PORT=8080
```

**Best Practice:**
- ✅ Use `default:"value"` tag for all optional configuration
- ✅ Choose sensible defaults based on typical production workloads
- ✅ Only mark truly required fields as `required:"true"`
- ✅ Document defaults in README or config struct comments
- ✅ Allow users to override any default via environment variable

**Default Value Guidelines:**

| Config Type | Default Strategy | Example |
|-------------|-----------------|---------|
| **Required Secrets** | No default, `required:"true"` | `DATABASE_URL`, `JWT_SECRET` |
| **Server Ports** | Standard ports | `8080` (HTTP), `8443` (HTTPS), `9090` (metrics) |
| **Timeouts** | Conservative defaults | Read: `10s`, Write: `10s`, Idle: `60s` |
| **Connection Pools** | Based on workload | DB: `25` open, `5` idle; Redis: `10` pool size |
| **Logging** | Info level | `LogLevel: "info"`, `Debug: false` |
| **Feature Flags** | Disabled by default | `EnableProfiling: false` |

### 1.2.3 Verification and Troubleshooting

#### Health Check Endpoint Showing Config Status

Expose a health check endpoint that verifies configuration and displays non-sensitive settings for debugging[^25][^26].

```go
// File: internal/http/handler/health_handler.go
package handler

import (
	"context"
	"database/sql"
	"encoding/json"
	"net/http"
	"time"

	"github.com/example/project/internal/cache"
	"github.com/example/project/internal/config"
	"github.com/redis/go-redis/v9"
)

// HealthHandler provides health and readiness checks.
type HealthHandler struct {
	db    *sql.DB
	cache *redis.Client
}

func NewHealthHandler(db *sql.DB, cache *redis.Client) *HealthHandler {
	return &HealthHandler{
		db:    db,
		cache: cache,
	}
}

// HealthResponse represents the health check response.
type HealthResponse struct {
	Status      string                 `json:"status"`       // "healthy" or "unhealthy"
	Version     string                 `json:"version"`      // Application version
	Environment string                 `json:"environment"`  // dev, staging, prod
	Config      ConfigStatus           `json:"config"`       // Config verification
	Dependencies map[string]DepStatus  `json:"dependencies"` // Database, Redis, etc.
	Timestamp   time.Time              `json:"timestamp"`    // Check timestamp
}

// ConfigStatus shows non-sensitive configuration status.
type ConfigStatus struct {
	Loaded       bool     `json:"loaded"`
	AppName      string   `json:"app_name"`
	ServerPort   int      `json:"server_port"`
	Debug        bool     `json:"debug"`

	// Connection pool settings (useful for debugging)
	DBMaxOpenConns int `json:"db_max_open_conns"`
	DBMaxIdleConns int `json:"db_max_idle_conns"`
	RedisPoolSize  int `json:"redis_pool_size"`

	// NEVER expose sensitive values (secrets, passwords, URLs)
	DatabaseConfigured bool `json:"database_configured"` // true if DATABASE_URL set
	RedisConfigured    bool `json:"redis_configured"`    // true if REDIS_ADDR set
	JWTConfigured      bool `json:"jwt_configured"`      // true if JWT_SECRET set
}

// DepStatus represents dependency health status.
type DepStatus struct {
	Status  string        `json:"status"`  // "up", "down", "degraded"
	Latency time.Duration `json:"latency"` // Response time
	Message string        `json:"message,omitempty"` // Error message if down
}

// Health returns overall application health.
func (h *HealthHandler) Health(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()
	cfg := config.Get()

	response := HealthResponse{
		Status:      "healthy",
		Version:     "1.0.0", // TODO: Read from build info
		Environment: getEnvironment(),
		Config:      h.checkConfig(cfg),
		Dependencies: make(map[string]DepStatus),
		Timestamp:   time.Now(),
	}

	// Check database health
	dbStatus := h.checkDatabase(ctx)
	response.Dependencies["database"] = dbStatus
	if dbStatus.Status != "up" {
		response.Status = "unhealthy"
	}

	// Check Redis health
	redisStatus := h.checkRedis(ctx)
	response.Dependencies["redis"] = redisStatus
	if redisStatus.Status != "up" {
		response.Status = "degraded" // Redis down is degraded, not unhealthy
	}

	// Set HTTP status code
	statusCode := http.StatusOK
	if response.Status == "unhealthy" {
		statusCode = http.StatusServiceUnavailable
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(response)
}

// checkConfig verifies configuration status (non-sensitive values only).
func (h *HealthHandler) checkConfig(cfg *config.Config) ConfigStatus {
	return ConfigStatus{
		Loaded:          true,
		AppName:         cfg.AppName,
		ServerPort:      cfg.ServerPort,
		Debug:           cfg.Debug,
		DBMaxOpenConns:  cfg.DBMaxOpenConns,
		DBMaxIdleConns:  cfg.DBMaxIdleConns,
		RedisPoolSize:   cfg.RedisPoolSize,

		// Check if sensitive values configured (don't expose actual values)
		DatabaseConfigured: cfg.DatabaseURL != "",
		RedisConfigured:    cfg.RedisAddr != "",
		JWTConfigured:      cfg.JWTSecret != "",
	}
}

// checkDatabase verifies database connectivity.
func (h *HealthHandler) checkDatabase(ctx context.Context) DepStatus {
	start := time.Now()

	// Use context with timeout to prevent hanging health checks
	ctx, cancel := context.WithTimeout(ctx, 2*time.Second)
	defer cancel()

	if err := h.db.PingContext(ctx); err != nil {
		return DepStatus{
			Status:  "down",
			Latency: time.Since(start),
			Message: err.Error(),
		}
	}

	return DepStatus{
		Status:  "up",
		Latency: time.Since(start),
	}
}

// checkRedis verifies Redis connectivity.
func (h *HealthHandler) checkRedis(ctx context.Context) DepStatus {
	start := time.Now()

	ctx, cancel := context.WithTimeout(ctx, 2*time.Second)
	defer cancel()

	if err := h.cache.Ping(ctx).Err(); err != nil {
		return DepStatus{
			Status:  "down",
			Latency: time.Since(start),
			Message: err.Error(),
		}
	}

	return DepStatus{
		Status:  "up",
		Latency: time.Since(start),
	}
}

// getEnvironment returns the current environment (dev, staging, prod).
func getEnvironment() string {
	cfg := config.Get()
	if cfg.Debug {
		return "development"
	}
	return "production"
}

// Readiness returns whether application is ready to serve traffic.
// Kubernetes uses this for readiness probes.
func (h *HealthHandler) Readiness(w http.ResponseWriter, r *http.Request) {
	ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
	defer cancel()

	// Check critical dependencies (database must be up)
	if err := h.db.PingContext(ctx); err != nil {
		http.Error(w, "database not ready", http.StatusServiceUnavailable)
		return
	}

	w.WriteHeader(http.StatusOK)
	w.Write([]byte("ready"))
}

// Liveness returns whether application is alive.
// Kubernetes uses this for liveness probes (restart if fails).
func (h *HealthHandler) Liveness(w http.ResponseWriter, r *http.Request) {
	// Liveness is simple - just return 200 if application running
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("alive"))
}
```

**Register health endpoints in main.go:**

```go
// File: cmd/server/main.go
package main

import (
	"net/http"
	"github.com/example/project/internal/config"
	"github.com/example/project/internal/database"
	"github.com/example/project/internal/cache"
	"github.com/example/project/internal/http/handler"
)

func main() {
	cfg := config.MustLoad()
	db, _ := database.NewPostgresDB(/* ... */)
	redisCache := cache.NewCache(cfg.RedisAddr, cfg.RedisPassword, cfg.RedisDB)

	// Setup health check handler
	healthHandler := handler.NewHealthHandler(db, redisCache.client)

	mux := http.NewServeMux()

	// Health endpoints
	mux.HandleFunc("GET /health", healthHandler.Health)
	mux.HandleFunc("GET /health/ready", healthHandler.Readiness)
	mux.HandleFunc("GET /health/live", healthHandler.Liveness)

	// Application routes
	// mux.HandleFunc("POST /api/users", ...)

	http.ListenAndServe(":8080", mux)
}
```

**Example health check response:**

```bash
$ curl http://localhost:8080/health | jq
```

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "config": {
    "loaded": true,
    "app_name": "go-microservice",
    "server_port": 8080,
    "debug": false,
    "db_max_open_conns": 25,
    "db_max_idle_conns": 5,
    "redis_pool_size": 10,
    "database_configured": true,
    "redis_configured": true,
    "jwt_configured": true
  },
  "dependencies": {
    "database": {
      "status": "up",
      "latency": 2345600
    },
    "redis": {
      "status": "up",
      "latency": 1234500
    }
  },
  "timestamp": "2025-11-02T10:30:45Z"
}
```

**Kubernetes health probe configuration:**

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: go-microservice
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: app
        image: myapp:latest
        ports:
        - containerPort: 8080

        # Liveness probe: Restart container if fails
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3

        # Readiness probe: Remove from load balancer if fails
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 2
          failureThreshold: 2

        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: REDIS_ADDR
          value: "redis:6379"
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: jwt-secret
              key: secret
```

**Troubleshooting with health endpoint:**

```bash
# Check if config loaded correctly
curl http://localhost:8080/health | jq '.config'

# Check database connectivity
curl http://localhost:8080/health | jq '.dependencies.database'

# Check Redis connectivity
curl http://localhost:8080/health | jq '.dependencies.redis'

# Check overall status (exit code 0 if healthy, non-zero if unhealthy)
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health
```

**Best Practices:**
- ✅ Expose `/health` for detailed status, `/health/ready` for readiness, `/health/live` for liveness
- ✅ Include non-sensitive config values (ports, pool sizes, debug mode)
- ✅ **NEVER** expose secrets (JWT tokens, passwords, database URLs)
- ✅ Check critical dependencies (database, cache, external APIs)
- ✅ Use timeouts for dependency checks (prevent hanging health checks)
- ✅ Return appropriate HTTP status codes (200 healthy, 503 unhealthy)
- ✅ Include latency metrics for performance monitoring


STDIN
### 1.5 Type Safety with Struct Tags and Custom Types

Go's type system combined with struct tags provides compile-time safety for configuration values[^27][^28]. Using custom types instead of primitives (type aliases vs. defined types) adds semantic safety and prevents mixing incompatible values.

**Core Benefits:**
- **Compile-Time Safety:** Type checker catches mismatched types before runtime
- **Semantic Types:** Domain-specific types prevent mixing values (UserID vs. OrderID)
- **Self-Documenting:** Types convey intent (EmailAddress, DatabaseURL, Port)
- **Validation Integration:** Custom types can have Validate() methods
- **Refactoring-Safe:** Compiler catches type mismatches during refactoring

#### Pattern 1: Custom Types for Semantic Safety

```go
// File: internal/config/types.go
package config

import (
    "fmt"
    "net"
    "net/url"
    "regexp"
    "time"
)

// Port represents a network port number with validation.
// Defined type (not alias) prevents mixing with raw integers.
type Port int

// Validate checks port is in valid range (1-65535).
func (p Port) Validate() error {
    if p < 1 || p > 65535 {
        return fmt.Errorf("invalid port %d: must be 1-65535", p)
    }
    return nil
}

// String returns port as string for logging.
func (p Port) String() string {
    return fmt.Sprintf(":%d", p)
}

// DatabaseURL represents a validated database connection string.
type DatabaseURL string

// Validate checks URL format and required components.
func (d DatabaseURL) Validate() error {
    if d == "" {
        return fmt.Errorf("database URL cannot be empty")
    }

    u, err := url.Parse(string(d))
    if err != nil {
        return fmt.Errorf("invalid database URL format: %w", err)
    }

    // Check required URL components
    if u.Scheme == "" {
        return fmt.Errorf("database URL missing scheme (postgres://...)")
    }
    if u.Host == "" {
        return fmt.Errorf("database URL missing host")
    }

    return nil
}

// RedisAddr represents a Redis server address (host:port format).
type RedisAddr string

// Validate checks address format.
func (r RedisAddr) Validate() error {
    if r == "" {
        return fmt.Errorf("redis address cannot be empty")
    }

    // Validate host:port format
    host, port, err := net.SplitHostPort(string(r))
    if err != nil {
        return fmt.Errorf("invalid redis address format (expected host:port): %w", err)
    }

    if host == "" {
        return fmt.Errorf("redis address missing host")
    }
    if port == "" {
        return fmt.Errorf("redis address missing port")
    }

    return nil
}

// JWTSecret represents a JSON Web Token signing secret with strength validation.
type JWTSecret string

// Validate checks secret meets minimum security requirements.
func (j JWTSecret) Validate() error {
    if len(j) == 0 {
        return fmt.Errorf("JWT secret cannot be empty")
    }

    // Minimum 32 characters for HS256 (OWASP recommendation)
    if len(j) < 32 {
        return fmt.Errorf("JWT secret too weak: %d characters (minimum 32)", len(j))
    }

    return nil
}

// EmailAddress represents a validated email address.
type EmailAddress string

var emailRegex = regexp.MustCompile(`^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$`)

// Validate checks email address format.
func (e EmailAddress) Validate() error {
    if e == "" {
        return fmt.Errorf("email address cannot be empty")
    }

    if !emailRegex.MatchString(string(e)) {
        return fmt.Errorf("invalid email address format: %s", e)
    }

    return nil
}

// Timeout represents a validated timeout duration.
type Timeout time.Duration

// Validate checks timeout is reasonable (not too short or too long).
func (t Timeout) Validate() error {
    dur := time.Duration(t)

    // Minimum 100ms (prevent too-short timeouts causing failures)
    if dur < 100*time.Millisecond {
        return fmt.Errorf("timeout %v too short (minimum 100ms)", dur)
    }

    // Maximum 5 minutes (prevent hanging connections)
    if dur > 5*time.Minute {
        return fmt.Errorf("timeout %v too long (maximum 5m)", dur)
    }

    return nil
}
```

**Usage in configuration struct:**

```go
// File: internal/config/config.go
package config

import (
    "fmt"
    "time"

    "github.com/kelseyhightower/envconfig"
)

// Config uses custom types for type safety and semantic validation.
type Config struct {
    // Application metadata
    AppName string `envconfig:"APP_NAME" default:"go-microservice"`
    Debug   bool   `envconfig:"DEBUG" default:"false"`

    // Server configuration (type-safe)
    ServerPort   Port    `envconfig:"SERVER_PORT" default:"8080"`
    ReadTimeout  Timeout `envconfig:"READ_TIMEOUT" default:"10s"`
    WriteTimeout Timeout `envconfig:"WRITE_TIMEOUT" default:"10s"`
    IdleTimeout  Timeout `envconfig:"IDLE_TIMEOUT" default:"60s"`

    // Database configuration (validated types)
    DatabaseURL       DatabaseURL `envconfig:"DATABASE_URL" required:"true"`
    DBMaxOpenConns    int         `envconfig:"DB_MAX_OPEN_CONNS" default:"25"`
    DBMaxIdleConns    int         `envconfig:"DB_MAX_IDLE_CONNS" default:"5"`
    DBConnMaxLifetime time.Duration `envconfig:"DB_CONN_MAX_LIFETIME" default:"5m"`

    // Redis configuration (validated address)
    RedisAddr     RedisAddr `envconfig:"REDIS_ADDR" required:"true"`
    RedisPassword string    `envconfig:"REDIS_PASSWORD"`
    RedisDB       int       `envconfig:"REDIS_DB" default:"0"`
    RedisPoolSize int       `envconfig:"REDIS_POOL_SIZE" default:"10"`

    // Security (validated secret)
    JWTSecret JWTSecret `envconfig:"JWT_SECRET" required:"true"`
}

// Load reads configuration with automatic validation.
func Load() (*Config, error) {
    var cfg Config

    // envconfig handles struct tag validation
    if err := envconfig.Process("", &cfg); err != nil {
        return nil, fmt.Errorf("failed to process config: %w", err)
    }

    // Custom type validation
    if err := cfg.Validate(); err != nil {
        return nil, fmt.Errorf("config validation failed: %w", err)
    }

    return &cfg, nil
}

// Validate runs all custom type validators.
func (c *Config) Validate() error {
    // Validate port
    if err := c.ServerPort.Validate(); err != nil {
        return fmt.Errorf("server port: %w", err)
    }

    // Validate timeouts
    if err := c.ReadTimeout.Validate(); err != nil {
        return fmt.Errorf("read timeout: %w", err)
    }
    if err := c.WriteTimeout.Validate(); err != nil {
        return fmt.Errorf("write timeout: %w", err)
    }
    if err := c.IdleTimeout.Validate(); err != nil {
        return fmt.Errorf("idle timeout: %w", err)
    }

    // Validate database URL
    if err := c.DatabaseURL.Validate(); err != nil {
        return fmt.Errorf("database URL: %w", err)
    }

    // Validate Redis address
    if err := c.RedisAddr.Validate(); err != nil {
        return fmt.Errorf("redis address: %w", err)
    }

    // Validate JWT secret
    if err := c.JWTSecret.Validate(); err != nil {
        return fmt.Errorf("JWT secret: %w", err)
    }

    // Validate connection pool constraints
    if c.DBMaxOpenConns < c.DBMaxIdleConns {
        return fmt.Errorf("DB_MAX_OPEN_CONNS (%d) must be >= DB_MAX_IDLE_CONNS (%d)",
            c.DBMaxOpenConns, c.DBMaxIdleConns)
    }

    return nil
}
```

**Benefits:**
- ✅ **Type Safety:** Cannot pass Port to function expecting int (prevents mistakes)
- ✅ **Semantic Clarity:** `func Listen(port Port)` clearer than `func Listen(port int)`
- ✅ **Centralized Validation:** Each type validates itself (single responsibility)
- ✅ **Self-Documenting:** Type name conveys meaning and constraints
- ✅ **Refactoring-Safe:** Changing validation logic updates all usages

**Drawbacks:**
- ❌ **Conversion Overhead:** Must convert custom types to standard library types
- ❌ **Verbose:** More type definitions than using primitives
- ❌ **Learning Curve:** Team must understand custom type patterns

**Use When:**
- Configuration values have validation rules (ports, URLs, secrets)
- Preventing mixing incompatible values (UserID vs. ProductID)
- Domain model requires semantic types (Money, Percentage, Email)
- Team prioritizes type safety over simplicity

---


---

### 1.3 Alternative Approaches

**Alternative 1: Viper for Multi-Source Configuration**

Viper provides flexibility when configuration comes from multiple sources (files, env vars, remote config servers)[^6]. Suitable for complex scenarios but adds overhead for simple microservices.

*Pros:* Multiple config sources, hot-reloading, integration with Spring Cloud Config
*Cons:* More complex API, additional dependency, overkill for env-var-only configs
*Use When:* Need file-based development config + env var production config, or remote config integration

```go
import "github.com/spf13/viper"

func LoadWithViper() (*Config, error) {
	viper.SetConfigName("config")
	viper.SetConfigType("yaml")
	viper.AddConfigPath("./configs")

	// Environment variables take precedence
	viper.AutomaticEnv()
	viper.SetEnvPrefix("APP")

	if err := viper.ReadInConfig(); err != nil {
		// Config file optional in production (use env vars)
		log.Printf("No config file found, using environment variables: %v", err)
	}

	var cfg Config
	if err := viper.Unmarshal(&cfg); err != nil {
		return nil, fmt.Errorf("failed to unmarshal config: %w", err)
	}

	return &cfg, nil
}
```

**Alternative 2: Standard Library flag Package**

Use `flag` package for command-line configuration, suitable for CLI tools or local development[^7].

*Pros:* No external dependencies, explicit configuration, built-in help text
*Cons:* Verbose for many parameters, not suitable for containerized deployments
*Use When:* Building CLI tools, local development scripts, or small utilities

```go
import "flag"

func LoadFromFlags() *Config {
	cfg := &Config{}

	flag.StringVar(&cfg.AppName, "app-name", "go-microservice", "Application name")
	flag.BoolVar(&cfg.Debug, "debug", false, "Enable debug mode")
	flag.IntVar(&cfg.ServerPort, "port", 8080, "Server port")
	flag.StringVar(&cfg.DatabaseURL, "database-url", "", "Database connection URL")

	flag.Parse()

	return cfg
}
```

### 1.4 Decision Criteria

| Factor | envconfig | Viper | flag |
|--------|-----------|-------|------|
| Twelve-Factor Compliance | ✅ Perfect | ✅ Supported | ❌ CLI-focused |
| Container-Native | ✅ Excellent | ✅ Good | ❌ Poor |
| Simplicity | ✅ Simple | ⚠️ Complex | ✅ Simple |
| Multi-Source Config | ❌ Env vars only | ✅ Advanced | ❌ CLI only |
| Type Safety | ✅ Struct tags | ✅ Unmarshaling | ✅ Native types |
| Hot Reload | ❌ No | ✅ Yes | ❌ No |
| **Recommended For** | **Microservices** | Complex apps | CLI tools |

**Decision Rule:** Use envconfig for microservices (default), Viper when multiple config sources required, flag for CLI tools only.

---

## 2. Structured Logging

### 2.1 Recommended Approach: slog (Standard Library, Go 1.21+)

Go 1.21 introduced `log/slog` as the official structured logging package, providing JSON output, log levels, and context propagation without external dependencies[^2][^8]. For new projects on Go 1.21+, slog is the recommended default.

**Core Benefits:**
- **Standard Library:** No external dependencies, guaranteed compatibility
- **Structured Logging:** JSON output for machine parsing, key-value pairs for context
- **Performance:** Efficient allocation patterns, suitable for high-throughput services
- **Context Integration:** Seamless propagation of request IDs via context.Context

### 2.2 Implementation Example

```go
// File: internal/logging/logger.go
package logging

import (
	"context"
	"log/slog"
	"os"
)

// ContextKey is the type for context keys to avoid collisions.
type contextKey string

const requestIDKey contextKey = "request_id"

// InitLogger creates and configures the global slog logger.
// Call during application startup before any logging occurs.
func InitLogger(debug bool) {
	level := slog.LevelInfo
	if debug {
		level = slog.LevelDebug
	}

	opts := &slog.HandlerOptions{
		Level: level,
		// Add source location (file:line) to logs in debug mode
		AddSource: debug,
	}

	// JSON handler for production (structured logs)
	handler := slog.NewJSONHandler(os.Stdout, opts)

	// For development, use TextHandler for human-readable output
	// handler := slog.NewTextHandler(os.Stdout, opts)

	logger := slog.New(handler)
	slog.SetDefault(logger)
}

// WithRequestID adds request ID to context for tracing.
func WithRequestID(ctx context.Context, requestID string) context.Context {
	return context.WithValue(ctx, requestIDKey, requestID)
}

// RequestIDFromContext extracts request ID from context.
func RequestIDFromContext(ctx context.Context) string {
	if id, ok := ctx.Value(requestIDKey).(string); ok {
		return id
	}
	return ""
}

// LogWithContext returns a logger with context values attached.
// Use this to include request ID in all log entries within a request.
func LogWithContext(ctx context.Context) *slog.Logger {
	logger := slog.Default()

	if requestID := RequestIDFromContext(ctx); requestID != "" {
		logger = logger.With("request_id", requestID)
	}

	return logger
}
```

**Usage in HTTP handlers:**

```go
// File: internal/http/middleware/logging.go
package middleware

import (
	"net/http"
	"time"

	"github.com/example/project/internal/logging"
	"github.com/google/uuid"
)

// RequestLogger middleware adds request ID and logs HTTP requests.
func RequestLogger(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()

		// Generate request ID
		requestID := uuid.New().String()
		ctx := logging.WithRequestID(r.Context(), requestID)

		// Get logger with request ID attached
		logger := logging.LogWithContext(ctx)

		logger.Info("request started",
			"method", r.Method,
			"path", r.URL.Path,
			"remote_addr", r.RemoteAddr,
		)

		// Pass context with request ID to handler
		next.ServeHTTP(w, r.WithContext(ctx))

		logger.Info("request completed",
			"method", r.Method,
			"path", r.URL.Path,
			"duration_ms", time.Since(start).Milliseconds(),
		)
	})
}
```

**Usage in application code:**

```go
// File: internal/service/user_service.go
package service

import (
	"context"
	"github.com/example/project/internal/logging"
)

type UserService struct {
	repo UserRepository
}

func (s *UserService) CreateUser(ctx context.Context, email string) error {
	logger := logging.LogWithContext(ctx)

	logger.Info("creating user", "email", email)

	user, err := s.repo.Save(ctx, &User{Email: email})
	if err != nil {
		logger.Error("failed to create user",
			"email", email,
			"error", err,
		)
		return err
	}

	logger.Info("user created successfully",
		"user_id", user.ID,
		"email", email,
	)

	return nil
}
```

### 2.2.1 Logger Initialization Patterns

#### Pattern 1: Global Logger with Init Function (Recommended)

Initialize slog once at application startup, set as default logger, use throughout application[^8].

```go
// File: cmd/server/main.go
package main

import (
	"log/slog"
	"os"
	"github.com/example/project/internal/config"
	"github.com/example/project/internal/logging"
)

func main() {
	// Step 1: Load configuration
	cfg := config.MustLoad()

	// Step 2: Initialize logging FIRST (before any log calls)
	logging.InitLogger(cfg.Debug)

	// Step 3: Log application startup
	slog.Info("application starting",
		"app_name", cfg.AppName,
		"port", cfg.ServerPort,
		"debug", cfg.Debug,
	)

	// Step 4: Initialize other resources (database, cache, etc.)
	// ...

	slog.Info("application ready")
}
```

**Benefits:**
- ✅ Single initialization point
- ✅ Consistent logging from startup to shutdown
- ✅ Easy to test (override slog.Default() in tests)

**Use When:** Standard microservice applications (default recommendation)

#### Pattern 2: Dependency-Injected Logger (Testing-Friendly)

Pass logger as dependency instead of using global default[^9].

```go
// File: internal/service/user_service.go
package service

import (
	"context"
	"log/slog"
)

type UserService struct {
	repo   UserRepository
	logger *slog.Logger  // Logger as dependency
}

func NewUserService(repo UserRepository, logger *slog.Logger) *UserService {
	return &UserService{
		repo:   repo,
		logger: logger,
	}
}

func (s *UserService) CreateUser(ctx context.Context, email string) error {
	// Use injected logger instead of slog.Default()
	s.logger.InfoContext(ctx, "creating user", "email", email)

	// ... implementation ...

	return nil
}
```

**Benefits:**
- ✅ Explicit dependency (no global state)
- ✅ Easy to mock in unit tests
- ✅ Supports multiple loggers (e.g., per-tenant logging)

**Drawbacks:**
- ❌ More boilerplate (pass logger everywhere)
- ❌ Can be verbose for large codebases

**Use When:** Applications requiring multiple logger instances or strict no-globals policy

### 2.2.2 Common Initialization Mistakes

**❌ Mistake 1: Using logger before initialization**

```go
// BAD: slog used before InitLogger() called
package main

import "log/slog"

func main() {
	slog.Info("starting app")  // Uses default text handler, not JSON!

	InitLogger(true)  // Too late - first log already written with wrong format
}
```

**✅ Fix: Initialize logger FIRST**

```go
// GOOD: Initialize logger before any log calls
func main() {
	InitLogger(true)  // Configure FIRST

	slog.Info("starting app")  // Now uses JSON handler
}
```

**❌ Mistake 2: Missing context propagation in goroutines**

```go
// BAD: Goroutine loses request ID from context
func (h *Handler) ProcessAsync(ctx context.Context, data string) {
	go func() {
		// New goroutine - ctx not passed, request ID lost!
		slog.Info("processing data", "data", data)
		// Log entry missing request_id field
	}()
}
```

**✅ Fix: Pass context to goroutines**

```go
// GOOD: Pass context to goroutine for request ID tracing
func (h *Handler) ProcessAsync(ctx context.Context, data string) {
	go func(ctx context.Context) {
		logger := logging.LogWithContext(ctx)
		logger.Info("processing data", "data", data)
		// Log entry includes request_id field
	}(ctx)
}
```

**❌ Mistake 3: Not configuring logging in tests**

```go
// BAD: Tests use default logger (text format, wrong level)
func TestUserService_CreateUser(t *testing.T) {
	// No logger initialization - test output messy
	service := NewUserService(mockRepo)
	err := service.CreateUser(context.Background(), "test@example.com")
	// Test logs pollute output
}
```

**✅ Fix: Configure logging in test setup**

```go
// GOOD: Configure logger for tests (or discard logs)
func TestUserService_CreateUser(t *testing.T) {
	// Option 1: Set log level to suppress output
	slog.SetDefault(slog.New(slog.NewTextHandler(io.Discard, nil)))

	// Option 2: Capture logs for assertions
	var buf bytes.Buffer
	slog.SetDefault(slog.New(slog.NewJSONHandler(&buf, nil)))

	service := NewUserService(mockRepo)
	err := service.CreateUser(context.Background(), "test@example.com")

	// Can assert on log content if needed
}
```

### 2.3 Alternative Approaches

**Alternative 1: zerolog for High Performance**

zerolog provides zero-allocation JSON logging, ideal for high-throughput services where logging overhead matters[^10].

*Pros:* Fastest JSON logger, zero allocations, sub-microsecond latency
*Cons:* External dependency, less idiomatic API than slog
*Use When:* Logging is a performance bottleneck (>100K logs/sec)

**Alternative 2: zap for Structured Logging**

Uber's zap offers strongly-typed logging with excellent performance[^11].

*Pros:* Great performance, strongly-typed fields, mature ecosystem
*Cons:* More complex API, external dependency
*Use When:* Need strongly-typed logging or migrating from existing zap codebase

### 2.4 Decision Criteria

**Use slog when:**
- Go 1.21+ project (standard library preferred)
- Standard logging needs (info, debug, error levels)
- Want zero external dependencies
- Context-based request tracing sufficient

**Use zerolog when:**
- Logging throughput >100K logs/second
- Every allocation matters (ultra-low-latency services)
- Need zero-allocation guarantee

**Use zap when:**
- Migrating existing zap codebase
- Need strongly-typed field validation at compile time
- Prefer sugared (easy) and structured (fast) logger modes

---

## 3. Caching Strategies

### 3.1 Recommended Approach: Redis with go-redis Client

Redis with the `go-redis/redis` client provides production-grade distributed caching with connection pooling, pipelining, and goroutine-safe operations[^3][^12]. The cache-aside pattern balances performance and data freshness.

**Core Benefits:**
- **Distributed:** Shared cache across multiple service instances
- **Goroutine-Safe:** Connection pool handles concurrent access
- **Feature-Rich:** TTL, pub/sub, pipelining, Lua scripts
- **Battle-Tested:** Used by major production systems at scale

### 3.2 Implementation Example

```go
// File: internal/cache/redis.go
package cache

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/redis/go-redis/v9"
)

// Cache provides Redis-based caching with JSON serialization.
type Cache struct {
	client *redis.Client
}

// NewCache creates a new Redis cache client.
func NewCache(addr, password string, db int) *Cache {
	client := redis.NewClient(&redis.Options{
		Addr:     addr,     // "localhost:6379"
		Password: password, // "" for no password
		DB:       db,       // 0 is default DB

		// Connection pool configuration
		PoolSize:     10,              // Max concurrent connections
		MinIdleConns: 2,               // Min idle connections to maintain
		MaxRetries:   3,               // Retry failed commands
		DialTimeout:  5 * time.Second, // Connection timeout
		ReadTimeout:  3 * time.Second, // Read operation timeout
		WriteTimeout: 3 * time.Second, // Write operation timeout
	})

	return &Cache{client: client}
}

// Get retrieves value from cache, returns nil if not found.
func (c *Cache) Get(ctx context.Context, key string) ([]byte, error) {
	val, err := c.client.Get(ctx, key).Bytes()
	if err == redis.Nil {
		return nil, nil // Key does not exist (cache miss)
	}
	if err != nil {
		return nil, fmt.Errorf("cache get failed: %w", err)
	}
	return val, nil
}

// Set stores value in cache with TTL.
func (c *Cache) Set(ctx context.Context, key string, value interface{}, ttl time.Duration) error {
	// Serialize value to JSON
	data, err := json.Marshal(value)
	if err != nil {
		return fmt.Errorf("failed to marshal value: %w", err)
	}

	if err := c.client.Set(ctx, key, data, ttl).Err(); err != nil {
		return fmt.Errorf("cache set failed: %w", err)
	}

	return nil
}

// Delete removes key from cache.
func (c *Cache) Delete(ctx context.Context, key string) error {
	if err := c.client.Del(ctx, key).Err(); err != nil {
		return fmt.Errorf("cache delete failed: %w", err)
	}
	return nil
}

// Exists checks if key exists in cache.
func (c *Cache) Exists(ctx context.Context, key string) (bool, error) {
	count, err := c.client.Exists(ctx, key).Result()
	if err != nil {
		return false, fmt.Errorf("cache exists check failed: %w", err)
	}
	return count > 0, nil
}

// Close closes the Redis connection pool.
func (c *Cache) Close() error {
	return c.client.Close()
}
```

**Cache-aside pattern in repository:**

```go
// File: internal/repository/user_repository.go
package repository

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"time"

	"github.com/example/project/internal/cache"
	"github.com/example/project/internal/domain"
)

type UserRepository struct {
	db    *sql.DB
	cache *cache.Cache
}

func (r *UserRepository) GetByID(ctx context.Context, userID int64) (*domain.User, error) {
	cacheKey := fmt.Sprintf("user:%d", userID)

	// 1. Check cache first (cache-aside pattern)
	cached, err := r.cache.Get(ctx, cacheKey)
	if err != nil {
		// Log cache error but continue (degrade gracefully)
		slog.WarnContext(ctx, "cache get failed, querying database",
			"user_id", userID,
			"error", err,
		)
	} else if cached != nil {
		// Cache hit - deserialize and return
		var user domain.User
		if err := json.Unmarshal(cached, &user); err != nil {
			slog.WarnContext(ctx, "cache unmarshal failed",
				"user_id", userID,
				"error", err,
			)
		} else {
			return &user, nil
		}
	}

	// 2. Cache miss - load from database
	var user domain.User
	query := `SELECT id, email, name, created_at FROM users WHERE id = $1`

	err = r.db.QueryRowContext(ctx, query, userID).Scan(
		&user.ID,
		&user.Email,
		&user.Name,
		&user.CreatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, nil // User not found
	}
	if err != nil {
		return nil, fmt.Errorf("database query failed: %w", err)
	}

	// 3. Populate cache for next request (async, don't block)
	go func() {
		if err := r.cache.Set(context.Background(), cacheKey, user, 5*time.Minute); err != nil {
			slog.Warn("failed to cache user",
				"user_id", userID,
				"error", err,
			)
		}
	}()

	return &user, nil
}
```

### 3.2.1 Cache Client Initialization Patterns

#### Pattern 1: Singleton Cache Client (Recommended)

Create single Redis client at application startup, share across goroutines via connection pool[^12].

```go
// File: cmd/server/main.go
package main

import (
	"context"
	"log"
	"log/slog"

	"github.com/example/project/internal/cache"
	"github.com/example/project/internal/config"
)

func main() {
	cfg := config.MustLoad()
	logging.InitLogger(cfg.Debug)

	// Initialize Redis cache (singleton pattern)
	slog.Info("initializing redis cache", "addr", cfg.RedisAddr)

	redisCache := cache.NewCache(cfg.RedisAddr, cfg.RedisPassword, cfg.RedisDB)

	// Test connection
	ctx := context.Background()
	if err := redisCache.client.Ping(ctx).Err(); err != nil {
		log.Fatalf("failed to connect to redis: %v", err)
	}

	slog.Info("redis connection established")

	// Use cache throughout application
	userRepo := repository.NewUserRepository(db, redisCache)

	// Cleanup on shutdown
	defer func() {
		slog.Info("closing redis connection")
		if err := redisCache.Close(); err != nil {
			slog.Error("failed to close redis", "error", err)
		}
	}()

	// Start server...
}
```

**Benefits:**
- ✅ Single connection pool for entire application
- ✅ Maximum connection reuse, minimal overhead
- ✅ Goroutine-safe by default (connection pool handles concurrency)

**Use When:** Production applications (default recommendation)

#### Pattern 2: Dependency-Injected Cache (Testing-Friendly)

Pass cache as interface for easy mocking in tests[^13].

```go
// File: internal/cache/cache.go
package cache

import (
	"context"
	"time"
)

// Cacher is the interface for cache operations.
// Enables mocking in tests without Redis dependency.
type Cacher interface {
	Get(ctx context.Context, key string) ([]byte, error)
	Set(ctx context.Context, key string, value interface{}, ttl time.Duration) error
	Delete(ctx context.Context, key string) error
	Exists(ctx context.Context, key string) (bool, error)
}

// Ensure RedisCache implements Cacher
var _ Cacher = (*Cache)(nil)

// File: internal/repository/user_repository.go
type UserRepository struct {
	db    *sql.DB
	cache cache.Cacher  // Interface, not concrete type
}

func NewUserRepository(db *sql.DB, cache cache.Cacher) *UserRepository {
	return &UserRepository{
		db:    db,
		cache: cache,
	}
}
```

**Testing with mock cache:**

```go
// File: internal/repository/user_repository_test.go
package repository

import (
	"context"
	"testing"
	"time"
)

// MockCache implements cache.Cacher for testing
type MockCache struct {
	store map[string][]byte
}

func (m *MockCache) Get(ctx context.Context, key string) ([]byte, error) {
	return m.store[key], nil
}

func (m *MockCache) Set(ctx context.Context, key string, value interface{}, ttl time.Duration) error {
	// Simplified mock - just store as-is
	m.store[key] = value.([]byte)
	return nil
}

func TestUserRepository_GetByID(t *testing.T) {
	mockCache := &MockCache{store: make(map[string][]byte)}
	mockDB := setupMockDB()  // Not shown

	repo := NewUserRepository(mockDB, mockCache)

	user, err := repo.GetByID(context.Background(), 123)
	// Test assertions...
}
```

**Benefits:**
- ✅ Easy to mock for unit tests (no Redis required)
- ✅ Interface enables alternative cache implementations
- ✅ Explicit dependency (no global state)

**Use When:** Applications requiring extensive unit testing or multiple cache backends

### 3.2.2 Connection Pool Configuration Best Practices

Redis connection pool settings significantly impact performance and reliability[^12][^14].

```go
import "github.com/redis/go-redis/v9"

// Production-optimized configuration
client := redis.NewClient(&redis.Options{
	Addr:     "redis:6379",
	Password: "", // Set in production

	// Connection pool
	PoolSize:     10,              // Max concurrent connections
	// Scale based on: (expected_concurrent_requests / 2)
	// Example: 100 concurrent requests → 10 connections sufficient

	MinIdleConns: 2,               // Maintain 2 idle connections
	// Reduces latency for new requests (connection already established)

	// Timeouts
	DialTimeout:  5 * time.Second, // Connection establishment timeout
	ReadTimeout:  3 * time.Second, // Read operation timeout
	WriteTimeout: 3 * time.Second, // Write operation timeout

	// Retry behavior
	MaxRetries:      3,                      // Retry failed commands
	MinRetryBackoff: 8 * time.Millisecond,  // Min wait between retries
	MaxRetryBackoff: 512 * time.Millisecond, // Max wait between retries

	// Connection lifecycle
	PoolTimeout:  4 * time.Second,  // Max wait time for connection from pool
	IdleTimeout:  5 * time.Minute,  // Close idle connections after this time
	MaxConnAge:   30 * time.Minute, // Close connections older than this
})
```

**Configuration Guidelines:**

| Setting | Recommended Value | Rationale |
|---------|------------------|-----------|
| `PoolSize` | `concurrent_requests / 2` | Each request uses connection briefly |
| `MinIdleConns` | `2-5` | Reduces latency for new requests |
| `DialTimeout` | `5s` | Balance between retry speed and giving Redis time |
| `ReadTimeout` | `3s` | Fast failure for read operations |
| `WriteTimeout` | `3s` | Fast failure for write operations |
| `MaxRetries` | `3` | Tolerate transient network issues |
| `IdleTimeout` | `5m` | Close unused connections, free resources |

### 3.3 Alternative Approaches

**Alternative 1: In-Memory Cache (sync.Map or ristretto)**

Use Go's `sync.Map` or `github.com/dgraph-io/ristretto` for single-instance deployments[^15].

*Pros:* Sub-millisecond latency, no network overhead, no external dependency
*Cons:* Not shared across instances, data lost on restart, memory-bound capacity
*Use When:* Development environment, single-instance deployment, or second-level cache

**Alternative 2: Write-Through Cache**

Write to cache and database simultaneously.

*Pros:* Cache always up-to-date, simpler read logic
*Cons:* Higher write latency, wasted cache writes for rarely-read data
*Use When:* Read-heavy workloads (>90% reads) with infrequent writes

### 3.4 Decision Criteria

| Pattern | Best For | Cache Freshness | Write Performance |
|---------|----------|----------------|-------------------|
| **Cache-Aside** | **General use** | ✅ Configurable TTL | ✅ Fast (no cache write) |
| Write-Through | Read-heavy (>90%) | ✅✅ Always fresh | ⚠️ Slower (dual write) |
| In-Memory | Single instance | ✅ Instant | ✅ Instant |

**TTL Selection Guidelines:**
- **User profiles:** 5 minutes - infrequently changed
- **Product catalog:** 10 minutes - stable data
- **Real-time inventory:** 10 seconds - frequently updated
- **Session data:** 30 minutes - bound to session lifetime

---

## 4. Data Access Patterns

### 4.1 Recommended Approach: database/sql with Repository Pattern

Go's `database/sql` package with the repository pattern provides Clean Architecture compliance while leveraging the standard library[^4][^16]. For enhanced scanning capabilities, `jmoiron/sqlx` extends database/sql with minimal overhead.

**Core Benefits:**
- **Standard Library:** database/sql is battle-tested, stable, well-documented
- **Dependency Inversion:** Repository interface defined in domain layer, implementation in infrastructure
- **Testability:** Mock repositories in unit tests without database overhead
- **Explicit SQL:** Full control over queries, no hidden ORM behavior
- **Connection Pooling:** Built-in connection pool with tunable settings

### 4.2 Database Connection Initialization

#### Pattern 1: Singleton DB Connection (Recommended)

Create single `*sql.DB` at application startup, share across goroutines via connection pool[^17].

```go
// File: internal/database/postgres.go
package database

import (
	"database/sql"
	"fmt"
	"time"

	_ "github.com/lib/pq" // PostgreSQL driver
)

// Config holds database connection configuration.
type Config struct {
	URL              string
	MaxOpenConns     int
	MaxIdleConns     int
	ConnMaxLifetime  time.Duration
	ConnMaxIdleTime  time.Duration
}

// NewPostgresDB creates a new PostgreSQL database connection.
func NewPostgresDB(cfg Config) (*sql.DB, error) {
	db, err := sql.Open("postgres", cfg.URL)
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	// Connection pool configuration
	db.SetMaxOpenConns(cfg.MaxOpenConns)       // Max concurrent connections
	db.SetMaxIdleConns(cfg.MaxIdleConns)       // Max idle connections to keep
	db.SetConnMaxLifetime(cfg.ConnMaxLifetime) // Max connection lifetime
	db.SetConnMaxIdleTime(cfg.ConnMaxIdleTime) // Max idle time before close

	// Test connection
	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	return db, nil
}

// File: cmd/server/main.go
package main

import (
	"log/slog"
	"time"

	"github.com/example/project/internal/config"
	"github.com/example/project/internal/database"
)

func main() {
	cfg := config.MustLoad()
	logging.InitLogger(cfg.Debug)

	// Initialize database connection (singleton pattern)
	slog.Info("initializing database connection")

	db, err := database.NewPostgresDB(database.Config{
		URL:              cfg.DatabaseURL,
		MaxOpenConns:     cfg.DBMaxOpenConns,
		MaxIdleConns:     cfg.DBMaxIdleConns,
		ConnMaxLifetime:  cfg.DBConnMaxLifetime,
		ConnMaxIdleTime:  5 * time.Minute,
	})
	if err != nil {
		log.Fatalf("failed to connect to database: %v", err)
	}

	slog.Info("database connection established",
		"max_open_conns", cfg.DBMaxOpenConns,
		"max_idle_conns", cfg.DBMaxIdleConns,
	)

	// Use db throughout application
	userRepo := repository.NewUserRepository(db)

	// Cleanup on shutdown
	defer func() {
		slog.Info("closing database connection")
		if err := db.Close(); err != nil {
			slog.Error("failed to close database", "error", err)
		}
	}()

	// Start server...
}
```

**Benefits:**
- ✅ Single connection pool for entire application
- ✅ Goroutine-safe (database/sql handles concurrency)
- ✅ Automatic connection reuse and lifecycle management

**Use When:** Production applications (default recommendation)

### 4.3 Repository Pattern Implementation

#### Repository Interface (Domain Layer)

```go
// File: internal/domain/repository/user_repository.go
package repository

import (
	"context"
	"github.com/example/project/internal/domain/entity"
)

// UserRepository defines the interface for user persistence (port).
// Domain layer defines WHAT operations needed, infrastructure defines HOW.
// This achieves Dependency Inversion Principle (DIP).
type UserRepository interface {
	GetByID(ctx context.Context, userID int64) (*entity.User, error)
	GetByEmail(ctx context.Context, email string) (*entity.User, error)
	List(ctx context.Context, limit, offset int) ([]*entity.User, error)
	Save(ctx context.Context, user *entity.User) error
	Delete(ctx context.Context, userID int64) error
	Exists(ctx context.Context, userID int64) (bool, error)
}
```

#### Repository Implementation (Infrastructure Layer)

```go
// File: internal/infrastructure/postgres/user_repository.go
package postgres

import (
	"context"
	"database/sql"
	"fmt"

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
	query := `SELECT id, email, name, created_at, updated_at FROM users WHERE id = $1`

	var user entity.User
	err := r.db.QueryRowContext(ctx, query, userID).Scan(
		&user.ID,
		&user.Email,
		&user.Name,
		&user.CreatedAt,
		&user.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, nil // User not found (not an error)
	}
	if err != nil {
		return nil, fmt.Errorf("failed to get user by ID: %w", err)
	}

	return &user, nil
}

// GetByEmail retrieves a user by email address.
func (r *UserRepo) GetByEmail(ctx context.Context, email string) (*entity.User, error) {
	query := `SELECT id, email, name, created_at, updated_at FROM users WHERE email = $1`

	var user entity.User
	err := r.db.QueryRowContext(ctx, query, email).Scan(
		&user.ID,
		&user.Email,
		&user.Name,
		&user.CreatedAt,
		&user.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, fmt.Errorf("failed to get user by email: %w", err)
	}

	return &user, nil
}

// List retrieves users with pagination.
func (r *UserRepo) List(ctx context.Context, limit, offset int) ([]*entity.User, error) {
	query := `SELECT id, email, name, created_at, updated_at FROM users ORDER BY id LIMIT $1 OFFSET $2`

	rows, err := r.db.QueryContext(ctx, query, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to list users: %w", err)
	}
	defer rows.Close()

	var users []*entity.User
	for rows.Next() {
		var user entity.User
		if err := rows.Scan(&user.ID, &user.Email, &user.Name, &user.CreatedAt, &user.UpdatedAt); err != nil {
			return nil, fmt.Errorf("failed to scan user: %w", err)
		}
		users = append(users, &user)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("row iteration error: %w", err)
	}

	return users, nil
}

// Save persists a user entity (create or update).
func (r *UserRepo) Save(ctx context.Context, user *entity.User) error {
	if user.ID == 0 {
		// Create new user
		query := `INSERT INTO users (email, name, created_at, updated_at) VALUES ($1, $2, NOW(), NOW()) RETURNING id`
		err := r.db.QueryRowContext(ctx, query, user.Email, user.Name).Scan(&user.ID)
		if err != nil {
			return fmt.Errorf("failed to create user: %w", err)
		}
		return nil
	}

	// Update existing user
	query := `UPDATE users SET email = $1, name = $2, updated_at = NOW() WHERE id = $3`
	_, err := r.db.ExecContext(ctx, query, user.Email, user.Name, user.ID)
	if err != nil {
		return fmt.Errorf("failed to update user: %w", err)
	}

	return nil
}

// Delete removes a user from persistence.
func (r *UserRepo) Delete(ctx context.Context, userID int64) error {
	query := `DELETE FROM users WHERE id = $1`

	result, err := r.db.ExecContext(ctx, query, userID)
	if err != nil {
		return fmt.Errorf("failed to delete user: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		// User not found (can choose to return error or ignore)
		return nil
	}

	return nil
}

// Exists checks if a user exists.
func (r *UserRepo) Exists(ctx context.Context, userID int64) (bool, error) {
	query := `SELECT EXISTS(SELECT 1 FROM users WHERE id = $1)`

	var exists bool
	err := r.db.QueryRowContext(ctx, query, userID).Scan(&exists)
	if err != nil {
		return false, fmt.Errorf("failed to check user existence: %w", err)
	}

	return exists, nil
}
```

### 4.4 Repository Dependency Injection

#### Constructor Injection Pattern

```go
// File: internal/service/user_service.go
package service

import (
	"context"
	"fmt"
	"log/slog"

	"github.com/example/project/internal/domain/entity"
	"github.com/example/project/internal/domain/repository"
)

// UserService handles user business logic.
type UserService struct {
	repo repository.UserRepository
}

// NewUserService creates a new user service with repository dependency.
func NewUserService(repo repository.UserRepository) *UserService {
	return &UserService{
		repo: repo,
	}
}

// CreateUser creates a new user.
func (s *UserService) CreateUser(ctx context.Context, email, name string) (*entity.User, error) {
	slog.InfoContext(ctx, "creating user", "email", email)

	// Check if email already exists
	existing, err := s.repo.GetByEmail(ctx, email)
	if err != nil {
		return nil, fmt.Errorf("failed to check existing user: %w", err)
	}
	if existing != nil {
		return nil, fmt.Errorf("user with email %s already exists", email)
	}

	// Create user entity
	user := &entity.User{
		Email: email,
		Name:  name,
	}

	// Save via repository
	if err := s.repo.Save(ctx, user); err != nil {
		return nil, fmt.Errorf("failed to save user: %w", err)
	}

	slog.InfoContext(ctx, "user created successfully", "user_id", user.ID)

	return user, nil
}
```

#### Usage in HTTP Handlers

```go
// File: internal/http/handler/user_handler.go
package handler

import (
	"encoding/json"
	"net/http"

	"github.com/example/project/internal/service"
)

type UserHandler struct {
	userService *service.UserService
}

func NewUserHandler(userService *service.UserService) *UserHandler {
	return &UserHandler{
		userService: userService,
	}
}

type CreateUserRequest struct {
	Email string `json:"email"`
	Name  string `json:"name"`
}

func (h *UserHandler) CreateUser(w http.ResponseWriter, r *http.Request) {
	var req CreateUserRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "invalid request body", http.StatusBadRequest)
		return
	}

	user, err := h.userService.CreateUser(r.Context(), req.Email, req.Name)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteStatus(http.StatusCreated)
	json.NewEncoder(w).Encode(user)
}
```

#### Dependency Wiring in main.go

```go
// File: cmd/server/main.go
package main

import (
	"github.com/example/project/internal/http/handler"
	"github.com/example/project/internal/infrastructure/postgres"
	"github.com/example/project/internal/service"
)

func main() {
	// ... config, logging, database initialization ...

	// Wire dependencies (manual dependency injection)
	userRepo := postgres.NewUserRepository(db)
	userService := service.NewUserService(userRepo)
	userHandler := handler.NewUserHandler(userService)

	// Setup HTTP routes
	mux := http.NewServeMux()
	mux.HandleFunc("POST /users", userHandler.CreateUser)
	mux.HandleFunc("GET /users/{id}", userHandler.GetUser)

	// Start server...
}
```

### 4.5 Testing with Mocked Repositories

```go
// File: internal/service/user_service_test.go
package service

import (
	"context"
	"testing"

	"github.com/example/project/internal/domain/entity"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// MockUserRepository is a mock implementation of repository.UserRepository
type MockUserRepository struct {
	mock.Mock
}

func (m *MockUserRepository) GetByID(ctx context.Context, userID int64) (*entity.User, error) {
	args := m.Called(ctx, userID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*entity.User), args.Error(1)
}

func (m *MockUserRepository) GetByEmail(ctx context.Context, email string) (*entity.User, error) {
	args := m.Called(ctx, email)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*entity.User), args.Error(1)
}

func (m *MockUserRepository) Save(ctx context.Context, user *entity.User) error {
	args := m.Called(ctx, user)
	return args.Error(0)
}

// Test cases using mock
func TestUserService_CreateUser_Success(t *testing.T) {
	// Setup
	mockRepo := new(MockUserRepository)
	service := NewUserService(mockRepo)

	// Mock expectations
	mockRepo.On("GetByEmail", mock.Anything, "test@example.com").Return(nil, nil) // No existing user
	mockRepo.On("Save", mock.Anything, mock.AnythingOfType("*entity.User")).Return(nil)

	// Execute
	user, err := service.CreateUser(context.Background(), "test@example.com", "Test User")

	// Assert
	assert.NoError(t, err)
	assert.NotNil(t, user)
	assert.Equal(t, "test@example.com", user.Email)
	assert.Equal(t, "Test User", user.Name)

	mockRepo.AssertExpectations(t)
}

func TestUserService_CreateUser_DuplicateEmail(t *testing.T) {
	// Setup
	mockRepo := new(MockUserRepository)
	service := NewUserService(mockRepo)

	existingUser := &entity.User{
		ID:    123,
		Email: "test@example.com",
		Name:  "Existing User",
	}

	// Mock expectations
	mockRepo.On("GetByEmail", mock.Anything, "test@example.com").Return(existingUser, nil)

	// Execute
	user, err := service.CreateUser(context.Background(), "test@example.com", "New User")

	// Assert
	assert.Error(t, err)
	assert.Nil(t, user)
	assert.Contains(t, err.Error(), "already exists")

	mockRepo.AssertExpectations(t)
}
```

### 4.6 Connection Pool Configuration Best Practices

```go
import "database/sql"

// Production-optimized database connection pool
db.SetMaxOpenConns(25)
// Max concurrent database connections
// Scale based on: (expected_concurrent_requests * avg_query_duration)
// Example: 100 RPS * 0.1s query = 10 concurrent queries → 25 provides headroom

db.SetMaxIdleConns(5)
// Max idle connections to keep alive
// Reduces latency for new requests (connection already established)
// Too high: wastes database resources
// Too low: connection establishment overhead

db.SetConnMaxLifetime(5 * time.Minute)
// Max connection lifetime (before recycling)
// Prevents stale connections, aligns with database timeouts
// PostgreSQL default: 8 hours (but 5-15 minutes safer for apps)

db.SetConnMaxIdleTime(5 * time.Minute)
// Max idle time before closing idle connections
// Frees resources when load decreases
// Balance between responsiveness and resource usage
```

**Configuration Guidelines:**

| Setting | Recommended Value | Rationale |
|---------|------------------|-----------|
| `MaxOpenConns` | `concurrent_requests * avg_duration * 2` | Handles request spikes |
| `MaxIdleConns` | `MaxOpenConns / 5` | Balance latency vs. resources |
| `ConnMaxLifetime` | `5m` | Prevent stale connections |
| `ConnMaxIdleTime` | `5m` | Free unused connections |

### 4.7 Decision Criteria

**Use database/sql when:**
- Want standard library (no external ORM dependency)
- Need full control over SQL queries
- Optimizing for performance (no ORM abstraction overhead)

**Use sqlx when:**
- Need enhanced scanning (struct tags, named parameters)
- Want to reduce boilerplate but stay close to SQL
- Migration from database/sql (drop-in replacement)

**Use GORM when:**
- Rapid prototyping (auto-migrations, associations)
- Team prefers ORM convenience over raw SQL
- Willing to accept ORM learning curve and hidden behavior

---



## 9. Error Handling and Validation

### 9.1 Type-Safe Error Handling with Sentinel Errors and Custom Types

Go 1.13+ introduced `errors.Is` and `errors.As` for type-safe error handling[^31][^32]. Combined with sentinel errors and custom error types, this enables structured error handling without string matching.

**Core Benefits:**
- **Type Safety:** Errors checked by type, not string comparison
- **Error Wrapping:** `%w` verb preserves error chain for root cause analysis
- **Error Inspection:** `errors.Is` checks error chain, `errors.As` extracts typed errors
- **Context Preservation:** Wrap errors with context while maintaining original error

#### Sentinel Errors for Expected Conditions

```go
// File: internal/domain/errors/errors.go
package errors

import (
	"errors"
	"fmt"
)

// Sentinel errors for expected domain conditions.
// Use errors.Is() to check for these errors.
var (
	// ErrNotFound indicates requested entity does not exist.
	ErrNotFound = errors.New("entity not found")

	// ErrAlreadyExists indicates entity with unique constraint already exists.
	ErrAlreadyExists = errors.New("entity already exists")

	// ErrInvalidInput indicates client provided invalid input.
	ErrInvalidInput = errors.New("invalid input")

	// ErrUnauthorized indicates request lacks valid authentication.
	ErrUnauthorized = errors.New("unauthorized")

	// ErrForbidden indicates authenticated user lacks permission.
	ErrForbidden = errors.New("forbidden")

	// ErrConflict indicates operation conflicts with current state.
	ErrConflict = errors.New("conflict")

	// ErrRateLimitExceeded indicates too many requests.
	ErrRateLimitExceeded = errors.New("rate limit exceeded")
)

// ValidationError represents an input validation failure with field details.
type ValidationError struct {
	Field   string // Field name that failed validation
	Value   any    // Invalid value provided
	Message string // Human-readable error message
}

func (e *ValidationError) Error() string {
	return fmt.Sprintf("validation failed for field '%s': %s (value: %v)", e.Field, e.Message, e.Value)
}

// NewValidationError creates a new validation error.
func NewValidationError(field string, value any, message string) *ValidationError {
	return &ValidationError{
		Field:   field,
		Value:   value,
		Message: message,
	}
}

// AuthenticationError represents authentication failure with details.
type AuthenticationError struct {
	Reason string // Reason for authentication failure
	UserID int64  // User ID if known, 0 if unknown
}

func (e *AuthenticationError) Error() string {
	if e.UserID != 0 {
		return fmt.Sprintf("authentication failed for user %d: %s", e.UserID, e.Reason)
	}
	return fmt.Sprintf("authentication failed: %s", e.Reason)
}

// DatabaseError represents a database operation failure.
type DatabaseError struct {
	Operation string // Operation that failed (SELECT, INSERT, UPDATE, DELETE)
	Table     string // Database table
	Err       error  // Underlying database error
}

func (e *DatabaseError) Error() string {
	return fmt.Sprintf("database %s failed on table '%s': %v", e.Operation, e.Table, e.Err)
}

// Unwrap returns the underlying error for errors.Is/As compatibility.
func (e *DatabaseError) Unwrap() error {
	return e.Err
}

// ExternalServiceError represents failure calling external API.
type ExternalServiceError struct {
	Service    string // Service name (Stripe, Twilio, AWS S3)
	Operation  string // API operation (create_payment, send_sms)
	StatusCode int    // HTTP status code (if applicable)
	Err        error  // Underlying error
}

func (e *ExternalServiceError) Error() string {
	if e.StatusCode > 0 {
		return fmt.Sprintf("%s API %s failed (HTTP %d): %v", e.Service, e.Operation, e.StatusCode, e.Err)
	}
	return fmt.Sprintf("%s API %s failed: %v", e.Service, e.Operation, e.Err)
}

func (e *ExternalServiceError) Unwrap() error {
	return e.Err
}
```

**Usage with errors.Is and errors.As:**

```go
// File: internal/repository/user_repository.go
package repository

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/example/project/internal/domain/entity"
	"github.com/example/project/internal/domain/errors"
)

type UserRepository struct {
	db *sql.DB
}

func NewUserRepository(db *sql.DB) *UserRepository {
	return &UserRepository{db: db}
}

// GetByID retrieves user by ID, returns errors.ErrNotFound if not exists.
func (r *UserRepository) GetByID(ctx context.Context, userID int64) (*entity.User, error) {
	query := `SELECT id, email, name FROM users WHERE id = $1`

	var user entity.User
	err := r.db.QueryRowContext(ctx, query, userID).Scan(&user.ID, &user.Email, &user.Name)

	if err == sql.ErrNoRows {
		// Wrap sentinel error with context
		return nil, fmt.Errorf("user %d: %w", userID, errors.ErrNotFound)
	}
	if err != nil {
		// Wrap database error with context
		return nil, &errors.DatabaseError{
			Operation: "SELECT",
			Table:     "users",
			Err:       err,
		}
	}

	return &user, nil
}

// Create creates new user, returns errors.ErrAlreadyExists if email taken.
func (r *UserRepository) Create(ctx context.Context, user *entity.User) error {
	query := `INSERT INTO users (email, name) VALUES ($1, $2) RETURNING id`

	err := r.db.QueryRowContext(ctx, query, user.Email, user.Name).Scan(&user.ID)
	if err != nil {
		// Check for unique constraint violation (PostgreSQL error code 23505)
		if isUniqueViolation(err) {
			return fmt.Errorf("email %s: %w", user.Email, errors.ErrAlreadyExists)
		}

		return &errors.DatabaseError{
			Operation: "INSERT",
			Table:     "users",
			Err:       err,
		}
	}

	return nil
}

// isUniqueViolation checks if error is PostgreSQL unique constraint violation.
func isUniqueViolation(err error) bool {
	// PostgreSQL-specific check (simplified - use lib/pq for production)
	return err != nil && (err.Error() == "pq: duplicate key value violates unique constraint \"users_email_key\"")
}
```

**HTTP handler with type-safe error handling:**

```go
// File: internal/http/handler/user_handler.go
package handler

import (
	"encoding/json"
	"errors"
	"net/http"
	"strconv"

	domainerrors "github.com/example/project/internal/domain/errors"
	"github.com/example/project/internal/repository"
)

type UserHandler struct {
	repo *repository.UserRepository
}

func NewUserHandler(repo *repository.UserRepository) *UserHandler {
	return &UserHandler{repo: repo}
}

// GetUser retrieves user by ID.
func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
	// Parse user ID from URL
	userIDStr := r.PathValue("id")
	userID, err := strconv.ParseInt(userIDStr, 10, 64)
	if err != nil {
		h.writeError(w, domainerrors.NewValidationError("id", userIDStr, "must be valid integer"), http.StatusBadRequest)
		return
	}

	// Fetch user from repository
	user, err := h.repo.GetByID(r.Context(), userID)
	if err != nil {
		h.handleRepositoryError(w, err)
		return
	}

	// Success response
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(user)
}

// handleRepositoryError maps domain errors to HTTP status codes.
func (h *UserHandler) handleRepositoryError(w http.ResponseWriter, err error) {
	// Check for sentinel errors using errors.Is
	if errors.Is(err, domainerrors.ErrNotFound) {
		h.writeError(w, err, http.StatusNotFound)
		return
	}
	if errors.Is(err, domainerrors.ErrAlreadyExists) {
		h.writeError(w, err, http.StatusConflict)
		return
	}
	if errors.Is(err, domainerrors.ErrUnauthorized) {
		h.writeError(w, err, http.StatusUnauthorized)
		return
	}
	if errors.Is(err, domainerrors.ErrForbidden) {
		h.writeError(w, err, http.StatusForbidden)
		return
	}

	// Check for typed errors using errors.As
	var validationErr *domainerrors.ValidationError
	if errors.As(err, &validationErr) {
		h.writeError(w, validationErr, http.StatusBadRequest)
		return
	}

	var dbErr *domainerrors.DatabaseError
	if errors.As(err, &dbErr) {
		// Database errors are internal server errors
		h.writeError(w, errors.New("internal server error"), http.StatusInternalServerError)
		// Log full database error for debugging (don't expose to client)
		slog.Error("database error", "operation", dbErr.Operation, "table", dbErr.Table, "error", dbErr.Err)
		return
	}

	// Default: internal server error
	h.writeError(w, errors.New("internal server error"), http.StatusInternalServerError)
}

// ErrorResponse represents API error response.
type ErrorResponse struct {
	Error   string `json:"error"`
	Message string `json:"message,omitempty"`
	Field   string `json:"field,omitempty"` // For validation errors
}

// writeError writes JSON error response.
func (h *UserHandler) writeError(w http.ResponseWriter, err error, statusCode int) {
	response := ErrorResponse{
		Error: http.StatusText(statusCode),
	}

	// Extract validation error details if available
	var validationErr *domainerrors.ValidationError
	if errors.As(err, &validationErr) {
		response.Message = validationErr.Message
		response.Field = validationErr.Field
	} else {
		response.Message = err.Error()
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(response)
}
```

**Benefits:**
- ✅ **Type Safety:** Errors checked by type (compile-time safety)
- ✅ **Context Preservation:** Error wrapping maintains full error chain
- ✅ **Separation of Concerns:** Domain errors defined in domain layer
- ✅ **Testability:** Easy to test error conditions with sentinel errors

**Drawbacks:**
- ❌ **Boilerplate:** Must define custom error types for each domain error
- ❌ **Verbose:** More code than string-based error matching

**Use When:**
- Production applications requiring robust error handling
- API servers mapping errors to HTTP status codes
- Complex error conditions with additional context (fields, user IDs, etc.)

### 9.2 Request/Response Validation in HTTP Handlers

HTTP handlers require validation of incoming requests (JSON bodies, query parameters, path parameters) before processing[^33][^34]. Integration with `go-playground/validator` provides declarative validation rules.

#### Gin Framework Validation Integration

```go
// File: internal/http/handler/user_handler_gin.go
package handler

import (
	"errors"
	"fmt"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	domainerrors "github.com/example/project/internal/domain/errors"
	"github.com/example/project/internal/service"
	"github.com/go-playground/validator/v10"
)

type UserHandlerGin struct {
	service *service.UserService
}

func NewUserHandlerGin(service *service.UserService) *UserHandlerGin {
	return &UserHandlerGin{service: service}
}

// CreateUserRequest represents POST /users request body.
type CreateUserRequest struct {
	Email string `json:"email" binding:"required,email,max=255"`
	Name  string `json:"name" binding:"required,min=2,max=100"`
	Age   int    `json:"age" binding:"required,gte=18,lte=120"`
}

// CreateUserResponse represents POST /users response.
type CreateUserResponse struct {
	ID    int64  `json:"id"`
	Email string `json:"email"`
	Name  string `json:"name"`
	Age   int    `json:"age"`
}

// CreateUser creates a new user (POST /users).
func (h *UserHandlerGin) CreateUser(c *gin.Context) {
	var req CreateUserRequest

	// Gin automatically validates using binding tags
	if err := c.ShouldBindJSON(&req); err != nil {
		h.handleValidationError(c, err)
		return
	}

	// Call service layer
	user, err := h.service.CreateUser(c.Request.Context(), req.Email, req.Name)
	if err != nil {
		h.handleServiceError(c, err)
		return
	}

	// Success response
	response := CreateUserResponse{
		ID:    user.ID,
		Email: user.Email,
		Name:  user.Name,
		Age:   req.Age,
	}

	c.JSON(http.StatusCreated, response)
}

// UpdateUserRequest represents PATCH /users/:id request body.
type UpdateUserRequest struct {
	Name *string `json:"name,omitempty" binding:"omitempty,min=2,max=100"`
	Age  *int    `json:"age,omitempty" binding:"omitempty,gte=18,lte=120"`
}

// UpdateUser updates existing user (PATCH /users/:id).
func (h *UserHandlerGin) UpdateUser(c *gin.Context) {
	// Validate path parameter
	userID, err := parseUserID(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Bad Request",
			"message": err.Error(),
		})
		return
	}

	// Validate request body
	var req UpdateUserRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		h.handleValidationError(c, err)
		return
	}

	// Check at least one field provided
	if req.Name == nil && req.Age == nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Bad Request",
			"message": "at least one field (name or age) required",
		})
		return
	}

	// Call service layer
	// user, err := h.service.UpdateUser(c.Request.Context(), userID, req)
	// ... handle error and return response
}

// ListUsersRequest represents GET /users query parameters.
type ListUsersRequest struct {
	Limit  int    `form:"limit" binding:"omitempty,min=1,max=100"`
	Offset int    `form:"offset" binding:"omitempty,min=0"`
	SortBy string `form:"sort_by" binding:"omitempty,oneof=name email created_at"`
	Order  string `form:"order" binding:"omitempty,oneof=asc desc"`
}

// ListUsers retrieves paginated user list (GET /users).
func (h *UserHandlerGin) ListUsers(c *gin.Context) {
	var req ListUsersRequest

	// Set defaults
	req.Limit = 20
	req.SortBy = "created_at"
	req.Order = "desc"

	// Bind query parameters (overrides defaults)
	if err := c.ShouldBindQuery(&req); err != nil {
		h.handleValidationError(c, err)
		return
	}

	// Call service layer
	// users, total, err := h.service.ListUsers(c.Request.Context(), req.Limit, req.Offset, req.SortBy, req.Order)
	// ... handle error and return response
}

// handleValidationError formats validator errors for API response.
func (h *UserHandlerGin) handleValidationError(c *gin.Context, err error) {
	var validationErrs validator.ValidationErrors
	if errors.As(err, &validationErrs) {
		// Extract first validation error
		firstErr := validationErrs[0]

		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Validation Failed",
			"field":   firstErr.Field(),
			"message": formatValidatorError(firstErr),
		})
		return
	}

	// JSON syntax error
	c.JSON(http.StatusBadRequest, gin.H{
		"error":   "Bad Request",
		"message": "invalid JSON format",
	})
}

// formatValidatorError creates human-readable error message.
func formatValidatorError(err validator.FieldError) string {
	switch err.Tag() {
	case "required":
		return fmt.Sprintf("%s is required", err.Field())
	case "email":
		return fmt.Sprintf("%s must be a valid email address", err.Field())
	case "min":
		return fmt.Sprintf("%s must be at least %s", err.Field(), err.Param())
	case "max":
		return fmt.Sprintf("%s must be at most %s", err.Field(), err.Param())
	case "gte":
		return fmt.Sprintf("%s must be %s or greater", err.Field(), err.Param())
	case "lte":
		return fmt.Sprintf("%s must be %s or less", err.Field(), err.Param())
	case "oneof":
		return fmt.Sprintf("%s must be one of: %s", err.Field(), err.Param())
	default:
		return fmt.Sprintf("%s failed validation '%s'", err.Field(), err.Tag())
	}
}

// handleServiceError maps service errors to HTTP responses.
func (h *UserHandlerGin) handleServiceError(c *gin.Context, err error) {
	if errors.Is(err, domainerrors.ErrNotFound) {
		c.JSON(http.StatusNotFound, gin.H{
			"error":   "Not Found",
			"message": err.Error(),
		})
		return
	}
	if errors.Is(err, domainerrors.ErrAlreadyExists) {
		c.JSON(http.StatusConflict, gin.H{
			"error":   "Conflict",
			"message": err.Error(),
		})
		return
	}

	var validationErr *domainerrors.ValidationError
	if errors.As(err, &validationErr) {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Validation Failed",
			"field":   validationErr.Field,
			"message": validationErr.Message,
		})
		return
	}

	// Default: internal server error
	c.JSON(http.StatusInternalServerError, gin.H{
		"error":   "Internal Server Error",
		"message": "an unexpected error occurred",
	})
}

// parseUserID validates and parses user ID from path parameter.
func parseUserID(idStr string) (int64, error) {
	id, err := strconv.ParseInt(idStr, 10, 64)
	if err != nil {
		return 0, fmt.Errorf("invalid user ID format: must be integer")
	}
	if id <= 0 {
		return 0, fmt.Errorf("invalid user ID: must be positive integer")
	}
	return id, nil
}
```

**Example API requests and responses:**

```bash
# Valid request
$ curl -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","name":"John Doe","age":30}'

{
  "id": 123,
  "email": "user@example.com",
  "name": "John Doe",
  "age": 30
}

# Invalid email format
$ curl -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{"email":"invalid-email","name":"John Doe","age":30}'

{
  "error": "Validation Failed",
  "field": "Email",
  "message": "Email must be a valid email address"
}

# Age below minimum
$ curl -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","name":"John Doe","age":15}'

{
  "error": "Validation Failed",
  "field": "Age",
  "message": "Age must be 18 or greater"
}

# Missing required field
$ curl -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","age":30}'

{
  "error": "Validation Failed",
  "field": "Name",
  "message": "Name is required"
}

# Invalid query parameter
$ curl http://localhost:8080/users?limit=999

{
  "error": "Validation Failed",
  "field": "Limit",
  "message": "Limit must be at most 100"
}
```

**Common validator tags:**

| Tag | Description | Example |
|-----|-------------|---------|
| `required` | Field must not be zero value | `binding:"required"` |
| `email` | Valid email address | `binding:"email"` |
| `url` | Valid URL | `binding:"url"` |
| `min`, `max` | Range validation (numbers, strings, slices) | `binding:"min=1,max=100"` |
| `gte`, `lte` | Greater/less than or equal | `binding:"gte=18,lte=120"` |
| `oneof` | Value must be one of options | `binding:"oneof=dev prod staging"` |
| `hostname_port` | Host:port format | `binding:"hostname_port"` |
| `uuid`, `uuid4` | UUID validation | `binding:"uuid4"` |
| `len`, `eq` | Exact length/value | `binding:"len=10"` |
| `lt`, `gt` | Comparison operators | `binding:"gt=0,lt=100"` |
| `ltefield`, `gtefield` | Compare to another field | `binding:"ltefield=MaxValue"` |

**Benefits:**
- ✅ **Declarative:** Validation rules in struct tags (co-located with fields)
- ✅ **Framework Integration:** Gin automatically validates using `binding` tags
- ✅ **Type Safety:** Request fields type-checked at compile time
- ✅ **Error Messages:** Consistent validation error format across endpoints

**Drawbacks:**
- ❌ **Framework Lock-In:** Tightly coupled to Gin framework
- ❌ **Tag Complexity:** Complex validation logic hard to express in tags

**Use When:**
- Using Gin web framework for HTTP API
- Need declarative request validation (10+ endpoints)
- Want automatic validation error formatting

---

### 9.3 Error Correlation with Distributed Tracing

In distributed systems, errors often span multiple services. Integrating error handling with distributed tracing (OpenTelemetry) enables correlation of errors across service boundaries[^35][^36].

**Core Benefits:**
- **Trace Context Propagation:** Errors linked to trace spans for end-to-end visibility
- **Root Cause Analysis:** Follow trace to identify where error originated across services
- **Error Sampling:** Sample all errors regardless of trace sampling rate
- **Structured Error Metadata:** Attach error details to span events for debugging

#### OpenTelemetry Error Integration

```go
// File: internal/telemetry/errors.go
package telemetry

import (
	"context"
	"errors"
	"fmt"

	domainerrors "github.com/example/project/internal/domain/errors"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/codes"
	"go.opentelemetry.io/otel/trace"
)

// RecordError records an error on the current span with structured attributes.
// Automatically extracts error type, message, and custom error fields.
func RecordError(ctx context.Context, err error, opts ...trace.EventOption) {
	span := trace.SpanFromContext(ctx)
	if !span.IsRecording() {
		return // No active span - skip recording
	}

	// Set span status to error
	span.SetStatus(codes.Error, err.Error())

	// Record error event with timestamp and attributes
	attrs := extractErrorAttributes(err)
	span.RecordError(err, append(opts, trace.WithAttributes(attrs...))...)
}

// extractErrorAttributes extracts structured attributes from custom error types.
func extractErrorAttributes(err error) []attribute.KeyValue {
	attrs := []attribute.KeyValue{
		attribute.String("error.type", fmt.Sprintf("%T", err)),
		attribute.String("error.message", err.Error()),
	}

	// Extract typed error attributes
	var validationErr *domainerrors.ValidationError
	if errors.As(err, &validationErr) {
		attrs = append(attrs,
			attribute.String("error.kind", "validation"),
			attribute.String("error.field", validationErr.Field),
			attribute.String("error.value", fmt.Sprintf("%v", validationErr.Value)),
		)
	}

	var dbErr *domainerrors.DatabaseError
	if errors.As(err, &dbErr) {
		attrs = append(attrs,
			attribute.String("error.kind", "database"),
			attribute.String("error.operation", dbErr.Operation),
			attribute.String("error.table", dbErr.Table),
		)
	}

	var externalErr *domainerrors.ExternalServiceError
	if errors.As(err, &externalErr) {
		attrs = append(attrs,
			attribute.String("error.kind", "external_service"),
			attribute.String("error.service", externalErr.Service),
			attribute.String("error.operation", externalErr.Operation),
			attribute.Int("error.status_code", externalErr.StatusCode),
		)
	}

	// Check for sentinel errors
	if errors.Is(err, domainerrors.ErrNotFound) {
		attrs = append(attrs, attribute.String("error.kind", "not_found"))
	} else if errors.Is(err, domainerrors.ErrUnauthorized) {
		attrs = append(attrs, attribute.String("error.kind", "unauthorized"))
	} else if errors.Is(err, domainerrors.ErrForbidden) {
		attrs = append(attrs, attribute.String("error.kind", "forbidden"))
	}

	return attrs
}

// StartSpanWithError starts a span and records error if operation fails.
// Returns span and context - caller must defer span.End().
func StartSpanWithError(ctx context.Context, spanName string, err *error) (context.Context, trace.Span) {
	tracer := otel.Tracer("github.com/example/project")
	ctx, span := tracer.Start(ctx, spanName)

	// If caller provides error pointer, record error on defer
	if err != nil {
		// This runs when defer executes (after function returns)
		go func() {
			if *err != nil {
				RecordError(ctx, *err)
			}
		}()
	}

	return ctx, span
}
```

**Usage in repository layer:**

```go
// File: internal/repository/user_repository.go
package repository

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/example/project/internal/domain/entity"
	"github.com/example/project/internal/domain/errors"
	"github.com/example/project/internal/telemetry"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/trace"
)

type UserRepository struct {
	db *sql.DB
}

func NewUserRepository(db *sql.DB) *UserRepository {
	return &UserRepository{db: db}
}

// GetByID retrieves user by ID with distributed tracing.
func (r *UserRepository) GetByID(ctx context.Context, userID int64) (*entity.User, error) {
	// Start span for database operation
	tracer := otel.Tracer("github.com/example/project/repository")
	ctx, span := tracer.Start(ctx, "UserRepository.GetByID",
		trace.WithAttributes(
			attribute.Int64("user.id", userID),
			attribute.String("db.operation", "SELECT"),
			attribute.String("db.table", "users"),
		),
	)
	defer span.End()

	query := `SELECT id, email, name FROM users WHERE id = $1`

	var user entity.User
	err := r.db.QueryRowContext(ctx, query, userID).Scan(&user.ID, &user.Email, &user.Name)

	if err == sql.ErrNoRows {
		// Record not found error with trace context
		notFoundErr := fmt.Errorf("user %d: %w", userID, errors.ErrNotFound)
		telemetry.RecordError(ctx, notFoundErr)
		return nil, notFoundErr
	}
	if err != nil {
		// Record database error with trace context
		dbErr := &errors.DatabaseError{
			Operation: "SELECT",
			Table:     "users",
			Err:       err,
		}
		telemetry.RecordError(ctx, dbErr)
		return nil, dbErr
	}

	// Success - add user data to span
	span.SetAttributes(
		attribute.String("user.email", user.Email),
		attribute.String("user.name", user.Name),
	)

	return &user, nil
}

// Create creates new user with distributed tracing.
func (r *UserRepository) Create(ctx context.Context, user *entity.User) error {
	tracer := otel.Tracer("github.com/example/project/repository")
	ctx, span := tracer.Start(ctx, "UserRepository.Create",
		trace.WithAttributes(
			attribute.String("user.email", user.Email),
			attribute.String("db.operation", "INSERT"),
			attribute.String("db.table", "users"),
		),
	)
	defer span.End()

	query := `INSERT INTO users (email, name) VALUES ($1, $2) RETURNING id`

	err := r.db.QueryRowContext(ctx, query, user.Email, user.Name).Scan(&user.ID)
	if err != nil {
		// Check for unique constraint violation
		if isUniqueViolation(err) {
			constraintErr := fmt.Errorf("email %s: %w", user.Email, errors.ErrAlreadyExists)
			telemetry.RecordError(ctx, constraintErr)
			return constraintErr
		}

		dbErr := &errors.DatabaseError{
			Operation: "INSERT",
			Table:     "users",
			Err:       err,
		}
		telemetry.RecordError(ctx, dbErr)
		return dbErr
	}

	// Success - add created user ID to span
	span.SetAttributes(attribute.Int64("user.id", user.ID))
	return nil
}

func isUniqueViolation(err error) bool {
	// PostgreSQL-specific check (use lib/pq for production)
	return err != nil && (err.Error() == "pq: duplicate key value violates unique constraint \"users_email_key\"")
}
```

**Usage in HTTP handler with trace propagation:**

```go
// File: internal/http/handler/user_handler.go
package handler

import (
	"encoding/json"
	"errors"
	"net/http"
	"strconv"

	domainerrors "github.com/example/project/internal/domain/errors"
	"github.com/example/project/internal/repository"
	"github.com/example/project/internal/telemetry"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/trace"
)

type UserHandler struct {
	repo *repository.UserRepository
}

func NewUserHandler(repo *repository.UserRepository) *UserHandler {
	return &UserHandler{repo: repo}
}

// GetUser retrieves user by ID with distributed tracing.
func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
	// Context already has trace context from middleware
	ctx := r.Context()

	// Start handler span (child of HTTP request span)
	tracer := otel.Tracer("github.com/example/project/handler")
	ctx, span := tracer.Start(ctx, "UserHandler.GetUser",
		trace.WithAttributes(
			attribute.String("http.method", r.Method),
			attribute.String("http.path", r.URL.Path),
		),
	)
	defer span.End()

	// Parse user ID
	userIDStr := r.PathValue("id")
	userID, err := strconv.ParseInt(userIDStr, 10, 64)
	if err != nil {
		validationErr := domainerrors.NewValidationError("id", userIDStr, "must be valid integer")
		telemetry.RecordError(ctx, validationErr)
		h.writeError(w, validationErr, http.StatusBadRequest)
		return
	}

	span.SetAttributes(attribute.Int64("user.id", userID))

	// Fetch user (repository will create child span)
	user, err := h.repo.GetByID(ctx, userID)
	if err != nil {
		// Error already recorded in repository layer
		// Map domain error to HTTP status code
		h.handleRepositoryError(w, err)
		return
	}

	// Success response
	span.SetAttributes(attribute.String("response.status", "success"))
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(user)
}

// handleRepositoryError maps domain errors to HTTP status codes.
// Errors already recorded in repository layer with trace context.
func (h *UserHandler) handleRepositoryError(w http.ResponseWriter, err error) {
	if errors.Is(err, domainerrors.ErrNotFound) {
		h.writeError(w, err, http.StatusNotFound)
		return
	}
	if errors.Is(err, domainerrors.ErrAlreadyExists) {
		h.writeError(w, err, http.StatusConflict)
		return
	}

	var validationErr *domainerrors.ValidationError
	if errors.As(err, &validationErr) {
		h.writeError(w, validationErr, http.StatusBadRequest)
		return
	}

	var dbErr *domainerrors.DatabaseError
	if errors.As(err, &dbErr) {
		// Don't expose internal database errors to client
		h.writeError(w, errors.New("internal server error"), http.StatusInternalServerError)
		return
	}

	h.writeError(w, errors.New("internal server error"), http.StatusInternalServerError)
}

type ErrorResponse struct {
	Error   string `json:"error"`
	Message string `json:"message,omitempty"`
	Field   string `json:"field,omitempty"`
}

func (h *UserHandler) writeError(w http.ResponseWriter, err error, statusCode int) {
	response := ErrorResponse{
		Error: http.StatusText(statusCode),
	}

	var validationErr *domainerrors.ValidationError
	if errors.As(err, &validationErr) {
		response.Message = validationErr.Message
		response.Field = validationErr.Field
	} else {
		response.Message = err.Error()
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(response)
}
```

**Trace visualization example (Jaeger UI):**

When error occurs, trace shows:
```
HTTP Request: GET /users/123 [ERROR]
├─ UserHandler.GetUser [ERROR]
│  ├─ user.id: 123
│  ├─ error.type: *errors.DatabaseError
│  ├─ error.message: "database SELECT failed on table 'users': connection timeout"
│  └─ UserRepository.GetByID [ERROR]
│     ├─ db.operation: SELECT
│     ├─ db.table: users
│     ├─ error.kind: database
│     ├─ error.operation: SELECT
│     └─ error.table: users
```

**Error sampling configuration:**

```go
// File: internal/telemetry/sampling.go
package telemetry

import (
	"go.opentelemetry.io/otel/sdk/trace"
)

// ErrorSampler samples ALL traces that contain errors, regardless of base sampling rate.
// Normal traces sampled at 10%, error traces sampled at 100%.
type ErrorSampler struct {
	baseSampler trace.Sampler // Parent-based sampler with 10% rate
}

func NewErrorSampler(baseSamplingRate float64) trace.Sampler {
	return &ErrorSampler{
		baseSampler: trace.ParentBased(trace.TraceIDRatioBased(baseSamplingRate)),
	}
}

func (es *ErrorSampler) ShouldSample(p trace.SamplingParameters) trace.SamplingResult {
	// If span has error status, ALWAYS sample
	for _, event := range p.Attributes {
		if event.Key == "error" {
			return trace.SamplingResult{
				Decision:   trace.RecordAndSample,
				Tracestate: p.ParentContext.TraceState(),
			}
		}
	}

	// Otherwise use base sampler (10% rate)
	return es.baseSampler.ShouldSample(p)
}

func (es *ErrorSampler) Description() string {
	return "ErrorSampler{always sample errors, base rate for normal traces}"
}
```

**Benefits:**
- ✅ **End-to-End Visibility:** Trace errors across service boundaries
- ✅ **Root Cause Analysis:** Follow trace to identify error origin
- ✅ **Structured Error Data:** Error attributes attached to spans for filtering
- ✅ **Error Sampling:** Sample all errors even with low base sampling rate
- ✅ **Context Propagation:** Trace context flows through `context.Context`

**Drawbacks:**
- ❌ **Overhead:** Tracing adds latency (~1-5ms per span)
- ❌ **Complexity:** Requires OpenTelemetry setup and trace backend (Jaeger, Zipkin)
- ❌ **Storage Cost:** Storing all error traces increases backend storage

**Use When:**
- Distributed systems with multiple microservices
- Need to correlate errors across service boundaries
- Debugging production issues requiring trace context
- Have tracing infrastructure (Jaeger, Zipkin, Datadog)

---

## 10. Telemetry and Observability

### 10.1 Recommended Approach: OpenTelemetry with Go net/http Integration

OpenTelemetry provides vendor-neutral instrumentation for metrics, traces, and logs in Go microservices[^35][^36][^37]. Combined with Prometheus for metrics and Jaeger/Zipkin for distributed tracing, this approach offers comprehensive observability.

**Core Benefits:**
- **Vendor-Neutral:** OpenTelemetry standardizes instrumentation across backends (Jaeger, Datadog, AWS X-Ray)
- **Auto-Instrumentation:** Middleware automatically instruments HTTP handlers, database clients
- **Distributed Tracing:** Trace requests across service boundaries with context propagation
- **Metrics Integration:** Export metrics to Prometheus, Datadog, or custom backends
- **Production-Ready:** Used by major companies (Google, Microsoft, Uber) for production observability

### 10.2 Implementation Examples

#### OpenTelemetry SDK Initialization

```go
// File: internal/telemetry/telemetry.go
package telemetry

import (
	"context"
	"fmt"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/jaeger"
	"go.opentelemetry.io/otel/exporters/prometheus"
	"go.opentelemetry.io/otel/metric"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/sdk/resource"
	sdkmetric "go.opentelemetry.io/otel/sdk/metric"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.20.0"
	"go.opentelemetry.io/otel/trace"
)

// Config holds telemetry configuration.
type Config struct {
	ServiceName    string  // Service name for traces/metrics
	ServiceVersion string  // Service version
	Environment    string  // Environment: dev, staging, prod
	JaegerEndpoint string  // Jaeger collector endpoint (http://localhost:14268/api/traces)
	SamplingRate   float64 // Trace sampling rate (0.0-1.0)
}

// Telemetry holds initialized telemetry providers.
type Telemetry struct {
	TracerProvider trace.TracerProvider
	MeterProvider  metric.MeterProvider
	Shutdown       func(context.Context) error // Cleanup function
}

// InitTelemetry initializes OpenTelemetry with Jaeger tracing and Prometheus metrics.
func InitTelemetry(ctx context.Context, cfg Config) (*Telemetry, error) {
	// Create resource with service metadata
	res, err := resource.New(ctx,
		resource.WithAttributes(
			semconv.ServiceName(cfg.ServiceName),
			semconv.ServiceVersion(cfg.ServiceVersion),
			attribute.String("environment", cfg.Environment),
		),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create resource: %w", err)
	}

	// Initialize Jaeger exporter for distributed tracing
	traceExporter, err := jaeger.New(jaeger.WithCollectorEndpoint(jaeger.WithEndpoint(cfg.JaegerEndpoint)))
	if err != nil {
		return nil, fmt.Errorf("failed to create Jaeger exporter: %w", err)
	}

	// Create trace provider with sampling
	tracerProvider := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(traceExporter),
		sdktrace.WithResource(res),
		sdktrace.WithSampler(sdktrace.ParentBased(sdktrace.TraceIDRatioBased(cfg.SamplingRate))),
	)

	// Set global tracer provider
	otel.SetTracerProvider(tracerProvider)

	// Set global trace context propagator (for distributed tracing)
	otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
		propagation.TraceContext{},
		propagation.Baggage{},
	))

	// Initialize Prometheus exporter for metrics
	metricExporter, err := prometheus.New()
	if err != nil {
		return nil, fmt.Errorf("failed to create Prometheus exporter: %w", err)
	}

	// Create meter provider
	meterProvider := sdkmetric.NewMeterProvider(
		sdkmetric.WithReader(metricExporter),
		sdkmetric.WithResource(res),
	)

	// Set global meter provider
	otel.SetMeterProvider(meterProvider)

	// Cleanup function to shutdown providers
	shutdown := func(ctx context.Context) error {
		if err := tracerProvider.Shutdown(ctx); err != nil {
			return fmt.Errorf("failed to shutdown tracer provider: %w", err)
		}
		if err := meterProvider.Shutdown(ctx); err != nil {
			return fmt.Errorf("failed to shutdown meter provider: %w", err)
		}
		return nil
	}

	return &Telemetry{
		TracerProvider: tracerProvider,
		MeterProvider:  meterProvider,
		Shutdown:       shutdown,
	}, nil
}
```

**HTTP middleware for automatic tracing:**

```go
// File: internal/http/middleware/tracing.go
package middleware

import (
	"net/http"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/propagation"
	semconv "go.opentelemetry.io/otel/semconv/v1.20.0"
	"go.opentelemetry.io/otel/trace"
)

// TracingMiddleware instruments HTTP handlers with OpenTelemetry tracing.
func TracingMiddleware(serviceName string) func(http.Handler) http.Handler {
	tracer := otel.Tracer(serviceName)

	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Extract trace context from incoming request headers
			ctx := otel.GetTextMapPropagator().Extract(r.Context(), propagation.HeaderCarrier(r.Header))

			// Start span for HTTP request
			ctx, span := tracer.Start(ctx, r.Method+" "+r.URL.Path,
				trace.WithAttributes(
					semconv.HTTPMethod(r.Method),
					semconv.HTTPTarget(r.URL.Path),
					semconv.HTTPRoute(r.URL.Path),
					semconv.HTTPScheme(r.URL.Scheme),
					semconv.HTTPUserAgent(r.UserAgent()),
					semconv.NetPeerIP(r.RemoteAddr),
				),
			)
			defer span.End()

			// Wrap response writer to capture status code
			rw := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}

			// Continue with request handling (context has trace span)
			next.ServeHTTP(rw, r.WithContext(ctx))

			// Record response status
			span.SetAttributes(
				semconv.HTTPStatusCode(rw.statusCode),
			)

			// Set span status based on HTTP status code
			if rw.statusCode >= 400 {
				span.SetStatus(trace.StatusError, http.StatusText(rw.statusCode))
			} else {
				span.SetStatus(trace.StatusOk, "")
			}
		})
	}
}

// responseWriter wraps http.ResponseWriter to capture status code.
type responseWriter struct {
	http.ResponseWriter
	statusCode int
}

func (rw *responseWriter) WriteHeader(code int) {
	rw.statusCode = code
	rw.ResponseWriter.WriteHeader(code)
}
```

**Prometheus metrics with custom instrumentation:**

```go
// File: internal/metrics/metrics.go
package metrics

import (
	"context"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/metric"
)

// Metrics holds application metrics instruments.
type Metrics struct {
	// HTTP metrics
	HTTPRequestDuration metric.Float64Histogram
	HTTPRequestsTotal   metric.Int64Counter
	HTTPRequestsActive  metric.Int64UpDownCounter

	// Database metrics
	DBQueryDuration metric.Float64Histogram
	DBConnectionsActive metric.Int64UpDownCounter

	// Business metrics
	UsersCreated metric.Int64Counter
	OrdersPlaced metric.Int64Counter
}

// NewMetrics creates application metrics instruments.
func NewMetrics() (*Metrics, error) {
	meter := otel.Meter("github.com/example/project")

	httpRequestDuration, err := meter.Float64Histogram(
		"http.server.request.duration",
		metric.WithDescription("HTTP request duration in seconds"),
		metric.WithUnit("s"),
	)
	if err != nil {
		return nil, err
	}

	httpRequestsTotal, err := meter.Int64Counter(
		"http.server.requests.total",
		metric.WithDescription("Total HTTP requests"),
	)
	if err != nil {
		return nil, err
	}

	httpRequestsActive, err := meter.Int64UpDownCounter(
		"http.server.requests.active",
		metric.WithDescription("Active HTTP requests"),
	)
	if err != nil {
		return nil, err
	}

	dbQueryDuration, err := meter.Float64Histogram(
		"db.query.duration",
		metric.WithDescription("Database query duration in seconds"),
		metric.WithUnit("s"),
	)
	if err != nil {
		return nil, err
	}

	dbConnectionsActive, err := meter.Int64UpDownCounter(
		"db.connections.active",
		metric.WithDescription("Active database connections"),
	)
	if err != nil {
		return nil, err
	}

	usersCreated, err := meter.Int64Counter(
		"users.created.total",
		metric.WithDescription("Total users created"),
	)
	if err != nil {
		return nil, err
	}

	ordersPlaced, err := meter.Int64Counter(
		"orders.placed.total",
		metric.WithDescription("Total orders placed"),
	)
	if err != nil {
		return nil, err
	}

	return &Metrics{
		HTTPRequestDuration:  httpRequestDuration,
		HTTPRequestsTotal:    httpRequestsTotal,
		HTTPRequestsActive:   httpRequestsActive,
		DBQueryDuration:      dbQueryDuration,
		DBConnectionsActive:  dbConnectionsActive,
		UsersCreated:         usersCreated,
		OrdersPlaced:         ordersPlaced,
	}, nil
}

// RecordHTTPRequest records HTTP request metrics.
func (m *Metrics) RecordHTTPRequest(ctx context.Context, method, path string, statusCode int, duration time.Duration) {
	attrs := []attribute.KeyValue{
		attribute.String("http.method", method),
		attribute.String("http.path", path),
		attribute.Int("http.status_code", statusCode),
	}

	m.HTTPRequestDuration.Record(ctx, duration.Seconds(), metric.WithAttributes(attrs...))
	m.HTTPRequestsTotal.Add(ctx, 1, metric.WithAttributes(attrs...))
}

// RecordDBQuery records database query metrics.
func (m *Metrics) RecordDBQuery(ctx context.Context, operation, table string, duration time.Duration) {
	attrs := []attribute.KeyValue{
		attribute.String("db.operation", operation),
		attribute.String("db.table", table),
	}

	m.DBQueryDuration.Record(ctx, duration.Seconds(), metric.WithAttributes(attrs...))
}
```

**Metrics middleware for HTTP:**

```go
// File: internal/http/middleware/metrics.go
package middleware

import (
	"net/http"
	"time"

	"github.com/example/project/internal/metrics"
)

// MetricsMiddleware instruments HTTP handlers with Prometheus metrics.
func MetricsMiddleware(m *metrics.Metrics) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()

			// Increment active requests
			m.HTTPRequestsActive.Add(r.Context(), 1)
			defer m.HTTPRequestsActive.Add(r.Context(), -1)

			// Wrap response writer to capture status code
			rw := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}

			// Continue with request handling
			next.ServeHTTP(rw, r)

			// Record metrics
			duration := time.Since(start)
			m.RecordHTTPRequest(r.Context(), r.Method, r.URL.Path, rw.statusCode, duration)
		})
	}
}
```

**Usage in main.go:**

```go
// File: cmd/server/main.go
package main

import (
	"context"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"time"

	"github.com/example/project/internal/config"
	"github.com/example/project/internal/http/handler"
	"github.com/example/project/internal/http/middleware"
	"github.com/example/project/internal/metrics"
	"github.com/example/project/internal/telemetry"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

func main() {
	ctx := context.Background()

	// Load configuration
	cfg := config.MustLoad()

	// Initialize telemetry
	telem, err := telemetry.InitTelemetry(ctx, telemetry.Config{
		ServiceName:    cfg.AppName,
		ServiceVersion: "1.0.0",
		Environment:    getEnvironment(cfg.Debug),
		JaegerEndpoint: "http://localhost:14268/api/traces",
		SamplingRate:   0.1, // Sample 10% of traces
	})
	if err != nil {
		slog.Error("failed to initialize telemetry", "error", err)
		os.Exit(1)
	}
	defer telem.Shutdown(ctx)

	// Initialize metrics
	appMetrics, err := metrics.NewMetrics()
	if err != nil {
		slog.Error("failed to initialize metrics", "error", err)
		os.Exit(1)
	}

	// Setup HTTP server with middleware
	mux := http.NewServeMux()

	// Health endpoints (no tracing overhead)
	healthHandler := handler.NewHealthHandler(/* ... */)
	mux.HandleFunc("GET /health", healthHandler.Health)
	mux.HandleFunc("GET /health/ready", healthHandler.Readiness)
	mux.HandleFunc("GET /health/live", healthHandler.Liveness)

	// Prometheus metrics endpoint
	mux.Handle("GET /metrics", promhttp.Handler())

	// Application routes (with tracing and metrics)
	userHandler := handler.NewUserHandler(/* ... */)
	apiMux := http.NewServeMux()
	apiMux.HandleFunc("GET /api/users/{id}", userHandler.GetUser)
	apiMux.HandleFunc("POST /api/users", userHandler.CreateUser)

	// Apply middleware (tracing → metrics → handler)
	mux.Handle("/api/", middleware.TracingMiddleware(cfg.AppName)(
		middleware.MetricsMiddleware(appMetrics)(apiMux),
	))

	// Start server
	server := &http.Server{
		Addr:         ":8080",
		Handler:      mux,
		ReadTimeout:  cfg.ReadTimeout,
		WriteTimeout: cfg.WriteTimeout,
		IdleTimeout:  cfg.IdleTimeout,
	}

	// Graceful shutdown
	go func() {
		slog.Info("server starting", "port", 8080)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			slog.Error("server error", "error", err)
		}
	}()

	// Wait for interrupt signal
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt)
	<-stop

	slog.Info("shutting down server...")
	shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := server.Shutdown(shutdownCtx); err != nil {
		slog.Error("server shutdown error", "error", err)
	}

	slog.Info("server stopped")
}

func getEnvironment(debug bool) string {
	if debug {
		return "development"
	}
	return "production"
}
```

### 10.2.1 Telemetry Initialization Patterns

#### Pattern 1: OpenTelemetry Auto-Instrumentation (Recommended)

Use OpenTelemetry middleware to automatically instrument HTTP handlers without manual span creation[^35][^36].

**Benefits:**
- ✅ **Zero Code Changes:** Automatic instrumentation via middleware
- ✅ **Consistent Spans:** All HTTP requests traced with standard attributes
- ✅ **Context Propagation:** Trace context flows through `context.Context` automatically
- ✅ **Production-Ready:** Battle-tested by major companies

**Drawbacks:**
- ❌ **Limited Customization:** Auto-instrumentation provides standard attributes only
- ❌ **Framework Dependency:** Middleware tightly coupled to HTTP framework

**Use When:**
- Standard HTTP API with typical request/response patterns
- Want minimal code changes for observability
- Don't need custom span attributes beyond standard HTTP metadata

#### Pattern 2: Manual Instrumentation with Custom Spans

Manually create spans for fine-grained control over tracing attributes and business logic instrumentation[^35].

```go
// File: internal/service/order_service.go
package service

import (
	"context"
	"fmt"

	"github.com/example/project/internal/domain/entity"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/trace"
)

type OrderService struct {
	repo OrderRepository
}

func NewOrderService(repo OrderRepository) *OrderService {
	return &OrderService{repo: repo}
}

// PlaceOrder creates order with custom span attributes.
func (s *OrderService) PlaceOrder(ctx context.Context, order *entity.Order) error {
	tracer := otel.Tracer("github.com/example/project/service")

	// Create parent span for business operation
	ctx, span := tracer.Start(ctx, "OrderService.PlaceOrder",
		trace.WithAttributes(
			attribute.String("order.id", order.ID),
			attribute.Float64("order.total", order.Total),
			attribute.Int("order.items_count", len(order.Items)),
		),
	)
	defer span.End()

	// Step 1: Validate order (child span)
	if err := s.validateOrder(ctx, order); err != nil {
		span.RecordError(err)
		return err
	}

	// Step 2: Check inventory (child span)
	if err := s.checkInventory(ctx, order); err != nil {
		span.RecordError(err)
		return err
	}

	// Step 3: Process payment (child span)
	if err := s.processPayment(ctx, order); err != nil {
		span.RecordError(err)
		return err
	}

	// Step 4: Save order (repository creates child span)
	if err := s.repo.Create(ctx, order); err != nil {
		span.RecordError(err)
		return err
	}

	// Add success attributes
	span.SetAttributes(
		attribute.String("order.status", "confirmed"),
		attribute.Int64("order.created_at", order.CreatedAt.Unix()),
	)

	return nil
}

// validateOrder validates order with dedicated span.
func (s *OrderService) validateOrder(ctx context.Context, order *entity.Order) error {
	tracer := otel.Tracer("github.com/example/project/service")
	ctx, span := tracer.Start(ctx, "OrderService.validateOrder")
	defer span.End()

	if order.Total <= 0 {
		err := fmt.Errorf("invalid order total: %.2f", order.Total)
		span.RecordError(err)
		return err
	}

	if len(order.Items) == 0 {
		err := fmt.Errorf("order must have at least one item")
		span.RecordError(err)
		return err
	}

	span.SetAttributes(attribute.Bool("validation.passed", true))
	return nil
}

// checkInventory checks inventory with external service span.
func (s *OrderService) checkInventory(ctx context.Context, order *entity.Order) error {
	tracer := otel.Tracer("github.com/example/project/service")
	ctx, span := tracer.Start(ctx, "OrderService.checkInventory",
		trace.WithAttributes(
			attribute.String("span.kind", "client"), // External service call
		),
	)
	defer span.End()

	// Call inventory service (implementation omitted)
	// span.SetAttributes(attribute.String("inventory.service", "http://inventory:8080"))

	return nil
}

// processPayment processes payment with external service span.
func (s *OrderService) processPayment(ctx context.Context, order *entity.Order) error {
	tracer := otel.Tracer("github.com/example/project/service")
	ctx, span := tracer.Start(ctx, "OrderService.processPayment",
		trace.WithAttributes(
			attribute.String("span.kind", "client"),
			attribute.Float64("payment.amount", order.Total),
		),
	)
	defer span.End()

	// Call payment service (implementation omitted)
	// span.SetAttributes(attribute.String("payment.provider", "stripe"))

	return nil
}
```

**Benefits:**
- ✅ **Fine-Grained Control:** Custom attributes for business logic
- ✅ **Business Metrics:** Trace business operations (order placement, payment processing)
- ✅ **Multi-Step Workflows:** Span hierarchy shows operation flow

**Drawbacks:**
- ❌ **Code Overhead:** Manual span creation in every instrumented function
- ❌ **Error-Prone:** Easy to forget `defer span.End()` (resource leak)

**Use When:**
- Complex business logic requiring detailed tracing
- Need custom attributes beyond HTTP metadata
- Multi-step workflows (order processing, payment flows)

#### Pattern 3: Prometheus Metrics with Registry

Use Prometheus client library directly for custom metrics without OpenTelemetry[^38][^39].

```go
// File: internal/metrics/prometheus.go
package metrics

import (
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

// PrometheusMetrics holds Prometheus metric collectors.
type PrometheusMetrics struct {
	// HTTP metrics
	HTTPRequestDuration *prometheus.HistogramVec
	HTTPRequestsTotal   *prometheus.CounterVec
	HTTPRequestsInFlight prometheus.Gauge

	// Database metrics
	DBQueryDuration *prometheus.HistogramVec
	DBConnectionsActive prometheus.Gauge

	// Business metrics
	UsersCreatedTotal prometheus.Counter
	OrdersPlacedTotal prometheus.Counter
}

// NewPrometheusMetrics creates Prometheus metrics collectors.
func NewPrometheusMetrics(namespace string) *PrometheusMetrics {
	return &PrometheusMetrics{
		HTTPRequestDuration: promauto.NewHistogramVec(
			prometheus.HistogramOpts{
				Namespace: namespace,
				Name:      "http_request_duration_seconds",
				Help:      "HTTP request duration in seconds",
				Buckets:   []float64{.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10},
			},
			[]string{"method", "path", "status_code"},
		),

		HTTPRequestsTotal: promauto.NewCounterVec(
			prometheus.CounterOpts{
				Namespace: namespace,
				Name:      "http_requests_total",
				Help:      "Total HTTP requests",
			},
			[]string{"method", "path", "status_code"},
		),

		HTTPRequestsInFlight: promauto.NewGauge(
			prometheus.GaugeOpts{
				Namespace: namespace,
				Name:      "http_requests_in_flight",
				Help:      "Active HTTP requests",
			},
		),

		DBQueryDuration: promauto.NewHistogramVec(
			prometheus.HistogramOpts{
				Namespace: namespace,
				Name:      "db_query_duration_seconds",
				Help:      "Database query duration in seconds",
				Buckets:   []float64{.001, .005, .01, .025, .05, .1, .25, .5, 1},
			},
			[]string{"operation", "table"},
		),

		DBConnectionsActive: promauto.NewGauge(
			prometheus.GaugeOpts{
				Namespace: namespace,
				Name:      "db_connections_active",
				Help:      "Active database connections",
			},
		),

		UsersCreatedTotal: promauto.NewCounter(
			prometheus.CounterOpts{
				Namespace: namespace,
				Name:      "users_created_total",
				Help:      "Total users created",
			},
		),

		OrdersPlacedTotal: promauto.NewCounter(
			prometheus.CounterOpts{
				Namespace: namespace,
				Name:      "orders_placed_total",
				Help:      "Total orders placed",
			},
		),
	}
}
```

**Benefits:**
- ✅ **Lightweight:** No OpenTelemetry dependency
- ✅ **Prometheus-Native:** Direct Prometheus exposition format
- ✅ **Simple:** Straightforward metric collection

**Drawbacks:**
- ❌ **Prometheus-Only:** Locked to Prometheus (can't switch to Datadog easily)
- ❌ **No Distributed Tracing:** Metrics only, no traces

**Use When:**
- Only need metrics (no distributed tracing)
- Already using Prometheus infrastructure
- Want minimal dependencies

#### Pattern 4: Hybrid Approach (OpenTelemetry + Prometheus)

Use OpenTelemetry for tracing, Prometheus client library for metrics[^35][^38].

**Benefits:**
- ✅ **Best of Both:** OpenTelemetry tracing + Prometheus metrics
- ✅ **Mature Metrics:** Prometheus client library more mature than OTel metrics
- ✅ **Flexible:** Can switch tracing backend without changing metrics

**Drawbacks:**
- ❌ **Two Systems:** Must manage both OpenTelemetry and Prometheus
- ❌ **Complexity:** More configuration and initialization code

**Use When:**
- Need distributed tracing AND detailed metrics
- Prometheus already deployed for metrics
- Want vendor-neutral tracing with mature metrics library

### 10.2.2 Common Telemetry Mistakes

#### Mistake 1: Not Propagating context.Context Across Goroutines

**Problem:** Trace context lost when spawning goroutines without passing `context.Context`[^40][^41].

**❌ Bad Example:**

```go
func (s *Service) ProcessAsync(ctx context.Context, data string) {
	// BAD: Spawning goroutine without context - trace context lost!
	go func() {
		// This function has NO trace context
		s.repo.Save(context.Background(), data) // Creates orphan span
	}()
}
```

**✅ Good Example:**

```go
func (s *Service) ProcessAsync(ctx context.Context, data string) {
	// GOOD: Pass context to goroutine to preserve trace context
	go func(ctx context.Context) {
		// This function inherits trace context from parent
		s.repo.Save(ctx, data) // Span linked to parent trace
	}(ctx)
}
```

#### Mistake 2: Creating Metrics in Request Handlers (Use Global Registry)

**Problem:** Creating metric collectors in request handlers causes memory leaks and registration errors[^38][^39].

**❌ Bad Example:**

```go
func (h *Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	// BAD: Creating metric on every request - memory leak!
	counter := prometheus.NewCounter(prometheus.CounterOpts{
		Name: "requests_total",
	})
	counter.Inc() // Panic: metric already registered
}
```

**✅ Good Example:**

```go
// GOOD: Create metrics once at initialization
var requestsTotal = promauto.NewCounter(prometheus.CounterOpts{
	Name: "requests_total",
})

func (h *Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	requestsTotal.Inc() // Use global metric
}
```

#### Mistake 3: Missing span.End() Calls (Resource Leaks)

**Problem:** Forgetting to call `span.End()` causes memory leaks as spans accumulate without being flushed[^35].

**❌ Bad Example:**

```go
func (s *Service) ProcessData(ctx context.Context) error {
	_, span := tracer.Start(ctx, "ProcessData")
	// Missing defer span.End() - memory leak!

	if err := s.validate(); err != nil {
		return err // Span never ends
	}

	return s.save()
}
```

**✅ Good Example:**

```go
func (s *Service) ProcessData(ctx context.Context) error {
	_, span := tracer.Start(ctx, "ProcessData")
	defer span.End() // ALWAYS defer span.End() immediately

	if err := s.validate(); err != nil {
		span.RecordError(err)
		return err
	}

	return s.save()
}
```

### 10.2.3 Verification and Troubleshooting

#### Health Check Endpoints for Kubernetes Probes

```go
// File: internal/http/handler/health.go
package handler

import (
	"context"
	"database/sql"
	"encoding/json"
	"net/http"
	"time"

	"github.com/redis/go-redis/v9"
)

type HealthHandler struct {
	db    *sql.DB
	cache *redis.Client
}

func NewHealthHandler(db *sql.DB, cache *redis.Client) *HealthHandler {
	return &HealthHandler{db: db, cache: cache}
}

// Liveness returns 200 if application is alive (Kubernetes liveness probe).
func (h *HealthHandler) Liveness(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("alive"))
}

// Readiness returns 200 if application ready to serve traffic (Kubernetes readiness probe).
func (h *HealthHandler) Readiness(w http.ResponseWriter, r *http.Request) {
	ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
	defer cancel()

	// Check database connectivity
	if err := h.db.PingContext(ctx); err != nil {
		http.Error(w, "database not ready", http.StatusServiceUnavailable)
		return
	}

	// Check Redis connectivity (optional - degraded service acceptable)
	if err := h.cache.Ping(ctx).Err(); err != nil {
		// Log warning but don't fail readiness check
		// Redis down is degraded service, not unavailable
	}

	w.WriteHeader(http.StatusOK)
	w.Write([]byte("ready"))
}

// Health returns detailed health status with metrics (for monitoring dashboards).
func (h *HealthHandler) Health(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()

	health := map[string]interface{}{
		"status":    "healthy",
		"timestamp": time.Now().UTC(),
		"checks": map[string]interface{}{
			"database": h.checkDatabase(ctx),
			"redis":    h.checkRedis(ctx),
		},
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(health)
}

func (h *HealthHandler) checkDatabase(ctx context.Context) map[string]interface{} {
	ctx, cancel := context.WithTimeout(ctx, 2*time.Second)
	defer cancel()

	start := time.Now()
	err := h.db.PingContext(ctx)
	latency := time.Since(start)

	if err != nil {
		return map[string]interface{}{
			"status":  "down",
			"latency": latency.String(),
			"error":   err.Error(),
		}
	}

	return map[string]interface{}{
		"status":  "up",
		"latency": latency.String(),
	}
}

func (h *HealthHandler) checkRedis(ctx context.Context) map[string]interface{} {
	ctx, cancel := context.WithTimeout(ctx, 2*time.Second)
	defer cancel()

	start := time.Now()
	err := h.cache.Ping(ctx).Err()
	latency := time.Since(start)

	if err != nil {
		return map[string]interface{}{
			"status":  "down",
			"latency": latency.String(),
			"error":   err.Error(),
		}
	}

	return map[string]interface{}{
		"status":  "up",
		"latency": latency.String(),
	}
}
```

**Kubernetes deployment with probes:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: go-microservice
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: app
        image: go-microservice:latest
        ports:
        - containerPort: 8080

        # Liveness probe - restart if fails
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 2
          failureThreshold: 3

        # Readiness probe - remove from service if fails
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 2
          failureThreshold: 2
```

#### Metrics Endpoint Verification

```bash
# Check Prometheus metrics endpoint
$ curl http://localhost:8080/metrics

# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/api/users",status_code="200"} 1523

# HELP http_request_duration_seconds HTTP request duration in seconds
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",path="/api/users",status_code="200",le="0.005"} 1234
http_request_duration_seconds_bucket{method="GET",path="/api/users",status_code="200",le="0.01"} 1456
http_request_duration_seconds_sum{method="GET",path="/api/users",status_code="200"} 12.45
http_request_duration_seconds_count{method="GET",path="/api/users",status_code="200"} 1523

# HELP db_query_duration_seconds Database query duration in seconds
# TYPE db_query_duration_seconds histogram
db_query_duration_seconds_bucket{operation="SELECT",table="users",le="0.001"} 543
db_query_duration_seconds_sum{operation="SELECT",table="users"} 2.34
db_query_duration_seconds_count{operation="SELECT",table="users"} 876
```

#### Trace Sampling Configuration and Debugging

```go
// File: internal/telemetry/sampling.go
package telemetry

import (
	"go.opentelemetry.io/otel/sdk/trace"
)

// NewSampler creates a production-ready sampler with error sampling.
// - Sample 10% of successful traces
// - Sample 100% of error traces
func NewSampler() trace.Sampler {
	return &errorAwareSampler{
		baseSampler: trace.ParentBased(trace.TraceIDRatioBased(0.1)),
	}
}

type errorAwareSampler struct {
	baseSampler trace.Sampler
}

func (s *errorAwareSampler) ShouldSample(p trace.SamplingParameters) trace.SamplingResult {
	// Check if span will record error (based on attributes)
	for _, attr := range p.Attributes {
		if attr.Key == "error" && attr.Value.AsBool() {
			// Always sample error traces
			return trace.SamplingResult{
				Decision:   trace.RecordAndSample,
				Tracestate: p.ParentContext.TraceState(),
			}
		}
	}

	// Use base sampler for non-error traces
	return s.baseSampler.ShouldSample(p)
}

func (s *errorAwareSampler) Description() string {
	return "ErrorAwareSampler{10% base rate, 100% error rate}"
}
```

### 10.3 Alternative Approaches

**OpenTelemetry vs. Prometheus vs. StatsD:**

| Aspect | OpenTelemetry | Prometheus | StatsD |
|--------|---------------|------------|--------|
| **Tracing** | ✅ Native support | ❌ None | ❌ None |
| **Metrics** | ✅ Vendor-neutral | ✅ Pull-based, mature | ✅ Push-based, simple |
| **Logs** | ✅ Experimental | ❌ None | ❌ None |
| **Vendor Lock-In** | ✅ None (portable) | ⚠️ Prometheus ecosystem | ⚠️ Backend-specific |
| **Maturity** | ⚠️ Evolving | ✅ Battle-tested | ✅ Mature |
| **Complexity** | ⚠️ Higher (SDK setup) | ✅ Simple (library) | ✅ Very simple |

**Jaeger vs. Zipkin vs. AWS X-Ray:**

| Aspect | Jaeger | Zipkin | AWS X-Ray |
|--------|--------|--------|-----------|
| **Open Source** | ✅ CNCF project | ✅ Apache project | ❌ Proprietary |
| **Deployment** | Self-hosted or cloud | Self-hosted or cloud | AWS-managed only |
| **Cost** | Free (infra costs) | Free (infra costs) | Pay per trace |
| **OTel Support** | ✅ Native | ✅ Native | ✅ Via exporter |
| **UI** | ✅ Rich, modern | ✅ Simple, functional | ✅ AWS Console |

### 10.4 Decision Criteria

**When to Use OpenTelemetry (Recommended):**
- Need vendor-neutral observability (avoid lock-in)
- Distributed systems with multiple services
- Want unified telemetry (traces + metrics + logs)
- May switch backends (Jaeger → Datadog → New Relic)

**When to Use Prometheus Only:**
- Metrics-only requirements (no distributed tracing)
- Already using Prometheus infrastructure
- Simple microservice (single service, no cross-service calls)
- Want minimal dependencies

**When to Use Proprietary Solutions (Datadog, New Relic, AWS X-Ray):**
- Need managed observability platform (no ops burden)
- Want APM features (code profiling, anomaly detection)
- Budget for commercial observability solution
- Already using cloud platform (AWS X-Ray for AWS deployments)

### 10.5 Integrating slog with OpenTelemetry Trace Context

Correlate structured logs with distributed traces by injecting trace and span IDs into log records automatically[^42][^43]. This enables filtering logs by trace ID to see all logs for a request across services.

**Core Benefits:**
- **Log-Trace Correlation:** Click trace ID in logs → jump to full distributed trace in Jaeger/Zipkin
- **Request Context:** All logs for a request include same trace ID (cross-service correlation)
- **Zero Manual Effort:** Automatic trace/span ID injection via context propagation
- **Structured Format:** JSON logs with `trace_id` and `span_id` fields for querying

#### slog Handler with OpenTelemetry Context

```go
// File: internal/logging/otel_handler.go
package logging

import (
	"context"
	"log/slog"

	"go.opentelemetry.io/otel/trace"
)

// OTelHandler wraps slog.Handler to inject OpenTelemetry trace context.
type OTelHandler struct {
	handler slog.Handler
}

// NewOTelHandler creates a handler that injects trace/span IDs into logs.
func NewOTelHandler(handler slog.Handler) *OTelHandler {
	return &OTelHandler{handler: handler}
}

// Enabled reports whether the handler handles records at the given level.
func (h *OTelHandler) Enabled(ctx context.Context, level slog.Level) bool {
	return h.handler.Enabled(ctx, level)
}

// Handle adds trace_id and span_id to log record if context has active span.
func (h *OTelHandler) Handle(ctx context.Context, record slog.Record) error {
	// Extract span from context
	span := trace.SpanFromContext(ctx)
	if span.IsRecording() {
		spanCtx := span.SpanContext()

		// Add trace_id and span_id attributes to log record
		record.AddAttrs(
			slog.String("trace_id", spanCtx.TraceID().String()),
			slog.String("span_id", spanCtx.SpanID().String()),
		)

		// Add trace flags if sampled
		if spanCtx.IsSampled() {
			record.AddAttrs(slog.Bool("trace_sampled", true))
		}
	}

	return h.handler.Handle(ctx, record)
}

// WithAttrs returns a new handler with additional attributes.
func (h *OTelHandler) WithAttrs(attrs []slog.Attr) slog.Handler {
	return &OTelHandler{handler: h.handler.WithAttrs(attrs)}
}

// WithGroup returns a new handler with the given group name.
func (h *OTelHandler) WithGroup(name string) slog.Handler {
	return &OTelHandler{handler: h.handler.WithGroup(name)}
}
```

**Initialize logger with OTel context in main.go:**

```go
// File: cmd/server/main.go (initialization section)
package main

import (
	"log/slog"
	"os"

	"github.com/example/project/internal/logging"
)

func main() {
	// Create base JSON handler
	jsonHandler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelInfo,
		AddSource: true,
	})

	// Wrap with OTel context handler
	otelHandler := logging.NewOTelHandler(jsonHandler)

	// Set global logger
	logger := slog.New(otelHandler)
	slog.SetDefault(logger)

	// Initialize telemetry (from section 10.2)
	// ... telemetry initialization code ...

	// Now all logs automatically include trace_id/span_id when context has active span
	ctx := context.Background()
	slog.InfoContext(ctx, "server starting", "port", 8080)
}
```

**Usage in HTTP handlers with automatic trace context:**

```go
// File: internal/http/handler/user_handler.go
package handler

import (
	"context"
	"log/slog"
	"net/http"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/trace"
)

type UserHandler struct {
	service UserService
}

func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context() // Context has trace span from TracingMiddleware

	userID := r.PathValue("id")

	// Log with context - automatically includes trace_id and span_id
	slog.InfoContext(ctx, "fetching user",
		"user_id", userID,
		"method", r.Method,
		"path", r.URL.Path,
	)

	user, err := h.service.GetUserByID(ctx, userID)
	if err != nil {
		// Error log automatically includes trace_id for correlation
		slog.ErrorContext(ctx, "failed to fetch user",
			"user_id", userID,
			"error", err,
		)
		http.Error(w, "user not found", http.StatusNotFound)
		return
	}

	// Success log with trace_id
	slog.InfoContext(ctx, "user fetched successfully",
		"user_id", userID,
		"username", user.Username,
	)

	// ... encode response ...
}
```

**Example log output with trace correlation:**

```json
{
  "time": "2025-11-03T10:23:45.123Z",
  "level": "INFO",
  "msg": "fetching user",
  "user_id": "user_12345",
  "method": "GET",
  "path": "/api/users/user_12345",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "trace_sampled": true,
  "source": "internal/http/handler/user_handler.go:23"
}
```

**Query logs by trace ID in production:**

```bash
# Filter logs by trace ID to see all logs for a request
$ kubectl logs -l app=user-service | jq 'select(.trace_id == "4bf92f3577b34da6a3ce929d0e0e4736")'

# Output shows all logs for this trace across services
{"time": "...", "msg": "fetching user", "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736", ...}
{"time": "...", "msg": "database query started", "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736", ...}
{"time": "...", "msg": "cache lookup", "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736", ...}
{"time": "...", "msg": "user fetched successfully", "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736", ...}
```

### 10.6 OTLP Exporters Configuration (gRPC and HTTP)

OpenTelemetry Protocol (OTLP) is the recommended exporter format for sending traces, metrics, and logs to observability backends[^44][^45]. OTLP supports both gRPC (high performance) and HTTP (firewall-friendly) transports.

**Core Benefits:**
- **Vendor-Neutral:** OTLP is standard protocol supported by Jaeger, Prometheus, Datadog, Honeycomb, etc.
- **Efficient:** gRPC provides high-throughput binary encoding
- **Firewall-Friendly:** HTTP/1.1 fallback for restrictive networks
- **Single Endpoint:** Export traces AND metrics to same collector endpoint
- **Production-Ready:** Used in production by CNCF projects

#### OTLP gRPC Exporter (Recommended for Performance)

```go
// File: internal/telemetry/otlp_grpc.go
package telemetry

import (
	"context"
	"fmt"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.20.0"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

// OTLPGRPCConfig holds OTLP gRPC exporter configuration.
type OTLPGRPCConfig struct {
	Endpoint       string  // OTLP collector endpoint (e.g., "localhost:4317")
	ServiceName    string  // Service name for traces
	ServiceVersion string  // Service version
	Environment    string  // Environment: dev, staging, prod
	SamplingRate   float64 // Trace sampling rate (0.0-1.0)
	Insecure       bool    // Use insecure connection (dev only)
}

// InitOTLPGRPC initializes OpenTelemetry with OTLP gRPC exporter.
func InitOTLPGRPC(ctx context.Context, cfg OTLPGRPCConfig) (*Telemetry, error) {
	// Create resource with service metadata
	res, err := resource.New(ctx,
		resource.WithAttributes(
			semconv.ServiceName(cfg.ServiceName),
			semconv.ServiceVersion(cfg.ServiceVersion),
			semconv.DeploymentEnvironment(cfg.Environment),
		),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create resource: %w", err)
	}

	// Configure gRPC connection options
	var grpcOpts []grpc.DialOption
	if cfg.Insecure {
		grpcOpts = append(grpcOpts, grpc.WithTransportCredentials(insecure.NewCredentials()))
	}

	// Create OTLP gRPC exporter
	traceClient := otlptracegrpc.NewClient(
		otlptracegrpc.WithEndpoint(cfg.Endpoint),
		otlptracegrpc.WithDialOption(grpcOpts...),
		otlptracegrpc.WithTimeout(5*time.Second),
		otlptracegrpc.WithRetry(otlptracegrpc.RetryConfig{
			Enabled:         true,
			InitialInterval: 1 * time.Second,
			MaxInterval:     10 * time.Second,
			MaxElapsedTime:  30 * time.Second,
		}),
	)

	traceExporter, err := otlptrace.New(ctx, traceClient)
	if err != nil {
		return nil, fmt.Errorf("failed to create OTLP gRPC exporter: %w", err)
	}

	// Create trace provider with batch span processor
	tracerProvider := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(traceExporter,
			sdktrace.WithBatchTimeout(5*time.Second),
			sdktrace.WithMaxExportBatchSize(512),
		),
		sdktrace.WithResource(res),
		sdktrace.WithSampler(sdktrace.ParentBased(sdktrace.TraceIDRatioBased(cfg.SamplingRate))),
	)

	// Set global tracer provider
	otel.SetTracerProvider(tracerProvider)

	// Set global trace context propagator (W3C Trace Context + Baggage)
	otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
		propagation.TraceContext{},
		propagation.Baggage{},
	))

	// Cleanup function
	shutdown := func(ctx context.Context) error {
		return tracerProvider.Shutdown(ctx)
	}

	return &Telemetry{
		TracerProvider: tracerProvider,
		Shutdown:       shutdown,
	}, nil
}
```

#### OTLP HTTP Exporter (Firewall-Friendly Alternative)

```go
// File: internal/telemetry/otlp_http.go
package telemetry

import (
	"context"
	"fmt"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.20.0"
)

// OTLPHTTPConfig holds OTLP HTTP exporter configuration.
type OTLPHTTPConfig struct {
	Endpoint       string            // OTLP collector HTTP endpoint (e.g., "http://localhost:4318")
	ServiceName    string            // Service name for traces
	ServiceVersion string            // Service version
	Environment    string            // Environment: dev, staging, prod
	SamplingRate   float64           // Trace sampling rate (0.0-1.0)
	Headers        map[string]string // Custom HTTP headers (e.g., API keys)
}

// InitOTLPHTTP initializes OpenTelemetry with OTLP HTTP exporter.
func InitOTLPHTTP(ctx context.Context, cfg OTLPHTTPConfig) (*Telemetry, error) {
	// Create resource with service metadata
	res, err := resource.New(ctx,
		resource.WithAttributes(
			semconv.ServiceName(cfg.ServiceName),
			semconv.ServiceVersion(cfg.ServiceVersion),
			semconv.DeploymentEnvironment(cfg.Environment),
		),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create resource: %w", err)
	}

	// Configure OTLP HTTP client options
	httpOpts := []otlptracehttp.Option{
		otlptracehttp.WithEndpoint(cfg.Endpoint),
		otlptracehttp.WithTimeout(10 * time.Second),
		otlptracehttp.WithRetry(otlptracehttp.RetryConfig{
			Enabled:         true,
			InitialInterval: 1 * time.Second,
			MaxInterval:     10 * time.Second,
			MaxElapsedTime:  30 * time.Second,
		}),
	}

	// Add custom headers if provided (e.g., API keys for SaaS backends)
	if len(cfg.Headers) > 0 {
		httpOpts = append(httpOpts, otlptracehttp.WithHeaders(cfg.Headers))
	}

	// Create OTLP HTTP exporter
	traceClient := otlptracehttp.NewClient(httpOpts...)
	traceExporter, err := otlptrace.New(ctx, traceClient)
	if err != nil {
		return nil, fmt.Errorf("failed to create OTLP HTTP exporter: %w", err)
	}

	// Create trace provider
	tracerProvider := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(traceExporter,
			sdktrace.WithBatchTimeout(5*time.Second),
			sdktrace.WithMaxExportBatchSize(512),
		),
		sdktrace.WithResource(res),
		sdktrace.WithSampler(sdktrace.ParentBased(sdktrace.TraceIDRatioBased(cfg.SamplingRate))),
	)

	otel.SetTracerProvider(tracerProvider)
	otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
		propagation.TraceContext{},
		propagation.Baggage{},
	))

	shutdown := func(ctx context.Context) error {
		return tracerProvider.Shutdown(ctx)
	}

	return &Telemetry{
		TracerProvider: tracerProvider,
		Shutdown:       shutdown,
	}, nil
}
```

**Usage with environment-based configuration:**

```go
// File: cmd/server/main.go
package main

import (
	"context"
	"log/slog"
	"os"

	"github.com/example/project/internal/telemetry"
)

func main() {
	ctx := context.Background()

	// Determine exporter type from environment
	exporterType := getEnv("OTEL_EXPORTER_TYPE", "otlp-grpc")

	var telem *telemetry.Telemetry
	var err error

	switch exporterType {
	case "otlp-grpc":
		telem, err = telemetry.InitOTLPGRPC(ctx, telemetry.OTLPGRPCConfig{
			Endpoint:       getEnv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317"),
			ServiceName:    "user-service",
			ServiceVersion: "1.0.0",
			Environment:    getEnv("ENVIRONMENT", "production"),
			SamplingRate:   0.1,
			Insecure:       getEnv("ENVIRONMENT", "production") == "development",
		})

	case "otlp-http":
		telem, err = telemetry.InitOTLPHTTP(ctx, telemetry.OTLPHTTPConfig{
			Endpoint:       getEnv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318"),
			ServiceName:    "user-service",
			ServiceVersion: "1.0.0",
			Environment:    getEnv("ENVIRONMENT", "production"),
			SamplingRate:   0.1,
			Headers: map[string]string{
				// Example: Add API key for SaaS backends (Honeycomb, Lightstep)
				// "x-honeycomb-team": os.Getenv("HONEYCOMB_API_KEY"),
			},
		})

	default:
		slog.Error("unknown OTEL_EXPORTER_TYPE", "type", exporterType)
		os.Exit(1)
	}

	if err != nil {
		slog.Error("failed to initialize telemetry", "error", err)
		os.Exit(1)
	}
	defer telem.Shutdown(ctx)

	// ... rest of application initialization ...
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
```

**Docker Compose with OpenTelemetry Collector:**

```yaml
version: '3.8'
services:
  # Application service
  user-service:
    build: .
    environment:
      - OTEL_EXPORTER_TYPE=otlp-grpc
      - OTEL_EXPORTER_OTLP_ENDPOINT=otel-collector:4317
      - ENVIRONMENT=production
    depends_on:
      - otel-collector

  # OpenTelemetry Collector (receives traces from services, exports to backends)
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml
    ports:
      - "4317:4317"   # OTLP gRPC receiver
      - "4318:4318"   # OTLP HTTP receiver
      - "8889:8889"   # Prometheus metrics exporter
      - "13133:13133" # Health check
    depends_on:
      - jaeger
      - prometheus

  # Jaeger (trace backend)
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686" # Jaeger UI

  # Prometheus (metrics backend)
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090" # Prometheus UI
```

**OpenTelemetry Collector configuration:**

```yaml
# File: otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 10s
    send_batch_size: 1024

exporters:
  # Export traces to Jaeger
  jaeger:
    endpoint: jaeger:14250
    tls:
      insecure: true

  # Export metrics to Prometheus
  prometheus:
    endpoint: 0.0.0.0:8889

  # Debug exporter (print to console)
  logging:
    loglevel: debug

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [jaeger, logging]

    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus, logging]
```

### 10.7 Distributed Tracing with Automatic net/http Instrumentation

Use `otelhttp` package to automatically instrument HTTP clients and servers with distributed tracing[^36][^46]. This enables cross-service trace propagation without manual span creation.

**Core Benefits:**
- **Zero-Code Instrumentation:** Wrap `http.Handler` or `http.RoundTripper` for automatic tracing
- **Cross-Service Propagation:** Trace context flows across service boundaries via HTTP headers
- **Standard Attributes:** Automatic capture of HTTP method, status code, URL, user agent
- **Client and Server:** Instrument both incoming requests (server) and outgoing calls (client)

#### Automatic Server Instrumentation with otelhttp

```go
// File: cmd/server/main.go (simplified example with otelhttp)
package main

import (
	"context"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"time"

	"github.com/example/project/internal/config"
	"github.com/example/project/internal/http/handler"
	"github.com/example/project/internal/telemetry"
	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
)

func main() {
	ctx := context.Background()

	// Initialize telemetry (OTLP gRPC from section 10.6)
	telem, err := telemetry.InitOTLPGRPC(ctx, telemetry.OTLPGRPCConfig{
		Endpoint:       "localhost:4317",
		ServiceName:    "user-service",
		ServiceVersion: "1.0.0",
		Environment:    "production",
		SamplingRate:   0.1,
		Insecure:       true,
	})
	if err != nil {
		slog.Error("failed to initialize telemetry", "error", err)
		os.Exit(1)
	}
	defer telem.Shutdown(ctx)

	// Create HTTP router
	mux := http.NewServeMux()

	// Health endpoints (no tracing overhead)
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("healthy"))
	})

	// Application routes
	userHandler := handler.NewUserHandler()
	mux.HandleFunc("GET /api/users/{id}", userHandler.GetUser)
	mux.HandleFunc("POST /api/users", userHandler.CreateUser)

	// Wrap entire mux with otelhttp for automatic tracing
	instrumentedHandler := otelhttp.NewHandler(mux, "user-service",
		otelhttp.WithSpanNameFormatter(func(operation string, r *http.Request) string {
			// Custom span name: "GET /api/users/{id}" instead of generic "HTTP GET"
			return r.Method + " " + r.URL.Path
		}),
	)

	// Start server
	server := &http.Server{
		Addr:    ":8080",
		Handler: instrumentedHandler,
	}

	go func() {
		slog.Info("server starting", "port", 8080)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			slog.Error("server error", "error", err)
		}
	}()

	// Graceful shutdown
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt)
	<-stop

	slog.Info("shutting down server...")
	shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	server.Shutdown(shutdownCtx)
}
```

#### Automatic HTTP Client Instrumentation with otelhttp

```go
// File: internal/client/order_client.go
package client

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
)

// OrderClient calls external order service with automatic tracing.
type OrderClient struct {
	baseURL    string
	httpClient *http.Client
}

// NewOrderClient creates HTTP client with automatic OTel instrumentation.
func NewOrderClient(baseURL string) *OrderClient {
	// Wrap http.DefaultTransport with otelhttp for automatic trace propagation
	instrumentedTransport := otelhttp.NewTransport(http.DefaultTransport,
		otelhttp.WithSpanNameFormatter(func(operation string, r *http.Request) string {
			return "HTTP " + r.Method + " " + r.URL.Path
		}),
	)

	return &OrderClient{
		baseURL: baseURL,
		httpClient: &http.Client{
			Transport: instrumentedTransport,
			Timeout:   10 * time.Second,
		},
	}
}

// GetOrder fetches order by ID with automatic trace propagation to order service.
func (c *OrderClient) GetOrder(ctx context.Context, orderID string) (*Order, error) {
	url := fmt.Sprintf("%s/api/orders/%s", c.baseURL, orderID)

	// Create HTTP request with context (context has parent span from caller)
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	// otelhttp.Transport automatically:
	// 1. Extracts trace context from ctx
	// 2. Injects W3C Trace Context headers (traceparent, tracestate)
	// 3. Creates child span for HTTP call
	// 4. Records HTTP attributes (method, status_code, url)
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to call order service: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("order service returned %d", resp.StatusCode)
	}

	var order Order
	if err := json.NewDecoder(resp.Body).Decode(&order); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &order, nil
}

type Order struct {
	ID     string  `json:"id"`
	Total  float64 `json:"total"`
	Status string  `json:"status"`
}
```

**Usage example showing cross-service trace propagation:**

```go
// File: internal/http/handler/checkout_handler.go
package handler

import (
	"log/slog"
	"net/http"

	"github.com/example/project/internal/client"
	"go.opentelemetry.io/otel"
)

type CheckoutHandler struct {
	orderClient *client.OrderClient
}

func (h *CheckoutHandler) ProcessCheckout(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context() // Context has trace span from otelhttp.NewHandler

	tracer := otel.Tracer("github.com/example/project")

	// Create manual span for business logic
	ctx, span := tracer.Start(ctx, "CheckoutHandler.ProcessCheckout")
	defer span.End()

	orderID := r.PathValue("order_id")

	slog.InfoContext(ctx, "processing checkout", "order_id", orderID)

	// Call order service - trace context automatically propagated
	// The HTTP client (OrderClient) automatically:
	// 1. Creates child span for HTTP request
	// 2. Injects trace context into HTTP headers (traceparent header)
	// 3. Order service extracts trace context from headers
	// 4. All spans linked in distributed trace
	order, err := h.orderClient.GetOrder(ctx, orderID)
	if err != nil {
		span.RecordError(err)
		slog.ErrorContext(ctx, "failed to fetch order", "order_id", orderID, "error", err)
		http.Error(w, "order not found", http.StatusNotFound)
		return
	}

	slog.InfoContext(ctx, "order fetched", "order_id", orderID, "total", order.Total)

	// ... process payment, update inventory, etc. ...

	w.Write([]byte("checkout successful"))
}
```

**Trace visualization in Jaeger:**

```
user-service: GET /api/checkout/{order_id}                    [200ms]
  ├─ CheckoutHandler.ProcessCheckout                          [195ms]
  │   ├─ HTTP GET /api/orders/{id}                            [50ms]
  │   │   └─ order-service: GET /api/orders/{id}              [45ms]
  │   │       ├─ OrderRepository.GetByID                      [30ms]
  │   │       │   └─ database query: SELECT * FROM orders     [25ms]
  │   │       └─ serialize response                           [10ms]
  │   ├─ PaymentService.ProcessPayment                        [80ms]
  │   │   └─ HTTP POST /api/payments                          [75ms]
  │   │       └─ payment-service: POST /api/payments          [70ms]
  │   └─ InventoryService.UpdateStock                         [40ms]
```

**Verification - Check HTTP headers for trace propagation:**

```bash
# Incoming request headers (extracted by otelhttp.NewHandler)
GET /api/checkout/order_123 HTTP/1.1
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
tracestate: vendor1=value1,vendor2=value2

# Outgoing request headers (injected by otelhttp.NewTransport)
GET /api/orders/order_123 HTTP/1.1
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-8c3c4ed519ae4f3a-01
# Note: Same trace ID (4bf92f3577b34da6a3ce929d0e0e4736), different span ID
```

### 10.8 Context Propagation Patterns and Common Mistakes

Proper `context.Context` propagation is critical for distributed tracing in Go[^40][^41]. Lost context = broken traces.

#### Pattern 1: Always Pass context.Context as First Parameter

**Go convention:** First parameter of functions should be `context.Context`[^47].

```go
// ✅ GOOD: Context as first parameter (Go convention)
func (s *Service) GetUser(ctx context.Context, userID string) (*User, error) {
	tracer := otel.Tracer("service")
	ctx, span := tracer.Start(ctx, "Service.GetUser")
	defer span.End()

	// Pass context to repository (preserves trace)
	return s.repo.FindByID(ctx, userID)
}

// ❌ BAD: No context parameter (trace context lost)
func (s *Service) GetUser(userID string) (*User, error) {
	// Cannot create span without context
	return s.repo.FindByID(userID)
}
```

#### Pattern 2: Propagate Context Through Goroutines

**Problem:** Goroutines don't inherit context automatically - must explicitly pass it[^40].

```go
// ❌ BAD: Spawning goroutine without context (trace context lost)
func (s *Service) ProcessAsync(ctx context.Context, data string) {
	go func() {
		// NO TRACE CONTEXT HERE - context.Background() creates orphan span
		s.repo.Save(context.Background(), data)
	}()
}

// ✅ GOOD: Pass context to goroutine (preserves trace)
func (s *Service) ProcessAsync(ctx context.Context, data string) {
	go func(ctx context.Context) {
		// Trace context preserved from parent
		s.repo.Save(ctx, data)
	}(ctx)
}
```

#### Pattern 3: Use context.WithTimeout for Bounded Operations

**Create child context with timeout while preserving trace context[^41].**

```go
// ✅ GOOD: Create timeout context while preserving trace
func (s *Service) CallExternalAPI(ctx context.Context, url string) (*Response, error) {
	tracer := otel.Tracer("service")
	ctx, span := tracer.Start(ctx, "Service.CallExternalAPI")
	defer span.End()

	// Create child context with 5s timeout (preserves trace context from parent)
	timeoutCtx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()

	req, _ := http.NewRequestWithContext(timeoutCtx, http.MethodGet, url, nil)
	// Trace context propagated to external service via HTTP headers
	return http.DefaultClient.Do(req)
}

// ❌ BAD: Using context.Background() loses trace
func (s *Service) CallExternalAPI(ctx context.Context, url string) (*Response, error) {
	// WRONG: context.Background() discards parent trace context
	timeoutCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	req, _ := http.NewRequestWithContext(timeoutCtx, http.MethodGet, url, nil)
	return http.DefaultClient.Do(req) // Orphan span - not linked to parent trace
}
```

#### Pattern 4: Extract Context from Middleware

**HTTP middleware provides context with trace span - always use `r.Context()`.**

```go
// ✅ GOOD: Use r.Context() from HTTP request (has trace span from otelhttp)
func (h *Handler) HandleRequest(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context() // Context has trace span from otelhttp.NewHandler

	// All downstream calls inherit trace context
	user, err := h.service.GetUser(ctx, r.PathValue("id"))
	if err != nil {
		slog.ErrorContext(ctx, "failed to get user", "error", err)
		return
	}

	// Log automatically includes trace_id (from OTelHandler in section 10.5)
	slog.InfoContext(ctx, "user fetched", "username", user.Username)
}

// ❌ BAD: Using context.Background() discards trace span
func (h *Handler) HandleRequest(w http.ResponseWriter, r *http.Request) {
	// WRONG: Creates new context without trace span
	ctx := context.Background()

	// This call creates orphan span (not linked to HTTP request trace)
	user, err := h.service.GetUser(ctx, r.PathValue("id"))
	// ...
}
```

#### Pattern 5: Detached Context for Background Tasks

**When spawning background work that should NOT inherit request timeout:**

```go
// ✅ GOOD: Detach context for background work while preserving trace
func (h *Handler) ProcessOrder(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context() // Has trace span + request timeout (e.g., 30s)

	order := parseOrder(r)

	// Save order synchronously (inherits request timeout)
	if err := h.service.SaveOrder(ctx, order); err != nil {
		http.Error(w, "failed to save order", http.StatusInternalServerError)
		return
	}

	// Respond immediately
	w.WriteHeader(http.StatusCreated)

	// Spawn background notification job AFTER response sent
	// Use detached context (no timeout) but PRESERVE trace context
	go func() {
		// Create new context with trace context but no timeout
		detachedCtx := trace.ContextWithSpanContext(
			context.Background(),
			trace.SpanContextFromContext(ctx), // Preserve trace ID
		)

		// This can run for 5 minutes without hitting request timeout
		h.notificationService.SendOrderConfirmation(detachedCtx, order.ID)
	}()
}
```

#### Common Mistake: Context Propagation in Database Queries

**Always pass context to database queries for trace correlation.**

```go
// ❌ BAD: Using context.Background() (orphan database span)
func (r *Repository) FindByID(userID string) (*User, error) {
	var user User
	// WRONG: context.Background() creates orphan span
	err := r.db.QueryRow(context.Background(), "SELECT * FROM users WHERE id = $1", userID).Scan(&user)
	return &user, err
}

// ✅ GOOD: Pass context from caller (trace link preserved)
func (r *Repository) FindByID(ctx context.Context, userID string) (*User, error) {
	tracer := otel.Tracer("repository")
	ctx, span := tracer.Start(ctx, "Repository.FindByID")
	defer span.End()

	var user User
	err := r.db.QueryRowContext(ctx, "SELECT * FROM users WHERE id = $1", userID).Scan(&user)
	return &user, err
}
```

### 10.9 Verification and Troubleshooting

#### Verify Trace Export to OTLP Collector

```bash
# Check OpenTelemetry Collector logs for received traces
$ docker logs otel-collector 2>&1 | grep -i trace

# Expected output:
# 2025-11-03T10:23:45.123Z info ResourceSpans #0
# Resource SchemaURL: https://opentelemetry.io/schemas/1.20.0
# Resource attributes:
#      -> service.name: Str(user-service)
#      -> service.version: Str(1.0.0)
# ScopeSpans #0
# Span #0
#     Trace ID       : 4bf92f3577b34da6a3ce929d0e0e4736
#     Parent ID      : 00f067aa0ba902b7
#     ID             : 8c3c4ed519ae4f3a
#     Name           : GET /api/users/{id}
#     Kind           : Server
#     Status code    : Ok
```

#### Verify Trace Context in HTTP Headers

```bash
# Use curl with verbose output to see trace headers
$ curl -v http://localhost:8080/api/users/user_123

# Expected request headers (if propagating from upstream):
> GET /api/users/user_123 HTTP/1.1
> traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01

# Check response headers (some systems echo trace ID for client correlation):
< X-Trace-Id: 4bf92f3577b34da6a3ce929d0e0e4736
```

#### Verify Logs Include Trace Context

```bash
# Filter application logs by trace_id
$ kubectl logs -l app=user-service --tail=100 | jq 'select(.trace_id != null)'

# Expected output (logs with trace context):
{
  "time": "2025-11-03T10:23:45.123Z",
  "level": "INFO",
  "msg": "fetching user",
  "user_id": "user_123",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "trace_sampled": true
}
```

#### Debug Missing Trace Context (Common Issues)

**Issue 1: Trace context lost in goroutines**

```bash
# Symptom: Orphan spans in Jaeger (no parent link)
# Cause: Goroutine spawned without passing context

# Fix: Always pass context to goroutines
go func(ctx context.Context) {
    // Use ctx here
}(ctx)
```

**Issue 2: context.Background() replaces trace context**

```bash
# Symptom: Logs missing trace_id field after certain point
# Cause: Code using context.Background() instead of parent context

# Fix: Search codebase for context.Background() and replace with ctx parameter
grep -rn "context.Background()" internal/
```

**Issue 3: HTTP client not instrumented**

```bash
# Symptom: Outgoing HTTP calls don't appear as child spans
# Cause: Using http.DefaultClient instead of instrumented client

# Fix: Wrap transport with otelhttp.NewTransport
client := &http.Client{
    Transport: otelhttp.NewTransport(http.DefaultTransport),
}
```

**Issue 4: Trace sampling excludes your traces**

```bash
# Symptom: No traces appear in Jaeger
# Cause: Sampling rate too low (e.g., 0.01 = 1%)

# Fix: Increase sampling rate temporarily for debugging
cfg.SamplingRate = 1.0 // Sample 100% of traces
# Or use error-aware sampler (section 10.2.3) to always sample errors
```

### 10.10 References

[^35]: OpenTelemetry Documentation, "Getting Started with OpenTelemetry Go," https://opentelemetry.io/docs/instrumentation/go/getting-started/, accessed 2025-11-02.

[^36]: Go OpenTelemetry, "net/http Instrumentation," https://pkg.go.dev/go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp, accessed 2025-11-02.

[^37]: CNCF, "OpenTelemetry Specification," https://github.com/open-telemetry/opentelemetry-specification, accessed 2025-11-02.

[^38]: Prometheus Documentation, "Go Client Library," https://prometheus.io/docs/guides/go-application/, accessed 2025-11-02.

[^39]: Prometheus, "prometheus/client_golang," https://github.com/prometheus/client_golang, accessed 2025-11-02.

[^40]: Go Blog, "Go Concurrency Patterns: Context," https://go.dev/blog/context, accessed 2025-11-02.

[^41]: Go Documentation, "context Package," https://pkg.go.dev/context, accessed 2025-11-02.

[^42]: OpenTelemetry Go, "Logging with slog," https://opentelemetry.io/docs/languages/go/instrumentation/#logging, accessed 2025-11-03.

[^43]: GitHub OpenTelemetry Go, "Bridge slog with OpenTelemetry," https://github.com/open-telemetry/opentelemetry-go-contrib/tree/main/bridges/otelslog, accessed 2025-11-03.

[^44]: OpenTelemetry Documentation, "OTLP Exporter Configuration," https://opentelemetry.io/docs/specs/otel/protocol/exporter/, accessed 2025-11-03.

[^45]: Go OpenTelemetry, "OTLP gRPC Exporter," https://pkg.go.dev/go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc, accessed 2025-11-03.

[^46]: OpenTelemetry Go Contrib, "Instrumentation Libraries," https://github.com/open-telemetry/opentelemetry-go-contrib/tree/main/instrumentation, accessed 2025-11-03.

[^47]: Go Code Review Comments, "Contexts," https://go.dev/wiki/CodeReviewComments#contexts, accessed 2025-11-03.

---

## 11. Audit Logging

### 11.1 Recommended Approach: Structured Audit Events with Immutable Storage

Audit logging captures security-sensitive events (authentication, authorization, data access, configuration changes) in an immutable, append-only format for compliance and forensics[^42][^43][^44]. Use structured events with `context.Context` propagation to capture user identity and request context.

**Core Benefits:**
- **Compliance:** Meet regulatory requirements (GDPR, SOC 2, HIPAA, PCI DSS)
- **Security Forensics:** Investigate security incidents with complete audit trail
- **Immutability:** Append-only storage prevents tampering with audit records
- **Structured Data:** Query audit events by user, resource, action, timestamp
- **Context Propagation:** Capture user identity from request context automatically

### 11.2 Implementation Examples

#### Audit Event Structs with Validation

```go
// File: internal/audit/event.go
package audit

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/go-playground/validator/v10"
)

// EventType represents the type of audited action.
type EventType string

const (
	// Authentication events
	EventUserLogin         EventType = "user.login"
	EventUserLogout        EventType = "user.logout"
	EventUserLoginFailed   EventType = "user.login_failed"
	EventPasswordChanged   EventType = "user.password_changed"

	// Authorization events
	EventAccessGranted     EventType = "access.granted"
	EventAccessDenied      EventType = "access.denied"
	EventPermissionChanged EventType = "permission.changed"

	// Data access events
	EventDataRead          EventType = "data.read"
	EventDataCreated       EventType = "data.created"
	EventDataUpdated       EventType = "data.updated"
	EventDataDeleted       EventType = "data.deleted"

	// Configuration events
	EventConfigChanged     EventType = "config.changed"
	EventFeatureFlagToggled EventType = "feature_flag.toggled"

	// Administrative events
	EventUserCreated       EventType = "admin.user_created"
	EventUserDeleted       EventType = "admin.user_deleted"
	EventRoleAssigned      EventType = "admin.role_assigned"
)

// Event represents a single audit event.
// Fields are immutable after creation - use pointer receivers for JSON marshaling only.
type Event struct {
	// Unique event identifier (UUID v4)
	ID string `json:"id" validate:"required,uuid4"`

	// Event timestamp (UTC)
	Timestamp time.Time `json:"timestamp" validate:"required"`

	// Event type (user.login, data.created, etc.)
	EventType EventType `json:"event_type" validate:"required"`

	// User context (who performed the action)
	UserID    int64  `json:"user_id" validate:"required,gt=0"`
	UserEmail string `json:"user_email" validate:"required,email"`
	Username  string `json:"username" validate:"required"`

	// Tenant context (multi-tenant systems)
	TenantID string `json:"tenant_id,omitempty" validate:"omitempty,uuid4"`

	// Request context (how action was performed)
	RequestID string `json:"request_id" validate:"required,uuid4"`
	IPAddress string `json:"ip_address" validate:"required,ip"`
	UserAgent string `json:"user_agent,omitempty"`

	// Resource context (what was affected)
	ResourceType string `json:"resource_type" validate:"required"` // "user", "order", "config"
	ResourceID   string `json:"resource_id" validate:"required"`

	// Action details
	Action      string                 `json:"action" validate:"required"` // "read", "create", "update", "delete"
	Status      string                 `json:"status" validate:"required,oneof=success failure"`
	ErrorReason string                 `json:"error_reason,omitempty"`     // If status=failure
	Metadata    map[string]interface{} `json:"metadata,omitempty"`         // Additional context

	// Computed fields (for compliance reporting)
	Date string `json:"date"` // YYYY-MM-DD (for date-based queries)
}

// Validate checks event for required fields and format.
func (e *Event) Validate() error {
	validate := validator.New()
	if err := validate.Struct(e); err != nil {
		return fmt.Errorf("audit event validation failed: %w", err)
	}
	return nil
}

// ToJSON marshals event to JSON bytes (for storage).
func (e *Event) ToJSON() ([]byte, error) {
	return json.Marshal(e)
}

// FromJSON unmarshals event from JSON bytes.
func FromJSON(data []byte) (*Event, error) {
	var event Event
	if err := json.Unmarshal(data, &event); err != nil {
		return nil, fmt.Errorf("failed to unmarshal audit event: %w", err)
	}

	if err := event.Validate(); err != nil {
		return nil, err
	}

	return &event, nil
}
```

#### Audit Middleware for HTTP Handlers

```go
// File: internal/http/middleware/audit.go
package middleware

import (
	"context"
	"net/http"
	"time"

	"github.com/example/project/internal/audit"
	"github.com/google/uuid"
)

// UserContext holds user information extracted from authentication.
type UserContext struct {
	UserID    int64
	UserEmail string
	Username  string
	TenantID  string
}

// contextKey is a private type for context keys (prevents collisions).
type contextKey string

const (
	userContextKey contextKey = "user_context"
	requestIDKey   contextKey = "request_id"
)

// WithUserContext adds user context to request context (from JWT, session, etc.).
func WithUserContext(ctx context.Context, user UserContext) context.Context {
	return context.WithValue(ctx, userContextKey, user)
}

// GetUserContext extracts user context from request context.
func GetUserContext(ctx context.Context) (UserContext, bool) {
	user, ok := ctx.Value(userContextKey).(UserContext)
	return user, ok
}

// WithRequestID adds request ID to context.
func WithRequestID(ctx context.Context, requestID string) context.Context {
	return context.WithValue(ctx, requestIDKey, requestID)
}

// GetRequestID extracts request ID from context.
func GetRequestID(ctx context.Context) string {
	requestID, _ := ctx.Value(requestIDKey).(string)
	return requestID
}

// AuditMiddleware adds audit logging to HTTP handlers.
func AuditMiddleware(logger audit.Logger) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Generate request ID
			requestID := uuid.New().String()
			ctx := WithRequestID(r.Context(), requestID)

			// Extract user context (assumes auth middleware ran first)
			user, ok := GetUserContext(ctx)
			if !ok {
				// No user context - skip audit (unauthenticated request)
				next.ServeHTTP(w, r.WithContext(ctx))
				return
			}

			// Wrap response writer to capture status code
			rw := &auditResponseWriter{ResponseWriter: w, statusCode: http.StatusOK}

			// Continue with request handling
			start := time.Now()
			next.ServeHTTP(rw, r.WithContext(ctx))
			duration := time.Since(start)

			// Log audit event after request completes
			event := &audit.Event{
				ID:           uuid.New().String(),
				Timestamp:    time.Now().UTC(),
				EventType:    mapHTTPMethodToEventType(r.Method),
				UserID:       user.UserID,
				UserEmail:    user.UserEmail,
				Username:     user.Username,
				TenantID:     user.TenantID,
				RequestID:    requestID,
				IPAddress:    extractIPAddress(r),
				UserAgent:    r.UserAgent(),
				ResourceType: extractResourceType(r.URL.Path),
				ResourceID:   extractResourceID(r.URL.Path),
				Action:       mapHTTPMethodToAction(r.Method),
				Status:       mapStatusCodeToStatus(rw.statusCode),
				Metadata: map[string]interface{}{
					"http_method":      r.Method,
					"http_path":        r.URL.Path,
					"http_status_code": rw.statusCode,
					"duration_ms":      duration.Milliseconds(),
				},
				Date: time.Now().UTC().Format("2006-01-02"),
			}

			// Write audit event (async, non-blocking)
			if err := logger.LogAsync(ctx, event); err != nil {
				// Log error but don't fail request
				// TODO: Alert on audit logging failures
			}
		})
	}
}

type auditResponseWriter struct {
	http.ResponseWriter
	statusCode int
}

func (rw *auditResponseWriter) WriteHeader(code int) {
	rw.statusCode = code
	rw.ResponseWriter.WriteHeader(code)
}

// mapHTTPMethodToEventType maps HTTP method to audit event type.
func mapHTTPMethodToEventType(method string) audit.EventType {
	switch method {
	case http.MethodGet:
		return audit.EventDataRead
	case http.MethodPost:
		return audit.EventDataCreated
	case http.MethodPut, http.MethodPatch:
		return audit.EventDataUpdated
	case http.MethodDelete:
		return audit.EventDataDeleted
	default:
		return audit.EventType("http." + method)
	}
}

// mapHTTPMethodToAction maps HTTP method to action string.
func mapHTTPMethodToAction(method string) string {
	switch method {
	case http.MethodGet:
		return "read"
	case http.MethodPost:
		return "create"
	case http.MethodPut, http.MethodPatch:
		return "update"
	case http.MethodDelete:
		return "delete"
	default:
		return method
	}
}

// mapStatusCodeToStatus maps HTTP status code to success/failure.
func mapStatusCodeToStatus(code int) string {
	if code >= 200 && code < 400 {
		return "success"
	}
	return "failure"
}

// extractIPAddress extracts client IP from request headers or RemoteAddr.
func extractIPAddress(r *http.Request) string {
	// Check X-Forwarded-For header (if behind proxy)
	if xff := r.Header.Get("X-Forwarded-For"); xff != "" {
		return xff
	}

	// Check X-Real-IP header
	if xri := r.Header.Get("X-Real-IP"); xri != "" {
		return xri
	}

	// Use RemoteAddr as fallback
	return r.RemoteAddr
}

// extractResourceType extracts resource type from URL path.
// Example: /api/users/123 → "user"
func extractResourceType(path string) string {
	// Simple implementation - enhance with routing metadata
	if len(path) > 5 && path[:5] == "/api/" {
		// Extract first path segment after /api/
		remaining := path[5:]
		for i, ch := range remaining {
			if ch == '/' {
				return remaining[:i]
			}
		}
		return remaining
	}
	return "unknown"
}

// extractResourceID extracts resource ID from URL path.
// Example: /api/users/123 → "123"
func extractResourceID(path string) string {
	// Simple implementation - enhance with routing metadata
	// Returns last path segment
	for i := len(path) - 1; i >= 0; i-- {
		if path[i] == '/' {
			return path[i+1:]
		}
	}
	return path
}
```

#### Audit Repository Interface (Write-Only)

```go
// File: internal/audit/repository.go
package audit

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	_ "github.com/lib/pq" // PostgreSQL driver
)

// Logger defines audit logging interface (write-only for services).
type Logger interface {
	// Log writes audit event synchronously (blocking).
	Log(ctx context.Context, event *Event) error

	// LogAsync writes audit event asynchronously (non-blocking).
	LogAsync(ctx context.Context, event *Event) error
}

// PostgresLogger implements audit logging to PostgreSQL database.
type PostgresLogger struct {
	db          *sql.DB
	asyncBuffer chan *Event // Buffered channel for async writes
	stopCh      chan struct{}
}

// NewPostgresLogger creates audit logger with async background writer.
func NewPostgresLogger(db *sql.DB, bufferSize int) *PostgresLogger {
	logger := &PostgresLogger{
		db:          db,
		asyncBuffer: make(chan *Event, bufferSize),
		stopCh:      make(chan struct{}),
	}

	// Start background writer goroutine
	go logger.backgroundWriter()

	return logger
}

// Log writes audit event synchronously (blocks until written).
func (l *PostgresLogger) Log(ctx context.Context, event *Event) error {
	// Validate event before writing
	if err := event.Validate(); err != nil {
		return err
	}

	// Write to database (blocking)
	query := `
		INSERT INTO audit_events (
			id, timestamp, event_type, user_id, user_email, username, tenant_id,
			request_id, ip_address, user_agent, resource_type, resource_id,
			action, status, error_reason, metadata, date
		) VALUES (
			$1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17
		)
	`

	metadataJSON, err := event.ToJSON()
	if err != nil {
		return fmt.Errorf("failed to marshal event metadata: %w", err)
	}

	_, err = l.db.ExecContext(ctx, query,
		event.ID, event.Timestamp, event.EventType,
		event.UserID, event.UserEmail, event.Username, event.TenantID,
		event.RequestID, event.IPAddress, event.UserAgent,
		event.ResourceType, event.ResourceID,
		event.Action, event.Status, event.ErrorReason,
		metadataJSON, event.Date,
	)

	if err != nil {
		return fmt.Errorf("failed to write audit event: %w", err)
	}

	return nil
}

// LogAsync writes audit event asynchronously (non-blocking).
// Sends event to buffered channel, background goroutine writes to database.
func (l *PostgresLogger) LogAsync(ctx context.Context, event *Event) error {
	// Validate event before queuing
	if err := event.Validate(); err != nil {
		return err
	}

	// Send to async buffer (non-blocking if buffer not full)
	select {
	case l.asyncBuffer <- event:
		return nil
	default:
		// Buffer full - write synchronously to avoid dropping events
		return l.Log(ctx, event)
	}
}

// backgroundWriter processes async audit events from buffer.
func (l *PostgresLogger) backgroundWriter() {
	for {
		select {
		case event := <-l.asyncBuffer:
			// Write event to database (with retry on transient errors)
			ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
			if err := l.Log(ctx, event); err != nil {
				// TODO: Implement retry logic and dead-letter queue
				// For now, log error (don't drop event silently)
				fmt.Printf("ERROR: failed to write audit event: %v\n", err)
			}
			cancel()

		case <-l.stopCh:
			// Drain remaining events before stopping
			for len(l.asyncBuffer) > 0 {
				event := <-l.asyncBuffer
				ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
				l.Log(ctx, event)
				cancel()
			}
			return
		}
	}
}

// Close stops background writer and flushes remaining events.
func (l *PostgresLogger) Close() error {
	close(l.stopCh)
	// Wait for background writer to finish
	time.Sleep(100 * time.Millisecond)
	return nil
}
```

#### Audit Query Service (Read-Only, Compliance)

```go
// File: internal/audit/query.go
package audit

import (
	"context"
	"database/sql"
	"fmt"
	"time"
)

// QueryService provides read-only access to audit events (for compliance reporting).
type QueryService struct {
	db *sql.DB
}

// NewQueryService creates audit query service.
func NewQueryService(db *sql.DB) *QueryService {
	return &QueryService{db: db}
}

// QueryParams holds audit event query parameters.
type QueryParams struct {
	// Filter by user
	UserID    *int64
	UserEmail *string

	// Filter by resource
	ResourceType *string
	ResourceID   *string

	// Filter by action
	EventType *EventType
	Action    *string
	Status    *string

	// Filter by time range
	StartDate time.Time
	EndDate   time.Time

	// Pagination
	Limit  int
	Offset int
}

// Query retrieves audit events matching filters.
func (s *QueryService) Query(ctx context.Context, params QueryParams) ([]*Event, error) {
	// Build dynamic query with filters
	query := `
		SELECT id, timestamp, event_type, user_id, user_email, username, tenant_id,
		       request_id, ip_address, user_agent, resource_type, resource_id,
		       action, status, error_reason, metadata, date
		FROM audit_events
		WHERE timestamp >= $1 AND timestamp < $2
	`
	args := []interface{}{params.StartDate, params.EndDate}
	argIndex := 3

	// Add optional filters
	if params.UserID != nil {
		query += fmt.Sprintf(" AND user_id = $%d", argIndex)
		args = append(args, *params.UserID)
		argIndex++
	}

	if params.UserEmail != nil {
		query += fmt.Sprintf(" AND user_email = $%d", argIndex)
		args = append(args, *params.UserEmail)
		argIndex++
	}

	if params.ResourceType != nil {
		query += fmt.Sprintf(" AND resource_type = $%d", argIndex)
		args = append(args, *params.ResourceType)
		argIndex++
	}

	if params.ResourceID != nil {
		query += fmt.Sprintf(" AND resource_id = $%d", argIndex)
		args = append(args, *params.ResourceID)
		argIndex++
	}

	if params.EventType != nil {
		query += fmt.Sprintf(" AND event_type = $%d", argIndex)
		args = append(args, string(*params.EventType))
		argIndex++
	}

	if params.Action != nil {
		query += fmt.Sprintf(" AND action = $%d", argIndex)
		args = append(args, *params.Action)
		argIndex++
	}

	if params.Status != nil {
		query += fmt.Sprintf(" AND status = $%d", argIndex)
		args = append(args, *params.Status)
		argIndex++
	}

	// Order by timestamp descending (most recent first)
	query += " ORDER BY timestamp DESC"

	// Add pagination
	if params.Limit > 0 {
		query += fmt.Sprintf(" LIMIT $%d", argIndex)
		args = append(args, params.Limit)
		argIndex++
	}

	if params.Offset > 0 {
		query += fmt.Sprintf(" OFFSET $%d", argIndex)
		args = append(args, params.Offset)
		argIndex++
	}

	// Execute query
	rows, err := s.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, fmt.Errorf("failed to query audit events: %w", err)
	}
	defer rows.Close()

	// Scan results
	var events []*Event
	for rows.Next() {
		var event Event
		var metadataJSON []byte

		err := rows.Scan(
			&event.ID, &event.Timestamp, &event.EventType,
			&event.UserID, &event.UserEmail, &event.Username, &event.TenantID,
			&event.RequestID, &event.IPAddress, &event.UserAgent,
			&event.ResourceType, &event.ResourceID,
			&event.Action, &event.Status, &event.ErrorReason,
			&metadataJSON, &event.Date,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan audit event: %w", err)
		}

		// Unmarshal metadata JSON
		if len(metadataJSON) > 0 {
			if err := json.Unmarshal(metadataJSON, &event.Metadata); err != nil {
				return nil, fmt.Errorf("failed to unmarshal metadata: %w", err)
			}
		}

		events = append(events, &event)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("audit events query error: %w", err)
	}

	return events, nil
}

// GetByRequestID retrieves all audit events for a request ID (trace full request flow).
func (s *QueryService) GetByRequestID(ctx context.Context, requestID string) ([]*Event, error) {
	query := `
		SELECT id, timestamp, event_type, user_id, user_email, username, tenant_id,
		       request_id, ip_address, user_agent, resource_type, resource_id,
		       action, status, error_reason, metadata, date
		FROM audit_events
		WHERE request_id = $1
		ORDER BY timestamp ASC
	`

	rows, err := s.db.QueryContext(ctx, query, requestID)
	if err != nil {
		return nil, fmt.Errorf("failed to query audit events by request_id: %w", err)
	}
	defer rows.Close()

	var events []*Event
	for rows.Next() {
		var event Event
		var metadataJSON []byte

		err := rows.Scan(
			&event.ID, &event.Timestamp, &event.EventType,
			&event.UserID, &event.UserEmail, &event.Username, &event.TenantID,
			&event.RequestID, &event.IPAddress, &event.UserAgent,
			&event.ResourceType, &event.ResourceID,
			&event.Action, &event.Status, &event.ErrorReason,
			&metadataJSON, &event.Date,
		)
		if err != nil {
			return nil, err
		}

		if len(metadataJSON) > 0 {
			json.Unmarshal(metadataJSON, &event.Metadata)
		}

		events = append(events, &event)
	}

	return events, nil
}
```

**Database schema for audit events:**

```sql
-- File: migrations/001_create_audit_events_table.sql
CREATE TABLE IF NOT EXISTS audit_events (
    -- Primary key (UUID)
    id UUID PRIMARY KEY,

    -- Event metadata
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    date DATE NOT NULL, -- For date-based partitioning

    -- User context
    user_id BIGINT NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    tenant_id UUID, -- NULL for single-tenant systems

    -- Request context
    request_id UUID NOT NULL,
    ip_address VARCHAR(45) NOT NULL, -- IPv4/IPv6
    user_agent TEXT,

    -- Resource context
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(255) NOT NULL,

    -- Action details
    action VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'failure')),
    error_reason TEXT,
    metadata JSONB, -- Additional context

    -- Indexes for common queries
    CONSTRAINT audit_events_timestamp_not_null CHECK (timestamp IS NOT NULL)
);

-- Indexes for performance
CREATE INDEX idx_audit_events_user_id ON audit_events (user_id, timestamp DESC);
CREATE INDEX idx_audit_events_resource ON audit_events (resource_type, resource_id, timestamp DESC);
CREATE INDEX idx_audit_events_request_id ON audit_events (request_id);
CREATE INDEX idx_audit_events_date ON audit_events (date DESC);
CREATE INDEX idx_audit_events_event_type ON audit_events (event_type, timestamp DESC);

-- Partitioning by date for large-scale systems (PostgreSQL 10+)
-- CREATE TABLE audit_events PARTITION BY RANGE (date);
-- CREATE TABLE audit_events_2025_01 PARTITION OF audit_events
--     FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

### 11.2.1 Audit Logging Patterns

#### Pattern 1: Database Audit Trail (Recommended for Compliance)

Store audit events in dedicated database table (PostgreSQL, MySQL) for ACID guarantees and SQL querying[^42][^44].

**Benefits:**
- ✅ **ACID Compliance:** Transactions ensure atomicity and consistency
- ✅ **SQL Queries:** Rich querying for compliance reports
- ✅ **Partitioning:** Date-based partitioning for large-scale systems
- ✅ **Immutability:** Revoke UPDATE/DELETE permissions on audit table

**Drawbacks:**
- ❌ **Write Overhead:** Audit writes add latency to requests (5-10ms)
- ❌ **Storage Cost:** Audit table grows rapidly (GB/day for high-traffic systems)

**Use When:**
- Regulatory compliance requires immutable audit trail (SOC 2, GDPR, HIPAA)
- Need rich SQL queries for compliance reporting
- Can tolerate write overhead for compliance benefits

#### Pattern 2: Event Stream (Kafka, NATS)

Stream audit events to message broker for decoupled, high-throughput auditing[^45][^46].

```go
// File: internal/audit/kafka_logger.go
package audit

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/segmentio/kafka-go"
)

// KafkaLogger streams audit events to Kafka topic.
type KafkaLogger struct {
	writer *kafka.Writer
}

// NewKafkaLogger creates Kafka audit logger.
func NewKafkaLogger(brokers []string, topic string) *KafkaLogger {
	return &KafkaLogger{
		writer: &kafka.Writer{
			Addr:     kafka.TCP(brokers...),
			Topic:    topic,
			Balancer: &kafka.LeastBytes{},
		},
	}
}

// Log writes audit event to Kafka (async, non-blocking).
func (l *KafkaLogger) Log(ctx context.Context, event *Event) error {
	// Marshal event to JSON
	eventJSON, err := event.ToJSON()
	if err != nil {
		return err
	}

	// Write to Kafka (async)
	err = l.writer.WriteMessages(ctx, kafka.Message{
		Key:   []byte(event.UserID), // Partition by user ID
		Value: eventJSON,
	})

	if err != nil {
		return fmt.Errorf("failed to write audit event to Kafka: %w", err)
	}

	return nil
}

func (l *KafkaLogger) LogAsync(ctx context.Context, event *Event) error {
	// Kafka writes are already async - use same implementation
	return l.Log(ctx, event)
}

func (l *KafkaLogger) Close() error {
	return l.writer.Close()
}
```

**Benefits:**
- ✅ **High Throughput:** Kafka handles millions of events/sec
- ✅ **Decoupling:** Audit consumers independent of producers
- ✅ **Scalability:** Horizontal scaling via partitions

**Drawbacks:**
- ❌ **Operational Complexity:** Kafka cluster management overhead
- ❌ **No SQL Queries:** Must stream to database for querying

**Use When:**
- High-traffic systems (>10K requests/sec)
- Need decoupled audit processing (real-time alerts, analytics)
- Have Kafka infrastructure for event streaming

#### Pattern 3: Hybrid Approach (Database + Event Stream)

Write audit events to both database (for compliance queries) and event stream (for real-time monitoring)[^42][^45].

**Benefits:**
- ✅ **Best of Both:** SQL queries + real-time streaming
- ✅ **Redundancy:** Audit events stored in multiple systems

**Drawbacks:**
- ❌ **Complexity:** Maintain two audit systems
- ❌ **Cost:** Storage cost for both database and Kafka retention

**Use When:**
- Need both compliance reporting (SQL) and real-time monitoring (streaming)
- Have budget for dual storage

#### Pattern 4: Centralized Audit Service (gRPC)

Centralize audit logging in dedicated microservice with gRPC API[^47].

```go
// File: audit-service/api/audit.proto
syntax = "proto3";

package audit;

service AuditService {
  rpc LogEvent (AuditEvent) returns (LogEventResponse);
  rpc QueryEvents (QueryEventsRequest) returns (QueryEventsResponse);
}

message AuditEvent {
  string id = 1;
  int64 timestamp = 2;
  string event_type = 3;
  int64 user_id = 4;
  string user_email = 5;
  string username = 6;
  string tenant_id = 7;
  string request_id = 8;
  string ip_address = 9;
  string user_agent = 10;
  string resource_type = 11;
  string resource_id = 12;
  string action = 13;
  string status = 14;
  string error_reason = 15;
  map<string, string> metadata = 16;
  string date = 17;
}

message LogEventResponse {
  bool success = 1;
  string error = 2;
}

message QueryEventsRequest {
  int64 user_id = 1;
  string start_date = 2;
  string end_date = 3;
  int32 limit = 4;
  int32 offset = 5;
}

message QueryEventsResponse {
  repeated AuditEvent events = 1;
}
```

**Benefits:**
- ✅ **Centralized:** Single audit service for all microservices
- ✅ **Policy Enforcement:** Audit rules enforced in one place
- ✅ **Specialized Storage:** Optimize audit database separately

**Drawbacks:**
- ❌ **Single Point of Failure:** Audit service unavailability affects all services
- ❌ **Network Overhead:** gRPC call per audit event

**Use When:**
- Many microservices requiring consistent audit logging
- Need centralized audit policy enforcement
- Have service mesh for reliable inter-service communication

### 11.2.2 Common Audit Mistakes

#### Mistake 1: Not Capturing User Context from context.Context

**Problem:** Missing user identity in audit events makes forensics impossible[^42].

**❌ Bad Example:**

```go
func (h *Handler) DeleteUser(w http.ResponseWriter, r *http.Request) {
	// BAD: Hard-coded or missing user context
	auditEvent := &audit.Event{
		UserID:    0, // Missing!
		UserEmail: "unknown",
		Action:    "delete",
		// ...
	}
	logger.Log(r.Context(), auditEvent)
}
```

**✅ Good Example:**

```go
func (h *Handler) DeleteUser(w http.ResponseWriter, r *http.Request) {
	// GOOD: Extract user from context (set by auth middleware)
	user, ok := middleware.GetUserContext(r.Context())
	if !ok {
		http.Error(w, "unauthorized", http.StatusUnauthorized)
		return
	}

	auditEvent := &audit.Event{
		UserID:    user.UserID,
		UserEmail: user.UserEmail,
		Username:  user.Username,
		Action:    "delete",
		// ...
	}
	logger.Log(r.Context(), auditEvent)
}
```

#### Mistake 2: Mutable Audit Records (Allowing Updates/Deletes)

**Problem:** Mutable audit trail violates compliance requirements (tampering risk)[^42][^44].

**❌ Bad Example:**

```sql
-- BAD: Users can update/delete audit records
GRANT SELECT, INSERT, UPDATE, DELETE ON audit_events TO app_user;
```

**✅ Good Example:**

```sql
-- GOOD: Append-only audit table (no UPDATE/DELETE permissions)
GRANT SELECT, INSERT ON audit_events TO app_user;

-- Revoke dangerous permissions explicitly
REVOKE UPDATE, DELETE ON audit_events FROM app_user;

-- Optional: Row-level security to prevent deletion
ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY audit_events_no_delete ON audit_events FOR DELETE USING (false);
CREATE POLICY audit_events_no_update ON audit_events FOR UPDATE USING (false);
```

#### Mistake 3: Missing Critical Events (Auth Failures, Privilege Escalation)

**Problem:** Not auditing security-critical events like failed logins, permission denials[^43][^44].

**❌ Bad Example:**

```go
func (s *AuthService) Login(email, password string) error {
	user, err := s.repo.GetByEmail(email)
	if err != nil {
		return err // No audit event for failed login!
	}

	if !s.checkPassword(user, password) {
		return errors.New("invalid password") // No audit event!
	}

	return nil
}
```

**✅ Good Example:**

```go
func (s *AuthService) Login(ctx context.Context, email, password string) error {
	user, err := s.repo.GetByEmail(email)
	if err != nil {
		// Audit failed login attempt
		s.auditLogger.Log(ctx, &audit.Event{
			EventType:   audit.EventUserLoginFailed,
			UserEmail:   email,
			Status:      "failure",
			ErrorReason: "user not found",
			// ...
		})
		return err
	}

	if !s.checkPassword(user, password) {
		// Audit invalid password
		s.auditLogger.Log(ctx, &audit.Event{
			EventType:   audit.EventUserLoginFailed,
			UserID:      user.ID,
			UserEmail:   email,
			Status:      "failure",
			ErrorReason: "invalid password",
			// ...
		})
		return errors.New("invalid password")
	}

	// Audit successful login
	s.auditLogger.Log(ctx, &audit.Event{
		EventType: audit.EventUserLogin,
		UserID:    user.ID,
		UserEmail: email,
		Status:    "success",
		// ...
	})

	return nil
}
```

### 11.2.3 Verification and Troubleshooting

#### Audit Completeness Verification

```go
// File: internal/audit/verification.go
package audit

import (
	"context"
	"fmt"
	"time"
)

// VerifyCompleteness checks if all expected audit events exist for a request.
func (s *QueryService) VerifyCompleteness(ctx context.Context, requestID string, expectedEvents []EventType) error {
	events, err := s.GetByRequestID(ctx, requestID)
	if err != nil {
		return fmt.Errorf("failed to fetch audit events: %w", err)
	}

	// Build map of actual events
	actualEvents := make(map[EventType]bool)
	for _, event := range events {
		actualEvents[event.EventType] = true
	}

	// Check for missing expected events
	var missing []EventType
	for _, expected := range expectedEvents {
		if !actualEvents[expected] {
			missing = append(missing, expected)
		}
	}

	if len(missing) > 0 {
		return fmt.Errorf("missing audit events: %v", missing)
	}

	return nil
}

// VerifyTimeline checks if audit events occurred in expected order.
func (s *QueryService) VerifyTimeline(ctx context.Context, requestID string) error {
	events, err := s.GetByRequestID(ctx, requestID)
	if err != nil {
		return err
	}

	// Events should be chronologically ordered
	for i := 1; i < len(events); i++ {
		if events[i].Timestamp.Before(events[i-1].Timestamp) {
			return fmt.Errorf("audit events out of order: event %d before event %d", i, i-1)
		}
	}

	return nil
}
```

#### Audit Trail Integrity Checks (Cryptographic Signatures)

```go
// File: internal/audit/integrity.go
package audit

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
)

// ComputeEventSignature computes HMAC-SHA256 signature for audit event.
func ComputeEventSignature(event *Event, secretKey []byte) string {
	// Canonical representation for signing
	canonical := fmt.Sprintf("%s|%d|%s|%s|%s|%s",
		event.ID,
		event.Timestamp.Unix(),
		event.EventType,
		event.UserID,
		event.ResourceType,
		event.ResourceID,
	)

	// Compute HMAC-SHA256
	h := hmac.New(sha256.New, secretKey)
	h.Write([]byte(canonical))
	signature := h.Sum(nil)

	return hex.EncodeToString(signature)
}

// VerifyEventSignature verifies audit event signature.
func VerifyEventSignature(event *Event, signature string, secretKey []byte) bool {
	expected := ComputeEventSignature(event, secretKey)
	return hmac.Equal([]byte(signature), []byte(expected))
}
```

#### Compliance Reporting with SQL Queries

```sql
-- User activity report (GDPR compliance)
SELECT
    event_type,
    timestamp,
    action,
    resource_type,
    resource_id,
    status
FROM audit_events
WHERE user_email = 'user@example.com'
    AND date >= '2025-01-01'
    AND date < '2025-02-01'
ORDER BY timestamp DESC;

-- Failed login attempts (security monitoring)
SELECT
    user_email,
    ip_address,
    COUNT(*) AS failed_attempts,
    MAX(timestamp) AS last_attempt
FROM audit_events
WHERE event_type = 'user.login_failed'
    AND date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY user_email, ip_address
HAVING COUNT(*) >= 5
ORDER BY failed_attempts DESC;

-- Data access by resource (audit trail for specific record)
SELECT
    timestamp,
    user_email,
    action,
    status,
    ip_address
FROM audit_events
WHERE resource_type = 'order'
    AND resource_id = '12345'
ORDER BY timestamp DESC;

-- Administrative actions (privilege escalation monitoring)
SELECT
    timestamp,
    user_email,
    event_type,
    resource_id,
    metadata
FROM audit_events
WHERE event_type IN ('admin.user_created', 'admin.role_assigned', 'permission.changed')
    AND date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY timestamp DESC;
```

### 11.3 Alternative Approaches

**Database Audit Tables vs. Event Streaming:**

| Aspect | Database Audit Table | Event Streaming (Kafka) |
|--------|---------------------|------------------------|
| **Compliance** | ✅ ACID guarantees | ⚠️ Eventually consistent |
| **Query Capability** | ✅ Rich SQL queries | ❌ Stream processing only |
| **Throughput** | ⚠️ Limited by DB writes | ✅ Millions events/sec |
| **Operational Cost** | ✅ Simple (existing DB) | ⚠️ Kafka cluster overhead |
| **Immutability** | ✅ Revoke UPDATE/DELETE | ✅ Append-only log |

**Synchronous vs. Buffered Async Audit Logging:**

| Aspect | Synchronous | Buffered Async |
|--------|------------|---------------|
| **Latency Impact** | ⚠️ +5-10ms per request | ✅ <1ms (non-blocking) |
| **Reliability** | ✅ Guaranteed write before response | ⚠️ May lose events if crash |
| **Complexity** | ✅ Simple | ⚠️ Buffering logic required |

**Self-Managed vs. Managed Audit Services:**

| Aspect | Self-Managed | Managed (AWS CloudTrail, Datadog) |
|--------|--------------|----------------------------------|
| **Cost** | ✅ Infrastructure only | ⚠️ Per-event pricing |
| **Ops Burden** | ⚠️ Database/Kafka management | ✅ Fully managed |
| **Compliance** | ✅ Full control | ✅ SOC 2/HIPAA certified |
| **Customization** | ✅ Full flexibility | ⚠️ Limited to provider features |

### 11.4 Decision Criteria

**Compliance Requirements Drive Architecture:**
- **SOC 2 Type II:** Requires immutable audit trail with SQL query capability → Database audit table
- **HIPAA:** Requires audit of all PHI access → Capture all data.read events
- **GDPR:** Requires user data access reports → Index audit events by user_email
- **PCI DSS:** Requires audit of payment operations → Capture all payment-related events

**Audit Query Patterns:**
- **Real-Time Monitoring:** Need instant alerts on suspicious activity → Event streaming (Kafka + real-time consumers)
- **Batch Compliance Reports:** Monthly/quarterly reports for auditors → Database audit table with SQL queries
- **Security Forensics:** Investigate security incidents after the fact → Database audit table with rich indexing

**Retention Policies:**
- **Short-Term (30 days):** In-memory audit log with log rotation
- **Medium-Term (1-7 years):** Database audit table with date-based partitioning
- **Long-Term (7+ years):** Archive to cold storage (S3 Glacier) after active period

### 11.5 References

[^42]: OWASP, "Logging Cheat Sheet," https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html, accessed 2025-11-02.

[^43]: NIST, "Guide to Computer Security Log Management (SP 800-92)," https://csrc.nist.gov/publications/detail/sp/800-92/final, accessed 2025-11-02.

[^44]: GDPR, "Article 30: Records of Processing Activities," https://gdpr-info.eu/art-30-gdpr/, accessed 2025-11-02.

[^45]: Apache Kafka Documentation, "Use Cases: Logging," https://kafka.apache.org/uses#uses_logs, accessed 2025-11-02.

[^46]: NATS Documentation, "NATS Streaming," https://docs.nats.io/nats-streaming-concepts/intro, accessed 2025-11-02.

[^47]: gRPC Documentation, "Go Quick Start," https://grpc.io/docs/languages/go/quickstart/, accessed 2025-11-02.

---

## References

[^1]: DEV Community, "A Guide to Configuration Management in Go with Viper," https://dev.to/kittipat1413/a-guide-to-configuration-management-in-go-with-viper-5271, accessed 2025-11-01.

[^2]: Go Blog, "Structured Logging with slog," https://go.dev/blog/slog, accessed 2025-11-01.

[^3]: go-redis Documentation, "Redis Client for Go," https://redis.uptrace.dev/, accessed 2025-11-01.

[^4]: Go Documentation, "database/sql Package," https://pkg.go.dev/database/sql, accessed 2025-11-01.

[^5]: The Twelve-Factor App, "III. Config," https://12factor.net/config, accessed 2025-11-01.

[^6]: GitHub, "spf13/viper: Go configuration with fangs," https://github.com/spf13/viper, accessed 2025-11-01.

[^7]: Go Documentation, "flag Package," https://pkg.go.dev/flag, accessed 2025-11-01.

[^8]: Go Documentation, "log/slog Package," https://pkg.go.dev/log/slog, accessed 2025-11-01.

[^9]: Dave Cheney, "Let's talk about logging," https://dave.cheney.net/2015/11/05/lets-talk-about-logging, accessed 2025-11-01.

[^10]: GitHub, "rs/zerolog: Zero Allocation JSON Logger," https://github.com/rs/zerolog, accessed 2025-11-01.

[^11]: GitHub, "uber-go/zap: Blazing fast, structured, leveled logging in Go," https://github.com/uber-go/zap, accessed 2025-11-01.

[^12]: redis.uptrace.dev, "Go Redis Connection Pool," https://redis.uptrace.dev/guide/go-redis-connection-pool.html, accessed 2025-11-01.

[^13]: Medium, "Dependency Injection in Go," https://medium.com/@matryer/golang-advent-calendar-day-sixteen-dependency-injection-in-go-5f9b0b3bbdb3, accessed 2025-11-01.

[^14]: Redis Documentation, "Clients," https://redis.io/docs/clients/, accessed 2025-11-01.

[^15]: GitHub, "dgraph-io/ristretto: A high performance memory-bound Go cache," https://github.com/dgraph-io/ristretto, accessed 2025-11-01.

[^16]: Go Documentation, "database/sql Tutorial," https://go.dev/doc/database/sql-tutorial, accessed 2025-11-01.

[^17]: Alex Edwards, "Organising Database Access," https://www.alexedwards.net/blog/organising-database-access, accessed 2025-11-01.

[^18]: GitHub, "kelseyhightower/envconfig: Managing configuration with environment variables," https://github.com/kelseyhightower/envconfig, accessed 2025-11-01.

[^19]: Martin Fowler, "Inversion of Control Containers and the Dependency Injection pattern," https://martinfowler.com/articles/injection.html, accessed 2025-11-01.

[^20]: Go Documentation, "sync.Once," https://pkg.go.dev/sync#Once, accessed 2025-11-01.

[^21]: Go Wiki, "CommonMistakes: Using goroutines on loop iterator variables," https://github.com/golang/go/wiki/CommonMistakes, accessed 2025-11-01.

[^22]: Go Wiki, "When To Use Init Functions," https://github.com/golang/go/wiki/CodeReviewComments#init, accessed 2025-11-01.

[^23]: Dave Cheney, "Don't use init()," https://dave.cheney.net/2014/10/17/functional-options-for-friendly-apis, accessed 2025-11-01.

[^24]: OWASP, "Configuration Management Best Practices," https://owasp.org/www-project-proactive-controls/v3/en/c8-protect-data-everywhere, accessed 2025-11-01.

[^25]: Kubernetes Documentation, "Configure Liveness, Readiness and Startup Probes," https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/, accessed 2025-11-01.

[^26]: Google Cloud, "Best practices for building containers: Health checks," https://cloud.google.com/architecture/best-practices-for-building-containers#signal_readiness_and_liveness, accessed 2025-11-01.



[^27]: Go Documentation, "Type Declarations," https://go.dev/ref/spec#Type_declarations, accessed 2025-11-02.

[^28]: Effective Go, "Type Switches," https://go.dev/doc/effective_go#type_switch, accessed 2025-11-02.

[^29]: go-playground/validator Documentation, https://pkg.go.dev/github.com/go-playground/validator/v10, accessed 2025-11-02.

[^30]: Gin Web Framework, "Model binding and validation," https://gin-gonic.com/docs/examples/binding-and-validation/, accessed 2025-11-02.

[^31]: Go Blog, "Working with Errors in Go 1.13," https://go.dev/blog/go1.13-errors, accessed 2025-11-02.

[^32]: Go Documentation, "errors Package," https://pkg.go.dev/errors, accessed 2025-11-02.

[^33]: OWASP, "Input Validation Cheat Sheet," https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html, accessed 2025-11-02.

[^34]: Go Documentation, "net/http Package," https://pkg.go.dev/net/http, accessed 2025-11-02.

---

**Next Steps:**

This report covers sections 1-4 (Configuration, Logging, Caching, Data Access). To complete the research:
- Section 5: External Service Integration (HTTP clients, circuit breakers, retry patterns)
- Section 6: Dependency Injection in Go (constructor injection, wire, manual DI)
- Section 7: Clean Architecture Layers (domain, application, infrastructure, presentation)
- Section 8: Testing Strategies (table-driven tests, testify, gomock, subtests)
- Section 9: Error Handling (errors.Is/As, wrapping, custom error types)
- Section 10: Project Structure (directory organization, package naming, internal packages)
- Appendix A: Example Project Structure (complete directory tree)
- Appendix B: Recommended Libraries (curated list with justifications)
