#!/usr/bin/env python3
"""
Startup script for the Citation Verifier Remote MCP Server
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.citation_verifier_mcp.websocket_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
