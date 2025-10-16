# Error Handling Patterns

Comprehensive error handling patterns and best practices for Go.

## Core Error Handling Principles

1. **Always check errors** - Never ignore error return values
2. **Handle errors once** - Don't log and return; choose one
3. **Add context when wrapping** - Use `fmt.Errorf` with `%w`
4. **Return errors, don't panic** - Reserve `panic` for truly exceptional cases
5. **Use custom error types** for domain-specific errors

## Basic Error Handling

### ✅ Correct: Check and Return

```go
func GetUser(id string) (*User, error) {
    user, err := repository.FindByID(id)
    if err != nil {
        return nil, fmt.Errorf("get user %s: %w", id, err)
    }
    return user, nil
}
```

### ✅ Correct: Early Return Pattern

```go
func ProcessUser(id string) error {
    user, err := GetUser(id)
    if err != nil {
        return fmt.Errorf("process user: %w", err)
    }

    if err := user.Validate(); err != nil {
        return fmt.Errorf("invalid user: %w", err)
    }

    if err := repository.Save(user); err != nil {
        return fmt.Errorf("save user: %w", err)
    }

    return nil
}
```

### ❌ Bad: Ignoring Errors

```go
// DON'T DO THIS
user, _ := GetUser("123")  // Silent failure

// DON'T DO THIS
GetUser("123")  // Result ignored
```

### ❌ Bad: Logging and Returning (Handle Once)

```go
// DON'T DO THIS
func GetUser(id string) (*User, error) {
    user, err := repository.FindByID(id)
    if err != nil {
        log.Printf("Error: %v", err)  // Don't log here
        return nil, err               // AND return
    }
    return user, nil
}
```

## Custom Error Types

### Domain-Specific Errors

```go
// NotFoundError for resource not found scenarios
type NotFoundError struct {
    Resource string
    ID       string
}

func (e *NotFoundError) Error() string {
    return fmt.Sprintf("%s not found: %s", e.Resource, e.ID)
}

// ValidationError for input validation failures
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation error on %s: %s", e.Field, e.Message)
}

// UnauthorizedError for auth failures
type UnauthorizedError struct {
    Action string
    Reason string
}

func (e *UnauthorizedError) Error() string {
    return fmt.Sprintf("unauthorized %s: %s", e.Action, e.Reason)
}
```

### Using Custom Errors

```go
func GetUser(id string) (*User, error) {
    user, err := repository.FindByID(id)
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, &NotFoundError{Resource: "user", ID: id}
        }
        return nil, fmt.Errorf("get user: %w", err)
    }
    return user, nil
}

func CreateUser(email string) (*User, error) {
    if !isValidEmail(email) {
        return nil, &ValidationError{
            Field:   "email",
            Message: "invalid email format",
        }
    }

    // Check duplicate
    existing, err := repository.FindByEmail(email)
    if err == nil && existing != nil {
        return nil, &ValidationError{
            Field:   "email",
            Message: "email already exists",
        }
    }

    user := &User{Email: email}
    if err := repository.Save(user); err != nil {
        return nil, fmt.Errorf("save user: %w", err)
    }

    return user, nil
}
```

## Error Inspection with errors.Is and errors.As

### Using errors.Is for Sentinel Errors

```go
// Define sentinel errors
var (
    ErrUserNotFound   = errors.New("user not found")
    ErrInvalidEmail   = errors.New("invalid email")
    ErrDuplicateEmail = errors.New("email already exists")
    ErrUnauthorized   = errors.New("unauthorized")
)

// Check with errors.Is
func HandleError(err error) {
    if errors.Is(err, ErrUserNotFound) {
        // Handle not found
        log.Printf("Resource not found: %v", err)
        return
    }

    if errors.Is(err, context.DeadlineExceeded) {
        // Handle timeout
        log.Printf("Request timeout: %v", err)
        return
    }

    // Handle other errors
    log.Printf("Unexpected error: %v", err)
}
```

### Using errors.As for Type Assertion

```go
func HandleHTTPError(err error) int {
    var notFound *NotFoundError
    if errors.As(err, &notFound) {
        return http.StatusNotFound
    }

    var validation *ValidationError
    if errors.As(err, &validation) {
        return http.StatusBadRequest
    }

    var unauthorized *UnauthorizedError
    if errors.As(err, &unauthorized) {
        return http.StatusUnauthorized
    }

    return http.StatusInternalServerError
}
```

### Advanced Error Inspection

```go
func ProcessWithRetry(ctx context.Context) error {
    err := doOperation(ctx)
    if err != nil {
        // Check for specific error types
        var netErr *net.OpError
        if errors.As(err, &netErr) && netErr.Temporary() {
            // Retry on temporary network errors
            return retry(ctx, doOperation)
        }

        // Check for context errors
        if errors.Is(err, context.DeadlineExceeded) {
            return fmt.Errorf("operation timeout: %w", err)
        }

        if errors.Is(err, context.Canceled) {
            return fmt.Errorf("operation canceled: %w", err)
        }

        return fmt.Errorf("operation failed: %w", err)
    }

    return nil
}
```

## Error Wrapping and Unwrapping

### Proper Error Wrapping

```go
func GetUserProfile(userID string) (*Profile, error) {
    user, err := GetUser(userID)
    if err != nil {
        // Wrap with %w to preserve original error
        return nil, fmt.Errorf("get user profile for %s: %w", userID, err)
    }

    profile, err := repository.GetProfile(user.ID)
    if err != nil {
        return nil, fmt.Errorf("fetch profile: %w", err)
    }

    return profile, nil
}

// Error chain: "get user profile for 123: get user: user not found: 123"
```

### Multiple Error Handling (Go 1.20+)

```go
func ProcessBatch(items []Item) error {
    var errs []error

    for _, item := range items {
        if err := processItem(item); err != nil {
            errs = append(errs, fmt.Errorf("process item %s: %w", item.ID, err))
        }
    }

    if len(errs) > 0 {
        // Join multiple errors (Go 1.20+)
        return errors.Join(errs...)
    }

    return nil
}
```

## HTTP Error Handling

### Error Response Mapper

```go
type ErrorResponse struct {
    Error   string `json:"error"`
    Code    string `json:"code,omitempty"`
    Details map[string]string `json:"details,omitempty"`
}

func HandleHTTPError(w http.ResponseWriter, err error) {
    var (
        status   int
        code     string
        message  string
        details  map[string]string
    )

    // Type assertion for custom errors
    var notFound *NotFoundError
    if errors.As(err, &notFound) {
        status = http.StatusNotFound
        code = "NOT_FOUND"
        message = notFound.Error()
    }

    var validation *ValidationError
    if errors.As(err, &validation) {
        status = http.StatusBadRequest
        code = "VALIDATION_ERROR"
        message = "Validation failed"
        details = map[string]string{
            validation.Field: validation.Message,
        }
    }

    var unauthorized *UnauthorizedError
    if errors.As(err, &unauthorized) {
        status = http.StatusUnauthorized
        code = "UNAUTHORIZED"
        message = unauthorized.Error()
    }

    // Default to 500
    if status == 0 {
        status = http.StatusInternalServerError
        code = "INTERNAL_ERROR"
        message = "Internal server error"
        // Log the actual error internally, don't expose it
        log.Printf("Internal error: %v", err)
    }

    response := ErrorResponse{
        Error:   message,
        Code:    code,
        Details: details,
    }

    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(response)
}
```

### HTTP Handler with Error Handling

```go
func (h *UserHandler) CreateUser(w http.ResponseWriter, r *http.Request) {
    var req CreateUserRequest

    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        HandleHTTPError(w, &ValidationError{
            Field:   "body",
            Message: "invalid JSON",
        })
        return
    }

    user, err := h.useCase.Execute(r.Context(), req)
    if err != nil {
        HandleHTTPError(w, err)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusCreated)
    json.NewEncoder(w).Encode(user)
}
```

## Error Handling with Context

### Timeout and Cancellation

```go
func ProcessWithTimeout(ctx context.Context, id string) error {
    ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
    defer cancel()

    resultCh := make(chan error, 1)

    go func() {
        user, err := GetUser(id)
        if err != nil {
            resultCh <- fmt.Errorf("get user: %w", err)
            return
        }

        if err := ProcessUser(user); err != nil {
            resultCh <- fmt.Errorf("process user: %w", err)
            return
        }

        resultCh <- nil
    }()

    select {
    case err := <-resultCh:
        return err
    case <-ctx.Done():
        return fmt.Errorf("process timeout: %w", ctx.Err())
    }
}
```

### Cancellation Handling

```go
func LongRunningOperation(ctx context.Context) error {
    for i := 0; i < 1000; i++ {
        // Check for cancellation
        select {
        case <-ctx.Done():
            return fmt.Errorf("operation canceled at step %d: %w", i, ctx.Err())
        default:
        }

        // Do work
        if err := doStep(i); err != nil {
            return fmt.Errorf("step %d failed: %w", i, err)
        }
    }

    return nil
}
```

## Panic and Recover

### When to Use Panic

```go
// ✅ Acceptable: Panic in init or startup for configuration errors
func init() {
    if err := loadConfig(); err != nil {
        panic(fmt.Sprintf("failed to load config: %v", err))
    }
}

// ✅ Acceptable: Panic for programmer errors (should never happen)
func MustParse(s string) int {
    i, err := strconv.Atoi(s)
    if err != nil {
        panic(fmt.Sprintf("MustParse: invalid integer: %s", s))
    }
    return i
}

// ❌ Don't panic in library code or normal operations
func GetUser(id string) *User {
    user, err := repository.FindByID(id)
    if err != nil {
        panic(err)  // DON'T DO THIS
    }
    return user
}
```

### Recover from Panics

```go
// HTTP middleware to recover from panics
func RecoverMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if err := recover(); err != nil {
                log.Printf("PANIC: %v\n%s", err, debug.Stack())

                w.Header().Set("Content-Type", "application/json")
                w.WriteHeader(http.StatusInternalServerError)
                json.NewEncoder(w).Encode(map[string]string{
                    "error": "Internal server error",
                })
            }
        }()

        next.ServeHTTP(w, r)
    })
}
```

## Error Logging Best Practices

### Structured Logging with Errors

```go
import "log/slog"

func ProcessOrder(ctx context.Context, orderID string) error {
    order, err := GetOrder(orderID)
    if err != nil {
        slog.ErrorContext(ctx, "failed to get order",
            "order_id", orderID,
            "error", err,
        )
        return fmt.Errorf("get order: %w", err)
    }

    if err := ValidateOrder(order); err != nil {
        slog.WarnContext(ctx, "order validation failed",
            "order_id", orderID,
            "error", err,
        )
        return fmt.Errorf("validate order: %w", err)
    }

    slog.InfoContext(ctx, "order processed successfully",
        "order_id", orderID,
    )

    return nil
}
```

### Error Metrics and Monitoring

```go
type ErrorCounter struct {
    mu     sync.Mutex
    counts map[string]int64
}

func (ec *ErrorCounter) Record(errType string) {
    ec.mu.Lock()
    defer ec.mu.Unlock()
    ec.counts[errType]++
}

func HandleError(err error) {
    var notFound *NotFoundError
    if errors.As(err, &notFound) {
        errorCounter.Record("not_found")
        return
    }

    var validation *ValidationError
    if errors.As(err, &validation) {
        errorCounter.Record("validation")
        return
    }

    errorCounter.Record("internal")
}
```

## Best Practices Summary

### ✅ DO
- Always check errors explicitly
- Wrap errors with context using `%w`
- Use custom error types for domain errors
- Use `errors.Is()` and `errors.As()` for inspection
- Return errors from functions, handle at appropriate level
- Log errors at the boundary (HTTP handlers, main)
- Use structured logging with error context
- Handle context cancellation and timeouts

### ❌ DON'T
- Don't ignore errors with `_`
- Don't log and return the same error (handle once)
- Don't panic in library code or normal operations
- Don't expose internal error details to users
- Don't use string matching for error types
- Don't create error variables in loops
- Don't forget to wrap errors with context
