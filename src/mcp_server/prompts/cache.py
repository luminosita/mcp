"""
Prompt caching layer with TTL expiration.

In-memory cache for generator XML content with 5-minute TTL.
Implements TASK-010: Prompt caching layer with TTL.
"""

import time
from dataclasses import dataclass

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class CacheEntry:
    """
    Cache entry with TTL metadata.

    Stores cached prompt content along with creation timestamp for TTL expiration.
    """

    content: str
    created_at: float  # Unix timestamp
    ttl_seconds: int

    @property
    def is_expired(self) -> bool:
        """Check if cache entry has expired based on TTL."""
        age = time.time() - self.created_at
        return age > self.ttl_seconds


class PromptCache:
    """
    In-memory cache for generator prompts with TTL expiration.

    Features:
    - Cache-aside pattern (lazy loading)
    - 5-minute default TTL for cache entries
    - Automatic expiration on access
    - Cache hit/miss metrics for observability

    Thread-safety: Not thread-safe. Use with asyncio single-threaded event loop.
    """

    def __init__(self, ttl_seconds: int = 300) -> None:
        """
        Initialize prompt cache.

        Args:
            ttl_seconds: Time-to-live for cache entries in seconds (default: 300 = 5 minutes)
        """
        self._cache: dict[str, CacheEntry] = {}
        self.ttl_seconds = ttl_seconds
        self._hits = 0
        self._misses = 0
        logger.info(
            "prompt_cache_initialized",
            ttl_seconds=ttl_seconds,
        )

    def get(self, artifact_name: str) -> str | None:
        """
        Get cached prompt content by artifact name.

        Returns:
            Cached content if exists and not expired, None otherwise

        Side effects:
            - Increments cache hit/miss counters
            - Removes expired entries on access
        """
        entry = self._cache.get(artifact_name)

        if entry is None:
            self._misses += 1
            logger.debug(
                "prompt_cache_miss",
                artifact_name=artifact_name,
                hit_rate=self.hit_rate,
            )
            return None

        if entry.is_expired:
            # Remove expired entry
            del self._cache[artifact_name]
            self._misses += 1
            logger.debug(
                "prompt_cache_expired",
                artifact_name=artifact_name,
                age_seconds=time.time() - entry.created_at,
                ttl_seconds=entry.ttl_seconds,
            )
            return None

        self._hits += 1
        logger.debug(
            "prompt_cache_hit",
            artifact_name=artifact_name,
            age_seconds=time.time() - entry.created_at,
            hit_rate=self.hit_rate,
        )
        return entry.content

    def set(self, artifact_name: str, content: str) -> None:
        """
        Store prompt content in cache with TTL.

        Args:
            artifact_name: Artifact name (cache key)
            content: Generator XML content (cache value)
        """
        entry = CacheEntry(
            content=content,
            created_at=time.time(),
            ttl_seconds=self.ttl_seconds,
        )
        self._cache[artifact_name] = entry
        logger.debug(
            "prompt_cache_set",
            artifact_name=artifact_name,
            content_length=len(content),
            ttl_seconds=self.ttl_seconds,
        )

    def invalidate(self, artifact_name: str) -> None:
        """
        Invalidate cache entry for artifact.

        Args:
            artifact_name: Artifact name to invalidate
        """
        if artifact_name in self._cache:
            del self._cache[artifact_name]
            logger.debug("prompt_cache_invalidated", artifact_name=artifact_name)

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info("prompt_cache_cleared")

    @property
    def size(self) -> int:
        """Get number of entries in cache."""
        return len(self._cache)

    @property
    def hit_rate(self) -> float:
        """
        Calculate cache hit rate.

        Returns:
            Hit rate as percentage (0.0 to 1.0)
        """
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total

    def get_stats(self) -> dict[str, int | float]:
        """
        Get cache statistics for observability.

        Returns:
            Dictionary with cache metrics
        """
        return {
            "size": self.size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self.hit_rate,
            "ttl_seconds": self.ttl_seconds,
        }
