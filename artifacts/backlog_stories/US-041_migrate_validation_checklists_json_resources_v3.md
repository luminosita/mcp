# User Story: Migrate Validation Checklists to JSON Resources

## Metadata
- **Story ID:** US-041
- **Title:** Migrate Validation Checklists to JSON Resources
- **Type:** Feature
- **Status:** Draft (v3)
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
- **Dual-Source Extraction:** Extract from TWO sources per generator:
  1. `<validation_checklist>` section: General validation criteria (CQ-XX, UT-XX, CC-XX, OQ-XX criterion IDs)
  2. `<guideline category="open_questions">` section: Open Questions marker validation rules (allowed markers, sub-field requirements, special validations, error message templates) - applies to 6 generators with OQ criteria
- Convert to structured JSON format with fields: id, category, description, validation_type (automated/agent/manual), check_type (template_sections/id_format/marker_validation/etc.)
- **Extended Schema for Open Questions Markers:** Add fields for marker validation: applies_to, allowed_markers, marker_sub_fields, prohibited_patterns, special_validations, error_message_templates
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
1. Extract validation criteria from all 12 generator prompts (TWO SOURCES):
   - **Source 1:** `<validation_checklist>` section (general validation criteria)
   - **Source 2:** `<guideline category="open_questions">` section (Open Questions marker validation for v2+ artifacts)

   Generators to process:
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
   - `id`: Criterion identifier (e.g., "CQ-01", "UT-02", "CC-03", "OQ-01")
   - `category`: Criterion category (e.g., "content_quality", "traceability", "consistency", "open_questions_markers")
   - `description`: Human-readable description
   - `validation_type`: "automated", "agent", or "manual"
   - `check_type`: For automated criteria, specifies check algorithm (e.g., "template_sections", "id_format", "no_placeholders", "references_valid", "marker_validation")
   - `pattern`: For regex-based checks, the regex pattern
   - `required_sections`: For template section checks, list of required section headers
   - **Open Questions Marker Validation fields (OQ-XX criteria only):**
     - `applies_to`: Version lifecycle ("v1", "v2+", or "all")
     - `allowed_markers`: List of allowed markers for this artifact type (e.g., ["[REQUIRES SPIKE]", "[REQUIRES ADR]"])
     - `marker_sub_fields`: Map of marker names to required sub-fields (e.g., {"[REQUIRES SPIKE]": ["Investigation Needed", "Spike Scope", "Time Box", "Blocking"]})
     - `prohibited_patterns`: List of free-form text patterns to reject (e.g., ["Decision:\\s*\\w+\\s*needed"])
     - `special_validations`: List of special validation rules (e.g., [{"marker": "[REQUIRES SPIKE]", "field": "Time Box", "valid_values": ["1 day", "2 days", "3 days"]}])
     - `error_message_templates`: Map of validation failure types to error message templates
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
   class SpecialValidation(BaseModel):
       """Special validation rule for marker sub-fields"""
       marker: str  # e.g., "[REQUIRES SPIKE]"
       field: str   # e.g., "Time Box"
       valid_values: List[str]  # e.g., ["1 day", "2 days", "3 days"]

   class ValidationCriterion(BaseModel):
       id: str
       category: str
       description: str
       validation_type: Literal["automated", "agent", "manual"]
       check_type: Optional[str] = None  # e.g., "template_sections", "marker_validation"
       pattern: Optional[str] = None  # Regex pattern
       required_sections: Optional[List[str]] = None

       # Open Questions Marker Validation fields (OQ-XX criteria only)
       applies_to: Optional[Literal["v1", "v2+", "all"]] = None
       allowed_markers: Optional[List[str]] = None  # e.g., ["[REQUIRES SPIKE]", "[REQUIRES ADR]"]
       marker_sub_fields: Optional[Dict[str, List[str]]] = None  # {marker: [required_fields]}
       prohibited_patterns: Optional[List[str]] = None  # Regex patterns
       special_validations: Optional[List[SpecialValidation]] = None
       error_message_templates: Optional[Dict[str, str]] = None  # {failure_type: template}

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

1. **JSON Checklist Schema Example (Backlog Story Validation with Open Questions Markers):**
   ```json
   {
     "artifact_type": "backlog_story",
     "version": 1,
     "criteria": [
       {
         "id": "CQ-01",
         "category": "content_quality",
         "description": "Story title is action-oriented and specific",
         "validation_type": "agent"
       },
       {
         "id": "CC-02",
         "category": "consistency",
         "description": "Story ID follows standard format: US-XXX",
         "validation_type": "automated",
         "check_type": "id_format",
         "pattern": "^US-\\d{3,}$"
       },
       {
         "id": "CC-03",
         "category": "consistency",
         "description": "All placeholder fields [brackets] have been filled in",
         "validation_type": "automated",
         "check_type": "no_placeholders"
       },
       {
         "id": "OQ-01",
         "category": "open_questions_markers",
         "description": "Version detected correctly (v1 skips marker validation, v2+ enforces)",
         "validation_type": "automated",
         "check_type": "marker_validation",
         "applies_to": "all"
       },
       {
         "id": "OQ-02",
         "category": "open_questions_markers",
         "description": "Section Structure: Decisions Made section exists",
         "validation_type": "automated",
         "check_type": "marker_validation",
         "applies_to": "v2+"
       },
       {
         "id": "OQ-05",
         "category": "open_questions_markers",
         "description": "Each Open Question uses allowed marker",
         "validation_type": "automated",
         "check_type": "marker_validation",
         "applies_to": "v2+",
         "allowed_markers": [
           "[REQUIRES SPIKE]",
           "[REQUIRES ADR]",
           "[REQUIRES TECH LEAD]",
           "[BLOCKED BY]"
         ],
         "error_message_templates": {
           "missing_marker": "❌ ERROR: Open Question missing standardized marker\n\nQuestion text: \"{question}\"\nArtifact: US-{XXX} v{N}\nRequired: [REQUIRES SPIKE], [REQUIRES ADR], [REQUIRES TECH LEAD], or [BLOCKED BY]"
         }
       },
       {
         "id": "OQ-06",
         "category": "open_questions_markers",
         "description": "No free-form text patterns",
         "validation_type": "automated",
         "check_type": "marker_validation",
         "applies_to": "v2+",
         "prohibited_patterns": [
           "Decision:\\s*\\w+\\s*needed",
           "Action Required:\\s*(?!.*ACTION REQUIRED)"
         ]
       },
       {
         "id": "OQ-07",
         "category": "open_questions_markers",
         "description": "All [REQUIRES SPIKE] markers include required sub-fields",
         "validation_type": "automated",
         "check_type": "marker_validation",
         "applies_to": "v2+",
         "marker_sub_fields": {
           "[REQUIRES SPIKE]": [
             "Investigation Needed",
             "Spike Scope",
             "Time Box",
             "Blocking"
           ]
         },
         "error_message_templates": {
           "missing_subfields": "❌ ERROR: Marker missing required sub-fields\n\nMarker: [REQUIRES SPIKE]\nQuestion: \"{question}\"\nMissing sub-fields: {missing_fields}\n\nAll required sub-fields: Investigation Needed, Spike Scope, Time Box (1-3 days), Blocking"
         }
       },
       {
         "id": "OQ-11",
         "category": "open_questions_markers",
         "description": "SPIKE Time Box values are exactly 1 day, 2 days, or 3 days (hard limit)",
         "validation_type": "automated",
         "check_type": "marker_validation",
         "applies_to": "v2+",
         "special_validations": [
           {
             "marker": "[REQUIRES SPIKE]",
             "field": "Time Box",
             "valid_values": ["1 day", "2 days", "3 days"]
           }
         ],
         "error_message_templates": {
           "invalid_time_box": "❌ ERROR: Invalid Time Box value for SPIKE\n\nQuestion: \"{question}\"\nTime Box Value: \"{value}\"\nValid values: \"1 day\", \"2 days\", \"3 days\" (HARD LIMIT)"
         }
       }
     ]
   }
   ```

2. **Migration Process:**

   **Phase 1: Extract from `<validation_checklist>` section**
   - Extract criteria from each generator's `<validation_checklist>` section
   - Map markdown criteria to JSON fields:
     - Extract criterion ID (CQ-01, UT-02, CC-XX, OQ-XX) from markdown header
     - Extract category from section grouping
     - Extract description from criterion text
     - Extract `applies_to` attribute if present (v1, v2+, or all)
     - Classify as automated/agent/manual based on:
       - Automated: Objective, deterministic checks (sections present, ID format, placeholders)
       - Agent: Subjective content quality checks requiring AI review (readability, appropriateness, clarity)
       - Manual: Human-only judgment (business alignment, strategic fit)
     - For automated criteria, determine check_type:
       - "All template sections present" → check_type: "template_sections"
       - "ID format valid" → check_type: "id_format", pattern: regex
       - "No placeholders remaining" → check_type: "no_placeholders"
       - "References valid" → check_type: "references_valid", pattern: regex
       - OQ-XX criteria → check_type: "marker_validation"

   **Phase 2: Extract from `<guideline category="open_questions">` section**
   - Locate "Marker Validation (v2+ artifacts only)" subsection
   - Extract allowed markers list from criterion OQ-05 or guideline text
   - Extract marker sub-field requirements from criteria OQ-07, OQ-08, OQ-09, OQ-10, etc.
   - Map to marker_sub_fields dict: `{marker_name: [required_fields]}`
   - Extract prohibited patterns from criterion OQ-06 or guideline text
   - Extract special validations (e.g., SPIKE Time Box constraint from criterion OQ-11)
   - Extract error message templates from guideline text (Missing Marker, Missing Sub-fields, Invalid Time Box)
   - Merge into OQ-XX criteria from Phase 1

   **Phase 3: Write JSON files**
   - Combine criteria from both phases
   - Validate against Pydantic schema
   - Write JSON files to configured validation directory

3. **Pydantic Schema Implementation:**
   ```python
   from pydantic import BaseModel, Field
   from typing import List, Optional, Literal, Dict
   from config import settings
   import json

   class SpecialValidation(BaseModel):
       """Special validation rule for marker sub-fields (e.g., SPIKE Time Box constraint)"""
       marker: str = Field(..., description="Marker name, e.g., '[REQUIRES SPIKE]'")
       field: str = Field(..., description="Sub-field name, e.g., 'Time Box'")
       valid_values: List[str] = Field(..., description="Allowed values for this field")

   class ValidationCriterion(BaseModel):
       """Single validation criterion"""
       id: str = Field(..., pattern=r'^[A-Z]{2}-\d{2}$')  # e.g., CQ-01, OQ-05
       category: Literal["content_quality", "traceability", "consistency", "open_questions_markers"]
       description: str = Field(..., min_length=10)
       validation_type: Literal["automated", "agent", "manual"]
       check_type: Optional[Literal[
           "template_sections",
           "id_format",
           "no_placeholders",
           "references_valid",
           "status_format",
           "metadata_present",
           "marker_validation"  # New: for Open Questions marker validation
       ]] = None
       pattern: Optional[str] = None  # Regex pattern for id_format, references_valid
       required_sections: Optional[List[str]] = None  # For template_sections check

       # Open Questions Marker Validation fields (OQ-XX criteria only)
       applies_to: Optional[Literal["v1", "v2+", "all"]] = None
       allowed_markers: Optional[List[str]] = None
       marker_sub_fields: Optional[Dict[str, List[str]]] = None  # {marker: [required_fields]}
       prohibited_patterns: Optional[List[str]] = None  # Regex patterns
       special_validations: Optional[List[SpecialValidation]] = None
       error_message_templates: Optional[Dict[str, str]] = None  # {failure_type: template}

   class ValidationChecklist(BaseModel):
       """Validation checklist for artifact type"""
       artifact_type: str = Field(..., pattern=r'^[a-z_]+$')  # e.g., "prd", "epic", "backlog_story"
       version: int = Field(..., ge=1)
       criteria: List[ValidationCriterion] = Field(..., min_items=1)

       @classmethod
       def validate_json(cls, file_path: str) -> "ValidationChecklist":
           """Loads and validates checklist JSON from file"""
           with open(file_path, 'r') as f:
               data = json.load(f)
           return cls(**data)  # Pydantic validates schema
   ```

4. **MCP Resource Endpoint:**
   ```python
   import aiofiles
   import json
   from config import settings
   from pydantic import ValidationError

   @app.get("/mcp/resources/validation/{checklist_id}")
   async def get_validation_checklist(checklist_id: str):
       """Returns validation checklist as MCP resource"""
       # Validate checklist_id format
       if not re.match(r'^[a-z_]+_validation_v\d+$', checklist_id):
           raise ValueError(f"Invalid checklist ID format: {checklist_id}")  # → JSON-RPC -32602

       # Construct file path using configured validation directory
       file_path = Path(settings.VALIDATION_RESOURCES_DIR) / f"{checklist_id}.json"

       if not file_path.exists():
           raise FileNotFoundError(
               f"Resource not found: mcp://resources/validation/{checklist_id}"
           )  # → JSON-RPC -32001

       # Load and validate JSON
       async with aiofiles.open(file_path, mode='r') as f:
           content = await f.read()
           checklist_data = json.loads(content)

       # Validate against Pydantic schema
       try:
           checklist = ValidationChecklist(**checklist_data)
       except ValidationError as e:
           logger.error("invalid_checklist_schema", checklist_id=checklist_id, error=str(e))
           raise  # Re-raise ValidationError for FastMCP (→ JSON-RPC -32603)

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
- [ ] Extract validation criteria from `<validation_checklist>` sections (12 generator XML prompts)
- [ ] Extract Open Questions marker validation from `<guideline category="open_questions">` sections (6 generators with OQ criteria)
- [ ] Convert criteria to JSON format (Pydantic schema with OQ marker validation fields)
- [ ] Map marker sub-field requirements to marker_sub_fields dict
- [ ] Extract special validations (e.g., SPIKE Time Box constraint)
- [ ] Extract error message templates for marker validation failures
- [ ] Write JSON files to configured validation directory
- [ ] Implement Pydantic models (SpecialValidation, ValidationCriterion, ValidationChecklist)
- [ ] Implement MCP resource endpoint for checklists
- [ ] Add JSON schema validation on load (including OQ fields)
- [ ] Add structured logging for checklist loading
- [ ] Write unit tests for Pydantic schema validation (including OQ marker fields)
- [ ] Write integration tests for MCP resource endpoint
- [ ] Write migration tests (verify all criteria migrated from both sources)
- [ ] Write marker validation tests (verify OQ criteria include marker rules)
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

### Scenario 9: Open Questions marker validation criteria migrated
**Given** Generators have Open Questions marker validation in `<guideline category="open_questions">` sections
**When** Validation checklists migrated to JSON
**Then** Backlog Story checklist includes OQ-XX criteria with:
  - `category: "open_questions_markers"`
  - `check_type: "marker_validation"`
  - `applies_to: "v2+"` for v2+ lifecycle enforcement
  - `allowed_markers: ["[REQUIRES SPIKE]", "[REQUIRES ADR]", "[REQUIRES TECH LEAD]", "[BLOCKED BY]"]`
  - `marker_sub_fields` dict with required fields per marker
  - `special_validations` for SPIKE Time Box constraint
  - `error_message_templates` for validation failures
**And** Epic checklist includes OQ-XX criteria with:
  - `allowed_markers: ["[REQUIRES EXECUTIVE DECISION]", "[REQUIRES PORTFOLIO PLANNING]", "[REQUIRES RESOURCE PLANNING]", "[REQUIRES ORGANIZATIONAL ALIGNMENT]"]`
**And** PRD checklist includes OQ-XX criteria with:
  - `allowed_markers: ["[REQUIRES PM + TECH LEAD]", "[REQUIRES EXECUTIVE DECISION]", "[REQUIRES ORGANIZATIONAL ALIGNMENT]"]`
**And** HLS checklist includes OQ-XX criteria with:
  - `allowed_markers: ["[REQUIRES UX RESEARCH]", "[REQUIRES UX DESIGN]", "[REQUIRES PRODUCT OWNER]"]`
**And** All OQ criteria extracted from both `<validation_checklist>` AND `<guideline>` sections
**And** No Open Questions marker validation logic lost during migration

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Not Needed (Single Sprint-Ready Task)

**Rationale:**
- **Story Points:** 5 SP (AT threshold - CONSIDER per decision matrix, but single developer and familiar domain favor SKIP)
- **Developer Count:** Single developer (data migration + schema implementation + extraction from two sources)
- **Domain Span:** Single domain (data migration and JSON schema with Open Questions marker validation extraction)
- **Complexity:** Medium - data transformation, schema definition, dual-source extraction (validation checklist + guideline sections)
- **Uncertainty:** Low - clear migration path, well-defined JSON schema, explicit extraction rules
- **Override Factors:** None (no security-critical, no external dependencies, no unfamiliar technology)

Per SDLC Section 11.6 Decision Matrix: "5 SP at threshold, single developer, familiar domain → CONSIDER but lean towards SKIP given straightforward implementation path".

**No task decomposition needed.** Story can be completed as single unit of work in 2-3 days. Dual-source extraction adds complexity but follows explicit documented patterns (Generator Validation Spec v1.0).

## Definition of Done
- [ ] Validation criteria extracted from 12 generator XML prompts (`<validation_checklist>` sections)
- [ ] Open Questions marker validation extracted from 6 generators (`<guideline category="open_questions">` sections)
- [ ] JSON files created for all 12 artifact types (with OQ marker validation for applicable generators)
- [ ] Pydantic models implemented (SpecialValidation, ValidationCriterion, ValidationChecklist with OQ fields)
- [ ] MCP resource endpoint implemented for checklists
- [ ] JSON schema validation on load (reject invalid schemas, including OQ marker validation fields)
- [ ] Structured logging for checklist loading events
- [ ] Unit tests written and passing (Pydantic schema validation with OQ fields)
- [ ] Integration tests passing (MCP resource endpoint)
- [ ] Migration tests passing (all criteria migrated from BOTH sources, no data loss)
- [ ] Marker validation tests passing (OQ criteria include allowed_markers, marker_sub_fields, special_validations)
- [ ] `validate_artifact` tool updated to load checklists from resources
- [ ] Manual testing: Verify checklist update without code changes
- [ ] Taskfile commands added for checklist validation
- [ ] Product Owner approval obtained

## Additional Information
**Suggested Labels:** mcp-resources, validation, data-migration, open-questions-markers
**Estimated Story Points:** 5 (increased from 3 SP due to Open Questions marker validation extraction complexity - Decision 4)
**Dependencies:**
- **Depends On:** None (can be implemented independently)
- **Blocks:** US-040 (validate_artifact tool needs checklists to function)
- **Related:** US-030, US-031 (similar MCP resource migration pattern), Generator Validation Spec v1.0

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

**Decision 4: Extract Open Questions marker validation from TWO sources**
- **Made:** 2025-10-20 (during Generator Validation Spec v1.0 implementation)
- **Rationale:** Open Questions marker validation logic exists in TWO places: (1) `<validation_checklist>` section contains OQ-XX criterion IDs, and (2) `<guideline category="open_questions">` section contains detailed marker validation rules (allowed markers, sub-field requirements, special validations, error message templates). Both sources must be extracted to preserve complete validation logic
- **Impact:** Extended migration process to Phase 2 extraction from `<guideline category="open_questions">` sections. Added new JSON fields: `applies_to`, `allowed_markers`, `marker_sub_fields`, `prohibited_patterns`, `special_validations`, `error_message_templates`. Added Scenario 9 acceptance criterion. Estimated effort increased from 3 SP to 5 SP (additional extraction complexity)

## Decisions Made

**Decision 1: Rename request_id → task_id for consistency**
- **Made:** During v3 refinement (feedback from US-040-047_v2_comments.md)
- **Rationale:** While this story has no tool implementation, documentation is updated to use consistent "task_id" terminology across all stories in alignment with other tool stories (US-040, US-042, US-043, US-044)
- **Impact:** Documentation uses task_id terminology for consistency with related tool stories

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md` (§2.1 Python Type Safety, §5.3 Input Validation, §6.1 Structured Logging)
- **Generator Validation Spec:** `/docs/generator_validation_spec.md` (v1.0 - defines Open Questions marker validation rules to be extracted)
- **CLAUDE.md:** `/CLAUDE.md` (v2.0 - Framework Design Principles, Open Questions Marker System sections)
- **Related Stories:** US-040 (validate_artifact tool), US-030 (MCP resource pattern), US-031 (template resources)
- **Feedback v1:** `/feedback/US-040-047_v1_comments.md`
- **Feedback v2:** `/feedback/US-040-047_v2_comments.md`
- **Changes Applied:** `/feedback/US-040-047_v2_changes_applied.md`
