# User Story: Migrate Validation Checklists to JSON Resources

## Metadata
- **Story ID:** US-041
- **Title:** Migrate Validation Checklists to JSON Resources
- **Type:** Feature
- **Status:** Draft
- **Priority:** High (enables dynamic checklist updates without code changes)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-008 (MCP Tools - Validation and Path Resolution)
- **Functional Requirements Covered:** FR-16
- **Informed By Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Functional Requirements - FR-16
- **Functional Requirements Coverage:**
  - **FR-16:** MCP Server SHALL expose validation checklists as structured data resources (JSON format) allowing dynamic checklist updates without MCP Server code changes

**Parent High-Level Story:** [HLS-008: MCP Tools - Validation and Path Resolution]
- **Link:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 2: Migrate Validation Checklists to JSON Resources

## User Story
As a Framework Maintainer, I want validation checklists stored as structured JSON resources accessible via MCP protocol, so that I can update validation criteria without code changes or redeployment.

## Description
Validation checklists are currently embedded in generator XML prompts as markdown-formatted criterion lists. This creates several problems:
1. **Code Changes Required:** Adding/updating validation criteria requires editing generator code and redeploying MCP Server
2. **Duplication:** Same criteria repeated across multiple generators (e.g., "ID format valid" appears in Epic, PRD, HLS, Backlog Story generators)
3. **Inconsistency Risk:** Manual updates across N generators can miss criteria or introduce typos
4. **No Versioning:** Cannot track checklist version history or roll back changes

This story migrates validation checklists to JSON resources served via MCP protocol:
- Extract existing checklists from all generator prompts (12 total: Product Vision, Initiative, Epic, PRD, HLS, Backlog Story, Tech Spec, ADR, Spike, Implementation Task, Business Research, Implementation Research)
- Convert to structured JSON format with fields: id, category, description, validation_type (automated/agent/manual), check_type (template_sections/id_format/etc.)
- Store as versioned resources at configured validation directory: `{VALIDATION_RESOURCES_DIR}/{artifact_type}_validation_v1.json`
- Expose via MCP resource URI: `mcp://resources/validation/{artifact_type}_validation_v1`
- Update `validate_artifact` tool to load checklists dynamically from resources (not hardcoded)

After implementation, Framework Maintainers can update validation criteria by editing JSON files and restarting MCP Server (no code changes).

## Implementation Research References

**Primary Research Document:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

**Technical Patterns Applied:**
- **§2.1: Python 3.11+ with Type Safety:** Use Pydantic models to validate JSON checklist schema (ref: Implementation Research §2.1 - Programming Language: Python 3.11+)
- **§5.3: Input Validation:** Validate checklist JSON against Pydantic schema on load, fail fast if schema invalid (ref: Implementation Research §5.3 - Input Validation and Command Injection Prevention)
- **§6.1: Structured Logging:** Log checklist loading events (file path, criteria count, version) (ref: Implementation Research §6.1 - Structured Logging)

**Anti-Patterns Avoided:**
- **§8.2: Storing State in Server Instance Variables:** Checklists loaded from disk on each request with caching (no global state) (ref: Implementation Research §8.2 - Anti-Pattern 2)

**Performance Considerations:**
- **§2.4: Caching Layer:** Checklist JSON files cached in memory (TTL: 5 minutes, same as US-040 validation tool) to avoid repeated file I/O (ref: Implementation Research §2.4 - Caching Layer)

## Functional Requirements
1. Extract validation criteria from all 12 generator prompts:
   - product-vision-generator.xml
   - initiative-generator.xml
   - epic-generator.xml
   - prd-generator.xml
   - high-level-user-story-generator.xml
   - backlog-story-generator.xml
   - tech-spec-generator.xml
   - adr-generator.xml
   - spike-generator.xml
   - implementation-task-generator.xml
   - business-research-generator.xml
   - implementation-research-generator.xml
2. Convert each checklist to JSON format with fields:
   - `id`: Criterion identifier (e.g., "CQ-01", "UT-02", "CC-03")
   - `category`: Criterion category (e.g., "content_quality", "traceability", "consistency")
   - `description`: Human-readable description
   - `validation_type`: "automated", "agent", or "manual"
   - `check_type`: For automated criteria, specifies check algorithm (e.g., "template_sections", "id_format", "no_placeholders", "references_valid")
   - `pattern`: For regex-based checks, the regex pattern
   - `required_sections`: For template section checks, list of required section headers
3. Store JSON files at configured validation directory: `{VALIDATION_RESOURCES_DIR}/{artifact_type}_validation_v1.json`
   - product_vision_validation_v1.json
   - initiative_validation_v1.json
   - epic_validation_v1.json
   - prd_validation_v1.json
   - hls_validation_v1.json
   - backlog_story_validation_v1.json
   - tech_spec_validation_v1.json
   - adr_validation_v1.json
   - spike_validation_v1.json
   - implementation_task_validation_v1.json
   - business_research_validation_v1.json
   - implementation_research_validation_v1.json
4. Implement Pydantic schema for checklist validation:
   ```python
   class ValidationCriterion(BaseModel):
       id: str
       category: str
       description: str
       validation_type: Literal["automated", "agent", "manual"]
       check_type: Optional[str] = None  # e.g., "template_sections"
       pattern: Optional[str] = None  # Regex pattern
       required_sections: Optional[List[str]] = None

   class ValidationChecklist(BaseModel):
       artifact_type: str
       version: int
       criteria: List[ValidationCriterion]
   ```
5. Update `validate_artifact` tool to load checklists from JSON resources (not hardcoded)
6. MCP Server exposes checklists via resource URI: `mcp://resources/validation/{checklist_id}`

## Non-Functional Requirements
- **Maintainability:** Checklists editable without code changes (edit JSON, restart server)
- **Consistency:** Single source of truth for validation criteria (no duplication across generators)
- **Versioning:** Checklist files versioned (v1, v2, v3) to support backward compatibility
- **Reliability:** Invalid JSON files rejected on load with clear error messages
- **Observability:** Structured logging captures checklist loading events

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** Follow established implementation patterns. Supplement with story-specific JSON schema and migration process.

**References to Implementation Standards:**
- **prompts/CLAUDE/python/patterns-tooling.md:** Use Taskfile commands for testing
- **prompts/CLAUDE/python/patterns-typing.md:** Pydantic models for JSON schema validation
- **prompts/CLAUDE/python/patterns-validation.md:** Input validation patterns
- **prompts/CLAUDE/python/patterns-testing.md:** Testing patterns (80% coverage)

### Implementation Guidance

**Story-Specific Technical Approach:**

1. **JSON Checklist Schema Example (PRD Validation):**
   ```json
   {
     "artifact_type": "prd",
     "version": 1,
     "criteria": [
       {
         "id": "CQ-01",
         "category": "content_quality",
         "description": "All template sections present",
         "validation_type": "automated",
         "check_type": "template_sections",
         "required_sections": [
           "Metadata",
           "Executive Summary",
           "Background & Context",
           "Problem Statement",
           "Goals & Success Metrics",
           "User Personas & Use Cases",
           "Requirements",
           "User Experience",
           "Technical Considerations",
           "Risks & Mitigations",
           "Timeline & Milestones",
           "Decisions Made",
           "Related Documents",
           "Version History",
           "Appendix"
         ]
       },
       {
         "id": "CQ-02",
         "category": "content_quality",
         "description": "PRD ID format valid",
         "validation_type": "automated",
         "check_type": "id_format",
         "pattern": "^PRD-\\d{3,}$"
       },
       {
         "id": "CC-03",
         "category": "consistency",
         "description": "No placeholder fields remaining",
         "validation_type": "automated",
         "check_type": "no_placeholders"
       },
       {
         "id": "CQ-12",
         "category": "content_quality",
         "description": "Readability accessible to cross-functional team",
         "validation_type": "agent"
       }
     ]
   }
   ```

2. **Migration Process:**
   - Extract criteria from each generator's `<validation_checklist>` section
   - Map markdown criteria to JSON fields:
     - Extract criterion ID (CQ-01, UT-02, etc.) from markdown header
     - Extract category from section grouping
     - Extract description from criterion text
     - Classify as automated/agent/manual based on:
       - Automated: Objective, deterministic checks (sections present, ID format, placeholders)
       - Agent: Subjective content quality checks requiring AI review (readability, appropriateness, clarity)
       - Manual: Human-only judgment (business alignment, strategic fit)
     - For automated criteria, determine check_type:
       - "All template sections present" → check_type: "template_sections"
       - "ID format valid" → check_type: "id_format", pattern: regex
       - "No placeholders remaining" → check_type: "no_placeholders"
       - "References valid" → check_type: "references_valid", pattern: regex
   - Write JSON files to configured validation directory

3. **Pydantic Schema Implementation:**
   ```python
   from pydantic import BaseModel, Field
   from typing import List, Optional, Literal
   from config import settings

   class ValidationCriterion(BaseModel):
       """Single validation criterion"""
       id: str = Field(..., pattern=r'^[A-Z]{2}-\d{2}$')  # e.g., CQ-01
       category: Literal["content_quality", "traceability", "consistency"]
       description: str = Field(..., min_length=10)
       validation_type: Literal["automated", "agent", "manual"]
       check_type: Optional[Literal[
           "template_sections",
           "id_format",
           "no_placeholders",
           "references_valid",
           "status_format",
           "metadata_present"
       ]] = None
       pattern: Optional[str] = None  # Regex pattern for id_format, references_valid
       required_sections: Optional[List[str]] = None  # For template_sections check

   class ValidationChecklist(BaseModel):
       """Validation checklist for artifact type"""
       artifact_type: str = Field(..., pattern=r'^[a-z_]+$')  # e.g., "prd", "epic"
       version: int = Field(..., ge=1)
       criteria: List[ValidationCriterion] = Field(..., min_items=1)

       def validate_json(cls, file_path: str) -> "ValidationChecklist":
           """Loads and validates checklist JSON from file"""
           with open(file_path, 'r') as f:
               data = json.load(f)
           return cls(**data)  # Pydantic validates schema
   ```

4. **MCP Resource Endpoint:**
   ```python
   from fastapi import HTTPException
   import aiofiles
   import json
   from config import settings

   @app.get("/mcp/resources/validation/{checklist_id}")
   async def get_validation_checklist(checklist_id: str):
       """Returns validation checklist as MCP resource"""
       # Validate checklist_id format
       if not re.match(r'^[a-z_]+_validation_v\d+$', checklist_id):
           raise HTTPException(status_code=400, detail="Invalid checklist ID format")

       # Construct file path using configured validation directory
       file_path = Path(settings.VALIDATION_RESOURCES_DIR) / f"{checklist_id}.json"

       if not file_path.exists():
           raise HTTPException(
               status_code=404,
               detail=f"Resource not found: mcp://resources/validation/{checklist_id}"
           )

       # Load and validate JSON
       async with aiofiles.open(file_path, mode='r') as f:
           content = await f.read()
           checklist_data = json.loads(content)

       # Validate against Pydantic schema
       try:
           checklist = ValidationChecklist(**checklist_data)
       except ValidationError as e:
           logger.error("invalid_checklist_schema", checklist_id=checklist_id, error=str(e))
           raise HTTPException(
               status_code=500,
               detail=f"Invalid checklist schema: {checklist_id}"
           )

       return {
           "uri": f"mcp://resources/validation/{checklist_id}",
           "content": checklist.dict()
       }
   ```

5. **Testing Strategy:**
   - Unit tests: Validate Pydantic schema correctly parses/rejects JSON
   - Integration tests: Verify MCP resource endpoint returns checklist
   - Migration tests: Confirm all criteria from generator XML mapped to JSON
   - Validation tests: Ensure `validate_artifact` tool loads checklists correctly

### Technical Tasks
- [ ] Extract validation criteria from 12 generator XML prompts
- [ ] Convert criteria to JSON format (Pydantic schema)
- [ ] Write JSON files to configured validation directory
- [ ] Implement Pydantic models (ValidationCriterion, ValidationChecklist)
- [ ] Implement MCP resource endpoint for checklists
- [ ] Add JSON schema validation on load
- [ ] Add structured logging for checklist loading
- [ ] Write unit tests for Pydantic schema validation
- [ ] Write integration tests for MCP resource endpoint
- [ ] Write migration tests (verify all criteria migrated)
- [ ] Update `validate_artifact` tool to load checklists from resources
- [ ] Add Taskfile commands for checklist validation

## Acceptance Criteria

### Scenario 1: PRD validation checklist accessible via MCP
**Given** PRD validation checklist migrated to JSON
**When** Claude Code requests `mcp://resources/validation/prd_validation_v1`
**Then** server returns JSON with 26 criteria (24 automated, 2 agent)
**And** response includes uri: "mcp://resources/validation/prd_validation_v1"
**And** JSON validated against Pydantic schema (no errors)

### Scenario 2: All artifact type checklists migrated
**Given** Checklists extracted from 12 generators
**When** Claude Code requests each checklist:
  - `mcp://resources/validation/product_vision_validation_v1`
  - `mcp://resources/validation/initiative_validation_v1`
  - `mcp://resources/validation/epic_validation_v1`
  - `mcp://resources/validation/prd_validation_v1`
  - `mcp://resources/validation/hls_validation_v1`
  - `mcp://resources/validation/backlog_story_validation_v1`
  - `mcp://resources/validation/tech_spec_validation_v1`
  - `mcp://resources/validation/adr_validation_v1`
  - `mcp://resources/validation/spike_validation_v1`
  - `mcp://resources/validation/implementation_task_validation_v1`
  - `mcp://resources/validation/business_research_validation_v1`
  - `mcp://resources/validation/implementation_research_validation_v1`
**Then** All checklists return valid JSON
**And** Criteria counts match generator XML (no criteria lost in migration)

### Scenario 3: Invalid JSON rejected on load
**Given** Checklist JSON file has invalid schema (missing required field)
**When** MCP Server attempts to load checklist
**Then** Server logs error: "invalid_checklist_schema"
**And** Returns 500 error (Internal Server Error)
**And** Error message indicates schema validation failure

### Scenario 4: Missing checklist file handled gracefully
**Given** Checklist ID requested but file does not exist
**When** Claude Code requests `mcp://resources/validation/unknown_validation_v1`
**Then** server returns 404 error
**And** error message includes: "Resource not found: mcp://resources/validation/unknown_validation_v1"

### Scenario 5: Checklist loading logged
**Given** MCP Server is running with logging configured
**When** Checklist loaded from file
**Then** server logs event with fields: checklist_id, criteria_count, version, duration_ms
**And** log format is JSON (structured logging)

### Scenario 6: validate_artifact tool uses dynamic checklists
**Given** Checklists stored as JSON resources
**When** `validate_artifact` tool called with checklist_id="prd_validation_v1"
**Then** Tool loads checklist from configured validation directory (not hardcoded path)
**And** Tool evaluates artifact against 26 criteria from JSON
**And** Results match expected validation outcomes

### Scenario 7: Checklist update without code changes
**Given** Framework Maintainer wants to add new validation criterion
**When** Maintainer edits `prd_validation_v1.json` to add criterion "CQ-27: Security review marker present"
**And** Maintainer restarts MCP Server
**Then** `validate_artifact` tool automatically uses updated checklist (no code changes)
**And** Next PRD validation includes 27 criteria (was 26)

### Scenario 8: Three-tier validation types supported
**Given** Checklist contains automated, agent, and manual validation types
**When** Claude Code requests validation checklist
**Then** JSON includes validation_type field with values: "automated", "agent", or "manual"
**And** Automated criteria have check_type specified
**And** Agent criteria flagged for AI content review
**And** Manual criteria flagged for human review

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Not Needed (Single Sprint-Ready Task)

**Rationale:**
- **Story Points:** 3 SP (below 5 SP threshold - CONSIDER SKIPPING per decision matrix)
- **Developer Count:** Single developer (straightforward data migration + schema implementation)
- **Domain Span:** Single domain (data migration and JSON schema)
- **Complexity:** Low - primarily data transformation and schema definition
- **Uncertainty:** Low - clear migration path, well-defined JSON schema
- **Override Factors:** None (no security-critical, no external dependencies)

Per SDLC Section 11.6 Decision Matrix: "3 SP, single developer, low complexity → SKIP (Single sprint-ready task)".

**No task decomposition needed.** Story can be completed as single unit of work in 1-2 days.

## Definition of Done
- [ ] Validation criteria extracted from 12 generator XML prompts
- [ ] JSON files created for all 12 artifact types
- [ ] Pydantic models implemented (ValidationCriterion, ValidationChecklist)
- [ ] MCP resource endpoint implemented for checklists
- [ ] JSON schema validation on load (reject invalid schemas)
- [ ] Structured logging for checklist loading events
- [ ] Unit tests written and passing (Pydantic schema validation)
- [ ] Integration tests passing (MCP resource endpoint)
- [ ] Migration tests passing (all criteria migrated, no data loss)
- [ ] `validate_artifact` tool updated to load checklists from resources
- [ ] Manual testing: Verify checklist update without code changes
- [ ] Taskfile commands added for checklist validation
- [ ] Product Owner approval obtained

## Additional Information
**Suggested Labels:** mcp-resources, validation, data-migration
**Estimated Story Points:** 3
**Dependencies:**
- **Depends On:** None (can be implemented independently)
- **Blocks:** US-040 (validate_artifact tool needs checklists to function)
- **Related:** US-030, US-031 (similar MCP resource migration pattern)

**Related PRD Section:** PRD-006 §Functional Requirements - FR-16

## Decisions Made

**Decision 1: Include all 12 generators in validation checklist migration**
- **Made:** During v2 refinement (feedback from US-040-047_v1_comments.md)
- **Rationale:** Comprehensive validation coverage requires checklists for all artifact types, not just the 6 originally specified. This includes Product Vision, Initiative, Business Research, Implementation Research, Spike, and Implementation Task generators
- **Impact:** Increased scope from 6 to 12 checklists, updated functional requirements and acceptance criteria

**Decision 2: Three-tier validation type system (automated/agent/manual)**
- **Made:** During v2 refinement (feedback from US-040-047_v1_comments.md)
- **Rationale:** AI Agent should perform content review before human review. Automated checks are deterministic, agent checks require AI content analysis, manual checks require human judgment
- **Impact:** Changed `validation_type` from two values ("automated", "manual") to three values ("automated", "agent", "manual")

**Decision 3: Externalize validation resources directory path**
- **Made:** During v2 refinement (feedback from US-040-047_v1_comments.md)
- **Rationale:** Hardcoded paths prevent configuration flexibility and testing with different directory structures
- **Impact:** Use `settings.VALIDATION_RESOURCES_DIR` from configuration instead of hardcoded `"resources/validation/"` path

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md` (§2.1 Python Type Safety, §5.3 Input Validation, §6.1 Structured Logging)
- **Related Stories:** US-040 (validate_artifact tool), US-030 (MCP resource pattern), US-031 (template resources)
- **Feedback:** `/feedback/US-040-047_v1_comments.md`
