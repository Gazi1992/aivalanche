"""
Simplified perturbation functions for the DifferentialEvolution class.

This module implements a streamlined perturbation system to help escape local minima
during optimization. The system perturbs converged parameters (those with low variance)
by adding noise proportional to their current standard deviation.

Configuration Parameters:
- trigger_ratio: When to trigger perturbation (fraction of max_iter_without_improvement)
- std_threshold: Parameters with std below this are considered converged
- scale: Multiplier for std when generating perturbation noise
- population_ratio: Fraction of population to perturb

Note: All functions in this module are prefixed with an underscore (_) to indicate
they are internal implementation details not meant to be called directly from outside
the DifferentialEvolution class.
"""

import numpy as np
from typing import Dict, Any, Optional, Union

__all__ = [
    '_setup_perturbation_config',
    '_apply_perturbation', 
    '_update_perturbation_effectiveness'
]

def _setup_perturbation_config(de_instance):
    """
    Setup perturbation configuration with defaults.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        
    Returns:
        None: Sets the _perturbation_active_config attribute
    """
    if de_instance.perturbation_mode == 'off':
        de_instance._perturbation_active_config = None
        return
    
    # Set default configuration
    default_config = {
        'trigger_ratio': 0.2,
        'std_threshold': 0.05,
        'scale': (1.5, 4),
        'population_ratio': (0.6, 1.0)
    }
    
    # Override with user config if provided
    if de_instance.perturbation_config:
        default_config.update(de_instance.perturbation_config)
    
    de_instance._perturbation_active_config = default_config


def _should_apply_perturbation(de_instance) -> bool:
    """
    Check if perturbation should be applied in current iteration.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        
    Returns:
        bool: True if perturbation should be applied
    """
    if de_instance.perturbation_mode == 'off' or de_instance._perturbation_active_config is None:
        return False
    
    # Check if we've had enough iterations without improvement
    trigger_ratio = de_instance._perturbation_active_config.get('trigger_ratio', 0.2)
    trigger_threshold = int(de_instance.max_iter_without_improvement * trigger_ratio)
    
    return (de_instance.iter_no_improvement >= trigger_threshold and 
            de_instance.iter > 10)  # Don't perturb too early


def _get_scalar_value(de_instance, config_value, default=0.5):
    """
    Get a single scalar value from configuration.
    Handles fixed values or random selection from ranges.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        config_value: Configuration value - can be float, int, or tuple/list for range
        default: Default value to use if configuration is invalid
        
    Returns:
        float: Single scalar value
    """
    if isinstance(config_value, (float, int)):
        return float(config_value)
    elif isinstance(config_value, (tuple, list)) and len(config_value) == 2:
        return de_instance.rng.uniform(config_value[0], config_value[1])
    else:
        return default


def _apply_perturbation(de_instance):
    """
    Apply perturbation to converged parameters.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        
    Returns:
        None: Modifies trials in place
    """
    if not _should_apply_perturbation(de_instance):
        return
    
    config = de_instance._perturbation_active_config
    
    # Calculate standard deviation for each parameter
    param_stds = np.std(de_instance.trials, axis=0)
    
    # Select converged parameters (those with std below threshold)
    std_threshold = config.get('std_threshold', 0.05)
    converged_params = np.where(param_stds < std_threshold)[0]
    
    if len(converged_params) == 0:
        print(f"\n{'='*60}")
        print(f"Perturbation triggered but skipped")
        print(f"  Iteration: {de_instance.iter}")
        print(f"  No improvement for: {de_instance.iter_no_improvement} iterations")
        print(f"  Reason: No parameters have converged (std < {std_threshold})")
        print(f"{'='*60}\n")
        return
    
    # Select population members to perturb
    pop_ratio = _get_scalar_value(de_instance, config.get('population_ratio', (0.6, 1.0)))
    n_members = max(1, int(de_instance.pop_size * pop_ratio))
    member_indices = de_instance.rng.choice(de_instance.pop_size, size=n_members, replace=False)
    
    # Get scale for perturbation
    scale = _get_scalar_value(de_instance, config.get('scale', (1.5, 4)))
    
    # Store pre-perturbation metric for tracking
    pre_perturbation_best = de_instance.best_metric
    
    # Track perturbation for history
    if not hasattr(de_instance, '_perturbation_history'):
        de_instance._perturbation_history = []
    
    # Print perturbation message
    print(f"\n{'='*60}")
    print(f"Applying perturbation")
    print(f"  Iteration: {de_instance.iter}")
    print(f"  Current best: {pre_perturbation_best:.6e}")
    print(f"  No improvement for: {de_instance.iter_no_improvement} iterations")
    print(f"  Converged parameters: {len(converged_params)} (std < {std_threshold})")
    print(f"  Perturbing: {n_members} population members")
    print(f"  Perturbation scale: {scale:.2f}")
    
    param_names = [de_instance.variable_parameters_names[i] for i in converged_params]
    if len(param_names) <= 5:
        print(f"  Parameters: {', '.join(param_names)}")
    else:
        print(f"  Parameters: {', '.join(param_names[:3])}, ... ({len(param_names)} total)")
    print(f"{'='*60}\n")
    
    # Apply perturbations
    for param_idx in converged_params:
        # Perturbation scale is current std * scale factor
        perturbation_std = param_stds[param_idx] * scale
        
        for member_idx in member_indices:
            # Generate perturbation
            perturbation = de_instance.rng.normal(0, perturbation_std)
            
            # Apply perturbation and ensure boundaries
            new_value = de_instance.trials[member_idx, param_idx] + perturbation
            new_value = np.clip(new_value, 0, 1)  # Keep within [0, 1] normalized range
            
            # Update the trials
            de_instance.trials[member_idx, param_idx] = new_value
    
    # Update perturbation history
    de_instance._perturbation_history.append({
        'iteration': de_instance.iter,
        'parameters': converged_params.tolist(),
        'n_members': n_members,
        'scale': scale,
        'pre_metric': pre_perturbation_best,
        'post_metric': None  # Will be updated after evaluation
    })
    
    # Update basic tracking
    de_instance.perturbation_memory['last_perturbation_iter'] = de_instance.iter
    de_instance.perturbation_memory['perturbations_applied'] += 1


def _update_perturbation_effectiveness(de_instance):
    """
    Update perturbation effectiveness tracking after evaluation.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        
    Returns:
        None: Updates history in place
    """
    if not hasattr(de_instance, '_perturbation_history') or not de_instance._perturbation_history:
        return
    
    # Check the most recent perturbation event
    for event in de_instance._perturbation_history:
        if event['post_metric'] is None and event['iteration'] < de_instance.iter:
            # Update post-perturbation metric
            event['post_metric'] = de_instance.best_metric
            
            # Calculate improvement
            if de_instance.opt_min_or_max == 'min':
                improved = event['post_metric'] < event['pre_metric']
            else:
                improved = event['post_metric'] > event['pre_metric']
            
            event['improved'] = improved
            
            # Print effectiveness message (only for the most recent perturbation)
            if event['iteration'] == de_instance.iter - 1:
                if improved:
                    improvement = abs(event['post_metric'] - event['pre_metric'])
                    relative_improvement = improvement / (abs(event['pre_metric']) + 1e-10)
                    print(f"\n[SUCCESS] Perturbation effective!")
                    print(f"  Improved from {event['pre_metric']:.6e} to {event['post_metric']:.6e}")
                    print(f"  Relative improvement: {relative_improvement:.2%}\n")
                else:
                    print(f"\n[INFO] Perturbation did not improve solution")
                    print(f"  Best remains: {event['pre_metric']:.6e}\n")