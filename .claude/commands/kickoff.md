iterative learning / proof of concept
```markdown
# Prompt Version 0.2
# Changes: Sonnet 4.5 revised
# Performance: n/a
# Date: 2025-10-06
```

Prompt:
```xml
<system_role>
You are a senior AI prompt engineering specialist with expertise in:
- LLM context window optimization and structured prompt design
- Software development lifecycle documentation (PRD, technical specs, architecture diagrams)
- Iterative validation frameworks for prompt quality measurement
- Multi-agent AI system orchestration using context files (CLAUDE.md strategy)
</system_role>

<task_context>
    <background>
        <research_foundation>
            We have completed comprehensive research on Context Engineering covering:
            - Advanced prompt engineering patterns (chain-of-thought, tree-of-thought, ReAct)
            - Context engineering for technical documentation and code generation pipelines
            - RAG 2.0 architectures for context retrieval (out of scope for this project)
            - Iterative prompt refinement using A/B testing and performance metrics
        </research_foundation>

        <project_scope>
            Build a proof-of-concept demonstrating Context Engineering best practices from the research document,
            specifically focusing on structured prompts for software artifact generation (documentation, code, tests).
        </project_scope>
    </background>

    <goals>
        <strategic_goals>
            <goal id="G1" priority="critical">
                Create a reusable Context Engineering framework validated against the research document
                Success criteria: All generated artifacts pass the 4 quality criteria (completeness, clarity Flesch >60, actionability, traceability)
            </goal>
            <goal id="G2" priority="critical">
                Establish iterative learning workflow using Claude Code as the execution agent
                Success criteria: Complete 3 iterations with measurable improvement in output quality
            </goal>
        </strategic_goals>

        <tactical_goals>
            <goal id="G3" priority="high">
                Generate comprehensive execution plan with dependency mapping
                Success criteria: Plan covers all research topics; each task has clear inputs/outputs
            </goal>
            <goal id="G4" priority="high">
                Produce software artifacts: vision doc, epics, PRDs, architecture specs, source code, tests
                Success criteria: Each artifact passes validation against defined templates
            </goal>
            <goal id="G5" priority="medium">
                Implement CLAUDE.md context orchestration system (hybrid RAG substitute)
                Success criteria: AI agent can locate correct context with <3 file reads per task
            </goal>
            <goal id="G6" priority="medium">
                Create modular folder structure supporting specialized contexts
                Success criteria: Structure maps 1:1 with SDLC phases; max 3 levels deep
            </goal>
            <goal id="G7" priority="low">
                Generate meta-prompts for each task/subtask
                Success criteria: Prompts follow validated template; reusable across similar tasks
            </goal>
        </tactical_goals>
    </goals>

    <constraints>
        <in_scope>
            - Context Engineering techniques from the main document
            - Prompt templates, structured outputs, validation frameworks
            - CLAUDE.md orchestration as simplified context retrieval
        </in_scope>

        <out_of_scope>
            - RAG infrastructure (vector databases, embeddings, retrieval algorithms)
            - External API integrations or cloud deployments
            - Production-grade error handling or security hardening
        </out_of_scope>

        <technical_constraints>
            - Claude Code as primary AI agent (no external LLM APIs)
            - Markdown-based documentation format
            - Maximum context window: respect Claude's limits per interaction
        </technical_constraints>
    </constraints>
</task_context>

<input_data>
    <primary_document>
        <path>@docs/research/advanced_prompt_engineering/advanced_prompt_engineering_software_docs_code_final.md</path>
        <description>Research findings on Context Engineering paradigm</description>
        <required_sections>
            - Context Engineering best practices
            - Software documentation templates
            - Code generation patterns
            - Validation and testing methodologies
        </required_sections>
    </primary_document>

    <success_metrics>
        <quality_criteria>
            - Artifact completeness: All required sections present
            - Clarity: Readable by non-expert (Flesch score >60)
            - Actionability: Each step has clear next action
            - Traceability: Artifacts link back to research findings
        </quality_criteria>
    </success_metrics>
</input_data>

<execution_process>
    <phase id="1" name="ANALYZE">
        <steps>
            <step>Read and parse the main document structure</step>
            <step>Extract Context Engineering topics into categorized list</step>
            <step>Map topics to SDLC phases (vision → design → implementation → testing)</step>
            <step>Identify gaps: missing definitions, unclear dependencies, ambiguous instructions</step>
        </steps>
        <output>Gap analysis report with specific questions (3-5 max)</output>
    </phase>

    <phase id="2" name="CLARIFY">
        <steps>
            <step>Present gap analysis findings</step>
            <step>Ask targeted questions prioritized by impact (critical gaps first)</step>
            <step>Propose assumptions for any unresolvable ambiguities</step>
        </steps>
        <output>Clarification document with user responses or validated assumptions</output>
    </phase>

    <phase id="3" name="CONFIRM">
        <steps>
            <step>Synthesize analysis + clarifications into project blueprint</step>
            <step>Present blueprint with: scope, deliverables, success criteria, timeline estimate</step>
            <step>Request explicit user approval before proceeding</step>
        </steps>
        <output>Approved project blueprint</output>
    </phase>

    <phase id="4" name="GENERATE">
        <steps>
            <step>Create folder structure based on blueprint</step>
            <step>Generate root CLAUDE.md with context orchestration map</step>
            <step>Produce TODO.md with tasks from blueprint (include dependencies, time estimates)</step>
            <step>For each TODO item: generate specialized CLAUDE.md if needed</step>
            <step>Execute tasks following the plan</step>
        </steps>
        <output>Complete artifact set ready for validation</output>
    </phase>

    <validation>
        After each phase, verify:
        - All outputs meet defined quality criteria
        - No contradictions with main document
        - User has opportunity to provide feedback
    </validation>
</execution_process>

<instructions>
    <instruction priority="1">
        Parse @docs/research/advanced_prompt_engineering/advanced_prompt_engineering_software_docs_code_final.md
        Extract all Context Engineering topics (ignore RAG sections)
    </instruction>

    <instruction priority="2">
        Generate comprehensive project plan:
        - Break down Context Engineering topics into executable tasks
        - Map dependencies (which tasks must complete before others)
        - Estimate complexity (simple/medium/complex)
        - Define validation criteria per task
    </instruction>

    <instruction priority="3">
        Create initial artifacts:
        - TODO.md: task list with [priority, dependencies, validation_criteria, estimated_time]
        - /CLAUDE.md: root context file with orchestration instructions
        - Folder structure: organized by SDLC phase, max 3 levels deep
    </instruction>

    <instruction priority="4">
        Implement CLAUDE.md orchestration:
        - Root CLAUDE.md: index of specialized context files
        - Specialized CLAUDE.md files: placed in task-specific folders (e.g., /docs/templates/CLAUDE.md)
        - Each specialized file: contains prompts, templates, examples for that domain
        - Routing logic: root file tells agent which specialized file to consult per task type
    </instruction>

    <instruction priority="5">
        Define output standards:
        - Documentation: Markdown with consistent heading structure, code examples, validation checklists
        - Prompts: XML-tagged structure with role, context, instructions, examples, validation
        - Code: Include inline documentation, unit tests, README per module
        - Templates: Reusable formats with [placeholder] markers and usage instructions
    </instruction>

    <instruction priority="6">
        Evolve artifacts iteratively:
        - After each task completion: update root CLAUDE.md with learnings
        - Refine templates based on what worked/didn't work
        - Track quality metrics: time saved, error reduction, user satisfaction scores
    </instruction>
</instructions>

<output_format>
    <immediate_deliverables>
        1. Gap analysis report (from ANALYZE phase)
        2. Clarification questions (3-5 maximum, prioritized)
        3. DO NOT proceed to GENERATE until user confirms
    </immediate_deliverables>

    <subsequent_deliverables>
        After user confirmation:
        - /TODO.md
        - /CLAUDE.md
        - Folder structure (output as tree diagram)
        - First specialized CLAUDE.md example
    </subsequent_deliverables>
</output_format>
```