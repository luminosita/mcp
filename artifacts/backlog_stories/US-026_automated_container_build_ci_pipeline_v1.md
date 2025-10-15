# User Story: Automated Container Build in CI/CD Pipeline

## Metadata
- **Story ID:** US-026
- **Title:** Automated Container Build in CI/CD Pipeline
- **Type:** Feature
- **Status:** Draft
- **Priority:** High - Enables automated container deployment workflow
- **Parent PRD:** PRD-000
- **Parent High-Level Story:** HLS-005 (Containerized Deployment Enabling Production Readiness)
- **Functional Requirements Covered:** FR-13 (automated aspect)
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## User Story
As a software engineer merging code to main branch,
I want the CI/CD pipeline to automatically build and push production container images,
So that deployments use tested, versioned container images without manual build steps.

## Description
Extend the GitHub Actions CI/CD pipeline to automatically build production container images on successful merge to main branch. Images are tagged with version numbers and commit SHAs, then pushed to a container registry (GitHub Container Registry). This automation ensures every main branch commit produces a deployable artifact, enabling continuous deployment workflows.

This story extends US-020 (Containerfile) and US-003 (CI/CD Pipeline Infrastructure) by adding automated container build stage.

## Functional Requirements
- CI/CD pipeline builds container image on merge to main branch
- Image tagged with version (from pyproject.toml) and commit SHA
- Image pushed to GitHub Container Registry (ghcr.io)
- Build uses Containerfile from US-020
- Image build status visible on GitHub commit/PR
- Failed builds block deployment workflow
- Registry credentials managed via GitHub Secrets

## Non-Functional Requirements
- **Performance:** Container build completes within 5 minutes
- **Reliability:** Build succeeds >95% on clean main branch
- **Security:** Registry credentials never exposed in logs
- **Traceability:** Every main commit maps to unique image tag

## Technical Requirements

### Implementation Guidance

Add container build job to `.github/workflows/ci.yml`:

**Trigger:** Merge to `main` branch (after all validation jobs pass)

**Build Job:**
```yaml
build-container:
  runs-on: ubuntu-latest
  needs: [lint-and-format, type-check, test-and-coverage]
  if: github.ref == 'refs/heads/main'
  steps:
    - uses: actions/checkout@v4
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    - name: Login to GHCR
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    - name: Extract version
      id: version
      run: |
        VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
        echo "version=$VERSION" >> $GITHUB_OUTPUT
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        file: ./Containerfile
        push: true
        tags: |
          ghcr.io/${{ github.repository }}:latest
          ghcr.io/${{ github.repository }}:${{ steps.version.outputs.version }}
          ghcr.io/${{ github.repository }}:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

**Registry Configuration:**
- GitHub Container Registry (ghcr.io) - free for public repos
- Authentication: GitHub Actions GITHUB_TOKEN (automatic)
- Repository settings: Enable GHCR package creation

**Image Tagging Strategy:**
- `latest`: Always points to most recent main build
- `v0.1.0`: Semantic version from pyproject.toml
- `abc123def`: Git commit SHA for traceability

## Acceptance Criteria

### Scenario 1: Container builds on main merge
**Given** PR merged to main with all checks passing
**When** CI/CD pipeline executes
**Then** container image builds successfully
**And** image pushed to ghcr.io with version and SHA tags
**And** build completes within 5 minutes

### Scenario 2: Failed builds visible
**Given** main merge triggers container build
**When** Containerfile has errors
**Then** build job fails with clear error message
**And** failure visible on commit status

### Scenario 3: Image tagged correctly
**Given** container build successful
**When** checking registry
**Then** image tagged with latest, version, and commit SHA
**And** all three tags point to same image digest

## Implementation Tasks Evaluation

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 3 SP - Straightforward GitHub Actions workflow addition
- **Developer Count:** Single developer
- **Complexity:** Low - Standard Docker build action with well-documented patterns
- **Uncertainty:** Low - Using established GitHub Actions marketplace actions

## Definition of Done
- [ ] GitHub Actions workflow updated with container build job
- [ ] Build triggered only on main branch merges
- [ ] Image successfully pushed to ghcr.io with correct tags
- [ ] Build completes within 5 minutes
- [ ] Failed builds block deployment workflow
- [ ] No credentials exposed in build logs
- [ ] Documentation updated with registry information
- [ ] Manual test: Verify built image runs correctly
- [ ] Code reviewed and approved
- [ ] All acceptance criteria validated

## Additional Information
**Suggested Labels:** ci-cd, container, docker, automation, infrastructure
**Estimated Story Points:** 3 (Fibonacci scale)
**Dependencies:**
- US-020 (Containerfile) completed - Provides container build definition
- US-003 (CI/CD Pipeline) completed - Provides pipeline foundation
- US-024 (Database Migration) completed - Ensures migrations ready for container deployment

**Related Stories:**
- US-020: Production Containerfile (provides build definition)
- US-003: CI/CD Pipeline Infrastructure (provides pipeline foundation)
- US-025: Staging Validation (uses built images)

## Open Questions & Implementation Uncertainties

**No open questions.** GitHub Actions container build is well-established pattern with extensive documentation. Using GitHub Container Registry avoids external service setup.

---

**Document Version:** v1.0
**Generated By:** Manual creation (quick story)
**Generation Date:** 2025-10-15
**Parent:** HLS-005 Containerized Deployment Enabling Production Readiness
**Story Sequence:** 7 of 7 in HLS-005 decomposition
