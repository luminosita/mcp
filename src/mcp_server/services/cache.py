"""
Resource caching service with Redis backend and in-memory fallback.

Implements cache-aside pattern with TTL-based expiration for MCP resources.
Provides <10ms cache hit latency for frequently accessed resources.

Supports two backends:
- Redis (primary): Distributed caching for production
- In-memory (fallback): Used when Redis is unavailable or not configured
"""

import json
import time
from collections.abc import Callable, Coroutine
from datetime import UTC, datetime
from typing import Any

import redis.asyncio as redis
import structlog
from prometheus_client import Counter, Gauge, Histogram

from mcp_server.config import settings

logger = structlog.get_logger(__name__)

# Prometheus metrics for cache monitoring
cache_hits_total = Counter(
    "mcp_resource_cache_hits_total",
    "Total number of cache hits",
    ["resource_type"],
)

cache_misses_total = Counter(
    "mcp_resource_cache_misses_total",
    "Total number of cache misses",
    ["resource_type"],
)

cache_size = Gauge(
    "mcp_resource_cache_size",
    "Number of cached resources",
)

cache_latency_seconds = Histogram(
    "mcp_resource_cache_latency_seconds",
    "Cache lookup latency distribution",
    ["cache_result"],  # hit or miss
    buckets=[0.001, 0.005, 0.010, 0.050, 0.100],
)


class ResourceCacheService:
    """
    Caching service for MCP resources with Redis backend and in-memory fallback.

    Implements cache-aside pattern with TTL-based expiration.
    Provides distributed caching for horizontal scalability (Redis) or
    in-memory caching when Redis is unavailable.

    Attributes:
        redis: Async Redis client (None if using in-memory fallback)
        ttl_seconds: Time-to-live for cache entries (default: 300s)
        _in_memory_cache: In-memory cache used when Redis unavailable
        _use_redis: Flag indicating which backend is active
    """

    def __init__(self, redis_url: str | None = None, ttl_seconds: int | None = None):
        """
        Initialize cache service with Redis connection and in-memory fallback.

        Args:
            redis_url: Redis connection URL (defaults to settings.redis_url)
            ttl_seconds: Cache TTL in seconds (defaults to settings.cache_ttl)
        """
        from mcp_server.utils import MemoryCache

        self.redis_url = redis_url or settings.redis_url
        self.ttl_seconds = ttl_seconds or settings.cache_ttl

        # Redis client initialized lazily in async context
        self._redis: redis.Redis | None = None

        # In-memory cache fallback
        self._in_memory_cache = MemoryCache(ttl_seconds=self.ttl_seconds)
        self._use_redis = False  # Track which backend is active

    async def connect(self) -> None:
        """
        Establish Redis connection with automatic fallback to in-memory cache.

        Should be called on application startup.

        Behavior:
        - Attempts Redis connection first
        - Falls back to in-memory cache if Redis unavailable
        - Logs backend selection for observability
        """
        if self._redis is None:
            try:
                self._redis = await redis.from_url(  # type: ignore[no-untyped-call]
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
                # Verify connection with ping
                await self._redis.ping()
                self._use_redis = True
                logger.info(
                    "cache_connected_redis",
                    redis_url=self.redis_url,
                    ttl_seconds=self.ttl_seconds,
                    backend="redis",
                )
            except Exception as e:
                # Fall back to in-memory cache
                self._redis = None
                self._use_redis = False
                logger.warning(
                    "cache_redis_unavailable_using_fallback",
                    redis_url=self.redis_url,
                    error=str(e),
                    backend="in-memory",
                    ttl_seconds=self.ttl_seconds,
                )

    async def disconnect(self) -> None:
        """
        Close Redis connection.

        Should be called on application shutdown.
        In-memory cache is automatically cleaned up.
        """
        if self._redis is not None:
            await self._redis.aclose()
            self._redis = None
            self._use_redis = False
            logger.info("cache_disconnected", backend="redis")
        else:
            logger.info("cache_disconnected", backend="in-memory")

    @property
    def redis(self) -> redis.Redis:
        """
        Get Redis client instance.

        Raises:
            RuntimeError: If Redis connection not established
        """
        if self._redis is None:
            raise RuntimeError("Redis connection not established. Using in-memory cache fallback.")
        return self._redis

    async def get_or_fetch(
        self,
        cache_key: str,
        fetch_func: Callable[[str], Coroutine[Any, Any, str]],
        file_path: str,
        resource_type: str = "unknown",
    ) -> str:
        """
        Get resource from cache or fetch from source (cache-aside pattern).

        Supports both Redis and in-memory backends with automatic fallback.
        Provides <10ms latency on cache hit, ~50ms on cache miss.

        Args:
            cache_key: Unique cache key (format: resource:{type}:{name})
            fetch_func: Async function to fetch content on cache miss
            file_path: File path to pass to fetch_func
            resource_type: Resource type for metrics (patterns, templates, sdlc)

        Returns:
            str: Resource content

        Raises:
            Exception: Propagates exceptions from fetch_func on cache miss
        """
        start_time = time.time()
        backend = "redis" if self._use_redis else "in-memory"

        # Try cache first
        cached_content = await self._cache_get(cache_key)
        if cached_content is not None:
            # Cache hit - return immediately
            latency = time.time() - start_time
            cache_hits_total.labels(resource_type=resource_type).inc()
            cache_latency_seconds.labels(cache_result="hit").observe(latency)

            logger.debug(
                "cache_hit",
                cache_key=cache_key,
                resource_type=resource_type,
                backend=backend,
                latency_ms=latency * 1000,
            )

            return cached_content

        # Cache miss - fetch from source
        cache_misses_total.labels(resource_type=resource_type).inc()
        logger.debug(
            "cache_miss",
            cache_key=cache_key,
            resource_type=resource_type,
            backend=backend,
        )

        # Fetch content from source (disk I/O)
        content = await fetch_func(file_path)

        # Store in cache with TTL
        await self._cache_set(cache_key, content, file_path, resource_type)

        # Update metrics
        latency = time.time() - start_time
        cache_latency_seconds.labels(cache_result="miss").observe(latency)

        logger.debug(
            "cache_miss_fetched",
            cache_key=cache_key,
            resource_type=resource_type,
            backend=backend,
            latency_ms=latency * 1000,
        )

        return content

    async def _cache_get(self, cache_key: str) -> str | None:
        """
        Get content from cache (backend-agnostic).

        Args:
            cache_key: Unique cache key

        Returns:
            Cached content if exists and not expired, None otherwise
        """
        if self._use_redis:
            try:
                cached = await self.redis.get(cache_key)
                if cached:
                    cache_data = json.loads(cached)
                    return str(cache_data["content"])
            except Exception as e:
                # Log cache read error but don't fail - return None
                logger.warning(
                    "cache_read_error",
                    cache_key=cache_key,
                    backend="redis",
                    error=str(e),
                )
            return None
        else:
            return self._in_memory_cache.get(cache_key)

    async def _cache_set(
        self,
        cache_key: str,
        content: str,
        file_path: str,
        resource_type: str,
    ) -> None:
        """
        Store content in cache (backend-agnostic).

        Args:
            cache_key: Unique cache key
            content: Content to cache
            file_path: Source file path (metadata)
            resource_type: Resource type (metadata)
        """
        if self._use_redis:
            try:
                cache_data = {
                    "content": content,
                    "cached_at": datetime.now(UTC).isoformat(),
                    "file_path": file_path,
                    "resource_type": resource_type,
                }
                await self.redis.setex(
                    cache_key,
                    self.ttl_seconds,
                    json.dumps(cache_data),
                )

                logger.debug(
                    "cache_stored",
                    cache_key=cache_key,
                    resource_type=resource_type,
                    backend="redis",
                    ttl_seconds=self.ttl_seconds,
                )
            except Exception as e:
                # Log cache write error but don't fail - content already fetched
                logger.warning(
                    "cache_write_error",
                    cache_key=cache_key,
                    backend="redis",
                    error=str(e),
                )
        else:
            self._in_memory_cache.set(cache_key, content)
            logger.debug(
                "cache_stored",
                cache_key=cache_key,
                resource_type=resource_type,
                backend="in-memory",
                ttl_seconds=self.ttl_seconds,
            )

    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all cache keys matching pattern.

        Supports both Redis and in-memory backends.

        Args:
            pattern: Key pattern (e.g., "resource:patterns:*")
                     Uses Redis pattern syntax for Redis backend
                     Uses simple glob pattern for in-memory backend

        Returns:
            int: Number of keys invalidated
        """
        if self._use_redis:
            try:
                keys = await self.redis.keys(pattern)
                if keys:
                    deleted_count = await self.redis.delete(*keys)
                    logger.info(
                        "cache_invalidated",
                        pattern=pattern,
                        deleted_count=deleted_count,
                        backend="redis",
                    )
                    return int(deleted_count)
                return 0
            except Exception as e:
                logger.error(
                    "cache_invalidation_error",
                    pattern=pattern,
                    backend="redis",
                    error=str(e),
                )
                raise
        else:
            # In-memory cache: clear all (pattern matching not supported in simple impl)
            # Could be enhanced with fnmatch for pattern matching if needed
            self._in_memory_cache.clear()
            logger.info(
                "cache_invalidated",
                pattern=pattern,
                backend="in-memory",
                note="cleared_all_entries",
            )
            return 0  # Return 0 as we don't track exact count for in-memory

    async def get_cache_size(self) -> int:
        """
        Get number of cached resources.

        Supports both Redis and in-memory backends.

        Returns:
            int: Current cache size (number of keys)
        """
        if self._use_redis:
            try:
                size = await self.redis.dbsize()
                cache_size.set(size)
                return int(size)
            except Exception as e:
                logger.error(
                    "cache_size_error",
                    backend="redis",
                    error=str(e),
                )
                raise
        else:
            size = self._in_memory_cache.size
            cache_size.set(size)
            return size


# Global cache service instance
# Initialized on application startup via lifespan context manager
cache_service = ResourceCacheService()
