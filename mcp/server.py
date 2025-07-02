"""
Global MCP Server - Main entry point for the MCP toolchain
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import json
import logging
from pathlib import Path

from .services.freqkv_service import FreqKVService
from .services.lococo_service import LoCoCoService
from .services.routing_service import RoutingService
from .utils.config_loader import ConfigLoader
from .utils.model_registry import ModelRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Global MCP Server",
    description="MCP server with KV compression and intelligent routing",
    version="1.0.0"
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class MCPRequest(BaseModel):
    method: str
    params: Dict[str, Any]
    id: Optional[str] = None

class MCPResponse(BaseModel):
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None

class KVCompressionRequest(BaseModel):
    kv_cache: List[List[float]]
    sink_tokens: int = 10
    compression_ratio: float = 0.5

class PromptRoutingRequest(BaseModel):
    prompt: str
    context: Optional[str] = None
    max_tokens: Optional[int] = None

# Global services
freqkv_service = FreqKVService()
lococo_service = LoCoCoService()
routing_service = RoutingService()
config_loader = ConfigLoader()
model_registry = ModelRegistry()

@app.on_event("startup")
async def startup_event():
    """Initialize services and load configurations"""
    logger.info("Starting Global MCP Server...")
    
    # Load MCP configurations
    try:
        await config_loader.load_configs()
        await model_registry.initialize()
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "services": ["freqkv", "lococo", "routing"]}

@app.post("/mcp", response_model=MCPResponse)
async def handle_mcp_request(request: MCPRequest):
    """Main MCP request handler"""
    try:
        method = request.method
        params = request.params
        
        if method == "tools/list":
            return MCPResponse(
                result={"tools": await get_available_tools()},
                id=request.id
            )
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            result = await call_tool(tool_name, tool_args)
            return MCPResponse(result=result, id=request.id)
        else:
            return MCPResponse(
                error={"code": -32601, "message": f"Unknown method: {method}"},
                id=request.id
            )
    except Exception as e:
        logger.error(f"Error handling MCP request: {e}")
        return MCPResponse(
            error={"code": -32603, "message": str(e)},
            id=request.id
        )

async def get_available_tools() -> List[Dict[str, Any]]:
    """Get list of available MCP tools"""
    return [
        {
            "name": "compress_kv_cache",
            "description": "Compress KV cache using FreqKV and LoCoCo algorithms",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "kv_cache": {
                        "type": "array",
                        "description": "KV cache as nested arrays"
                    },
                    "sink_tokens": {
                        "type": "integer",
                        "description": "Number of sink tokens to preserve",
                        "default": 10
                    },
                    "compression_ratio": {
                        "type": "number",
                        "description": "Target compression ratio",
                        "default": 0.5
                    }
                },
                "required": ["kv_cache"]
            }
        },
        {
            "name": "route_prompt",
            "description": "Route prompt to appropriate model based on complexity",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The prompt to route"
                    },
                    "context": {
                        "type": "string",
                        "description": "Additional context"
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Maximum tokens for response"
                    }
                },
                "required": ["prompt"]
            }
        },
        {
            "name": "process_full_pipeline",
            "description": "Process prompt through full compression and routing pipeline",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The prompt to process"
                    },
                    "kv_cache": {
                        "type": "array",
                        "description": "Optional KV cache to compress"
                    },
                    "context": {
                        "type": "string",
                        "description": "Additional context"
                    }
                },
                "required": ["prompt"]
            }
        }
    ]

async def call_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Call the specified tool with given arguments"""
    if tool_name == "compress_kv_cache":
        return await compress_kv_cache(args)
    elif tool_name == "route_prompt":
        return await route_prompt(args)
    elif tool_name == "process_full_pipeline":
        return await process_full_pipeline(args)
    else:
        raise HTTPException(status_code=404, message=f"Tool not found: {tool_name}")

async def compress_kv_cache(args: Dict[str, Any]) -> Dict[str, Any]:
    """Compress KV cache using FreqKV and LoCoCo"""
    kv_cache = args["kv_cache"]
    sink_tokens = args.get("sink_tokens", 10)
    compression_ratio = args.get("compression_ratio", 0.5)
    
    # Apply FreqKV compression
    freq_compressed = await freqkv_service.compress(
        kv_cache, sink_tokens=sink_tokens
    )
    
    # Apply LoCoCo fusion
    final_compressed = await lococo_service.fuse(
        freq_compressed, target_ratio=compression_ratio
    )
    
    return {
        "compressed_kv": final_compressed,
        "original_size": len(kv_cache),
        "compressed_size": len(final_compressed),
        "compression_ratio": len(final_compressed) / len(kv_cache)
    }

async def route_prompt(args: Dict[str, Any]) -> Dict[str, Any]:
    """Route prompt to appropriate model"""
    prompt = args["prompt"]
    context = args.get("context", "")
    max_tokens = args.get("max_tokens")
    
    # Classify prompt complexity
    complexity = await routing_service.classify_complexity(prompt, context)
    
    # Get model for complexity level
    model_endpoint = model_registry.get_model_for_complexity(complexity)
    
    # Generate response using selected model
    response = await routing_service.generate_response(
        prompt, model_endpoint, context=context, max_tokens=max_tokens
    )
    
    return {
        "response": response,
        "complexity": complexity,
        "model_used": model_endpoint,
        "routing_decision": {
            "reasoning": f"Classified as {complexity} complexity",
            "model_endpoint": model_endpoint
        }
    }

async def process_full_pipeline(args: Dict[str, Any]) -> Dict[str, Any]:
    """Process through full compression and routing pipeline"""
    prompt = args["prompt"]
    kv_cache = args.get("kv_cache")
    context = args.get("context", "")
    
    result = {"prompt": prompt}
    
    # Compress KV cache if provided
    if kv_cache:
        compression_result = await compress_kv_cache({
            "kv_cache": kv_cache,
            "sink_tokens": 10,
            "compression_ratio": 0.5
        })
        result["compression"] = compression_result
        
        # Use compressed context for routing
        context = f"{context}\n[Compressed KV context available]"
    
    # Route prompt
    routing_result = await route_prompt({
        "prompt": prompt,
        "context": context
    })
    result["routing"] = routing_result
    
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
