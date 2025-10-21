# CLAUDE.md - HTTP Framework Selection Guide

**← [Back to Go Development Guide](../CLAUDE.md)**

## Overview

This guide provides detailed comparison and selection criteria for Go HTTP frameworks based on 2025 research and production experience.

## Framework Comparison Matrix

| Feature | Gin | Chi | Fiber | net/http |
|---------|-----|-----|-------|----------|
| **Community** | 81k+ stars | 18k+ stars | 33k+ stars | stdlib |
| **stdlib-compatible** | ✅ Yes | ✅ Yes | ❌ No (fasthttp) | ✅ Native |
| **HTTP/2 Support** | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| **HTTP/3 Support** | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| **Middleware Ecosystem** | Excellent | Excellent | Limited | Excellent |
| **OpenTelemetry** | Out-of-box | Out-of-box | Manual | Out-of-box |
| **Prometheus** | Easy | Easy | Custom | Easy |
| **Learning Curve** | Low | Medium | Low | Medium |
| **Performance (req/sec)** | ~90k | ~100k | ~140k | ~100k |
| **Memory Footprint** | Low | Lowest | Very Low | Low |
| **Context Propagation** | stdlib | stdlib | Custom | stdlib |

## Detailed Framework Analysis

### Gin (Recommended Default)

**Best for**: Production applications, teams new to Go, rapid development

#### Advantages
- ✅ **Largest Community**: 81k+ GitHub stars, most contributors
- ✅ **stdlib-compatible**: Works with all net/http middleware
- ✅ **Express.js-like API**: Familiar for Node.js/JavaScript developers
- ✅ **Full HTTP/2 & HTTP/3**: Modern protocol support
- ✅ **Mature Ecosystem**: Auth, rate limiting, CORS, validation
- ✅ **Excellent Observability**: OpenTelemetry, Prometheus, Datadog, New Relic
- ✅ **Zero Config Tracing**: Standard context.Context propagation
- ✅ **Beginner Friendly**: Clear documentation, large Q&A community

#### Disadvantages
- ⚠️ Slightly slower than Chi/stdlib (not noticeable in most apps)
- ⚠️ More opinionated than Chi
- ⚠️ Larger binary size than Chi

#### When to Use Gin
- Default choice for most production applications
- Teams transitioning from Node.js/Express.js
- Projects requiring observability and monitoring
- Rapid prototyping and MVP development
- Microservices with standard tooling requirements

#### Example: Basic Gin Server
```go
package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
)

func main() {
	r := gin.Default() // Includes logger and recovery middleware

	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "healthy",
		})
	})

	r.Run(":8080")
}
```

---

### Chi (Most Idiomatic)

**Best for**: Idiomatic Go projects, minimal dependencies, stdlib purists

#### Advantages
- ✅ **Pure stdlib**: Zero external dependencies beyond net/http
- ✅ **Idiomatic Go**: Uses standard http.Handler interface
- ✅ **Minimal Abstractions**: Close to bare metal net/http
- ✅ **Composable Middleware**: Standard middleware chain pattern
- ✅ **Excellent Performance**: On par with stdlib net/http
- ✅ **Small Binary Size**: Minimal overhead
- ✅ **Full Compatibility**: Works with ANY net/http middleware

#### Disadvantages
- ⚠️ Requires more boilerplate than Gin
- ⚠️ No built-in JSON helpers (manual encoding/decoding)
- ⚠️ Smaller community than Gin
- ⚠️ More verbose error handling

#### When to Use Chi
- You prefer idiomatic Go over convenience
- Minimal dependencies are critical
- You want maximum flexibility
- Security/compliance requires stdlib-only
- Building libraries that others will extend

#### Example: Basic Chi Server
```go
package main

import (
	"encoding/json"
	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"net/http"
)

func main() {
	r := chi.NewRouter()
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)

	r.Get("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{
			"status": "healthy",
		})
	})

	http.ListenAndServe(":8080", r)
}
```

---

### Fiber (Maximum Performance)

**Best for**: High-throughput microservices, latency-critical applications

#### Advantages
- ✅ **Fastest Framework**: 30-70% faster than stdlib (benchmarks)
- ✅ **Zero Allocations**: Optimized memory management
- ✅ **Express.js API**: Familiar for Node.js developers
- ✅ **Low Memory Footprint**: Efficient resource usage

#### Disadvantages
- ❌ **NOT stdlib-compatible**: Built on fasthttp, not net/http
- ❌ **No HTTP/2**: Major limitation for modern services
- ❌ **Limited Middleware**: Fewer third-party options
- ❌ **Manual Observability**: OpenTelemetry requires custom setup
- ❌ **Custom Context**: Doesn't use stdlib context.Context
- ❌ **Integration Overhead**: Auth, tracing, metrics need adapters
- ❌ **Migration Difficulty**: Hard to switch to/from stdlib frameworks

#### When to Use Fiber
- Performance is THE critical factor (100k+ req/sec)
- Sub-millisecond latency requirements
- Resource-constrained environments (embedded, edge)
- You understand and accept fasthttp trade-offs
- Team has bandwidth to handle manual instrumentation

#### ⚠️ Important Caveats
**Do NOT use Fiber if you need:**
- HTTP/2 support (not available)
- Standard observability tools (requires manual setup)
- Easy integration with auth libraries (OAuth2, JWT)
- Fast onboarding (non-idiomatic patterns)
- Future flexibility (vendor lock-in to fasthttp)

#### Example: Basic Fiber Server
```go
package main

import (
	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	app.Get("/health", func(c *fiber.Ctx) error {
		return c.JSON(fiber.Map{
			"status": "healthy",
		})
	})

	app.Listen(":8080")
}
```

---

### net/http (stdlib)

**Best for**: Maximum control, learning Go, no dependencies

#### Advantages
- ✅ **Zero Dependencies**: Pure stdlib
- ✅ **Maximum Control**: Full control over every aspect
- ✅ **Educational**: Best for learning HTTP fundamentals
- ✅ **Long-term Stability**: Maintained by Go team

#### Disadvantages
- ⚠️ Most boilerplate code
- ⚠️ No routing beyond basic patterns
- ⚠️ Manual middleware composition
- ⚠️ Verbose error handling

#### When to Use net/http
- Learning Go and HTTP fundamentals
- Simple services with few routes
- Maximum control is required
- Building your own framework/router

---

## Decision Tree

```
Start: Need HTTP framework for Go project
│
├─ Performance THE critical factor? (100k+ req/sec)
│  └─ Yes → Consider Fiber (with caveats)
│  └─ No → Continue
│
├─ Minimal dependencies required? (stdlib-only)
│  └─ Yes → Use Chi
│  └─ No → Continue
│
├─ Team coming from Node.js/Express?
│  └─ Yes → Use Gin (familiar API)
│  └─ No → Continue
│
├─ Need observability out-of-box? (tracing, metrics)
│  └─ Yes → Use Gin
│  └─ No → Continue
│
├─ Prefer idiomatic Go patterns?
│  └─ Yes → Use Chi
│  └─ No → Use Gin
│
Default: Use Gin
```

## Performance Benchmarks (2025)

**Synthetic Benchmark** (Hello World, single endpoint):
```
Fiber:    ~140,000 req/sec
Chi:      ~100,000 req/sec
net/http: ~100,000 req/sec
Gin:      ~90,000 req/sec
```

**Real-World Impact**:
- For 99% of applications, the 10-40% performance difference is negligible
- Bottlenecks are typically database, external APIs, or business logic
- Observability, maintainability, and ecosystem matter more

## Observability Comparison

### OpenTelemetry Integration

**Gin** (Excellent):
```go
import "go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin/otelgin"

r := gin.New()
r.Use(otelgin.Middleware("my-service"))
```

**Chi** (Excellent):
```go
import "go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"

r := chi.NewRouter()
r.Use(func(next http.Handler) http.Handler {
    return otelhttp.NewHandler(next, "my-service")
})
```

**Fiber** (Manual):
```go
// Requires custom implementation
// No official OpenTelemetry middleware
// Must manually propagate context
```

## Migration Path

### Gin ↔ Chi (Easy)
Both are stdlib-compatible, migration is straightforward:
- Gin → Chi: Replace `gin.Context` with `http.ResponseWriter` and `*http.Request`
- Chi → Gin: Wrap handlers with Gin adapter

### Fiber ↔ Anything (Hard)
Fiber is not stdlib-compatible:
- Requires full rewrite of handlers
- Context propagation must be re-implemented
- Middleware must be replaced
- Testing infrastructure changes

## Recommendations by Use Case

### Startup/MVP
**Use Gin**: Fastest development, mature ecosystem, easy hiring

### Enterprise Production
**Use Gin or Chi**: Mature, observable, well-documented

### High-Frequency Trading / Edge Computing
**Use Fiber**: Only if performance is THE factor and you accept trade-offs

### Microservices
**Use Gin**: Standardized observability across services

### API Gateway
**Use Chi**: Minimal overhead, stdlib compatibility

### Learning Go
**Use Chi or net/http**: Most idiomatic, teaches fundamentals

## Conclusion

**Default Recommendation: Gin**

Gin provides the best balance of:
- Developer productivity
- Performance (good enough for 99% of apps)
- Ecosystem maturity
- stdlib compatibility
- Observability support

**Only deviate from Gin if:**
- You need absolute minimal dependencies (Chi)
- You have extreme performance requirements AND understand trade-offs (Fiber)
- You're building a framework or library (Chi or net/http)

---

**See Also**:
- [patterns-api]mcp://resources/patterns/go/patterns-api - REST API patterns with Gin
- [patterns-testing]mcp://resources/patterns/go/patterns-testing - Testing HTTP handlers
- [patterns-observability]mcp://resources/patterns/go/patterns-observability - Monitoring and tracing
