# CLAUDE-validation.md - Input Validation & Data Models

**← [Back to Go Development Guide](./CLAUDE-core.md)**

## Overview

This document covers input validation patterns, request/response data models, sanitization strategies, and security best practices for validating user input in Go applications.

---

## Core Validation Principles

1. **Validate at boundaries** - All external input must be validated at entry points (HTTP handlers, CLI, gRPC)
2. **Fail fast** - Return validation errors immediately before processing
3. **Use struct tags** - Leverage `validate` tags for declarative validation
4. **Whitelist approach** - Accept only known-good input, reject everything else
5. **Type safety** - Use strong typing to enforce constraints at compile time

---

## Struct Validation with validator

### Basic Validation Setup

```go
import (
    "github.com/go-playground/validator/v10"
)

// Global validator instance (reusable across application)
var validate = validator.New()

type CreateUserRequest struct {
    Email    string `json:"email" validate:"required,email"`
    Name     string `json:"name" validate:"required,min=1,max=100"`
    Password string `json:"password" validate:"required,min=8,max=72"`
    Age      int    `json:"age" validate:"required,gte=18,lte=120"`
    Website  string `json:"website" validate:"omitempty,url"`
}

func ValidateStruct(s interface{}) error {
    return validate.Struct(s)
}
```

### Common Validation Tags

```go
type ValidationExamples struct {
    // Required fields
    RequiredField string `validate:"required"`

    // String constraints
    MinMaxString  string `validate:"min=3,max=50"`
    Email         string `validate:"email"`
    URL           string `validate:"url"`
    UUID          string `validate:"uuid"`
    AlphaNumeric  string `validate:"alphanum"`

    // Numeric constraints
    PositiveInt   int     `validate:"gt=0"`
    RangeInt      int     `validate:"gte=18,lte=120"`
    PositiveFloat float64 `validate:"gt=0.0"`

    // Optional fields with validation
    OptionalEmail string `validate:"omitempty,email"`

    // Custom validation
    Status string `validate:"oneof=pending approved rejected"`

    // Nested struct validation
    Address Address `validate:"required"`

    // Slice validation
    Tags []string `validate:"required,dive,min=1,max=50"`
}

type Address struct {
    Street  string `validate:"required,min=5,max=200"`
    City    string `validate:"required,min=2,max=100"`
    ZipCode string `validate:"required,len=5|len=10"` // 5 or 10 digits
}
```

### HTTP Request Validation

```go
func (h *UserHandler) CreateUser(w http.ResponseWriter, r *http.Request) {
    var req CreateUserRequest

    // Step 1: Decode JSON
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        h.respondError(w, "invalid JSON format", http.StatusBadRequest)
        return
    }

    // Step 2: Validate struct
    if err := validate.Struct(req); err != nil {
        h.respondValidationError(w, err)
        return
    }

    // Step 3: Process validated request
    user, err := h.userService.CreateUser(r.Context(), req)
    if err != nil {
        h.respondError(w, err.Error(), http.StatusInternalServerError)
        return
    }

    h.respondJSON(w, user, http.StatusCreated)
}

// Format validation errors for API response
func (h *UserHandler) respondValidationError(w http.ResponseWriter, err error) {
    validationErrors, ok := err.(validator.ValidationErrors)
    if !ok {
        h.respondError(w, "validation failed", http.StatusBadRequest)
        return
    }

    errors := make(map[string]string)
    for _, fieldErr := range validationErrors {
        errors[fieldErr.Field()] = formatValidationError(fieldErr)
    }

    h.respondJSON(w, map[string]interface{}{
        "error":   "validation failed",
        "details": errors,
    }, http.StatusBadRequest)
}

func formatValidationError(err validator.FieldError) string {
    switch err.Tag() {
    case "required":
        return "this field is required"
    case "email":
        return "must be a valid email address"
    case "min":
        return fmt.Sprintf("must be at least %s characters", err.Param())
    case "max":
        return fmt.Sprintf("must be at most %s characters", err.Param())
    case "gte":
        return fmt.Sprintf("must be greater than or equal to %s", err.Param())
    case "lte":
        return fmt.Sprintf("must be less than or equal to %s", err.Param())
    default:
        return fmt.Sprintf("failed on %s validation", err.Tag())
    }
}
```

---

## Custom Validation Functions

### Register Custom Validators

```go
import "regexp"

func init() {
    validate = validator.New()

    // Register custom username validator
    validate.RegisterValidation("username", validateUsername)

    // Register custom phone number validator
    validate.RegisterValidation("phone", validatePhone)
}

// Custom username validation (alphanumeric + underscore, 3-20 chars)
func validateUsername(fl validator.FieldLevel) bool {
    username := fl.Field().String()
    match, _ := regexp.MatchString(`^[a-zA-Z0-9_]{3,20}$`, username)
    return match
}

// Custom phone number validation (E.164 format)
func validatePhone(fl validator.FieldLevel) bool {
    phone := fl.Field().String()
    match, _ := regexp.MatchString(`^\+[1-9]\d{1,14}$`, phone)
    return match
}

// Usage in struct
type UserProfile struct {
    Username string `validate:"required,username"`
    Phone    string `validate:"omitempty,phone"`
}
```

### Cross-Field Validation

```go
type PasswordChange struct {
    Password        string `validate:"required,min=8,max=72"`
    ConfirmPassword string `validate:"required,eqfield=Password"`
}

type DateRange struct {
    StartDate time.Time `validate:"required"`
    EndDate   time.Time `validate:"required,gtfield=StartDate"`
}
```

---

## Input Sanitization

### HTML/XSS Prevention

```go
import (
    "html"
    "strings"
)

// SanitizeString removes dangerous characters and trims whitespace
func SanitizeString(input string) string {
    // Trim whitespace
    sanitized := strings.TrimSpace(input)

    // Escape HTML entities
    sanitized = html.EscapeString(sanitized)

    return sanitized
}

// StripTags removes all HTML tags from input
func StripTags(input string) string {
    // Simple tag removal (use bluemonday for production)
    re := regexp.MustCompile(`<[^>]*>`)
    return re.ReplaceAllString(input, "")
}

// Usage in handler
func (h *PostHandler) CreatePost(w http.ResponseWriter, r *http.Request) {
    var req CreatePostRequest

    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "invalid JSON", http.StatusBadRequest)
        return
    }

    // Sanitize user input
    req.Title = SanitizeString(req.Title)
    req.Content = StripTags(req.Content) // or use bluemonday for rich text

    // Validate after sanitization
    if err := validate.Struct(req); err != nil {
        h.respondValidationError(w, err)
        return
    }

    // Process sanitized and validated request
    // ...
}
```

### Using bluemonday for Rich Text

```go
import "github.com/microcosm-cc/bluemonday"

var htmlPolicy = bluemonday.UGCPolicy()

// SanitizeHTML allows safe HTML tags, removes dangerous ones
func SanitizeHTML(input string) string {
    return htmlPolicy.Sanitize(input)
}

// Strict sanitization (plain text only)
func SanitizeToPlainText(input string) string {
    return bluemonday.StrictPolicy().Sanitize(input)
}
```

---

## SQL Injection Prevention

### Parameterized Queries (database/sql)

```go
// ✅ CORRECT: Use parameterized queries
func (r *UserRepository) FindByEmail(ctx context.Context, email string) (*User, error) {
    query := `SELECT id, email, name FROM users WHERE email = $1`

    var user User
    err := r.db.QueryRowContext(ctx, query, email).Scan(
        &user.ID,
        &user.Email,
        &user.Name,
    )

    if err == sql.ErrNoRows {
        return nil, fmt.Errorf("user not found")
    }
    if err != nil {
        return nil, fmt.Errorf("query error: %w", err)
    }

    return &user, nil
}

// ❌ WRONG: Never concatenate user input into SQL
func (r *UserRepository) FindByEmailDangerous(email string) (*User, error) {
    // DON'T DO THIS - vulnerable to SQL injection
    query := fmt.Sprintf("SELECT * FROM users WHERE email = '%s'", email)
    // Attacker could use: ' OR '1'='1
    // This would bypass authentication!

    // ...
}
```

### Parameterized Queries (GORM)

```go
import "gorm.io/gorm"

// ✅ CORRECT: GORM automatically uses parameterized queries
func (r *UserRepository) FindByEmail(ctx context.Context, email string) (*User, error) {
    var user User

    // GORM uses placeholders automatically
    err := r.db.WithContext(ctx).
        Where("email = ?", email).
        First(&user).Error

    if err == gorm.ErrRecordNotFound {
        return nil, fmt.Errorf("user not found")
    }
    if err != nil {
        return nil, fmt.Errorf("query error: %w", err)
    }

    return &user, nil
}

// ❌ WRONG: Don't use raw SQL with string concatenation
func (r *UserRepository) DangerousQuery(email string) (*User, error) {
    var user User

    // DON'T DO THIS
    err := r.db.Raw(fmt.Sprintf("SELECT * FROM users WHERE email = '%s'", email)).
        Scan(&user).Error

    // ...
}
```

---

## Path Traversal Prevention

### Safe File Path Handling

```go
import (
    "path/filepath"
    "strings"
    "os"
)

// SafeJoinPath prevents directory traversal attacks
func SafeJoinPath(baseDir, userPath string) (string, error) {
    // Clean the user path (removes .., ., etc.)
    cleanPath := filepath.Clean(userPath)

    // Join with base directory
    fullPath := filepath.Join(baseDir, cleanPath)

    // Ensure the final path is still within baseDir
    cleanBase := filepath.Clean(baseDir) + string(os.PathSeparator)
    if !strings.HasPrefix(fullPath, cleanBase) {
        return "", errors.New("invalid file path: attempted directory traversal")
    }

    return fullPath, nil
}

// SafeFileRead reads a file within a safe directory
func SafeFileRead(baseDir, userPath string) ([]byte, error) {
    safePath, err := SafeJoinPath(baseDir, userPath)
    if err != nil {
        return nil, err
    }

    return os.ReadFile(safePath)
}

// Example usage in HTTP handler
func (h *FileHandler) DownloadFile(w http.ResponseWriter, r *http.Request) {
    filename := r.URL.Query().Get("file")

    // Validate filename is not empty
    if filename == "" {
        http.Error(w, "filename required", http.StatusBadRequest)
        return
    }

    // Safe file read (prevents ../../../etc/passwd)
    data, err := SafeFileRead("/var/app/files", filename)
    if err != nil {
        http.Error(w, "file not found", http.StatusNotFound)
        return
    }

    // Set appropriate content type
    http.ServeContent(w, r, filename, time.Now(), bytes.NewReader(data))
}
```

---

## Request/Response Data Models

### Domain vs DTO Pattern

```go
// Domain entity (internal/domain/entities/user.go)
type User struct {
    ID             string
    Email          string
    HashedPassword string // Never expose in API
    Name           string
    CreatedAt      time.Time
    UpdatedAt      time.Time
}

// Request DTO (internal/interfaces/http/dto/user_dto.go)
type CreateUserRequest struct {
    Email    string `json:"email" validate:"required,email"`
    Name     string `json:"name" validate:"required,min=1,max=100"`
    Password string `json:"password" validate:"required,min=8,max=72"`
}

// Response DTO (never expose sensitive fields)
type UserResponse struct {
    ID        string    `json:"id"`
    Email     string    `json:"email"`
    Name      string    `json:"name"`
    CreatedAt time.Time `json:"created_at"`
}

// Conversion functions
func ToUserResponse(user *User) UserResponse {
    return UserResponse{
        ID:        user.ID,
        Email:     user.Email,
        Name:      user.Name,
        CreatedAt: user.CreatedAt,
    }
}
```

### Pagination Request/Response

```go
type PaginationRequest struct {
    Page     int `json:"page" validate:"omitempty,gte=1"`
    PageSize int `json:"page_size" validate:"omitempty,gte=1,lte=100"`
}

func (p *PaginationRequest) SetDefaults() {
    if p.Page == 0 {
        p.Page = 1
    }
    if p.PageSize == 0 {
        p.PageSize = 20
    }
    if p.PageSize > 100 {
        p.PageSize = 100 // Enforce max
    }
}

type PaginatedResponse struct {
    Data       interface{} `json:"data"`
    Page       int         `json:"page"`
    PageSize   int         `json:"page_size"`
    TotalItems int64       `json:"total_items"`
    TotalPages int         `json:"total_pages"`
}
```

---

## Best Practices

### ✅ DO

- Validate all external input at boundaries (HTTP, CLI, gRPC)
- Use struct tags for declarative validation
- Sanitize user input before storage
- Use parameterized queries for database operations
- Validate file paths to prevent directory traversal
- Return clear validation error messages
- Use DTOs to separate domain models from API contracts
- Set sensible defaults for optional fields
- Enforce maximum limits on pagination, file uploads, etc.

### ❌ DON'T

- Trust any user input without validation
- Concatenate user input into SQL queries
- Expose internal domain entities directly in APIs
- Return stack traces or internal errors to users
- Allow unlimited pagination page sizes
- Skip sanitization for "trusted" input
- Use reflection-based validation in hot paths (pre-compile with validator)

---

## Pre-commit Checklist

- [ ] All request structs have validation tags
- [ ] Custom validation functions registered in `init()`
- [ ] User input sanitized before storage
- [ ] Database queries use parameterized statements (no string concatenation)
- [ ] File paths validated to prevent directory traversal
- [ ] DTOs separate domain models from API responses
- [ ] Validation errors formatted user-friendly
- [ ] No sensitive data exposed in responses (passwords, tokens, internal IDs)

---

## Related Files

- **[CLAUDE-security.md](./CLAUDE-security.md)** - Authentication, authorization, encryption, CSRF protection
- **[CLAUDE-api.md](./CLAUDE-api.md)** - REST API design, error responses, versioning
- **[CLAUDE-database.md](./CLAUDE-database.md)** - Repository pattern, parameterized queries, migrations
- **[CLAUDE-testing.md](./CLAUDE-testing.md)** - Testing validation logic and error cases
- **[CLAUDE-error-handling.md](./CLAUDE-error-handling.md)** - Error wrapping and HTTP error mapping

---

## External References

- **go-playground/validator**: https://github.com/go-playground/validator
- **bluemonday (HTML sanitization)**: https://github.com/microcosm-cc/bluemonday
- **OWASP Input Validation**: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html
- **SQL Injection Prevention**: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
