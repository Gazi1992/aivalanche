"""
No transformation (identity) implementation.

This transformation doesn't change values - it's used for linear scale parameters.
"""

from typing import Union
from .base import BaseTransform


class NoTransform(BaseTransform):
    """
    No transformation (identity) - values pass through unchanged.
    
    This is used for parameters with linear scale.
    """
    
    def scale(self, value: Union[int, float]) -> float:
        """
        Apply the identity transformation (no change).
        
        Args:
            value: The value to transform
            
        Returns:
            The same value as float
        """
        return float(value)
    
    def unscale(self, scaled_value: float) -> float:
        """
        Apply the inverse identity transformation (no change).
        
        Args:
            scaled_value: The scaled value
            
        Returns:
            The same value
        """
        return scaled_value
    
    def validate_value(self, value: Union[int, float]) -> bool:
        """
        Check if a value is valid for no transformation.
        
        All numeric values are valid since no transformation is applied.
        
        Args:
            value: The value to check
            
        Returns:
            True for all numeric values
        """
        try:
            float(value)
            return True
        except (TypeError, ValueError):
            return False
    
    def __repr__(self) -> str:
        """Return a string representation of this transformation."""
        return "NoTransform()"
    
    @property
    def name(self) -> str:
        """Get the name of this transformation."""
        return "none"