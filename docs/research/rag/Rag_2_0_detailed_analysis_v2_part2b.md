## 5. Architecture & Technology Stack Recommendations

### 5.1 Overall Architecture

**Recommended Architecture Pattern: Microservices with Serverless Gateway**

For software engineering knowledge base systems scaling from 10 to 200 users, a hybrid architecture combining microservices for core components with serverless entry points provides optimal balance between flexibility, cost, and operational complexity.[^143]

**High-Level System Design:**

```
┌─────────────────────────────────────────────────────────────────┐
│                     Client Applications Layer                     │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│   │ Web UI   │  │   CLI    │  │ IDE Ext  │  │   API    │       │
│   └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘       │
└─────────┼─────────────┼─────────────┼─────────────┼─────────────┘
          │             │             │             │
          └─────────────┴─────────────┴─────────────┘
                              │
          ┌───────────────────▼───────────────────┐
          │    API Gateway / Load Balancer        │
          │  (Authentication, Rate Limiting)      │
          └───────────────────┬───────────────────┘
                              │
          ┌───────────────────▼───────────────────┐
          │      Orchestration Layer              │
          │   (Query Router, Agent Controller)    │
          └───────────┬───────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼────┐  ┌─────▼─────┐  ┌───▼──────┐
│ Retrieval  │  │Generation │  │ Indexing │
│  Service   │  │  Service  │  │ Service  │
└───────┬────┘  └─────┬─────┘  └───┬──────┘
        │             │             │
        │      ┌──────▼──────┐      │
        │      │   Cache     │      │
        │      │  (Redis)    │      │
        │      └─────────────┘      │
        │                           │
┌───────▼─────────────┐  ┌──────────▼──────────┐
│   Vector Database   │  │  Graph Database     │
│  (Qdrant/Pinecone)  │  │    (Neo4j)          │
└─────────────────────┘  └─────────────────────┘
        │                           │
        └────────────┬──────────────┘
                     │
          ┌──────────▼──────────┐
          │  Document Storage   │
          │    (S3/Blob)        │
          └─────────────────────┘
```

**Key Components:**

1. **API Gateway Layer:**
   - **Responsibility:** Authentication, authorization, rate limiting, request routing, SSL termination
   - **Rationale:** Centralized security and traffic management prevents duplicate logic across services. Serverless gateways (AWS API Gateway, Azure API Management) provide auto-scaling with pay-per-request pricing for variable workloads.[^144]

2. **Orchestration Layer:**
   - **Responsibility:** Query complexity assessment, adaptive routing (simple → no retrieval, moderate → single-step, complex → multi-step), agent coordination for multi-hop reasoning
   - **Rationale:** Separates business logic from retrieval/generation, enabling independent scaling and easier testing. Implements Adaptive RAG patterns that reduce unnecessary retrievals by 29%.[^145]

3. **Retrieval Service:**
   - **Responsibility:** Hybrid search (vector + BM25), two-stage retrieval with reranking, parent-child chunk retrieval, access control filtering, query caching
   - **Rationale:** Dedicated service scales independently based on query load. Stateless design enables horizontal scaling. Redis cache provides 5-10x speedup for frequent queries.[^146]

4. **Generation Service:**
   - **Responsibility:** LLM API calls with prompt engineering, context assembly, streaming responses, hallucination detection, PII filtering
   - **Rationale:** Isolates expensive LLM calls for separate scaling, timeout management, and cost monitoring. Supports multiple LLM providers (OpenAI, Anthropic, self-hosted) through abstraction layer.[^147]

5. **Indexing Service:**
   - **Responsibility:** Document ingestion from data sources (Confluence, GitHub, Jira), chunking with context-aware strategies, embedding generation, metadata extraction, incremental updates
   - **Rationale:** Background processing decoupled from query path prevents user-facing latency. Event-driven architecture triggers reindexing on document changes via webhooks.[^148]

6. **Vector Database:**
   - **Responsibility:** High-performance similarity search, metadata filtering, namespace isolation per product, hybrid search support
   - **Rationale:** Purpose-built for sub-100ms p95 latency at million-vector scale. Managed services (Pinecone, Qdrant Cloud) eliminate operational overhead for teams prioritizing development velocity.[^149]

7. **Graph Database:**
   - **Responsibility:** Hierarchical relationship traversal (product → epic → PRD → user story → task), dependency graph queries, author/contributor relationships, temporal relationship tracking
   - **Rationale:** Vector databases excel at semantic similarity but struggle with structured relationships. Graph databases reason over connections efficiently. Hybrid VectorRAG + GraphRAG achieves higher accuracy than either alone.[^150]

**Data Flow:**

1. **Query Processing:**
   - User query → API Gateway (auth) → Orchestration Layer (complexity assessment) → Retrieval Service (hybrid search + reranking) → access control filtering → Generation Service (LLM with context) → streaming response to client
   - **Latency Budget:** 500ms-1s retrieval + 1-2s generation = <3s total[^151]

2. **Indexing Pipeline:**
   - Webhook trigger (GitHub push, Confluence update) → Indexing Service → document fetch → chunking → embedding generation → metadata extraction → vector DB write + graph DB write → cache invalidation
   - **Throughput:** Batch processing with parallelization for bulk imports, incremental updates for real-time changes[^152]

3. **Cache Flow:**
   - Retrieval Service checks Redis cache for query embedding → cache hit returns results immediately (5-10x faster) → cache miss executes full retrieval + caches results with TTL (1-24 hours based on content freshness requirements)[^153]

**Architecture Trade-offs:**

**Advantages:**
1. **Independent Scaling:** Retrieval service scales based on query volume, indexing service scales during bulk imports, generation service scales based on LLM throughput
2. **Technology Flexibility:** Each service uses optimal technology stack (Python for ML/AI, Go for performance-critical retrieval, Node.js for API gateway)
3. **Fault Isolation:** Indexing failures don't impact query serving, generation timeouts fall back to retrieved documents with citations
4. **Cost Optimization:** Serverless components (API Gateway, indexing triggers) scale to zero during idle periods

**Trade-offs:**
1. **Operational Complexity:** Multiple services require container orchestration (Kubernetes), monitoring across distributed traces, and service mesh for inter-service communication
2. **Network Latency:** Inter-service calls add 10-50ms per hop. Mitigated by co-locating services in same availability zone and using gRPC for internal communication
3. **Eventual Consistency:** Async indexing means newly committed documents take 1-5 minutes to become searchable. Acceptable for most knowledge base use cases but may require synchronous indexing for critical updates

**Scaling Progression:**

**Small Deployment (10-50 users):**
- Serverless architecture with AWS Lambda/Vercel functions for orchestration and generation
- Managed vector database (Pinecone Starter $70/month or Qdrant Cloud $100/month)
- OpenAI/Anthropic APIs for generation (no self-hosted LLMs)
- Single-region deployment
- **Monthly Cost:** $500-2,000[^154]

**Medium Deployment (50-100 users):**
- Containerized services on Kubernetes (AWS EKS, GCP GKE, Azure AKS)
- Managed vector database upgraded tier (Pinecone Standard, Qdrant Cloud scaled)
- Potentially self-hosted LLMs (vLLM serving Llama 3.3 70B) for cost optimization on high query volume
- Redis cluster for caching
- Multi-AZ deployment within single region
- **Monthly Cost:** $2,000-10,000[^155]

**Large Deployment (100-200+ users):**
- Multi-region Kubernetes clusters with global load balancing
- Distributed vector database (Milvus cluster or Pinecone Enterprise with regional replicas)
- Dedicated LLM serving infrastructure (vLLM on GPU instances, TensorRT optimization)
- Comprehensive monitoring (LangSmith, Datadog, Arize Phoenix)
- CI/CD pipelines with blue-green deployment
- Multi-region active-active deployment
- **Monthly Cost:** $10,000-50,000+[^156]

---

### 5.2 Technology Stack

**Programming Language: Python (Primary)**

- **Justification:** Dominant ecosystem for AI/ML with mature libraries (LlamaIndex, LangChain, Transformers, sentence-transformers), excellent embedding and vector database client support, rapid prototyping with strong typing via type hints, extensive community and documentation for RAG patterns.[^157]
- **Alternatives Considered:**
  - **TypeScript/Node.js:** Strong for API layers and frontend, weak AI/ML ecosystem. Used for API Gateway layer but not core RAG services.
  - **Rust:** Exceptional performance for vector databases (Qdrant implemented in Rust), steep learning curve and smaller AI/ML library ecosystem. Used by infrastructure components but not application layer.
  - **Go:** Excellent concurrency and performance, limited AI/ML libraries. Potential for performance-critical retrieval service after prototyping in Python.

**Example Code:**
```python
# Type-hinted Python for RAG pipeline
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Document:
    id: str
    content: str
    metadata: dict[str, any]
    score: float

async def hybrid_retrieval(
    query: str,
    collection: str,
    top_k: int = 10,
    filters: Optional[dict] = None
) -> List[Document]:
    """
    Execute hybrid search with type safety

    Args:
        query: User query string
        collection: Vector database collection name
        top_k: Number of results to return
        filters: Metadata filters for pre-filtering

    Returns:
        List of Document objects sorted by relevance
    """
    # Implementation with strong typing ensures correctness
    pass
```

**Backend Framework: FastAPI**

- **Recommended Framework:** FastAPI for Python services
- **Justification:**
  - Async/await support for concurrent LLM API calls improves throughput by 3-10x over synchronous frameworks
  - Automatic OpenAPI documentation generation creates interactive API docs
  - Built-in request validation via Pydantic models prevents malformed queries
  - WebSocket support enables streaming responses for real-time user experience
  - Performance within 15% of Go/Rust while maintaining Python's AI/ML ecosystem[^158]
- **Key Features Utilized:**
  - Dependency injection for database clients, authentication, rate limiting
  - Background tasks for async indexing triggers
  - Streaming responses for generation (reduces perceived latency by 40-60%)

**Example Server Setup:**
```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio

app = FastAPI(
    title="RAG Knowledge Base API",
    version="2.0.0",
    docs_url="/api/docs"
)

class QueryRequest(BaseModel):
    query: str
    top_k: int = 10
    stream: bool = True

@app.post("/api/v1/query")
async def query_knowledge_base(
    request: QueryRequest,
    user_id: str = Depends(verify_auth_token)
):
    """Execute RAG query with streaming response"""

    # Retrieve documents (fast, ~500ms)
    documents = await retrieval_service.search(
        query=request.query,
        top_k=request.top_k,
        user_id=user_id
    )

    # Check access control
    allowed_docs = [d for d in documents if check_access(user_id, d.id)]

    if request.stream:
        # Stream generation token-by-token
        async def generate_stream():
            async for chunk in generation_service.generate_stream(
                query=request.query,
                context=allowed_docs
            ):
                yield f"data: {chunk}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream"
        )
    else:
        # Standard response
        answer = await generation_service.generate(
            query=request.query,
            context=allowed_docs
        )
        return {"answer": answer, "sources": allowed_docs}

@app.get("/health")
async def health_check():
    """Health check for load balancer"""
    # Verify critical dependencies
    vector_db_healthy = await check_vector_db()
    llm_api_healthy = await check_llm_api()

    if not (vector_db_healthy and llm_api_healthy):
        raise HTTPException(status_code=503, detail="Service degraded")

    return {"status": "healthy"}
```

**Database & Storage:**

**Primary Vector Database: Qdrant (Recommended) or Pinecone (Alternative)**

**Qdrant:**
- **Justification:** Best-in-class performance with sub-10ms p50 latency, Rust implementation provides memory safety and performance, advanced pre-filtering with cardinality-based strategy switching (brute force for selective filters, HNSW for broad filters), open-source with commercial cloud option, excellent cost-to-performance ratio at $1,000-1,500/month for 50M vectors (vs. Pinecone $3,241/month).[^159]
- **Schema Design Considerations:**
  - Collections per product for namespace isolation
  - Payload (metadata) optimized with indexed fields for frequent filters (document_type, access_level, created_date)
  - Vector dimensions: 768-1024 with int8 quantization (4x compression, <2% accuracy loss)

**Pinecone:**
- **Justification:** Fully-managed serverless with zero operational overhead, proven scale to billions of vectors with sub-100ms p95 latency, excellent developer experience with multi-language SDKs, enterprise SLAs with 99.9% uptime, automatic scaling without capacity planning. Premium pricing justified for teams prioritizing zero-ops.[^160]

**Graph Database: Neo4j (Recommended)**

- **Justification:** Native vector indexing (HNSW from v5.11+) enables GraphRAG combining semantic search with relationship traversal, mature Cypher query language for complex graph queries, active community and extensive documentation, Community Edition free (GPLv3) for development, AuraDB cloud from $65/month for production.[^161]
- **Schema Design:** Nodes represent documents (PRD, Epic, UserStory, TechSpec, Code), relationships capture hierarchies (PARENT_OF, IMPLEMENTS, DEPENDS_ON, AUTHORED_BY), properties store metadata with indexes on frequently-queried fields.

**Example Schema:**
```cypher
// Create document nodes with vector embeddings
CREATE (prd:PRD {
  id: 'PRD-123',
  title: 'User Authentication System',
  content: 'OAuth2.0 implementation...',
  embedding: [0.1, 0.2, ...],  // 1024-dimensional vector
  status: 'approved',
  created_date: datetime('2024-10-01'),
  owner: 'user:alice'
})

CREATE (story:UserStory {
  id: 'US-123-01',
  title: 'OAuth2 Login Flow',
  embedding: [...],
  story_points: 5
})

// Create relationships
CREATE (story)-[:IMPLEMENTS {created_date: datetime()}]->(prd)
CREATE (story)-[:DEPENDS_ON]->(other_story)

// Vector + Graph query combining semantic search with relationship traversal
CALL db.index.vector.queryNodes('embedding_index', 10, [0.1, 0.2, ...])
YIELD node, score
WHERE score > 0.8
MATCH (node)-[:IMPLEMENTS]->(prd:PRD)
RETURN node, prd, score
ORDER BY score DESC
```

**Document Storage: S3 / Azure Blob / Google Cloud Storage**

- **Justification:** Object storage for original documents (PDFs, DOCX, markdown files), versioning support tracks document history, lifecycle policies archive cold data to cheaper tiers (Glacier, Archive Storage), presigned URLs for secure access without exposing credentials, 99.999999999% durability guarantees data safety.[^162]

**Caching Layer: Redis**

- **Justification:** Sub-millisecond latency for frequent queries, supports complex data structures (strings, hashes, sorted sets) for embedding caches and result caches, TTL (time-to-live) expiration for automatic cache invalidation, Redis Cluster provides horizontal scaling for large deployments, persistence options (RDB snapshots, AOF logs) prevent cache cold-start after restarts.[^163]

**Use Cases:**
```python
import redis
import json
import hashlib

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Cache query embeddings (expensive to compute)
def get_cached_embedding(text: str) -> Optional[List[float]]:
    cache_key = f"embedding:{hashlib.md5(text.encode()).hexdigest()}"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    # Compute embedding
    embedding = embed_model.get_text_embedding(text)

    # Cache with 24-hour TTL
    redis_client.setex(cache_key, 86400, json.dumps(embedding))

    return embedding

# Cache retrieval results for frequent queries
def get_cached_results(query: str) -> Optional[List[Document]]:
    cache_key = f"results:{hashlib.md5(query.encode()).hexdigest()}"
    cached = redis_client.get(cache_key)

    if cached:
        return [Document(**d) for d in json.loads(cached)]

    # Execute retrieval
    results = hybrid_search_with_reranking(query)

    # Cache with 1-hour TTL for dynamic content
    redis_client.setex(cache_key, 3600, json.dumps([r.dict() for r in results]))

    return results
```

**Message Queue: Redis Streams or RabbitMQ**

- **Use Cases:** Document indexing job queue, webhook event processing, async notification delivery, dead letter queue for failed operations.[^164]
- **Redis Streams:** Simpler setup (reuses Redis infrastructure), sufficient for moderate throughput (<10,000 msgs/sec).
- **RabbitMQ:** Better for high throughput, complex routing, guaranteed delivery with acknowledgments, message durability.

**Infrastructure & Deployment:**

**Container Platform: Docker**
- Industry standard with extensive ecosystem, reproducible builds with multi-stage Dockerfiles reduce image size by 60-80%, Docker Compose for local development, compatibility with all major orchestrators.[^165]

**Orchestration: Kubernetes**
- **Justification:** De facto standard for container orchestration, declarative configuration with YAML manifests enables GitOps workflows, horizontal pod autoscaling based on CPU, memory, or custom metrics (QPS), rolling updates with zero downtime, self-healing through pod restarts and health checks, multi-cloud portability (AWS EKS, GCP GKE, Azure AKS).[^166]
- **Alternatives:** Docker Swarm (simpler but less ecosystem), AWS ECS (vendor lock-in), Nomad (smaller community).

**Example Deployment Configuration:**
```yaml
# Kubernetes deployment for retrieval service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: retrieval-service
  labels:
    app: rag-system
    component: retrieval
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rag-system
      component: retrieval
  template:
    metadata:
      labels:
        app: rag-system
        component: retrieval
    spec:
      containers:
      - name: retrieval
        image: rag-system/retrieval:v2.0.0
        ports:
        - containerPort: 8080
        env:
        - name: QDRANT_URL
          valueFrom:
            configMapKeyRef:
              name: rag-config
              key: qdrant_url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: rag-secrets
              key: redis_url
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
---
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: retrieval-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: retrieval-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
```

**CI/CD: GitHub Actions (Recommended)**

- **Justification:** Native integration with GitHub repositories, generous free tier (2,000 minutes/month), matrix builds for multi-platform testing, secrets management with encrypted variables, marketplace with 10,000+ pre-built actions, self-hosted runners for cost savings on high usage.[^167]
- **Pipeline Stages:** Lint (Ruff, Black) → Unit tests (pytest) → Integration tests → Build Docker images → Push to registry → Deploy to staging → Evaluation tests (RAGAS) → Deploy to production (blue-green)

**Example CI/CD Pipeline:**
```yaml
# .github/workflows/deploy.yml
name: Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: pytest tests/ --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Build Docker image
      run: docker build -t rag-system/retrieval:${{ github.sha }} .

    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push rag-system/retrieval:${{ github.sha }}

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    steps:
    - name: Deploy to staging
      run: |
        kubectl set image deployment/retrieval-service \
          retrieval=rag-system/retrieval:${{ github.sha }} \
          --namespace=staging

    - name: Run evaluation tests
      run: |
        python scripts/run_ragas_evaluation.py --environment staging

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to production
      run: |
        kubectl set image deployment/retrieval-service \
          retrieval=rag-system/retrieval:${{ github.sha }} \
          --namespace=production
```

---

### 5.3 Data Model & Schema Design

**Core Entities:**

A software engineering knowledge base system requires entities representing the document hierarchy, user/access control, and operational metadata.

**Entity 1: Document (Universal Base)**

Core fields shared across all document types:
- `id` (string, UUID): Unique identifier
- `document_type` (enum): PRD, Epic, UserStory, TechSpec, Code, Email, Ticket
- `title` (string): Human-readable title
- `content` (text): Full document content
- `summary` (text): LLM-generated summary (100-200 tokens)
- `embedding` (vector, 1024-dim): Semantic embedding for similarity search
- `created_date` (timestamp): Document creation time
- `modified_date` (timestamp): Last modification time
- `author` (string): User ID of creator
- `owner` (string): Current owner user ID
- `version` (integer): Version number for tracking changes
- `status` (enum): draft, review, approved, deprecated
- `source_url` (string): Link to original document
- `access_level` (enum): public, internal, confidential, restricted
- `department` (enum): engineering, product, design, sales
- `tags` (array[string]): Categorization tags

**Entity 2: ProductDocument (Extends Document)**

Product-specific documents (PRD, Epic, UserStory) add:
- `product_name` (string): Product identifier
- `epic_id` (string): Parent epic reference
- `release_version` (string): Target release (e.g., "v2.5.0")
- `priority` (enum): P0, P1, P2, P3
- `stakeholders` (array[string]): User IDs of stakeholders
- `target_date` (date): Planned completion date
- `dependencies` (array[string]): Document IDs of dependencies
- `feature_tags` (array[string]): Feature categorization
- `approval_status` (enum): pending, approved, rejected
- `story_points` (integer): Effort estimation (for user stories)

**Entity 3: TechnicalDocument (Extends Document)**

Technical specifications and code add:
- `component_name` (string): Component identifier
- `architecture_layer` (enum): backend, frontend, infrastructure, database
- `technology_stack` (array[string]): Technologies used (Python, React, PostgreSQL)
- `api_endpoints` (array[object]): API endpoint definitions
- `review_status` (enum): pending_review, approved, changes_requested
- `implementation_status` (enum): not_started, in_progress, completed
- `repository` (string): Git repository name
- `file_path` (string): Path within repository
- `language` (enum): python, javascript, go, rust, java
- `test_coverage` (float): Percentage (0.0-100.0)
- `last_commit_hash` (string): Git commit SHA

**Entity 4: Chunk (Document Fragment)**

Individual chunks for granular retrieval:
- `chunk_id` (string, UUID): Unique chunk identifier
- `document_id` (string): Parent document reference
- `parent_chunk_id` (string, nullable): Parent chunk for hierarchical chunking
- `content` (text): Chunk text content (200-1024 tokens)
- `embedding` (vector, 1024-dim): Chunk embedding
- `chunk_index` (integer): Position in document (0-indexed)
- `chunk_type` (enum): body, header, code_block, table, list
- `section_hierarchy` (array[string]): Section path (["Chapter 3", "Section 3.2"])
- `contextual_summary` (text): LLM-generated context (50-100 tokens)
- `prev_chunk_id` (string, nullable): Previous chunk for sequential reading
- `next_chunk_id` (string, nullable): Next chunk for sequential reading
- `metadata` (json): Inherited from parent document plus chunk-specific metadata

**Entity 5: User**

User accounts and access control:
- `user_id` (string, UUID): Unique identifier
- `email` (string): Email address
- `name` (string): Full name
- `role` (enum): admin, engineer, product_manager, viewer
- `groups` (array[string]): Group memberships (engineering, mobile_team, leadership)
- `access_level` (enum): restricted, internal, confidential, all
- `created_date` (timestamp)
- `last_login` (timestamp)
- `status` (enum): active, inactive, suspended

**Relationships:**

Critical relationships modeled explicitly in graph database:

1. **Document Hierarchy:**
   - `Product → Epic → PRD → UserStory → Task → TechSpec`
   - Relationship properties: `created_date`, `dependency_type` (required, optional, related)

2. **Implementation Relationships:**
   - `UserStory -[:IMPLEMENTS]-> PRD`
   - `TechSpec -[:SPECIFIES]-> UserStory`
   - `Code -[:IMPLEMENTS]-> TechSpec`

3. **Dependency Relationships:**
   - `Document -[:DEPENDS_ON]-> Document`
   - Properties: `dependency_type` (blocking, related), `status` (active, resolved)

4. **Authorship Relationships:**
   - `User -[:AUTHORED]-> Document`
   - `User -[:REVIEWED]-> Document`
   - `User -[:APPROVED]-> Document`
   - Properties: `timestamp`, `comment`

5. **Access Control Relationships:**
   - `User -[:CAN_READ]-> Document`
   - `User -[:CAN_WRITE]-> Document`
   - `Group -[:CAN_READ]-> Document`

**Schema Evolution Strategy:**

Production systems require non-breaking schema changes to avoid downtime.[^168]

**Backward-Compatible Changes:**
- **Adding Fields:** New optional fields default to null. Old code ignores unknown fields.
- **Adding Indexes:** Create concurrently without locking tables (`CREATE INDEX CONCURRENTLY` in PostgreSQL).
- **Adding Enum Values:** Append to enum definition. Old code treats unknown values as "other".

**Breaking Changes (Require Migration):**
- **Renaming Fields:** Create new field, copy data, deprecate old field, remove after transition period (3-6 months).
- **Changing Types:** Create new field with new type, migrate data with validation, switch references, remove old field.
- **Removing Fields:** Mark as deprecated for 2-3 versions before removal. Monitor usage logs to ensure no active queries.

**Example Migration Script:**
```python
# Alembic migration for adding story_points to UserStory
"""Add story_points field to user stories

Revision ID: 20241010_001
Revises: 20241009_003
Create Date: 2024-10-10 10:00:00
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add new optional field
    op.add_column(
        'documents',
        sa.Column('story_points', sa.Integer, nullable=True)
    )

    # Backfill default value for existing records
    op.execute(
        "UPDATE documents SET story_points = 5 "
        "WHERE document_type = 'UserStory' AND story_points IS NULL"
    )

    # Add index for filtering
    op.create_index(
        'idx_documents_story_points',
        'documents',
        ['story_points'],
        postgresql_where=sa.text("document_type = 'UserStory'")
    )

def downgrade():
    op.drop_index('idx_documents_story_points')
    op.drop_column('documents', 'story_points')
```

**Vector Database Schema (Qdrant):**

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

client = QdrantClient(url="http://localhost:6333")

# Create collection with optimized configuration
client.create_collection(
    collection_name="software_docs",
    vectors_config=VectorParams(
        size=1024,  # Voyage-3 embedding dimension
        distance=Distance.COSINE,
        on_disk=False  # Keep vectors in memory for speed
    ),
    optimizers_config={
        "default_segment_number": 5,
        "indexing_threshold": 20000,
    },
    # Enable payload indexing for fast filtering
    payload_schema={
        "document_type": PayloadSchemaType.KEYWORD,
        "access_level": PayloadSchemaType.KEYWORD,
        "created_date": PayloadSchemaType.DATETIME,
        "department": PayloadSchemaType.KEYWORD,
        "status": PayloadSchemaType.KEYWORD,
    }
)
```

---

### 5.4 Scalability Considerations

**Horizontal Scaling:**

RAG systems scale horizontally by adding more instances of stateless services.[^169]

**Stateless Design Patterns:**
1. **API Gateway:** Multiple instances behind load balancer (AWS ALB, NGINX). Session state stored in Redis, not process memory.
2. **Retrieval Service:** Stateless workers scale based on QPS. Each request independent. Connection pooling to vector database prevents connection exhaustion.
3. **Generation Service:** Stateless LLM API clients. Concurrent requests limited by rate limits (OpenAI: 10,000 RPM for Tier 4). Queue overflow requests.
4. **Indexing Service:** Stateless workers consume jobs from message queue (RabbitMQ, Redis Streams). Multiple workers process in parallel.

**Load Balancing Strategy:**
- **Round-robin** for API gateway (equal distribution)
- **Least connections** for generation service (expensive long-running LLM calls)
- **Consistent hashing** for cache queries (maximize cache hit rate)

**Scaling Triggers:**
```yaml
# Kubernetes HPA based on custom metrics
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: retrieval-service-hpa
spec:
  minReplicas: 3
  maxReplicas: 20
  metrics:
  # Scale on CPU (general load)
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  # Scale on custom metric (QPS)
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "500"
  # Scale on queue depth (indexing service)
  - type: External
    external:
      metric:
        name: rabbitmq_queue_depth
      target:
        type: AverageValue
        averageValue: "100"
```

**Vertical Scaling:**

Optimize resource utilization before adding instances.[^170]

**Resource Optimization Approaches:**
1. **Memory Profiling:** Identify memory leaks with `memory_profiler`, optimize large object allocations, use generators instead of lists for large datasets.
2. **CPU Optimization:** Profile with `cProfile`, vectorize operations with NumPy, use multiprocessing for CPU-bound tasks (embedding generation), enable JIT compilation with Numba for hot paths.
3. **I/O Optimization:** Connection pooling for databases (max 10-20 connections per instance), async I/O with `asyncio` for concurrent API calls, batch operations (embedding 100 texts vs. 1 at a time reduces latency by 80%).

**Performance Tuning Targets:**
- **Vector Search:** <50ms p95 for 1M vectors, <100ms for 10M vectors
- **Reranking:** <200ms for 100 candidates
- **Embedding Generation:** <500ms for 512-token text (batch 10+ for amortization)
- **LLM Generation:** 1-2s for 500-token response with streaming
- **Cache Hit Rate:** >70% for frequent queries

**Bottlenecks & Mitigations:**

**Bottleneck 1: Vector Database Query Latency**
- **Symptom:** P95 latency >100ms, degrading user experience
- **Mitigation Strategy:**
  1. **Index Optimization:** Use HNSW with `ef_search` tuning (higher = better recall but slower). Balance at 90-95% recall.
  2. **Metadata Pre-Filtering:** Filter on indexed fields before vector search reduces search space by 80-95% for access control queries.
  3. **Horizontal Sharding:** Partition collections by product/department for independent scaling. Query routing based on filters.
  4. **Read Replicas:** Qdrant and Pinecone support read replicas. Route read-heavy workloads to replicas, writes to primary.

**Bottleneck 2: LLM API Rate Limits**
- **Symptom:** 429 Too Many Requests errors during peak usage
- **Mitigation Strategy:**
  1. **Request Queueing:** Queue overflow requests with exponential backoff retry. Set max queue depth (1000 requests) with rejection beyond.
  2. **Model Tier Scaling:** OpenAI Tier 4 provides 10,000 RPM. Higher tiers increase limits. Monitor usage and upgrade proactively.
  3. **Self-Hosted LLMs:** Deploy vLLM serving Llama 3.3 70B on GPU instances. Eliminates rate limits, reduces cost at high volume (breakeven ~10M tokens/month).
  4. **Smart Caching:** Cache generated responses for frequent queries. Semantic similarity matching detects near-duplicate queries (embed query, search cache with threshold >0.95).

**Bottleneck 3: Embedding Generation Throughput**
- **Symptom:** Indexing pipeline processes <1,000 documents/hour
- **Mitigation Strategy:**
  1. **Batch Processing:** Embed 100 documents per API call instead of 1 at a time. Reduces latency by 80% through amortization.
  2. **Parallel Workers:** Multiple indexing workers process batches concurrently. Scale workers based on queue depth.
  3. **Self-Hosted Embeddings:** Deploy sentence-transformers models on GPU instances. Eliminates API rate limits, reduces cost for high volume.
  4. **Incremental Updates:** Only recompute embeddings for modified chunks. Track document version with commit hash. 90% of updates affect <10% of chunks.

**Database Connection Pooling:**

Prevent connection exhaustion with pooling.[^171]

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# PostgreSQL connection pool
engine = create_engine(
    "postgresql://user:pass@localhost/rag_db",
    poolclass=QueuePool,
    pool_size=10,  # Base connections
    max_overflow=20,  # Burst connections
    pool_timeout=30,  # Wait 30s for connection
    pool_recycle=3600,  # Recycle connections every hour
    pool_pre_ping=True  # Verify connection health
)

# Qdrant client with connection pooling
from qdrant_client import QdrantClient
from qdrant_client.http import SyncApis

qdrant = QdrantClient(
    url="http://localhost:6333",
    timeout=30,  # 30s timeout
    # Connection pooling handled by httpx
    limits={
        "max_connections": 100,
        "max_keepalive_connections": 20
    }
)
```

---

### 5.5 High Availability & Disaster Recovery

**HA Strategy:**

Production RAG systems require 99.9% uptime (8.76 hours downtime/year) or better.[^172]

**Redundancy Approach:**

1. **Multi-AZ Deployment:** Deploy services across 3 availability zones within a region. Load balancer distributes traffic. Single AZ failure affects 33% capacity but system remains operational.

2. **Service Redundancy:**
   - **API Gateway:** 3+ instances across AZs. Health checks remove failed instances from load balancer rotation.
   - **Retrieval Service:** Min 3 replicas, scale to 10-20 during peak. One replica can fail without impact.
   - **Generation Service:** Min 3 replicas. LLM API failures fall back to alternative provider (OpenAI → Anthropic).
   - **Indexing Service:** Min 2 workers. Failed jobs requeue automatically with dead letter queue after 3 retries.

3. **Database Redundancy:**
   - **Vector Database:** Qdrant cluster mode (3-node minimum) or Pinecone multi-AZ. Read replicas scale query throughput.
   - **Graph Database:** Neo4j cluster with causal clustering (3+ core servers, 2+ read replicas). Raft consensus for write consistency.
   - **Redis:** Redis Sentinel (1 primary + 2 replicas) with automatic failover. Persistent AOF logging prevents data loss.
   - **PostgreSQL:** Primary-replica setup with synchronous replication. Automatic failover via Patroni or cloud-managed (RDS Multi-AZ).

**Failover Mechanisms:**

**Active-Active (Preferred for Stateless Services):**
```yaml
# Kubernetes Service with automatic pod failover
apiVersion: v1
kind: Service
metadata:
  name: retrieval-service
spec:
  selector:
    app: rag-system
    component: retrieval
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  # Load balance across healthy pods
  sessionAffinity: None
  type: LoadBalancer
  # Health checks remove failed pods
  healthCheckNodePort: 30000
```

**Active-Passive (Databases):**
```python
# Database failover with connection retry
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import time

def get_db_connection(max_retries=3):
    """Connect to database with automatic failover"""

    # Primary and replica endpoints
    endpoints = [
        "postgresql://primary.db:5432/rag",
        "postgresql://replica1.db:5432/rag",
        "postgresql://replica2.db:5432/rag"
    ]

    for retry in range(max_retries):
        for endpoint in endpoints:
            try:
                engine = create_engine(endpoint, pool_pre_ping=True)
                # Test connection
                with engine.connect() as conn:
                    conn.execute("SELECT 1")
                return engine
            except OperationalError:
                continue

        time.sleep(2 ** retry)  # Exponential backoff

    raise Exception("All database endpoints failed")
```

**Health Checks and Monitoring:**

**Liveness Probe:** Detects if service is alive (restart if failing)
```python
@app.get("/health/live")
async def liveness():
    """Simple liveness check - is process running?"""
    return {"status": "alive"}
```

**Readiness Probe:** Detects if service is ready to serve traffic (remove from load balancer if failing)
```python
@app.get("/health/ready")
async def readiness():
    """Comprehensive readiness check"""

    checks = {
        "vector_db": await check_vector_db_connection(),
        "redis": await check_redis_connection(),
        "llm_api": await check_llm_api_availability()
    }

    all_healthy = all(checks.values())

    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks
    }, 200 if all_healthy else 503

async def check_vector_db_connection() -> bool:
    try:
        # Simple ping query
        result = qdrant.get_collections()
        return True
    except Exception:
        return False
```

**Circuit Breaker Pattern:**

Prevent cascade failures when downstream service degrades.[^173]

```python
from pybreaker import CircuitBreaker

# Circuit breaker for LLM API calls
llm_breaker = CircuitBreaker(
    fail_max=5,  # Open after 5 failures
    timeout_duration=60,  # Stay open for 60s
    exclude=[RateLimitError],  # Don't count rate limits as failures
    listeners=[log_circuit_state_change]
)

@llm_breaker
async def call_llm_api(prompt: str) -> str:
    """LLM API call with circuit breaker protection"""

    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            timeout=30
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM API failure: {e}")
        raise

# Fallback when circuit open
async def generate_with_fallback(query: str, context: List[Document]) -> str:
    """Generate with fallback strategies"""

    try:
        # Primary: OpenAI GPT-4
        return await call_llm_api(build_prompt(query, context))
    except CircuitBreakerError:
        # Fallback 1: Anthropic Claude
        try:
            return await call_anthropic_api(build_prompt(query, context))
        except Exception:
            # Fallback 2: Return documents with citation
            return format_documents_as_answer(query, context)
```

**Backup & Recovery:**

**Backup Strategy:**

1. **Vector Database:**
   - **Qdrant:** Snapshot collections to S3 daily. Snapshots include vectors, payload, and configuration.
   - **Pinecone:** Backups automated by Pinecone for paid tiers. Export via API for self-managed backups.

2. **Graph Database (Neo4j):**
   - **Full Backups:** Weekly full backup to S3 (compressed tar of data directory).
   - **Incremental Backups:** Daily transaction log backups for point-in-time recovery.

3. **Document Storage (S3):**
   - **Versioning:** S3 versioning enabled for all buckets. Recover deleted/overwritten files.
   - **Cross-Region Replication:** Replicate to secondary region for disaster recovery.

4. **Configuration:**
   - **GitOps:** All configuration in Git (Kubernetes manifests, Terraform, environment configs). Recovery = redeploy from Git.

**Recovery Time Objective (RTO):**
- **Tier 1 (Critical):** Query serving - RTO 15 minutes (multi-AZ failover automatic)
- **Tier 2 (Important):** Indexing - RTO 1 hour (restart workers, replay queue)
- **Tier 3 (Non-Critical):** Analytics - RTO 4 hours (rebuild from logs)

**Recovery Point Objective (RPO):**
- **Vector Database:** RPO 24 hours (daily snapshots, acceptable to reindex last day's documents)
- **Graph Database:** RPO 1 hour (transaction log backups every hour)
- **Document Storage:** RPO 0 (S3 versioning + cross-region replication provides near-zero data loss)
- **Query Logs:** RPO 5 minutes (buffered writes to log aggregator)

**Disaster Recovery Runbook:**

```bash
# Scenario: Complete region failure, failover to secondary region

# Step 1: Update DNS to point to secondary region (Route53 health checks automate this)
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch file://failover-dns.json

# Step 2: Restore vector database from latest snapshot
qdrant-cli restore \
  --collection software_docs \
  --snapshot s3://rag-backups/qdrant/2024-10-10/software_docs.snapshot

# Step 3: Restore graph database from backup
neo4j-admin restore \
  --from=/backups/neo4j/2024-10-10-full.backup \
  --database=neo4j

# Step 4: Scale up services in secondary region
kubectl scale deployment retrieval-service --replicas=10 -n production
kubectl scale deployment generation-service --replicas=10 -n production

# Step 5: Verify health checks pass
curl https://api-secondary.example.com/health/ready

# Step 6: Monitor error rates and latency
# Alert if p95 latency >3s or error rate >1%
```

**Testing HA:**

Regular chaos engineering validates failover mechanisms.[^174]

```python
# Chaos testing with random pod deletion
import random
import subprocess

def chaos_test_pod_failure():
    """Randomly delete retrieval service pod, verify no user impact"""

    # Get list of retrieval pods
    pods = subprocess.check_output([
        "kubectl", "get", "pods",
        "-l", "component=retrieval",
        "-o", "jsonpath={.items[*].metadata.name}"
    ]).decode().split()

    # Delete random pod
    victim = random.choice(pods)
    print(f"Deleting pod: {victim}")
    subprocess.run(["kubectl", "delete", "pod", victim])

    # Verify:
    # 1. New pod starts within 30s
    # 2. No increase in error rate
    # 3. P95 latency stays <3s
    # 4. All health checks pass

    time.sleep(30)

    # Check metrics
    error_rate = get_metric("http_errors_total", last="5m")
    latency_p95 = get_metric("http_request_latency_p95", last="5m")

    assert error_rate < 0.01, f"Error rate {error_rate} exceeds threshold"
    assert latency_p95 < 3.0, f"P95 latency {latency_p95}s exceeds threshold"
```

---

## References

[^143]: AWS Well-Architected Framework, "Microservices Architecture Best Practices", accessed October 2024, https://aws.amazon.com/architecture/well-architected/

[^144]: AWS API Gateway Documentation, "Serverless API Gateway Patterns", accessed October 2024, https://docs.aws.amazon.com/apigateway/

[^145]: Jeong, Soyeong et al., "Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity", arXiv:2403.14403, March 2024, https://arxiv.org/abs/2403.14403

[^146]: Redis Documentation, "Caching Strategies for High Performance", accessed October 2024, https://redis.io/docs/manual/patterns/

[^147]: OpenAI, "Production Best Practices for LLM API Usage", accessed October 2024, https://platform.openai.com/docs/guides/production-best-practices

[^148]: Martin Fowler, "Event-Driven Architecture", martinfowler.com, accessed October 2024, https://martinfowler.com/articles/201701-event-driven.html

[^149]: Qdrant Documentation, "Performance Benchmarks and Tuning", accessed October 2024, https://qdrant.tech/documentation/guides/performance/

[^150]: Edge, Darren et al., "HybridRAG: Integrating Knowledge Graphs and Vector Retrieval", arXiv:2408.04948, August 2024, https://arxiv.org/abs/2408.04948

[^151]: Google SRE Book, "User-Facing Latency Targets", accessed October 2024, https://sre.google/sre-book/

[^152]: Kafka Documentation, "Event Streaming for Data Pipelines", accessed October 2024, https://kafka.apache.org/documentation/

[^153]: Memcached Documentation, "Cache Invalidation Strategies", accessed October 2024, https://memcached.org/about

[^154]: Pinecone, "Pricing Calculator", accessed October 2024, https://www.pinecone.io/pricing/

[^155]: AWS, "EKS Pricing and Cost Estimation", accessed October 2024, https://aws.amazon.com/eks/pricing/

[^156]: Databricks, "Enterprise ML Infrastructure Costs", accessed October 2024, https://www.databricks.com/

[^157]: Python Software Foundation, "Python for AI/ML Ecosystem", accessed October 2024, https://www.python.org/

[^158]: FastAPI Documentation, "Performance Benchmarks", accessed October 2024, https://fastapi.tiangolo.com/benchmarks/

[^159]: Qdrant Blog, "Performance Comparison: Qdrant vs. Competitors", accessed September 2024, https://qdrant.tech/blog/benchmark-1b/

[^160]: Pinecone Documentation, "Serverless Vector Database Architecture", accessed October 2024, https://docs.pinecone.io/docs/architecture

[^161]: Neo4j Documentation, "Vector Search with HNSW Index", accessed October 2024, https://neo4j.com/docs/cypher-manual/current/indexes-for-vector-search/

[^162]: AWS S3 Documentation, "Durability and Availability", accessed October 2024, https://docs.aws.amazon.com/AmazonS3/latest/userguide/DataDurability.html

[^163]: Redis Documentation, "Persistence Options", accessed October 2024, https://redis.io/docs/manual/persistence/

[^164]: RabbitMQ Documentation, "Message Queueing Patterns", accessed October 2024, https://www.rabbitmq.com/getstarted.html

[^165]: Docker Documentation, "Multi-Stage Builds", accessed October 2024, https://docs.docker.com/build/building/multi-stage/

[^166]: Kubernetes Documentation, "Production Best Practices", accessed October 2024, https://kubernetes.io/docs/setup/best-practices/

[^167]: GitHub Actions Documentation, accessed October 2024, https://docs.github.com/actions

[^168]: Thoughtworks, "Database Migration Patterns", accessed October 2024, https://www.thoughtworks.com/insights/

[^169]: Martin Fowler, "Scaling Horizontally and Vertically", martinfowler.com, accessed October 2024, https://martinfowler.com/bliki/

[^170]: Google SRE, "Capacity Planning", accessed October 2024, https://sre.google/sre-book/capacity-planning/

[^171]: SQLAlchemy Documentation, "Connection Pooling", accessed October 2024, https://docs.sqlalchemy.org/en/20/core/pooling.html

[^172]: AWS, "High Availability Architecture Patterns", accessed October 2024, https://aws.amazon.com/architecture/

[^173]: Nygard, Michael, "Release It! Design Patterns for Production Systems", Pragmatic Bookshelf, 2018

[^174]: Chaos Engineering, "Principles of Chaos Engineering", accessed October 2024, https://principlesofchaos.org/
