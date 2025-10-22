"""
Prompt registry for MCP Server.

Registers generator prompts with FastMCP using async file loading and caching.
Implements TASK-008 and TASK-009: Prompt registration with security validation.
Uses unified caching service (Redis with in-memory fallback).
"""

from pathlib import Path

import structlog

from mcp_server.prompts.scanner import GeneratorScanner
from mcp_server.services.cache import ResourceCacheService
from mcp_server.utils import FileLoader

logger = structlog.get_logger(__name__)


class PromptRegistry:
    """
    Registry for MCP generator prompts.

    Combines generator scanning, async file loading, and unified caching to provide
    efficient prompt content retrieval for MCP clients.

    Features:
    - Async file I/O with aiofiles (non-blocking)
    - Unified caching (Redis with in-memory fallback)
    - Security validation (path traversal prevention)
    - Structured logging for observability
    """

    def __init__(self, prompts_dir: Path, cache: ResourceCacheService | None = None) -> None:
        """
        Initialize prompt registry.

        Args:
            prompts_dir: Path to prompts directory containing generator XML files
            cache: Optional ResourceCacheService instance (uses global instance if not provided)
        """
        from mcp_server.services import cache_service

        self.scanner = GeneratorScanner(prompts_dir)
        self.cache = cache or cache_service
        self.prompts_dir = prompts_dir
        logger.info(
            "prompt_registry_initialized",
            prompts_dir=str(prompts_dir),
            cache_ttl=self.cache.ttl_seconds,
        )

    async def load_prompt(self, artifact_name: str) -> str:
        """
        Load generator prompt content by artifact name.

        Uses unified caching service (Redis with in-memory fallback).
        Implements cache-aside pattern via ResourceCacheService.

        Args:
            artifact_name: Artifact name (e.g., "epic", "backlog-story")

        Returns:
            Generator XML content as string

        Raises:
            ValueError: If artifact_name fails security validation
            FileNotFoundError: If generator file doesn't exist
            OSError: If file read fails

        Performance:
            - Cache hit: <10ms (Redis or in-memory)
            - Cache miss: <100ms (disk I/O + cache update)
        """
        # Security validation
        if not self.scanner.validate_artifact_name(artifact_name):
            msg = f"Invalid artifact name format: {artifact_name}"
            logger.warning(
                "invalid_artifact_name_rejected",
                artifact_name=artifact_name,
                reason="failed_security_validation",
            )
            raise ValueError(msg)

        # Get file path for artifact
        file_path = self.scanner.get_generator_path(artifact_name)

        if not file_path.exists():
            msg = f"Generator file not found: {file_path}"
            logger.error(
                "generator_file_not_found",
                artifact_name=artifact_name,
                file_path=str(file_path),
            )
            raise FileNotFoundError(msg)

        # Use cache-aside pattern via ResourceCacheService
        cache_key = f"prompt:{artifact_name}"
        content = await self.cache.get_or_fetch(
            cache_key=cache_key,
            fetch_func=self._load_file_from_disk,
            file_path=str(file_path),
            resource_type="prompt",
        )

        return content

    async def _load_file_from_disk(self, file_path: str) -> str:
        """
        Load file content from disk (used by cache on miss).

        Args:
            file_path: Absolute path to file

        Returns:
            str: File content

        Raises:
            FileNotFoundError: If file does not exist
            PermissionError: If file cannot be read due to permissions
            OSError: If file read fails
        """
        try:
            return await FileLoader.load_file(
                file_path=file_path,
                validate_base_dir=False,  # Path already validated by scanner
            )
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error(
                "generator_file_read_error",
                file_path=file_path,
                error=str(e),
            )
            raise

    def list_available_prompts(self) -> list[str]:
        """
        List all available generator prompts.

        Scans prompts directory and returns artifact names for prompt discovery.

        Returns:
            List of artifact names (e.g., ["epic", "prd", "backlog-story"])

        Raises:
            FileNotFoundError: If prompts directory doesn't exist
        """
        generators = self.scanner.scan_generators()
        artifact_names = sorted(generators.keys())

        logger.info(
            "prompts_listed",
            total_prompts=len(artifact_names),
            artifact_names=artifact_names,
        )

        return artifact_names

    async def get_cache_stats(self) -> dict[str, int | float]:
        """
        Get cache statistics for observability.

        Returns:
            Dictionary with cache metrics (size, ttl_seconds)
        """
        size = await self.cache.get_cache_size()
        return {
            "size": size,
            "ttl_seconds": self.cache.ttl_seconds,
        }
