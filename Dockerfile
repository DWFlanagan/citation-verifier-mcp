# Dockerfile for Citation Verifier MCP Server

FROM python:3.11-slim

# Install uv - the fast Python package installer
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev --all-extras

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Set environment variables for production
ENV HOST=0.0.0.0
ENV PORT=8000
ENV LOG_LEVEL=info
ENV RELOAD=false

# Run the server
CMD ["uv", "run", "citation-verifier-remote"]
