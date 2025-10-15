# CLAUDE-architecture.md - Project Structure & Design Patterns

> **Specialized Guide**: Comprehensive project architecture, modularity patterns, and design principles for Python projects.

## 🏗️ Project Structure Philosophy

### Src Layout Benefits
- **Better test isolation** - Tests can't accidentally import from source
- **Cleaner imports** - Explicit package structure
- **Editable installs** - Proper development workflow
- **Distribution ready** - Build and publish easily

### Vertical Slice Architecture
- **Feature-based organization** - Group by feature, not layer
- **Tests live with code** - Easy to find and maintain
- **Clear boundaries** - Self-contained modules
- **Reduced coupling** - Features are independent

---

## 📁 Standard Project Structure

### Basic Layout

```
project-root/
├── pyproject.toml              # Project metadata and dependencies
├── uv.lock                     # Locked dependencies
├── README.md                   # Project documentation
├── LICENSE                     # License file
├── .gitignore                  # Git ignore rules
├── .env.example                # Example environment variables
│
├── .claude/                    # Claude Code configuration
│   └── commands/               # Custom commands
│
├── src/                        # Source code
│   └── project_name/
│       ├── __init__.py
│       ├── __main__.py         # Entry point for -m execution
│       ├── main.py             # Application entry
│       │
│       ├── core/               # Core business logic
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── exceptions.py
│       │   └── constants.py
│       │
│       ├── models/             # Data models
│       │   ├── __init__.py
│       │   ├── user.py
│       │   └── product.py
│       │
│       ├── services/           # Business services
│       │   ├── __init__.py
│       │   ├── user_service.py
│       │   └── auth_service.py
│       │
│       ├── repositories/       # Data access layer
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── user_repository.py
│       │
│       ├── api/                # API endpoints
│       │   ├── __init__.py
│       │   ├── routes/
│       │   │   ├── users.py
│       │   │   └── products.py
│       │   └── schemas/
│       │       ├── user.py
│       │       └── product.py
│       │
│       ├── utils/              # Utility functions
│       │   ├── __init__.py
│       │   ├── helpers.py
│       │   └── validators.py
│       │
│       └── config/             # Configuration
│           ├── __init__.py
│           └── settings.py
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Shared fixtures
│   │
│   ├── unit/                   # Unit tests
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_utils.py
│   │
│   ├── integration/            # Integration tests
│   │   ├── test_database.py
│   │   └── test_api.py
│   │
│   └── e2e/                    # End-to-end tests
│       └── test_workflows.py
│
├── docs/                       # Documentation
│   ├── api.md
│   ├── architecture.md
│   └── deployment.md
│
└── scripts/                    # Development scripts (NuShell)
    ├── setup.nu                # Main setup script (orchestrator)
    ├── lib/                    # NuShell modules (use explicit exports)
    └── tests/                  # Script test suite
        └── integration         # Integration script test suite
```

---

## 🎯 Alternative: Vertical Slice Structure

### Feature-Based Organization

```
project-root/
├── src/
│   └── project_name/
│       ├── __init__.py
│       ├── main.py
│       │
│       ├── shared/             # Shared components
│       │   ├── __init__.py
│       │   ├── database.py
│       │   ├── exceptions.py
│       │   └── middleware.py
│       │
│       ├── features/           # Feature slices
│       │   │
│       │   ├── users/          # User management feature
│       │   │   ├── __init__.py
│       │   │   ├── models.py
│       │   │   ├── service.py
│       │   │   ├── repository.py
│       │   │   ├── routes.py
│       │   │   ├── schemas.py
│       │   │   └── tests/
│       │   │       ├── test_service.py
│       │   │       └── test_routes.py
│       │   │
│       │   ├── products/       # Product management feature
│       │   │   ├── __init__.py
│       │   │   ├── models.py
│       │   │   ├── service.py
│       │   │   ├── repository.py
│       │   │   ├── routes.py
│       │   │   ├── schemas.py
│       │   │   └── tests/
│       │   │       ├── test_service.py
│       │   │       └── test_routes.py
│       │   │
│       │   └── orders/         # Order processing feature
│       │       ├── __init__.py
│       │       ├── models.py
│       │       ├── service.py
│       │       ├── repository.py
│       │       ├── routes.py
│       │       ├── schemas.py
│       │       └── tests/
│       │           ├── test_service.py
│       │           └── test_routes.py
│       │
│       └── config/
│           └── settings.py
```

---

## 🔧 Design Patterns

### Repository Pattern

```python
# src/project_name/repositories/base.py
from typing import TypeVar, Generic, Optional, List
from abc import ABC, abstractmethod

T = TypeVar('T')

class BaseRepository(Generic[T], ABC):
    """Base repository interface."""

    @abstractmethod
    async def find_by_id(self, id_: int) -> Optional[T]:
        """Find entity by ID."""
        pass

    @abstractmethod
    async def find_all(self) -> List[T]:
        """Find all entities."""
        pass

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create new entity."""
        pass

    @abstractmethod
    async def update(self, id_: int, entity: T) -> Optional[T]:
        """Update existing entity."""
        pass

    @abstractmethod
    async def delete(self, id_: int) -> bool:
        """Delete entity by ID."""
        pass

# src/project_name/repositories/user_repository.py
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .base import BaseRepository
from ..models.user import User

class UserRepository(BaseRepository[User]):
    """User repository implementation."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_id(self, id_: int) -> Optional[User]:
        """Find user by ID."""
        result = await self._session.execute(
            select(User).where(User.id == id_)
        )
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        result = await self._session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def find_all(self) -> List[User]:
        """Find all users."""
        result = await self._session.execute(select(User))
        return list(result.scalars().all())

    async def create(self, user: User) -> User:
        """Create new user."""
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def update(self, id_: int, user: User) -> Optional[User]:
        """Update existing user."""
        existing = await self.find_by_id(id_)
        if not existing:
            return None

        for key, value in user.__dict__.items():
            if not key.startswith('_'):
                setattr(existing, key, value)

        await self._session.commit()
        await self._session.refresh(existing)
        return existing

    async def delete(self, id_: int) -> bool:
        """Delete user by ID."""
        user = await self.find_by_id(id_)
        if not user:
            return False

        await self._session.delete(user)
        await self._session.commit()
        return True
```

### Service Layer Pattern

```python
# src/project_name/services/user_service.py
from typing import Optional, List
from ..repositories.user_repository import UserRepository
from ..models.user import User
from ..core.exceptions import UserNotFoundError, DuplicateEmailError
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    """User business logic service."""

    def __init__(self, repository: UserRepository):
        self._repository = repository

    async def get_user(self, user_id: int) -> User:
        """Get user by ID."""
        user = await self._repository.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        return user

    async def get_all_users(self) -> List[User]:
        """Get all users."""
        return await self._repository.find_all()

    async def create_user(
        self,
        email: str,
        password: str,
        name: str
    ) -> User:
        """Create new user."""
        # Check for duplicate email
        existing = await self._repository.find_by_email(email)
        if existing:
            raise DuplicateEmailError(f"Email {email} already exists")

        # Hash password
        hashed_password = pwd_context.hash(password)

        # Create user
        user = User(
            email=email,
            hashed_password=hashed_password,
            name=name
        )

        return await self._repository.create(user)

    async def update_user(
        self,
        user_id: int,
        email: Optional[str] = None,
        name: Optional[str] = None
    ) -> User:
        """Update user details."""
        user = await self.get_user(user_id)

        if email and email != user.email:
            existing = await self._repository.find_by_email(email)
            if existing:
                raise DuplicateEmailError(f"Email {email} already exists")
            user.email = email

        if name:
            user.name = name

        updated = await self._repository.update(user_id, user)
        if not updated:
            raise UserNotFoundError(f"User {user_id} not found")

        return updated

    async def delete_user(self, user_id: int) -> None:
        """Delete user."""
        success = await self._repository.delete(user_id)
        if not success:
            raise UserNotFoundError(f"User {user_id} not found")

    async def verify_password(
        self,
        email: str,
        password: str
    ) -> Optional[User]:
        """Verify user credentials."""
        user = await self._repository.find_by_email(email)
        if not user:
            return None

        if not pwd_context.verify(password, user.hashed_password):
            return None

        return user
```

### Dependency Injection Pattern

```python
# src/project_name/core/dependencies.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from ..config.settings import get_settings
from ..repositories.user_repository import UserRepository
from ..services.user_service import UserService

settings = get_settings()

# Database engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_size=settings.database_pool_size,
)

# Session factory
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_user_repository(
    session: AsyncSession
) -> UserRepository:
    """Get user repository."""
    return UserRepository(session)

async def get_user_service(
    repository: UserRepository
) -> UserService:
    """Get user service."""
    return UserService(repository)

# FastAPI integration
from fastapi import Depends

async def get_current_user_service(
    session: AsyncSession = Depends(get_db_session)
) -> UserService:
    """Get user service with injected dependencies."""
    repository = await get_user_repository(session)
    return await get_user_service(repository)
```

---

## 🌐 FastAPI Application Structure

### Application Factory

```python
# src/project_name/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import users, products, orders
from .config.settings import get_settings
from .core.exceptions import setup_exception_handlers

def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="1.0.0",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(users.router, prefix="/api/v1", tags=["users"])
    app.include_router(products.router, prefix="/api/v1", tags=["products"])
    app.include_router(orders.router, prefix="/api/v1", tags=["orders"])

    # Setup exception handlers
    setup_exception_handlers(app)

    return app

app = create_app()
```

### API Routes Structure

```python
# src/project_name/api/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ...services.user_service import UserService
from ...core.dependencies import get_current_user_service
from ..schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter()

@router.post(
    "/users/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user"
)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_current_user_service)
) -> UserResponse:
    """Create a new user account."""
    user = await service.create_user(
        email=user_data.email,
        password=user_data.password,
        name=user_data.name
    )
    return UserResponse.model_validate(user)

@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID"
)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_current_user_service)
) -> UserResponse:
    """Retrieve user by ID."""
    user = await service.get_user(user_id)
    return UserResponse.model_validate(user)

@router.get(
    "/users/",
    response_model=List[UserResponse],
    summary="List all users"
)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    service: UserService = Depends(get_current_user_service)
) -> List[UserResponse]:
    """List all users with pagination."""
    users = await service.get_all_users()
    return [UserResponse.model_validate(user) for user in users[skip:skip + limit]]

@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Update user"
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    service: UserService = Depends(get_current_user_service)
) -> UserResponse:
    """Update user details."""
    user = await service.update_user(
        user_id=user_id,
        email=user_data.email,
        name=user_data.name
    )
    return UserResponse.model_validate(user)

@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user"
)
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_current_user_service)
) -> None:
    """Delete user by ID."""
    await service.delete_user(user_id)
```

---

## 🔒 Exception Handling

### Custom Exceptions

```python
# src/project_name/core/exceptions.py
class AppException(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class UserNotFoundError(AppException):
    """User not found exception."""
    def __init__(self, message: str = "User not found"):
        super().__init__(message, status_code=404)

class DuplicateEmailError(AppException):
    """Duplicate email exception."""
    def __init__(self, message: str = "Email already exists"):
        super().__init__(message, status_code=409)

class UnauthorizedError(AppException):
    """Unauthorized access exception."""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)

class ValidationError(AppException):
    """Validation error exception."""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=422)
```

### Exception Handlers

```python
# src/project_name/core/exception_handlers.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from .exceptions import AppException
import logging

logger = logging.getLogger(__name__)

def setup_exception_handlers(app: FastAPI) -> None:
    """Setup application exception handlers."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """Handle application exceptions."""
        logger.error(f"Application error: {exc.message}", exc_info=True)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.__class__.__name__,
                "message": exc.message,
                "path": str(request.url)
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "path": str(request.url)
            }
        )
```

---

## 🌐 CORS (Cross-Origin Resource Sharing) Configuration

### Basic CORS Setup

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Basic CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
```

### Production CORS Configuration

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import re
from pydantic_settings import BaseSettings

class CORSSettings(BaseSettings):
    """CORS configuration settings."""
    # Allowed origins (exact match)
    allowed_origins: List[str] = [
        "https://app.example.com",
        "https://admin.example.com",
    ]

    # Allowed origin patterns (regex)
    allowed_origin_patterns: List[str] = [
        r"^https://.*\.example\.com$",  # All subdomains
        r"^http://localhost:\d+$",       # Any localhost port (dev only)
    ]

    # CORS settings
    allow_credentials: bool = True
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    allowed_headers: List[str] = [
        "Content-Type",
        "Authorization",
        "X-Request-ID",
        "X-API-Key",
    ]
    expose_headers: List[str] = [
        "X-Total-Count",
        "X-Page-Count",
    ]
    max_age: int = 3600  # Cache preflight requests for 1 hour

def is_allowed_origin(origin: str, settings: CORSSettings) -> bool:
    """
    Check if origin is allowed.

    Validates against:
    1. Exact match in allowed_origins
    2. Pattern match in allowed_origin_patterns
    """
    # Check exact match
    if origin in settings.allowed_origins:
        return True

    # Check pattern match
    for pattern in settings.allowed_origin_patterns:
        if re.match(pattern, origin):
            return True

    return False

# Configure CORS
cors_settings = CORSSettings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_settings.allowed_origins,
    allow_origin_regex="|".join(cors_settings.allowed_origin_patterns),
    allow_credentials=cors_settings.allow_credentials,
    allow_methods=cors_settings.allowed_methods,
    allow_headers=cors_settings.allowed_headers,
    expose_headers=cors_settings.expose_headers,
    max_age=cors_settings.max_age,
)
```

### Custom CORS Middleware (Advanced Control)

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi import Request
import re

class CustomCORSMiddleware(BaseHTTPMiddleware):
    """
    Custom CORS middleware with fine-grained control.

    Features:
    - Dynamic origin validation
    - Per-route CORS policies
    - Credentials handling
    - Custom preflight optimization
    """

    def __init__(
        self,
        app,
        allowed_origins: List[str],
        allowed_origin_patterns: List[str],
        allow_credentials: bool = True,
        allowed_methods: List[str] = None,
        allowed_headers: List[str] = None,
        expose_headers: List[str] = None,
        max_age: int = 3600
    ):
        super().__init__(app)
        self.allowed_origins = set(allowed_origins)
        self.allowed_origin_patterns = [re.compile(p) for p in allowed_origin_patterns]
        self.allow_credentials = allow_credentials
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE"]
        self.allowed_headers = allowed_headers or ["*"]
        self.expose_headers = expose_headers or []
        self.max_age = max_age

    def is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed."""
        # Exact match
        if origin in self.allowed_origins:
            return True

        # Pattern match
        for pattern in self.allowed_origin_patterns:
            if pattern.match(origin):
                return True

        return False

    async def dispatch(self, request: Request, call_next):
        """Process CORS headers for all requests."""
        origin = request.headers.get("origin")

        # Handle preflight requests (OPTIONS)
        if request.method == "OPTIONS":
            return self.handle_preflight(request, origin)

        # Process actual request
        response = await call_next(request)

        # Add CORS headers to response
        if origin and self.is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin

            if self.allow_credentials:
                response.headers["Access-Control-Allow-Credentials"] = "true"

            if self.expose_headers:
                response.headers["Access-Control-Expose-Headers"] = ", ".join(
                    self.expose_headers
                )

        return response

    def handle_preflight(self, request: Request, origin: str) -> Response:
        """
        Handle CORS preflight (OPTIONS) request.

        Preflight optimization:
        - Cache preflight responses (max_age)
        - Validate requested method and headers
        - Return minimal response
        """
        # Validate origin
        if not origin or not self.is_origin_allowed(origin):
            return Response(status_code=403, content="Origin not allowed")

        # Get requested method and headers
        requested_method = request.headers.get("Access-Control-Request-Method")
        requested_headers = request.headers.get("Access-Control-Request-Headers", "")

        # Validate requested method
        if requested_method and requested_method not in self.allowed_methods:
            return Response(status_code=403, content="Method not allowed")

        # Build preflight response headers
        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": ", ".join(self.allowed_methods),
            "Access-Control-Max-Age": str(self.max_age),
        }

        if self.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"

        # Handle requested headers
        if self.allowed_headers == ["*"]:
            # Allow all requested headers
            headers["Access-Control-Allow-Headers"] = requested_headers or "*"
        else:
            # Only allow specific headers
            headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)

        if self.expose_headers:
            headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)

        return Response(status_code=200, headers=headers)

# Usage
app.add_middleware(
    CustomCORSMiddleware,
    allowed_origins=["https://app.example.com"],
    allowed_origin_patterns=[r"^https://.*\.example\.com$"],
    allow_credentials=True,
    allowed_methods=["GET", "POST", "PUT", "DELETE"],
    allowed_headers=["Content-Type", "Authorization"],
    expose_headers=["X-Total-Count"],
    max_age=3600
)
```

### Per-Route CORS Policies

```python
from fastapi import FastAPI, Request, Response
from typing import Optional, List
from functools import wraps

class RouteCORSPolicy:
    """Per-route CORS policy definition."""
    def __init__(
        self,
        allowed_origins: List[str],
        allow_credentials: bool = False,
        allowed_methods: Optional[List[str]] = None,
        allowed_headers: Optional[List[str]] = None
    ):
        self.allowed_origins = set(allowed_origins)
        self.allow_credentials = allow_credentials
        self.allowed_methods = allowed_methods or ["GET", "POST"]
        self.allowed_headers = allowed_headers or ["Content-Type"]

def cors_route(policy: RouteCORSPolicy):
    """
    Decorator for route-specific CORS policies.

    Usage:
        @app.get("/api/public")
        @cors_route(public_policy)
        async def public_endpoint():
            return {"data": "public"}
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            origin = request.headers.get("origin")

            # Handle preflight
            if request.method == "OPTIONS":
                if origin and origin in policy.allowed_origins:
                    headers = {
                        "Access-Control-Allow-Origin": origin,
                        "Access-Control-Allow-Methods": ", ".join(policy.allowed_methods),
                        "Access-Control-Allow-Headers": ", ".join(policy.allowed_headers),
                        "Access-Control-Max-Age": "3600",
                    }
                    if policy.allow_credentials:
                        headers["Access-Control-Allow-Credentials"] = "true"

                    return Response(status_code=200, headers=headers)
                else:
                    return Response(status_code=403)

            # Execute route
            response = await func(*args, request=request, **kwargs)

            # Add CORS headers
            if origin and origin in policy.allowed_origins:
                response.headers["Access-Control-Allow-Origin"] = origin
                if policy.allow_credentials:
                    response.headers["Access-Control-Allow-Credentials"] = "true"

            return response

        return wrapper
    return decorator

# Define policies
public_policy = RouteCORSPolicy(
    allowed_origins=["*"],
    allow_credentials=False
)

authenticated_policy = RouteCORSPolicy(
    allowed_origins=["https://app.example.com"],
    allow_credentials=True,
    allowed_methods=["GET", "POST", "PUT", "DELETE"]
)

# Apply to routes
@app.get("/api/public")
@cors_route(public_policy)
async def public_endpoint(request: Request):
    """Public endpoint with relaxed CORS."""
    return {"data": "public"}

@app.post("/api/secure")
@cors_route(authenticated_policy)
async def secure_endpoint(request: Request):
    """Secure endpoint with strict CORS."""
    return {"data": "secure"}
```

### Environment-Based CORS Configuration

```python
from pydantic_settings import BaseSettings
from typing import List
from enum import Enum

class Environment(str, Enum):
    """Application environment."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    """Application settings with environment-aware CORS."""
    environment: Environment = Environment.DEVELOPMENT

    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins based on environment."""
        if self.environment == Environment.DEVELOPMENT:
            return [
                "http://localhost:3000",
                "http://localhost:8080",
                "http://127.0.0.1:3000",
            ]
        elif self.environment == Environment.STAGING:
            return [
                "https://staging.example.com",
                "https://staging-admin.example.com",
            ]
        else:  # PRODUCTION
            return [
                "https://app.example.com",
                "https://admin.example.com",
            ]

    @property
    def cors_allow_credentials(self) -> bool:
        """Allow credentials in CORS."""
        # Disable credentials in development for easier testing
        return self.environment != Environment.DEVELOPMENT

    @property
    def cors_max_age(self) -> int:
        """CORS preflight cache duration."""
        # Longer cache in production
        if self.environment == Environment.PRODUCTION:
            return 7200  # 2 hours
        return 600  # 10 minutes

settings = Settings()

# Configure CORS based on environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    max_age=settings.cors_max_age,
)
```

### CORS Security Best Practices

```python
"""
CORS Security Guidelines:

✅ DO:

1. Explicitly list allowed origins
   - allow_origins=["https://app.example.com"]
   - Use environment variables for different environments

2. Use allow_credentials=True only when necessary
   - Required for cookies, authorization headers
   - Must specify exact origins (not "*")

3. Limit allowed methods
   - allow_methods=["GET", "POST", "PUT", "DELETE"]
   - Don't use ["*"] in production

4. Limit allowed headers
   - List specific headers needed
   - ["Content-Type", "Authorization", "X-API-Key"]

5. Set appropriate max_age
   - Cache preflight requests (3600-7200 seconds)
   - Reduces OPTIONS requests

6. Use regex patterns carefully
   - Validate subdomain patterns: r"^https://.*\.example\.com$"
   - Escape special characters

7. Log CORS violations
   - Monitor rejected origins
   - Detect potential attacks

❌ DON'T:

1. Use allow_origins=["*"] with credentials
   - Security risk: exposes authentication to all origins
   - Browser will reject this configuration

2. Use wildcard (*) in production
   - Allow specific origins only
   - Wildcard acceptable only for public APIs

3. Allow all methods
   - Limit to what's actually needed
   - Reduces attack surface

4. Trust user-provided origin header
   - Always validate against whitelist
   - Origin header can be spoofed (but browser enforces it)

5. Forget about preflight caching
   - Missing max_age causes excessive OPTIONS requests
   - Set reasonable cache duration

6. Mix HTTP and HTTPS origins
   - Use HTTPS everywhere in production
   - HTTP allowed only for localhost development

EXAMPLE - Secure Production Configuration:

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.example.com",
        "https://admin.example.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
    expose_headers=["X-Total-Count", "X-Page-Number"],
    max_age=3600
)
"""
```

### Troubleshooting CORS Issues

```python
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import logging

logger = logging.getLogger(__name__)

class CORSDebugMiddleware(BaseHTTPMiddleware):
    """
    Debug middleware to log CORS requests.

    Helps diagnose CORS issues in development.
    """

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")

        # Log CORS-related info
        if origin:
            logger.info(f"CORS Request: {request.method} {request.url.path}")
            logger.info(f"  Origin: {origin}")
            logger.info(f"  Headers: {dict(request.headers)}")

            if request.method == "OPTIONS":
                logger.info("  Preflight Request Detected")
                logger.info(f"    Requested Method: {request.headers.get('Access-Control-Request-Method')}")
                logger.info(f"    Requested Headers: {request.headers.get('Access-Control-Request-Headers')}")

        response = await call_next(request)

        # Log CORS response headers
        if origin:
            cors_headers = {
                k: v for k, v in response.headers.items()
                if k.lower().startswith('access-control-')
            }
            logger.info(f"  Response CORS Headers: {cors_headers}")

        return response

# Use in development only
if settings.environment == Environment.DEVELOPMENT:
    app.add_middleware(CORSDebugMiddleware)

# Common CORS errors and solutions:
"""
1. "No 'Access-Control-Allow-Origin' header present"
   - Origin not in allowed_origins list
   - Check CORS middleware is installed
   - Verify origin matches exactly (including protocol and port)

2. "Credentials flag is true, but Access-Control-Allow-Credentials header is not present"
   - Set allow_credentials=True in CORS config
   - Ensure origin is specific (not "*")

3. "Method X not allowed by Access-Control-Allow-Methods"
   - Add method to allowed_methods list
   - Check if using correct HTTP method

4. "Request header X not allowed by Access-Control-Allow-Headers"
   - Add header to allowed_headers list
   - Or use allow_headers=["*"] (not recommended for production)

5. "Preflight request didn't succeed"
   - OPTIONS request failing
   - Check if endpoint exists
   - Verify CORS middleware is before route handlers
"""
```

---

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
