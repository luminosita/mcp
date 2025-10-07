# Context Engineering Strategy Document v1.0

## Executive Summary

This document defines the **Context Engineering Framework** for AI-assisted software development using recursive prompt generation. The framework transforms traditional artifact creation into a self-propagating chain where prompts generate both deliverables and next-level generator prompts.

**Core Innovation**: Treat prompts as executable artifacts that spawn subsequent prompts, creating an SDLC-aligned cascade from Product Vision → Epic → PRD → Story → Spec → Code → Test.

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
  2. Next-level generator prompt (e.g., epic_generator.xml)
- Chain depth: SDLC-aligned (Vision → Epic → PRD → Story → ADR+Spec → Code → Test)

### 1.4 Progressive Automation Maturity
- **Phase 1 (PoC)**: Human-triggered execution with manual approval gates
- **Phase 2 (Target)**: Semi-automated with self-critique loops
- **Phase 3 (Future)**: Fully automated orchestration with quality thresholds

---

## 2. Workflow Phases

### 2.1 Phase 1: Meta-Prompt Generation (This Session)
**Objective**: Bootstrap the framework with foundational artifacts

**Inputs**:
- `/docs/advanced_prompt_engineering_software_docs_code_final.md` (research)
- User responses to clarification questions

**Outputs**:
- `/docs/context_engineering_strategy_v1.md` (this document)
- `/TODO.md` (master task list with dependencies)
- `/CLAUDE.md` (root orchestration guide)
- `/.claude/commands/execute-generator.xml` (universal executor)
- `/prompts/templates/*.xml` (extracted/generated templates)
- `/prompts/product_vision_generator.xml` (first exemplar)
- `/docs/product-idea.md` (initial CLI tool concept stub)

**Validation Criteria**:
- [ ] All templates extracted from research document (Section 6.1-6.4)
- [ ] Master Plan contains enumerated tasks (TASK-001, TASK-002...)
- [ ] Each task has explicit validation criteria
- [ ] Folder structure supports versioned outputs (v1, v2, v3)

---

### 2.2 Phase 2: Generator Execution & Iteration
**Objective**: Execute generator prompts with 3-iteration refinement cycle

**Execution Pattern** (per generator):
```
Iteration 1: Execute generator → Generate artifact v1
↓
Human Review: Approve/critique artifact v1
↓
Iteration 2: Refine generator based on feedback → Generate artifact v2
↓
Human Review: Approve/critique artifact v2
↓
Iteration 3: Apply learnings → Update Strategy Doc → Generate artifact v3
↓
Human Approval: Accept final version
```

**Context Setup** (example for Product Vision Generator):
```
New Claude Code Session C1
├── /CLAUDE.md (root)
├── /prompts/CLAUDE-product-vision.md (specialized, lazy-generated)
├── /prompts/product_vision_generator.xml
├── /prompts/templates/product-vision-template.xml
└── /docs/product-idea.md
```

**Outputs** (from C1):
```
/artifacts/product_vision_v1.md (Iteration 1)
/artifacts/product_vision_v2.md (Iteration 2)
/artifacts/product_vision_v3.md (Iteration 3 - final)
/prompts/epic_generator.xml (next-level generator)
```

**Validation Criteria** (Product Vision example):
- [ ] Contains all 8 required sections (from template)
- [ ] Problem statement includes quantified pain points
- [ ] Success metrics are SMART-compliant
- [ ] Target users clearly defined
- [ ] Epic generator prompt is syntactically valid XML
- [ ] Flesch readability score >60 (manual assessment in Phase 1)

---

### 2.3 Phase 3: Cascade Execution
**Objective**: Propagate through SDLC phases using generated prompts

**Dependency Chain**:
```
C1: product_vision_generator.xml
    ├── Reads: product-idea.md
    ├── Outputs: product_vision_v3.md + epic_generator.xml

C2: epic_generator.xml
    ├── Reads: product_vision_v3.md (file system lookup)
    ├── Outputs: /artifacts/epics/epic_001.md ... epic_00N.md + prd_generator.xml

C3: prd_generator.xml
    ├── Reads: epic_001.md (specified via argument)
    ├── Outputs: /artifacts/prds/epic_001_prd_v3.md + user_story_generator.xml

[Continue cascade...]
```

**File Routing Convention**:
```
/artifacts/
├── product_vision_v{iteration}.md
├── epics/
│   ├── epic_{id}_v{iteration}.md
│   └── ...
├── prds/
│   ├── epic_{id}_prd_v{iteration}.md
│   └── ...
├── user_stories/
│   ├── epic_{id}_story_{id}_v{iteration}.md
│   └── ...
└── [code/tests follow similar pattern]
```

---

## 3. Folder Structure Standard

```
/
├── .claude/
│   └── commands/
│       ├── execute-generator.xml       # Universal executor (fixed)
│       └── refine-generator.xml        # Refinement orchestrator
│
├── docs/
│   ├── advanced_prompt_engineering_software_docs_code_final.md  # Research (immutable)
│   ├── context_engineering_strategy_v1.md # This document
│   └── product-idea.md                 # CLI tool initial concept
│
├── prompts/
│   ├── CLAUDE-product-vision.md        # Specialized contexts (lazy-generated)
│   ├── CLAUDE-epic.md
│   ├── CLAUDE-prd.md
│   ├── [...additional specialized contexts...]
│   │
│   ├── templates/                      # XML-formatted templates
│   │   ├── product-vision-template.xml
│   │   ├── epic-template.xml
│   │   ├── prd-template.xml
│   │   ├── adr-template.xml
│   │   ├── tech-spec-template.xml
│   │   └── user-story-template.xml
│   │
│   ├── product_vision_generator.xml    # Generator prompts
│   ├── epic_generator.xml              # (created by prior generators)
│   ├── prd_generator.xml
│   └── [...cascade continues...]
│
├── artifacts/                          # All generated deliverables
│   ├── product_vision_v{1-3}.md
│   ├── epics/
│   ├── prds/
│   ├── user_stories/
│   ├── specs/
│   ├── code/
│   └── tests/
│
├── feedback/                           # Human critique logs
│   ├── product_vision_v1_critique.md
│   ├── product_vision_v2_critique.md
│   └── [...per iteration...]
│
├── CLAUDE.md                           # Root orchestration
└── TODO.md                             # Master Plan (single source of truth)
```

**Design Rationale**:
- Max 3 levels deep (prevents navigation complexity)
- Versioned outputs prevent overwriting during iterations
- Specialized CLAUDE.md co-located with prompts directory
- Feedback folder supports human-in-loop iteration

---

## 4. CLAUDE.md Orchestration Rules

### 4.1 Root CLAUDE.md (`/CLAUDE.md`)

**Purpose**: Project-wide context and navigation guide

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
2. Run: /kickoff execute-generator {task_id}
3. System loads:
   - /prompts/{task}_generator.xml
   - /prompts/CLAUDE-{task}.md (auto-generates if missing)
   - Required templates from /prompts/templates/
4. Review output in /artifacts/
5. Provide feedback in /feedback/{artifact}_v{N}_critique.md

## Quality Standards
- All documents: Flesch readability >60
- Code: 80% test coverage, zero critical security issues
- Prompts: Valid XML, include validation checklists

## Current Phase
[Updated by each generator execution]
Phase: {Vision|Epic|PRD|Story|Spec|Code|Test}
Last completed: {artifact name}
Next generator: {path to next .xml}
```

---

### 4.2 Specialized CLAUDE.md (`/prompts/CLAUDE-{task}.md`)

**Purpose**: Task-specific guidance and context

**Lifecycle**: Lazy-generated on first execution
- Execute-generator checks if `/prompts/CLAUDE-{task}.md` exists
- If missing: Prompts human for confirmation → Generates from template
- If exists: Loads directly

**Contents Template**:
```markdown
# Specialized Context: {Task Name}

## Task-Specific Guidelines
[Domain expertise for this SDLC phase]

## Template Location
Path: /prompts/templates/{task}-template.xml
Validation: [Checklist for this template type]

## Input Requirements
Required files:
- {upstream artifact path}
- {template path}
Optional: {additional context}

## Output Specifications
Terminal artifact: /artifacts/{path}/{name}_v{N}.md
Next generator: /prompts/{next_task}_generator.xml

## Common Pitfalls
[Lessons learned from research document]

## Example Outputs
[Reference examples from Section 6.X of research]
```

**Boundary Definition**:
- **Root CLAUDE.md**: Project navigation, universal standards
- **Specialized CLAUDE.md**: Phase-specific templates, validation rules, examples

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
      Create next-level generator prompt: {next_generator}.xml
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

    <next_generator>
      <path>/prompts/{next_task}_generator.xml</path>
      <validation>Must be valid XML, include all required sections</validation>
    </next_generator>
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
1. Run `/kickoff` with master prompt
2. Answer clarification questions (Q1-Q13)
3. Review generated artifacts:
   - `/docs/context_engineering_strategy_v1.md`
   - `/TODO.md`
   - `/CLAUDE.md`
   - `/prompts/templates/*.xml`
   - `/prompts/product_vision_generator.xml`
4. Approve to proceed to Phase 2

**AI Actions** (Master Prompt):
1. Extract templates from research document
2. Generate folder structure
3. Create universal executor (`execute-generator.xml`)
4. Generate first generator prompt (Product Vision)
5. Create product idea stub (`/docs/product-idea.md`)
6. Exit context with handoff instructions

---

### 6.2 Phase 2: First Generator Execution (Context C1)

**Task**: TASK-001 - Execute Product Vision Generator

**Human Actions**:
1. Start new Claude Code session
2. Run: `/kickoff execute-generator TASK-001`
3. System prompts if `/prompts/CLAUDE-product-vision.md` missing
4. Confirm generation of specialized CLAUDE.md
5. Review `/artifacts/product_vision_v1.md`
6. Create `/feedback/product_vision_v1_critique.md` with notes
7. Run: `/kickoff refine-generator product_vision_generator`
8. Repeat for v2, v3
9. Approve final version

**AI Actions** (execute-generator.xml):
1. Parse TASK-001 from `/TODO.md`
2. Check for `/prompts/CLAUDE-product-vision.md`
   - If missing: Generate from template (with human approval)
3. Load context:
   - `/CLAUDE.md`
   - `/prompts/CLAUDE-product-vision.md`
   - `/prompts/product_vision_generator.xml`
   - `/prompts/templates/product-vision-template.xml`
   - `/docs/product-idea.md`
4. Execute generator
5. Save outputs:
   - `/artifacts/product_vision_v1.md`
   - `/prompts/epic_generator.xml`
6. Update `/CLAUDE.md` with current phase
7. Report completion with validation checklist status

---

### 6.3 Phase 3: Iteration & Refinement

**Iteration 1 → 2**:
1. Human reviews v1 artifact
2. Creates critique file: `/feedback/{artifact}_v1_critique.md`
3. Runs: `/kickoff refine-generator {task}_generator`
4. System:
   - Loads generator + critique
   - Applies Self-Refine pattern (research Section 2.4)
   - Updates generator prompt based on feedback
   - Re-executes → outputs v2
5. Human reviews v2

**Iteration 2 → 3**:
1. Human reviews v2 artifact
2. Creates `/feedback/{artifact}_v2_critique.md`
3. Runs refinement again
4. System:
   - Analyzes patterns from v1→v2 critiques
   - Updates `/docs/context_engineering_strategy_v1.md` (lessons learned)
   - Refines generator
   - Executes → outputs v3
5. Human approves final version

**Approval Gate**:
```
Human checklist:
☐ All template sections complete
☐ Readable by non-expert (subjective Flesch >60)
☐ Actionable (clear next steps)
☐ Traceable (links to upstream artifacts)
☐ Next generator is valid XML
```

---

### 6.4 Phase 4: Cascade to Next SDLC Phase

**Task**: TASK-002 - Execute Epic Generator

**Human Actions**:
1. Start new Claude Code session (C2)
2. Run: `/kickoff execute-generator TASK-002`
3. When prompted for input artifact location, confirm:
   `/artifacts/product_vision_v3.md`
4. Proceed with same iteration cycle (v1 → v2 → v3)

**AI Actions**:
1. Load context:
   - `/CLAUDE.md`
   - `/prompts/CLAUDE-epic.md` (lazy-generated if missing)
   - `/prompts/epic_generator.xml` (created in C1)
   - `/prompts/templates/epic-template.xml`
   - `/artifacts/product_vision_v3.md` (dependency)
2. Execute generator
3. Save outputs:
   - `/artifacts/epics/epic_001_v1.md` ... `epic_00N_v1.md`
   - `/prompts/prd_generator.xml`
4. Iterate (v1 → v2 → v3) per epic
5. Update `/CLAUDE.md` with phase progression

**Note**: Epic generator outputs **multiple documents** (one per epic). Folder structure prevents collision.

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
- [ ] Traceability: References product-idea.md
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
*Document transitions from manual → semi-automated → fully automated*

---

## 9. Maturity Roadmap

### 9.1 Current State (PoC Phase 1)
- **Execution**: Human-triggered via `/kickoff execute-generator {task_id}`
- **Iteration**: Manual critique files + human approval
- **Quality Gates**: Checklist-based, subjective assessment

### 9.2 Target State (Phase 2)
**Graduation Criteria**:
- [ ] Complete 1 full SDLC cascade (Vision → Test)
- [ ] Validate 3-iteration refinement on ≥3 different generators
- [ ] Document ≥5 lessons learned in strategy doc

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

### 9.3 Future State (Phase 3)
**Vision**: Fully autonomous SDLC orchestration

**Capabilities**:
- Agentic workflow: Reads TODO.md → spawns contexts → executes → validates → iterates
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
- **Iteration**: Refinement cycle (v1 → critique → v2 → critique → v3)
- **Context Isolation**: Each generator executes in fresh Claude Code session
- **Cascade**: SDLC progression through generated prompts (Vision→Epic→PRD...)

---

## Appendix B: Task Graduation Checklist

Track automation maturity per task type:

| Task Type | Phase 1 (Manual) | Phase 2 (Semi-Auto) | Phase 3 (Full-Auto) |
|-----------|------------------|---------------------|---------------------|
| Execution Trigger | ☐ Human runs command | ☐ Script-assisted | ☐ Agentic spawn |
| Iteration Trigger | ☐ Manual critique | ☐ Self-critique + approval | ☐ Threshold-based |
| Quality Assessment | ☐ Subjective checklist | ☐ Quantitative metrics | ☐ ML prediction |
| Context Assembly | ☐ Manual file lookup | ☐ Convention-based load | ☐ Dependency graph |

---

**Document Version**: 1.0
**Status**: Draft (Pending approval to generate artifacts)
**Next Action**: Generate `/TODO.md` and folder structure upon user confirmation
**Owner**: Context Engineering PoC Team
