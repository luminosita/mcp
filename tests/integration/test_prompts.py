"""
Integration tests for MCP generator prompts.

Tests TASK-011: Integration testing for all 10 generator prompts.
"""

from pathlib import Path
from typing import ClassVar

import pytest

from mcp_server.prompts.cache import PromptCache
from mcp_server.prompts.registry import PromptRegistry
from mcp_server.prompts.scanner import GeneratorScanner


@pytest.fixture
def prompts_dir():
    """Get path to prompts directory."""
    return Path(__file__).parent.parent.parent / "prompts"


@pytest.fixture
def prompt_cache():
    """Create fresh prompt cache for each test."""
    return PromptCache(ttl_seconds=300)


@pytest.fixture
def prompt_registry(prompts_dir, prompt_cache):
    """Create prompt registry for testing."""
    return PromptRegistry(prompts_dir=prompts_dir, cache=prompt_cache)


@pytest.fixture
def generator_scanner(prompts_dir):
    """Create generator scanner for testing."""
    return GeneratorScanner(prompts_dir=prompts_dir)


class TestGeneratorScanner:
    """Test generator file scanner functionality."""

    def test_scan_generators(self, generator_scanner):
        """Test successful generator discovery."""
        generators = generator_scanner.scan_generators()

        # Verify we found generators
        assert len(generators) >= 10, "Should discover at least 10 generators"

        # Verify expected generators exist
        expected_generators = [
            "epic",
            "prd",
            "backlog-story",
            "spike",
            "adr",
            "tech-spec",
            "implementation-task",
        ]
        for gen_name in expected_generators:
            assert gen_name in generators, f"Missing generator: {gen_name}"

    def test_validate_artifact_name_valid(self):
        """Test artifact name validation with valid names."""
        valid_names = [
            "epic",
            "prd",
            "backlog-story",
            "high-level-user-story",
            "tech-spec",
        ]
        for name in valid_names:
            assert GeneratorScanner.validate_artifact_name(name), f"Valid name rejected: {name}"

    def test_validate_artifact_name_invalid(self):
        """Test artifact name validation rejects attacks."""
        invalid_names = [
            "../etc/passwd",  # Path traversal
            "./secret",  # Relative path
            "EPIC",  # Uppercase
            "epic generator",  # Spaces
            "epic_generator",  # Underscore
            "epic@generator",  # Special chars
            "",  # Empty
        ]
        for name in invalid_names:
            assert not GeneratorScanner.validate_artifact_name(
                name
            ), f"Invalid name accepted: {name}"

    def test_get_generator_path(self, generator_scanner):
        """Test generator path resolution."""
        path = generator_scanner.get_generator_path("epic")
        assert path.name == "epic-generator.xml"
        assert path.parent.name == "prompts"

    def test_get_generator_path_rejects_invalid(self, generator_scanner):
        """Test generator path resolution rejects invalid names."""
        with pytest.raises(ValueError, match="Invalid artifact name format"):
            generator_scanner.get_generator_path("../etc/passwd")


class TestPromptCache:
    """Test prompt caching functionality."""

    def test_cache_miss(self, prompt_cache):
        """Test cache miss returns None."""
        result = prompt_cache.get("nonexistent")
        assert result is None
        assert prompt_cache.get_stats()["misses"] == 1

    def test_cache_hit(self, prompt_cache):
        """Test cache hit returns content."""
        content = "<generator>test content</generator>"
        prompt_cache.set("epic", content)

        result = prompt_cache.get("epic")
        assert result == content
        assert prompt_cache.get_stats()["hits"] == 1

    def test_cache_expiration(self, prompt_cache):
        """Test cache entry expires after TTL."""
        # Create cache with 1-second TTL
        short_ttl_cache = PromptCache(ttl_seconds=1)
        content = "<generator>test content</generator>"
        short_ttl_cache.set("epic", content)

        # Immediate retrieval should hit
        result = short_ttl_cache.get("epic")
        assert result == content

        # Wait for expiration (2 seconds to be safe)
        import time

        time.sleep(2)

        # Should now be expired
        result = short_ttl_cache.get("epic")
        assert result is None

    def test_cache_invalidate(self, prompt_cache):
        """Test cache invalidation."""
        prompt_cache.set("epic", "<generator>content</generator>")
        prompt_cache.invalidate("epic")

        result = prompt_cache.get("epic")
        assert result is None

    def test_cache_clear(self, prompt_cache):
        """Test clearing all cache entries."""
        prompt_cache.set("epic", "content1")
        prompt_cache.set("prd", "content2")

        prompt_cache.clear()

        assert prompt_cache.size == 0
        assert prompt_cache.get("epic") is None
        assert prompt_cache.get("prd") is None

    def test_cache_stats(self, prompt_cache):
        """Test cache statistics tracking."""
        prompt_cache.set("epic", "content")
        prompt_cache.get("epic")  # Hit
        prompt_cache.get("prd")  # Miss

        stats = prompt_cache.get_stats()
        assert stats["size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5
        assert stats["ttl_seconds"] == 300


class TestPromptRegistry:
    """Test prompt registry functionality."""

    @pytest.mark.asyncio
    async def test_load_prompt_success(self, prompt_registry):
        """Test successful prompt loading."""
        content = await prompt_registry.load_prompt("epic")

        assert content is not None
        assert len(content) > 0
        assert "<generator" in content or "<?xml" in content

    @pytest.mark.asyncio
    async def test_load_prompt_with_cache(self, prompt_registry):
        """Test prompt loading uses cache."""
        # First load - cache miss
        content1 = await prompt_registry.load_prompt("epic")

        # Second load - cache hit
        content2 = await prompt_registry.load_prompt("epic")

        assert content1 == content2

        # Verify cache hit
        stats = prompt_registry.get_cache_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    @pytest.mark.asyncio
    async def test_load_prompt_invalid_name(self, prompt_registry):
        """Test loading with invalid artifact name."""
        with pytest.raises(ValueError, match="Invalid artifact name format"):
            await prompt_registry.load_prompt("../etc/passwd")

    @pytest.mark.asyncio
    async def test_load_prompt_not_found(self, prompt_registry):
        """Test loading nonexistent generator."""
        with pytest.raises(FileNotFoundError, match="Generator file not found"):
            await prompt_registry.load_prompt("nonexistent")

    def test_list_available_prompts(self, prompt_registry):
        """Test listing available prompts."""
        prompts = prompt_registry.list_available_prompts()

        # Verify we have at least 10 prompts
        assert len(prompts) >= 10

        # Verify expected prompts
        expected = [
            "epic",
            "prd",
            "backlog-story",
            "spike",
            "adr",
            "tech-spec",
        ]
        for prompt_name in expected:
            assert prompt_name in prompts

        # Verify sorted
        assert prompts == sorted(prompts)


class TestAllGenerators:
    """Test all 10 generator prompts are accessible."""

    # List of all expected generators
    EXPECTED_GENERATORS: ClassVar[list[str]] = [
        "product-vision",
        "initiative",
        "epic",
        "prd",
        "high-level-user-story",
        "backlog-story",
        "spike",
        "adr",
        "tech-spec",
        "implementation-task",
        "business-research",
        "implementation-research",
        "funcspec",
    ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("artifact_name", EXPECTED_GENERATORS)
    async def test_load_all_generators(self, prompt_registry, artifact_name):
        """Test loading each generator by name (Acceptance Criteria 8)."""
        content = await prompt_registry.load_prompt(artifact_name)

        # Verify content is not empty
        assert len(content) > 0

        # Verify content looks like XML
        assert "<?xml" in content or "<generator" in content

        # Verify content is substantial (generators are typically >1KB)
        assert len(content) > 1000


class TestPerformance:
    """Test performance requirements."""

    @pytest.mark.asyncio
    async def test_prompt_loading_latency(self, prompt_registry):
        """Test p95 latency <100ms requirement (Acceptance Criteria 2)."""
        import time

        latencies = []

        # Load prompt 10 times to get p95
        for _ in range(10):
            start = time.time()
            await prompt_registry.load_prompt("epic")
            latency_ms = (time.time() - start) * 1000
            latencies.append(latency_ms)

        # Calculate p95 (9th value when sorted)
        p95 = sorted(latencies)[8]

        # Verify p95 < 100ms
        assert p95 < 100, f"p95 latency {p95:.2f}ms exceeds 100ms target"

    @pytest.mark.asyncio
    async def test_cache_hit_latency(self, prompt_registry):
        """Test cache hit latency <10ms (Acceptance Criteria 3)."""
        import time

        # Prime cache
        await prompt_registry.load_prompt("epic")

        # Measure cache hit latency
        start = time.time()
        await prompt_registry.load_prompt("epic")
        latency_ms = (time.time() - start) * 1000

        # Verify cache hit < 10ms
        assert latency_ms < 10, f"Cache hit latency {latency_ms:.2f}ms exceeds 10ms target"


class TestSecurityValidation:
    """Test security validation (Acceptance Criteria 6)."""

    @pytest.mark.asyncio
    async def test_path_traversal_prevention(self, prompt_registry):
        """Test path traversal attacks are rejected."""
        attack_vectors = [
            "../etc/passwd",
            "../../secret/config",
            "./local/file",
            "/etc/passwd",
            "..\\..\\windows\\system32",
        ]

        for attack in attack_vectors:
            with pytest.raises(ValueError, match="Invalid artifact name format"):
                await prompt_registry.load_prompt(attack)
