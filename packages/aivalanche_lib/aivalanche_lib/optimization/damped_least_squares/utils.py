"""
Utility functions for the DampedLeastSquares class.

This module contains helper functions for:
- Computing Jacobian matrices
- Computing residuals
- Updating damping factors
- Converting optimization history to DataFrames
- Handling callback execution

Note: All functions in this module are prefixed with an underscore (_) to indicate
they are internal implementation details not meant to be called directly from outside
the DampedLeastSquares class.
"""

import numpy as np
import pandas as pd
from typing import Optional, Tuple, Union


def _update_history(dls_instance):
    """
    Update history by appending current state.
    
    Args:
        dls_instance: Instance of DampedLeastSquares
        
    Returns:
        None: Updates history attributes in the dls_instance directly
    """
    # Append current point
    dls_instance.all_points.append(dls_instance.current_point.copy())
    
    # Append current metric
    dls_instance.all_metrics.append(dls_instance.current_metric)
    
    # Append residuals
    if dls_instance.current_residuals is not None:
        dls_instance.all_residuals.append(dls_instance.current_residuals.copy())
    
    # Append algorithm state
    dls_instance.all_damping_factors.append(dls_instance.damping_factor)
    dls_instance.all_gradient_norms.append(dls_instance.gradient_norm)
    dls_instance.all_step_norms.append(dls_instance.step_norm)


def _get_history_as_df(dls_instance, which='points'):
    """
    Convert the optimization history to DataFrames for analysis.
    
    Args:
        dls_instance: Instance of DampedLeastSquares
        which (str): Which history to convert (currently only 'points' is supported)
        
    Returns:
        tuple: (df, df_normed)
            - df: DataFrame with iteration number and denormalized parameters
            - df_normed: DataFrame with iteration number and normalized parameters
    """
    if which != 'points':
        raise ValueError("Only 'points' history is currently supported")
    
    if len(dls_instance.all_points) == 0:
        return pd.DataFrame(), pd.DataFrame()
    
    # Convert points list to numpy array
    points_array = np.array(dls_instance.all_points)
    n_iters = points_array.shape[0]
    
    # Create normalized DataFrame
    df_normed = pd.DataFrame(
        points_array,
        columns=dls_instance.variable_parameters_names
    )
    
    # Convert normalized values to original parameter values
    df = dls_instance.parameters.unnorm_all(df_normed.copy())
    
    # Add iteration column
    df_normed.insert(0, 'iter', range(1, n_iters + 1))
    df.insert(0, 'iter', range(1, n_iters + 1))
    
    # Add metric column
    df_normed['metric'] = dls_instance.all_metrics[:n_iters]
    df['metric'] = dls_instance.all_metrics[:n_iters]
    
    return df, df_normed


def _compute_jacobian(dls_instance) -> np.ndarray:
    """
    Compute the Jacobian matrix using batch evaluation or provided gradients.
    
    This implementation supports:
    1. Provided gradients/Jacobian from eval_func
    2. Batch finite differences (all perturbations evaluated at once)
    3. Central differences for better accuracy
    
    Args:
        dls_instance: Instance of DampedLeastSquares
        
    Returns:
        np.ndarray: Jacobian matrix (n_residuals x n_parameters) or gradient vector
    """
    # First check if gradients/Jacobian were provided in the response
    if hasattr(dls_instance, 'current_response') and dls_instance.current_response is not None:
        if isinstance(dls_instance.current_response, list) and len(dls_instance.current_response) > 0:
            response = dls_instance.current_response[0]
            
            # Check for provided Jacobian (for vector residuals)
            if 'jacobian' in response and dls_instance.residual_type == 'vector':
                return np.array(response['jacobian'])
            
            # Check for provided gradients (for scalar case)
            if 'gradients' in response and dls_instance.residual_type == 'scalar':
                return _extract_provided_gradients(dls_instance, response['gradients'])
    
    # Check if jacobian_method is 'provided' but no jacobian/gradients were found
    if dls_instance.jacobian_method == 'provided':
        if dls_instance.residual_type == 'vector':
            raise ValueError("jacobian_method='provided' but no 'jacobian' found in eval_func response")
        else:
            raise ValueError("jacobian_method='provided' but no 'gradients' found in eval_func response")
    
    n_params = dls_instance.nr_variable_parameters
    
    if dls_instance.jacobian_method == 'finite_difference':
        return _compute_jacobian_finite_difference_batch(dls_instance)
    elif dls_instance.jacobian_method == 'central_difference':
        return _compute_jacobian_central_difference_batch(dls_instance)
    elif dls_instance.jacobian_method == 'complex_step':
        # Complex step differentiation for higher accuracy
        if dls_instance.residual_type != 'vector':
            raise NotImplementedError("Complex step only implemented for vector residuals")
        raise NotImplementedError("Complex step differentiation not yet implemented")
    elif dls_instance.jacobian_method == 'automatic':
        # Automatic differentiation
        raise NotImplementedError("Automatic differentiation not yet implemented")
    else:
        raise ValueError(f"Unknown jacobian_method: {dls_instance.jacobian_method}")


def _extract_provided_gradients(dls_instance, gradients_dict):
    """
    Extract gradients that were provided in the eval_func response.
    
    The gradients are expected to be in the denormalized parameter space,
    so they need to be transformed to the normalized space used internally.
    
    Args:
        dls_instance: Instance of DampedLeastSquares
        gradients_dict: Dictionary of gradients from eval_func
    
    Returns:
        np.ndarray: Gradient in normalized space
    """
    # Get current parameter values in denormalized space
    current_denorm = dls_instance.current_parameters
    
    # Use Parameters class to properly transform gradients to normalized space
    norm_grads = dls_instance.parameters.norm_gradients(gradients_dict, current_denorm)
    
    # Convert to numpy array in the correct order
    gradient = np.zeros(dls_instance.nr_variable_parameters)
    for i, param_name in enumerate(dls_instance.variable_parameters_names):
        if param_name not in norm_grads:
            raise ValueError(f"Gradient for parameter '{param_name}' not provided")
        gradient[i] = norm_grads[param_name]
    
    return gradient


def _compute_jacobian_finite_difference_batch(dls_instance) -> np.ndarray:
    """
    Compute Jacobian using forward finite differences with batch evaluation.
    
    All perturbations are evaluated in a single batch call to eval_func.
    """
    n_params = dls_instance.nr_variable_parameters
    original_point = dls_instance.current_point.copy()
    
    # Create all perturbed points at once
    perturbed_points = []
    step_sizes = []
    
    for i in range(n_params):
        # Compute step size
        if dls_instance.jacobian_step_size_relative:
            h = dls_instance.jacobian_step_size * max(abs(original_point[i]), 1.0)
        else:
            h = dls_instance.jacobian_step_size
        
        step_sizes.append(h)
        
        # Forward perturbation
        perturbed_point = original_point.copy()
        perturbed_point[i] += h
        
        # Apply boundaries
        perturbed_point = dls_instance._apply_boundary_constraints(perturbed_point)
        perturbed_points.append(perturbed_point)
    
    # Batch evaluate all perturbed points
    if len(perturbed_points) > 0:
        # Convert to DataFrame for batch evaluation
        params_df = pd.DataFrame(perturbed_points, columns=dls_instance.variable_parameters_names)
        denorm_params = dls_instance.parameters.unnorm_all(params_df)
        
        # Single batch call to eval_func
        responses = dls_instance.eval_func(denorm_params, **dls_instance.eval_func_args)
        dls_instance.nr_evaluations += len(perturbed_points)
        
        # Build Jacobian from responses
        if dls_instance.residual_type == 'vector':
            n_residuals = len(dls_instance.current_residuals)
            jacobian = np.zeros((n_residuals, n_params))
            
            for i in range(n_params):
                perturbed_residuals = _compute_residuals(responses[i:i+1])
                jacobian[:, i] = (perturbed_residuals - dls_instance.current_residuals) / step_sizes[i]
        else:
            # For scalar case, compute gradient
            jacobian = np.zeros(n_params)
            original_metric = dls_instance.current_metric
            
            for i in range(n_params):
                perturbed_metric = responses[i]['metric']
                jacobian[i] = (perturbed_metric - original_metric) / step_sizes[i]
    
    return jacobian


def _compute_jacobian_central_difference_batch(dls_instance) -> np.ndarray:
    """
    Compute Jacobian using central finite differences with batch evaluation.
    
    More accurate than forward differences but requires 2N evaluations.
    All perturbations are evaluated in a single batch call.
    """
    n_params = dls_instance.nr_variable_parameters
    original_point = dls_instance.current_point.copy()
    
    # Create all perturbed points (forward and backward)
    perturbed_points = []
    step_sizes = []
    
    for i in range(n_params):
        # Compute step size
        if dls_instance.jacobian_step_size_relative:
            h = dls_instance.jacobian_step_size * max(abs(original_point[i]), 1.0)
        else:
            h = dls_instance.jacobian_step_size
        
        step_sizes.append(h)
        
        # Forward perturbation
        point_forward = original_point.copy()
        point_forward[i] += h
        point_forward = dls_instance._apply_boundary_constraints(point_forward)
        
        # Backward perturbation
        point_backward = original_point.copy()
        point_backward[i] -= h
        point_backward = dls_instance._apply_boundary_constraints(point_backward)
        
        # Add both to batch
        perturbed_points.append(point_forward)
        perturbed_points.append(point_backward)
    
    # Batch evaluate all perturbed points
    if len(perturbed_points) > 0:
        params_df = pd.DataFrame(perturbed_points, columns=dls_instance.variable_parameters_names)
        denorm_params = dls_instance.parameters.unnorm_all(params_df)
        
        # Single batch call to eval_func
        responses = dls_instance.eval_func(denorm_params, **dls_instance.eval_func_args)
        dls_instance.nr_evaluations += len(perturbed_points)
        
        # Build Jacobian from responses
        if dls_instance.residual_type == 'vector':
            n_residuals = len(dls_instance.current_residuals)
            jacobian = np.zeros((n_residuals, n_params))
            
            for i in range(n_params):
                forward_residuals = _compute_residuals(responses[2*i:2*i+1])
                backward_residuals = _compute_residuals(responses[2*i+1:2*i+2])
                jacobian[:, i] = (forward_residuals - backward_residuals) / (2 * step_sizes[i])
        else:
            # For scalar case, compute gradient
            jacobian = np.zeros(n_params)
            
            for i in range(n_params):
                forward_metric = responses[2*i]['metric']
                backward_metric = responses[2*i+1]['metric']
                jacobian[i] = (forward_metric - backward_metric) / (2 * step_sizes[i])
    
    return jacobian


def _compute_residuals(response: Union[dict, list]) -> np.ndarray:
    """
    Extract or compute residuals from evaluation response.
    
    Args:
        response: Response from eval_func
        
    Returns:
        np.ndarray: Residual vector
    """
    if isinstance(response, list) and len(response) > 0:
        if 'residuals' in response[0]:
            return np.array(response[0]['residuals'])
        elif 'metric' in response[0]:
            # Create artificial residual from metric
            metric = response[0]['metric']
            return np.array([np.sqrt(abs(metric))])
    
    raise ValueError("Cannot extract residuals from response")


def _update_damping_factor(current_damping: float, 
                          direction: str,
                          factor: float,
                          min_damping: float,
                          max_damping: float) -> float:
    """
    Update the damping factor based on step success.
    
    Args:
        current_damping: Current damping value
        direction: 'increase' or 'decrease'
        factor: Multiplication factor
        min_damping: Minimum allowed damping
        max_damping: Maximum allowed damping
        
    Returns:
        float: Updated damping factor
    """
    if direction == 'increase':
        new_damping = current_damping * factor
    elif direction == 'decrease':
        new_damping = current_damping / factor
    else:
        raise ValueError(f"Unknown direction: {direction}")
    
    # Clip to bounds
    return np.clip(new_damping, min_damping, max_damping)


def _run_callbacks(dls_instance, last_iteration=False):
    """
    Execute the appropriate callback functions based on the current optimization state.
    
    Args:
        dls_instance: Instance of DampedLeastSquares
        last_iteration (bool): Whether this is the final iteration
        
    Returns:
        None: Executes callback functions directly
    """
    # Prepare common arguments for all callbacks
    callbacks_args = {
        'optimizer': dls_instance,
        'iteration': dls_instance.iter,
        'parameters': dls_instance.current_parameters,
        'best_parameters': dls_instance.best_parameters,
        'best_metric': dls_instance.best_metric,
        'gradient_norm': dls_instance.gradient_norm,
        'damping_factor': dls_instance.damping_factor,
        'step_norm': dls_instance.step_norm,
        'parameters_names': dls_instance.parameters.names,
        'stop_reason': dls_instance.stop_reason,
        **dls_instance.eval_func_args
    }
    
    if last_iteration:
        # Execute callback for the last iteration
        if dls_instance.callback_after_last_iter is not None:
            dls_instance.callback_after_last_iter(**callbacks_args)
    else:
        # Execute callback for the first iteration
        if dls_instance.iter == 1 and dls_instance.callback_after_first_iter is not None:
            dls_instance.callback_after_first_iter(**callbacks_args)
        
        # Execute callback for each iteration
        if dls_instance.callback_after_each_iter is not None:
            dls_instance.callback_after_each_iter(**callbacks_args)
        
        # Execute callback when a better solution is found
        if dls_instance.better_solution_found and dls_instance.callback_after_better_solution is not None:
            dls_instance.callback_after_better_solution(**callbacks_args)