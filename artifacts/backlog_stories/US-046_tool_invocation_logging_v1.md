# User Story: Tool Invocation Logging

## Metadata
- **Story ID:** US-046
- **Title:** Tool Invocation Logging
- **Type:** Feature
- **Status:** Draft
- **Priority:** Should-have (enables observability for MCP tools, supports FR-17)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-008 (MCP Tools - Validation and Path Resolution)
- **Functional Requirements Covered:** FR-17
- **Informed By Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Functional Requirements - FR-17
- **Functional Requirements Coverage:**
  - **FR-17:** MCP Server SHALL log all tool invocations (validation, path resolution, task tracking, ID management) with timestamp, input parameters, execution duration, and result status for observability

**Parent High-Level Story:** [HLS-008: MCP Tools - Validation and Path Resolution]
- **Link:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 7: Tool Invocation Logging

## User Story
As a Framework Maintainer, I want comprehensive logging for all MCP tool invocations, so that I can monitor tool usage patterns, debug failures, and optimize performance.

## Description
MCP tools (validate_artifact, resolve_artifact_path, store_artifact, add_task) currently have basic logging scattered across implementations. This creates:
1. **Inconsistent Logging:** Each tool logs different fields, making cross-tool analysis difficult
2. **Missing Context:** No request ID correlation across tool calls in same workflow
3. **Limited Observability:** Cannot easily query tool usage patterns (most used tool, failure rate, latency distribution)

This story standardizes tool invocation logging across all MCP tools with:
1. **Structured Logging:** JSON format with consistent field names using structlog library
2. **Standard Fields:** All tools log: timestamp, tool_name, request_id, input_params (summary), duration_ms, success, error_message (if failed)
3. **Tool-Specific Fields:** Each tool adds domain-specific fields (e.g., validate_artifact logs checklist_id, artifact_type)
4. **Correlation:** Request ID propagates across tool calls in same workflow (e.g., generate PRD → validate_artifact → add_task)
5. **Retention:** Logs retained for ≥30 days for error analysis and performance monitoring (per FR-17)

After implementation, Framework Maintainers can query logs to answer:
- "What's the p95 latency for validate_artifact tool?"
- "Which tool has highest failure rate?"
- "How many times was resolve_artifact_path called this week?"
- "Which workflows trigger the most tool invocations?"

## Implementation Research References

**Primary Research Document:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

**Technical Patterns Applied:**
- **§6.1: Structured Logging:** Use structlog for JSON-formatted logs with structured context (ref: Implementation Research §6.1 - Structured Logging)
- **§6.2: Prometheus Metrics:** Instrument tool execution time and success/failure rates for observability (ref: Implementation Research §6.2 - Prometheus Metrics)

## Functional Requirements
1. Standardize logging across 4 MCP tools:
   - `validate_artifact`
   - `resolve_artifact_path`
   - `store_artifact`
   - `add_task`
2. All tools log standard fields in JSON format:
   - `timestamp`: ISO 8601 timestamp (e.g., "2025-10-18T14:30:00.123Z")
   - `tool_name`: Tool identifier (e.g., "validate_artifact")
   - `request_id`: UUID for correlation across tool calls
   - `input_params_summary`: Summarized input parameters (not full content, to limit log size)
   - `duration_ms`: Execution duration in milliseconds
   - `success`: Boolean (true if tool succeeded, false if error)
   - `error_message`: Error message (if success=false)
   - `error_type`: Error type (e.g., "validation_error", "not_found", "api_error")
3. Each tool adds tool-specific fields:
   - **validate_artifact:** `checklist_id`, `artifact_type`, `automated_pass_rate`, `manual_review_count`
   - **resolve_artifact_path:** `pattern`, `variables`, `resolved_path`, `match_count`
   - **store_artifact:** `artifact_id`, `artifact_type`, `version`, `size_bytes`, `storage_path`
   - **add_task:** `tasks_added`, `artifact_ids`, `generators`
4. Implement request ID generation and propagation:
   - Generate UUID on first tool call in workflow
   - Propagate request_id to subsequent tool calls (via context or parameter)
   - Log request_id in all tool invocation log entries
5. Log output destination:
   - Development: stdout (JSON lines)
   - Production: Log aggregation system (e.g., Loki, CloudWatch Logs, Elasticsearch)
6. Log retention:
   - Minimum 30 days (per FR-17)
   - Configurable retention period via environment variable

## Non-Functional Requirements
- **Observability:** Logs queryable via log aggregation system (structured JSON format)
- **Performance:** Logging overhead <10ms per tool invocation (negligible impact on NFR-Performance-02 <500ms target)
- **Consistency:** Same JSON schema across all tools for interoperability
- **Privacy:** Do not log sensitive data (API keys, full artifact content - only summaries)
- **Reliability:** Logging failures do not crash tool execution (log errors to stderr, continue execution)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** Follow established logging patterns from Implementation Research. Supplement with story-specific structured logging configuration.

**References to Implementation Standards:**
- **prompts/CLAUDE/python/patterns-tooling.md:** Use Taskfile commands for testing
- **prompts/CLAUDE/python/patterns-testing.md:** Testing patterns (verify log output format)
- **Implementation Research §6.1:** Structured logging with structlog

### Implementation Guidance

**Story-Specific Technical Approach:**

1. **Structured Logging Configuration:**
   ```python
   import structlog
   import logging
   import sys

   # Configure structlog for JSON output
   structlog.configure(
       processors=[
           structlog.stdlib.filter_by_level,
           structlog.stdlib.add_logger_name,
           structlog.stdlib.add_log_level,
           structlog.stdlib.PositionalArgumentsFormatter(),
           structlog.processors.TimeStamper(fmt="iso"),  # ISO 8601 timestamp
           structlog.processors.StackInfoRenderer(),
           structlog.processors.format_exc_info,
           structlog.processors.UnicodeDecoder(),
           structlog.processors.JSONRenderer()  # JSON output
       ],
       context_class=dict,
       logger_factory=structlog.stdlib.LoggerFactory(),
       cache_logger_on_first_use=True,
   )

   # Configure standard library logging to output to stdout
   logging.basicConfig(
       format="%(message)s",
       stream=sys.stdout,
       level=logging.INFO,
   )

   logger = structlog.get_logger()
   ```

2. **Standard Logging Decorator:**
   ```python
   from functools import wraps
   import time
   import uuid

   def log_tool_invocation(tool_name: str):
       """Decorator for standardized tool invocation logging"""
       def decorator(func):
           @wraps(func)
           async def wrapper(params, request_id: str = None):
               # Generate request ID if not provided
               if not request_id:
                   request_id = str(uuid.uuid4())

               start_time = time.time()

               # Log tool invocation start
               logger.info(
                   f"{tool_name}_invocation_started",
                   tool_name=tool_name,
                   request_id=request_id,
                   input_params_summary=_summarize_input(params)
               )

               try:
                   # Execute tool
                   result = await func(params, request_id=request_id)

                   # Calculate duration
                   duration_ms = (time.time() - start_time) * 1000

                   # Log success
                   logger.info(
                       f"{tool_name}_invocation_completed",
                       tool_name=tool_name,
                       request_id=request_id,
                       duration_ms=duration_ms,
                       success=True,
                       **_extract_tool_specific_fields(tool_name, params, result)
                   )

                   return result

               except Exception as e:
                   # Calculate duration
                   duration_ms = (time.time() - start_time) * 1000

                   # Log failure
                   logger.error(
                       f"{tool_name}_invocation_failed",
                       tool_name=tool_name,
                       request_id=request_id,
                       duration_ms=duration_ms,
                       success=False,
                       error_message=str(e),
                       error_type=type(e).__name__
                   )

                   raise  # Re-raise exception for upstream handling

           return wrapper
       return decorator

   def _summarize_input(params) -> dict:
       """Summarizes input parameters for logging (avoids logging full artifact content)"""
       summary = {}
       for key, value in params.dict().items():
           if key == "artifact_content":
               summary[key] = f"<content: {len(value)} chars>"
           elif isinstance(value, str) and len(value) > 100:
               summary[key] = f"{value[:100]}..."
           else:
               summary[key] = value
       return summary

   def _extract_tool_specific_fields(tool_name: str, params, result) -> dict:
       """Extracts tool-specific fields for logging"""
       if tool_name == "validate_artifact":
           return {
               "checklist_id": params.checklist_id,
               "artifact_type": _infer_artifact_type(params.artifact_content),
               "automated_pass_rate": result.automated_pass_rate if hasattr(result, 'automated_pass_rate') else None,
               "manual_review_count": result.manual_review_required if hasattr(result, 'manual_review_required') else None
           }
       elif tool_name == "resolve_artifact_path":
           return {
               "pattern": params.pattern,
               "variables": params.variables,
               "resolved_path": result.path if result.success else None,
               "match_count": result.match_count if result.success else 0
           }
       elif tool_name == "store_artifact":
           return {
               "artifact_id": params.metadata.artifact_id,
               "artifact_type": params.metadata.artifact_type,
               "version": params.metadata.version,
               "size_bytes": len(params.artifact_content),
               "storage_path": result.storage_path if hasattr(result, 'storage_path') else None
           }
       elif tool_name == "add_task":
           return {
               "tasks_added": len(params.tasks),
               "artifact_ids": [task.artifact_id for task in params.tasks],
               "generators": [task.generator for task in params.tasks]
           }
       else:
           return {}
   ```

3. **Apply Decorator to All Tools:**
   ```python
   # Example: validate_artifact tool with logging
   @log_tool_invocation(tool_name="validate_artifact")
   @mcp.tool(name="validate_artifact", description="...")
   async def validate_artifact(params: ValidateArtifactInput, request_id: str = None) -> ValidationResult:
       """Validates artifact content against validation checklist"""
       # Tool implementation (no manual logging needed - decorator handles it)
       checklist = await checklist_cache.load_checklist(params.checklist_id)
       validator = ArtifactValidator(params.artifact_content)
       results = evaluate_criteria(validator, checklist)
       return ValidationResult(...)
   ```

4. **Request ID Propagation:**
   ```python
   # In generate.md command execution:
   request_id = str(uuid.uuid4())

   # Call validate_artifact with request_id
   validation_result = await validate_artifact(params, request_id=request_id)

   # Call add_task with same request_id (for correlation)
   task_result = await add_task(task_params, request_id=request_id)

   # All tool invocations in same workflow share request_id for correlation
   ```

5. **Log Query Examples (using jq for JSON logs):**
   ```bash
   # Query p95 latency for validate_artifact
   cat mcp_server.log | jq -r 'select(.tool_name=="validate_artifact") | .duration_ms' | sort -n | awk 'BEGIN{c=0} {a[c]=$1; c++} END{print a[int(c*0.95)]}'

   # Count tool invocations by tool_name
   cat mcp_server.log | jq -r '.tool_name' | sort | uniq -c

   # Find all failed tool invocations
   cat mcp_server.log | jq -r 'select(.success==false)'

   # Find all tool invocations in specific workflow (by request_id)
   cat mcp_server.log | jq -r 'select(.request_id=="abc123-...")'
   ```

6. **Testing Strategy:**
   - Unit tests: Verify log decorator captures all standard fields
   - Integration tests: Verify all tools produce valid JSON logs
   - Correlation tests: Verify request_id propagates across tool calls
   - Performance tests: Verify logging overhead <10ms per invocation

### Technical Tasks
- [ ] Configure structlog for JSON output
- [ ] Implement `log_tool_invocation` decorator with standard fields
- [ ] Implement input parameter summarization (avoid logging full content)
- [ ] Implement tool-specific field extraction
- [ ] Apply decorator to validate_artifact tool
- [ ] Apply decorator to resolve_artifact_path tool
- [ ] Apply decorator to store_artifact tool
- [ ] Apply decorator to add_task tool
- [ ] Implement request ID generation and propagation
- [ ] Write unit tests for logging decorator
- [ ] Write integration tests for log output format
- [ ] Write correlation tests for request ID propagation
- [ ] Write performance tests (<10ms logging overhead)
- [ ] Document log schema and query examples

## Acceptance Criteria

### Scenario 1: validate_artifact logs standard fields
**Given** validate_artifact tool is called
**When** Tool execution completes
**Then** Log entry includes standard fields:
  - `timestamp` (ISO 8601)
  - `tool_name="validate_artifact"`
  - `request_id` (UUID)
  - `input_params_summary` (checklist_id, artifact content length)
  - `duration_ms` (execution time)
  - `success=true`
**And** Log entry includes tool-specific fields:
  - `checklist_id`
  - `artifact_type`
  - `automated_pass_rate`
  - `manual_review_count`
**And** Log format is valid JSON

### Scenario 2: resolve_artifact_path logs error on not_found
**Given** resolve_artifact_path tool is called with non-existent artifact
**When** Tool returns not_found error
**Then** Log entry includes:
  - `success=false`
  - `error_message="No files match pattern: ..."`
  - `error_type="PathResolutionError"` (or similar)
  - `pattern` (path pattern searched)
  - `variables` (variable substitutions)
  - `resolved_path=null`

### Scenario 3: Request ID propagates across tool calls
**Given** Workflow: generate PRD → validate_artifact → add_task
**When** All tools execute with same request_id
**Then** All 3 log entries include same `request_id` value
**And** Logs queryable by request_id to see full workflow trace

### Scenario 4: Input parameter summarization avoids logging full content
**Given** validate_artifact tool called with 50KB artifact content
**When** Tool logs invocation
**Then** Log entry includes `input_params_summary.artifact_content="<content: 50000 chars>"`
**And** Full artifact content NOT logged (only summary)
**And** Log entry size <5KB (manageable for log aggregation)

### Scenario 5: All 4 tools produce consistent JSON logs
**Given** All 4 MCP tools (validate_artifact, resolve_artifact_path, store_artifact, add_task)
**When** Each tool invoked
**Then** All tools produce JSON logs with same standard field names
**And** Logs parseable by same JSON schema
**And** Cross-tool analysis possible (e.g., latency comparison)

### Scenario 6: Logging failure does not crash tool
**Given** Log aggregation system is down (logging write fails)
**When** Tool executes
**Then** Tool continues execution (does not crash)
**And** Logging error written to stderr
**And** Tool returns result successfully

### Scenario 7: Logs retained for 30 days
**Given** Log retention configured for 30 days
**When** Logs written to log aggregation system
**Then** Logs queryable for 30 days after creation
**And** Logs older than 30 days automatically deleted (retention policy)

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Not Needed (Single Sprint-Ready Task)

**Rationale:**
- **Story Points:** 3 SP (below 5 SP threshold - CONSIDER SKIPPING per decision matrix)
- **Developer Count:** Single developer (applying decorator pattern to 4 tools)
- **Domain Span:** Single domain (observability/logging)
- **Complexity:** Low - straightforward decorator pattern with structlog library
- **Uncertainty:** Low - well-defined structured logging pattern
- **Override Factors:** None (no security-critical, no external dependencies)

Per SDLC Section 11.6 Decision Matrix: "3 SP, single developer, low complexity → SKIP (Single sprint-ready task)".

**No task decomposition needed.** Story can be completed as single unit of work in 1-2 days.

## Definition of Done
- [ ] structlog configured for JSON output
- [ ] `log_tool_invocation` decorator implemented with standard fields
- [ ] Input parameter summarization implemented
- [ ] Tool-specific field extraction implemented
- [ ] Decorator applied to all 4 MCP tools (validate_artifact, resolve_artifact_path, store_artifact, add_task)
- [ ] Request ID generation and propagation implemented
- [ ] Unit tests written and passing (logging decorator)
- [ ] Integration tests passing (log output format)
- [ ] Correlation tests passing (request ID propagation)
- [ ] Performance tests passing (<10ms logging overhead)
- [ ] Log schema and query examples documented
- [ ] Product Owner approval obtained

## Additional Information
**Suggested Labels:** observability, logging, monitoring
**Estimated Story Points:** 3
**Dependencies:**
- **Depends On:** US-040, US-042, US-043, US-044 (all 4 MCP tools must exist)
- **Blocks:** US-047 (integration testing may validate log output)
- **Related:** FR-17 (tool invocation logging requirement), NFR-Observability-01

**Related PRD Section:** PRD-006 §Functional Requirements - FR-17, §Non-Functional Requirements - NFR-Observability-01

## Open Questions & Implementation Uncertainties

**No open implementation questions.** Structured logging approach and decorator pattern clearly defined.

Technical implementation details (structlog configuration, decorator pattern, request ID propagation) defined in Implementation Guidance section above.

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md` (§6.1 Structured Logging, §6.2 Prometheus Metrics)
- **Related Stories:** US-040, US-042, US-043, US-044 (all 4 MCP tools)
