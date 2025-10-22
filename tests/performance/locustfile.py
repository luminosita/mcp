"""
Locust load testing script for MCP resource endpoints (US-033).

Tests resource loading performance under realistic load:
- 100 concurrent users
- 10 spawn rate
- 5-minute duration
- Realistic access patterns (frequent SDLC core, varied patterns, occasional templates)

Target: <100ms p95 latency for resource loading

Usage:
    # Run with default configuration (100 users, 5 minutes)
    locust -f locustfile.py --headless --users 100 --spawn-rate 10 --run-time 5m

    # Run with web UI for real-time monitoring
    locust -f locustfile.py

    # Run with custom configuration
    locust -f locustfile.py --headless --users 50 --spawn-rate 5 --run-time 2m

    # Export results to CSV
    locust -f locustfile.py --headless --users 100 --spawn-rate 10 --run-time 5m --csv=results
"""

import random

from locust import HttpUser, between, task


class ResourceLoadUser(HttpUser):
    """
    Simulates Claude Code user loading MCP resources.

    Models realistic access patterns:
    - Frequent: SDLC core resource (high cache hit rate expected)
    - Frequent: Pattern core resource (high cache hit rate)
    - Moderate: Other pattern files (varied cache behavior)
    - Occasional: Template files (varied cache behavior)
    """

    # Wait 0.1-0.5 seconds between requests (simulates user reading/processing)
    wait_time = between(0.1, 0.5)

    # Base URL for API (override with --host flag or in web UI)
    # Example: locust -f locustfile.py --host http://localhost:8000
    host = "http://localhost:8000"

    @task(5)
    def get_sdlc_core(self):
        """
        Frequent: SDLC core resource (highest access frequency).

        Expected: High cache hit rate (>90%) after warmup.
        Target latency: <10ms p95 (cache hit), <50ms p95 (cache miss).
        """
        with self.client.get(
            "/mcp/resources/sdlc/core",
            name="/mcp/resources/sdlc/core",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "content" in data and data["size_bytes"] > 0:
                    response.success()
                else:
                    response.failure("Invalid response: missing content or size_bytes")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(4)
    def get_pattern_core(self):
        """
        Frequent: Pattern core resource (second highest frequency).

        Expected: High cache hit rate (>80%) after warmup.
        Target latency: <10ms p95 (cache hit), <50ms p95 (cache miss).
        """
        with self.client.get(
            "/mcp/resources/patterns/core?language=python",
            name="/mcp/resources/patterns/{name}",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "content" in data and data["size_bytes"] > 0:
                    response.success()
                else:
                    response.failure("Invalid response: missing content or size_bytes")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(3)
    def get_pattern_varied(self):
        """
        Moderate: Various pattern files (moderate frequency).

        Expected: Moderate cache hit rate (50-70%) due to variety.
        Target latency: <100ms p95 (combined cache hit + miss).
        """
        patterns = [
            "tooling",
            "testing",
            "typing",
            "validation",
            "architecture",
            "auth",
            "database",
            "http-frameworks",
        ]
        pattern = random.choice(patterns)  # noqa: S311

        with self.client.get(
            f"/mcp/resources/patterns/{pattern}?language=python",
            name="/mcp/resources/patterns/{name}",
            catch_response=True,
        ) as response:
            # Accept 404 for non-existent patterns (testing robustness)
            if response.status_code == 200:
                data = response.json()
                if "content" in data and data["size_bytes"] > 0:
                    response.success()
                else:
                    response.failure("Invalid response: missing content or size_bytes")
            elif response.status_code == 404:
                # 404 is acceptable for non-existent patterns
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(2)
    def get_template(self):
        """
        Occasional: Template files (lower frequency).

        Expected: Variable cache hit rate (30-50%) due to variety.
        Target latency: <100ms p95 (combined cache hit + miss).
        """
        templates = [
            "prd",
            "epic",
            "story",
            "spec",
            "task",
            "spike",
            "adr",
            "hls",
            "vision",
            "initiative",
        ]
        template = random.choice(templates)  # noqa: S311

        with self.client.get(
            f"/mcp/resources/templates/{template}",
            name="/mcp/resources/templates/{type}",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "content" in data and data["size_bytes"] > 0:
                    response.success()
                else:
                    response.failure("Invalid response: missing content or size_bytes")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(1)
    def list_templates(self):
        """
        Rare: List all templates (metadata endpoint).

        Expected: Fast response (no file I/O, returns cached metadata).
        Target latency: <50ms p95.
        """
        with self.client.get(
            "/mcp/resources/templates",
            name="/mcp/resources/templates (list)",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "templates" in data and len(data["templates"]) == 10:
                    response.success()
                else:
                    response.failure("Invalid response: expected 10 templates")
            else:
                response.failure(f"Status code: {response.status_code}")


# Custom test configuration for CI/CD integration
class QuickLoadUser(HttpUser):
    """
    Quick load test for CI/CD pipelines (30 users, 1 minute).

    Use for fast feedback in CI/CD:
        locust -f locustfile.py --headless --users 30 --spawn-rate 5 --run-time 1m QuickLoadUser
    """

    wait_time = between(0.1, 0.3)
    host = "http://localhost:8000"

    @task(3)
    def get_sdlc_core(self):
        """Quick test: SDLC core resource."""
        self.client.get("/mcp/resources/sdlc/core")

    @task(2)
    def get_pattern_core(self):
        """Quick test: Pattern core resource."""
        self.client.get("/mcp/resources/patterns/core?language=python")

    @task(1)
    def get_template(self):
        """Quick test: Random template."""
        template = random.choice(["prd", "epic", "story"])  # noqa: S311
        self.client.get(f"/mcp/resources/templates/{template}")
