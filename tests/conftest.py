"""
Test configuration and shared fixtures.
"""

import asyncio
import os
import sys
from typing import Any, Generator

import pytest

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def citation_verifier() -> Any:
    """Create a citation verifier instance for testing."""
    from citation_verifier_mcp.server import initialize_citation_verifier

    await initialize_citation_verifier()
    from citation_verifier_mcp.server import citation_verifier as cv

    return cv


# Test data - real DOIs for testing
VALID_DOI = "10.1038/nature12373"  # A real Nature paper
INVALID_DOI = "10.1234/fake.citation.2024"  # Fake DOI that shouldn't exist
MALFORMED_DOI = "not-a-doi"  # Invalid DOI format
