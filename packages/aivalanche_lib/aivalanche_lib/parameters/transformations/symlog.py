"""
Symmetric logarithmic transformation implementation.

This module provides symlog transformation that can handle both positive and negative values.
"""

import numpy as np
from typing import Union
from .base import BaseTransform


class SymLogTransform(BaseTransform):
    """
    Symmetric logarithmic transformation.
    
    This transformation can handle both positive and negative values,
    including values close to zero. It applies sign(x) * log10(1 + |x|/threshold).
    
    Attributes:
        threshold: The threshold value for the transformation (default: 1e-6)
    """
    
    def __init__(self, threshold: float = 1e-6):
        """
        Initialize the symmetric log transformation.
        
        Args:
            threshold: The threshold value for smooth behavior near zero
        """
        if threshold <= 0:
            raise ValueError(f"Threshold must be positive, got {threshold}")
        self.threshold = threshold
    
    def scale(self, value: Union[int, float]) -> float:
        """
        Apply symmetric log transformation.
        
        Args:
            value: The value to transform
            
        Returns:
            sign(value) * log10(1 + |value|/threshold)
        """
        value = float(value)
        return np.sign(value) * np.log10(1 + np.abs(value) / self.threshold)
    
    def unscale(self, scaled_value: float) -> float:
        """
        Apply inverse symmetric log transformation.
        
        Args:
            scaled_value: The symlog-scaled value
            
        Returns:
            sign(scaled_value) * threshold * (10^|scaled_value| - 1)
        """
        return np.sign(scaled_value) * self.threshold * (10.0 ** np.abs(scaled_value) - 1)
    
    def validate_value(self, value: Union[int, float]) -> bool:
        """
        Check if a value is valid for symlog transformation.
        
        All finite numeric values are valid for symlog transformation.
        
        Args:
            value: The value to check
            
        Returns:
            True for all finite numeric values
        """
        try:
            val = float(value)
            return bool(np.isfinite(val))
        except (TypeError, ValueError):
            return False
    
    def __repr__(self) -> str:
        """Return a string representation of this transformation."""
        return f"SymLogTransform(threshold={self.threshold})"
    
    @property
    def name(self) -> str:
        """Get the name of this transformation."""
        return "symlog"