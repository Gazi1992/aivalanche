"""
Logarithmic transformation implementation.

This module provides the log transformation for parameters with positive values.
"""

import numpy as np
from typing import Union
from .base import BaseTransform


class LogTransform(BaseTransform):
    """
    Logarithmic transformation using log base 10.
    
    Useful for parameters that vary over many orders of magnitude.
    Only works with positive values.
    """
    
    def scale(self, value: Union[int, float]) -> float:
        """
        Apply log10 transformation.
        
        Args:
            value: The value to transform (must be positive)
            
        Returns:
            log10(value)
            
        Raises:
            ValueError: If value is not positive
        """
        value = float(value)
        if value <= 0:
            raise ValueError(f"Log transform requires positive values, got {value}")
        return np.log10(value)
    
    def unscale(self, scaled_value: float) -> float:
        """
        Apply inverse log10 transformation.
        
        Args:
            scaled_value: The log-scaled value
            
        Returns:
            10^scaled_value
        """
        return 10.0 ** scaled_value
    
    def validate_value(self, value: Union[int, float]) -> bool:
        """
        Check if a value is valid for log transformation.
        
        Args:
            value: The value to check
            
        Returns:
            True if value is positive
        """
        try:
            return float(value) > 0
        except (TypeError, ValueError):
            return False
    
    def __repr__(self) -> str:
        """Return a string representation of this transformation."""
        return "LogTransform()"
    
    @property
    def name(self) -> str:
        """Get the name of this transformation."""
        return "log"