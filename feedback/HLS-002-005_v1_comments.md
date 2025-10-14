# Decisions Made

## HLS-002

### Open Questions

**High-Level Story Open Questions focus on USER/UX/FUNCTIONAL uncertainties needing validation before backlog refinement.**

**✅ INCLUDE - User/UX/Functional Questions:**

1. "Should build status notifications be sent to Slack/email in addition to GitHub UI, or is GitHub UI sufficient for developer awareness?"
D1: for MVP - NO, later stage - YES

2. "Do developers need ability to manually re-run failed builds without new commit, or is commit-triggered execution sufficient?"
D2: for MVP - NO, later - YES

3. "Should pre-commit hooks be optional (developer choice) or mandatory (enforced by repository), or should there be different levels (basic vs. comprehensive)?"
D3: Mandatory

4. "What visibility should developers have into build queue status when multiple developers commit simultaneously?"
D4: Build queue status should follow Git commit hash. Developer should receive the result of his/her commit only.

---

## HLS-003

### Open Questions

**High-Level Story Open Questions focus on USER/UX/FUNCTIONAL uncertainties needing validation before backlog refinement.**

**✅ INCLUDE - User/UX/Functional Questions:**

1. "Should example tool demonstrate external service integration (e.g., HTTP API call), or focus purely on MCP protocol patterns without external dependencies?"

D1: MPC protocol patterns

2. "Should application skeleton include multiple example tools demonstrating different patterns (simple vs. complex, synchronous vs. asynchronous), or single comprehensive example sufficient?"

D2: Single comprehensive

3. "Should example tool business logic be realistic (e.g., 'format code snippet') or abstract/dummy (e.g., 'echo input')?"

D3: Simple "Hello world"

4. "What level of documentation should be in code (docstrings/comments) vs. separate architecture documentation?"

D4: Follow "documentation-driven development" - start with comprehensive inline docs, extract to architecture docs during Story 5


---

## HLS-004

### Open Questions

**High-Level Story Open Questions focus on USER/UX/FUNCTIONAL uncertainties needing validation before backlog refinement.**

**✅ INCLUDE - User/UX/Functional Questions:**

1. "Should documentation include video tutorials in addition to text and diagrams, or is text + diagrams sufficient for MVP?"

D1: text + diagram

2. "Should code review checklist be integrated into PR template (GitHub), kept as separate documentation, or both?"

D2: brief checklist in PR template, detailed reference in documentation

3. "What level of troubleshooting documentation is sufficient - common issues only, or comprehensive failure mode catalog?"

D3: Start with common issues based on beta testing, expand based on actual support questions during first sprints

4. "Should documentation reference external resources (Python best practices, FastAPI docs, MCP protocol spec), or duplicate relevant information inline?"

D4: Hybrid approach - reference external for general knowledge (Python, FastAPI), inline for project-specific applications. Include "Further Reading" sections with curated external links.

---

## HLS-005

### Open Questions

**High-Level Story Open Questions focus on USER/UX/FUNCTIONAL uncertainties needing validation before backlog refinement.**

**✅ INCLUDE - User/UX/Functional Questions:**

1. "Should hot-reload be enabled by default in local development, or should developers opt-in via flag?"
D1: Default to enabled for MVP (optimizes for convenience), document how to disable if issues encountered

2. "Should database container data persist between restarts, or reset to clean state each time?"
D2: Implement persistence by default (maintains data), provide `task db:reset` command for clean state when needed

3. "Should container build include development dependencies, or production-only?"
D3: Production-only in container image (optimizes size per best practices), use Devbox for development workflows (already includes dev dependencies)

4. "What container registry authentication approach for developers pushing images - shared credentials, individual accounts, or automated via CI/CD only?" [REQUIRES PRODUCT OWNER]

D4: Automated via CI/CD for production, individual for staging testing
