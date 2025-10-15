# CLAUDE-typing.md - Type Safety & Annotations

> **Specialized Guide**: Comprehensive type hints, annotations, and type safety patterns for Python projects.

## 🎯 Type Hints Philosophy

### Why Type Hints?
- **Catch errors early** - Before runtime
- **Better IDE support** - Autocomplete, refactoring, navigation
- **Self-documenting code** - Types explain intent
- **Easier refactoring** - Confidence in changes
- **Team collaboration** - Shared understanding of data structures

### Type Hints Are Mandatory
- Always use type hints for function signatures
- All public APIs must be fully typed
- Use `mypy --strict` to enforce type safety
- No `Any` type unless absolutely necessary

---

## 📚 Basic Type Annotations

### Function Signatures

```python
from typing import Optional

def greet(name: str) -> str:
    """Greet a person by name."""
    return f"Hello, {name}!"

def calculate_total(items: list[float], tax_rate: float = 0.1) -> float:
    """Calculate total price with tax."""
    subtotal = sum(items)
    return subtotal * (1 + tax_rate)

def find_user(user_id: int) -> Optional[dict]:
    """Find user by ID, returns None if not found."""
    # Implementation
    return None
```

### Variable Annotations

```python
# Basic types
count: int = 0
price: float = 9.99
name: str = "Product"
is_active: bool = True

# Collections
items: list[str] = ["apple", "banana", "cherry"]
scores: dict[str, int] = {"alice": 95, "bob": 87}
unique_ids: set[int] = {1, 2, 3}
coordinates: tuple[float, float] = (10.5, 20.3)

# Optional values
middle_name: Optional[str] = None
data: dict[str, any] | None = None  # Python 3.10+
```

---

## 🔧 Modern Type Syntax (Python 3.9+)

### Built-in Generic Types

```python
# Python 3.9+ - Use built-in generics instead of typing module
def process_items(items: list[str]) -> dict[str, int]:
    """Process items and return counts."""
    return {item: len(item) for item in items}

def merge_dicts(d1: dict[str, int], d2: dict[str, int]) -> dict[str, int]:
    """Merge two dictionaries."""
    return d1 | d2

def get_first(items: tuple[str, ...]) -> str | None:
    """Get first item from tuple."""
    return items[0] if items else None
```

### Union Types (Python 3.10+)

```python
# Old style (still valid)
from typing import Union, Optional
def process(value: Union[int, str]) -> Optional[str]:
    pass

# New style (Python 3.10+)
def process(value: int | str) -> str | None:
    """Process integer or string value."""
    if isinstance(value, int):
        return str(value)
    return value
```

---

## 🏗️ Advanced Type Annotations

### Type Aliases

```python
from typing import TypeAlias

# Simple type aliases
UserId: TypeAlias = int
Email: TypeAlias = str
JSON: TypeAlias = dict[str, any]

# Complex type aliases
UserData: TypeAlias = dict[str, str | int | bool]
ResponseData: TypeAlias = tuple[int, dict[str, any]]

# Using aliases
def get_user(user_id: UserId) -> UserData:
    """Get user data by ID."""
    return {"id": user_id, "name": "John", "active": True}

def send_email(recipient: Email, subject: str) -> bool:
    """Send email to recipient."""
    return True
```

### TypeVar and Generics

```python
from typing import TypeVar, Generic, Protocol

# Simple TypeVar
T = TypeVar('T')

def first_item(items: list[T]) -> T | None:
    """Get first item from list."""
    return items[0] if items else None

# Constrained TypeVar
NumberT = TypeVar('NumberT', int, float)

def add_numbers(a: NumberT, b: NumberT) -> NumberT:
    """Add two numbers of the same type."""
    return a + b

# Generic classes
K = TypeVar('K')
V = TypeVar('V')

class Cache(Generic[K, V]):
    """Generic cache implementation."""

    def __init__(self) -> None:
        self._data: dict[K, V] = {}

    def get(self, key: K) -> V | None:
        """Get value from cache."""
        return self._data.get(key)

    def set(self, key: K, value: V) -> None:
        """Set value in cache."""
        self._data[key] = value

# Usage
string_cache: Cache[str, str] = Cache()
int_cache: Cache[int, dict] = Cache()
```

### Protocols (Structural Typing)

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    """Protocol for drawable objects."""

    def draw(self) -> None:
        """Draw the object."""
        ...

@runtime_checkable
class Comparable(Protocol):
    """Protocol for comparable objects."""

    def __lt__(self, other: "Comparable") -> bool:
        """Less than comparison."""
        ...

    def __gt__(self, other: "Comparable") -> bool:
        """Greater than comparison."""
        ...

# Usage
def render(obj: Drawable) -> None:
    """Render any drawable object."""
    obj.draw()

def sort_items(items: list[Comparable]) -> list[Comparable]:
    """Sort items that implement Comparable protocol."""
    return sorted(items)
```

---

## 📦 Collections and Iterables

### Sequence Types

```python
from collections.abc import Sequence, Mapping, Iterable, Iterator

def process_sequence(items: Sequence[str]) -> list[str]:
    """Process any sequence type (list, tuple, etc)."""
    return [item.upper() for item in items]

def count_items(items: Iterable[any]) -> int:
    """Count items in any iterable."""
    return sum(1 for _ in items)

def get_value(data: Mapping[str, int], key: str) -> int:
    """Get value from any mapping type."""
    return data.get(key, 0)
```

### Generator and Iterator Types

```python
from collections.abc import Iterator, Generator
from typing import Any

def count_up(n: int) -> Iterator[int]:
    """Generate numbers from 0 to n-1."""
    for i in range(n):
        yield i

def process_lines(filename: str) -> Generator[str, None, None]:
    """Generate processed lines from file."""
    with open(filename) as f:
        for line in f:
            yield line.strip()

def fibonacci() -> Generator[int, None, None]:
    """Generate Fibonacci sequence."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b
```

---

## 🎨 Callable and Function Types

### Function Type Annotations

```python
from collections.abc import Callable

def apply_operation(
    value: int,
    operation: Callable[[int], int]
) -> int:
    """Apply operation to value."""
    return operation(value)

def retry(
    func: Callable[..., T],
    max_attempts: int = 3
) -> Callable[..., T]:
    """Decorator to retry function on failure."""
    def wrapper(*args: Any, **kwargs: Any) -> T:
        for _ in range(max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception:
                continue
        return func(*args, **kwargs)
    return wrapper

# Specific callable signatures
Validator: TypeAlias = Callable[[str], bool]
Transformer: TypeAlias = Callable[[dict], dict]
ErrorHandler: TypeAlias = Callable[[Exception], None]
```

---

## 📝 TypedDict and Structured Data

### TypedDict for Dictionaries

```python
from typing import TypedDict, NotRequired

class UserDict(TypedDict):
    """Typed dictionary for user data."""
    id: int
    name: str
    email: str
    is_active: bool

class UserCreateDict(TypedDict):
    """Typed dict for user creation (id is optional)."""
    id: NotRequired[int]
    name: str
    email: str
    is_active: NotRequired[bool]

# Usage
def create_user(data: UserCreateDict) -> UserDict:
    """Create user from input data."""
    return {
        "id": data.get("id", 0),
        "name": data["name"],
        "email": data["email"],
        "is_active": data.get("is_active", True),
    }
```

### Literal Types

```python
from typing import Literal

Status: TypeAlias = Literal["pending", "approved", "rejected"]
LogLevel: TypeAlias = Literal["debug", "info", "warning", "error"]

def set_status(status: Status) -> None:
    """Set status to one of allowed values."""
    print(f"Status: {status}")

def log(message: str, level: LogLevel = "info") -> None:
    """Log message with specified level."""
    print(f"[{level.upper()}] {message}")
```

---

## 🔄 Self Type and Method Chaining

### Self Type (Python 3.11+)

```python
from typing import Self

class Builder:
    """Fluent builder with method chaining."""

    def __init__(self) -> None:
        self._data: dict[str, any] = {}

    def add_field(self, key: str, value: any) -> Self:
        """Add field and return self for chaining."""
        self._data[key] = value
        return self

    def remove_field(self, key: str) -> Self:
        """Remove field and return self for chaining."""
        self._data.pop(key, None)
        return self

    def build(self) -> dict[str, any]:
        """Build final dictionary."""
        return self._data.copy()

# Usage with type safety
result = (Builder()
    .add_field("name", "John")
    .add_field("age", 30)
    .remove_field("temp")
    .build())
```

---

## 🔐 Type Guards and Narrowing

### Type Guards

```python
from typing import TypeGuard

def is_string_list(value: list[any]) -> TypeGuard[list[str]]:
    """Check if list contains only strings."""
    return all(isinstance(item, str) for item in value)

def process_data(items: list[any]) -> None:
    """Process data with type narrowing."""
    if is_string_list(items):
        # items is now typed as list[str]
        for item in items:
            print(item.upper())
```

### isinstance Checks

```python
def process_value(value: int | str | None) -> str:
    """Process value with type narrowing."""
    if value is None:
        return "empty"
    elif isinstance(value, int):
        return str(value)
    else:
        return value.upper()
```

---

## 🏛️ Class Type Annotations

### Dataclass with Types

```python
from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar

@dataclass
class User:
    """User model with type annotations."""
    id: int
    name: str
    email: str
    created_at: datetime
    is_active: bool = True

    # Class variable
    table_name: ClassVar[str] = "users"

    def get_display_name(self) -> str:
        """Get display name."""
        return self.name.title()
```

### Generic Repository Pattern

```python
from typing import TypeVar, Generic, Protocol
from abc import abstractmethod

T = TypeVar('T')

class Entity(Protocol):
    """Protocol for entities with ID."""
    id: int

class Repository(Generic[T]):
    """Generic repository for CRUD operations."""

    def __init__(self) -> None:
        self._data: dict[int, T] = {}

    def find_by_id(self, id_: int) -> T | None:
        """Find entity by ID."""
        return self._data.get(id_)

    def find_all(self) -> list[T]:
        """Find all entities."""
        return list(self._data.values())

    def save(self, entity: T) -> T:
        """Save entity."""
        self._data[entity.id] = entity
        return entity

    def delete(self, id_: int) -> bool:
        """Delete entity by ID."""
        if id_ in self._data:
            del self._data[id_]
            return True
        return False

# Usage
user_repo: Repository[User] = Repository()
```

---

## 🔀 Async Type Annotations

### Async Functions and Coroutines

```python
from typing import Awaitable, Coroutine
from collections.abc import AsyncIterator, AsyncGenerator

async def fetch_data(url: str) -> dict[str, any]:
    """Fetch data asynchronously."""
    # Implementation
    return {}

async def process_async(coro: Awaitable[T]) -> T:
    """Process any awaitable."""
    return await coro

async def stream_data(source: str) -> AsyncIterator[dict]:
    """Stream data asynchronously."""
    for i in range(10):
        yield {"index": i, "data": f"item_{i}"}

async def generate_items(n: int) -> AsyncGenerator[int, None]:
    """Generate items asynchronously."""
    for i in range(n):
        yield i
```

---

## 🔄 Async Context Managers & Patterns

### Basic Async Context Manager

```python
from typing import AsyncContextManager, Self
from types import TracebackType

class AsyncResource:
    """
    Basic async context manager for resource management.

    Ensures proper cleanup with async/await.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.is_open = False

    async def __aenter__(self) -> Self:
        """Acquire resource asynchronously."""
        print(f"Opening {self.name}")
        await self._open()
        self.is_open = True
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Release resource asynchronously."""
        print(f"Closing {self.name}")
        await self._close()
        self.is_open = False

        # Return False to propagate exceptions
        # Return True to suppress exceptions
        return None

    async def _open(self) -> None:
        """Open resource."""
        # Simulate async operation
        import asyncio
        await asyncio.sleep(0.1)

    async def _close(self) -> None:
        """Close resource."""
        # Simulate async operation
        import asyncio
        await asyncio.sleep(0.1)

# Usage
async def example() -> None:
    async with AsyncResource("database") as resource:
        print(f"Using {resource.name}")
        # Resource automatically closed on exit
```

### Database Connection Async Context Manager

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncIterator
from contextlib import asynccontextmanager

class DatabaseConfig:
    """Database configuration."""
    database_url: str = "postgresql+asyncpg://user:pass@localhost/db"
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False

class Database:
    """
    Database connection manager with async context.

    Provides async session lifecycle management.
    """

    def __init__(self, config: DatabaseConfig) -> None:
        self.config = config
        self._engine = create_async_engine(
            config.database_url,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            echo=config.echo,
        )
        self._session_maker = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def __aenter__(self) -> AsyncSession:
        """Create new database session."""
        self._session = self._session_maker()
        return self._session

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Close database session."""
        await self._session.close()

    async def close(self) -> None:
        """Close database engine."""
        await self._engine.dispose()

# Usage
db = Database(DatabaseConfig())

async def get_user(user_id: int) -> dict[str, any]:
    async with db as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        return {"id": user.id, "name": user.name} if user else {}
```

### asynccontextmanager Decorator

```python
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncIterator

@asynccontextmanager
async def get_db_session() -> AsyncIterator[AsyncSession]:
    """
    Create database session with automatic cleanup.

    Decorator-based async context manager - simpler than class-based.
    """
    engine = create_async_engine("postgresql+asyncpg://localhost/db")
    async_session = async_sessionmaker(engine, class_=AsyncSession)

    session = async_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
        await engine.dispose()

# Usage
async def create_user(name: str, email: str) -> User:
    async with get_db_session() as session:
        user = User(name=name, email=email)
        session.add(user)
        # Automatic commit on success, rollback on error
        return user
```

### HTTP Client Session Management

```python
import aiohttp
from typing import AsyncIterator
from contextlib import asynccontextmanager

@asynccontextmanager
async def http_session(
    base_url: str,
    timeout: int = 30,
    headers: dict[str, str] | None = None
) -> AsyncIterator[aiohttp.ClientSession]:
    """
    Create HTTP client session with automatic cleanup.

    Features:
    - Connection pooling
    - Automatic cookie handling
    - Timeout configuration
    - Header management
    """
    timeout_config = aiohttp.ClientTimeout(total=timeout)

    async with aiohttp.ClientSession(
        base_url=base_url,
        timeout=timeout_config,
        headers=headers or {}
    ) as session:
        yield session

# Usage
async def fetch_user_data(user_id: int) -> dict[str, any]:
    """Fetch user data from API."""
    async with http_session("https://api.example.com") as session:
        async with session.get(f"/users/{user_id}") as response:
            response.raise_for_status()
            return await response.json()

# Multiple requests with same session
async def fetch_multiple_users(user_ids: list[int]) -> list[dict[str, any]]:
    """Fetch multiple users efficiently with connection pooling."""
    results: list[dict[str, any]] = []

    async with http_session("https://api.example.com") as session:
        for user_id in user_ids:
            async with session.get(f"/users/{user_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    results.append(data)

    return results
```

### File I/O Async Context Manager

```python
import aiofiles
from typing import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

@asynccontextmanager
async def async_open_file(
    filepath: str | Path,
    mode: str = "r",
    encoding: str = "utf-8"
) -> AsyncIterator[aiofiles.threadpool.text.AsyncTextIOWrapper]:
    """
    Open file asynchronously with automatic closure.

    Uses aiofiles for non-blocking file I/O.
    """
    file = await aiofiles.open(filepath, mode=mode, encoding=encoding)
    try:
        yield file
    finally:
        await file.close()

# Usage
async def read_config(config_path: str) -> dict[str, any]:
    """Read configuration file asynchronously."""
    async with async_open_file(config_path, "r") as f:
        content = await f.read()
        return json.loads(content)

async def write_log(log_path: str, message: str) -> None:
    """Write to log file asynchronously."""
    async with async_open_file(log_path, "a") as f:
        timestamp = datetime.now().isoformat()
        await f.write(f"[{timestamp}] {message}\n")
```

### Resource Pool Async Context Manager

```python
import asyncio
from typing import AsyncIterator, Generic, TypeVar
from contextlib import asynccontextmanager

T = TypeVar('T')

class AsyncPool(Generic[T]):
    """
    Generic async resource pool with context management.

    Features:
    - Resource pooling
    - Automatic cleanup
    - Size limits
    - Timeout handling
    """

    def __init__(self, max_size: int = 10) -> None:
        self._available: asyncio.Queue[T] = asyncio.Queue(maxsize=max_size)
        self._in_use: set[T] = set()
        self._max_size = max_size

    async def add_resource(self, resource: T) -> None:
        """Add resource to pool."""
        await self._available.put(resource)

    @asynccontextmanager
    async def acquire(self, timeout: float = 10.0) -> AsyncIterator[T]:
        """
        Acquire resource from pool with timeout.

        Automatically returns resource to pool on exit.
        """
        try:
            resource = await asyncio.wait_for(
                self._available.get(),
                timeout=timeout
            )
            self._in_use.add(resource)
            yield resource
        except asyncio.TimeoutError:
            raise TimeoutError(f"Failed to acquire resource within {timeout}s")
        finally:
            if resource in self._in_use:
                self._in_use.remove(resource)
                await self._available.put(resource)

    async def close_all(self) -> None:
        """Close all resources in pool."""
        while not self._available.empty():
            resource = await self._available.get()
            if hasattr(resource, 'close'):
                await resource.close()

# Usage with database connections
db_pool: AsyncPool[AsyncSession] = AsyncPool(max_size=10)

async def init_pool() -> None:
    """Initialize connection pool."""
    for _ in range(10):
        session = create_async_session()
        await db_pool.add_resource(session)

async def query_with_pool(query: str) -> list[dict]:
    """Execute query using pooled connection."""
    async with db_pool.acquire(timeout=5.0) as session:
        result = await session.execute(query)
        return [dict(row) for row in result]
```

### Nested Async Context Managers

```python
from contextlib import asynccontextmanager
from typing import AsyncIterator

@asynccontextmanager
async def transaction_context(
    session: AsyncSession
) -> AsyncIterator[AsyncSession]:
    """Transaction context with automatic commit/rollback."""
    async with session.begin():
        try:
            yield session
        except Exception:
            await session.rollback()
            raise

@asynccontextmanager
async def audit_context(
    session: AsyncSession,
    user_id: int,
    action: str
) -> AsyncIterator[AsyncSession]:
    """Audit context that logs actions."""
    start_time = datetime.now()
    try:
        yield session
        # Log successful action
        await log_audit(session, user_id, action, "success", start_time)
    except Exception as e:
        # Log failed action
        await log_audit(session, user_id, action, f"failed: {e}", start_time)
        raise

# Usage with nested contexts
async def update_user_with_audit(
    user_id: int,
    data: dict[str, any],
    admin_id: int
) -> User:
    """Update user with transaction and audit logging."""
    async with get_db_session() as session:
        async with transaction_context(session):
            async with audit_context(session, admin_id, "update_user"):
                user = await session.get(User, user_id)
                if not user:
                    raise ValueError(f"User {user_id} not found")

                for key, value in data.items():
                    setattr(user, key, value)

                return user
```

### Async Generator Context Manager

```python
from typing import AsyncGenerator
from contextlib import asynccontextmanager

@asynccontextmanager
async def stream_large_file(
    filepath: str,
    chunk_size: int = 8192
) -> AsyncGenerator[bytes, None]:
    """
    Stream large file in chunks with context management.

    Combines async generator with context manager.
    """
    async with aiofiles.open(filepath, 'rb') as f:
        try:
            while chunk := await f.read(chunk_size):
                yield chunk
        finally:
            # Cleanup handled by aiofiles context
            pass

# Usage
async def process_large_file(filepath: str) -> int:
    """Process large file without loading entire content."""
    total_bytes = 0

    async with stream_large_file(filepath) as chunks:
        async for chunk in chunks:
            total_bytes += len(chunk)
            await process_chunk(chunk)

    return total_bytes
```

### Timeout Async Context Manager

```python
import asyncio
from typing import AsyncIterator
from contextlib import asynccontextmanager

@asynccontextmanager
async def timeout_context(
    seconds: float
) -> AsyncIterator[None]:
    """
    Timeout context manager for async operations.

    Raises TimeoutError if operation exceeds limit.
    """
    try:
        async with asyncio.timeout(seconds):
            yield
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation exceeded {seconds}s timeout")

# Usage
async def fetch_with_timeout(url: str) -> dict[str, any]:
    """Fetch data with 5-second timeout."""
    async with timeout_context(5.0):
        async with http_session(url) as session:
            async with session.get("/data") as response:
                return await response.json()

# Nested with other contexts
async def safe_database_operation(user_id: int) -> User:
    """Database operation with timeout and transaction."""
    async with timeout_context(10.0):
        async with get_db_session() as session:
            async with transaction_context(session):
                return await get_user(session, user_id)
```

### Lock Async Context Manager

```python
import asyncio
from typing import AsyncIterator
from contextlib import asynccontextmanager

class AsyncLock:
    """
    Async lock with context manager support.

    Prevents race conditions in async code.
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()

    async def __aenter__(self) -> None:
        """Acquire lock."""
        await self._lock.acquire()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Release lock."""
        self._lock.release()

# Usage
user_locks: dict[int, AsyncLock] = {}

async def get_user_lock(user_id: int) -> AsyncLock:
    """Get or create lock for user."""
    if user_id not in user_locks:
        user_locks[user_id] = AsyncLock()
    return user_locks[user_id]

async def update_user_balance(user_id: int, amount: float) -> None:
    """Update user balance with lock to prevent race conditions."""
    lock = await get_user_lock(user_id)

    async with lock:
        # Critical section - only one coroutine can execute this
        async with get_db_session() as session:
            user = await session.get(User, user_id)
            user.balance += amount
            await session.commit()
```

### Error Handling in Async Context Managers

```python
from typing import AsyncIterator
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def resilient_connection(
    url: str,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> AsyncIterator[aiohttp.ClientSession]:
    """
    Connection with automatic retry and error handling.

    Handles connection failures gracefully.
    """
    session: aiohttp.ClientSession | None = None

    for attempt in range(max_retries):
        try:
            session = aiohttp.ClientSession()
            # Test connection
            async with session.get(url) as response:
                response.raise_for_status()

            yield session
            break

        except aiohttp.ClientError as e:
            logger.warning(f"Connection attempt {attempt + 1} failed: {e}")

            if session:
                await session.close()
                session = None

            if attempt == max_retries - 1:
                raise ConnectionError(f"Failed to connect after {max_retries} attempts")

            await asyncio.sleep(retry_delay * (attempt + 1))

    finally:
        if session:
            await session.close()

# Usage
async def fetch_with_retry(url: str) -> dict[str, any]:
    """Fetch data with automatic retry."""
    async with resilient_connection(url) as session:
        async with session.get("/api/data") as response:
            return await response.json()
```

### Async Context Manager Protocol

```python
from typing import Protocol, Self, TypeVar
from types import TracebackType

T = TypeVar('T', covariant=True)

class AsyncContextManagerProtocol(Protocol[T]):
    """
    Protocol for async context managers.

    Defines the interface any async context manager must implement.
    """

    async def __aenter__(self) -> T:
        """Enter async context."""
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        """Exit async context."""
        ...

# Usage with protocol
async def use_async_context(
    context: AsyncContextManagerProtocol[AsyncSession]
) -> None:
    """Use any object that implements async context manager protocol."""
    async with context as session:
        # Use session
        pass
```

### Complete Example: Multi-Resource Manager

```python
from typing import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

@dataclass
class Resources:
    """Container for multiple managed resources."""
    db_session: AsyncSession
    cache: Redis
    http_client: aiohttp.ClientSession

@asynccontextmanager
async def managed_resources(
    db_url: str,
    redis_url: str,
    api_base_url: str
) -> AsyncIterator[Resources]:
    """
    Manage multiple resources with single context.

    All resources properly cleaned up even if one fails.
    """
    db_session: AsyncSession | None = None
    cache: Redis | None = None
    http_client: aiohttp.ClientSession | None = None

    try:
        # Initialize resources
        engine = create_async_engine(db_url)
        async_session = async_sessionmaker(engine, class_=AsyncSession)
        db_session = async_session()

        cache = await aioredis.from_url(redis_url)

        http_client = aiohttp.ClientSession(base_url=api_base_url)

        # Yield all resources
        yield Resources(
            db_session=db_session,
            cache=cache,
            http_client=http_client
        )

    finally:
        # Cleanup in reverse order
        if http_client:
            await http_client.close()

        if cache:
            await cache.close()

        if db_session:
            await db_session.close()
            await engine.dispose()

# Usage
async def complex_operation(user_id: int) -> dict[str, any]:
    """Operation using multiple resources."""
    async with managed_resources(
        "postgresql://localhost/db",
        "redis://localhost",
        "https://api.example.com"
    ) as resources:
        # Check cache first
        cached = await resources.cache.get(f"user:{user_id}")
        if cached:
            return json.loads(cached)

        # Query database
        result = await resources.db_session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user:
            # Fetch additional data from API
            async with resources.http_client.get(f"/users/{user_id}/extra") as resp:
                extra_data = await resp.json()

            # Combine and cache
            data = {"id": user.id, "name": user.name, **extra_data}
            await resources.cache.set(
                f"user:{user_id}",
                json.dumps(data),
                ex=3600
            )
            return data

        return {}
```

---

## 🛡️ Avoiding Common Pitfalls

### Mutable Default Arguments

```python
# ❌ Bad: Mutable default argument
def add_item(item: str, items: list[str] = []) -> list[str]:
    items.append(item)
    return items

# ✅ Good: Use None and create new list
def add_item(item: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    items.append(item)
    return items
```

### Forward References

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from project_name.models import User

class UserService:
    """Service that references User model."""

    def get_user(self, id_: int) -> User:
        """Get user by ID."""
        # Implementation
        ...

    def create_user(self, data: dict) -> User:
        """Create new user."""
        # Implementation
        ...
```

### Any vs Unknown

```python
from typing import Any

# ❌ Avoid: Any disables type checking
def process_data(data: Any) -> Any:
    return data.value  # No type checking

# ✅ Better: Use specific types
def process_data(data: dict[str, any]) -> str:
    return str(data.get("value", ""))

# ✅ Best: Use generics
T = TypeVar('T')

def process_data(data: T) -> T:
    return data
```

---

## 🔍 MyPy Configuration

### Strict Mode Configuration

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[[tool.mypy.overrides]]
module = "third_party.*"
ignore_missing_imports = true
```

### Inline Type Ignores

```python
from typing import Any

def legacy_function() -> Any:  # type: ignore[misc]
    """Legacy function with type ignore."""
    pass

# Ignore specific error
result = unsafe_operation()  # type: ignore[name-defined]

# Better: Fix the issue instead of ignoring
def legacy_function() -> dict[str, any]:
    """Fixed legacy function."""
    return {}
```

---

## ⚠️ Type Safety Best Practices

1. **Always use type hints** - No untyped public APIs
2. **Use strict MyPy configuration** - `mypy --strict`
3. **Prefer specific types over Any** - Use protocols or generics
4. **Use built-in generics** - `list[str]` instead of `typing.List[str]`
5. **Leverage Union types** - `str | int` instead of `Union[str, int]`
6. **Create type aliases** - For complex types
7. **Use Protocols for duck typing** - More flexible than inheritance
8. **Annotate return types** - Including `None`
9. **Use TypedDict for dictionaries** - Better than `dict[str, any]`
10. **Document type constraints** - In docstrings

---

## 📋 Type Checking Checklist

- [ ] All function signatures have type hints
- [ ] Return types are annotated
- [ ] Complex types use aliases
- [ ] No `Any` type unless necessary
- [ ] Protocols used for structural typing
- [ ] Generics used for reusable components
- [ ] MyPy strict mode passes
- [ ] Type ignores are documented
- [ ] Forward references handled correctly
- [ ] Async types properly annotated

---

**Back to [Core Guide](./CLAUDE-core.md)**
