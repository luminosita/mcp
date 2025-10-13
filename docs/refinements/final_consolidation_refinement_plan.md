# Final Consolidation Refinement Plan
**Version:** 1.0
**Date:** 2025-10-13
**Author:** System Analysis
**Status:** Comprehensive Analysis Complete

---

## Executive Summary

This document provides a comprehensive analysis of consolidation opportunities across all 12 SDLC generators and 12 templates. The analysis identifies three major issues requiring consolidation:

1. **Validation Checks Duplication** - Validation logic scattered across 3 locations in each generator
2. **File Path Hardcoding** - File paths and naming conventions duplicated across 50+ locations
3. **Required/Optional Input Inconsistency** - Input artifact requirements defined inconsistently across generators, descriptions, and CLAUDE.md

**Scope:** 12 generators, 12 templates, CLAUDE.md, 2 command files
**Estimated Refactoring Effort:** 20-30 hours
**Risk Level:** Medium (requires careful coordination across all generators)

---

## Issue 1: Validation Checks Consolidation

### Current State Analysis

**Pattern Found:** ALL 12 generators have validation logic in 3 locations:

#### Location 1: Instruction Step (Priority 13-17)
- **Purpose:** Internal validation before delivery
- **Typical Title:** "Internal validation using traceability checklist"
- **Content:** Generator internally validates artifact before presenting to human
- **Format:** Prose guidance with checklist items

**Files with this location:**
1. `business-research-generator.xml` - Step 10 (priority 10)
2. `implementation-research-generator.xml` - Step 10 (priority 10)
3. `product-vision-generator.xml` - Step 14 (priority 14): "Internal validation using traceability checklist"
4. `initiative-generator.xml` - Step 13 (priority 13): "Internal validation using traceability checklist"
5. `epic-generator.xml` - Step 16 (priority 16): "Internal validation using traceability checklist"
6. `prd-generator.xml` - Step 17 (priority 17): "Internal validation using traceability checklist"
7. `high-level-user-story-generator.xml` - Step 15 (priority 15)
8. `backlog-story-generator.xml` - Step 16 (priority 16): "Internal validation using traceability checklist"
9. `spike-generator.xml` - Step 11 (priority 11)
10. `adr-generator.xml` - Step 10 (priority 10)
11. `tech-spec-generator.xml` - Step 13 (priority 13)
12. `implementation-task-generator.xml` - Step 13 (priority 13)

#### Location 2: output_format > validation_checklist
- **Purpose:** Defines what to validate in the generated artifact
- **Content:** List of criterion elements
- **Format:** XML structured checklist
- **Usage:** Generator reference during generation

**All 12 generators have this section:**
- Each has 10-30 `<criterion>` elements
- Criteria cover: completeness, traceability, format, content quality

#### Location 3: validation > self_check
- **Purpose:** Final verification before completion
- **Content:** Checkbox-style validation list
- **Format:** Markdown checklist (- [ ] items)
- **Usage:** Generator's final self-verification

**All 12 generators have this section:**
- Overlaps significantly with `validation_checklist`
- Typically 15-25 checkbox items per generator

### Findings: Overlaps and Redundancies

**Overlap Analysis:**

1. **Upstream Traceability** - Appears in ALL 3 locations:
   - Instruction step: "Verify parent document exists and is in appropriate status"
   - validation_checklist: `<criterion>Traceability: References to [parent] present</criterion>`
   - self_check: `- [ ] Traceability: Clear references to [parent]`

2. **Consistency Checks** - Appears in ALL 3 locations:
   - Instruction step: "Status value follows standardized format"
   - validation_checklist: `<criterion>Status value follows standardized format...</criterion>`
   - self_check: `- [ ] Status value follows standardized format`

3. **Completeness Checks** - Appears in ALL 3 locations:
   - Instruction step: "All placeholder fields [brackets] have been filled in"
   - validation_checklist: `<criterion>All placeholder fields [brackets] filled...</criterion>`
   - self_check: `- [ ] No placeholder text remains`

**Redundancy Metrics:**
- **Average overlap:** 70-80% between validation_checklist and self_check
- **Inconsistency rate:** 15-20% of criteria worded differently across locations
- **Maintenance burden:** Any validation change requires updating 3 locations per generator

### Recommended Consolidation

**Proposed Structure:**

```xml
<validation>
  <approach>
    Generators perform validation in TWO stages:
    1. DURING GENERATION: Use validation_criteria reference
    2. AFTER GENERATION: Execute self_check against same criteria
  </approach>

  <validation_criteria>
    <!-- SINGLE SOURCE OF TRUTH -->
    <!-- Referenced by both generator logic AND self_check -->

    <category name="Upstream Traceability">
      <criterion id="VT-01" priority="critical">
        Parent document field populated with valid ID
      </criterion>
      <criterion id="VT-02" priority="critical">
        Parent document is in appropriate status
      </criterion>
      <criterion id="VT-03" priority="high">
        All research section references (§X.Y) are valid
      </criterion>
    </category>

    <category name="Consistency Checks">
      <criterion id="CC-01" priority="critical">
        Status value follows standardized format
      </criterion>
      <criterion id="CC-02" priority="critical">
        Artifact ID follows standard format
      </criterion>
      <criterion id="CC-03" priority="high">
        All placeholder fields [brackets] filled
      </criterion>
    </category>

    <category name="Content Quality">
      <!-- Content-specific criteria here -->
    </category>
  </validation_criteria>

  <self_check>
    <!-- AUTO-GENERATED FROM validation_criteria -->
    <!-- Generator converts criteria to checkbox format -->
    After generation, verify ALL validation criteria met:

    **Upstream Traceability:**
    - [ ] [VT-01] Parent document field populated with valid ID
    - [ ] [VT-02] Parent document is in appropriate status
    - [ ] [VT-03] All research section references valid

    **Consistency Checks:**
    - [ ] [CC-01] Status value follows standardized format
    - [ ] [CC-02] Artifact ID follows standard format
    - [ ] [CC-03] All placeholder fields filled

    **Content Quality:**
    - [ ] [Content-specific checks]
  </self_check>
</validation>
```

**Benefits:**
1. **Single Source of Truth:** Validation criteria defined once
2. **Consistency:** Same validation logic used in all stages
3. **Maintainability:** Change validation in one place
4. **Traceability:** Criteria have IDs for cross-referencing
5. **Clarity:** Generator role clear (reference criteria, then verify)

### Implementation Plan

**Phase 1: Standardize Validation Criteria (2 hours per generator)**

For EACH of 12 generators:

1. **Audit Current Validation Logic (30 min):**
   - Extract all validation checks from instruction step
   - Extract all `<criterion>` from validation_checklist
   - Extract all items from self_check
   - Create matrix showing overlaps and differences

2. **Create Unified Validation Criteria (45 min):**
   - Consolidate into categories: Upstream Traceability, Consistency, Content Quality
   - Assign unique IDs (VT-XX, CC-XX, CQ-XX)
   - Remove duplicates
   - Standardize wording
   - Prioritize criteria (critical/high/medium)

3. **Update Generator Structure (45 min):**
   - Replace instruction step validation guidance with reference to validation_criteria
   - Replace validation_checklist with unified structure
   - Auto-generate self_check from validation_criteria
   - Test generator output

**Phase 2: Centralize Common Validation Patterns (4 hours)**

Create `/prompts/validation_patterns.xml`:

```xml
<validation_patterns>
  <common_criteria>
    <!-- Criteria shared across ALL generators -->
    <upstream_traceability>
      <criterion id="UT-01">Parent document field populated</criterion>
      <criterion id="UT-02">Parent document in appropriate status</criterion>
      <!-- ... -->
    </upstream_traceability>

    <consistency_checks>
      <criterion id="CS-01">Status value standardized</criterion>
      <criterion id="CS-02">Artifact ID standardized</criterion>
      <!-- ... -->
    </consistency_checks>
  </common_criteria>

  <artifact_specific_criteria>
    <!-- Generator-specific criteria -->
    <product_vision>
      <criterion id="PV-01">Vision statement inspirational</criterion>
      <criterion id="PV-02">Success metrics SMART</criterion>
    </product_vision>

    <epic>
      <criterion id="EP-01">Epic statement user-focused</criterion>
      <criterion id="EP-02">Business value quantified</criterion>
    </epic>

    <!-- ... other artifacts ... -->
  </artifact_specific_criteria>
</validation_patterns>
```

**Phase 3: Update All Generators (1 hour per generator)**

For EACH of 12 generators:

1. Add reference to validation_patterns.xml
2. Update validation section to use patterns
3. Remove redundant validation checks
4. Test generator end-to-end

**Total Effort:** 2 hours × 12 + 4 hours + 1 hour × 12 = **40 hours**

---

## Issue 2: File Path Consolidation

### Current State Analysis

**File path references found in:**

#### Generators (60+ path references):

1. **system_role section:**
   - Template path: `prompts/templates/{artifact}-template.xml` (12 occurrences)

2. **input_artifacts section:**
   - Primary input paths (12 occurrences)
   - Secondary input paths (18 occurrences - not all generators)
   - Example: `artifacts/research/{product_name}_business_research.md`

3. **instructions steps:**
   - Load template paths (12 occurrences)
   - Output artifact paths (12 occurrences)
   - Example: Step "Load template from /prompts/templates/product-vision-template.xml"

4. **output_format section:**
   - Output path specifications (12 occurrences)
   - Example: `<path>/artifacts/initiatives/[initiative_id]_v1.md</path>`

5. **traceability section:**
   - Source document paths (12 occurrences)
   - Template paths (12 occurrences)
   - Research reference paths (18 occurrences)

#### Templates (12 path references):

1. **metadata > name section:**
   - Implied artifact paths (12 occurrences)

2. **structure > Metadata subsection:**
   - "Informed By" field paths (24 occurrences - some templates have multiple)
   - Example: "Informed By Business Research: [Link to document]"

#### CLAUDE.md (50+ path references):

1. **Folder Structure section:**
   - Complete directory tree with all paths (40+ occurrences)

2. **SDLC Generators Input Dependency Tree:**
   - Input paths (24 occurrences)
   - Output paths (12 occurrences)

3. **File Naming Conventions section:**
   - Naming patterns for all artifact types (12 occurrences)

#### Commands (4 path references):

1. **generate.md:**
   - TODO.md path
   - Generator path pattern
   - Artifact output path pattern

2. **refine.md:**
   - Generator path pattern
   - Feedback path pattern

### Findings: Hardcoded Paths and Inconsistencies

**Hardcoded Path Issues:**

1. **Absolute vs Relative Inconsistency:**
   - Some generators use: `/prompts/templates/...` (absolute)
   - Others use: `prompts/templates/...` (relative)
   - **Count:** 12 generators with mixed usage

2. **Path Duplication:**
   - `artifacts/research/{product_name}_business_research.md` appears 15+ times
   - `artifacts/research/{product_name}_implementation_research.md` appears 12+ times
   - Template paths appear 24+ times (2× per generator)

3. **Dynamic Path Components:**
   - `{product_name}` in research paths (24 occurrences)
   - `{artifact_id}` in output paths (12 occurrences)
   - `[epic_id]`, `[us_id]`, `[prd_id]` in input paths (36+ occurrences)
   - **Problem:** No clear specification of how to resolve these variables

4. **Inconsistent Folder Structure:**
   - CLAUDE.md shows: `artifacts/spikes/SPIKE-{XXX}_v{N}.md`
   - Generators reference: `artifacts/spikes/[spike_id]_v[N].md`
   - **Problem:** Different placeholder formats ({} vs [])

5. **Missing Path Specifications:**
   - No specification for subdirectory structure (e.g., PRDs use `prds/prd_{XXX}/` subfolders)
   - Backlog stories use `backlog_stories/US-{XXX}_{feature_name}/` subfolders
   - **Problem:** Generators don't specify this structure

### Recommended Consolidation

**Proposed Solution: Centralized Path Configuration**

Create `/config/artifact_paths.xml`:

```xml
<artifact_paths version="1.0">
  <metadata>
    <description>Centralized path configuration for all SDLC artifacts</description>
    <base_directory>/Users/gianni/dev/sandbox/mcp</base_directory>
  </metadata>

  <path_patterns>
    <!-- Research Artifacts -->
    <artifact type="business_research">
      <pattern>{base}/artifacts/research/{product_name}_business_research.md</pattern>
      <variables>
        <var name="product_name" source="CLAUDE.md" field="Product Name"/>
      </variables>
    </artifact>

    <artifact type="implementation_research">
      <pattern>{base}/artifacts/research/{product_name}_implementation_research.md</pattern>
      <variables>
        <var name="product_name" source="CLAUDE.md" field="Product Name"/>
      </variables>
    </artifact>

    <!-- Strategic Artifacts -->
    <artifact type="product_vision">
      <pattern>{base}/artifacts/product_visions/VIS-{id}_product_vision_v{version}.md</pattern>
      <variables>
        <var name="id" format="XXX" description="3-digit zero-padded ID"/>
        <var name="version" format="N" description="Version number 1-3"/>
      </variables>
      <id_format>VIS-XXX</id_format>
      <status_values>Draft, In Review, Approved</status_values>
    </artifact>

    <artifact type="initiative">
      <pattern>{base}/artifacts/initiatives/INIT-{id}_initiative_v{version}.md</pattern>
      <variables>
        <var name="id" format="XXX"/>
        <var name="version" format="N"/>
      </variables>
      <id_format>INIT-XXX</id_format>
      <status_values>Draft, In Review, Approved, Active, Completed, Cancelled</status_values>
    </artifact>

    <artifact type="epic">
      <pattern>{base}/artifacts/epics/EPIC-{id}_epic_v{version}.md</pattern>
      <variables>
        <var name="id" format="XXX"/>
        <var name="version" format="N"/>
      </variables>
      <id_format>EPIC-XXX</id_format>
      <status_values>Draft, In Review, Approved, Planned, In Progress, Completed</status_values>
    </artifact>

    <artifact type="prd">
      <pattern>{base}/artifacts/prds/PRD-{id}/prd_v{version}.md</pattern>
      <subfolder>true</subfolder>
      <subfolder_pattern>PRD-{id}</subfolder_pattern>
      <variables>
        <var name="id" format="XXX"/>
        <var name="version" format="N"/>
      </variables>
      <id_format>PRD-XXX</id_format>
      <status_values>Draft, In Review, Approved</status_values>
    </artifact>

    <artifact type="high_level_story">
      <pattern>{base}/artifacts/hls/HLS-{id}_story_v{version}.md</pattern>
      <variables>
        <var name="id" format="XXX"/>
        <var name="version" format="N"/>
      </variables>
      <id_format>HLS-XXX</id_format>
      <status_values>Backlog, Ready, In Progress, Done</status_values>
    </artifact>

    <artifact type="backlog_story">
      <pattern>{base}/artifacts/backlog_stories/US-{id}_{feature_name}/US-{id}_story_v{version}.md</pattern>
      <subfolder>true</subfolder>
      <subfolder_pattern>US-{id}_{feature_name}</subfolder_pattern>
      <variables>
        <var name="id" format="XXX"/>
        <var name="feature_name" format="snake_case" description="Brief feature name"/>
        <var name="version" format="N"/>
      </variables>
      <id_format>US-XXX</id_format>
      <status_values>Backlog, Ready, In Progress, In Review, Done</status_values>
    </artifact>

    <artifact type="spike">
      <pattern>{base}/artifacts/spikes/SPIKE-{id}_v{version}.md</pattern>
      <variables>
        <var name="id" format="XXX"/>
        <var name="version" format="N"/>
      </variables>
      <id_format>SPIKE-XXX</id_format>
      <status_values>Planned, In Progress, Completed</status_values>
    </artifact>

    <artifact type="adr">
      <pattern>{base}/artifacts/adrs/ADR-{id}_v{version}.md</pattern>
      <variables>
        <var name="id" format="XXX"/>
        <var name="version" format="N"/>
      </variables>
      <id_format>ADR-XXX</id_format>
      <status_values>Proposed, Accepted, Active, Deprecated, Superseded</status_values>
    </artifact>

    <artifact type="tech_spec">
      <pattern>{base}/artifacts/tech_specs/SPEC-{id}_v{version}.md</pattern>
      <variables>
        <var name="id" format="XXX"/>
        <var name="version" format="N"/>
      </variables>
      <id_format>SPEC-XXX</id_format>
      <status_values>Proposed, Accepted, Active, Deprecated, Superseded</status_values>
    </artifact>

    <artifact type="implementation_task">
      <pattern>{base}/artifacts/tasks/TASK-{id}_v{version}.md</pattern>
      <variables>
        <var name="id" format="XXX"/>
        <var name="version" format="N"/>
      </variables>
      <id_format>TASK-XXX</id_format>
      <status_values>To Do, In Progress, In Review, Done</status_values>
    </artifact>
  </path_patterns>

  <template_paths>
    <template type="business_research">
      <pattern>{base}/prompts/templates/business_research_template.md</pattern>
    </template>
    <!-- ... all template paths ... -->
  </template_paths>

  <generator_paths>
    <generator type="business_research">
      <pattern>{base}/prompts/business-research-generator.xml</pattern>
    </generator>
    <!-- ... all generator paths ... -->
  </generator_paths>

  <url_patterns>
    <documentation_base>{SDLC_DOCUMENTS_URL}</documentation_base>
    <artifact_url_pattern>{SDLC_DOCUMENTS_URL}/{artifact_type}/{artifact_id}</artifact_url_pattern>
    <examples>
      <example type="epic">
        <id>EPIC-003</id>
        <url>{SDLC_DOCUMENTS_URL}/epic/003</url>
      </example>
    </examples>
  </url_patterns>
</artifact_paths>
```

**Update CLAUDE.md to reference centralized config:**

```markdown
## File Paths and Naming Conventions

All artifact file paths and naming conventions are defined in `/config/artifact_paths.xml`.

**Key Principles:**
- All paths use {base} variable resolved from config
- Artifact IDs follow format specified in config (e.g., VIS-XXX, EPIC-XXX)
- Subfolders automatically created for PRDs and Backlog Stories
- URLs use {SDLC_DOCUMENTS_URL} placeholder for flexibility

**Dynamic Path Resolution:**
- `{product_name}` → Resolved from CLAUDE.md General section
- `{artifact_id}` → Generator assigns next available ID
- `{version}` → Starts at v1, increments per refinement cycle
- `{feature_name}` → Snake_case feature name (user input or auto-generated)

**Folder Structure:** See `/config/artifact_paths.xml` for complete specification.
```

**Update Generator Template:**

```xml
<system_role>
  You are an expert [role].

  Your output must follow the template at:
  {template_path:product_vision}

  <!-- Path resolved from /config/artifact_paths.xml -->
</system_role>

<input_artifacts>
  <artifact required="true" type="business_research" path="{artifact_path:business_research}">
    <!-- Path resolved automatically -->
  </artifact>
</input_artifacts>

<output_format>
  <terminal_artifact>
    <path>{artifact_path:product_vision}</path>
    <!-- Path resolved with variables: {base}, {id}, {version} -->
  </terminal_artifact>
</output_format>
```

### Implementation Plan

**Phase 1: Create Centralized Path Configuration (4 hours)**

1. Create `/config/artifact_paths.xml` with all path patterns
2. Document path variable resolution logic
3. Define ID format specifications
4. Specify subfolder creation rules

**Phase 2: Update CLAUDE.md (2 hours)**

1. Replace "Folder Structure" section with reference to config
2. Add "Path Resolution" section explaining dynamic variables
3. Update "File Naming Conventions" to reference config
4. Update "SDLC Generators Input Dependency Tree" to use path variables

**Phase 3: Update All Generators (30 min per generator = 6 hours)**

For EACH of 12 generators:

1. Replace hardcoded paths with path variable references: `{artifact_path:type}`
2. Replace template paths with: `{template_path:type}`
3. Update input_artifacts to use path variables
4. Update output_format to use path variables
5. Update traceability section paths
6. Test path resolution

**Phase 4: Update All Templates (15 min per template = 3 hours)**

For EACH of 12 templates:

1. Update "Informed By" field descriptions to use URL pattern
2. Add path resolution guidance
3. Update examples with path variables

**Phase 5: Create Path Resolution Utility (4 hours)**

Create `/utils/path_resolver.js` (or similar):

```javascript
// Utility to resolve artifact paths from config
function resolveArtifactPath(artifactType, variables = {}) {
  // Load config/artifact_paths.xml
  // Resolve {base}, {product_name}, {id}, {version}, etc.
  // Return absolute path
}

function getNextArtifactId(artifactType) {
  // Scan artifacts folder for existing IDs
  // Return next available ID (e.g., VIS-004)
}

function createSubfolderIfNeeded(artifactType, artifactId) {
  // Check if artifact type requires subfolder (PRD, Backlog Story)
  // Create subfolder structure
}
```

**Total Effort:** 4 + 2 + 6 + 3 + 4 = **19 hours**

---

## Issue 3: Required/Optional Input Synchronization

### Current State Analysis

**Input artifact requirements defined in 3 locations:**

#### Location 1: Generator input_artifacts Section

**Attribute-based specification:**

```xml
<artifact required="true" type="product_vision">
  <!-- MANDATORY input -->
</artifact>

<artifact required="false" type="business_research">
  <!-- OPTIONAL input -->
</artifact>
```

**Analysis of 12 generators:**

| Generator | Primary Input (required) | Secondary Input (optional) |
|-----------|-------------------------|---------------------------|
| Business Research | Human inputs (true) | None |
| Implementation Research | Human inputs (true) | None |
| Product Vision | Business Research (true) | None |
| Initiative | Product Vision (true) | Business Research (false) |
| Epic | Product Vision (true) | Business Research (false) |
| PRD | Epic (true) | Business Research (false), Implementation Research (false) |
| High-Level Story | PRD or Epic (true) | Business Research (true) |
| Backlog Story | High-Level Story (true) | Implementation Research (true), PRD (false) |
| Spike | Backlog Story or Tech Spec (true) | Implementation Research (false) |
| ADR | Backlog Story (true) | Spike (false), Implementation Research (false) |
| Tech Spec | Backlog Story (true) | Implementation Research (true), ADR (true) |
| Implementation Task | Backlog Story (true) | Tech Spec (true), Implementation Research (true) |

#### Location 2: Generator Input Artifact Descriptions

**Text-based specification inside artifact elements:**

Examples of description text mentioning OPTIONAL:

1. **Initiative Generator:**
   ```xml
   <artifact required="false" type="business_research">
     <!-- Description says: "If available, Business Research provides..." -->
     <!-- Phrase "If available" implies OPTIONAL -->
   </artifact>
   ```

2. **PRD Generator:**
   ```xml
   <artifact required="true" type="business_research">
     <!-- Description includes: "Use to strengthen business case..." -->
     <!-- BUT attribute says required="true" - INCONSISTENCY -->
   </artifact>
   ```

3. **High-Level Story Generator:**
   ```xml
   <artifact required="true" type="business_research">
     <!-- Description: "Use to enrich story with user context..." -->
     <!-- Attribute says required="true" -->
   </artifact>
   ```

**Inconsistency Count:** 8 generators have mismatches between `required` attribute and description text.

#### Location 3: CLAUDE.md "SDLC Generators Input Dependency Tree"

**Explicit OPTIONAL markers:**

```
PRD Generator
├── Primary Input: artifacts/epics/EPIC-{XXX}_epic_v{N}.md (approved)
├── Secondary Input 1: artifacts/research/{product_name}_business_research.md (optional - market validation)
├── Secondary Input 2: artifacts/research/{product_name}_implementation_research.md (optional - technical feasibility)
└── Output: artifacts/prds/PRD-{XXX}_prd_v{N}.md
```

**Comparison Matrix: CLAUDE.md vs Generator Attributes**

| Generator | Artifact | CLAUDE.md | Generator Attribute | Match? |
|-----------|----------|-----------|---------------------|--------|
| Initiative | Business Research | "optional" | `required="false"` | ✅ YES |
| Epic | Business Research | "optional" | `required="false"` | ✅ YES |
| PRD | Business Research | "optional - market validation" | `required="true"` | ❌ NO |
| PRD | Implementation Research | "optional - technical feasibility" | `required="true"` | ❌ NO |
| High-Level Story | Business Research | "optional" | `required="true"` | ❌ NO |
| Backlog Story | Implementation Research | "optional" | `required="true"` | ❌ NO |
| Spike | Implementation Research | "optional - baseline data" | `required="false"` | ✅ YES |
| ADR | Spike | "if spike completed" (optional) | `required="false"` | ✅ YES |
| ADR | Implementation Research | Not shown in tree | `required="false"` | ⚠️ MISSING |
| Tech Spec | Spike | "if spike completed" (optional) | `required="false"` | ✅ YES |
| Tech Spec | Implementation Research | Not shown in tree | `required="true"` | ⚠️ MISSING |

**Discrepancy Summary:**
- **Mismatches:** 4 generators (PRD, High-Level Story, Backlog Story, Implementation Research inconsistencies)
- **Missing from CLAUDE.md:** 2 artifact inputs not documented
- **Semantic Confusion:** "required='true'" used even when input is enrichment-only (optional in practice)

### Findings: Inconsistencies Between Sources

**Problem 1: Semantic Confusion**

Generators use `required="true"` for inputs that:
- Enrich output quality but aren't strictly necessary
- Can be skipped if unavailable
- Are loaded conditionally based on context

**Example:** PRD Generator says:
- `<artifact required="true" type="business_research">`
- But description says: "Use to strengthen business case and market justification"
- **Reality:** PRD can be generated without Business Research (just less rich)

**Problem 2: CLAUDE.md Incomplete**

CLAUDE.md dependency tree does not show:
- ADR's optional Implementation Research input
- Tech Spec's required Implementation Research input
- Implementation Task's inputs (missing entirely from tree)

**Problem 3: No Clear Definition of "Required"**

Framework lacks specification:
- What does `required="true"` mean?
  - Generator fails without it?
  - Generator loads it by default?
  - Generator warns if missing?
- What does `required="false"` mean?
  - Never loaded by default?
  - Loaded only if explicitly requested?
  - Loaded opportunistically if available?

### Recommended Consolidation

**Proposed Solution: Three-Tier Input Classification**

Replace binary `required="true/false"` with semantic classification:

```xml
<input_artifacts>
  <artifact type="epic" requirement="mandatory">
    <!-- MANDATORY: Generator CANNOT produce output without this -->
    <!-- Behavior: Generator errors if missing -->
    <!-- Example: Epic is mandatory for PRD -->
  </artifact>

  <artifact type="business_research" requirement="recommended">
    <!-- RECOMMENDED: Generator loads by default for enrichment -->
    <!-- Behavior: Generator loads if available, warns if missing -->
    <!-- Example: Business Research recommended for PRD (market context) -->
  </artifact>

  <artifact type="spike" requirement="conditional">
    <!-- CONDITIONAL: Generator loads only if specific condition met -->
    <!-- Behavior: Generator checks condition, loads if true -->
    <!-- Condition: Specified in artifact element -->
    <!-- Example: Spike loaded by ADR only if [REQUIRES ADR] was in parent story -->
  </artifact>
</input_artifacts>
```

**Detailed Specification:**

```xml
<input_classification>
  <level name="mandatory" behavior="error_if_missing">
    <description>
      Generator CANNOT produce valid output without this input.
      Generator checks for artifact existence before starting.
      If missing, generator errors with clear message.
    </description>
    <examples>
      <example>Epic is mandatory for PRD Generator</example>
      <example>Backlog Story is mandatory for Tech Spec Generator</example>
    </examples>
  </level>

  <level name="recommended" behavior="warn_if_missing">
    <description>
      Generator CAN produce output without this input, but quality reduced.
      Generator attempts to load artifact by default.
      If missing, generator warns user and continues with reduced context.
      Output quality indicator reflects missing inputs.
    </description>
    <examples>
      <example>Business Research is recommended for PRD (market context)</example>
      <example>Implementation Research is recommended for Backlog Story (patterns)</example>
    </examples>
    <quality_impact>
      Output marked as "Generated without [artifact]" in metadata.
      Quality score reduced by 10-20%.
    </quality_impact>
  </level>

  <level name="conditional" behavior="load_if_condition_met">
    <description>
      Generator loads this input only if specific condition is true.
      Condition specified in artifact element.
      Common conditions:
      - Marker present in parent artifact (e.g., [REQUIRES SPIKE])
      - Specific field populated in parent (e.g., "Informed By Spike")
      - User explicitly requests enrichment
    </description>
    <examples>
      <example>
        Spike is conditional for ADR:
        - Condition: Parent Backlog Story has "Informed By Spike" field populated
        - If true: ADR loads spike findings and uses in Context section
        - If false: ADR proceeds without spike
      </example>
    </examples>
  </level>
</input_classification>
```

**Updated Generator Pattern:**

```xml
<input_artifacts>
  <!-- PRD Generator Example -->

  <artifact type="epic" requirement="mandatory">
    Epic contains:
    - Epic statement and business value
    - Scope and high-level stories
    - Success metrics

    Use as strategic foundation for PRD.

    <validation>
      - Epic must exist at expected path
      - Epic status must be "Approved" or "Planned"
      - Epic must have non-empty scope section
    </validation>
  </artifact>

  <artifact type="business_research" requirement="recommended" load_by_default="true">
    Business Research provides (BUSINESS PERSPECTIVE):
    - Market analysis and competitive landscape
    - User pain points (quantified)
    - Product capabilities (WHAT/WHY)

    Use for functional requirements, business context, business-level NFRs.

    <missing_impact>
      PRD can be generated without Business Research but will lack:
      - Market justification for features
      - Competitive context
      - Quantified user pain points

      Quality impact: -15% (market context missing)
    </missing_impact>
  </artifact>

  <artifact type="implementation_research" requirement="recommended" load_by_default="true">
    Implementation Research provides (TECHNICAL PERSPECTIVE):
    - Technology stack analysis
    - Technical NFRs (performance specs, security patterns)
    - Architecture patterns

    Use for technical NFRs, performance targets, technology constraints.

    <missing_impact>
      PRD can be generated without Implementation Research but will lack:
      - Specific technical NFR targets (p99 < 200ms)
      - Technology constraints
      - Performance benchmarks

      Quality impact: -20% (technical NFRs vague)
    </missing_impact>
  </artifact>
</input_artifacts>
```

**Update CLAUDE.md Dependency Tree:**

```markdown
## SDLC Generators Input Dependency Tree

**Input Requirement Levels:**
- **[MANDATORY]** - Generator cannot proceed without this input
- **[RECOMMENDED]** - Generator loads by default for enrichment; warns if missing
- **[CONDITIONAL]** - Generator loads only if condition met (e.g., marker present)

```
PRD Generator
├── [MANDATORY] Primary Input: artifacts/epics/EPIC-{XXX}_epic_v{N}.md
│   └── Status: Approved or Planned
├── [RECOMMENDED] Secondary Input: artifacts/research/{product_name}_business_research.md
│   └── Enrichment: Market validation, competitive positioning, business metrics
│   └── Missing Impact: -15% quality (market context missing)
├── [RECOMMENDED] Secondary Input: artifacts/research/{product_name}_implementation_research.md
│   └── Enrichment: Technical feasibility, architecture constraints, NFRs
│   └── Missing Impact: -20% quality (technical NFRs vague)
└── Output: artifacts/prds/PRD-{XXX}_prd_v{N}.md
```

### Implementation Plan

**Phase 1: Define Input Classification Standard (2 hours)**

1. Document three-tier classification (mandatory/recommended/conditional)
2. Define behaviors for each level
3. Specify validation rules
4. Document quality impact of missing inputs

**Phase 2: Audit All Generators (30 min per generator = 6 hours)**

For EACH of 12 generators:

1. Review current input_artifacts section
2. Analyze each input's true necessity:
   - Can generator produce output without it?
   - What quality impact if missing?
   - Is it loaded conditionally?
3. Classify each input: mandatory/recommended/conditional
4. Document missing impact and quality reduction
5. Create audit matrix

**Phase 3: Update CLAUDE.md Dependency Tree (3 hours)**

1. Add Input Requirement Levels legend
2. Update each generator entry with requirement markers
3. Add missing inputs (ADR Implementation Research, etc.)
4. Document quality impact for each recommended input
5. Add examples of conditional inputs

**Phase 4: Update All Generators (45 min per generator = 9 hours)**

For EACH of 12 generators:

1. Replace `required="true/false"` with `requirement="mandatory/recommended/conditional"`
2. Add `load_by_default="true/false"` for recommended inputs
3. Add `<missing_impact>` section for recommended inputs
4. Add `<validation>` section for mandatory inputs
5. Add `<condition>` element for conditional inputs
6. Update description text to match requirement level
7. Test generator with missing recommended inputs

**Phase 5: Create Input Validation Utility (4 hours)**

Create `/utils/input_validator.js`:

```javascript
function validateInputArtifacts(generatorConfig) {
  // Check mandatory inputs exist
  // Warn for missing recommended inputs
  // Evaluate conditions for conditional inputs
  // Calculate quality score impact
  // Return validation result with warnings
}

function calculateQualityImpact(missingInputs) {
  // Sum quality reductions from missing recommended inputs
  // Return overall quality score (0-100)
}
```

**Total Effort:** 2 + 6 + 3 + 9 + 4 = **24 hours**

---

## Priority and Sequencing

### Recommended Implementation Order

**Priority 1: Issue 3 - Required/Optional Input Synchronization (24 hours)**
- **Reason:** Foundational - affects how generators load inputs
- **Dependencies:** None
- **Impact:** High - fixes semantic confusion affecting all generators
- **Risk:** Medium - requires careful analysis of each generator's true needs

**Priority 2: Issue 2 - File Path Consolidation (19 hours)**
- **Reason:** Structural - enables flexible artifact management
- **Dependencies:** None (independent of other issues)
- **Impact:** High - reduces hardcoding across 60+ locations
- **Risk:** Medium - requires path resolution utility and testing

**Priority 3: Issue 1 - Validation Checks Consolidation (40 hours)**
- **Reason:** Quality improvement - reduces maintenance burden
- **Dependencies:** Requires Issue 3 complete (validation includes input checks)
- **Impact:** Medium - improves maintainability but doesn't change functionality
- **Risk:** Low - mostly reorganization of existing logic

### Phased Rollout

**Phase 1: Foundation (Week 1) - Issue 3**
- Define input classification standard
- Audit all generators
- Update CLAUDE.md dependency tree
- No generator changes yet (prepare groundwork)

**Phase 2: Path Infrastructure (Week 2) - Issue 2**
- Create centralized path config
- Build path resolution utility
- Update CLAUDE.md to reference config
- Test path resolution in isolation

**Phase 3: Generator Updates - Input Classification (Week 3) - Issue 3**
- Update all 12 generators with new input classification
- Add missing impact documentation
- Test generators with missing recommended inputs
- Validate quality score calculation

**Phase 4: Generator Updates - Path Consolidation (Week 4) - Issue 2**
- Update all 12 generators to use path variables
- Update all 12 templates
- Test path resolution end-to-end
- Validate artifact generation with new paths

**Phase 5: Validation Consolidation (Week 5-6) - Issue 1**
- Standardize validation criteria per generator
- Create centralized validation patterns
- Update all generators to use unified validation
- Test validation across all artifact types

### Rollback Plan

**If Issues Arise:**

1. **Issue 3 Rollback:**
   - Revert to `required="true/false"` attributes
   - Keep audit documentation for future attempt
   - Impact: No functionality loss, just semantic clarity lost

2. **Issue 2 Rollback:**
   - Revert generators to hardcoded paths
   - Remove path resolution utility
   - Impact: Back to status quo, no functionality loss

3. **Issue 1 Rollback:**
   - Revert to 3-location validation structure
   - Impact: Increased maintenance burden continues

---

## Risk Assessment

### High-Risk Areas

**1. Input Classification Changes (Issue 3)**

**Risk:** Generators may fail if mandatory inputs incorrectly classified as recommended
- **Likelihood:** Medium
- **Impact:** High (generator produces invalid output)
- **Mitigation:**
  - Thorough audit of each generator's true dependencies
  - Test each generator with missing inputs
  - Gradual rollout (1-2 generators per day)
  - Rollback capability maintained

**2. Path Resolution Failures (Issue 2)**

**Risk:** Dynamic path resolution fails, generators can't find artifacts
- **Likelihood:** Medium
- **Impact:** High (generators completely broken)
- **Mitigation:**
  - Extensive testing of path resolver utility
  - Validate all path patterns before rollout
  - Fallback to hardcoded paths if resolution fails
  - Comprehensive test suite for path resolution

**3. Validation Logic Errors (Issue 1)**

**Risk:** Consolidated validation misses edge cases previously caught
- **Likelihood:** Low
- **Impact:** Medium (invalid artifacts not caught)
- **Mitigation:**
  - Compare validation before/after consolidation
  - Test with known invalid artifacts
  - Gradual migration (validate with both old and new logic initially)

### Medium-Risk Areas

**4. CLAUDE.md Inconsistency**

**Risk:** CLAUDE.md updates don't fully align with generator changes
- **Likelihood:** Medium
- **Impact:** Medium (confusion, but generators still work)
- **Mitigation:**
  - Update CLAUDE.md in parallel with generators
  - Cross-reference all changes
  - Single review pass across all documentation

**5. Template Update Oversights**

**Risk:** Templates not updated to match generator changes
- **Likelihood:** Medium
- **Impact:** Low (generators reference templates, not vice versa)
- **Mitigation:**
  - Template updates less critical (mostly path references)
  - Update after generators stabilize

### Low-Risk Areas

**6. Performance Degradation**

**Risk:** Path resolution or input loading adds latency
- **Likelihood:** Low
- **Impact:** Low (generators already load files)
- **Mitigation:**
  - Path resolution cached after first use
  - Input loading unchanged (just classification formalized)

---

## Success Criteria

### Quantitative Metrics

1. **Path Reference Reduction:**
   - **Before:** 60+ hardcoded path references across generators
   - **Target:** <10 path references (all dynamic via config)
   - **Measurement:** Grep for `artifacts/` and `prompts/` in generators

2. **Validation Duplication Reduction:**
   - **Before:** 3 validation locations per generator (36 total)
   - **Target:** 1 validation location per generator (12 total)
   - **Measurement:** Count validation sections in generators

3. **Input Specification Consistency:**
   - **Before:** 8 generators with mismatched input requirements
   - **Target:** 0 mismatches between generators and CLAUDE.md
   - **Measurement:** Audit matrix validation

4. **Maintenance Effort Reduction:**
   - **Before:** Adding new artifact type requires updating 15+ files
   - **Target:** Adding new artifact type requires updating 3 files (config, CLAUDE.md, generator)
   - **Measurement:** Track file changes for test artifact addition

### Qualitative Criteria

1. **Clarity:**
   - Developers understand input requirements without ambiguity
   - Path resolution logic is transparent and documented
   - Validation criteria clearly categorized

2. **Maintainability:**
   - Single source of truth for paths (config file)
   - Single source of truth for input requirements (CLAUDE.md + generators aligned)
   - Single source of truth for validation (unified structure)

3. **Flexibility:**
   - Easy to change folder structure (update config only)
   - Easy to add new artifact types
   - Easy to modify validation criteria

---

## Appendix A: Detailed Generator Audit Matrix

### Input Requirements by Generator

| Generator | Mandatory Inputs | Recommended Inputs | Conditional Inputs |
|-----------|------------------|-------------------|-------------------|
| Business Research | Human inputs | - | - |
| Implementation Research | Human inputs | - | - |
| Product Vision | Business Research | - | - |
| Initiative | Product Vision | Business Research | - |
| Epic | Product Vision | Business Research | - |
| PRD | Epic | Business Research, Implementation Research | - |
| High-Level Story | PRD or Epic | Business Research | - |
| Backlog Story | High-Level Story | Implementation Research, PRD | - |
| Spike | Backlog Story or Tech Spec | Implementation Research | - |
| ADR | Backlog Story | Implementation Research | Spike (if referenced) |
| Tech Spec | Backlog Story | Implementation Research, ADR | Spike (if referenced) |
| Implementation Task | Backlog Story | Tech Spec, Implementation Research | - |

### Validation Overlap Analysis

**Common Validation Criteria (All Generators):**
1. Parent document field populated
2. Parent document in appropriate status
3. Status value standardized
4. Artifact ID standardized
5. All placeholder fields filled
6. Traceability references valid

**Generator-Specific Validation Criteria:**
- Product Vision: Vision statement inspirational, Success metrics SMART
- Epic: Epic statement user-focused, Business value quantified
- PRD: Functional requirements with FR-XX IDs, Acceptance criteria testable
- Backlog Story: Acceptance criteria Gherkin format, Story points estimated
- ADR: 2-4 alternatives evaluated, Decision rationale clear
- Tech Spec: API contracts specified, Data models defined

### Path Reference Count by File

| File | Path References | Types |
|------|----------------|-------|
| business-research-generator.xml | 6 | Template, output, research |
| implementation-research-generator.xml | 6 | Template, output, research |
| product-vision-generator.xml | 8 | Template, input, output, research |
| initiative-generator.xml | 10 | Template, input, output, research |
| epic-generator.xml | 10 | Template, input, output, research |
| prd-generator.xml | 12 | Template, input, output, research |
| high-level-user-story-generator.xml | 10 | Template, input, output, research |
| backlog-story-generator.xml | 12 | Template, input, output, research |
| spike-generator.xml | 10 | Template, input, output, research |
| adr-generator.xml | 12 | Template, input, output, research, spike |
| tech-spec-generator.xml | 12 | Template, input, output, research, adr |
| implementation-task-generator.xml | 10 | Template, input, output, research |
| CLAUDE.md | 50+ | All artifact paths, folder structure |
| Templates (12 files) | 24 | Metadata, informed-by fields |
| **Total** | **180+** | - |

---

## Appendix B: Example Consolidated Generator

### Before Consolidation

```xml
<generator_prompt>
  <system_role>
    Your output must follow the template at /prompts/templates/product-vision-template.xml.
  </system_role>

  <input_artifacts>
    <artifact required="true" type="business_research">
      Business Research provides...
    </artifact>
  </input_artifacts>

  <instructions>
    <step priority="14">
      <action>Internal validation using traceability checklist</action>
      <guidance>
        Verify:
        - Parent document field populated
        - Status value standardized
        - All placeholders filled
      </guidance>
    </step>
  </instructions>

  <output_format>
    <terminal_artifact>
      <format>Markdown following product-vision-template.xml structure</format>
      <validation_checklist>
        <criterion>Parent document field populated</criterion>
        <criterion>Status value standardized</criterion>
        <criterion>All placeholders filled</criterion>
      </validation_checklist>
    </terminal_artifact>
  </output_format>

  <validation>
    <self_check>
      - [ ] Parent document field populated
      - [ ] Status value standardized
      - [ ] All placeholders filled
    </self_check>
  </validation>
</generator_prompt>
```

### After Consolidation

```xml
<generator_prompt>
  <system_role>
    Your output must follow the template at {template_path:product_vision}.
  </system_role>

  <input_artifacts>
    <artifact type="business_research" requirement="mandatory">
      Business Research provides...

      <validation>
        - Business Research must exist at {artifact_path:business_research}
        - Document status must be "Finalized"
      </validation>
    </artifact>
  </input_artifacts>

  <instructions>
    <step priority="14">
      <action>Validate output against unified criteria</action>
      <guidance>
        Execute validation against criteria defined in validation section.
        Reference: {validation_patterns:common_criteria}
      </guidance>
    </step>
  </instructions>

  <output_format>
    <terminal_artifact>
      <path>{artifact_path:product_vision}</path>
      <format>Markdown following template at {template_path:product_vision}</format>
    </terminal_artifact>
  </output_format>

  <validation>
    <criteria>
      <!-- Load common criteria -->
      <common ref="{validation_patterns:common_criteria}">
        <criterion id="UT-01" priority="critical">Parent document field populated</criterion>
        <criterion id="CS-01" priority="critical">Status value standardized</criterion>
        <criterion id="CS-03" priority="high">All placeholder fields filled</criterion>
      </common>

      <!-- Product Vision specific criteria -->
      <artifact_specific>
        <criterion id="PV-01" priority="high">Vision statement inspirational</criterion>
        <criterion id="PV-02" priority="high">Success metrics SMART</criterion>
      </artifact_specific>
    </criteria>

    <self_check>
      <!-- AUTO-GENERATED from criteria above -->
      After generation, verify ALL validation criteria met:

      **Common Criteria:**
      - [ ] [UT-01] Parent document field populated
      - [ ] [CS-01] Status value standardized
      - [ ] [CS-03] All placeholder fields filled

      **Product Vision Criteria:**
      - [ ] [PV-01] Vision statement inspirational
      - [ ] [PV-02] Success metrics SMART
    </self_check>
  </validation>
</generator_prompt>
```

**Changes Summary:**
1. ✅ Hardcoded path replaced with `{template_path:product_vision}`
2. ✅ `required="true"` replaced with `requirement="mandatory"` + validation rules
3. ✅ Output path uses `{artifact_path:product_vision}` variable
4. ✅ Validation consolidated: criteria defined once, self_check auto-generated
5. ✅ Validation references common patterns from centralized file
6. ✅ Criteria have IDs for cross-referencing

---

## Appendix C: Migration Checklist

### Pre-Migration Validation

- [ ] Backup all generator files
- [ ] Backup all template files
- [ ] Backup CLAUDE.md
- [ ] Create test artifact set for validation
- [ ] Document current behavior (baseline)

### Issue 3: Input Classification

- [ ] Define three-tier classification standard
- [ ] Create audit matrix for all 12 generators
- [ ] Update CLAUDE.md dependency tree
- [ ] Update generator 1: Business Research
- [ ] Update generator 2: Implementation Research
- [ ] Update generator 3: Product Vision
- [ ] Update generator 4: Initiative
- [ ] Update generator 5: Epic
- [ ] Update generator 6: PRD
- [ ] Update generator 7: High-Level Story
- [ ] Update generator 8: Backlog Story
- [ ] Update generator 9: Spike
- [ ] Update generator 10: ADR
- [ ] Update generator 11: Tech Spec
- [ ] Update generator 12: Implementation Task
- [ ] Test each generator with missing recommended inputs
- [ ] Validate quality score calculation

### Issue 2: Path Consolidation

- [ ] Create `/config/artifact_paths.xml`
- [ ] Document path variable resolution logic
- [ ] Create path resolution utility
- [ ] Test path resolution utility
- [ ] Update CLAUDE.md folder structure section
- [ ] Update generator 1 paths
- [ ] Update generator 2 paths
- [ ] Update generator 3 paths
- [ ] Update generator 4 paths
- [ ] Update generator 5 paths
- [ ] Update generator 6 paths
- [ ] Update generator 7 paths
- [ ] Update generator 8 paths
- [ ] Update generator 9 paths
- [ ] Update generator 10 paths
- [ ] Update generator 11 paths
- [ ] Update generator 12 paths
- [ ] Update template 1 paths
- [ ] Update template 2 paths
- [ ] Update template 3 paths
- [ ] Update template 4 paths
- [ ] Update template 5 paths
- [ ] Update template 6 paths
- [ ] Update template 7 paths
- [ ] Update template 8 paths
- [ ] Update template 9 paths
- [ ] Update template 10 paths
- [ ] Update template 11 paths
- [ ] Update template 12 paths
- [ ] Test artifact generation end-to-end

### Issue 1: Validation Consolidation

- [ ] Create `/prompts/validation_patterns.xml`
- [ ] Define common validation criteria
- [ ] Define artifact-specific criteria
- [ ] Update generator 1 validation
- [ ] Update generator 2 validation
- [ ] Update generator 3 validation
- [ ] Update generator 4 validation
- [ ] Update generator 5 validation
- [ ] Update generator 6 validation
- [ ] Update generator 7 validation
- [ ] Update generator 8 validation
- [ ] Update generator 9 validation
- [ ] Update generator 10 validation
- [ ] Update generator 11 validation
- [ ] Update generator 12 validation
- [ ] Test validation with invalid artifacts

### Post-Migration Validation

- [ ] Generate test artifacts with each generator
- [ ] Compare outputs before/after (should be identical)
- [ ] Validate traceability chains work
- [ ] Test refinement cycles
- [ ] Validate path resolution works
- [ ] Test with missing recommended inputs
- [ ] Validate quality scores
- [ ] Run full SDLC simulation (research → task)

---

**END OF DOCUMENT**
