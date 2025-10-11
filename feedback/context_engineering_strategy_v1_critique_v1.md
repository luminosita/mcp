# Critique

## Questions:

### Q1: Duplication of instructions
- Q1a: Why both documents, Product Vision generator prompt and Product Vision template, contain identical validation checklist? 
- Q1b: What is the reason for duplication?

### Q2 Research 

We are instructing LLM to "Research or infer 2-3 existing solutions in this space". 

- Q2a: Should we instruct LLM to research and suggest additional product capabilities for the review or just rely on the product idea document input for capabilities? 
- Q2b: Do we want to do that part within epic generator prompt? If yes, I do not see any research instructions as part of `<step priority="12">` nor in `<next-generator>` section.
- Q2c: Product vision creation is an iterative research-based process. How can we achieve this if we do not instruct LLM to do a research on important areas. Please disregard this part, if it is implied that LLMs will do a research by default if they miss information, regardless of our instructions. Do we need to specify `deep reasearch` or `deep thinking` instructions in that case.


### Q3 Background and Constraints

- Q3a: Why do we keep a reference to Context Engineering research document? Would it be smarter just to extract important pieces of Section 6.1 and embed it into the prompt. It would reduce context space if we load the entire research document just to collect minor facts. Maybe, I understand the "Reference" in the wrong way. Maybe it is just for documentation reason and that the prompt will not load it at all. If that is the case, ignore my comments on this subject
- Q3b: There are four constraints listed in `task_context/constraints` section. These are pretty strict constraints. If this is a generic Product Vision Generator following the input from a general product idea document then these constraints are wrong. Please describe the rationale behind this section

### Q4 Epic Generator

- Q4a: `<step priority="12">` instructs LLM model to "Follow generator prompt XML schema (see Section 5.1 of strategy document)". It refers to "strategy document" for XML Schema. Strategy document is not an input for this generator prompt. Should we extract templates from strategy document and refer to them when we instruct LLM to generate promtps?
 
### Q5 Main CLAUDE.md

- Q5a: In Step 3 of main CLAUDE.md, why do we use `/kickoff xecute-generator ...` instead of `/generate ...`
- Q5b: In Step 4, point 2, "If missing: Prompt human for confirmation > Generate from template". What template?
- Q5c: In Step 6, "Update this file's Current Phase section". I think it is better to keep all updates and tracking within TODO.md file as a main tracking file. We should have instruction in main CLAUDE.md to check Current Phase section for the progress when we start new session.
- Q5d: In Step 7, "/refine {task}_generator". We should use `/refine {task}_generator`
- Q5e: In `Key Research References", we keep references to strategy document and main research document. We should extract important information from those documents instead of keeping them as a constant reference and forcing AI agent to load them into context.

### Q6 6.3 Phase 3: Iteration & Refinement (strategy document)

- Q6a: Where is the statement "Updates `/docs/context_engineering_strategy_v1.md` (lessons learned)" reflected as an instruction to AI agent? How does agent knows to apply these updates?

### Q7: generate prompt

- Q7a: in Step 2, "- Determine specialized context file: `/prompts/CLAUDE-{phase}.md`". Where `phase` attribute/parameter comes from? I do not see `phase` listed in task metadata in `TODO.md`, if that is a source
- Q7b: in Step 2, "**If approved**: Generate from template (see Section 4.2 of strategy doc)". We keep the reference to strategy doc. Is it better to just extract the template and reference it directly instead of loading the entire file.
- Q7c: in Step 7, "Update CLAUDE.md", should be "Update TODO.md" instruction with appropriate details
- Q7d: in "**Related Commands**", there are some unknown/undefined commands (e.g. validate-artifact, update-phase). Do we have a task in TODO.md to create these commands or there is a different plan for this?
- Q7e: in "**See Also**", "- `/docs/context_engineering_strategy_v1.md` - Section 6.2", should we extract information instead of keep a reference to a big document.

## Remarks
* Phase 1-4 of the strategy is PoC for the core principles listed in the Section 1 of the strategy document. We are executing prompts, validating results, refining and progressing through the workflow. That being the primary goal it seems find to keep references to strategy document or the main research document in files like CLAUDE.md, generate prompt, refine promtp, templates and others. Once we complete PoC we need to clean up all these files from those references in order to use the strategy on various other products.
* Expected /.claude/commands/generate.xml (XML format), found Markdown file format
* Expected /.claude/commands/refine.xml (XML format), found Markdown file format
* Product-idea.md needs to be regenerated with a different idea outlined in @IDEA.md. Do not proceed with regeneration. Just specify a new task in `TODO.md`
* Add checkboxes in `TODO.md` for task status tracking
* Why do we use `/generate ...` or `/refine ...` instead of `/generate ...` or `refine ...`?
* Section 7.0 covers various metrics data. Where this data comes from?
* Sync strategy document with `TODO.md`, task numbers are out of sync and some tasks are already completed. Keep tracking history/status as part of `TODO.md` file for easier reference when we instruct agent to `run the next TODO task`
* Rename `TODO.md` → `PLAN.md`

## Change in the strategy
I revisited the phases listed in Section 1.4 of the strategy document. We need to insert new phase after the Phase 1 (PoC). That will be MCP Server phase. That phase will include:
- Cleanup of all prompts (.claude/commands/* and /prompts/*) and templates 
- Extraction of all prompts and templates and relocation of these files into a new MCP Server repository
- MCP Server will be Python/Pydantic based product serving our prompts and templates and making them available for any future project
- **Rationale**: current folder structure is great for the PoC product. If we want to use it for other products we need to copy/paste prompt and template files. This is a headache for maintenance. Much better approach is to isolate everything into a common repository (MCP Server repository) and make them reusable.
- This requires update of the main strategy document as well as Graduation related documents

**CRITICAL** Analyze my critiques, and perform clarification loop by asking questions until all statements are clarified. Propose updates to our plan with new tasks based on the critiques. Only proceed with updates upon confirmation.
 

