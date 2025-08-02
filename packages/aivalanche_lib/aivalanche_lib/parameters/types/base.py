"""
Base abstract class for parameter types.

This module defines the interface that all parameter types must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Literal, Union
import warnings
import numpy as np
from ..transformations.base import BaseTransform
from ..transformations.no_transform import NoTransform
from ..transformations.log import LogTransform
from ..transformations.neglog import NegLogTransform
from ..transformations.symlog import SymLogTransform


class BaseParameterType(ABC):
    """
    Abstract base class for all parameter types.
    
    This class defines the interface that must be implemented by all parameter types
    (continuous, discrete, categorical).
    """
    
    def __init__(
        self,
        name: str,
        default: Any,
        scale: Optional[Literal['lin', 'log']] = None,
        mode: str = 'variable',
        description: Optional[str] = None
    ):
        """
        Initialize the base parameter type.
        
        Args:
            name: The parameter name
            default: The default value for this parameter
            scale: The scale type ('lin' or 'log'), if None will be auto-detected
            mode: The parameter mode ('variable' or 'fixed')
            description: Optional description of the parameter
        """
        if mode not in ['variable', 'fixed']:
            raise ValueError(f"Mode must be 'variable' or 'fixed', got '{mode}'")
        
        self._name = name
        self._default = default
        self._scale = scale
        self._mode = mode
        self._description = description
        self._transform = None  # Will be set by subclasses
    
    @property
    def name(self) -> str:
        """Get the parameter name."""
        return self._name
    
    @property
    def default(self) -> Any:
        """Get the default value for this parameter."""
        return self._default
    
    @property
    def scale(self) -> Literal['lin', 'log']:
        """Get the scale type for this parameter."""
        return self._scale
    
    @property
    def mode(self) -> str:
        """Get the parameter mode ('variable' or 'fixed')."""
        return self._mode
    
    @property
    def description(self) -> Optional[str]:
        """Get the parameter description."""
        return self._description
    
    @property
    def transform(self) -> BaseTransform:
        """Get the transform for this parameter."""
        return self._transform
    
    @property
    def is_variable(self) -> bool:
        """Check if this parameter is variable."""
        return self._mode == 'variable'
    
    @property
    def is_fixed(self) -> bool:
        """Check if this parameter is fixed."""
        return self._mode == 'fixed'
    
    @property
    @abstractmethod
    def type(self) -> str:
        """Get the parameter type as a string."""
        pass
    
    @abstractmethod
    def validate(self, value: Any) -> bool:
        """
        Validate if a value is valid for this parameter type.
        
        Args:
            value: The value to validate
            
        Returns:
            True if the value is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def norm_value(self, value: Any) -> float:
        """
        Normalize a value to the range [0, 1].
        
        Args:
            value: The value to normalize
            
        Returns:
            The normalized value in range [0, 1]
            
        Raises:
            ValueError: If the value is invalid for this parameter type
        """
        pass
    
    @abstractmethod
    def unnorm_value(self, norm_value: float) -> Any:
        """
        Denormalize a value from the range [0, 1] back to the parameter's domain.
        
        Args:
            norm_value: The normalized value in range [0, 1]
            
        Returns:
            The denormalized value in the parameter's domain
            
        Raises:
            ValueError: If the normalized value is not in [0, 1]
        """
        pass
    
    @abstractmethod
    def sample_random(self, random_state: Optional[int] = None) -> Any:
        """
        Sample a random valid value for this parameter.
        
        Args:
            random_state: Optional random seed for reproducibility
            
        Returns:
            A random valid value for this parameter
        """
        pass
    
    @abstractmethod
    def __repr__(self) -> str:
        """Return a string representation of this parameter type."""
        pass
    
    def validate_norm_value(self, norm_value: float) -> None:
        """
        Validate that a normalized value is in the valid range [0, 1].
        
        Args:
            norm_value: The normalized value to validate
            
        Raises:
            ValueError: If the value is not in [0, 1]
        """
        if not 0 <= norm_value <= 1:
            raise ValueError(f"Normalized value must be in [0, 1], got {norm_value}")
    
    def _auto_detect_scale(self, min_val: Union[int, float], max_val: Union[int, float]) -> Literal['lin', 'log']:
        """
        Auto-detect the scale based on the parameter range.
        
        Args:
            min_val: The minimum value
            max_val: The maximum value
            
        Returns:
            'log' if the range suggests logarithmic scale, 'lin' otherwise
        """
        # If both have the same sign
        if min_val * max_val > 0:
            if min_val > 0:
                # Both positive
                ratio = max_val / min_val
            else:
                # Both negative
                ratio = abs(min_val / max_val)
            
            if ratio >= 100:
                return 'log'
        elif min_val < 0 and max_val > 0:
            # Opposite signs
            if (max_val - min_val) > 100:
                return 'log'
        
        return 'lin'
    
    def _determine_scale(
        self, 
        scale: Optional[Union[Literal['lin', 'log'], str]], 
        mode: str,
        min_val: Optional[Union[int, float]] = None,
        max_val: Optional[Union[int, float]] = None
    ) -> Literal['lin', 'log']:
        """
        Determine the scale to use, either from explicit value or auto-detection.
        
        Args:
            scale: The explicitly provided scale (or None)
            mode: The parameter mode ('fixed' or 'variable')
            min_val: The minimum value (required if scale is None and mode is 'variable')
            max_val: The maximum value (required if scale is None and mode is 'variable')
            
        Returns:
            The scale to use: 'lin' or 'log'
        """
        # Fixed parameters always use 'lin' scale
        if mode == 'fixed':
            return 'lin'
        
        if scale is not None:
            # Handle aliases and validate scale value
            scale_lower = scale.lower()
            if scale_lower in ['lin', 'linear']:
                return 'lin'
            elif scale_lower in ['log', 'logarithmic']:
                return 'log'
            else:
                # Invalid scale value, fall through to auto-detection
                warnings.warn(
                    f"Invalid scale value '{scale}'. Valid values are 'lin', 'log', 'linear', or 'logarithmic'. "
                    f"Auto-detecting scale instead.",
                    UserWarning
                )
                scale = None
        
        if scale is None:
            if min_val is None or max_val is None:
                raise ValueError("min_val and max_val are required for auto-detecting scale")
            return self._auto_detect_scale(min_val, max_val)
        
        return scale
    
    def _determine_transform(
        self, 
        scale: Literal['lin', 'log'],
        min_val: Optional[Union[int, float]] = None,
        max_val: Optional[Union[int, float]] = None
    ) -> BaseTransform:
        """
        Determine the transform to use based on scale and range.
        
        Args:
            scale: The scale type ('lin' or 'log')
            min_val: The minimum value (required for log scale)
            max_val: The maximum value (required for log scale)
            
        Returns:
            The appropriate transform instance
        """
        if scale == 'lin':
            return NoTransform()
        
        # For log scale, need to determine which log transform to use
        if min_val is None or max_val is None:
            raise ValueError("min_val and max_val are required for log scale transform selection")
        
        # Check if range includes zero or spans opposite signs
        if min_val <= 0 and max_val >= 0:
            # Range includes zero or spans opposite signs -> use SymLogTransform
            return SymLogTransform()
        elif min_val > 0:
            # All positive values -> use LogTransform
            return LogTransform()
        else:
            # All negative values -> use NegLogTransform
            return NegLogTransform()