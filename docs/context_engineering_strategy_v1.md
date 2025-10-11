# Context Engineering Strategy Document v1.1

## Executive Summary

This document defines the **Context Engineering Framework** for AI-assisted software development using recursive prompt generation. The framework transforms traditional artifact creation into a self-propagating chain where prompts generate both deliverables and next-level generator prompts.

**Core Innovation**: Treat prompts as executable artifacts that spawn subsequent prompts, creating an SDLC-aligned cascade from Product Vision > Epic > PRD > Story > Spec > Code > Test.

---

## 1. Core Principles

### 1.1 Prompt-as-Artifact Paradigm
- Every generator prompt is a versioned, reusable artifact
- Templates are XML-formatted prompts with embedded validation logic
- Output artifacts are final documents, not templates

### 1.2 Standalone Context Isolation
- Each generator executes in fresh Claude Code session
- Context contains: root CLAUDE.md + specialized CLAUDE.md + templates + immediate inputs only
- No cumulative context pollution across SDLC phases

### 1.3 Recursive Generation Chains
- Generator outputs dual artifacts:
  1. Terminal deliverable (e.g., Product Vision Document v1.md)
  2. Next-level generator prompt (e.g., epic-generator.xml)
- Chain depth: SDLC-aligned (Vision > Epic > PRD > Story > ADR+Spec > Code > Test)

### 1.4 Progressive Automation Maturity
- **Phase 1 (PoC)**: Human-triggered execution with manual approval gates - Complete PoC demonstrating framework viability
- **Phase 2 (MCP Server Extraction)**: Extract prompts/templates into standalone MCP Server repository for reusability across projects
- **Phase 3 (Semi-Automated)**: Semi-automated coding AI agent with self-critique loops
- **Phase 4 (Agentic Orchestration)**: Fully automated AI agent orchestration with quality thresholds (coding, unit tests, deployment)
- **Phase 5 (Production Readiness)**: Production-grade tooling and documentation

---

## 2. Workflow Phases

### 2.1 Phase 1: PoC - Bootstrap and Execution Cascade
**Objective**: Bootstrap the framework and validate through the execution of the full generator cascade from Product Vision through Backlog Stories.

**Inputs**:
- `/docs/research/advanced_prompt_engineering/advanced_prompt_engineering_software_docs_code_final.md` (research)
- User responses to clarification questions

**Outputs**:
- `/docs/context_engineering_strategy_v1.md` (this document)
- `/TODO.md` (master task list with dependencies)
- `/CLAUDE.md` (root orchestration guide)
- `/.claude/commands/generate.md` (universal executor)
- `/.claude/commands/refine.md` (iteration orchestrator)
- `/prompts/templates/*.xml` (extracted/generated templates)
- `/prompts/templates/generator-schema.xml` (schema for all generators)
- `/prompts/*_generator.xml` (generator prompts)
- Product Vision, Epic, and PRD artifacts (v1, v2, v3)

**Validation Criteria**:
- [ ] All templates extracted from research document (Section 6.1-6.4)
- [ ] Master Plan contains enumerated tasks (TASK-001 through TASK-015)
- [ ] Each task has explicit validation criteria
- [ ] Folder structure supports versioned outputs (v1, v2, v3)
- [ ] At least 3 generator types completed through 3-iteration refinement cycles
- [ ] Framework viability demonstrated

**Phase 1 Completion**: Ends with TASK-015 (Backlog Story Generation)

---

### 2.2 Phase 2: MCP Server Extraction & Productization
**Objective**: Extract prompts and templates into standalone MCP Server for reusability

**Activities**:
1. Create new MCP Server project repository
2. Clean up all prompts and templates from PoC-specific references
3. Extract and relocate:
   - All `/prompts/templates/*.xml` files
   - Generator schema template
   - Command documentation
4. Implement MCP Server (Python/FastMCP or other framework - TBD)
5. Document MCP Server usage patterns
6. Test MCP Server integration with new project

**Outputs**:
- Standalone MCP Server repository
- Clean, reusable prompts and templates
- MCP Server integration documentation
- Usage examples

**Rationale**:
- Current folder structure is optimized for PoC
- Copy/paste approach for new projects creates maintenance burden
- MCP Server enables framework reuse across multiple products
- Centralizes prompt/template versioning and updates

**Phase 2 Completion**: MCP Server operational and tested with new project

---

## 3. Folder Structure Standard

```
/
   .claude/
      commands/
         generate.md       # Universal executor
         refine.md        # Iteration orchestrator

   docs/
      context_engineering_strategy_v1.md           # Comprehensive methodology
      sdlc_artifacts_comprehensive_guideline.md    # SDLC artifacts guideline               
   prompts/
      templates/                          # XML-formatted templates
         {phase}-template_v{1-3}.md       ## SDLC artifacts templates 
      {phase}_generator_v{1-3}.xml               # Generator prompts

   artifacts/                              # All generated deliverables
      product_vision_v{1-3}.md
      epics/
      prds/
         prd_{id}/
            prd_v{1-3}.md
            TODO.md                        # High-level story tracking
      backlog_stories/
         US-{prd_id}-{story_id}_{feature_name}/
            backlog_story_v{1-3}.md
            TODO.md                        # Implementation task tracking
      specs/
      code/
      tests/

   feedback/                               # Human critique logs
      {artifact}_v{N}_critique.md

   CLAUDE.md                               # This file
   TODO.md                                 # Master Plan (single source of truth)
```

**Design Rationale**:
- Max 3 levels deep (prevents navigation complexity)
- Versioned outputs prevent overwriting during iterations
- Specialized CLAUDE.md co-located with prompts directory
- Feedback folder supports human-in-loop iteration

---

## 4. CLAUDE.md Orchestration Rules

### 4.1 Root CLAUDE.md (`/CLAUDE.md`)

**Purpose**: Project-wide context and navigation guide for the AI agent.

**Contents**:
```markdown
# Context Engineering Framework - Root Orchestration

## Project Overview
Proof-of-concept for recursive prompt generation following SDLC phases.
CLI tool development demonstration.

## Folder Structure
[Link to Section 3 of strategy document]

## Execution Instructions
To execute a generator:
1. Identify task in /TODO.md (e.g., TASK-002)
2. Run: /generate {task_id}
3. System loads:
   - /prompts/{task}_generator.xml
   - Required templates from /prompts/templates/
4. Review output in /artifacts/
5. Provide feedback in /feedback/{artifact}_v{N}_critique.md

## Quality Standards
- All documents: Flesch readability >60
- Code: 80% test coverage, zero critical security issues
- Prompts: Valid XML, include validation checklists
````

*(Note: The "Current Phase" section was removed to simplify the root context file)*.

---

## 5. Prompt Template Specifications

### 5.1 Generator Prompt Structure

All generator prompts follow this XML schema:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<generator_prompt>
  <metadata>
    <name>{Task}_Generator</name>
    <version>1.{iteration}</version>
    <sdlc_phase>{Vision|Epic|PRD|Story|Spec|Code|Test}</sdlc_phase>
    <depends_on>{upstream_artifact_path}</depends_on>
  </metadata>

  <system_role>
    You are {expert persona} specializing in {domain}.
    Your output must follow the template at {template_path}.
  </system_role>

  <task_context>
    <background>
      {Relevant context from research document}
    </background>
    <input_artifacts>
      <artifact path="{upstream_path}" type="{doc_type}">
        {Load content here during execution}
      </artifact>
    </input_artifacts>
    <constraints>
      {Specific requirements for this phase}
    </constraints>
  </task_context>

  <instructions>
    <step priority="1">
      Load template from {template_path}
    </step>
    <step priority="2">
      Analyze input artifact: {upstream_artifact}
    </step>
    <step priority="3">
      Generate {terminal_artifact} following template structure
    </step>
    <step priority="4">
      Create next-level generator prompt: {next-generator}.xml
    </step>
    <step priority="5">
      Validate outputs against checklist
    </step>
    </instructions>

  <output_format>
    <terminal_artifact>
      <path>/artifacts/{path}/{name}_v{iteration}.md</path>
      <validation_checklist>
        {Task-specific criteria from TODO.md}
      </validation_checklist>
    </terminal_artifact>

    <next-generator>
      <path>/prompts/{next_task}_generator.xml</path>
      <validation>Must be valid XML, include all required sections</validation>
    </next-generator>
  </output_format>

  <validation>
    After generation, verify:
    - [ ] Terminal artifact has all template sections
    - [ ] Readability: Flesch score >60 (manual check)
    - [ ] Traceability: References upstream artifact
    - [ ] Next generator: Syntactically valid, executable
  </validation>
</generator_prompt>
```

---

### 5.2 Template Artifact Structure

Templates extracted from research document (Section 6.1-6.4) converted to:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<template>
  <metadata>
    <name>{Artifact_Type}_Template</name>
    <version>1.0</version>
    <source>Section {X.Y} of research document</source>
  </metadata>

  <instructions>
    <guideline>Fill all sections marked [placeholder]</guideline>
    <guideline>{Specific requirement from research}</guideline>
  </instructions>

  <structure format="markdown">
    <![CDATA[
    # {Artifact Title}

    ## Section 1: {Name}
    [Placeholder with instructions]

    ## Section 2: {Name}
    [Placeholder with instructions]

    ...
    ]]>
  </structure>

  <validation_checklist>
    <criterion>All placeholders replaced with content</criterion>
    <criterion>{Quality requirement from research}</criterion>
  </validation_checklist>

  <examples>
    <example source="Section {X.Y}">
      {Optional: Include exemplar from research}
    </example>
  </examples>
</template>
```

---

## 6. Execution Playbook

### 6.1 Phase 1: Bootstrap (This Session)

**Human Actions**:
1. Run master prompt execution
2. Answer clarification questions (Q1-Q13)
3. Review generated artifacts:
   - `/docs/context_engineering_strategy_v1.md`
   - `/TODO.md`
   - `/CLAUDE.md`
   - `/prompts/templates/*.xml`
   - `/prompts/product-vision-generator.xml`
4. Approve to proceed to Phase 2

**AI Actions** (Master Prompt):
1. Extract templates from research document
2. Generate folder structure
3. Create universal executor (`generate.xml`)
4. Generate first generator prompt (Product Vision)
5. Exit context with handoff instructions

---

### 6.2 First Generator Execution (Context C1)

**Task**: TASK-004 - Execute Product Vision Generator

**Human Actions**:
1. Start new Claude Code session
2. Run: `/generate TASK-004`
3. Confirm generation of specialized CLAUDE.md
4. Review `/artifacts/product_vision_v1.md`
5. Create `/feedback/product_vision_v1_critique.md` with notes
6. Run: `/refine product-vision-generator`
7. Repeat for v2, v3
8. Approve final version

**AI Actions** (generate.xml):
1. Parse TASK-004 from `/TODO.md`
2. Load context:
   - `/CLAUDE.md`
   - `/prompts/product-vision-generator.xml`
   - `/prompts/templates/product-vision-template.xml`
3. Execute generator
4. Save outputs:
   - `/artifacts/product_vision_v1.md`
5. Update `/CLAUDE.md` with current phase
6. Report completion with validation checklist status

---

### 6.3 Iteration & Refinement

**Iteration 1 > 2**:
1. Human reviews v1 artifact
2. Creates critique file: `/feedback/{artifact}_v1_critique.md`
3. Runs: `/refine {task}_generator`
4. System:
   - Loads generator + critique
   - Applies Self-Refine pattern (research Section 2.4)
   - Updates generator prompt based on feedback
   - Re-executes > outputs v2
5. Human reviews v2

**Iteration 2 > 3**:
1. Human reviews v2 artifact
2. Creates `/feedback/{artifact}_v2_critique.md`
3. Runs refinement again
4. System:
   - Analyzes patterns from v1>v2 critiques
   - Updates `/docs/context_engineering_strategy_v1.md` (lessons learned)
   - Refines generator
   - Executes > outputs v3
5. Human approves final version

**Approval Gate**:
```
Human checklist:
[ ] All template sections complete
[ ] Readable by non-expert (subjective Flesch >60)
[ ] Actionable (clear next steps)
[ ] Traceable (links to upstream artifacts)
[ ] Next generator is valid XML
```

---

### 6.4 Cascade to Next SDLC Phase

**Task**: `TASK-009 - Execute Epic Generator v1

**Human Actions**:
1. Start new Claude Code session (C2)
2. Run: `/generate TASK-002`
3. When prompted for input artifact location, confirm:
   `/artifacts/product_vision_v3.md`
4. Proceed with same iteration cycle (v1 > v2 > v3)

**AI Actions**:
1. Load context:
   - `/CLAUDE.md`
   - `/prompts/epic-generator.xml` (created in C1)
   - `/prompts/templates/epic-template.xml`
   - `/artifacts/product_vision_v3.md` (dependency)
2. Execute generator
3. Save outputs:
   - `/artifacts/epics/epic_001_v1.md` ... `epic_00N_v1.md`
   - `/prompts/prd-generator.xml`
4. Iterate (v1 > v2 > v3) per epic
5. Update `/CLAUDE.md` with phase progression

**Note**: Epic generator outputs **multiple documents** (one per epic). Folder structure prevents collision.

---

### 6.5 Backlog Story Generation (Context C4)

**Task**: TASK-014 - Execute Backlog Story Generator

**Human Actions**:
1. Start new Claude Code session (C4)
2. Run: `/generate TASK-014`
3. When prompted for PRD location, confirm: `/artifacts/prds/prd_001/prd_v3.md`
4. Proceed with iteration cycle (v1 > v2 > v3)

**AI Actions**:
1. Load context:
   - `/CLAUDE.md`
   - `/prompts/backlog-story-generator.xml` (created in C3)
   - `/prompts/templates/backlog-story-template.xml`
   - `/artifacts/prds/prd_001/prd_v3.md` (dependency)
   - `/artifacts/prds/prd_001/TODO.md` (story status tracking)
2. Execute generator
3. Save outputs:
   - `/artifacts/backlog_stories/US-01-01_feature/backlog_story_v1.md`
   - `/artifacts/backlog_stories/US-01-01_feature/TODO.md`
   - `/prompts/adr-generator.xml`
4. Iterate (v1 > v2 > v3)
5. Update `/CLAUDE.md` with phase progression
6. Update `/artifacts/prds/prd_001/TODO.md` to mark story as processed

**Note**: Backlog Story Generator may split one high-level story into multiple detailed backlog stories, each in its own subfolder.

---

## 7. Quality Metrics

### 7.1 Per-Task Validation Criteria

Defined in `/TODO.md` for each task. Example:

```markdown
## TASK-001: Execute Product Vision Generator

**Success Criteria**:
- [ ] Vision document contains 8 required sections (per template)
- [ ] Problem statement includes quantified pain points
- [ ] Success metrics are SMART-compliant
- [ ] Target users clearly defined
- [ ] Epic generator prompt is syntactically valid XML
- [ ] Flesch readability >60 (manual assessment)
```

### 7.2 Framework-Level Metrics

**Iteration Efficiency**:
- Track # of iterations to reach approval (target: ≤3)
- Measure % of validation criteria met per iteration

**Context Optimization**:
- Monitor token usage per generator execution
- Target: <50% of Claude's context window per task

**Automation Progression**:
- Phase 1: 100% human-triggered
- Phase 2 Target: 70% automated (self-critique), 30% human approval
- Phase 3 Future: 90% automated with threshold-based gates

### 7.3 Quality Thresholds (Phase 2 Automation)

**Criteria for automated iteration**:
```
IF (validation_checklist_pass_rate >= 80%) AND
   (critique_severity NOT IN ['critical', 'blocker'])
THEN auto-approve and proceed
ELSE prompt human for review
```

---

## 8. Lessons Learned Log

### 8.1 Template Extraction Insights
*To be populated after TASK-000 (template extraction)*

### 8.2 Generator Refinement Patterns
*To be populated after first 3-iteration cycle*

### 8.3 Context Optimization Findings
*Track what context components were unnecessary/critical*

### 8.4 Automation Maturity Progression
*Document transitions from manual > semi-automated > fully automated*

---

## 9. Maturity Roadmap

### 9.1 Current State (PoC Phase 1)
- **Execution**: Human-triggered via `/generate {task_id}`
- **Iteration**: Manual critique files + human approval
- **Quality Gates**: Checklist-based, subjective assessment

### 9.3 Target State (Phase 3)
**Graduation Criteria**:
- [ ] Complete 1 full SDLC cascade (Vision > Test)
- [ ] Validate 3-iteration refinement on >= 3 different generators
- [ ] Document >= 5 lessons learned in strategy doc

**Enhancements**:
- **Task Execution Trigger**: Graduate to semi-automated
  - System generates execution script from TODO.md
  - Human runs script (reduces manual lookup)
- **Iteration Trigger**: Graduate to self-critique
  - Automated Chain-of-Verification (research Section 2.4)
  - Human approval only on 80% threshold failures
- **Quality Assessment**: Graduate to quantitative
  - Automated Flesch scoring via readability API
  - Structured validation output (JSON checklist)

### 9.4 Future State (Phase 4)
**Vision**: Fully autonomous SDLC orchestration

**Capabilities**:
- Agentic workflow: Reads TODO.md > spawns contexts > executes > validates > iterates
- Multi-agent critique: Separate generator/reviewer agents (research Section 7.7)
- Adaptive thresholds: ML-based quality prediction
- Live documentation: Auto-updates strategy doc with learnings

**Constraints**:
- Requires Claude Code API enhancements (context spawning)
- Human oversight remains for critical decisions (architecture, security)

---

## 10. References & Traceability

### 10.1 Research Document Mapping

| Framework Component | Research Section | Page/Line Ref |
|---------------------|------------------|---------------|
| Generator Prompt Structure | 1.1 Anatomy of Effective Prompt | Lines 49-92 |
| XML Tag Usage | 5.1 Claude Optimization | Lines 456-465 |
| Template Formats | 6.1-6.4 Documentation Prompts | Lines 620-1117 |
| Self-Refine Pattern | 2.4 Self-Correction | Lines 176-184 |
| Chain-of-Verification | 2.4 CoVe | Lines 186-194 |
| Validation Metrics | 4.5 RAGAS Evaluation | Lines 347-366 |
| Iterative Clarification | 1.3 Clarification Pattern | Lines 116-128 |

### 10.2 Decision Log

| Decision | Rationale | Date |
|----------|-----------|------|
| XML format for templates | Research Section 5.1: Claude parses XML well | 2025-10-06 |
| 3-iteration refinement | Research Section 2.4: Self-Refine pattern | 2025-10-06 |
| Standalone contexts | Prevents context pollution, enforces modularity | 2025-10-06 |
| Lazy-generated CLAUDE.md | Reduces upfront work, validates on-demand need | 2025-10-06 |
| File system reads for deps | Simple, no complex passing; validated during exec | 2025-10-06 |

---

## Appendix A: Glossary

- **Generator Prompt**: XML artifact that produces terminal deliverable + next-level generator
- **Terminal Artifact**: Final document (e.g., Product Vision v3.md), not a template
- **Template**: XML-formatted prompt with structure/validation for specific document type
- **Specialized CLAUDE.md**: Phase-specific context file (lazy-generated)
- **Iteration**: Refinement cycle (v1 > critique > v2 > critique > v3)
- **Context Isolation**: Each generator executes in fresh Claude Code session
- **Cascade**: SDLC progression through generated prompts (Vision>Epic>PRD...)
- **High-Level User Story**: Conceptual story in PRD, references functional requirements
- **Backlog User Story**: Detailed, implementation-ready story with non-functional requirements, technical requirements, and tasks

---

**Document Version**: 1.0
**Status**: Draft (Pending approval to generate artifacts)
**Next Action**: Generate `/TODO.md` and folder structure upon user confirmation
**Owner**: Context Engineering PoC Team
