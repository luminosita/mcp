# User Story: Implement validate_artifact Tool

## Metadata
- **Story ID:** US-040
- **Title:** Implement validate_artifact Tool
- **Type:** Feature
- **Status:** Draft
- **Priority:** Critical (replaces AI inference for artifact validation, reducing error rate from 20-30% to <5%)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-008 (MCP Tools - Validation and Path Resolution)
- **Functional Requirements Covered:** FR-06, FR-16, FR-22
- **Informed By Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Functional Requirements - FR-06, FR-16, FR-22
- **Functional Requirements Coverage:**
  - **FR-06:** MCP Server SHALL provide `validate_artifact` tool accepting artifact content and validation checklist ID, returning pass/fail results with criterion-level details
  - **FR-16:** MCP Server SHALL expose validation checklists as structured data resources (JSON format)
  - **FR-22:** Validation tool SHALL support both automated validation and agent review flags

**Parent High-Level Story:** [HLS-008: MCP Tools - Validation and Path Resolution]
- **Link:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 1: Implement validate_artifact Tool

## User Story
As Claude Code, I want a deterministic validation tool that evaluates artifact quality against structured checklists, so that I provide consistent validation results with <5% error rate instead of 20-30% AI inference errors.

## Description
Currently, Claude Code uses AI inference to validate generated artifacts (PRDs, Epics, Backlog Stories, etc.) against quality checklists embedded in generator prompts. This approach is error-prone (20-30% error rate), token-intensive (~2-5k tokens per validation), and slow (~2 seconds inference time).

This story implements a deterministic Python tool (`validate_artifact`) that:
1. Accepts artifact content (markdown text) and checklist ID (e.g., "prd_validation_v1")
2. Loads validation checklist from JSON resource (FR-16)
3. Evaluates automated criteria deterministically (template sections present, ID format correct, references valid)
4. Flags agent review criteria for AI Agent content review (readability, appropriateness)
5. Returns structured JSON with pass/fail results per criterion

The tool reduces validation errors from 20-30% to <5%, execution time from ~2s to <500ms, and eliminates token consumption for validation operations.

## Implementation Research References

**Primary Research Document:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

**Technical Patterns Applied:**
- **§2.1: Python 3.11+ with Type Safety:** Use Pydantic models for validation input/output schemas with full type hints (ref: Implementation Research §2.1 - Programming Language: Python 3.11+)
- **§2.2: FastAPI Integration:** Expose validation tool as MCP tool via FastAPI with auto-generated OpenAPI documentation (ref: Implementation Research §2.2 - Backend Framework: FastAPI 0.100+)
- **§5.3: Input Validation:** Validate artifact content and checklist ID with Pydantic, reject malformed inputs (ref: Implementation Research §5.3 - Input Validation and Command Injection Prevention)
- **§6.1: Structured Logging:** Log validation invocations with artifact ID, checklist ID, pass/fail counts, duration (ref: Implementation Research §6.1 - Structured Logging)
- **§6.2: Prometheus Metrics:** Instrument validation execution time and pass/fail rates for observability (ref: Implementation Research §6.2 - Prometheus Metrics)

**Anti-Patterns Avoided:**
- **§8.1: Poor Error Handling:** Return structured error responses with retryable flag and suggested action instead of raw exceptions (ref: Implementation Research §8.1 - Pitfall 3)
- **§8.2: Synchronous Blocking Calls:** Use async file I/O to load checklist JSON without blocking event loop (ref: Implementation Research §8.2 - Anti-Pattern 1)

**Performance Considerations:**
- **§2.4: Caching Layer:** Cache loaded validation checklists in memory (TTL: 5 minutes) to avoid repeated JSON file I/O (ref: Implementation Research §2.4 - Caching Layer)

## Functional Requirements
1. Tool accepts two parameters: `artifact_content` (string) and `checklist_id` (string, e.g., "prd_validation_v1")
2. Tool loads validation checklist from configured validation resources directory via URI pattern: `mcp://resources/validation/{checklist_id}`
3. Tool evaluates all automated criteria deterministically:
   - Template sections present (check for markdown headers)
   - ID format correct (regex validation for PRD-XXX, US-XXX, etc.)
   - References valid (check that referenced artifact IDs exist)
   - No placeholder fields remaining (check for [brackets])
4. Tool flags agent review criteria with `requires_agent_review: true`:
   - Readability checks
   - Appropriateness of content
5. Tool returns structured JSON response:
   ```json
   {
     "passed": true/false,
     "automated_pass_rate": 24/26,
     "agent_review_required": 2,
     "results": [
       {
         "id": "CQ-01",
         "category": "content_quality",
         "description": "All template sections present",
         "passed": true,
         "validation_type": "automated",
         "details": "Found 8/8 required sections"
       },
       {
         "id": "CQ-12",
         "category": "content_quality",
         "description": "Readability accessible to cross-functional team",
         "passed": null,
         "validation_type": "agent",
         "requires_agent_review": true,
         "details": "Agent review required for readability assessment"
       }
     ]
   }
   ```
6. Tool execution completes in <500ms p95 (NFR-Performance-02)
7. Tool logs validation invocations with timestamp, artifact type, checklist ID, pass/fail counts, duration

## Non-Functional Requirements
- **Performance:** Validation execution latency <500ms p95 (per PRD-006 NFR-Performance-02)
- **Accuracy:** Deterministic validation (same input → same output, 100% consistency)
- **Reliability:** Handle malformed checklists gracefully, return clear error messages
- **Observability:** Structured logging captures validation patterns for debugging and improvement
- **Maintainability:** Clear separation between checklist loading, criterion evaluation, and result formatting

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** Follow established implementation patterns for MCP tools. Supplement with story-specific validation logic.

**References to Implementation Standards:**
- **prompts/CLAUDE/python/patterns-tooling.md:** Use Taskfile commands (`task test`, `task lint`, `task type-check`)
- **prompts/CLAUDE/python/patterns-testing.md:** Testing patterns (80% coverage, async tests with pytest-asyncio)
- **prompts/CLAUDE/python/patterns-typing.md:** Type hints with mypy strict mode, Pydantic models for validation
- **prompts/CLAUDE/python/patterns-validation.md:** Input validation with Pydantic, security patterns
- **prompts/CLAUDE/python/patterns-architecture.md:** Project structure following established patterns

### Implementation Guidance

**Story-Specific Technical Approach:**

1. **Pydantic Models for Tool Input/Output:**
   ```python
   from pydantic import BaseModel, Field
   from typing import List, Optional, Literal

   class ValidateArtifactInput(BaseModel):
       """Input schema for validate_artifact tool"""
       artifact_content: str = Field(..., description="Full artifact text (markdown)")
       checklist_id: str = Field(
           ...,
           pattern=r'^[a-z_]+_v\d+$',
           description="Validation checklist ID (e.g., 'prd_validation_v1')"
       )

   class CriterionResult(BaseModel):
       """Result for single validation criterion"""
       id: str  # e.g., "CQ-01"
       category: str  # e.g., "content_quality"
       description: str
       passed: Optional[bool]  # None for agent review
       validation_type: Literal["automated", "agent", "manual"]
       requires_agent_review: bool = False
       details: str

   class ValidationResult(BaseModel):
       """Validation tool output"""
       passed: bool
       automated_pass_rate: str  # e.g., "24/26"
       agent_review_required: int
       results: List[CriterionResult]
   ```

2. **Checklist Loading with Caching:**
   ```python
   import json
   import aiofiles
   from pathlib import Path
   from functools import lru_cache
   from datetime import datetime, timedelta
   from config import settings  # Configuration module

   class ChecklistCache:
       def __init__(self, ttl_seconds: int = 300):
           self.ttl_seconds = ttl_seconds
           self._cache: dict[str, tuple[dict, datetime]] = {}

       async def load_checklist(self, checklist_id: str) -> dict:
           """Loads checklist from JSON file with in-memory caching"""
           # Check cache first
           if checklist_id in self._cache:
               checklist, timestamp = self._cache[checklist_id]
               if datetime.utcnow() - timestamp < timedelta(seconds=self.ttl_seconds):
                   return checklist

           # Cache miss - load from file
           # Use configured validation resources path (not hardcoded)
           checklist_path = Path(settings.VALIDATION_RESOURCES_DIR) / f"{checklist_id}.json"
           if not checklist_path.exists():
               raise FileNotFoundError(f"Checklist not found: {checklist_id}")

           async with aiofiles.open(checklist_path, mode='r') as f:
               content = await f.read()
               checklist = json.loads(content)

           # Update cache
           self._cache[checklist_id] = (checklist, datetime.utcnow())
           return checklist

   checklist_cache = ChecklistCache(ttl_seconds=300)
   ```

3. **Automated Criterion Evaluation Logic:**
   ```python
   import re
   from typing import List

   class ArtifactValidator:
       def __init__(self, artifact_content: str):
           self.content = artifact_content
           self.lines = artifact_content.split('\n')

       def check_template_sections(self, required_sections: List[str]) -> tuple[bool, str]:
           """Checks if all required markdown sections present"""
           headers = [line for line in self.lines if line.startswith('#')]
           found_sections = [h.strip('# ').lower() for h in headers]

           missing = [s for s in required_sections if s.lower() not in found_sections]
           if missing:
               return False, f"Missing sections: {', '.join(missing)}"
           return True, f"Found {len(required_sections)}/{len(required_sections)} required sections"

       def check_id_format(self, id_pattern: str) -> tuple[bool, str]:
           """Validates artifact ID format using regex"""
           match = re.search(id_pattern, self.content)
           if not match:
               return False, f"ID format does not match pattern: {id_pattern}"
           return True, f"ID format valid: {match.group(0)}"

       def check_no_placeholders(self) -> tuple[bool, str]:
           """Checks for remaining placeholder brackets"""
           placeholders = re.findall(r'\[.*?\]', self.content)
           # Filter out valid markdown links
           placeholders = [p for p in placeholders if not p.startswith('[') or '](http' not in self.content]
           if placeholders:
               return False, f"Found {len(placeholders)} placeholders: {placeholders[:3]}"
           return True, "No placeholder fields remaining"

       def check_references_valid(self, reference_pattern: str) -> tuple[bool, str]:
           """Validates that referenced artifact IDs exist (simplified - checks format only)"""
           references = re.findall(reference_pattern, self.content)
           if not references:
               return False, "No references found"
           return True, f"Found {len(references)} valid references"
   ```

4. **MCP Tool Implementation:**
   ```python
   from mcp.server.fastmcp import FastMCP
   import structlog

   mcp = FastMCP(name="MCPServer", version="1.0.0")
   logger = structlog.get_logger()

   @mcp.tool(
       name="validate_artifact",
       description="""
       Validates generated artifact against structured validation checklist.

       Use this tool when:
       - You have generated a new artifact (PRD, Epic, Backlog Story, etc.)
       - You need to verify artifact quality before presenting to user
       - You want deterministic validation instead of AI inference

       Returns pass/fail results for each validation criterion with:
       - Automated criteria: evaluated deterministically by script
       - Agent review criteria: flagged for AI Agent content review

       Reduces validation errors from 20-30% (AI inference) to <5% (deterministic).
       """
   )
   async def validate_artifact(params: ValidateArtifactInput) -> ValidationResult:
       """Validates artifact content against validation checklist"""
       start_time = time.time()

       try:
           # Load checklist from cache
           checklist = await checklist_cache.load_checklist(params.checklist_id)

           # Initialize validator
           validator = ArtifactValidator(params.artifact_content)

           # Evaluate each criterion
           results = []
           automated_pass_count = 0
           automated_total_count = 0
           agent_review_count = 0

           for criterion in checklist["criteria"]:
               if criterion["validation_type"] == "automated":
                   automated_total_count += 1
                   passed, details = evaluate_criterion(validator, criterion)
                   if passed:
                       automated_pass_count += 1
                   results.append(CriterionResult(
                       id=criterion["id"],
                       category=criterion["category"],
                       description=criterion["description"],
                       passed=passed,
                       validation_type="automated",
                       details=details
                   ))
               elif criterion["validation_type"] == "agent":
                   agent_review_count += 1
                   results.append(CriterionResult(
                       id=criterion["id"],
                       category=criterion["category"],
                       description=criterion["description"],
                       passed=None,
                       validation_type="agent",
                       requires_agent_review=True,
                       details="Agent review required for subjective assessment"
                   ))
               else:  # manual
                   results.append(CriterionResult(
                       id=criterion["id"],
                       category=criterion["category"],
                       description=criterion["description"],
                       passed=None,
                       validation_type="manual",
                       details="Manual review required for subjective assessment"
                   ))

           # Determine overall pass/fail
           passed = (automated_pass_count == automated_total_count)

           # Log validation invocation
           duration_ms = (time.time() - start_time) * 1000
           logger.info(
               "validation_completed",
               checklist_id=params.checklist_id,
               automated_pass_rate=f"{automated_pass_count}/{automated_total_count}",
               agent_review_count=agent_review_count,
               passed=passed,
               duration_ms=duration_ms
           )

           return ValidationResult(
               passed=passed,
               automated_pass_rate=f"{automated_pass_count}/{automated_total_count}",
               agent_review_required=agent_review_count,
               results=results
           )

       except FileNotFoundError as e:
           logger.error("checklist_not_found", checklist_id=params.checklist_id, error=str(e))
           raise HTTPException(status_code=404, detail=f"Checklist not found: {params.checklist_id}")
       except Exception as e:
           logger.error("validation_error", error=str(e))
           raise HTTPException(status_code=500, detail="Validation failed due to internal error")

   def evaluate_criterion(validator: ArtifactValidator, criterion: dict) -> tuple[bool, str]:
       """Maps criterion to appropriate validation method"""
       check_type = criterion.get("check_type")

       if check_type == "template_sections":
           return validator.check_template_sections(criterion["required_sections"])
       elif check_type == "id_format":
           return validator.check_id_format(criterion["pattern"])
       elif check_type == "no_placeholders":
           return validator.check_no_placeholders()
       elif check_type == "references_valid":
           return validator.check_references_valid(criterion["pattern"])
       else:
           return False, f"Unknown check type: {check_type}"
   ```

5. **Testing Strategy:**
   - Unit tests: Validate individual criterion checks (template sections, ID format, placeholders)
   - Integration tests: Validate full PRD artifact with 26-criterion checklist
   - Performance tests: Verify <500ms p95 latency with 10 sample artifacts
   - Cache tests: Verify checklist caching behavior (TTL expiration)

### Technical Tasks
- [ ] Implement Pydantic models for tool input/output
- [ ] Implement checklist loading with in-memory caching (TTL: 5 minutes)
- [ ] Implement ArtifactValidator class with criterion evaluation methods
- [ ] Implement MCP tool endpoint with FastMCP decorator
- [ ] Add structured logging for validation invocations
- [ ] Add Prometheus metrics for validation latency and pass/fail rates
- [ ] Write unit tests for ArtifactValidator methods (80% coverage)
- [ ] Write integration tests with full PRD validation
- [ ] Write performance tests (<500ms p95 validation)
- [ ] Add Taskfile commands for running validation tool tests

## Acceptance Criteria

### Scenario 1: PRD validation with all automated criteria passing
**Given** Claude Code has generated PRD-006 artifact
**When** Claude Code calls `validate_artifact(artifact_content=prd_text, checklist_id="prd_validation_v1")`
**Then** tool loads prd_validation_v1.json checklist from configured validation resources directory
**And** tool evaluates 24 automated criteria deterministically
**And** tool returns `{passed: true, automated_pass_rate: "24/24", agent_review_required: 2}`
**And** response includes detailed results for all 26 criteria
**And** execution completes in <500ms

### Scenario 2: Epic validation with missing template section
**Given** Claude Code has generated Epic-006 artifact missing "Risks" section
**When** Claude Code calls `validate_artifact(artifact_content=epic_text, checklist_id="epic_validation_v1")`
**Then** tool evaluates template sections criterion
**And** criterion CQ-02 returns `{passed: false, details: "Missing sections: Risks"}`
**And** overall result returns `{passed: false, automated_pass_rate: "23/24"}`
**And** failed criterion clearly identified in results array

### Scenario 3: Agent review criteria flagged
**Given** Claude Code has generated Backlog Story artifact
**When** Claude Code calls `validate_artifact(artifact_content=story_text, checklist_id="backlog_story_validation_v1")`
**Then** tool evaluates automated criteria and flags agent review criteria
**And** agent criterion CQ-12 (Readability) returns `{passed: null, validation_type: "agent", requires_agent_review: true}`
**And** response includes `agent_review_required: 2` count
**And** Claude Code performs agent review before presenting to user

### Scenario 4: Checklist not found error
**Given** Claude Code requests validation with unknown checklist ID
**When** Claude Code calls `validate_artifact(artifact_content=text, checklist_id="unknown_v1")`
**Then** tool returns 404 error
**And** error message includes: "Checklist not found: unknown_v1"
**And** error logged with checklist_id for debugging

### Scenario 5: Validation execution logged
**Given** Claude Code calls validate_artifact tool
**When** validation completes
**Then** tool logs structured event with fields: checklist_id, automated_pass_rate, agent_review_count, passed, duration_ms
**And** log format is JSON (structured logging)
**And** log includes timestamp and validation success/failure

### Scenario 6: Performance target met
**Given** 10 sample artifacts (PRD, Epic, HLS, Backlog Story)
**When** Each artifact validated 100 times
**Then** p95 latency <500ms for all artifact types
**And** p99 latency <1000ms
**And** Prometheus metrics capture latency histogram

### Scenario 7: Checklist caching reduces I/O
**Given** Checklist loaded once from disk
**When** Same checklist requested 100 times within 5 minutes
**Then** Checklist loaded from memory cache (not disk)
**And** Cache hit rate >99%
**And** Latency improved by >50% vs. no caching

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Needed

**Rationale:**
- **Story Points:** 8 SP (exceeds 5 SP threshold - DON'T SKIP per decision matrix)
- **Developer Count:** Potentially multiple developers (validation logic + caching + testing + observability)
- **Domain Span:** Cross-domain (backend tool implementation, file I/O, caching, observability)
- **Complexity:** High - involves criterion evaluation logic, caching strategy, performance optimization
- **Uncertainty:** Low-moderate - clear implementation approach but criterion evaluation requires careful testing
- **Override Factors:** None (complexity and SP threshold sufficient)

Per SDLC Section 11.6 Decision Matrix: "5+ SP, any team size → DON'T SKIP (Complexity requires decomposition)".

**Proposed Implementation Tasks** (TASK IDs to be allocated):
- **TASK-XXX:** Implement Pydantic models and checklist loading with caching (4-6 hours)
  - Input/output Pydantic models
  - ChecklistCache class with TTL
  - Async JSON file loading

- **TASK-YYY:** Implement ArtifactValidator with criterion evaluation logic (6-8 hours)
  - ArtifactValidator class
  - Criterion evaluation methods (template sections, ID format, placeholders, references)
  - Mapping logic from criterion to validation method

- **TASK-ZZZ:** Implement MCP tool endpoint with observability (3-4 hours)
  - FastMCP tool decorator
  - Structured logging integration
  - Prometheus metrics instrumentation

- **TASK-AAA:** Comprehensive testing (unit, integration, performance) (6-8 hours)
  - Unit tests for ArtifactValidator methods
  - Integration tests with full PRD validation
  - Performance tests for <500ms p95 target
  - Cache behavior tests
  - 80% coverage target

**Total Estimated Task Hours:** 19-26 hours (aligns with 8 SP estimate)

**Note:** TASK IDs to be allocated in TODO.md during sprint planning.

## Definition of Done
- [ ] Pydantic models implemented for tool input/output
- [ ] Checklist loading with in-memory caching (TTL: 5 minutes)
- [ ] ArtifactValidator class with criterion evaluation methods
- [ ] MCP tool endpoint implemented with FastMCP
- [ ] Structured logging for validation invocations
- [ ] Prometheus metrics for latency and pass/fail rates
- [ ] Unit tests written and passing (80% coverage)
- [ ] Integration tests passing (full PRD validation)
- [ ] Performance tests passing (<500ms p95 latency)
- [ ] Manual testing: Validate PRD-006 artifact with tool
- [ ] Taskfile commands added for validation tool tests
- [ ] Product Owner approval obtained

## Additional Information
**Suggested Labels:** mcp-tools, validation, performance, critical
**Estimated Story Points:** 8
**Dependencies:**
- **Depends On:** US-041 (validation checklists must exist as JSON resources)
- **Blocks:** US-046 (tool invocation logging depends on validate_artifact working)
- **Blocks:** US-047 (integration testing depends on all tools including validation)

**Related PRD Section:** PRD-006 §Functional Requirements - FR-06, FR-16, FR-22

## Decisions Made

**Decision 1: Three-tier validation approach (automated → agent → manual)**
- **Made:** During v2 refinement (feedback from US-040-047_v1_comments.md)
- **Rationale:** AI Agent should perform content review first before flagging for human review. Deterministic validation (automated) → AI content review (agent) → human review (manual) provides better quality control and reduces unnecessary human intervention
- **Impact:** Changed `requires_manual_review` to `requires_agent_review` flag, added `validation_type: "agent"` tier

**Decision 2: Externalize validation resources directory path**
- **Made:** During v2 refinement (feedback from US-040-047_v1_comments.md)
- **Rationale:** Hardcoded paths prevent configuration flexibility and testing with different directory structures
- **Impact:** Use `settings.VALIDATION_RESOURCES_DIR` from configuration instead of hardcoded `"resources/validation/"` path

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md` (§2.1 Python Type Safety, §2.2 FastAPI, §5.3 Input Validation, §6.1 Structured Logging, §6.2 Prometheus Metrics)
- **Feedback:** `/feedback/US-040-047_v1_comments.md`
