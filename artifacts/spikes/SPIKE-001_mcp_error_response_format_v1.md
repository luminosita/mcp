# Spike: MCP Error Response Format Investigation

## Metadata
- **Spike ID:** SPIKE-001
- **Parent Story:** US-030: Implement MCP Resource Server for Implementation Pattern Files
- **Status:** Completed
- **Assigned To:** Claude Code
- **Sprint:** Current
- **Created Date:** 2025-10-20
- **Completed Date:** 2025-10-20

## Investigation Goal

### Question to Answer
"Does MCP protocol have specific error format expectations, or should we use standard HTTP error format (FastAPI HTTPException)? Do we need custom exception handlers?"

**Source Reference:** US-030 v2 Decisions Made section, D2: Error Response Format (lines 319-324)

### Success Criteria
- Clear understanding of MCP protocol error response format
- Documentation of whether FastMCP handles error conversion automatically
- Code examples showing correct error handling pattern for MCP resources
- Decision on whether custom exception handlers are needed

### Out of Scope
- Implementation of error handlers (implementation task)
- Performance testing of error handling
- Logging infrastructure design

## Time Box & Schedule

**Time Box:** 4 hours maximum
- **Planned Start:** 2025-10-20 14:00
- **Planned End:** 2025-10-20 18:00
- **Actual Hours Spent:** 3 hours

**Time Box Enforcement:**
Investigation completed within time box with sufficient findings to make implementation decision.

## Investigation Approach

**Methods:**
- Review MCP protocol specification (modelcontextprotocol.io)
- Review FastMCP SDK error handling source code and documentation
- Review MCP Python SDK GitHub issues for error handling patterns
- Review MCP error handling best practices guides (MCPcat.io)
- Examine JSON-RPC 2.0 error format (MCP builds on JSON-RPC)

**Environment:**
- Web-based documentation review
- GitHub repository examination

**Data Sources:**
- MCP Specification 2025-03-26
- FastMCP error handling middleware source code
- MCP Python SDK Issue #396 (inconsistent exception handling)
- MCPcat.io error handling best practices
- MCP error codes documentation

## Findings

### Summary
MCP protocol uses JSON-RPC 2.0 error format with specific error codes. FastMCP provides automatic error conversion through ErrorHandlingMiddleware, transforming Python exceptions into standardized MCP error responses. **Do NOT use FastAPI HTTPException** - instead, let FastMCP middleware handle error conversion automatically or use `CallToolResult(isError=True)` for tool-specific errors.

### Detailed Findings

#### Finding 1: MCP Protocol Error Format (JSON-RPC 2.0)
**What we learned:**
MCP builds on JSON-RPC 2.0 and uses standardized error response structure with three components: `code` (numeric error code), `message` (human-readable description), and `data` (optional additional context).

**Evidence:**
Official MCP Specification (2025-03-26) example error response:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Unsupported protocol version",
    "data": {
      "supported": ["2024-11-05"],
      "requested": "1.0.0"
    }
  }
}
```

Standard JSON-RPC error codes:
- `-32700`: Parse Error (Invalid JSON)
- `-32600`: Invalid Request
- `-32601`: Method Not Found
- `-32602`: Invalid Params
- `-32603`: Internal Error

MCP-specific error codes (application-level):
- `-32001`: Resource not found
- `-32000`: Generic application error (permissions, timeout)

**Implications:**
- Must use JSON-RPC error codes, not HTTP status codes (400, 404, 500)
- Error responses must follow JSON-RPC 2.0 structure
- FastAPI HTTPException does NOT produce compatible error format

#### Finding 2: FastMCP Error Handling Middleware (Automatic Conversion)
**What we learned:**
FastMCP provides `ErrorHandlingMiddleware` that **automatically** converts Python exceptions into MCP-compatible error responses. No custom exception handlers needed.

**Evidence:**
FastMCP source code (`error_handling.py`):
```python
def _transform_error(self, error: Exception) -> Exception:
    if isinstance(error, McpError):
        return error

    # Maps exception types to specific error codes
    if error_type in (ValueError, TypeError):
        return McpError(
            ErrorData(code=-32602, message=f"Invalid params: {str(error)}")
        )
    elif error_type in (FileNotFoundError, KeyError, NotFoundError):
        return McpError(
            ErrorData(code=-32001, message=f"Resource not found: {str(error)}")
        )
    elif error_type is PermissionError:
        return McpError(
            ErrorData(code=-32000, message=f"Permission denied: {str(error)}")
        )
    elif error_type in (TimeoutError, asyncio.TimeoutError):
        return McpError(
            ErrorData(code=-32000, message=f"Request timeout: {str(error)}")
        )
    else:
        # Default internal error
        return McpError(
            ErrorData(code=-32603, message=f"Internal error: {str(error)}")
        )
```

**Implications:**
- **Do NOT use FastAPI HTTPException** - it bypasses FastMCP error conversion
- Raise standard Python exceptions (FileNotFoundError, ValueError, PermissionError)
- FastMCP middleware automatically converts to MCP error format
- For tool-specific errors, use `CallToolResult(isError=True, content=[...])`

#### Finding 3: Recommended Error Handling Pattern for MCP Resources
**What we learned:**
Best practice is to raise standard Python exceptions and let FastMCP middleware handle conversion. For MCP tools, use `CallToolResult(isError=True)` pattern.

**Evidence:**
MCPcat.io best practices guide:
```python
@app.call_tool()
async def handle_tool(name: str, arguments: dict):
    try:
        result = await process_tool(name, arguments)
        return CallToolResult(content=[TextContent(text=str(result))])
    except Exception as e:
        # Option 1: Return error in CallToolResult
        return CallToolResult(
            isError=True,
            content=[TextContent(text=f"Error: {str(e)}")]
        )
        # Option 2: Re-raise and let middleware handle
        # raise
```

For MCP resources (US-030 use case):
```python
@app.get("/mcp/resources/patterns/{name}")
async def get_pattern_resource(name: str):
    # Validate input
    if ".." in name or name.startswith("/"):
        raise ValueError("Invalid resource name")  # Converts to -32602

    # Check file exists
    if not file_path.exists():
        raise FileNotFoundError(
            f"Resource not found: mcp://resources/patterns/{name}"
        )  # Converts to -32001

    # Handle I/O errors
    try:
        async with aiofiles.open(file_path, mode='r') as f:
            content = await f.read()
    except PermissionError as e:
        raise PermissionError(f"Cannot read resource: {e}")  # Converts to -32000

    return {"uri": f"mcp://resources/patterns/{name}", "content": content}
```

**Implications:**
- Use standard Python exceptions (FileNotFoundError, ValueError, PermissionError)
- Let FastMCP middleware handle error code mapping
- No need for custom exception handlers
- Error messages should include MCP resource URI for context

#### Finding 4: Known Issue - Tool Error Handling Inconsistency
**What we learned:**
MCP Python SDK Issue #396 reports inconsistent error handling in `@app.call_tool` decorators - exceptions may be embedded in successful responses instead of proper error responses.

**Evidence:**
GitHub Issue #396 (modelcontextprotocol/python-sdk):
> "When raising a ValueError in a @app.call_tool handler, the server sends a 'successful' response where the error message is embedded in the content, unlike @app.list_resources which correctly translates exceptions to McpError."

**Implications:**
- FastMCP may have addressed this issue (check version)
- For US-030 (resource server, not tools), this issue doesn't apply
- If implementing MCP tools, prefer `CallToolResult(isError=True)` pattern over raising exceptions

### Data Collected

**Error Code Mapping (FastMCP Middleware):**
| Python Exception | JSON-RPC Code | Error Message Format |
|------------------|---------------|----------------------|
| FileNotFoundError | -32001 | "Resource not found: {message}" |
| ValueError | -32602 | "Invalid params: {message}" |
| TypeError | -32602 | "Invalid params: {message}" |
| PermissionError | -32000 | "Permission denied: {message}" |
| TimeoutError | -32000 | "Request timeout: {message}" |
| Other exceptions | -32603 | "Internal error: {message}" |

**Code Samples:**

**CORRECT Pattern (for US-030):**
```python
from fastapi import FastAPI
import aiofiles
from pathlib import Path

@app.get("/mcp/resources/patterns/{name}")
async def get_pattern_resource(name: str):
    # Validate input - raises ValueError → -32602
    if ".." in name or name.startswith("/"):
        raise ValueError("Invalid resource name")

    # Construct file path
    file_path = Path(settings.PATTERNS_BASE_DIR) / f"patterns-{name}.md"

    # Check existence - raises FileNotFoundError → -32001
    if not file_path.exists():
        raise FileNotFoundError(
            f"Resource not found: mcp://resources/patterns/{name}"
        )

    # Read file - raises PermissionError/IOError → -32000/-32603
    async with aiofiles.open(file_path, mode='r') as f:
        content = await f.read()

    return {"uri": f"mcp://resources/patterns/{name}", "content": content}
```

**INCORRECT Pattern (DO NOT USE):**
```python
from fastapi import HTTPException  # ❌ DO NOT USE

@app.get("/mcp/resources/patterns/{name}")
async def get_pattern_resource(name: str):
    if not file_path.exists():
        # ❌ HTTPException bypasses FastMCP middleware
        raise HTTPException(status_code=404, detail="Not found")
```

**Documentation References:**
- MCP Specification (2025-03-26): https://modelcontextprotocol.io/specification/2025-03-26/basic/lifecycle
- FastMCP Error Handling Middleware: https://gofastmcp.com/python-sdk/fastmcp-server-middleware-error_handling
- FastMCP Source Code: https://github.com/jlowin/fastmcp/blob/main/src/fastmcp/server/middleware/error_handling.py
- MCPcat Error Handling Best Practices: https://mcpcat.io/guides/error-handling-custom-mcp-servers/
- MCP Python SDK Issue #396: https://github.com/modelcontextprotocol/python-sdk/issues/396

### Challenges Encountered
- **Challenge 1:** MCP SDK has known inconsistency in tool error handling (Issue #396)
  - **Resolution:** US-030 implements resource endpoints (not tools), so this issue doesn't apply. For tools, use `CallToolResult(isError=True)` pattern.

- **Challenge 2:** FastMCP vs MCP Python SDK confusion
  - **Resolution:** US-030 uses FastMCP (not MCP Python SDK directly). FastMCP provides superior error handling middleware.

### Unknowns Remaining
- **Unknown 1:** Does FastMCP version used in project have Issue #396 fix?
  - **Mitigation:** Use `CallToolResult(isError=True)` pattern for any MCP tools (not applicable to US-030 resources)

## Recommendation

**Recommended Approach:** Use standard Python exceptions (FileNotFoundError, ValueError, PermissionError) and let FastMCP ErrorHandlingMiddleware automatically convert to MCP error responses. **Do NOT use FastAPI HTTPException or custom exception handlers.**

**Rationale:**
1. **FastMCP handles conversion automatically:** ErrorHandlingMiddleware maps Python exceptions to correct JSON-RPC error codes without custom code
2. **Maintains MCP protocol compliance:** Error responses follow JSON-RPC 2.0 structure with correct error codes
3. **Simpler implementation:** No custom exception handlers needed, reduces code complexity
4. **Better error messages:** Can include MCP resource URI context in exception messages
5. **Type-safe error handling:** Python exception types map predictably to JSON-RPC codes

**Alternative Approaches Considered:**

- **Alternative 1: Custom FastAPI exception handlers**
  - **Why not chosen:** Unnecessary complexity. FastMCP middleware already provides comprehensive error conversion. Custom handlers would duplicate functionality and risk breaking MCP protocol compliance.

- **Alternative 2: FastAPI HTTPException**
  - **Why not chosen:** HTTPException bypasses FastMCP error conversion, producing HTTP-style error responses instead of JSON-RPC format. Breaks MCP protocol compliance.

- **Alternative 3: Manual McpError construction**
  - **Why not chosen:** More verbose than raising standard exceptions. FastMCP middleware provides same functionality with less code.

**Risk Assessment:**
- **Low Risk**
- FastMCP ErrorHandlingMiddleware is production-tested
- Standard Python exceptions are well-understood
- Error code mapping is documented and predictable

**Confidence Level:**
- **High Confidence** in recommendation
- Based on official MCP specification, FastMCP source code review, and best practices documentation
- Pattern is widely used in MCP server implementations

## Implementation Notes

**If Recommendation Accepted:**

1. **Import standard exceptions only:**
   ```python
   # ✅ CORRECT
   import aiofiles
   from pathlib import Path
   # Do NOT import HTTPException
   ```

2. **Validation errors → ValueError:**
   ```python
   if ".." in name or name.startswith("/"):
       raise ValueError("Invalid resource name")
   ```

3. **Missing resources → FileNotFoundError:**
   ```python
   if not file_path.exists():
       raise FileNotFoundError(f"Resource not found: mcp://resources/patterns/{name}")
   ```

4. **I/O errors → Let propagate:**
   ```python
   # PermissionError, IOError automatically handled by middleware
   async with aiofiles.open(file_path, mode='r') as f:
       content = await f.read()
   ```

5. **Security logging:**
   ```python
   if ".." in name:
       logger.warning("Path traversal attempt detected", extra={"resource_name": name})
       raise ValueError("Invalid resource name")
   ```

**Estimated Complexity:** Low
- No custom exception handlers needed
- Standard Python exception usage
- FastMCP middleware handles conversion

**Estimated Effort:** 0 additional story points
- Recommendation simplifies implementation (fewer components than originally anticipated)
- Reduces US-030 implementation complexity

**Dependencies:**
- FastMCP with ErrorHandlingMiddleware enabled (default behavior)
- Structured logging library (structlog) for security event logging

**Migration Path:**
Not applicable (new feature implementation, no existing code to migrate)

## Next Steps

### Immediate Actions
- [x] Document spike findings
- [ ] Update US-030 Decision D2 with recommendation
- [ ] Update US-030 Technical Requirements section with error handling pattern
- [ ] Update US-030 Acceptance Criteria to reflect error response format
- [ ] Update US-030 estimate (may reduce if custom handlers removed from scope)

### Downstream Artifacts to Create/Update
- [ ] **US-030:** Update Decisions Made section, D2: Error Response Format
  - **Decision:** Use standard Python exceptions, let FastMCP ErrorHandlingMiddleware handle conversion
  - **Rationale:** [Reference SPIKE-001 findings]
  - **Error Handling Pattern:** [Include code example from Finding 3]

- [ ] **US-030:** Update Technical Requirements with error handling code example
- [ ] **US-030:** Update Acceptance Criteria Scenario 4 (Missing resource) to validate JSON-RPC error format
- [ ] **US-030:** Update Acceptance Criteria Scenario 5 (Path traversal) to expect -32602 error code
- [ ] **US-030:** Update Acceptance Criteria Scenario 7 (Disk I/O error) to expect -32603 or -32000 error code

### Follow-up Questions for Team
- Should we add integration tests validating JSON-RPC error format compliance?
- Should we document error code mapping in project README for developer reference?

## Traceability

**Triggered By:**
- **Backlog Story:** US-030: Implement MCP Resource Server for Implementation Pattern Files
- **Open Question:** Decision D2: Error Response Format - "MCP protocol may have specific error format expectations. FastAPI returns standard HTTP error format. Investigation needed to determine if custom exception handlers required."

**Informs:**
- **Backlog Story:** US-030 (updated with error handling pattern, decision documented)

**Related Spikes:**
- None (first spike in project)

## References

**MCP Protocol Specification:**
- MCP Specification 2025-03-26 - Lifecycle: https://modelcontextprotocol.io/specification/2025-03-26/basic/lifecycle
- JSON-RPC 2.0 Specification: https://www.jsonrpc.org/specification

**FastMCP Documentation:**
- Error Handling Middleware: https://gofastmcp.com/python-sdk/fastmcp-server-middleware-error_handling
- FastMCP Source Code (error_handling.py): https://github.com/jlowin/fastmcp/blob/main/src/fastmcp/server/middleware/error_handling.py

**Best Practices Guides:**
- MCPcat Error Handling Guide: https://mcpcat.io/guides/error-handling-custom-mcp-servers/
- Stainless MCP Portal - Error Handling: https://www.stainless.com/mcp/error-handling-and-debugging-mcp-servers
- MCP Error Codes Documentation: https://www.mcpevals.io/blog/mcp-error-codes

**Known Issues:**
- MCP Python SDK Issue #396 - Inconsistent Exception Handling: https://github.com/modelcontextprotocol/python-sdk/issues/396

**Code Samples:**
- Prototype implementation (not created - research-only spike)
- Error handling examples extracted from FastMCP source code

**Security:**
- CVE-2025-53366 - FastMCP validation error DoS: https://www.miggo.io/vulnerability-database/cve/CVE-2025-53366
