"""
Discrete parameter type implementation.

This module implements parameters that can only take specific discrete values,
either within a range with an optional step size, or from a specific list of values.
Values can be integers or floats.
"""

import numpy as np
import warnings
from typing import Optional, Union, List, Tuple, Any, Literal
from .base import BaseParameterType


class DiscreteParameter(BaseParameterType):
    """
    A discrete parameter that can only take specific discrete values.
    
    Can be initialized in two ways:
    1. With min/max/step to define a range
    2. With a list/tuple of specific allowed values
    
    Attributes:
        min_val: The minimum allowed value
        max_val: The maximum allowed value
        values: List of all valid values
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
        return "discrete"
    
    def __init__(
        self,
        name: str,
        min_val: Optional[Union[int, float]] = None,
        max_val: Optional[Union[int, float]] = None, 
        default: Optional[Union[int, float]] = None, 
        step: Union[int, float] = 1,
        values: Optional[Union[List[Union[int, float]], Tuple[Union[int, float], ...]]] = None,
        scale: Optional[Union[Literal['lin', 'log'], str]] = None,
        mode: str = 'variable',
        description: Optional[str] = None
    ):
        """
        Initialize a discrete parameter.
        
        Can be called in two ways:
        1. DiscreteParameter(min_val=0, max_val=10, step=2)
        2. DiscreteParameter(values=[1, 2, 5, 10, 20])
        
        Args:
            name: The parameter name
            min_val: The minimum allowed value (for range mode)
            max_val: The maximum allowed value (for range mode)
            default: The default value (if None, uses midpoint or first value)
            step: The step size between values (for range mode, default: 1)
            values: Explicit list/tuple of allowed values (for list mode)
            scale: The scale type ('lin', 'log', 'linear', or 'logarithmic'), if None or invalid will be auto-detected
            mode: The parameter mode ('variable' or 'fixed')
            description: Optional description of the parameter
            
        Raises:
            ValueError: If neither range nor values are properly specified
        """
        if values is not None:
            # List mode
            if not values:
                raise ValueError("Values list cannot be empty")
            
            self.values = sorted(list(set(float(v) for v in values)))  # Remove duplicates and sort
            self.min_val = self.values[0]
            self.max_val = self.values[-1]
            
        elif min_val is not None and max_val is not None:
            # Range mode
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
                    f"This discrete parameter will have only one value.",
                    UserWarning
                )
            
            if step <= 0:
                raise ValueError(f"step ({step}) must be positive")
            
            self.min_val = float(min_val)
            self.max_val = float(max_val)
            step = float(step)
            
            # Generate values based on range and step
            # Calculate number of steps
            n_steps = int(round((self.max_val - self.min_val) / step))
            
            # Generate values
            self.values = []
            for i in range(n_steps + 1):
                value = self.min_val + i * step
                if value <= self.max_val + step * 0.01:  # Small tolerance
                    self.values.append(value)
            
            # Ensure we have at least min_val
            if len(self.values) == 0:
                self.values = [self.min_val]
            
            # If the last generated value is very close to max_val, use max_val
            if len(self.values) > 0 and abs(self.values[-1] - self.max_val) < step * 0.1:
                self.values[-1] = self.max_val
            else:
                # Update max_val to actual maximum value in the list
                self.max_val = self.values[-1]
        
        else:
            raise ValueError(
                "DiscreteParameter requires either (min_val, max_val) or values list"
            )
        
        # Set default
        if default is None:
            # Use middle value
            default = self.values[len(self.values) // 2]
        else:
            default = float(default)
            if default not in self.values:
                # Snap to nearest valid value
                nearest = min(self.values, key=lambda x: abs(x - default))
                warnings.warn(
                    f"Default value ({default}) is not in the list of valid values. "
                    f"It will be snapped to the nearest valid value ({nearest}).",
                    UserWarning
                )
                default = nearest
        
        # Determine scale using base class method - need to do this before calling super().__init__
        scale = self._determine_scale(scale, mode, self.min_val, self.max_val)
        
        super().__init__(name, default, scale, mode, description)
        
        # Now determine and set the transform based on scale and range
        self._transform = self._determine_transform(self._scale, self.min_val, self.max_val)
        
        # Calculate scaled min and max for normalization
        # We can't use scale_value yet as it's not fully initialized, so use transform directly
        self._scaled_min = self._transform.scale(self.min_val)
        self._scaled_max = self._transform.scale(self.max_val)
        
        # Also scale all discrete values for easier lookup
        self._scaled_values = [self._transform.scale(v) for v in self.values]
    
    def snap_to_nearest(self, value: float) -> float:
        """
        Snap a value to the nearest valid discrete value.
        
        Args:
            value: The value to snap
            
        Returns:
            The nearest valid discrete value
        """
        return min(self.values, key=lambda x: abs(x - value))
    
    def validate(self, value: Any) -> bool:
        """
        Check if a value is valid for this discrete parameter.
        
        If value is not in the allowed list, a warning is raised and it will
        be snapped to the nearest valid value.
        
        Args:
            value: The value to validate
            
        Returns:
            True if the value is a number (will be snapped if not in values)
        """
        try:
            val = float(value)
            # Check if value is in the allowed values (with small tolerance for floats)
            if not any(abs(val - v) < 1e-10 for v in self.values):
                closest = self.snap_to_nearest(val)
                warnings.warn(
                    f"Value {val} is not in allowed values {self.values} "
                    f"for parameter '{self.name}'. Will snap to nearest value: {closest}",
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
        
        # If not in values, snap to nearest
        if not any(abs(value - v) < 1e-10 for v in self.values):
            value = self.snap_to_nearest(value)
            # validate() will have already warned about this
        
        # Scale the value first
        scaled_value = self._transform.scale(value)
        
        if self._scaled_max == self._scaled_min:
            return 0.5  # Single value maps to center
        
        # Normalize using scaled range
        return (scaled_value - self._scaled_min) / (self._scaled_max - self._scaled_min)
    
    def unnorm_value(self, norm_value: float) -> Union[int, float]:
        """
        Denormalize a value from [0, 1] back to a valid discrete value.
        
        First denormalizes using scaled range, then unscales and snaps
        to nearest valid discrete value.
        
        Args:
            norm_value: The normalized value (typically in range [0, 1])
            
        Returns:
            The nearest valid discrete value
        """
        if len(self.values) == 1:
            return self.values[0]
        
        # Denormalize to scaled range
        scaled_value = self._scaled_min + norm_value * (self._scaled_max - self._scaled_min)
        
        # Unscale to get continuous value
        continuous_value = self._transform.unscale(scaled_value)
        
        # Snap to nearest valid discrete value
        return self.snap_to_nearest(continuous_value)
    
    def sample_random(self, random_state: Optional[int] = None) -> Union[int, float]:
        """
        Sample a random valid value from the parameter's discrete values.
        
        Args:
            random_state: Optional random seed for reproducibility
            
        Returns:
            A random valid discrete value
        """
        if random_state is not None:
            np.random.seed(random_state)
        
        return np.random.choice(self.values)
    
    
    def __repr__(self) -> str:
        """Return a string representation of this parameter."""
        desc = f", description='{self.description}'" if self.description else ""
        
        if len(self.values) <= 6:
            return (
                f"DiscreteParameter(name='{self.name}', values={self.values}, "
                f"default={self.default}, scale='{self.scale}', mode='{self.mode}'{desc})"
            )
        else:
            # For range-based, show min/max/step if it's a regular sequence
            diffs = [self.values[i+1] - self.values[i] for i in range(len(self.values)-1)]
            if len(set(diffs)) == 1:  # Regular step
                step = diffs[0]
                return (
                    f"DiscreteParameter(name='{self.name}', min={self.min_val}, max={self.max_val}, "
                    f"step={step}, default={self.default}, scale='{self.scale}', mode='{self.mode}'{desc})"
                )
            else:
                return (
                    f"DiscreteParameter(name='{self.name}', values=[{self.values[0]}, {self.values[1]}, ..., "
                    f"{self.values[-1]}] ({len(self.values)} values), default={self.default}, "
                    f"scale='{self.scale}', mode='{self.mode}'{desc})"
                )