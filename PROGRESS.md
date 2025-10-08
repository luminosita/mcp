# Progress Steps
## Next Steps
- feedback/context_engineering_strategy_v1_critique_v3.md
- rewrite TASK_003 based on critique_v3 file before execution
- verify Claude context is in the task report

## Open Questions
### PRD Generator
- How is Epic ID specified? Attribute, extraction from TASK name?

### Backlog Story Generator
- How is PRD ID, High-level User Story ID specified? Attribute, extraction from TASK name?

### Product Management 
- Adding new PRDs with TODO.md or directly invoking commands? Probably update to Epic's (non)functional requirements
- Adding new high-level user stories with TODO.md or directly invoking commands? Probably update to PRD's (non)functional requirements
- Adding new backlog user stories with TODO.md or directly invoking commands? Probably update to PRD's (non)functional requirements
- Adding new high-level user stories without PRD reference (standalone) - research required
- Adding new backlog user stories without PRD/high-level US reference (standalone -> enhancements) - research required
- Adding new implementation tasks without US reference (standalone -> quick bug fix) - research required

## Pre-finalization
- `docs/research/research_coverage_evaluation.md`
- verify that all requests from CHAT.md are applied (or create AI report)
- review all documents from the beginning
- analyze all `portal` documents

## Finalization
- remove CLAUDE-*.md lazy generation instructions, keep "if exists" verification
- remove next_generator instructions, keep only reference to next_generator to be invoked in the report
- strategy doc update
- GRADUATION.md review

## Next Phases
### Phase 2 
    * software implementation generator prompts (source code, unit tests, deployments)
    * specialed CLAUDE.md files in `portal` project 
    * TODO.md tasks
    * strategy doc update
    * GRADUATION.md
### Phase 3
    * generate MCP Server implementation 
    * TODO.md tasks 
    * strategy doc update
### Phase 4
    * move AI artifacts to MCP server 
    * tracking strategy (tracking TODO.md files, PRDs, USs ...)
    * strategy doc update
    * add new product repo initialization tool to MCP Server
### Phase 5
    * Backlog product
### Phase 6
    * SHH tool using MCP Server (final MCP server end-to-end test)
    * add full git support (PR merge requests)
    * add CI/CD 
### Phase 7
    * add RAG tool to MCP server
    * index all AI artifacts 
    * index source code
### Phase 8 
    * MCP server graduation to semi-automation/full automation software implementation
    * Task orchestration automatization with Backlog tasks 
    * Sub-agents
