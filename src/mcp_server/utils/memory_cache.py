"""
In-memory caching layer with TTL expiration.

Generic in-memory cache for any string content with TTL-based expiration.
Used as fallback when Redis is unavailable.
"""

import time
from dataclasses import dataclass

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class CacheEntry:
    """
    Cache entry with TTL metadata.

    Stores cached content along with creation timestamp for TTL expiration.
    """

    content: str
    created_at: float  # Unix timestamp
    ttl_seconds: int

    @property
    def is_expired(self) -> bool:
        """Check if cache entry has expired based on TTL."""
        age = time.time() - self.created_at
        return age > self.ttl_seconds


class MemoryCache:
    """
    In-memory cache for string content with TTL expiration.

    Generic cache implementation used across MCP Server for:
    - Resource files (patterns, templates, SDLC core)
    - Generator prompts
    - Any other string content requiring caching

    Features:
    - Cache-aside pattern (lazy loading)
    - Configurable TTL for cache entries (default: 300 seconds)
    - Automatic expiration on access
    - Cache hit/miss metrics for observability

    Thread-safety: Not thread-safe. Use with asyncio single-threaded event loop.
    """

    def __init__(self, ttl_seconds: int = 300) -> None:
        """
        Initialize memory cache.

        Args:
            ttl_seconds: Time-to-live for cache entries in seconds (default: 300 = 5 minutes)
        """
        self._cache: dict[str, CacheEntry] = {}
        self.ttl_seconds = ttl_seconds
        self._hits = 0
        self._misses = 0
        logger.info(
            "memory_cache_initialized",
            ttl_seconds=ttl_seconds,
        )

    def get(self, cache_key: str) -> str | None:
        """
        Get cached content by cache key.

        Args:
            cache_key: Unique cache key

        Returns:
            Cached content if exists and not expired, None otherwise

        Side effects:
            - Increments cache hit/miss counters
            - Removes expired entries on access
        """
        entry = self._cache.get(cache_key)

        if entry is None:
            self._misses += 1
            logger.debug(
                "memory_cache_miss",
                cache_key=cache_key,
                hit_rate=self.hit_rate,
            )
            return None

        if entry.is_expired:
            # Remove expired entry
            del self._cache[cache_key]
            self._misses += 1
            logger.debug(
                "memory_cache_expired",
                cache_key=cache_key,
                age_seconds=time.time() - entry.created_at,
                ttl_seconds=entry.ttl_seconds,
            )
            return None

        self._hits += 1
        logger.debug(
            "memory_cache_hit",
            cache_key=cache_key,
            age_seconds=time.time() - entry.created_at,
            hit_rate=self.hit_rate,
        )
        return entry.content

    def set(self, cache_key: str, content: str) -> None:
        """
        Store content in cache with TTL.

        Args:
            cache_key: Unique cache key
            content: String content to cache
        """
        entry = CacheEntry(
            content=content,
            created_at=time.time(),
            ttl_seconds=self.ttl_seconds,
        )
        self._cache[cache_key] = entry
        logger.debug(
            "memory_cache_set",
            cache_key=cache_key,
            content_length=len(content),
            ttl_seconds=self.ttl_seconds,
        )

    def invalidate(self, cache_key: str) -> None:
        """
        Invalidate cache entry.

        Args:
            cache_key: Cache key to invalidate
        """
        if cache_key in self._cache:
            del self._cache[cache_key]
            logger.debug("memory_cache_invalidated", cache_key=cache_key)

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info("memory_cache_cleared")

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
