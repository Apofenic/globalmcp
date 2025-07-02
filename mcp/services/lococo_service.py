"""
LoCoCo Service - Convolution-based KV fusion for context compression
"""
import numpy as np
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class LoCoCoService:
    """Service for fusing KV cache using convolution-based compression"""
    
    def __init__(self, default_kernel_size: int = 7, default_target_size: int = 256):
        self.default_kernel_size = default_kernel_size
        self.default_target_size = default_target_size
        
    async def fuse(
        self,
        kv_cache: List[List[float]],
        target_ratio: float = 0.5,
        kernel_size: int = None,
        target_size: int = None
    ) -> List[List[float]]:
        """
        Fuse KV cache using 1D convolution to reduce sequence length
        
        Args:
            kv_cache: Input KV cache as nested lists
            target_ratio: Target compression ratio (0.5 = half the size)
            kernel_size: Convolution kernel size (default uses instance setting)
            target_size: Explicit target size (overrides target_ratio)
            
        Returns:
            Fused KV cache with reduced sequence length
        """
        if kernel_size is None:
            kernel_size = self.default_kernel_size
            
        logger.info(f"Fusing KV cache: {len(kv_cache)} tokens with kernel size {kernel_size}")
        
        if len(kv_cache) == 0:
            return kv_cache
            
        # Convert to numpy array
        kv_array = np.array(kv_cache, dtype=np.float32)
        n_tokens, n_dims = kv_array.shape
        
        # Determine target size
        if target_size is None:
            target_size = max(1, int(n_tokens * target_ratio))
        else:
            target_size = min(target_size, n_tokens)
            
        # If already smaller than target, return as-is
        if n_tokens <= target_size:
            logger.info("Cache already smaller than target size, returning unchanged")
            return kv_cache
            
        # Apply convolution-based fusion
        fused_cache = self._apply_convolution_fusion(
            kv_array, target_size, kernel_size
        )
        
        logger.info(f"Fusion complete: {n_tokens} -> {len(fused_cache)} tokens")
        
        return fused_cache.tolist()
    
    def _apply_convolution_fusion(
        self, 
        cache: np.ndarray, 
        target_size: int, 
        kernel_size: int
    ) -> np.ndarray:
        """Apply convolution-based fusion to reduce sequence length"""
        
        n_tokens, n_dims = cache.shape
        
        # Calculate stride to achieve target size
        stride = max(1, n_tokens // target_size)
        
        # Create averaging kernel
        kernel = np.ones(kernel_size) / kernel_size
        
        # Apply 1D convolution along sequence dimension for each feature
        fused_tokens = []
        
        for i in range(0, n_tokens - kernel_size + 1, stride):
            if len(fused_tokens) >= target_size:
                break
                
            # Extract window
            window = cache[i:i + kernel_size]
            
            # Apply kernel (weighted average)
            fused_token = np.average(window, axis=0, weights=kernel[:len(window)])
            fused_tokens.append(fused_token)
        
        # Ensure we have exactly target_size tokens
        while len(fused_tokens) < target_size and len(fused_tokens) < n_tokens:
            # Add remaining tokens if needed
            remaining_start = len(fused_tokens) * stride
            if remaining_start < n_tokens:
                fused_tokens.append(cache[remaining_start])
            else:
                break
                
        # Trim to exact target size
        fused_tokens = fused_tokens[:target_size]
        
        return np.array(fused_tokens)
    
    def get_fusion_stats(
        self,
        original_size: int,
        fused_size: int,
        kernel_size: int
    ) -> Dict[str, Any]:
        """Calculate fusion statistics"""
        ratio = fused_size / original_size if original_size > 0 else 0
        
        return {
            "original_size": original_size,
            "fused_size": fused_size,
            "fusion_ratio": ratio,
            "kernel_size": kernel_size,
            "tokens_per_fused": original_size / fused_size if fused_size > 0 else 0
        }
