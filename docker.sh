#!/bin/bash
# Docker helper script for Global MCP Server
# Provides convenient commands for Docker operations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Functions
show_help() {
    echo "Global MCP Server Docker Helper"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev             Start development environment"
    echo "  prod            Start production environment"
    echo "  build           Build development image"
    echo "  build-prod      Build production image"
    echo "  stop            Stop all containers"
    echo "  clean           Stop and remove containers, networks, and volumes"
    echo "  logs            Show logs from all services"
    echo "  shell           Open shell in running container"
    echo "  test            Run tests in container"
    echo "  health          Check container health"
    echo "  help            Show this help message"
    echo ""
}

start_dev() {
    log_info "Starting development environment..."
    docker compose up -d
    log_success "Development environment started!"
    log_info "MCP Server: http://localhost:8000"
    log_info "Ollama API: http://localhost:11434"
    log_info "View logs: $0 logs"
}

start_prod() {
    log_info "Starting production environment..."
    docker compose -f docker-compose.prod.yml up -d
    log_success "Production environment started!"
    log_info "MCP Server: http://localhost:8000"
    log_info "Ollama API: http://localhost:11434"
}

build_dev() {
    log_info "Building development image..."
    docker compose build --no-cache
    log_success "Development image built!"
}

build_prod() {
    log_info "Building production image..."
    docker compose -f docker-compose.prod.yml build --no-cache
    log_success "Production image built!"
}

stop_containers() {
    log_info "Stopping containers..."
    docker compose down 2>/dev/null || true
    docker compose -f docker-compose.prod.yml down 2>/dev/null || true
    log_success "Containers stopped!"
}

clean_all() {
    log_warning "This will remove all containers, networks, and volumes!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up..."
        docker compose down -v --remove-orphans 2>/dev/null || true
        docker compose -f docker-compose.prod.yml down -v --remove-orphans 2>/dev/null || true
        docker system prune -f
        log_success "Cleanup complete!"
    else
        log_info "Cleanup cancelled."
    fi
}

show_logs() {
    log_info "Showing logs (press Ctrl+C to exit)..."
    if docker compose ps -q > /dev/null 2>&1; then
        docker compose logs -f
    elif docker compose -f docker-compose.prod.yml ps -q > /dev/null 2>&1; then
        docker compose -f docker-compose.prod.yml logs -f
    else
        log_error "No running containers found!"
        exit 1
    fi
}

open_shell() {
    log_info "Opening shell in MCP server container..."
    CONTAINER=$(docker ps --filter "name=globalmcp-server" --format "{{.Names}}" | head -1)
    if [ -z "$CONTAINER" ]; then
        log_error "No running MCP server container found!"
        exit 1
    fi
    docker exec -it "$CONTAINER" /bin/bash
}

run_tests() {
    log_info "Running tests in container..."
    docker compose exec globalmcp python -m pytest mcp/tests/ -v
}

check_health() {
    log_info "Checking container health..."
    
    # Check MCP server
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "MCP Server is healthy"
    else
        log_error "MCP Server is not responding"
    fi
    
    # Check Ollama
    if curl -f http://localhost:11434/api/tags > /dev/null 2>&1; then
        log_success "Ollama is healthy"
    else
        log_error "Ollama is not responding"
    fi
    
    # Show container status
    echo ""
    log_info "Container status:"
    docker ps --filter "name=globalmcp" --filter "name=ollama" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

# Main script logic
case "${1:-help}" in
    dev)
        start_dev
        ;;
    prod)
        start_prod
        ;;
    build)
        build_dev
        ;;
    build-prod)
        build_prod
        ;;
    stop)
        stop_containers
        ;;
    clean)
        clean_all
        ;;
    logs)
        show_logs
        ;;
    shell)
        open_shell
        ;;
    test)
        run_tests
        ;;
    health)
        check_health
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
