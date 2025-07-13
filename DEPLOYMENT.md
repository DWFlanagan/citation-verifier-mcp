# 🚀 Deployment Guide - Citation Verifier Remote MCP Server

This guide shows you exactly how to deploy your remote MCP server to production.

## 🎯 Quick Deploy Options

### Option 1: Railway (Recommended - 1 minute setup)

Railway is the easiest way to deploy Python apps with `uv`:

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Deploy from your current directory
railway init
railway up
```

**That's it!** Railway will:
- Auto-detect your Python project
- Install dependencies with `uv`
- Run your server using the `Procfile`
- Give you a public URL like `https://your-app.up.railway.app`

### Option 2: Render (Also very easy)

1. Go to [render.com](https://render.com)
2. Connect your GitHub repository
3. Create a new "Web Service"
4. Set these settings:
   - **Build Command**: `uv sync --frozen --no-dev --all-extras`
   - **Start Command**: `uv run citation-verifier-remote`
   - **Python Version**: 3.11

### Option 3: Fly.io (Great performance)

```bash
# 1. Install Fly CLI
curl -L https://fly.io/install.sh | sh

# 2. Login and create app
fly auth login
fly launch

# 3. Deploy
fly deploy
```

## 🐳 Docker Deployment

### Local Docker Testing

```bash
# Build the image
docker build -t citation-verifier-mcp .

# Run locally
docker run -p 8000:8000 citation-verifier-mcp

# Or use docker-compose
docker-compose up
```

### Deploy to any Docker host

The included `Dockerfile` works on:
- **DigitalOcean App Platform**
- **Google Cloud Run**
- **AWS ECS/Fargate**
- **Azure Container Instances**
- Any VPS with Docker

## ⚡ Platform-Specific Instructions

### Railway Deployment (Detailed)

1. **Prepare your repo:**
   ```bash
   git add .
   git commit -m "Add remote MCP server"
   git push origin main
   ```

2. **Deploy to Railway:**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login
   railway login
   
   # Initialize project
   railway init
   
   # Deploy
   railway up
   ```

3. **Get your URL:**
   Railway will give you a URL like: `https://citation-verifier-mcp-production.up.railway.app`

### Heroku Deployment

```bash
# 1. Install Heroku CLI and login
heroku login

# 2. Create Heroku app
heroku create your-citation-verifier

# 3. Deploy
git push heroku main

# 4. Scale up
heroku ps:scale web=1
```

### DigitalOcean App Platform

1. Go to [DigitalOcean Apps](https://cloud.digitalocean.com/apps)
2. Create new app from GitHub
3. Configure:
   - **Build Command**: `uv sync --frozen --no-dev --all-extras`
   - **Run Command**: `uv run citation-verifier-remote`
   - **HTTP Port**: 8000

### Google Cloud Run

```bash
# 1. Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/citation-verifier

# 2. Deploy to Cloud Run
gcloud run deploy citation-verifier \
  --image gcr.io/YOUR_PROJECT_ID/citation-verifier \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🔧 Configuration for Production

### Environment Variables

Set these in your deployment platform:

- `HOST=0.0.0.0` (already set in code)
- `PORT=8000` (or let platform set it)
- `LOG_LEVEL=info`
- `RELOAD=false` (for production)

### CORS Configuration

For production, update the CORS settings in `websocket_server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Replace with your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🌐 After Deployment

### 1. Test Your Deployed Server

```bash
# Replace with your actual deployed URL
curl https://your-app.up.railway.app/health

# Should return: {"status": "healthy", "service": "citation-verifier-mcp"}
```

### 2. Update Claude Desktop Configuration

```json
{
  "mcpServers": {
    "citation-verifier-remote": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "wss://your-app.up.railway.app/mcp"
      ]
    }
  }
}
```

**Note**: Use `wss://` (WebSocket Secure) for HTTPS deployments.

### 3. Share with Others

Your deployed server can be used by anyone! Just share the WebSocket URL:
`wss://your-app.up.railway.app/mcp`

## 💰 Cost Estimates

| Platform | Free Tier | Paid Plans |
|----------|-----------|------------|
| Railway | $5/month credit | $5/month + usage |
| Render | 750 hours/month | $7/month |
| Fly.io | 3 shared-cpu apps | $1.94/month + usage |
| Heroku | Limited hours | $7/month |
| DigitalOcean | N/A | $12/month |

## 🚨 Troubleshooting

### Common Issues

1. **Build Fails**: Ensure `uv.lock` is committed to git
2. **Port Binding**: Make sure you're using `HOST=0.0.0.0`
3. **WebSocket Errors**: Check that the platform supports WebSockets
4. **CORS Issues**: Update allowed origins in production

### Debug Commands

```bash
# Check logs (Railway)
railway logs

# Check logs (Heroku)
heroku logs --tail

# Test WebSocket connection
wscat -c wss://your-deployed-url.com/mcp
```

## 🎉 Success!

Once deployed, your citation verifier will be available to anyone with the URL. They can use it in:

- Claude Desktop (via mcp-remote)
- Custom MCP clients
- Web applications
- Other AI tools that support MCP

Your academic citation verification tool is now accessible worldwide! 🌍
