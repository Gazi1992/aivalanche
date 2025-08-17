"""
Negative logarithmic transformation implementation.

This module provides the negative log transformation for parameters with negative values.
"""

import numpy as np
from typing import Union
from .base import BaseTransform


class NegLogTransform(BaseTransform):
    """
    Negative logarithmic transformation: -log10(-x).
    
    Useful for parameters that are negative and vary over many orders of magnitude.
    Only works with negative values.
    """
    
    def scale(self, value: Union[int, float]) -> float:
        """
        Apply -log10(-x) transformation.
        
        Args:
            value: The value to transform (must be negative)
            
        Returns:
            -log10(-value)
            
        Raises:
            ValueError: If value is not negative
        """
        value = float(value)
        if value >= 0:
            raise ValueError(f"NegLog transform requires negative values, got {value}")
        return -np.log10(-value)
    
    def unscale(self, scaled_value: float) -> float:
        """
        Apply inverse neglog transformation.
        
        Args:
            scaled_value: The neglog-scaled value
            
        Returns:
            -(10^(-scaled_value))
        """
        return -(10.0 ** (-scaled_value))
    
    def validate_value(self, value: Union[int, float]) -> bool:
        """
        Check if a value is valid for neglog transformation.
        
        Args:
            value: The value to check
            
        Returns:
            True if value is negative
        """
        try:
            return float(value) < 0
        except (TypeError, ValueError):
            return False
    
    def __repr__(self) -> str:
        """Return a string representation of this transformation."""
        return "NegLogTransform()"
    
    @property
    def name(self) -> str:
        """Get the name of this transformation."""
        return "neglog"
    
    def scale_gradient(self, gradient: float, value: float) -> float:
        """
        Transform gradient from original to neglog space.
        
        For neglog: scale(x) = -log10(-x) where x < 0
        Chain rule: df/dy = df/dx * dx/dy
        Since dy/dx = -1/(x*ln(10)) where x < 0, we have dx/dy = -x*ln(10) = |x|*ln(10)
        Therefore: df/dy = df/dx * |x| * ln(10) = df/dx * (-x) * ln(10)
        
        Args:
            gradient: The gradient in original space (df/dx)
            value: The current value in original space (x, must be negative)
            
        Returns:
            The gradient in neglog space (df/dy)
        """
        if value >= 0:
            raise ValueError(f"NegLog gradient transform requires negative value, got {value}")
        # Multiply by -x*ln(10) = |x|*ln(10) since x is negative
        return gradient * (-value) * np.log(10)
    
    def unscale_gradient(self, gradient: float, scaled_value: float) -> float:
        """
        Transform gradient from neglog space to original space.
        
        For neglog: unscale(y) = -(10^(-y))
        Chain rule: df/dx = df/dy * dy/dx
        Since dx/dy = -(10^(-y)) * (-ln(10)) = 10^(-y) * ln(10)
        And dy/dx = 1/(dx/dy), we have:
        df/dx = df/dy / (10^(-y) * ln(10))
        
        Since x = -(10^(-y)), we have 10^(-y) = -x = |x|
        So: df/dx = df/dy / (|x| * ln(10))
        
        Args:
            gradient: The gradient in neglog space (df/dy)
            scaled_value: The current value in neglog space (y)
            
        Returns:
            The gradient in original space (df/dx)
        """
        # Divide by 10^(-y) * ln(10) where 10^(-y) = |x|
        return gradient / ((10.0 ** (-scaled_value)) * np.log(10))