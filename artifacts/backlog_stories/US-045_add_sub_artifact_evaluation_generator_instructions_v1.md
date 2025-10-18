# User Story: Add Sub-artifact Evaluation Instructions to All Generators

## Metadata
- **Story ID:** US-045
- **Title:** Add Sub-artifact Evaluation Instructions to All Generators
- **Type:** Feature
- **Status:** Draft
- **Priority:** Must-have (enables automatic sub-artifact workflow, critical for FR-25)
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-008 (MCP Tools - Validation and Path Resolution)
- **Functional Requirements Covered:** FR-25
- **Informed By Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Functional Requirements - FR-25
- **Functional Requirements Coverage:**
  - **FR-25:** All artifact generators SHALL evaluate whether sub-artifacts are required after generation and return appropriate metadata flags for automatic task queue population

**Parent High-Level Story:** [HLS-008: MCP Tools - Validation and Path Resolution]
- **Link:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 6: Add Sub-artifact Evaluation Instructions to All Generators

## User Story
As a Framework Maintainer, I want all artifact generators to evaluate sub-artifact requirements and return metadata flags, so that sub-artifact workflows initiate automatically via `add_task` tool without manual intervention.

## Description
Currently, artifact generators produce only the primary artifact (e.g., PRD generator produces PRD). They do not evaluate whether sub-artifacts are required (e.g., PRD requires 6 HLS decompositions). This requires:
1. **Manual Analysis:** Human reviews generated PRD to determine HLS count
2. **Manual TODO.md Updates:** Human adds tasks for each HLS generation
3. **Risk of Forgetting:** Sub-artifacts may be forgotten if not immediately documented

This story updates all artifact generators to include sub-artifact evaluation logic and output metadata flags enabling automatic workflow initiation:

**Generators to Update:**
1. **Initiative Generator** → Evaluates Epic requirements
2. **Epic Generator** → Evaluates HLS requirements (or PRD if Epic is large)
3. **PRD Generator** → Evaluates HLS requirements
4. **HLS Generator** → Evaluates Backlog Story requirements
5. **Backlog Story Generator** → Evaluates Tech Spec/ADR/Spike requirements (case-by-case basis)

**Generator Output Enhancement:**
```xml
<!-- Example PRD Generator Output Metadata -->
<generation_metadata>
  <primary_artifact>
    <artifact_id>PRD-006</artifact_id>
    <artifact_type>prd</artifact_type>
    <version>1</version>
  </primary_artifact>

  <sub_artifacts_evaluation>
    <requires_sub_artifacts>true</requires_sub_artifacts>
    <sub_artifact_type>hls</sub_artifact_type>
    <sub_artifact_count>6</sub_artifact_count>
    <required_artifact_ids>HLS-006,HLS-007,HLS-008,HLS-009,HLS-010,HLS-011</required_artifact_ids>
    <rationale>PRD scope (6 high-level features) requires decomposition into 6 HLS stories</rationale>
  </sub_artifacts_evaluation>

  <open_questions>
    <has_open_questions>false</has_open_questions>
  </open_questions>

  <action_required>
    <call_add_task_tool>true</call_add_task_tool>
    <task_list>
      <task artifact_id="HLS-006" generator="hls-generator" parent_id="PRD-006" />
      <task artifact_id="HLS-007" generator="hls-generator" parent_id="PRD-006" />
      <task artifact_id="HLS-008" generator="hls-generator" parent_id="PRD-006" />
      <task artifact_id="HLS-009" generator="hls-generator" parent_id="PRD-006" />
      <task artifact_id="HLS-010" generator="hls-generator" parent_id="PRD-006" />
      <task artifact_id="HLS-011" generator="hls-generator" parent_id="PRD-006" />
    </task_list>
  </action_required>
</generation_metadata>
```

After implementation, generators automatically trigger sub-artifact workflows by returning metadata that Claude Code uses to call `add_task` tool.

## Implementation Research References

**Primary Research Document:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`

**Technical Patterns Applied:**
- **§Prompt Engineering Best Practices:** Structure generator prompts with clear sub-artifact evaluation instructions and output format specifications

**No direct implementation research reference** (this is generator prompt enhancement, not code implementation).

## Functional Requirements
1. Update 5 artifact generators with sub-artifact evaluation instructions:
   - `prompts/initiative-generator.xml`
   - `prompts/epic-generator.xml`
   - `prompts/prd-generator.xml`
   - `prompts/hls-generator.xml`
   - `prompts/backlog-story-generator.xml`
2. Add `<sub_artifact_evaluation_instructions>` section to each generator:
   - Describes when sub-artifacts are required (e.g., PRD always requires HLS decomposition)
   - Specifies evaluation criteria (e.g., count features/capabilities to determine HLS count)
   - Defines output metadata format (XML structure for sub-artifact requirements)
3. Add `<generation_metadata>` output template to each generator:
   - `<primary_artifact>`: Generated artifact ID, type, version
   - `<sub_artifacts_evaluation>`: Sub-artifact requirements (true/false, type, count, IDs, rationale)
   - `<open_questions>`: Open questions flag (blocks sub-artifact generation if unresolved)
   - `<action_required>`: Task list for `add_task` tool invocation
4. Update generator execution instructions to:
   - Parse generation metadata from generator output
   - Call `add_task` tool if `<call_add_task_tool>true</call_add_task_tool>`
   - Present task list to user for confirmation before calling tool
5. Sub-artifact evaluation rules per generator:
   - **Initiative Generator:** Evaluate Epic count based on strategic capabilities (typically 3-5 Epics per Initiative)
   - **Epic Generator:** Evaluate HLS or PRD requirements (if Epic is large/complex, decompose to PRD first; if moderate, decompose directly to HLS)
   - **PRD Generator:** Evaluate HLS count based on feature/capability count (typically 5-10 HLS per PRD)
   - **HLS Generator:** Evaluate Backlog Story count based on implementation tasks (typically 5-10 US per HLS)
   - **Backlog Story Generator:** Evaluate Tech Spec/ADR/Spike on case-by-case basis (check for [REQUIRES TECH SPEC], [REQUIRES ADR], [REQUIRES SPIKE] markers in Open Questions)

## Non-Functional Requirements
- **Maintainability:** Sub-artifact evaluation logic clearly documented in generator prompts
- **Consistency:** All generators use same metadata output format for interoperability
- **Clarity:** Evaluation rationale included in metadata (explains why N sub-artifacts needed)
- **Flexibility:** Generators support override (if sub-artifact count manually specified in input, use that instead of auto-evaluation)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story updates generator prompts (XML files), not implementation code. Follow existing generator structure conventions.

**References to Existing Patterns:**
- Review existing generator prompts (`prompts/*-generator.xml`) for structure conventions
- Maintain consistency with existing `<instructions>`, `<input_artifacts>`, `<output_format>` sections

### Implementation Guidance

**Story-Specific Technical Approach:**

1. **Sub-Artifact Evaluation Instructions Template:**
   ```xml
   <sub_artifact_evaluation_instructions>
     <purpose>
       After generating primary artifact, evaluate whether sub-artifacts (downstream artifacts in SDLC dependency chain) are required for implementation.
     </purpose>

     <evaluation_criteria>
       <!-- Generator-specific criteria -->
       <!-- Example for PRD Generator: -->
       <criterion>Count functional requirements or high-level features in PRD</criterion>
       <criterion>Each major feature/capability typically requires 1 HLS story</criterion>
       <criterion>Complex features may require multiple HLS stories</criterion>
       <criterion>Target: 5-10 HLS stories per PRD (adjust based on scope)</criterion>
     </evaluation_criteria>

     <output_metadata_format>
       <generation_metadata>
         <primary_artifact>
           <artifact_id>{generated_artifact_id}</artifact_id>
           <artifact_type>{artifact_type}</artifact_type>
           <version>{version}</version>
         </primary_artifact>

         <sub_artifacts_evaluation>
           <requires_sub_artifacts>{true|false}</requires_sub_artifacts>
           <sub_artifact_type>{hls|backlog_story|tech_spec|etc}</sub_artifact_type>
           <sub_artifact_count>{N}</sub_artifact_count>
           <required_artifact_ids>{comma-separated IDs}</required_artifact_ids>
           <rationale>{explanation of why N sub-artifacts needed}</rationale>
         </sub_artifacts_evaluation>

         <open_questions>
           <has_open_questions>{true|false}</has_open_questions>
           <blocking_count>{number of [REQUIRES ...] markers}</blocking_count>
         </open_questions>

         <action_required>
           <call_add_task_tool>{true|false}</call_add_task_tool>
           <task_list>
             <task artifact_id="{SUB_ID}" generator="{generator}" parent_id="{PRIMARY_ID}" />
             ...
           </task_list>
         </action_required>
       </generation_metadata>
     </output_metadata_format>

     <decision_logic>
       <if condition="primary_artifact requires decomposition (e.g., PRD requires HLS)">
         <set requires_sub_artifacts="true" />
         <set sub_artifact_count="{evaluated count}" />
         <generate required_artifact_ids="{next available IDs}" />
         <generate task_list for add_task tool />
       </if>
       <if condition="primary_artifact standalone (e.g., Tech Spec does not require sub-artifacts)">
         <set requires_sub_artifacts="false" />
       </if>
     </decision_logic>
   </sub_artifact_evaluation_instructions>
   ```

2. **Generator-Specific Evaluation Criteria:**

   **PRD Generator:**
   - Count high-level features/capabilities (from §Requirements or §User Experience sections)
   - Each feature → 1 HLS story (minimum)
   - Complex features → 2-3 HLS stories
   - Target: 5-10 HLS stories per PRD

   **Epic Generator:**
   - Evaluate Epic scope/complexity
   - If Epic < 3 months effort → decompose directly to HLS stories (skip PRD)
   - If Epic >= 3 months effort → create PRD first, then decompose PRD to HLS
   - Decision rule: "Does this Epic require detailed requirements specification (PRD)?"

   **HLS Generator:**
   - Count implementation tasks/features in HLS story
   - Each significant task → 1 Backlog Story
   - Related tasks → group into single Backlog Story
   - Target: 5-10 US stories per HLS

   **Initiative Generator:**
   - Count strategic capabilities/themes in Initiative
   - Each capability → 1 Epic
   - Target: 3-5 Epics per Initiative

   **Backlog Story Generator:**
   - Check Open Questions for markers: [REQUIRES TECH SPEC], [REQUIRES ADR], [REQUIRES SPIKE]
   - If markers present → create tasks for Tech Spec/ADR/Spike
   - If no markers → no sub-artifacts required

3. **Generator Execution Updates:**

   Update `.claude/commands/generate.md` to:
   - Parse `<generation_metadata>` from generator output
   - If `<call_add_task_tool>true</call_add_task_tool>`:
     - Present task list to user: "Generator evaluated {N} sub-artifacts required. Add tasks to queue?"
     - If user confirms → call `add_task` tool with task list
     - If user declines → skip task addition (manual TODO.md update required)

4. **Testing Strategy:**
   - Manual testing: Generate PRD-006, verify metadata includes 6 HLS tasks
   - Manual testing: Generate Epic-006, verify metadata evaluates PRD or HLS requirement
   - Manual testing: Generate HLS-006, verify metadata includes Backlog Story tasks
   - Validation: Ensure metadata XML structure valid (no syntax errors)

### Technical Tasks
- [ ] Add `<sub_artifact_evaluation_instructions>` section to initiative-generator.xml
- [ ] Add `<sub_artifact_evaluation_instructions>` section to epic-generator.xml
- [ ] Add `<sub_artifact_evaluation_instructions>` section to prd-generator.xml
- [ ] Add `<sub_artifact_evaluation_instructions>` section to hls-generator.xml
- [ ] Add `<sub_artifact_evaluation_instructions>` section to backlog-story-generator.xml
- [ ] Add `<generation_metadata>` output template to all 5 generators
- [ ] Update `.claude/commands/generate.md` to parse metadata and call add_task tool
- [ ] Write evaluation criteria for each generator (generator-specific rules)
- [ ] Test PRD generator with PRD-006 (verify 6 HLS tasks in metadata)
- [ ] Test Epic generator with Epic-006 (verify PRD or HLS evaluation)
- [ ] Test HLS generator with HLS-006 (verify Backlog Story tasks)
- [ ] Document metadata format in SDLC artifacts guideline

## Acceptance Criteria

### Scenario 1: PRD generator evaluates 6 HLS requirements
**Given** PRD-006 has 6 high-level features (MCP Resources, MCP Prompts, MCP Tools, Task Tracking, Integration Testing, Production Readiness)
**When** PRD generator completes generation
**Then** generator outputs `<generation_metadata>` with:
  - `<requires_sub_artifacts>true</requires_sub_artifacts>`
  - `<sub_artifact_type>hls</sub_artifact_type>`
  - `<sub_artifact_count>6</sub_artifact_count>`
  - `<required_artifact_ids>HLS-006,HLS-007,HLS-008,HLS-009,HLS-010,HLS-011</required_artifact_ids>`
  - `<task_list>` with 6 tasks for add_task tool
**And** Claude Code parses metadata and prompts user: "Generator evaluated 6 HLS stories required. Add tasks to queue?"

### Scenario 2: Epic generator evaluates PRD requirement
**Given** Epic-006 scope is large (>3 months, multiple complex capabilities)
**When** Epic generator completes generation
**Then** generator outputs `<generation_metadata>` with:
  - `<requires_sub_artifacts>true</requires_sub_artifacts>`
  - `<sub_artifact_type>prd</sub_artifact_type>`
  - `<sub_artifact_count>1</sub_artifact_count>`
  - `<required_artifact_ids>PRD-006</required_artifact_ids>`
  - `<rationale>Epic scope requires detailed requirements specification (PRD) before decomposition to HLS</rationale>`

### Scenario 3: HLS generator evaluates Backlog Story requirements
**Given** HLS-006 (MCP Resources Migration) has 7 implementation tasks
**When** HLS generator completes generation
**Then** generator outputs `<generation_metadata>` with:
  - `<requires_sub_artifacts>true</requires_sub_artifacts>`
  - `<sub_artifact_type>backlog_story</sub_artifact_type>`
  - `<sub_artifact_count>7</sub_artifact_count>`
  - `<required_artifact_ids>US-028,US-029,US-030,US-031,US-032,US-033,US-034</required_artifact_ids>`

### Scenario 4: Backlog Story generator detects Tech Spec requirement
**Given** Backlog Story US-040 has [REQUIRES TECH SPEC] marker in Open Questions
**When** Backlog Story generator completes generation
**Then** generator outputs `<generation_metadata>` with:
  - `<requires_sub_artifacts>true</requires_sub_artifacts>`
  - `<sub_artifact_type>tech_spec</sub_artifact_type>`
  - `<sub_artifact_count>1</sub_artifact_count>`
  - `<required_artifact_ids>SPEC-XXX</required_artifact_ids>`

### Scenario 5: Generator evaluation metadata triggers add_task tool
**Given** PRD generator outputs metadata with `<call_add_task_tool>true</call_add_task_tool>`
**When** User confirms task addition
**Then** Claude Code calls `add_task` tool with task list from metadata
**And** Task Tracking microservice receives 6 tasks (HLS-006 through HLS-011)
**And** Next `get_next_task` call returns HLS-006 generation task

### Scenario 6: User declines automatic task addition
**Given** Generator outputs metadata with task list
**When** User declines task addition
**Then** Claude Code skips `add_task` tool invocation
**And** presents message: "Manual TODO.md update required for 6 HLS tasks"
**And** user can manually add tasks later

### Scenario 7: All 5 generators include sub-artifact evaluation
**Given** Updated generators (Initiative, Epic, PRD, HLS, Backlog Story)
**When** Each generator executes
**Then** Each generator outputs `<generation_metadata>` section
**And** Metadata format consistent across all generators (same XML structure)
**And** Evaluation criteria documented in each generator's instructions

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Not Needed (Single Sprint-Ready Task)

**Rationale:**
- **Story Points:** 5 SP (at threshold - CONSIDER SKIPPING per decision matrix)
- **Developer Count:** Single developer (generator prompt updates, not code)
- **Domain Span:** Single domain (generator prompt engineering)
- **Complexity:** Low-moderate - adding instructions and output templates to existing generators
- **Uncertainty:** Low - clear metadata format, well-defined evaluation criteria
- **Override Factors:** None (no technical implementation, just prompt updates)

Per SDLC Section 11.6 Decision Matrix: "5 SP, single developer, low-moderate complexity → SKIP (Prompt updates are straightforward)".

**No task decomposition needed.** Story can be completed as single unit of work in 2-3 days.

## Definition of Done
- [ ] `<sub_artifact_evaluation_instructions>` added to initiative-generator.xml
- [ ] `<sub_artifact_evaluation_instructions>` added to epic-generator.xml
- [ ] `<sub_artifact_evaluation_instructions>` added to prd-generator.xml
- [ ] `<sub_artifact_evaluation_instructions>` added to hls-generator.xml
- [ ] `<sub_artifact_evaluation_instructions>` added to backlog-story-generator.xml
- [ ] `<generation_metadata>` output template added to all 5 generators
- [ ] `.claude/commands/generate.md` updated to parse metadata and call add_task tool
- [ ] Evaluation criteria documented for each generator
- [ ] Manual testing: PRD-006 generation includes 6 HLS tasks in metadata
- [ ] Manual testing: Epic-006 generation evaluates PRD or HLS requirement
- [ ] Manual testing: HLS-006 generation includes Backlog Story tasks
- [ ] Metadata format documented in SDLC artifacts guideline
- [ ] Product Owner approval obtained

## Additional Information
**Suggested Labels:** generators, prompt-engineering, automation
**Estimated Story Points:** 5
**Dependencies:**
- **Depends On:** US-044 (add_task tool must exist to call from generate command)
- **Blocks:** None (enables automatic workflow but doesn't block other features)
- **Related:** FR-24 (add_task tool), FR-25 (sub-artifact evaluation requirement)

**Related PRD Section:** PRD-006 §Functional Requirements - FR-25

## Open Questions & Implementation Uncertainties

**Q1: Should generators include ID allocation logic or rely on add_task tool to allocate IDs?**

**Resolution:** Generators include required_artifact_ids in metadata using next available IDs from CLAUDE.md ID Allocation Tracking section. Claude Code parses these IDs and passes to `add_task` tool. Task Tracking microservice validates IDs are available (not already allocated) during task creation.

**Q2: How should generators handle manual override of sub-artifact count?**

**Resolution:** Generators check for explicit count in input (e.g., "Generate PRD with 8 HLS stories"). If manual count provided, use that instead of auto-evaluation. Document in generator instructions.

**No other open implementation questions.** Metadata format and evaluation criteria clearly defined in Implementation Guidance section.

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **Parent HLS:** `/artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md`
- **Related Stories:** US-044 (add_task tool)
- **SDLC Artifacts Guideline:** `/docs/sdlc_artifacts_comprehensive_guideline.md` (will be updated with metadata format)
