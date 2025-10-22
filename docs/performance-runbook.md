# Resource Loading Performance Runbook

**Document Version:** 1.0
**Last Updated:** 2025-10-21
**User Story:** US-033 - Resource Loading Performance Optimization
**Owner:** Development Team

---

## Overview

This runbook documents performance benchmarking methodology, baseline results, and optimization strategies for MCP resource loading endpoints.

**Performance Target:** <100ms p95 latency for resource loading (end-to-end request → response)

**Scope:** All MCP resource endpoints
- `/mcp/resources/patterns/{name}` - Implementation pattern files
- `/mcp/resources/sdlc/core` - SDLC framework core
- `/mcp/resources/templates/{artifact_type}` - Artifact templates

---

## Quick Start

### Prerequisites
- MCP server running: `task dev` (in separate terminal)
- Redis cache running: `task db:start` (or separate Redis instance)
- Dependencies installed: `uv sync --all-extras`

### Running Performance Tests

```bash
# Full load test (100 users, 5 minutes) - production validation
task perf:test

# Quick load test (30 users, 1 minute) - development/CI
task perf:test:quick

# Profile server performance (60 seconds, flame graph)
task perf:profile

# Run complete benchmark suite with documentation
task perf:benchmark

# Clean performance artifacts
task perf:clean
```

---

## Performance Testing Tools

### 1. Locust Load Testing

**Purpose:** Simulate concurrent users requesting resources under realistic load.

**Configuration:**
- **Users:** 100 concurrent users (simulates 10 projects × 10 concurrent operations)
- **Spawn Rate:** 10 users/second
- **Duration:** 5 minutes
- **Access Pattern:** Realistic (frequent SDLC core, varied patterns, occasional templates)

**Load Distribution:**
- 50% - SDLC core resource (high cache hit rate)
- 40% - Pattern files (moderate cache hit rate)
- 20% - Template files (variable cache hit rate)
- 10% - Template listing (metadata endpoint)

**Command:**
```bash
# Headless mode with results export
uv run locust -f locustfile.py --headless \
  --users 100 --spawn-rate 10 --run-time 5m \
  --csv=perf-results --html=perf-report.html \
  --host http://localhost:8000

# Interactive web UI mode
uv run locust -f locustfile.py
# Then open: http://localhost:8089
```

**Key Metrics:**
- **Requests/sec:** Throughput (target: >500 req/s)
- **Response Time p50:** Median latency (target: <50ms)
- **Response Time p95:** 95th percentile (target: <100ms)
- **Response Time p99:** 99th percentile (target: <200ms)
- **Failure Rate:** Error percentage (target: 0%)

### 2. py-spy Profiling

**Purpose:** Identify bottlenecks in resource loading code path.

**Configuration:**
- **Duration:** 60 seconds
- **Sampling Rate:** 100 Hz (samples per second)
- **Output:** Flame graph (SVG)

**Command:**
```bash
# Auto-detect server PID and profile
task perf:profile

# Manual profiling
PID=$(pgrep -f "uvicorn.*mcp_server.main:app" | head -1)
uv run py-spy record -o profile.svg --pid $PID --duration 60 --rate 100
```

**Analysis:**
1. Open `profile.svg` in browser
2. Look for wide horizontal bars (time-consuming functions)
3. Focus on:
   - File I/O operations (`aiofiles.open`, `read`)
   - Redis cache operations (`redis.get`, `redis.setex`)
   - JSON serialization/deserialization
   - Path validation and resolution

**Common Bottlenecks:**
- **File I/O:** Slow disk reads (>20ms) → Consider SSD or file preloading
- **Cache lookup:** Redis network latency (>5ms) → Check Redis connection pool settings
- **JSON serialization:** Large file serialization (>10ms) → Consider compression or caching serialized data

### 3. Prometheus Metrics

**Purpose:** Real-time monitoring of latency distributions.

**Metrics:**
- `mcp_resource_loading_latency_seconds` - End-to-end latency histogram
  - Labels: `resource_type` (patterns, templates, sdlc), `cache_result` (hit, miss)
  - Buckets: 10ms, 50ms, 100ms, 200ms, 500ms, 1s

- `mcp_resource_cache_latency_seconds` - Cache lookup latency histogram
  - Labels: `cache_result` (hit, miss)
  - Buckets: 1ms, 5ms, 10ms, 50ms, 100ms

**Querying Metrics:**
```bash
# Access Prometheus metrics endpoint
curl http://localhost:8000/metrics | grep mcp_resource

# Example queries (requires Prometheus server):
# P95 latency for pattern resources (cache hit)
histogram_quantile(0.95, mcp_resource_loading_latency_seconds{resource_type="patterns",cache_result="hit"})

# P95 latency for pattern resources (cache miss)
histogram_quantile(0.95, mcp_resource_loading_latency_seconds{resource_type="patterns",cache_result="miss"})

# Combined p95 latency (all resources)
histogram_quantile(0.95, sum(rate(mcp_resource_loading_latency_seconds_bucket[5m])) by (le))
```

---

## Baseline Performance

**Environment:**
- **Hardware:** [Document your hardware specs]
- **OS:** macOS Darwin 25.0.0
- **Python:** 3.11
- **Redis:** Local instance (localhost:6379)
- **Cache TTL:** 300 seconds (5 minutes)

**Test Configuration:**
- **Users:** 100 concurrent
- **Duration:** 5 minutes
- **Total Requests:** [To be filled after benchmarking]
- **RPS:** [To be filled after benchmarking]

### Expected Results (Cache Warm)

| Resource Type | Cache Hit Rate | p50 Latency | p95 Latency | p99 Latency |
|---------------|----------------|-------------|-------------|-------------|
| SDLC Core     | >90%          | <10ms       | <15ms       | <30ms       |
| Patterns      | >70%          | <15ms       | <30ms       | <60ms       |
| Templates     | >50%          | <20ms       | <50ms       | <100ms      |
| **Combined**  | **>70%**      | **<15ms**   | **<50ms**   | **<100ms**  |

### Expected Results (Cache Cold Start)

| Resource Type | p50 Latency | p95 Latency | p99 Latency |
|---------------|-------------|-------------|-------------|
| SDLC Core     | <30ms       | <60ms       | <100ms      |
| Patterns      | <40ms       | <80ms       | <150ms      |
| Templates     | <50ms       | <100ms      | <200ms      |
| **Combined**  | **<40ms**   | **<80ms**   | **<150ms**  |

---

## Optimization Strategies

### Implemented Optimizations

#### 1. Async File I/O (US-030)
**Implementation:** `aiofiles` library for non-blocking file reads.

**Impact:**
- Prevents thread blocking during disk I/O
- Enables concurrent request processing
- Expected latency reduction: 20-30% under load

**Code Reference:** `src/mcp_server/api/routes/resources.py:113-114`

#### 2. Redis Caching with TTL (US-032)
**Implementation:** Cache-aside pattern with 300-second TTL.

**Impact:**
- Cache hit latency: <10ms (vs ~50ms cache miss)
- Reduced disk I/O by 70-90% after warmup
- Expected latency reduction: 80% for frequently accessed resources

**Code Reference:** `src/mcp_server/services/cache.py`

**Cache Key Format:**
- Patterns: `resource:patterns:{language}:{name}`
- Templates: `resource:templates:{artifact_type}`
- SDLC: `resource:sdlc:core`

#### 3. Path Traversal Protection (US-030, US-031)
**Implementation:** Input validation and `Path.resolve().relative_to()` checks.

**Impact:**
- Security: Prevents unauthorized file access
- Performance: Validation adds <1ms overhead
- No significant performance impact

**Code Reference:** `src/mcp_server/api/routes/resources.py:99-109`

### Potential Future Optimizations

#### 1. File Preloading at Startup
**Decision:** Deferred (per Decision D2 in US-033)

**Rationale:**
- Current cache warmup via TTL is sufficient
- Preloading adds startup time and memory usage
- Only implement if cold start latency >100ms

**Implementation (if needed):**
```python
async def preload_frequently_accessed_resources():
    """Preload SDLC core and common patterns at startup."""
    resources = [
        ("sdlc/core", None),
        ("patterns/core", "python"),
        ("patterns/tooling", "python"),
    ]
    for resource, language in resources:
        await get_pattern_resource(resource, language)
```

#### 2. Content Compression (gzip)
**Trigger:** If any resource >100KB and latency >100ms

**Expected Impact:**
- Reduce transfer time by 70-80%
- Add compression overhead: 5-10ms
- Net benefit for large files only

**Implementation:**
- Use `gzip` middleware or `Content-Encoding: gzip` response header
- Compress files >10KB

#### 3. Redis Connection Pooling
**Status:** Already implemented (default Redis client behavior)

**Configuration:** Check `redis.asyncio.from_url` connection pool settings if latency >5ms

#### 4. HTTP/2 Server Push
**Trigger:** If client requests multiple resources sequentially

**Expected Impact:**
- Reduce round-trip latency for multi-resource loads
- Requires HTTP/2 client support

---

## Troubleshooting

### Issue: p95 Latency >100ms

**Diagnosis:**
1. Check cache hit rate: `curl http://localhost:8000/metrics | grep cache_hits`
   - If <50%: Increase cache TTL or verify Redis is running
2. Profile server: `task perf:profile`
   - Look for slow file I/O or JSON serialization
3. Check disk I/O: `iostat -x 1`
   - If disk utilization >80%: Consider SSD or file preloading

**Solutions:**
- **Low cache hit rate:** Increase TTL from 300s to 600s or 900s
- **Slow disk I/O:** Migrate to SSD or implement file preloading
- **Redis latency:** Check Redis connection (should be localhost, <1ms)

### Issue: High p99 Latency (>200ms)

**Diagnosis:**
1. Check outliers in Locust report: Look for 99th percentile spike
2. Profile during load test: `task perf:profile` (while `task perf:test` running)
3. Check Redis eviction: `redis-cli info stats | grep evicted_keys`
   - If >0: Increase Redis memory limit

**Solutions:**
- **Garbage collection pauses:** Tune Python GC settings
- **Redis eviction:** Increase `maxmemory` in Redis config
- **Network latency:** Ensure Redis on localhost (not remote)

### Issue: Failure Rate >0%

**Diagnosis:**
1. Check error logs: `docker logs mcp-server` or application logs
2. Check Locust failure report: Look for specific HTTP error codes
3. Verify file permissions: `ls -la prompts/CLAUDE/python/`

**Solutions:**
- **404 errors:** Verify all resource files exist
- **403 errors:** Check file permissions (should be readable)
- **500 errors:** Check application logs for exceptions

---

## CI/CD Integration

### Quick Performance Check

Add to CI/CD pipeline for regression detection:

```yaml
# .github/workflows/ci.yml (example)
- name: Performance smoke test
  run: |
    task dev &
    sleep 5  # Wait for server startup
    task perf:test:quick
    if [ $? -ne 0 ]; then
      echo "Performance regression detected"
      exit 1
    fi
```

**Acceptance Criteria:**
- Quick load test (30 users, 1 minute) completes without errors
- p95 latency <100ms
- Failure rate 0%

---

## Prometheus Query Examples

```promql
# P50 latency for all resources
histogram_quantile(0.50, sum(rate(mcp_resource_loading_latency_seconds_bucket[5m])) by (le))

# P95 latency for patterns (cache hit vs miss)
histogram_quantile(0.95, rate(mcp_resource_loading_latency_seconds_bucket{resource_type="patterns"}[5m])) by (cache_result)

# P99 latency for all resources
histogram_quantile(0.99, sum(rate(mcp_resource_loading_latency_seconds_bucket[5m])) by (le))

# Cache hit rate percentage
sum(rate(mcp_resource_cache_hits_total[5m]))
/
(sum(rate(mcp_resource_cache_hits_total[5m])) + sum(rate(mcp_resource_cache_misses_total[5m])))
* 100

# Request rate (requests/second)
sum(rate(mcp_resource_loading_latency_seconds_count[5m]))
```

---

## Appendix: Locust Test Scenarios

### Full Load Test (Production Validation)
```bash
uv run locust -f locustfile.py --headless \
  --users 100 --spawn-rate 10 --run-time 5m \
  --csv=prod-results --html=prod-report.html \
  --host http://localhost:8000
```

### Quick Load Test (Development/CI)
```bash
uv run locust -f locustfile.py --headless \
  --users 30 --spawn-rate 5 --run-time 1m \
  --csv=dev-results --host http://localhost:8000
```

### Stress Test (Find Breaking Point)
```bash
uv run locust -f locustfile.py --headless \
  --users 500 --spawn-rate 50 --run-time 10m \
  --csv=stress-results --html=stress-report.html \
  --host http://localhost:8000
```

### Warmup Test (Prime Cache)
```bash
uv run locust -f locustfile.py --headless \
  --users 10 --spawn-rate 5 --run-time 30s \
  --host http://localhost:8000
```

---

## Version History

- **v1.0 (2025-10-21):** Initial performance runbook (US-033)
  - Documented testing methodology
  - Baseline performance targets
  - Optimization strategies
  - Troubleshooting guide

---

## Related Documents

- **User Story:** `/artifacts/backlog_stories/US-033_resource_loading_performance_optimization_v2.md`
- **Parent HLS:** `/artifacts/hls/HLS-006_mcp_resources_migration_v2.md`
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md` (§6.2 Prometheus Metrics, §6.3 Distributed Tracing)
