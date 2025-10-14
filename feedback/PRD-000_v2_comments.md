## Additional Tool
### Issue
Shell CLI tools for various development tasks are scattered(e.g., for linting and testing - `ruff check .`, `mypy src/ --strict`, `uv run pytest -v`, for running code - `uv run python script.py`)

### Proposed Solution
Consolidate all CLI tool executions into Taskfile and central place for all tool capabilities. Consolidate all `CLAUDE.md` instructions to exclusively use Taskfile tasks for the operations

**Rationale**: 
Current MCP project uses Python as a main programming language and Python-orientied specialized `CLAUDE.md` files. Future projects will have different architectures and programming languages. Common thing among all these architectures is hybrid approach with specialized `CLAUDE.md` files. Each architecture has it's own tooling and we need to establish a common fasade for all architectures. Taskfile gives as that capability to unify tooling under the common fasade

### Affected artifacts
- CLAUDE-tooling.md (requires update with Taskfile instructions)
- PRD-000, HLS-001, US-001 (add new tool requirement)

---

## Specialized CLAUDE.md files
### Issue
In the first round of PRD refinement (@feedback/PRD-000_v1_comments.md) we introduced establish standard defined in "Hybrid CLAUDE.md approach". We refined PRD successfully, but forget to refine PRD generator and template for future PRDs

### Proposed Solution
Update PRD generator and template accordingly. Evaluate if update is required for HLS and Backlog generators and templates
