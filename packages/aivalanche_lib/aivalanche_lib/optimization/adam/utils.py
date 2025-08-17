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
    
    This function first checks if gradients were provided in the eval_func response.
    If not, it falls back to numerical estimation methods.
    
    Args:
        optimizer: The Adam optimizer instance
    
    Returns:
        numpy array: Estimated gradient in normalized space
    """
    # Check if gradients were provided in the response
    if hasattr(optimizer, 'current_response') and optimizer.current_response is not None:
        if 'gradients' in optimizer.current_response:
            return _extract_provided_gradients(optimizer)
    
    # Check if gradient_method is 'provided' but no gradients were found
    if optimizer.gradient_method == 'provided':
        raise ValueError("gradient_method='provided' but no gradients found in eval_func response. "
                        "Expected response format: {'metric': value, 'gradients': {'param1': grad1, ...}}")
    
    # Fall back to numerical estimation
    if optimizer.gradient_method == 'finite_difference':
        return _finite_difference_gradient(optimizer)
    elif optimizer.gradient_method == 'central_difference':
        return _central_difference_gradient(optimizer)
    elif optimizer.gradient_method == 'simultaneous_perturbation':
        return _simultaneous_perturbation_gradient(optimizer)
    else:
        raise ValueError(f"Unknown gradient method: {optimizer.gradient_method}")


def _extract_provided_gradients(optimizer):
    """
    Extract gradients that were provided in the eval_func response.
    
    The gradients are expected to be in the denormalized parameter space,
    so they need to be transformed to the normalized space used internally.
    
    Args:
        optimizer: The Adam optimizer instance
    
    Returns:
        numpy array: Gradient in normalized space
    """
    provided_grads = optimizer.current_response['gradients']
    
    # Check that all variable parameters have gradients
    for param_name in optimizer.variable_parameters_names:
        if param_name not in provided_grads:
            if optimizer.gradient_method == 'provided':
                raise ValueError(f"Gradient for parameter '{param_name}' not provided")
            else:
                # Will need to estimate this gradient separately
                # For now, raise an error - full mixed mode would require more refactoring
                raise ValueError(f"Gradient for parameter '{param_name}' not provided. "
                               f"All gradients must be provided when using provided gradients.")
    
    # Get current parameter values in denormalized space
    current_denorm = optimizer.current_parameters
    
    # Use Parameters class to properly transform gradients to normalized space
    # This handles all the complexity of different scales (log, symlog, etc.)
    norm_grads = optimizer.parameters.norm_gradients(provided_grads, current_denorm)
    
    # Convert to numpy array in the correct order
    gradient = np.zeros(optimizer.nr_variable_parameters)
    for i, param_name in enumerate(optimizer.variable_parameters_names):
        gradient[i] = norm_grads[param_name]
    
    return gradient


def _finite_difference_gradient(optimizer):
    """
    Estimate gradient using finite differences with batch evaluation.
    
    This implementation creates all perturbed points at once and evaluates
    them in a single batch call to eval_func, which is much more efficient
    than the previous loop-based approach.
    
    Args:
        optimizer: The Adam optimizer instance
    
    Returns:
        numpy array: Gradient estimate
    """
    gradient = np.zeros(optimizer.nr_variable_parameters)
    base_point = optimizer.current_point.copy()
    base_metric = optimizer.current_metric
    
    # Create all perturbed points at once
    perturbed_points = []
    step_sizes = []
    
    for i in range(optimizer.nr_variable_parameters):
        # Determine step size
        if optimizer.gradient_step_size_relative:
            # Relative step size
            step = optimizer.gradient_step_size * max(abs(base_point[i]), 0.1)
        else:
            # Absolute step size
            step = optimizer.gradient_step_size
        
        step_sizes.append(step)
        
        # Forward difference
        perturbed_point = base_point.copy()
        perturbed_point[i] += step
        
        # Apply boundary constraints
        perturbed_point = optimizer._apply_boundary_constraints(perturbed_point)
        perturbed_points.append(perturbed_point)
    
    # Batch evaluate all perturbed points at once
    if len(perturbed_points) > 0:
        params_df = pd.DataFrame(perturbed_points, columns=optimizer.variable_parameters_names)
        denorm_params = optimizer.parameters.unnorm_all(params_df)
        
        # Single batch call to eval_func
        responses = optimizer.eval_func(denorm_params, **optimizer.eval_func_args)
        optimizer.nr_evaluations += len(perturbed_points)
        
        # Extract gradients from responses
        for i in range(optimizer.nr_variable_parameters):
            perturbed_metric = responses[i]['metric']
            
            # Add penalty if using penalty boundary handling
            if optimizer.boundary_handling == 'penalty':
                violations = np.maximum(0, -perturbed_points[i]) + np.maximum(0, perturbed_points[i] - 1)
                penalty = 1000 * np.sum(violations**2)
                perturbed_metric += penalty
            
            gradient[i] = (perturbed_metric - base_metric) / step_sizes[i]
    
    return gradient


def _central_difference_gradient(optimizer):
    """
    Estimate gradient using central differences with batch evaluation.
    
    Central differences is more accurate than forward differences as it uses
    both forward and backward perturbations: f'(x) ≈ [f(x+h) - f(x-h)] / (2h)
    
    This implementation evaluates all perturbed points in a single batch call.
    
    Args:
        optimizer: The Adam optimizer instance
    
    Returns:
        numpy array: Gradient estimate
    """
    gradient = np.zeros(optimizer.nr_variable_parameters)
    base_point = optimizer.current_point.copy()
    
    # Create all perturbed points at once (both forward and backward)
    perturbed_points = []
    step_sizes = []
    
    for i in range(optimizer.nr_variable_parameters):
        # Determine step size
        if optimizer.gradient_step_size_relative:
            # Relative step size
            step = optimizer.gradient_step_size * max(abs(base_point[i]), 0.1)
        else:
            # Absolute step size
            step = optimizer.gradient_step_size
        
        step_sizes.append(step)
        
        # Forward perturbation
        point_forward = base_point.copy()
        point_forward[i] += step
        point_forward = optimizer._apply_boundary_constraints(point_forward)
        
        # Backward perturbation
        point_backward = base_point.copy()
        point_backward[i] -= step
        point_backward = optimizer._apply_boundary_constraints(point_backward)
        
        # Add both to the batch
        perturbed_points.append(point_forward)
        perturbed_points.append(point_backward)
    
    # Batch evaluate all perturbed points at once
    if len(perturbed_points) > 0:
        params_df = pd.DataFrame(perturbed_points, columns=optimizer.variable_parameters_names)
        denorm_params = optimizer.parameters.unnorm_all(params_df)
        
        # Single batch call to eval_func for all perturbations
        responses = optimizer.eval_func(denorm_params, **optimizer.eval_func_args)
        optimizer.nr_evaluations += len(perturbed_points)
        
        # Extract gradients from responses (pairs of forward/backward)
        for i in range(optimizer.nr_variable_parameters):
            metric_forward = responses[2*i]['metric']
            metric_backward = responses[2*i + 1]['metric']
            
            # Add penalties if using penalty boundary handling
            if optimizer.boundary_handling == 'penalty':
                # Forward point penalty
                violations_forward = np.maximum(0, -perturbed_points[2*i]) + np.maximum(0, perturbed_points[2*i] - 1)
                penalty_forward = 1000 * np.sum(violations_forward**2)
                metric_forward += penalty_forward
                
                # Backward point penalty
                violations_backward = np.maximum(0, -perturbed_points[2*i + 1]) + np.maximum(0, perturbed_points[2*i + 1] - 1)
                penalty_backward = 1000 * np.sum(violations_backward**2)
                metric_backward += penalty_backward
            
            # Central difference formula
            gradient[i] = (metric_forward - metric_backward) / (2 * step_sizes[i])
    
    return gradient


def _simultaneous_perturbation_gradient(optimizer):
    """
    Estimate gradient using simultaneous perturbation (SPSA-like) with batch evaluation.
    
    This method evaluates both positive and negative perturbations in a single
    batch call to eval_func, reducing the number of function calls from 2 to 1.
    
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
    
    # Batch evaluate both perturbations at once
    perturbed_points = [point_plus, point_minus]
    params_df = pd.DataFrame(perturbed_points, columns=optimizer.variable_parameters_names)
    denorm_params = optimizer.parameters.unnorm_all(params_df)
    
    # Single batch call to eval_func for both perturbations
    responses = optimizer.eval_func(denorm_params, **optimizer.eval_func_args)
    optimizer.nr_evaluations += 2
    
    metric_plus = responses[0]['metric']
    metric_minus = responses[1]['metric']
    
    # Add penalties if using penalty boundary handling
    if optimizer.boundary_handling == 'penalty':
        # Plus point penalty
        violations_plus = np.maximum(0, -point_plus) + np.maximum(0, point_plus - 1)
        penalty_plus = 1000 * np.sum(violations_plus**2)
        metric_plus += penalty_plus
        
        # Minus point penalty
        violations_minus = np.maximum(0, -point_minus) + np.maximum(0, point_minus - 1)
        penalty_minus = 1000 * np.sum(violations_minus**2)
        metric_minus += penalty_minus
    
    # Compute gradient estimate
    gradient = (metric_plus - metric_minus) / (2 * steps) * delta
    
    return gradient