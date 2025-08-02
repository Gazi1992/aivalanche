"""
Utility functions for the DifferentialEvolution class.

This module contains helper functions for:
- Converting optimization history to DataFrames
- Processing boundary information
- Updating history tracking variables
- Managing adaptive boundaries
- Handling callback execution

Note: All functions in this module are prefixed with an underscore (_) to indicate
they are internal implementation details not meant to be called directly from outside
the DifferentialEvolution class.
"""

import numpy as np
import pandas as pd


def _update_history(de_instance):
    """
    Update history by appending current trial vectors, metrics, survivors, and survivor metrics.

    Args:
        de_instance: Instance of DifferentialEvolution

    Returns:
        None: Updates history attributes in the de_instance directly
    """
    # Append current trials to history
    trials_to_append = de_instance.trials.reshape(1, de_instance.pop_size, de_instance.nr_variable_parameters)
    de_instance.all_trials = np.vstack((de_instance.all_trials, trials_to_append))

    # Append current metrics to metrics history
    metrics_to_append = de_instance.trials_metrics.reshape(1, de_instance.pop_size)
    de_instance.all_trials_metrics = np.vstack((de_instance.all_trials_metrics, metrics_to_append))

    # Append current survivors to survivors history
    survivors_to_append = de_instance.survivors.reshape(1, de_instance.pop_size, de_instance.nr_variable_parameters)
    de_instance.all_survivors = np.vstack((de_instance.all_survivors, survivors_to_append))

    # Append current survivor metrics to survivor metrics history
    survivor_metrics_to_append = de_instance.survivors_metrics.reshape(1, de_instance.pop_size)
    de_instance.all_survivors_metrics = np.vstack((de_instance.all_survivors_metrics, survivor_metrics_to_append))

    # Append current best to bests history
    best_to_append = de_instance.best.reshape(1, de_instance.nr_variable_parameters)
    de_instance.all_bests = np.vstack((de_instance.all_bests, best_to_append))

    # Append current best metric to bests metrics history
    best_metric_to_append = de_instance.best_metric
    de_instance.all_bests_metrics = np.vstack((de_instance.all_bests_metrics, best_metric_to_append))


def _update_boundaries(de_instance):
    """
    Update the parameter boundaries based on population distribution using vectorized operations.

    This method implements adaptive boundaries by checking if a significant portion
    of the population is near the boundaries, and extending them if necessary.

    Args:
        de_instance: Instance of DifferentialEvolution

    Returns:
        None: Updates boundary attributes in the de_instance directly
    """
    # Skip if adaptive boundaries are not enabled
    if not de_instance.adaptive_boundaries:
        return

    # Skip if it's not time to check boundaries based on the period
    if de_instance.iter % de_instance.adaptive_boundaries_check_period != 0:
        return

    # Calculate quantiles for all parameters at once
    lower_quantiles = np.quantile(de_instance.survivors, 1 - de_instance.adaptive_boundaries_pop_quantile, axis=0)
    upper_quantiles = np.quantile(de_instance.survivors, de_instance.adaptive_boundaries_pop_quantile, axis=0)

    # Calculate thresholds for boundary extension
    lower_thresholds = de_instance.boundaries_min + de_instance.adaptive_boundaries_edge_threshold * de_instance.boundaries_range
    upper_thresholds = de_instance.boundaries_max - de_instance.adaptive_boundaries_edge_threshold * de_instance.boundaries_range

    # Check which parameters need boundary extensions
    lower_extension_mask = lower_quantiles < lower_thresholds
    upper_extension_mask = upper_quantiles > upper_thresholds

    # Flag to track if boundaries were changed
    boundaries_changed = False

    # Calculate new boundary values
    if np.any(lower_extension_mask):
        boundaries_changed = True
        # Extend lower boundaries where needed
        extension_amount = de_instance.adaptive_boundaries_extension * de_instance.boundaries_range[lower_extension_mask]
        new_mins = de_instance.boundaries_min[lower_extension_mask] - extension_amount

        # Log the parameters that were extended
        for i, param_idx in enumerate(np.where(lower_extension_mask)[0]):
            print(f"Extended lower boundary for parameter {param_idx} to {new_mins[i]}")

        # Update the boundaries
        de_instance.boundaries_min[lower_extension_mask] = new_mins

    if np.any(upper_extension_mask):
        boundaries_changed = True
        # Extend upper boundaries where needed
        extension_amount = de_instance.adaptive_boundaries_extension * de_instance.boundaries_range[upper_extension_mask]
        new_maxs = de_instance.boundaries_max[upper_extension_mask] + extension_amount

        # Log the parameters that were extended
        for i, param_idx in enumerate(np.where(upper_extension_mask)[0]):
            print(f"Extended upper boundary for parameter {param_idx} to {new_maxs[i]}")

        # Update the boundaries
        de_instance.boundaries_max[upper_extension_mask] = new_maxs

    # Update the range after modifying boundaries
    de_instance.boundaries_range = de_instance.boundaries_max - de_instance.boundaries_min

    # If boundaries were changed, add new entries to the boundaries history
    if boundaries_changed:
        # Create MultiIndex for the new entries
        new_index = pd.MultiIndex.from_product([[de_instance.iter], ['min', 'max', 'range']], names=['iter', 'type'])

        # Create DataFrame with current boundaries
        new_boundaries = pd.DataFrame(
            index=new_index,
            columns=de_instance.variable_parameters_names,
            dtype=float
        )

        # Set values
        new_boundaries.loc[(de_instance.iter, 'min'), :] = de_instance.boundaries_min
        new_boundaries.loc[(de_instance.iter, 'max'), :] = de_instance.boundaries_max
        new_boundaries.loc[(de_instance.iter, 'range'), :] = de_instance.boundaries_range

        # Append to the history
        de_instance.all_boundaries = pd.concat([de_instance.all_boundaries, new_boundaries])


def _get_history_as_df(de_instance, which='trials'):
    """
    Convert the optimization history to two DataFrames for analysis.

    Args:
        de_instance: Instance of DifferentialEvolution
        which (str): Which history to convert: 'trials', 'survivors', or 'bests'

    Returns:
        tuple: (df, df_normed)
            - df: DataFrame with iteration number, denormalized parameters, and metrics
            - df_normed: DataFrame with iteration number, normalized parameters, and metrics
    """
    if which not in ['trials', 'survivors', 'bests']:
        raise ValueError("'which' parameter must be 'trials', 'survivors', or 'bests'")

    # Select the appropriate arrays based on 'which' parameter
    if which == 'trials':
        values_array = de_instance.all_trials
        metrics_array = de_instance.all_trials_metrics
    elif which == 'survivors':
        values_array = de_instance.all_survivors
        metrics_array = de_instance.all_survivors_metrics
    else:  # bests
        values_array = de_instance.all_bests
        metrics_array = de_instance.all_bests_metrics

    if len(values_array) == 0:
        return pd.DataFrame(), pd.DataFrame()

    # Number of iterations
    n_iters = values_array.shape[0]

    # Special handling for bests which has a different shape
    if which == 'bests':
        # Create iteration column (one iteration number per best solution)
        iter_column = np.arange(1, n_iters + 1)

        # For bests, metrics_array might be a 2D array with one value per row
        # Ensure metrics_flat is a 1D array
        metrics_flat = metrics_array.flatten()

        # Reshape values to 2D array (n_iters, n_params) - bests already has the right shape
        values_normed_flat = values_array
    else:
        # Create iteration column (repeating each iteration number pop_size times)
        iter_column = np.repeat(np.arange(1, n_iters + 1), de_instance.pop_size)

        # Flatten metrics to 1D array
        metrics_flat = metrics_array.flatten()

        # Reshape values to 2D array (n_iters*pop_size, n_params)
        values_normed_flat = values_array.reshape(-1, de_instance.nr_variable_parameters)

    # Create DataFrame with normalized values
    df_normed = pd.DataFrame(
        values_normed_flat,
        columns=de_instance.variable_parameters_names
    )

    # Convert normalized values to original parameter values
    df_temp = pd.DataFrame(columns=de_instance.variable_parameters_names, data=values_normed_flat)
    df = de_instance.parameters.unnorm_all(df_temp)

    # Add iter and metric columns to both DataFrames
    # Insert iter as first column
    df_normed.insert(0, 'iter', iter_column)
    df.insert(0, 'iter', iter_column)

    # Add metric as last column
    df_normed['metric'] = metrics_flat
    df['metric'] = metrics_flat

    return df, df_normed


def _get_all_denormalized_boundaries(de_instance):
    """
    Get the denormalized boundary values for all iterations in history using vectorized operations.

    Args:
        de_instance: Instance of DifferentialEvolution

    Returns:
        pandas.DataFrame: DataFrame with multi-index (iter, type: 'min', 'max', 'range')
                         and columns for each parameter name, containing the
                         denormalized boundary values throughout optimization.
    """
    # Initialize result DataFrame with same structure as boundaries
    result = pd.DataFrame(
        index=de_instance.all_boundaries.index,
        columns=de_instance.variable_parameters_names,
        dtype=float
    )

    # Get all unique iterations
    iterations = de_instance.all_boundaries.index.get_level_values('iter').unique()

    # Extract all min boundaries at once
    all_mins = de_instance.all_boundaries.xs('min', level='type')

    # Extract all max boundaries at once
    all_maxs = de_instance.all_boundaries.xs('max', level='type')

    # Denormalize all min values at once (only variable parameters)
    denorm_mins = de_instance.parameters.unnorm_all(all_mins)
    # Remove fixed parameters from the result since we only want variable params
    denorm_mins = denorm_mins[de_instance.variable_parameters_names]

    # Denormalize all max values at once (only variable parameters)
    denorm_maxs = de_instance.parameters.unnorm_all(all_maxs)
    # Remove fixed parameters from the result since we only want variable params
    denorm_maxs = denorm_maxs[de_instance.variable_parameters_names]

    # Calculate the range in denormalized space
    denorm_ranges = denorm_maxs - denorm_mins

    # Store the denormalized values in the result DataFrame
    for iter_num in iterations:
        result.loc[(iter_num, 'min')] = denorm_mins.loc[iter_num]
        result.loc[(iter_num, 'max')] = denorm_maxs.loc[iter_num]
        result.loc[(iter_num, 'range')] = denorm_ranges.loc[iter_num]

    return result


def _run_callbacks(de_instance, last_iteration=False):
    """
    Execute the appropriate callback functions based on the current optimization state.

    Args:
        de_instance: Instance of DifferentialEvolution
        last_iteration (bool): Whether this is the final iteration of optimization

    Returns:
        None: Executes callback functions directly
    """
    # Prepare common arguments for all callbacks
    callbacks_args = {
        'optimizer': de_instance,
        'iteration': de_instance.iter,
        'parameters': de_instance.current_parameters,
        'responses': de_instance.current_responses,
        'best_parameters': de_instance.best_parameters,
        'best_metric': de_instance.best_metric,
        'best_response': de_instance.best_response,
        'parameters_names': de_instance.parameters.names,
        'all_trials': de_instance.all_trials,
        'stop_reason': de_instance.stop_reason,
        **de_instance.eval_func_args
    }

    if last_iteration:
        # Execute callback for the last iteration
        if de_instance.callback_after_last_iter is not None:
            de_instance.callback_after_last_iter(**callbacks_args)
    else:
        # Execute callback for the first iteration
        if de_instance.iter == 1 and de_instance.callback_after_first_iter is not None:
            de_instance.callback_after_first_iter(**callbacks_args)

        # Execute callback for each iteration
        if de_instance.callback_after_each_iter is not None:
            de_instance.callback_after_each_iter(**callbacks_args)

        # Execute callback when a better solution is found
        if de_instance.better_solution_found and de_instance.callback_after_better_solution is not None:
            de_instance.callback_after_better_solution(**callbacks_args)
