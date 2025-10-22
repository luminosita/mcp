"""
MCP Resource API routes.

Implements resource endpoints for serving implementation pattern files and SDLC
framework content via MCP protocol. Supports language-specific subdirectories
(Python, Go) for multi-language projects.

Resource URIs:
- mcp://resources/patterns/{name} - Pattern files (patterns-*.md or CLAUDE-*.md)
- mcp://resources/patterns/{language}/{name} - Language-specific patterns
- mcp://resources/sdlc/core - SDLC framework core content

Security:
- Path traversal protection via input validation
- Restricted to configured base directory
- No directory listing or traversal allowed
"""

import time
from pathlib import Path

import aiofiles
import structlog
from fastapi import APIRouter, Query
from prometheus_client import Histogram

from mcp_server.api.schemas.resources import (
    TEMPLATE_FILE_MAP,
    ResourceNameValidator,
    ResourceResponse,
)
from mcp_server.config import settings
from mcp_server.core.exceptions import (
    ForbiddenError,
    ResourceNotFoundError,
    ValidationError,
)
from mcp_server.services import cache_service

router = APIRouter(prefix="/mcp/resources", tags=["MCP Resources"])
logger = structlog.get_logger(__name__)

# Prometheus metrics for end-to-end resource loading performance (US-033)
resource_loading_latency_seconds = Histogram(
    "mcp_resource_loading_latency_seconds",
    "End-to-end resource loading latency distribution (request → response)",
    ["resource_type", "cache_result"],
    buckets=[0.010, 0.050, 0.100, 0.200, 0.500, 1.000],  # 10ms to 1s
)


async def _load_file_from_disk(file_path: str) -> str:
    """
    Load file content from disk (used by cache on miss).

    Args:
        file_path: Absolute path to file

    Returns:
        str: File content

    Raises:
        FileNotFoundError: If file does not exist
        PermissionError: If file cannot be read
        IOError: If file read fails
    """
    try:
        async with aiofiles.open(file_path, encoding="utf-8") as f:
            return await f.read()
    except FileNotFoundError:
        raise
    except PermissionError:
        raise
    except Exception as e:
        raise OSError(f"Failed to read file: {file_path}") from e


async def load_resource_file(
    file_path: Path, resource_uri: str, base_dir: str | None = None
) -> ResourceResponse:
    """
    Load resource file from disk asynchronously.

    Args:
        file_path: Path to resource file
        resource_uri: MCP resource URI for response
        base_dir: Base directory for path traversal check (defaults to patterns_base_dir)

    Returns:
        ResourceResponse: Resource content and metadata

    Raises:
        ResourceNotFoundError: If resource file does not exist
        ForbiddenError: If file cannot be read due to permissions
        IOError: If file read fails
    """
    start_time = time.time()

    # Check file exists
    if not file_path.exists():
        logger.warning(
            "resource_not_found",
            resource_uri=resource_uri,
            file_path=str(file_path),
        )
        raise ResourceNotFoundError(f"Resource not found: {resource_uri}")

    # Check file is within allowed base directory (defense in depth)
    if base_dir is None:
        base_dir = settings.patterns_base_dir
    allowed_base = Path(base_dir).resolve()
    try:
        file_path_resolved = file_path.resolve()
        file_path_resolved.relative_to(allowed_base)
    except ValueError as err:
        logger.error(
            "path_traversal_detected",
            resource_uri=resource_uri,
            file_path=str(file_path),
            base_dir=str(allowed_base),
        )
        raise ForbiddenError(f"Access denied: {resource_uri}") from err

    # Read file asynchronously
    try:
        async with aiofiles.open(file_path, encoding="utf-8") as f:
            content = await f.read()
    except PermissionError as e:
        logger.error(
            "file_permission_error",
            resource_uri=resource_uri,
            file_path=str(file_path),
        )
        raise ForbiddenError(f"Access denied: {resource_uri}") from e
    except Exception as e:
        logger.error(
            "file_read_error",
            resource_uri=resource_uri,
            file_path=str(file_path),
            error=str(e),
        )
        raise OSError(f"Failed to read resource: {resource_uri}") from e

    latency_ms = (time.time() - start_time) * 1000
    size_bytes = len(content.encode("utf-8"))

    logger.info(
        "resource_loaded",
        resource_uri=resource_uri,
        file_path=str(file_path),
        size_bytes=size_bytes,
        latency_ms=latency_ms,
    )

    return ResourceResponse(
        uri=resource_uri,
        content=content,
        size_bytes=size_bytes,
    )


async def load_resource_file_cached(
    file_path: Path,
    resource_uri: str,
    resource_type: str,
    cache_key: str,
    base_dir: str | None = None,
) -> ResourceResponse:
    """
    Load resource file with caching (cache-aside pattern).

    Provides <10ms latency on cache hit, ~50ms on cache miss.

    Args:
        file_path: Path to resource file
        resource_uri: MCP resource URI for response
        resource_type: Resource type for metrics (patterns, templates, sdlc)
        cache_key: Unique cache key (format: resource:{type}:{name})
        base_dir: Base directory for path traversal check (defaults to patterns_base_dir)

    Returns:
        ResourceResponse: Resource content and metadata

    Raises:
        ResourceNotFoundError: If resource file does not exist
        ForbiddenError: If file cannot be read due to permissions
        IOError: If file read fails
    """
    start_time = time.time()

    # Check file exists
    if not file_path.exists():
        logger.warning(
            "resource_not_found",
            resource_uri=resource_uri,
            file_path=str(file_path),
        )
        raise ResourceNotFoundError(f"Resource not found: {resource_uri}")

    # Check file is within allowed base directory (defense in depth)
    if base_dir is None:
        base_dir = settings.patterns_base_dir
    allowed_base = Path(base_dir).resolve()
    try:
        file_path_resolved = file_path.resolve()
        file_path_resolved.relative_to(allowed_base)
    except ValueError as err:
        logger.error(
            "path_traversal_detected",
            resource_uri=resource_uri,
            file_path=str(file_path),
            base_dir=str(allowed_base),
        )
        raise ForbiddenError(f"Access denied: {resource_uri}") from err

    # Get content from cache or fetch from disk
    try:
        content = await cache_service.get_or_fetch(
            cache_key=cache_key,
            fetch_func=_load_file_from_disk,
            file_path=str(file_path),
            resource_type=resource_type,
        )
    except Exception as e:
        logger.error(
            "resource_load_error",
            resource_uri=resource_uri,
            file_path=str(file_path),
            error=str(e),
        )
        raise

    latency_ms = (time.time() - start_time) * 1000
    size_bytes = len(content.encode("utf-8"))

    logger.info(
        "resource_loaded_cached",
        resource_uri=resource_uri,
        file_path=str(file_path),
        size_bytes=size_bytes,
        latency_ms=latency_ms,
        cache_key=cache_key,
    )

    return ResourceResponse(
        uri=resource_uri,
        content=content,
        size_bytes=size_bytes,
    )


@router.get("/patterns/{name:path}", response_model=ResourceResponse)
async def get_pattern_resource(
    name: str,
    language: str = Query(default="python", pattern=r"^[a-z]+$"),
) -> ResourceResponse:
    """
    Get implementation pattern file content.

    Serves pattern files from prompts/CLAUDE/{language}/ directory.
    Supports both patterns-*.md (new format) and CLAUDE-*.md (legacy format).

    Args:
        name: Pattern resource name (e.g., 'core', 'tooling', 'testing')
        language: Programming language subdirectory (default: python)

    Returns:
        ResourceResponse: Pattern file content with metadata

    Raises:
        ValidationError: Invalid resource name (path traversal attempt)
        ResourceNotFoundError: Resource file not found
        ForbiddenError: File permission error
        IOError: File read error

    Examples:
        GET /mcp/resources/patterns/core?language=python
        -> Returns prompts/CLAUDE/python/patterns-core.md (or CLAUDE-core.md)

        GET /mcp/resources/patterns/tooling?language=go
        -> Returns prompts/CLAUDE/go/patterns-tooling.md (or CLAUDE-tooling.md)
    """
    # Start end-to-end latency measurement (US-033)
    start_time = time.time()
    cache_result = "miss"  # Will be updated based on actual cache hit/miss

    # Validate input to prevent path traversal
    try:
        validated_name = ResourceNameValidator.validate_resource_name(name)
        validated_language = language.lower()
        if not validated_language.isalpha():
            raise ValueError("Language must contain only letters")
    except ValueError as e:
        logger.warning(
            "invalid_resource_name",
            name=name,
            language=language,
            error=str(e),
        )
        raise ValidationError(str(e)) from e

    # Construct file path using configuration
    patterns_dir = Path(settings.patterns_base_dir) / validated_language
    resource_uri = f"mcp://resources/patterns/{validated_language}/{validated_name}"

    # Try patterns-*.md format first (new format per US-029)
    file_path = patterns_dir / f"patterns-{validated_name}.md"

    # Fallback to CLAUDE-*.md format if patterns-*.md doesn't exist
    # This maintains compatibility until US-029 completes file renaming
    if not file_path.exists():
        file_path = patterns_dir / f"CLAUDE-{validated_name}.md"
        logger.debug(
            "fallback_to_legacy_format",
            resource_uri=resource_uri,
            legacy_file=str(file_path),
        )

    # Load resource file with caching (US-032)
    # Cache key format: resource:patterns:{language}:{name}
    cache_key = f"resource:patterns:{validated_language}:{validated_name}"

    # Check if cached to determine cache result for metrics
    try:
        cached_exists = await cache_service.redis.exists(cache_key)
        cache_result = "hit" if cached_exists else "miss"
    except Exception:
        # If cache check fails, assume miss
        cache_result = "miss"

    # Load resource (exceptions handled by centralized exception handlers)
    response = await load_resource_file_cached(
        file_path=file_path,
        resource_uri=resource_uri,
        resource_type="patterns",
        cache_key=cache_key,
    )

    # Record end-to-end latency (US-033)
    latency = time.time() - start_time
    resource_loading_latency_seconds.labels(
        resource_type="patterns",
        cache_result=cache_result,
    ).observe(latency)

    return response


@router.get("/sdlc/core", response_model=ResourceResponse)
async def get_sdlc_core_resource() -> ResourceResponse:
    """
    Get SDLC framework core content.

    Serves SDLC framework orchestration file from configured path.

    Returns:
        ResourceResponse: SDLC core content with metadata

    Raises:
        ResourceNotFoundError: SDLC core file not found
        ForbiddenError: File permission error
        IOError: File read error

    Examples:
        GET /mcp/resources/sdlc/core
        -> Returns prompts/CLAUDE/sdlc-core.md
    """
    # Start end-to-end latency measurement (US-033)
    start_time = time.time()
    cache_result = "miss"

    # Use configuration for SDLC core file path
    file_path = Path(settings.sdlc_core_file_path)
    resource_uri = "mcp://resources/sdlc/core"

    # Load resource file with caching (US-032)
    # Cache key format: resource:sdlc:core
    cache_key = "resource:sdlc:core"

    # Check if cached to determine cache result for metrics
    try:
        cached_exists = await cache_service.redis.exists(cache_key)
        cache_result = "hit" if cached_exists else "miss"
    except Exception:
        cache_result = "miss"

    # Load resource (exceptions handled by centralized exception handlers)
    response = await load_resource_file_cached(
        file_path=file_path,
        resource_uri=resource_uri,
        resource_type="sdlc",
        cache_key=cache_key,
    )

    # Record end-to-end latency (US-033)
    latency = time.time() - start_time
    resource_loading_latency_seconds.labels(
        resource_type="sdlc",
        cache_result=cache_result,
    ).observe(latency)

    return response


@router.get("/templates")
async def list_template_resources() -> dict[str, list[dict[str, str]]]:
    """
    List all available template resources.

    Returns list of all artifact templates with their URIs and filenames.
    Useful for Claude Code to discover available template resources.

    Returns:
        dict: Dictionary with 'templates' key containing list of template metadata

    Examples:
        GET /mcp/resources/templates
        -> Returns list of all 10 templates with URIs and filenames
    """
    logger.info(
        "listing_templates",
        template_count=len(TEMPLATE_FILE_MAP),
    )

    templates = [
        {
            "name": name,
            "uri": f"mcp://resources/templates/{name}",
            "filename": filename,
        }
        for name, filename in TEMPLATE_FILE_MAP.items()
    ]

    return {"templates": templates}


@router.get("/templates/{artifact_type}", response_model=ResourceResponse)
async def get_template_resource(artifact_type: str) -> ResourceResponse:
    """
    Get artifact template XML content.

    Serves template files from prompts/templates/ directory.
    Uses simplified URI naming: 'prd', 'epic', 'story', etc.

    Args:
        artifact_type: Template type name (e.g., 'prd', 'epic', 'story')

    Returns:
        ResourceResponse: Template XML content with metadata

    Raises:
        ValidationError: Invalid template name (path traversal attempt)
        ResourceNotFoundError: Template file not found
        ForbiddenError: File permission error
        IOError: File read error

    Examples:
        GET /mcp/resources/templates/prd
        -> Returns prompts/templates/prd-template.xml

        GET /mcp/resources/templates/story
        -> Returns prompts/templates/backlog-story-template.xml
    """
    # Start end-to-end latency measurement (US-033)
    start_time = time.time()
    cache_result = "miss"

    # Validate input to prevent path traversal
    if ".." in artifact_type or artifact_type.startswith("/"):
        logger.warning(
            "invalid_template_name",
            artifact_type=artifact_type,
            error="Path traversal attempt detected",
        )
        raise ValidationError("Invalid template name")

    # Validate artifact_type against allowed template names
    if artifact_type not in TEMPLATE_FILE_MAP:
        logger.warning(
            "template_not_found",
            artifact_type=artifact_type,
            available_templates=list(TEMPLATE_FILE_MAP.keys()),
        )
        raise ResourceNotFoundError(
            f"Resource not found: mcp://resources/templates/{artifact_type}"
        )

    # Construct file path using configuration
    template_filename = TEMPLATE_FILE_MAP[artifact_type]
    file_path = Path(settings.templates_dir) / template_filename
    resource_uri = f"mcp://resources/templates/{artifact_type}"

    # Load resource file with caching (US-032)
    # Cache key format: resource:templates:{artifact_type}
    cache_key = f"resource:templates:{artifact_type}"

    # Check if cached to determine cache result for metrics
    try:
        cached_exists = await cache_service.redis.exists(cache_key)
        cache_result = "hit" if cached_exists else "miss"
    except Exception:
        cache_result = "miss"

    # Load resource file with templates_dir as base directory
    # Exceptions handled by centralized exception handlers
    response = await load_resource_file_cached(
        file_path=file_path,
        resource_uri=resource_uri,
        resource_type="templates",
        cache_key=cache_key,
        base_dir=settings.templates_dir,
    )

    # Record end-to-end latency (US-033)
    latency = time.time() - start_time
    resource_loading_latency_seconds.labels(
        resource_type="templates",
        cache_result=cache_result,
    ).observe(latency)

    return response
