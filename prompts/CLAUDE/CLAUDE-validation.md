# CLAUDE-validation.md - Input Validation & Security

> **Specialized Guide**: Comprehensive Pydantic validation patterns, security best practices, and input handling for Python projects.

## 🔐 Validation Philosophy

### Why Pydantic?
- **Runtime validation** - Catch invalid data before processing
- **Type coercion** - Automatic type conversion
- **Clear error messages** - User-friendly validation errors
- **JSON serialization** - Built-in JSON encoding/decoding
- **Settings management** - Environment variable handling

### Validation is Security
- Never trust user input
- Validate at system boundaries
- Use Pydantic for all external data
- Fail fast with clear errors

---

## 📦 Pydantic v2 Basics

### Basic Models

```python
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

class User(BaseModel):
    """User model with basic validation."""
    id: int
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(ge=0, le=150)
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

# Usage
user = User(
    id=1,
    name="John Doe",
    email="john@example.com",
    age=30
)

# JSON serialization
json_data = user.model_dump_json()
user_from_json = User.model_validate_json(json_data)
```

### Field Validation

```python
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Annotated

class Product(BaseModel):
    """Product with field-level validation."""
    name: Annotated[str, Field(
        min_length=2,
        max_length=100,
        pattern=r"^[a-zA-Z0-9\s-]+$",
        description="Product name (alphanumeric, spaces, hyphens)"
    )]
    price: Annotated[float, Field(
        gt=0,
        le=1000000,
        description="Price in dollars"
    )]
    quantity: Annotated[int, Field(
        ge=0,
        description="Available quantity"
    )]
    sku: Annotated[str, Field(
        pattern=r"^[A-Z]{3}-\d{6}$",
        description="SKU format: AAA-123456",
        examples=["ABC-123456"]
    )]

    @field_validator('price')
    @classmethod
    def validate_price_precision(cls, v: float) -> float:
        """Ensure price has max 2 decimal places."""
        if round(v, 2) != v:
            raise ValueError('Price must have at most 2 decimal places')
        return v
```

---

## 🎯 Advanced Validation Patterns

### Custom Validators

```python
from pydantic import BaseModel, field_validator, model_validator
import re

class UserCreate(BaseModel):
    """User creation with complex validation."""
    username: str
    email: str
    password: str
    password_confirm: str
    age: int

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, - and _')
        return v.lower()

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password complexity."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*()_+-=' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v

    @model_validator(mode='after')
    def validate_passwords_match(self) -> 'UserCreate':
        """Ensure passwords match."""
        if self.password != self.password_confirm:
            raise ValueError('Passwords do not match')
        return self

    @model_validator(mode='after')
    def validate_age_username(self) -> 'UserCreate':
        """Validate age-based username restrictions."""
        if self.age < 13:
            raise ValueError('Users must be at least 13 years old')
        if self.age < 18 and not self.username.endswith('_minor'):
            raise ValueError('Minors must have username ending with _minor')
        return self
```

### Validation with Context

```python
from pydantic import BaseModel, field_validator, ValidationInfo

class Payment(BaseModel):
    """Payment with context-aware validation."""
    amount: float
    currency: str
    payment_method: str

    @field_validator('amount')
    @classmethod
    def validate_amount_by_method(cls, v: float, info: ValidationInfo) -> float:
        """Validate amount based on payment method."""
        if not info.context:
            return v

        max_amounts = info.context.get('max_amounts', {})
        payment_method = info.data.get('payment_method')

        if payment_method and payment_method in max_amounts:
            if v > max_amounts[payment_method]:
                raise ValueError(
                    f'Amount exceeds maximum for {payment_method}: '
                    f'{max_amounts[payment_method]}'
                )
        return v

# Usage with context
payment_data = {
    'amount': 1500.00,
    'currency': 'USD',
    'payment_method': 'credit_card'
}

payment = Payment.model_validate(
    payment_data,
    context={
        'max_amounts': {
            'credit_card': 10000,
            'debit_card': 5000,
            'paypal': 2000
        }
    }
)
```

---

## 🏗️ Model Configuration

### Pydantic Config

```python
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal

class Order(BaseModel):
    """Order with custom configuration."""
    model_config = ConfigDict(
        # Validation settings
        validate_assignment=True,      # Validate on assignment
        validate_default=True,         # Validate default values
        strict=True,                   # Strict type checking

        # Serialization settings
        use_enum_values=True,          # Use enum values in dict
        str_strip_whitespace=True,     # Strip whitespace from strings

        # Extra fields handling
        extra='forbid',                # Forbid extra fields

        # JSON encoding
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v),
        },

        # ORM integration
        from_attributes=True,          # Enable ORM mode
    )

    id: int
    total: Decimal
    created_at: datetime
```

### Model Inheritance

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class BaseEntity(BaseModel):
    """Base model with common fields."""
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
    )

    id: int = Field(gt=0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

class User(BaseEntity):
    """User extends base entity."""
    name: str = Field(min_length=1, max_length=100)
    email: str
    is_active: bool = True

class Product(BaseEntity):
    """Product extends base entity."""
    name: str = Field(min_length=1, max_length=200)
    price: Decimal = Field(gt=0, decimal_places=2)
    stock: int = Field(ge=0)
```

---

## 🔄 CRUD Model Patterns

### Base, Create, Update Response Pattern

```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """Shared user properties."""
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    is_active: bool = True

class UserCreate(UserBase):
    """Properties required for user creation."""
    password: str = Field(min_length=8, max_length=128)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password complexity."""
        if not any(c.isupper() for c in v):
            raise ValueError('Must contain uppercase')
        if not any(c.isdigit() for c in v):
            raise ValueError('Must contain digit')
        return v

class UserUpdate(BaseModel):
    """Properties that can be updated."""
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)

    @model_validator(mode='after')
    def check_at_least_one_field(self) -> 'UserUpdate':
        """Ensure at least one field is being updated."""
        if not any([self.email, self.name, self.is_active, self.password]):
            raise ValueError('At least one field must be provided')
        return self

class UserInDB(UserBase):
    """User as stored in database."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    hashed_password: str

    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserBase):
    """User response for API (no sensitive data)."""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

---

## 🌍 Environment Settings

### Settings Management

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings from environment."""
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
    )

    # Application
    app_name: str = "MyApp"
    debug: bool = False
    environment: str = Field(default="development", pattern=r'^(development|staging|production)$')

    # Database
    database_url: str
    database_pool_size: int = Field(default=10, ge=1, le=100)
    database_echo: bool = False

    # Security
    secret_key: str = Field(min_length=32)
    access_token_expire_minutes: int = Field(default=30, ge=1)

    # External Services
    redis_url: Optional[str] = None
    api_key: str
    api_timeout: int = Field(default=30, ge=1, le=300)

    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Ensure secret key is sufficiently random."""
        if v == 'changeme' or v == 'secret':
            raise ValueError('Secret key must be changed from default')
        return v

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL."""
        return self.database_url.replace('postgresql+asyncpg', 'postgresql')

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

# Usage
settings = get_settings()
```

---

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

## 🔐 JWT Authentication & Authorization

### JWT Token Generation

```python
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

# Token configuration
SECRET_KEY = "your-secret-key-here"  # Load from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class TokenPayload(BaseModel):
    """JWT token payload structure."""
    sub: str = Field(description="Subject (user ID)")
    exp: datetime = Field(description="Expiration timestamp")
    iat: datetime = Field(description="Issued at timestamp")
    token_type: str = Field(description="access or refresh")
    scopes: list[str] = Field(default_factory=list, description="User permissions")

class TokenData(BaseModel):
    """Validated token data."""
    user_id: str
    scopes: list[str] = []

class Token(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token with claims.

    Args:
        data: Token payload data (user_id, scopes, etc.)
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Add standard claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "token_type": "access"
    })

    # Encode token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: str) -> str:
    """
    Create long-lived refresh token.

    Refresh tokens should:
    - Have longer expiration (days/weeks)
    - Be stored in database for revocation
    - Only be used to generate new access tokens
    """
    to_encode = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": datetime.utcnow(),
        "token_type": "refresh"
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_token_pair(user_id: str, scopes: list[str]) -> Token:
    """
    Create access and refresh token pair.

    Usage:
        tokens = create_token_pair(user_id="user123", scopes=["read", "write"])
    """
    access_token = create_access_token(
        data={"sub": user_id, "scopes": scopes}
    )
    refresh_token = create_refresh_token(user_id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
```

### JWT Token Validation

```python
from jose import JWTError, jwt, ExpiredSignatureError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

security = HTTPBearer()

async def decode_token(token: str) -> TokenPayload:
    """
    Decode and validate JWT token.

    Raises:
        HTTPException: If token invalid, expired, or malformed
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_payload = TokenPayload(**payload)

        # Validate token type
        if token_payload.token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        return token_payload

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """
    FastAPI dependency to extract and validate current user from JWT.

    Usage:
        @app.get("/protected")
        async def protected_route(user: TokenData = Depends(get_current_user)):
            return {"user_id": user.user_id}
    """
    token = credentials.credentials
    payload = await decode_token(token)

    return TokenData(
        user_id=payload.sub,
        scopes=payload.scopes
    )

async def require_scopes(required_scopes: list[str]):
    """
    Dependency factory for scope-based authorization.

    Usage:
        @app.delete("/admin/users/{user_id}")
        async def delete_user(
            user_id: int,
            user: TokenData = Depends(require_scopes(["admin:write"]))
        ):
            # User must have "admin:write" scope
            pass
    """
    async def scope_checker(user: TokenData = Depends(get_current_user)) -> TokenData:
        for scope in required_scopes:
            if scope not in user.scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required scope: {scope}"
                )
        return user

    return scope_checker
```

### Token Refresh Flow

```python
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

class RefreshTokenRequest(BaseModel):
    """Request to refresh access token."""
    refresh_token: str

async def refresh_access_token(
    request: RefreshTokenRequest,
    session: AsyncSession
) -> Token:
    """
    Generate new access token from refresh token.

    Process:
    1. Validate refresh token format and expiration
    2. Check if token is blacklisted
    3. Verify user still exists and is active
    4. Generate new access token (optionally rotate refresh token)
    """
    try:
        # Decode refresh token
        payload = jwt.decode(
            request.refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # Validate token type
        if payload.get("token_type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        # Check if refresh token is blacklisted
        is_blacklisted = await check_token_blacklist(session, request.refresh_token)
        if is_blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )

        # Verify user exists and is active
        user = await get_user_by_id(session, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Generate new access token
        access_token = create_access_token(
            data={"sub": user_id, "scopes": user.scopes}
        )

        # Optional: Rotate refresh token for added security
        new_refresh_token = create_refresh_token(user_id)

        # Blacklist old refresh token
        await blacklist_token(session, request.refresh_token)

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
```

### Token Blacklist Strategy

```python
from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

class TokenBlacklist(Base):
    """
    Store revoked tokens.

    Cleanup strategy:
    - Periodically delete expired entries
    - Consider Redis for better performance
    """
    __tablename__ = "token_blacklist"

    token = Column(String(500), primary_key=True)
    blacklisted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    # Index for efficient cleanup
    __table_args__ = (
        Index('idx_expires_at', 'expires_at'),
    )

async def blacklist_token(session: AsyncSession, token: str) -> None:
    """
    Add token to blacklist.

    Store token expiration to enable automatic cleanup.
    """
    try:
        # Decode to get expiration
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_timestamp = payload.get("exp")
        expires_at = datetime.fromtimestamp(exp_timestamp)

        # Add to blacklist
        blacklisted = TokenBlacklist(
            token=token,
            expires_at=expires_at
        )
        session.add(blacklisted)
        await session.commit()

    except JWTError:
        # If token invalid, still blacklist it
        blacklisted = TokenBlacklist(
            token=token,
            expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        session.add(blacklisted)
        await session.commit()

async def check_token_blacklist(session: AsyncSession, token: str) -> bool:
    """Check if token is blacklisted."""
    stmt = select(TokenBlacklist).where(TokenBlacklist.token == token)
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None

async def cleanup_expired_tokens(session: AsyncSession) -> int:
    """
    Remove expired tokens from blacklist.

    Run periodically (e.g., daily cron job):
        await cleanup_expired_tokens(session)

    Returns:
        Number of tokens removed
    """
    from sqlalchemy import delete

    stmt = delete(TokenBlacklist).where(
        TokenBlacklist.expires_at < datetime.utcnow()
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount
```

### Redis-Based Token Blacklist (Alternative)

```python
import redis.asyncio as redis
from datetime import datetime

class RedisTokenBlacklist:
    """
    Redis-based token blacklist for better performance.

    Advantages:
    - Faster lookups than database
    - Automatic expiration with TTL
    - No manual cleanup needed
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.prefix = "blacklist:"

    async def blacklist_token(self, token: str) -> None:
        """Add token to Redis blacklist with automatic expiration."""
        try:
            # Decode to get expiration
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            exp_timestamp = payload.get("exp")

            # Calculate TTL (time until token expires)
            ttl = exp_timestamp - datetime.utcnow().timestamp()

            if ttl > 0:
                # Store token with TTL
                key = f"{self.prefix}{token}"
                await self.redis.setex(key, int(ttl), "1")

        except JWTError:
            # If token invalid, store with default TTL
            key = f"{self.prefix}{token}"
            await self.redis.setex(
                key,
                REFRESH_TOKEN_EXPIRE_DAYS * 86400,
                "1"
            )

    async def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        key = f"{self.prefix}{token}"
        return await self.redis.exists(key) > 0
```

### Complete Authentication Example

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    """User login credentials."""
    email: str
    password: str

@app.post("/auth/login", response_model=Token)
async def login(
    credentials: LoginRequest,
    session: AsyncSession = Depends(get_session)
) -> Token:
    """
    Authenticate user and return token pair.

    Process:
    1. Validate credentials
    2. Generate access + refresh token
    3. Store refresh token in database (for revocation)
    4. Return token pair
    """
    # Verify credentials
    user = await authenticate_user(session, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate token pair
    tokens = create_token_pair(
        user_id=str(user.id),
        scopes=user.scopes
    )

    # Store refresh token for tracking (optional)
    await store_refresh_token(session, user.id, tokens.refresh_token)

    return tokens

@app.post("/auth/refresh", response_model=Token)
async def refresh(
    request: RefreshTokenRequest,
    session: AsyncSession = Depends(get_session)
) -> Token:
    """Refresh access token using refresh token."""
    return await refresh_access_token(request, session)

@app.post("/auth/logout")
async def logout(
    user: TokenData = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, str]:
    """
    Logout user by blacklisting tokens.

    Client should:
    1. Call this endpoint
    2. Delete tokens from storage
    3. Redirect to login
    """
    # Blacklist current access token (if provided in header)
    # Note: Client should send refresh token to blacklist it
    return {"message": "Successfully logged out"}

@app.get("/protected")
async def protected_route(
    user: TokenData = Depends(get_current_user)
) -> Dict[str, str]:
    """Protected route requiring valid JWT."""
    return {"message": f"Hello user {user.user_id}"}

@app.get("/admin/users")
async def admin_route(
    user: TokenData = Depends(require_scopes(["admin:read"]))
) -> Dict[str, str]:
    """Protected route requiring specific scope."""
    return {"message": "Admin access granted"}
```

### Security Considerations

#### Token Expiration Strategy

```python
# ✅ DO: Short-lived access tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15 minutes

# ✅ DO: Longer-lived refresh tokens
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days

# ❌ DON'T: Long-lived access tokens (security risk)
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 1 week - TOO LONG
```

#### Secure Token Storage (Client Side)

```markdown
✅ Recommended Storage:
- **Access Token**: Memory only (JavaScript variable)
  - Never localStorage (XSS risk)
  - httpOnly cookie acceptable for same-domain

- **Refresh Token**: httpOnly, Secure, SameSite cookie
  - httpOnly: Prevents JavaScript access
  - Secure: HTTPS only
  - SameSite: CSRF protection

❌ Avoid:
- localStorage (vulnerable to XSS)
- sessionStorage (vulnerable to XSS)
- Regular cookies without httpOnly flag
```

#### Token Rotation

```python
# ✅ DO: Rotate refresh tokens on use
@app.post("/auth/refresh")
async def refresh_token(request: RefreshTokenRequest):
    # 1. Validate old refresh token
    # 2. Blacklist old refresh token
    # 3. Generate new access + refresh token pair
    # 4. Return new tokens
    pass

# Why? Limits damage if refresh token is compromised
```

#### CSRF Protection with JWT

```python
from fastapi import Cookie, HTTPException

# ✅ DO: Use double-submit cookie pattern for CSRF protection
@app.post("/api/action")
async def protected_action(
    csrf_token: str = Cookie(...),
    x_csrf_token: str = Header(...),
    user: TokenData = Depends(get_current_user)
):
    """
    Verify CSRF token matches cookie.

    Client must:
    1. Read CSRF token from cookie
    2. Send in X-CSRF-Token header
    """
    if csrf_token != x_csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token mismatch"
        )

    # Process action
    return {"status": "success"}
```

#### Token Claims Validation

```python
from typing import List

def validate_token_claims(payload: dict, expected_audience: str) -> None:
    """
    Validate JWT claims for security.

    Standard claims:
    - iss (Issuer): Who issued the token
    - aud (Audience): Who the token is for
    - sub (Subject): User ID
    - exp (Expiration): When token expires
    - iat (Issued At): When token was created
    - nbf (Not Before): Token not valid before this time
    """
    # Validate audience
    aud = payload.get("aud")
    if aud and aud != expected_audience:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token audience"
        )

    # Validate issuer
    iss = payload.get("iss")
    expected_issuer = "https://your-api.com"
    if iss and iss != expected_issuer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token issuer"
        )

    # Check not-before claim
    nbf = payload.get("nbf")
    if nbf and datetime.fromtimestamp(nbf) > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not yet valid"
        )

# Usage in token creation
def create_secure_token(user_id: str) -> str:
    """Create token with all security claims."""
    to_encode = {
        "sub": user_id,
        "iss": "https://your-api.com",
        "aud": "https://your-api.com",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "nbf": datetime.utcnow(),
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

---

## 📤 File Upload Security

### File Validation Basics

```python
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from pydantic import BaseModel, Field
from typing import Annotated
import magic  # python-magic for MIME detection
from pathlib import Path
import hashlib

app = FastAPI()

class FileMetadata(BaseModel):
    """Validated file metadata."""
    filename: str
    content_type: str
    size: int
    sha256: str

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {
    'image/jpeg',
    'image/png',
    'image/gif',
    'application/pdf',
    'text/plain',
}
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

async def validate_file_upload(file: UploadFile) -> FileMetadata:
    """
    Comprehensive file upload validation.

    Validates:
    - File size (streaming and total)
    - MIME type (actual content, not just extension)
    - Filename (sanitization)

    Raises:
        HTTPException: If validation fails
    """
    # Read file header for MIME detection (first 8KB)
    header = await file.read(8192)

    # Detect actual MIME type from content
    mime = magic.from_buffer(header, mime=True)

    # Validate MIME type
    if mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed: {mime}. Allowed types: {ALLOWED_MIME_TYPES}"
        )

    # Reset file pointer to beginning
    await file.seek(0)

    # Stream file and validate size
    total_size = 0
    file_hash = hashlib.sha256()
    chunks = []

    while chunk := await file.read(8192):
        total_size += len(chunk)

        # Check size limit
        if total_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE} bytes"
            )

        # Update hash
        file_hash.update(chunk)
        chunks.append(chunk)

    # Sanitize filename
    safe_filename = sanitize_filename(file.filename or "upload")

    return FileMetadata(
        filename=safe_filename,
        content_type=mime,
        size=total_size,
        sha256=file_hash.hexdigest()
    )

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and injection attacks.

    Rules:
    - Remove path components (keep only filename)
    - Replace dangerous characters
    - Limit length
    - Ensure valid extension
    """
    # Remove path components
    safe_name = Path(filename).name

    # Block dangerous patterns
    if '..' in safe_name or safe_name.startswith('.'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename"
        )

    # Replace dangerous characters
    import re
    safe_name = re.sub(r'[^\w\s.-]', '_', safe_name)

    # Limit length
    if len(safe_name) > 255:
        name, ext = safe_name.rsplit('.', 1)
        safe_name = name[:250] + '.' + ext

    # Ensure filename is not empty
    if not safe_name or safe_name == '.':
        safe_name = 'unnamed'

    return safe_name

@app.post("/upload", response_model=FileMetadata)
async def upload_file(
    file: Annotated[UploadFile, File(description="File to upload")]
) -> FileMetadata:
    """
    Upload file with validation.

    Security checks:
    - MIME type verification
    - Size validation
    - Filename sanitization
    """
    # Validate file
    metadata = await validate_file_upload(file)

    # Reset file pointer
    await file.seek(0)

    # Save file with safe filename
    file_path = UPLOAD_DIR / f"{metadata.sha256}_{metadata.filename}"

    with open(file_path, 'wb') as f:
        while chunk := await file.read(8192):
            f.write(chunk)

    return metadata
```

### MIME Type Verification

```python
import magic
from typing import Dict, Set

class MIMEValidator:
    """
    Validate MIME types from file content, not just extension.

    Why? Extensions can be changed, but magic bytes cannot.
    """

    # Mapping of allowed MIME types to allowed extensions
    MIME_EXTENSION_MAP: Dict[str, Set[str]] = {
        'image/jpeg': {'.jpg', '.jpeg'},
        'image/png': {'.png'},
        'image/gif': {'.gif'},
        'application/pdf': {'.pdf'},
        'text/plain': {'.txt'},
        'application/zip': {'.zip'},
    }

    @classmethod
    async def validate_mime_and_extension(
        cls,
        file: UploadFile,
        allowed_mimes: Set[str]
    ) -> str:
        """
        Validate both MIME type and extension match.

        Returns:
            Detected MIME type

        Raises:
            HTTPException: If MIME type or extension invalid
        """
        # Read header
        header = await file.read(8192)
        await file.seek(0)

        # Detect MIME from content
        detected_mime = magic.from_buffer(header, mime=True)

        # Check MIME is allowed
        if detected_mime not in allowed_mimes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed: {detected_mime}"
            )

        # Verify extension matches MIME type
        if file.filename:
            file_ext = Path(file.filename).suffix.lower()
            allowed_extensions = cls.MIME_EXTENSION_MAP.get(detected_mime, set())

            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Extension {file_ext} does not match file type {detected_mime}"
                )

        return detected_mime

# Usage
@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    """Upload image with strict MIME validation."""
    mime = await MIMEValidator.validate_mime_and_extension(
        file,
        allowed_mimes={'image/jpeg', 'image/png', 'image/gif'}
    )

    # Process image...
    return {"mime_type": mime}
```

### File Size Validation (Streaming)

```python
from fastapi import Request
from starlette.datastructures import UploadFile as StarletteUploadFile

class MaxSizeValidator:
    """
    Validate file size during streaming upload.

    Prevents memory exhaustion from large files.
    """

    def __init__(self, max_size: int):
        """
        Args:
            max_size: Maximum file size in bytes
        """
        self.max_size = max_size

    async def __call__(self, file: UploadFile) -> UploadFile:
        """
        Validate file size during streaming.

        Raises:
            HTTPException: If file exceeds max size
        """
        total_size = 0

        # Create new file object that validates during read
        original_read = file.read

        async def validated_read(size: int = -1):
            nonlocal total_size
            chunk = await original_read(size)
            total_size += len(chunk)

            if total_size > self.max_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large. Maximum: {self.max_size} bytes"
                )

            return chunk

        file.read = validated_read
        return file

# Usage with dependency injection
@app.post("/upload/large")
async def upload_large_file(
    file: Annotated[
        UploadFile,
        Depends(MaxSizeValidator(max_size=100 * 1024 * 1024))  # 100 MB
    ]
):
    """Upload with size validation during streaming."""
    # File is already validated during streaming
    return {"status": "uploaded"}
```

### Virus Scanning Integration

```python
import subprocess
from typing import Optional
import tempfile

class VirusScanner:
    """
    Integrate virus scanning with ClamAV.

    Setup:
        apt-get install clamav clamav-daemon
        systemctl start clamav-daemon
    """

    @staticmethod
    async def scan_file(file_path: Path) -> bool:
        """
        Scan file for viruses using ClamAV.

        Returns:
            True if file is clean, False if infected

        Raises:
            HTTPException: If scan fails or virus detected
        """
        try:
            # Run ClamAV scan
            result = subprocess.run(
                ['clamdscan', '--no-summary', str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Check result
            if result.returncode == 0:
                return True  # Clean
            elif result.returncode == 1:
                # Virus found
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File contains malware"
                )
            else:
                # Scan error
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Virus scan failed"
                )

        except subprocess.TimeoutExpired:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Virus scan timeout"
            )

    @staticmethod
    async def scan_upload(file: UploadFile) -> bool:
        """
        Scan uploaded file before processing.

        Creates temporary file for scanning.
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            # Write uploaded file to temp
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)

        try:
            # Reset file pointer
            await file.seek(0)

            # Scan temp file
            is_clean = await VirusScanner.scan_file(tmp_path)
            return is_clean

        finally:
            # Clean up temp file
            tmp_path.unlink(missing_ok=True)

# Usage
@app.post("/upload/secure")
async def upload_with_scan(file: UploadFile = File(...)):
    """Upload with virus scanning."""
    # Scan file
    is_clean = await VirusScanner.scan_upload(file)

    if not is_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File failed security scan"
        )

    # Process file...
    return {"status": "clean"}
```

### Image Manipulation Safety

```python
from PIL import Image, ImageFile
from io import BytesIO

# Prevent decompression bomb attacks
Image.MAX_IMAGE_PIXELS = 89478485  # ~8K image
ImageFile.LOAD_TRUNCATED_IMAGES = False

class ImageValidator:
    """
    Secure image validation and processing.

    Protects against:
    - Decompression bombs
    - Malicious EXIF data
    - Oversized images
    """

    MAX_WIDTH = 4096
    MAX_HEIGHT = 4096

    @classmethod
    async def validate_image(cls, file: UploadFile) -> Image.Image:
        """
        Validate and safely load image.

        Raises:
            HTTPException: If image is invalid or dangerous
        """
        try:
            # Read file content
            content = await file.read()
            await file.seek(0)

            # Load image
            image = Image.open(BytesIO(content))

            # Verify image can be loaded
            image.verify()

            # Reload image for processing (verify() invalidates it)
            image = Image.open(BytesIO(content))

            # Check dimensions
            width, height = image.size
            if width > cls.MAX_WIDTH or height > cls.MAX_HEIGHT:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image too large. Max: {cls.MAX_WIDTH}x{cls.MAX_HEIGHT}"
                )

            return image

        except Image.DecompressionBombError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image too large (decompression bomb suspected)"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image: {str(e)}"
            )

    @classmethod
    async def sanitize_image(cls, image: Image.Image) -> Image.Image:
        """
        Strip dangerous metadata and re-encode image.

        Removes:
        - EXIF data
        - Comments
        - Other metadata
        """
        # Create new image without metadata
        clean_image = Image.new(image.mode, image.size)
        clean_image.putdata(list(image.getdata()))

        return clean_image

    @classmethod
    async def process_upload(cls, file: UploadFile) -> BytesIO:
        """
        Complete image validation and sanitization.

        Returns:
            Clean image as BytesIO
        """
        # Validate image
        image = await cls.validate_image(file)

        # Sanitize (remove metadata)
        clean_image = await cls.sanitize_image(image)

        # Convert to bytes
        output = BytesIO()
        clean_image.save(output, format=image.format or 'PNG')
        output.seek(0)

        return output

# Usage
@app.post("/upload/image/safe")
async def upload_safe_image(file: UploadFile = File(...)):
    """Upload image with full security validation."""
    # Validate MIME type
    mime = await MIMEValidator.validate_mime_and_extension(
        file,
        allowed_mimes={'image/jpeg', 'image/png'}
    )

    # Process and sanitize image
    clean_image = await ImageValidator.process_upload(file)

    # Save clean image
    safe_filename = sanitize_filename(file.filename or "image.png")
    file_path = UPLOAD_DIR / safe_filename

    with open(file_path, 'wb') as f:
        f.write(clean_image.getvalue())

    return {"filename": safe_filename, "mime_type": mime}
```

### Chunked Upload Handling

```python
from fastapi import BackgroundTasks
import aiofiles
from typing import List
from pydantic import BaseModel

class ChunkMetadata(BaseModel):
    """Metadata for chunked upload."""
    upload_id: str
    chunk_index: int
    total_chunks: int
    chunk_hash: str

class ChunkedUploadManager:
    """
    Handle large file uploads in chunks.

    Benefits:
    - Resume interrupted uploads
    - Stream large files without memory issues
    - Validate chunks independently
    """

    def __init__(self, upload_dir: Path):
        self.upload_dir = upload_dir
        self.chunks_dir = upload_dir / "chunks"
        self.chunks_dir.mkdir(exist_ok=True)

    async def upload_chunk(
        self,
        upload_id: str,
        chunk_index: int,
        total_chunks: int,
        chunk: UploadFile
    ) -> ChunkMetadata:
        """
        Upload single chunk.

        Validates:
        - Chunk size
        - Chunk hash
        - Upload ID
        """
        # Read chunk
        content = await chunk.read()

        # Validate chunk size (max 5 MB per chunk)
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Chunk too large"
            )

        # Calculate hash
        chunk_hash = hashlib.sha256(content).hexdigest()

        # Save chunk
        chunk_path = self.chunks_dir / f"{upload_id}_{chunk_index:04d}"

        async with aiofiles.open(chunk_path, 'wb') as f:
            await f.write(content)

        return ChunkMetadata(
            upload_id=upload_id,
            chunk_index=chunk_index,
            total_chunks=total_chunks,
            chunk_hash=chunk_hash
        )

    async def finalize_upload(
        self,
        upload_id: str,
        total_chunks: int,
        expected_hashes: List[str]
    ) -> Path:
        """
        Combine chunks into final file after validation.

        Validates:
        - All chunks present
        - Chunk hashes match
        - Final file integrity
        """
        # Verify all chunks present
        chunk_paths = []
        for i in range(total_chunks):
            chunk_path = self.chunks_dir / f"{upload_id}_{i:04d}"
            if not chunk_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing chunk {i}"
                )
            chunk_paths.append(chunk_path)

        # Combine chunks
        final_path = self.upload_dir / f"{upload_id}_complete"

        async with aiofiles.open(final_path, 'wb') as outfile:
            for i, chunk_path in enumerate(chunk_paths):
                async with aiofiles.open(chunk_path, 'rb') as infile:
                    chunk_content = await infile.read()

                    # Verify chunk hash
                    chunk_hash = hashlib.sha256(chunk_content).hexdigest()
                    if chunk_hash != expected_hashes[i]:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Chunk {i} hash mismatch"
                        )

                    await outfile.write(chunk_content)

        # Clean up chunks
        for chunk_path in chunk_paths:
            chunk_path.unlink()

        return final_path

# Usage
chunk_manager = ChunkedUploadManager(UPLOAD_DIR)

@app.post("/upload/chunk", response_model=ChunkMetadata)
async def upload_chunk(
    upload_id: str,
    chunk_index: int,
    total_chunks: int,
    chunk: UploadFile = File(...)
):
    """Upload single chunk."""
    return await chunk_manager.upload_chunk(
        upload_id,
        chunk_index,
        total_chunks,
        chunk
    )

@app.post("/upload/finalize")
async def finalize_upload(
    upload_id: str,
    total_chunks: int,
    chunk_hashes: List[str],
    background_tasks: BackgroundTasks
):
    """Finalize chunked upload."""
    final_path = await chunk_manager.finalize_upload(
        upload_id,
        total_chunks,
        chunk_hashes
    )

    # Optionally: Run virus scan in background
    background_tasks.add_task(VirusScanner.scan_file, final_path)

    return {"status": "complete", "file_id": upload_id}
```

### Storage Path Security

```python
from pathlib import Path
import os

class SecureStorage:
    """
    Secure file storage with path traversal prevention.

    Security principles:
    - Never trust user-provided paths
    - Use absolute paths
    - Validate paths are within allowed directory
    - Use UUIDs for filenames (not user input)
    """

    def __init__(self, base_dir: Path):
        """
        Args:
            base_dir: Absolute path to upload directory
        """
        self.base_dir = base_dir.resolve()

        # Ensure base directory exists
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_safe_path(self, filename: str) -> Path:
        """
        Get safe file path, preventing path traversal.

        Raises:
            HTTPException: If path escapes base directory
        """
        # Remove any path components
        safe_filename = Path(filename).name

        # Construct full path
        file_path = (self.base_dir / safe_filename).resolve()

        # Verify path is within base directory
        if not str(file_path).startswith(str(self.base_dir)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file path"
            )

        return file_path

    def generate_safe_filename(self, original_filename: str) -> str:
        """
        Generate UUID-based filename to avoid collisions.

        Format: {uuid}_{sanitized_original_name}
        """
        import uuid

        # Sanitize original filename
        safe_name = sanitize_filename(original_filename)

        # Generate UUID prefix
        file_id = uuid.uuid4().hex[:8]

        return f"{file_id}_{safe_name}"

# Usage
storage = SecureStorage(UPLOAD_DIR)

@app.post("/upload/secure-path")
async def upload_secure_path(file: UploadFile = File(...)):
    """Upload with secure path handling."""
    # Generate safe filename
    safe_filename = storage.generate_safe_filename(file.filename or "upload")

    # Get validated path
    file_path = storage.get_safe_path(safe_filename)

    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        while chunk := await file.read(8192):
            await f.write(chunk)

    return {"filename": safe_filename}
```

### Complete Secure Upload Example

```python
@app.post("/upload/complete-security", response_model=FileMetadata)
async def upload_complete_security(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> FileMetadata:
    """
    Complete file upload with all security measures.

    Security layers:
    1. MIME type validation (content-based)
    2. File size validation (streaming)
    3. Filename sanitization
    4. Secure path handling
    5. Virus scanning (background)
    6. Image sanitization (if image)
    """
    # 1. Validate MIME type
    mime = await MIMEValidator.validate_mime_and_extension(
        file,
        allowed_mimes=ALLOWED_MIME_TYPES
    )

    # 2. Validate file (size, content)
    metadata = await validate_file_upload(file)
    await file.seek(0)

    # 3. Generate secure filename
    safe_filename = storage.generate_safe_filename(metadata.filename)
    file_path = storage.get_safe_path(safe_filename)

    # 4. Process based on file type
    if mime.startswith('image/'):
        # Sanitize image
        clean_image = await ImageValidator.process_upload(file)

        # Save sanitized image
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(clean_image.getvalue())
    else:
        # Save file normally
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(8192):
                await f.write(chunk)

    # 5. Schedule virus scan
    background_tasks.add_task(VirusScanner.scan_file, file_path)

    return FileMetadata(
        filename=safe_filename,
        content_type=mime,
        size=metadata.size,
        sha256=metadata.sha256
    )
```

---

## 🚦 API Rate Limiting

### slowapi Rate Limiting (Redis-Based)

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from redis.asyncio import Redis
import redis.asyncio as redis

app = FastAPI()

# Initialize Redis connection
redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)

# Initialize limiter
limiter = Limiter(
    key_func=get_remote_address,  # Rate limit by IP
    storage_uri="redis://localhost:6379",
    default_limits=["100/hour"]  # Global default
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Per-route rate limiting
@app.get("/api/data")
@limiter.limit("5/minute")  # 5 requests per minute
async def get_data(request: Request):
    """Endpoint with rate limiting."""
    return {"data": "value"}

@app.post("/api/upload")
@limiter.limit("10/hour")  # Stricter limit for expensive operations
async def upload_data(request: Request):
    """Upload endpoint with strict rate limit."""
    return {"status": "uploaded"}

# Multiple rate limits
@app.get("/api/search")
@limiter.limit("10/minute;100/hour")  # Both minute and hour limits
async def search(request: Request):
    """Search with multiple rate limit windows."""
    return {"results": []}
```

### Custom Rate Limiter with Redis

```python
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
import redis.asyncio as redis
from pydantic import BaseModel

class RateLimitConfig(BaseModel):
    """Rate limit configuration."""
    max_requests: int
    window_seconds: int
    identifier: str  # User ID or IP address

class TokenBucketLimiter:
    """
    Token bucket rate limiting algorithm.

    Advantages:
    - Allows burst traffic
    - Smooth rate limiting
    - Configurable bucket size and refill rate
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def is_allowed(
        self,
        identifier: str,
        max_tokens: int,
        refill_rate: float,  # Tokens per second
        bucket_size: int
    ) -> bool:
        """
        Check if request is allowed under token bucket algorithm.

        Args:
            identifier: User ID or IP address
            max_tokens: Maximum tokens in bucket
            refill_rate: Token refill rate (per second)
            bucket_size: Maximum bucket capacity

        Returns:
            True if request allowed, False otherwise
        """
        now = datetime.utcnow().timestamp()
        key = f"rate_limit:token_bucket:{identifier}"

        # Get current bucket state
        bucket_data = await self.redis.hgetall(key)

        if not bucket_data:
            # Initialize bucket
            tokens = bucket_size - 1  # Consume one token
            last_refill = now
        else:
            tokens = float(bucket_data.get('tokens', bucket_size))
            last_refill = float(bucket_data.get('last_refill', now))

            # Calculate tokens to add based on time elapsed
            elapsed = now - last_refill
            tokens_to_add = elapsed * refill_rate
            tokens = min(bucket_size, tokens + tokens_to_add)

            # Try to consume token
            if tokens >= 1:
                tokens -= 1
            else:
                return False  # No tokens available

        # Update bucket state
        await self.redis.hset(key, mapping={
            'tokens': str(tokens),
            'last_refill': str(now)
        })
        await self.redis.expire(key, int(bucket_size / refill_rate) + 60)

        return True

class SlidingWindowLimiter:
    """
    Sliding window rate limiting algorithm.

    Advantages:
    - More accurate than fixed window
    - Prevents burst at window boundaries
    - Smooth rate limiting
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def is_allowed(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, dict]:
        """
        Check if request is allowed under sliding window algorithm.

        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        now = datetime.utcnow().timestamp()
        window_start = now - window_seconds
        key = f"rate_limit:sliding:{identifier}"

        # Remove old entries
        await self.redis.zremrangebyscore(key, 0, window_start)

        # Count requests in current window
        request_count = await self.redis.zcard(key)

        # Check if limit exceeded
        if request_count >= max_requests:
            # Get oldest request timestamp for retry-after calculation
            oldest = await self.redis.zrange(key, 0, 0, withscores=True)
            if oldest:
                retry_after = int(oldest[0][1] + window_seconds - now)
            else:
                retry_after = window_seconds

            return False, {
                'allowed': False,
                'limit': max_requests,
                'remaining': 0,
                'reset': int(now + retry_after),
                'retry_after': retry_after
            }

        # Add current request
        await self.redis.zadd(key, {str(now): now})
        await self.redis.expire(key, window_seconds)

        return True, {
            'allowed': True,
            'limit': max_requests,
            'remaining': max_requests - request_count - 1,
            'reset': int(now + window_seconds)
        }

# Initialize limiters
token_bucket = TokenBucketLimiter(redis_client)
sliding_window = SlidingWindowLimiter(redis_client)
```

### Rate Limiting Dependency

```python
from fastapi import Depends, Request, HTTPException, status
from typing import Callable

async def get_client_identifier(request: Request) -> str:
    """
    Get client identifier for rate limiting.

    Priority:
    1. Authenticated user ID (if available)
    2. API key (if provided)
    3. IP address (fallback)
    """
    # Check for authenticated user
    user = getattr(request.state, 'user', None)
    if user:
        return f"user:{user.id}"

    # Check for API key
    api_key = request.headers.get('X-API-Key')
    if api_key:
        return f"api_key:{api_key}"

    # Fallback to IP address
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return f"ip:{forwarded.split(',')[0].strip()}"

    return f"ip:{request.client.host}"

def rate_limit(
    max_requests: int,
    window_seconds: int,
    identifier_func: Callable = get_client_identifier
):
    """
    Dependency factory for rate limiting.

    Usage:
        @app.get("/api/data")
        async def get_data(
            _: None = Depends(rate_limit(max_requests=10, window_seconds=60))
        ):
            return {"data": "value"}
    """
    async def check_rate_limit(request: Request) -> None:
        # Get client identifier
        identifier = await identifier_func(request)

        # Check rate limit
        allowed, info = await sliding_window.is_allowed(
            identifier,
            max_requests,
            window_seconds
        )

        # Set rate limit headers
        request.state.rate_limit_info = info

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "retry_after": info['retry_after']
                },
                headers={
                    "X-RateLimit-Limit": str(info['limit']),
                    "X-RateLimit-Remaining": str(info['remaining']),
                    "X-RateLimit-Reset": str(info['reset']),
                    "Retry-After": str(info['retry_after'])
                }
            )

    return check_rate_limit

# Usage
@app.get("/api/protected")
async def protected_endpoint(
    request: Request,
    _: None = Depends(rate_limit(max_requests=10, window_seconds=60))
):
    """Endpoint with rate limiting."""
    return {"data": "value"}
```

### Rate Limit Response Headers Middleware

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class RateLimitHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add rate limit headers to all responses.

    Standard headers:
    - X-RateLimit-Limit: Maximum requests allowed
    - X-RateLimit-Remaining: Remaining requests
    - X-RateLimit-Reset: Unix timestamp when limit resets
    - Retry-After: Seconds to wait (if rate limited)
    """

    async def dispatch(self, request: Request, call_next):
        # Process request
        response = await call_next(request)

        # Add rate limit headers if available
        if hasattr(request.state, 'rate_limit_info'):
            info = request.state.rate_limit_info

            response.headers['X-RateLimit-Limit'] = str(info['limit'])
            response.headers['X-RateLimit-Remaining'] = str(info['remaining'])
            response.headers['X-RateLimit-Reset'] = str(info['reset'])

            if not info['allowed']:
                response.headers['Retry-After'] = str(info.get('retry_after', 60))

        return response

# Add middleware
app.add_middleware(RateLimitHeadersMiddleware)
```

### Per-User Rate Limiting

```python
from fastapi.security import HTTPBearer
from typing import Optional

security = HTTPBearer()

class UserRateLimiter:
    """
    Rate limit based on user tier/subscription.

    Different limits for different user types:
    - Free users: 100 requests/hour
    - Basic users: 1000 requests/hour
    - Premium users: 10000 requests/hour
    """

    RATE_LIMITS = {
        'free': (100, 3600),      # 100 requests per hour
        'basic': (1000, 3600),    # 1000 requests per hour
        'premium': (10000, 3600),  # 10000 requests per hour
        'anonymous': (10, 3600)    # 10 requests per hour for unauthenticated
    }

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.limiter = SlidingWindowLimiter(redis_client)

    async def check_user_limit(
        self,
        user_id: Optional[str],
        user_tier: str = 'free'
    ) -> tuple[bool, dict]:
        """
        Check rate limit for specific user.

        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        # Get rate limit config for user tier
        max_requests, window = self.RATE_LIMITS.get(
            user_tier,
            self.RATE_LIMITS['free']
        )

        # Use user ID or mark as anonymous
        identifier = f"user:{user_id}" if user_id else "anonymous"

        # Check rate limit
        return await self.limiter.is_allowed(
            identifier,
            max_requests,
            window
        )

user_limiter = UserRateLimiter(redis_client)

def user_rate_limit():
    """
    Dependency for per-user rate limiting.

    Usage:
        @app.get("/api/user/data")
        async def get_user_data(
            user: TokenData = Depends(get_current_user),
            _: None = Depends(user_rate_limit())
        ):
            return {"data": "value"}
    """
    async def check_limit(request: Request) -> None:
        # Get user from request state (if authenticated)
        user = getattr(request.state, 'user', None)

        if user:
            user_id = user.id
            user_tier = getattr(user, 'tier', 'free')
        else:
            user_id = None
            user_tier = 'anonymous'

        # Check rate limit
        allowed, info = await user_limiter.check_user_limit(user_id, user_tier)

        # Store info for headers
        request.state.rate_limit_info = info

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded for your tier",
                    "tier": user_tier,
                    "limit": info['limit'],
                    "retry_after": info.get('retry_after', 60)
                },
                headers={
                    "Retry-After": str(info.get('retry_after', 60))
                }
            )

    return check_limit

# Usage
@app.get("/api/user/data")
async def get_user_data(
    request: Request,
    _: None = Depends(user_rate_limit())
):
    """User-specific rate limited endpoint."""
    return {"data": "value"}
```

### Rate Limiting by Endpoint Cost

```python
from enum import IntEnum

class EndpointCost(IntEnum):
    """Cost of different endpoint operations."""
    READ = 1
    WRITE = 5
    SEARCH = 10
    EXPENSIVE = 50

class CostBasedLimiter:
    """
    Rate limit based on operation cost.

    Users have credit pool that refills over time.
    Different operations consume different amounts of credits.
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def consume_credits(
        self,
        identifier: str,
        cost: int,
        max_credits: int = 1000,
        refill_rate: float = 10.0  # Credits per second
    ) -> tuple[bool, int]:
        """
        Try to consume credits for operation.

        Args:
            identifier: User identifier
            cost: Credit cost of operation
            max_credits: Maximum credit pool size
            refill_rate: Credits refilled per second

        Returns:
            Tuple of (success, remaining_credits)
        """
        now = datetime.utcnow().timestamp()
        key = f"rate_limit:credits:{identifier}"

        # Get current credits
        credit_data = await self.redis.hgetall(key)

        if not credit_data:
            # Initialize credits
            credits = max_credits - cost
            last_refill = now
        else:
            credits = float(credit_data.get('credits', max_credits))
            last_refill = float(credit_data.get('last_refill', now))

            # Refill credits based on elapsed time
            elapsed = now - last_refill
            credits_to_add = elapsed * refill_rate
            credits = min(max_credits, credits + credits_to_add)

            # Try to consume credits
            if credits >= cost:
                credits -= cost
            else:
                return False, int(credits)

        # Update credit state
        await self.redis.hset(key, mapping={
            'credits': str(credits),
            'last_refill': str(now)
        })
        await self.redis.expire(key, 3600)

        return True, int(credits)

cost_limiter = CostBasedLimiter(redis_client)

def cost_based_limit(cost: EndpointCost):
    """
    Dependency for cost-based rate limiting.

    Usage:
        @app.get("/api/search")
        async def search(
            _: None = Depends(cost_based_limit(EndpointCost.SEARCH))
        ):
            return {"results": []}
    """
    async def check_credits(request: Request) -> None:
        identifier = await get_client_identifier(request)

        # Try to consume credits
        allowed, remaining = await cost_limiter.consume_credits(
            identifier,
            cost=cost
        )

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Insufficient credits",
                    "cost": cost,
                    "remaining": remaining
                }
            )

    return check_credits

# Usage with different costs
@app.get("/api/data")
async def get_data(
    _: None = Depends(cost_based_limit(EndpointCost.READ))
):
    """Low-cost read operation."""
    return {"data": "value"}

@app.post("/api/process")
async def process_data(
    _: None = Depends(cost_based_limit(EndpointCost.EXPENSIVE))
):
    """High-cost processing operation."""
    return {"status": "processed"}
```

### Distributed Rate Limiting (Redis Cluster)

```python
from redis.cluster import RedisCluster
from redis.cluster import ClusterNode

class DistributedRateLimiter:
    """
    Rate limiting across multiple servers using Redis Cluster.

    Ensures consistent rate limits even with multiple API servers.
    """

    def __init__(self, redis_nodes: list[ClusterNode]):
        """
        Initialize distributed rate limiter.

        Args:
            redis_nodes: List of Redis cluster nodes
        """
        self.redis = RedisCluster(
            startup_nodes=redis_nodes,
            decode_responses=True
        )

    async def check_limit_distributed(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, dict]:
        """
        Check rate limit across distributed system.

        Uses Redis transactions for atomic operations.
        """
        now = int(datetime.utcnow().timestamp())
        window_start = now - window_seconds
        key = f"rate_limit:distributed:{identifier}"

        # Use Lua script for atomic operation
        lua_script = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local window_start = tonumber(ARGV[2])
        local max_requests = tonumber(ARGV[3])
        local window_seconds = tonumber(ARGV[4])

        -- Remove old entries
        redis.call('ZREMRANGEBYSCORE', key, 0, window_start)

        -- Count requests in window
        local count = redis.call('ZCARD', key)

        if count >= max_requests then
            return {0, count, 0}
        end

        -- Add current request
        redis.call('ZADD', key, now, now)
        redis.call('EXPIRE', key, window_seconds)

        return {1, max_requests, max_requests - count - 1}
        """

        # Execute Lua script
        result = await self.redis.eval(
            lua_script,
            1,
            key,
            now,
            window_start,
            max_requests,
            window_seconds
        )

        allowed, limit, remaining = result

        return bool(allowed), {
            'allowed': bool(allowed),
            'limit': limit,
            'remaining': remaining,
            'reset': now + window_seconds
        }

# Initialize distributed limiter
distributed_limiter = DistributedRateLimiter([
    ClusterNode("redis-node-1", 6379),
    ClusterNode("redis-node-2", 6379),
    ClusterNode("redis-node-3", 6379)
])
```

### Complete Rate Limiting Example

```python
@app.get("/api/complete-rate-limit")
async def complete_rate_limit_example(
    request: Request,
    user: Optional[TokenData] = Depends(get_current_user),
    _: None = Depends(user_rate_limit())
):
    """
    Complete endpoint with:
    - Per-user rate limiting
    - Rate limit headers
    - Proper error handling
    """
    # Rate limit info available in request.state
    rate_info = request.state.rate_limit_info

    return {
        "data": "value",
        "rate_limit": {
            "limit": rate_info['limit'],
            "remaining": rate_info['remaining'],
            "reset": rate_info['reset']
        }
    }

# Custom rate limit exceeded handler
@app.exception_handler(HTTPException)
async def rate_limit_exception_handler(request: Request, exc: HTTPException):
    """Custom handler for rate limit errors."""
    if exc.status_code == 429:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "retry_after": exc.headers.get("Retry-After", 60)
            },
            headers=exc.headers
        )

    # Re-raise other exceptions
    raise exc
```

---

## 🔍 API Validation Patterns

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from typing import Annotated

app = FastAPI()

class ItemCreate(BaseModel):
    """Item creation schema."""
    name: Annotated[str, Field(
        min_length=1,
        max_length=100,
        description="Item name",
        examples=["Widget"]
    )]
    price: Annotated[float, Field(
        gt=0,
        le=1000000,
        description="Price in USD",
        examples=[19.99]
    )]
    quantity: Annotated[int, Field(
        ge=0,
        description="Available quantity",
        examples=[100]
    )]

@app.post("/items/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate) -> ItemResponse:
    """Create a new item with validation."""
    # Pydantic automatically validates the input
    # If validation fails, returns 422 Unprocessable Entity
    return ItemResponse(**item.model_dump(), id=1)
```

### Error Handling

```python
from pydantic import ValidationError
from fastapi import Request, status
from fastapi.responses import JSONResponse

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )
```

---

## 🔐 Security Best Practices

### Password Handling

```python
from pydantic import BaseModel, SecretStr, field_validator
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserLogin(BaseModel):
    """User login with secure password handling."""
    email: str
    password: SecretStr  # Never logged or serialized

    def verify_password(self, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(
            self.password.get_secret_value(),
            hashed_password
        )

class UserPasswordChange(BaseModel):
    """Password change with validation."""
    current_password: SecretStr
    new_password: SecretStr
    confirm_password: SecretStr

    @model_validator(mode='after')
    def validate_passwords(self) -> 'UserPasswordChange':
        """Validate password change requirements."""
        new_pwd = self.new_password.get_secret_value()
        confirm_pwd = self.confirm_password.get_secret_value()

        if new_pwd != confirm_pwd:
            raise ValueError('New passwords do not match')

        if len(new_pwd) < 12:
            raise ValueError('Password must be at least 12 characters')

        return self
```

### Token Validation

```python
from pydantic import BaseModel, Field, field_validator
import secrets

class APIToken(BaseModel):
    """API token with validation."""
    token: str = Field(min_length=32, max_length=256)

    @field_validator('token')
    @classmethod
    def validate_token_format(cls, v: str) -> str:
        """Ensure token is properly formatted."""
        if not re.match(r'^[A-Za-z0-9_-]+$', v):
            raise ValueError('Invalid token format')
        return v

def generate_secure_token() -> str:
    """Generate cryptographically secure token."""
    return secrets.token_urlsafe(32)
```

---

## ⚠️ Validation Best Practices

1. **Validate at boundaries** - All external inputs
2. **Use Field constraints** - Min/max length, patterns
3. **Custom validators for complex logic** - Business rules
4. **Fail fast** - Validate early in the request lifecycle
5. **Clear error messages** - Help users fix issues
6. **Sanitize HTML content** - Prevent XSS attacks
7. **Prevent SQL injection** - Validate queries
8. **Block path traversal** - Secure file operations
9. **Use SecretStr for passwords** - Never log secrets
10. **Validate in context** - Consider related fields

---

## 📋 Security Checklist

- [ ] All user inputs validated with Pydantic
- [ ] Field constraints defined (min/max, patterns)
- [ ] Custom validators for complex rules
- [ ] HTML content sanitized (bleach)
- [ ] SQL injection prevented
- [ ] Path traversal blocked
- [ ] Passwords use SecretStr
- [ ] Tokens validated and secure
- [ ] Environment variables validated
- [ ] Error messages don't leak sensitive data

---

**Back to [Core Guide](./CLAUDE-core.md)**
