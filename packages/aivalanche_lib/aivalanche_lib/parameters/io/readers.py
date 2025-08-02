"""
Parameter readers for JSON and CSV files.

This module provides functions to read parameter configurations from various file formats.
"""

import json
import pandas as pd
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from ..types.base import BaseParameterType
from ..types.continuous import ContinuousParameter
from ..types.discrete import DiscreteParameter
from ..types.categorical import CategoricalParameter


def parse_parameters(parameters: Union[List[BaseParameterType], List[Dict[str, Any]], str, pd.DataFrame]) -> List[BaseParameterType]:
    """
    Parse various parameter input formats into a list of parameter type instances.
    
    This function handles the different ways parameters can be specified:
    - List of parameter type instances (already parsed, returned as-is)
    - List of parameter definition dictionaries
    - Path to a CSV or JSON file
    - DataFrame with parameter definitions
    
    Args:
        parameters: Input parameters in various formats
        
    Returns:
        List of BaseParameterType instances
        
    Raises:
        TypeError: If input type is not supported
        ValueError: If parameter definitions are invalid
        FileNotFoundError: If file path doesn't exist
    """
    # Already a list of parameter instances
    if isinstance(parameters, list) and parameters:
        if isinstance(parameters[0], BaseParameterType):
            return parameters
        elif isinstance(parameters[0], dict):
            # List of dictionaries
            return _create_parameters_from_dicts(parameters)
        else:
            raise TypeError(f"Unsupported list element type: {type(parameters[0])}")
    
    # File path
    elif isinstance(parameters, str):
        path = Path(parameters)
        if path.suffix.lower() == '.json':
            return read_json(parameters)
        elif path.suffix.lower() == '.csv':
            return read_csv(parameters)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    
    # DataFrame
    elif isinstance(parameters, pd.DataFrame):
        param_dicts = parameters.to_dict('records')
        return _create_parameters_from_dicts(param_dicts)
    
    # Empty list
    elif isinstance(parameters, list) and not parameters:
        return []
    
    else:
        raise TypeError(f"Unsupported parameters type: {type(parameters)}")


def read_json(file_path: Union[str, Path]) -> List[BaseParameterType]:
    """
    Read parameters from a JSON file.
    
    Expected JSON format:
    [
        {
            "name": "param1",
            "type": "continuous",  # Optional, defaults to "continuous"
            "min": 0.0,
            "max": 1.0,
            "default": 0.5,
            "mode": "variable",
            "scale": "lin",
            "description": "Optional description"
        },
        ...
    ]
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        List of BaseParameterType instances
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
        ValueError: If parameter definitions are invalid
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        raise ValueError("JSON file must contain a list of parameter definitions")
    
    return _create_parameters_from_dicts(data)


def read_csv(file_path: Union[str, Path]) -> List[BaseParameterType]:
    """
    Read parameters from a CSV file.
    
    Expected CSV columns:
    - name: Parameter name
    - type: continuous, discrete, or categorical (optional, default: continuous)
    - min: Minimum value (for continuous/discrete)
    - max: Maximum value (for continuous/discrete)
    - step: Step size (for discrete, optional)
    - values: Comma-separated list of values (for categorical)
    - default: Default value
    - mode: variable or fixed (optional, default: variable)
    - scale: lin or log (optional, auto-detected if not specified)
    - description: Optional description of the parameter
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        List of BaseParameterType instances
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If CSV format or parameter definitions are invalid
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    df = pd.read_csv(file_path)
    
    # Convert DataFrame to list of dictionaries
    param_dicts = []
    for _, row in df.iterrows():
        param_dict = row.to_dict()
        
        # Handle categorical values (comma-separated string to list)
        if param_dict.get('type') == 'categorical' and 'values' in param_dict:
            if isinstance(param_dict['values'], str):
                param_dict['values'] = [v.strip() for v in param_dict['values'].split(',')]
        
        # Remove NaN values (but keep lists intact)
        cleaned_dict = {}
        for k, v in param_dict.items():
            if isinstance(v, list):
                cleaned_dict[k] = v  # Keep lists as-is
            elif pd.notna(v):
                cleaned_dict[k] = v
        param_dict = cleaned_dict
        
        param_dicts.append(param_dict)
    
    return _create_parameters_from_dicts(param_dicts)


def read_dict_list(param_dicts: List[Dict[str, Any]]) -> List[BaseParameterType]:
    """
    Create parameter type instances from a list of parameter dictionaries.
    
    Args:
        param_dicts: List of parameter definition dictionaries
        
    Returns:
        List of BaseParameterType instances
        
    Raises:
        ValueError: If parameter definitions are invalid
    """
    return _create_parameters_from_dicts(param_dicts)


def _create_parameters_from_dicts(param_dicts: List[Dict[str, Any]]) -> List[BaseParameterType]:
    """
    Create parameter type instances from a list of parameter dictionaries.
    
    Args:
        param_dicts: List of parameter definition dictionaries
        
    Returns:
        List of BaseParameterType instances
        
    Raises:
        ValueError: If parameter definitions are invalid
    """
    parameters = []
    
    for param_dict in param_dicts:
        # Validate required fields
        if 'name' not in param_dict:
            raise ValueError("Parameter definition missing 'name' field")
        
        name = param_dict['name']
        
        # Type defaults to 'continuous' if not specified
        param_type = param_dict.get('type', 'continuous')
        if pd.isna(param_type):
            param_type = 'continuous'
        param_type_str = str(param_type).lower()
        
        mode = param_dict.get('mode', 'variable')
        scale = param_dict.get('scale')  # None if not specified, will auto-detect
        description = param_dict.get('description')  # Optional description
        
        # Create parameter type instance
        if param_type_str == 'continuous':
            if 'min' not in param_dict or 'max' not in param_dict:
                raise ValueError(f"Continuous parameter '{name}' missing 'min' or 'max'")
            
            parameter = ContinuousParameter(
                name=name,
                min_val=float(param_dict['min']),
                max_val=float(param_dict['max']),
                default=float(param_dict['default']) if 'default' in param_dict else None,
                scale=scale,
                mode=mode,
                description=description
            )
        
        elif param_type_str == 'discrete':
            # Check if values list is provided
            if 'values' in param_dict:
                # List mode
                values = param_dict['values']
                if not isinstance(values, list):
                    raise ValueError(f"Discrete parameter '{name}' 'values' must be a list")
                
                parameter = DiscreteParameter(
                    name=name,
                    values=values,
                    default=float(param_dict['default']) if 'default' in param_dict else None,
                    scale=scale,
                    mode=mode,
                    description=description
                )
            else:
                # Range mode
                if 'min' not in param_dict or 'max' not in param_dict:
                    raise ValueError(f"Discrete parameter '{name}' missing 'min' or 'max'")
                
                parameter = DiscreteParameter(
                    name=name,
                    min_val=float(param_dict['min']),
                    max_val=float(param_dict['max']),
                    default=float(param_dict['default']) if 'default' in param_dict else None,
                    step=float(param_dict.get('step', 1)),
                    scale=scale,
                    mode=mode,
                    description=description
                )
        
        elif param_type_str == 'categorical':
            if 'values' not in param_dict:
                raise ValueError(f"Categorical parameter '{name}' missing 'values'")
            
            values = param_dict['values']
            if not isinstance(values, list):
                raise ValueError(f"Categorical parameter '{name}' 'values' must be a list")
            
            parameter = CategoricalParameter(
                name=name,
                categories=values,
                default=param_dict.get('default'),
                scale=scale,  # Will be ignored, categorical always uses 'lin'
                mode=mode,
                description=description
            )
        
        else:
            raise ValueError(f"Unknown parameter type '{param_type_str}' for parameter '{name}'")
        
        parameters.append(parameter)
    
    return parameters