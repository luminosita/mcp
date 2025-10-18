## artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v1.md

### Two Separate Microservices

**Priority:** CRITICAL

**Issue:**

PRD-006 defines two separate microservices:

**FR-15** | Task tracking microservice ...
**FR-16** | ID management microservice ...

These are two are not two separate services, but one providing the same functionallity as listed in FRs

**Proposed Solution:**

Merge definition of these two microservices into one (Task Tracking) and aggregate functionallity of both microservices into single one

### General Misconception of Prompts

**Issue:**
Current prompts, located at `.claude/commands` folder should stay as a local instructions. The actual MCP Server prompts as Generators ({artifact}-generator.xml)

**Proposed Solution:**
Remove references to `generate` and `refine` prompts and rewrite documentation to treat generators as MCP prompts

### User Flow 1

**Priority:** CRITICAL

**Issue:**

Flow 1 lists some invalid steps

**Proposed Solution:**

Flow 1: New Project Setup Using MCP Framework
1. Developer creates new project repository
2. Developer adds MCP Server connection configuration (server URL, authentication)
   └─ Config file: `.mcp/config.json` with `{server_url: "http://localhost:3000", use_mcp_framework: true}`
3. Developer creates minimal local CLAUDE.md orchestrator (50 lines)
   └─ References MCP resources: "See mcp://resources/claude/sdlc for SDLC workflow instructions"
4. Developer runs first generator: `claude-code "/generate epic-generator"`
   └─ AI Agent calls MCP prompt `mcp://prompts/epic-generator`
   └─ AI Agent calls MCP Server tool `resolve_artifact_path` tool to locate input artifacts
   └─ AI Agent fetches input artifacts from MCP resources
   └─ AI Agent executes prompt with input artifacts and generates epic artifact
5. AI Agent calls `validate_artifact` tool with epic content + validation checklist
   └─ Tool returns validation results: 25/25 criteria passed
6. Developer confirms artifact looks correct
7. AI Agent calls `update_task_status` tool to mark task completed
8. AI Agent calls MCP Server tool `store_artifact` to upload new epic artifact

### Architecture Section

**Issues:**
- "Directs to MCP resources for SDLC workflow instructions"
    MCP resources are artifacts without instructions
- "Directs to MCP prompts for /generate and /refine commands"
    MCP prompts are generators not "generate" and "refine" commands. Those stay local
- "Generators (product-vision, epic, prd, hls, backlog-story, etc.)"
    These do not belong to "MCP Resources Layer", but "MCP Prompts Layer"
- "Integration with microservices (REST API calls):"
    There is only one microservice handling both concerns (task tracking, ID management)


### Dependencies Section

**Issue:**

```context
Go Components (task tracking microservice, ID management microservice):

CLAUDE-core.md (Go): To be created during implementation (reference Go best practices, similar philosophy to Python CLAUDE-core.md)
CLAUDE-tooling.md (Go): To be created (golangci-lint for linting, go test for testing, Taskfile integration, module management)
Note: Language-specific CLAUDE.md files located in prompts/CLAUDE/{language}/ subdirectories. Go-specific files will be created as part of this PRD's implementation, establishing framework's multi-language capability.
```

Statement is wrong: "Go-specific files will be created as ..."

Go-specific files are already created and ready for consumption as a architecture and implementation instructions provider

**Proposed Solution:**
Update document to reflect upon the fact that Go-specific files are ready and to load them if required for this PRD update

Decisions Made

Business Questions
[BUSINESS] Question 1: Pilot Project Expansion Timeline

D1: 30-day stability period

--

[BUSINESS] Question 2: Open Source Timing for Go Microservices

D2: Kept private

---

[TECHNICAL] Question 3: Database Hosting Model for Pilot Phase

D3: Containerized PostgreSQL

---

[TECHNICAL] Question 4: MCP Resource Granularity for Artifacts

D4: individual resources (mcp://resources/artifacts/epic/000)

---

[TECHNICAL] Question 5: Validation Checklist Versioning Strategy

D5: (C) Hybrid (default to latest, override with explicit version)
