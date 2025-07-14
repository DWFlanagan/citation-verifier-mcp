# Remote Citation Verifier MCP Server

This document explains how to deploy and use your Citation Verifier MCP Server as a remote service, similar to the Cloudflare example you referenced.

## What's New: Remote Access

Your MCP server now supports **remote access** through HTTP endpoints, allowing it to be used by:

- Claude Desktop (via `mcp-remote` proxy)
- Web-based MCP clients
- Any application that supports MCP over WebSocket or HTTP

## Architecture

The remote server exposes several endpoints:

- **`/mcp`** - WebSocket endpoint for real-time MCP communication
- **`/sse`** - Server-Sent Events endpoint (basic implementation)
- **`/health`** - Health check endpoint
- **`/`** - API information endpoint

## Quick Start

### 1. Start the Remote Server

Using uv (recommended):

```bash
# Navigate to your project directory
cd /path/to/citation-verifier-mcp

# Start the server
uv run python start_server.py
```

Or using the console script:

```bash
uv run citation-verifier-remote
```

The server will start on `http://localhost:8000` by default.

### 2. Test the Server

Visit `http://localhost:8000` in your browser to see the API information.

Check health: `http://localhost:8000/health`

## Connecting Claude Desktop

To connect Claude Desktop to your remote MCP server:

### Option 1: Using mcp-remote (Recommended)

1. Install the mcp-remote proxy:

   ```bash
   npm install -g mcp-remote
   ```

2. Update your Claude Desktop configuration (`claude_desktop_config.json`):

   ```json
   {
     "mcpServers": {
       "citation-verifier-remote": {
         "command": "npx",
         "args": [
           "mcp-remote",
           "ws://localhost:8000/mcp"
         ]
       }
     }
   }
   ```

3. Restart Claude Desktop

### Option 2: Direct WebSocket (Advanced)

For applications that support WebSocket directly, connect to: `ws://localhost:8000/mcp`

## Deployment Options

### Local Development

- Run locally as shown above
- Access via `http://localhost:8000`

### Cloud Deployment

#### Render.com (Recommended)

1. Connect your GitHub repository to Render.com
2. Create a new Web Service
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python simple_start.py`
4. Deploy automatically on git push

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.
echo "web: uv run citation-verifier-remote --host 0.0.0.0 --port \$PORT" > Procfile

## Deploy

```bash
heroku create your-citation-verifier
git push heroku main
```

### DigitalOcean App Platform

1. Connect your GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set run command: `python simple_start.py`

## Configuration

### Environment Variables

- `HOST` - Server host (default: "0.0.0.0")
- `PORT` - Server port (default: 8000)
- `LOG_LEVEL` - Logging level (default: "info")

### Production Considerations

1. **CORS**: Update CORS origins in production:

   ```python
   # In websocket_server.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],  # Restrict origins
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **HTTPS**: Use a reverse proxy (nginx, Cloudflare) for HTTPS
3. **Rate Limiting**: Add rate limiting middleware
4. **Monitoring**: Add health checks and logging

## API Endpoints

### GET /

Returns server information and available endpoints.

### GET /health

Health check endpoint returning server status.

### WebSocket /mcp

Main MCP communication endpoint. Supports:

- `initialize` - Initialize MCP session
- `tools/list` - List available tools
- `tools/call` - Call citation verification tool

### GET /sse

Server-Sent Events endpoint (basic implementation).

## Usage Examples

### Testing with curl

```bash
# Check server health
curl http://localhost:8000/health

# Get server info
curl http://localhost:8000/
```

### WebSocket Test (using wscat)

```bash
# Install wscat
npm install -g wscat

# Connect to WebSocket
wscat -c ws://localhost:8000/mcp

# Send initialize message
{"id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}}}

# List tools
{"id": 2, "method": "tools/list", "params": {}}

# Call citation verification
{"id": 3, "method": "tools/call", "params": {"name": "verify_citation", "arguments": {"doi": "10.1038/nature12373"}}}
```

## Differences from Cloudflare Example

| Feature | Cloudflare Example | Your Implementation |
|---------|-------------------|-------------------|
| Runtime | Cloudflare Workers (Edge) | Python/FastAPI |
| Language | TypeScript | Python |
| Deployment | Cloudflare Workers | Any Python host |
| Protocol | SSE + HTTP | WebSocket + SSE |
| Cost | Pay-per-request | Fixed hosting cost |

## Troubleshooting

### Server Won't Start

- Check if port 8000 is already in use: `lsof -i :8000`
- Try a different port: `uv run citation-verifier-remote --port 8001`

### Claude Desktop Can't Connect

- Ensure the server is running: `curl http://localhost:8000/health`
- Check Claude Desktop logs for connection errors
- Verify `mcp-remote` is installed: `npm list -g mcp-remote`

### WebSocket Connection Issues

- Test WebSocket connection with wscat
- Check firewall settings
- Ensure proper CORS configuration

## Next Steps

1. **Deploy to Production**: Choose a cloud provider and deploy
2. **Add Authentication**: Implement API key authentication
3. **Add Rate Limiting**: Prevent abuse with rate limiting
4. **Monitor Usage**: Add logging and metrics
5. **Scale**: Use load balancers for high availability

## Support

For issues specific to the remote server implementation, check:

- Server logs: The FastAPI server provides detailed logging
- Health endpoint: `GET /health` shows server status
- Original MCP server: Your stdio-based server in `server.py` still works locally
