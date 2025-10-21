# patterns-architecture-patterns - Design Patterns & FastAPI


> **Specialized Guide**: Design patterns, dependency injection, and FastAPI application structure.

> **Specialized Guide**: Comprehensive project architecture, modularity patterns, and design principles for Python projects.
## 🔧 Design Patterns

### Repository Pattern

```python
# src/mcp_server/repositories/base.py
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

# src/mcp_server/repositories/user_repository.py
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
# src/mcp_server/services/user_service.py
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
# src/mcp_server/core/dependencies.py
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
# src/mcp_server/main.py
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
# src/mcp_server/api/routes/users.py
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
