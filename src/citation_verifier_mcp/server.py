# src/citation_verifier_mcp/server.py

import asyncio
import logging
from typing import Any, Dict, List

import mcp.server.stdio
import mcp.types as types
from llm_citation_verifier import CitationVerifier
from mcp.server import Server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
server: Server = Server("citation-verifier", version="0.1.2")

# Global citation verifier instance
citation_verifier = None


async def initialize_citation_verifier() -> None:
    """Initialize the citation verifier."""
    global citation_verifier

    try:
        citation_verifier = CitationVerifier()
        logger.info("Citation verifier initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize citation verifier: {e}")
        raise


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="verify_citation",
            description="Verify a DOI citation against the Crossref database. Detects potentially hallucinated citations by checking if DOIs exist and retrieving bibliographic metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "doi": {
                        "type": "string",
                        "description": "The DOI to verify (e.g., '10.1038/nature12373'). Can include URL prefixes which will be automatically stripped.",
                    }
                },
                "required": ["doi"],
            },
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls."""

    if name != "verify_citation":
        raise ValueError(f"Unknown tool: {name}")

    if not citation_verifier:
        raise RuntimeError("Citation verifier not initialized")

    try:
        # Extract DOI from arguments
        doi = arguments["doi"]

        logger.info(f"Verifying citation for DOI: {doi}")

        # Call your citation verifier
        result = citation_verifier.verify_doi(doi)

        # Format the result for MCP response
        formatted_result = format_verification_result(result)

        return [types.TextContent(type="text", text=formatted_result)]

    except Exception as e:
        logger.error(f"Error in citation verification: {e}")
        return [
            types.TextContent(type="text", text=f"Error during citation verification: {str(e)}")
        ]


def format_verification_result(result: Dict) -> str:
    """Format citation verification result for display."""
    if result["verified"]:
        # Successfully verified citation
        output = f"""# ✅ Citation Verified

**DOI:** {result["doi"]}
**Title:** {result["title"]}
**Authors:** {result["authors"]}
**Journal:** {result["journal"]}
**Publisher:** {result["publisher"]}
**Year:** {result["year"]}
**URL:** {result["url"]}

This DOI exists in the Crossref database and appears to be a legitimate citation."""
    else:
        # Failed verification - likely hallucinated
        output = f"""# ❌ Citation Not Verified

**DOI:** {result["doi"]}
**Error:** {result["error"]}

⚠️ **Warning:** This DOI was not found in the Crossref database. This may indicate:
- The DOI is hallucinated/fake
- The DOI contains typos
- The paper is very recent and not yet indexed
- The publisher doesn't use Crossref

**Recommendation:** Verify this citation manually or find an alternative source."""

    return output


async def main() -> None:
    """Run the MCP server."""
    try:
        # Initialize citation verifier
        await initialize_citation_verifier()

        # Start MCP server
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            options = server.create_initialization_options()
            await server.run(read_stream, write_stream, options)
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
