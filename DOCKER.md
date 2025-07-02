# Docker Setup Guide for Global MCP Server

This guide covers how to run the Global MCP Server using Docker containers for both development and production environments.

## Quick Start

### Development Environment

```bash
# Start development environment with hot reload
./docker.sh dev

# Or manually:
docker-compose up -d
```

### Production Environment

```bash
# Start production environment
./docker.sh prod

# Or manually:
docker-compose -f docker-compose.prod.yml up -d
```

## Docker Helper Script

The `docker.sh` script provides convenient commands for common Docker operations:

```bash
./docker.sh help          # Show all available commands
./docker.sh dev            # Start development environment
./docker.sh prod           # Start production environment
./docker.sh build          # Build development image
./docker.sh build-prod     # Build production image
./docker.sh stop           # Stop all containers
./docker.sh clean          # Clean up containers, networks, volumes
./docker.sh logs           # Show logs from all services
./docker.sh shell          # Open shell in running container
./docker.sh test           # Run tests in container
./docker.sh health         # Check container health
```

## Container Architecture

### Services

1. **globalmcp**: Main MCP server with FastAPI
   - Handles FreqKV compression, LoCoCo fusion, and prompt routing
   - Exposes port 8000
   - Health check: `http://localhost:8000/health`

2. **ollama**: Local LLM inference server
   - Provides model inference for prompt routing
   - Exposes port 11434
   - Health check: `http://localhost:11434/api/tags`

3. **nginx** (production only): Reverse proxy for SSL/TLS termination

### Volumes

- **ollama_data**: Persists Ollama models between container restarts
- **globalmcp_logs**: Stores application logs (production only)
- **Source code**: Mounted for hot reload (development only)

## Environment-Specific Configurations

### Development (`docker-compose.yml`)

- **Hot Reload**: Source code mounted as volume for live editing
- **Debug Mode**: Full logging and development dependencies
- **Resource Limits**: Moderate (1GB memory, 0.5 CPU)
- **Security**: Relaxed for development convenience

### Production (`docker-compose.prod.yml`)

- **Optimized Build**: Multi-stage build excluding dev dependencies
- **Security Hardened**: Read-only filesystem, non-root user, dropped capabilities
- **Resource Limits**: Higher (2GB memory, 1.0 CPU)
- **Health Checks**: Comprehensive monitoring
- **Logging**: Structured logging with external volume

## Building Images

### Development Image

```bash
docker build --target development -t globalmcp:dev .
```

### Production Image

```bash
docker build --target production -t globalmcp:prod .
```

## Health Monitoring

The containers include comprehensive health checks:

```bash
# Check all services
./docker.sh health

# Manual health checks
curl http://localhost:8000/health    # MCP Server
curl http://localhost:11434/api/tags # Ollama
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8000 and 11434 are available
2. **Memory issues**: Increase Docker memory limits in Docker Desktop
3. **Permission issues**: Run with `sudo` on Linux if needed
4. **Model downloads**: First Ollama startup may take time to download models

### Debugging

```bash
# View logs
./docker.sh logs

# Open shell in container
./docker.sh shell

# Check container status
docker ps

# Inspect specific service
docker-compose logs globalmcp
docker-compose logs ollama
```

### Performance Tuning

1. **Memory**: Adjust container memory limits in compose files
2. **CPU**: Modify CPU limits based on your hardware
3. **GPU**: Uncomment GPU support in docker-compose.yml for NVIDIA GPUs
4. **Caching**: Enable Redis service for improved performance

## Security Considerations

### Production Security

- Containers run as non-root user
- Read-only filesystem enabled
- Unnecessary capabilities dropped
- Secret management via environment variables
- Network isolation with custom bridge network

### SSL/TLS (Production)

To enable HTTPS in production:

1. Add SSL certificates to `./ssl/` directory
2. Configure `nginx.conf` for SSL termination
3. Update docker-compose.prod.yml nginx service

## Scaling and Orchestration

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml globalmcp
```

### Kubernetes

Convert Docker Compose to Kubernetes manifests:

```bash
# Using kompose
kompose convert -f docker-compose.prod.yml
```

## Development Workflow

1. **Setup**: `./docker.sh dev`
2. **Code**: Edit source files (automatically reloaded)
3. **Test**: `./docker.sh test`
4. **Debug**: `./docker.sh logs` or `./docker.sh shell`
5. **Cleanup**: `./docker.sh clean`

## Production Deployment

1. **Build**: `./docker.sh build-prod`
2. **Deploy**: `./docker.sh prod`
3. **Monitor**: `./docker.sh health`
4. **Scale**: Use Docker Swarm or Kubernetes
5. **Update**: Rolling updates with zero downtime

## Integration with VS Code

The Docker setup integrates with VS Code MCP configuration:

```json
{
  "globalmcp-docker": {
    "command": "docker",
    "args": [
      "exec", "-i", "globalmcp-server",
      "python", "-m", "mcp.server"
    ]
  }
}
```

This allows VS Code to communicate with the containerized MCP server while maintaining development flexibility.
