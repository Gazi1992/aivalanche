"""
Collection of parameters with batch operations.

This module provides the Parameters class for managing multiple parameters
and performing batch operations on them.
"""

import numpy as np
import pandas as pd
import warnings
from typing import Dict, List, Any, Optional, Type, Union, Literal
from .types.base import BaseParameterType
from .types.continuous import ContinuousParameter
from .types.discrete import DiscreteParameter
from .types.categorical import CategoricalParameter


class Parameters:
    """
    A collection of parameters with batch operations.
    
    This class manages multiple parameters and provides methods for:
    - Batch normalization/denormalization
    - Filtering by type or mode
    - Random sampling
    - Validation
    
    Attributes:
        parameters: List of parameter type instances
    """
    
    def __init__(self, parameters: Union[List[BaseParameterType], List[Dict[str, Any]], str, pd.DataFrame]):
        """
        Initialize a parameters collection.
        
        Args:
            parameters: Can be one of:
                - List of BaseParameterType instances (ContinuousParameter, DiscreteParameter, or CategoricalParameter)
                - List of parameter definition dictionaries
                - Path to a CSV or JSON file
                - DataFrame with parameter definitions
            
        Raises:
            ValueError: If parameter names are not unique or definitions are invalid
        """
        # Convert input to list of parameter type instances
        from .io.readers import parse_parameters
        param_list = parse_parameters(parameters)
        
        # Create name-to-parameter mapping and handle duplicates
        self._param_map = {}
        unique_params = []
        seen_names = set()
        
        for param in param_list:
            if param.name in seen_names:
                warnings.warn(
                    f"Duplicate parameter name '{param.name}' found. Only the first occurrence will be kept.",
                    UserWarning
                )
            else:
                self._param_map[param.name] = param
                unique_params.append(param)
                seen_names.add(param.name)
        
        # Sort parameters alphabetically by name
        self.parameters = sorted(unique_params, key=lambda p: p.name)
        
        # Cache for quick access
        self._variable_params = None
        self._fixed_params = None
    
    def __len__(self) -> int:
        """Get the number of parameters."""
        return len(self.parameters)
    
    def __iter__(self):
        """Iterate over parameters."""
        return iter(self.parameters)
    
    def __getitem__(self, name: str) -> BaseParameterType:
        """Get a parameter by name."""
        return self.get_parameter(name)
    
    @property
    def names(self) -> List[str]:
        """Get all parameter names."""
        return [param.name for param in self.parameters]
    
    @property
    def variable_names(self) -> List[str]:
        """Get names of variable parameters."""
        return [param.name for param in self.get_variable_parameters()]
    
    @property
    def fixed_names(self) -> List[str]:
        """Get names of fixed parameters."""
        return [param.name for param in self.get_fixed_parameters()]
    
    @property
    def n_parameters(self) -> int:
        """Get the number of parameters."""
        return len(self.parameters)
    
    @property
    def n_variable(self) -> int:
        """Get the number of variable parameters."""
        return len(self.get_variable_parameters())
    
    @property
    def n_fixed(self) -> int:
        """Get the number of fixed parameters."""
        return len(self.get_fixed_parameters())
    
    @property
    def n_continuous(self) -> int:
        """Get the number of continuous parameters."""
        return len(self.get_continuous_parameters())
    
    @property
    def n_discrete(self) -> int:
        """Get the number of discrete parameters."""
        return len(self.get_discrete_parameters())
    
    @property
    def n_categorical(self) -> int:
        """Get the number of categorical parameters."""
        return len(self.get_categorical_parameters())
    
    def get_parameter(self, name: str) -> BaseParameterType:
        """
        Get a parameter by name.
        
        Args:
            name: The parameter name
            
        Returns:
            The parameter type instance
            
        Raises:
            KeyError: If parameter not found
        """
        if name not in self._param_map:
            raise KeyError(f"Parameter '{name}' not found")
        return self._param_map[name]
    
    def get_by_type(self, param_type: Type[BaseParameterType]) -> List[BaseParameterType]:
        """
        Get all parameters of a specific type.
        
        Args:
            param_type: The parameter type class (ContinuousParameter, DiscreteParameter, etc.)
            
        Returns:
            List of parameters of the specified type
        """
        return [param for param in self.parameters if isinstance(param, param_type)]
    
    def get_variable_parameters(self) -> List[BaseParameterType]:
        """Get all variable parameters."""
        if self._variable_params is None:
            self._variable_params = [param for param in self.parameters if param.is_variable]
        return self._variable_params
    
    def get_fixed_parameters(self) -> List[BaseParameterType]:
        """Get all fixed parameters."""
        if self._fixed_params is None:
            self._fixed_params = [param for param in self.parameters if param.is_fixed]
        return self._fixed_params
    
    def get_continuous_parameters(self) -> List[BaseParameterType]:
        """Get all continuous parameters."""
        return self.get_by_type(ContinuousParameter)
    
    def get_discrete_parameters(self) -> List[BaseParameterType]:
        """Get all discrete parameters."""
        return self.get_by_type(DiscreteParameter)
    
    def get_categorical_parameters(self) -> List[BaseParameterType]:
        """Get all categorical parameters."""
        return self.get_by_type(CategoricalParameter)
    
    def validate_values(self, values: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate a dictionary of parameter values.
        
        Args:
            values: Dictionary mapping parameter names to values
            
        Returns:
            Dictionary mapping parameter names to validation results
        """
        results = {}
        for name, value in values.items():
            if name in self._param_map:
                results[name] = self._param_map[name].validate(value)
            else:
                results[name] = False
        return results
    
    def norm_all(
        self, 
        values: Union[np.ndarray, List[float], Dict[str, Any], List[Dict[str, Any]], pd.DataFrame]
    ) -> Union[np.ndarray, Dict[str, Any], List[Dict[str, Any]], pd.DataFrame]:
        """
        Normalize all parameter values to [0, 1] range.
        
        Args:
            values: Can be:
                - Array or list of values (assumes alphabetically sorted variable parameters)
                - Dictionary mapping parameter names to values
                - List of dictionaries with parameter names as keys
                - DataFrame with parameter names as columns
            
        Returns:
            Same format as input but with normalized values for variable parameters
            and default values for fixed parameters (when applicable)
            
        Raises:
            ValueError: If any value is invalid or parameter not found
        """
        # Handle different input formats
        if isinstance(values, pd.DataFrame):
            # DataFrame input
            result_df = values.copy()
            
            # Normalize variable parameters
            for param in self.get_variable_parameters():
                if param.name not in result_df.columns:
                    raise ValueError(f"Missing column for parameter '{param.name}'")
                result_df[param.name] = result_df[param.name].apply(param.norm_value)
            
            # Add fixed parameter defaults
            for param in self.get_fixed_parameters():
                if param.name not in result_df.columns:
                    result_df[param.name] = param.default
            
            return result_df
            
        elif isinstance(values, list) and values and isinstance(values[0], dict):
            # List of dicts input
            result_list = []
            for value_dict in values:
                norm_dict = {}
                
                # Normalize variable parameters
                for param in self.get_variable_parameters():
                    if param.name not in value_dict:
                        raise ValueError(f"Missing value for parameter '{param.name}'")
                    norm_dict[param.name] = param.norm_value(value_dict[param.name])
                
                # Add fixed parameter defaults
                for param in self.get_fixed_parameters():
                    norm_dict[param.name] = param.default
                
                result_list.append(norm_dict)
            
            return result_list
            
        elif isinstance(values, dict):
            # Single dict input - return normalized dict
            norm_dict = {}
            
            # Handle empty parameter set
            if not self.parameters:
                return norm_dict
            
            # Normalize variable parameters
            for param in self.get_variable_parameters():
                if param.name not in values:
                    raise ValueError(f"Missing value for parameter '{param.name}'")
                norm_dict[param.name] = param.norm_value(values[param.name])
            
            # Add fixed parameter defaults
            for param in self.get_fixed_parameters():
                norm_dict[param.name] = param.default
            
            return norm_dict
            
        elif isinstance(values, (np.ndarray, list)):
            # Array/list input - assumes alphabetically sorted variable parameters
            params = self.get_variable_parameters()
            
            if len(values) != len(params):
                raise ValueError(f"Expected {len(params)} values, got {len(values)}")
            
            normalized = []
            for param, value in zip(params, values):
                normalized.append(param.norm_value(value))
            
            return np.array(normalized)
        
        else:
            raise TypeError(f"Unsupported input type: {type(values)}")
    
    def unnorm_all(
        self, 
        norm_values: Union[np.ndarray, List[float], Dict[str, Any], List[Dict[str, Any]], pd.DataFrame]
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame]:
        """
        Denormalize values from [0, 1] range back to parameter domains.
        
        Args:
            norm_values: Can be:
                - Array or list of normalized values (for variable params only)
                - Dictionary mapping parameter names to normalized values
                - List of dictionaries with parameter names as keys
                - DataFrame with parameter names as columns
            
        Returns:
            Same format as input (dict/list/DataFrame) with denormalized values
            
        Raises:
            ValueError: If array size doesn't match parameter count
        """
        # Handle DataFrame input
        if isinstance(norm_values, pd.DataFrame):
            result_df = norm_values.copy()
            
            # Denormalize variable parameters
            for param in self.get_variable_parameters():
                if param.name in result_df.columns:
                    result_df[param.name] = result_df[param.name].apply(param.unnorm_value)
            
            # Add fixed parameter defaults
            for param in self.get_fixed_parameters():
                if param.name not in result_df.columns:
                    result_df[param.name] = param.default
            
            return result_df
            
        # Handle list of dicts input
        elif isinstance(norm_values, list) and norm_values and isinstance(norm_values[0], dict):
            result_list = []
            for norm_dict in norm_values:
                unnorm_dict = {}
                
                # Denormalize variable parameters
                for param in self.get_variable_parameters():
                    if param.name in norm_dict:
                        unnorm_dict[param.name] = param.unnorm_value(norm_dict[param.name])
                
                # Add fixed parameter defaults
                for param in self.get_fixed_parameters():
                    unnorm_dict[param.name] = param.default
                
                result_list.append(unnorm_dict)
            
            return result_list
            
        # Handle single dict input
        elif isinstance(norm_values, dict):
            result = {}
            
            # Denormalize variable parameters
            for param in self.get_variable_parameters():
                if param.name in norm_values:
                    result[param.name] = param.unnorm_value(norm_values[param.name])
            
            # Add fixed parameter defaults
            for param in self.get_fixed_parameters():
                result[param.name] = param.default
            
            return result
            
        # Handle array/list input
        else:
            params = self.get_variable_parameters()
            
            if len(norm_values) != len(params):
                raise ValueError(
                    f"Expected {len(params)} normalized values, got {len(norm_values)}"
                )
            
            result = {}
            for param, norm_value in zip(params, norm_values):
                result[param.name] = param.unnorm_value(float(norm_value))
            
            # Add fixed parameter defaults
            for param in self.get_fixed_parameters():
                result[param.name] = param.default
            
            return result
    
    
    def sample_random(
        self, 
        n_samples: int = 1,
        random_state: Optional[int] = None,
        output_format: Literal['dict', 'df'] = 'df'
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame]:
        """
        Sample random values for variable parameters.
        
        Fixed parameters always use their default values.
        
        Args:
            n_samples: Number of samples to generate
            random_state: Optional random seed for reproducibility
            output_format: Output format - 'dict' for dictionary/list or 'df' for DataFrame
            
        Returns:
            If n_samples=1 and output_format='dict': Dictionary mapping parameter names to values
            If n_samples>1 and output_format='dict': List of dictionaries
            If output_format='df': DataFrame with parameter names as columns
        """
        if n_samples < 1:
            raise ValueError("n_samples must be at least 1")
        
        # Set random state if provided
        if random_state is not None:
            np.random.seed(random_state)
        
        samples = []
        for _ in range(n_samples):
            sample = {}
            
            # Sample variable parameters
            for param in self.get_variable_parameters():
                sample[param.name] = param.sample_random()
            
            # Use defaults for fixed parameters
            for param in self.get_fixed_parameters():
                sample[param.name] = param.default
            
            samples.append(sample)
        
        # Return in requested format
        if output_format == 'df':
            return pd.DataFrame(samples)
        else:
            # Return single dict if n_samples=1, otherwise list
            return samples[0] if n_samples == 1 else samples
    
    def get_defaults(self) -> Dict[str, Any]:
        """
        Get default values for all parameters.
        
        Returns:
            Dictionary mapping parameter names to default values
        """
        return {param.name: param.default for param in self.parameters}
    
    def get_bounds(self, only_variable: bool = True) -> Dict[str, tuple]:
        """
        Get bounds for all numeric parameters.
        
        Args:
            only_variable: If True, only return bounds for variable parameters
            
        Returns:
            Dictionary mapping parameter names to (min, max) tuples
        """
        params = self.get_variable_parameters() if only_variable else self.parameters
        
        bounds = {}
        for param in params:
            if isinstance(param, (ContinuousParameter, DiscreteParameter)):
                bounds[param.name] = (param.min_val, param.max_val)
            elif isinstance(param, CategoricalParameter):
                # For categorical, return the number of categories
                bounds[param.name] = (0, len(param.categories) - 1)
        
        return bounds
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """
        Convert parameter set to a list of dictionaries.
        
        Returns:
            List of parameter dictionaries
        """
        result = []
        for param in self.parameters:
            param_dict = {
                'name': param.name,
                'mode': param.mode,
                'scale': param.scale,
                'default': param.default
            }
            
            # Add description if present
            if param.description:
                param_dict['description'] = param.description
            
            if isinstance(param, ContinuousParameter):
                param_dict.update({
                    'type': 'continuous',
                    'min': param.min_val,
                    'max': param.max_val
                })
            elif isinstance(param, DiscreteParameter):
                param_dict.update({
                    'type': 'discrete',
                    'min': param.min_val,
                    'max': param.max_val
                })
                # Add step if it's a regular sequence
                if len(param.values) > 1:
                    diffs = [param.values[i+1] - param.values[i] 
                            for i in range(len(param.values)-1)]
                    if len(set(diffs)) == 1:  # Regular step
                        param_dict['step'] = diffs[0]
                    else:
                        # Irregular sequence, store values list
                        param_dict['values'] = param.values
            elif isinstance(param, CategoricalParameter):
                param_dict.update({
                    'type': 'categorical',
                    'values': param.categories
                })
            
            result.append(param_dict)
        
        return result
    
    def __repr__(self) -> str:
        """Return a string representation of this parameters collection."""
        return f"Parameters({len(self)} parameters: {', '.join(self.names[:5])}{'...' if len(self) > 5 else ''})"