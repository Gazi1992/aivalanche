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
    
    def scale_gradient(self, gradient: float, value: float) -> float:
        """
        Transform gradient from original to symlog space.
        
        For symlog: scale(x) = sign(x) * log10(1 + |x|/t)
        Chain rule: df/dy = df/dx * dx/dy
        Since dy/dx = 1 / (t * ln(10) * (1 + |x|/t))
        We have dx/dy = t * ln(10) * (1 + |x|/t)
        Therefore: df/dy = df/dx * t * ln(10) * (1 + |x|/t)
        
        Args:
            gradient: The gradient in original space (df/dx)
            value: The current value in original space (x)
            
        Returns:
            The gradient in symlog space (df/dy)
        """
        abs_value = np.abs(value)
        multiplier = self.threshold * np.log(10) * (1 + abs_value / self.threshold)
        return gradient * multiplier
    
    def unscale_gradient(self, gradient: float, scaled_value: float) -> float:
        """
        Transform gradient from symlog space to original space.
        
        For symlog: unscale(y) = sign(y) * t * (10^|y| - 1)
        Chain rule: df/dx = df/dy * dy/dx
        Since dx/dy = t * 10^|y| * ln(10)
        And dy/dx = 1/(dx/dy), we have:
        df/dx = df/dy / (t * 10^|y| * ln(10))
        
        Args:
            gradient: The gradient in symlog space (df/dy)
            scaled_value: The current value in symlog space (y)
            
        Returns:
            The gradient in original space (df/dx)
        """
        abs_scaled = np.abs(scaled_value)
        divisor = self.threshold * (10.0 ** abs_scaled) * np.log(10)
        return gradient / divisor