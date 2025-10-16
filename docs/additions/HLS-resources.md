# Overview for EPIC-006

We completed EPIC-000 and as a result we have a project foundation with complete bootstrap. We have a fully functional MCP Server implemented using industry best practices with an example tool implementation as a PoC. In order to achieve this we heavily relied on AI Agent to locate local files (artifacts, generators, templates, etc), load them into AI context and generate response based on the input.

EPIC-001 addresses the need to integrated Project Management solution to track artifacts and relationships between. There should be one step in between EPIC-000 and EPIC-001, which defines usage of our newly implemented MCP Server to demonstrate abilities to server prompts, resources and tools. EPIC-006 should address this step. EPIC-006 should have INIT-001 as a parent Initiative.

## MCP Server Prompts

Claude commands are effectively prompts corresponding to MCP Server prompts, located at @.claude/commands/*.md

## MCP Server Resources

### Hybrid `CLAUDE.md` files

**Step 1:** Refactoring of main CLAUDE.md

**Issue:**
Main `CLAUDE.md` is the very main orchestrator, mainly containing SDLC workflow instructions, and partly directing implementation instructions to be gathered from `prompts/CLAUDE/CLAUDE-core.md`, which in turn directs various implementation concerns toward other `prompts/CLAUDE/CLAUDE-*.md` files.

**Proposed Solution:**
Splitting of main `CLAUDE.md` into two parts:
- Part 1: pure SDLC workflow related instructions
- Part 2: implementation orchestration pointing to `prompts/CLAUDE/CLAUDE-core.md`

Output of Part 1 would be new `prompts/CLAUDE/CLAUDE-sdlc.md` file.
Output of Part 2 would remain in main `CLAUDE.md` and it will be extended to add new orchestration instructions pointing to the newly created `prompts/CLAUDE/CLAUDE-sdlc.md` file for SDLC workflow related concerns.

**Rationale:**
By doing the split of the current main `CLAUDE.md`, we are clearly separated two sets of `CLAUDE.md` files:
- pure orchestrator (new main `CLAUDE.md`)
- SDLC planning + Implementation instructions (`prompts/CLAUDE/CLAUDE-*.md`)

**Step 2:**

Move `prompts/CLAUDE/CLAUDE-*.md` files as part of MCP Server Resources and keep main `CLAUDE.md` as an orchestrator pointing to hybrid `CLAUDE.md` files, but not as local files, rather as MCP Server Resources.

**Rationale:**
This gives us a great flexibility in reusing hybrid `CLAUDE.md` approach for future Python projects, since current `CLAUDE.md` files as Python specific. We can easily split MCP Server Resource to include similar Go Lang oriented `CLAUDE.md` files. All these hybrid `CLAUDE.md` files can be loaded into AI context on demand during future planning phases, for research and for implementation. Big advantage will be maintenance. All files will be centralized as part of one MCP Server repository and not copied between various future project git repos.

### Artifacts (`artifacts/**/*`)

Same rationale as we hybrid `CLAUDE.md` files, we can move all artifacts into MCP Server repository and use them as MCP Resources.

### Generators and Templates (@prompts/*, @prompts/templates/*)

Same rationale as we hybrid `CLAUDE.md` files, we can move all generators and templates into MCP Server repository and use them as MCP Resources.

## MCP Server Tools

Our main `CLAUDE.md` and all generator validation checklists with corresponding instructions are performing inference, which are better placed and organized as Python scripts.

Candidates for migration from instructions to Python scripts:
- Validation instructions (e.g. generator input classification rules, artifacts ID assignment, statuses, tracibility concerns)
- Artifact paths resolution

**Requirement:**
Deep analysis of all `CLAUDE.md` files, generators and templates and evaluation of potential refactoring of all instructions into deterministic Python scripts. First part would be to determine all insturctions able to be scripted per each `CLAUDE.md` file, generator and template. Finally, a synthesis of gather information into a fewer reusable tools.

**Rationale:**
Huge gain in precision by using deterministic Python scripts vs non-deterministic AI inference. Each script can become a part a MCP Server Tool significantly reducing relience on AI inference

## Main `CLAUDE.md` as Main Orchestrator For MCP Server Tools, Prompts and Resources

New main `CLAUDE.md` file becomes a main orchestrator, having the instructions on how to utilise newly created tools, prompts and resources without loosing any functionallity of the existing system.

## TODO.md

**Issue:**
Our `TODO.md` is the central tracking file for generation and implementation tasks. It relies on Claude commands (prompts) and `CLAUDE*.md` instructions to properly infer artifact IDs, names and paths, to validate the outcome of each workflow step. Even though `TOOD.md` is great for task tracking, it has a bad side-effect that it grows in size with each task. It requires constant update by AI agent to keep task statuses in sync and to give us a clear picture of what is done and what is next in line. Every interaction with `TODO.md` file burns unnecessary AI tokens to analyse it, which each step.

**Proposed Solution:**
Create new task tracking tool, which defines proper template required by prompts to identified all required input artifacts and context for each task. Instead of keeping tasks in the same repository as project being developed, we can store tasks into a database and fetch them with the simple request (Get Next Task). This gives us huge simplification.

## Artifact IDs

**Issue:**
We are currently keeping all artifact IDs as part of main `CLAUDE.md` file with constant updates to the file to avoid ID overlap

**Proposed Solution:**
Track artifact IDs in the database and provide MCP Server Tool for retrieval. It should cover two scenarios:
1. Retrieve next available artifact ID
Example: this new Epic (EPIC-006) is not defined as part of an Initiative. We are treating it as an adhoc Epic attached to existing Initiative thru tracibiliy metadata and other related sections. We only need proper tracibility information for Parent artifacts and referenced documents, but there is no requirement for chaining this Epic with other Epics in the same Initiative.
2. Retrieve next set of artifact IDs
Example: one Initiative generates several Epics, mutually connected. In order for Epic Generator to specify dependencies for an Epic, being generated, it needs to be aware of corresponding IDs for all Epics belonging to the same Initiative.

## Big Picture

EPIC-006 becomes a critical step towards future Project Management integration. Sets a new standard approach on full SDLC planning and implementation. With this Epic we are improving our MCP Server product from simple example tool container to a more advanced MCP Server implementation and at the same time we are improving and advancing our SDLC strategy from local files based towards utilization of MCP Server capabilities. Additional benefit is the constant testing and improvements of our MCP Server through the actual usage.
