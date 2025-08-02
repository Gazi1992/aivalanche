"""
Base abstract class for parameter transformations.

This module defines the interface that all transformation strategies must implement.
"""

from abc import ABC, abstractmethod
from typing import Union


class BaseTransform(ABC):
    """
    Abstract base class for parameter transformations.
    
    Transformations are applied before normalization to change the scale
    of the parameter space (e.g., logarithmic scale for parameters that
    vary over many orders of magnitude).
    """
    
    @abstractmethod
    def scale(self, value: Union[int, float]) -> float:
        """
        Apply the transformation to scale a value.
        
        Args:
            value: The value to transform
            
        Returns:
            The transformed (scaled) value
            
        Raises:
            ValueError: If the value is invalid for this transformation
        """
        pass
    
    @abstractmethod
    def unscale(self, scaled_value: float) -> float:
        """
        Apply the inverse transformation to unscale a value.
        
        Args:
            scaled_value: The scaled value to transform back
            
        Returns:
            The original (unscaled) value
        """
        pass
    
    @abstractmethod
    def validate_value(self, value: Union[int, float]) -> bool:
        """
        Check if a value is valid for this transformation.
        
        Args:
            value: The value to check
            
        Returns:
            True if the value can be transformed, False otherwise
        """
        pass
    
    @abstractmethod
    def __repr__(self) -> str:
        """Return a string representation of this transformation."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this transformation."""
        pass