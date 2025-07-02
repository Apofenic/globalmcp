"""
Main module for running the Global MCP Server
"""
import asyncio
import argparse
import uvicorn
import logging
from pathlib import Path

def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main entry point for the MCP server"""
    parser = argparse.ArgumentParser(description="Global MCP Server")
    parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to bind the server to"
    )
    parser.add_argument(
        "--log-level", 
        default="INFO", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level"
    )
    parser.add_argument(
        "--config-path",
        help="Path to configuration directory"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Set configuration path if provided
    if args.config_path:
        import os
        os.environ["MCP_CONFIG_PATH"] = args.config_path
    
    # Run the server
    uvicorn.run(
        "mcp.server:app",
        host=args.host,
        port=args.port,
        reload=False,
        log_level=args.log_level.lower()
    )

if __name__ == "__main__":
    main()
