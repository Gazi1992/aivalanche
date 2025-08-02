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