"""
Categorical parameter type implementation.

This module implements parameters that can only take values from a predefined set of categories.
"""

import numpy as np
import warnings
from typing import Any, List, Optional, Union, Literal
from .base import BaseParameterType


class CategoricalParameter(BaseParameterType):
    """
    A categorical parameter that can only take values from a predefined set.
    
    Attributes:
        categories: The list of allowed values
        default: The default value
    """
    
    @property
    def type(self) -> str:
        """Get the parameter type as a string."""
        return "categorical"
    
    
    def __init__(
        self,
        name: str,
        categories: List[Any],
        default: Optional[Any] = None,
        scale: Optional[Union[Literal['lin', 'log'], str]] = None,
        mode: str = 'variable',
        description: Optional[str] = None
    ):
        """
        Initialize a categorical parameter.
        
        Args:
            name: The parameter name
            categories: List of allowed values (must have at least one)
            default: The default value (if None, uses first category)
            scale: Not used for categorical parameters, always set to 'lin'
            mode: The parameter mode ('variable' or 'fixed')
            description: Optional description of the parameter
            
        Raises:
            ValueError: If categories is empty or default is not in categories
        """
        if not categories:
            raise ValueError("Categories list cannot be empty")
        
        # Store categories preserving order and uniqueness
        self.categories = list(dict.fromkeys(categories))  # Remove duplicates while preserving order
        
        if len(self.categories) != len(categories):
            # Log warning about duplicates?
            pass
        
        if default is None:
            default = self.categories[0]
        elif default not in self.categories:
            raise ValueError(f"Default value '{default}' is not in categories: {self.categories}")
        
        # Categorical parameters always use 'lin' scale, ignore any provided scale
        super().__init__(name, default, 'lin', mode, description)
        
        # Categorical parameters always use NoTransform
        from ..transformations.no_transform import NoTransform
        self._transform = NoTransform()
        
        # Create mapping for efficient lookups first
        self._category_to_index = {cat: i for i, cat in enumerate(self.categories)}
        
        # For categorical parameters, range is the number of categories minus 1
        self._range = float(len(self.categories) - 1) if len(self.categories) > 1 else 0.0
        
        # For categorical parameters, scaled values are just indices
        self._scaled_min = 0.0
        self._scaled_max = float(len(self.categories) - 1) if len(self.categories) > 1 else 0.0
        self._scaled_default = float(self._category_to_index.get(default, 0))
        self._scaled_range = self._scaled_max - self._scaled_min
    
    def validate(self, value: Any) -> bool:
        """
        Check if a value is valid for this categorical parameter.
        
        If value is not in categories, a warning is raised and the first
        category will be used.
        
        Args:
            value: The value to validate
            
        Returns:
            True (always accepts values, will use first category if invalid)
        """
        if value not in self.categories:
            warnings.warn(
                f"Value '{value}' is not in categories {self.categories} "
                f"for parameter '{self.name}'. Will use first category: '{self.categories[0]}'",
                UserWarning
            )
        return True
    
    def norm_value(self, value: Any) -> float:
        """
        Normalize a categorical value to the range [0, 1].
        
        Maps each category to an evenly spaced point in [0, 1].
        
        Args:
            value: The categorical value to normalize
            
        Returns:
            The normalized value in range [0, 1]
            
        Raises:
            ValueError: If the value is not in categories
        """
        # If not in categories, use first category
        if value not in self.categories:
            value = self.categories[0]
            # validate() will have already warned about this
        
        if len(self.categories) == 1:
            return 0.5  # Single category maps to center
        
        idx = self._category_to_index[value]
        return idx / (len(self.categories) - 1)
    
    def unnorm_value(self, norm_value: float) -> Any:
        """
        Denormalize a value from [0, 1] back to a category.
        
        Values outside [0, 1] are clipped to the valid range.
        
        Args:
            norm_value: The normalized value (typically in range [0, 1])
            
        Returns:
            The corresponding category
        """
        # Clip to [0, 1] range instead of raising error
        norm_value = max(0.0, min(1.0, norm_value))
        
        if len(self.categories) == 1:
            return self.categories[0]
        
        # Map to nearest category index
        idx = int(round(norm_value * (len(self.categories) - 1)))
        idx = max(0, min(idx, len(self.categories) - 1))
        
        return self.categories[idx]
    
    def sample_random(self, random_state: Optional[int] = None) -> Any:
        """
        Sample a random category.
        
        Args:
            random_state: Optional random seed for reproducibility
            
        Returns:
            A random category from the allowed values
        """
        if random_state is not None:
            np.random.seed(random_state)
        
        return np.random.choice(self.categories)
    
    def get_category_index(self, value: Any) -> int:
        """
        Get the index of a category.
        
        Args:
            value: The category value
            
        Returns:
            The index of the category
            
        Raises:
            ValueError: If value is not in categories
        """
        if value not in self._category_to_index:
            raise ValueError(f"Value '{value}' is not in categories: {self.categories}")
        return self._category_to_index[value]
    
    def get_category_by_index(self, index: int) -> Any:
        """
        Get a category by its index.
        
        Args:
            index: The index of the category
            
        Returns:
            The category at the given index
            
        Raises:
            IndexError: If index is out of range
        """
        return self.categories[index]
    
    
    def __repr__(self) -> str:
        """Return a string representation of this parameter."""
        cats_str = str(self.categories) if len(self.categories) <= 5 else f"{self.categories[:3]}... ({len(self.categories)} total)"
        desc = f", description='{self.description}'" if self.description else ""
        return (
            f"CategoricalParameter(name='{self.name}', categories={cats_str}, "
            f"default={self.default!r}, scale='{self.scale}', mode='{self.mode}'{desc})"
        )