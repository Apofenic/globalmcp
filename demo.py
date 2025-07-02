#!/usr/bin/env python3
"""
Demo script for Global MCP Server
"""
import asyncio
import json
import numpy as np
from pathlib import Path

# Add the project root to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from mcp.services.freqkv_service import FreqKVService
from mcp.services.lococo_service import LoCoCoService
from mcp.services.routing_service import RoutingService
from mcp.utils.model_registry import ModelRegistry

async def demo_compression():
    """Demo KV cache compression pipeline"""
    print("=== KV Cache Compression Demo ===")
    
    # Create sample KV cache
    np.random.seed(42)
    kv_cache = np.random.randn(200, 64).tolist()
    print(f"Original KV cache size: {len(kv_cache)} tokens")
    
    # Initialize services
    freqkv = FreqKVService()
    lococo = LoCoCoService()
    
    # Apply FreqKV compression
    freq_compressed = await freqkv.compress(kv_cache, sink_tokens=10, compression_ratio=0.7)
    print(f"After FreqKV compression: {len(freq_compressed)} tokens")
    
    # Apply LoCoCo fusion
    final_compressed = await lococo.fuse(freq_compressed, target_ratio=0.5)
    print(f"After LoCoCo fusion: {len(final_compressed)} tokens")
    
    # Calculate final compression ratio
    final_ratio = len(final_compressed) / len(kv_cache)
    print(f"Final compression ratio: {final_ratio:.2f} ({final_ratio:.1%})")
    print()

async def demo_routing():
    """Demo prompt routing"""
    print("=== Prompt Routing Demo ===")
    
    # Initialize services
    routing = RoutingService()
    registry = ModelRegistry()
    await registry.initialize()
    
    # Test prompts of different complexity
    test_prompts = [
        "Fix the indentation in this function",
        "Refactor this class to use dependency injection",
        "Design a microservices architecture for this e-commerce platform"
    ]
    
    for prompt in test_prompts:
        complexity = await routing.classify_complexity(prompt)
        model = registry.get_model_for_complexity(complexity)
        
        print(f"Prompt: {prompt}")
        print(f"Classified as: {complexity}")
        print(f"Routed to: {model}")
        
        # Generate mock response
        response = await routing.generate_response(prompt, model)
        print(f"Response: {response}")
        print("-" * 50)

async def demo_full_pipeline():
    """Demo the complete pipeline"""
    print("=== Full Pipeline Demo ===")
    
    # Sample data
    np.random.seed(42)
    kv_cache = np.random.randn(150, 32).tolist()
    prompt = "Implement a caching layer for this API with Redis"
    
    print(f"Input: KV cache with {len(kv_cache)} tokens")
    print(f"Prompt: {prompt}")
    print()
    
    # Initialize all services
    freqkv = FreqKVService()
    lococo = LoCoCoService()
    routing = RoutingService()
    registry = ModelRegistry()
    await registry.initialize()
    
    # Step 1: Compress KV cache
    freq_compressed = await freqkv.compress(kv_cache, sink_tokens=5)
    final_compressed = await lococo.fuse(freq_compressed, target_ratio=0.6)
    
    print(f"Compressed KV: {len(kv_cache)} → {len(final_compressed)} tokens")
    
    # Step 2: Route prompt
    complexity = await routing.classify_complexity(prompt)
    model = registry.get_model_for_complexity(complexity)
    
    print(f"Prompt complexity: {complexity}")
    print(f"Selected model: {model}")
    
    # Step 3: Generate response
    context = f"[Using compressed KV context with {len(final_compressed)} tokens]"
    response = await routing.generate_response(prompt, model, context=context)
    
    print(f"Generated response: {response}")

async def main():
    """Run all demos"""
    print("Global MCP Server Demo\n")
    
    try:
        await demo_compression()
        await demo_routing()
        await demo_full_pipeline()
        
        print("\n✅ Demo completed successfully!")
        print("\nTo start the MCP server:")
        print("  python -m mcp.server")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
