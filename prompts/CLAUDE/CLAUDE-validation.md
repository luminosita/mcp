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
