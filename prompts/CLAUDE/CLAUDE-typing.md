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
