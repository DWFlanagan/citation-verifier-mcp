#!/usr/bin/env python3
"""
Ultra-simple startup script for deployment
"""
import os

def main():
    """Start the citation verifier server."""
    
    # Get port from environment (Render, etc.)
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"🚀 Starting Citation Verifier MCP Server on {host}:{port}")
    
    # Start the server
    import uvicorn
    uvicorn.run(
        "src.citation_verifier_mcp.websocket_server:app",
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
