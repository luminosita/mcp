# Feedback for Backlog Stories US-028 thru US-033

## General for all stories

### Open Questions
Convert Open Questions section into Decision Made section

### Hardcoded Paths in code snippets

**Issue:**

Paths must not be hardcoded. Examples of hardcoded paths

1.
```python
 file_path = Path(f"prompts/CLAUDE/python/patterns-{name}.md")
```
2.
```
allowed_templates = [
    "product-vision", "initiative", "epic", "prd", "hls",
    "backlog-story", "spike", "adr", "tech-spec", "implementation-task"
]
```

**Allowed URIs:**
1.
```python
return {"uri": f"mcp://resources/patterns/{name}", "content": content}
```
2.
```python
detail=f"Resource not found: mcp://resources/templates/{artifact_type}-template"
```

**Solution:**
Externalize all paths to configuration

**Rationale:**
Location of resource files can be changed and should not be hardcoded but configurable. URIs can remain in code since the actual routing path at the top of the corresponding method as a decorator (e.g., @app.get("/mcp/resources/templates/{artifact_type}-template")
)

## US-030

### Decisions Made:

Q1: MCP Resource URI Scheme

D1: Use nested URI per HLS-006 examples. Aligns with REST best practices and semantic resource naming.

Q2: Error Response Format

D2: Spike needed for this decision
---

## US-031

### URL correction

**Issue:**

URL for templates should be corrected.

**Solution:**

Instead of `mcp://resources/templates/{artifact-type}-template`, use `mcp://resources/templates/{artifact-type}`

Other URL naming corrections:
- product-vision-template -> vision
- initiative-template -> initiative
- epic-template -> epic
- prd-template -> prd
- hls-template -> hls
- backlog-story-template -> story
- spike-template -> spike
- adr-template -> adr
- tech-spec-template -> spec
- implementation-task-template -> task

## US-032

### Cache Configuration

All cache settings must be configurable (.env, .env.example). Add configuration if caching is active

### Cache key issue

**Issue:**

Wrong naming, see US-031 (Issue URL correction section above)
Cache key format: `resource:{type}:{name}` (e.g., `resource:patterns:core`, `resource:templates:prd-template`)

**Solution:**

Cache key format: `resource:{type}:{name}` (e.g., `resource:patterns:core`, `resource:templates:prd`)

Same as US-031 URL correction Solution section above

### Decisions Made:

Q1: Redis vs. In-Memory Caching
D1: Use Redis per Implementation Research recommendation.

Q2: Cache Invalidation Strategy
D2: Add explicit invalidation API

## US-033

### Decisions Made:

Q1: Acceptable Cache Miss Latency
D1: Validate with load testing. If combined p95 <100ms and cache hit rate >70%, individual cache miss latency >100ms is acceptable.

Q2: File Preloading Strategy
D2: Defer preloading unless profiling shows cold start latency >100ms. Caching (US-032) should handle warmup naturally.
