"""
Utility functions for Nelder-Mead optimization.

This module contains helper functions for history management, data conversion,
and callback execution.
"""

import numpy as np
import pandas as pd

def _update_history(optimizer):
    """
    Update the history arrays with current iteration data.
    
    Args:
        optimizer: The NelderMead optimizer instance
    """
    # Update simplex history
    optimizer.all_simplexes = np.concatenate([
        optimizer.all_simplexes,
        optimizer.simplex.reshape(1, optimizer.simplex_size, optimizer.nr_variable_parameters)
    ], axis=0)
    
    optimizer.all_simplexes_metrics = np.concatenate([
        optimizer.all_simplexes_metrics,
        optimizer.simplex_metrics.reshape(1, optimizer.simplex_size)
    ], axis=0)
    
    # Update best history
    optimizer.all_bests = np.vstack([optimizer.all_bests, optimizer.best.reshape(1, -1)])
    optimizer.all_bests_metrics = np.vstack([optimizer.all_bests_metrics, [[optimizer.best_metric]]])

def _get_history_as_df(optimizer, which='trials'):
    """
    Convert history arrays to DataFrames.
    
    Args:
        optimizer: The NelderMead optimizer instance
        which: Type of history to retrieve ('trials', 'simplexes', or 'bests')
    
    Returns:
        tuple: (denormalized_df, normalized_df)
    """
    if which == 'trials':
        if optimizer.all_trials.shape[0] == 0:
            return pd.DataFrame(), pd.DataFrame()
        
        # Create normalized DataFrame
        normed_df = pd.DataFrame(
            data=optimizer.all_trials,
            columns=optimizer.variable_parameters_names
        )
        normed_df['metric'] = optimizer.all_trials_metrics
        normed_df['iter'] = np.arange(1, len(normed_df) + 1)
        
        # Denormalize and descale
        params_df = optimizer.parameters.denormalize_and_descale_parameters_array(
            normed_df[optimizer.variable_parameters_names],
            include_fixed=True
        )
        
        # Create denormalized DataFrame
        df = params_df.copy()
        df['metric'] = normed_df['metric']
        df['iter'] = normed_df['iter']
        
        # Reorder columns
        df = df[['iter'] + optimizer.parameters_names + ['metric']]
        normed_df = normed_df[['iter'] + optimizer.variable_parameters_names + ['metric']]
        
        return df, normed_df
    
    elif which == 'simplexes':
        if optimizer.all_simplexes.shape[0] == 0:
            return pd.DataFrame(), pd.DataFrame()
        
        # Flatten simplex history
        all_data = []
        all_data_normed = []
        
        for iter_idx in range(optimizer.all_simplexes.shape[0]):
            for vertex_idx in range(optimizer.simplex_size):
                # Normalized data
                row_normed = {
                    'iter': iter_idx + 1,
                    'vertex': vertex_idx,
                    'metric': optimizer.all_simplexes_metrics[iter_idx, vertex_idx]
                }
                for param_idx, param_name in enumerate(optimizer.variable_parameters_names):
                    row_normed[param_name] = optimizer.all_simplexes[iter_idx, vertex_idx, param_idx]
                all_data_normed.append(row_normed)
                
                # Denormalized data
                vertex_data = optimizer.all_simplexes[iter_idx, vertex_idx, :]
                params_df = pd.DataFrame(columns=optimizer.variable_parameters_names, data=[vertex_data])
                params_denorm = optimizer.parameters.denormalize_and_descale_parameters_array(
                    params_df, include_fixed=True
                ).to_dict('records')[0]
                
                row = {
                    'iter': iter_idx + 1,
                    'vertex': vertex_idx,
                    'metric': optimizer.all_simplexes_metrics[iter_idx, vertex_idx]
                }
                row.update(params_denorm)
                all_data.append(row)
        
        df = pd.DataFrame(all_data)
        normed_df = pd.DataFrame(all_data_normed)
        
        # Reorder columns
        df = df[['iter', 'vertex'] + optimizer.parameters_names + ['metric']]
        normed_df = normed_df[['iter', 'vertex'] + optimizer.variable_parameters_names + ['metric']]
        
        return df, normed_df
    
    elif which == 'bests':
        if optimizer.all_bests.shape[0] == 0:
            return pd.DataFrame(), pd.DataFrame()
        
        # Create normalized DataFrame
        normed_df = pd.DataFrame(
            data=optimizer.all_bests,
            columns=optimizer.variable_parameters_names
        )
        normed_df['metric'] = optimizer.all_bests_metrics.flatten()
        normed_df['iter'] = np.arange(1, len(normed_df) + 1)
        
        # Denormalize and descale
        params_df = optimizer.parameters.denormalize_and_descale_parameters_array(
            normed_df[optimizer.variable_parameters_names],
            include_fixed=True
        )
        
        # Create denormalized DataFrame
        df = params_df.copy()
        df['metric'] = normed_df['metric']
        df['iter'] = normed_df['iter']
        
        # Reorder columns
        df = df[['iter'] + optimizer.parameters_names + ['metric']]
        normed_df = normed_df[['iter'] + optimizer.variable_parameters_names + ['metric']]
        
        return df, normed_df
    
    else:
        raise ValueError(f"Invalid 'which' parameter: {which}")

def _run_callbacks(optimizer, last_iteration=False):
    """
    Run the appropriate callbacks based on iteration state.
    
    Args:
        optimizer: The NelderMead optimizer instance
        last_iteration: Whether this is the last iteration
    """
    # Prepare common arguments for all callbacks (matching DE structure)
    callbacks_args = {
        'optimizer': optimizer,
        'iteration': optimizer.iter,
        'parameters': optimizer.current_parameters,
        'responses': optimizer.current_responses,
        'best_parameters': optimizer.best_parameters,
        'best_metric': optimizer.best_metric,
        'best_response': optimizer.best_response,
        'parameters_names': optimizer.parameters.parameters_names,
        'all_trials': optimizer.all_trials,
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

def _generate_spendley_points(optimizer):
    """
    Generate initial simplex vertices using Spendley's method.
    
    Args:
        optimizer: The NelderMead optimizer instance
    
    Returns:
        numpy array: Initial simplex vertices in normalized space
    """
    n = optimizer.nr_variable_parameters
    
    # Determine edge length
    if isinstance(optimizer.initial_simplex_edge_length, (float, int)):
        edge_length = optimizer.initial_simplex_edge_length
    else:
        edge_length = optimizer.rng.uniform(
            optimizer.initial_simplex_edge_length[0],
            optimizer.initial_simplex_edge_length[1]
        )
    
    # Determine initial point
    if optimizer.initial_point is not None:
        if isinstance(optimizer.initial_point, str):
            # Load from file
            initial_point_df = pd.read_csv(optimizer.initial_point)
            if 'value' in initial_point_df.columns:
                initial_values = initial_point_df.set_index('name')['value'].to_dict()
            else:
                initial_values = initial_point_df.iloc[0].to_dict()
            
            # Create parameter DataFrame
            params_list = []
            for param_name in optimizer.parameters_names:
                if param_name in initial_values:
                    params_list.append({param_name: initial_values[param_name]})
                else:
                    # Use default if not provided
                    default_val = optimizer.parameters.all_parameters[
                        optimizer.parameters.all_parameters['name'] == param_name
                    ]['default'].iloc[0]
                    params_list.append({param_name: default_val})
            
            params_df = pd.DataFrame(params_list)
            
            # Normalize the initial point
            normalized = optimizer.parameters.scale_and_normalize_parameters_array(params_df)
            initial_point = normalized.values[0]
            
        elif isinstance(optimizer.initial_point, pd.DataFrame):
            # Normalize the DataFrame
            normalized = optimizer.parameters.scale_and_normalize_parameters_array(optimizer.initial_point)
            initial_point = normalized.values[0]
        else:
            # Assume it's already normalized
            initial_point = np.array(optimizer.initial_point)
    
    elif optimizer.defaults_in_initial_simplex:
        # Use default values
        default_values = []
        for param_name in optimizer.variable_parameters_names:
            default_val = optimizer.parameters.all_parameters[
                optimizer.parameters.all_parameters['name'] == param_name
            ]['default'].iloc[0]
            default_values.append(default_val)
        
        params_df = pd.DataFrame([default_values], columns=optimizer.variable_parameters_names)
        normalized = optimizer.parameters.scale_and_normalize_parameters_array(params_df)
        initial_point = normalized.values[0]
    
    else:
        # Use center of normalized space
        initial_point = np.full(n, 0.5)
    
    # Generate simplex vertices using Spendley's method
    vertices = np.zeros((n + 1, n))
    
    # Calculate coefficients for regular simplex
    p = edge_length / (n * np.sqrt(2)) * (np.sqrt(n + 1) - 1)
    q = edge_length / np.sqrt(2) * (np.sqrt(n + 1) + n - 1)
    
    if optimizer.initial_point_mode == 'corner':
        # Initial point is first vertex
        vertices[0] = initial_point
        
        # Generate other vertices
        for i in range(1, n + 1):
            vertices[i] = initial_point + p
            vertices[i, i-1] = initial_point[i-1] + q
    
    else:  # centroid
        # Initial point is centroid of simplex
        # First generate simplex around origin
        for i in range(1, n + 1):
            vertices[i] = p * np.ones(n)
            vertices[i, i-1] = q
        
        # Shift to center around initial point
        centroid = np.mean(vertices, axis=0)
        shift = initial_point - centroid
        vertices += shift
    
    # Ensure all vertices are within bounds [0, 1]
    for i in range(n + 1):
        vertices[i] = np.clip(vertices[i], 0, 1)
    
    return vertices