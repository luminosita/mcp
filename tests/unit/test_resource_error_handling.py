"""
Unit tests for resource loading error handling.

Tests error scenarios: file not found, permission errors, I/O errors,
cache failures. Focuses on error handling paths not covered by integration tests.
"""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_server.api.routes.resources import (
    _load_file_from_disk,
    load_resource_file,
    load_resource_file_cached,
)
from mcp_server.api.schemas.resources import ResourceResponse


class TestLoadFileFromDisk:
    """Test _load_file_from_disk() error handling."""

    @pytest.mark.asyncio
    async def test_file_not_found_raises(self, tmp_path):
        """Test FileNotFoundError raised for missing file."""
        nonexistent_file = str(tmp_path / "nonexistent.md")

        with pytest.raises(FileNotFoundError):
            await _load_file_from_disk(nonexistent_file)

    @pytest.mark.asyncio
    async def test_permission_error_raises(self, tmp_path):
        """Test PermissionError raised for unreadable file."""
        test_file = tmp_path / "protected.md"
        test_file.write_text("protected content")
        test_file.chmod(0o000)  # Remove all permissions

        try:
            with pytest.raises(PermissionError):
                await _load_file_from_disk(str(test_file))
        finally:
            # Restore permissions for cleanup
            test_file.chmod(0o644)

    @pytest.mark.asyncio
    async def test_io_error_on_read_failure(self, tmp_path):
        """Test IOError raised on file read failure."""
        test_file = tmp_path / "test.md"
        test_file.write_text("content")

        # Mock aiofiles.open to raise IOError
        with patch("mcp_server.api.routes.resources.aiofiles.open") as mock_open:
            mock_open.side_effect = OSError("Disk I/O error")

            with pytest.raises(IOError, match="Failed to read file"):
                await _load_file_from_disk(str(test_file))


class TestLoadResourceFile:
    """Test load_resource_file() error handling (non-cached)."""

    @pytest.mark.asyncio
    async def test_file_not_found_raises(self, tmp_path):
        """Test FileNotFoundError raised for missing resource."""
        nonexistent_file = tmp_path / "nonexistent.md"

        with pytest.raises(FileNotFoundError, match="Resource not found"):
            await load_resource_file(
                file_path=nonexistent_file,
                resource_uri="mcp://resources/test",
                base_dir=str(tmp_path),
            )

    @pytest.mark.asyncio
    async def test_path_traversal_raises_permission_error(self, tmp_path):
        """Test path traversal attempt raises PermissionError."""
        # Create base directory and file outside base
        base_dir = tmp_path / "base"
        base_dir.mkdir()

        outside_dir = tmp_path / "outside"
        outside_dir.mkdir()
        outside_file = outside_dir / "secret.md"
        outside_file.write_text("secret content")

        # Attempt to access file outside base directory
        with pytest.raises(PermissionError, match="Access denied"):
            await load_resource_file(
                file_path=outside_file,
                resource_uri="mcp://resources/secret",
                base_dir=str(base_dir),
            )

    @pytest.mark.asyncio
    async def test_permission_error_on_unreadable_file(self, tmp_path):
        """Test PermissionError raised for file without read permissions."""
        test_file = tmp_path / "protected.md"
        test_file.write_text("protected content")
        test_file.chmod(0o000)

        try:
            with pytest.raises(PermissionError):
                await load_resource_file(
                    file_path=test_file,
                    resource_uri="mcp://resources/protected",
                    base_dir=str(tmp_path),
                )
        finally:
            test_file.chmod(0o644)

    @pytest.mark.asyncio
    async def test_io_error_on_read_failure(self, tmp_path):
        """Test IOError raised on file read failure."""
        test_file = tmp_path / "test.md"
        test_file.write_text("content")

        # Mock aiofiles.open to raise exception during read
        with patch("mcp_server.api.routes.resources.aiofiles.open") as mock_open:
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value.read.side_effect = Exception("Read error")
            mock_open.return_value = mock_context

            with pytest.raises(IOError, match="Failed to read resource"):
                await load_resource_file(
                    file_path=test_file,
                    resource_uri="mcp://resources/test",
                    base_dir=str(tmp_path),
                )


class TestLoadResourceFileCached:
    """Test load_resource_file_cached() error handling."""

    @pytest.mark.asyncio
    async def test_file_not_found_raises(self, tmp_path):
        """Test FileNotFoundError raised for missing resource."""
        nonexistent_file = tmp_path / "nonexistent.md"

        with pytest.raises(FileNotFoundError, match="Resource not found"):
            await load_resource_file_cached(
                file_path=nonexistent_file,
                resource_uri="mcp://resources/test",
                resource_type="patterns",
                cache_key="resource:test",
                base_dir=str(tmp_path),
            )

    @pytest.mark.asyncio
    async def test_path_traversal_raises_permission_error(self, tmp_path):
        """Test path traversal attempt raises PermissionError."""
        base_dir = tmp_path / "base"
        base_dir.mkdir()

        outside_dir = tmp_path / "outside"
        outside_dir.mkdir()
        outside_file = outside_dir / "secret.md"
        outside_file.write_text("secret content")

        with pytest.raises(PermissionError, match="Access denied"):
            await load_resource_file_cached(
                file_path=outside_file,
                resource_uri="mcp://resources/secret",
                resource_type="patterns",
                cache_key="resource:secret",
                base_dir=str(base_dir),
            )

    @pytest.mark.asyncio
    async def test_cache_service_error_propagates(self, tmp_path):
        """Test cache service errors are propagated."""
        test_file = tmp_path / "test.md"
        test_file.write_text("test content")

        # Mock cache service to raise exception
        with patch("mcp_server.api.routes.resources.cache_service") as mock_cache:
            mock_cache.get_or_fetch.side_effect = Exception("Cache service error")

            with pytest.raises(Exception, match="Cache service error"):
                await load_resource_file_cached(
                    file_path=test_file,
                    resource_uri="mcp://resources/test",
                    resource_type="patterns",
                    cache_key="resource:test",
                    base_dir=str(tmp_path),
                )


class TestResourceResponseCreation:
    """Test ResourceResponse model validation and creation."""

    def test_valid_response_creation(self):
        """Test ResourceResponse creates successfully with valid data."""
        response = ResourceResponse(
            uri="mcp://resources/patterns/core",
            content="# Core Patterns\n\nContent here...",
            size_bytes=100,
        )

        assert response.uri == "mcp://resources/patterns/core"
        assert "Core Patterns" in response.content
        assert response.size_bytes == 100

    def test_size_bytes_matches_content_length(self):
        """Test size_bytes should match actual UTF-8 content length."""
        content = "Test content with émojis 🎉"
        size_bytes = len(content.encode("utf-8"))

        response = ResourceResponse(
            uri="mcp://resources/test",
            content=content,
            size_bytes=size_bytes,
        )

        assert response.size_bytes == len(response.content.encode("utf-8"))

    def test_empty_content_allowed(self):
        """Test ResourceResponse allows empty content (valid edge case)."""
        response = ResourceResponse(
            uri="mcp://resources/empty",
            content="",
            size_bytes=0,
        )

        assert response.content == ""
        assert response.size_bytes == 0
