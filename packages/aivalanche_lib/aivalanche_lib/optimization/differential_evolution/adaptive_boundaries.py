"""
Adaptive boundaries system for Differential Evolution.

This module implements the adaptive boundaries feature that dynamically adjusts
parameter boundaries based on population distribution during optimization.
"""

import numpy as np
import pandas as pd


def get_default_config():
    """
    Get the default configuration for adaptive boundaries.
    
    Returns:
        dict: Default configuration parameters
    """
    return {
        'edge_threshold': 0.05,    # How close to boundary is "edge" (5% of range)
        'pop_quantile': 0.7,       # Fraction of population needed at edge (70%)
        'extension': 0.1,          # How much to extend boundaries (10% of range)
        'check_period': 10         # Check every N iterations
    }


def should_update_boundaries(de_instance):
    """
    Check if boundaries should be updated based on current iteration and config.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        
    Returns:
        bool: True if boundaries should be checked/updated
    """
    if de_instance.adaptive_boundaries_mode == 'off':
        return False
        
    if de_instance._adaptive_boundaries_active_config is None:
        return False
        
    # Check if it's time based on the period
    return de_instance.iter % de_instance._adaptive_boundaries_active_config['check_period'] == 0


def update_boundaries(de_instance):
    """
    Update the parameter boundaries based on population distribution.
    
    This method implements adaptive boundaries by checking if a significant portion
    of the population is near the boundaries, and extending them if necessary.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        
    Returns:
        bool: True if boundaries were changed, False otherwise
    """
    if not should_update_boundaries(de_instance):
        return False
    
    config = de_instance._adaptive_boundaries_active_config
    
    # Calculate quantiles for all parameters at once
    lower_quantiles = np.quantile(de_instance.survivors, 1 - config['pop_quantile'], axis=0)
    upper_quantiles = np.quantile(de_instance.survivors, config['pop_quantile'], axis=0)
    
    # Calculate thresholds for boundary extension
    lower_thresholds = de_instance.boundaries_min + config['edge_threshold'] * de_instance.boundaries_range
    upper_thresholds = de_instance.boundaries_max - config['edge_threshold'] * de_instance.boundaries_range
    
    # Check which parameters need boundary extensions
    lower_extension_mask = lower_quantiles < lower_thresholds
    upper_extension_mask = upper_quantiles > upper_thresholds
    
    # Flag to track if boundaries were changed
    boundaries_changed = False
    
    # Calculate new boundary values
    if np.any(lower_extension_mask):
        boundaries_changed = True
        # Extend lower boundaries where needed
        extension_amount = config['extension'] * de_instance.boundaries_range[lower_extension_mask]
        new_mins = de_instance.boundaries_min[lower_extension_mask] - extension_amount
        
        # Log the parameters that were extended
        for i, param_idx in enumerate(np.where(lower_extension_mask)[0]):
            param_name = de_instance.variable_parameters_names[param_idx]
            print(f"Extended lower boundary for {param_name} to {new_mins[i]:.6f}")
        
        # Update the boundaries
        de_instance.boundaries_min[lower_extension_mask] = new_mins
    
    if np.any(upper_extension_mask):
        boundaries_changed = True
        # Extend upper boundaries where needed
        extension_amount = config['extension'] * de_instance.boundaries_range[upper_extension_mask]
        new_maxs = de_instance.boundaries_max[upper_extension_mask] + extension_amount
        
        # Log the parameters that were extended
        for i, param_idx in enumerate(np.where(upper_extension_mask)[0]):
            param_name = de_instance.variable_parameters_names[param_idx]
            print(f"Extended upper boundary for {param_name} to {new_maxs[i]:.6f}")
        
        # Update the boundaries
        de_instance.boundaries_max[upper_extension_mask] = new_maxs
    
    # Update the range after modifying boundaries
    if boundaries_changed:
        de_instance.boundaries_range = de_instance.boundaries_max - de_instance.boundaries_min
        _record_boundary_change(de_instance)
    
    return boundaries_changed


def _record_boundary_change(de_instance):
    """
    Record the current boundary values in the history.
    
    Args:
        de_instance: Instance of DifferentialEvolution
    """
    # Create MultiIndex for the new entries
    new_index = pd.MultiIndex.from_product(
        [[de_instance.iter], ['min', 'max', 'range']], 
        names=['iter', 'type']
    )
    
    # Create DataFrame with current boundaries
    new_boundaries = pd.DataFrame(
        index=new_index,
        columns=de_instance.variable_parameters_names,
        dtype=float
    )
    
    # Set values
    new_boundaries.loc[(de_instance.iter, 'min'), :] = de_instance.boundaries_min
    new_boundaries.loc[(de_instance.iter, 'max'), :] = de_instance.boundaries_max
    new_boundaries.loc[(de_instance.iter, 'range'), :] = de_instance.boundaries_range
    
    # Append to the history
    de_instance.all_boundaries = pd.concat([de_instance.all_boundaries, new_boundaries])


def get_boundary_statistics(de_instance):
    """
    Get statistics about boundary changes during optimization.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        
    Returns:
        dict: Statistics about boundary changes
    """
    if de_instance.all_boundaries.empty:
        return {
            'total_changes': 0,
            'parameters_changed': [],
            'iterations_with_changes': []
        }
    
    # Get all iterations except the initial one
    all_iters = de_instance.all_boundaries.index.get_level_values('iter').unique()
    change_iters = [i for i in all_iters if i > 0]
    
    # Track which parameters had changes
    parameters_changed = set()
    
    if len(change_iters) > 0:
        # Compare with initial boundaries
        initial_min = de_instance.all_boundaries.loc[(0, 'min'), :]
        initial_max = de_instance.all_boundaries.loc[(0, 'max'), :]
        
        for param in de_instance.variable_parameters_names:
            # Check if min or max changed at any iteration
            for iter_num in change_iters:
                if (de_instance.all_boundaries.loc[(iter_num, 'min'), param] != initial_min[param] or
                    de_instance.all_boundaries.loc[(iter_num, 'max'), param] != initial_max[param]):
                    parameters_changed.add(param)
    
    return {
        'total_changes': len(change_iters),
        'parameters_changed': list(parameters_changed),
        'iterations_with_changes': list(change_iters)
    }


def validate_config(config):
    """
    Validate adaptive boundaries configuration.
    
    Args:
        config (dict): Configuration to validate
        
    Returns:
        dict: Validated configuration
        
    Raises:
        ValueError: If configuration is invalid
    """
    default_config = get_default_config()
    
    # Start with default config
    validated = default_config.copy()
    
    # Update with user config
    if config:
        validated.update(config)
    
    # Validate edge_threshold
    if not 0 < validated['edge_threshold'] < 0.5:
        raise ValueError("edge_threshold must be between 0 and 0.5")
    
    # Validate pop_quantile
    if not 0 < validated['pop_quantile'] < 1:
        raise ValueError("pop_quantile must be between 0 and 1")
    
    # Validate extension
    if not 0 < validated['extension'] < 1:
        raise ValueError("extension must be between 0 and 1")
    
    # Validate check_period
    if not isinstance(validated['check_period'], int) or validated['check_period'] < 1:
        raise ValueError("check_period must be a positive integer")
    
    return validated