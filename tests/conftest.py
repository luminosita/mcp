"""
Pytest configuration and shared fixtures.

Defines fixtures and test configuration for the entire test suite.
"""

import pytest


@pytest.fixture
def sample_fixture():
    """Sample fixture for demonstration."""
    return {"status": "test"}
