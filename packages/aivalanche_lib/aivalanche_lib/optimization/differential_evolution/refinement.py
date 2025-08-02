"""
Local refinement module for Differential Evolution.
Provides integration with local optimization methods like DLS.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple, Union
from ..damped_least_squares import DampedLeastSquares
from .refinement_modes import get_refinement_config, get_mode_description
import copy


def apply_local_refinement(de_instance, 
                          method: str = 'dls',
                          max_iterations: int = 50,
                          options: Optional[Dict[str, Any]] = None,
                          during_optimization: bool = False) -> Tuple[bool, Dict[str, Any]]:
    """
    Apply local refinement to the best solution found by DE.
    
    Note: Categorical parameters are automatically excluded from refinement
    as gradient-based methods like DLS cannot optimize discrete variables.
    
    Args:
        de_instance: The DifferentialEvolution instance
        method: Refinement method ('dls' currently supported)
        max_iterations: Maximum iterations for refinement
        options: Additional options for the refinement method
        during_optimization: If True, updates best trial instead of de_instance.best
        
    Returns:
        Tuple of (success, refinement_info)
    """
    if method != 'dls':
        raise ValueError(f"Unknown refinement method: {method}")
    
    # Create a modified parameters object that excludes categorical parameters
    # This ensures DLS only operates on continuous/discrete numeric parameters
    refinement_parameters = _create_refinement_parameters(de_instance)
    
    if refinement_parameters.nr_variable_parameters == 0:
        print("\n[INFO] No continuous/discrete parameters available for refinement.")
        print("      All parameters are categorical or fixed.")
        return False, {'method': method, 'improved': False, 'reason': 'no_refinable_parameters'}
    
    # Get current best solution (only non-categorical parameters)
    best_params_full = de_instance.best_parameters
    best_params_refinable = {k: v for k, v in best_params_full.items() 
                            if k in refinement_parameters.variable_parameters_names}
    best_point_df = pd.DataFrame([best_params_refinable])
    initial_metric = de_instance.best_metric
    
    print(f"\n{'='*60}")
    print(f"Starting local refinement with {method.upper()}")
    print(f"Initial metric: {initial_metric:.6e}")
    print(f"{'='*60}\n")
    
    # Set up DLS options
    dls_options = {
        'seed': de_instance.seed + 1000,  # Different seed
        'eval_func': _create_wrapped_eval_func(de_instance, refinement_parameters),
        'eval_func_args': de_instance.eval_func_args,
        'parameters': refinement_parameters,  # Use filtered parameters
        'opt_min_or_max': de_instance.opt_min_or_max,
        'max_iterations': max_iterations,
        'initial_point': best_point_df,
        'metric_threshold': de_instance.metric_threshold,
        
        # DLS-specific defaults for refinement
        'initial_damping': 0.01,
        'damping_increase_factor': 2.0,
        'damping_decrease_factor': 0.5,
        'gradient_tolerance': 1e-8,
        'parameter_tolerance': 1e-10,
        'jacobian_step_size': 1e-8,
        'residual_type': 'scalar',  # Default to scalar
        'use_qr_decomposition': True,
        'boundary_handling': 'reflect'
    }
    
    # Override with user options
    if options:
        dls_options.update(options)
    
    # Create and run DLS
    try:
        dls = DampedLeastSquares(**dls_options)
        dls.run_optimization()
        
        # Check if DLS improved the solution
        improved = False
        if de_instance.opt_min_or_max == 'min':
            improved = dls.best_metric < initial_metric
        else:
            improved = dls.best_metric > initial_metric
        
        refinement_info = {
            'method': method,
            'improved': improved,
            'initial_metric': initial_metric,
            'refined_metric': dls.best_metric,
            'improvement': abs(dls.best_metric - initial_metric),
            'relative_improvement': abs(dls.best_metric - initial_metric) / (abs(initial_metric) + 1e-10),
            'iterations': dls.iter,
            'evaluations': dls.nr_evaluations,
            'stop_reason': dls.stop_reason,
            'refined_parameters': _merge_refined_parameters(de_instance, dls.best_parameters),
            'optimizer_instance': dls
        }
        
        # Update DE instance if improved
        if improved:
            if during_optimization:
                # During optimization: update the best trial but not de_instance.best
                # Find the best trial to refine
                if de_instance.opt_min_or_max == 'min':
                    best_trial_idx = np.argmin(de_instance.trials_metrics)
                else:
                    best_trial_idx = np.argmax(de_instance.trials_metrics)
                
                # Update the best trial with refined solution
                # Convert parameters to normalized values for trials array
                refined_params_norm = de_instance.parameters.scale_and_normalize_parameters_array(
                    pd.DataFrame([dls.best_parameters])
                ).values.flatten()
                
                de_instance.trials[best_trial_idx] = refined_params_norm
                de_instance.trials_metrics[best_trial_idx] = dls.best_metric
                
                # Update current_responses for proper tracking
                if hasattr(de_instance, 'current_responses') and de_instance.current_responses:
                    de_instance.current_responses[best_trial_idx] = dls.best_response
                    de_instance.current_metrics[best_trial_idx] = dls.best_metric
            else:
                # After optimization: update de_instance.best as before
                de_instance.best_metric = dls.best_metric
                de_instance.best_parameters = _merge_refined_parameters(de_instance, dls.best_parameters)
                de_instance.best_response = dls.best_response
                de_instance.refinement_applied = True
                de_instance.refinement_info = refinement_info
            
            print(f"\n[SUCCESS] Refinement successful!")
            print(f"  Improved from {initial_metric:.6e} to {dls.best_metric:.6e}")
            print(f"  Relative improvement: {refinement_info['relative_improvement']:.2%}")
        else:
            print(f"\n[INFO] Refinement did not improve solution")
            print(f"  Best remains: {initial_metric:.6e}")
        
        return improved, refinement_info
        
    except Exception as e:
        print(f"\n[ERROR] Refinement failed: {str(e)}")
        refinement_info = {
            'method': method,
            'improved': False,
            'error': str(e),
            'initial_metric': initial_metric
        }
        return False, refinement_info


def should_trigger_refinement(de_instance, trigger_mode: str) -> bool:
    """
    Determine if refinement should be triggered.
    
    Args:
        de_instance: The DifferentialEvolution instance
        trigger_mode: When to trigger ('on_completion', 'on_stagnation', 'adaptive', 'both')
        
    Returns:
        bool: Whether to trigger refinement
    """
    # Handle 'both' mode - trigger during AND after optimization
    if trigger_mode == 'both':
        # Check if we should trigger during optimization
        if not de_instance.is_stop_criteria_reached:
            # Use adaptive logic during optimization
            return should_trigger_refinement(de_instance, 'adaptive')
        else:
            # Always trigger after optimization completes (if not already applied at the end)
            return not getattr(de_instance, '_refinement_applied_at_end', False)
    
    # Don't trigger if already applied (unless adaptive mode allows multiple)
    if de_instance.refinement_applied and trigger_mode not in ['adaptive', 'both']:
        return False
    
    if trigger_mode == 'on_completion':
        # Only trigger when DE is done
        return de_instance.is_stop_criteria_reached
    
    elif trigger_mode == 'on_stagnation':
        # Trigger when DE has stagnated for a while
        stagnation_threshold = getattr(de_instance, 'refinement_stagnation_threshold', 
                                      max(10, de_instance.max_iter_without_improvement // 2))
        stagnated = de_instance.iter_no_improvement >= stagnation_threshold
        
        # Additional check: must have run for minimum iterations
        min_iter = max(20, de_instance.pop_size)
        return stagnated and de_instance.iter >= min_iter
    
    elif trigger_mode == 'adaptive':
        # Don't refine too frequently
        min_gap = max(20, de_instance.pop_size // 2)
        if de_instance.iter - de_instance._last_refinement_iter < min_gap:
            return False
        
        # Use configured interval or default
        period = getattr(de_instance, 'refinement_adaptive_interval', 
                        max(50, de_instance.max_iterations // 4))
        at_period = de_instance.iter > 0 and de_instance.iter % period == 0
        stagnating = de_instance.iter_no_improvement >= 15
        
        should_trigger = at_period or stagnating
        
        # Update last refinement iteration if triggering
        if should_trigger:
            de_instance._last_refinement_iter = de_instance.iter
        
        return should_trigger
    
    else:
        return False


def get_refinement_summary(refinement_info: Dict[str, Any]) -> str:
    """Generate a summary string of refinement results."""
    if not refinement_info:
        return "No refinement applied"
    
    if 'error' in refinement_info:
        return f"Refinement failed: {refinement_info['error']}"
    
    summary = f"Refinement with {refinement_info['method'].upper()}:\n"
    summary += f"  Initial metric: {refinement_info['initial_metric']:.6e}\n"
    summary += f"  Refined metric: {refinement_info['refined_metric']:.6e}\n"
    summary += f"  Improvement: {refinement_info['improvement']:.6e} "
    summary += f"({refinement_info['relative_improvement']:.2%})\n"
    summary += f"  Iterations: {refinement_info['iterations']}\n"
    summary += f"  Status: {'[IMPROVED]' if refinement_info['improved'] else '[NO IMPROVEMENT]'}"
    
    return summary


def _create_refinement_parameters(de_instance):
    """
    Create a modified Parameters object that excludes categorical parameters.
    
    Args:
        de_instance: DifferentialEvolution instance
        
    Returns:
        Parameters object with only continuous/discrete parameters marked as variable
    """
    # Deep copy the parameters to avoid modifying the original
    refinement_params = copy.deepcopy(de_instance.parameters)
    
    # Mark all categorical parameters as fixed
    param_types = refinement_params.all_parameters['type'].values
    param_modes = refinement_params.all_parameters['mode'].values
    
    for i, (ptype, mode) in enumerate(zip(param_types, param_modes)):
        if ptype == 'categorical' and mode == 'variable':
            # Change mode to fixed for categorical parameters
            refinement_params.all_parameters.loc[i, 'mode'] = 'fixed'
            if hasattr(refinement_params, 'all_parameters_scaled'):
                refinement_params.all_parameters_scaled.loc[i, 'mode'] = 'fixed'
            if hasattr(refinement_params, 'all_parameters_normed'):
                refinement_params.all_parameters_normed.loc[i, 'mode'] = 'fixed'
    
    # Force re-computation of cached properties
    if hasattr(refinement_params, '_variable_parameters_names'):
        del refinement_params._variable_parameters_names
    if hasattr(refinement_params, '_variable_parameters'):
        del refinement_params._variable_parameters
    
    return refinement_params


def _create_wrapped_eval_func(de_instance, refinement_parameters):
    """
    Create a wrapped evaluation function that handles parameter merging.
    
    The wrapped function receives only non-categorical parameters from DLS,
    merges them with the current categorical parameter values, and calls
    the original eval_func with the complete parameter set.
    
    Args:
        de_instance: DifferentialEvolution instance
        refinement_parameters: Parameters object with only refinable parameters
        
    Returns:
        Wrapped evaluation function
    """
    def wrapped_eval_func(parameters_df, **kwargs):
        # Get current best categorical parameter values
        categorical_params = {}
        for param_name in de_instance.variable_parameters_names:
            if param_name not in refinement_parameters.variable_parameters_names:
                # This is a categorical parameter
                categorical_params[param_name] = de_instance.best_parameters[param_name]
        
        # Merge categorical parameters with the refinable parameters from DLS
        if isinstance(parameters_df, pd.DataFrame):
            # Add categorical columns to the DataFrame
            for name, value in categorical_params.items():
                parameters_df[name] = value
        else:
            # Handle dict case
            parameters_df.update(categorical_params)
        
        # Call original eval_func with complete parameter set
        return de_instance.eval_func(parameters_df, **kwargs)
    
    return wrapped_eval_func


def _merge_refined_parameters(de_instance, refined_params):
    """
    Merge refined parameters with the original categorical parameters.
    
    Args:
        de_instance: DifferentialEvolution instance
        refined_params: Dictionary of refined parameter values (non-categorical only)
        
    Returns:
        Complete parameter dictionary including both refined and categorical values
    """
    # Start with current best parameters
    merged_params = de_instance.best_parameters.copy()
    
    # Update with refined values
    merged_params.update(refined_params)
    
    return merged_params