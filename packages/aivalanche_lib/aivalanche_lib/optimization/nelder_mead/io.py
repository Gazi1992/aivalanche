"""
I/O functions for Nelder-Mead optimization.

This module handles file input/output operations for saving optimization
results, history, and parameters.
"""

import os
import json
import pandas as pd
from datetime import datetime

def write_history_to_file(optimizer, which='trials', file_path=None):
    """
    Write optimization history to a CSV file.
    
    Args:
        optimizer: The NelderMead optimizer instance
        which: Type of history to write ('trials', 'simplexes', or 'bests')
        file_path: Path to save the file. If None, creates default path
    
    Returns:
        str: Path where the file was saved
    """
    if file_path is None:
        if optimizer.results_dir is not None:
            os.makedirs(optimizer.results_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = os.path.join(optimizer.results_dir, f'history_{which}_{timestamp}.csv')
        else:
            file_path = f'history_{which}.csv'
    
    # Get the appropriate history
    df, _ = optimizer.history[which], optimizer.history[f'{which}_normed']
    
    # Save to CSV
    df.to_csv(file_path, index=False)
    
    return file_path

def write_optimization_info_to_file(optimizer, file_path=None):
    """
    Write optimization information to a JSON file.
    
    Args:
        optimizer: The NelderMead optimizer instance
        file_path: Path to save the file. If None, creates default path
    
    Returns:
        str: Path where the file was saved
    """
    if file_path is None:
        if optimizer.results_dir is not None:
            os.makedirs(optimizer.results_dir, exist_ok=True)
            file_path = os.path.join(optimizer.results_dir, 'optimization_info.json')
        else:
            file_path = 'optimization_info.json'
    
    # Get optimization info
    info = optimizer.optimization_info
    
    # Convert numpy types to Python types for JSON serialization
    def convert_types(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        elif isinstance(obj, dict):
            return {k: convert_types(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_types(item) for item in obj]
        elif callable(obj):
            # Convert callable objects to string representation
            return f"<function {obj.__name__ if hasattr(obj, '__name__') else 'callable'}>"
        elif isinstance(obj, type(None)):
            return None
        return obj
    
    info = convert_types(info)
    
    # Write to JSON with nice formatting
    with open(file_path, 'w') as f:
        json.dump(info, f, indent=2)
    
    return file_path

def write_best_parameters_to_file(optimizer, file_path=None):
    """
    Write best parameters to a CSV file.
    
    Args:
        optimizer: The NelderMead optimizer instance
        file_path: Path to save the file. If None, creates default path
    
    Returns:
        str: Path where the file was saved
    """
    if optimizer.best_parameters is None:
        raise ValueError("No best parameters found yet")
    
    if file_path is None:
        if optimizer.results_dir is not None:
            os.makedirs(optimizer.results_dir, exist_ok=True)
            file_path = os.path.join(optimizer.results_dir, 'best_parameters.csv')
        else:
            file_path = 'best_parameters.csv'
    
    # Create DataFrame with best parameters
    df = pd.DataFrame([
        {'name': name, 'value': value}
        for name, value in optimizer.best_parameters.items()
    ])
    
    # Save to CSV
    df.to_csv(file_path, index=False)
    
    return file_path

def write_current_population_to_file(optimizer, file_path=None):
    """
    Write current simplex (population) to a CSV file.
    
    Args:
        optimizer: The NelderMead optimizer instance
        file_path: Path to save the file. If None, creates default path
    
    Returns:
        str: Path where the file was saved
    """
    if file_path is None:
        if optimizer.results_dir is not None:
            os.makedirs(optimizer.results_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = os.path.join(optimizer.results_dir, f'current_simplex_{timestamp}.csv')
        else:
            file_path = 'current_simplex.csv'
    
    # Get current parameters DataFrame
    current_params = optimizer.current_parameters
    if current_params is None:
        raise ValueError("No current simplex available")
    
    # Add metrics
    current_params['metric'] = optimizer.simplex_metrics
    
    # Save to CSV
    current_params.to_csv(file_path, index=False)
    
    return file_path

# Import numpy for type conversion
import numpy as np