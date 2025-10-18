# User Story: Implement Resource Caching with TTL

## Metadata
- **Story ID:** US-032
- **Title:** Implement Resource Caching with Time-To-Live (TTL)
- **Type:** Feature
- **Status:** Draft
- **Version:** v2 (Applied feedback from US-028-033_v1_comments.md - cache config, cache key fixes)
- **Priority:** High (performance optimization enabling <10ms cache hit latency)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-006 (MCP Resources Migration)
- **Functional Requirements Covered:** FR-20
- **Informed By Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Functional Requirements - FR-20: MCP Server SHALL implement resource caching with TTL
- **Functional Requirements Coverage:**
  - **FR-20:** MCP Server SHALL implement resource caching with TTL

**Parent High-Level Story:** [HLS-006: MCP Resources Migration]
- **Link:** `/artifacts/hls/HLS-006_mcp_resources_migration_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 5: Implement Resource Caching with TTL

## User Story
As a Claude Code user, I want frequently accessed resources cached in memory, so that subsequent requests have <10ms latency instead of 50ms disk I/O overhead.

## Description
Resource server (US-030, US-031) currently loads files from disk on every request, incurring ~50ms latency for file I/O. Since resources (patterns, templates, SDLC core) are static content that changes infrequently (weekly/monthly), caching provides significant performance improvement without staleness concerns.

This story implements in-memory caching with Time-To-Live (TTL) to reduce resource loading latency:
1. **Cache-Aside Pattern:** Check cache first, load from disk on miss, store in cache
2. **TTL-Based Expiration:** Cache entries expire after 5 minutes (configurable)
3. **Automatic Invalidation:** Stale entries automatically reloaded from disk
4. **Cache Hit Metrics:** Prometheus metrics track cache hit rate for monitoring
5. **Memory Bounded:** Cache size limited to 1000 resources (per NFR-Scalability-03)

After implementation, frequently accessed resources (e.g., sdlc-core.md, patterns-core.md, prd-template.xml) will have <10ms latency on cache hits, meeting PRD-006 performance target.

## Implementation Research References

**Primary Research Document:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

**Technical Patterns Applied:**
- **§2.4: Caching Layer - Redis:** Use Redis for distributed caching across multiple MCP Server instances (ref: Implementation Research §2.4 - Caching Layer: Redis 7+)
- **§2.4: Cache-Aside Pattern Implementation:** Implement get_or_fetch pattern with automatic TTL expiration (ref: Implementation Research §2.4 - Cache-Aside Pattern Implementation, lines 262-311)
- **§6.2: Prometheus Metrics:** Instrument cache hit/miss metrics for observability (ref: Implementation Research §6.2 - Prometheus Metrics, lines 812-885)

**Anti-Patterns Avoided:**
- **§8.2: Storing State in Server Instance Variables:** Use Redis for caching instead of in-memory dict, enabling horizontal scalability (ref: Implementation Research §8.2 - Anti-Pattern 2, lines 1223-1261)

**Performance Considerations:**
- Cache hit latency: <10ms (Redis in-memory lookup)
- Cache miss latency: ~50ms (disk I/O + Redis write)
- Target cache hit rate: >70% (per HLS-006 success criteria)

## Functional Requirements
1. Cache stores resource content in memory with unique cache key (e.g., `resource:patterns:core`)
2. Cache key format: `resource:{type}:{name}` (e.g., `resource:patterns:core`, `resource:templates:prd`) - uses simplified template names per US-031
3. TTL set to 5 minutes (300 seconds) - configurable via environment variable
4. Resource loading logic implements cache-aside pattern:
   - Check cache first
   - If cache hit, return cached content immediately (<10ms)
   - If cache miss, load from disk, store in cache with TTL, return content
5. Cache invalidation on TTL expiration (automatic)
6. Cache size bounded to 1000 resources maximum (LRU eviction if exceeded)
7. Prometheus metrics track cache hit rate, cache size, cache latency
8. Cache keys include resource version or file modification time for freshness

## Non-Functional Requirements
- **Performance:** Cache hit latency <10ms (p95)
- **Cache Hit Rate:** >70% for frequently accessed resources (measured over 1 hour window)
- **Memory Usage:** Cache size bounded to prevent memory exhaustion
- **Scalability:** Cache shared across multiple MCP Server instances (Redis-based, not in-process)
- **Observability:** Prometheus metrics expose cache hit rate, size, latency distributions
- **Configuration:** All cache settings configurable via .env file (REDIS_URL, CACHE_TTL, CACHE_MAX_SIZE)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** When implementing resource caching, follow established implementation standards. Supplement with story-specific technical guidance.

**References to Implementation Standards:**
- **prompts/CLAUDE/python/patterns-tooling.md:** Use Taskfile commands for development workflow
- **prompts/CLAUDE/python/patterns-testing.md:** Follow testing patterns (80% coverage minimum, async test support)
- **prompts/CLAUDE/python/patterns-typing.md:** Apply type hints (strict mode, Pydantic models for cache configuration)
- **prompts/CLAUDE/python/patterns-architecture.md:** Follow project structure, modularity patterns
- **prompts/CLAUDE/python/patterns-validation.md:** Input validation for cache configuration

### Implementation Guidance

**Story-Specific Technical Approach:**

1. **Redis Cache Service Implementation:**
   ```python
   import redis.asyncio as redis
   from typing import Optional, Callable
   import json
   from datetime import datetime

   class ResourceCacheService:
       def __init__(self, redis_url: str, ttl_seconds: int = 300):
           self.redis = redis.from_url(redis_url, decode_responses=True)
           self.ttl_seconds = ttl_seconds

       async def get_or_fetch(
           self,
           cache_key: str,
           fetch_func: Callable,
           file_path: str
       ) -> str:
           """Cache-aside pattern with automatic fetch on miss"""
           # Try cache first
           cached = await self.redis.get(cache_key)
           if cached:
               # Cache hit - return immediately
               return json.loads(cached)["content"]

           # Cache miss - fetch from source
           content = await fetch_func(file_path)

           # Store in cache with TTL
           await self.redis.setex(
               cache_key,
               self.ttl_seconds,
               json.dumps({
                   "content": content,
                   "cached_at": datetime.utcnow().isoformat(),
                   "file_path": file_path
               })
           )

           return content

       async def invalidate_pattern(self, pattern: str):
           """Invalidates all keys matching pattern"""
           keys = await self.redis.keys(pattern)
           if keys:
               await self.redis.delete(*keys)

       async def get_cache_size(self) -> int:
           """Returns number of cached resources"""
           return await self.redis.dbsize()
   ```

2. **Integrate Caching into Resource Handlers:**
   ```python
   from fastapi import FastAPI
   import aiofiles

   cache = ResourceCacheService(settings.REDIS_URL, ttl_seconds=settings.CACHE_TTL)

   async def load_file_from_disk(file_path: str) -> str:
       """Loads file content from disk (cache miss)"""
       async with aiofiles.open(file_path, mode='r') as f:
           return await f.read()

   @app.get("/mcp/resources/patterns/{name}")
   async def get_pattern_resource(name: str):
       cache_key = f"resource:patterns:{name}"
       file_path = Path(f"prompts/CLAUDE/python/patterns-{name}.md")

       content = await cache.get_or_fetch(
           cache_key,
           load_file_from_disk,
           str(file_path)
       )

       return {"uri": f"mcp://resources/patterns/{name}", "content": content}
   ```

3. **Prometheus Metrics Instrumentation:**
   ```python
   from prometheus_client import Counter, Gauge, Histogram

   cache_hits_total = Counter(
       'mcp_resource_cache_hits_total',
       'Total number of cache hits',
       ['resource_type']
   )

   cache_misses_total = Counter(
       'mcp_resource_cache_misses_total',
       'Total number of cache misses',
       ['resource_type']
   )

   cache_size = Gauge(
       'mcp_resource_cache_size',
       'Number of cached resources'
   )

   cache_latency_seconds = Histogram(
       'mcp_resource_cache_latency_seconds',
       'Cache lookup latency',
       ['cache_result'],  # hit or miss
       buckets=[0.001, 0.005, 0.010, 0.050, 0.100]
   )
   ```

4. **Testing Strategy:**
   - Unit tests: Validate cache-aside logic, TTL expiration behavior
   - Integration tests: Verify cache hit/miss scenarios, Redis integration
   - Performance tests: Measure cache hit latency (<10ms), cache miss latency

### Technical Tasks
- [ ] Implement ResourceCacheService with Redis client (cache-aside pattern)
- [ ] Integrate caching into pattern resource handler
- [ ] Integrate caching into template resource handler
- [ ] Integrate caching into SDLC core resource handler
- [ ] Implement cache key generation (format: `resource:{type}:{name}`)
- [ ] Add Prometheus metrics for cache hits, misses, size, latency
- [ ] Add environment variable for TTL configuration (default: 300 seconds)
- [ ] Implement cache size monitoring (bounded to 1000 resources)
- [ ] Write unit tests for cache-aside logic (80% coverage)
- [ ] Write integration tests for cache hit/miss scenarios
- [ ] Write performance tests measuring cache latency

## Acceptance Criteria

### Scenario 1: Cache hit provides low latency
**Given** resource previously loaded and cached
**When** Claude Code requests same resource within TTL window (5 minutes)
**Then** server returns cached content
**And** response latency <10ms (p95 - cache hit)
**And** cache_hits_total metric incremented

### Scenario 2: Cache miss loads from disk
**Given** resource not in cache OR TTL expired
**When** Claude Code requests resource
**Then** server loads content from disk
**And** content stored in cache with TTL
**And** response latency ~50ms (cache miss + disk I/O)
**And** cache_misses_total metric incremented

### Scenario 3: TTL expiration triggers reload
**Given** resource cached 5 minutes ago
**When** Claude Code requests resource after TTL expiration
**Then** server reloads content from disk (cache miss behavior)
**And** new cache entry created with fresh TTL

### Scenario 4: Cache hit rate >70%
**Given** MCP Server under normal load (multiple projects requesting resources)
**When** measured over 1 hour window
**Then** cache hit rate exceeds 70% (cache_hits / (cache_hits + cache_misses))
**And** frequently accessed resources (sdlc-core, patterns-core, common templates) have >90% hit rate

### Scenario 5: Cache size bounded
**Given** cache storing many resources
**When** cache size approaches 1000 resources
**Then** LRU eviction removes least recently used entries
**And** cache size remains ≤1000 resources
**And** cache_size metric reflects current count

### Scenario 6: Prometheus metrics available
**Given** MCP Server running with caching enabled
**When** I query Prometheus metrics endpoint
**Then** metrics include:
  - mcp_resource_cache_hits_total (counter by resource_type)
  - mcp_resource_cache_misses_total (counter by resource_type)
  - mcp_resource_cache_size (gauge)
  - mcp_resource_cache_latency_seconds (histogram by cache_result)

### Scenario 7: Cache invalidation works
**Given** resource cached
**When** framework maintainer deploys updated MCP Server with changed resource file
**Then** cache invalidation API or TTL expiration reloads updated content
**And** subsequent requests receive new content (not stale)

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 5 SP (at threshold - CONSIDER territory)
- **Developer Count:** Single developer (extends US-030/US-031 implementation)
- **Domain Span:** Single domain (backend caching layer)
- **Complexity:** Moderate - well-defined caching pattern (cache-aside) with clear implementation example from Implementation Research §2.4
- **Uncertainty:** Low - Implementation Research provides complete code example for cache-aside pattern, Redis integration, and metrics
- **Override Factors:** None - not cross-domain, not security-critical, caching is orthogonal concern to business logic

Per SDLC Section 11.6 Decision Matrix: "3-5 SP, single dev, familiar domain → CONSIDER". Since Implementation Research §2.4 provides comprehensive cache-aside implementation example and developer is familiar with codebase from US-030/US-031, overhead of task decomposition is not justified.

**Note:** If Redis integration complexity proves higher than estimated, reconsider task decomposition.

## Definition of Done
- [ ] ResourceCacheService implemented with Redis client
- [ ] Cache-aside pattern integrated into all resource handlers (patterns, templates, SDLC core)
- [ ] Cache key generation implemented (`resource:{type}:{name}` format)
- [ ] TTL configuration via environment variable (default: 300 seconds)
- [ ] Prometheus metrics instrumented (cache hits, misses, size, latency)
- [ ] Cache size bounded to 1000 resources (LRU eviction)
- [ ] Unit tests written and passing (80% coverage)
- [ ] Integration tests passing (cache hit/miss scenarios, Redis integration)
- [ ] Performance tests validate cache hit latency <10ms
- [ ] Manual testing: Verify cache hit rate >70% under normal load
- [ ] Product Owner approval obtained

## Additional Information
**Suggested Labels:** backend, performance, caching, observability
**Estimated Story Points:** 5
**Dependencies:**
- **Depends On:** US-030 (patterns resource server must exist)
- **Depends On:** US-031 (templates resource server must exist)
- **Blocks:** US-033 (performance optimization depends on caching baseline)

**Related PRD Section:** PRD-006 §Functional Requirements - FR-20

## Decisions Made

### D1: Redis vs. In-Memory Caching
**Decision:** Use Redis per Implementation Research recommendation.

**Rationale:** Enables horizontal scaling in production without refactoring. Redis operational overhead minimal with managed Redis service (e.g., AWS ElastiCache). Implementation Research §2.4 recommends Redis for distributed caching to support multiple MCP Server instances.

**Configuration:** REDIS_URL configurable via .env file.

### D2: Cache Invalidation Strategy
**Decision:** Add explicit invalidation API in addition to TTL-based expiration.

**Rationale:** TTL-based expiration (5 minutes configurable via CACHE_TTL) provides automatic freshness. Explicit invalidation API enables immediate propagation of critical framework updates without waiting for TTL expiration.

**Configuration:** CACHE_TTL configurable via .env file (default: 300 seconds).

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-006_mcp_resources_migration_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md` (§2.4 Caching Layer - Redis, §6.2 Prometheus Metrics, §8.2 Anti-Pattern 2)
