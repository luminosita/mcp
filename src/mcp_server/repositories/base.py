"""
Base repository interface.

Defines abstract base class for repository pattern implementation.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository for data access operations."""

    @abstractmethod
    async def get(self, id: Any) -> T | None:
        """Retrieve entity by ID."""
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> list[T]:
        """List entities with pagination."""
        pass

    @abstractmethod
    async def create(self, data: dict[str, Any]) -> T:
        """Create new entity."""
        pass

    @abstractmethod
    async def update(self, id: Any, data: dict[str, Any]) -> T | None:
        """Update existing entity."""
        pass

    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """Delete entity by ID."""
        pass
