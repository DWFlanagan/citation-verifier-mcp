#!/usr/bin/env python3
"""
Ultra-simple startup script for Railway deployment
"""
import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    """Start the citation verifier server."""
    
    # Get port from Railway
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"🚀 Starting Citation Verifier MCP Server on {host}:{port}")
    
    # Install required packages
    packages = [
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0", 
        "websockets>=12.0",
        "python-multipart>=0.0.6",
        "llm-citation-verifier>=0.1.1",
        "mcp>=1.0.0"
    ]
    
    print("📦 Installing dependencies...")
    for package in packages:
        try:
            print(f"   Installing {package}...")
            install_package(package)
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to install {package}: {e}")
    
    print("✅ Dependencies installed!")
    
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
