"""
Unit tests for ResourceCacheService.

Tests cache operations, TTL expiration, invalidation, and error handling
without requiring a real Redis instance.
"""

import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from redis.exceptions import ConnectionError as RedisConnectionError

from mcp_server.services.cache import ResourceCacheService


class TestCacheServiceInitialization:
    """Test cache service initialization and connection lifecycle."""

    def test_init_with_defaults(self):
        """Test cache service initializes with default settings."""
        cache = ResourceCacheService()

        assert cache.redis_url is not None
        assert cache.ttl_seconds > 0
        assert cache._redis is None

    def test_init_with_custom_params(self):
        """Test cache service initializes with custom parameters."""
        custom_url = "redis://custom:6379"
        custom_ttl = 600

        cache = ResourceCacheService(redis_url=custom_url, ttl_seconds=custom_ttl)

        assert cache.redis_url == custom_url
        assert cache.ttl_seconds == custom_ttl

    @pytest.mark.asyncio
    async def test_connect_initializes_redis_client(self):
        """Test connect() establishes Redis connection."""
        cache = ResourceCacheService()

        with patch("mcp_server.services.cache.redis.from_url") as mock_from_url:
            mock_redis = AsyncMock()

            # from_url is an async function, so we need to make it awaitable
            async def async_from_url(*args, **kwargs):
                return mock_redis

            mock_from_url.side_effect = async_from_url

            await cache.connect()

            assert cache._redis is not None
            mock_from_url.assert_called_once_with(
                cache.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )

    @pytest.mark.asyncio
    async def test_disconnect_closes_redis_client(self):
        """Test disconnect() closes Redis connection."""
        cache = ResourceCacheService()
        mock_redis = AsyncMock()
        cache._redis = mock_redis

        await cache.disconnect()

        mock_redis.aclose.assert_called_once()
        assert cache._redis is None

    def test_redis_property_raises_if_not_connected(self):
        """Test accessing redis property before connect() raises RuntimeError."""
        cache = ResourceCacheService()

        with pytest.raises(RuntimeError, match="Redis connection not established"):
            _ = cache.redis


class TestGetOrFetch:
    """Test get_or_fetch() cache-aside pattern."""

    @pytest.mark.asyncio
    async def test_cache_hit_returns_cached_content(self):
        """Test cache hit returns cached content immediately without fetching."""
        cache = ResourceCacheService()
        mock_redis = AsyncMock()
        cache._redis = mock_redis

        # Mock cache hit - return cached data
        cached_data = {
            "content": "cached content from Redis",
            "cached_at": datetime.now(UTC).isoformat(),
            "file_path": "/path/to/file.md",
            "resource_type": "patterns",
        }
        mock_redis.get.return_value = json.dumps(cached_data)

        # Mock fetch function - should NOT be called on cache hit
        fetch_func = AsyncMock()

        result = await cache.get_or_fetch(
            cache_key="resource:patterns:core",
            fetch_func=fetch_func,
            file_path="/path/to/file.md",
            resource_type="patterns",
        )

        assert result == "cached content from Redis"
        mock_redis.get.assert_called_once_with("resource:patterns:core")
        fetch_func.assert_not_called()  # Should NOT fetch on cache hit

    @pytest.mark.asyncio
    async def test_cache_miss_fetches_and_caches(self):
        """Test cache miss fetches from source and stores in cache."""
        cache = ResourceCacheService(ttl_seconds=300)
        mock_redis = AsyncMock()
        cache._redis = mock_redis

        # Mock cache miss - return None
        mock_redis.get.return_value = None

        # Mock fetch function - return fresh content
        fetch_func = AsyncMock(return_value="fresh content from disk")

        result = await cache.get_or_fetch(
            cache_key="resource:patterns:core",
            fetch_func=fetch_func,
            file_path="/path/to/file.md",
            resource_type="patterns",
        )

        assert result == "fresh content from disk"
        mock_redis.get.assert_called_once_with("resource:patterns:core")
        fetch_func.assert_called_once_with("/path/to/file.md")

        # Verify content was cached with TTL
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == "resource:patterns:core"  # cache key
        assert call_args[0][1] == 300  # TTL

        # Verify cached data structure
        cached_json = call_args[0][2]
        cached_data = json.loads(cached_json)
        assert cached_data["content"] == "fresh content from disk"
        assert cached_data["file_path"] == "/path/to/file.md"
        assert cached_data["resource_type"] == "patterns"

    @pytest.mark.asyncio
    async def test_cache_read_error_falls_through_to_fetch(self):
        """Test cache read error doesn't fail - falls through to fetch."""
        cache = ResourceCacheService()
        mock_redis = AsyncMock()
        cache._redis = mock_redis

        # Mock cache read error
        mock_redis.get.side_effect = RedisConnectionError("Redis unavailable")

        # Mock fetch function
        fetch_func = AsyncMock(return_value="fresh content")

        result = await cache.get_or_fetch(
            cache_key="resource:patterns:core",
            fetch_func=fetch_func,
            file_path="/path/to/file.md",
            resource_type="patterns",
        )

        # Should still return content (graceful degradation)
        assert result == "fresh content"
        fetch_func.assert_called_once_with("/path/to/file.md")

    @pytest.mark.asyncio
    async def test_cache_write_error_doesnt_fail_request(self):
        """Test cache write error doesn't fail request - content already fetched."""
        cache = ResourceCacheService()
        mock_redis = AsyncMock()
        cache._redis = mock_redis

        # Mock cache miss
        mock_redis.get.return_value = None

        # Mock cache write error
        mock_redis.setex.side_effect = RedisConnectionError("Redis unavailable")

        # Mock fetch function
        fetch_func = AsyncMock(return_value="fresh content")

        result = await cache.get_or_fetch(
            cache_key="resource:patterns:core",
            fetch_func=fetch_func,
            file_path="/path/to/file.md",
            resource_type="patterns",
        )

        # Should still return content (graceful degradation)
        assert result == "fresh content"
        fetch_func.assert_called_once()


class TestCacheInvalidation:
    """Test cache invalidation functionality."""

    @pytest.mark.asyncio
    async def test_invalidate_pattern_deletes_matching_keys(self):
        """Test invalidate_pattern() deletes all matching keys."""
        cache = ResourceCacheService()
        mock_redis = AsyncMock()
        cache._redis = mock_redis

        # Mock keys() to return matching cache keys
        mock_redis.keys.return_value = [
            "resource:patterns:core",
            "resource:patterns:tooling",
            "resource:patterns:testing",
        ]

        # Mock delete() to return count of deleted keys
        mock_redis.delete.return_value = 3

        deleted_count = await cache.invalidate_pattern("resource:patterns:*")

        assert deleted_count == 3
        mock_redis.keys.assert_called_once_with("resource:patterns:*")
        mock_redis.delete.assert_called_once_with(
            "resource:patterns:core",
            "resource:patterns:tooling",
            "resource:patterns:testing",
        )

    @pytest.mark.asyncio
    async def test_invalidate_pattern_no_matching_keys(self):
        """Test invalidate_pattern() returns 0 if no matching keys."""
        cache = ResourceCacheService()
        mock_redis = AsyncMock()
        cache._redis = mock_redis

        # Mock keys() to return empty list
        mock_redis.keys.return_value = []

        deleted_count = await cache.invalidate_pattern("resource:patterns:*")

        assert deleted_count == 0
        mock_redis.keys.assert_called_once()
        mock_redis.delete.assert_not_called()  # Should not call delete if no keys

    @pytest.mark.asyncio
    async def test_invalidate_pattern_redis_error_raises(self):
        """Test invalidate_pattern() raises on Redis error."""
        cache = ResourceCacheService()
        mock_redis = AsyncMock()
        cache._redis = mock_redis

        # Mock Redis error
        mock_redis.keys.side_effect = RedisConnectionError("Redis unavailable")

        with pytest.raises(RedisConnectionError):
            await cache.invalidate_pattern("resource:patterns:*")


class TestCacheSize:
    """Test get_cache_size() functionality."""

    @pytest.mark.asyncio
    async def test_get_cache_size_returns_dbsize(self):
        """Test get_cache_size() returns Redis dbsize."""
        cache = ResourceCacheService()
        mock_redis = AsyncMock()
        cache._redis = mock_redis

        # Mock dbsize() to return cache size
        mock_redis.dbsize.return_value = 42

        size = await cache.get_cache_size()

        assert size == 42
        mock_redis.dbsize.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_cache_size_redis_error_raises(self):
        """Test get_cache_size() raises on Redis error."""
        cache = ResourceCacheService()
        mock_redis = AsyncMock()
        cache._redis = mock_redis

        # Mock Redis error
        mock_redis.dbsize.side_effect = RedisConnectionError("Redis unavailable")

        with pytest.raises(RedisConnectionError):
            await cache.get_cache_size()
