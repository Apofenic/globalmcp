"""
Tests for FreqKV Service
"""
import pytest
import numpy as np
from mcp.services.freqkv_service import FreqKVService

@pytest.fixture
def freqkv_service():
    return FreqKVService()

@pytest.fixture
def sample_kv_cache():
    """Generate sample KV cache for testing"""
    np.random.seed(42)
    return np.random.randn(100, 64).tolist()

@pytest.mark.asyncio
async def test_compress_basic(freqkv_service, sample_kv_cache):
    """Test basic compression functionality"""
    compressed = await freqkv_service.compress(
        sample_kv_cache, 
        sink_tokens=10, 
        compression_ratio=0.5
    )
    
    # Should preserve sink tokens + compressed tokens
    expected_size = 10 + int((len(sample_kv_cache) - 10) * 0.5)
    assert len(compressed) == expected_size
    assert len(compressed[0]) == len(sample_kv_cache[0])  # Same feature dimension

@pytest.mark.asyncio
async def test_compress_small_cache(freqkv_service):
    """Test compression with cache smaller than sink tokens"""
    small_cache = [[1.0, 2.0], [3.0, 4.0]]
    compressed = await freqkv_service.compress(small_cache, sink_tokens=10)
    
    # Should return unchanged
    assert compressed == small_cache

@pytest.mark.asyncio
async def test_compress_preserve_sink_tokens(freqkv_service, sample_kv_cache):
    """Test that sink tokens are preserved exactly"""
    sink_tokens = 5
    compressed = await freqkv_service.compress(
        sample_kv_cache, 
        sink_tokens=sink_tokens
    )
    
    # First sink_tokens should be identical
    original_array = np.array(sample_kv_cache)
    compressed_array = np.array(compressed)
    
    np.testing.assert_array_equal(
        original_array[:sink_tokens], 
        compressed_array[:sink_tokens]
    )

def test_compression_stats(freqkv_service):
    """Test compression statistics calculation"""
    stats = freqkv_service.get_compression_stats(100, 50)
    
    assert stats["original_size"] == 100
    assert stats["compressed_size"] == 50
    assert stats["compression_ratio"] == 0.5
    assert stats["space_savings"] == 0.5
    assert stats["reduction_factor"] == 2.0

@pytest.mark.asyncio
async def test_compress_different_ratios(freqkv_service, sample_kv_cache):
    """Test compression with different ratios"""
    ratios = [0.3, 0.5, 0.8]
    
    for ratio in ratios:
        compressed = await freqkv_service.compress(
            sample_kv_cache,
            sink_tokens=5,
            compression_ratio=ratio
        )
        
        expected_size = 5 + int((len(sample_kv_cache) - 5) * ratio)
        assert len(compressed) == expected_size
