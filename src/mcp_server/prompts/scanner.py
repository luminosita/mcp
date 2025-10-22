"""
Generator file scanner for MCP prompts.

Scans prompts/ directory for *-generator.xml files and maps them to artifact names.
Implements TASK-008: Prompt registration and file scanner module.
"""

import re
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)


class GeneratorScanner:
    """
    Scans prompts directory for generator XML files.

    Maps generator filenames to artifact names for MCP prompt registration:
    - epic-generator.xml → artifact name "epic"
    - backlog-story-generator.xml → artifact name "backlog-story"

    Security: Validates filenames to prevent path traversal attacks.
    """

    # Generator filename pattern: {artifact-name}-generator.xml
    GENERATOR_PATTERN = re.compile(r"^([a-z]+(?:-[a-z]+)*)-generator\.xml$")

    def __init__(self, prompts_dir: Path) -> None:
        """
        Initialize generator scanner.

        Args:
            prompts_dir: Path to prompts directory containing generator XML files
        """
        self.prompts_dir = prompts_dir
        logger.info(
            "generator_scanner_initialized",
            prompts_dir=str(prompts_dir),
        )

    def scan_generators(self) -> dict[str, Path]:
        """
        Scan prompts directory for generator XML files.

        Returns:
            Mapping of artifact names to generator file paths
            Example: {"epic": Path("prompts/epic-generator.xml")}

        Raises:
            FileNotFoundError: If prompts directory doesn't exist
        """
        if not self.prompts_dir.exists():
            msg = f"Prompts directory not found: {self.prompts_dir}"
            logger.error("prompts_directory_not_found", prompts_dir=str(self.prompts_dir))
            raise FileNotFoundError(msg)

        generators: dict[str, Path] = {}

        for file_path in self.prompts_dir.glob("*-generator.xml"):
            filename = file_path.name
            match = self.GENERATOR_PATTERN.match(filename)

            if match:
                artifact_name = match.group(1)
                generators[artifact_name] = file_path
                logger.debug(
                    "generator_discovered",
                    artifact_name=artifact_name,
                    file_path=str(file_path),
                )
            else:
                logger.warning(
                    "invalid_generator_filename",
                    filename=filename,
                    expected_pattern="{artifact-name}-generator.xml",
                )

        logger.info(
            "generator_scan_complete",
            total_generators=len(generators),
            artifact_names=sorted(generators.keys()),
        )

        return generators

    @staticmethod
    def validate_artifact_name(artifact_name: str) -> bool:
        """
        Validate artifact name to prevent path traversal attacks.

        Security validation rules:
        - Only lowercase letters and hyphens allowed
        - Must match pattern: [a-z]+(?:-[a-z]+)*
        - Rejects: "../", "./", absolute paths, special characters

        Args:
            artifact_name: Artifact name to validate

        Returns:
            True if valid, False otherwise

        Examples:
            >>> GeneratorScanner.validate_artifact_name("epic")
            True
            >>> GeneratorScanner.validate_artifact_name("backlog-story")
            True
            >>> GeneratorScanner.validate_artifact_name("../etc/passwd")
            False
            >>> GeneratorScanner.validate_artifact_name("EPIC")
            False
        """
        # Pattern allows only lowercase letters and hyphens
        # Prevents path traversal, uppercase, numbers, special chars
        artifact_pattern = re.compile(r"^[a-z]+(?:-[a-z]+)*$")
        return bool(artifact_pattern.match(artifact_name))

    def get_generator_path(self, artifact_name: str) -> Path:
        """
        Get file path for generator by artifact name.

        Security: Validates artifact_name before constructing path.

        Args:
            artifact_name: Artifact name (e.g., "epic", "backlog-story")

        Returns:
            Path to generator XML file

        Raises:
            ValueError: If artifact_name fails security validation
        """
        if not self.validate_artifact_name(artifact_name):
            msg = f"Invalid artifact name format: {artifact_name}"
            logger.warning(
                "invalid_artifact_name_rejected",
                artifact_name=artifact_name,
                reason="failed_security_validation",
            )
            raise ValueError(msg)

        return self.prompts_dir / f"{artifact_name}-generator.xml"
