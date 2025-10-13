# Python CLAUDE.md - Improvement TODO

**Status**: Active
**Last Updated**: 2025-09-23
**Priority System**: 🔴 High | 🟡 Medium | 🟢 Low

---

## 🔴 HIGH PRIORITY - Critical Missing Examples

### 1. Async Context Managers & Patterns
**File**: `CLAUDE-typing.md`
**Estimated Effort**: 2-3 hours
**Instructions**:
```
Add comprehensive async context manager examples including:
- Database connection async context managers
- File I/O async context managers
- HTTP client session management
- Resource cleanup patterns with async generators
- Async context manager protocols

Example structure:
\```python
from typing import AsyncContextManager
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_connection():
    conn = await create_connection()
    try:
        yield conn
    finally:
        await conn.close()
\```

Add error handling, timeout patterns, and nested async context managers.
```

### 2. Database Transaction Management
**File**: `CLAUDE-architecture.md`
**Estimated Effort**: 3-4 hours
**Instructions**:
```
Add transaction management patterns for SQLAlchemy async:
- Transaction context managers
- Nested transactions and savepoints
- Rollback on exception
- Transaction isolation levels
- Unit of Work pattern implementation

Include examples of:
- Manual transaction control
- Automatic transaction decorator
- Transaction retry logic
- Distributed transaction considerations

Example:
\```python
@asynccontextmanager
async def transaction(session: AsyncSession):
    async with session.begin():
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
\```
```

### 3. JWT Authentication Flow
**File**: `CLAUDE-validation.md`
**Estimated Effort**: 3-4 hours
**Instructions**:
```
Add complete JWT authentication implementation:
- Access token generation and validation
- Refresh token flow
- Token blacklisting strategy
- Token claims validation
- FastAPI dependency injection for auth

Include security considerations:
- Token expiration handling
- Secure storage recommendations
- Token rotation strategies
- CSRF protection with JWT

Example structure:
\```python
from jose import JWTError, jwt
from datetime import datetime, timedelta

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
\```

Add dependency for protecting routes and token refresh endpoint.
```

### 4. File Upload Security
**File**: `CLAUDE-validation.md`
**Estimated Effort**: 2-3 hours
**Instructions**:
```
Add comprehensive file upload security:
- File size validation (streaming and total)
- MIME type verification (not just extension)
- Virus scanning integration (ClamAV example)
- Secure filename sanitization
- Storage path security
- Image manipulation safety (PIL/Pillow)

Include examples:
\```python
from fastapi import UploadFile, HTTPException
import magic  # python-magic for MIME detection

async def validate_upload(file: UploadFile):
    # Size check
    contents = await file.read(8192)  # Read header
    mime = magic.from_buffer(contents, mime=True)

    allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
    if mime not in allowed_types:
        raise HTTPException(400, "Invalid file type")

    # Reset file pointer
    await file.seek(0)
\```

Add chunked upload handling and malware scanning integration.
```

### 5. API Rate Limiting Implementation
**File**: `CLAUDE-validation.md`
**Estimated Effort**: 2-3 hours
**Instructions**:
```
Add rate limiting patterns:
- FastAPI rate limiting middleware
- Redis-based rate limiting (slowapi)
- Token bucket algorithm
- Sliding window rate limiting
- Per-user and per-IP limits
- Rate limit headers (X-RateLimit-*)

Include configuration:
\```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/data")
@limiter.limit("5/minute")
async def get_data():
    return {"data": "value"}
\```

Add custom rate limit strategies and distributed rate limiting with Redis.
```

---

## 🟡 MEDIUM PRIORITY - Tool Configuration Expansions

### 6. pytest-xdist Parallel Testing
**File**: `CLAUDE-testing.md`
**Estimated Effort**: 1-2 hours
**Instructions**:
```
Add detailed pytest-xdist configuration:
- Installation and setup
- Parallel execution strategies (load, each, loadscope, loadfile)
- Fixture scope with parallel tests
- Database isolation per worker
- Test data management for parallel runs

Configuration example:
\```toml
[tool.pytest.ini_options]
addopts = [
    "-n", "auto",  # Auto-detect CPU count
    "--dist", "loadscope",  # Distribute by test scope
]
\```

Add troubleshooting section for parallel test issues and fixture sharing.
```

### 7. Hypothesis Property-Based Testing
**File**: `CLAUDE-testing.md`
**Estimated Effort**: 2-3 hours
**Instructions**:
```
Expand property-based testing guide:
- Hypothesis strategies (st.integers, st.text, st.lists, etc.)
- Custom strategies for domain models
- Stateful testing with RuleBasedStateMachine
- Shrinking examples and minimal failing cases
- Integration with pytest fixtures

Examples:
\```python
from hypothesis import given, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule

@given(st.lists(st.integers(), min_size=1))
def test_sort_idempotent(items):
    assert sorted(sorted(items)) == sorted(items)

class UserStateMachine(RuleBasedStateMachine):
    @rule(username=st.text(min_size=3))
    def create_user(self, username):
        # Test state transitions
        pass
\```

Add best practices for property selection and common patterns.
```

### 8. Syrupy Snapshot Testing
**File**: `CLAUDE-testing.md`
**Estimated Effort**: 1-2 hours
**Instructions**:
```
Add comprehensive snapshot testing guide:
- Installation and basic usage
- Snapshot serialization formats
- Updating snapshots workflow
- Filtering and excluding fields
- Custom snapshot serializers

Examples:
\```python
def test_user_serialization(snapshot):
    user = User(id=1, name="Test", created_at=datetime.now())
    assert user.model_dump() == snapshot

def test_api_response(snapshot):
    response = get_user_profile(1)
    assert response == snapshot(exclude=props("created_at"))
\```

Add CI/CD integration and snapshot review process.
```

### 9. Structlog Structured Logging
**File**: `CLAUDE-architecture.md`
**Estimated Effort**: 2-3 hours
**Instructions**:
```
Add structured logging implementation:
- Structlog setup and configuration
- JSON logging for production
- Context binding (request_id, user_id)
- Log processors and formatters
- Integration with FastAPI middleware

Configuration:
\```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()
logger.info("user_login", user_id=123, ip="192.168.1.1")
\```

Add ELK/CloudWatch integration examples.
```

---

## 🟡 MEDIUM PRIORITY - Security Critical Examples

### 10. Complete CORS Configuration
**File**: `CLAUDE-architecture.md`
**Estimated Effort**: 1-2 hours
**Instructions**:
```
Expand CORS middleware configuration:
- Origin validation patterns
- Credentials handling
- Preflight request optimization
- Per-route CORS policies
- Security considerations

Example:
\```python
from fastapi.middleware.cors import CORSMiddleware

def is_allowed_origin(origin: str) -> bool:
    allowed_patterns = [
        r"^https://.*\.example\.com$",
        r"^http://localhost:\d+$"
    ]
    return any(re.match(pattern, origin) for pattern in allowed_patterns)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https://.*\.example\.com$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=3600,
)
\```

Add troubleshooting section for common CORS issues.
```

### 11. SQL Injection Prevention Examples
**File**: `CLAUDE-validation.md`
**Estimated Effort**: 1-2 hours
**Instructions**:
```
Add SQL injection prevention with SQLAlchemy:
- Parameterized queries with SQLAlchemy Core
- ORM query safety
- Raw SQL execution safely
- Dynamic query building
- Input validation before queries

Examples:
\```python
# ✅ Safe: Parameterized query
stmt = select(User).where(User.email == email)

# ✅ Safe: ORM with bound parameters
users = session.query(User).filter(User.email == email).all()

# ✅ Safe: Raw SQL with parameters
result = session.execute(
    text("SELECT * FROM users WHERE email = :email"),
    {"email": email}
)

# ❌ NEVER: String formatting
# query = f"SELECT * FROM users WHERE email = '{email}'"
\```

Add section on dynamic table/column names and escaping.
```

---

## 🟢 LOW PRIORITY - Advanced Features

### 12. Caching Strategies
**File**: `CLAUDE-architecture.md`
**Estimated Effort**: 3-4 hours
**Instructions**:
```
Add comprehensive caching guide:
- LRU cache decorator usage
- Redis caching patterns
- Cache invalidation strategies
- Cache warming and preloading
- Distributed caching with Redis Cluster

Include patterns:
- Cache-aside pattern
- Write-through cache
- Write-behind cache
- Refresh-ahead cache

Example:
\```python
from functools import lru_cache
import redis.asyncio as redis

# In-memory cache
@lru_cache(maxsize=1000)
def get_config(key: str) -> str:
    return load_from_db(key)

# Redis cache
async def get_user_cached(user_id: int) -> User:
    cache_key = f"user:{user_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return User.model_validate_json(cached)

    user = await db.get_user(user_id)
    await redis_client.setex(
        cache_key,
        3600,
        user.model_dump_json()
    )
    return user
\```

Add cache key design patterns and TTL strategies.
```

### 13. WebSocket Real-time Patterns
**File**: `CLAUDE-architecture.md`
**Estimated Effort**: 3-4 hours
**Instructions**:
```
Add WebSocket implementation guide:
- FastAPI WebSocket setup
- Connection management
- Broadcasting to multiple clients
- Room/channel patterns
- Authentication with WebSockets
- Reconnection handling

Example:
\```python
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
\```

Add scaling considerations and Redis pub/sub for multi-server.
```

### 14. Monorepo/Workspace Configuration
**File**: New `CLAUDE-monorepo.md` or in `CLAUDE-tooling.md`
**Estimated Effort**: 2-3 hours
**Instructions**:
```
Add UV workspace setup for monorepos:
- Workspace configuration in pyproject.toml
- Shared dependencies management
- Inter-package dependencies
- Development workflow for workspaces
- Build and publish strategies

Configuration:
```toml
[tool.uv.workspace]
members = [
    "packages/core",
    "packages/api",
    "packages/worker",
]

[tool.uv.workspace.dependencies]
shared-utils = { path = "packages/shared", develop = true }
\```

Add scripts for monorepo operations and CI/CD integration.
```

### 15. Background Job Processing
**File**: `CLAUDE-architecture.md`
**Estimated Effort**: 3-4 hours
**Instructions**:
```
Add async task processing patterns:
- Celery with FastAPI integration
- Dramatiq task queue patterns
- ARQ (async task queue)
- Task retry strategies
- Result backends and monitoring

Examples:
\```python
# Celery
from celery import Celery

celery_app = Celery('tasks', broker='redis://localhost:6379/0')

@celery_app.task
def process_upload(file_id: int):
    # Long-running task
    pass

# Dramatiq
import dramatiq

@dramatiq.actor
def send_email(user_id: int, subject: str):
    # Email sending task
    pass

# FastAPI integration
@app.post("/upload")
async def upload_file(file: UploadFile):
    process_upload.delay(file_id)
    return {"status": "processing"}
\```

Add task monitoring, failure handling, and scheduling patterns.
```

---

## 📋 Configuration & Project Setup Gaps

### 16. Alembic Database Migrations
**File**: New `CLAUDE-database.md` or in `CLAUDE-architecture.md`
**Estimated Effort**: 2-3 hours
**Instructions**:
```
Add database migration best practices:
- Alembic setup and configuration
- Migration file generation
- Manual migration writing
- Data migrations vs schema migrations
- Rollback strategies
- Multi-environment migrations

Configuration:
\```python
# alembic/env.py
from sqlalchemy import pool
from alembic import context
from myapp.models import Base

config = context.config
config.set_main_option(
    "sqlalchemy.url",
    settings.database_url
)

target_metadata = Base.metadata

# Migration example
def upgrade():
    op.add_column('users', sa.Column('phone', sa.String(20)))
    op.create_index('idx_users_phone', 'users', ['phone'])
\```

Add zero-downtime migration patterns and testing strategies.
```

### 17. Docker Best Practices
**File**: New `CLAUDE-deployment.md`
**Estimated Effort**: 3-4 hours
**Instructions**:
```
Add containerization guide:
- Multi-stage Dockerfile for Python
- UV in Docker optimization
- Docker Compose for development
- Production-ready image patterns
- Security hardening (non-root user, minimal base)

Example:
```dockerfile
FROM python:3.11-slim as builder
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:3.11-slim
COPY --from=builder /app/.venv /app/.venv
COPY src/ /app/src/
ENV PATH="/app/.venv/bin:$PATH"
USER nobody
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
\```

Add health checks, logging, and orchestration examples.
```

### 18. CI/CD Pipeline Configuration
**File**: New `CLAUDE-deployment.md`
**Estimated Effort**: 2-3 hours
**Instructions**:
```
Add CI/CD examples for GitHub Actions:
- UV caching strategies
- Matrix testing across Python versions
- Linting and type checking in CI
- Test coverage reporting
- Automated deployment

Example:
```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v3
      - uses: astral-sh/setup-uv@v1
      - run: uv sync --frozen
      - run: uv run pytest --cov
      - run: uv run ruff check
      - run: uv run mypy src/
\```

Add GitLab CI, CircleCI examples and deployment strategies.
```

### 19. GraphQL API Patterns
**File**: New `CLAUDE-graphql.md` or in `CLAUDE-architecture.md`
**Estimated Effort**: 3-4 hours
**Instructions**:
```
Add Strawberry GraphQL patterns:
- Schema definition with Strawberry
- Resolvers and dataloaders
- Authentication/authorization
- Subscription patterns (WebSocket)
- Error handling in GraphQL

Example:
\```python
import strawberry
from typing import List

@strawberry.type
class User:
    id: int
    name: str
    email: str

@strawberry.type
class Query:
    @strawberry.field
    async def user(self, id: int) -> User:
        return await get_user(id)

    @strawberry.field
    async def users(self) -> List[User]:
        return await get_all_users()

schema = strawberry.Schema(query=Query)
\```

Add N+1 query prevention with dataloaders and pagination.
```

### 20. API Versioning Strategies
**File**: `CLAUDE-architecture.md`
**Estimated Effort**: 1-2 hours
**Instructions**:
```
Add API versioning patterns:
- URL path versioning (/api/v1/, /api/v2/)
- Header-based versioning
- Content negotiation versioning
- Deprecation strategies
- Version migration guides

Examples:
\```python
# URL versioning
v1_router = APIRouter(prefix="/api/v1")
v2_router = APIRouter(prefix="/api/v2")

# Header versioning
@app.get("/api/users")
async def get_users(api_version: str = Header(default="1.0")):
    if api_version == "2.0":
        return v2_get_users()
    return v1_get_users()

# Deprecation
@app.get("/api/v1/users")
@deprecated(sunset_date="2025-12-31", replacement="/api/v2/users")
async def old_get_users():
    pass
\```

Add sunset headers and gradual migration strategies.
```

---

## 🔄 Continuous Improvement Tasks

### 21. Quarterly Review Process
**Recurrence**: Every 3 months
**Instructions**:
```
Review and update CLAUDE.md files:
1. Check for new Python version features
2. Update tool versions (UV, Ruff, MyPy, pytest)
3. Review and update examples for clarity
4. Add newly discovered patterns from projects
5. Remove deprecated practices
6. Update performance benchmarks
7. Review security recommendations

Create quarterly review checklist:
- [ ] Python version compatibility (3.9-3.12+)
- [ ] Tool version updates (UV, Ruff, MyPy)
- [ ] Security advisories review
- [ ] Community best practices
- [ ] Example code testing
- [ ] Link validation
- [ ] Token count optimization
```

### 22. Community Pattern Integration
**Recurrence**: Monthly
**Instructions**:
```
Monitor and integrate community patterns:
1. Review GitHub discussions/issues
2. Check Python community forums (Reddit r/Python, discuss.python.org)
3. Review FastAPI/Pydantic/SQLAlchemy release notes
4. Collect feedback from CLAUDE.md users
5. Integrate valuable patterns into guides

Process:
1. Identify valuable pattern/practice
2. Validate with testing
3. Write example following guide style
4. Add to appropriate specialized file
5. Cross-reference from other relevant files
```

---

## 📈 Success Metrics

Track improvements with these metrics:

| Metric | Target | Current | Gap |
|--------|--------|---------|-----|
| Critical examples covered | 100% | 60% | 40% |
| Tool configurations complete | 100% | 70% | 30% |
| Security patterns comprehensive | 100% | 65% | 35% |
| Project patterns coverage | 90% | 50% | 40% |
| Code examples tested | 100% | 85% | 15% |
| Cross-references accurate | 100% | 90% | 10% |

---

## 🎯 Implementation Priority Order

### Phase 1 - Critical Security & Examples (Week 1-2)
1. JWT Authentication Flow (#3)
2. File Upload Security (#4)
3. API Rate Limiting (#5)
4. SQL Injection Prevention (#11)
5. Complete CORS Configuration (#10)

### Phase 2 - Core Patterns & Tools (Week 3-4)
6. Async Context Managers (#1)
7. Database Transaction Management (#2)
8. pytest-xdist Configuration (#6)
9. Structlog Setup (#9)
10. Caching Strategies (#12)

### Phase 3 - Advanced Features (Week 5-6)
11. WebSocket Patterns (#13)
12. Hypothesis Property Testing (#7)
13. Background Job Processing (#15)
14. Alembic Migrations (#16)
15. Syrupy Snapshot Testing (#8)

### Phase 4 - Infrastructure & Deployment (Week 7-8)
16. Docker Best Practices (#17)
17. CI/CD Pipeline Configuration (#18)
18. Monorepo/Workspace Setup (#14)
19. GraphQL API Patterns (#19)
20. API Versioning Strategies (#20)

---

## 📝 IMPLEMENTATION INSTRUCTIONS FOR AI AGENT

### When Creating New Pattern Files:

1. **Read existing files first** to understand style and structure
2. **Follow the pattern**: Introduction → Core Concepts → Examples → Best Practices → Anti-patterns
3. **Use code fences** with language specification (```python, ```bash, etc.)
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
- [ ] Python idioms and best practices followed
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
- High Priority: 0/5 completed
- Medium Priority: 0/6 completed
- Low Priority: 0/4 completed
- Configuration & Project Setup Gaps: 0/5 completed
- Continuous Improvements: 0/2 completed 

---

**Last Updated**: 2025-09-23
**Next Review**: 2025-12-23 (Quarterly)
**Maintained By**: AI Development Team