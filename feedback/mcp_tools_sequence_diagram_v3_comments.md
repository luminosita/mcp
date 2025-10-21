## MCP Tools Sequence Diagram - Comments

### MCP Resource URI

**Issue:**

In several places there is a mentioning of MCP Resource URI and given example is invalid.

Examples:
Line 198:
```
Manager->>Manager: Generate MCP resource URI<br/>("file:///workspace/artifacts/epic/EPIC-006_v1.md")
```

Line 437:
```
mcp_resource_uri: str         # "file:///workspace/artifacts/prds/PRD-006_v3.md"
```

Line 912:
```
inputs_json JSONB NOT NULL,                -- [{name: "prd", artifact_id: "PRD-006", resource_uri: "file://...", ...}, ...]
```

MCP Resource Path MUST be mcp://resources/artifacts/..., or mcp://resources/sdlc/..., or mcp://resources/patterns/...

**Solution:**
Correct examples to use proper MCP Resource Paths

**Rationale:**

MCP Resource Path is required as part of response to inform AI Agent of MCP paths for store artifacts, or the most importantly, next_task. Fetched task must contain proper MCP Resource paths since it uses those URIs to retrieve input artifacts for generator prompts. That way it loads all resources into context and generation will be sucessful
