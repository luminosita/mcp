# User Story: Comprehensive Framework Documentation

## Metadata
- **Story ID:** US-068
- **Title:** Create Migration Guide, API Reference, and Deployment Documentation
- **Type:** Feature
- **Status:** Backlog
- **Priority:** High - Blocks pilot expansion; framework adoption requires complete documentation
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-011
- **Functional Requirements Covered:** NFR-Maintainability-03 (API documentation)
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Timeline & Milestones - Phase 5: Documentation; §NFR-Maintainability-03 (API documentation in OpenAPI format)
- **Functional Requirements Coverage:**
  - **NFR-Maintainability-03:** MCP Server SHALL expose API documentation (OpenAPI/Swagger) auto-generated from code annotations

**Parent High-Level Story:** [HLS-011: Production Readiness and Pilot]
- **Link:** `/artifacts/hls/HLS-011_production_readiness_pilot_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 6: Documentation (Migration Guide, API Reference, Deployment)

## User Story
As an **Enterprise Development Team Lead**, I want **comprehensive documentation covering framework migration, API usage, and deployment procedures** so that **my team can adopt MCP framework independently without constant maintainer support**.

## Description

The MCP framework requires user-facing documentation for successful adoption beyond the initial AI Agent MCP Server pilot. This story delivers three critical documentation artifacts:

**1. Migration Guide** (for teams migrating from local file approach)
- **Audience:** Development teams currently using local CLAUDE.md files, generators, TODO.md task tracking
- **Content:**
  - Step-by-step migration procedure (local files → MCP framework)
  - Configuration changes required (.mcp/config.json setup)
  - Backward compatibility mode usage during transition
  - Token consumption comparison (before/after migration)
  - Rollback procedure if migration issues discovered
- **Format:** Markdown tutorial with code examples, expected outputs, troubleshooting section
- **Estimated Length:** 2000-3000 words

**2. API Reference** (for MCP Server resources, prompts, tools)
- **Audience:** AI agents (Claude Code), developers integrating with MCP Server programmatically
- **Content:**
  - MCP Resources catalog (sdlc-core.md, patterns-*.md, templates, artifact metadata)
  - MCP Prompts catalog (all 10 generator prompts with input parameters)
  - MCP Tools catalog (validate_artifact, resolve_artifact_path, store_artifact, task tracking tools, ID management tools)
  - Request/response schemas (Pydantic models in JSON Schema format)
  - Error codes and troubleshooting (authentication errors, validation failures, rate limits)
- **Format:** OpenAPI 3.0 specification (auto-generated from FastAPI code annotations) + human-readable reference docs
- **Estimated Length:** Auto-generated (OpenAPI spec ~500 lines YAML)

**3. Deployment Guide** (for infrastructure teams deploying MCP Server)
- **Audience:** DevOps engineers, infrastructure teams, tech leads deploying MCP framework
- **Content:**
  - System requirements (Python 3.11+, PostgreSQL 15+, Redis 7+, Docker/Podman)
  - Docker Compose deployment procedure (staging and production configurations)
  - Kubernetes deployment procedure (optional for enterprise scale)
  - Environment variable configuration (DATABASE_URL, REDIS_URL, JWT_PUBLIC_KEY, etc.)
  - TLS certificate setup for HTTPS access
  - Backup and disaster recovery procedures
  - Monitoring and observability setup (Prometheus, Grafana)
  - Common deployment issues and resolutions
- **Format:** Markdown operational runbook with command-line examples, configuration templates
- **Estimated Length:** 3000-4000 words

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§2.2: FastAPI Automatic Documentation** - FastAPI generates OpenAPI spec and interactive Swagger UI from code annotations (docs_url="/docs", redoc_url="/redoc")
  - **Example Code:** §2.2 shows FastAPI app configuration with auto-generated documentation
- **§9.1: Kubernetes Deployment** - Deployment guide references Production deployment manifest from Implementation Research
  - **Example Code:** §9.1 provides deployment.yaml template
- **§9.2: CI/CD Pipeline** - Deployment guide includes GitHub Actions workflow example
  - **Example Code:** §9.2 shows automated deployment pipeline

**Anti-Patterns Avoided:**
- **Documentation Drift:** Auto-generate API reference from code (not manually written) to prevent documentation/code divergence

**Performance Considerations:**
- N/A (documentation story)

## Functional Requirements
- **Migration Guide** (docs/migration_guide.md)
  - Step-by-step migration from local file approach to MCP framework
  - Configuration examples for .mcp/config.json
  - Backward compatibility mode instructions
  - Token consumption comparison methodology
  - Rollback procedure
  - Troubleshooting section (common migration issues)
- **API Reference** (auto-generated OpenAPI spec + docs/api_reference.md)
  - OpenAPI 3.0 specification at /openapi.json endpoint
  - Swagger UI at /docs endpoint for interactive API exploration
  - ReDoc UI at /redoc endpoint for pretty documentation
  - Human-readable API reference (Markdown) covering:
    - MCP Resources catalog (all resource URIs, query parameters, response schemas)
    - MCP Prompts catalog (all generator prompts with parameters)
    - MCP Tools catalog (all tools with input/output schemas, error codes)
- **Deployment Guide** (docs/deployment_guide.md)
  - System requirements table
  - Docker Compose deployment procedure (step-by-step commands)
  - Kubernetes deployment procedure (optional)
  - Environment variable reference table
  - TLS certificate setup instructions
  - Backup and disaster recovery procedures
  - Monitoring setup (Prometheus + Grafana integration)
  - Troubleshooting section (common deployment issues)

## Non-Functional Requirements
- **Completeness:** Documentation covers 100% of user-facing features (migration, API usage, deployment)
- **Accuracy:** Code examples tested and verified (no outdated or incorrect examples)
- **Accessibility:** Documentation written for technical audience (developers, DevOps) with clear terminology, no jargon
- **Maintainability:** API reference auto-generated from code (prevents drift)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** Reference patterns-architecture.md for documentation structure.

### Implementation Guidance

**Documentation Tools:**
- **FastAPI OpenAPI Generation** - Auto-generate API spec from Pydantic models and route annotations
- **Markdown** - Human-readable documentation format (migration guide, deployment guide)
- **Swagger UI / ReDoc** - Interactive API exploration (embedded in FastAPI)

**OpenAPI Auto-Generation Example:**
```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="AI Agent MCP Server",
    version="1.0.0",
    description="MCP Server for SDLC framework orchestration",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc UI
    openapi_url="/openapi.json"  # OpenAPI spec
)

class ValidateArtifactInput(BaseModel):
    """Input schema for validate_artifact tool"""
    artifact_content: str = Field(..., description="Full artifact markdown content")
    checklist_id: str = Field(..., description="Validation checklist ID (e.g., 'prd_checklist_v1')")

class ValidateArtifactOutput(BaseModel):
    """Output schema for validate_artifact tool"""
    passed: bool = Field(..., description="Overall validation pass/fail status")
    results: list[dict] = Field(..., description="Per-criterion validation results")

@app.post("/tools/validate_artifact", response_model=ValidateArtifactOutput)
async def validate_artifact(input: ValidateArtifactInput):
    """
    Validates artifact against validation checklist.

    **Use Cases:**
    - Validate PRD against 26-criterion checklist
    - Validate Epic against 25-criterion checklist
    - Validate Backlog Story against checklist

    **Returns:**
    - Validation results with passed/failed criteria
    - Detailed failure reasons for debugging
    """
    # Implementation
    pass

# OpenAPI spec auto-generated at /openapi.json
# Swagger UI available at /docs
```

**References to Implementation Standards:**
- **patterns-architecture.md:** Follow established documentation structure (docs/ directory, separation of user-facing vs. developer docs)
- **patterns-tooling.md:** Document Taskfile commands for common operations (`task server:start`, `task benchmark`, `task security-scan`)

**Note:** Treat patterns-*.md content as authoritative - supplement with story-specific MCP framework documentation.

### Technical Tasks

**Migration Guide Tasks:**
1. Write introduction and migration overview (target audience, expected duration)
2. Document prerequisite steps (MCP Server deployment, authentication setup)
3. Write step-by-step migration procedure (local files → MCP framework)
4. Document .mcp/config.json configuration format with examples
5. Explain backward compatibility mode (how to enable, when to disable)
6. Document token consumption measurement procedure (baseline vs. MCP approach)
7. Write rollback procedure (MCP framework → local files)
8. Create troubleshooting section (common migration issues and resolutions)

**API Reference Tasks:**
1. Ensure all FastAPI routes have docstrings and Pydantic models annotated with Field descriptions
2. Configure FastAPI OpenAPI metadata (title, version, description)
3. Enable Swagger UI and ReDoc endpoints (/docs, /redoc, /openapi.json)
4. Write human-readable API reference supplement (Markdown) covering:
   - MCP Resources catalog (table with resource URIs, descriptions, query parameters)
   - MCP Prompts catalog (table with prompt names, input parameters, use cases)
   - MCP Tools catalog (table with tool names, input/output schemas, error codes)
5. Document authentication requirements (JWT format, API key usage)
6. Document error response format (error codes, messages, troubleshooting steps)

**Deployment Guide Tasks:**
1. Write system requirements section (Python, PostgreSQL, Redis, Docker versions)
2. Document Docker Compose deployment (step-by-step commands with expected outputs)
3. Document Kubernetes deployment (optional - deployment.yaml manifest, kubectl commands)
4. Create environment variable reference table (all required/optional env vars with descriptions)
5. Document TLS certificate setup (Let's Encrypt, self-signed, or enterprise CA)
6. Write backup and disaster recovery procedures (database backups, restore steps)
7. Document monitoring setup (Prometheus scrape config, Grafana dashboard import)
8. Create troubleshooting section (common deployment issues: connection errors, permission issues, resource exhaustion)

**Testing and Validation Tasks:**
1. Test all code examples in documentation (execute commands, verify outputs)
2. Review documentation for accuracy (compare with actual implementation)
3. Peer review by developer unfamiliar with MCP framework (validate clarity)

## Acceptance Criteria

### Scenario 1: Migration Guide Completeness
**Given** Migration guide documentation at docs/migration_guide.md
**When** Developer reads guide to migrate from local file approach
**Then** Guide includes all required sections:
  - Introduction and overview
  - Prerequisites
  - Step-by-step migration procedure (≥5 steps with code examples)
  - Configuration examples (.mcp/config.json)
  - Backward compatibility mode instructions
  - Token consumption comparison procedure
  - Rollback procedure
  - Troubleshooting section (≥3 common issues)
**And** Code examples tested and verified (no errors when executed)

### Scenario 2: API Reference Auto-Generation (OpenAPI)
**Given** FastAPI application with all routes, Pydantic models annotated
**When** User navigates to /openapi.json endpoint
**Then** OpenAPI 3.0 specification returned in JSON format
**And** Specification includes:
  - All MCP tool endpoints (/tools/validate_artifact, /tools/resolve_artifact_path, etc.)
  - All MCP resource endpoints (/resources/artifacts/metadata, /resources/patterns/*)
  - Request/response schemas for all endpoints (Pydantic models serialized to JSON Schema)
  - Authentication requirements (security scheme for JWT/API key)

### Scenario 3: Interactive API Documentation (Swagger UI)
**Given** FastAPI application with Swagger UI enabled
**When** User navigates to /docs endpoint
**Then** Swagger UI loads with interactive API explorer
**And** All endpoints listed with descriptions, parameters, request/response schemas
**And** User can execute test requests directly from Swagger UI ("Try it out" functionality)
**And** Authentication can be configured in Swagger UI (JWT token input)

### Scenario 4: Human-Readable API Reference Supplement
**Given** API reference documentation at docs/api_reference.md
**When** Developer reads reference to understand MCP resources, prompts, tools
**Then** Reference includes:
  - MCP Resources catalog table (≥15 resources listed with URIs and descriptions)
  - MCP Prompts catalog table (10 generator prompts listed with parameters)
  - MCP Tools catalog table (≥8 tools listed with input/output schemas)
  - Authentication section explaining JWT and API key usage
  - Error codes reference table (401, 422, 429, 500 with meanings and troubleshooting)

### Scenario 5: Deployment Guide Completeness
**Given** Deployment guide documentation at docs/deployment_guide.md
**When** Infrastructure engineer reads guide to deploy MCP Server
**Then** Guide includes all required sections:
  - System requirements table (Python, PostgreSQL, Redis, Docker versions)
  - Docker Compose deployment procedure (≥10 steps with commands)
  - Kubernetes deployment procedure (optional - deployment.yaml example)
  - Environment variable reference table (≥10 variables with descriptions)
  - TLS certificate setup instructions (Let's Encrypt example)
  - Backup and disaster recovery procedures (database backup commands)
  - Monitoring setup (Prometheus + Grafana integration)
  - Troubleshooting section (≥5 common deployment issues)

### Scenario 6: Code Example Accuracy
**Given** Migration guide with code example: `docker-compose up -d mcp-server`
**When** Developer executes command from documentation
**Then** Command succeeds without errors
**And** Expected output matches documentation description (MCP Server starts successfully)
**And** All code examples tested during documentation review (no outdated commands)

### Scenario 7: Documentation Peer Review
**Given** All three documentation artifacts (migration guide, API reference, deployment guide)
**When** Developer unfamiliar with MCP framework reviews documentation
**Then** Developer can complete migration procedure without additional help
**And** Developer can deploy MCP Server using deployment guide only
**And** Developer can invoke MCP tools using API reference only
**And** No critical gaps or ambiguities identified during review

### Scenario 8: Documentation Maintainability (API Reference)
**Given** FastAPI code updated with new tool endpoint `/tools/new_tool`
**When** FastAPI application restarted
**Then** OpenAPI spec at /openapi.json automatically includes new endpoint
**And** Swagger UI at /docs displays new endpoint (no manual documentation update required)
**And** API reference Markdown updated to reference new tool (one-time manual addition to catalog table)

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** Tasks Needed

**Rationale:**
- **Story Points:** 8 SP (DON'T SKIP per decision matrix - complexity requires decomposition)
- **Developer Count:** Multiple developers (technical writer for migration/deployment guides, backend engineer for API reference validation)
- **Domain Span:** Cross-domain (documentation + backend code annotation for OpenAPI generation)
- **Complexity:** High - three separate documentation artifacts with different formats and audiences
- **Uncertainty:** Low - clear documentation requirements, well-defined content sections
- **Override Factors:**
  - **Cross-domain changes:** Documentation (technical writing) + Backend (OpenAPI annotation validation)

**Proposed Implementation Tasks:**
- **TASK-025:** Write migration guide (introduction, prerequisites, step-by-step procedure, rollback, troubleshooting) (8-10 hours)
  - Deliverables: docs/migration_guide.md with tested code examples
- **TASK-026:** Configure FastAPI OpenAPI generation and validate annotations (4-6 hours)
  - Deliverables: OpenAPI spec at /openapi.json, Swagger UI at /docs, ReDoc at /redoc
- **TASK-027:** Write human-readable API reference supplement (resource/prompt/tool catalogs) (6-8 hours)
  - Deliverables: docs/api_reference.md with catalog tables
- **TASK-028:** Write deployment guide (system requirements, Docker Compose, Kubernetes, monitoring, troubleshooting) (8-10 hours)
  - Deliverables: docs/deployment_guide.md with tested commands
- **TASK-029:** Test all code examples and conduct peer review (4-6 hours)
  - Deliverables: Validation report, documentation corrections

**Note:** TASK IDs (TASK-025 through TASK-029) follow sequential allocation after TASK-024 (from US-065).

## Definition of Done
- [ ] Migration guide written and published at docs/migration_guide.md
- [ ] API reference auto-generated (OpenAPI spec at /openapi.json, Swagger UI at /docs, ReDoc at /redoc)
- [ ] Human-readable API reference supplement written at docs/api_reference.md
- [ ] Deployment guide written and published at docs/deployment_guide.md
- [ ] All code examples tested and verified (100% accuracy)
- [ ] Peer review completed by developer unfamiliar with MCP framework
- [ ] Documentation accessible via project repository (README.md links to all guides)
- [ ] Product Owner validates documentation completeness and clarity

## Additional Information
**Suggested Labels:** documentation, user-guides, api-reference, deployment
**Estimated Story Points:** 8 SP
**Dependencies:**
- **Upstream:** US-030 through US-058 (all MCP Server features implemented, ready for documentation)
- **Blocked By:** None (all dependencies completed)
**Related PRD Section:** PRD-006 §Timeline & Milestones - Phase 5 (Documentation)

## Open Questions & Implementation Uncertainties

**Question 1:** Should migration guide include video walkthrough or text-only documentation?
- **Marker:** [REQUIRES TECH LEAD]
- **Context:** Video provides visual guidance but adds production time and maintenance burden; text-only faster to create and update
- **Recommendation:** Text-only for initial version (pilot phase); video walkthrough deferred to future enhancement based on pilot feedback

**Question 2:** Should Kubernetes deployment guide be included in this story or deferred?
- **Marker:** [REQUIRES TECH LEAD]
- **Context:** Docker Compose sufficient for pilot; Kubernetes needed for enterprise scale but adds documentation complexity
- **Recommendation:** Include basic Kubernetes deployment section (deployment.yaml example) but mark as "optional"; full Kubernetes guide deferred to production deployment story

**Question 3:** What level of detail should troubleshooting sections include (common issues only or comprehensive)?
- **Marker:** [REQUIRES TECH LEAD]
- **Context:** Comprehensive troubleshooting adds documentation length; common issues only covers 80% of cases
- **Recommendation:** Start with ≥3-5 most common issues per guide; expand troubleshooting sections based on pilot project feedback

No open implementation questions requiring spikes or ADRs. All technical approaches clear from Implementation Research and PRD.

---

**Version History:**
- **v1 (2025-10-18):** Initial version generated from HLS-011 v2
