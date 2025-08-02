"""
Utility functions for ADAM optimization.

This module contains helper functions for history management, gradient estimation,
and callback execution.
"""

import numpy as np
import pandas as pd


def _update_history(optimizer):
    """
    Update the history arrays with current iteration data.
    
    Args:
        optimizer: The Adam optimizer instance
    """
    # Update point history
    optimizer.all_points = np.vstack([optimizer.all_points, optimizer.current_point.reshape(1, -1)])
    optimizer.all_metrics = np.append(optimizer.all_metrics, optimizer.current_metric)
    
    # Update gradient history
    if hasattr(optimizer, 'gradient') and optimizer.gradient is not None:
        optimizer.all_gradients = np.vstack([optimizer.all_gradients, optimizer.gradient.reshape(1, -1)])
        optimizer.all_gradient_norms = np.append(optimizer.all_gradient_norms, optimizer.gradient_norm)


def _get_history_as_df(optimizer, which='points'):
    """
    Convert history arrays to DataFrames.
    
    Args:
        optimizer: The Adam optimizer instance
        which: Type of history to retrieve ('points' or 'gradients')
    
    Returns:
        tuple: (denormalized_df, normalized_df)
    """
    if which == 'points':
        if optimizer.all_points.shape[0] == 0:
            return pd.DataFrame(), pd.DataFrame()
        
        # Create normalized DataFrame
        normed_df = pd.DataFrame(
            data=optimizer.all_points,
            columns=optimizer.variable_parameters_names
        )
        normed_df['metric'] = optimizer.all_metrics
        normed_df['iter'] = np.arange(1, len(normed_df) + 1)
        
        # Denormalize and descale
        params_df = optimizer.parameters.unnorm_all(
            normed_df[optimizer.variable_parameters_names]
        )
        
        # Create denormalized DataFrame
        df = params_df.copy()
        df['metric'] = normed_df['metric']
        df['iter'] = normed_df['iter']
        
        # Reorder columns
        df = df[['iter'] + optimizer.parameters.names + ['metric']]
        normed_df = normed_df[['iter'] + optimizer.variable_parameters_names + ['metric']]
        
        return df, normed_df
    
    elif which == 'gradients':
        if optimizer.all_gradients.shape[0] == 0:
            return pd.DataFrame(), pd.DataFrame()
        
        # Create gradient DataFrame
        grad_df = pd.DataFrame(
            data=optimizer.all_gradients,
            columns=[f'grad_{name}' for name in optimizer.variable_parameters_names]
        )
        grad_df['gradient_norm'] = optimizer.all_gradient_norms
        grad_df['iter'] = np.arange(1, len(grad_df) + 1)
        
        # Reorder columns
        grad_df = grad_df[['iter'] + [f'grad_{name}' for name in optimizer.variable_parameters_names] + ['gradient_norm']]
        
        return grad_df, grad_df  # No denormalization needed for gradients
    
    else:
        raise ValueError(f"Invalid 'which' parameter: {which}")


def _run_callbacks(optimizer, last_iteration=False):
    """
    Run the appropriate callbacks based on iteration state.
    
    Args:
        optimizer: The Adam optimizer instance
        last_iteration: Whether this is the last iteration
    """
    # Prepare common arguments for all callbacks
    callbacks_args = {
        'optimizer': optimizer,
        'iteration': optimizer.iter,
        'parameters': optimizer.current_parameters,
        'responses': optimizer.current_response,
        'best_parameters': optimizer.best_parameters,
        'best_metric': optimizer.best_metric,
        'best_response': optimizer.best_response,
        'parameters_names': optimizer.parameters.names,
        'gradient': optimizer.gradient,
        'gradient_norm': optimizer.gradient_norm,
        'stop_reason': optimizer.stop_reason,
        **optimizer.eval_func_args
    }
    
    if last_iteration:
        # Execute callback for the last iteration
        if optimizer.callback_after_last_iter is not None:
            optimizer.callback_after_last_iter(**callbacks_args)
    else:
        # Execute callback for the first iteration
        if optimizer.iter == 1 and optimizer.callback_after_first_iter is not None:
            optimizer.callback_after_first_iter(**callbacks_args)
        
        # Execute callback for each iteration
        if optimizer.callback_after_each_iter is not None:
            optimizer.callback_after_each_iter(**callbacks_args)
        
        # Execute callback when a better solution is found
        if optimizer.better_solution_found and optimizer.callback_after_better_solution is not None:
            optimizer.callback_after_better_solution(**callbacks_args)


def _estimate_gradient(optimizer):
    """
    Estimate the gradient at the current point.
    
    Args:
        optimizer: The Adam optimizer instance
    
    Returns:
        numpy array: Estimated gradient in normalized space
    """
    if optimizer.gradient_method == 'finite_difference':
        return _finite_difference_gradient(optimizer)
    elif optimizer.gradient_method == 'simultaneous_perturbation':
        return _simultaneous_perturbation_gradient(optimizer)
    else:
        raise ValueError(f"Unknown gradient method: {optimizer.gradient_method}")


def _finite_difference_gradient(optimizer):
    """
    Estimate gradient using finite differences.
    
    Args:
        optimizer: The Adam optimizer instance
    
    Returns:
        numpy array: Gradient estimate
    """
    gradient = np.zeros(optimizer.nr_variable_parameters)
    base_point = optimizer.current_point.copy()
    base_metric = optimizer.current_metric
    
    # For each parameter, estimate partial derivative
    for i in range(optimizer.nr_variable_parameters):
        # Determine step size
        if optimizer.gradient_step_size_relative:
            # Relative step size
            step = optimizer.gradient_step_size * max(abs(base_point[i]), 0.1)
        else:
            # Absolute step size
            step = optimizer.gradient_step_size
        
        # Forward difference
        perturbed_point = base_point.copy()
        perturbed_point[i] += step
        
        # Apply boundary constraints
        perturbed_point = optimizer._apply_boundary_constraints(perturbed_point)
        
        # Evaluate perturbed point
        params_df = pd.DataFrame([perturbed_point], columns=optimizer.variable_parameters_names)
        denorm_params = optimizer.parameters.unnorm_all(params_df)
        
        responses = optimizer.eval_func(denorm_params, **optimizer.eval_func_args)
        optimizer.nr_evaluations += 1
        perturbed_metric = responses[0]['metric']
        
        # Compute partial derivative
        gradient[i] = (perturbed_metric - base_metric) / step
    
    return gradient


def _simultaneous_perturbation_gradient(optimizer):
    """
    Estimate gradient using simultaneous perturbation (SPSA-like).
    
    Args:
        optimizer: The Adam optimizer instance
    
    Returns:
        numpy array: Gradient estimate
    """
    # Generate random perturbation vector
    delta = optimizer.rng.choice([-1, 1], size=optimizer.nr_variable_parameters)
    
    # Determine step size
    if optimizer.gradient_step_size_relative:
        # Relative step size for each parameter
        steps = optimizer.gradient_step_size * np.maximum(np.abs(optimizer.current_point), 0.1)
    else:
        # Absolute step size
        steps = optimizer.gradient_step_size * np.ones(optimizer.nr_variable_parameters)
    
    # Create perturbed points
    point_plus = optimizer.current_point + steps * delta
    point_minus = optimizer.current_point - steps * delta
    
    # Apply boundary constraints
    point_plus = optimizer._apply_boundary_constraints(point_plus)
    point_minus = optimizer._apply_boundary_constraints(point_minus)
    
    # Evaluate positive perturbation
    params_df_plus = pd.DataFrame([point_plus], columns=optimizer.variable_parameters_names)
    denorm_params_plus = optimizer.parameters.unnorm_all(params_df_plus)
    responses_plus = optimizer.eval_func(denorm_params_plus, **optimizer.eval_func_args)
    optimizer.nr_evaluations += 1
    metric_plus = responses_plus[0]['metric']
    
    # Evaluate negative perturbation
    params_df_minus = pd.DataFrame([point_minus], columns=optimizer.variable_parameters_names)
    denorm_params_minus = optimizer.parameters.unnorm_all(params_df_minus)
    responses_minus = optimizer.eval_func(denorm_params_minus, **optimizer.eval_func_args)
    optimizer.nr_evaluations += 1
    metric_minus = responses_minus[0]['metric']
    
    # Compute gradient estimate
    gradient = (metric_plus - metric_minus) / (2 * steps) * delta
    
    return gradient