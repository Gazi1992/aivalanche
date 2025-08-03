"""
Local refinement module for Differential Evolution.
Provides integration with local optimization methods like DLS.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple, Union
from ..damped_least_squares import DampedLeastSquares
from ...parameters import Parameters
import copy


def get_default_config():
    """
    Get the default configuration for refinement.
    
    Returns:
        dict: Default configuration parameters optimized for convergence
    """
    return {
        'method': 'dls',                # Only 'dls' supported for now
        'trigger_ratio': 0.2,           # Trigger at 20% of max_iter_without_improvement
        'max_iterations': 1000,         # Allow more iterations for convergence
        'options': {
            'initial_damping': 0.01,
            'damping_increase_factor': 10.0,
            'damping_decrease_factor': 0.1,
            'gradient_tolerance': 1e-10,
            'parameter_tolerance': 1e-10,
            'improvement_threshold': 1e-8,
            'max_iter_without_improvement': 50,  # Stop if no improvement
            'jacobian_step_size': 1e-8,
            'residual_type': 'scalar',
            'use_qr_decomposition': True,
            'boundary_handling': 'reflect'
        }
    }


def validate_config(config):
    """
    Validate refinement configuration.
    
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
    
    # Deep copy the options
    validated['options'] = default_config['options'].copy()
    
    # Update with user config
    if config:
        # Handle method
        if 'method' in config:
            if config['method'] != 'dls':
                raise ValueError(f"Only 'dls' method is currently supported, got: {config['method']}")
            validated['method'] = config['method']
        
        # Handle trigger_ratio
        if 'trigger_ratio' in config:
            trigger_ratio = config['trigger_ratio']
            if trigger_ratio != -1 and not (0 < trigger_ratio <= 1):
                raise ValueError("trigger_ratio must be between 0 and 1, or -1 for post-optimization only")
            validated['trigger_ratio'] = trigger_ratio
        
        # Handle max_iterations
        if 'max_iterations' in config:
            if not isinstance(config['max_iterations'], int) or config['max_iterations'] < 1:
                raise ValueError("max_iterations must be a positive integer")
            validated['max_iterations'] = config['max_iterations']
        
        # Handle options
        if 'options' in config and isinstance(config['options'], dict):
            validated['options'].update(config['options'])
    
    return validated


def _setup_refinement_config(de_instance):
    """
    Setup refinement configuration with defaults.
    
    Args:
        de_instance: Instance of DifferentialEvolution
        
    Returns:
        None: Sets the _refinement_active_config attribute
    """
    if de_instance.refinement_mode == 'off':
        de_instance._refinement_active_config = None
        return
    
    # Validate and set configuration
    try:
        de_instance._refinement_active_config = validate_config(de_instance.refinement_config)
    except Exception as e:
        print(f"\n[WARNING] Refinement configuration validation failed: {str(e)}")
        print("[WARNING] Setting refinement_mode to 'off'")
        de_instance.refinement_mode = 'off'
        de_instance._refinement_active_config = None
        return
    
    # Extract specific values for easier access
    config = de_instance._refinement_active_config
    de_instance.refinement_method = config['method']
    de_instance.refinement_max_iterations = config['max_iterations']
    de_instance.refinement_options = config['options']
    de_instance.refinement_trigger_ratio = config['trigger_ratio']


def _should_trigger_refinement(de_instance) -> bool:
    """
    Determine if refinement should be triggered.
    
    Args:
        de_instance: The DifferentialEvolution instance
        
    Returns:
        bool: Whether to trigger refinement
    """
    if de_instance.refinement_mode == 'off':
        return False
    
    trigger_ratio = de_instance.refinement_trigger_ratio
    
    # Post-optimization only mode
    if trigger_ratio == -1:
        return not de_instance.is_running
    
    # Always refine after optimization when mode is 'on'
    if not de_instance.is_running:
        return True
    
    # During optimization checks
    if de_instance.is_running:
        # Don't refine too frequently
        min_gap = max(20, de_instance.pop_size // 2)
        last_iter = getattr(de_instance, '_last_refinement_iter', -min_gap)
        if de_instance.iter - last_iter < min_gap:
            return False
        
        # Check if we've stagnated enough
        threshold = int(trigger_ratio * de_instance.max_iter_without_improvement)
        if de_instance.iter_no_improvement >= threshold:
            de_instance._last_refinement_iter = de_instance.iter
            return True
    
    return False


def _apply_local_refinement(de_instance) -> Tuple[bool, Dict[str, Any]]:
    """
    Apply local refinement to the best solution found by DE.
    
    Note: Categorical parameters are automatically excluded from refinement
    as gradient-based methods like DLS cannot optimize discrete variables.
    
    Args:
        de_instance: The DifferentialEvolution instance
        
    Returns:
        Tuple of (success, refinement_info)
    """
    # Get configuration from de_instance
    config = de_instance._refinement_active_config
    method = config['method']
    max_iterations = config['max_iterations']
    options = config['options']
    
    # Create a modified parameters object that excludes categorical parameters
    # This ensures DLS only operates on continuous/discrete numeric parameters
    refinement_parameters = _create_refinement_parameters(de_instance)
    
    if len(refinement_parameters.get_variable_parameters()) == 0:
        print("\n[INFO] No continuous/discrete parameters available for refinement.")
        print("      All parameters are categorical or fixed.")
        return False, {'method': method, 'improved': False, 'reason': 'no_refinable_parameters'}
    
    # Get current best solution (only non-categorical parameters)
    best_params_full = de_instance.best_parameters
    best_params_refinable = {k: v for k, v in best_params_full.items() if k in refinement_parameters.variable_names}
    best_point_df = pd.DataFrame([best_params_refinable])
    initial_metric = de_instance.best_metric
    
    # Info about parameters being refined
    if len(refinement_parameters.variable_names) < len(de_instance.variable_parameters_names):
        excluded_params = [p for p in de_instance.variable_parameters_names if p not in refinement_parameters.variable_names]
        print(f"\n[INFO] Refinement will optimize: {refinement_parameters.variable_names}")
        print(f"[INFO] Categorical parameters excluded: {excluded_params}")
    
    print(f"\n{'='*60}")
    print(f"Starting local refinement with {method.upper()}")
    print(f"Initial metric: {initial_metric:.6e}")
    print(f"{'='*60}\n")
    
    # Set up DLS options
    dls_options = {
        'seed': de_instance.seed + 1000,  # Different seed
        'eval_func': de_instance.eval_func,
        'eval_func_args': de_instance.eval_func_args if de_instance.eval_func_args else {},
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
            'refined_parameters': dls.best_parameters,
            'optimizer_instance': dls
        }
        
        # Update DE instance if improved
        if improved:
            if de_instance.is_running:
                # During optimization: update the survivor that corresponds to the best solution
                # At this point, survivors have been determined and best has been updated
                # Find which survivor is the best
                if de_instance.opt_min_or_max == 'min':
                    best_survivor_idx = np.argmin(de_instance.survivors_metrics)
                else:
                    best_survivor_idx = np.argmax(de_instance.survivors_metrics)
                
                # Update the best survivor with refined solution
                # Convert parameters to normalized values for survivors array
                refined_params_norm = de_instance.parameters.norm_all(
                    pd.DataFrame([dls.best_parameters])
                ).values.flatten()
                
                # Update survivors array
                de_instance.survivors[best_survivor_idx] = refined_params_norm
                de_instance.survivors_metrics[best_survivor_idx] = dls.best_metric
                
                # Also update the best solution tracking
                de_instance.best_metric = dls.best_metric
                de_instance.best_parameters = dls.best_parameters
                de_instance.best_response = dls.best_response
            else:
                # After optimization: update de_instance.best as before
                de_instance.best_metric = dls.best_metric
                de_instance.best_parameters = dls.best_parameters
                de_instance.best_response = dls.best_response
                de_instance.refinement_applied = True
                de_instance.refinement_info = refinement_info
            
            print(f"\n[SUCCESS] Refinement successful!")
            print(f"  Improved from {initial_metric:.6e} to {dls.best_metric:.6e}")
            print(f"  Relative improvement: {refinement_info['relative_improvement']:.2%}")
        else:
            print(f"\n[INFO] Refinement did not improve solution")
            print(f"  Best remains: {initial_metric:.6e}")
        
        # Record refinement in history
        _record_refinement_history(de_instance, refinement_info)
        
        return improved, refinement_info
        
    except Exception as e:
        print(f"\n[ERROR] Refinement failed: {str(e)}")
        refinement_info = {
            'method': method,
            'improved': False,
            'error': str(e),
            'initial_metric': initial_metric
        }
        
        # Record failed refinement in history
        _record_refinement_history(de_instance, refinement_info)
        
        return False, refinement_info




def _get_refinement_summary(refinement_info: Dict[str, Any]) -> str:
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
    Create a modified Parameters object that marks categorical parameters as fixed
    with their current best values as defaults.
    
    Args:
        de_instance: DifferentialEvolution instance
        
    Returns:
        Parameters object with categorical parameters marked as fixed and
        current best values as defaults for all fixed parameters
    """
    # Get all parameters
    all_params = de_instance.parameters.parameters
    best_values = de_instance.best_parameters
    
    # Create new parameter list with categorical parameters marked as fixed
    new_params = []
    for param in all_params:
        # Create parameter dict based on type
        if param.type == 'continuous':
            param_dict = {
                'name': param.name,
                'type': 'continuous',
                'min': param.min,
                'max': param.max,
                'default': best_values.get(param.name, param.default),  # Use current best value
                'scale': param.scale,
                'mode': param.mode,
                'description': param.description
            }
        elif param.type == 'discrete':
            param_dict = {
                'name': param.name,
                'type': 'discrete',
                'values': param.values,
                'default': best_values.get(param.name, param.default),  # Use current best value
                'mode': param.mode,
                'description': param.description
            }
        elif param.type == 'categorical':
            param_dict = {
                'name': param.name,
                'type': 'categorical',
                'values': param.categories,
                'default': best_values.get(param.name, param.default),  # Use current best value
                'mode': 'fixed',  # Always fixed for categorical in refinement
                'description': param.description
            }
        
        new_params.append(param_dict)
    
    # Create new Parameters object
    refinement_params = Parameters(new_params)
    
    return refinement_params



def _record_refinement_history(de_instance, refinement_info: Dict[str, Any]):
    """
    Record refinement event in the history.
    
    Args:
        de_instance: The DifferentialEvolution instance
        refinement_info: Information about the refinement
    """
    if not hasattr(de_instance, '_refinement_history'):
        de_instance._refinement_history = []
    
    # Create history entry
    history_entry = {
        'iteration': de_instance.iter,
        'evaluations': de_instance.nr_evaluations,
        'when': 'during' if de_instance.is_running else 'after',
        'method': refinement_info.get('method', 'unknown'),
        'improved': refinement_info.get('improved', False),
        'initial_metric': refinement_info.get('initial_metric'),
        'refined_metric': refinement_info.get('refined_metric'),
        'improvement': refinement_info.get('improvement'),
        'relative_improvement': refinement_info.get('relative_improvement'),
        'refinement_iterations': refinement_info.get('iterations'),
        'refinement_evaluations': refinement_info.get('evaluations'),
        'stop_reason': refinement_info.get('stop_reason'),
        'error': refinement_info.get('error', None)
    }
    
    de_instance._refinement_history.append(history_entry)


def get_refinement_history(de_instance) -> list:
    """
    Get the refinement history.
    
    Args:
        de_instance: The DifferentialEvolution instance
        
    Returns:
        list: List of refinement history entries
    """
    return getattr(de_instance, '_refinement_history', [])