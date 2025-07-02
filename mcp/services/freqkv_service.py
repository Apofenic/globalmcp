"""
FreqKV Service - Frequency-domain KV cache compression using DCT
"""
import numpy as np
from scipy.fft import dct, idct
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FreqKVService:
    """Service for compressing KV cache using frequency-domain filtering (DCT)"""
    
    def __init__(self, default_compression_ratio: float = 0.7):
        self.default_compression_ratio = default_compression_ratio
        
    async def compress(
        self, 
        kv_cache: List[List[float]], 
        sink_tokens: int = 10,
        compression_ratio: float = None
    ) -> List[List[float]]:
        """
        Compress KV cache using DCT-based frequency filtering
        
        Args:
            kv_cache: Input KV cache as nested lists
            sink_tokens: Number of initial tokens to preserve uncompressed
            compression_ratio: Fraction of frequencies to keep (default uses instance setting)
            
        Returns:
            Compressed KV cache
        """
        if compression_ratio is None:
            compression_ratio = self.default_compression_ratio
            
        logger.info(f"Compressing KV cache: {len(kv_cache)} tokens, {sink_tokens} sink tokens")
        
        if len(kv_cache) <= sink_tokens:
            logger.warning("KV cache smaller than sink tokens, returning unchanged")
            return kv_cache
            
        # Convert to numpy array for processing
        kv_array = np.array(kv_cache, dtype=np.float32)
        
        # Preserve sink tokens
        sink_cache = kv_array[:sink_tokens]
        compressible_cache = kv_array[sink_tokens:]
        
        # Apply DCT compression to each dimension
        compressed_cache = self._apply_dct_compression(
            compressible_cache, compression_ratio
        )
        
        # Combine sink tokens with compressed cache
        result_cache = np.vstack([sink_cache, compressed_cache])
        
        logger.info(f"Compression complete: {len(kv_cache)} -> {len(result_cache)} tokens")
        
        return result_cache.tolist()
    
    def _apply_dct_compression(
        self, 
        cache: np.ndarray, 
        compression_ratio: float
    ) -> np.ndarray:
        """Apply DCT-based compression to cache array"""
        
        # Apply DCT along sequence dimension
        dct_coeffs = dct(cache, axis=0, norm='ortho')
        
        # Determine how many coefficients to keep
        n_tokens, n_dims = cache.shape
        n_keep = int(n_tokens * compression_ratio)
        
        # Zero out high-frequency components
        compressed_coeffs = dct_coeffs.copy()
        compressed_coeffs[n_keep:] = 0
        
        # Apply inverse DCT to reconstruct
        reconstructed = idct(compressed_coeffs, axis=0, norm='ortho')
        
        # Ensure we only return the compressed number of tokens
        return reconstructed[:n_keep]
    
    def get_compression_stats(
        self, 
        original_size: int, 
        compressed_size: int
    ) -> Dict[str, Any]:
        """Calculate compression statistics"""
        ratio = compressed_size / original_size if original_size > 0 else 0
        savings = 1 - ratio
        
        return {
            "original_size": original_size,
            "compressed_size": compressed_size,
            "compression_ratio": ratio,
            "space_savings": savings,
            "reduction_factor": original_size / compressed_size if compressed_size > 0 else float('inf')
        }
