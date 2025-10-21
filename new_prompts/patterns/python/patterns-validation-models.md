# patterns-validation-models - Pydantic Models & Validation


> **Specialized Guide**: Pydantic v2 models, field validation, model configuration, CRUD patterns, and environment settings.

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
