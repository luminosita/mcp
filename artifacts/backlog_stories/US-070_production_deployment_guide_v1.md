# User Story: Production Deployment Guide

## Metadata
- **Story ID:** US-070
- **Title:** Create Production Deployment Runbook for MCP Framework
- **Type:** Feature
- **Status:** Backlog
- **Priority:** High - Enables production deployment after 30-day stability period
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-011
- **Functional Requirements Covered:** Deployment operational readiness
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Timeline & Milestones - Phase 6: Production deployment guide

**Parent High-Level Story:** [HLS-011: Production Readiness and Pilot]
- **Link:** `/artifacts/hls/HLS-011_production_readiness_pilot_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 8: Production Deployment Guide

## User Story
As an **Infrastructure Engineer**, I want **step-by-step production deployment runbook** so that **I can deploy MCP framework to production environment without trial-and-error or maintainer assistance**.

## Description

After 30-day stability period completes (US-069), infrastructure teams need operational runbook for deploying MCP framework to production. This differs from general deployment guide (US-068) by focusing on production-specific concerns:

**Production-Specific Requirements:**
- **High Availability:** Multi-replica deployment with load balancing, zero downtime updates
- **Security Hardening:** TLS certificates, firewall rules, secrets management (AWS Secrets Manager or HashiCorp Vault)
- **Backup and Disaster Recovery:** Automated database backups, restore procedures, runbook for system recovery
- **Monitoring and Alerting:** Production-grade observability (Prometheus, Grafana, PagerDuty integration)
- **Capacity Planning:** Resource allocation (CPU, memory, database size), scaling thresholds
- **Incident Response:** Runbook for common production incidents (database failure, MCP Server crash, network issues)

This story delivers production deployment runbook (docs/production_deployment_runbook.md) covering:
1. **Pre-Deployment Checklist** - Infrastructure prerequisites, security requirements, capacity planning
2. **Deployment Procedure** - Step-by-step commands for production deployment (Kubernetes recommended, Docker Compose alternative)
3. **Post-Deployment Validation** - Smoke tests, health checks, performance validation
4. **Backup Configuration** - Automated PostgreSQL backups (daily snapshots, 30-day retention)
5. **Disaster Recovery Procedures** - Database restore, MCP Server recovery, rollback procedures
6. **Incident Response Runbook** - Troubleshooting common production incidents with escalation paths

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§9.1: Kubernetes Deployment** - Production deployment uses Kubernetes for HA, horizontal scaling, zero-downtime updates
  - **Example Code:** §9.1 provides deployment.yaml manifest with replicas=3, resource limits, health probes
- **§9.2: CI/CD Pipeline** - Automated deployment via GitHub Actions with health check validation
  - **Example Code:** §9.2 shows kubectl rollout status validation in CI/CD workflow

**Anti-Patterns Avoided:**
- **Manual deployment:** Production uses GitOps or CI/CD automation (not manual kubectl apply)

**Performance Considerations:**
- N/A (operational deployment guide)

## Functional Requirements
- Production deployment runbook (docs/production_deployment_runbook.md)
- **Pre-Deployment Checklist:**
  - Infrastructure prerequisites (Kubernetes cluster, PostgreSQL managed instance, Redis cluster)
  - Security requirements (TLS certificates, firewall rules, secrets management setup)
  - Capacity planning (recommended CPU/memory allocations, database sizing)
- **Deployment Procedure:**
  - Kubernetes deployment steps (namespace creation, secrets configuration, deployment.yaml apply)
  - Docker Compose alternative (for smaller deployments)
  - Zero-downtime update procedure (rolling deployment with health checks)
- **Post-Deployment Validation:**
  - Smoke tests (call /health endpoint, test MCP tool invocation)
  - Performance validation (p95 latency <100ms for resources, <500ms for tools)
  - Security validation (TLS certificate check, authentication test)
- **Backup Configuration:**
  - Automated PostgreSQL backup setup (daily snapshots, 30-day retention)
  - Backup verification procedure (test restore to staging environment)
- **Disaster Recovery Procedures:**
  - Database restore from snapshot (step-by-step commands)
  - MCP Server recovery (restart pods, check logs, validate health)
  - Full system rollback (revert to previous deployment version)
- **Incident Response Runbook:**
  - **Incident 1:** MCP Server unavailable → Check pod status, review logs, restart if needed
  - **Incident 2:** High latency (p95 >500ms) → Check database connection pool, review slow queries, scale pods if needed
  - **Incident 3:** Authentication failures → Validate JWT public key, check secrets configuration
  - **Incident 4:** Database connection errors → Check PostgreSQL availability, connection pool exhaustion
  - Escalation path (contact framework maintainer if incidents persist >1 hour)

## Non-Functional Requirements
- **Completeness:** Runbook covers 100% of production deployment scenarios (deployment, validation, backup, disaster recovery, incident response)
- **Clarity:** Commands copy-paste ready (no placeholders requiring manual substitution except environment-specific values like cluster name)
- **Testability:** All procedures validated against production-equivalent staging environment

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** Reference patterns-architecture.md for deployment structure.

### Implementation Guidance

**Deployment Architecture (Production Recommendation):**
```
┌───────────────────────────────────────────────────┐
│   Kubernetes Cluster (Production)                 │
│                                                    │
│   ┌──────────────────────────────────────────┐   │
│   │  MCP Server Deployment (3 replicas)      │   │
│   │  - Rolling update strategy                │   │
│   │  - Resource limits: CPU 1000m, Memory 2Gi │   │
│   │  - Health probes: liveness, readiness     │   │
│   └──────────────────────────────────────────┘   │
│                                                    │
│   ┌──────────────────────────────────────────┐   │
│   │  Task Tracking Microservice (2 replicas) │   │
│   │  - Go binary in container                 │   │
│   │  - Resource limits: CPU 500m, Memory 1Gi  │   │
│   └──────────────────────────────────────────┘   │
│                                                    │
│   ┌──────────────────────────────────────────┐   │
│   │  Redis (managed or 3-replica cluster)     │   │
│   │  - Persistence enabled (AOF + RDB)        │   │
│   └──────────────────────────────────────────┘   │
└───────────────────────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────┐
│   Managed PostgreSQL (AWS RDS, GCP Cloud SQL)     │
│   - Multi-AZ deployment                            │
│   - Automated backups (daily, 30-day retention)    │
│   - Point-in-time recovery enabled                 │
└───────────────────────────────────────────────────┘
```

**Runbook Format:**
- **Markdown** - Human-readable with code blocks for commands
- **Step-by-step numbering** - Clear sequence for deployment
- **Expected outputs** - Show what success looks like after each step
- **Troubleshooting sidebars** - Common issues inline with steps

**References to Implementation Standards:**
- **patterns-architecture.md:** Follow established Kubernetes deployment structure
- **patterns-tooling.md:** Reference Taskfile commands for local testing

**Note:** Treat patterns-*.md content as authoritative - supplement with production-specific deployment guidance.

### Technical Tasks

**Runbook Writing Tasks:**
1. Write Pre-Deployment Checklist (infrastructure, security, capacity planning)
2. Write Kubernetes Deployment Procedure (step-by-step with kubectl commands)
3. Write Docker Compose Alternative Deployment Procedure (for smaller deployments)
4. Write Post-Deployment Validation Section (smoke tests, performance validation, security validation)
5. Write Backup Configuration Section (PostgreSQL automated backups, verification procedure)
6. Write Disaster Recovery Procedures (database restore, MCP Server recovery, rollback)
7. Write Incident Response Runbook (4 common incidents with troubleshooting steps)

**Validation Tasks:**
1. Test all kubectl commands against production-equivalent staging cluster
2. Validate backup and restore procedures (restore database from snapshot to staging)
3. Test incident response procedures (simulate incidents, validate troubleshooting steps)
4. Peer review by infrastructure engineer unfamiliar with deployment

## Acceptance Criteria

### Scenario 1: Pre-Deployment Checklist Completeness
**Given** Production deployment runbook at docs/production_deployment_runbook.md
**When** Infrastructure engineer reads Pre-Deployment Checklist
**Then** Checklist includes all prerequisites:
  - [ ] Kubernetes cluster provisioned (v1.25+, 3+ nodes)
  - [ ] Managed PostgreSQL instance provisioned (Multi-AZ, automated backups enabled)
  - [ ] Redis cluster provisioned (3-replica for HA, persistence enabled)
  - [ ] TLS certificate obtained (Let's Encrypt, enterprise CA, or cloud provider certificate)
  - [ ] Secrets management configured (AWS Secrets Manager, HashiCorp Vault, or Kubernetes Secrets)
  - [ ] Firewall rules configured (allow HTTPS traffic to MCP Server, PostgreSQL access from cluster)
  - [ ] Capacity planned (CPU: 3× 1000m cores, Memory: 3× 2Gi RAM for MCP Server; 2× 500m cores, 2× 1Gi RAM for Task Tracking microservice)

### Scenario 2: Kubernetes Deployment Procedure
**Given** Runbook Kubernetes Deployment section
**When** Infrastructure engineer follows step-by-step procedure
**Then** Deployment completes successfully with commands:
  1. `kubectl create namespace mcp-framework`
  2. `kubectl create secret generic mcp-secrets --from-literal=database-url="..." --from-literal=redis-url="..." -n mcp-framework`
  3. `kubectl apply -f k8s/deployment.yaml -n mcp-framework` (deploys MCP Server with 3 replicas)
  4. `kubectl apply -f k8s/task-tracking-deployment.yaml -n mcp-framework` (deploys Task Tracking microservice with 2 replicas)
  5. `kubectl apply -f k8s/service.yaml -n mcp-framework` (exposes MCP Server via LoadBalancer)
  6. `kubectl rollout status deployment/mcp-server -n mcp-framework` (waits for deployment success)
**And** Expected output shown for each step (e.g., "deployment.apps/mcp-server created")

### Scenario 3: Post-Deployment Validation (Smoke Tests)
**Given** MCP framework deployed to production
**When** Infrastructure engineer runs smoke tests from runbook
**Then** All smoke tests pass:
  - [x] Health check: `curl https://mcp-server.prod.example.com/health` returns `{"status": "healthy"}`
  - [x] MCP tool invocation: Call `validate_artifact` tool via MCP client, returns successful validation result
  - [x] Task Tracking API: `curl https://mcp-server.prod.example.com/tasks/next?project=test` returns 401 Unauthorized (authentication required - correct behavior)
  - [x] Performance validation: `curl https://mcp-server.prod.example.com/resources/sdlc/core` completes within <100ms (p95 latency target)
  - [x] TLS certificate validation: `curl -v https://mcp-server.prod.example.com/health` shows valid TLS certificate (not self-signed warning)

### Scenario 4: Backup Configuration
**Given** Runbook Backup Configuration section
**When** Infrastructure engineer configures PostgreSQL automated backups
**Then** Backup configuration includes:
  - **Backup Schedule:** Daily snapshots at 2:00 AM UTC
  - **Retention Policy:** 30-day retention (delete snapshots older than 30 days)
  - **Verification Procedure:** Weekly restore test to staging environment (every Monday)
**And** Runbook provides example AWS RDS backup command: `aws rds create-db-snapshot --db-instance-identifier mcp-postgres-prod --db-snapshot-identifier mcp-backup-$(date +%Y%m%d)`

### Scenario 5: Disaster Recovery - Database Restore
**Given** Production database corruption or data loss
**When** Infrastructure engineer follows Database Restore procedure from runbook
**Then** Restore completes successfully with steps:
  1. Identify latest snapshot: `aws rds describe-db-snapshots --db-instance-identifier mcp-postgres-prod | grep SnapshotCreateTime | tail -1`
  2. Restore snapshot to new instance: `aws rds restore-db-instance-from-db-snapshot --db-instance-identifier mcp-postgres-prod-restored --db-snapshot-identifier mcp-backup-20251018`
  3. Wait for restore completion: `aws rds describe-db-instances --db-instance-identifier mcp-postgres-prod-restored | grep DBInstanceStatus` (wait for "available")
  4. Update MCP Server DATABASE_URL secret to point to restored instance
  5. Restart MCP Server pods: `kubectl rollout restart deployment/mcp-server -n mcp-framework`
  6. Validate data integrity (query database for expected artifacts)

### Scenario 6: Incident Response - MCP Server Unavailable
**Given** Production incident: MCP Server returns 503 Service Unavailable
**When** On-call engineer follows Incident 1 runbook
**Then** Troubleshooting steps resolve incident:
  1. Check pod status: `kubectl get pods -n mcp-framework -l app=mcp-server` (shows 0/3 pods Running)
  2. Review pod logs: `kubectl logs deployment/mcp-server -n mcp-framework --tail=50` (shows database connection timeout errors)
  3. Check database availability: `psql -h mcp-postgres-prod.example.com -U mcp_user -c "SELECT 1"` (succeeds - database available)
  4. Identify issue: Connection pool exhaustion (all 20 connections in use, max_overflow=10 exceeded)
  5. Remediation: Scale MCP Server to 5 replicas: `kubectl scale deployment/mcp-server --replicas=5 -n mcp-framework`
  6. Validate health: `curl https://mcp-server.prod.example.com/health` returns 200 OK
**And** Escalation path: If incident not resolved within 1 hour, contact framework maintainer (Slack DM or PagerDuty escalation)

### Scenario 7: Zero-Downtime Update Procedure
**Given** New MCP Server version ready for deployment (v1.1.0)
**When** Infrastructure engineer follows Zero-Downtime Update procedure
**Then** Update completes without downtime:
  1. Update deployment.yaml with new image tag: `image: mcp-server:v1.1.0`
  2. Apply updated manifest: `kubectl apply -f k8s/deployment.yaml -n mcp-framework`
  3. Monitor rolling update: `kubectl rollout status deployment/mcp-server -n mcp-framework` (shows "successfully rolled out")
  4. Validate new version: `curl https://mcp-server.prod.example.com/health | jq '.version'` returns `"v1.1.0"`
**And** Traffic served continuously (Kubernetes rolling update replaces pods one at a time, readiness probe ensures traffic only to healthy pods)

### Scenario 8: Runbook Validation Against Staging
**Given** All runbook procedures written
**When** Infrastructure engineer tests procedures against production-equivalent staging environment
**Then** All procedures execute successfully:
  - [x] Deployment procedure completes without errors
  - [x] Post-deployment validation passes all smoke tests
  - [x] Backup configuration verified (snapshot created and restored)
  - [x] Disaster recovery procedures tested (database restore validated)
  - [x] Incident response procedures tested (simulated incidents resolved)
**And** Any command errors corrected in runbook before production deployment

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 3 SP (SKIP per decision matrix - straightforward documentation task)
- **Developer Count:** Single developer (infrastructure engineer or tech lead with ops experience)
- **Domain Span:** Single domain (documentation only - no code changes)
- **Complexity:** Low - operational runbook writing, similar to US-068 deployment guide but production-specific
- **Uncertainty:** Low - clear runbook structure, well-defined sections
- **Override Factors:** None - no cross-domain changes, no unfamiliar activities

**Justification for No Tasks:** 3 SP straightforward documentation task does not justify task decomposition overhead. Implementation can proceed as cohesive unit by single developer.

## Definition of Done
- [ ] Production deployment runbook written at docs/production_deployment_runbook.md
- [ ] Pre-Deployment Checklist complete (infrastructure, security, capacity planning)
- [ ] Kubernetes Deployment Procedure complete with step-by-step commands
- [ ] Post-Deployment Validation section complete (smoke tests, performance validation)
- [ ] Backup Configuration section complete (automated backups, verification procedure)
- [ ] Disaster Recovery Procedures complete (database restore, MCP Server recovery, rollback)
- [ ] Incident Response Runbook complete (≥4 common incidents with troubleshooting steps)
- [ ] All commands tested against production-equivalent staging environment
- [ ] Peer review completed by infrastructure engineer unfamiliar with deployment
- [ ] Product Owner validates runbook completeness and clarity

## Additional Information
**Suggested Labels:** documentation, production-deployment, runbook, operational
**Estimated Story Points:** 3 SP
**Dependencies:**
- **Upstream:** US-068 (General deployment guide provides foundation), US-069 (30-day stability period validates production readiness)
- **Blocked By:** None (all dependencies completed)
**Related PRD Section:** PRD-006 §Timeline & Milestones - Phase 6: Production deployment guide

## Open Questions & Implementation Uncertainties

**Question 1:** Should runbook include Terraform/CloudFormation infrastructure-as-code templates or just manual provisioning steps?
- **Marker:** [REQUIRES TECH LEAD]
- **Context:** IaC provides automation but adds complexity; manual provisioning more universally applicable
- **Recommendation:** Manual provisioning for initial runbook (cloud-agnostic); defer IaC templates to future enhancement

**Question 2:** Should disaster recovery procedures include cross-region failover or single-region restore only?
- **Marker:** [REQUIRES TECH LEAD]
- **Context:** Cross-region failover provides higher availability but requires additional infrastructure (replicated database, multi-region Kubernetes)
- **Recommendation:** Single-region restore for pilot phase (simpler); cross-region failover deferred to future production scaling story

**Question 3:** Should runbook include PagerDuty integration setup or just email alerts?
- **Marker:** [REQUIRES TECH LEAD]
- **Context:** PagerDuty provides 24/7 on-call rotation but requires subscription; email alerts simpler but may be missed
- **Recommendation:** Include both options in runbook (email for pilot, PagerDuty for production scale); document PagerDuty setup as optional

No open implementation questions requiring spikes or ADRs. All operational procedures clear from HLS-011 and PRD-006.

---

**Version History:**
- **v1 (2025-10-18):** Initial version generated from HLS-011 v2
