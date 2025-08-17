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
    
    def scale_gradient(self, gradient: float, value: float) -> float:
        """
        Transform gradient from original to log space.
        
        For log10: scale(x) = log10(x)
        Chain rule: df/dy = df/dx * dx/dy
        Since dy/dx = 1/(x*ln(10)), we have dx/dy = x*ln(10)
        Therefore: df/dy = df/dx * x * ln(10)
        
        Args:
            gradient: The gradient in original space (df/dx)
            value: The current value in original space (x)
            
        Returns:
            The gradient in log space (df/dy)
        """
        if value <= 0:
            raise ValueError(f"Log gradient transform requires positive value, got {value}")
        return gradient * value * np.log(10)
    
    def unscale_gradient(self, gradient: float, scaled_value: float) -> float:
        """
        Transform gradient from log space to original space.
        
        For log10: unscale(y) = 10^y
        Chain rule: df/dx = df/dy * dy/dx
        Since dx/dy = 10^y * ln(10), and dy/dx = 1/(dx/dy)
        Therefore: df/dx = df/dy / (10^y * ln(10))
        
        Args:
            gradient: The gradient in log space (df/dy)
            scaled_value: The current value in log space (y)
            
        Returns:
            The gradient in original space (df/dx)
        """
        unscaled_value = self.unscale(scaled_value)
        return gradient / (unscaled_value * np.log(10))