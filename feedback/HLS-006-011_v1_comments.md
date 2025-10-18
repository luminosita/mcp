# General Comments for All HLS Stories (006-011)

## CLAUDE.md Files

Artifacts needs to be corrected related to the nameing of MCP Server Resources, specifically related to hybrid `CLAUDE.md` files.

**Issue:**
Claude Code AI Agent uses `CLAUDE.md` naming for a default AI context priming. When we migrate all hybrid `CLAUDE.md` files as MCP Resources they will still be called `CLAUDE.md` (e.g., CLAUDE-core.md, CLAUDE-architecute.md, etc). This is ok for Claude Code AI Agent but it is too specific for general AI Agent usage. Other agents uses different naming.

**Solution:**
When we perform migration to MCP Resources the new names for the resources will be "Patterns" (e.g., patterns-core.md, patterns-architecture.md), and corresponding MCP URLs will be `mcp://resources/patterns/{artifact_name}` (e.g., mcp://resources/patterns/go/architecture, mcp://resources/patterns/python/core).
The only exception will be naming of SDLC instructions file, CLAUDE-sdlc.md. It will be called `sdlc-core.md` with the resource URL `mcp://resources/sdlc/core`

## Prompts

All prompts should be accessible via `mcp://prompts/generator/{artifact_name}` (e.g., mcp://prompts/generator/epic)

## Additional Backlog Story to HLS-008

Most of the artifacts always require generation of sub-artifacts. Initiative always requires Epics as child artifacts. Epics require High-level Stories. High-level Stories require Backlog stories. In some cases (documented in SDLC guideline document) Backlog stories does not require Implemetation tasks. Also, there is no requirement for Tech Specs, ADRs and Spikes all the time. It is on case-by-case basis. We want each generated artifact to be evaluated for sub-artifact requirement. Backlog Story generator has that instruction but it need to be reviewed. Other generators are lacking those instructions and need to be refined as part of this HLS.

We should add additional Backlog Story to HLS-008 (or where appropriate), which will add necessary instructions to all generators.

## Additional MCP Tool to HLS-008

After successful artifact generation and decomposition to sub-artifacts we should instruct Task Tracking service to add new tasks to the queue

MCP Server tool `add_task` should be created to add those tasks via REST API. Tool receives sub-artifacts metadata and creates new tasks approprietely. Supplied sub-artifact metadata is important since the requirement for `get_next_task` tool is to fetch next_task metadata for proper `resolve_artifact_path` arguments and prompt resources retrieval

## Evaluate if update to EPIC-006 and PRD-006 is required

These additional requirements may affect already generated EPIC-006 and PRD-006. We should evaluate if those artifacts should be updated with these additions.

---

# HSL-008

## Primary User Flow Section

**Issue:** Invalid happy path

**Solution:**

### **Happy Path (Path Resolution):**
1. Claude Code receives next_task for the Task tracking tool
2. Task contains metadata with required input artifacts for the generator (artifact ID, parent ID, referenced documents IDs) (e.g.,
```json
    {
        "id": "006",
        "parent":
        {
            "type": "epic",
            "id": "006",
            "version": "1"
        },
        "refs":
        [
            {
                "type": "business_research",
                "id": "AI_AI_Agent_MCP_Server",
                "version": "1"
            },
            ...
        ]
    }
```
)
1. Claude Code needs to locate EPIC-006 artifact for PRD generation
2. Claude Code calls MCP tool `resolve_artifact_path(type="epic", id="006", version="1")`
3. MCP Server searches filesystem using glob pattern
4. MCP Server finds exact match: `mcp://resources/artifacts/epic/006`
5. MCP Server returns JSON: `{path: "mcp://resources/artifacts/epic/006"}`
6. Claude Code reads artifact from resolved path
7. Claude Code executes PRD generator with EPIC-006 as input

---

**Issue:** Additional happy path

**Solution:**

### **Happy Path (Sub-artifact Generation):**
1. Claude Code generates PRD-006 artifact
2. MCP Server returns JSON `{requires_sub_artifacts: true, open_questions: true, required_artifacts_ids: US-010, US-011, US-012}` (flags requirement for sub-artifacts generation and the existance of open questions for human review)
3. Claude Code presents report to developer
4. Developer confirms sub-artifact requirement
5. Claude Code proceeds with generating new tasks via tool (`/add_task` with artifact metadata)

**Rationale:** see, Additional Backlog Story section above

---
Primary User Flow (Task Tracking)

# HSL-009

## Primary User Flow Section

We should add additional Happy Path to reflect adding of new tasks for sub-artifacts upon successful artifact generation and validation

---
