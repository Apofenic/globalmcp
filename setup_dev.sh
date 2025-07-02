#!/bin/bash
# Development setup script

echo "Setting up Global MCP Server development environment..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create necessary directories
mkdir -p logs
mkdir -p data/cache

echo "Setup complete!"
echo "To start the server:"
echo "  source venv/bin/activate"
echo "  python -m mcp.server"
