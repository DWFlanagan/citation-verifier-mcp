#!/bin/bash

# Citation Verifier Remote MCP Server Launcher
# This script makes it easy to start your remote MCP server

echo "🚀 Starting Citation Verifier Remote MCP Server..."
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed or not in PATH"
    echo "   Please install uv: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found"
    echo "   Please run this script from the citation-verifier-mcp directory"
    exit 1
fi

# Set default values
HOST=${HOST:-"0.0.0.0"}
PORT=${PORT:-8000}
LOG_LEVEL=${LOG_LEVEL:-"info"}

echo "📋 Configuration:"
echo "   Host: $HOST"
echo "   Port: $PORT"
echo "   Log Level: $LOG_LEVEL"
echo ""

echo "🔧 Installing/updating dependencies..."
uv sync --all-extras

echo ""
echo "✅ Starting server..."
echo "   Access the server at: http://localhost:$PORT"
echo "   Health check: http://localhost:$PORT/health"
echo "   API info: http://localhost:$PORT/"
echo ""
echo "💡 For Claude Desktop:"
echo "   1. Install mcp-remote: npm install -g mcp-remote"
echo "   2. Add to claude_desktop_config.json:"
echo '   {
     "mcpServers": {
       "citation-verifier-remote": {
         "command": "npx",
         "args": ["mcp-remote", "ws://localhost:'$PORT'/mcp"]
       }
     }
   }'
echo ""
echo "Press Ctrl+C to stop the server"
echo "----------------------------------------"

# Start the server
uv run python start_server.py
