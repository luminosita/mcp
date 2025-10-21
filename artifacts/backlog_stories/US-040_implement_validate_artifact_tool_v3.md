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
  - **FR-06:** MCP Server SHALL provide `validate_artifact` tool accepting artifact content and artifact ID, returning pass/fail results with criterion-level details
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
1. Accepts artifact content (markdown text) and artifact ID (e.g., "EPIC-006", "PRD-006", "US-040")
2. Infers artifact type from artifact ID prefix (EPIC → epic, PRD → prd, US → backlog_story)
3. Constructs checklist ID from artifact type (epic → epic_validation_v1)
4. Loads validation checklist from JSON resource (FR-16)
5. Evaluates automated criteria deterministically (template sections present, ID format correct, references valid)
6. Flags agent review criteria for AI Agent content review (readability, appropriateness)
7. Returns structured JSON with pass/fail results per criterion

The tool reduces validation errors from 20-30% to <5%, execution time from ~2s to <500ms, and eliminates token consumption for validation operations.

## Implementation Research References

**Primary Research Document:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

**Technical Patterns Applied:**
- **§2.1: Python 3.11+ with Type Safety:** Use Pydantic models for validation input/output schemas with full type hints (ref: Implementation Research §2.1 - Programming Language: Python 3.11+)
- **§2.2: FastAPI Integration:** Expose validation tool as MCP tool via FastAPI with auto-generated OpenAPI documentation (ref: Implementation Research §2.2 - Backend Framework: FastAPI 0.100+)
- **§5.3: Input Validation:** Validate artifact content and artifact ID with Pydantic, reject malformed inputs (ref: Implementation Research §5.3 - Input Validation and Command Injection Prevention)
- **§6.1: Structured Logging:** Log validation invocations with artifact ID, checklist ID, pass/fail counts, duration (ref: Implementation Research §6.1 - Structured Logging)
- **§6.2: Prometheus Metrics:** Instrument validation execution time and pass/fail rates for observability (ref: Implementation Research §6.2 - Prometheus Metrics)

**Anti-Patterns Avoided:**
- **§8.1: Poor Error Handling:** Return structured error responses with retryable flag and suggested action instead of raw exceptions (ref: Implementation Research §8.1 - Pitfall 3)
- **§8.2: Synchronous Blocking Calls:** Use async file I/O to load checklist JSON without blocking event loop (ref: Implementation Research §8.2 - Anti-Pattern 1)

**Performance Considerations:**
- **§2.4: Caching Layer:** Cache loaded validation checklists in memory (TTL: 5 minutes) to avoid repeated JSON file I/O (ref: Implementation Research §2.4 - Caching Layer)

## Functional Requirements
1. Tool accepts three parameters:
   - `artifact_content` (string): Full artifact markdown text
   - `artifact_id` (string): Full artifact ID with prefix (e.g., "EPIC-006", "PRD-006", "US-040")
   - `task_id` (string, mandatory): Task tracking ID for log correlation
2. Tool infers artifact type from artifact ID prefix:
   - EPIC-XXX → epic
   - PRD-XXX → prd
   - HLS-XXX → hls
   - US-XXX → backlog_story
   - SPEC-XXX → tech_spec
   - ADR-XXX → adr
   - SPIKE-XXX → spike
   - TASK-XXX → task
   - VIS-XXX → product_vision
   - INIT-XXX → initiative
3. Tool constructs checklist ID from artifact type:
   - epic → epic_validation_v1
   - prd → prd_validation_v1
   - backlog_story → backlog_story_validation_v1
   - (Always uses latest version: v1)
4. Tool loads validation checklist from configured validation resources directory via constructed checklist ID
5. Tool evaluates all automated criteria deterministically:
   - Template sections present (check for markdown headers)
   - ID format correct (regex validation for PRD-XXX, US-XXX, etc.)
   - References valid (check that referenced artifact IDs exist)
   - No placeholder fields remaining (check for [brackets])
6. Tool flags agent review criteria with `requires_agent_review: true`:
   - Readability checks
   - Appropriateness of content
7. Tool returns structured JSON response:
   ```json
   {
     "passed": true/false,
     "automated_pass_rate": "24/26",
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
8. Tool execution completes in <500ms p95 (NFR-Performance-02)
9. Tool logs validation invocations with timestamp, task_id, artifact ID, checklist ID, pass/fail counts, duration

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
   from pydantic import BaseModel, Field, validator
   from typing import List, Optional, Literal

   class ValidateArtifactInput(BaseModel):
       """Input schema for validate_artifact tool"""
       artifact_content: str = Field(..., description="Full artifact text (markdown)")
       artifact_id: str = Field(
           ...,
           pattern=r'^[A-Z]+-\d{3,}$',
           description="Full artifact ID (e.g., 'EPIC-006', 'US-040')"
       )
       task_id: str = Field(..., description="Task tracking ID for log correlation")

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

2. **Artifact Type and Checklist ID Inference:**
   ```python
   class ArtifactTypeInference:
       """Infers artifact type and checklist ID from artifact ID"""

       TYPE_PREFIX_MAP = {
           "EPIC": "epic",
           "PRD": "prd",
           "HLS": "hls",
           "US": "backlog_story",
           "SPEC": "tech_spec",
           "ADR": "adr",
           "SPIKE": "spike",
           "TASK": "task",
           "VIS": "product_vision",
           "INIT": "initiative"
       }

       @classmethod
       def infer_artifact_type(cls, artifact_id: str) -> str:
           """Infers artifact type from ID prefix"""
           prefix = artifact_id.split('-')[0]
           if prefix not in cls.TYPE_PREFIX_MAP:
               raise ValueError(
                   f"Unknown artifact ID prefix: {prefix}. "
                   f"Valid prefixes: {', '.join(cls.TYPE_PREFIX_MAP.keys())}"
               )
           return cls.TYPE_PREFIX_MAP[prefix]

       @classmethod
       def infer_checklist_id(cls, artifact_id: str) -> str:
           """Infers checklist ID from artifact ID"""
           artifact_type = cls.infer_artifact_type(artifact_id)
           return f"{artifact_type}_validation_v1"

       @classmethod
       def validate_id_format(cls, artifact_id: str, expected_type: Optional[str] = None) -> bool:
           """Validates artifact ID matches expected type"""
           try:
               inferred_type = cls.infer_artifact_type(artifact_id)
               if expected_type and inferred_type != expected_type:
                   raise ValueError(
                       f"Artifact ID '{artifact_id}' has type '{inferred_type}', "
                       f"expected '{expected_type}'"
                   )
               return True
           except ValueError:
               return False
   ```

3. **Checklist Loading with Caching:**
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

4. **Automated Criterion Evaluation Logic:**
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

5. **MCP Tool Implementation:**
   ```python
   from mcp.server.fastmcp import FastMCP
   import structlog
   import time

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

       Input:
       - artifact_content: Full markdown text
       - artifact_id: Full artifact ID (e.g., "EPIC-006", "US-040")
       - task_id: Task tracking ID for log correlation

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
           # Infer checklist ID from artifact ID
           checklist_id = ArtifactTypeInference.infer_checklist_id(params.artifact_id)
           artifact_type = ArtifactTypeInference.infer_artifact_type(params.artifact_id)

           # Load checklist from cache
           checklist = await checklist_cache.load_checklist(checklist_id)

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
               task_id=params.task_id,
               artifact_id=params.artifact_id,
               artifact_type=artifact_type,
               checklist_id=checklist_id,
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
           logger.error("checklist_not_found", task_id=params.task_id, artifact_id=params.artifact_id, checklist_id=checklist_id, error=str(e))
           raise  # Re-raise for FastMCP ErrorHandlingMiddleware (→ JSON-RPC -32001)
       except ValueError as e:
           logger.error("invalid_artifact_id", task_id=params.task_id, artifact_id=params.artifact_id, error=str(e))
           raise  # Re-raise for FastMCP ErrorHandlingMiddleware (→ JSON-RPC -32602)
       except Exception as e:
           logger.error("validation_error", task_id=params.task_id, artifact_id=params.artifact_id, error=str(e))
           raise  # Re-raise for FastMCP ErrorHandlingMiddleware (→ JSON-RPC -32603)

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

6. **Testing Strategy:**
   - Unit tests: Validate individual criterion checks (template sections, ID format, placeholders)
   - Unit tests: Validate artifact type inference (EPIC-006 → epic → epic_validation_v1)
   - Integration tests: Validate full PRD artifact with 26-criterion checklist
   - Performance tests: Verify <500ms p95 latency with 10 sample artifacts
   - Cache tests: Verify checklist caching behavior (TTL expiration)
   - Error tests: Invalid artifact ID prefix rejected with clear error

### Technical Tasks
- [ ] Implement Pydantic models for tool input/output
- [ ] Implement ArtifactTypeInference class with prefix mapping
- [ ] Implement checklist ID inference from artifact ID
- [ ] Implement checklist loading with in-memory caching (TTL: 5 minutes)
- [ ] Implement ArtifactValidator class with criterion evaluation methods
- [ ] Implement MCP tool endpoint with FastMCP decorator
- [ ] Add structured logging for validation invocations (with task_id)
- [ ] Add Prometheus metrics for validation latency and pass/fail rates
- [ ] Write unit tests for artifact type inference (80% coverage)
- [ ] Write unit tests for ArtifactValidator methods (80% coverage)
- [ ] Write integration tests with full PRD validation
- [ ] Write error tests for invalid artifact ID prefixes
- [ ] Write performance tests (<500ms p95 validation)
- [ ] Add Taskfile commands for running validation tool tests

## Acceptance Criteria

### Scenario 1: PRD validation with artifact ID inference
**Given** Claude Code has generated PRD-006 artifact
**When** Claude Code calls `validate_artifact(artifact_content=prd_text, artifact_id="PRD-006", task_id="task-123")`
**Then** tool infers artifact_type="prd" from artifact_id prefix
**And** tool constructs checklist_id="prd_validation_v1"
**And** tool loads prd_validation_v1.json checklist from configured validation resources directory
**And** tool evaluates 24 automated criteria deterministically
**And** tool returns `{passed: true, automated_pass_rate: "24/24", agent_review_required: 2}`
**And** response includes detailed results for all 26 criteria
**And** execution completes in <500ms

### Scenario 2: Epic validation with missing template section
**Given** Claude Code has generated Epic-006 artifact missing "Risks" section
**When** Claude Code calls `validate_artifact(artifact_content=epic_text, artifact_id="EPIC-006", task_id="task-123")`
**Then** tool infers checklist_id="epic_validation_v1"
**And** tool evaluates template sections criterion
**And** criterion CQ-02 returns `{passed: false, details: "Missing sections: Risks"}`
**And** overall result returns `{passed: false, automated_pass_rate: "23/24"}`
**And** failed criterion clearly identified in results array

### Scenario 3: Backlog Story validation with correct inference
**Given** Claude Code has generated Backlog Story US-040
**When** Claude Code calls `validate_artifact(artifact_content=story_text, artifact_id="US-040", task_id="task-123")`
**Then** tool infers artifact_type="backlog_story" from "US" prefix
**And** tool constructs checklist_id="backlog_story_validation_v1"
**And** tool loads backlog_story_validation_v1.json
**And** validation proceeds with correct checklist

### Scenario 4: Invalid artifact ID prefix rejected
**Given** Claude Code provides invalid artifact ID
**When** Claude Code calls `validate_artifact(artifact_content=text, artifact_id="INVALID-006", task_id="task-123")`
**Then** tool returns 400 error
**And** error message includes: "Unknown artifact ID prefix: INVALID. Valid prefixes: EPIC, PRD, HLS, US, SPEC, ADR, SPIKE, TASK, VIS, INIT"
**And** error logged with task_id for debugging

### Scenario 5: Agent review criteria flagged
**Given** Claude Code has generated Backlog Story artifact
**When** Claude Code calls `validate_artifact(artifact_content=story_text, artifact_id="US-040", task_id="task-123")`
**Then** tool evaluates automated criteria and flags agent review criteria
**And** agent criterion CQ-12 (Readability) returns `{passed: null, validation_type: "agent", requires_agent_review: true}`
**And** response includes `agent_review_required: 2` count
**And** Claude Code performs agent review before presenting to user

### Scenario 6: Validation execution logged with task_id
**Given** Claude Code calls validate_artifact tool
**When** Validation completes
**Then** tool logs structured event with fields: task_id, artifact_id, artifact_type, checklist_id, automated_pass_rate, agent_review_count, passed, duration_ms
**And** log format is JSON (structured logging)
**And** log includes task_id for correlation with other tool calls

### Scenario 7: Performance target met
**Given** 10 sample artifacts (PRD, Epic, HLS, Backlog Story)
**When** Each artifact validated 100 times
**Then** p95 latency <500ms for all artifact types
**And** p99 latency <1000ms
**And** Prometheus metrics capture latency histogram

### Scenario 8: Checklist caching reduces I/O
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
- **Developer Count:** Potentially multiple developers (validation logic + inference + caching + testing + observability)
- **Domain Span:** Cross-domain (backend tool implementation, file I/O, caching, observability, type inference)
- **Complexity:** High - involves criterion evaluation logic, artifact type inference, caching strategy, performance optimization
- **Uncertainty:** Low-moderate - clear implementation approach but inference and criterion evaluation require careful testing
- **Override Factors:** None (complexity and SP threshold sufficient)

Per SDLC Section 11.6 Decision Matrix: "5+ SP, any team size → DON'T SKIP (Complexity requires decomposition)".

**Proposed Implementation Tasks** (TASK IDs to be allocated):
- **TASK-AAA:** Implement Pydantic models and artifact type inference (4-6 hours)
  - Input/output Pydantic models
  - ArtifactTypeInference class with TYPE_PREFIX_MAP
  - Validation of artifact ID format

- **TASK-BBB:** Implement checklist loading with caching (4-6 hours)
  - ChecklistCache class with TTL
  - Async JSON file loading
  - Cache hit/miss logic

- **TASK-CCC:** Implement ArtifactValidator with criterion evaluation logic (6-8 hours)
  - ArtifactValidator class
  - Criterion evaluation methods (template sections, ID format, placeholders, references)
  - Mapping logic from criterion to validation method

- **TASK-DDD:** Implement MCP tool endpoint with observability (3-4 hours)
  - FastMCP tool decorator
  - Structured logging integration with task_id
  - Prometheus metrics instrumentation

- **TASK-EEE:** Comprehensive testing (unit, integration, performance) (6-8 hours)
  - Unit tests for ArtifactTypeInference (prefix inference)
  - Unit tests for ArtifactValidator methods
  - Integration tests with full PRD validation
  - Performance tests for <500ms p95 target
  - Cache behavior tests
  - Error tests for invalid artifact ID
  - 80% coverage target

**Total Estimated Task Hours:** 23-32 hours (aligns with 8 SP estimate)

**Note:** TASK IDs to be allocated in TODO.md during sprint planning.

## Definition of Done
- [ ] Pydantic models implemented for tool input/output
- [ ] ArtifactTypeInference class with prefix mapping implemented
- [ ] Checklist ID inference from artifact ID implemented
- [ ] Checklist loading with in-memory caching (TTL: 5 minutes)
- [ ] ArtifactValidator class with criterion evaluation methods
- [ ] MCP tool endpoint implemented with FastMCP
- [ ] Structured logging for validation invocations (with task_id)
- [ ] Prometheus metrics for latency and pass/fail rates
- [ ] Unit tests written and passing (80% coverage, includes inference tests)
- [ ] Integration tests passing (full PRD validation)
- [ ] Error tests passing (invalid artifact ID prefix)
- [ ] Performance tests passing (<500ms p95 latency)
- [ ] Manual testing: Validate PRD-006, EPIC-006, US-040 artifacts with tool
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

**Decision 3: Infer checklist_id from artifact_id (remove explicit parameter)**
- **Made:** During v3 refinement (feedback from US-040-047_v2_comments.md)
- **Rationale:** Checklist ID is fully deterministic from artifact_id. Artifact ID format is `{TYPE}-{ID}` (e.g., EPIC-006, US-040), allowing prefix extraction and type inference. This eliminates client-side parameter errors and ensures latest checklist version always used
- **Impact:**
  - Removed `checklist_id` parameter from ValidateArtifactInput
  - Added `artifact_id` parameter (e.g., "EPIC-006", "US-040")
  - Added ArtifactTypeInference class with TYPE_PREFIX_MAP
  - Tool now infers: artifact_id → artifact_type → checklist_id
  - Simpler client interface (one less parameter)
  - Validation errors for unknown artifact ID prefixes
- **Alternative Considered:** Keep checklist_id parameter for flexibility, but artifact type is always 1:1 mapped to checklist, making explicit parameter redundant

**Decision 4: Rename request_id → task_id (mandatory parameter)**
- **Made:** During v3 refinement (feedback from US-040-047_v2_comments.md)
- **Rationale:** "task_id" provides better visibility and traceability in logs. Naming aligns with task tracking system terminology. Mandatory parameter ensures all tool invocations are correlated
- **Impact:**
  - Parameter renamed: `request_id: str = None` → `task_id: str` (mandatory)
  - All logging updated to use `task_id` field
  - Function signature change across all tool calls
  - Better log correlation with task tracking microservice

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md` (§2.1 Python Type Safety, §2.2 FastAPI, §5.3 Input Validation, §6.1 Structured Logging, §6.2 Prometheus Metrics)
- **Feedback v1:** `/feedback/US-040-047_v1_comments.md`
- **Feedback v2:** `/feedback/US-040-047_v2_comments.md`
- **Changes Applied:** `/feedback/US-040-047_v2_changes_applied.md`
