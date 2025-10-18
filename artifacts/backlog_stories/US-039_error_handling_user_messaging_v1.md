# User Story: Error Handling and User Messaging

## Metadata
- **Story ID:** US-039
- **Title:** Error Handling and User Messaging for MCP Prompt Migration
- **Type:** Feature
- **Status:** Backlog
- **Priority:** High - improves user experience and reduces support burden
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-007 (MCP Prompts - Generators Migration)
- **Functional Requirements Covered:** FR-05 (implicit - error handling), NFR-Reliability-01
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration v3]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Requirements - FR-05 (error handling), NFR-Reliability-01
- **Functional Requirements Coverage:**
  - **FR-05 (implicit):** MCP prompts must handle errors gracefully (missing prompt, malformed XML, connection failures)
  - **NFR-Reliability-01:** MCP Server SHALL implement retry logic for transient failures (3 retries with exponential backoff: 100ms, 200ms, 400ms)

**Parent High-Level Story:** [HLS-007: MCP Prompts - Generators Migration]
- **Link:** `/artifacts/hls/HLS-007_mcp_prompts_generators_migration_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 5

## User Story
As a Developer, I want clear, actionable error messages when generator execution fails (MCP Server unreachable, prompt not found, invalid content), so that I can quickly diagnose and resolve issues without Tech Lead assistance.

## Description
The MCP prompt migration introduces new failure modes (MCP Server unreachable, prompt not found, malformed response, authentication failures). This story implements comprehensive error handling with user-friendly messages, retry logic for transient failures, and actionable troubleshooting guidance.

**Current State:** Local file approach has simple error messages ("File not found: prompts/epic-generator.xml"). MCP approach needs richer error context (connection failures, server errors, retry exhaustion).

**Desired State:** Errors classified by type (connection, prompt not found, server error, malformed content), clear user messages with troubleshooting steps, automatic retry for transient failures, structured logging for debugging.

**Business Value:** Reduces support burden (developers self-serve troubleshooting), improves adoption confidence (clear error messages reduce frustration), enables faster issue resolution (structured logs aid debugging).

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§6.1: Structured Logging:** Use structured logging (JSON format) for error details (ref: Implementation Research §6.1 lines 872-919)
- **§8.2 Anti-Pattern 2: Synchronous Blocking Calls:** Implement retry logic with exponential backoff for transient failures

**Anti-Patterns Avoided:**
- **§8.3: Error Handling:** Avoid generic "Error occurred" messages - provide specific error type, context, and troubleshooting guidance

**Performance Considerations:**
- Retry logic adds latency (3 retries × backoff = ~700ms worst case), acceptable for transient failure recovery
- Per PRD-006 NFR-Reliability-01: 3 retries with exponential backoff (100ms, 200ms, 400ms)

## Functional Requirements
- Classify MCP prompt errors into categories: Connection Error, Prompt Not Found, Server Error, Malformed Content, Timeout, Authentication Failed
- Display user-friendly error messages with troubleshooting guidance for each category
- Implement retry logic for transient failures (connection errors, timeouts, 5xx server errors)
- Log structured error details for debugging (error type, prompt URI, MCP Server URL, retry count, response body)
- Provide fallback guidance (e.g., "Falling back to local file: prompts/epic-generator.xml")
- Document common error scenarios in troubleshooting guide

## Non-Functional Requirements
- **Usability:** Error messages clear to developers unfamiliar with MCP protocol
- **Reliability:** Retry logic recovers from transient failures ≥80% of the time (per PRD-006 NFR-Reliability-01)
- **Observability:** Structured logs enable rapid debugging of MCP Server issues
- **Performance:** Retry logic completes within 1 second for 3 retries (per exponential backoff schedule)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story implements error handling patterns. Reference error handling standards.

### Implementation Guidance

**Error Classification and User Messages:**

```python
class MCPPromptError(Exception):
    """Base class for MCP prompt errors"""
    def __init__(self, message: str, prompt_uri: str, troubleshooting: str):
        self.message = message
        self.prompt_uri = prompt_uri
        self.troubleshooting = troubleshooting
        super().__init__(self.message)

class ConnectionError(MCPPromptError):
    """MCP Server unreachable"""
    def __init__(self, prompt_uri: str, server_url: str):
        super().__init__(
            message=f"Cannot connect to MCP Server at {server_url}",
            prompt_uri=prompt_uri,
            troubleshooting=(
                "Troubleshooting steps:\n"
                "1. Verify MCP Server is running: curl {server_url}/health\n"
                "2. Check server URL in .mcp/config.json\n"
                "3. Verify network connectivity\n"
                "4. Falling back to local file: prompts/{generator_name}-generator.xml"
            )
        )

class PromptNotFoundError(MCPPromptError):
    """Prompt does not exist on MCP Server"""
    def __init__(self, prompt_uri: str):
        super().__init__(
            message=f"Prompt not found: {prompt_uri}",
            prompt_uri=prompt_uri,
            troubleshooting=(
                "Troubleshooting steps:\n"
                "1. Verify prompt name is correct (available prompts: epic, prd, hls, backlog-story, etc.)\n"
                "2. Check MCP Server version (generator may not be exposed yet)\n"
                "3. List available prompts: curl {server_url}/mcp/prompts\n"
                "4. Falling back to local file: prompts/{generator_name}-generator.xml"
            )
        )

class ServerError(MCPPromptError):
    """MCP Server returned 5xx error"""
    def __init__(self, prompt_uri: str, status_code: int, response_body: str):
        super().__init__(
            message=f"MCP Server error {status_code} for {prompt_uri}",
            prompt_uri=prompt_uri,
            troubleshooting=(
                f"Troubleshooting steps:\n"
                f"1. Check MCP Server logs for error details\n"
                f"2. Server response: {response_body[:200]}\n"
                f"3. Retry in a few minutes (server may be temporarily overloaded)\n"
                f"4. Falling back to local file: prompts/{{generator_name}}-generator.xml"
            )
        )

class MalformedContentError(MCPPromptError):
    """MCP Server returned invalid XML content"""
    def __init__(self, prompt_uri: str, parse_error: str):
        super().__init__(
            message=f"Invalid generator XML from {prompt_uri}",
            prompt_uri=prompt_uri,
            troubleshooting=(
                f"Troubleshooting steps:\n"
                f"1. XML parsing error: {parse_error}\n"
                f"2. Report issue to MCP Server maintainer\n"
                f"3. Falling back to local file: prompts/{{generator_name}}-generator.xml"
            )
        )
```

**Retry Logic with Exponential Backoff:**

```python
import asyncio
from typing import Callable, TypeVar

T = TypeVar('T')

async def retry_with_backoff(
    func: Callable[[], T],
    max_retries: int = 3,
    backoff_ms: list[int] = [100, 200, 400],
    retryable_exceptions: tuple = (ConnectionError, TimeoutError, ServerError)
) -> T:
    """Retries function with exponential backoff for transient failures"""
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except retryable_exceptions as e:
            if attempt == max_retries:
                # Final retry exhausted - raise error
                logger.error(
                    "Retry exhausted",
                    extra={
                        "attempt": attempt + 1,
                        "max_retries": max_retries,
                        "error": str(e)
                    }
                )
                raise
            else:
                # Retry with backoff
                backoff_duration = backoff_ms[attempt] / 1000  # Convert to seconds
                logger.warning(
                    "Retrying after failure",
                    extra={
                        "attempt": attempt + 1,
                        "max_retries": max_retries,
                        "backoff_ms": backoff_ms[attempt],
                        "error": str(e)
                    }
                )
                await asyncio.sleep(backoff_duration)
```

**Structured Error Logging:**

```python
import logging
import json

logger = logging.getLogger(__name__)

def log_mcp_error(error: MCPPromptError, context: dict):
    """Logs MCP prompt error with structured details"""
    logger.error(
        "MCP prompt error",
        extra={
            "error_type": error.__class__.__name__,
            "message": error.message,
            "prompt_uri": error.prompt_uri,
            "context": context,  # {generator_name, server_url, retry_count, etc.}
            "troubleshooting": error.troubleshooting
        }
    )
```

**References to Implementation Standards:**
- **CLAUDE-tooling.md (Python):** Use Python standard logging library with structured JSON format
- **CLAUDE-testing.md (Python):** Test error scenarios (mock MCP Server failures, validate retry logic)
- **CLAUDE-validation.md (Python):** Validate error messages are user-friendly (no stack traces exposed to users)

**Note:** Treat CLAUDE.md content as authoritative - supplement with story-specific context, don't duplicate.

### Technical Tasks
- **Error Classes:** Define exception hierarchy (MCPPromptError base class, specific error types)
- **Retry Logic:** Implement retry_with_backoff utility with exponential backoff
- **User Messages:** Write user-friendly error messages with troubleshooting steps for each error type
- **Structured Logging:** Implement structured error logging with JSON format
- **Command Integration:** Update `/generate` command to catch MCP errors and display user messages
- **Fallback Guidance:** Display fallback message when falling back to local files
- **Testing:** Test all error scenarios (connection failures, 404, 500, malformed XML, timeout)
- **Documentation:** Add troubleshooting guide to docs with common error scenarios and resolutions

## Acceptance Criteria

**Format Guidance:** Gherkin format (Given-When-Then) for scenario-based validation.

### Scenario 1: Connection error displays clear message
**Given** MCP Server is not running or unreachable
**When** developer runs `/generate epic-generator` command
**Then** command displays error message: "Cannot connect to MCP Server at http://localhost:3000"
**And** message includes troubleshooting steps (check server running, verify URL, check network)
**And** message indicates fallback: "Falling back to local file: prompts/epic-generator.xml"
**And** structured log entry created with error details

### Scenario 2: Prompt not found error displays available prompts
**Given** MCP Server is running but prompt `mcp://prompts/generator/invalid` does not exist
**When** developer runs `/generate invalid-generator` command
**Then** command displays error message: "Prompt not found: mcp://prompts/generator/invalid"
**And** message suggests verifying prompt name and lists available prompts
**And** message indicates fallback to local file
**And** structured log entry created

### Scenario 3: Retry logic recovers from transient connection failure
**Given** MCP Server experiences transient network issue (first 2 requests fail, 3rd succeeds)
**When** developer runs `/generate prd-generator` command
**Then** command retries with exponential backoff: 100ms, 200ms
**And** 3rd attempt succeeds, generator executes normally
**And** user sees warning log: "Retrying after failure (attempt 1/3)"
**And** user sees success message: "Generator executed successfully"

### Scenario 4: Retry exhaustion falls back to local file
**Given** MCP Server is persistently unreachable (all 3 retries fail)
**When** developer runs `/generate hls-generator` command
**Then** command attempts 3 retries with exponential backoff (100ms, 200ms, 400ms)
**And** after 3rd retry fails, command displays: "Retry exhausted, falling back to local file"
**And** command reads local file `prompts/hls-generator.xml` and executes successfully
**And** structured log entry includes retry_count: 3, final_error: "ConnectionError"

### Scenario 5: Server error (5xx) provides troubleshooting context
**Given** MCP Server returns 500 Internal Server Error
**When** developer runs `/generate backlog-story-generator` command
**Then** command displays error message: "MCP Server error 500 for mcp://prompts/generator/backlog-story"
**And** message includes server response excerpt (first 200 chars)
**And** message suggests checking server logs and retrying later
**And** message indicates fallback to local file

### Scenario 6: Malformed XML error reports parsing issue
**Given** MCP Server returns invalid XML content (e.g., missing closing tag)
**When** developer runs `/generate spike-generator` command
**Then** command displays error message: "Invalid generator XML from mcp://prompts/generator/spike"
**And** message includes XML parsing error details
**And** message suggests reporting issue to MCP Server maintainer
**And** message indicates fallback to local file

### Scenario 7: Timeout error triggers retry
**Given** MCP Server response time exceeds timeout (5 seconds)
**When** developer runs `/generate tech-spec-generator` command
**Then** command times out after 5 seconds
**And** command retries with exponential backoff (3 attempts)
**And** if all retries time out: displays timeout error with troubleshooting steps
**And** falls back to local file

### Scenario 8: Structured logs enable debugging
**Given** developer encounters MCP prompt error
**When** developer checks log file or log aggregation system
**Then** log entry includes structured JSON with fields:
  - error_type (e.g., "ConnectionError")
  - message (user-friendly error message)
  - prompt_uri (e.g., "mcp://prompts/generator/epic")
  - context (generator_name, server_url, retry_count, timestamp)
  - troubleshooting (troubleshooting steps displayed to user)
**And** logs queryable by error_type for trend analysis

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 2 SP (DON'T SPLIT per SDLC Section 11.6 - <3 SP rarely benefits from decomposition)
- **Developer Count:** Single developer (error handling + logging)
- **Domain Span:** Single domain (client-side command layer)
- **Complexity:** Low - standard error handling patterns (exception hierarchy, retry logic, structured logging)
- **Uncertainty:** Low - error scenarios well-defined, retry logic straightforward
- **Override Factors:** None (not cross-domain, not security-critical, standard implementation)

Per SDLC Section 11.6 Decision Matrix: "<3 SP → DON'T SPLIT". Implementation is straightforward error handling with retry logic. Decomposition overhead not justified for 2 SP story.

## Definition of Done
- [ ] Code implemented and reviewed
- [ ] Error class hierarchy defined (MCPPromptError and specific error types)
- [ ] Retry logic implemented with exponential backoff
- [ ] User-friendly error messages written for all error scenarios
- [ ] Structured logging implemented with JSON format
- [ ] `/generate` command updated to catch and display MCP errors
- [ ] Fallback guidance displayed when falling back to local files
- [ ] Unit tests written for all error scenarios (connection failure, 404, 500, malformed XML, timeout)
- [ ] Unit tests validate retry logic (mock transient failures, verify backoff timing)
- [ ] Troubleshooting guide added to documentation
- [ ] Acceptance criteria validated (all 8 scenarios passing)
- [ ] Product owner approval obtained

## Additional Information
**Suggested Labels:** error-handling, user-experience, reliability, observability
**Estimated Story Points:** 2
**Dependencies:**
- **Story Dependencies:**
  - US-035 (Expose Generators as MCP Prompts) - must complete first
  - US-036 (Update /generate Command to Call MCP Prompts) - must complete first (provides MCP call logic to wrap with error handling)
- **Technical Dependencies:**
  - Python logging library (stdlib)
  - MCP client library (for error types like ConnectionError, TimeoutError)
- **Team Dependencies:** None

**Related PRD Section:** PRD-006 §Non-Functional Requirements - NFR-Reliability-01 (retry logic); §User Experience - User Flows (error scenarios)

## Decisions Made

**All technical approaches resolved.**

**D1: Retry Strategy**
- **Decision:** 3 retries with exponential backoff (100ms, 200ms, 400ms) per PRD-006 NFR-Reliability-01
- **Rationale:** Balances reliability (recover from transient failures) with latency (total retry time <1 second)
- **Retryable Errors:** Connection errors, timeouts, 5xx server errors (transient)
- **Non-Retryable Errors:** 404 Prompt Not Found, 400 Bad Request, malformed XML (persistent, retry won't help)

**D2: User Message Format**
- **Decision:** Error message includes 3 parts: (1) error description, (2) troubleshooting steps (numbered list), (3) fallback guidance
- **Rationale:** User-friendly, actionable, reduces support burden by enabling self-service debugging
- **Example:** See error class definitions in Implementation Guidance section

**D3: Structured Logging Format**
- **Decision:** JSON structured logs with fields: error_type, message, prompt_uri, context, troubleshooting
- **Rationale:** Enables log aggregation queries (filter by error_type), trend analysis (error rate over time), debugging (full context included)
- **Integration:** Works with standard log aggregation systems (Grafana Loki, CloudWatch Logs, etc.)

**D4: Fallback Behavior**
- **Decision:** Always attempt fallback to local file after MCP prompt error (with clear message to user)
- **Rationale:** Maximizes reliability (user can still work even if MCP Server down), maintains backward compatibility
- **Exception:** If local file also missing, display final error message (no fallback available)

**D5: Error Classification Hierarchy**
- **Decision:** Base class MCPPromptError with specific subclasses (ConnectionError, PromptNotFoundError, ServerError, MalformedContentError, TimeoutError)
- **Rationale:** Enables fine-grained error handling (retry only transient errors), structured logging (error_type field), user-specific messages per error type
- **Implementation:** Python exception hierarchy with custom __init__ methods
