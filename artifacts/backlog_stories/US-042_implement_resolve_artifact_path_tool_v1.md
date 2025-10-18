# User Story: Implement resolve_artifact_path Tool

## Metadata
- **Story ID:** US-042
- **Title:** Implement resolve_artifact_path Tool
- **Type:** Feature
- **Status:** Draft
- **Priority:** Critical (replaces AI inference for path resolution, reducing error rate from 20-30% to <5%)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-008 (MCP Tools - Validation and Path Resolution)
- **Functional Requirements Covered:** FR-07
- **Informed By Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Functional Requirements - FR-07
- **Functional Requirements Coverage:**
  - **FR-07:** MCP Server SHALL provide `resolve_artifact_path` tool that accepts path pattern with variables and returns exact file path or error if not found

**Parent High-Level Story:** [HLS-008: MCP Tools - Validation and Path Resolution]
- **Link:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 3: Implement resolve_artifact_path Tool

## User Story
As Claude Code, I want a deterministic path resolution tool that converts artifact path patterns to exact file paths, so that I locate artifacts with <5% error rate instead of 20-30% AI inference errors.

## Description
Currently, Claude Code uses AI inference to resolve artifact path patterns from CLAUDE.md (e.g., `artifacts/epics/EPIC-{id}_{slug}_v{version}.md`) to actual file paths. This approach is error-prone (20-30% error rate due to variable substitution mistakes), token-intensive (~1-2k tokens per resolution), and slow (~1 second inference time).

This story implements a deterministic Python tool (`resolve_artifact_path`) that:
1. Accepts path pattern with variable placeholders (e.g., `artifacts/epics/EPIC-{id}*_v{version}.md`)
2. Accepts variable substitutions (e.g., `{id: "006", version: 1}`)
3. Performs variable substitution (pattern → `artifacts/epics/EPIC-006*_v1.md`)
4. Uses glob matching to find file
5. Returns exact file path or structured error (multiple matches, no match)

The tool reduces path resolution errors from 20-30% to <5%, execution time from ~1s to <200ms, and eliminates token consumption for path resolution operations.

## Implementation Research References

**Primary Research Document:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

**Technical Patterns Applied:**
- **§2.1: Python 3.11+ with Type Safety:** Use Pydantic models for path resolution input/output schemas with full type hints (ref: Implementation Research §2.1 - Programming Language: Python 3.11+)
- **§2.2: FastAPI Integration:** Expose path resolution tool as MCP tool via FastAPI with auto-generated OpenAPI documentation (ref: Implementation Research §2.2 - Backend Framework: FastAPI 0.100+)
- **§5.3: Input Validation:** Validate path pattern and variables with Pydantic, reject path traversal attempts (ref: Implementation Research §5.3 - Input Validation and Command Injection Prevention)
- **§6.1: Structured Logging:** Log path resolution invocations with pattern, variables, result path, duration (ref: Implementation Research §6.1 - Structured Logging)

**Anti-Patterns Avoided:**
- **§5.3: Path Traversal Vulnerabilities:** Validate resolved path is within artifacts/ directory before returning (ref: Implementation Research §5.3 - Input Validation)
- **§8.1: Poor Error Handling:** Return structured error responses distinguishing "not found", "multiple matches", "ambiguous pattern" (ref: Implementation Research §8.1 - Pitfall 3)

**Performance Considerations:**
- **§2.4: Caching Layer:** Path resolution results cached in memory (TTL: 1 minute) for frequently requested artifacts to reduce repeated glob operations (ref: Implementation Research §2.4 - Caching Layer)

## Functional Requirements
1. Tool accepts two parameters:
   - `pattern` (string): Path pattern with variable placeholders (e.g., `artifacts/epics/EPIC-{id}*_v{version}.md`)
   - `variables` (dict): Variable substitutions (e.g., `{id: "006", version: 1}`)
2. Tool performs variable substitution:
   - Replace `{id}` with provided ID value
   - Replace `{version}` with provided version number
   - Support wildcard `*` for slug matching
3. Tool validates resolved pattern for security:
   - Reject patterns containing `..` (path traversal)
   - Reject absolute paths (must be relative to artifacts/ directory)
   - Reject patterns outside artifacts/ directory tree
4. Tool uses glob matching to find file(s)
5. Tool returns structured JSON response:
   ```json
   // Success (single match)
   {
     "success": true,
     "path": "artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md",
     "match_count": 1
   }

   // Error (no match)
   {
     "success": false,
     "error": "not_found",
     "message": "No files match pattern: artifacts/epics/EPIC-006*_v1.md",
     "pattern_resolved": "artifacts/epics/EPIC-006*_v1.md"
   }

   // Error (multiple matches)
   {
     "success": false,
     "error": "multiple_matches",
     "message": "Multiple files match pattern (expected 1): artifacts/epics/EPIC-006*_v1.md",
     "pattern_resolved": "artifacts/epics/EPIC-006*_v1.md",
     "candidates": [
       "artifacts/epics/EPIC-006_mcp_server_integration_v1.md",
       "artifacts/epics/EPIC-006_sdlc_framework_v1.md"
     ]
   }
   ```
6. Tool execution completes in <200ms p95 (per PRD-006 NFR-Performance-02, path resolution subset)
7. Tool logs path resolution invocations with timestamp, pattern, variables, result path, duration

## Non-Functional Requirements
- **Performance:** Path resolution latency <200ms p95 (subset of NFR-Performance-02 <500ms tool execution target)
- **Accuracy:** Deterministic resolution (same input → same output, 100% consistency)
- **Security:** Path traversal protection (validate resolved path within artifacts/ directory)
- **Reliability:** Handle ambiguous patterns gracefully, return clear error messages
- **Observability:** Structured logging captures resolution patterns for debugging

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** Follow established implementation patterns for MCP tools. Supplement with story-specific path resolution logic.

**References to Implementation Standards:**
- **prompts/CLAUDE/python/patterns-tooling.md:** Use Taskfile commands (`task test`, `task lint`, `task type-check`)
- **prompts/CLAUDE/python/patterns-testing.md:** Testing patterns (80% coverage, async tests)
- **prompts/CLAUDE/python/patterns-typing.md:** Type hints with mypy strict mode, Pydantic models
- **prompts/CLAUDE/python/patterns-validation.md:** Input validation with Pydantic, security patterns
- **prompts/CLAUDE/python/patterns-architecture.md:** Project structure following established patterns

### Implementation Guidance

**Story-Specific Technical Approach:**

1. **Pydantic Models for Tool Input/Output:**
   ```python
   from pydantic import BaseModel, Field, validator
   from typing import Dict, List, Optional, Literal

   class ResolveArtifactPathInput(BaseModel):
       """Input schema for resolve_artifact_path tool"""
       pattern: str = Field(
           ...,
           description="Path pattern with variables (e.g., 'artifacts/epics/EPIC-{id}*_v{version}.md')"
       )
       variables: Dict[str, str] = Field(
           ...,
           description="Variable substitutions (e.g., {'id': '006', 'version': '1'})"
       )

       @validator('pattern')
       def validate_pattern_safety(cls, v):
           """Prevents path traversal attacks"""
           if '..' in v or v.startswith('/'):
               raise ValueError("Pattern contains path traversal or absolute path")
           if not v.startswith('artifacts/'):
               raise ValueError("Pattern must start with 'artifacts/'")
           return v

   class PathResolutionSuccess(BaseModel):
       """Successful path resolution result"""
       success: Literal[True] = True
       path: str = Field(..., description="Resolved file path")
       match_count: Literal[1] = 1

   class PathResolutionError(BaseModel):
       """Failed path resolution result"""
       success: Literal[False] = False
       error: Literal["not_found", "multiple_matches", "invalid_pattern"]
       message: str
       pattern_resolved: str
       candidates: Optional[List[str]] = None  # For multiple_matches error

   PathResolutionResult = PathResolutionSuccess | PathResolutionError
   ```

2. **Path Resolution Logic:**
   ```python
   import glob
   import re
   from pathlib import Path

   class ArtifactPathResolver:
       def __init__(self, base_dir: str = "artifacts"):
           self.base_dir = Path(base_dir)

       def resolve(self, pattern: str, variables: Dict[str, str]) -> PathResolutionResult:
           """Resolves path pattern to exact file path"""
           # Step 1: Variable substitution
           resolved_pattern = self._substitute_variables(pattern, variables)

           # Step 2: Security validation
           if not self._is_safe_path(resolved_pattern):
               return PathResolutionError(
                   error="invalid_pattern",
                   message=f"Unsafe pattern after substitution: {resolved_pattern}",
                   pattern_resolved=resolved_pattern
               )

           # Step 3: Glob matching
           matches = list(glob.glob(resolved_pattern))

           # Step 4: Return result based on match count
           if len(matches) == 0:
               return PathResolutionError(
                   error="not_found",
                   message=f"No files match pattern: {resolved_pattern}",
                   pattern_resolved=resolved_pattern
               )
           elif len(matches) == 1:
               return PathResolutionSuccess(
                   path=matches[0],
                   match_count=1
               )
           else:  # multiple matches
               return PathResolutionError(
                   error="multiple_matches",
                   message=f"Multiple files match pattern (expected 1): {resolved_pattern}",
                   pattern_resolved=resolved_pattern,
                   candidates=matches
               )

       def _substitute_variables(self, pattern: str, variables: Dict[str, str]) -> str:
           """Replaces {variable} placeholders with values"""
           resolved = pattern
           for var_name, var_value in variables.items():
               placeholder = f"{{{var_name}}}"
               resolved = resolved.replace(placeholder, str(var_value))
           return resolved

       def _is_safe_path(self, path: str) -> bool:
           """Validates path is within artifacts/ directory (no traversal)"""
           # Check for path traversal
           if '..' in path or path.startswith('/'):
               return False

           # Resolve path and check it's within base_dir
           try:
               resolved = Path(path).resolve()
               base = self.base_dir.resolve()
               return resolved.is_relative_to(base) or str(resolved).startswith(str(base))
           except Exception:
               return False
   ```

3. **MCP Tool Implementation:**
   ```python
   from mcp.server.fastmcp import FastMCP
   import structlog
   import time

   mcp = FastMCP(name="MCPServer", version="1.0.0")
   logger = structlog.get_logger()
   resolver = ArtifactPathResolver(base_dir="artifacts")

   @mcp.tool(
       name="resolve_artifact_path",
       description="""
       Resolves artifact path pattern to exact file path.

       Use this tool when:
       - You need to locate an artifact using path pattern from CLAUDE.md
       - You have artifact ID and version but need full file path
       - You want deterministic path resolution instead of AI inference

       Supports path patterns like:
       - artifacts/epics/EPIC-{id}*_v{version}.md
       - artifacts/prds/PRD-{id}*_v{version}.md
       - artifacts/backlog_stories/US-{id}*_v{version}.md

       Returns exact file path or structured error (not_found, multiple_matches).

       Reduces path resolution errors from 20-30% (AI inference) to <5% (deterministic).
       """
   )
   async def resolve_artifact_path(params: ResolveArtifactPathInput) -> PathResolutionResult:
       """Resolves artifact path pattern to exact file path"""
       start_time = time.time()

       try:
           # Resolve path using pattern matching
           result = resolver.resolve(params.pattern, params.variables)

           # Log resolution invocation
           duration_ms = (time.time() - start_time) * 1000
           logger.info(
               "path_resolution_completed",
               pattern=params.pattern,
               variables=params.variables,
               success=result.success,
               resolved_path=result.path if result.success else None,
               error=result.error if not result.success else None,
               duration_ms=duration_ms
           )

           return result

       except Exception as e:
           logger.error("path_resolution_error", error=str(e))
           raise HTTPException(status_code=500, detail="Path resolution failed due to internal error")
   ```

4. **Caching Strategy (Optional Enhancement):**
   ```python
   from functools import lru_cache
   from datetime import datetime, timedelta

   class CachedPathResolver(ArtifactPathResolver):
       def __init__(self, base_dir: str = "artifacts", cache_ttl_seconds: int = 60):
           super().__init__(base_dir)
           self.cache_ttl_seconds = cache_ttl_seconds
           self._cache: Dict[tuple, tuple[PathResolutionResult, datetime]] = {}

       def resolve(self, pattern: str, variables: Dict[str, str]) -> PathResolutionResult:
           """Resolves with caching"""
           cache_key = (pattern, tuple(sorted(variables.items())))

           # Check cache
           if cache_key in self._cache:
               result, timestamp = self._cache[cache_key]
               if datetime.utcnow() - timestamp < timedelta(seconds=self.cache_ttl_seconds):
                   return result

           # Cache miss - resolve and cache
           result = super().resolve(pattern, variables)
           self._cache[cache_key] = (result, datetime.utcnow())
           return result
   ```

5. **Testing Strategy:**
   - Unit tests: Validate variable substitution, security validation, glob matching
   - Integration tests: Verify tool resolves paths for all artifact types (Epic, PRD, HLS, US, etc.)
   - Security tests: Attempt path traversal attacks, verify rejection
   - Error handling tests: Test not_found, multiple_matches, invalid_pattern scenarios
   - Performance tests: Verify <200ms p95 latency with 10 sample patterns

### Technical Tasks
- [ ] Implement Pydantic models for tool input/output
- [ ] Implement ArtifactPathResolver class with variable substitution
- [ ] Implement glob matching logic
- [ ] Implement security validation (path traversal protection)
- [ ] Implement MCP tool endpoint with FastMCP decorator
- [ ] Add structured logging for path resolution invocations
- [ ] Add caching layer (optional, TTL: 1 minute)
- [ ] Write unit tests for ArtifactPathResolver methods (80% coverage)
- [ ] Write integration tests for all artifact types
- [ ] Write security tests for path traversal protection
- [ ] Write performance tests (<200ms p95 latency)
- [ ] Add Taskfile commands for running path resolution tool tests

## Acceptance Criteria

### Scenario 1: Epic path resolved successfully
**Given** Epic file exists at `artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md`
**When** Claude Code calls `resolve_artifact_path(pattern="artifacts/epics/EPIC-{id}*_v{version}.md", variables={id: "006", version: 1})`
**Then** tool substitutes variables: pattern → `artifacts/epics/EPIC-006*_v1.md`
**And** tool uses glob to find file
**And** returns `{success: true, path: "artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md", match_count: 1}`
**And** execution completes in <200ms

### Scenario 2: Artifact not found error
**Given** No epic exists with ID 999
**When** Claude Code calls `resolve_artifact_path(pattern="artifacts/epics/EPIC-{id}*_v{version}.md", variables={id: "999", version: 1})`
**Then** tool returns `{success: false, error: "not_found", message: "No files match pattern: artifacts/epics/EPIC-999*_v1.md"}`
**And** error includes pattern_resolved field for debugging
**And** error logged with structured logging

### Scenario 3: Multiple matches error
**Given** Two epic files exist: EPIC-006_v1.md and EPIC-006_draft_v1.md
**When** Claude Code calls `resolve_artifact_path(pattern="artifacts/epics/EPIC-{id}*_v{version}.md", variables={id: "006", version: 1})`
**Then** tool returns `{success: false, error: "multiple_matches", message: "Multiple files match pattern (expected 1): artifacts/epics/EPIC-006*_v1.md", candidates: [...]}`
**And** candidates array includes both file paths
**And** Claude Code can disambiguate by inspecting candidates

### Scenario 4: Path traversal attack prevented
**Given** Malicious pattern attempts to access parent directory
**When** Claude Code calls `resolve_artifact_path(pattern="artifacts/epics/../../../etc/passwd", variables={})`
**Then** tool returns `{success: false, error: "invalid_pattern", message: "Unsafe pattern after substitution: artifacts/epics/../../../etc/passwd"}`
**And** security event logged
**And** no file system access outside artifacts/ directory

### Scenario 5: All artifact types resolvable
**Given** Sample artifacts exist for all types (Epic, PRD, HLS, US, SPEC, TASK, ADR, SPIKE)
**When** Claude Code calls resolve_artifact_path for each type:
  - Epic: `artifacts/epics/EPIC-{id}*_v{version}.md`
  - PRD: `artifacts/prds/PRD-{id}*_v{version}.md`
  - HLS: `artifacts/hls/HLS-{id}*_v{version}.md`
  - US: `artifacts/backlog_stories/US-{id}*_v{version}.md`
  - SPEC: `artifacts/tech_specs/SPEC-{id}*_v{version}.md`
  - TASK: `artifacts/tasks/TASK-{id}*_v{version}.md`
  - ADR: `artifacts/adrs/ADR-{id}*_v{version}.md`
  - SPIKE: `artifacts/spikes/SPIKE-{id}*_v{version}.md`
**Then** All patterns resolve successfully
**And** Each resolution returns exact file path

### Scenario 6: Path resolution execution logged
**Given** Claude Code calls resolve_artifact_path tool
**When** Resolution completes
**Then** tool logs structured event with fields: pattern, variables, success, resolved_path, error, duration_ms
**And** log format is JSON (structured logging)

### Scenario 7: Performance target met
**Given** 10 sample path patterns (Epic, PRD, HLS, US, SPEC)
**When** Each pattern resolved 100 times
**Then** p95 latency <200ms for all pattern types
**And** p99 latency <500ms

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Not Needed (Single Sprint-Ready Task)

**Rationale:**
- **Story Points:** 5 SP (at threshold - CONSIDER SKIPPING per decision matrix)
- **Developer Count:** Single developer (straightforward path resolution logic)
- **Domain Span:** Single domain (file system operations and pattern matching)
- **Complexity:** Low-moderate - well-defined glob matching and variable substitution
- **Uncertainty:** Low - clear implementation approach, standard Python glob library
- **Override Factors:** Security-critical (path traversal protection) - but simple validation logic, not complex enough to require decomposition

Per SDLC Section 11.6 Decision Matrix: "5 SP, single developer, low-moderate complexity, security-critical but simple → SKIP (Security validation is straightforward)".

**No task decomposition needed.** Story can be completed as single unit of work in 2-3 days.

## Definition of Done
- [ ] Pydantic models implemented for tool input/output
- [ ] ArtifactPathResolver class with variable substitution and glob matching
- [ ] Security validation (path traversal protection)
- [ ] MCP tool endpoint implemented with FastMCP
- [ ] Structured logging for path resolution invocations
- [ ] Caching layer implemented (optional, TTL: 1 minute)
- [ ] Unit tests written and passing (80% coverage)
- [ ] Integration tests passing (all artifact types)
- [ ] Security tests passing (path traversal protection validated)
- [ ] Performance tests passing (<200ms p95 latency)
- [ ] Manual testing: Resolve paths for EPIC-006, PRD-006, HLS-006
- [ ] Taskfile commands added for path resolution tool tests
- [ ] Product Owner approval obtained

## Additional Information
**Suggested Labels:** mcp-tools, path-resolution, security, performance
**Estimated Story Points:** 5
**Dependencies:**
- **Depends On:** None (can be implemented independently)
- **Blocks:** US-046 (tool invocation logging depends on resolve_artifact_path working)
- **Blocks:** US-047 (integration testing depends on all tools including path resolution)

**Related PRD Section:** PRD-006 §Functional Requirements - FR-07

## Open Questions & Implementation Uncertainties

**No open implementation questions.** Path resolution approach and security validation clearly defined.

Technical implementation details (glob matching, variable substitution, path safety validation) defined in Implementation Guidance section above.

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md` (§2.1 Python Type Safety, §2.2 FastAPI, §5.3 Input Validation, §6.1 Structured Logging)
- **Related Stories:** US-040 (validate_artifact tool), US-043 (store_artifact tool)
