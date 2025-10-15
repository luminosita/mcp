# Extension Guide: Adding Database Access to Tools

**Last Updated**: 2025-10-15
**Version**: 1.0
**Status**: Active

## Purpose

This guide provides patterns for adding database access to MCP tools using SQLAlchemy async with proper connection pooling, transaction management, and error handling.

**After following this guide, you will understand**:
- How to access database sessions in tools via dependency injection
- Query patterns with SQLAlchemy async
- Transaction management and error handling
- Connection pooling configuration
- Testing with database fixtures

**Prerequisites**:
- Basic SQL knowledge
- Understanding of SQLAlchemy ORM concepts
- Familiarity with async/await patterns

---

## Database Architecture Overview

**Technology Stack**:
- **Database**: PostgreSQL 15+ (with pgvector extension for future RAG)
- **ORM**: SQLAlchemy 2.x with async support
- **Connection Pooling**: SQLAlchemy engine pool (10 permanent + 20 overflow)
- **Migration Tool**: Alembic (not yet configured - future EPIC)

**Key Advantages**:
- **Async**: Non-blocking database queries (high concurrency)
- **Connection Pooling**: Reuse connections (reduce handshake overhead)
- **Transaction Management**: Automatic commit/rollback via dependency injection
- **Type Safety**: SQLAlchemy models with type hints

---

## Step 1: Define Database Model

Create SQLAlchemy model for your database table.

**File**: `src/mcp_server/models/resource.py` (create models/ directory if needed)

```python
"""
Database models for resource management.
"""

from datetime import datetime
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class Resource(Base):
    """
    Resource model for storing resource information.

    Table: resources
    """

    __tablename__ = "resources"

    # Primary key
    id: Mapped[str] = mapped_column(String(100), primary_key=True)

    # Required fields
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")

    # Optional fields
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Boolean flags
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return f"<Resource(id={self.id!r}, name={self.name!r}, status={self.status!r})>"
```

**Key Patterns**:
- Use `Mapped[type]` for typed columns
- Use `mapped_column()` for column configuration
- Include timestamps (`created_at`, `updated_at`) for auditing
- Use `String` for text (specify max length)
- Use `Boolean` for flags
- Use `DateTime(timezone=True)` for timestamps with timezone

---

## Step 2: Access Database Session in Tool

Inject database session via dependency injection.

```python
from sqlalchemy.ext.asyncio import AsyncSession
from mcp_server.core.dependencies import get_db_session


# Business logic function (testable)
async def query_resource(
    resource_id: str,
    session: AsyncSession,  # Injected dependency
    logger: logging.Logger,
) -> Resource | None:
    """
    Query resource by ID.

    Args:
        resource_id: Resource identifier
        session: Database session (injected)
        logger: Logger instance (injected)

    Returns:
        Resource if found, None otherwise
    """
    from sqlalchemy import select
    from mcp_server.models.resource import Resource

    logger.info(f"Querying resource: {resource_id}")

    try:
        # Execute query
        result = await session.execute(
            select(Resource).where(Resource.id == resource_id)
        )

        # Get single result (or None if not found)
        resource = result.scalar_one_or_none()

        if resource:
            logger.info(f"Resource found: {resource.name}")
        else:
            logger.warning(f"Resource not found: {resource_id}")

        return resource

    except Exception as e:
        logger.exception(f"Database error querying resource: {e}")
        raise


# MCP tool wrapper (accesses dependencies directly)
@mcp.tool(name="resources.query")
async def query_resource_tool(params: QueryResourceInput) -> QueryResourceOutput:
    """MCP tool wrapper for querying resources."""
    from mcp_server.core.dependencies import get_db_session, get_logger

    logger = get_logger("mcp_server.tools.resources")

    # Access database session directly
    # NOTE: For MCP tools, we need to call the generator manually
    session_gen = get_db_session()
    session = await session_gen.__anext__()

    try:
        resource = await query_resource(params.resource_id, session, logger)

        if not resource:
            raise BusinessLogicError(
                f"Resource {params.resource_id} not found",
                details={"resource_id": params.resource_id},
            )

        return QueryResourceOutput(
            id=resource.id,
            name=resource.name,
            status=resource.status,
            is_active=resource.is_active,
        )
    finally:
        # Cleanup session
        await session_gen.aclose()
```

**Important**: FastMCP tools can't use `Depends()` directly, so we manually call the generator.

---

## Step 3: Common Query Patterns

### Pattern 1: Query Single Record

```python
from sqlalchemy import select

async def get_resource_by_id(
    resource_id: str,
    session: AsyncSession,
) -> Resource | None:
    """Get single resource by ID."""
    result = await session.execute(
        select(Resource).where(Resource.id == resource_id)
    )
    return result.scalar_one_or_none()  # Returns None if not found
```

### Pattern 2: Query Multiple Records

```python
async def get_active_resources(
    session: AsyncSession,
) -> list[Resource]:
    """Get all active resources."""
    result = await session.execute(
        select(Resource).where(Resource.is_active == True).order_by(Resource.name)
    )
    return list(result.scalars().all())
```

### Pattern 3: Query with Filters

```python
async def search_resources(
    name_pattern: str,
    status: str | None,
    session: AsyncSession,
) -> list[Resource]:
    """Search resources by name pattern and optional status."""
    query = select(Resource).where(Resource.name.ilike(f"%{name_pattern}%"))

    if status:
        query = query.where(Resource.status == status)

    result = await session.execute(query.order_by(Resource.created_at.desc()))
    return list(result.scalars().all())
```

### Pattern 4: Create Record

```python
async def create_resource(
    resource_id: str,
    name: str,
    status: str,
    session: AsyncSession,
) -> Resource:
    """Create new resource."""
    resource = Resource(
        id=resource_id,
        name=name,
        status=status,
        is_active=True,
    )

    session.add(resource)
    # Session auto-commits after tool completes (via dependency injection)

    return resource
```

### Pattern 5: Update Record

```python
async def update_resource_status(
    resource_id: str,
    new_status: str,
    session: AsyncSession,
) -> Resource:
    """Update resource status."""
    result = await session.execute(
        select(Resource).where(Resource.id == resource_id)
    )
    resource = result.scalar_one_or_none()

    if not resource:
        raise BusinessLogicError(f"Resource {resource_id} not found")

    resource.status = new_status
    resource.updated_at = datetime.utcnow()

    # Session auto-commits after tool completes

    return resource
```

### Pattern 6: Delete Record

```python
async def delete_resource(
    resource_id: str,
    session: AsyncSession,
) -> bool:
    """Delete resource (soft delete by setting is_active=False)."""
    result = await session.execute(
        select(Resource).where(Resource.id == resource_id)
    )
    resource = result.scalar_one_or_none()

    if not resource:
        return False

    # Soft delete (keep record, mark as inactive)
    resource.is_active = False
    resource.updated_at = datetime.utcnow()

    # Hard delete (remove record entirely)
    # await session.delete(resource)

    return True
```

---

## Step 4: Transaction Management

**Automatic Transaction Management**: Database session dependency handles transactions automatically.

### Default Behavior

```python
async def my_tool_function(session: AsyncSession):
    # Start of function = start of transaction

    # All database operations are part of transaction
    resource = Resource(id="res-123", name="My Resource")
    session.add(resource)

    # If function completes without exception:
    # → session.commit() called automatically

    # If function raises exception:
    # → session.rollback() called automatically

    return resource
```

### Manual Rollback (Rare Cases)

```python
async def my_tool_with_manual_rollback(session: AsyncSession):
    try:
        # Perform some operations
        resource = Resource(id="res-123", name="Test")
        session.add(resource)

        # Business logic check
        if some_business_rule_violated:
            await session.rollback()  # Manual rollback
            raise BusinessLogicError("Business rule violated")

        # Continue with other operations
        ...

    except Exception:
        await session.rollback()
        raise
```

**Note**: Manual transaction management rarely needed. Dependency injection handles 99% of cases.

---

## Step 5: Error Handling

### Database Errors to Handle

```python
from sqlalchemy.exc import IntegrityError, OperationalError

async def create_resource_with_error_handling(
    resource_id: str,
    name: str,
    session: AsyncSession,
    logger: logging.Logger,
) -> Resource:
    """Create resource with comprehensive error handling."""
    try:
        resource = Resource(id=resource_id, name=name)
        session.add(resource)
        await session.flush()  # Force execute to catch errors before commit

        return resource

    except IntegrityError as e:
        # Constraint violation (duplicate ID, foreign key violation)
        logger.error(f"Integrity error creating resource: {e}")
        raise BusinessLogicError(
            f"Resource {resource_id} already exists or violates constraint",
            details={"resource_id": resource_id, "error": str(e)},
        )

    except OperationalError as e:
        # Connection error, timeout
        logger.error(f"Database connection error: {e}")
        raise BusinessLogicError(
            "Database temporarily unavailable",
            details={"error": str(e)},
        )

    except Exception as e:
        logger.exception(f"Unexpected database error: {e}")
        raise BusinessLogicError(
            "Failed to create resource due to unexpected error",
            details={"error": str(e)},
        )
```

---

## Step 6: Connection Pooling Configuration

Connection pool is configured during application startup.

**File**: `src/mcp_server/core/dependencies.py`

```python
async def initialize_db_session_maker() -> None:
    """
    Initialize database session maker at application startup.
    """
    global _session_maker
    if _session_maker is not None:
        raise RuntimeError("Database session maker already initialized")

    settings = get_settings()
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,              # Log SQL in debug mode
        pool_pre_ping=True,               # Verify connections before use
        pool_size=10,                      # Permanent connections (default: 5)
        max_overflow=20,                   # Additional when pool exhausted (default: 10)
        pool_timeout=30,                   # Wait for connection (seconds)
        pool_recycle=3600,                 # Recycle connections after 1 hour
    )

    _session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,  # Allow access to objects after commit
    )
```

**Key Parameters**:
- `pool_size=10`: Number of permanent connections kept open
- `max_overflow=20`: Additional connections when pool exhausted (total = 30)
- `pool_pre_ping=True`: Test connection before use (prevents stale connections)
- `pool_recycle=3600`: Close and recreate connections after 1 hour (prevents stale connections)

**Tuning**:
- **High Concurrency**: Increase `pool_size` and `max_overflow`
- **Low Latency**: Increase `pool_size` (reduce wait for connections)
- **Memory Constraints**: Decrease `pool_size` and `max_overflow`

---

## Step 7: Testing with Database Fixtures

### Test with In-Memory SQLite

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from mcp_server.models.resource import Base, Resource


@pytest.fixture
async def test_db_session():
    """Create test database session with in-memory SQLite."""
    # Create in-memory database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session maker
    session_maker = async_sessionmaker(engine, class_=AsyncSession)

    # Provide session to test
    async with session_maker() as session:
        yield session

    # Cleanup
    await engine.dispose()


@pytest.mark.asyncio
async def test_query_resource(test_db_session):
    """Test querying resource from database."""
    # Arrange: Insert test data
    resource = Resource(id="res-123", name="Test Resource", status="active")
    test_db_session.add(resource)
    await test_db_session.commit()

    # Act: Query resource
    result = await query_resource("res-123", test_db_session, mock_logger)

    # Assert
    assert result is not None
    assert result.name == "Test Resource"
    assert result.status == "active"
```

### Test with Real PostgreSQL (Docker)

```python
@pytest.fixture(scope="session")
async def test_db_url():
    """Start PostgreSQL container for testing."""
    # Requires testcontainers library
    import testcontainers.postgres

    with testcontainers.postgres.PostgresContainer("postgres:15") as postgres:
        yield postgres.get_connection_url()


@pytest.fixture
async def test_db_session_postgres(test_db_url):
    """Create test database session with real PostgreSQL."""
    engine = create_async_engine(test_db_url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession)

    async with session_maker() as session:
        yield session

    await engine.dispose()
```

---

## Best Practices

### 1. Use Soft Deletes

Instead of hard deleting records, mark them as inactive:

```python
class Resource(Base):
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

# Soft delete
resource.is_active = False

# Query only active records
query = select(Resource).where(Resource.is_active == True)
```

### 2. Include Timestamps

Always include `created_at` and `updated_at` for auditing:

```python
class Resource(Base):
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 3. Use Indexes for Performance

Add indexes to frequently queried columns:

```python
from sqlalchemy import Index

class Resource(Base):
    __tablename__ = "resources"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Composite index for common query pattern
    __table_args__ = (
        Index("idx_status_active", "status", "is_active"),
    )
```

### 4. Avoid N+1 Query Problems

Use eager loading for relationships:

```python
from sqlalchemy.orm import selectinload

# Bad: N+1 queries
resources = await session.execute(select(Resource))
for resource in resources.scalars():
    # This triggers separate query for each resource
    print(resource.related_entity.name)

# Good: Eager loading
resources = await session.execute(
    select(Resource).options(selectinload(Resource.related_entity))
)
for resource in resources.scalars():
    # No additional queries
    print(resource.related_entity.name)
```

### 5. Use Type Hints Throughout

```python
from typing import Sequence

async def get_resources(
    status: str,
    session: AsyncSession,
) -> Sequence[Resource]:  # Use Sequence for SQLAlchemy results
    result = await session.execute(
        select(Resource).where(Resource.status == status)
    )
    return result.scalars().all()
```

---

## Troubleshooting

### Error: "Connection pool exhausted"

**Cause**: More concurrent requests than available connections.

**Solution**:
1. Increase `pool_size` and `max_overflow`
2. Optimize query performance (reduce query time)
3. Add connection timeout handling

### Error: "Connection closed by server"

**Cause**: Stale connections in pool.

**Solution**:
- Enable `pool_pre_ping=True` (tests connections before use)
- Reduce `pool_recycle` time (e.g., 1800 seconds)

### Error: "Transaction already committed/rolled back"

**Cause**: Manual transaction management conflicting with dependency injection.

**Solution**: Let dependency injection handle transactions automatically. Remove manual `commit()`/`rollback()` calls.

---

## Related Documentation

- **Dependency Injection**: [../dependency-injection.md](../dependency-injection.md) - DI patterns
- **Extension Guide**: [add-new-tool.md](add-new-tool.md) - Tool implementation patterns
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

### CLAUDE.md Standards

- **CLAUDE-architecture.md**: Database layer architecture
- **CLAUDE-testing.md**: Database testing patterns

---

## Changelog

- **2025-10-15** (v1.0): Initial database access guide (US-013)
