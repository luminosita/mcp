# EPIC-000
## Open Questions
1. **Container Runtime Selection:** Do we standardize on Docker Desktop for local development, or support multiple container runtimes (Podman, Rancher Desktop)? [DECISION REQUIRED: Week 1]

2. **Monorepo vs. Multi-Repo:** Should foundation support monorepo structure for all components, or separate repositories per major capability? [DECISION REQUIRED: Week 1]

3. **CI/CD Platform:** Do we use GitHub Actions (if GitHub-hosted), GitLab CI, or alternative? Must align with organizational standards. [REQUIRES PLATFORM TEAM INPUT]

4. **Python Version Policy:** What Python version range do we support (e.g., 3.10+, 3.11+ only)? Impacts dependency choices. [DECISION REQUIRED: Week 1]

5. **Dependency Management Tool:** Do we use Poetry, pip-tools, or alternative for Python dependency management? [DECISION REQUIRED: Week 1]


# EPIC-001
## Open Questions

[Require product/engineering input before PRD phase]

1. **Custom Field Support:** Do we need to support JIRA custom fields in MVP, or is standard field set sufficient? (Impacts scope and timeline)

2. **Write Operations:** Should we defer all write operations (create, update issues) to post-MVP, or is there high-value subset we should include? (Security vs. user value trade-off)

3. **Caching Strategy:** What cache TTL is acceptable? 5-minute cache reduces API calls but may show stale data. (Performance vs. freshness trade-off)

4. **Error Handling UX:** When PM API is down or rate-limited, should agent fail gracefully with explanation, or retry automatically? (User experience decision)

5. **Multi-Project Support:** Should agents query across all projects user has access to, or scope to specific project(s)? (Permission model and performance implications)

6. **Additional PM Tools Priority:** After JIRA/Linear, which PM tool should we prioritize next? (GitHub Projects, Asana, Monday.com, Trello) - Validate with customer development.

## Technical Considerations

### Architecture Impact

[High-level technical changes required—no detailed design at epic level]

**MCP Server Architecture:**
- Implement tool connectors as modular plugins (JIRA connector, Linear connector)
- Tool registration system exposing PM operations to MCP protocol
- Authentication credential management (secure storage, rotation)
- Rate limiting and caching layer to respect API quotas

**Agent Integration:**
- Tool schemas defining available PM operations (get_issue, search_issues, get_sprint)
- Natural language → structured query translation (agent responsibility, not server)
- Result formatting utilities for agent response generation

**Security & Observability:**
- OAuth 2.0 flow implementation for JIRA/Linear
- Audit logging for all PM tool queries (who, what, when)
- Error tracking and alerting for integration failures

### Dependencies

**Technical Dependencies:**
- **JIRA REST API v3:** Stable API, well-documented (mitigate: version compatibility checks)
- **Linear GraphQL API:** Stable API, TypeScript SDK available (mitigate: use official SDK)
- **OAuth 2.0 Library:** Python library for OAuth flows (mitigate: use battle-tested library like `authlib`)
- **MCP Python SDK:** Core protocol implementation (dependency: EPIC-003 must provide auth framework)

---
# EPIC-002

## Open Questions

[Require product/engineering/security input before PRD phase]

1. **Vector Database Selection:** Qdrant (open-source, self-hosted) vs. Pinecone (managed, simpler) vs. Weaviate? (Infrastructure complexity vs. operational burden trade-off)

2. **Embedding Model:** Use open-source sentence-transformers (free, self-hosted) or OpenAI embeddings (higher quality, cost)? (Cost vs. quality trade-off)

3. **ACL Granularity:** Space-level permissions (simpler) or page-level permissions (more accurate)? (Implementation complexity vs. security precision)

4. **Indexing Frequency:** Hourly, daily, or on-demand refresh? (Freshness vs. resource consumption trade-off)

5. **Chunk Size:** 256, 512, or 1024 tokens per chunk? (Retrieval precision vs. context completeness trade-off—requires experimentation)

6. **PII Filtering Strategy:** Block documents with PII entirely, mask PII in responses, or trust ACLs? (Security vs. usability trade-off—requires legal/compliance input)

7. **Multi-Tenancy:** How do we isolate knowledge bases for different customers/teams? (Enterprise deployment model question)


## Technical Considerations

### Architecture Impact

[High-level technical changes required—no detailed design at epic level]

**Indexing Pipeline:**
- Background job scheduler for periodic re-indexing (hourly/daily)
- Document chunking with configurable strategy (token limits, overlap)
- Embedding generation using sentence-transformers (all-MiniLM-L6-v2 or similar)
- Vector database storage with metadata filtering (Qdrant, Weaviate, Pinecone)

**MCP Server Integration:**
- Knowledge query tool exposing semantic search to agents
- Retrieval-Augmented Generation (RAG) pattern implementation
- Result ranking and snippet extraction
- Source citation metadata in tool responses

**Access Control:**
- Permission synchronization from source systems
- Document-level ACL enforcement during retrieval
- User context propagation through query pipeline
- Audit logging for compliance

**Observability:**
- Query latency tracking (P50, P95, P99)
- Retrieval precision monitoring (user feedback)
- Index freshness alerts (detect stale documents)
- Error tracking for connector failures

### Dependencies

**Technical Dependencies:**
- **Vector Database:** Qdrant, Weaviate, or Pinecone for embeddings storage
- **Embedding Model:** sentence-transformers library (HuggingFace)
- **Confluence/Notion APIs:** Official SDKs for document fetching
- **Document Parsers:** Libraries for PDF, Markdown, HTML extraction
- **MCP Python SDK:** Core protocol implementation (prerequisite: Month 1 foundation)

---
# EPIC-003

## Open Questions

[Require security/engineering/compliance input before PRD phase]

1. **SSO Provider Priority:** Which SSO providers should we prioritize? Okta, Auth0, Azure AD confirmed—others needed? (Customer validation)

2. **RBAC Granularity:** Tool-level permissions sufficient, or need resource-level (e.g., specific JIRA projects)? (Complexity vs. precision trade-off)

3. **Audit Log Retention:** How long should audit logs be retained? 90 days, 1 year, 7 years? (Compliance requirement varies by industry)

4. **Secrets Management:** Require KMS (Vault, AWS KMS) for MVP, or document for Phase 2? (Security vs. scope trade-off)

5. **Security Audit Timing:** Schedule audit in Month 4-5 or after all features complete in Month 6? (Risk mitigation vs. iteration time)

6. **Rate Limiting Strategy:** Per-user limits only, or also per-tool, per-IP, global? (Granularity vs. complexity)

7. **SAML Support:** Required for MVP (some enterprises mandate SAML), or defer to Phase 3? (Enterprise requirement validation needed)

## Technical Considerations

### Architecture Impact

[High-level technical changes required—no detailed design at epic level]

**Authentication Layer:**
- Middleware intercepting all MCP requests for authentication
- Multi-method auth handler (JWT, API key, OAuth 2.0)
- Token validation and user context extraction
- Session management with secure cookies/tokens

**Authorization Framework:**
- RBAC policy engine evaluating tool permissions
- Permission definitions in config files or database
- User-to-role mapping (via SSO claims or local config)
- Tool registration with required permissions

**Audit System:**
- Structured logging framework (JSON logs)
- Async log writer to avoid performance impact
- Log rotation and retention policy
- SIEM integration endpoints (syslog, HTTP)

**Security Hardening:**
- Rate limiting middleware (per-user, per-IP, global)
- Input validation and sanitization
- TLS/HTTPS enforcement
- Secrets management (environment variables, future KMS)

## Dependencies

**Technical Dependencies:**
- **JWT Library:** PyJWT or authlib for token validation
- **OAuth 2.0 Library:** authlib or requests-oauthlib for OAuth flows
- **Logging Framework:** Python logging with structured formatter
- **Rate Limiting:** redis-py or in-memory rate limiter
- **MCP Python SDK:** Core protocol implementation (prerequisite: Month 1 foundation)

---
# EPIC-004

## Open Questions

[Require DevOps/engineering input before PRD phase]

1. **Tracing Backend:** Jaeger (mature, more features) vs. Grafana Tempo (simpler, integrates with Grafana)? (Operational complexity vs. feature set trade-off)

2. **Trace Sampling:** What sampling rate? 100% (low volume), 10% (medium), adaptive? (Completeness vs. cost trade-off)

3. **Metrics Retention:** How long to retain metrics? 30 days, 90 days, 1 year? (Storage cost vs. historical analysis needs)

4. **Alerting Channels:** PagerDuty required, or also Slack, email, Opsgenie? (Integration scope based on customer needs)

5. **Dashboard Customization:** Allow customers to customize dashboards, or provide fixed templates? (Flexibility vs. support complexity)

6. **Multi-Tenancy:** How to isolate metrics for different customers/teams? (Enterprise deployment model question)

7. **Logging Integration:** Basic structured logging sufficient, or need full log aggregation (ELK, Splunk)? (Scope for MVP vs. Phase 2)

## Technical Considerations

### Architecture Impact

[High-level technical changes required—no detailed design at epic level]

**Instrumentation Layer:**
- OpenTelemetry SDK integration for metrics, tracing, logging
- Automatic instrumentation for HTTP, DB, external API calls
- Custom instrumentation for MCP protocol operations
- Context propagation across async operations

**Metrics Collection:**
- Prometheus client library for metrics export
- Metrics endpoint (:/metrics) for Prometheus scraping
- Metric naming conventions (RED method, resource utilization)
- Cardinality management (avoid high-cardinality labels)

**Tracing System:**
- Jaeger or Tempo backend for trace storage
- Span creation for key operations (auth, tool invocation, retrieval)
- Trace sampling strategy (100% for low volume, adaptive for high volume)
- Trace context propagation in HTTP headers

**Error Tracking:**
- Sentry SDK integration for error capture
- Error fingerprinting and grouping
- Stack trace and context capture
- Release tracking for error regression detection

**Dashboards:**
- Grafana for visualization
- Pre-built dashboard templates (health, tools, SLA)
- Dashboard-as-code (JSON configs in repo)
- Alerting rules configured in Grafana or Alertmanager

### Dependencies

**Technical Dependencies:**
- **OpenTelemetry SDK:** Instrumentation library for Python
- **Prometheus:** Metrics storage and query engine
- **Grafana:** Dashboard and visualization platform
- **Jaeger or Grafana Tempo:** Distributed tracing backend
- **Sentry:** Error tracking platform
- **PagerDuty/Opsgenie:** Incident alerting (optional, configurable)

---
# EPIC-005

## Open Questions

[Require DevOps/security input before PRD phase]

1. **Helm vs. Raw Manifests:** Generate Helm charts or raw Kubernetes YAML? (Flexibility vs. simplicity trade-off—Helm has adoption but adds complexity)

2. **CI/CD Platform Priority:** GitHub Actions, GitLab CI confirmed—need Jenkins, CircleCI, others? (Customer validation)

3. **Security Scanner:** Trivy (open-source, container focus) or Checkov (infrastructure-as-code focus) or both? (Coverage vs. integration complexity)

4. **Configuration Customization:** How much parameterization? Opinionated defaults vs. full customization? (Usability vs. flexibility)

5. **Deployment Automation:** Keep out of scope for MVP, or add basic deployment execution? (Security vs. convenience trade-off)

6. **Multi-Cloud Support:** Kubernetes-only sufficient, or need AWS ECS/GCP Cloud Run templates? (Scope validation with customers)

7. **GitOps Integration:** Defer to future or include basic ArgoCD/Flux support? (Adoption pattern in target customers)

## Technical Considerations

### Architecture Impact

[High-level technical changes required—no detailed design at epic level]

**Configuration Generation Engine:**
- Template-based generation (Jinja2 templates for Kubernetes, Docker, CI/CD)
- Parameter inference from MCP server configuration
- Validation engine (syntax, security policies, best practices)
- Multi-environment support (parameterized configs)

**MCP Server Integration:**
- Deployment tool schema exposing config generation capabilities
- Context propagation (MCP server config → deployment params)
- Interactive refinement (iterative config generation based on feedback)
- Output formatting (YAML, JSON, multi-file generation)

**Security Scanning Integration:**
- Trivy or Checkov integration for security validation
- Policy-as-code enforcement (OPA, Kyverno policies)
- Automated security checks in generation pipeline

**Documentation Generation:**
- Deployment guide generation (prerequisites, steps, troubleshooting)
- Architecture diagram generation (optional, if feasible)

### Dependencies

**Technical Dependencies:**
- **Template Engine:** Jinja2 for YAML/Dockerfile templates
- **Validation Libraries:** yamllint, kubeval for Kubernetes validation
- **Security Scanners:** Trivy, Checkov for security scanning
- **Docker SDK:** For Dockerfile validation and build testing
- **Kubernetes Client:** For kubectl --dry-run validation
- **MCP Python SDK:** Core protocol implementation
