# EPIC-001

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

---

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
