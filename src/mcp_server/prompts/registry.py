"""
Prompt registry for MCP Server.

Registers generator prompts with FastMCP using async file loading and caching.
Implements TASK-008 and TASK-009: Prompt registration with security validation.
"""

from pathlib import Path

import aiofiles  # type: ignore[import-untyped]
import structlog

from mcp_server.prompts.cache import PromptCache
from mcp_server.prompts.scanner import GeneratorScanner

logger = structlog.get_logger(__name__)


class PromptRegistry:
    """
    Registry for MCP generator prompts.

    Combines generator scanning, async file loading, and caching to provide
    efficient prompt content retrieval for MCP clients.

    Features:
    - Async file I/O with aiofiles (non-blocking)
    - In-memory caching with 5-minute TTL
    - Security validation (path traversal prevention)
    - Structured logging for observability
    """

    def __init__(self, prompts_dir: Path, cache: PromptCache | None = None) -> None:
        """
        Initialize prompt registry.

        Args:
            prompts_dir: Path to prompts directory containing generator XML files
            cache: Optional PromptCache instance (creates default if not provided)
        """
        self.scanner = GeneratorScanner(prompts_dir)
        self.cache = cache or PromptCache(ttl_seconds=300)
        self.prompts_dir = prompts_dir
        logger.info(
            "prompt_registry_initialized",
            prompts_dir=str(prompts_dir),
            cache_ttl=self.cache.ttl_seconds,
        )

    async def load_prompt(self, artifact_name: str) -> str:
        """
        Load generator prompt content by artifact name.

        Implements cache-aside pattern:
        1. Check cache for existing entry
        2. If cache miss, load from disk asynchronously
        3. Store in cache for future requests
        4. Return content

        Args:
            artifact_name: Artifact name (e.g., "epic", "backlog-story")

        Returns:
            Generator XML content as string

        Raises:
            ValueError: If artifact_name fails security validation
            FileNotFoundError: If generator file doesn't exist
            OSError: If file read fails

        Performance:
            - Cache hit: <10ms (in-memory read)
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

        # Check cache first (cache-aside pattern)
        cached_content = self.cache.get(artifact_name)
        if cached_content is not None:
            logger.debug(
                "prompt_loaded_from_cache",
                artifact_name=artifact_name,
                content_length=len(cached_content),
            )
            return cached_content

        # Cache miss - load from disk
        file_path = self.scanner.get_generator_path(artifact_name)

        if not file_path.exists():
            msg = f"Generator file not found: {file_path}"
            logger.error(
                "generator_file_not_found",
                artifact_name=artifact_name,
                file_path=str(file_path),
            )
            raise FileNotFoundError(msg)

        # Async file I/O (non-blocking)
        try:
            async with aiofiles.open(file_path, encoding="utf-8") as f:
                content: str = await f.read()
        except OSError as e:
            logger.error(
                "generator_file_read_error",
                artifact_name=artifact_name,
                file_path=str(file_path),
                error=str(e),
            )
            raise

        # Store in cache
        self.cache.set(artifact_name, content)

        logger.info(
            "prompt_loaded_from_disk",
            artifact_name=artifact_name,
            file_path=str(file_path),
            content_length=len(content),
        )

        return content

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

    def get_cache_stats(self) -> dict[str, int | float]:
        """
        Get cache statistics for observability.

        Returns:
            Dictionary with cache metrics (size, hits, misses, hit_rate)
        """
        return self.cache.get_stats()
