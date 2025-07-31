"""
Perturbation functions for the DifferentialEvolution class.

This module contains helper functions for implementing adaptive perturbation
to help escape local minima during optimization. The perturbation system includes:
- Smart parameter selection based on variance, stagnation, and importance
- Adaptive perturbation scaling
- Memory mechanism to track perturbation effectiveness
- Multiple predefined perturbation modes (auto, aggressive, conservative)

Parameter Selection Methods:
- 'random': Randomly selects parameters. Uses 'param_ratio' to determine how many.
- 'variance': Selects parameters with variance below 'sigma_threshold'. Ignores 'param_ratio'.
- 'smart': Intelligently selects parameters based on multiple criteria. Uses 'param_ratio' to determine how many.
- 'all': Selects all parameters for perturbation. Ignores 'param_ratio'.

Configuration Parameters:
- param_ratio: Float between 0 and 1, or tuple (min, max) for random selection. Used only for 'random' and 'smart' selection methods.
- population_ratio: Float between 0 and 1, or tuple (min, max) for random selection. Fraction of population to perturb.
- sigma_threshold: Float threshold for variance. Used only for 'variance' selection method.
- scale: Perturbation scale - can be 'adaptive', 'adaptive_strong', 'adaptive_weak', 'random', a fixed float, or tuple (min, max) for random range.

Note: All functions in this module are prefixed with an underscore (_) to indicate
they are internal implementation details not meant to be called directly from outside
the DifferentialEvolution class.
"""

import numpy as np
from typing import Dict, Any, Optional, List, Union
from .perturbation_modes import get_perturbation_config

__all__ = [
    '_setup_perturbation_config',
    '_apply_perturbation', 
    '_update_perturbation_effectiveness'
]

def _setup_perturbation_config(de_instance):
    """
    Setup perturbation configuration based on mode.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        
    Returns:
        None: Sets the _perturbation_active_config attribute
    """
    # Get configuration from perturbation_modes module
    base_config = get_perturbation_config(
        de_instance.perturbation_mode, 
        de_instance.perturbation_config
    )
    
    # Set active configuration
    de_instance._perturbation_active_config = base_config
    
    # Auto-adjust configuration based on problem characteristics if not 'off'
    if base_config is not None and de_instance.perturbation_mode != 'custom':
        de_instance._perturbation_active_config = _auto_adjust_config(de_instance, base_config.copy())


def _auto_adjust_config(de_instance, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Automatically adjust perturbation configuration based on problem characteristics.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        config: Base configuration dictionary
        
    Returns:
        dict: Adjusted configuration
    """
    # Adjust based on dimensionality
    if de_instance.nr_variable_parameters > 50:
        config['population_ratio'] *= 0.7  # Perturb fewer in high dimensions
        config['trigger_ratio'] *= 0.8  # Trigger earlier
    
    # Adjust based on population size
    if de_instance.pop_size < 50:
        config['population_ratio'] = max(0.4, config['population_ratio'])  # Ensure enough diversity
    
    # These adjustments will be made dynamically during optimization
    # based on convergence rate and other runtime metrics
    
    return config


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
    trigger_ratio = de_instance._perturbation_active_config.get('trigger_ratio', 0.5)
    trigger_threshold = int(de_instance.max_iter_without_improvement * trigger_ratio)
    
    return (de_instance.iter_no_improvement >= trigger_threshold and 
            de_instance.iter > 10)


def _get_current_parameter_stats(de_instance) -> Dict[str, np.ndarray]:
    """
    Get statistics for parameters in current population.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        
    Returns:
        dict: Dictionary with 'mean', 'std', 'min', 'max', 'median' arrays
    """
    # Use survivors for statistics as they represent the best current solutions
    return {
        'mean': np.mean(de_instance.trials, axis=0),
        'std': np.std(de_instance.trials, axis=0),
        'min': np.min(de_instance.trials, axis=0),
        'max': np.max(de_instance.trials, axis=0),
        'median': np.median(de_instance.trials, axis=0)
    }


def _get_parameter_recent_change(de_instance, param_idx: int, window: int = 10) -> float:
    """
    Calculate how much a parameter has changed in recent iterations.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        param_idx: Index of the parameter
        window: Number of recent iterations to consider
        
    Returns:
        float: Standard deviation of parameter means across recent iterations
    """
    if de_instance.iter < window:
        return 1.0  # High change assumed for early iterations
    
    # Get parameter values from recent history
    recent_start = max(0, len(de_instance.all_survivors) - window)
    recent_survivors = de_instance.all_survivors[recent_start:, :, param_idx]
    
    # Calculate change as std of means across iterations
    iter_means = np.mean(recent_survivors, axis=1)
    return np.std(iter_means)


def _calculate_cooldown_factor(de_instance, param_idx: int) -> float:
    """
    Calculate cooldown factor for a parameter.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        param_idx: Index of the parameter
        
    Returns:
        float: Cooldown factor between 0 and 1
    """
    if not de_instance._perturbation_active_config.get('memory_enabled', True):
        return 1.0
    
    cooldown_ratio = de_instance._perturbation_active_config.get('cooldown_ratio', 0.1)
    cooldown_iterations = de_instance.max_iter_without_improvement * cooldown_ratio
    
    iterations_since_perturbed = de_instance.iter - de_instance.perturbation_memory['param_last_perturbed_iter'][param_idx]
    
    if iterations_since_perturbed < cooldown_iterations:
        # Linear cooldown factor from 0 to 1
        return min(iterations_since_perturbed / cooldown_iterations, 1.0)
    
    return 1.0


def _select_parameters_for_perturbation(de_instance) -> np.ndarray:
    """
    Select which parameters to perturb based on the configured strategy.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        
    Returns:
        np.ndarray: Indices of parameters to perturb
    """
    selection_method = de_instance._perturbation_active_config.get('param_selection', 'smart')
    
    if selection_method == 'random':
        # Random selection - param_ratio must be a number
        n_params = _determine_n_params_to_perturb(de_instance, selection_method)
        return de_instance.rng.choice(de_instance.nr_variable_parameters, size=n_params, replace=False)
    
    elif selection_method == 'variance':
        # Select parameters with variance below threshold
        stats = _get_current_parameter_stats(de_instance)
        sigma_threshold = de_instance._perturbation_active_config.get('sigma_threshold', 0.01)
        # Get indices of parameters with std below threshold
        low_variance_params = np.where(stats['std'] < sigma_threshold)[0]
        # If no parameters below threshold, select the one with lowest variance
        if len(low_variance_params) == 0:
            return np.array([np.argmin(stats['std'])])
        return low_variance_params
    
    elif selection_method == 'smart':
        # Smart selection considering multiple factors
        return _smart_parameter_selection(de_instance)
    
    elif selection_method == 'all':
        # Select all parameters for perturbation
        return np.arange(de_instance.nr_variable_parameters)
    
    else:
        raise ValueError(f"Unknown parameter selection method: {selection_method}")


def _smart_parameter_selection(de_instance) -> np.ndarray:
    """
    Intelligently select parameters to perturb using multiple criteria.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        
    Returns:
        np.ndarray: Indices of parameters to perturb
    """
    stats = _get_current_parameter_stats(de_instance)
    scores = np.zeros(de_instance.nr_variable_parameters)
    
    for i in range(de_instance.nr_variable_parameters):
        # Low variance score (parameters that have converged)
        variance_score = 1.0 / (stats['std'][i] + 1e-8)
        
        # Stagnation score (parameters that haven't changed recently)
        recent_change = _get_parameter_recent_change(de_instance, i)
        stagnation_score = 1.0 / (recent_change + 1e-8)
        
        # Memory factors
        if de_instance._perturbation_active_config.get('memory_enabled', True):
            cooldown = _calculate_cooldown_factor(de_instance, i)
            success_history = 1.0 - de_instance.perturbation_memory['param_improvement_after_perturbation'][i] * 0.5
            reconvergence_penalty = 1.0 - de_instance.perturbation_memory['param_reconvergence_speed'][i] * 0.3
        else:
            cooldown = 1.0
            success_history = 1.0
            reconvergence_penalty = 1.0
        
        # Combined score
        scores[i] = (variance_score * stagnation_score * 
                    cooldown * success_history * reconvergence_penalty)
    
    # Determine how many parameters to perturb
    n_params = _determine_n_params_to_perturb(de_instance, 'smart')
    
    # Return indices of parameters with highest scores
    return np.argsort(scores)[-n_params:]


def _get_scalar_value(de_instance, config_value, default=0.3):
    """
    Get a single scalar value from configuration (follows pattern from _get_coefficient).
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
        print(f"Warning: Invalid configuration {config_value}. Using default {default}")
        return default


def _determine_n_params_to_perturb(de_instance, selection_method: str = None) -> int:
    """
    Determine number of parameters to perturb.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        selection_method: The parameter selection method being used
        
    Returns:
        int: Number of parameters to perturb
    """
    if selection_method is None:
        selection_method = de_instance._perturbation_active_config.get('param_selection', 'smart')
    
    # For variance method, the number is determined by threshold (handled in _select_parameters_for_perturbation)
    if selection_method == 'variance':
        raise ValueError("_determine_n_params_to_perturb should not be called for variance selection method")
    
    # For 'all' method, return all parameters
    if selection_method == 'all':
        return de_instance.nr_variable_parameters
    
    # For random and smart methods, param_ratio can be a number or tuple
    param_ratio = de_instance._perturbation_active_config.get('param_ratio', 0.3)
    
    if selection_method in ['random', 'smart']:
        # Use the helper function to get a single ratio value
        actual_ratio = _get_scalar_value(de_instance, param_ratio, default=0.3)
        
        # Calculate number of parameters
        n_params = int(de_instance.nr_variable_parameters * actual_ratio)
        return max(1, min(n_params, de_instance.nr_variable_parameters))
    
    else:
        # Default fallback
        return max(1, int(de_instance.nr_variable_parameters * 0.3))


def _calculate_perturbation_scale(de_instance, param_idx: int) -> float:
    """
    Calculate perturbation scale for a specific parameter.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        param_idx: Index of the parameter
        
    Returns:
        float: Perturbation scale
    """
    scale_config = de_instance._perturbation_active_config.get('scale', 'adaptive')
    
    if scale_config == 'random':
        # Random scale between 0 and 1
        return de_instance.rng.random()
    
    elif isinstance(scale_config, (int, float, tuple, list)):
        # Fixed scale or random from range
        return _get_scalar_value(de_instance, scale_config, default=0.1)
    
    elif scale_config in ['adaptive', 'adaptive_strong', 'adaptive_weak']:
        # Adaptive scale based on parameter statistics
        stats = _get_current_parameter_stats(de_instance)
        param_std = stats['std'][param_idx]
        param_range = de_instance.boundaries_range[param_idx]
        
        # Base scale relative to current spread and boundaries
        base_scale = max(param_std * 3, param_range * 0.5)
        
        # Progress factor (decrease perturbation as optimization progresses)
        progress_factor = 1.0 - (de_instance.iter / de_instance.max_iterations) * 0.5
        
        # Strength multipliers
        strength_multipliers = {
            'adaptive': 2,
            'adaptive_strong': 3,
            'adaptive_weak': 1
        }
        strength_mult = strength_multipliers.get(scale_config, 1.0)
        
        # Memory-based adjustment
        if de_instance._perturbation_active_config.get('memory_enabled', True):
            # Increase scale for parameters that reconverge quickly
            reconvergence_mult = 1.0 + de_instance.perturbation_memory['param_reconvergence_speed'][param_idx] * 0.5
            # Increase scale based on number of previous attempts
            attempt_mult = 1.0 + (de_instance.perturbation_memory['param_perturbation_count'][param_idx] * 0.1)
            memory_mult = reconvergence_mult * attempt_mult
        else:
            memory_mult = 1.0
        
        return base_scale * progress_factor * strength_mult * memory_mult
    
    else:
        # Default to adaptive
        print(f"Warning: Invalid scale configuration '{scale_config}'. Using 'adaptive'.")
        return _calculate_perturbation_scale(de_instance, param_idx)


def _apply_perturbation(de_instance):
    """
    Apply perturbation to selected parameters and population members.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        
    Returns:
        None: Modifies trials in place
    """
    if not _should_apply_perturbation(de_instance):
        return
    
    # Select parameters to perturb
    param_indices = _select_parameters_for_perturbation(de_instance)
    
    # Select population members to perturb
    pop_ratio_config = de_instance._perturbation_active_config.get('population_ratio', 0.3)
    pop_ratio = _get_scalar_value(de_instance, pop_ratio_config, default=0.3)
    n_members = max(1, int(de_instance.pop_size * pop_ratio))
    member_indices = de_instance.rng.choice(de_instance.pop_size, size=n_members, replace=False)
    
    # Store pre-perturbation metric for tracking improvement
    pre_perturbation_best = de_instance.best_metric
    
    # Print perturbation message
    print(f"\n{'='*60}")
    print(f"Applying perturbation (mode: {de_instance.perturbation_mode})")
    print(f"  Iteration: {de_instance.iter}")
    print(f"  Current best: {pre_perturbation_best:.6e}")
    print(f"  No improvement for: {de_instance.iter_no_improvement} iterations")
    print(f"  Perturbing: {len(param_indices)} parameters, {n_members} population members")
    param_names = [de_instance.variable_parameters_names[i] for i in param_indices]
    if len(param_names) <= 5:
        print(f"  Parameters: {', '.join(param_names)}")
    else:
        print(f"  Parameters: {', '.join(param_names[:3])}, ... ({len(param_names)} total)")
    print(f"{'='*60}\n")
    
    # Apply perturbations
    for param_idx in param_indices:
        scale = _calculate_perturbation_scale(de_instance, param_idx)
        
        for member_idx in member_indices:
            # Generate perturbation
            perturbation = de_instance.rng.normal(0, scale)
            
            # Apply perturbation and ensure boundaries
            new_value = de_instance.trials[member_idx, param_idx] + perturbation
            new_value = np.clip(new_value, 0, 1)  # Keep within [0, 1] normalized range
            
            # Update the trials
            de_instance.trials[member_idx, param_idx] = new_value
    
    # Update memory
    _update_perturbation_memory(de_instance, param_indices, pre_perturbation_best)
    
    # Log perturbation event
    if de_instance.callback_after_each_iter:
        perturbation_info = {
            'iteration': de_instance.iter,
            'parameters_perturbed': [de_instance.variable_parameters_names[i] for i in param_indices],
            'members_perturbed': len(member_indices),
            'trigger_reason': f'no improvement for {de_instance.iter_no_improvement} iterations'
        }
        # Could be passed to callback or logged


def _update_perturbation_memory(de_instance, param_indices: np.ndarray, pre_perturbation_metric: float):
    """
    Update perturbation memory after applying perturbations.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        param_indices: Indices of parameters that were perturbed
        pre_perturbation_metric: Best metric value before perturbation
        
    Returns:
        None: Updates memory in place
    """
    # Update counters
    de_instance.perturbation_memory['last_perturbation_iter'] = de_instance.iter
    de_instance.perturbation_memory['perturbations_applied'] += 1
    
    # Update per-parameter information
    for param_idx in param_indices:
        de_instance.perturbation_memory['param_perturbation_count'][param_idx] += 1
        de_instance.perturbation_memory['param_last_perturbed_iter'][param_idx] = de_instance.iter
    
    # Record event in history
    event = {
        'iteration': de_instance.iter,
        'parameters': param_indices.tolist(),
        'pre_metric': pre_perturbation_metric,
        'post_metric': None  # Will be updated after evaluation
    }
    de_instance.perturbation_memory['history'].append(event)
    
    # Note: Improvement tracking and reconvergence speed will be updated
    # in subsequent iterations when we can measure the effect


def _update_perturbation_effectiveness(de_instance):
    """
    Update memory about perturbation effectiveness after evaluation.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        
    Returns:
        None: Updates memory in place
    """
    if not de_instance.perturbation_memory['history']:
        return
    
    # Check recent perturbation events for effectiveness
    for event in de_instance.perturbation_memory['history']:
        if event['post_metric'] is None and event['iteration'] < de_instance.iter:
            # Update post-perturbation metric
            event['post_metric'] = de_instance.best_metric
            
            # Calculate improvement
            if de_instance.opt_min_or_max == 'min':
                improved = event['post_metric'] < event['pre_metric']
            else:
                improved = event['post_metric'] > event['pre_metric']
            
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
            
            # Update parameter-specific improvement tracking
            for param_idx in event['parameters']:
                if improved:
                    # Exponential moving average
                    alpha = 0.3
                    de_instance.perturbation_memory['param_improvement_after_perturbation'][param_idx] = (
                        alpha * 1.0 + (1 - alpha) * 
                        de_instance.perturbation_memory['param_improvement_after_perturbation'][param_idx]
                    )
    
    # Update reconvergence speed (how quickly parameters return to low variance)
    if de_instance.iter > 20:
        stats = _get_current_parameter_stats(de_instance)
        for i in range(de_instance.nr_variable_parameters):
            iters_since = de_instance.iter - de_instance.perturbation_memory['param_last_perturbed_iter'][i]
            if 2 <= iters_since <= 20:  # Check reconvergence in a window
                if stats['std'][i] < 0.01:  # Parameter has reconverged
                    # Fast reconvergence indicates strong attractor
                    reconvergence_speed = 1.0 / (iters_since + 1)
                    # Exponential moving average
                    alpha = 0.3
                    de_instance.perturbation_memory['param_reconvergence_speed'][i] = (
                        alpha * reconvergence_speed + (1 - alpha) * 
                        de_instance.perturbation_memory['param_reconvergence_speed'][i]
                    )