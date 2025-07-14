# 🚀 Deployment Guide - Citation Verifier Remote MCP Server

This guide shows you exactly how to deploy your remote MCP server to production using Render.com.

## 🎯 Quick Deploy - Render.com (Recommended)

Render.com provides excellent support for Python applications and is very easy to use.

### Prerequisites

- GitHub account with this repository
- Render.com account (free signup at [render.com](https://render.com))

### Deployment Steps

1. **Connect to GitHub:**
   - Go to [render.com](https://render.com) and sign up/login
   - Connect your GitHub account
   - Grant Render access to your repositories

2. **Create Web Service:**
   - Click "New +" → "Web Service"
   - Choose "Build and deploy from a Git repository"
   - Select your `citation-verifier-mcp` repository
   - Click "Connect"

3. **Configure Settings:**
   - **Name**: `citation-verifier-mcp` (or your preferred name)
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python simple_start.py`
   - **Plan**: Select "Free" (perfect for testing)

4. **Deploy:**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application
   - Wait for deployment to complete (usually 2-3 minutes)
   - You'll get a URL like: `https://citation-verifier-mcp.onrender.com`

## ✅ Testing Your Deployment

### 1. Health Check

Test that your server is running:

```bash
curl https://your-app-name.onrender.com/health
```

Expected response:

```json
{"status": "healthy", "service": "citation-verifier-mcp"}
```

### 2. MCP Protocol Test

Test the MCP endpoints:

```bash
# Test initialization
curl -X POST https://your-app-name.onrender.com/ \
  -H "Content-Type: application/json" \
  -d '{"method": "initialize", "id": 1}'

# Test tools list
curl -X POST https://your-app-name.onrender.com/ \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list", "id": 2}'
```

### 3. Using MCP Inspector

Test with the official MCP inspector:

```bash
npx @modelcontextprotocol/inspector https://your-app-name.onrender.com
```

## 🔧 Connecting to Claude Desktop

Once deployed, you can connect Claude Desktop to your remote server:

### Option 1: Using mcp-remote (Current Working Method)

Add to your `claude_desktop_config.json`:

```json
{
    "mcpServers": {
        "citation-verifier-mcp": {
            "command": "npx",
            "args": [
                "-y",
                "mcp-remote",
                "https://your-app-name.onrender.com"
            ]
        }
    }
}
```

### Option 2: Claude.ai Integrations (Alternative)

1. Go to [Claude.ai Settings > Integrations](https://claude.ai/settings/integrations)
2. Add your server URL: `https://your-app-name.onrender.com`

## 🔄 Updates and Redeployment

Render automatically redeploys when you push to GitHub:

```bash
# Make your changes
git add .
git commit -m "Update server"
git push origin main
```

Render will automatically detect the push and redeploy your service.

## 📊 Monitoring

- **Render Dashboard**: Monitor logs, metrics, and deployments at [dashboard.render.com](https://dashboard.render.com)
- **Health Endpoint**: `https://your-app-name.onrender.com/health`
- **Logs**: Available in real-time through the Render dashboard

## 💡 Tips

- **Free Tier**: Render's free tier is perfect for testing and personal use
- **Custom Domain**: You can add a custom domain in the Render dashboard
- **Environment Variables**: Add any needed environment variables in the Render dashboard
- **Automatic HTTPS**: Render provides free SSL certificates automatically

## 🆘 Troubleshooting

### Common Issues

1. **Build Fails**: Check that `requirements.txt` is properly formatted
