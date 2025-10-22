"""
Integration tests for MCP resource endpoints.

Tests resource loading, error handling, and security for pattern and SDLC resources.
Uses real file system operations with test fixtures.
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mcp_server.config import settings


@pytest.fixture
def temp_patterns_dir(tmp_path: Path):
    """
    Create temporary patterns directory with test files.

    Args:
        tmp_path: Pytest temporary directory fixture

    Yields:
        Path to temporary patterns directory
    """
    # Create directory structure
    python_dir = tmp_path / "python"
    python_dir.mkdir(parents=True)

    go_dir = tmp_path / "go"
    go_dir.mkdir(parents=True)

    # Create test pattern files
    (python_dir / "CLAUDE-core.md").write_text(
        "# Core Patterns\n\nPython implementation patterns..."
    )
    (python_dir / "CLAUDE-tooling.md").write_text(
        "# Tooling Patterns\n\nUV, Ruff, MyPy configuration..."
    )
    (go_dir / "CLAUDE-core.md").write_text("# Core Patterns\n\nGo implementation patterns...")

    # Create SDLC core file
    (tmp_path / "sdlc-core.md").write_text("# SDLC Framework\n\nSDLC orchestration...")

    # Temporarily override settings
    original_patterns_base_dir = settings.patterns_base_dir
    original_sdlc_core_file_path = settings.sdlc_core_file_path

    settings.patterns_base_dir = str(tmp_path)
    settings.sdlc_core_file_path = str(tmp_path / "sdlc-core.md")

    yield tmp_path

    # Restore original settings
    settings.patterns_base_dir = original_patterns_base_dir
    settings.sdlc_core_file_path = original_sdlc_core_file_path


@pytest.fixture
def temp_templates_dir(tmp_path: Path):
    """
    Create temporary templates directory with test template files.

    Args:
        tmp_path: Pytest temporary directory fixture

    Yields:
        Path to temporary templates directory
    """
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir(parents=True)

    # Create test template files for all 10 artifact types
    templates = {
        "product-vision-template.xml": "<?xml version='1.0'?><template><name>Vision</name></template>",
        "initiative-template.xml": "<?xml version='1.0'?><template><name>Initiative</name></template>",
        "epic-template.xml": "<?xml version='1.0'?><template><name>Epic</name></template>",
        "prd-template.xml": "<?xml version='1.0'?><template><name>PRD</name></template>",
        "hls-template.xml": "<?xml version='1.0'?><template><name>HLS</name></template>",
        "backlog-story-template.xml": "<?xml version='1.0'?><template><name>Story</name></template>",
        "spike-template.xml": "<?xml version='1.0'?><template><name>Spike</name></template>",
        "adr-template.xml": "<?xml version='1.0'?><template><name>ADR</name></template>",
        "tech-spec-template.xml": "<?xml version='1.0'?><template><name>Spec</name></template>",
        "implementation-task-template.xml": "<?xml version='1.0'?><template><name>Task</name></template>",
    }

    for filename, content in templates.items():
        (templates_dir / filename).write_text(content)

    # Temporarily override settings
    original_templates_dir = settings.templates_dir

    settings.templates_dir = str(templates_dir)

    yield templates_dir

    # Restore original settings
    settings.templates_dir = original_templates_dir


class TestPatternResourceEndpoint:
    """Test /mcp/resources/patterns/{name} endpoint."""

    def test_get_python_core_pattern(self, client: TestClient, temp_patterns_dir):
        """Test retrieving Python core pattern file."""
        response = client.get("/mcp/resources/patterns/core?language=python")

        assert response.status_code == 200
        data = response.json()

        assert data["uri"] == "mcp://resources/patterns/python/core"
        assert "Core Patterns" in data["content"]
        assert "Python implementation patterns" in data["content"]
        assert data["size_bytes"] > 0

    def test_get_go_core_pattern(self, client: TestClient, temp_patterns_dir):
        """Test retrieving Go core pattern file."""
        response = client.get("/mcp/resources/patterns/core?language=go")

        assert response.status_code == 200
        data = response.json()

        assert data["uri"] == "mcp://resources/patterns/go/core"
        assert "Go implementation patterns" in data["content"]
        assert data["size_bytes"] > 0

    def test_get_tooling_pattern(self, client: TestClient, temp_patterns_dir):
        """Test retrieving tooling pattern file."""
        response = client.get("/mcp/resources/patterns/tooling?language=python")

        assert response.status_code == 200
        data = response.json()

        assert data["uri"] == "mcp://resources/patterns/python/tooling"
        assert "Tooling Patterns" in data["content"]
        assert "UV, Ruff, MyPy" in data["content"]

    def test_default_language_is_python(self, client: TestClient, temp_patterns_dir):
        """Test that default language is Python when not specified."""
        response = client.get("/mcp/resources/patterns/core")

        assert response.status_code == 200
        data = response.json()

        assert data["uri"] == "mcp://resources/patterns/python/core"
        assert "Python implementation patterns" in data["content"]

    def test_missing_resource_returns_404(self, client: TestClient, temp_patterns_dir):
        """Test that missing resource returns 404 error."""
        response = client.get("/mcp/resources/patterns/nonexistent?language=python")

        assert response.status_code == 404
        assert "Resource not found" in response.json()["detail"]

    def test_missing_language_directory_returns_404(self, client: TestClient, temp_patterns_dir):
        """Test that missing language directory returns 404."""
        response = client.get("/mcp/resources/patterns/core?language=rust")

        assert response.status_code == 404


class TestSDLCCoreResourceEndpoint:
    """Test /mcp/resources/sdlc/core endpoint."""

    def test_get_sdlc_core(self, client: TestClient, temp_patterns_dir):
        """Test retrieving SDLC core framework file."""
        response = client.get("/mcp/resources/sdlc/core")

        assert response.status_code == 200
        data = response.json()

        assert data["uri"] == "mcp://resources/sdlc/core"
        assert "SDLC Framework" in data["content"]
        assert "SDLC orchestration" in data["content"]
        assert data["size_bytes"] > 0

    def test_missing_sdlc_core_returns_404(self, client: TestClient, tmp_path):
        """Test that missing SDLC core file returns 404."""
        # Override settings to point to non-existent file
        original_sdlc_path = settings.sdlc_core_file_path
        settings.sdlc_core_file_path = str(tmp_path / "nonexistent.md")

        response = client.get("/mcp/resources/sdlc/core")

        assert response.status_code == 404
        assert "Resource not found" in response.json()["detail"]

        # Restore settings
        settings.sdlc_core_file_path = original_sdlc_path


class TestPathTraversalSecurity:
    """Test path traversal attack prevention."""

    def test_reject_parent_directory_reference(self, client: TestClient, temp_patterns_dir):
        """
        Test that parent directory references are rejected.

        Note: FastAPI/Starlette normalizes URLs before routing, so all path traversal
        attempts like "../etc/passwd" or "foo/../bar" are normalized to their resolved
        paths before reaching our validation code.

        This is GOOD security - attacks are blocked at the HTTP server level.
        All attack vectors should return either 404 (route not found) or 400 (validation).
        """
        attack_vectors = [
            "../etc/passwd",
            "../../etc/passwd",
            "foo/../bar",
            "..core",
        ]

        for attack in attack_vectors:
            response = client.get(f"/mcp/resources/patterns/{attack}?language=python")
            # Path traversal attempts are blocked at HTTP server level (normalized away)
            # or by validation - both return non-2xx status codes
            assert response.status_code in [400, 404], f"Failed to block: {attack}"

    def test_reject_absolute_path(self, client: TestClient, temp_patterns_dir):
        """
        Test that absolute paths are rejected.

        Note: Double slashes in URLs are normalized by HTTP server,
        so "//etc/passwd" becomes "/etc/passwd" which doesn't match route.
        """
        response = client.get("/mcp/resources/patterns//etc/passwd?language=python")

        # Should return 404 (route not found after normalization) or 400 (validation)
        assert response.status_code in [400, 404]

    def test_reject_invalid_characters(self, client: TestClient, temp_patterns_dir):
        """Test that invalid characters are rejected."""
        invalid_names = [
            "core.md",  # Dots
            "core;rm",  # Semicolon
            "core|cat",  # Pipe
            "CORE",  # Uppercase
        ]

        for invalid_name in invalid_names:
            response = client.get(f"/mcp/resources/patterns/{invalid_name}?language=python")
            assert response.status_code == 400, f"Failed to block: {invalid_name}"

    def test_file_access_restricted_to_base_directory(self, client: TestClient, tmp_path):
        """Test that file access is restricted to configured base directory."""
        # Create test file outside base directory
        outside_dir = tmp_path / "outside"
        outside_dir.mkdir()
        (outside_dir / "secret.md").write_text("Secret content")

        # Create patterns dir
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()
        python_dir = patterns_dir / "python"
        python_dir.mkdir()

        # Override settings
        original_patterns_base_dir = settings.patterns_base_dir
        settings.patterns_base_dir = str(patterns_dir)

        # Attempt to access file outside base directory (even with valid path construction)
        # This should be blocked by the relative_to() check in load_resource_file
        response = client.get("/mcp/resources/patterns/secret?language=python")

        # Should return 404 (file not found in allowed directory)
        assert response.status_code == 404

        # Restore settings
        settings.patterns_base_dir = original_patterns_base_dir


class TestErrorHandling:
    """Test error handling for various failure scenarios."""

    def test_handle_permission_error(self, client: TestClient, tmp_path):
        """Test handling of permission errors when reading files."""
        # Create patterns directory
        python_dir = tmp_path / "python"
        python_dir.mkdir(parents=True)

        # Create file with no read permissions
        test_file = python_dir / "CLAUDE-core.md"
        test_file.write_text("Test content")
        test_file.chmod(0o000)  # Remove all permissions

        # Override settings
        original_patterns_base_dir = settings.patterns_base_dir
        settings.patterns_base_dir = str(tmp_path)

        try:
            response = client.get("/mcp/resources/patterns/core?language=python")

            # Should return 403 Forbidden or 500 Internal Server Error
            assert response.status_code in [403, 500]
        finally:
            # Restore permissions and settings
            test_file.chmod(0o644)
            settings.patterns_base_dir = original_patterns_base_dir

    def test_invalid_language_parameter(self, client: TestClient, temp_patterns_dir):
        """Test that invalid language parameter is rejected."""
        invalid_languages = [
            "Python",  # Uppercase
            "python3",  # Numbers
            "go-lang",  # Hyphen
        ]

        for lang in invalid_languages:
            response = client.get(f"/mcp/resources/patterns/core?language={lang}")
            assert response.status_code == 422, f"Failed to block language: {lang}"


class TestResponseFormat:
    """Test resource response format compliance."""

    def test_response_includes_required_fields(self, client: TestClient, temp_patterns_dir):
        """Test that response includes all required fields."""
        response = client.get("/mcp/resources/patterns/core?language=python")

        assert response.status_code == 200
        data = response.json()

        # Verify required fields
        assert "uri" in data
        assert "content" in data
        assert "size_bytes" in data

        # Verify field types
        assert isinstance(data["uri"], str)
        assert isinstance(data["content"], str)
        assert isinstance(data["size_bytes"], int)
        assert data["size_bytes"] >= 0

    def test_size_bytes_matches_content_length(self, client: TestClient, temp_patterns_dir):
        """Test that size_bytes field matches actual content length."""
        response = client.get("/mcp/resources/patterns/core?language=python")

        assert response.status_code == 200
        data = response.json()

        actual_size = len(data["content"].encode("utf-8"))
        assert data["size_bytes"] == actual_size


class TestTemplateResourceEndpoints:
    """Test /mcp/resources/templates endpoints (US-031)."""

    def test_list_all_templates(self, client: TestClient, temp_templates_dir):
        """Test template enumeration endpoint returns all 10 templates."""
        response = client.get("/mcp/resources/templates")

        assert response.status_code == 200
        data = response.json()

        assert "templates" in data
        templates = data["templates"]
        assert len(templates) == 10

        # Verify all template names are present
        template_names = {t["name"] for t in templates}
        expected_names = {
            "vision",
            "initiative",
            "epic",
            "prd",
            "hls",
            "story",
            "spike",
            "adr",
            "spec",
            "task",
        }
        assert template_names == expected_names

        # Verify each template has required fields
        for template in templates:
            assert "name" in template
            assert "uri" in template
            assert "filename" in template
            assert template["uri"].startswith("mcp://resources/templates/")

    def test_get_prd_template(self, client: TestClient, temp_templates_dir):
        """Test retrieving PRD template."""
        response = client.get("/mcp/resources/templates/prd")

        assert response.status_code == 200
        data = response.json()

        assert data["uri"] == "mcp://resources/templates/prd"
        assert "<name>PRD</name>" in data["content"]
        assert data["size_bytes"] > 0

    def test_get_story_template(self, client: TestClient, temp_templates_dir):
        """Test retrieving backlog story template."""
        response = client.get("/mcp/resources/templates/story")

        assert response.status_code == 200
        data = response.json()

        assert data["uri"] == "mcp://resources/templates/story"
        assert "<name>Story</name>" in data["content"]
        assert data["size_bytes"] > 0

    def test_get_all_10_template_types(self, client: TestClient, temp_templates_dir):
        """Test that all 10 template types are accessible."""
        template_types = [
            ("vision", "Vision"),
            ("initiative", "Initiative"),
            ("epic", "Epic"),
            ("prd", "PRD"),
            ("hls", "HLS"),
            ("story", "Story"),
            ("spike", "Spike"),
            ("adr", "ADR"),
            ("spec", "Spec"),
            ("task", "Task"),
        ]

        for template_name, expected_content in template_types:
            response = client.get(f"/mcp/resources/templates/{template_name}")

            assert response.status_code == 200, f"Failed to load {template_name} template"
            data = response.json()

            assert data["uri"] == f"mcp://resources/templates/{template_name}"
            assert f"<name>{expected_content}</name>" in data["content"]
            assert data["size_bytes"] > 0

    def test_invalid_template_name_returns_404(self, client: TestClient, temp_templates_dir):
        """Test that invalid template name returns 404."""
        response = client.get("/mcp/resources/templates/nonexistent")

        assert response.status_code == 404
        assert "Resource not found" in response.json()["detail"]

    def test_path_traversal_protection(self, client: TestClient, temp_templates_dir):
        """Test that path traversal attempts are blocked."""
        attack_vectors = [
            "../etc/passwd",
            "../../etc/passwd",
            "foo/../bar",
        ]

        for attack in attack_vectors:
            response = client.get(f"/mcp/resources/templates/{attack}")
            # Should return 400 Bad Request or 404 Not Found (route mismatch)
            assert response.status_code in [400, 404], f"Failed to block: {attack}"

    def test_template_not_in_whitelist_returns_404(self, client: TestClient, temp_templates_dir):
        """Test that template names not in TEMPLATE_FILE_MAP are rejected."""
        # Create a template file that exists but isn't in the whitelist
        (temp_templates_dir / "custom-template.xml").write_text(
            "<?xml version='1.0'?><template><name>Custom</name></template>"
        )

        response = client.get("/mcp/resources/templates/custom")

        # Should return 404 because "custom" is not in TEMPLATE_FILE_MAP
        assert response.status_code == 404
        assert "Resource not found" in response.json()["detail"]

    def test_template_response_format(self, client: TestClient, temp_templates_dir):
        """Test that template responses include all required fields."""
        response = client.get("/mcp/resources/templates/prd")

        assert response.status_code == 200
        data = response.json()

        # Verify required fields
        assert "uri" in data
        assert "content" in data
        assert "size_bytes" in data

        # Verify field types
        assert isinstance(data["uri"], str)
        assert isinstance(data["content"], str)
        assert isinstance(data["size_bytes"], int)
        assert data["size_bytes"] >= 0

    def test_template_size_matches_content(self, client: TestClient, temp_templates_dir):
        """Test that size_bytes matches actual content length."""
        response = client.get("/mcp/resources/templates/epic")

        assert response.status_code == 200
        data = response.json()

        actual_size = len(data["content"].encode("utf-8"))
        assert data["size_bytes"] == actual_size
