"""
Local refinement module for Differential Evolution.
Provides integration with local optimization methods like DLS and Adam.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple, Union
from ..damped_least_squares import DampedLeastSquares
from ..adam import Adam
from ..nelder_mead import NelderMead
from ...parameters import Parameters
from .utils import _get_current_denormalized_boundaries
import copy


# Default configurations for each refinement method
_METHOD_DEFAULTS = {
    'common': {
        # Common parameters used by all methods
        'max_iter_without_improvement': 50,
        'improvement_threshold': 1e-8
    },
    'refinement': {
        # Default refinement configuration
        'method': 'dls',
        'trigger_ratio': 0.2,  # Trigger at 20% of max_iter_without_improvement
        'max_iterations': 1000,  # Allow more iterations for convergence
        
        # Metamodel-based refinement settings
        'use_metamodel': False,  # Whether to use metamodel for refinement (default: False)
        'metamodel_min_training_points': None,  # Min points for metamodel (None = pop_size)
        'metamodel_min_accuracy': 0.95  # Min R² for metamodel (0.95 for high accuracy in refinement)
    },
    'dls': {
        # DLS-specific defaults
        'initial_damping': 0.01,
        'damping_increase_factor': 10.0,
        'damping_decrease_factor': 0.1,
        'parameter_tolerance': 1e-10,
        'gradient_tolerance': 1e-8,
        'jacobian_step_size': 1e-8,
        'residual_type': 'scalar',
        'use_qr_decomposition': True,
        'boundary_handling': None
    },
    'adam': {
        # Adam-specific defaults - tuned for refinement
        'learning_rate': 0.001,  # Low learning rate for refinement
        'beta1': 0.9,
        'beta2': 0.999,
        'epsilon': 1e-8,
        'learning_rate_decay': 0.95,  # Fast decay for refinement
        'amsgrad': False,
        'gradient_tolerance': 1e-8,
        'gradient_method': 'finite_difference',
        'gradient_step_size': 1e-6,  # Small step for more accurate gradients
        'gradient_step_size_relative': True,
        'boundary_handling': None
    },
    'nelder_mead': {
        # Nelder-Mead specific defaults - tuned for refinement
        'reflection_coefficient': 1.0,
        'expansion_coefficient': 2.0,
        'contraction_coefficient': 0.5,
        'shrink_coefficient': 0.5,
        'initial_simplex_edge_length': 0.05,  # 5% of parameter range for refinement
        'defaults_in_initial_simplex': False,
        # Refinement-specific options (not NelderMead parameters)
        'initial_simplex_scale': 0.05,  # 5% of parameter range
        'initial_simplex_absolute_scale': None,  # Optional absolute scale
        'best_point_position': 'corner',  # 'corner' or 'centroid'
    }
}


def get_default_config():
    """
    Get the default configuration for refinement.
    
    Returns:
        dict: Default configuration parameters optimized for convergence
    """
    # Return refinement defaults from _METHOD_DEFAULTS
    config = _METHOD_DEFAULTS['refinement'].copy()
    # Add default options for the default method
    config['options'] = get_method_defaults(config['method'])
    return config


def get_method_defaults(method: str) -> dict:
    """
    Get default options for a specific refinement method.
    
    Args:
        method: The refinement method ('dls', 'adam', or 'nelder_mead')
        
    Returns:
        dict: Default options for the specified method
    """
    if method not in ['dls', 'adam', 'nelder_mead']:
        raise ValueError(f"Unknown refinement method: {method}")
    
    # Start with common defaults
    defaults = _METHOD_DEFAULTS['common'].copy()
    
    # Add method-specific defaults
    defaults.update(_METHOD_DEFAULTS[method])
    
    return defaults


def validate_config(config):
    """
    Validate refinement configuration.
    
    Args:
        config (dict): Configuration to validate
        
    Returns:
        dict: Validated configuration with user_options tracked separately
        
    Raises:
        ValueError: If configuration is invalid
    """
    default_config = get_default_config()
    
    # Start with default config
    validated = default_config.copy()
    
    # Deep copy the options
    validated['options'] = default_config['options'].copy()
    
    # Track user-provided options separately
    validated['user_options'] = {}
    
    # Update with user config
    if config:
        # Handle method
        if 'method' in config:
            if config['method'] not in ['dls', 'adam', 'nelder_mead']:
                raise ValueError(f"Only 'dls', 'adam', and 'nelder_mead' methods are supported, got: {config['method']}")
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
        
        # Handle metamodel-based refinement settings
        if 'use_metamodel' in config:
            validated['use_metamodel'] = bool(config['use_metamodel'])
        
        if 'metamodel_min_training_points' in config:
            validated['metamodel_min_training_points'] = config['metamodel_min_training_points']
        
        if 'metamodel_min_accuracy' in config:
            min_acc = config['metamodel_min_accuracy']
            if not (0 <= min_acc <= 1):
                raise ValueError("metamodel_min_accuracy must be between 0 and 1")
            validated['metamodel_min_accuracy'] = min_acc
        
        # Handle options - update full options AND track user options separately
        if 'options' in config and isinstance(config['options'], dict):
            validated['options'].update(config['options'])
            validated['user_options'] = config['options'].copy()
    
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


def _get_scale_tier(metric_value: float) -> tuple:
    """
    Determine the scale tier based on metric value.
    
    Returns:
        tuple: (tier_name, scale_factor)
    """
    if metric_value >= 1.0:
        return 'normal', 1.0
    elif metric_value >= 1e-3:
        return 'small', 1e-1
    elif metric_value >= 1e-6:
        return 'micro', 1e-2
    elif metric_value >= 1e-9:
        return 'nano', 1e-3
    elif metric_value >= 1e-12:
        return 'pico', 1e-4
    else:
        return 'extreme', 1e-5


def _adapt_adam_config_for_scale(optimizer_options: dict, initial_metric: float, 
                                 user_provided_options: set) -> None:
    """
    Adapt Adam optimizer configuration based on problem scale.
    
    Args:
        optimizer_options: The optimizer configuration dictionary (modified in-place)
        initial_metric: The initial metric value
        user_provided_options: Set of options explicitly provided by user
    """
    tier_name, scale_factor = _get_scale_tier(initial_metric)
    
    if tier_name == 'normal':
        # No adaptation needed for normal scale
        return
    
    print(f"\n[INFO] Detected {tier_name}-scale problem (metric={initial_metric:.2e})")
    
    # Adapt learning rate only if not user-specified
    if 'learning_rate' not in user_provided_options:
        original_lr = optimizer_options.get('learning_rate', 0.001)
        # Scale learning rate based on problem scale
        new_lr = original_lr * scale_factor
        optimizer_options['learning_rate'] = new_lr
        print(f"[INFO] Auto-adapting learning rate: {original_lr} -> {new_lr:.2e}")
    
    # Adapt gradient step size only if not user-specified
    if 'gradient_step_size' not in user_provided_options:
        original_gs = optimizer_options.get('gradient_step_size', 1e-6)
        # For very small scales, use even smaller gradient steps
        if tier_name in ['pico', 'extreme']:
            new_gs = 1e-10
        elif tier_name in ['nano']:
            new_gs = 1e-8
        else:
            new_gs = original_gs * scale_factor
        optimizer_options['gradient_step_size'] = new_gs
        print(f"[INFO] Auto-adapting gradient_step_size: {original_gs:.2e} -> {new_gs:.2e}")
    
    # Adapt epsilon only if not user-specified (important for numerical stability)
    if 'epsilon' not in user_provided_options and tier_name in ['nano', 'pico', 'extreme']:
        original_eps = optimizer_options.get('epsilon', 1e-8)
        # Scale epsilon for very small problems
        new_eps = original_eps * scale_factor
        optimizer_options['epsilon'] = new_eps
        print(f"[INFO] Auto-adapting epsilon: {original_eps:.2e} -> {new_eps:.2e}")
    
    # Adapt gradient tolerance for very small scales
    if 'gradient_tolerance' not in user_provided_options and tier_name in ['pico', 'extreme']:
        original_tol = optimizer_options.get('gradient_tolerance', 1e-8)
        new_tol = original_tol * scale_factor
        optimizer_options['gradient_tolerance'] = new_tol
        print(f"[INFO] Auto-adapting gradient_tolerance: {original_tol:.2e} -> {new_tol:.2e}")


def _adapt_dls_config_for_scale(optimizer_options: dict, initial_metric: float,
                                user_provided_options: set) -> None:
    """
    Adapt DLS optimizer configuration based on problem scale.
    
    Args:
        optimizer_options: The optimizer configuration dictionary (modified in-place)
        initial_metric: The initial metric value
        user_provided_options: Set of options explicitly provided by user
    """
    tier_name, scale_factor = _get_scale_tier(initial_metric)
    
    if tier_name == 'normal':
        # No adaptation needed for normal scale
        return
    
    print(f"\n[INFO] Detected {tier_name}-scale problem (metric={initial_metric:.2e})")
    
    # Adapt jacobian step size for numerical differentiation
    if 'jacobian_step_size' not in user_provided_options:
        original_js = optimizer_options.get('jacobian_step_size', 1e-8)
        # Scale based on problem scale
        if tier_name in ['pico', 'extreme']:
            new_js = 1e-12
        elif tier_name == 'nano':
            new_js = 1e-10
        else:
            new_js = original_js * scale_factor
        optimizer_options['jacobian_step_size'] = new_js
        print(f"[INFO] Auto-adapting jacobian_step_size: {original_js:.2e} -> {new_js:.2e}")
    
    # Adapt parameter tolerance
    if 'parameter_tolerance' not in user_provided_options:
        original_tol = optimizer_options.get('parameter_tolerance', 1e-10)
        new_tol = original_tol * scale_factor * scale_factor  # Square for more aggressive scaling
        optimizer_options['parameter_tolerance'] = new_tol
        print(f"[INFO] Auto-adapting parameter_tolerance: {original_tol:.2e} -> {new_tol:.2e}")
    
    # Adapt initial damping for very small scales
    if 'initial_damping' not in user_provided_options and tier_name in ['nano', 'pico', 'extreme']:
        original_damp = optimizer_options.get('initial_damping', 0.01)
        # Smaller initial damping for small-scale problems
        new_damp = original_damp * scale_factor
        optimizer_options['initial_damping'] = new_damp
        print(f"[INFO] Auto-adapting initial_damping: {original_damp:.2e} -> {new_damp:.2e}")


def _adapt_nelder_mead_config_for_scale(optimizer_options: dict, initial_metric: float,
                                       user_provided_options: set) -> None:
    """
    Adapt Nelder-Mead optimizer configuration based on problem scale.
    
    Args:
        optimizer_options: The optimizer configuration dictionary (modified in-place)
        initial_metric: The initial metric value
        user_provided_options: Set of options explicitly provided by user
    """
    tier_name, scale_factor = _get_scale_tier(initial_metric)
    
    if tier_name == 'normal':
        # No adaptation needed for normal scale
        return
    
    print(f"\n[INFO] Detected {tier_name}-scale problem (metric={initial_metric:.2e})")
    
    # Adapt initial simplex scale only if not user-specified
    if 'initial_simplex_scale' not in user_provided_options:
        original_scale = optimizer_options.get('initial_simplex_scale', 0.05)
        # For small-scale problems, use smaller initial simplex
        if tier_name in ['pico', 'extreme']:
            new_scale = 0.001  # 0.1% of range
        elif tier_name == 'nano':
            new_scale = 0.005  # 0.5% of range
        elif tier_name == 'micro':
            new_scale = 0.01   # 1% of range
        elif tier_name == 'small':
            new_scale = 0.02   # 2% of range
        else:
            new_scale = original_scale * scale_factor
        
        optimizer_options['initial_simplex_scale'] = new_scale
        print(f"[INFO] Auto-adapting initial_simplex_scale: {original_scale} -> {new_scale:.3f}")
        
    # Adapt improvement threshold for very small scales
    if 'improvement_threshold' not in user_provided_options and tier_name in ['pico', 'extreme']:
        original_tol = optimizer_options.get('improvement_threshold', 1e-8)
        new_tol = original_tol * scale_factor
        optimizer_options['improvement_threshold'] = new_tol
        print(f"[INFO] Auto-adapting improvement_threshold: {original_tol:.2e} -> {new_tol:.2e}")


def _build_optimizer_config(method: str, common_options: dict, options: dict = None) -> tuple:
    """
    Build optimizer configuration by merging common options, method defaults, and user options.
    
    Args:
        method: The optimization method ('dls' or 'adam')
        common_options: Common options for all optimizers
        options: User-provided options (optional)
        
    Returns:
        tuple: (optimizer_options, user_provided_options)
    """
    # Get method-specific defaults
    method_defaults = get_method_defaults(method)
    
    # Start with common options
    optimizer_options = common_options.copy()
    optimizer_options.update(method_defaults)
    
    # Track which options were explicitly provided by user
    user_provided_options = set()
    
    if options:
        # Apply user options (filter to only valid ones)
        for key, value in options.items():
            if key in optimizer_options:  # Check if it's a valid option
                optimizer_options[key] = value
                user_provided_options.add(key)
    
    return optimizer_options, user_provided_options


def _create_optimizer(method: str, optimizer_options: dict, initial_metric: float = None, 
                     best_point: pd.DataFrame = None, parameters: Parameters = None):
    """
    Create optimizer instance based on method.
    
    Args:
        method: The optimization method ('dls', 'adam', or 'nelder_mead')
        optimizer_options: The optimizer configuration
        initial_metric: Initial metric value (used for Adam adaptive scaling)
        best_point: Best point for Nelder-Mead initialization
        parameters: Parameters object for Nelder-Mead initialization
        
    Returns:
        Optimizer instance
    """
    if method == 'dls':
        return DampedLeastSquares(**optimizer_options)
    
    elif method == 'adam':
        return Adam(**optimizer_options)
    
    elif method == 'nelder_mead':
        # For Nelder-Mead, handle special refinement parameters
        nm_options = optimizer_options.copy()
        
        # Extract refinement-specific options that aren't NelderMead parameters
        best_point_position = nm_options.pop('best_point_position', 'corner')
        initial_simplex_scale = nm_options.pop('initial_simplex_scale', 0.05)
        initial_simplex_absolute_scale = nm_options.pop('initial_simplex_absolute_scale', None)
        
        # Set initial_point_mode based on best_point_position
        if best_point is not None:
            nm_options['initial_point'] = best_point
            nm_options['initial_point_mode'] = 'centroid' if best_point_position == 'centroid' else 'corner'
            
            # Handle simplex scale - convert from percentage to edge length
            if initial_simplex_absolute_scale is not None:
                # Use absolute scale if provided
                nm_options['initial_simplex_edge_length'] = initial_simplex_absolute_scale
            else:
                # Use relative scale (percentage of parameter range)
                nm_options['initial_simplex_edge_length'] = initial_simplex_scale
        
        return NelderMead(**nm_options)
    
    else:
        raise ValueError(f"Unknown refinement method: {method}")


def _apply_local_refinement(de_instance) -> Tuple[bool, Dict[str, Any]]:
    """
    Apply local refinement to the best solution found by DE.
    
    Note: Categorical parameters are automatically excluded from refinement
    as gradient-based methods like DLS and Adam cannot optimize discrete variables.
    
    Args:
        de_instance: The DifferentialEvolution instance
        
    Returns:
        Tuple of (success, refinement_info)
    """
    # Get configuration from de_instance
    config = de_instance._refinement_active_config
    method = config['method']
    max_iterations = config['max_iterations']
    # Use user_options to track what the user explicitly provided
    user_options = config.get('user_options', {})
    
    # Create a modified parameters object that excludes categorical parameters
    # This ensures DLS only operates on continuous/discrete numeric parameters
    refinement_parameters = _create_refinement_parameters(de_instance)
    
    if len(refinement_parameters.get_variable_parameters()) == 0:
        print("\n[INFO] No continuous/discrete parameters available for refinement.")
        print("      All parameters are categorical or fixed.")
        return False, {'method': method, 'improved': False, 'reason': 'no_refinable_parameters'}
    
    # Get current best solution (only non-categorical parameters)
    best_params_full = de_instance.best_parameters
    
    # If best_parameters is None, skip refinement
    if best_params_full is None:
        print("\n[INFO] No best solution available for refinement yet.")
        return False, {'method': method, 'improved': False, 'reason': 'no_best_solution'}
    
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
    
    # Check if we should use metamodel for refinement
    use_metamodel = config.get('use_metamodel', False)
    metamodel_eval_func = None
    using_metamodel = False
    
    if use_metamodel:
        # Import metamodel functions
        from .metamodels import check_metamodel_criteria, create_metamodel_eval_func
        
        # Get metamodel criteria from config
        min_points = config.get('metamodel_min_training_points')
        if min_points is None:
            min_points = de_instance.pop_size  # Default to pop_size
        min_accuracy = config.get('metamodel_min_accuracy', 0.95)
        
        # Check if metamodel criteria are met
        can_use, reason = check_metamodel_criteria(de_instance, min_points, min_accuracy)
        
        if can_use:
            # Get the metamodel manager (either regular or temporary)
            if hasattr(de_instance, 'metamodel_manager') and de_instance.metamodel_manager is not None:
                manager = de_instance.metamodel_manager
            elif hasattr(de_instance, '_temp_metamodel_manager'):
                manager = de_instance._temp_metamodel_manager
            else:
                # Should not happen if can_use is True
                print(f"[ERROR] Metamodel manager not found despite criteria being met")
                can_use = False
            
            if can_use:
                # Create metamodel evaluation function
                metamodel_eval_func = create_metamodel_eval_func(manager)
                using_metamodel = True
                print(f"[INFO] Using METAMODEL for refinement (accuracy: {manager.current_accuracy:.3f})")
        else:
            print(f"[INFO] Cannot use metamodel for refinement: {reason}")
            print(f"[INFO] Falling back to real evaluation function")
    
    # Common options for both optimizers
    common_options = {
        'seed': de_instance.seed + 1000,  # Different seed
        'eval_func': metamodel_eval_func if using_metamodel else de_instance.eval_func,
        'eval_func_args': {} if using_metamodel else (de_instance.eval_func_args if de_instance.eval_func_args else {}),
        'parameters': refinement_parameters,  # Use filtered parameters
        'opt_min_or_max': de_instance.opt_min_or_max,
        'max_iterations': max_iterations,
        'initial_point': best_point_df,
        'metric_threshold': de_instance.metric_threshold,
    }
    
    # Create and run optimizer based on method
    try:
        # Build optimizer configuration
        optimizer_options, user_provided_options = _build_optimizer_config(
            method, common_options, user_options
        )
        
        # Apply method-specific adaptations
        if method == 'adam':
            _adapt_adam_config_for_scale(optimizer_options, initial_metric, user_provided_options)
        elif method == 'dls':
            _adapt_dls_config_for_scale(optimizer_options, initial_metric, user_provided_options)
        elif method == 'nelder_mead':
            _adapt_nelder_mead_config_for_scale(optimizer_options, initial_metric, user_provided_options)
        
        # Create optimizer instance
        optimizer = _create_optimizer(method, optimizer_options, initial_metric, 
                                    best_point_df, refinement_parameters)
        
        # Run optimization
        optimizer.run_optimization()
        
        # If we used metamodel, validate the final result with real evaluation function
        if using_metamodel and optimizer.best_parameters is not None:
            print(f"\n[INFO] Validating metamodel-refined solution with real evaluation function...")
            
            # Prepare parameters for real evaluation
            best_params_df = pd.DataFrame([optimizer.best_parameters])
            
            # Call real evaluation function
            real_eval_func = de_instance.eval_func
            real_eval_args = de_instance.eval_func_args if de_instance.eval_func_args else {}
            real_response = real_eval_func(best_params_df, **real_eval_args)[0]
            real_metric = real_response['metric']
            
            # Report the difference
            metamodel_metric = optimizer.best_metric
            difference = abs(real_metric - metamodel_metric)
            rel_difference = difference / (abs(real_metric) + 1e-10)
            
            print(f"  Metamodel prediction: {metamodel_metric:.6e}")
            print(f"  Real evaluation:     {real_metric:.6e}")
            print(f"  Difference:          {difference:.6e} ({rel_difference:.2%})")
            
            # Update optimizer's best metric with the real value
            optimizer.best_metric = real_metric
            optimizer.best_response = real_response
            optimizer.nr_evaluations += 1  # Count the validation evaluation
        
        # Check if optimizer improved the solution
        improved = False
        if de_instance.opt_min_or_max == 'min':
            improved = optimizer.best_metric < initial_metric
        else:
            improved = optimizer.best_metric > initial_metric
        
        refinement_info = {
            'method': method,
            'improved': improved,
            'initial_metric': initial_metric,
            'refined_metric': optimizer.best_metric,
            'improvement': abs(optimizer.best_metric - initial_metric),
            'relative_improvement': abs(optimizer.best_metric - initial_metric) / (abs(initial_metric) + 1e-10),
            'iterations': optimizer.iter,
            'evaluations': optimizer.nr_evaluations,
            'stop_reason': optimizer.stop_reason,
            'refined_parameters': optimizer.best_parameters,
            'optimizer_instance': optimizer,
            'used_metamodel': using_metamodel
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
                    pd.DataFrame([optimizer.best_parameters])
                ).values.flatten()
                
                # Update survivors array
                de_instance.survivors[best_survivor_idx] = refined_params_norm
                de_instance.survivors_metrics[best_survivor_idx] = optimizer.best_metric
                
                # Also update the best solution tracking
                de_instance.best_metric = optimizer.best_metric
                de_instance.best_parameters = optimizer.best_parameters
                de_instance.best_response = optimizer.best_response
            else:
                # After optimization: update de_instance.best as before
                de_instance.best_metric = optimizer.best_metric
                de_instance.best_parameters = optimizer.best_parameters
                de_instance.best_response = optimizer.best_response
                de_instance.refinement_applied = True
                de_instance.refinement_info = refinement_info
            
            print(f"\n[SUCCESS] Refinement successful!")
            print(f"  Improved from {initial_metric:.6e} to {optimizer.best_metric:.6e}")
            print(f"  Relative improvement: {refinement_info['relative_improvement']:.2%}")
        else:
            print(f"\n[INFO] Refinement did not improve solution")
            print(f"  Best remains: {initial_metric:.6e}")
        
        # Record refinement in history
        _record_refinement_history(de_instance, refinement_info)
        
        # Clean up temporary metamodel manager if it was created
        if hasattr(de_instance, '_temp_metamodel_manager'):
            del de_instance._temp_metamodel_manager
        
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
        
        # Clean up temporary metamodel manager if it was created
        if hasattr(de_instance, '_temp_metamodel_manager'):
            del de_instance._temp_metamodel_manager
        
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
    with their current best values as defaults. Uses adaptive boundaries if active.
    
    Args:
        de_instance: DifferentialEvolution instance
        
    Returns:
        Parameters object with categorical parameters marked as fixed and
        current best values as defaults for all fixed parameters
    """
    # Get all parameters
    all_params = de_instance.parameters.parameters
    best_values = de_instance.best_parameters
    
    # If best_values is None, use parameter defaults
    if best_values is None:
        best_values = {}
    
    # Get current denormalized boundaries (adaptive or original)
    denorm_mins, denorm_maxs = _get_current_denormalized_boundaries(de_instance)
    
    # Create new parameter list with categorical parameters marked as fixed
    new_params = []
    for param in all_params:
        # Create parameter dict based on type
        if param.type == 'continuous':
            # Get bounds - use adaptive if available and parameter is variable
            if (param.mode == 'variable' and denorm_mins is not None and 
                param.name in denorm_mins):
                # Use adaptive boundaries (already denormalized)
                param_min = denorm_mins[param.name]
                param_max = denorm_maxs[param.name]
            else:
                # Use original boundaries
                param_min = param.min
                param_max = param.max
                
            param_dict = {
                'name': param.name,
                'type': 'continuous',
                'min': param_min,
                'max': param_max,
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
    
    # Log if adaptive boundaries were used
    if hasattr(de_instance, 'adaptive_boundaries_mode') and de_instance.adaptive_boundaries_mode != 'off':
        print("[INFO] Using adaptive boundaries for refinement parameters")
    
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