"""
Continuous parameter type implementation.

This module implements parameters that can take any real value within a range.
"""

import numpy as np
import warnings
from typing import Optional, Union, Any, Literal
from .base import BaseParameterType


class ContinuousParameter(BaseParameterType):
    """
    A continuous parameter that can take any real value within a specified range.
    
    Attributes:
        min_val: The minimum allowed value
        max_val: The maximum allowed value
        default: The default value
    """
    
    @property
    def min(self) -> float:
        """Get the minimum value."""
        return self.min_val
    
    @property
    def max(self) -> float:
        """Get the maximum value."""
        return self.max_val
    
    @property
    def type(self) -> str:
        """Get the parameter type as a string."""
        return "continuous"
    
    def __init__(
        self,
        name: str,
        min_val: float, 
        max_val: float, 
        default: Optional[float] = None,
        scale: Optional[Union[Literal['lin', 'log'], str]] = None,
        mode: str = 'variable',
        description: Optional[str] = None
    ):
        """
        Initialize a continuous parameter.
        
        Args:
            name: The parameter name
            min_val: The minimum allowed value
            max_val: The maximum allowed value
            default: The default value (if None, uses midpoint of range)
            scale: The scale type ('lin', 'log', 'linear', or 'logarithmic'), if None or invalid will be auto-detected
            mode: The parameter mode ('variable' or 'fixed')
            description: Optional description of the parameter
            
        Raises:
            ValueError: If min_val >= max_val or default is outside the range
        """
        # Handle min > max case by flipping with warning
        if min_val > max_val:
            warnings.warn(
                f"min_val ({min_val}) is greater than max_val ({max_val}). "
                f"Values will be flipped.",
                UserWarning
            )
            min_val, max_val = max_val, min_val
        elif min_val == max_val:
            warnings.warn(
                f"min_val and max_val are equal ({min_val}). "
                f"This parameter will have a constant value.",
                UserWarning
            )
        
        self.min_val = float(min_val)
        self.max_val = float(max_val)
        
        if default is None:
            default = (self.min_val + self.max_val) / 2
        else:
            default = float(default)
            if not self.min_val <= default <= self.max_val:
                warnings.warn(
                    f"Default value ({default}) is outside range [{self.min_val}, {self.max_val}]. "
                    f"It will be clipped to the nearest boundary.",
                    UserWarning
                )
                default = np.clip(default, self.min_val, self.max_val)
        
        # Determine scale using base class method - need to do this before calling super().__init__
        scale = self._determine_scale(scale, mode, self.min_val, self.max_val)
        
        super().__init__(name, default, scale, mode, description)
        
        # Now determine and set the transform based on scale and range
        self._transform = self._determine_transform(self._scale, self.min_val, self.max_val)
        
        # Calculate scaled min and max for normalization
        # We can't use scale_value yet as it's not fully initialized, so use transform directly
        self._scaled_min = self._transform.scale(self.min_val)
        self._scaled_max = self._transform.scale(self.max_val)
    
    def validate(self, value: Any) -> bool:
        """
        Check if a value is valid for this continuous parameter.
        
        Out-of-range values are accepted but will trigger a warning.
        
        Args:
            value: The value to validate
            
        Returns:
            True if the value is a number (even if out of range)
        """
        try:
            val = float(value)
            if not self.min_val <= val <= self.max_val:
                warnings.warn(
                    f"Value {val} is outside range [{self.min_val}, {self.max_val}] "
                    f"for parameter '{self.name}'",
                    UserWarning
                )
            return True
        except (TypeError, ValueError):
            return False
    
    def norm_value(self, value: Union[int, float]) -> float:
        """
        Normalize a value to the range [0, 1] using scaled range.
        
        First scales the value using the transform, then normalizes
        to [0, 1] using the scaled min/max.
        
        Args:
            value: The value to normalize
            
        Returns:
            The normalized value in range [0, 1]
            
        Raises:
            ValueError: If the value is invalid for this parameter
        """
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"Value {value} cannot be converted to float for parameter '{self.name}'"
            )
        
        # Validate triggers warning if out of range
        self.validate(value)
        
        # Scale the value first
        scaled_value = self._transform.scale(value)
        
        if self._scaled_max == self._scaled_min:
            return 0.5  # All values map to center if range is zero
        
        # Normalize using scaled range
        return (scaled_value - self._scaled_min) / (self._scaled_max - self._scaled_min)
    
    def unnorm_value(self, norm_value: float) -> float:
        """
        Denormalize a value from [0, 1] back to the parameter's range.
        
        First denormalizes using scaled range, then unscales to get
        the original value. Values outside [0, 1] are allowed and 
        will be extrapolated.
        
        Args:
            norm_value: The normalized value (typically in range [0, 1])
            
        Returns:
            The denormalized value in the parameter's range
        """
        # Denormalize to scaled range
        scaled_value = self._scaled_min + norm_value * (self._scaled_max - self._scaled_min)
        
        # Unscale to get original value
        return self._transform.unscale(scaled_value)
    
    def sample_random(self, random_state: Optional[int] = None) -> float:
        """
        Sample a random value from the parameter's range.
        
        Args:
            random_state: Optional random seed for reproducibility
            
        Returns:
            A random value within the parameter's range
        """
        if random_state is not None:
            np.random.seed(random_state)
        
        return np.random.uniform(self.min_val, self.max_val)
    
    def __repr__(self) -> str:
        """Return a string representation of this parameter."""
        desc = f" description='{self.description}'" if self.description else ""
        return (
            f"ContinuousParameter(name='{self.name}', min={self.min_val}, max={self.max_val}, "
            f"default={self.default}, scale='{self.scale}', mode='{self.mode}'{desc})"
        )