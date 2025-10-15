# CLAUDE-architecture-observability.md - Logging & Caching


> **Specialized Guide**: Structured logging with structlog and caching strategies for Python applications.

> **Specialized Guide**: Comprehensive project architecture, modularity patterns, and design principles for Python projects.
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
from project_name.config import settings
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
    from project_name.config import settings
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
from project_name.config import settings

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
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

### Integration with CloudWatch

```python
import structlog
import watchtower
import logging
from botocore.session import Session

def configure_cloudwatch_logging(
    log_group: str,
    stream_name: str,
    region: str = "us-east-1"
) -> None:
    """
    Configure logging for AWS CloudWatch.

    Sends structured logs to CloudWatch Logs.
    """
    # Create CloudWatch handler
    boto3_session = Session()
    handler = watchtower.CloudWatchLogHandler(
        log_group=log_group,
        stream_name=stream_name,
        boto3_session=boto3_session,
        send_interval=5,  # Send logs every 5 seconds
        create_log_group=True
    )

    # Configure root logger
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.INFO)

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

# Usage
configure_cloudwatch_logging(
    log_group="/aws/lambda/api-server",
    stream_name="production"
)
```

### Complete Configuration Example

```python
# src/project_name/logging_config.py
import structlog
import logging
import sys
from typing import Any
from project_name.config import settings

def configure_logging() -> None:
    """
    Complete logging configuration.

    Configures structlog with environment-specific settings.
    """
    # Define processors
    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.environment == "development":
        # Development: Pretty console output
        processors = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(colors=True)
        ]
        log_level = logging.DEBUG

    else:
        # Production: JSON output
        processors = [
            *shared_processors,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ]
        log_level = logging.INFO

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

# Call on application startup
# In main.py:
from project_name.logging_config import configure_logging

configure_logging()
logger = structlog.get_logger()
logger.info("application_started", version="1.0.0")
```

---

## 💾 Caching Strategies

### LRU Cache Decorator

```python
from functools import lru_cache
from typing import Any

# Basic LRU cache
@lru_cache(maxsize=128)
def get_user_permissions(user_id: int) -> list[str]:
    """
    Get user permissions with caching.

    Cached for duration of application run.
    """
    # Expensive database query
    permissions = db.query(Permission).filter_by(user_id=user_id).all()
    return [p.name for p in permissions]

# Clear cache manually
get_user_permissions.cache_clear()

# Get cache statistics
stats = get_user_permissions.cache_info()
print(f"Hits: {stats.hits}, Misses: {stats.misses}")

# Cache with TTL using custom decorator
import time
from functools import wraps

def timed_lru_cache(seconds: int, maxsize: int = 128):
    """LRU cache with time-based expiration."""
    def wrapper(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = seconds
        func.expiration = time.time() + seconds

        @wraps(func)
        def wrapped(*args, **kwargs):
            if time.time() >= func.expiration:
                func.cache_clear()
                func.expiration = time.time() + func.lifetime

            return func(*args, **kwargs)

        return wrapped
    return wrapper

@timed_lru_cache(seconds=300, maxsize=100)  # 5 minutes
def get_config_value(key: str) -> str:
    """Get configuration with 5-minute cache."""
    return load_from_database(key)
```

### Redis Cache Patterns

```python
import redis.asyncio as redis
from typing import Any, Optional
import json
from datetime import timedelta

class RedisCache:
    """
    Redis cache wrapper with common patterns.

    Supports string, JSON, and binary data caching.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        return await self.redis.get(key)

    async def set(
        self,
        key: str,
        value: str,
        ttl: int | timedelta | None = None
    ) -> None:
        """
        Set value in cache with optional TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live (seconds or timedelta)
        """
        if isinstance(ttl, timedelta):
            ttl = int(ttl.total_seconds())

        if ttl:
            await self.redis.setex(key, ttl, value)
        else:
            await self.redis.set(key, value)

    async def get_json(self, key: str) -> Optional[dict]:
        """Get JSON value from cache."""
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set_json(
        self,
        key: str,
        value: dict,
        ttl: int | None = None
    ) -> None:
        """Set JSON value in cache."""
        await self.set(key, json.dumps(value), ttl)

    async def delete(self, key: str) -> None:
        """Delete key from cache."""
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return bool(await self.redis.exists(key))

    async def close(self) -> None:
        """Close Redis connection."""
        await self.redis.close()

# Usage
cache = RedisCache()

# Simple caching
await cache.set("user:123", "John Doe", ttl=3600)
name = await cache.get("user:123")

# JSON caching
user_data = {"id": 123, "name": "John", "email": "john@example.com"}
await cache.set_json("user:123:data", user_data, ttl=3600)
cached_user = await cache.get_json("user:123:data")
```

### Cache-Aside Pattern

```python
from typing import Optional
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

class UserCache:
    """
    Cache-aside pattern for user data.

    Flow:
    1. Check cache
    2. If miss, query database
    3. Store result in cache
    4. Return result
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.ttl = 3600  # 1 hour

    async def get_user(
        self,
        user_id: int,
        session: AsyncSession
    ) -> Optional[dict]:
        """
        Get user with cache-aside pattern.

        Cache key: user:{user_id}
        """
        cache_key = f"user:{user_id}"

        # 1. Try cache first
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # 2. Cache miss - query database
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        # 3. Store in cache
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
        await self.redis.setex(
            cache_key,
            self.ttl,
            json.dumps(user_data)
        )

        # 4. Return result
        return user_data

    async def invalidate_user(self, user_id: int) -> None:
        """Invalidate user cache on update."""
        cache_key = f"user:{user_id}"
        await self.redis.delete(cache_key)

# Usage
user_cache = UserCache(redis_client)

# Get user (from cache or database)
user = await user_cache.get_user(123, session)

# Update user (invalidate cache)
await update_user_in_db(123, {"name": "New Name"}, session)
await user_cache.invalidate_user(123)
```

### Write-Through Cache

```python
from typing import Any
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

class WriteThroughCache:
    """
    Write-through cache pattern.

    Writes go to cache and database simultaneously.
    Ensures cache is always consistent with database.
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.ttl = 3600

    async def create_user(
        self,
        user_data: dict,
        session: AsyncSession
    ) -> User:
        """
        Create user with write-through caching.

        1. Write to database
        2. Write to cache
        3. Return result
        """
        # 1. Write to database
        user = User(**user_data)
        session.add(user)
        await session.flush()  # Get ID

        # 2. Write to cache
        cache_key = f"user:{user.id}"
        await self.redis.setex(
            cache_key,
            self.ttl,
            json.dumps({
                "id": user.id,
                "name": user.name,
                "email": user.email
            })
        )

        # 3. Return result
        return user

    async def update_user(
        self,
        user_id: int,
        updates: dict,
        session: AsyncSession
    ) -> User:
        """
        Update user with write-through caching.

        Updates database and cache atomically.
        """
        # Update database
        user = await session.get(User, user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        for key, value in updates.items():
            setattr(user, key, value)

        await session.flush()

        # Update cache
        cache_key = f"user:{user.id}"
        await self.redis.setex(
            cache_key,
            self.ttl,
            json.dumps({
                "id": user.id,
                "name": user.name,
                "email": user.email
            })
        )

        return user
```

### Write-Behind (Write-Back) Cache

```python
import asyncio
from collections import deque
from typing import Deque
import redis.asyncio as redis

class WriteBehindCache:
    """
    Write-behind cache pattern.

    Writes go to cache immediately, database updated asynchronously.
    Higher performance but risk of data loss.
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        flush_interval: int = 60
    ):
        self.redis = redis_client
        self.flush_interval = flush_interval
        self.write_queue: Deque[dict] = deque()
        self._running = False

    async def start(self) -> None:
        """Start background flush task."""
        self._running = True
        asyncio.create_task(self._flush_worker())

    async def stop(self) -> None:
        """Stop background flush task."""
        self._running = False
        await self._flush_to_database()  # Final flush

    async def update_user(self, user_id: int, updates: dict) -> None:
        """
        Update user (cache immediately, database later).

        1. Update cache immediately
        2. Queue database write
        3. Background worker flushes to database
        """
        # 1. Update cache
        cache_key = f"user:{user_id}"
        cached = await self.redis.get(cache_key)

        if cached:
            user_data = json.loads(cached)
            user_data.update(updates)
        else:
            user_data = {"id": user_id, **updates}

        await self.redis.setex(cache_key, 3600, json.dumps(user_data))

        # 2. Queue database write
        self.write_queue.append({
            "user_id": user_id,
            "updates": updates
        })

    async def _flush_worker(self) -> None:
        """Background worker to flush writes to database."""
        while self._running:
            await asyncio.sleep(self.flush_interval)
            await self._flush_to_database()

    async def _flush_to_database(self) -> None:
        """Flush queued writes to database."""
        while self.write_queue:
            write = self.write_queue.popleft()

            try:
                # Write to database
                async with get_db_session() as session:
                    user = await session.get(User, write["user_id"])
                    if user:
                        for key, value in write["updates"].items():
                            setattr(user, key, value)
                        await session.commit()

            except Exception as e:
                # Re-queue on failure
                self.write_queue.append(write)
                logger.error(f"Failed to flush write: {e}")
                break
```

### Refresh-Ahead Cache

```python
import asyncio
from typing import Callable, Any
import redis.asyncio as redis

class RefreshAheadCache:
    """
    Refresh-ahead cache pattern.

    Proactively refreshes cache before expiration.
    Reduces cache misses for frequently accessed data.
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        ttl: int = 3600,
        refresh_threshold: float = 0.8
    ):
        self.redis = redis_client
        self.ttl = ttl
        self.refresh_threshold = refresh_threshold

    async def get_or_refresh(
        self,
        key: str,
        loader: Callable[[], Any]
    ) -> Any:
        """
        Get value from cache, refresh if near expiration.

        If TTL < threshold%, refresh in background.
        """
        # Get value and TTL
        cached_value = await self.redis.get(key)
        remaining_ttl = await self.redis.ttl(key)

        if not cached_value:
            # Cache miss - load and cache
            value = await loader()
            await self.redis.setex(key, self.ttl, json.dumps(value))
            return value

        # Check if refresh needed
        if remaining_ttl < self.ttl * self.refresh_threshold:
            # Refresh in background
            asyncio.create_task(self._background_refresh(key, loader))

        return json.loads(cached_value)

    async def _background_refresh(
        self,
        key: str,
        loader: Callable[[], Any]
    ) -> None:
        """Refresh cache in background."""
        try:
            value = await loader()
            await self.redis.setex(key, self.ttl, json.dumps(value))
        except Exception as e:
            logger.error(f"Background refresh failed: {e}")

# Usage
refresh_cache = RefreshAheadCache(redis_client, ttl=3600)

async def load_user_stats(user_id: int) -> dict:
    """Expensive operation to load user stats."""
    return await calculate_user_stats(user_id)

# Get with auto-refresh
stats = await refresh_cache.get_or_refresh(
    f"user:{user_id}:stats",
    lambda: load_user_stats(user_id)
)
```

### Cache Invalidation Strategies

```python
from typing import List
import redis.asyncio as redis

class CacheInvalidator:
    """
    Cache invalidation patterns.

    Supports various invalidation strategies.
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def invalidate_key(self, key: str) -> None:
        """Invalidate single cache key."""
        await self.redis.delete(key)

    async def invalidate_pattern(self, pattern: str) -> None:
        """
        Invalidate keys matching pattern.

        Example: invalidate_pattern("user:*")
        """
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(
                cursor,
                match=pattern,
                count=100
            )

            if keys:
                await self.redis.delete(*keys)

            if cursor == 0:
                break

    async def invalidate_tags(self, tags: List[str]) -> None:
        """
        Invalidate cache entries by tags.

        Uses Redis sets to track tagged entries.
        """
        for tag in tags:
            # Get all keys with this tag
            tag_key = f"tag:{tag}"
            keys = await self.redis.smembers(tag_key)

            if keys:
                # Delete all tagged keys
                await self.redis.delete(*keys)

                # Delete tag set
                await self.redis.delete(tag_key)

    async def set_with_tags(
        self,
        key: str,
        value: str,
        tags: List[str],
        ttl: int | None = None
    ) -> None:
        """
        Set cache value with tags for group invalidation.

        Example:
            await set_with_tags(
                "post:123",
                post_data,
                tags=["user:456", "category:tech"]
            )
        """
        # Set value
        if ttl:
            await self.redis.setex(key, ttl, value)
        else:
            await self.redis.set(key, value)

        # Add to tag sets
        for tag in tags:
            tag_key = f"tag:{tag}"
            await self.redis.sadd(tag_key, key)

            # Set TTL on tag set if value has TTL
            if ttl:
                await self.redis.expire(tag_key, ttl)

# Usage
invalidator = CacheInvalidator(redis_client)

# Set post with tags
await invalidator.set_with_tags(
    "post:123",
    json.dumps(post_data),
    tags=["user:456", "category:tech"],
    ttl=3600
)

# Invalidate all posts by user
await invalidator.invalidate_tags(["user:456"])

# Invalidate all user-related caches
await invalidator.invalidate_pattern("user:456:*")
```

### Distributed Caching with Redis Cluster

```python
from redis.cluster import RedisCluster, ClusterNode

class DistributedCache:
    """
    Distributed cache using Redis Cluster.

    Ensures cache consistency across multiple servers.
    """

    def __init__(self, nodes: List[ClusterNode]):
        self.redis = RedisCluster(
            startup_nodes=nodes,
            decode_responses=True,
            skip_full_coverage_check=True
        )

    async def get(self, key: str) -> Optional[str]:
        """Get value from distributed cache."""
        return await self.redis.get(key)

    async def set(
        self,
        key: str,
        value: str,
        ttl: int | None = None
    ) -> None:
        """Set value in distributed cache."""
        if ttl:
            await self.redis.setex(key, ttl, value)
        else:
            await self.redis.set(key, value)

    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Atomic increment in distributed cache.

        Useful for counters, rate limiting, etc.
        """
        return await self.redis.incrby(key, amount)

    async def get_or_compute(
        self,
        key: str,
        compute_fn: Callable[[], Any],
        ttl: int = 3600
    ) -> Any:
        """
        Get from cache or compute if missing (distributed-safe).

        Uses distributed lock to prevent cache stampede.
        """
        # Try cache first
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)

        # Acquire distributed lock
        lock_key = f"lock:{key}"
        lock_acquired = await self.redis.set(
            lock_key,
            "1",
            nx=True,  # Only set if not exists
            ex=30  # Lock expires in 30 seconds
        )

        if lock_acquired:
            try:
                # Compute value
                value = await compute_fn()

                # Cache result
                await self.redis.setex(key, ttl, json.dumps(value))

                return value

            finally:
                # Release lock
                await self.redis.delete(lock_key)
        else:
            # Wait for other process to compute
            for _ in range(30):
                await asyncio.sleep(0.1)
                cached = await self.redis.get(key)
                if cached:
                    return json.loads(cached)

            # Fallback: compute without lock
            return await compute_fn()

# Initialize distributed cache
distributed_cache = DistributedCache([
    ClusterNode("redis-node-1", 6379),
    ClusterNode("redis-node-2", 6379),
    ClusterNode("redis-node-3", 6379)
])
```

### Cache Key Design Patterns

```python
"""
Cache Key Design Best Practices:

1. Hierarchical Keys
   Format: {resource}:{id}:{subresource}

   Examples:
   - user:123
   - user:123:profile
   - user:123:posts
   - post:456:comments

2. Versioned Keys
   Format: {resource}:{id}:v{version}

   Examples:
   - user:123:v2
   - config:app:v3

   Benefit: Easy cache invalidation on schema changes

3. Computed Keys
   Format: {resource}:{params_hash}

   Example:
   - search:a1b2c3d4  (hash of search params)

4. Time-Based Keys
   Format: {resource}:{timestamp}

   Examples:
   - stats:daily:2024-01-15
   - metrics:hourly:2024-01-15-14

5. Namespace Keys
   Format: {namespace}:{resource}:{id}

   Examples:
   - prod:user:123
   - staging:user:123
"""

class CacheKeyBuilder:
    """Helper to build consistent cache keys."""

    def __init__(self, namespace: str = ""):
        self.namespace = namespace

    def user_key(self, user_id: int) -> str:
        """Build user cache key."""
        return f"{self.namespace}:user:{user_id}"

    def user_posts_key(self, user_id: int) -> str:
        """Build user posts cache key."""
        return f"{self.namespace}:user:{user_id}:posts"

    def search_key(self, **params) -> str:
        """Build search cache key from parameters."""
        # Create deterministic hash of params
        import hashlib
        params_str = json.dumps(params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"{self.namespace}:search:{params_hash}"

# Usage
keys = CacheKeyBuilder(namespace="prod")
user_key = keys.user_key(123)  # "prod:user:123"
posts_key = keys.user_posts_key(123)  # "prod:user:123:posts"
```

### Complete Caching Example

```python
from typing import Optional, List
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

class UserCacheService:
    """
    Complete caching service for users.

    Implements cache-aside pattern with proper invalidation.
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.ttl = 3600  # 1 hour

    async def get_user(
        self,
        user_id: int,
        session: AsyncSession
    ) -> Optional[dict]:
        """Get user with caching."""
        cache_key = f"user:{user_id}"

        # Try cache
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # Query database
        user = await session.get(User, user_id)
        if not user:
            return None

        # Cache result
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at.isoformat()
        }
        await self.redis.setex(cache_key, self.ttl, json.dumps(user_data))

        return user_data

    async def create_user(
        self,
        user_data: dict,
        session: AsyncSession
    ) -> User:
        """Create user and cache."""
        # Create in database
        user = User(**user_data)
        session.add(user)
        await session.flush()

        # Cache immediately (write-through)
        cache_key = f"user:{user.id}"
        await self.redis.setex(
            cache_key,
            self.ttl,
            json.dumps({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at.isoformat()
            })
        )

        return user

    async def update_user(
        self,
        user_id: int,
        updates: dict,
        session: AsyncSession
    ) -> User:
        """Update user and invalidate cache."""
        # Update database
        user = await session.get(User, user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        for key, value in updates.items():
            setattr(user, key, value)

        await session.flush()

        # Invalidate cache
        await self.invalidate_user(user_id)

        return user

    async def invalidate_user(self, user_id: int) -> None:
        """Invalidate all user-related caches."""
        # Invalidate user cache
        await self.redis.delete(f"user:{user_id}")

        # Invalidate related caches
        await self.redis.delete(f"user:{user_id}:posts")
        await self.redis.delete(f"user:{user_id}:stats")
```

---

## 📊 Database Models

### SQLAlchemy Models

```python
# src/project_name/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from ..core.database import Base

class User(Base):
    """User database model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
```

---

## ⚠️ Architecture Best Practices

1. **Follow src layout** - Better test isolation
2. **Use dependency injection** - Easier testing and flexibility
3. **Separate concerns** - Models, services, repositories, routes
4. **Keep modules focused** - Single responsibility
5. **Use feature slices** - Group related functionality
6. **Handle exceptions centrally** - Custom exception handlers
7. **Validate at boundaries** - API layer validation
8. **Keep business logic in services** - Not in routes
9. **Use repositories for data access** - Abstract database operations
10. **Document architecture decisions** - ADR (Architecture Decision Records)

---

## 📋 Architecture Checklist

- [ ] Follows src layout structure
- [ ] Clear separation of concerns (models, services, repos, routes)
- [ ] Dependency injection implemented
- [ ] Custom exceptions defined
- [ ] Exception handlers configured
- [ ] Repository pattern for data access
- [ ] Service layer for business logic
- [ ] API routes are thin (delegate to services)
- [ ] Tests organized by type (unit, integration, e2e)
- [ ] Configuration management with Pydantic

---

**Back to [Core Guide](./CLAUDE-core.md)**
