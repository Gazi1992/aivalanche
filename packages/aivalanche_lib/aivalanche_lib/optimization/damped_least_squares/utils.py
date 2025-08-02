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
    Compute the Jacobian matrix using finite differences or other methods.
    
    Args:
        dls_instance: Instance of DampedLeastSquares
        
    Returns:
        np.ndarray: Jacobian matrix (n_residuals x n_parameters) or gradient vector
    """
    n_params = dls_instance.nr_variable_parameters
    
    if dls_instance.jacobian_method == 'finite_difference':
        # Finite difference approximation
        if dls_instance.residual_type == 'vector':
            n_residuals = len(dls_instance.current_residuals)
            jacobian = np.zeros((n_residuals, n_params))
        else:
            # For scalar case, we compute gradient directly
            jacobian = np.zeros(n_params)
        
        # Save current state
        original_point = dls_instance.current_point.copy()
        original_metric = dls_instance.current_metric
        
        for i in range(n_params):
            # Compute step size
            if dls_instance.jacobian_step_size_relative:
                h = dls_instance.jacobian_step_size * max(abs(original_point[i]), 1.0)
            else:
                h = dls_instance.jacobian_step_size
            
            # Forward difference
            perturbed_point = original_point.copy()
            perturbed_point[i] += h
            
            # Apply boundaries
            perturbed_point = dls_instance._apply_boundary_constraints(perturbed_point)
            
            # Evaluate perturbed point
            perturbed_metric, perturbed_residuals = dls_instance._evaluate_point(perturbed_point)
            dls_instance.nr_evaluations += 1
            
            if dls_instance.residual_type == 'vector':
                # Jacobian column is derivative of residuals
                jacobian[:, i] = (perturbed_residuals - dls_instance.current_residuals) / h
            else:
                # Gradient element is derivative of metric
                jacobian[i] = (perturbed_metric - original_metric) / h
                
    elif dls_instance.jacobian_method == 'complex_step':
        # Complex step differentiation for higher accuracy
        if dls_instance.residual_type != 'vector':
            raise NotImplementedError("Complex step only implemented for vector residuals")
        
        n_residuals = len(dls_instance.current_residuals)
        jacobian = np.zeros((n_residuals, n_params))
        
        # Note: This requires the eval_func to handle complex parameters
        raise NotImplementedError("Complex step differentiation not yet implemented")
        
    elif dls_instance.jacobian_method == 'automatic':
        # Automatic differentiation
        raise NotImplementedError("Automatic differentiation not yet implemented")
    
    else:
        raise ValueError(f"Unknown jacobian_method: {dls_instance.jacobian_method}")
    
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