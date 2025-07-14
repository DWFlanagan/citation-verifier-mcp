"""
Basic smoke tests - "Does the MCP server start and work?"

These tests verify the core functionality without diving into complex scenarios.
"""

from typing import Any

import pytest

from citation_verifier_mcp.server import initialize_citation_verifier
from tests.conftest import INVALID_DOI, VALID_DOI


class TestMCPServerBasics:
    """Test that the MCP server can start and handle basic operations."""

    async def test_server_can_initialize(self) -> None:
        """Test: Can we create and initialize the MCP server?"""
        # This should not raise an exception
        await initialize_citation_verifier()

    async def test_citation_verifier_is_available(self, citation_verifier: Any) -> None:
        """Test: Is the citation verifier properly initialized?"""
        assert citation_verifier is not None
        # Should have the verify_doi method
        assert hasattr(citation_verifier, "verify_doi")
        assert callable(citation_verifier.verify_doi)

    async def test_server_lists_tools(self) -> None:
        """Test: Does the server report the citation verification tool?"""
        from citation_verifier_mcp.server import handle_list_tools

        tools = await handle_list_tools()

        assert len(tools) == 1
        tool = tools[0]
        assert tool.name == "verify_citation"
        assert tool.description is not None
        assert "DOI" in tool.description
        assert tool.inputSchema is not None

    async def test_valid_doi_verification_works(self, citation_verifier: Any) -> None:
        """Test: Can we verify a real DOI successfully?"""
        # Use a real DOI that should exist
        result = citation_verifier.verify_doi(VALID_DOI)

        assert isinstance(result, dict)
        assert "verified" in result
        assert "doi" in result

        # A valid DOI should be verified (assuming network access)
        if result["verified"]:
            assert "title" in result
            assert "authors" in result
            assert result["doi"] == VALID_DOI

    async def test_invalid_doi_is_handled(self, citation_verifier: Any) -> None:
        """Test: Does the system handle invalid DOIs gracefully?"""
        result = citation_verifier.verify_doi(INVALID_DOI)

        assert isinstance(result, dict)
        assert "verified" in result
        assert "doi" in result
        assert result["doi"] == INVALID_DOI

        # Should not be verified
        assert not result["verified"]
        assert "error" in result

    async def test_mcp_tool_call_with_valid_doi(self) -> None:
        """Test: Can we call the MCP tool with a valid DOI?"""
        from citation_verifier_mcp.server import handle_call_tool

        # Initialize first
        await initialize_citation_verifier()

        # Call the tool
        result = await handle_call_tool("verify_citation", {"doi": VALID_DOI})

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].type == "text"
        assert VALID_DOI in result[0].text

    async def test_mcp_tool_call_with_invalid_doi(self) -> None:
        """Test: Can we call the MCP tool with an invalid DOI?"""
        from citation_verifier_mcp.server import handle_call_tool

        # Initialize first
        await initialize_citation_verifier()

        # Call the tool
        result = await handle_call_tool("verify_citation", {"doi": INVALID_DOI})

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].type == "text"
        assert INVALID_DOI in result[0].text

    async def test_unknown_tool_raises_error(self) -> None:
        """Test: Does calling an unknown tool raise an appropriate error?"""
        from citation_verifier_mcp.server import handle_call_tool

        with pytest.raises(ValueError, match="Unknown tool"):
            await handle_call_tool("nonexistent_tool", {})

    async def test_tool_call_without_initialization_fails(self) -> None:
        """Test: Does calling tools before initialization fail gracefully?"""
        import citation_verifier_mcp.server as server_module
        from citation_verifier_mcp.server import handle_call_tool

        # Reset the global citation_verifier
        server_module.citation_verifier = None

        with pytest.raises(RuntimeError, match="Citation verifier not initialized"):
            await handle_call_tool("verify_citation", {"doi": VALID_DOI})
