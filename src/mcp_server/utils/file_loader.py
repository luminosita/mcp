"""
Unified file loading utility for MCP Server.

Provides consistent async file loading with security validation across all
components (resources, prompts, templates, patterns, artifacts).

Security Features:
- Path traversal prevention via base directory validation
- File existence validation
- Permission error handling
- Async I/O for non-blocking operations
"""

from pathlib import Path

import aiofiles
import structlog

logger = structlog.get_logger(__name__)


class FileLoader:
    """
    Unified file loader with security validation.

    Provides async file loading with consistent security checks and error
    handling across all MCP Server components.

    Features:
    - Async file I/O with aiofiles (non-blocking)
    - Path traversal prevention (validates files within base directory)
    - Comprehensive error handling (FileNotFoundError, PermissionError, OSError)
    - Structured logging for observability
    """

    @staticmethod
    async def load_file(
        file_path: Path | str,
        base_dir: Path | str | None = None,
        validate_base_dir: bool = True,
    ) -> str:
        """
        Load file content from disk asynchronously with security validation.

        Args:
            file_path: Path to file (absolute or relative)
            base_dir: Base directory for path traversal check (optional)
            validate_base_dir: Whether to validate file is within base_dir

        Returns:
            str: File content

        Raises:
            FileNotFoundError: If file does not exist
            PermissionError: If file cannot be read due to permissions
            ValueError: If path traversal detected (file outside base_dir)
            OSError: If file read fails for other reasons

        Examples:
            # Load with base directory validation
            content = await FileLoader.load_file(
                file_path="/path/to/file.md",
                base_dir="/path/to",
                validate_base_dir=True
            )

            # Load without validation (use with caution)
            content = await FileLoader.load_file(
                file_path="/path/to/file.md",
                validate_base_dir=False
            )
        """
        file_path = Path(file_path)

        # Check file exists
        if not file_path.exists():
            msg = f"File not found: {file_path}"
            logger.warning(
                "file_not_found",
                file_path=str(file_path),
            )
            raise FileNotFoundError(msg)

        # Validate file is within base directory (defense in depth)
        if validate_base_dir and base_dir is not None:
            allowed_base = Path(base_dir).resolve()
            try:
                file_path_resolved = file_path.resolve()
                file_path_resolved.relative_to(allowed_base)
            except ValueError as err:
                msg = f"Path traversal detected: {file_path} is outside {allowed_base}"
                logger.error(
                    "path_traversal_detected",
                    file_path=str(file_path),
                    base_dir=str(allowed_base),
                )
                raise ValueError(msg) from err

        # Read file asynchronously
        try:
            async with aiofiles.open(file_path, encoding="utf-8") as f:
                content = await f.read()
        except PermissionError as e:
            logger.error(
                "file_permission_error",
                file_path=str(file_path),
            )
            raise PermissionError(f"Access denied: {file_path}") from e
        except Exception as e:
            logger.error(
                "file_read_error",
                file_path=str(file_path),
                error=str(e),
            )
            raise OSError(f"Failed to read file: {file_path}") from e

        logger.debug(
            "file_loaded",
            file_path=str(file_path),
            size_bytes=len(content.encode("utf-8")),
        )

        return content

    @staticmethod
    def validate_path(
        file_path: Path | str,
        base_dir: Path | str,
    ) -> Path:
        """
        Validate file path is within base directory (path traversal prevention).

        Args:
            file_path: Path to validate
            base_dir: Base directory

        Returns:
            Path: Resolved file path

        Raises:
            ValueError: If path traversal detected

        Examples:
            # Valid path
            validated = FileLoader.validate_path(
                file_path="/base/dir/file.md",
                base_dir="/base/dir"
            )
            # Returns: Path("/base/dir/file.md")

            # Invalid path (path traversal)
            FileLoader.validate_path(
                file_path="/base/dir/../etc/passwd",
                base_dir="/base/dir"
            )
            # Raises: ValueError
        """
        file_path = Path(file_path)
        allowed_base = Path(base_dir).resolve()

        try:
            file_path_resolved = file_path.resolve()
            file_path_resolved.relative_to(allowed_base)
            return file_path_resolved
        except ValueError as err:
            msg = f"Path traversal detected: {file_path} is outside {allowed_base}"
            logger.error(
                "path_traversal_detected",
                file_path=str(file_path),
                base_dir=str(allowed_base),
            )
            raise ValueError(msg) from err
