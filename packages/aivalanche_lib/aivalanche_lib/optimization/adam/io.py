"""
I/O functions for ADAM optimizer.

This module handles reading and writing of optimization results,
parameters, and history data.
"""

import os
import json
import pandas as pd
from datetime import datetime
from .utils import _get_history_as_df


def write_history_to_file(optimizer, which='points', file_path=None):
    """
    Write optimization history to CSV file.
    
    Args:
        optimizer: The Adam optimizer instance
        which: Type of history ('points', 'gradients')
        file_path: Path to save file (if None, auto-generated)
    
    Returns:
        str: Path to the saved file
    """
    if file_path is None:
        if optimizer.results_dir is not None:
            base_dir = optimizer.results_dir
        else:
            base_dir = os.getcwd()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"adam_history_{which}_{timestamp}.csv"
        file_path = os.path.join(base_dir, filename)
    
    # Get history as DataFrame
    df, _ = _get_history_as_df(optimizer, which)
    
    if df.empty:
        print(f"Warning: No {which} history to write")
        return None
    
    # Save to CSV
    df.to_csv(file_path, index=False)
    print(f"History saved to: {file_path}")
    
    return file_path


def write_optimization_info_to_file(optimizer, file_path=None):
    """
    Write optimization configuration and results to JSON file.
    
    Args:
        optimizer: The Adam optimizer instance
        file_path: Path to save file (if None, auto-generated)
    
    Returns:
        str: Path to the saved file
    """
    if file_path is None:
        if optimizer.results_dir is not None:
            base_dir = optimizer.results_dir
        else:
            base_dir = os.getcwd()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"adam_optimization_info_{timestamp}.json"
        file_path = os.path.join(base_dir, filename)
    
    # Get optimization info
    info = optimizer.get_info()
    
    # Convert numpy types to Python types for JSON serialization
    def convert_to_json_serializable(obj):
        if isinstance(obj, pd.Series):
            return obj.to_dict()
        elif hasattr(obj, 'tolist'):  # numpy arrays
            return obj.tolist()
        elif hasattr(obj, 'item'):  # numpy scalars
            return obj.item()
        else:
            return obj
    
    # Recursively convert the info dictionary
    def convert_dict(d):
        result = {}
        for key, value in d.items():
            if isinstance(value, dict):
                result[key] = convert_dict(value)
            else:
                result[key] = convert_to_json_serializable(value)
        return result
    
    info_serializable = convert_dict(info)
    
    # Add timestamp
    info_serializable['timestamp'] = datetime.now().isoformat()
    
    # Save to JSON
    with open(file_path, 'w') as f:
        json.dump(info_serializable, f, indent=2)
    
    print(f"Optimization info saved to: {file_path}")
    return file_path


def write_best_parameters_to_file(optimizer, file_path=None):
    """
    Write best parameters to CSV file.
    
    Args:
        optimizer: The Adam optimizer instance
        file_path: Path to save file (if None, auto-generated)
    
    Returns:
        str: Path to the saved file
    """
    if file_path is None:
        if optimizer.results_dir is not None:
            base_dir = optimizer.results_dir
        else:
            base_dir = os.getcwd()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"adam_best_parameters_{timestamp}.csv"
        file_path = os.path.join(base_dir, filename)
    
    if optimizer.best_parameters is None:
        print("Warning: No best parameters to write")
        return None
    
    # Create DataFrame with best parameters
    best_params_dict = optimizer.best_parameters.to_dict()
    best_params_dict['metric'] = optimizer.best_metric
    best_params_dict['iteration'] = optimizer.iter
    best_params_dict['evaluations'] = optimizer.nr_evaluations
    
    # Convert to DataFrame
    df = pd.DataFrame([best_params_dict])
    
    # Reorder columns
    cols = ['iteration', 'evaluations'] + optimizer.parameters_names + ['metric']
    df = df[cols]
    
    # Save to CSV
    df.to_csv(file_path, index=False)
    print(f"Best parameters saved to: {file_path}")
    
    return file_path