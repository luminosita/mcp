# Hybrid CLAUDE.md Enhancement TODO

This document contains prioritized checklists for enhancing the hybrid CLAUDE.md structure based on identified gaps and missing configurations.

---

## 🔴 HIGH PRIORITY (Week 1)

### Missing Core Configurations

- [x] **Create `docs/hybrid/go/.claude/configs/github-actions.md`** ✅
  - Purpose: CI/CD workflow templates for GitHub Actions
  - Include: Go test workflow, lint workflow, security scanning, build/release pipeline
  - Example: `.github/workflows/ci.yml` with matrix builds, coverage upload, artifact creation
  - Reference: Standard Go CI patterns with golangci-lint, govulncheck, test with race detection

- [x] **Create `docs/hybrid/go/.claude/configs/taskfile.md`** ✅
  - Purpose: Comprehensive Taskfile for common development tasks
  - Include: Targets for build, test, lint, coverage, docker, migrations, generate
  - Reference: Common Go Takefile patterns with dependency management

- [x] **Create `docs/hybrid/go/.claude/configs/environment.md`** ✅
  - Purpose: Environment variable templates and configuration management
  - Include: `.env.example` template, required vs optional vars, validation patterns
  - Example: DATABASE_URL, JWT_SECRET, API keys structure, feature flags
  - Reference: 12-factor app configuration principles

### Critical Missing Examples

- [x] **Create `new_prompts/patterns/go/patterns-database.md`** ✅
  - Purpose: Database patterns, Database Migration Patterns, Database schema versioning and migration strategies
  - Include: golang-migrate/migrate examples, up/down migrations, seed data
  - Example: Migration file structure, rollback strategies, CI/CD integration

- [x] **Create `new_prompts/patterns/go/patterns-api.md`** ✅
  - Purpose: API patterns
  - Include: API version management strategies, URL versioning (/v1/, /v2/), header versioning, deprecation policies
  - Example: Handler organization for multiple versions, backward compatibility

- [x] **Create `new_prompts/patterns/go/patterns-observability.md`** ✅
  - Purpose: Monitoring, logging, and tracing patterns
  - Include: Structured logging (slog), Prometheus metrics, OpenTelemetry tracing, health checks
  - Example: Complete observability setup with middleware, metric collectors, trace spans
  - Reference: Go observability best practices, cloud-native patterns

- [ ] **Create `new_prompts/patterns/go/patterns-kubernetes.md`**
  - Purpose: Kubernetes deployment patterns and configurations for Go applications
  - Include: Deployment manifests, Service definitions, ConfigMaps/Secrets, Ingress, HPA, resource limits
  - Example: Complete k8s setup with health probes, rolling updates, init containers, pod security
  - Reference: Production-ready k8s patterns, 12-factor app deployment, observability integration

- [ ] **Create `new_prompts/patterns/go/patterns-crossplane.md`**
  - Purpose: Crossplane infrastructure patterns and Composition definitions
  - Include: Composite Resource Definitions (XRDs), Compositions, Claims, provider configurations
  - Example: Database provisioning, cloud resource management, GitOps integration, policy enforcement
  - Reference: Platform engineering patterns, cloud-native infrastructure as code, multi-cloud abstractions

- [ ] **Create `docs/hybrid/go/.claude/configs/kubernetes.md`**
  - Purpose: Kubernetes configuration templates and deployment strategies
  - Include: Deployment YAML, StatefulSet for stateful apps, CronJob patterns, namespace organization
  - Example: Complete manifest templates with best practices, Kustomize overlays, Helm chart structure
  - Reference: kubectl apply workflows, GitOps with ArgoCD/Flux, blue-green and canary deployments

- [ ] **Create `docs/hybrid/go/.claude/configs/crossplane.md`**
  - Purpose: Crossplane composition templates and provider setup
  - Include: XRD schemas, Composition templates, ProviderConfig, CompositeResourceClaim examples
  - Example: Multi-resource compositions (VPC + RDS + S3), patch and transform patterns, dependencies
  - Reference: Crossplane best practices, composition functions, policy as code integration

- [ ] **Create `new_prompts/patterns/go/patterns-chainsaw.md`**
  - Purpose: Chainsaw (Kyverno) Kubernetes testing framework patterns and test scenarios
  - Include: Test suite structure, assertion patterns, resource operations, scenario composition
  - Example: E2E tests for k8s resources, policy validation, deployment verification, chaos testing
  - Reference: Chainsaw test patterns, declarative k8s testing, CI/CD integration

- [ ] **Create `docs/hybrid/go/.claude/configs/chainsaw.md`**
  - Purpose: Chainsaw test configuration and test case templates
  - Include: chainsaw-test.yaml structure, test steps, assertions, bindings, cluster setup
  - Example: Complete test cases for deployments, statefulsets, operators, policy enforcement
  - Reference: Chainsaw configuration options, test organization, multi-cluster testing

---

## 🟡 MEDIUM PRIORITY (Weeks 2-3)

### Security Enhancements

- [x] **Add OAuth2/OIDC Integration to `new_prompts/patterns/go/patterns-security.md`** ✅
  - Purpose: Third-party authentication patterns
  - Include: OAuth2 flows, OIDC token validation, provider integration (Google, GitHub)
  - Example: Complete OAuth2 implementation with token exchange, refresh, PKCE
  - Add after: JWT section (line ~150)

- [x] **Add CSRF Protection to `new_prompts/patterns/go/patterns-security.md`** ✅
  - Purpose: Cross-Site Request Forgery prevention
  - Include: CSRF token generation, validation middleware, double-submit cookie pattern
  - Example: gorilla/csrf integration, stateless CSRF with JWT
  - Add after: Security headers middleware section

- [x] **Add API Key Management to `new_prompts/patterns/go/patterns-api.md`** ✅
  - Purpose: API key generation, rotation, and validation
  - Include: Secure key generation, hashing strategies, rotation policies, scoping
  - Example: Complete API key service with middleware, rate limiting per key
  - Add after: JWT validation section

### Infrastructure Patterns

- [x] **Create `new_prompts/patterns/go/patterns-caching.md`** ✅
  - Purpose: Caching strategies and Redis integration
  - Include: Cache-aside, read-through, write-through patterns, Redis client setup
  - Example: Distributed cache implementation, TTL strategies, cache invalidation
  - Reference: Cache coherence patterns, stampede prevention

- [x] **Create `new_prompts/patterns/go/patterns-grpc.md`** ✅
  - Purpose: gRPC service implementation patterns
  - Include: Proto definitions, server/client implementation, interceptors, streaming
  - Example: Complete gRPC service with unary and streaming RPCs, error handling
  - Reference: gRPC Go best practices, connection management

- [x] **Create `new_prompts/patterns/go/patterns-messaging.md`** ✅
  - Purpose: Message queue integration (RabbitMQ, Kafka, NATS)
  - Include: Publisher/subscriber patterns, dead letter queues, retry logic
  - Example: Event-driven architecture with message handlers, idempotency
  - Reference: Reliable messaging patterns, at-least-once delivery

### Configuration Expansions

- [x] **Expand Configuration Management in Core or Create Dedicated File** ✅
  - Purpose: Advanced config patterns beyond environment variables
  - Include: Viper integration, config file formats (YAML, TOML), environment overrides
  - Example: Hierarchical config with defaults, env-specific, runtime reload
  - Current coverage: 40% → Target: 90%
  - Note: Implemented in `environment.md` with comprehensive Viper integration

---

## 🟢 LOW PRIORITY (Week 4+)

### Additional Patterns

- [x] **Create `new_prompts/patterns/go/patterns-websockets.md`** ✅
  - Purpose: Real-time communication patterns
  - Include: WebSocket connection management, broadcasting, room patterns
  - Example: Chat server, real-time notifications, connection pooling
  - Reference: gorilla/websocket patterns, scaling considerations

- [x] **Create `new_prompts/patterns/go/patterns-cli.md`** ✅
  - Purpose: Command-line application patterns
  - Include: Cobra framework setup, flag parsing, subcommands, configuration
  - Example: Complete CLI app with commands, persistent flags, completion
  - Reference: CLI UX best practices, configuration precedence

- [x] **Add File Upload/Download Patterns** ✅
  - Purpose: File handling in HTTP services
  - Location: Add to `new_prompts/patterns/go/patterns-security.md` or create dedicated section
  - Include: Multipart form handling, streaming large files, progress tracking, validation
  - Example: Secure file upload with size limits, type validation, virus scanning hooks

### Operational Guides

- [ ] **Create `docs/hybrid/go/.claude/guides/onboarding.md`**
  - Purpose: New developer onboarding guide
  - Include: Setup checklist, architecture overview, development workflow, resources
  - Structure: Day 1 tasks, Week 1 goals, common gotchas, who to ask
  - Reference: Team-specific practices, code review process

- [ ] **Create `docs/hybrid/go/.claude/guides/troubleshooting.md`**
  - Purpose: Common issues and solutions
  - Include: Database connection issues, dependency conflicts, test failures, deployment problems
  - Structure: Problem → Diagnosis → Solution pattern, links to relevant docs
  - Reference: Stack traces interpretation, debugging techniques

- [ ] **Create `docs/hybrid/go/.claude/guides/deployment.md`**
  - Purpose: Deployment procedures and best practices
  - Include: Build process, environment promotion, rollback procedures, health checks
  - Structure: Step-by-step deployment guide, pre-deployment checklist, monitoring
  - Reference: Blue-green deployment, canary releases, feature flags

### Tool-Specific Configurations

- [x] **Create `.claude/configs/air.md`** (Live Reload for Development) ✅
  - Purpose: Hot reload configuration for development
  - Include: .air.toml configuration, exclude patterns, build commands
  - Example: Optimized Air config for Go projects with proper file watching
  - Reference: Air best practices, performance tuning
  - Note: Implemented in `taskfile.md` with complete Air configuration

- [x] **Create `docs/hybrid/go/.claude/configs/docker-compose.md`** ✅
  - Purpose: Local development environment with Docker Compose
  - Include: Multi-service setup (app, db, redis, etc.), networking, volumes
  - Example: Complete docker-compose.yml with health checks, depends_on, env files
  - Reference: Docker Compose best practices for Go development

### Advanced Topics

- [ ] **Add GraphQL Patterns** (if using GraphQL)
  - Location: Create `new_prompts/patterns/go/patterns-graphql.md`
  - Include: Schema definitions, resolver patterns, dataloader for N+1, subscriptions
  - Example: Complete GraphQL server with gqlgen, error handling, authentication
  - Reference: GraphQL Go best practices

- [ ] **Add Event Sourcing Patterns** (if applicable)
  - Location: Add to `new_prompts/patterns/go/patterns-events.md` or create dedicated file
  - Include: Event store implementation, aggregate patterns, projections, CQRS
  - Example: Event-sourced aggregate with command handlers, event replay
  - Reference: Event sourcing in Go, consistency boundaries

---

## 📋 CONTINUOUS IMPROVEMENT

### Version-Specific Updates

- [ ] **Monitor Go Version Updates**
  - Action: Review new Go version features quarterly
  - Update: Add new language features to relevant pattern files
  - Example: Go 1.22+ features, new standard library packages
  - Schedule: Every Go minor version release

- [ ] **Track Library Updates**
  - Action: Monitor updates to recommended libraries (testify, Wire, etc.)
  - Update: Revise examples when breaking changes occur
  - Example: Update mock generation syntax, new testing helpers
  - Schedule: Monthly review of major dependencies

### Metrics and Iteration

- [ ] **Establish Usage Metrics**
  - Metric 1: Track which pattern files are accessed most frequently
  - Metric 2: Measure AI suggestion acceptance rate
  - Metric 3: Count corrections needed per AI-generated code
  - Action: Use metrics to prioritize pattern improvements

- [ ] **Gather Team Feedback**
  - Action: Quarterly survey on CLAUDE.md helpfulness
  - Questions: Missing patterns? Unclear examples? Redundant content?
  - Process: Incorporate feedback into next iteration
  - Schedule: End of each quarter

- [ ] **Refine Based on Usage Patterns**
  - Action: Analyze actual AI conversations for pattern gaps
  - Identify: Repeated questions or corrections indicate missing guidance
  - Update: Add patterns for frequently encountered scenarios
  - Schedule: Monthly pattern analysis

---

## 🎯 QUICK WINS (Can Complete Anytime)

- [ ] **Add PR Template**
  - Location: `docs/hybrid/go/.github/pull_request_template.md`
  - Include: Checklist (tests, docs, breaking changes), description format
  - Reference in: Core CLAUDE.md workflow section

- [ ] **Add Issue Templates**
  - Location: `docs/hybrid/go/.github/ISSUE_TEMPLATE/`
  - Include: Bug report, feature request, documentation update templates
  - Reference in: Core CLAUDE.md contribution section

- [ ] **Create `.gitignore` Template**
  - Location: `docs/hybrid/go/.claude/configs/gitignore.md`
  - Include: Comprehensive Go .gitignore with IDE files, build artifacts, env files
  - Example: Complete .gitignore for Go projects with comments

- [ ] **Add VS Code Settings**
  - Location: `docs/hybrid/go/.claude/configs/vscode.md`
  - Include: Recommended extensions, settings.json for Go, launch.json for debugging
  - Example: Complete VS Code setup for Go development

- [ ] **Create Dependency Update Guide**
  - Location: `docs/hybrid/go/.claude/guides/dependencies.md`
  - Include: How to update deps, breaking change handling, security updates
  - Process: go get -u, testing strategy, rollback procedures

---

## 📝 IMPLEMENTATION INSTRUCTIONS FOR AI AGENT

### When Creating New Pattern Files:

1. **Read existing files first** to understand style and structure
2. **Follow the pattern**: Introduction → Core Concepts → Examples → Best Practices → Anti-patterns
3. **Use code fences** with language specification (```go, ```bash, etc.)
4. **Include ✅ DO and ❌ DON'T sections** for clarity
5. **Add file references** to core CLAUDE.md in appropriate sections
6. **Keep examples realistic** - working code that could be copy-pasted
7. **Add context comments** in code examples to explain why, not just what

### When Adding to Existing Files:

1. **Read the entire file first** to understand current coverage
2. **Find the logical insertion point** - group related patterns together
3. **Maintain consistent formatting** with existing content
4. **Update table of contents** if file has one
5. **Cross-reference** with other relevant pattern files
6. **Preserve the tone** - instructional but concise

### When Creating Configuration Files:

1. **Provide complete, working examples** - not snippets
2. **Include comments explaining** each section
3. **Show both basic and advanced configurations**
4. **Add troubleshooting section** for common issues
5. **Reference official documentation** for deeper learning
6. **Include validation steps** to verify configuration works

### Quality Checklist for All Additions:

- [ ] Code examples are complete and functional
- [ ] Go idioms and best practices followed
- [ ] Security considerations addressed
- [ ] Error handling demonstrated
- [ ] Performance implications noted
- [ ] Testing approach shown (if applicable)
- [ ] Links to external resources provided
- [ ] Cross-references to related patterns added

---

## 🔄 COMPLETION TRACKING

**Status Legend:**
- ⬜ Not Started
- 🟦 In Progress
- ✅ Completed
- ⏸️ Blocked/On Hold

**Progress Summary:**
- High Priority: 6/12 completed (50%)
- Medium Priority: 8/8 completed (100%) ✅
- Low Priority - Additional Patterns: 3/3 completed (100%) ✅
- Low Priority - Operational Guides: 0/3 completed (0%)
- Low Priority - Tool-Specific Configurations: 2/2 completed (100%) ✅
- Low Priority - Advanced Topics: 0/2 completed (0%)
- Quick Wins: 0/5 completed (0%)

**Last Updated:** 2025-09-23
**Next Review:** Kubernetes, Crossplane, and Chainsaw testing patterns

---

*This TODO list is a living document. Update it as items are completed and new gaps are identified.*
