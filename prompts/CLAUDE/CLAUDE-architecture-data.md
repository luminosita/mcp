# CLAUDE-architecture-data.md - Database Transactions & Models


> **Specialized Guide**: Database transaction management patterns, isolation levels, and SQLAlchemy models.

> **Specialized Guide**: Comprehensive project architecture, modularity patterns, and design principles for Python projects.

## 🗄️ Database Transaction Management

### Transaction Context Manager

```python
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from typing import AsyncIterator
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def transaction(session: AsyncSession) -> AsyncIterator[AsyncSession]:
    """
    Transaction context manager with automatic commit/rollback.

    Usage:
        async with transaction(session) as tx:
            # All operations in one transaction
            user = User(name="John")
            session.add(user)
            # Auto-commits on success, rolls back on exception
    """
    async with session.begin():
        try:
            yield session
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            await session.rollback()
            raise

# Alternative: Explicit control
async def manual_transaction(session: AsyncSession) -> None:
    """Manual transaction control."""
    try:
        async with session.begin():
            # Perform operations
            user = User(name="John", email="john@example.com")
            session.add(user)

            # Commit happens automatically at context exit
    except Exception:
        # Rollback happens automatically on exception
        raise
```

### Nested Transactions (Savepoints)

```python
from sqlalchemy.ext.asyncio import AsyncSession

async def nested_transaction_example(session: AsyncSession) -> None:
    """
    Nested transactions using savepoints.

    Savepoints allow partial rollback within a transaction.
    """
    async with session.begin():
        # Outer transaction
        user = User(name="Alice", email="alice@example.com")
        session.add(user)

        try:
            async with session.begin_nested():
                # Nested transaction (savepoint)
                post = Post(title="First Post", user_id=user.id)
                session.add(post)

                # Simulate error
                if post.title == "First Post":
                    raise ValueError("Post title validation failed")

        except ValueError:
            # Inner transaction rolled back, outer continues
            logger.warning("Post creation failed, but user still created")

        # Outer transaction commits successfully
```

### Transaction Decorator

```python
from functools import wraps
from typing import TypeVar, Callable, Any, ParamSpec
from sqlalchemy.ext.asyncio import AsyncSession

P = ParamSpec('P')
T = TypeVar('T')

def transactional(
    commit_on_success: bool = True,
    rollback_on_error: bool = True
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to wrap function in transaction.

    Usage:
        @transactional()
        async def create_user(session: AsyncSession, name: str) -> User:
            user = User(name=name)
            session.add(user)
            return user
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Get session from args or kwargs
            session = kwargs.get('session') or args[0]
            if not isinstance(session, AsyncSession):
                raise ValueError("First argument must be AsyncSession")

            try:
                async with session.begin():
                    result = await func(*args, **kwargs)

                    if commit_on_success:
                        await session.commit()

                    return result

            except Exception as e:
                if rollback_on_error:
                    await session.rollback()

                logger.error(f"Transaction failed in {func.__name__}: {e}")
                raise

        return wrapper
    return decorator

# Usage
@transactional()
async def create_user_with_posts(
    session: AsyncSession,
    user_data: dict,
    posts_data: list[dict]
) -> User:
    """Create user and posts in one transaction."""
    user = User(**user_data)
    session.add(user)
    await session.flush()  # Get user.id

    for post_data in posts_data:
        post = Post(**post_data, user_id=user.id)
        session.add(post)

    return user
```

### Transaction Isolation Levels

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Set isolation level at engine level
engine = create_async_engine(
    "postgresql+asyncpg://localhost/db",
    isolation_level="REPEATABLE READ"  # Options: READ COMMITTED, REPEATABLE READ, SERIALIZABLE
)

# Set isolation level per session
from sqlalchemy import Connection

async def transaction_with_isolation(
    session: AsyncSession,
    isolation_level: str = "SERIALIZABLE"
) -> None:
    """
    Execute transaction with specific isolation level.

    Isolation levels (strongest to weakest):
    - SERIALIZABLE: Full isolation, may have performance impact
    - REPEATABLE READ: Prevents dirty and non-repeatable reads
    - READ COMMITTED: Default in PostgreSQL
    - READ UNCOMMITTED: Lowest isolation
    """
    await session.execute(
        f"SET TRANSACTION ISOLATION LEVEL {isolation_level}"
    )

    async with session.begin():
        # Execute operations with specified isolation
        result = await session.execute(select(User).where(User.id == 1))
        user = result.scalar_one()
        user.balance += 100
```

### Transaction Retry Logic

```python
import asyncio
from typing import TypeVar, Callable, Awaitable
from sqlalchemy.exc import OperationalError, IntegrityError

T = TypeVar('T')

async def retry_transaction(
    func: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    exceptions: tuple = (OperationalError,)
) -> T:
    """
    Retry transaction on specific exceptions.

    Useful for handling deadlocks and temporary connection issues.

    Args:
        func: Async function to execute
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier
        exceptions: Exceptions to retry on

    Returns:
        Result of successful execution

    Raises:
        Last exception if all retries fail
    """
    last_exception: Exception | None = None

    for attempt in range(max_retries):
        try:
            return await func()

        except exceptions as e:
            last_exception = e
            logger.warning(
                f"Transaction attempt {attempt + 1} failed: {e}. "
                f"Retrying..."
            )

            if attempt < max_retries - 1:
                # Exponential backoff
                delay = backoff_factor * (2 ** attempt)
                await asyncio.sleep(delay)
            else:
                logger.error(f"Transaction failed after {max_retries} attempts")

    if last_exception:
        raise last_exception

    raise RuntimeError("Unexpected error in retry_transaction")

# Usage
async def transfer_money(
    from_user_id: int,
    to_user_id: int,
    amount: float,
    session: AsyncSession
) -> None:
    """Transfer money with automatic retry on deadlock."""

    async def _transfer() -> None:
        async with session.begin():
            # Lock rows in consistent order to prevent deadlocks
            user_ids = sorted([from_user_id, to_user_id])

            from_user = await session.get(User, user_ids[0], with_for_update=True)
            to_user = await session.get(User, user_ids[1], with_for_update=True)

            if from_user.id == from_user_id:
                from_user.balance -= amount
                to_user.balance += amount
            else:
                to_user.balance -= amount
                from_user.balance += amount

    await retry_transaction(_transfer, max_retries=3)
```

### Unit of Work Pattern

```python
from typing import Generic, TypeVar, Protocol
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')

class Entity(Protocol):
    """Protocol for domain entities."""
    id: int

class UnitOfWork:
    """
    Unit of Work pattern for managing transactions.

    Tracks changes and commits them as a single unit.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._new: list[Any] = []
        self._dirty: list[Any] = []
        self._deleted: list[Any] = []

    def register_new(self, entity: Entity) -> None:
        """Register new entity to be inserted."""
        if entity.id is not None:
            raise ValueError("Entity already has ID")
        self._new.append(entity)

    def register_dirty(self, entity: Entity) -> None:
        """Register entity to be updated."""
        if entity.id is None:
            raise ValueError("Entity has no ID")
        if entity not in self._dirty and entity not in self._new:
            self._dirty.append(entity)

    def register_deleted(self, entity: Entity) -> None:
        """Register entity to be deleted."""
        if entity.id is None:
            raise ValueError("Entity has no ID")
        self._deleted.append(entity)

    async def commit(self) -> None:
        """Commit all changes as a transaction."""
        async with self._session.begin():
            # Insert new entities
            for entity in self._new:
                self._session.add(entity)

            # Update dirty entities
            for entity in self._dirty:
                await self._session.merge(entity)

            # Delete entities
            for entity in self._deleted:
                await self._session.delete(entity)

            await self._session.flush()

        # Clear tracking lists
        self._new.clear()
        self._dirty.clear()
        self._deleted.clear()

    async def rollback(self) -> None:
        """Rollback transaction and clear changes."""
        await self._session.rollback()
        self._new.clear()
        self._dirty.clear()
        self._deleted.clear()

# Usage
async def transfer_with_uow(
    from_user_id: int,
    to_user_id: int,
    amount: float,
    session: AsyncSession
) -> None:
    """Transfer money using Unit of Work pattern."""
    uow = UnitOfWork(session)

    try:
        # Fetch users
        from_user = await session.get(User, from_user_id)
        to_user = await session.get(User, to_user_id)

        # Modify entities
        from_user.balance -= amount
        to_user.balance += amount

        # Register changes
        uow.register_dirty(from_user)
        uow.register_dirty(to_user)

        # Create transaction record
        transaction = Transaction(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            amount=amount
        )
        uow.register_new(transaction)

        # Commit all changes
        await uow.commit()

    except Exception as e:
        await uow.rollback()
        raise
```

### Distributed Transaction Considerations

```python
from enum import Enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum

class TransactionStatus(str, Enum):
    """Transaction status for distributed systems."""
    PENDING = "pending"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"

class DistributedTransaction(Base):
    """
    Track distributed transaction state.

    For two-phase commit or saga patterns.
    """
    __tablename__ = "distributed_transactions"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(36), unique=True, nullable=False)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

async def two_phase_commit(
    operations: list[Callable[[], Awaitable[None]]],
    session: AsyncSession
) -> None:
    """
    Simple two-phase commit pattern.

    Phase 1: Prepare (validate all operations can succeed)
    Phase 2: Commit (execute all operations)
    """
    import uuid

    transaction_id = str(uuid.uuid4())

    # Create transaction record
    dt = DistributedTransaction(
        transaction_id=transaction_id,
        status=TransactionStatus.PENDING
    )
    session.add(dt)
    await session.commit()

    try:
        # Phase 1: Prepare
        for operation in operations:
            # Validate operation can succeed
            # In real implementation, this would call remote services
            pass

        # Phase 2: Commit
        for operation in operations:
            await operation()

        # Mark as committed
        dt.status = TransactionStatus.COMMITTED
        dt.completed_at = datetime.utcnow()
        await session.commit()

    except Exception as e:
        logger.error(f"Distributed transaction {transaction_id} failed: {e}")

        # Rollback
        dt.status = TransactionStatus.ROLLED_BACK
        dt.completed_at = datetime.utcnow()
        await session.commit()

        raise
```

### Transaction Testing Patterns

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
async def transactional_session(async_session: AsyncSession):
    """
    Fixture that rolls back transaction after test.

    Ensures tests don't affect database.
    """
    async with async_session.begin():
        yield async_session
        await async_session.rollback()

# Usage in tests
@pytest.mark.asyncio
async def test_create_user(transactional_session: AsyncSession):
    """Test user creation without affecting database."""
    user = User(name="Test User", email="test@example.com")
    transactional_session.add(user)
    await transactional_session.flush()

    assert user.id is not None

    # Changes rolled back after test
```

### Transaction Best Practices

```python
"""
Transaction Management Best Practices:

✅ DO:

1. Keep transactions short
   - Minimize time between begin and commit
   - Reduces lock contention

2. Handle exceptions properly
   - Always rollback on error
   - Log transaction failures

3. Use appropriate isolation levels
   - READ COMMITTED for most cases
   - SERIALIZABLE for critical operations

4. Acquire locks in consistent order
   - Prevents deadlocks
   - Sort IDs before locking

5. Use savepoints for partial rollback
   - Nested transactions when needed
   - Better error recovery

6. Retry on transient failures
   - Deadlocks, connection issues
   - Exponential backoff

7. Test transaction behavior
   - Concurrent access
   - Rollback scenarios

❌ DON'T:

1. Hold transactions open unnecessarily
   - No external API calls in transaction
   - No long computations

2. Ignore deadlocks
   - Implement retry logic
   - Acquire locks in order

3. Use autocommit for business logic
   - Explicit transactions better
   - More control

4. Nest transactions excessively
   - Complexity increases
   - Harder to debug

5. Forget isolation levels
   - Default may not be appropriate
   - Consider data consistency needs

EXAMPLE - Good Transaction Pattern:

async def transfer_money(
    from_id: int,
    to_id: int,
    amount: float,
    session: AsyncSession
) -> None:
    \"""Transfer money with proper transaction handling.\"""

    async def _transfer():
        async with session.begin():
            # Lock in consistent order
            ids = sorted([from_id, to_id])
            users = [
                await session.get(User, ids[0], with_for_update=True),
                await session.get(User, ids[1], with_for_update=True)
            ]

            # Find correct users
            from_user = users[0] if users[0].id == from_id else users[1]
            to_user = users[1] if users[1].id == to_id else users[0]

            # Validate
            if from_user.balance < amount:
                raise ValueError("Insufficient funds")

            # Execute transfer
            from_user.balance -= amount
            to_user.balance += amount

    # Retry on deadlock
    await retry_transaction(_transfer, max_retries=3)
"""
```

---

## 📝 Structured Logging with Structlog

### Basic Structlog Setup

```python
import structlog
from typing import Any

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

# Get logger
logger = structlog.get_logger()

# Usage
logger.info("user_login", user_id=123, ip="192.168.1.1", success=True)
logger.error("payment_failed", user_id=456, amount=99.99, reason="insufficient_funds")
```

### Development vs Production Configuration

```python
import structlog
import sys
from typing import Any

def configure_logging(environment: str = "development") -> None:
    """
    Configure structlog based on environment.

    Development: Human-readable console output
    Production: JSON for log aggregation systems
    """
    if environment == "development":
        # Development: Colorful console output
        processors = [
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()  # Pretty console output
        ]
    else:
        # Production: JSON output for ELK/CloudWatch
        processors = [
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()  # JSON for log aggregation
        ]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

# Configure on application startup
from mcp_server.config import settings
configure_logging(settings.environment)
```

### Context Binding

```python
import structlog
from typing import Any

logger = structlog.get_logger()

# Bind context that persists across log calls
logger = logger.bind(user_id=123, session_id="abc-def")

# All subsequent calls include bound context
logger.info("page_view", page="/home")
# Output: {"user_id": 123, "session_id": "abc-def", "event": "page_view", "page": "/home"}

logger.info("button_click", button_id="submit")
# Output: {"user_id": 123, "session_id": "abc-def", "event": "button_click", "button_id": "submit"}

# Create new logger with additional context
request_logger = logger.bind(request_id="req-789")
request_logger.info("request_started")
# Output: {"user_id": 123, "session_id": "abc-def", "request_id": "req-789", "event": "request_started"}
```

### FastAPI Integration

```python
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
import uuid
from typing import Callable

logger = structlog.get_logger()

class StructlogMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add request context to logs.

    Automatically binds request_id, method, path, and user info.
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Bind request context to logger
        request_logger = logger.bind(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None
        )

        # Add user context if authenticated
        user = getattr(request.state, "user", None)
        if user:
            request_logger = request_logger.bind(
                user_id=user.id,
                user_email=user.email
            )

        # Store logger in request state
        request.state.logger = request_logger

        # Log request start
        request_logger.info("request_started")

        try:
            # Process request
            response = await call_next(request)

            # Log request completion
            request_logger.info(
                "request_completed",
                status_code=response.status_code,
                content_length=response.headers.get("content-length")
            )

            return response

        except Exception as exc:
            # Log request error
            request_logger.error(
                "request_failed",
                exc_info=True,
                error_type=type(exc).__name__,
                error_message=str(exc)
            )
            raise

# Add middleware to FastAPI app
app = FastAPI()
app.add_middleware(StructlogMiddleware)

# Use logger in routes
@app.get("/users/{user_id}")
async def get_user(user_id: int, request: Request):
    """Get user with automatic logging."""
    logger = request.state.logger

    logger.info("fetching_user", user_id=user_id)

    try:
        user = await fetch_user(user_id)
        logger.info("user_fetched", user_id=user_id, user_name=user.name)
        return user

    except UserNotFound:
        logger.warning("user_not_found", user_id=user_id)
        raise HTTPException(status_code=404, detail="User not found")
```

### Custom Processors

```python
from typing import Any
import structlog

def add_service_name(
    logger: Any, name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add service name to all log entries."""
    event_dict["service"] = "api-server"
    event_dict["version"] = "1.0.0"
    return event_dict

def add_environment(
    logger: Any, name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add environment to all log entries."""
    from mcp_server.config import settings
    event_dict["environment"] = settings.environment
    return event_dict

def sanitize_sensitive_data(
    logger: Any, name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """
    Remove sensitive data from logs.

    Redacts passwords, tokens, credit cards, etc.
    """
    sensitive_keys = {"password", "token", "api_key", "credit_card", "ssn"}

    def _sanitize(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {
                k: "[REDACTED]" if k.lower() in sensitive_keys else _sanitize(v)
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [_sanitize(item) for item in obj]
        return obj

    return _sanitize(event_dict)

# Configure with custom processors
structlog.configure(
    processors=[
        add_service_name,
        add_environment,
        sanitize_sensitive_data,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
```

### Log Levels and Filtering

```python
import structlog
import logging

# Set log level
logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,  # Set minimum level
)

logger = structlog.get_logger()

# Different log levels
logger.debug("debug_message", detail="verbose debugging info")
logger.info("info_message", status="normal operation")
logger.warning("warning_message", issue="potential problem")
logger.error("error_message", error="something failed")
logger.critical("critical_message", emergency="system down")

# Dynamic log level based on environment
from mcp_server.config import settings

if settings.environment == "development":
    logging.root.setLevel(logging.DEBUG)
elif settings.environment == "staging":
    logging.root.setLevel(logging.INFO)
else:  # production
    logging.root.setLevel(logging.WARNING)
```

### Database Query Logging

```python
import structlog
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time

logger = structlog.get_logger()

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log query execution start."""
    conn.info.setdefault('query_start_time', []).append(time.time())
    logger.debug(
        "sql_query_started",
        statement=statement[:500],  # Truncate long queries
        parameters=parameters if len(str(parameters)) < 200 else "[TRUNCATED]"
    )

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log query execution completion."""
    total_time = time.time() - conn.info['query_start_time'].pop()

    # Log slow queries as warnings
    if total_time > 1.0:  # Queries slower than 1 second
        logger.warning(
            "slow_sql_query",
            duration_ms=total_time * 1000,
            statement=statement[:500]
        )
    else:
        logger.debug(
            "sql_query_completed",
            duration_ms=total_time * 1000
        )
```

### Exception Logging

```python
import structlog
from typing import Any

logger = structlog.get_logger()

def safe_division(a: float, b: float) -> float:
    """Divide with exception logging."""
    try:
        result = a / b
        logger.info("division_successful", a=a, b=b, result=result)
        return result

    except ZeroDivisionError:
        logger.error(
            "division_by_zero",
            a=a,
            b=b,
            exc_info=True  # Include stack trace
        )
        raise

    except Exception as e:
        logger.error(
            "unexpected_error",
            operation="division",
            a=a,
            b=b,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise

# FastAPI exception handler with logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Log all unhandled exceptions."""
    logger = getattr(request.state, "logger", structlog.get_logger())

    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error_type=type(exc).__name__,
        error_message=str(exc),
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )
```

### Performance Metrics Logging

```python
import structlog
import time
from functools import wraps
from typing import TypeVar, Callable, ParamSpec

P = ParamSpec('P')
T = TypeVar('T')

logger = structlog.get_logger()

def log_performance(operation: str) -> Callable:
    """
    Decorator to log function execution time.

    Usage:
        @log_performance("user_creation")
        async def create_user(data: dict) -> User:
            pass
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                logger.info(
                    "operation_completed",
                    operation=operation,
                    duration_ms=duration * 1000,
                    success=True
                )

                return result

            except Exception as e:
                duration = time.time() - start_time

                logger.error(
                    "operation_failed",
                    operation=operation,
                    duration_ms=duration * 1000,
                    success=False,
                    error_type=type(e).__name__
                )
                raise

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                logger.info(
                    "operation_completed",
                    operation=operation,
                    duration_ms=duration * 1000,
                    success=True
                )

                return result

            except Exception as e:
                duration = time.time() - start_time

                logger.error(
                    "operation_failed",
                    operation=operation,
                    duration_ms=duration * 1000,
                    success=False,
                    error_type=type(e).__name__
                )
                raise

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator

# Usage
@log_performance("database_query")
async def fetch_users(limit: int) -> list[User]:
    """Fetch users with performance logging."""
    return await db.query(User).limit(limit).all()
```

### Integration with ELK Stack

```python
import structlog
from pythonjsonlogger import jsonlogger
import logging

def configure_elk_logging() -> None:
    """
    Configure logging for ELK (Elasticsearch, Logstash, Kibana) stack.

    Outputs JSON logs with standardized fields for log aggregation.
    """
    # JSON formatter for ELK
    class CustomJSONFormatter(jsonlogger.JsonFormatter):
        """Custom JSON formatter with additional fields."""

        def add_fields(self, log_record, record, message_dict):
            super().add_fields(log_record, record, message_dict)

            # Add standard fields
            log_record['@timestamp'] = self.formatTime(record)
            log_record['level'] = record.levelname
            log_record['logger'] = record.name
            log_record['thread'] = record.threadName
            log_record['process'] = record.processName

            # Add service metadata
            log_record['service'] = 'api-server'
            log_record['environment'] = 'production'

    # Configure handler
    handler = logging.StreamHandler()
    handler.setFormatter(CustomJSONFormatter())

    # Configure root logger
    logging.root.handlers = [handler]
    logging.root.setLevel(logging.INFO)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
