# Research Artifact Restructuring Guidelines

## Document Metadata
- **Purpose:** Guide AI-assisted migration of monolithic research artifacts to 2-part split (Business + Implementation)
- **Date:** 2025-10-10
- **Version:** 1.0
- **Target Audience:** AI assistants performing restructuring, Human reviewers validating migration

---

## Overview

This document provides instructions for restructuring existing comprehensive research artifacts (created with `research-generator.xml` and `research-artifact-template.md`) into the new 2-part split:

1. **Business Research**: Market analysis, user needs, competitive positioning, strategic recommendations
2. **Implementation Research**: Architecture, technology stack, code patterns, implementation pitfalls

### Why Split?

**Problem:** Loading comprehensive research (1200+ lines) for every SDLC artifact creation wastes context and buries relevant information.

**Solution:**
- Business-phase artifacts (Product Vision, Epics, PRDs) load Business Research only
- Implementation-phase artifacts (Backlog Stories, ADRs, Tech Specs) load Implementation Research only
- PRDs (bridge artifact) load BOTH for complete context

---

## File Inputs & Outputs

### Input (Existing Monolithic Research)
- Path pattern: `docs/research/[domain]/[Product]_research_report.md`
- Example: `docs/research/backlog/Backlog_Solution_Implementation_Guidelines_v2.md`

### Outputs (Split Research)
- **Business Research**: `docs/research/[domain]/[Product]_business_research.md`
- **Implementation Research**: `docs/research/[domain]/[Product]_implementation_research.md`

---

## Section Mapping Strategy

### Monolithic Research Structure (Original)

```
1. Problem Space Analysis
2. Market & Competitive Landscape
3. Gap Analysis
4. Product Capabilities Recommendations
5. Architecture & Technology Stack Recommendations
6. Implementation Pitfalls & Anti-Patterns
7. Strategic Recommendations
8. Areas for Further Research
9. Conclusion
Appendices (Product-specific, Examples, Resources)
References
```

### Split Mapping

| Original Section | Business Research | Implementation Research | Notes |
|-----------------|-------------------|-------------------------|-------|
| **1. Problem Space** | ✅ Full section | ⚠️ Brief 1-2 paragraph summary | Business gets full user pain point analysis; Implementation gets just enough context |
| **2. Market & Competitive** | ✅ Full section (business focus) | ✅ Partial (tech stack focus) | Business: Market segments, value props, business models. Implementation: Technology stacks, architecture patterns |
| **3. Gap Analysis** | ✅ Market gaps, UX gaps | ✅ Technical gaps, architecture gaps | **Split by lens**: Business sees unmet user needs; Implementation sees performance/architecture limitations |
| **4. Capabilities** | ✅ Strategic capabilities (WHAT/WHY) | ✅ Technical capabilities (HOW) | **Split by abstraction level**: Business describes user value; Implementation provides code examples |
| **5. Architecture & Tech Stack** | ❌ Exclude | ✅ Full section | Pure implementation content |
| **6. Pitfalls** | ❌ Exclude | ✅ Full section | Pure implementation content |
| **7. Strategic Recommendations** | ✅ Business focus (positioning, roadmap, GTM) | ✅ Technical focus (build/buy, tech evolution) | **Split by domain**: Business = market strategy; Implementation = technical strategy |
| **8. Further Research** | ✅ Business topics | ✅ Technical topics | Separate by domain |
| **9. Conclusion** | ✅ Business synthesis | ✅ Technical synthesis | Rewrite for each audience |
| **Appendices** | ✅ User personas, market sizing | ✅ Code examples, benchmarks, tech resources | Split by content type |
| **References** | ✅ Business citations subset | ✅ Technical citations subset | Each gets only relevant citations |

---

## Detailed Restructuring Instructions

### Step 1: Analyze Original Research

Before splitting, understand the structure:

1. **Read entire document** to understand scope and depth
2. **Identify section boundaries** (which content belongs to which phase)
3. **Map citations** (which footnotes are business vs technical)
4. **Note overlaps** (content that appears in both with different lens)

### Step 2: Extract Business Research

**Target Template:** `prompts/templates/business_research_template.md`

#### Section 1: Problem Space Analysis
**Extract:**
- Current state, pain points (user perspective)
- Impact if not solved (business impact, user impact)
- Evolution of problem (market trends, user behavior changes)

**Transform:**
- Remove technical details (e.g., "PostgreSQL fails at graph traversal")
- Keep user pain points (e.g., "Teams lose time manually tracking dependencies")
- Keep business impact (e.g., "Projects miss deadlines due to hidden blockers")

**Example Transformation:**
```
ORIGINAL:
"Traditional relational databases struggle with recursive JOIN operations for deep relationship chains. PostgreSQL requires N chained JOINs for N-level traversal, causing exponential performance degradation.[^11]"

BUSINESS VERSION:
"Current project management tools fail to visualize complex project dependencies, forcing teams to manually track blockers across disconnected systems. This causes delays when critical tasks are held up by hidden dependencies.[^user_review_citation]"

IMPLEMENTATION VERSION:
"Relational databases (PostgreSQL, MySQL) suffer exponential performance degradation for deep relationship traversal due to N chained JOINs. Graph databases solve this with index-free adjacency for constant-time traversal.[^11]"
```

#### Section 2: Market & Competitive Landscape

**Extract (Business Focus):**
- Market segmentation (by business model, target audience, value proposition)
- Competitive value propositions (what problems they solve)
- Business models (pricing, open-source vs commercial)
- User feedback (reviews, satisfaction, complaints)
- Target markets (company sizes, industries)

**Exclude from Business:**
- Technology stacks (move to Implementation)
- Architecture patterns (move to Implementation)
- Performance benchmarks (move to Implementation)

**Example:**
```
BUSINESS VERSION (Keep):
"**Atlassian Jira**
- Target Market: Enterprise software teams (500+ employees), IT service management
- Value Proposition: Comprehensive work management with deep Atlassian ecosystem integration
- Strengths: 3,000+ marketplace apps, enterprise readiness (SSO, compliance)
- Weaknesses: Steep learning curve, complexity overhead for small teams
- Business Model: SaaS subscription (Free, Standard, Premium, Enterprise)"

IMPLEMENTATION VERSION (Move here):
"**Atlassian Jira**
- Technology Stack: Java-based proprietary backend, supports PostgreSQL/MySQL/Oracle
- API: REST API v2/v3 with OAuth 2.0
- Architecture: Monolithic with plugin extensibility
- Performance: Query performance degrades with 100K+ issues (complex JQL)[^citation]"
```

#### Section 3: Gap Analysis (Split by Lens)

**Business Research Gets:**
- **Market Gaps**: Unmet user needs, underserved segments
- **UX Gaps**: User friction, adoption barriers, workflow pain points
- **Integration Gaps** (user perspective): Missing tool connections, manual workflows

**Example:**
```
BUSINESS VERSION:
**Gap: AI/ML Workflow Support**
- **Description**: Product teams building AI products lack tools to track ML experiments and dataset versions within their backlog
- **User Impact**: Data scientists use separate tools (MLflow), fragmenting context
- **Business Opportunity**: Capture fastest-growing market segment (AI-native companies)
```

**Implementation Research Gets:**
- **Technical Gaps**: Performance limitations, scalability constraints
- **Architecture Gaps**: Missing architectural patterns, event-driven limitations
- **Integration Gaps** (technical perspective): API design, webhook implementation

**Example:**
```
IMPLEMENTATION VERSION:
**Gap: Graph Query Performance at Scale**
- **Description**: Relational databases exhibit exponential performance degradation for deep relationship traversal (N chained JOINs for N-level depth)[^11]
- **Technical Impact**: Complex dependency queries unusable at 10K+ artifacts (multi-second latency)
- **Solution**: Neo4j with index-free adjacency for constant-time traversal[^42]
- **Implementation**: [Cypher query code example]
```

#### Section 4: Capabilities (Split by Abstraction Level)

**Business Research Gets (Strategic Capabilities):**
- **Description**: What capability does from USER perspective
- **User Value**: Why users need it, what problem it solves
- **Priority**: Must-have / Should-have / Nice-to-have
- **Success Criteria**: User adoption metrics, workflow improvements

**NO CODE EXAMPLES, NO TECHNOLOGY NAMES**

**Example:**
```
BUSINESS VERSION:
**Capability: Real-Time Dependency Visualization**
- **Description**: Users can view all project dependencies as an interactive graph showing how delays ripple through features
- **User Value**: Product managers instantly identify at-risk features without manually traversing links
- **Justification**: 35% of user reviews request better dependency tracking[^citation]
- **Priority**: Should-have (V1 differentiator)
- **Success Criteria**: 70% of users managing >20 tasks use visualization weekly
```

**Implementation Research Gets (Technical Capabilities):**
- **Implementation Approach**: Algorithm, data structure, architecture
- **Technology Requirements**: Specific technologies (Neo4j, GraphQL, etc.)
- **Code Examples**: Complete, runnable code
- **Performance Considerations**: Complexity, optimization strategies
- **Testing Strategy**: How to test this capability

**Example:**
```
IMPLEMENTATION VERSION:
**Capability: Graph-Based Dependency Traversal**
- **Implementation**: Cypher queries on Neo4j graph database
- **Data Model**:
  ```cypher
  (task:Task)-[:BLOCKS]->(dependent:Task)
  (task)-[:CHILD_OF]->(epic:Epic)
  ```
- **Query Pattern**:
  ```cypher
  MATCH (task:Task {id: $taskId})-[:BLOCKS*1..5]->(dependent)-[:CHILD_OF*]->(epic:Epic)
  RETURN DISTINCT epic.id, epic.title
  ```
- **Performance**: O(1) traversal per relationship (index-free adjacency)[^11]
- **Testing**: [Test code example with Neo4j Testcontainers]
```

#### Section 5: Architecture & Tech Stack
**Destination:** ✅ Implementation Research ONLY

**Action:** Move entire section verbatim (no transformation needed)

#### Section 6: Pitfalls & Anti-Patterns
**Destination:** ✅ Implementation Research ONLY

**Action:** Move entire section verbatim

#### Section 7: Strategic Recommendations (Split by Domain)

**Business Research Gets:**
- Market Positioning
- Feature Prioritization (MVP roadmap)
- Business Model & Monetization
- Go-to-Market Strategy
- Roadmap Phases (business perspective)
- Risk Analysis (market/competitive/adoption risks)

**Implementation Research Gets:**
- Build vs Buy Decisions (technical perspective)
- Technology Evolution Path (MVP → V1 → V2 tech choices)
- Open Source Strategy (licensing, contribution guidelines - technical aspects)

#### Section 8: Further Research (Split by Domain)

**Business Research:** Market validation, persona refinement, competitive intelligence

**Implementation Research:** Technology benchmarks, performance testing, framework evaluation

#### Section 9: Conclusion (Rewrite for Each Audience)

**Business:** Synthesize market opportunity, strategic direction, critical success factors

**Implementation:** Synthesize technical approach, architecture decisions, implementation priorities

#### Appendices (Split by Content Type)

**Business Research:**
- User Personas (detailed)
- Competitive Intelligence Summary (table)
- Market Sizing & Opportunity Analysis

**Implementation Research:**
- Code Examples & Reference Implementations
- Performance Benchmarks
- Additional Technical Resources

#### References (Split by Relevance)

**Business Research:** Subset of citations used in business sections

**Implementation Research:** Subset of citations used in implementation sections

**Note:** Some citations may appear in both (e.g., product documentation cited for both features and tech stack)

---

### Step 3: Quality Validation

After splitting, validate each research artifact:

#### Business Research Checklist:
- [ ] No specific technology recommendations (no "use Neo4j", "implement OAuth 2.0")
- [ ] Capabilities described from user perspective (what/why, not how)
- [ ] No code examples
- [ ] Focus on market, users, strategy
- [ ] Language appropriate for product managers/executives
- [ ] All citations relevant to business claims

#### Implementation Research Checklist:
- [ ] Abundant code examples (20+)
- [ ] Specific technology versions and choices
- [ ] Performance metrics specified (p99 < 200ms, not "fast")
- [ ] Architecture diagrams or clear descriptions
- [ ] Security/observability/testing patterns with code
- [ ] All citations relevant to technical claims

---

## Example: Full Section Transformation

### Original Monolithic Section (Gap Analysis):

```markdown
### 3.1 Market Gaps

**Gap 1: Native AI/ML Workflow Support**
- **Description:** None of the analyzed platforms provide native support for ML artifacts. Teams use custom fields (losing type safety) or separate systems (MLflow) that fragment context.[^5]
- **User Impact:** Data scientists cannot track experiments and datasets within their product backlog. Product managers lack visibility into ML-specific success criteria.
- **Current Workarounds:** Hybrid systems (Jira + MLflow + spreadsheets), creating sync overhead.[^6]
- **Opportunity:** Build native MLExperiment, Dataset, EthicalReview artifact types with dedicated UI.

### 3.2 Technical Gaps

**Technical Gap 1: Graph Query Performance**
- **Description:** Relational databases (PostgreSQL, MySQL) suffer exponential degradation for deep relationship traversal.[^11]
- **Why Existing Solutions Fail:** N chained JOINs for N-level traversal. Jira users report multi-second query times.[^11]
- **Solution Approach:** Neo4j with index-free adjacency for constant-time traversal.[^42]
- **Implementation:**
  ```cypher
  MATCH (task:Task {id: 'TASK-1'})-[:BLOCKS*1..5]->(dep)-[:CHILD_OF*]->(epic:Epic)
  RETURN DISTINCT epic
  ```
```

### Business Research Version:

```markdown
### 3.1 Market Gaps

**Gap 1: Native AI/ML Workflow Support**
- **Description:** Product teams building AI products lack tools to track ML experiments, dataset versions, and model performance within their product backlog
- **User Impact:** Data scientists must use separate tools (MLflow, Weights & Biases), fragmenting the product development context. Product managers cannot see ML-specific success criteria (model accuracy, bias metrics) when prioritizing work.[^5][^6]
- **Market Evidence:** User interviews and community discussions show teams maintaining hybrid tracking systems (Jira for features + MLflow for experiments + spreadsheets for datasets), creating synchronization overhead and reducing traceability.[^6]
- **Business Opportunity:** First-class ML artifact support differentiates platform for AI-native companies (fastest-growing market segment). Capture early adopters in emerging AI product development market.
- **Strategic Value:** Addresses underserved segment with unique needs that general project management tools don't support
```

### Implementation Research Version:

```markdown
### 3.1 Technical Gaps

**Gap 1: Graph Query Performance at Scale**
- **Description:** Relational databases (PostgreSQL, MySQL, SQL Server) exhibit exponential performance degradation when traversing deep relationship chains—exactly what's needed for dependency analysis and impact assessment.[^11][^12]
- **Technical Impact:** As backlogs grow to tens of thousands of items with complex interdependencies, queries like "find all work items 3+ levels deep that depend on this task" become prohibitively slow. Jira users report multi-second query times for complex JQL with issue links.[^11]
- **Why Existing Solutions Fail:** Relational databases store relationships in separate join tables. Traversing a relationship requires a JOIN operation. Traversing N levels deep requires N chained JOINs, which grows exponentially in complexity and execution time.[^11] Query planners struggle to optimize deep recursive queries.
- **Solution Approach:** Adopt native graph database (Neo4j) for artifact and relationship data model. Graph databases use "index-free adjacency"—relationships are physical pointers, making traversal a constant-time operation regardless of graph size.[^11][^42]
- **Implementation Pattern:**
  ```cypher
  // Cypher query: Find all Epics impacted by a delayed task
  MATCH (task:Task {id: 'TASK-123'})-[:BLOCKS*1..5]->(dependent)
    -[:CHILD_OF*]->(epic:Epic)
  RETURN DISTINCT epic.id, epic.title, epic.targetDate
  ORDER BY epic.targetDate
  ```
- **Performance Comparison:**
  - PostgreSQL (recursive CTE): 2000ms for 5-hop traversal on 10K node graph
  - Neo4j (index-free adjacency): 100ms for same query[^11]
- **Trade-offs:**
  - Advantage: 10-100x faster for graph queries
  - Trade-off: Team learning curve for Cypher query language
  - Trade-off: Operational complexity (managing graph database alongside relational)
```

---

## Automation Workflow

### For AI Assistants Performing Migration:

1. **Load Original Research**: Read existing monolithic research artifact
2. **Load Templates**: Read `business_research_template.md` and `implementation_research_template.md`
3. **Load These Guidelines**: Use this document for transformation rules
4. **Execute Split**:
   - Create Business Research following business template
   - Create Implementation Research following implementation template
   - Apply transformation rules from this document
5. **Validate**: Run quality checklists
6. **Save Outputs**: Write to `[Product]_business_research.md` and `[Product]_implementation_research.md`

### Command Pattern (If Integrated):

```bash
/restructure-research docs/research/backlog/Backlog_Solution_Implementation_Guidelines_v2.md
```

**Expected Output:**
- `docs/research/backlog/Backlog_Solution_business_research.md`
- `docs/research/backlog/Backlog_Solution_implementation_research.md`

---

## Common Pitfalls to Avoid

### Pitfall 1: Technology Leakage into Business Research
**Wrong:**
> "The system should use Neo4j graph database for dependency tracking to achieve p99 latency < 100ms."

**Right (Business):**
> "The system should enable real-time visualization of complex project dependencies, allowing product managers to instantly see how delays ripple through features."

**Right (Implementation):**
> "Use Neo4j 5.12+ for artifact relationship storage. Benchmark: p99 < 100ms for 5-hop traversal on 10K node graph.[^citation]"

### Pitfall 2: Business Jargon in Implementation Research
**Wrong:**
> "This architecture enables market differentiation through superior user experience and competitive positioning in the enterprise segment."

**Right (Business):**
> [Above statement belongs in Business Research]

**Right (Implementation):**
> "This architecture (event-driven microservices) enables horizontal scaling to support 10K+ concurrent users with p99 API latency < 200ms. Trade-off: Increased operational complexity vs monolithic approach."

### Pitfall 3: Incomplete Code Examples in Implementation
**Wrong:**
> "Implement authentication using OAuth 2.0 with proper security."

**Right:**
```python
# OAuth 2.0 authentication implementation
from authlib.integrations.flask_client import OAuth

oauth = OAuth(app)
oauth.register(
    'auth0',
    client_id=os.getenv('AUTH0_CLIENT_ID'),
    client_secret=os.getenv('AUTH0_CLIENT_SECRET'),
    server_metadata_url=f'https://{AUTH0_DOMAIN}/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'}
)

@app.route('/login')
def login():
    redirect_uri = url_for('callback', _external=True)
    return oauth.auth0.authorize_redirect(redirect_uri)
```

### Pitfall 4: Losing Citations During Split
**Problem:** Forgetting to include relevant citations in split versions

**Solution:**
- Business Research includes all citations used in business sections
- Implementation Research includes all citations used in implementation sections
- Some citations appear in both if used in both contexts

---

## Post-Migration Validation

After migration, verify:

### Structural Validation:
- [ ] Both files follow correct templates
- [ ] All template sections present
- [ ] Metadata complete

### Content Validation:
- [ ] Business Research has no technology prescriptions
- [ ] Implementation Research has abundant code (20+ examples)
- [ ] Capabilities split correctly (user value vs technical approach)
- [ ] Gap analysis split by lens (market vs technical)
- [ ] Strategic recommendations split by domain (business vs technical)

### Citation Validation:
- [ ] Every claim in Business Research has citation
- [ ] Every claim in Implementation Research has citation
- [ ] All URLs valid and accessible
- [ ] References sections complete

### Completeness Validation:
- [ ] No content lost (everything from original appears in one or both splits)
- [ ] No duplication (same content doesn't appear verbatim in both unless intentional overlap)
- [ ] Traceability maintained (can trace back to original sections)

---

## Appendix: Quick Reference

### Business Research = WHAT, WHY, WHO, WHEN
- Market opportunity
- User needs and pain points
- Competitive positioning
- Product capabilities (user perspective)
- Strategic roadmap
- Go-to-market strategy

**Audience:** Product managers, executives, sales, marketing

**NO:** Technology names, code, architecture diagrams, performance metrics

---

### Implementation Research = HOW, WITH WHAT, WHAT PITFALLS
- Architecture patterns
- Technology stack (specific products, versions)
- Implementation patterns (with code)
- Performance targets (specific metrics)
- Security/observability/testing (with code)
- Pitfalls and anti-patterns

**Audience:** Developers, architects, technical leads

**NO:** Market analysis, user personas, business strategy

---

**End of Restructuring Guidelines**
