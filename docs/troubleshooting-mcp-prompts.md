# MCP Prompt Troubleshooting Guide

This guide helps diagnose and resolve common errors when loading generator prompts via the MCP Server.

## Overview

The MCP Server exposes artifact generators as prompts. When the `/generate` command executes, it:

1. **Primary path**: Call MCP prompt `mcp://prompts/generator/{artifact_name}`
2. **Fallback path**: If MCP Server unavailable, read local file `prompts/{artifact_name}-generator.xml`

## Common Error Scenarios

### 1. Connection Error - MCP Server Unreachable

**Symptom:**
```
❌ ERROR: Cannot connect to MCP Server at http://localhost:3000
```

**Cause:** MCP Server is not running, wrong URL, or network issues.

**Troubleshooting Steps:**

1. **Verify MCP Server is running:**
   ```bash
   curl http://localhost:3000/health
   ```
   Expected response: `{"status": "healthy", ...}`

2. **Check server URL configuration:**
   - Verify `.mcp/config.json` has correct server URL
   - Default: `http://localhost:3000`

3. **Verify network connectivity:**
   ```bash
   ping localhost
   ```

4. **Check server logs:**
   ```bash
   # If running via task dev
   tail -f logs/mcp_server.log
   ```

**Resolution:**
- Start MCP Server: `uv run task dev`
- Update server URL in config if needed
- Fallback: Command automatically falls back to local file

---

### 2. Prompt Not Found - 404 Error

**Symptom:**
```
❌ ERROR: Prompt not found: mcp://prompts/generator/invalid-artifact
```

**Cause:** Artifact name incorrect or generator not exposed as MCP prompt.

**Troubleshooting Steps:**

1. **Verify prompt name is correct:**
   - Valid artifact names: `epic`, `prd`, `hls`, `backlog-story`, `spike`, `adr`, `tech-spec`, `implementation-task`
   - Note: Use artifact name (e.g., `epic`), not generator filename (e.g., `epic-generator`)

2. **List available prompts:**
   ```bash
   curl http://localhost:3000/mcp/prompts
   ```
   Returns: `["epic", "prd", "hls", ...]`

3. **Check MCP Server version:**
   ```bash
   curl http://localhost:3000/health
   ```
   Verify version includes prompt registration feature

**Resolution:**
- Fix artifact name in `/generate` command
- Verify generator XML file exists in `prompts/` directory
- Fallback: Command automatically falls back to local file

---

### 3. Server Error - 5xx Response

**Symptom:**
```
❌ ERROR: MCP Server error 500 for mcp://prompts/generator/epic
Server response: Internal server error...
```

**Cause:** Server-side failure (code bug, missing file, configuration error).

**Troubleshooting Steps:**

1. **Check MCP Server logs for error details:**
   ```bash
   tail -f logs/mcp_server.log | grep ERROR
   ```

2. **Verify generator file exists and is valid:**
   ```bash
   ls -la prompts/epic-generator.xml
   xmllint --noout prompts/epic-generator.xml  # Validate XML
   ```

3. **Restart MCP Server:**
   ```bash
   # Stop server (Ctrl+C), then restart
   uv run task dev
   ```

4. **Check server resource usage:**
   - Server may be overloaded
   - Monitor CPU/memory: `top` or `htop`

**Resolution:**
- Fix underlying server error (check logs)
- Wait a few minutes and retry (transient failure)
- Fallback: Command automatically falls back to local file

---

### 4. Malformed Content - Invalid XML

**Symptom:**
```
❌ ERROR: Invalid generator XML from mcp://prompts/generator/spike
XML parsing error: mismatched tag at line 42
```

**Cause:** Generator XML file is corrupted or has syntax errors.

**Troubleshooting Steps:**

1. **Validate XML syntax:**
   ```bash
   xmllint --noout prompts/spike-generator.xml
   ```
   Fix syntax errors shown in output

2. **Check file encoding:**
   ```bash
   file prompts/spike-generator.xml
   ```
   Should be: `UTF-8 Unicode text`

3. **Compare with working generator:**
   ```bash
   # Use known-good generator as template
   diff prompts/epic-generator.xml prompts/spike-generator.xml
   ```

4. **Report issue to MCP Server maintainer:**
   - If file is correct but MCP returns malformed content
   - May indicate server-side corruption or encoding issue

**Resolution:**
- Fix XML syntax errors in generator file
- Re-validate with `xmllint`
- Fallback: Command automatically falls back to local file

---

### 5. Timeout Error - Request Too Slow

**Symptom:**
```
❌ ERROR: MCP Server request timed out after 5.0s for mcp://prompts/generator/prd
```

**Cause:** Server overloaded, slow disk I/O, or network latency.

**Troubleshooting Steps:**

1. **Check server performance:**
   ```bash
   # Monitor CPU and memory usage
   top -p $(pgrep -f "mcp_server")
   ```

2. **Verify disk I/O is healthy:**
   ```bash
   # Check disk usage
   df -h
   # Check I/O wait
   iostat -x 1 5
   ```

3. **Check network latency:**
   ```bash
   # Measure round-trip time
   curl -w "@curl-format.txt" -o /dev/null -s http://localhost:3000/health
   ```

4. **Review server cache settings:**
   - Prompts are cached with 5-minute TTL
   - Cache miss = slower response (disk I/O)
   - Check cache hit ratio in logs

**Resolution:**
- Wait for server load to decrease
- Increase timeout in client configuration (if available)
- Fallback: Command automatically falls back to local file after retry

---

## Retry Logic

The MCP prompt loading implements automatic retry with exponential backoff:

- **Retries:** 3 attempts
- **Backoff delays:** 100ms, 200ms, 400ms
- **Total retry time:** ~700ms maximum
- **Retryable errors:**
  - Connection errors (server unreachable)
  - Timeout errors (slow response)
  - 5xx server errors (transient failures)

**Non-retryable errors** (immediate fallback):
- 404 Prompt Not Found (retry won't help)
- 400 Bad Request (input validation error)
- Malformed XML (server or file corruption)

### Example: Retry Success

```
⚠️  WARNING: Retrying after failure (attempt 1/3)
    Error: Connection refused
    Backoff: 100ms

⚠️  WARNING: Retrying after failure (attempt 2/3)
    Error: Connection refused
    Backoff: 200ms

✅ SUCCESS: Retry succeeded (attempt 3/3)
    Generator loaded successfully
```

### Example: Retry Exhaustion

```
⚠️  WARNING: Retrying after failure (attempt 1/3)
    Error: Connection refused
    Backoff: 100ms

⚠️  WARNING: Retrying after failure (attempt 2/3)
    Error: Connection refused
    Backoff: 200ms

⚠️  WARNING: Retrying after failure (attempt 3/3)
    Error: Connection refused
    Backoff: 400ms

❌ ERROR: Retry exhausted after 3 attempts
    Falling back to local file: prompts/epic-generator.xml

✅ Fallback successful, continuing execution
```

---

## Fallback Behavior

When MCP prompt loading fails after retries:

1. **Log warning** with error details
2. **Attempt fallback** to local file: `prompts/{artifact_name}-generator.xml`
3. **Continue execution** if fallback succeeds
4. **Fail with error** if fallback also fails

### Fallback File Location

```
prompts/
├── product-vision-generator.xml
├── initiative-generator.xml
├── epic-generator.xml
├── prd-generator.xml
├── high-level-user-story-generator.xml
├── backlog-story-generator.xml
├── spike-generator.xml
├── adr-generator.xml
├── tech-spec-generator.xml
└── implementation-task-generator.xml
```

### Example: Fallback Success

```
⚠️  MCP Server unavailable, falling back to local file
    MCP Prompt: mcp://prompts/generator/epic
    Fallback File: prompts/epic-generator.xml
    Status: Fallback successful ✅

✅ Generator loaded from local file
    Continuing execution...
```

### Example: Fallback Failure

```
❌ ERROR: Generator not available via MCP or local file
    MCP Prompt: mcp://prompts/generator/product-vision (404 Not Found)
    Local File: prompts/product-vision-generator.xml (File not found)

Action Required:
    - Create generator file: prompts/product-vision-generator.xml
    - Verify generator is registered with MCP Server
    - Check task dependencies in TODO.md
```

---

## Structured Logging

All MCP prompt errors are logged with structured JSON for debugging:

```json
{
  "timestamp": "2025-10-21T12:00:00Z",
  "level": "error",
  "event": "mcp_prompt_error",
  "error_type": "PromptConnectionError",
  "message": "Cannot connect to MCP Server at http://localhost:3000",
  "prompt_uri": "mcp://prompts/generator/epic",
  "context": {
    "generator_name": "epic",
    "server_url": "http://localhost:3000",
    "retry_count": 3
  },
  "troubleshooting": "1. Verify MCP Server is running: curl http://localhost:3000/health\n2. Check server URL in .mcp/config.json\n..."
}
```

### Query Logs by Error Type

```bash
# Filter by error type
cat logs/mcp_server.log | jq 'select(.error_type == "PromptConnectionError")'

# Count errors by type
cat logs/mcp_server.log | jq -r '.error_type' | sort | uniq -c

# Find recent errors (last hour)
cat logs/mcp_server.log | jq 'select(.timestamp > "2025-10-21T11:00:00Z")'
```

---

## Performance Metrics

### Target Latencies (p95)

- **MCP prompt call:** <500ms
  - Cache hit: <10ms
  - Cache miss: <100ms
- **Retry with backoff:** <1 second (3 retries × ~300ms average)
- **Fallback to local file:** <50ms

### Monitoring

Check MCP Server logs for performance metrics:

```json
{
  "event": "generator_prompt_loaded",
  "artifact_name": "epic",
  "content_length": 12876,
  "cache_stats": {
    "size": 5,
    "hits": 142,
    "misses": 8,
    "hit_rate": 0.947
  }
}
```

---

## Getting Help

If issues persist after troubleshooting:

1. **Check MCP Server logs:**
   ```bash
   tail -n 100 logs/mcp_server.log
   ```

2. **Verify system health:**
   ```bash
   curl http://localhost:3000/health
   ```

3. **Report issue with logs:**
   - Include error message
   - Include relevant log entries (structured JSON)
   - Include steps to reproduce

4. **Contact Support:**
   - GitHub Issues: https://github.com/your-org/mcp-server/issues
   - Include MCP Server version from `/health` endpoint
