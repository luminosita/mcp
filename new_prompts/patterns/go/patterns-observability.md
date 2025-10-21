# CLAUDE.md - Observability Patterns

**← [Back to Go Development Guide]mcp://resources/patterns/go/patterns-core**

## Overview

This document covers comprehensive observability patterns including structured logging, metrics collection, distributed tracing, and health checks for Go applications.

## Observability Stack

- **Logging**: slog (Go 1.21+), zerolog, or zap
- **Metrics**: Prometheus
- **Tracing**: OpenTelemetry
- **Visualization**: Grafana
- **APM**: Jaeger, Tempo, or Zipkin

## Structured Logging with slog

### Logger Setup

```go
package logger

import (
	"context"
	"log/slog"
	"os"
)

func NewLogger(level string, format string) *slog.Logger {
	var logLevel slog.Level
	switch level {
	case "debug":
		logLevel = slog.LevelDebug
	case "info":
		logLevel = slog.LevelInfo
	case "warn":
		logLevel = slog.LevelWarn
	case "error":
		logLevel = slog.LevelError
	default:
		logLevel = slog.LevelInfo
	}

	opts := &slog.HandlerOptions{
		Level: logLevel,
		AddSource: true,
	}

	var handler slog.Handler
	if format == "json" {
		handler = slog.NewJSONHandler(os.Stdout, opts)
	} else {
		handler = slog.NewTextHandler(os.Stdout, opts)
	}

	return slog.New(handler)
}

func WithRequestID(ctx context.Context, requestID string) context.Context {
	logger := slog.Default().With("request_id", requestID)
	return context.WithValue(ctx, loggerKey, logger)
}

func FromContext(ctx context.Context) *slog.Logger {
	if logger, ok := ctx.Value(loggerKey).(*slog.Logger); ok {
		return logger
	}
	return slog.Default()
}

type loggerKeyType string

const loggerKey loggerKeyType = "logger"
```

### Logging Middleware

```go
package middleware

import (
	"log/slog"
	"net/http"
	"time"

	"github.com/google/uuid"
)

type responseWriter struct {
	http.ResponseWriter
	status int
	bytes  int
}

func (rw *responseWriter) WriteHeader(status int) {
	rw.status = status
	rw.ResponseWriter.WriteHeader(status)
}

func (rw *responseWriter) Write(b []byte) (int, error) {
	rw.bytes = len(b)
	return rw.ResponseWriter.Write(b)
}

func LoggingMiddleware(logger *slog.Logger) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()
			requestID := uuid.New().String()

			w.Header().Set("X-Request-ID", requestID)

			rw := &responseWriter{ResponseWriter: w, status: http.StatusOK}

			ctx := logger.WithRequestID(r.Context(), requestID)

			logger.InfoContext(ctx, "request started",
				slog.String("method", r.Method),
				slog.String("path", r.URL.Path),
				slog.String("remote_addr", r.RemoteAddr),
				slog.String("user_agent", r.UserAgent()),
			)

			next.ServeHTTP(rw, r.WithContext(ctx))

			duration := time.Since(start)

			logger.InfoContext(ctx, "request completed",
				slog.Int("status", rw.status),
				slog.Int("bytes", rw.bytes),
				slog.Duration("duration", duration),
			)
		})
	}
}
```

### Application Logging Patterns

```go
package application

import (
	"context"
	"log/slog"
)

type UserUseCase struct {
	userRepo domain.UserRepository
	logger   *slog.Logger
}

func (uc *UserUseCase) Create(ctx context.Context, dto *CreateUserDTO) (*domain.User, error) {
	logger := logger.FromContext(ctx)

	logger.Info("creating user",
		slog.String("email", dto.Email),
		slog.String("username", dto.Username),
	)

	user, err := domain.NewUser(dto.Email, dto.Username, dto.Password)
	if err != nil {
		logger.Error("failed to create user entity",
			slog.String("error", err.Error()),
		)
		return nil, err
	}

	if err := uc.userRepo.Create(ctx, user); err != nil {
		logger.Error("failed to save user",
			slog.String("user_id", user.ID),
			slog.String("error", err.Error()),
		)
		return nil, err
	}

	logger.Info("user created successfully",
		slog.String("user_id", user.ID),
	)

	return user, nil
}
```

## Prometheus Metrics

### Metrics Setup

```go
package metrics

import (
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

type Metrics struct {
	RequestsTotal   *prometheus.CounterVec
	RequestDuration *prometheus.HistogramVec
	RequestSize     *prometheus.SummaryVec
	ResponseSize    *prometheus.SummaryVec
	DBQueryDuration *prometheus.HistogramVec
	ActiveUsers     prometheus.Gauge
}

func NewMetrics(reg prometheus.Registerer) *Metrics {
	return &Metrics{
		RequestsTotal: promauto.With(reg).NewCounterVec(
			prometheus.CounterOpts{
				Name: "http_requests_total",
				Help: "Total number of HTTP requests",
			},
			[]string{"method", "path", "status"},
		),
		RequestDuration: promauto.With(reg).NewHistogramVec(
			prometheus.HistogramOpts{
				Name:    "http_request_duration_seconds",
				Help:    "HTTP request duration in seconds",
				Buckets: prometheus.DefBuckets,
			},
			[]string{"method", "path", "status"},
		),
		RequestSize: promauto.With(reg).NewSummaryVec(
			prometheus.SummaryOpts{
				Name: "http_request_size_bytes",
				Help: "HTTP request size in bytes",
			},
			[]string{"method", "path"},
		),
		ResponseSize: promauto.With(reg).NewSummaryVec(
			prometheus.SummaryOpts{
				Name: "http_response_size_bytes",
				Help: "HTTP response size in bytes",
			},
			[]string{"method", "path"},
		),
		DBQueryDuration: promauto.With(reg).NewHistogramVec(
			prometheus.HistogramOpts{
				Name:    "db_query_duration_seconds",
				Help:    "Database query duration in seconds",
				Buckets: []float64{.001, .005, .01, .025, .05, .1, .25, .5, 1},
			},
			[]string{"query", "status"},
		),
		ActiveUsers: promauto.With(reg).NewGauge(
			prometheus.GaugeOpts{
				Name: "active_users_total",
				Help: "Number of currently active users",
			},
		),
	}
}
```

### Metrics Middleware

```go
package middleware

import (
	"net/http"
	"strconv"
	"time"

	"github.com/prometheus/client_golang/prometheus"
)

type MetricsMiddleware struct {
	metrics *metrics.Metrics
}

func NewMetricsMiddleware(m *metrics.Metrics) *MetricsMiddleware {
	return &MetricsMiddleware{metrics: m}
}

func (m *MetricsMiddleware) Handler(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()

		rw := &responseWriter{ResponseWriter: w, status: http.StatusOK}

		next.ServeHTTP(rw, r)

		duration := time.Since(start).Seconds()
		status := strconv.Itoa(rw.status)

		m.metrics.RequestsTotal.WithLabelValues(
			r.Method,
			r.URL.Path,
			status,
		).Inc()

		m.metrics.RequestDuration.WithLabelValues(
			r.Method,
			r.URL.Path,
			status,
		).Observe(duration)

		m.metrics.RequestSize.WithLabelValues(
			r.Method,
			r.URL.Path,
		).Observe(float64(r.ContentLength))

		m.metrics.ResponseSize.WithLabelValues(
			r.Method,
			r.URL.Path,
		).Observe(float64(rw.bytes))
	})
}
```

### Database Metrics

```go
package repositories

import (
	"context"
	"time"
)

type metricsUserRepository struct {
	repo    UserRepository
	metrics *metrics.Metrics
}

func (r *metricsUserRepository) FindByID(ctx context.Context, id string) (*domain.User, error) {
	start := time.Now()

	user, err := r.repo.FindByID(ctx, id)

	duration := time.Since(start).Seconds()
	status := "success"
	if err != nil {
		status = "error"
	}

	r.metrics.DBQueryDuration.WithLabelValues(
		"find_user_by_id",
		status,
	).Observe(duration)

	return user, err
}
```

### Metrics Endpoint

```go
package main

import (
	"net/http"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

func main() {
	reg := prometheus.NewRegistry()
	metrics := metrics.NewMetrics(reg)

	metricsHandler := promhttp.HandlerFor(reg, promhttp.HandlerOpts{
		EnableOpenMetrics: true,
	})

	http.Handle("/metrics", metricsHandler)

	http.ListenAndServe(":9090", nil)
}
```

## OpenTelemetry Tracing

### Tracer Setup

```go
package tracing

import (
	"context"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/exporters/jaeger"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.4.0"
)

func InitTracer(serviceName, jaegerEndpoint string) (*sdktrace.TracerProvider, error) {
	exporter, err := jaeger.New(
		jaeger.WithCollectorEndpoint(jaeger.WithEndpoint(jaegerEndpoint)),
	)
	if err != nil {
		return nil, err
	}

	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exporter),
		sdktrace.WithResource(resource.NewWithAttributes(
			semconv.SchemaURL,
			semconv.ServiceNameKey.String(serviceName),
		)),
	)

	otel.SetTracerProvider(tp)

	return tp, nil
}
```

### Tracing Middleware

```go
package middleware

import (
	"net/http"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/codes"
	"go.opentelemetry.io/otel/trace"
)

func TracingMiddleware(serviceName string) func(http.Handler) http.Handler {
	tracer := otel.Tracer(serviceName)

	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			ctx, span := tracer.Start(r.Context(), r.URL.Path,
				trace.WithAttributes(
					attribute.String("http.method", r.Method),
					attribute.String("http.url", r.URL.String()),
					attribute.String("http.remote_addr", r.RemoteAddr),
				),
			)
			defer span.End()

			rw := &responseWriter{ResponseWriter: w, status: http.StatusOK}

			next.ServeHTTP(rw, r.WithContext(ctx))

			span.SetAttributes(
				attribute.Int("http.status_code", rw.status),
				attribute.Int("http.response_size", rw.bytes),
			)

			if rw.status >= 400 {
				span.SetStatus(codes.Error, http.StatusText(rw.status))
			}
		})
	}
}
```

### Application Tracing

```go
package application

import (
	"context"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/trace"
)

type UserUseCase struct {
	userRepo domain.UserRepository
	tracer   trace.Tracer
}

func NewUserUseCase(userRepo domain.UserRepository) *UserUseCase {
	return &UserUseCase{
		userRepo: userRepo,
		tracer:   otel.Tracer("user-usecase"),
	}
}

func (uc *UserUseCase) Create(ctx context.Context, dto *CreateUserDTO) (*domain.User, error) {
	ctx, span := uc.tracer.Start(ctx, "UserUseCase.Create",
		trace.WithAttributes(
			attribute.String("email", dto.Email),
			attribute.String("username", dto.Username),
		),
	)
	defer span.End()

	user, err := domain.NewUser(dto.Email, dto.Username, dto.Password)
	if err != nil {
		span.RecordError(err)
		return nil, err
	}

	ctx, repoSpan := uc.tracer.Start(ctx, "UserRepository.Create")
	err = uc.userRepo.Create(ctx, user)
	repoSpan.End()

	if err != nil {
		span.RecordError(err)
		return nil, err
	}

	span.SetAttributes(attribute.String("user_id", user.ID))

	return user, nil
}
```

### Database Tracing

```go
package repositories

import (
	"context"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/trace"
)

type tracingUserRepository struct {
	repo   UserRepository
	tracer trace.Tracer
}

func (r *tracingUserRepository) FindByID(ctx context.Context, id string) (*domain.User, error) {
	ctx, span := r.tracer.Start(ctx, "UserRepository.FindByID",
		trace.WithAttributes(
			attribute.String("user_id", id),
		),
	)
	defer span.End()

	user, err := r.repo.FindByID(ctx, id)
	if err != nil {
		span.RecordError(err)
		return nil, err
	}

	return user, nil
}
```

## Health Checks

### Health Check Handler

```go
package handlers

import (
	"context"
	"database/sql"
	"encoding/json"
	"net/http"
	"time"
)

type HealthHandler struct {
	db *sql.DB
}

type HealthResponse struct {
	Status    string            `json:"status"`
	Timestamp time.Time         `json:"timestamp"`
	Checks    map[string]string `json:"checks"`
}

func (h *HealthHandler) Liveness(w http.ResponseWriter, r *http.Request) {
	response := HealthResponse{
		Status:    "ok",
		Timestamp: time.Now(),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func (h *HealthHandler) Readiness(w http.ResponseWriter, r *http.Request) {
	ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
	defer cancel()

	checks := make(map[string]string)

	if err := h.db.PingContext(ctx); err != nil {
		checks["database"] = "unhealthy"
		h.respondUnhealthy(w, checks)
		return
	}
	checks["database"] = "healthy"

	response := HealthResponse{
		Status:    "ok",
		Timestamp: time.Now(),
		Checks:    checks,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func (h *HealthHandler) respondUnhealthy(w http.ResponseWriter, checks map[string]string) {
	response := HealthResponse{
		Status:    "unhealthy",
		Timestamp: time.Now(),
		Checks:    checks,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusServiceUnavailable)
	json.NewEncoder(w).Encode(response)
}
```

### Advanced Health Checks

```go
package health

import (
	"context"
	"time"
)

type Checker interface {
	Check(ctx context.Context) error
}

type DatabaseChecker struct {
	db *sql.DB
}

func (c *DatabaseChecker) Check(ctx context.Context) error {
	return c.db.PingContext(ctx)
}

type RedisChecker struct {
	client *redis.Client
}

func (c *RedisChecker) Check(ctx context.Context) error {
	return c.client.Ping(ctx).Err()
}

type HealthChecker struct {
	checkers map[string]Checker
	timeout  time.Duration
}

func NewHealthChecker(timeout time.Duration) *HealthChecker {
	return &HealthChecker{
		checkers: make(map[string]Checker),
		timeout:  timeout,
	}
}

func (h *HealthChecker) AddChecker(name string, checker Checker) {
	h.checkers[name] = checker
}

func (h *HealthChecker) Check(ctx context.Context) map[string]string {
	ctx, cancel := context.WithTimeout(ctx, h.timeout)
	defer cancel()

	results := make(map[string]string)

	for name, checker := range h.checkers {
		if err := checker.Check(ctx); err != nil {
			results[name] = err.Error()
		} else {
			results[name] = "healthy"
		}
	}

	return results
}
```

## Correlation IDs

### Correlation ID Middleware

```go
package middleware

import (
	"context"
	"net/http"

	"github.com/google/uuid"
)

const (
	CorrelationIDHeader = "X-Correlation-ID"
	correlationIDKey    = "correlation_id"
)

func CorrelationIDMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		correlationID := r.Header.Get(CorrelationIDHeader)
		if correlationID == "" {
			correlationID = uuid.New().String()
		}

		w.Header().Set(CorrelationIDHeader, correlationID)

		ctx := context.WithValue(r.Context(), correlationIDKey, correlationID)

		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

func GetCorrelationID(ctx context.Context) string {
	if id, ok := ctx.Value(correlationIDKey).(string); ok {
		return id
	}
	return ""
}
```

## Best Practices

### ✅ DO

- **Use structured logging** (slog, zerolog, zap) for better searchability
- **Include request IDs** in all logs for request tracing
- **Log at appropriate levels** (debug, info, warn, error)
- **Add context to logs** with relevant attributes
- **Use metrics for quantitative data** (counts, durations, sizes)
- **Create custom metrics** for business-specific events
- **Instrument all external calls** (database, HTTP, gRPC)
- **Use distributed tracing** for multi-service architectures
- **Implement both liveness and readiness** health checks
- **Include dependency health** in readiness checks
- **Use correlation IDs** to track requests across services
- **Set appropriate metric buckets** based on actual data distribution
- **Monitor error rates** and set up alerting

### ❌ DON'T

- **Don't log sensitive information** (passwords, tokens, PII)
- **Don't use print statements** for production logging
- **Don't log at debug level** in production by default
- **Don't create unbounded metric labels** (cardinality explosion)
- **Don't ignore trace sampling** - sample in high-traffic scenarios
- **Don't block on logging** - use async logging for performance
- **Don't mix metrics with logs** - use appropriate tools for each
- **Don't skip health checks** in Kubernetes/Docker deployments
- **Don't forget to close spans** in tracing
- **Don't hardcode service names** - use configuration

## Grafana Dashboard Example

### Prometheus Queries

```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Database query duration
histogram_quantile(0.99, rate(db_query_duration_seconds_bucket[5m]))

# Active users
active_users_total
```

## Alerting Rules

### prometheus-rules.yml

```yaml
groups:
  - name: api_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} for {{ $labels.path }}"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "P95 latency is {{ $value }}s for {{ $labels.path }}"

      - alert: DatabaseDown
        expr: up{job="database"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database is down"
          description: "Database has been down for more than 1 minute"
```

## References

- [slog Documentation](https://pkg.go.dev/log/slog)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [OpenTelemetry Go](https://opentelemetry.io/docs/instrumentation/go/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)
