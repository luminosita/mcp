# patterns-validation-security - Input Validation & Security


> **Specialized Guide**: Input sanitization, SQL injection prevention, and path traversal protection.

> **Specialized Guide**: Comprehensive Pydantic validation patterns, security best practices, and input handling for Python projects.
## 🛡️ Security Validation

### Input Sanitization

```python
from pydantic import BaseModel, field_validator, Field
import bleach
from typing import Annotated

class BlogPost(BaseModel):
    """Blog post with sanitized HTML content."""
    title: Annotated[str, Field(min_length=1, max_length=200)]
    content: str
    author_id: int

    @field_validator('title')
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        """Remove any HTML from title."""
        return bleach.clean(v, tags=[], strip=True)

    @field_validator('content')
    @classmethod
    def sanitize_content(cls, v: str) -> str:
        """Allow only safe HTML tags in content."""
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li']
        allowed_attrs = {'a': ['href', 'title']}
        return bleach.clean(
            v,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True
        )
```

### SQL Injection Prevention

#### Input Validation Layer

```python
from pydantic import BaseModel, field_validator
import re

class SearchQuery(BaseModel):
    """Search query with SQL injection prevention."""
    query: str
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Prevent SQL injection patterns."""
        # Block common SQL injection patterns
        dangerous_patterns = [
            r"('\s*(or|and)\s*')",
            r'("\s*(or|and)\s*")',
            r'(;\s*drop\s+table)',
            r'(;\s*delete\s+from)',
            r'(union\s+select)',
            r'(insert\s+into)',
            r'(update\s+\w+\s+set)',
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Invalid query pattern detected')

        return v.strip()
```

#### SQLAlchemy ORM (Safe by Default)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

# ✅ SAFE: ORM queries with bound parameters
async def get_user_by_email_safe(session: AsyncSession, email: str) -> Optional[User]:
    """
    Safe query using SQLAlchemy ORM.

    ORM automatically parameterizes all values.
    """
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

# ✅ SAFE: Multiple conditions with ORM
async def search_users_safe(
    session: AsyncSession,
    name: str,
    min_age: int,
    max_age: int
) -> List[User]:
    """
    Safe complex query with multiple conditions.

    All parameters automatically bound.
    """
    stmt = (
        select(User)
        .where(
            User.name.ilike(f"%{name}%"),
            User.age >= min_age,
            User.age <= max_age
        )
        .order_by(User.created_at.desc())
        .limit(100)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())

# ✅ SAFE: Relationships and joins
async def get_user_with_posts_safe(
    session: AsyncSession,
    user_id: int
) -> Optional[User]:
    """
    Safe query with relationship loading.

    ORM handles all parameterization.
    """
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.posts))
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

# ❌ NEVER: String formatting in queries
async def get_user_by_email_unsafe(session: AsyncSession, email: str):
    """DANGEROUS: Never build queries with string formatting."""
    # This is vulnerable to SQL injection!
    query = f"SELECT * FROM users WHERE email = '{email}'"
    # DON'T DO THIS!
```

#### SQLAlchemy Core (Parameterized Queries)

```python
from sqlalchemy import text, Table, Column, Integer, String, MetaData
from sqlalchemy.ext.asyncio import AsyncSession

metadata = MetaData()

users_table = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('email', String(255)),
    Column('name', String(100))
)

# ✅ SAFE: Core select with bound parameters
async def get_user_core_safe(session: AsyncSession, email: str) -> Optional[dict]:
    """
    Safe query using SQLAlchemy Core.

    Parameters bound using where() clause.
    """
    stmt = users_table.select().where(users_table.c.email == email)
    result = await session.execute(stmt)
    row = result.first()
    return dict(row) if row else None

# ✅ SAFE: Core insert with bound parameters
async def create_user_core_safe(
    session: AsyncSession,
    email: str,
    name: str
) -> int:
    """
    Safe insert using SQLAlchemy Core.

    All values automatically parameterized.
    """
    stmt = users_table.insert().values(email=email, name=name)
    result = await session.execute(stmt)
    await session.commit()
    return result.inserted_primary_key[0]

# ✅ SAFE: Core update with bound parameters
async def update_user_core_safe(
    session: AsyncSession,
    user_id: int,
    new_name: str
) -> None:
    """
    Safe update using SQLAlchemy Core.

    Both WHERE and SET values parameterized.
    """
    stmt = (
        users_table.update()
        .where(users_table.c.id == user_id)
        .values(name=new_name)
    )
    await session.execute(stmt)
    await session.commit()
```

#### Raw SQL with text() (Parameterized)

```python
from sqlalchemy import text
from typing import List

# ✅ SAFE: Raw SQL with named parameters
async def search_users_raw_safe(
    session: AsyncSession,
    search_term: str,
    min_age: int
) -> List[dict]:
    """
    Safe raw SQL using parameterized queries.

    Parameters passed as dictionary, automatically escaped.
    """
    query = text("""
        SELECT id, email, name, age
        FROM users
        WHERE name ILIKE :search
        AND age >= :min_age
        ORDER BY created_at DESC
        LIMIT 100
    """)

    result = await session.execute(
        query,
        {"search": f"%{search_term}%", "min_age": min_age}
    )

    return [dict(row) for row in result.mappings()]

# ✅ SAFE: Raw SQL with positional parameters
async def get_user_by_id_raw_safe(
    session: AsyncSession,
    user_id: int
) -> Optional[dict]:
    """
    Safe raw SQL with positional parameters.

    Use :param_name syntax for named parameters.
    """
    query = text("SELECT * FROM users WHERE id = :user_id")
    result = await session.execute(query, {"user_id": user_id})
    row = result.first()
    return dict(row) if row else None

# ✅ SAFE: Complex query with multiple parameters
async def advanced_search_safe(
    session: AsyncSession,
    filters: dict
) -> List[dict]:
    """
    Safe complex query with dynamic filters.

    All parameters properly bound.
    """
    query = text("""
        SELECT u.id, u.email, u.name, COUNT(p.id) as post_count
        FROM users u
        LEFT JOIN posts p ON p.user_id = u.id
        WHERE u.email LIKE :email_pattern
        AND u.created_at >= :start_date
        AND u.is_active = :is_active
        GROUP BY u.id, u.email, u.name
        HAVING COUNT(p.id) >= :min_posts
        ORDER BY post_count DESC
        LIMIT :limit
    """)

    result = await session.execute(query, filters)
    return [dict(row) for row in result.mappings()]

# ❌ NEVER: String formatting with raw SQL
async def get_user_raw_unsafe(session: AsyncSession, email: str):
    """DANGEROUS: Never use f-strings or format() with SQL."""
    # VULNERABLE TO SQL INJECTION!
    query = text(f"SELECT * FROM users WHERE email = '{email}'")
    # DON'T DO THIS!

    # Also dangerous:
    query = text("SELECT * FROM users WHERE email = '{}'".format(email))
    # DON'T DO THIS!
```

#### Dynamic Query Building (Safe Patterns)

```python
from sqlalchemy import select, and_, or_
from typing import Optional, List

async def dynamic_user_search_safe(
    session: AsyncSession,
    email: Optional[str] = None,
    name: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None
) -> List[User]:
    """
    Safe dynamic query building.

    Conditions added programmatically, all values parameterized.
    """
    # Start with base query
    stmt = select(User)

    # Build conditions list
    conditions = []

    if email:
        conditions.append(User.email.ilike(f"%{email}%"))

    if name:
        conditions.append(User.name.ilike(f"%{name}%"))

    if min_age is not None:
        conditions.append(User.age >= min_age)

    if max_age is not None:
        conditions.append(User.age <= max_age)

    # Apply all conditions with AND
    if conditions:
        stmt = stmt.where(and_(*conditions))

    # Execute query
    result = await session.execute(stmt)
    return list(result.scalars().all())

# ✅ SAFE: Dynamic OR conditions
async def search_multiple_fields_safe(
    session: AsyncSession,
    search_term: str,
    fields: List[str]
) -> List[User]:
    """
    Safe search across multiple fields with OR.

    Search term parameterized, fields validated.
    """
    # Validate fields (whitelist approach)
    valid_fields = {'email', 'name', 'username'}
    fields = [f for f in fields if f in valid_fields]

    if not fields:
        raise ValueError("No valid search fields provided")

    # Build OR conditions
    conditions = []
    for field in fields:
        column = getattr(User, field)
        conditions.append(column.ilike(f"%{search_term}%"))

    stmt = select(User).where(or_(*conditions))
    result = await session.execute(stmt)
    return list(result.scalars().all())
```

#### Dynamic Table/Column Names (Advanced)

```python
from sqlalchemy import table, column, select
from typing import Literal

# Define allowed tables and columns (whitelist)
ALLOWED_TABLES = {'users', 'posts', 'comments'}
ALLOWED_COLUMNS = {
    'users': {'id', 'email', 'name', 'created_at'},
    'posts': {'id', 'title', 'content', 'user_id', 'created_at'},
    'comments': {'id', 'content', 'post_id', 'user_id', 'created_at'}
}

async def dynamic_table_query_safe(
    session: AsyncSession,
    table_name: str,
    column_name: str,
    value: str
) -> List[dict]:
    """
    Safe dynamic table/column query using whitelist validation.

    Table and column names validated against whitelist.
    Values still parameterized.
    """
    # Validate table name (whitelist)
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table name: {table_name}")

    # Validate column name for specific table
    if column_name not in ALLOWED_COLUMNS.get(table_name, set()):
        raise ValueError(f"Invalid column name: {column_name} for table {table_name}")

    # Build query safely
    # table() and column() are safe for identifiers when validated
    tbl = table(table_name)
    col = column(column_name)

    stmt = select(tbl).where(col == value)
    result = await session.execute(stmt)
    return [dict(row) for row in result.mappings()]

# ✅ SAFE: Dynamic sorting with whitelist
SortField = Literal['created_at', 'updated_at', 'name', 'email']
SortOrder = Literal['asc', 'desc']

async def get_users_sorted_safe(
    session: AsyncSession,
    sort_by: SortField = 'created_at',
    order: SortOrder = 'desc'
) -> List[User]:
    """
    Safe dynamic sorting using Literal types.

    Type hints ensure only valid values accepted.
    """
    # Get column from User model
    sort_column = getattr(User, sort_by)

    # Apply sort order
    if order == 'desc':
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    stmt = select(User).order_by(sort_column)
    result = await session.execute(stmt)
    return list(result.scalars().all())

# ❌ NEVER: Unvalidated table/column names
async def dynamic_query_unsafe(session: AsyncSession, table: str, column: str, value: str):
    """DANGEROUS: Never use unvalidated identifiers."""
    # VULNERABLE TO SQL INJECTION!
    query = text(f"SELECT * FROM {table} WHERE {column} = :value")
    # DON'T DO THIS! Table and column names can be injected!
```

#### SQL Injection Prevention Checklist

```python
"""
✅ SAFE PATTERNS:

1. ORM Queries (Preferred)
   - stmt = select(User).where(User.email == email)
   - All values automatically parameterized

2. SQLAlchemy Core
   - stmt = users_table.select().where(users_table.c.email == email)
   - Automatic parameterization

3. Raw SQL with text()
   - query = text("SELECT * FROM users WHERE email = :email")
   - result = session.execute(query, {"email": email})
   - Parameters passed separately

4. Dynamic Queries
   - Build conditions with SQLAlchemy expressions
   - Validate identifiers with whitelist
   - Always parameterize values

❌ NEVER DO:

1. String Formatting
   - f"SELECT * FROM users WHERE email = '{email}'"  # VULNERABLE!
   - "SELECT * FROM users WHERE email = '{}'".format(email)  # VULNERABLE!

2. String Concatenation
   - "SELECT * FROM users WHERE email = '" + email + "'"  # VULNERABLE!

3. Unvalidated Identifiers
   - text(f"SELECT * FROM {table_name}")  # Table name not validated!
   - text(f"SELECT {column} FROM users")  # Column name not validated!

GOLDEN RULES:
1. ALWAYS use parameterized queries for VALUES
2. ALWAYS validate table/column names with whitelist
3. NEVER build SQL with string formatting/concatenation
4. PREFER ORM queries over raw SQL
5. USE type hints (Literal) for dynamic identifiers
"""
```

#### Complete Safe Query Example

```python
from pydantic import BaseModel, field_validator
from typing import Optional, List
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

class UserSearchRequest(BaseModel):
    """Validated user search request."""
    email: Optional[str] = None
    name: Optional[str] = None
    min_age: Optional[int] = Field(None, ge=0, le=150)
    max_age: Optional[int] = Field(None, ge=0, le=150)
    sort_by: Literal['created_at', 'name', 'email'] = 'created_at'
    sort_order: Literal['asc', 'desc'] = 'desc'
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

    @field_validator('email', 'name')
    @classmethod
    def validate_search_terms(cls, v: Optional[str]) -> Optional[str]:
        """Validate and sanitize search terms."""
        if v is None:
            return None

        # Strip whitespace
        v = v.strip()

        # Block SQL injection patterns
        dangerous_patterns = [';', '--', '/*', '*/', 'xp_', 'sp_']
        for pattern in dangerous_patterns:
            if pattern in v.lower():
                raise ValueError(f'Invalid character pattern: {pattern}')

        return v

async def search_users_complete_safe(
    session: AsyncSession,
    search_request: UserSearchRequest
) -> List[User]:
    """
    Complete safe user search with all protections.

    Layers of defense:
    1. Pydantic validation of inputs
    2. SQLAlchemy ORM parameterization
    3. Whitelist validation for identifiers
    4. Type safety with Literal
    """
    # Build base query
    stmt = select(User)

    # Add search conditions (all parameterized)
    conditions = []

    if search_request.email:
        conditions.append(User.email.ilike(f"%{search_request.email}%"))

    if search_request.name:
        conditions.append(User.name.ilike(f"%{search_request.name}%"))

    if search_request.min_age is not None:
        conditions.append(User.age >= search_request.min_age)

    if search_request.max_age is not None:
        conditions.append(User.age <= search_request.max_age)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    # Add sorting (whitelist validated by Literal type)
    sort_column = getattr(User, search_request.sort_by)
    if search_request.sort_order == 'desc':
        sort_column = sort_column.desc()

    stmt = stmt.order_by(sort_column)

    # Add pagination
    stmt = stmt.limit(search_request.limit).offset(search_request.offset)

    # Execute safe query
    result = await session.execute(stmt)
    return list(result.scalars().all())

# Usage
@app.post("/users/search")
async def search_users_endpoint(
    search: UserSearchRequest,
    session: AsyncSession = Depends(get_session)
) -> List[UserResponse]:
    """Search users with complete SQL injection protection."""
    users = await search_users_complete_safe(session, search)
    return [UserResponse.model_validate(user) for user in users]
```

### Path Traversal Prevention

```python
from pydantic import BaseModel, field_validator
from pathlib import Path

class FileRequest(BaseModel):
    """File request with path traversal prevention."""
    filename: str
    directory: str = "uploads"

    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Prevent path traversal attacks."""
        # Remove any path separators
        safe_filename = Path(v).name

        # Block dangerous patterns
        if '..' in safe_filename or safe_filename.startswith('/'):
            raise ValueError('Invalid filename')

        # Ensure filename is alphanumeric with safe chars
        if not re.match(r'^[a-zA-Z0-9_.-]+$', safe_filename):
            raise ValueError('Filename contains invalid characters')

        return safe_filename

    @field_validator('directory')
    @classmethod
    def validate_directory(cls, v: str) -> str:
        """Ensure directory is within allowed paths."""
        allowed_dirs = ['uploads', 'downloads', 'temp']

        if v not in allowed_dirs:
            raise ValueError(f'Directory must be one of: {allowed_dirs}')

        return v
```

---
