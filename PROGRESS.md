# Progress Steps

## CLAUDE.md
- [X] Move researches to artifacts/researches and update references
- [X] Rename product_vision_v1.md to proper naming format, move it to product_visions, and update references
- [X] File/folder structures for artifacts
- [X] Revise sub TODO.md (tracking)
    - [X] Verify the references of those TODO.md files
    - [X] Drop sub TODO.md files

## Validation
- [X] Move tracebility generator validation checks to a proper section
    - [X] Review generators for paths in tracebility sections
- [X] Generator output file paths
- [X] Read all generated epics
- [X] Read all restructured research docs (business and implementation)
- [X] Read all generators and templates (file paths removed, no validation duplications, defragmented validation instructions)
- [X] Check output file name for generators
- [X] Remove all paths from generators and templates. Keep it only in CLAUDE.md (input, output)
- [X] Evaluation related to required/optional input data for generators
- [X] Remove Tracibility Checklists from templates (validate existance in generators)
- [X] verify generate and refine prompts
    - [X] examples (Step 5, Step 6 -> Updated Sections)
- [X] create refinemenets plan for generated artifacts and apply
- [X] apply Issue 1, PRD gen only
- [X] apply Issue 2, PRD only
- [X] apply Issue 3, all
- [X] Validate that everything was applied
- [X] CLAUDE.md consolidation after generate and refine prompts refinement
    - [X] Phase 1 (Revised): Removed entire "Artifact Path Patterns" section (100% redundancy elimination)
    - [X] Phase 2: Simplified SDLC Artifact Dependency Flow (removed path redundancy)
    - [X] Phase 3: Merged File Naming Conventions into Folder Structure (single source of truth)
    - [X] Manual: Update 12 generator prompts to reference "Folder Structure" patterns
- [X] Open Questions in EPIC-000 too techy

## PRD Validation
- [ ] Technical Consideration sections were removed from Epics and saved into `artifacts/technical_considerations_from_epic.md`
    - [ ] Validate that these sections are generated in PRDs and compare the content
    - [ ] Open Questions (technical) from all epics -> PRDs

## Semi-automatic testing
- [ ] feedback/context_engineering_strategy_v1_critique_v3.md
- [ ] rewrite TASK_003 based on critique_v3 file before execution
- [ ] Review execute-generator
- [ ] verify Claude context is in the task report (execute-generator)
- [ ] Review refine

## Pre-finalization
- [ ] `docs/research/advanced_prompt_engineering/research_coverage_evaluation.md`
- [X] verify that all requests from CHAT.md are applied (or create AI report)
- [X] review all documents from the beginning
- [ ] analyze all `claude-md` documents
- [ ] review strategy document, if is still needed


## Finalization
- [X] remove CLAUDE-*.md lazy generation instructions, keep "if exists" verification
- [X] remove next-generator instructions, keep only reference to next-generator to be invoked in the report
- [ ] Validation checks migration to a validation tool 
- [ ] strategy doc update
- [ ] GRADUATION.md review
- [ ] IMPORTANT: compare with dot-ai, prp, portal projects from sandbox

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
