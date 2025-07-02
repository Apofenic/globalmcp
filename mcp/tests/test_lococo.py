"""
Tests for LoCoCo Service
"""
import pytest
import numpy as np
from mcp.services.lococo_service import LoCoCoService

@pytest.fixture
def lococo_service():
    return LoCoCoService()

@pytest.fixture
def sample_kv_cache():
    """Generate sample KV cache for testing"""
    np.random.seed(42)
    return np.random.randn(200, 64).tolist()

@pytest.mark.asyncio
async def test_fuse_basic(lococo_service, sample_kv_cache):
    """Test basic fusion functionality"""
    fused = await lococo_service.fuse(
        sample_kv_cache, 
        target_ratio=0.5
    )
    
    expected_size = int(len(sample_kv_cache) * 0.5)
    assert len(fused) == expected_size
    assert len(fused[0]) == len(sample_kv_cache[0])  # Same feature dimension

@pytest.mark.asyncio
async def test_fuse_target_size(lococo_service, sample_kv_cache):
    """Test fusion with explicit target size"""
    target_size = 50
    fused = await lococo_service.fuse(
        sample_kv_cache, 
        target_size=target_size
    )
    
    assert len(fused) == target_size

@pytest.mark.asyncio
async def test_fuse_small_cache(lococo_service):
    """Test fusion with small cache"""
    small_cache = [[1.0, 2.0], [3.0, 4.0]]
    target_size = 5
    
    fused = await lococo_service.fuse(small_cache, target_size=target_size)
    
    # Should return original since it's smaller than target
    assert fused == small_cache

@pytest.mark.asyncio
async def test_fuse_empty_cache(lococo_service):
    """Test fusion with empty cache"""
    empty_cache = []
    fused = await lococo_service.fuse(empty_cache)
    
    assert fused == []

@pytest.mark.asyncio
async def test_fuse_different_kernel_sizes(lococo_service, sample_kv_cache):
    """Test fusion with different kernel sizes"""
    kernel_sizes = [3, 7, 11]
    
    for kernel_size in kernel_sizes:
        fused = await lococo_service.fuse(
            sample_kv_cache,
            target_ratio=0.5,
            kernel_size=kernel_size
        )
        
        expected_size = int(len(sample_kv_cache) * 0.5)
        assert len(fused) == expected_size

def test_fusion_stats(lococo_service):
    """Test fusion statistics calculation"""
    stats = lococo_service.get_fusion_stats(200, 100, 7)
    
    assert stats["original_size"] == 200
    assert stats["fused_size"] == 100
    assert stats["fusion_ratio"] == 0.5
    assert stats["kernel_size"] == 7
    assert stats["tokens_per_fused"] == 2.0

@pytest.mark.asyncio
async def test_fuse_preserves_information(lococo_service):
    """Test that fusion preserves some information from original"""
    # Create structured test data
    structured_cache = []
    for i in range(100):
        # Create tokens with pattern
        token = [float(i % 10)] * 32  # Pattern in first half
        token.extend([float(i // 10)] * 32)  # Different pattern in second half
        structured_cache.append(token)
    
    fused = await lococo_service.fuse(structured_cache, target_ratio=0.5)
    
    # Should have reduced size
    assert len(fused) == 50
    
    # Fused tokens should be averages, not just random values
    fused_array = np.array(fused)
    assert not np.allclose(fused_array, 0)  # Should have meaningful values
