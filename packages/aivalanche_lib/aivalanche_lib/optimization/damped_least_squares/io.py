"""
I/O functions for the DampedLeastSquares class.

This module handles saving optimization results to files in various formats.
"""

import os
import json
import pandas as pd
from typing import Optional


def write_history_to_file(dls_instance, which='points', file_path=None):
    """
    Write optimization history to a CSV file.
    
    Args:
        dls_instance: Instance of DampedLeastSquares
        which: Type of history to write ('points')
        file_path: Path to save the file (if None, uses default naming)
        
    Returns:
        str: Path to the saved file
    """
    # Get history as DataFrame
    df, _ = dls_instance.history[which], dls_instance.history[f'{which}_normed']
    
    # Determine file path
    if file_path is None:
        if dls_instance.results_dir:
            os.makedirs(dls_instance.results_dir, exist_ok=True)
            file_path = os.path.join(dls_instance.results_dir, f'history_{which}.csv')
        else:
            file_path = f'dls_history_{which}.csv'
    
    # Save to CSV
    df.to_csv(file_path, index=False)
    
    print(f"History saved to: {file_path}")
    return file_path


def write_optimization_info_to_file(dls_instance, file_path=None):
    """
    Write complete optimization information to a JSON file.
    
    Args:
        dls_instance: Instance of DampedLeastSquares
        file_path: Path to save the file (if None, uses default naming)
        
    Returns:
        str: Path to the saved file
    """
    # Get optimization info
    info = dls_instance.optimization_info
    
    # Convert numpy types to Python types for JSON serialization
    def convert_types(obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Series):
            return obj.to_dict()
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict('records')
        elif callable(obj):
            # Skip functions/callables
            return f"<{type(obj).__name__} object>"
        elif isinstance(obj, dict):
            return {k: convert_types(v) for k, v in obj.items() if not callable(v)}
        elif isinstance(obj, list):
            return [convert_types(item) for item in obj]
        return obj
    
    info_converted = convert_types(info)
    
    # Determine file path
    if file_path is None:
        if dls_instance.results_dir:
            os.makedirs(dls_instance.results_dir, exist_ok=True)
            file_path = os.path.join(dls_instance.results_dir, 'optimization_info.json')
        else:
            file_path = 'dls_optimization_info.json'
    
    # Save to JSON
    with open(file_path, 'w') as f:
        json.dump(info_converted, f, indent=2)
    
    print(f"Optimization info saved to: {file_path}")
    return file_path


def write_best_parameters_to_file(dls_instance, file_path=None):
    """
    Write best parameters to a CSV file.
    
    Args:
        dls_instance: Instance of DampedLeastSquares
        file_path: Path to save the file (if None, uses default naming)
        
    Returns:
        str: Path to the saved file
    """
    # Create DataFrame with best parameters
    best_params_df = pd.DataFrame([dls_instance.best_parameters])
    
    # Add metric
    best_params_df['metric'] = dls_instance.best_metric
    
    # Determine file path
    if file_path is None:
        if dls_instance.results_dir:
            os.makedirs(dls_instance.results_dir, exist_ok=True)
            file_path = os.path.join(dls_instance.results_dir, 'best_parameters.csv')
        else:
            file_path = 'dls_best_parameters.csv'
    
    # Save to CSV
    best_params_df.to_csv(file_path, index=False)
    
    print(f"Best parameters saved to: {file_path}")
    return file_path


# Import numpy for type conversion
import numpy as np