# Dockerfile for Citation Verifier MCP Server

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies using pip (more reliable in Docker)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Set environment variables for production
ENV HOST=0.0.0.0
ENV PORT=8000
ENV LOG_LEVEL=info
ENV RELOAD=false

# Run the server using the railway startup script
CMD ["python", "railway_start.py"]
