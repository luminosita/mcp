# CI/CD Staging Deployment Strategy

## Overview

This document describes the staging deployment strategy for the AI Agent MCP Server, including CI/CD workflow triggers, container image tagging, and deployment patterns.

## Workflow Structure

The project uses **two separate CI/CD workflows** for different purposes:

### 1. CI Workflow (`.github/workflows/ci.yml`)

**Purpose:** Code quality validation and production builds

**Triggers:**
- Feature branches (`feature/**`, `bugfix/**`, `chore/**`)
- Pull requests to `main`
- Release branches (`release/**`)

**Actions:**
- Lint and format validation
- Type checking
- Unit and integration tests
- Container build (all branches)
- Container push (only on `release/**` branches)
- Security scanning

**Image Tags (Production):**
```
ghcr.io/OWNER/REPO:latest
ghcr.io/OWNER/REPO:0.1.0          (version from pyproject.toml)
ghcr.io/OWNER/REPO:abc123def       (commit SHA)
```

### 2. Staging Deployment Workflow (`.github/workflows/deploy-staging.yml`)

**Purpose:** Deploy and validate staging environment

**Triggers (choose one or combine):**

#### Option A: Automatic Deployment on `develop` Branch (Recommended)
```yaml
on:
  push:
    branches:
      - develop
```

**Workflow:**
```
Feature branch → PR to develop → Merge → Auto-deploy to staging → Smoke tests
                                                                  ↓
                                                            If validated
                                                                  ↓
                                           PR develop → main → Production release
```

**Pros:**
- Continuous staging deployment (every merge triggers deployment)
- Fast feedback loop for developers
- Staging always reflects latest `develop` state

**Cons:**
- Requires `develop` branch in Git workflow
- More frequent deployments (may increase costs if using cloud infrastructure)

#### Option B: Manual Workflow Dispatch
```yaml
on:
  workflow_dispatch:
    inputs:
      ref:
        description: 'Git ref to deploy (branch, tag, or SHA)'
        default: 'develop'
```

**Workflow:**
```
Developer → GitHub Actions UI → Select "Deploy to Staging" workflow → Deploy
```

**Pros:**
- Full control over when staging deployments occur
- Can deploy any branch/tag/commit for testing
- Lower infrastructure costs (deploy only when needed)

**Cons:**
- Manual process (requires developer action)
- Staging may become stale if not deployed regularly

#### Option C: PR Label-Based Deployment
```yaml
on:
  pull_request:
    types:
      - labeled
    branches:
      - main
```

**Workflow:**
```
PR to main → Add label "deploy-to-staging" → Auto-deploy PR branch to staging → Validation
```

**Pros:**
- Staging validation as part of PR approval process
- Team can test PR changes before merging to main
- Self-service (any team member can trigger via label)

**Cons:**
- Only tests PRs to `main` (not continuous staging)
- Requires label discipline from team

**Image Tags (Staging):**
```
ghcr.io/OWNER/REPO:staging-v0.1.0-20251015-abc123d   (timestamped)
ghcr.io/OWNER/REPO:staging-latest                     (always latest staging)
```

## Comparison: CI vs Staging Workflow

| Aspect | CI Workflow | Staging Workflow |
|--------|-------------|------------------|
| **Trigger** | Feature branches, PRs, release branches | `develop` push, manual, or PR label |
| **Validation** | Lint, type-check, tests, container build | Quick validation + smoke tests |
| **Container Push** | Only on `release/**` branches | Every staging deployment |
| **Image Tags** | `latest`, `{version}`, `{sha}` | `staging-v{version}-{timestamp}-{sha}`, `staging-latest` |
| **Purpose** | Code quality gates | Deployment validation |
| **Security Scan** | Blocks on vulnerabilities | Warns on vulnerabilities (doesn't block) |
| **Deployment** | No deployment (build only) | Deploys to staging environment |
| **Smoke Tests** | No | Yes (post-deployment validation) |

## Recommended Workflow Choice

### For Small Teams or Solo Projects:
**Use Option B: Manual Workflow Dispatch**
- Deploy to staging when needed for validation
- Lower costs, full control
- Simple workflow: `develop` → manual staging → `main` → production

### For Teams Using GitFlow:
**Use Option A: Automatic on `develop` Branch**
- Continuous staging deployment
- Fast feedback on integration issues
- Clear workflow: `feature` → `develop` (auto-staging) → `main` (production)

### For Teams Requiring Pre-Merge Validation:
**Use Option C: PR Label-Based**
- Validate changes before merging to `main`
- Team can test and approve based on staging results
- Workflow: `feature` → PR to `main` → add label → staging validation → merge

### Hybrid Approach (Most Flexible):
**Combine Options A + B:**
```yaml
on:
  push:
    branches:
      - develop
  workflow_dispatch:
    inputs:
      ref:
        default: 'develop'
```

- Auto-deploy on `develop` merge (continuous staging)
- Manual deploy any branch for testing (flexibility)
- Best of both worlds

## Staging Workflow Jobs

### 1. `check-trigger`
**Purpose:** Validate deployment conditions
**Actions:**
- Check if triggered by `develop` push, manual dispatch, or PR label
- Output `should_deploy` flag for downstream jobs

### 2. `validate`
**Purpose:** Run quick validation before deployment
**Actions:**
- Lint checking
- Type checking
- Unit tests (fast subset)
**Can Skip:** Use `skip_tests: true` in manual dispatch (use with caution)

### 3. `build-and-push`
**Purpose:** Build and push staging container image
**Actions:**
- Build container image from Containerfile
- Tag with staging-specific tags (timestamped + `staging-latest`)
- Push to GitHub Container Registry (ghcr.io)
- Output image metadata for downstream jobs

### 4. `security-scan`
**Purpose:** Scan staging image for vulnerabilities
**Actions:**
- Run Trivy security scan
- Upload SARIF results to GitHub Security tab
- **Does NOT block deployment** (warnings only)
**Rationale:** Staging allows testing with known issues; production blocks on vulnerabilities

### 5. `smoke-tests`
**Purpose:** Validate staging deployment
**Actions:**
- **Option 1 (Local):** Pull staging image, run locally, test health endpoint
- **Option 2 (Remote):** Test actual staging environment URL
**Tests:**
- Health check endpoint (HTTP 200 OK)
- Basic API functionality
- Application startup time

### 6. `summary`
**Purpose:** Generate deployment report
**Actions:**
- Aggregate job results
- Post summary to GitHub Actions UI
- Optional: Send notifications (Slack, Discord, Teams)

## Container Image Tagging Strategy

### Production Images (CI Workflow)
```
ghcr.io/luminosita/mcp:latest              # Always points to latest release
ghcr.io/luminosita/mcp:0.1.0               # Semantic version from pyproject.toml
ghcr.io/luminosita/mcp:abc123def456789     # Full commit SHA (traceability)
```

**Use Cases:**
- `latest`: Production deployments (rolling updates)
- `{version}`: Versioned releases (e.g., v0.1.0, v1.0.0)
- `{sha}`: Exact commit traceability for debugging

### Staging Images (Staging Workflow)
```
ghcr.io/luminosita/mcp:staging-latest                          # Always latest staging
ghcr.io/luminosita/mcp:staging-v0.1.0-20251015-143052-abc123d  # Timestamped staging
```

**Format:** `staging-v{version}-{YYYYMMDD-HHMMSS}-{short-sha}`

**Components:**
- `staging` prefix: Identifies as staging image
- `v{version}`: Base version from pyproject.toml (e.g., v0.1.0)
- `{YYYYMMDD-HHMMSS}`: Timestamp (allows ordering by time)
- `{short-sha}`: Short commit SHA (7 characters, traceability)

**Use Cases:**
- `staging-latest`: Staging environment (always pulls newest)
- Timestamped: Rollback to specific staging deployment, audit trail

**Examples:**
```bash
# Deploy latest staging
docker pull ghcr.io/luminosita/mcp:staging-latest

# Rollback to specific staging deployment
docker pull ghcr.io/luminosita/mcp:staging-v0.1.0-20251015-143052-abc123d

# Promote staging to production (after validation)
docker tag ghcr.io/luminosita/mcp:staging-latest ghcr.io/luminosita/mcp:0.1.0
docker push ghcr.io/luminosita/mcp:0.1.0
```

## Security Scanning Differences

### CI Workflow (Production)
```yaml
exit-code: '1'  # FAIL on vulnerabilities (blocks deployment)
severity: 'CRITICAL,HIGH,MEDIUM,LOW'
ignore-unfixed: true
```

**Rationale:** Production deployments must have no fixable vulnerabilities

### Staging Workflow
```yaml
exit-code: '0'  # WARN on vulnerabilities (doesn't block)
severity: 'CRITICAL,HIGH,MEDIUM,LOW'
ignore-unfixed: true
```

**Rationale:** Staging allows testing with known issues; team can validate fix urgency

## Deployment to Staging Environment

The workflow includes a **commented-out** `deploy-to-environment` job for deploying to actual staging infrastructure. Uncomment and configure based on your setup:

### Kubernetes Example
```yaml
deploy-to-environment:
  name: Deploy to Staging Environment
  runs-on: ubuntu-latest
  needs: [build-and-push, security-scan]
  environment:
    name: staging
    url: https://staging.example.com
  steps:
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/mcp-server \
          mcp-server=ghcr.io/${{ github.repository }}:staging-latest \
          -n staging
        kubectl rollout status deployment/mcp-server -n staging
```

### Docker Compose (Remote Host) Example
```yaml
- name: Deploy via SSH
  run: |
    ssh staging-host << 'EOF'
      cd /opt/mcp-server
      docker pull ghcr.io/${{ github.repository }}:staging-latest
      docker-compose up -d
    EOF
```

### AWS ECS Example
```yaml
- name: Deploy to ECS
  run: |
    aws ecs update-service \
      --cluster staging-cluster \
      --service mcp-server \
      --force-new-deployment
```

## Smoke Tests: Local vs Remote

### Local Smoke Tests (Current Implementation)
**Approach:** Pull staging image, run locally in GitHub Actions runner, test endpoints

**Pros:**
- No staging infrastructure required
- Fast (no network latency)
- Free (runs on GitHub Actions runner)

**Cons:**
- Doesn't test actual staging environment
- Requires mock database/dependencies

### Remote Smoke Tests (Optional)
**Approach:** Test actual staging environment URL

**Pros:**
- Tests real staging infrastructure
- Validates networking, load balancers, databases
- More realistic validation

**Cons:**
- Requires staging infrastructure
- Slower (network latency)
- Potential costs (cloud hosting)

**Recommendation:** Start with local smoke tests, add remote tests when staging infrastructure is deployed.

## GitHub Environments and Approvals

To add **manual approval gates** before staging deployment:

```yaml
deploy-to-environment:
  environment:
    name: staging
    url: https://staging.example.com
```

**Configure in GitHub:**
1. Go to Settings → Environments → New Environment → "staging"
2. Add protection rules:
   - Required reviewers (e.g., Tech Lead, DevOps)
   - Wait timer (e.g., 5 minutes before auto-deploy)
   - Deployment branches (only `develop`)

**Result:** Deployment pauses for manual approval before proceeding.

## Notifications

Uncomment and configure notifications in the `summary` job:

### Slack Example
```yaml
- name: Notify Slack
  if: always()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "Staging Deployment ${{ job.status }}",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Staging Deployment*: ${{ job.status }}\n*Commit*: ${{ github.sha }}\n*Actor*: ${{ github.actor }}"
            }
          }
        ]
      }
```

## Cost Optimization

### GitHub Actions Minutes
- **Free tier:** 2,000 minutes/month (public repos: unlimited)
- **Optimization:**
  - Use caching (`cache-from: type=gha`)
  - Skip validation tests when safe (`skip_tests: true`)
  - Use manual dispatch to reduce frequency

### Container Registry Storage
- **Free tier:** 500 MB storage
- **Optimization:**
  - Delete old staging images regularly
  - Use image retention policies (ghcr.io supports automatic cleanup)

### Staging Infrastructure
- **Local testing:** Free (runs on GitHub Actions runner)
- **Cloud staging:** Costs vary by provider
  - Consider spot/preemptible instances
  - Auto-shutdown during off-hours

## Migration Path

### Phase 1: Local Validation Only (Current)
- Staging workflow builds image
- Smoke tests run locally in GitHub Actions
- No actual staging environment

### Phase 2: Deploy to Staging Environment
- Uncomment `deploy-to-environment` job
- Configure Kubernetes/Docker Compose deployment
- Add remote smoke tests

### Phase 3: Advanced Validation
- Add load testing (k6, Locust)
- Add integration tests against staging database
- Add automated rollback on failure

## Troubleshooting

### Workflow Not Triggering
**Issue:** Staging workflow doesn't run after merging to `develop`

**Solution:**
1. Verify `develop` branch exists
2. Check workflow file is on default branch (`main`)
3. Verify workflow triggers in `.github/workflows/deploy-staging.yml`

### Image Push Fails (Authentication)
**Issue:** `unauthorized: unauthenticated` when pushing to ghcr.io

**Solution:**
1. Verify `packages: write` permission in workflow
2. Check repository Settings → Actions → General → Workflow permissions → "Read and write permissions"

### Smoke Tests Fail
**Issue:** Health check returns 404 or timeout

**Solution:**
1. Check container logs: `docker logs mcp-staging-smoke-test`
2. Verify environment variables set correctly
3. Increase wait time after container start (currently 10 seconds)

## Related Documentation

- **CI Workflow:** `.github/workflows/ci.yml`
- **Staging Workflow:** `.github/workflows/deploy-staging.yml`
- **Deployment Guide:** `docs/deployment-staging.md`
- **Validation Results:** `docs/staging-validation-results.md`
- **US-025:** `artifacts/backlog_stories/US-025_validate_container_deployment_staging_v1.md`

---

**Document Version:** v1.0
**Last Updated:** 2025-10-15
**Author:** Context Engineering PoC Team
**Next Review:** After staging infrastructure deployment (Phase 2)
