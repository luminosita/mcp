# User Story: Artifact Metadata Resources

## Metadata
- **Story ID:** US-067
- **Title:** Implement MCP Resources for Artifact Metadata and Queryable Artifacts
- **Type:** Feature
- **Status:** Backlog
- **Priority:** High - Completes FR-03 and FR-21 feature set for production readiness
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-011
- **Functional Requirements Covered:** FR-03, FR-21
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Functional Requirements - FR-03, FR-21
- **Functional Requirements Coverage:**
  - **FR-03:** MCP Server SHALL expose shared artifacts (artifacts/**/*) as queryable MCP resources with filters by artifact type, status, and parent relationship
  - **FR-21:** MCP Server SHALL expose artifact metadata (ID, type, status, parent_id, created_at, updated_at) as queryable resources separate from full artifact content for efficient filtering and discovery

**Parent High-Level Story:** [HLS-011: Production Readiness and Pilot]
- **Link:** `/artifacts/hls/HLS-011_production_readiness_pilot_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 5: Artifact Metadata Resources (FR-03, FR-21)

## User Story
As an **AI Agent** (Claude Code orchestrating SDLC workflows), I want **fast artifact metadata queries without loading full content** so that **I can efficiently discover relevant artifacts for context loading and dependency resolution**.

## Description

The MCP framework currently provides SDLC pattern files, generators, and templates as resources (HLS-006, HLS-007), but shared artifacts (epics, PRDs, stories) are not yet exposed as MCP resources. This creates inefficiency:

**Current State (Without FR-03/FR-21):**
- AI agent must use local file system access (Read tool) to browse artifacts
- No filtering capability - must read full artifact to check status, parent, type
- Expensive context consumption - loading 50KB PRD just to check if Status = "Approved"

**Desired State (With FR-03/FR-21):**
- AI agent queries `mcp://resources/artifacts/metadata?type=prd&status=Approved&parent=EPIC-006` and receives lightweight metadata list (no full content)
- Metadata includes: `{id: "PRD-006", type: "prd", title: "...", status: "Approved", parent_id: "EPIC-006", created_at: "2025-10-17", file_path: "artifacts/prds/PRD-006_..._v3.md"}`
- Metadata loading ≥10× faster than full artifact loading (validation per FR-21)
- AI agent selectively loads full artifact content only when needed

**Use Cases:**
1. **Dependency Resolution:** Find approved parent artifacts (e.g., "Load Epic that is parent of PRD-006")
2. **Artifact Discovery:** List all backlog stories for HLS-006 (e.g., "Find US-028 through US-034")
3. **Status Filtering:** Query only approved artifacts for production workflows
4. **Hierarchy Navigation:** Find all children of EPIC-006 (PRDs, HLS stories)

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§2.2: FastAPI Resource Endpoints** - Implement GET /resources/artifacts/metadata with query parameter filtering
  - **Example Code:** §2.2 shows FastAPI route definition with Pydantic query models
- **§2.3: PostgreSQL Metadata Queries** - Optional: Store artifact metadata in database for fast queries (alternative to file system scanning)
  - **Performance Target:** Metadata query <50ms vs. 500ms+ for full artifact file read
- **§2.4: Redis Cache for Metadata** - Cache metadata index to avoid repeated file system scanning (TTL: 5 minutes)

**Anti-Patterns Avoided:**
- **§8.2: Synchronous Blocking in Async Context** - Use aiofiles for async file system scanning, avoid blocking event loop

**Performance Considerations:**
- **File System Scanning Performance:** Scanning 100+ artifact files synchronously blocks event loop; use asyncio.gather() for parallel scanning
- **Metadata Extraction:** Parse artifact frontmatter (YAML or Markdown metadata section) without loading full content

## Functional Requirements
- MCP resource endpoint: `mcp://resources/artifacts/metadata` with query parameters:
  - `type`: Filter by artifact type (epic, prd, hls, us, spike, adr, spec, task)
  - `status`: Filter by status (Draft, In Review, Approved, Completed)
  - `parent`: Filter by parent artifact ID (e.g., `parent=EPIC-006` returns all PRDs/HLS children)
- MCP resource endpoint: `mcp://resources/artifacts/{type}/{id}` for full artifact content
  - Example: `mcp://resources/artifacts/epic/006` returns full EPIC-006 content
- Metadata schema (Pydantic model):
  ```python
  class ArtifactMetadata(BaseModel):
      id: str  # "EPIC-006"
      type: str  # "epic"
      title: str  # "MCP Server SDLC Framework Integration"
      status: str  # "Draft" | "Approved" | etc.
      parent_id: Optional[str]  # "INIT-001" or null
      created_at: datetime
      updated_at: datetime
      file_path: str  # "artifacts/epics/EPIC-006_..._v2.md"
      version: int  # 2
  ```
- Metadata loading ≥10× faster than full artifact loading (benchmark validation)
- Cache metadata index in Redis with 5-minute TTL for repeated queries

## Non-Functional Requirements
- **Performance:** Metadata query returns results within 50ms for 95th percentile (vs. 500ms+ full artifact load)
- **Scalability:** Support metadata queries across 100+ artifacts without performance degradation
- **Accuracy:** Metadata extraction from artifact frontmatter 100% accurate (no missing or incorrect fields)
- **Caching:** Metadata cache hit rate >70% for repeated queries (same as resource cache target)

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** Reference patterns-architecture.md and patterns-validation.md for implementation standards.

### Implementation Guidance

**Technology Stack:**
- **FastAPI** - REST API endpoints for metadata queries and full artifact loading
- **aiofiles** - Async file I/O for artifact file reading
- **frontmatter** - Python library for parsing YAML frontmatter in Markdown files
- **Redis** - Metadata cache for fast repeated queries

**Metadata Extraction Strategy:**
```python
# Extract metadata from artifact frontmatter
import frontmatter
import aiofiles

async def extract_metadata(file_path: str) -> ArtifactMetadata:
    async with aiofiles.open(file_path, 'r') as f:
        content = await f.read()

    # Parse frontmatter (YAML header)
    post = frontmatter.loads(content)
    metadata = post.metadata  # Dict with id, type, status, parent_id, etc.

    return ArtifactMetadata(
        id=metadata['story_id'],  # or epic_id, prd_id depending on type
        type=infer_type(file_path),  # Extract from file path
        title=metadata.get('title', ''),
        status=metadata.get('status', 'Draft'),
        parent_id=metadata.get('parent_prd') or metadata.get('parent_epic'),
        created_at=os.path.getctime(file_path),
        updated_at=os.path.getmtime(file_path),
        file_path=file_path,
        version=extract_version(file_path)  # Parse from filename v1/v2/v3
    )
```

**Query Filtering Implementation:**
```python
@app.get("/resources/artifacts/metadata")
async def get_artifact_metadata(
    type: Optional[str] = None,
    status: Optional[str] = None,
    parent: Optional[str] = None
) -> List[ArtifactMetadata]:
    # Load metadata from cache or scan file system
    all_metadata = await load_or_scan_metadata()

    # Apply filters
    filtered = all_metadata
    if type:
        filtered = [m for m in filtered if m.type == type]
    if status:
        filtered = [m for m in filtered if m.status == status]
    if parent:
        filtered = [m for m in filtered if m.parent_id == parent]

    return filtered
```

**References to Implementation Standards:**
- **patterns-architecture.md:** Follow established project structure for MCP resource endpoints (src/resources/artifacts.py)
- **patterns-validation.md:** Pydantic models for ArtifactMetadata with Field constraints, type validation
- **patterns-tooling.md:** Use Taskfile command (`task resources:index`) to rebuild metadata cache manually
- **patterns-testing.md:** Unit tests for metadata extraction from various artifact types, integration tests for query filtering

**Note:** Treat patterns-*.md content as authoritative - supplement with story-specific artifact metadata implementation.

### Technical Tasks

**Backend Tasks:**
1. Implement artifact metadata extraction from frontmatter (Markdown YAML header parsing)
2. Implement file system scanner for artifacts directory (async scanning with aiofiles)
3. Implement metadata caching in Redis with 5-minute TTL
4. Implement FastAPI endpoint: GET /resources/artifacts/metadata with query parameter filtering
5. Implement FastAPI endpoint: GET /resources/artifacts/{type}/{id} for full artifact content
6. Implement Pydantic model: ArtifactMetadata with validation
7. Implement metadata cache invalidation on artifact file modification (file watcher or manual refresh)

**Performance Optimization Tasks:**
1. Benchmark metadata query latency vs. full artifact loading (validate ≥10× speedup)
2. Implement parallel metadata extraction (asyncio.gather() for concurrent file parsing)
3. Optimize Redis cache key structure for efficient query filtering

**Testing Tasks:**
1. Unit tests for metadata extraction from epic, prd, hls, us artifact files (validate all fields accurate)
2. Unit tests for query filtering logic (type, status, parent filters)
3. Integration tests for MCP resource endpoints (call via MCP client, validate responses)
4. Performance benchmark test (measure metadata query latency, validate <50ms p95)

## Acceptance Criteria

### Scenario 1: Metadata Query with Type Filter
**Given** MCP Server with artifact metadata resource endpoint
**When** AI agent queries `mcp://resources/artifacts/metadata?type=prd`
**Then** Response includes metadata for all PRD artifacts (PRD-000, PRD-006)
**And** Each metadata object includes: id, type, title, status, parent_id, created_at, updated_at, file_path, version
**And** Response does NOT include full artifact content (efficient payload)
**And** Query completes within 50ms (p95 latency target)

### Scenario 2: Metadata Query with Status Filter
**Given** Artifacts with varying statuses (Draft, Approved, Completed)
**When** AI agent queries `mcp://resources/artifacts/metadata?status=Approved`
**Then** Response includes ONLY artifacts with Status = "Approved"
**And** Draft and In Review artifacts excluded from response
**And** Filtering accurate across all artifact types (epic, prd, hls, us)

### Scenario 3: Metadata Query with Parent Filter
**Given** EPIC-006 with child artifacts (PRD-006, HLS-006, HLS-007, etc.)
**When** AI agent queries `mcp://resources/artifacts/metadata?parent=EPIC-006`
**Then** Response includes metadata for PRD-006, HLS-006, HLS-007, HLS-008, HLS-009, HLS-010, HLS-011
**And** Artifacts with different parents excluded (e.g., EPIC-000 children not included)
**And** Query completes within 50ms

### Scenario 4: Combined Query Filters
**Given** Multiple artifacts matching various criteria
**When** AI agent queries `mcp://resources/artifacts/metadata?type=us&status=Backlog&parent=HLS-011`
**Then** Response includes ONLY US artifacts with Status="Backlog" AND parent_id="HLS-011" (US-063 through US-070)
**And** Artifacts failing any filter excluded
**And** Query combines filters with AND logic (not OR)

### Scenario 5: Full Artifact Content Retrieval
**Given** MCP Server with artifact content resource endpoint
**When** AI agent requests `mcp://resources/artifacts/epic/006`
**Then** Response includes full EPIC-006 markdown content
**And** Content loaded from file: `artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v2.md`
**And** Response time <100ms (cached or efficient file read)

### Scenario 6: Metadata Extraction Accuracy
**Given** PRD-006 v3 artifact with frontmatter metadata
**When** Metadata extractor parses file
**Then** Extracted metadata matches artifact header exactly:
  - id: "PRD-006"
  - type: "prd"
  - status: "Draft"
  - parent_id: "EPIC-006"
  - version: 3 (parsed from filename)
**And** created_at and updated_at timestamps match file system metadata

### Scenario 7: Metadata Loading Performance (≥10× Speedup)
**Given** Baseline: Full PRD-006 loading takes 500ms (50KB file)
**When** Metadata query executed for same artifact
**Then** Metadata loading completes within 50ms (≥10× faster)
**And** Metadata response payload <5KB (vs. 50KB full content)

### Scenario 8: Metadata Cache Efficiency
**Given** Metadata cache enabled with 5-minute TTL
**When** AI agent queries metadata twice within 5 minutes
**Then** First request (cache miss) scans file system and populates cache (50ms)
**And** Second request (cache hit) serves from Redis (<10ms latency)
**And** Cache hit rate >70% over 100 repeated queries

### Scenario 9: Metadata Cache Invalidation on File Modification
**Given** Metadata cache contains EPIC-006 with status="Draft"
**When** EPIC-006 file updated with status="Approved"
**Then** Cache invalidation triggered (manual or file watcher)
**And** Next metadata query returns updated status="Approved"
**And** Stale cache not served after file modification

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 5 SP (CONSIDER per decision matrix - moderate complexity but straightforward implementation)
- **Developer Count:** Single developer (backend engineer)
- **Domain Span:** Single domain (backend only - MCP resource endpoints, metadata extraction)
- **Complexity:** Medium - frontmatter parsing well-documented, FastAPI query parameters standard pattern
- **Uncertainty:** Low - clear implementation path, similar to existing resource endpoints (HLS-006, HLS-007)
- **Override Factors:** None - no cross-domain changes, no unfamiliar tech, low security criticality

**Justification for No Tasks:** While 5 SP suggests "CONSIDER" decomposition, the straightforward nature (extend existing MCP resource pattern), single developer execution, and lack of cross-domain complexity make task decomposition unnecessary overhead. Implementation can proceed as cohesive unit within single sprint.

## Definition of Done
- [ ] Metadata extraction implemented for all artifact types (epic, prd, hls, us, spike, adr, spec, task)
- [ ] FastAPI endpoint implemented: GET /resources/artifacts/metadata with query parameters (type, status, parent)
- [ ] FastAPI endpoint implemented: GET /resources/artifacts/{type}/{id} for full content
- [ ] Pydantic model ArtifactMetadata implemented with validation
- [ ] Redis caching implemented with 5-minute TTL
- [ ] Performance benchmark validates ≥10× speedup vs. full artifact loading
- [ ] Unit tests written and passing for metadata extraction (≥80% coverage)
- [ ] Integration tests validate MCP resource endpoints
- [ ] Cache hit rate measured (>70% for repeated queries)
- [ ] Documentation updated (MCP resource API reference, query parameter guide)
- [ ] Product Owner validates metadata query functionality

## Additional Information
**Suggested Labels:** backend, mcp-resources, metadata, feature-completion
**Estimated Story Points:** 5 SP
**Dependencies:**
- **Upstream:** US-030, US-031 (MCP resource server infrastructure must be deployed)
- **Blocked By:** None (all dependencies completed)
**Related PRD Section:** PRD-006 §Functional Requirements - FR-03, FR-21

## Open Questions & Implementation Uncertainties

**Question 1:** Should metadata be stored in PostgreSQL database or extracted from artifact files on-demand?
- **Marker:** [REQUIRES TECH LEAD]
- **Context:** Database provides fast queries but adds complexity and synchronization overhead (files → database); file-based extraction simpler but slower
- **Recommendation:** Use file-based extraction with Redis caching for pilot phase (simpler); migrate to database if metadata queries become performance bottleneck

**Question 2:** How should metadata cache handle artifact file deletions (artifact removed from file system)?
- **Marker:** [REQUIRES TECH LEAD]
- **Context:** Cached metadata may reference deleted artifacts; need strategy for cache consistency
- **Recommendation:** Implement file existence check when serving cached metadata; remove stale entries on cache miss; optional: periodic cache validation job

**Question 3:** Should artifact metadata include additional fields (e.g., author, tags, word count)?
- **Marker:** [REQUIRES TECH LEAD]
- **Context:** Additional fields provide richer filtering but require more metadata extraction logic
- **Recommendation:** Start with core fields (id, type, status, parent_id, timestamps) per FR-21; defer extended metadata to future enhancement based on pilot feedback

No open implementation questions requiring spikes or ADRs. All technical approaches clear from Implementation Research and PRD.

---

**Version History:**
- **v1 (2025-10-18):** Initial version generated from HLS-011 v2
