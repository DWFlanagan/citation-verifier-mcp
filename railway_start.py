#!/usr/bin/env python3
"""
Railway-specific startup script
"""
import os
import subprocess
import sys

def main():
    """Start the citation verifier server for Railway deployment."""
    
    # Set environment variables for Railway
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"🚀 Starting Citation Verifier MCP Server on {host}:{port}")
    
    # Start the server directly with uvicorn
    try:
        import uvicorn
        uvicorn.run(
            "src.citation_verifier_mcp.websocket_server:app",
            host=host,
            port=port,
            log_level="info"
        )
    except ImportError:
        print("❌ Error: uvicorn not found. Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-simple.txt"])
        import uvicorn
        uvicorn.run(
            "src.citation_verifier_mcp.websocket_server:app",
            host=host,
            port=port,
            log_level="info"
        )

if __name__ == "__main__":
    main()
