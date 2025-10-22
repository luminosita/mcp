"""
Resource caching service with Redis backend.

Implements cache-aside pattern with TTL-based expiration for MCP resources.
Provides <10ms cache hit latency for frequently accessed resources.
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
    Redis-based caching service for MCP resources.

    Implements cache-aside pattern with TTL-based expiration.
    Provides distributed caching for horizontal scalability.

    Attributes:
        redis: Async Redis client
        ttl_seconds: Time-to-live for cache entries (default: 300s)
    """

    def __init__(self, redis_url: str | None = None, ttl_seconds: int | None = None):
        """
        Initialize cache service with Redis connection.

        Args:
            redis_url: Redis connection URL (defaults to settings.redis_url)
            ttl_seconds: Cache TTL in seconds (defaults to settings.cache_ttl)
        """
        self.redis_url = redis_url or settings.redis_url
        self.ttl_seconds = ttl_seconds or settings.cache_ttl

        # Redis client initialized lazily in async context
        self._redis: redis.Redis | None = None  # type: ignore[type-arg]

    async def connect(self) -> None:
        """
        Establish Redis connection.

        Should be called on application startup.
        """
        if self._redis is None:
            self._redis = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            logger.info(
                "cache_connected",
                redis_url=self.redis_url,
                ttl_seconds=self.ttl_seconds,
            )

    async def disconnect(self) -> None:
        """
        Close Redis connection.

        Should be called on application shutdown.
        """
        if self._redis is not None:
            await self._redis.aclose()
            self._redis = None
            logger.info("cache_disconnected")

    @property
    def redis(self) -> redis.Redis:  # type: ignore[type-arg]
        """
        Get Redis client instance.

        Raises:
            RuntimeError: If Redis connection not established
        """
        if self._redis is None:
            raise RuntimeError("Redis connection not established. Call connect() first.")
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

        # Try cache first
        try:
            cached = await self.redis.get(cache_key)
            if cached:
                # Cache hit - return immediately
                latency = time.time() - start_time
                cache_hits_total.labels(resource_type=resource_type).inc()
                cache_latency_seconds.labels(cache_result="hit").observe(latency)

                cache_data = json.loads(cached)
                logger.debug(
                    "cache_hit",
                    cache_key=cache_key,
                    resource_type=resource_type,
                    latency_ms=latency * 1000,
                    cached_at=cache_data.get("cached_at"),
                )

                return cache_data["content"]
        except Exception as e:
            # Log cache read error but don't fail - fall through to fetch
            logger.warning(
                "cache_read_error",
                cache_key=cache_key,
                error=str(e),
            )

        # Cache miss - fetch from source
        cache_misses_total.labels(resource_type=resource_type).inc()
        logger.debug(
            "cache_miss",
            cache_key=cache_key,
            resource_type=resource_type,
        )

        # Fetch content from source (disk I/O)
        content = await fetch_func(file_path)

        # Store in cache with TTL
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
                ttl_seconds=self.ttl_seconds,
            )
        except Exception as e:
            # Log cache write error but don't fail - content already fetched
            logger.warning(
                "cache_write_error",
                cache_key=cache_key,
                error=str(e),
            )

        # Update metrics
        latency = time.time() - start_time
        cache_latency_seconds.labels(cache_result="miss").observe(latency)

        logger.debug(
            "cache_miss_fetched",
            cache_key=cache_key,
            resource_type=resource_type,
            latency_ms=latency * 1000,
        )

        return content

    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all cache keys matching pattern.

        Args:
            pattern: Redis key pattern (e.g., "resource:patterns:*")

        Returns:
            int: Number of keys invalidated
        """
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                deleted_count = await self.redis.delete(*keys)
                logger.info(
                    "cache_invalidated",
                    pattern=pattern,
                    deleted_count=deleted_count,
                )
                return deleted_count
            return 0
        except Exception as e:
            logger.error(
                "cache_invalidation_error",
                pattern=pattern,
                error=str(e),
            )
            raise

    async def get_cache_size(self) -> int:
        """
        Get number of cached resources.

        Returns:
            int: Current cache size (number of keys in Redis DB)
        """
        try:
            size = await self.redis.dbsize()
            cache_size.set(size)
            return size
        except Exception as e:
            logger.error(
                "cache_size_error",
                error=str(e),
            )
            raise


# Global cache service instance
# Initialized on application startup via lifespan context manager
cache_service = ResourceCacheService()
