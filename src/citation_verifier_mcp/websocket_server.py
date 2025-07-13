# src/citation_verifier_mcp/websocket_server.py

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import mcp.types as types
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from llm_citation_verifier import CitationVerifier

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global citation verifier instance
citation_verifier: Optional[CitationVerifier] = None


async def initialize_citation_verifier():
    """Initialize the citation verifier."""
    global citation_verifier

    try:
        citation_verifier = CitationVerifier()
        logger.info("Citation verifier initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize citation verifier: {e}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    await initialize_citation_verifier()
    yield
    # Shutdown (if needed)


# Initialize FastAPI app with lifespan
app = FastAPI(title="Citation Verifier MCP Server", version="0.1.0", lifespan=lifespan)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


class MCPConnection:
    """Manages a single MCP connection via WebSocket."""

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.initialized = False

    async def handle_message(self, message: dict) -> dict:
        """Handle incoming MCP messages."""
        try:
            # Parse the MCP request
            if message.get("method") == "initialize":
                return {
                    "id": message.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "citation-verifier", "version": "0.1.0"},
                    },
                }

            elif message.get("method") == "tools/list":
                tools = await handle_list_tools()
                return {
                    "id": message.get("id"),
                    "result": {"tools": [tool.model_dump() for tool in tools]},
                }

            elif message.get("method") == "tools/call":
                params = message.get("params", {})
                name = params.get("name")
                arguments = params.get("arguments", {})

                result = await handle_call_tool(name, arguments)
                return {
                    "id": message.get("id"),
                    "result": {"content": [content.model_dump() for content in result]},
                }

            else:
                return {
                    "id": message.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {message.get('method')}",
                    },
                }

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return {
                "id": message.get("id"),
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
            }


@app.websocket("/mcp")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for MCP communication."""
    await websocket.accept()
    connection = MCPConnection(websocket)

    logger.info("New MCP WebSocket connection established")

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle the message
            response = await connection.handle_message(message)

            # Send response back to client
            await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        logger.info("MCP WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


@app.get("/sse")
async def sse_endpoint():
    """Server-Sent Events endpoint for MCP communication."""

    async def generate_sse():
        """Generate SSE events for MCP communication."""
        # Proper SSE headers and format
        yield "event: connect\n"
        yield f"data: {json.dumps({'type': 'connection', 'status': 'ready'})}\n\n"

        # Keep connection alive
        while True:
            await asyncio.sleep(30)  # Send keepalive every 30 seconds
            yield "event: keepalive\n"
            yield f"data: {json.dumps({'type': 'keepalive'})}\n\n"

    return StreamingResponse(
        generate_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )


@app.post("/messages")
async def handle_http_message(request: dict):
    """Handle HTTP POST messages for MCP communication."""
    try:
        # Handle the MCP message via HTTP POST
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "citation-verifier",
                        "version": "0.1.0"
                    }
                }
            }

        elif method == "tools/list":
            tools = await handle_list_tools()
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [tool.model_dump() for tool in tools]
                }
            }

        elif method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments", {})

            result = await handle_call_tool(name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [content.model_dump() for content in result]
                }
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

    except Exception as e:
        logger.error(f"Error handling HTTP message: {e}")
        return {
            "jsonrpc": "2.0",
            "id": request.get("id", None),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "citation-verifier-mcp"}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Citation Verifier MCP Server",
        "version": "0.1.0",
        "endpoints": {"websocket": "/mcp", "sse": "/sse", "health": "/health"},
        "description": "Remote MCP server for citation verification",
    }


@app.post("/")
async def handle_root_message(request: dict):
    """Handle HTTP POST messages at root path for MCP communication."""
    return await handle_http_message(request)


def main():
    """Main entry point for the remote MCP server."""
    import os
    import uvicorn
    
    # Get configuration from environment variables (for production deployment)
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    log_level = os.getenv("LOG_LEVEL", "info")
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    uvicorn.run(
        "src.citation_verifier_mcp.websocket_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )


if __name__ == "__main__":
    main()
