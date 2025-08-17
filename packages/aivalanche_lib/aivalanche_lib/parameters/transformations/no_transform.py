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
    
    def scale_gradient(self, gradient: float, value: float) -> float:
        """
        Transform gradient for identity transformation (no change).
        
        For identity: d(scale)/d(value) = 1
        
        Args:
            gradient: The gradient in original space
            value: The current value (unused for identity)
            
        Returns:
            The same gradient
        """
        return gradient
    
    def unscale_gradient(self, gradient: float, scaled_value: float) -> float:
        """
        Inverse transform gradient for identity transformation (no change).
        
        For identity: d(unscale)/d(scaled) = 1
        
        Args:
            gradient: The gradient in scaled space
            scaled_value: The current scaled value (unused for identity)
            
        Returns:
            The same gradient
        """
        return gradient