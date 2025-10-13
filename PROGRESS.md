# Progress Steps

## CLAUDE.md
- [X] Move researches to artifacts/researches and update references
- [X] Rename product_vision_v1.md to proper naming format, move it to product_visions, and update references
- [X] File/folder structures for artifacts
- [X] Revise sub TODO.md (tracking)
    - [X] Verify the references of those TODO.md files
    - [X] Drop sub TODO.md files

## Validation
- [ ] Move tracebility generator validation checks to a proper section
    - [ ] Review generators for paths in tracebility sections
- [ ] Generator output file paths
- [ ] Read all generated epics
- [ ] Read all restructured research docs (business and implementation)
- [ ] Read all generators and templates (file paths removed, no validation duplications, defragmented validation instructions)
- [X] Check output file name for generators
- [ ] Remove all paths from generators and templates. Keep it only in CLAUDE.md (input, output)
- [ ] Evaluation related to required/optional input data for generators
- [ ] Remove Tracibility Checklists from templates (validate existance in generators)

## PRD Validation
- [ ] Technical Consideration sections were removed from Epics and saved into `artifacts/technical_considerations_from_epic.md`
    - [ ] Validate that these sections are generated in PRDs and compare the content

## Semi-automatic testing
- [ ] feedback/context_engineering_strategy_v1_critique_v3.md
- [ ] rewrite TASK_003 based on critique_v3 file before execution
- [ ] Review execute-generator
- [ ] verify Claude context is in the task report (execute-generator)
- [ ] Review refine

## Open Questions
### PRD Generator
- [X] How is Epic ID specified? Attribute, extraction from TASK name?

### Backlog Story Generator
- [X] How is PRD ID, High-level User Story ID specified? Attribute, extraction from TASK name?

### Product Management 
- [X] Adding new PRDs with TODO.md or directly invoking commands? Probably update to Epic's (non)functional requirements
- [X] Adding new high-level user stories with TODO.md or directly invoking commands? Probably update to PRD's (non)functional requirements
- [X] Adding new backlog user stories with TODO.md or directly invoking commands? Probably update to PRD's (non)functional requirements
- [X] Adding new high-level user stories without PRD reference (standalone) - research required
- [X] Adding new backlog user stories without PRD/high-level US reference (standalone -> enhancements) - research required
- [X] Adding new implementation tasks without US reference (standalone -> quick bug fix) - research required

## Pre-finalization
- [ ] `docs/research/advanced_prompt_engineering/research_coverage_evaluation.md`
- [ ] verify that all requests from CHAT.md are applied (or create AI report)
- [ ] review all documents from the beginning
- [ ] analyze all `claude-md` documents
- [ ] review strategy document, if is still needed


## Finalization
- [X] remove CLAUDE-*.md lazy generation instructions, keep "if exists" verification
- [X] remove next-generator instructions, keep only reference to next-generator to be invoked in the report
- [ ] strategy doc update
- [ ] GRADUATION.md review

## Implementation
### Where is the specification/guidelines on:
- [ ] entities
- [ ] value objects
- [ ] data models
- [ ] API contracts to be created
- [ ] DTO
- [ ] interfaces
- [ ] abstract classes
- [ ] patterns (observability, security, encryption, logging ...)
- [ ] libraries (utility/common, external integration)
- [ ] frameworks / SDKs

### QA Test Plan test plan creation

## Next Phases
### Phase 2 
    * software implementation generator prompts (source code, unit tests, deployments)
    * specialed CLAUDE.md files in `claude.md` project 
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
    * make all product management artifact related and trackable
        * PRD has multiple sections, each sections should be linked to something within sub-artifact (Functional req from PRD is linked to functional req of user story). This gives a clear pictures of general requirement coverage (analogus to Code coverage with tests)
    * Backlog event should trigger re-indexing of document repository items within RAG system 
        * adding of a new User Story, can add new feature in PRD, which shell trigger PRD re-index
### Phase 6
    * SHH tool using MCP Server (final MCP server end-to-end test)
    * add full git support (PR merge requests)
    * add CI/CD 
### Phase 7
    * add RAG tool to MCP server
        * every RAG indexed item should have re-index trigger defined to prohibit out-of-sync RAG results
    * index all AI artifacts 
    * index source code
### Phase 8 
    * MCP server graduation to semi-automation/full automation software implementation
    * Task orchestration automatization with Backlog tasks 
    * Sub-agents
