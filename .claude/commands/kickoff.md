iterative learning / proof of concept
```markdown
# Prompt Version 0.1
# Changes: First draft
# Performance: n/a
# Date: 2025-10-06
```

Prompt:
```xml
<system_role>
You are a senior AI prompt engineer, with expertise in LLM context engineering
</system_role>

<task_context>
    <Background>
        We did AI-assisted deep research on Context Engineering paradigm covering the following topics:
        - advanced prompt engineering techniques
        - usage of context engineering as sophisticated process to documentation and source code generation for software products
        - usage of RAG 2.0 to efficiently form the basis of LLM contexts for specific tasks
        - iterative prompt generation process based on validation, testing and measured data
    </Background>
    <Goals>
        <Goal>Create a proof of concept following best practices outlined in the main document</Goal>
        <Goal>Follow iterative learning process by covering topics outlined in the main document using Claude Code AI Agent</Goal>
        <Goal>Establish a plan for every step of the processs</Goal>
        <Goal>Define and prioritize list of topics to plan and execute</Goal>
        <Goal>Clarify in details and with examples each topic</Goal>
        <Goal>Generate product vision, epics document, PRDs and the rest of the artifacts outlined in the main document</Goal>
        <Goal>Generate source code, unit tests, deployment artifacts outlined in the main document</Goal>
        <Goal>Generate inital CLAUDE.md documents</Goal>
        <Goal>Generate comprehensive folder structure</Goal>
        <Goal>Generate comprehensive structured prompt for each task/sub task of the plan</Goal>
    </Goals>
    <Constraints>
        <Constraint>We will cover only Context Engineering part outlined in the main document<Constraint>
        <Constraint>We will completely skip RAG related topics<Constraint>
    </Constraints>
</task_context>

<input_data>
    <documents>
        <document ref="main">@docs/advanced_prompt_engineering_software_docs_code_final.md</document>
    </documents>
</input_data>

<process>
1. ANALYZE: Identify gaps (clarity of goals/instrutions, scope, constraints, success criteria)
2. CLARIFY: Ask 3-5 specific questions
3. CONFIRM: Verify understanding
4. GENERATE: Proceed only after confirmation
</process>

<instructions>
    <instruction>Do a deep analysis of the main document</instruction>
    <instruction>Concentrating only on Context Engineering topics, generate a comprehensive plan for our proof of concept project</instruction>
    <instruction>Generate inital TODO.md file with tasks defined in the plan</instruction>
    <instruction>Each task should follow the defined process</instruction>
    <instruction>As a substitution for RAG our AI Agent will use hybrid CLAUDE.md strategy. Main CLAUDE.md file will be placed in the root of the project. Specialized CLAUDE.md files will be generated within subfolders designated for specialized tasks (concrete documentation prompts and templates generation, source code implementation, unit tests, deployment, and etc). Main CLAUDE.md will instruct AI Agent where to find context information for a particular task. Reason for this approach is to use very simplified RAG-like system for context priming</instruction>
    <instruction>Generate inital CLAUDE.md as base context for the kickoff. The file will progress together with the project and will be constantly upgraded with each step</instruction>
    <instruction>Generate inital folder structure</instruction>
    <instruction>Output formats and quality criteria for the artifacts (documents, templates, prompts, source code, snippets) will also be generated and upgraded with each step</instructions>
</instructions>
```