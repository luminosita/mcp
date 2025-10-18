# User Story: API Authentication (API Key/JWT)

## Metadata
- **Story ID:** US-052
- **Title:** API Authentication (API Key/JWT)
- **Type:** Feature
- **Status:** Backlog
- **Priority:** High - Security requirement (blocks production deployment)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-009
- **Functional Requirements Covered:** FR-14 (API authentication requirement)
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration v3]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Non-Functional Requirements - Security - NFR-Security-01
- **Functional Requirements Coverage:**
  - **FR-14:** Task Tracking microservice REST API SHALL require authentication via API key or JWT token (line 163: "API authenticated via API key or JWT token")

**Parent High-Level Story:** [HLS-009: Task Tracking Microservice]
- **Link:** `/artifacts/hls/HLS-009_task_tracking_microservice_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 5: API Authentication (API Key/JWT)

## User Story
As a Task Tracking microservice developer, I want API key or JWT authentication middleware for all REST endpoints, so that only authorized MCP Server instances can access task tracking and ID management APIs (no unauthenticated access).

## Description
The Task Tracking microservice exposes REST APIs for task tracking and ID management. These APIs must be protected from unauthenticated access to prevent unauthorized task manipulation, ID allocation abuse, and data leakage across projects. This story implements authentication middleware that validates API key or JWT token on every request, returns 401 Unauthorized for missing/invalid credentials, and logs all authentication failures for security monitoring.

Authentication approach decision: Start with API key (simpler, sufficient for pilot phase with single trusted MCP Server). JWT support can be added later for multi-tenant scenarios requiring fine-grained permissions.

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **HTTP Middleware Pattern:** Authentication middleware intercepts all requests before reaching endpoint handlers
  - **Execution Order:** Request → Auth Middleware (validate credentials) → Endpoint Handler → Response
  - **Short-Circuit:** If authentication fails, middleware returns 401 immediately (handler not executed)
- **API Key Authentication:** Simple bearer token authentication via HTTP Authorization header
  - **Header Format:** `Authorization: Bearer <API_KEY>`
  - **Validation:** Compare provided key against server-configured key (environment variable)
  - **Security:** API key stored securely (environment variable, not hardcoded)
- **JWT Authentication (Future):** Token-based authentication with expiration and claims
  - **Deferred to future story:** JWT adds complexity (token generation, expiration, claims validation) not needed for pilot phase

**Anti-Patterns Avoided:**
- **Avoid Hardcoded API Keys:** Store API key in environment variable (API_KEY=...), not source code
- **Avoid Plaintext Logging:** Do not log full API key in logs (log first 8 characters only: "API key: abc12345...")
- **Avoid Missing Endpoint Coverage:** Apply middleware to ALL endpoints (no unauthenticated bypass)

**Performance Considerations:**
- **Middleware Overhead:** API key validation adds <1ms latency per request (string comparison)
- **No Database Lookup:** API key stored in-memory (environment variable), no database query needed

## Functional Requirements
- Authentication middleware validates API key on all REST endpoints (task tracking + ID management)
- HTTP header format: `Authorization: Bearer <API_KEY>`
- Server configuration: API key loaded from environment variable `API_KEY` (fail to start if missing)
- Unauthorized response: Return 401 Unauthorized with JSON body `{success: false, error: "Unauthorized: Missing or invalid API key"}`
- Successful authentication: Request proceeds to endpoint handler
- Logging: Log all authentication failures with timestamp, endpoint, IP address (security monitoring)
- Health check endpoint exception: `/health` endpoint accessible without authentication (monitoring tools need unauthenticated access)

## Non-Functional Requirements
- **Security:** API key must be stored securely (environment variable or secret management system per NFR-Security-04)
- **Security:** No plaintext API keys in logs (log first 8 characters only for debugging: "API key: abc12345...")
- **Performance:** Middleware overhead <1ms per request (simple string comparison)
- **Reliability:** Server fails to start if API_KEY environment variable not set (fail-fast principle)
- **Observability:** Log all authentication failures with sufficient detail for security investigation

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story implements Go HTTP middleware. Reference Go implementation standards (CLAUDE-core.md, CLAUDE-tooling.md) for middleware patterns and security best practices.

### Implementation Guidance

**Middleware Implementation (Go):**

```go
// Example middleware function
func AuthMiddleware(apiKey string) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            // Extract Authorization header
            authHeader := r.Header.Get("Authorization")

            // Check if header present
            if authHeader == "" {
                respondUnauthorized(w, "Missing Authorization header")
                return
            }

            // Validate Bearer token format
            const prefix = "Bearer "
            if !strings.HasPrefix(authHeader, prefix) {
                respondUnauthorized(w, "Invalid Authorization header format. Expected: Bearer <API_KEY>")
                return
            }

            // Extract API key
            providedKey := strings.TrimPrefix(authHeader, prefix)

            // Validate API key
            if providedKey != apiKey {
                // Log failed authentication (first 8 chars only)
                log.Warn("Authentication failed", "api_key_prefix", providedKey[:min(8, len(providedKey))], "ip", r.RemoteAddr, "endpoint", r.URL.Path)
                respondUnauthorized(w, "Invalid API key")
                return
            }

            // Authentication successful, proceed to handler
            next.ServeHTTP(w, r)
        })
    }
}

func respondUnauthorized(w http.ResponseWriter, message string) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusUnauthorized)
    json.NewEncoder(w).Encode(map[string]interface{}{
        "success": false,
        "error":   message,
    })
}
```

**Middleware Registration:**

```go
// Example router setup (chi framework)
r := chi.NewRouter()

// Load API key from environment
apiKey := os.Getenv("API_KEY")
if apiKey == "" {
    log.Fatal("API_KEY environment variable not set")
}

// Apply auth middleware to all routes EXCEPT /health
r.Route("/", func(r chi.Router) {
    // Public endpoint (no auth)
    r.Get("/health", healthCheckHandler)

    // Protected endpoints (auth required)
    r.Group(func(r chi.Router) {
        r.Use(AuthMiddleware(apiKey))

        // Task tracking endpoints
        r.Get("/tasks/next", getNextTaskHandler)
        r.Put("/tasks/{id}/status", updateTaskStatusHandler)
        r.Get("/tasks", getTasksHandler)
        r.Post("/tasks/batch", batchAddTasksHandler)

        // ID management endpoints
        r.Get("/ids/next", getNextIDHandler)
        r.Post("/ids/reserve", reserveIDRangeHandler)
        r.Post("/ids/confirm", confirmReservationHandler)
        r.Delete("/ids/reservations/expired", cleanupExpiredHandler)
    })
})
```

**API Key Generation (for deployment):**

```bash
# Generate secure random API key (32 characters)
openssl rand -base64 32

# Example output: "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6="
```

**Environment Variable Configuration:**

```bash
# .env file (local development)
API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6=

# Docker Compose
services:
  task-tracking:
    environment:
      - API_KEY=${API_KEY}

# Podman/Docker run
podman run -e API_KEY="a1b2c3d4..." task-tracking:latest
```

**Security Logging:**

```go
// Log authentication failure with limited key exposure
log.Warn("Authentication failed",
    "api_key_prefix", providedKey[:min(8, len(providedKey))], // First 8 chars only
    "ip", r.RemoteAddr,
    "endpoint", r.URL.Path,
    "timestamp", time.Now().UTC(),
)
```

**References to Implementation Standards:**
- **CLAUDE-core.md (Go):** Middleware patterns, error handling, fail-fast principle
- **CLAUDE-tooling.md (Go):** Environment variable loading, configuration management
- **CLAUDE-validation.md (Go):** Input validation patterns (validate Authorization header format)

**Note:** Treat CLAUDE.md (Go) files as authoritative for security patterns and middleware implementation.

### Technical Tasks
- Implement AuthMiddleware function with API key validation
- Load API key from environment variable (API_KEY) with startup validation
- Apply middleware to all endpoints except /health
- Implement 401 Unauthorized response with JSON error message
- Add security logging for failed authentication attempts (limited key exposure)
- Update deployment documentation with API key generation instructions
- Write unit tests for middleware (valid key, invalid key, missing header, malformed header)
- Write integration tests for authenticated vs. unauthenticated requests

## Acceptance Criteria

### Scenario 1: Successful authentication with valid API key
**Given** server configured with API_KEY="test-key-12345"
**When** client sends GET /tasks/next with header `Authorization: Bearer test-key-12345`
**Then** request proceeds to endpoint handler
**And** endpoint returns 200 OK (or 404/400 depending on query)
**And** no authentication error logged

### Scenario 2: Reject request with invalid API key
**Given** server configured with API_KEY="test-key-12345"
**When** client sends GET /tasks/next with header `Authorization: Bearer wrong-key`
**Then** middleware returns 401 Unauthorized
**And** response body contains `{success: false, error: "Invalid API key"}`
**And** authentication failure logged with api_key_prefix="wrong-ke" (first 8 chars), IP address, endpoint

### Scenario 3: Reject request with missing Authorization header
**Given** server configured with API_KEY="test-key-12345"
**When** client sends GET /tasks/next without Authorization header
**Then** middleware returns 401 Unauthorized
**And** response body contains `{success: false, error: "Missing Authorization header"}`

### Scenario 4: Reject request with malformed Authorization header
**Given** server configured with API_KEY="test-key-12345"
**When** client sends GET /tasks/next with header `Authorization: test-key-12345` (missing "Bearer" prefix)
**Then** middleware returns 401 Unauthorized
**And** response body contains `{success: false, error: "Invalid Authorization header format. Expected: Bearer <API_KEY>"}`

### Scenario 5: Health check endpoint accessible without authentication
**Given** server configured with API_KEY="test-key-12345"
**When** client sends GET /health without Authorization header
**Then** endpoint returns 200 OK with health status (no authentication required)

### Scenario 6: All protected endpoints require authentication
**Given** server configured with API_KEY="test-key-12345"
**When** client sends unauthenticated requests to all 8 protected endpoints (GET /tasks/next, PUT /tasks/{id}/status, GET /tasks, POST /tasks/batch, GET /ids/next, POST /ids/reserve, POST /ids/confirm, DELETE /ids/reservations/expired)
**Then** all requests return 401 Unauthorized (no endpoint bypasses authentication)

### Scenario 7: Server fails to start if API_KEY not set
**Given** API_KEY environment variable not set
**When** server starts
**Then** server fails with error message "API_KEY environment variable not set" (fail-fast)
**And** process exits with non-zero status code

### Scenario 8: Middleware overhead is minimal
**Given** server configured with API_KEY="test-key-12345"
**When** client sends 100 authenticated requests to GET /tasks/next
**Then** middleware overhead <1ms per request (measured via request duration logging)

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 5 SP - CONSIDER threshold, but below 5+ SP (DON'T SKIP) threshold
- **Developer Count:** Single developer (backend security engineer or backend developer)
- **Domain Span:** Single domain (backend only - cross-cutting middleware concern but still backend)
- **Complexity:** Low - standard HTTP middleware pattern, simple string comparison for API key validation
- **Uncertainty:** Low - well-established authentication pattern, no new technology or framework learning required
- **Override Factors:** Security-critical, but implementation is straightforward (no complex cryptography, no multi-tenant permissions)

**Conclusion:** Story is within single developer capacity with straightforward implementation (middleware function + environment variable loading). API key authentication is simpler than JWT (no token generation, expiration, claims). Task decomposition overhead not justified. Implementation can proceed directly from this backlog story.

## Definition of Done
- [ ] AuthMiddleware implemented and tested
- [ ] API key loaded from environment variable with startup validation
- [ ] Middleware applied to all endpoints except /health
- [ ] 401 Unauthorized response implemented with JSON error message
- [ ] Security logging implemented for failed authentication
- [ ] Unit tests written and passing (80% coverage minimum)
- [ ] Integration tests passing (all 8 acceptance criteria validated)
- [ ] Code review completed
- [ ] Documentation updated (deployment guide with API key generation instructions, environment variable configuration)
- [ ] Product Owner acceptance obtained

## Additional Information
**Suggested Labels:** backend, go, security, authentication, middleware
**Estimated Story Points:** 5
**Dependencies:**
- US-050 completed (task tracking endpoints)
- US-051 completed (ID management endpoints)

**Related PRD Section:** PRD-006 §Non-Functional Requirements - Security - NFR-Security-01 (lines 195)

## Decisions Made

**All technical approaches clear from Implementation Research and PRD.**

API key authentication is standard HTTP middleware pattern (well-documented in Go community). Environment variable loading is standard configuration management approach. Security logging patterns established in CLAUDE-core.md (Go) standards.

**Future Enhancement (not in scope for this story):** JWT authentication for multi-tenant scenarios with fine-grained permissions (e.g., project-specific access control). Deferred until business requirement emerges for multiple MCP Server instances with different permission levels.
