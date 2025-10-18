# User Story: Observability (Health Check, Logging)

## Metadata
- **Story ID:** US-055
- **Title:** Observability (Health Check, Logging)
- **Type:** Feature
- **Status:** Backlog
- **Priority:** Medium - Operational requirement (enables production monitoring)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-009
- **Functional Requirements Covered:** FR-17 (tool invocation logging), NFR-Availability-02 (health check), NFR-Observability-01 (structured logging)
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration v3]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Non-Functional Requirements - Observability (NFR-Observability-01, NFR-Observability-02)
- **Functional Requirements Coverage:**
  - **FR-17:** MCP Server SHALL log all tool invocations with timestamp, input parameters, execution duration, result status
  - **NFR-Availability-02:** Task Tracking microservice SHALL implement health check endpoint (`/health`) returning status within 100ms
  - **NFR-Observability-01:** MCP Server SHALL log all tool invocations with structured JSON format

**Parent High-Level Story:** [HLS-009: Task Tracking Microservice]
- **Link:** `/artifacts/hls/HLS-009_task_tracking_microservice_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 8: Observability (Health Check, Logging)

## User Story
As a DevOps engineer, I want a health check endpoint for monitoring and structured logging for all API calls, so that I can monitor microservice availability, debug production issues, and detect performance anomalies.

## Description
The Task Tracking microservice requires observability features for production operations. This story implements two core capabilities:

1. **Health Check Endpoint:** `GET /health` returns microservice status and database connectivity within 100ms
2. **Structured Logging:** All API requests logged in JSON format with timestamp, method, path, status code, duration, error details

Health check endpoint enables monitoring tools (Prometheus, Datadog, Grafana) to detect outages and trigger alerts. Structured logging enables log aggregation systems (ELK stack, Splunk, Loki) to query logs efficiently and analyze request patterns.

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **Health Check Pattern:** Lightweight endpoint that verifies critical dependencies (database connectivity)
  - **Response Format:** JSON with status, version, uptime, dependencies (database status)
  - **Performance:** Health check <100ms (fast query like `SELECT 1` to verify database)
- **Structured Logging:** JSON-formatted logs for machine readability
  - **Fields:** timestamp, level (INFO/WARN/ERROR), method, path, status_code, duration_ms, error_message
  - **Library Options:** logrus (Go), zap (Go), zerolog (Go) - all support structured JSON logging
- **Middleware Logging:** HTTP middleware captures request/response details automatically
  - **Execution Order:** Request → Logging Middleware (start timer) → Handler → Logging Middleware (log duration) → Response

**Anti-Patterns Avoided:**
- **Avoid Heavy Health Checks:** Do not run expensive database queries (slow health checks mislead monitoring)
- **Avoid Plaintext Logs:** Use structured JSON (not "Request: GET /tasks/next took 45ms" - hard to parse)
- **Avoid Logging Sensitive Data:** Do not log API keys, full task content (log task_id only)

**Performance Considerations:**
- **Health Check Latency:** <100ms for monitoring tools (verify database with lightweight query: `SELECT 1`)
- **Logging Overhead:** Structured logging adds <1ms per request (negligible with async logging buffer)

## Functional Requirements
- Endpoint: `GET /health` - Returns JSON with microservice status, database connectivity, uptime
- Health check response time: <100ms (per NFR-Availability-02)
- Health check response format: `{status: "healthy", version: "1.0.0", uptime_seconds: 3600, dependencies: {database: "connected"}}`
- Health check database verification: Execute lightweight query (`SELECT 1`) to verify connectivity
- Structured logging for all API requests: Log timestamp, method, path, status_code, duration_ms, error_message (if applicable)
- Log levels: INFO (successful requests, 2xx/3xx status codes), WARN (client errors, 4xx status codes), ERROR (server errors, 5xx status codes)
- Log format: JSON (machine-readable for log aggregation)
- Log output: stdout (container-friendly, captured by Docker/Podman logs)
- Sensitive data protection: Do not log full API keys (log first 8 characters only: "api_key_prefix"), do not log full task content (log task_id only)

## Non-Functional Requirements
- **Performance:** Health check endpoint response time <100ms (per NFR-Availability-02)
- **Performance:** Structured logging overhead <1ms per request (negligible impact on API latency)
- **Observability:** Logs queryable by timestamp, status_code, endpoint path, error message
- **Reliability:** Health check endpoint accessible without authentication (monitoring tools need unauthenticated access)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story implements Go health check and logging. Reference Go implementation standards (CLAUDE-core.md, CLAUDE-tooling.md) for logging library selection and middleware patterns.

### Implementation Guidance

**Health Check Endpoint Implementation (Go):**

```go
// Health check handler
func healthCheckHandler(w http.ResponseWriter, r *http.Request) {
    start := time.Now()

    // Check database connectivity
    ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
    defer cancel()

    var dbStatus string
    err := db.Pool.QueryRow(ctx, "SELECT 1").Scan(new(int))
    if err != nil {
        dbStatus = "disconnected"
        log.Error("Health check: Database connectivity failed", "error", err)
    } else {
        dbStatus = "connected"
    }

    // Build health response
    health := HealthResponse{
        Status:         "healthy", // or "degraded" if database down
        Version:        "1.0.0",
        UptimeSeconds:  int(time.Since(startTime).Seconds()),
        Dependencies: map[string]string{
            "database": dbStatus,
        },
    }

    // Return response
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusOK)
    json.NewEncoder(w).Encode(health)

    // Log health check request
    duration := time.Since(start)
    log.Info("Health check",
        "duration_ms", duration.Milliseconds(),
        "db_status", dbStatus,
    )
}

type HealthResponse struct {
    Status         string            `json:"status"`
    Version        string            `json:"version"`
    UptimeSeconds  int               `json:"uptime_seconds"`
    Dependencies   map[string]string `json:"dependencies"`
}
```

**Structured Logging Middleware (Go with logrus/zap/zerolog):**

```go
import (
    "time"
    "github.com/rs/zerolog/log"
)

// Logging middleware
func LoggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()

        // Wrap ResponseWriter to capture status code
        wrapped := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}

        // Execute handler
        next.ServeHTTP(wrapped, r)

        // Log request details
        duration := time.Since(start)
        level := getLogLevel(wrapped.statusCode)

        log.WithLevel(level).
            Str("method", r.Method).
            Str("path", r.URL.Path).
            Int("status_code", wrapped.statusCode).
            Int64("duration_ms", duration.Milliseconds()).
            Str("remote_addr", r.RemoteAddr).
            Msg("API request")
    })
}

// responseWriter wrapper to capture status code
type responseWriter struct {
    http.ResponseWriter
    statusCode int
}

func (w *responseWriter) WriteHeader(code int) {
    w.statusCode = code
    w.ResponseWriter.WriteHeader(code)
}

// Determine log level based on status code
func getLogLevel(statusCode int) zerolog.Level {
    switch {
    case statusCode >= 500:
        return zerolog.ErrorLevel
    case statusCode >= 400:
        return zerolog.WarnLevel
    default:
        return zerolog.InfoLevel
    }
}
```

**Logging Configuration (main.go):**

```go
import (
    "os"
    "github.com/rs/zerolog"
    "github.com/rs/zerolog/log"
)

func main() {
    // Configure structured JSON logging
    zerolog.TimeFieldFormat = zerolog.TimeFormatUnix
    log.Logger = zerolog.New(os.Stdout).With().Timestamp().Logger()

    // Set log level from environment (default: INFO)
    logLevel := os.Getenv("LOG_LEVEL")
    if logLevel == "" {
        logLevel = "info"
    }
    level, _ := zerolog.ParseLevel(logLevel)
    zerolog.SetGlobalLevel(level)

    log.Info().Msg("Task Tracking microservice starting...")

    // Initialize router with logging middleware
    r := chi.NewRouter()
    r.Use(LoggingMiddleware)

    // Health check endpoint (no auth middleware)
    r.Get("/health", healthCheckHandler)

    // Protected endpoints (auth + logging middleware)
    r.Group(func(r chi.Router) {
        r.Use(AuthMiddleware(apiKey))
        // ... endpoints
    })

    // Start server
    log.Info().Msgf("Listening on :8080")
    http.ListenAndServe(":8080", r)
}
```

**Example Structured Log Output (JSON):**

```json
{"level":"info","method":"GET","path":"/tasks/next","status_code":200,"duration_ms":45,"remote_addr":"127.0.0.1:54321","time":1697654400,"message":"API request"}
{"level":"warn","method":"PUT","path":"/tasks/TASK-999/status","status_code":404,"duration_ms":12,"remote_addr":"127.0.0.1:54322","time":1697654401,"message":"API request"}
{"level":"error","method":"POST","path":"/ids/reserve","status_code":500,"duration_ms":230,"remote_addr":"127.0.0.1:54323","error":"database connection failed","time":1697654402,"message":"API request"}
```

**Health Check Monitoring Integration:**

```yaml
# Prometheus scrape config (example)
scrape_configs:
  - job_name: 'task-tracking'
    metrics_path: '/health'
    static_configs:
      - targets: ['localhost:8080']

# Docker Compose health check
services:
  task-tracking:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

**References to Implementation Standards:**
- **CLAUDE-core.md (Go):** Logging patterns, error handling
- **CLAUDE-tooling.md (Go):** Logging library selection (logrus vs. zap vs. zerolog), Taskfile integration
- **CLAUDE-architecture.md (Go):** Middleware patterns, project structure

**Note:** Treat CLAUDE.md (Go) files as authoritative for logging library selection and middleware implementation.

### Technical Tasks
- Implement GET /health endpoint with database connectivity check
- Implement LoggingMiddleware for structured JSON logging
- Configure logging library (logrus, zap, or zerolog) with JSON output
- Add log level configuration (environment variable LOG_LEVEL)
- Integrate logging middleware into HTTP router
- Add health check endpoint to Docker Compose health check configuration
- Write unit tests for health check endpoint (database connected, database disconnected)
- Write unit tests for logging middleware (verify JSON output, status code-based log levels)

## Acceptance Criteria

### Scenario 1: Health check returns healthy status with database connected
**Given** Task Tracking microservice running with PostgreSQL database accessible
**When** monitoring tool sends GET /health
**Then** endpoint returns 200 OK within 100ms
**And** response body contains `{status: "healthy", version: "1.0.0", uptime_seconds: ..., dependencies: {database: "connected"}}`
**And** health check logged with INFO level and duration_ms

### Scenario 2: Health check returns degraded status with database disconnected
**Given** Task Tracking microservice running with PostgreSQL database stopped
**When** monitoring tool sends GET /health
**Then** endpoint returns 200 OK within 100ms
**And** response body contains `{status: "degraded", dependencies: {database: "disconnected"}}`
**And** health check logged with ERROR level and error message "Database connectivity failed"

### Scenario 3: Health check endpoint accessible without authentication
**Given** Task Tracking microservice configured with API key authentication
**When** monitoring tool sends GET /health without Authorization header
**Then** endpoint returns 200 OK (no 401 Unauthorized)
**And** health check bypasses authentication middleware

### Scenario 4: Structured logging for successful request (200 OK)
**Given** Task Tracking microservice running with structured logging enabled
**When** client sends GET /tasks/next?project=ai-agent-mcp-server (returns 200 OK in 45ms)
**Then** log entry written to stdout in JSON format
**And** log contains fields: `{level: "info", method: "GET", path: "/tasks/next", status_code: 200, duration_ms: 45, remote_addr: "...", time: ..., message: "API request"}`

### Scenario 5: Structured logging for client error (404 Not Found)
**Given** Task Tracking microservice running
**When** client sends PUT /tasks/TASK-999/status for non-existent task (returns 404 in 12ms)
**Then** log entry written with WARN level
**And** log contains fields: `{level: "warn", method: "PUT", path: "/tasks/TASK-999/status", status_code: 404, duration_ms: 12, ...}`

### Scenario 6: Structured logging for server error (500 Internal Server Error)
**Given** Task Tracking microservice running with database temporarily unavailable
**When** client sends GET /tasks/next (returns 500 in 230ms due to database error)
**Then** log entry written with ERROR level
**And** log contains fields: `{level: "error", method: "GET", path: "/tasks/next", status_code: 500, duration_ms: 230, error: "database connection failed", ...}`

### Scenario 7: Logs do not contain sensitive data
**Given** Task Tracking microservice running with structured logging
**When** client sends authenticated request with API key "secret-key-12345"
**Then** log entry does NOT contain full API key (sensitive data protection)
**And** log MAY contain api_key_prefix "secret-k" (first 8 characters only for debugging)

### Scenario 8: Log level configurable via environment variable
**Given** Task Tracking microservice started with LOG_LEVEL=error
**When** client sends GET /tasks/next (returns 200 OK)
**Then** no log entry written (INFO level suppressed, only ERROR level logged)
**When** client sends GET /tasks/next (returns 500)
**Then** log entry written with ERROR level

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 3 SP - SKIP threshold (below 3-5 SP CONSIDER range)
- **Developer Count:** Single backend developer
- **Domain Span:** Single domain (backend infrastructure - health check + logging middleware)
- **Complexity:** Low - standard HTTP health check pattern, standard logging middleware pattern
- **Uncertainty:** Low - well-established observability patterns (health check JSON response, structured logging)
- **Override Factors:** None apply (standard infrastructure concern)

**Conclusion:** Story is within single developer capacity. Health check endpoint is straightforward (database SELECT 1 query + JSON response). Logging middleware is standard HTTP middleware pattern. Task decomposition overhead not justified for 3 SP infrastructure story.

## Definition of Done
- [ ] GET /health endpoint implemented with database connectivity check
- [ ] Health check response time <100ms validated
- [ ] Structured logging middleware implemented (JSON format)
- [ ] Log level configuration implemented (environment variable LOG_LEVEL)
- [ ] Health check endpoint bypasses authentication (accessible to monitoring tools)
- [ ] Sensitive data protection implemented (no full API keys in logs)
- [ ] Unit tests written and passing (health check, logging middleware)
- [ ] All 8 acceptance criteria validated
- [ ] Code review completed
- [ ] Documentation updated (health check endpoint documentation, logging configuration guide)
- [ ] Product Owner acceptance obtained

## Additional Information
**Suggested Labels:** backend, go, observability, monitoring, logging
**Estimated Story Points:** 3
**Dependencies:**
- US-050 completed (task tracking REST API)
- US-052 completed (API authentication - health check must bypass auth)

**Related PRD Section:** PRD-006 §Non-Functional Requirements - Observability (lines 201-205), Availability (lines 191-193)

## Decisions Made

**All technical approaches clear from Implementation Research and PRD.**

Health check pattern standard (SELECT 1 database query, JSON response). Structured logging standard (logrus/zap/zerolog with JSON formatter). Middleware pattern standard (Go HTTP middleware with responseWriter wrapper). Log level configuration standard (environment variable with zerolog.ParseLevel()).
