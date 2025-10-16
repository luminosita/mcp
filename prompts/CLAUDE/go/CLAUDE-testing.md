# Testing Patterns

Comprehensive testing strategies and patterns for Go applications.

## Testing Philosophy

- Test behavior, not implementation
- Write tests before or alongside code (TDD approach)
- Keep tests independent and isolated
- Use table-driven tests for multiple scenarios
- Mock external dependencies
- Aim for 80%+ coverage on business logic

## Table-Driven Tests

### Basic Table-Driven Test

```go
func TestValidateEmail(t *testing.T) {
    tests := []struct {
        name    string
        email   string
        wantErr bool
    }{
        {
            name:    "valid email",
            email:   "user@example.com",
            wantErr: false,
        },
        {
            name:    "missing @ symbol",
            email:   "userexample.com",
            wantErr: true,
        },
        {
            name:    "missing domain",
            email:   "user@",
            wantErr: true,
        },
        {
            name:    "empty email",
            email:   "",
            wantErr: true,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := ValidateEmail(tt.email)

            if tt.wantErr {
                assert.Error(t, err)
            } else {
                assert.NoError(t, err)
            }
        })
    }
}
```

### Advanced Table-Driven Test with testify

```go
import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func TestUser_Deactivate(t *testing.T) {
    tests := map[string]struct {
        setupUser   func() *User
        expectError bool
        errorMsg    string
        validate    func(t *testing.T, user *User)
    }{
        "active user can be deactivated": {
            setupUser: func() *User {
                return &User{Active: true}
            },
            expectError: false,
            validate: func(t *testing.T, user *User) {
                assert.False(t, user.IsActive())
            },
        },
        "inactive user cannot be deactivated": {
            setupUser: func() *User {
                return &User{Active: false}
            },
            expectError: true,
            errorMsg:    "user already inactive",
        },
        "deactivation sets timestamp": {
            setupUser: func() *User {
                return &User{Active: true}
            },
            expectError: false,
            validate: func(t *testing.T, user *User) {
                assert.False(t, user.IsActive())
                assert.NotZero(t, user.DeactivatedAt)
            },
        },
    }

    for name, tt := range tests {
        t.Run(name, func(t *testing.T) {
            user := tt.setupUser()
            err := user.Deactivate()

            if tt.expectError {
                require.Error(t, err)
                if tt.errorMsg != "" {
                    assert.Contains(t, err.Error(), tt.errorMsg)
                }
            } else {
                require.NoError(t, err)
                if tt.validate != nil {
                    tt.validate(t, user)
                }
            }
        })
    }
}
```

## Unit Testing with Mocks

### Using testify/mock

```go
// mocks/user_repository_mock.go
package mocks

import (
    "context"
    "github.com/stretchr/testify/mock"
    "myapp/internal/domain/entities"
)

type MockUserRepository struct {
    mock.Mock
}

func (m *MockUserRepository) Save(ctx context.Context, user *entities.User) error {
    args := m.Called(ctx, user)
    return args.Error(0)
}

func (m *MockUserRepository) FindByID(ctx context.Context, id entities.UserID) (*entities.User, error) {
    args := m.Called(ctx, id)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*entities.User), args.Error(1)
}

func (m *MockUserRepository) FindByEmail(ctx context.Context, email entities.EmailAddress) (*entities.User, error) {
    args := m.Called(ctx, email)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*entities.User), args.Error(1)
}
```

### Testing Use Cases with Mocks

```go
func TestCreateUserUseCase_Execute(t *testing.T) {
    tests := map[string]struct {
        command     CreateUserCommand
        setupMock   func(*mocks.MockUserRepository)
        expectError bool
        errorMsg    string
    }{
        "successful user creation": {
            command: CreateUserCommand{
                Email: "test@example.com",
                Name:  "Test User",
            },
            setupMock: func(m *mocks.MockUserRepository) {
                // Expect FindByEmail to return not found
                m.On("FindByEmail", mock.Anything, mock.Anything).
                    Return(nil, errors.New("not found"))

                // Expect Save to succeed
                m.On("Save", mock.Anything, mock.Anything).
                    Return(nil)
            },
            expectError: false,
        },
        "duplicate email error": {
            command: CreateUserCommand{
                Email: "existing@example.com",
                Name:  "Test User",
            },
            setupMock: func(m *mocks.MockUserRepository) {
                existingUser := &entities.User{
                    Email: "existing@example.com",
                }
                m.On("FindByEmail", mock.Anything, mock.Anything).
                    Return(existingUser, nil)
            },
            expectError: true,
            errorMsg:    "already exists",
        },
        "repository save error": {
            command: CreateUserCommand{
                Email: "test@example.com",
                Name:  "Test User",
            },
            setupMock: func(m *mocks.MockUserRepository) {
                m.On("FindByEmail", mock.Anything, mock.Anything).
                    Return(nil, errors.New("not found"))

                m.On("Save", mock.Anything, mock.Anything).
                    Return(errors.New("database error"))
            },
            expectError: true,
            errorMsg:    "failed to save",
        },
    }

    for name, tt := range tests {
        t.Run(name, func(t *testing.T) {
            // Setup
            mockRepo := new(mocks.MockUserRepository)
            tt.setupMock(mockRepo)

            useCase := NewCreateUserUseCase(mockRepo)

            // Execute
            user, err := useCase.Execute(context.Background(), tt.command)

            // Assert
            if tt.expectError {
                require.Error(t, err)
                if tt.errorMsg != "" {
                    assert.Contains(t, err.Error(), tt.errorMsg)
                }
                assert.Nil(t, user)
            } else {
                require.NoError(t, err)
                assert.NotNil(t, user)
                assert.Equal(t, tt.command.Email, user.Email().String())
                assert.Equal(t, tt.command.Name, user.Name())
            }

            // Verify all expectations were met
            mockRepo.AssertExpectations(t)
        })
    }
}
```

### Using gomock (Alternative)

```go
//go:generate mockgen -destination=mocks/user_repository_mock.go -package=mocks myapp/internal/domain/repositories UserRepository

func TestCreateUserUseCase_WithGomock(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockRepo := mocks.NewMockUserRepository(ctrl)
    useCase := NewCreateUserUseCase(mockRepo)

    email, _ := entities.NewEmailAddress("test@example.com")

    // Setup expectations
    mockRepo.EXPECT().
        FindByEmail(gomock.Any(), email).
        Return(nil, errors.New("not found"))

    mockRepo.EXPECT().
        Save(gomock.Any(), gomock.Any()).
        Return(nil)

    // Execute
    cmd := CreateUserCommand{
        Email: "test@example.com",
        Name:  "Test User",
    }

    user, err := useCase.Execute(context.Background(), cmd)

    // Assert
    require.NoError(t, err)
    assert.NotNil(t, user)
    assert.Equal(t, "test@example.com", user.Email().String())
}
```

## Integration Testing

### Database Integration Test

```go
//go:build integration

package postgres_test

import (
    "context"
    "database/sql"
    "testing"

    _ "github.com/lib/pq"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"

    "myapp/internal/domain/entities"
    "myapp/internal/infrastructure/persistence/postgres"
)

func setupTestDB(t *testing.T) *sql.DB {
    t.Helper()

    db, err := sql.Open("postgres",
        "postgres://test:test@localhost:5432/testdb?sslmode=disable")
    require.NoError(t, err)

    // Run migrations
    _, err = db.Exec(`
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(255) PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            active BOOLEAN NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    `)
    require.NoError(t, err)

    return db
}

func cleanupTestDB(t *testing.T, db *sql.DB) {
    t.Helper()

    _, err := db.Exec(`DROP TABLE IF EXISTS users`)
    require.NoError(t, err)

    db.Close()
}

func TestUserRepository_Integration(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test")
    }

    db := setupTestDB(t)
    defer cleanupTestDB(t, db)

    repo := postgres.NewUserRepository(db)
    ctx := context.Background()

    t.Run("save and find user", func(t *testing.T) {
        email, _ := entities.NewEmailAddress("test@example.com")
        user, _ := entities.NewUser(email, "Test User")

        // Save
        err := repo.Save(ctx, user)
        require.NoError(t, err)

        // Find by ID
        found, err := repo.FindByID(ctx, user.ID())
        require.NoError(t, err)
        assert.Equal(t, user.ID(), found.ID())
        assert.Equal(t, user.Email().String(), found.Email().String())
        assert.Equal(t, user.Name(), found.Name())
    })

    t.Run("find non-existent user", func(t *testing.T) {
        _, err := repo.FindByID(ctx, entities.UserID("non-existent"))
        require.Error(t, err)
        assert.Contains(t, err.Error(), "not found")
    })

    t.Run("duplicate email constraint", func(t *testing.T) {
        email, _ := entities.NewEmailAddress("duplicate@example.com")
        user1, _ := entities.NewUser(email, "User 1")

        err := repo.Save(ctx, user1)
        require.NoError(t, err)

        user2, _ := entities.NewUser(email, "User 2")
        err = repo.Save(ctx, user2)
        require.Error(t, err)
        assert.Contains(t, err.Error(), "duplicate")
    })
}
```

### HTTP Integration Test

```go
//go:build integration

func TestUserHandler_Integration(t *testing.T) {
    // Setup test server
    db := setupTestDB(t)
    defer cleanupTestDB(t, db)

    repo := postgres.NewUserRepository(db)
    useCase := usecases.NewCreateUserUseCase(repo)
    handler := httphandlers.NewUserHandler(useCase)

    router := http.NewServeMux()
    router.HandleFunc("/users", handler.CreateUser)

    server := httptest.NewServer(router)
    defer server.Close()

    t.Run("create user successfully", func(t *testing.T) {
        payload := `{"email":"test@example.com","name":"Test User"}`
        resp, err := http.Post(
            server.URL+"/users",
            "application/json",
            strings.NewReader(payload),
        )
        require.NoError(t, err)
        defer resp.Body.Close()

        assert.Equal(t, http.StatusCreated, resp.StatusCode)

        var user map[string]interface{}
        err = json.NewDecoder(resp.Body).Decode(&user)
        require.NoError(t, err)

        assert.NotEmpty(t, user["id"])
        assert.Equal(t, "test@example.com", user["email"])
        assert.Equal(t, "Test User", user["name"])
    })

    t.Run("validation error", func(t *testing.T) {
        payload := `{"email":"invalid-email","name":"Test"}`
        resp, err := http.Post(
            server.URL+"/users",
            "application/json",
            strings.NewReader(payload),
        )
        require.NoError(t, err)
        defer resp.Body.Close()

        assert.Equal(t, http.StatusBadRequest, resp.StatusCode)

        var errResp map[string]interface{}
        err = json.NewDecoder(resp.Body).Decode(&errResp)
        require.NoError(t, err)

        assert.Contains(t, errResp["error"], "invalid email")
    })
}
```

## Benchmark Tests

### Basic Benchmark

```go
func BenchmarkValidateEmail(b *testing.B) {
    email := "user@example.com"

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        ValidateEmail(email)
    }
}
```

### Benchmark with Setup

```go
func BenchmarkUserRepository_FindByID(b *testing.B) {
    db := setupTestDB(b)
    defer cleanupTestDB(b, db)

    repo := postgres.NewUserRepository(db)
    ctx := context.Background()

    // Seed data
    email, _ := entities.NewEmailAddress("bench@example.com")
    user, _ := entities.NewUser(email, "Bench User")
    repo.Save(ctx, user)

    b.ResetTimer()
    b.ReportAllocs()

    for i := 0; i < b.N; i++ {
        _, _ = repo.FindByID(ctx, user.ID())
    }
}
```

### Parallel Benchmark

```go
func BenchmarkUserService_Parallel(b *testing.B) {
    service := setupUserService()

    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            _, _ = service.GetUser(context.Background(), "user123")
        }
    })
}
```

## Test Helpers and Fixtures

### Test Helpers

```go
// testutil/helpers.go
package testutil

import (
    "testing"
    "myapp/internal/domain/entities"
)

func CreateTestUser(t *testing.T, email, name string) *entities.User {
    t.Helper()

    emailAddr, err := entities.NewEmailAddress(email)
    if err != nil {
        t.Fatalf("failed to create email: %v", err)
    }

    user, err := entities.NewUser(emailAddr, name)
    if err != nil {
        t.Fatalf("failed to create user: %v", err)
    }

    return user
}

func AssertUserEquals(t *testing.T, expected, actual *entities.User) {
    t.Helper()

    assert.Equal(t, expected.ID(), actual.ID())
    assert.Equal(t, expected.Email(), actual.Email())
    assert.Equal(t, expected.Name(), actual.Name())
    assert.Equal(t, expected.IsActive(), actual.IsActive())
}
```

### Test Fixtures

```go
// testdata/users.json
[
    {
        "id": "user_1",
        "email": "alice@example.com",
        "name": "Alice"
    },
    {
        "id": "user_2",
        "email": "bob@example.com",
        "name": "Bob"
    }
]

// testutil/fixtures.go
func LoadUserFixtures(t *testing.T) []*entities.User {
    t.Helper()

    data, err := os.ReadFile("testdata/users.json")
    if err != nil {
        t.Fatalf("failed to read fixtures: %v", err)
    }

    var fixtures []struct {
        ID    string `json:"id"`
        Email string `json:"email"`
        Name  string `json:"name"`
    }

    if err := json.Unmarshal(data, &fixtures); err != nil {
        t.Fatalf("failed to unmarshal fixtures: %v", err)
    }

    users := make([]*entities.User, len(fixtures))
    for i, f := range fixtures {
        users[i] = CreateTestUser(t, f.Email, f.Name)
    }

    return users
}
```

## Test Organization Best Practices

### ✅ DO
- Use table-driven tests for multiple scenarios
- Use `t.Run()` for subtests with descriptive names
- Mark test helpers with `t.Helper()`
- Use `require` for critical assertions (test stops on failure)
- Use `assert` for non-critical assertions (test continues)
- Keep setup and teardown in helpers
- Use build tags for integration tests: `//go:build integration`
- Run integration tests with: `go test -tags=integration`
- Test error cases as thoroughly as success cases
- Use meaningful test names that describe the scenario

### ❌ DON'T
- Don't test implementation details
- Don't create interdependent tests
- Don't skip cleanup (use `defer` or `t.Cleanup()`)
- Don't use global state in tests
- Don't hardcode values - use test data
- Don't write tests that depend on execution order
- Don't ignore race conditions - always run with `-race`
- Don't commit tests that require external services without proper mocking

## Running Tests

```bash
# Run all tests
go test ./...

# Run with verbose output
go test -v ./...

# Run with coverage
go test -cover ./...
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out

# Run with race detection
go test -race ./...

# Run only short tests (skip integration)
go test -short ./...

# Run integration tests
go test -tags=integration ./...

# Run specific test
go test -run TestCreateUser ./internal/application/usecases

# Run benchmarks
go test -bench=. ./...
go test -bench=BenchmarkUserRepository -benchmem ./...
```
