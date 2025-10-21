# Security Patterns

Security-critical code examples and best practices for Go applications: authentication, authorization, encryption, CSRF protection, rate limiting, and secure file handling.

**← [Back to Go Development Guide]mcp://resources/patterns/go/patterns-core**

> **Note:** Input validation patterns (struct validation, SQL injection prevention, path traversal protection, sanitization) have been moved to **[patterns-validation]mcp://resources/patterns/go/patterns-validation**. This file focuses on authentication, authorization, and security mechanisms.

---

## Overview

This document covers:
- Authentication (password hashing, JWT, OAuth2, PKCE)
- Authorization (RBAC, permission systems)
- Cryptographic operations (AES-GCM encryption, secure random generation)
- HTTPS/TLS configuration
- Security headers middleware
- CSRF protection
- Rate limiting
- Secure file upload/download patterns

---

## Authentication and Authorization

### Password Hashing (bcrypt)

```go
import "golang.org/x/crypto/bcrypt"

const bcryptCost = 12

// HashPassword generates a bcrypt hash of the password
func HashPassword(password string) (string, error) {
    if len(password) > 72 {
        return "", errors.New("password too long (max 72 bytes)")
    }

    hash, err := bcrypt.GenerateFromPassword([]byte(password), bcryptCost)
    if err != nil {
        return "", fmt.Errorf("failed to hash password: %w", err)
    }

    return string(hash), nil
}

// VerifyPassword checks if the password matches the hash
func VerifyPassword(hashedPassword, password string) error {
    err := bcrypt.CompareHashAndPassword(
        []byte(hashedPassword),
        []byte(password),
    )

    if err != nil {
        return errors.New("invalid password")
    }

    return nil
}

// Usage in registration
func (uc *RegisterUserUseCase) Execute(ctx context.Context, cmd RegisterUserCommand) error {
    // Hash password
    hashedPassword, err := HashPassword(cmd.Password)
    if err != nil {
        return fmt.Errorf("password hashing failed: %w", err)
    }

    user := &User{
        Email:          cmd.Email,
        HashedPassword: hashedPassword,
    }

    return uc.userRepo.Save(ctx, user)
}

// Usage in login
func (uc *LoginUserUseCase) Execute(ctx context.Context, email, password string) (*User, error) {
    user, err := uc.userRepo.FindByEmail(ctx, email)
    if err != nil {
        return nil, errors.New("invalid credentials")
    }

    if err := VerifyPassword(user.HashedPassword, password); err != nil {
        return nil, errors.New("invalid credentials")
    }

    return user, nil
}
```

### JWT Token Generation and Validation

```go
import (
    "github.com/golang-jwt/jwt/v5"
    "time"
)

type Claims struct {
    UserID string   `json:"user_id"`
    Email  string   `json:"email"`
    Roles  []string `json:"roles"`
    jwt.RegisteredClaims
}

var jwtSecret = []byte(os.Getenv("JWT_SECRET")) // Load from env

// GenerateToken creates a JWT token for the user
func GenerateToken(userID, email string, roles []string) (string, error) {
    claims := Claims{
        UserID: userID,
        Email:  email,
        Roles:  roles,
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(24 * time.Hour)),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
            Issuer:    "myapp",
        },
    }

    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString(jwtSecret)
}

// ValidateToken validates and parses a JWT token
func ValidateToken(tokenString string) (*Claims, error) {
    token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
        // Validate signing method
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
        }
        return jwtSecret, nil
    })

    if err != nil {
        return nil, fmt.Errorf("invalid token: %w", err)
    }

    claims, ok := token.Claims.(*Claims)
    if !ok || !token.Valid {
        return nil, errors.New("invalid token claims")
    }

    return claims, nil
}

// Middleware for JWT authentication
func AuthMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        authHeader := r.Header.Get("Authorization")
        if authHeader == "" {
            http.Error(w, "missing authorization header", http.StatusUnauthorized)
            return
        }

        // Extract token from "Bearer <token>"
        tokenString := strings.TrimPrefix(authHeader, "Bearer ")
        if tokenString == authHeader {
            http.Error(w, "invalid authorization format", http.StatusUnauthorized)
            return
        }

        claims, err := ValidateToken(tokenString)
        if err != nil {
            http.Error(w, "invalid token", http.StatusUnauthorized)
            return
        }

        // Add claims to context
        ctx := context.WithValue(r.Context(), "user_id", claims.UserID)
        ctx = context.WithValue(ctx, "roles", claims.Roles)

        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

### Role-Based Access Control (RBAC)

```go
type Role string

const (
    RoleAdmin  Role = "admin"
    RoleUser   Role = "user"
    RoleGuest  Role = "guest"
)

// RequireRole middleware checks if user has required role
func RequireRole(requiredRole Role) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            roles, ok := r.Context().Value("roles").([]string)
            if !ok {
                http.Error(w, "unauthorized", http.StatusUnauthorized)
                return
            }

            hasRole := false
            for _, role := range roles {
                if Role(role) == requiredRole {
                    hasRole = true
                    break
                }
            }

            if !hasRole {
                http.Error(w, "forbidden", http.StatusForbidden)
                return
            }

            next.ServeHTTP(w, r)
        })
    }
}

// Usage
adminOnlyHandler := RequireRole(RoleAdmin)(http.HandlerFunc(adminHandler))
```

### OAuth2/OIDC Integration

```go
import (
    "context"
    "encoding/json"
    "golang.org/x/oauth2"
    "golang.org/x/oauth2/google"
    "github.com/coreos/go-oidc/v3/oidc"
)

type OAuthConfig struct {
    ClientID     string
    ClientSecret string
    RedirectURL  string
    Scopes       []string
}

type OAuthProvider struct {
    config   *oauth2.Config
    verifier *oidc.IDTokenVerifier
}

func NewGoogleOAuthProvider(ctx context.Context, cfg OAuthConfig) (*OAuthProvider, error) {
    provider, err := oidc.NewProvider(ctx, "https://accounts.google.com")
    if err != nil {
        return nil, fmt.Errorf("failed to create OIDC provider: %w", err)
    }

    oauth2Config := &oauth2.Config{
        ClientID:     cfg.ClientID,
        ClientSecret: cfg.ClientSecret,
        RedirectURL:  cfg.RedirectURL,
        Endpoint:     google.Endpoint,
        Scopes:       append(cfg.Scopes, oidc.ScopeOpenID, "profile", "email"),
    }

    verifier := provider.Verifier(&oidc.Config{
        ClientID: cfg.ClientID,
    })

    return &OAuthProvider{
        config:   oauth2Config,
        verifier: verifier,
    }, nil
}

func (p *OAuthProvider) GetAuthURL(state string) string {
    return p.config.AuthCodeURL(state, oauth2.AccessTypeOffline)
}

type OAuthUserInfo struct {
    Email         string `json:"email"`
    EmailVerified bool   `json:"email_verified"`
    Name          string `json:"name"`
    Picture       string `json:"picture"`
    Sub           string `json:"sub"`
}

func (p *OAuthProvider) HandleCallback(ctx context.Context, code string) (*OAuthUserInfo, error) {
    oauth2Token, err := p.config.Exchange(ctx, code)
    if err != nil {
        return nil, fmt.Errorf("failed to exchange token: %w", err)
    }

    rawIDToken, ok := oauth2Token.Extra("id_token").(string)
    if !ok {
        return nil, errors.New("no id_token in response")
    }

    idToken, err := p.verifier.Verify(ctx, rawIDToken)
    if err != nil {
        return nil, fmt.Errorf("failed to verify ID token: %w", err)
    }

    var userInfo OAuthUserInfo
    if err := idToken.Claims(&userInfo); err != nil {
        return nil, fmt.Errorf("failed to parse claims: %w", err)
    }

    return &userInfo, nil
}

type OAuthHandler struct {
    provider *OAuthProvider
    userRepo UserRepository
}

func (h *OAuthHandler) Login(w http.ResponseWriter, r *http.Request) {
    state, err := GenerateSecureToken(32)
    if err != nil {
        http.Error(w, "internal error", http.StatusInternalServerError)
        return
    }

    http.SetCookie(w, &http.Cookie{
        Name:     "oauth_state",
        Value:    state,
        MaxAge:   300,
        HttpOnly: true,
        Secure:   true,
        SameSite: http.SameSiteLaxMode,
    })

    authURL := h.provider.GetAuthURL(state)
    http.Redirect(w, r, authURL, http.StatusTemporaryRedirect)
}

func (h *OAuthHandler) Callback(w http.ResponseWriter, r *http.Request) {
    stateCookie, err := r.Cookie("oauth_state")
    if err != nil {
        http.Error(w, "missing state cookie", http.StatusBadRequest)
        return
    }

    if r.URL.Query().Get("state") != stateCookie.Value {
        http.Error(w, "state mismatch", http.StatusBadRequest)
        return
    }

    code := r.URL.Query().Get("code")
    if code == "" {
        http.Error(w, "missing code", http.StatusBadRequest)
        return
    }

    userInfo, err := h.provider.HandleCallback(r.Context(), code)
    if err != nil {
        slog.Error("OAuth callback failed", "error", err)
        http.Error(w, "authentication failed", http.StatusInternalServerError)
        return
    }

    if !userInfo.EmailVerified {
        http.Error(w, "email not verified", http.StatusForbidden)
        return
    }

    user, err := h.userRepo.FindOrCreateByOAuth(r.Context(), userInfo.Sub, userInfo.Email, userInfo.Name)
    if err != nil {
        slog.Error("failed to find/create user", "error", err)
        http.Error(w, "internal error", http.StatusInternalServerError)
        return
    }

    token, err := GenerateToken(user.ID, user.Email, user.Roles)
    if err != nil {
        http.Error(w, "internal error", http.StatusInternalServerError)
        return
    }

    http.SetCookie(w, &http.Cookie{
        Name:     "oauth_state",
        Value:    "",
        MaxAge:   -1,
        HttpOnly: true,
    })

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]string{
        "token": token,
    })
}
```

### OAuth2 with PKCE (for mobile/SPA)

```go
import (
    "crypto/sha256"
    "encoding/base64"
)

type PKCEChallenge struct {
    Verifier  string
    Challenge string
}

func GeneratePKCEChallenge() (*PKCEChallenge, error) {
    verifierBytes := make([]byte, 32)
    if _, err := rand.Read(verifierBytes); err != nil {
        return nil, fmt.Errorf("failed to generate verifier: %w", err)
    }

    verifier := base64.RawURLEncoding.EncodeToString(verifierBytes)

    h := sha256.New()
    h.Write([]byte(verifier))
    challenge := base64.RawURLEncoding.EncodeToString(h.Sum(nil))

    return &PKCEChallenge{
        Verifier:  verifier,
        Challenge: challenge,
    }, nil
}

func (p *OAuthProvider) GetAuthURLWithPKCE(state string, challenge string) string {
    return p.config.AuthCodeURL(state,
        oauth2.AccessTypeOffline,
        oauth2.SetAuthURLParam("code_challenge", challenge),
        oauth2.SetAuthURLParam("code_challenge_method", "S256"),
    )
}

func (p *OAuthProvider) ExchangeWithPKCE(ctx context.Context, code string, verifier string) (*oauth2.Token, error) {
    return p.config.Exchange(ctx, code,
        oauth2.SetAuthURLParam("code_verifier", verifier),
    )
}
```

### Token Refresh Pattern

```go
type TokenPair struct {
    AccessToken  string    `json:"access_token"`
    RefreshToken string    `json:"refresh_token"`
    ExpiresAt    time.Time `json:"expires_at"`
}

func GenerateTokenPair(userID, email string, roles []string) (*TokenPair, error) {
    accessToken, err := GenerateToken(userID, email, roles)
    if err != nil {
        return nil, err
    }

    refreshTokenBytes := make([]byte, 32)
    if _, err := rand.Read(refreshTokenBytes); err != nil {
        return nil, fmt.Errorf("failed to generate refresh token: %w", err)
    }

    refreshToken := base64.URLEncoding.EncodeToString(refreshTokenBytes)

    return &TokenPair{
        AccessToken:  accessToken,
        RefreshToken: refreshToken,
        ExpiresAt:    time.Now().Add(24 * time.Hour),
    }, nil
}

func (h *AuthHandler) RefreshToken(w http.ResponseWriter, r *http.Request) {
    var req struct {
        RefreshToken string `json:"refresh_token"`
    }

    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "invalid request", http.StatusBadRequest)
        return
    }

    storedToken, err := h.tokenRepo.GetRefreshToken(r.Context(), req.RefreshToken)
    if err != nil {
        http.Error(w, "invalid refresh token", http.StatusUnauthorized)
        return
    }

    if storedToken.ExpiresAt.Before(time.Now()) {
        http.Error(w, "refresh token expired", http.StatusUnauthorized)
        return
    }

    user, err := h.userRepo.FindByID(r.Context(), storedToken.UserID)
    if err != nil {
        http.Error(w, "user not found", http.StatusUnauthorized)
        return
    }

    newTokenPair, err := GenerateTokenPair(user.ID, user.Email, user.Roles)
    if err != nil {
        http.Error(w, "internal error", http.StatusInternalServerError)
        return
    }

    if err := h.tokenRepo.RevokeRefreshToken(r.Context(), req.RefreshToken); err != nil {
        slog.Error("failed to revoke old refresh token", "error", err)
    }

    if err := h.tokenRepo.StoreRefreshToken(r.Context(), newTokenPair); err != nil {
        http.Error(w, "internal error", http.StatusInternalServerError)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(newTokenPair)
}
```

## Cryptographic Operations

### Secure Random Generation

```go
import "crypto/rand"

// ✅ CORRECT: Use crypto/rand for security
func GenerateSecureToken(length int) (string, error) {
    bytes := make([]byte, length)

    if _, err := rand.Read(bytes); err != nil {
        return "", fmt.Errorf("failed to generate random bytes: %w", err)
    }

    return base64.URLEncoding.EncodeToString(bytes), nil
}

// Generate API key
func GenerateAPIKey() (string, error) {
    return GenerateSecureToken(32) // 32 bytes = 256 bits
}

// Generate session ID
func GenerateSessionID() (string, error) {
    return GenerateSecureToken(24)
}

// ❌ WRONG: Never use math/rand for security
func GenerateInsecureToken() string {
    // DON'T DO THIS for security-critical operations
    return fmt.Sprintf("%d", mathrand.Int63())
}
```

### Data Encryption (AES-GCM)

```go
import (
    "crypto/aes"
    "crypto/cipher"
    "crypto/rand"
    "io"
)

// Encrypt encrypts plaintext using AES-GCM
func Encrypt(plaintext []byte, key []byte) ([]byte, error) {
    block, err := aes.NewCipher(key)
    if err != nil {
        return nil, fmt.Errorf("failed to create cipher: %w", err)
    }

    gcm, err := cipher.NewGCM(block)
    if err != nil {
        return nil, fmt.Errorf("failed to create GCM: %w", err)
    }

    nonce := make([]byte, gcm.NonceSize())
    if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
        return nil, fmt.Errorf("failed to generate nonce: %w", err)
    }

    ciphertext := gcm.Seal(nonce, nonce, plaintext, nil)
    return ciphertext, nil
}

// Decrypt decrypts ciphertext using AES-GCM
func Decrypt(ciphertext []byte, key []byte) ([]byte, error) {
    block, err := aes.NewCipher(key)
    if err != nil {
        return nil, fmt.Errorf("failed to create cipher: %w", err)
    }

    gcm, err := cipher.NewGCM(block)
    if err != nil {
        return nil, fmt.Errorf("failed to create GCM: %w", err)
    }

    nonceSize := gcm.NonceSize()
    if len(ciphertext) < nonceSize {
        return nil, errors.New("ciphertext too short")
    }

    nonce, ciphertext := ciphertext[:nonceSize], ciphertext[nonceSize:]
    plaintext, err := gcm.Open(nil, nonce, ciphertext, nil)
    if err != nil {
        return nil, fmt.Errorf("failed to decrypt: %w", err)
    }

    return plaintext, nil
}

// Usage
func EncryptSensitiveData(data string) (string, error) {
    key := []byte(os.Getenv("ENCRYPTION_KEY")) // Must be 32 bytes for AES-256

    encrypted, err := Encrypt([]byte(data), key)
    if err != nil {
        return "", err
    }

    return base64.StdEncoding.EncodeToString(encrypted), nil
}
```

## HTTPS and TLS Configuration

### Secure TLS Server Configuration

```go
import (
    "crypto/tls"
    "net/http"
)

func NewSecureServer(addr string, handler http.Handler) *http.Server {
    tlsConfig := &tls.Config{
        MinVersion: tls.VersionTLS12,
        CurvePreferences: []tls.CurveID{
            tls.CurveP256,
            tls.X25519,
        },
        PreferServerCipherSuites: true,
        CipherSuites: []uint16{
            tls.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,
            tls.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
            tls.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305,
            tls.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305,
            tls.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,
            tls.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
        },
    }

    return &http.Server{
        Addr:         addr,
        Handler:      handler,
        TLSConfig:    tlsConfig,
        ReadTimeout:  15 * time.Second,
        WriteTimeout: 15 * time.Second,
        IdleTimeout:  60 * time.Second,
    }
}

// Usage
server := NewSecureServer(":443", mux)
log.Fatal(server.ListenAndServeTLS("cert.pem", "key.pem"))
```

## Security Headers Middleware

```go
func SecurityHeadersMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Prevent clickjacking
        w.Header().Set("X-Frame-Options", "DENY")

        // Prevent MIME sniffing
        w.Header().Set("X-Content-Type-Options", "nosniff")

        // Enable XSS protection
        w.Header().Set("X-XSS-Protection", "1; mode=block")

        // Enforce HTTPS
        w.Header().Set("Strict-Transport-Security", "max-age=31536000; includeSubDomains")

        // Content Security Policy
        w.Header().Set("Content-Security-Policy", "default-src 'self'")

        // Referrer policy
        w.Header().Set("Referrer-Policy", "strict-origin-when-cross-origin")

        // Permissions policy
        w.Header().Set("Permissions-Policy", "geolocation=(), microphone=(), camera=()")

        next.ServeHTTP(w, r)
    })
}
```

## CSRF Protection

### Double-Submit Cookie Pattern

```go
import (
    "crypto/hmac"
    "crypto/sha256"
    "encoding/base64"
    "time"
)

type CSRFProtection struct {
    secret []byte
}

func NewCSRFProtection(secret []byte) *CSRFProtection {
    return &CSRFProtection{
        secret: secret,
    }
}

func (c *CSRFProtection) GenerateToken(sessionID string) (string, error) {
    timestamp := time.Now().Unix()
    message := fmt.Sprintf("%s:%d", sessionID, timestamp)

    h := hmac.New(sha256.New, c.secret)
    h.Write([]byte(message))
    signature := h.Sum(nil)

    token := fmt.Sprintf("%s.%s",
        base64.URLEncoding.EncodeToString([]byte(message)),
        base64.URLEncoding.EncodeToString(signature),
    )

    return token, nil
}

func (c *CSRFProtection) ValidateToken(token, sessionID string) error {
    parts := strings.Split(token, ".")
    if len(parts) != 2 {
        return errors.New("invalid token format")
    }

    messageBytes, err := base64.URLEncoding.DecodeString(parts[0])
    if err != nil {
        return fmt.Errorf("invalid token encoding: %w", err)
    }

    providedSig, err := base64.URLEncoding.DecodeString(parts[1])
    if err != nil {
        return fmt.Errorf("invalid signature encoding: %w", err)
    }

    h := hmac.New(sha256.New, c.secret)
    h.Write(messageBytes)
    expectedSig := h.Sum(nil)

    if !hmac.Equal(providedSig, expectedSig) {
        return errors.New("invalid token signature")
    }

    message := string(messageBytes)
    parts = strings.Split(message, ":")
    if len(parts) != 2 {
        return errors.New("invalid message format")
    }

    if parts[0] != sessionID {
        return errors.New("session mismatch")
    }

    timestamp, err := strconv.ParseInt(parts[1], 10, 64)
    if err != nil {
        return errors.New("invalid timestamp")
    }

    if time.Since(time.Unix(timestamp, 0)) > 24*time.Hour {
        return errors.New("token expired")
    }

    return nil
}

func (c *CSRFProtection) Middleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        if r.Method == http.MethodGet || r.Method == http.MethodHead || r.Method == http.MethodOptions {
            next.ServeHTTP(w, r)
            return
        }

        sessionID, ok := r.Context().Value("session_id").(string)
        if !ok {
            http.Error(w, "no session", http.StatusForbidden)
            return
        }

        csrfToken := r.Header.Get("X-CSRF-Token")
        if csrfToken == "" {
            csrfToken = r.FormValue("csrf_token")
        }

        if csrfToken == "" {
            http.Error(w, "missing CSRF token", http.StatusForbidden)
            return
        }

        if err := c.ValidateToken(csrfToken, sessionID); err != nil {
            slog.Warn("CSRF validation failed",
                "error", err,
                "session_id", sessionID,
            )
            http.Error(w, "invalid CSRF token", http.StatusForbidden)
            return
        }

        next.ServeHTTP(w, r)
    })
}

func (c *CSRFProtection) SetTokenCookie(w http.ResponseWriter, sessionID string) error {
    token, err := c.GenerateToken(sessionID)
    if err != nil {
        return err
    }

    http.SetCookie(w, &http.Cookie{
        Name:     "csrf_token",
        Value:    token,
        HttpOnly: false,
        Secure:   true,
        SameSite: http.SameSiteStrictMode,
        Path:     "/",
    })

    return nil
}
```

### Using gorilla/csrf Package

```go
import (
    "github.com/gorilla/csrf"
    "github.com/gorilla/mux"
)

func SetupCSRFProtection(r *mux.Router) http.Handler {
    csrfSecret := []byte(os.Getenv("CSRF_SECRET"))

    csrfMiddleware := csrf.Protect(
        csrfSecret,
        csrf.Secure(true),
        csrf.HttpOnly(true),
        csrf.SameSite(csrf.SameSiteStrictMode),
        csrf.Path("/"),
        csrf.MaxAge(12*3600),
        csrf.ErrorHandler(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            w.WriteHeader(http.StatusForbidden)
            json.NewEncoder(w).Encode(map[string]string{
                "error": "CSRF token validation failed",
            })
        })),
    )

    return csrfMiddleware(r)
}

func RenderFormWithCSRF(w http.ResponseWriter, r *http.Request) {
    token := csrf.Token(r)

    w.Header().Set("Content-Type", "text/html")
    fmt.Fprintf(w, `
        <form method="POST" action="/submit">
            <input type="hidden" name="csrf_token" value="%s">
            <input type="text" name="data">
            <button type="submit">Submit</button>
        </form>
    `, token)
}

func APIHandlerWithCSRF(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("X-CSRF-Token", csrf.Token(r))

    json.NewEncoder(w).Encode(map[string]string{
        "message": "Include the X-CSRF-Token header in your next request",
    })
}
```

### Stateless CSRF with JWT

```go
type CSRFClaims struct {
    SessionID string `json:"session_id"`
    jwt.RegisteredClaims
}

func GenerateCSRFToken(sessionID string, secret []byte) (string, error) {
    claims := CSRFClaims{
        SessionID: sessionID,
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(24 * time.Hour)),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
        },
    }

    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString(secret)
}

func ValidateCSRFToken(tokenString string, sessionID string, secret []byte) error {
    token, err := jwt.ParseWithClaims(tokenString, &CSRFClaims{}, func(token *jwt.Token) (interface{}, error) {
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
        }
        return secret, nil
    })

    if err != nil {
        return fmt.Errorf("invalid CSRF token: %w", err)
    }

    claims, ok := token.Claims.(*CSRFClaims)
    if !ok || !token.Valid {
        return errors.New("invalid token claims")
    }

    if claims.SessionID != sessionID {
        return errors.New("session mismatch")
    }

    return nil
}

func CSRFMiddlewareJWT(secret []byte) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            if r.Method == http.MethodGet || r.Method == http.MethodHead || r.Method == http.MethodOptions {
                next.ServeHTTP(w, r)
                return
            }

            sessionID, ok := r.Context().Value("session_id").(string)
            if !ok {
                http.Error(w, "no session", http.StatusForbidden)
                return
            }

            csrfToken := r.Header.Get("X-CSRF-Token")
            if csrfToken == "" {
                http.Error(w, "missing CSRF token", http.StatusForbidden)
                return
            }

            if err := ValidateCSRFToken(csrfToken, sessionID, secret); err != nil {
                http.Error(w, "invalid CSRF token", http.StatusForbidden)
                return
            }

            next.ServeHTTP(w, r)
        })
    }
}
```

## Rate Limiting

```go
import (
    "golang.org/x/time/rate"
    "sync"
)

type RateLimiter struct {
    limiters map[string]*rate.Limiter
    mu       sync.RWMutex
    rate     rate.Limit
    burst    int
}

func NewRateLimiter(r rate.Limit, burst int) *RateLimiter {
    return &RateLimiter{
        limiters: make(map[string]*rate.Limiter),
        rate:     r,
        burst:    burst,
    }
}

func (rl *RateLimiter) getLimiter(key string) *rate.Limiter {
    rl.mu.Lock()
    defer rl.mu.Unlock()

    limiter, exists := rl.limiters[key]
    if !exists {
        limiter = rate.NewLimiter(rl.rate, rl.burst)
        rl.limiters[key] = limiter
    }

    return limiter
}

func (rl *RateLimiter) Middleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Use IP address as key
        ip := r.RemoteAddr

        limiter := rl.getLimiter(ip)

        if !limiter.Allow() {
            http.Error(w, "rate limit exceeded", http.StatusTooManyRequests)
            return
        }

        next.ServeHTTP(w, r)
    })
}

// Usage: 10 requests per second with burst of 20
limiter := NewRateLimiter(10, 20)
http.Handle("/api/", limiter.Middleware(apiHandler))
```

## File Upload and Download Patterns

### Secure File Upload

```go
import (
    "crypto/sha256"
    "io"
    "mime/multipart"
    "path/filepath"
)

const (
    maxUploadSize = 10 << 20
    uploadPath    = "./uploads"
)

var allowedFileTypes = map[string]bool{
    "image/jpeg": true,
    "image/png":  true,
    "image/gif":  true,
    "application/pdf": true,
}

type FileUploadHandler struct {
    uploadDir string
    maxSize   int64
}

func NewFileUploadHandler(uploadDir string, maxSize int64) *FileUploadHandler {
    return &FileUploadHandler{
        uploadDir: uploadDir,
        maxSize:   maxSize,
    }
}

func (h *FileUploadHandler) Upload(w http.ResponseWriter, r *http.Request) {
    r.Body = http.MaxBytesReader(w, r.Body, h.maxSize)

    if err := r.ParseMultipartForm(h.maxSize); err != nil {
        http.Error(w, "file too large", http.StatusBadRequest)
        return
    }

    file, header, err := r.FormFile("file")
    if err != nil {
        http.Error(w, "error retrieving file", http.StatusBadRequest)
        return
    }
    defer file.Close()

    if header.Size > h.maxSize {
        http.Error(w, "file too large", http.StatusBadRequest)
        return
    }

    buffer := make([]byte, 512)
    if _, err := file.Read(buffer); err != nil {
        http.Error(w, "error reading file", http.StatusInternalServerError)
        return
    }

    contentType := http.DetectContentType(buffer)
    if !allowedFileTypes[contentType] {
        http.Error(w, "invalid file type", http.StatusBadRequest)
        return
    }

    if _, err := file.Seek(0, 0); err != nil {
        http.Error(w, "error processing file", http.StatusInternalServerError)
        return
    }

    filename, err := h.saveFile(file, header)
    if err != nil {
        http.Error(w, "error saving file", http.StatusInternalServerError)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]string{
        "filename": filename,
        "size":     fmt.Sprintf("%d", header.Size),
        "type":     contentType,
    })
}

func (h *FileUploadHandler) saveFile(file multipart.File, header *multipart.FileHeader) (string, error) {
    hash := sha256.New()
    if _, err := io.Copy(hash, file); err != nil {
        return "", err
    }

    if _, err := file.Seek(0, 0); err != nil {
        return "", err
    }

    filename := fmt.Sprintf("%x%s", hash.Sum(nil), filepath.Ext(header.Filename))

    dst, err := os.Create(filepath.Join(h.uploadDir, filename))
    if err != nil {
        return "", err
    }
    defer dst.Close()

    if _, err := io.Copy(dst, file); err != nil {
        return "", err
    }

    return filename, nil
}
```

### File Upload with Validation

```go
type FileValidator struct {
    MaxSize       int64
    AllowedTypes  map[string]bool
    AllowedExts   map[string]bool
}

func NewFileValidator() *FileValidator {
    return &FileValidator{
        MaxSize: 10 << 20,
        AllowedTypes: map[string]bool{
            "image/jpeg": true,
            "image/png":  true,
            "image/gif":  true,
        },
        AllowedExts: map[string]bool{
            ".jpg":  true,
            ".jpeg": true,
            ".png":  true,
            ".gif":  true,
        },
    }
}

func (v *FileValidator) Validate(file multipart.File, header *multipart.FileHeader) error {
    if header.Size > v.MaxSize {
        return fmt.Errorf("file size exceeds maximum: %d bytes", v.MaxSize)
    }

    buffer := make([]byte, 512)
    if _, err := file.Read(buffer); err != nil {
        return fmt.Errorf("failed to read file: %w", err)
    }

    contentType := http.DetectContentType(buffer)
    if !v.AllowedTypes[contentType] {
        return fmt.Errorf("invalid file type: %s", contentType)
    }

    ext := filepath.Ext(header.Filename)
    if !v.AllowedExts[ext] {
        return fmt.Errorf("invalid file extension: %s", ext)
    }

    if _, err := file.Seek(0, 0); err != nil {
        return fmt.Errorf("failed to reset file pointer: %w", err)
    }

    return nil
}
```

### Streaming Large File Upload

```go
func (h *FileUploadHandler) StreamUpload(w http.ResponseWriter, r *http.Request) {
    r.Body = http.MaxBytesReader(w, r.Body, h.maxSize)

    reader, err := r.MultipartReader()
    if err != nil {
        http.Error(w, "error parsing multipart", http.StatusBadRequest)
        return
    }

    for {
        part, err := reader.NextPart()
        if err == io.EOF {
            break
        }
        if err != nil {
            http.Error(w, "error reading part", http.StatusBadRequest)
            return
        }

        if part.FormName() != "file" {
            continue
        }

        filename := sanitizeFilename(part.FileName())
        filepath := filepath.Join(h.uploadDir, filename)

        dst, err := os.Create(filepath)
        if err != nil {
            http.Error(w, "error creating file", http.StatusInternalServerError)
            return
        }

        hash := sha256.New()
        writer := io.MultiWriter(dst, hash)

        written, err := io.Copy(writer, part)
        dst.Close()

        if err != nil {
            os.Remove(filepath)
            http.Error(w, "error saving file", http.StatusInternalServerError)
            return
        }

        checksum := fmt.Sprintf("%x", hash.Sum(nil))

        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(map[string]interface{}{
            "filename": filename,
            "size":     written,
            "checksum": checksum,
        })

        return
    }

    http.Error(w, "no file uploaded", http.StatusBadRequest)
}

func sanitizeFilename(filename string) string {
    filename = filepath.Base(filename)
    filename = strings.ReplaceAll(filename, "..", "")
    return filename
}
```

### File Download with Range Support

```go
func (h *FileUploadHandler) Download(w http.ResponseWriter, r *http.Request) {
    filename := r.URL.Query().Get("file")
    if filename == "" {
        http.Error(w, "missing filename", http.StatusBadRequest)
        return
    }

    cleanFilename := filepath.Clean(filename)
    if strings.Contains(cleanFilename, "..") {
        http.Error(w, "invalid filename", http.StatusBadRequest)
        return
    }

    filepath := filepath.Join(h.uploadDir, cleanFilename)

    file, err := os.Open(filepath)
    if err != nil {
        http.Error(w, "file not found", http.StatusNotFound)
        return
    }
    defer file.Close()

    stat, err := file.Stat()
    if err != nil {
        http.Error(w, "error reading file", http.StatusInternalServerError)
        return
    }

    w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=%s", cleanFilename))
    w.Header().Set("Content-Type", "application/octet-stream")
    w.Header().Set("Content-Length", fmt.Sprintf("%d", stat.Size()))

    http.ServeContent(w, r, cleanFilename, stat.ModTime(), file)
}
```

### Secure Download with Token

```go
type DownloadToken struct {
    FileID    string    `json:"file_id"`
    ExpiresAt time.Time `json:"expires_at"`
    jwt.RegisteredClaims
}

func GenerateDownloadToken(fileID string, secret []byte) (string, error) {
    claims := DownloadToken{
        FileID:    fileID,
        ExpiresAt: time.Now().Add(1 * time.Hour),
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(1 * time.Hour)),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
        },
    }

    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString(secret)
}

func (h *FileUploadHandler) SecureDownload(w http.ResponseWriter, r *http.Request) {
    token := r.URL.Query().Get("token")
    if token == "" {
        http.Error(w, "missing token", http.StatusUnauthorized)
        return
    }

    claims, err := ValidateDownloadToken(token, []byte(os.Getenv("JWT_SECRET")))
    if err != nil {
        http.Error(w, "invalid token", http.StatusUnauthorized)
        return
    }

    if time.Now().After(claims.ExpiresAt) {
        http.Error(w, "token expired", http.StatusUnauthorized)
        return
    }

    filepath := filepath.Join(h.uploadDir, claims.FileID)

    file, err := os.Open(filepath)
    if err != nil {
        http.Error(w, "file not found", http.StatusNotFound)
        return
    }
    defer file.Close()

    stat, err := file.Stat()
    if err != nil {
        http.Error(w, "error reading file", http.StatusInternalServerError)
        return
    }

    w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=%s", claims.FileID))
    w.Header().Set("Content-Type", "application/octet-stream")

    http.ServeContent(w, r, claims.FileID, stat.ModTime(), file)
}

func ValidateDownloadToken(tokenString string, secret []byte) (*DownloadToken, error) {
    token, err := jwt.ParseWithClaims(tokenString, &DownloadToken{}, func(token *jwt.Token) (interface{}, error) {
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
        }
        return secret, nil
    })

    if err != nil {
        return nil, fmt.Errorf("invalid token: %w", err)
    }

    claims, ok := token.Claims.(*DownloadToken)
    if !ok || !token.Valid {
        return nil, errors.New("invalid token claims")
    }

    return claims, nil
}
```

### Upload Progress Tracking

```go
type ProgressWriter struct {
    Total      int64
    Uploaded   int64
    OnProgress func(uploaded, total int64)
}

func (pw *ProgressWriter) Write(p []byte) (int, error) {
    n := len(p)
    pw.Uploaded += int64(n)

    if pw.OnProgress != nil {
        pw.OnProgress(pw.Uploaded, pw.Total)
    }

    return n, nil
}

func (h *FileUploadHandler) UploadWithProgress(w http.ResponseWriter, r *http.Request) {
    file, header, err := r.FormFile("file")
    if err != nil {
        http.Error(w, "error retrieving file", http.StatusBadRequest)
        return
    }
    defer file.Close()

    dst, err := os.Create(filepath.Join(h.uploadDir, header.Filename))
    if err != nil {
        http.Error(w, "error creating file", http.StatusInternalServerError)
        return
    }
    defer dst.Close()

    progressWriter := &ProgressWriter{
        Total: header.Size,
        OnProgress: func(uploaded, total int64) {
            percentage := float64(uploaded) / float64(total) * 100
            slog.Info("upload progress",
                "filename", header.Filename,
                "uploaded", uploaded,
                "total", total,
                "percentage", fmt.Sprintf("%.2f%%", percentage),
            )
        },
    }

    writer := io.MultiWriter(dst, progressWriter)

    if _, err := io.Copy(writer, file); err != nil {
        http.Error(w, "error saving file", http.StatusInternalServerError)
        return
    }

    w.WriteHeader(http.StatusOK)
    json.NewEncoder(w).Encode(map[string]string{
        "message": "file uploaded successfully",
    })
}
```

### Virus Scanning Integration Hook

```go
type VirusScanner interface {
    Scan(filepath string) error
}

type ClamAVScanner struct {
    socketPath string
}

func NewClamAVScanner(socketPath string) *ClamAVScanner {
    return &ClamAVScanner{
        socketPath: socketPath,
    }
}

func (s *ClamAVScanner) Scan(filepath string) error {
    return nil
}

func (h *FileUploadHandler) UploadWithScan(w http.ResponseWriter, r *http.Request, scanner VirusScanner) {
    file, header, err := r.FormFile("file")
    if err != nil {
        http.Error(w, "error retrieving file", http.StatusBadRequest)
        return
    }
    defer file.Close()

    filename, err := h.saveFile(file, header)
    if err != nil {
        http.Error(w, "error saving file", http.StatusInternalServerError)
        return
    }

    filepath := filepath.Join(h.uploadDir, filename)

    if err := scanner.Scan(filepath); err != nil {
        os.Remove(filepath)
        slog.Error("virus detected", "filename", filename, "error", err)
        http.Error(w, "file contains malware", http.StatusBadRequest)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]string{
        "filename": filename,
        "status":   "clean",
    })
}
```

## Secrets Management

### Loading Secrets from Environment

```go
type Config struct {
    DatabaseURL    string
    JWTSecret      string
    EncryptionKey  string
    APIKey         string
}

func LoadConfig() (*Config, error) {
    config := &Config{
        DatabaseURL:   os.Getenv("DATABASE_URL"),
        JWTSecret:     os.Getenv("JWT_SECRET"),
        EncryptionKey: os.Getenv("ENCRYPTION_KEY"),
        APIKey:        os.Getenv("API_KEY"),
    }

    // Validate required secrets
    if config.DatabaseURL == "" {
        return nil, errors.New("DATABASE_URL is required")
    }
    if config.JWTSecret == "" {
        return nil, errors.New("JWT_SECRET is required")
    }
    if len(config.EncryptionKey) != 32 {
        return nil, errors.New("ENCRYPTION_KEY must be 32 bytes")
    }

    return config, nil
}

// ❌ NEVER do this
const (
    APIKey = "hardcoded-api-key-12345"  // DON'T HARDCODE SECRETS
)
```

## Logging Best Practices

### Secure Logging (No Sensitive Data)

```go
import "log/slog"

// ✅ CORRECT: Redact sensitive information
func (uc *LoginUseCase) Execute(ctx context.Context, email, password string) error {
    slog.InfoContext(ctx, "login attempt",
        "email", email,  // OK to log email
        // "password", password,  // NEVER log passwords
    )

    user, err := uc.userRepo.FindByEmail(ctx, email)
    if err != nil {
        slog.ErrorContext(ctx, "login failed",
            "email", email,
            "error", err,
        )
        return errors.New("invalid credentials")
    }

    if err := VerifyPassword(user.HashedPassword, password); err != nil {
        slog.WarnContext(ctx, "invalid password",
            "email", email,
            // Don't log the password or hash
        )
        return errors.New("invalid credentials")
    }

    return nil
}

// Redact sensitive fields in structs
type User struct {
    ID             string `json:"id"`
    Email          string `json:"email"`
    HashedPassword string `json:"-"` // Never serialize
    APIKey         string `json:"-"` // Never serialize
}
```

## Security Checklist

### ✅ DO
- Use parameterized queries for all database operations
- Hash passwords with bcrypt or argon2
- Use crypto/rand for all random generation
- Validate and sanitize all user input
- Use HTTPS/TLS for all network communication
- Implement rate limiting on public endpoints
- Set secure HTTP headers
- Use strong encryption (AES-256-GCM)
- Load secrets from environment variables
- Never log sensitive data (passwords, tokens, keys)
- Implement proper authentication and authorization
- Keep dependencies updated (govulncheck)
- Use security scanning (gosec)

### ❌ DON'T
- Don't concatenate user input into SQL queries
- Don't use math/rand for security-critical operations
- Don't hardcode secrets in code
- Don't ignore security scanner warnings
- Don't expose internal error details to users
- Don't log passwords, tokens, or API keys
- Don't skip input validation
- Don't use weak hashing algorithms (MD5, SHA1 for passwords)
- Don't allow unlimited rate requests
- Don't serve over HTTP (use HTTPS only)
