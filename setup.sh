#!/bin/bash
# setup.sh - Quick setup script for citation-verifier-mcp

set -e

echo "🚀 Setting up Citation Verifier MCP Server..."

# Initialize uv project
echo "📦 Initializing uv project..."
uv init --package

# Add dependencies
echo "📋 Adding dependencies..."
uv add mcp llm-citation-verifier

# Add dev dependencies  
echo "🔧 Adding dev dependencies..."
uv add --dev pytest pytest-asyncio mypy ruff

# Create source structure
echo "📁 Creating source structure..."
mkdir -p src/citation_verifier_mcp tests

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Create the source files from the artifacts"
echo "2. Test with: uv run python -m citation_verifier_mcp.server"
echo "3. Add to Claude Desktop config"