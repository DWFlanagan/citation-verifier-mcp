# Citation Verifier MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that provides citation verification capabilities to Claude and other MCP-compatible AI assistants.

This server wraps the [llm-citation-verifier](https://github.com/dwflanagan/llm-citation-verifier) library to expose citation verification as an MCP tool.

## Features

- ✅ **Verify DOI citations** against the Crossref database
- ✅ **Detect hallucinated citations** by checking if DOIs actually exist
- ✅ **Extract bibliographic metadata** (title, authors, journal, year)
- ✅ **Clean, formatted output** with clear verification status
- ✅ **No API keys required** - uses public Crossref API
- 🆕 **Remote access support** - Deploy as a web service for remote MCP clients
- 🆕 **WebSocket & HTTP endpoints** - Compatible with web-based MCP clients

## Installation

### Prerequisites

- Python 3.10+
- Claude Desktop (for local testing)

### Local Installation

```bash
# Clone the repository
git clone https://github.com/dwflanagan/citation-verifier-mcp.git
cd citation-verifier-mcp

# Initialize uv project and install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### From PyPI (when published)

```bash
pip install citation-verifier-mcp
```

## Usage

### Local MCP Server (Claude Desktop)

This is the traditional way to use the server with Claude Desktop locally.

### With Claude Desktop

1. Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "citation-verifier": {
      "command": "python",
      "args": ["-m", "citation_verifier_mcp.server"]
    }
  }
}
```

2. Restart Claude Desktop
3. The citation verification tool will be available in your conversations:

```
You: Can you verify this DOI for me: 10.1038/nature12373

Claude: I'll verify that DOI using the citation verification tool.

[Tool call: verify_citation with DOI "10.1038/nature12373"]

# ✅ Citation Verified

**DOI:** 10.1038/nature12373
**Title:** A quantum gas of deeply bound ground state molecules
**Authors:** T. Takekoshi, L. Reichsöllner, et al.
**Journal:** Nature
**Publisher:** Springer Science and Business Media LLC
**Year:** 2014
**URL:** https://doi.org/10.1038/nature12373

This DOI exists in the Crossref database and appears to be a legitimate citation.
```

### Remote MCP Server (Web Service)

🆕 **New!** You can now run the Citation Verifier as a remote web service, similar to the [Cloudflare MCP example](https://github.com/cloudflare/ai/tree/main/demos/remote-mcp-authless).

#### Quick Start

```bash
# Start the remote server
./launch_remote_server.sh

# Or manually:
uv run python start_server.py
```

The server will be available at `http://localhost:8000` with these endpoints:
- **WebSocket**: `ws://localhost:8000/mcp` (for MCP clients)
- **Health Check**: `http://localhost:8000/health`
- **API Info**: `http://localhost:8000/`

#### Connect Claude Desktop to Remote Server

1. Install the mcp-remote proxy:
   ```bash
   npm install -g mcp-remote
   ```

2. Update your Claude Desktop configuration:
   ```json
   {
     "mcpServers": {
       "citation-verifier-remote": {
         "command": "npx",
         "args": ["mcp-remote", "ws://localhost:8000/mcp"]
       }
     }
   }
   ```

3. Restart Claude Desktop

#### Deploy to Production

See [`REMOTE_SETUP.md`](./REMOTE_SETUP.md) for detailed deployment instructions including:
- Cloud deployment (Render.com)
- Simple deployment to cloud platforms
- Production configuration
- Security considerations

## Development

```bash
# Install with development dependencies (already done with uv sync)
uv sync

# Run tests
uv run pytest

# Lint code
uv run ruff check .

# Type check
uv run mypy src/

# Run the server for testing
uv run python -m citation_verifier_mcp.server
```

## Tool Reference

### `verify_citation`

Verifies a DOI citation against the Crossref database.

**Parameters:**

- `doi` (string, required): The DOI to verify. Can include URL prefixes like `https://doi.org/` which will be automatically stripped.

**Returns:**

- Formatted verification result with bibliographic metadata if verified
- Error message and recommendations if not verified

**Example DOIs to try:**

- `10.1038/nature12373` (real paper)
- `10.1234/fake.doi.2024` (fake DOI)

## How It Works

This MCP server:

1. Receives DOI verification requests from MCP clients (like Claude)
2. Uses the `llm-citation-verifier` library to query the Crossref API
3. Returns formatted results indicating whether the DOI exists and includes metadata

The underlying verification process:

- Cleans DOI input (removes URL prefixes, whitespace)
- Queries Crossref REST API
- Extracts and formats bibliographic metadata
- Provides clear verification status

## Use Cases

- **Research assistance**: Verify citations in AI-generated content
- **Academic writing**: Check DOIs before publication
- **Fact-checking**: Validate suspicious citations
- **Quality control**: Audit AI tools for citation hallucination

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Related Projects

- [llm-citation-verifier](https://github.com/your-org/llm-citation-verifier) - The core citation verification library
- [Model Context Protocol](https://modelcontextprotocol.io/) - The protocol specification
