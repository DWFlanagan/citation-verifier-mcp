"""
Integration tests - "Does everything work together?"

These tests verify that the components work together end-to-end.
"""

import pytest


class TestIntegration:
    """Integration tests that verify the whole system works together."""

    @pytest.mark.slow
    async def test_citation_verification_end_to_end(self) -> None:
        """Test: Can we verify citations through the entire pipeline?"""
        from citation_verifier_mcp.server import handle_call_tool, initialize_citation_verifier
        from tests.conftest import INVALID_DOI, VALID_DOI

        # Initialize the system
        await initialize_citation_verifier()

        # Test valid DOI
        valid_result = await handle_call_tool("verify_citation", {"doi": VALID_DOI})
        assert isinstance(valid_result, list)
        assert len(valid_result) > 0
        assert VALID_DOI in str(valid_result)

        # Test invalid DOI
        invalid_result = await handle_call_tool("verify_citation", {"doi": INVALID_DOI})
        assert isinstance(invalid_result, list)
        assert len(invalid_result) > 0
        assert INVALID_DOI in str(invalid_result)

    @pytest.mark.slow
    async def test_multiple_concurrent_requests(self) -> None:
        """Test: Can the system handle multiple concurrent verification requests?"""
        import asyncio

        from citation_verifier_mcp.server import handle_call_tool, initialize_citation_verifier
        from tests.conftest import VALID_DOI

        async def verify_doi(doi: str) -> object:
            return await handle_call_tool("verify_citation", {"doi": doi})

        await initialize_citation_verifier()

        # Run multiple verifications concurrently
        tasks = [verify_doi(VALID_DOI) for _ in range(3)]
        results = await asyncio.gather(*tasks)

        # All should succeed
        assert len(results) == 3
        for result in results:
            assert isinstance(result, list)
            assert len(result) > 0
            assert VALID_DOI in str(result)

    async def test_error_handling_robustness(self) -> None:
        """Test: Does the system handle various error conditions gracefully?"""
        from citation_verifier_mcp.server import handle_call_tool, initialize_citation_verifier
        from tests.conftest import MALFORMED_DOI

        await initialize_citation_verifier()

        # Test with malformed DOI
        result = await handle_call_tool("verify_citation", {"doi": MALFORMED_DOI})
        assert isinstance(result, list)
        assert len(result) > 0
        # Should not crash, should return some kind of error message

        # Test with empty DOI
        result = await handle_call_tool("verify_citation", {"doi": ""})
        assert isinstance(result, list)
        assert len(result) > 0

        # Test with very long DOI
        long_doi = "10.1234/" + "x" * 1000
        result = await handle_call_tool("verify_citation", {"doi": long_doi})
        assert isinstance(result, list)
        assert len(result) > 0

    def test_format_verification_result_valid(self) -> None:
        """Test: Does the result formatting work correctly for valid citations?"""
        from citation_verifier_mcp.server import format_verification_result

        # Mock a successful verification result
        mock_result = {
            "verified": True,
            "doi": "10.1038/nature12373",
            "title": "Test Paper Title",
            "authors": "Test Author",
            "journal": "Test Journal",
            "publisher": "Test Publisher",
            "year": "2023",
            "url": "https://doi.org/10.1038/nature12373",
        }

        formatted = format_verification_result(mock_result)

        assert "✅ Citation Verified" in formatted
        assert "10.1038/nature12373" in formatted
        assert "Test Paper Title" in formatted
        assert "Test Author" in formatted
        assert "legitimate citation" in formatted

    def test_format_verification_result_invalid(self) -> None:
        """Test: Does the result formatting work correctly for invalid citations?"""
        from citation_verifier_mcp.server import format_verification_result

        # Mock a failed verification result
        mock_result = {
            "verified": False,
            "doi": "10.1234/fake.citation.2024",
            "error": "DOI not found in Crossref database",
        }

        formatted = format_verification_result(mock_result)

        assert "❌ Citation Not Verified" in formatted
        assert "10.1234/fake.citation.2024" in formatted
        assert "DOI not found in Crossref database" in formatted
        assert "hallucinated/fake" in formatted
        assert "Warning" in formatted


class TestPerformance:
    """Basic performance tests."""

    @pytest.mark.slow
    async def test_single_verification_performance(self) -> None:
        """Test: Is single verification reasonably fast?"""
        import time

        from citation_verifier_mcp.server import handle_call_tool, initialize_citation_verifier
        from tests.conftest import VALID_DOI

        await initialize_citation_verifier()

        start_time = time.time()
        await handle_call_tool("verify_citation", {"doi": VALID_DOI})
        end_time = time.time()

        # Should complete within reasonable time (30 seconds for network call)
        duration = end_time - start_time
        assert duration < 30.0, f"Verification took too long: {duration} seconds"


class TestConfiguration:
    """Test configuration and setup."""

    def test_project_structure_is_correct(self) -> None:
        """Test: Is the project structure what we expect?"""
        # Check that we can import the modules
        from citation_verifier_mcp.server import initialize_citation_verifier, main
        from citation_verifier_mcp.websocket_server import app

        # Key functions should exist
        assert callable(main)
        assert callable(initialize_citation_verifier)
        assert app is not None

    def test_dependencies_are_available(self) -> None:
        """Test: Are all required dependencies available?"""
        # These imports should work without error
        import fastapi
        import llm_citation_verifier
        import mcp

        # Basic functionality should be available
        assert hasattr(mcp, "server")
        assert hasattr(llm_citation_verifier, "CitationVerifier")
        assert hasattr(fastapi, "FastAPI")
