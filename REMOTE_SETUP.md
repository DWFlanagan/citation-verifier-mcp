# Citation Verifier MCP Server - Render.com Deployment

This guide explains how to deploy the Citation Verifier MCP Server on Render.com, making it accessible remotely for use with Claude Desktop and other MCP clients.

## What You'll Deploy

The MCP server will be hosted on Render.com and accessible via:

- **WebSocket endpoint**: `wss://your-app.onrender.com/mcp` - for real-time MCP communication
- **Health check**: `https://your-app.onrender.com/health` - for monitoring
- **API info**: `https://your-app.onrender.com/` - service information

## Prerequisites

- GitHub repository with the Citation Verifier MCP code
- Render.com account (free tier available)
- `uv` package manager configured in the project

## Deployment Steps

### 1. Prepare Your Repository

Ensure the repository has these files:

- `pyproject.toml` - Python dependencies and project configuration
- `uv.lock` - Lock file for reproducible builds
- `simple_start.py` or `start_server.py` - Server entry point

### 2. Create Web Service on Render.com

1. **Sign in** to [Render.com](https://render.com)
2. **Click "New +"** and select "Web Service"
3. **Connect the GitHub repository**
4. **Configure the service**:

   | Setting | Value |
   |---------|-------|
   | **Name** | `citation-verifier-mcp` (or preferred name) |
   | **Environment** | `Python 3` |
   | **Build Command** | `uv sync --no-dev` |
   | **Start Command** | `uv run python simple_start.py` |
   | **Instance Type** | `Free` (or paid for production) |

### 3. Environment Variables (Optional)

Configure these environment variables in Render's dashboard if needed:

| Variable | Value | Description |
|----------|-------|-------------|
| `HOST` | `0.0.0.0` | Server host (default) |
| `PORT` | `$PORT` | Port (Render sets this automatically) |
| `LOG_LEVEL` | `info` | Logging level |

### 4. Deploy

1. **Click "Create Web Service"**
2. **Wait for deployment** (usually 2-5 minutes)
3. **Note the service URL**: `https://your-app-name.onrender.com`

## Connecting Claude Desktop

Once deployed, connect Claude Desktop to the remote MCP server:

### Install mcp-remote

```bash
npm install -g mcp-remote
```

### Update Claude Desktop Configuration

Edit the `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "citation-verifier-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://citation-verifier-mcp.onrender.com"
      ]
    }
  }
}
```

**Replace `citation-verifier-mcp.onrender.com` with the actual Render service URL.**

### Restart Claude Desktop

Restart Claude Desktop to load the new configuration.

## Testing Your Deployment

### Health Check

Visit the service URL in a browser:

```text
https://your-app-name.onrender.com/health
```

Should return:

```json
{"status": "healthy", "service": "Citation Verifier MCP Server"}
```

### WebSocket Test

Use `wscat` to test the WebSocket connection:

```bash
# Install wscat
npm install -g wscat

# Connect to the deployed service
wscat -c wss://your-app-name.onrender.com/mcp

# Test initialize message
{"id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}}}
```

## Render.com Specifics

### Free Tier Limitations

- **Spins down after 15 minutes** of inactivity
- **Cold start time** of 10-30 seconds when waking up
- **750 hours per month** limit

### Production Considerations

For production use, consider upgrading to a paid plan for:

- **Always-on service** (no sleeping)
- **Faster builds**
- **Custom domains**
- **Higher resource limits**

### Automatic Deployments

Render automatically deploys when you push to the connected Git branch:

1. **Push changes** to the repository
2. **Render detects changes** and starts a new build
3. **Automatic deployment** with zero downtime

## Troubleshooting

### Deployment Fails

1. **Check build logs** in Render dashboard
2. **Verify `uv.lock`** is committed to the repository
3. **Ensure `simple_start.py`** exists and is executable

### Service Won't Start

1. **Check application logs** in Render dashboard
2. **Verify start command** uses correct entry point
3. **Check environment variables** if using custom configuration

### Claude Desktop Can't Connect

1. **Test health endpoint** manually in browser
2. **Verify WebSocket URL** uses `wss://` (not `ws://`)
3. **Check service status** in Render dashboard
4. **Wait for cold start** if service was sleeping (free tier)

### Connection Timeouts

Free tier services sleep after 15 minutes of inactivity:

- **First request** may take 10-30 seconds (cold start)
- **Subsequent requests** are fast
- **Consider paid tier** for always-on service

## Monitoring

### Render Dashboard

Monitor the service via Render's dashboard:

- **Deployment status**
- **Application logs**
- **Resource usage**
- **Build history**

### Health Endpoint

Set up external monitoring of the health endpoint:

```text
https://your-app-name.onrender.com/health
```

## Cost

### Free Tier

- **$0/month**
- **750 hours** of usage
- **Sleeps after 15 minutes** of inactivity

### Starter Plan

- **$7/month**
- **Always-on service**
- **Custom domains**
- **Better performance**

## Next Steps

1. **Test with Claude Desktop** to verify everything works
2. **Monitor logs** during initial usage
3. **Consider upgrading** to paid tier for production use
4. **Set up monitoring** for the health endpoint
5. **Add authentication** if needed for production

## Support

For deployment issues:

- **Render logs**: Check the dashboard for build and runtime logs
- **GitHub repository**: Ensure all files are committed
- **Health endpoint**: Test manually to verify service is running
