# Global MCP Server Dockerfile
# Multi-stage build for development and production deployments

# Development stage
FROM python:3.11-slim as development

LABEL maintainer="Global MCP Server Project"
LABEL description="Global MCP Server for context compression and prompt routing"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies (dev includes test dependencies)
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Copy source code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash mcpuser
RUN chown -R mcpuser:mcpuser /app
USER mcpuser

# Expose MCP server port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Development command (with hot reload)
CMD ["python", "-m", "mcp.server", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM python:3.11-slim as production

LABEL maintainer="Global MCP Server Project"
LABEL description="Global MCP Server for context compression and prompt routing (Production)"

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt ./

# Install Python dependencies (production only)
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary source files
COPY mcp/ ./mcp/
COPY config/ ./config/
COPY README.md ./

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash mcpuser
RUN chown -R mcpuser:mcpuser /app
USER mcpuser

# Expose MCP server port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command (optimized)
CMD ["python", "-m", "mcp.server", "--host", "0.0.0.0", "--port", "8000"]
