"""
Operators for Nelder-Mead algorithm.

This module contains the core operators for the Nelder-Mead simplex method:
reflection, expansion, contraction, and shrinking operations.
"""

import numpy as np

def _compute_centroid(optimizer):
    """
    Compute the centroid of all vertices except the worst.
    
    Args:
        optimizer: The NelderMead optimizer instance
    """
    optimizer.centroid = np.mean(optimizer.simplex[:-1], axis=0)

def _sort_simplex(optimizer):
    """
    Sort simplex vertices by their metric values and update best/worst.
    
    Args:
        optimizer: The NelderMead optimizer instance
    """
    # Sort indices by metric value
    order = np.argsort(optimizer.simplex_metrics)
    if optimizer.opt_min_or_max == 'max':
        order = order[::-1]  # Reverse order for maximization
    
    # Reorder simplex and metrics
    optimizer.simplex = optimizer.simplex[order]
    optimizer.simplex_metrics = optimizer.simplex_metrics[order]
    optimizer.current_responses = [optimizer.current_responses[i] for i in order]
    
    # Update best solution
    new_best_metric = optimizer.simplex_metrics[0]
    if optimizer._is_better(new_best_metric, optimizer.best_metric):
        # Calculate relative improvement (using DE's safe approach)
        improvement_significant = False
        abs_previous_best = abs(optimizer.best_metric)
        
        # Use a small tolerance for checking if the previous best is effectively zero
        if abs_previous_best > np.finfo(float).eps:  # Check if denominator is safely non-zero
            # Calculate relative improvement safely
            relative_improvement = np.inf  # Default to infinity if calculation fails below
            
            # Ensure the difference calculation itself doesn't create issues if metrics are huge
            diff = new_best_metric - optimizer.best_metric
            if np.isfinite(diff):
                # Perform division only if difference is finite
                relative_improvement = abs(diff) / abs_previous_best
            
            # Check if the calculated relative improvement is finite and meets threshold
            if np.isfinite(relative_improvement) and relative_improvement >= optimizer.improvement_threshold:
                improvement_significant = True
            # If relative_improvement ended up as inf (due to safe denominator but large diff/small denom),
            # consider it significant if the threshold is not also inf.
            elif np.isinf(relative_improvement) and np.isfinite(optimizer.improvement_threshold):
                improvement_significant = True
        
        # else: previous_best_metric is zero or very close to it
        # improvement_significant remains False, correctly handled below
        
        # Update no-improvement counter based on significance
        if improvement_significant:
            optimizer.iter_no_improvement = 0
        else:
            # If improvement wasn't significant OR if previous best was zero, increment counter
            optimizer.iter_no_improvement += 1
        
        # Update best solution
        optimizer.best = optimizer.simplex[0].copy()
        optimizer.best_metric = new_best_metric
        optimizer.best_response = optimizer.current_responses[0]
        
        # Convert to parameters DataFrame
        import pandas as pd
        params_df = pd.DataFrame(columns=optimizer.variable_parameters_names, data=[optimizer.best])
        optimizer.best_parameters = optimizer.parameters.denormalize_and_descale_parameters_array(
            params_df, include_fixed=True
        ).to_dict('records')[0]
        
        # Set flag for better solution found
        optimizer.better_solution_found = True
    else:
        optimizer.iter_no_improvement += 1
        optimizer.better_solution_found = False
    
    # Update worst and second worst metrics
    optimizer.worst_metric = optimizer.simplex_metrics[-1]
    optimizer.second_worst_metric = optimizer.simplex_metrics[-2]

def _generate_coefficient(optimizer, coef_range):
    """
    Generate a coefficient value from a range or return fixed value.
    
    Args:
        optimizer: The NelderMead optimizer instance
        coef_range: Either a float/int or a tuple of (min, max)
    
    Returns:
        float: The coefficient value
    """
    if isinstance(coef_range, (float, int)):
        return coef_range
    elif isinstance(coef_range, (tuple, list)):
        return optimizer.rng.uniform(coef_range[0], coef_range[1])
    else:
        raise ValueError(f"Invalid coefficient type: {type(coef_range)}")

def _check_boundaries(optimizer, point):
    """
    Check and correct boundary violations for a point.
    
    Args:
        optimizer: The NelderMead optimizer instance
        point: The point to check (numpy array)
    
    Returns:
        numpy array: The corrected point
    """
    # Normalized space is [0, 1]
    point = point.copy()
    
    if optimizer.boundary_constraint_method == 'clamp':
        # Clamp to boundaries
        point = np.clip(point, 0, 1)
    elif optimizer.boundary_constraint_method == 'random':
        # Replace out-of-bounds values with random values
        mask = (point < 0) | (point > 1)
        point[mask] = optimizer.rng.uniform(0, 1, size=np.sum(mask))
    elif optimizer.boundary_constraint_method == 'random_from_target':
        # For reflection/expansion, use centroid as target
        # Replace with random value between target and boundary
        upper_mask = point > 1
        lower_mask = point < 0
        
        if hasattr(optimizer, 'centroid') and optimizer.centroid is not None:
            target = optimizer.centroid
            point[upper_mask] = optimizer.rng.uniform(target[upper_mask], 1, size=np.sum(upper_mask))
            point[lower_mask] = optimizer.rng.uniform(0, target[lower_mask], size=np.sum(lower_mask))
        else:
            # Fallback to random if no centroid available
            point[upper_mask] = optimizer.rng.uniform(0.5, 1, size=np.sum(upper_mask))
            point[lower_mask] = optimizer.rng.uniform(0, 0.5, size=np.sum(lower_mask))
    
    return point

def _try_reflection(optimizer):
    """
    Try the reflection operation.
    
    Args:
        optimizer: The NelderMead optimizer instance
    """
    # Generate reflection coefficient
    optimizer.reflection_coef = _generate_coefficient(optimizer, optimizer.reflection_coefficient)
    
    # Compute reflected point
    optimizer.reflected = optimizer.centroid + optimizer.reflection_coef * (optimizer.centroid - optimizer.simplex[-1])
    optimizer.reflected = _check_boundaries(optimizer, optimizer.reflected)
    
    # Evaluate reflected point
    import pandas as pd
    params_df = pd.DataFrame(columns=optimizer.variable_parameters_names, data=[optimizer.reflected])
    parameters = optimizer.parameters.denormalize_and_descale_parameters_array(
        params_df, include_fixed=True
    )
    
    extra_arguments = {
        'iteration': optimizer.iter,
        'best_metric': optimizer.best_metric,
        'best_parameters': optimizer.best_parameters,
        **optimizer.eval_func_args
    }
    
    responses = optimizer.eval_func(parameters=parameters, **extra_arguments)
    optimizer.reflected_metric = responses[0]['metric']
    optimizer.reflected_response = responses[0]
    optimizer.nr_evaluations += 1
    
    # Update trial history
    optimizer.all_trials = np.vstack([optimizer.all_trials, optimizer.reflected.reshape(1, -1)])
    optimizer.all_trials_metrics = np.append(optimizer.all_trials_metrics, optimizer.reflected_metric)

def _try_expansion(optimizer):
    """
    Try the expansion operation.
    
    Args:
        optimizer: The NelderMead optimizer instance
    """
    # Generate expansion coefficient
    optimizer.expansion_coef = _generate_coefficient(optimizer, optimizer.expansion_coefficient)
    
    # Compute expanded point
    optimizer.expanded = optimizer.centroid + optimizer.expansion_coef * (optimizer.reflected - optimizer.centroid)
    optimizer.expanded = _check_boundaries(optimizer, optimizer.expanded)
    
    # Evaluate expanded point
    import pandas as pd
    params_df = pd.DataFrame(columns=optimizer.variable_parameters_names, data=[optimizer.expanded])
    parameters = optimizer.parameters.denormalize_and_descale_parameters_array(
        params_df, include_fixed=True
    )
    
    extra_arguments = {
        'iteration': optimizer.iter,
        'best_metric': optimizer.best_metric,
        'best_parameters': optimizer.best_parameters,
        **optimizer.eval_func_args
    }
    
    responses = optimizer.eval_func(parameters=parameters, **extra_arguments)
    optimizer.expanded_metric = responses[0]['metric']
    optimizer.expanded_response = responses[0]
    optimizer.nr_evaluations += 1
    
    # Update trial history
    optimizer.all_trials = np.vstack([optimizer.all_trials, optimizer.expanded.reshape(1, -1)])
    optimizer.all_trials_metrics = np.append(optimizer.all_trials_metrics, optimizer.expanded_metric)

def _try_contraction(optimizer, mode='outside'):
    """
    Try the contraction operation.
    
    Args:
        optimizer: The NelderMead optimizer instance
        mode: 'outside' or 'inside' contraction
    """
    # Generate contraction coefficient
    optimizer.contraction_coef = _generate_coefficient(optimizer, optimizer.contraction_coefficient)
    
    # Compute contracted point
    if mode == 'outside':
        optimizer.contracted = optimizer.centroid + optimizer.contraction_coef * (optimizer.reflected - optimizer.centroid)
    else:  # inside
        optimizer.contracted = optimizer.centroid + optimizer.contraction_coef * (optimizer.simplex[-1] - optimizer.centroid)
    
    optimizer.contracted = _check_boundaries(optimizer, optimizer.contracted)
    
    # Evaluate contracted point
    import pandas as pd
    params_df = pd.DataFrame(columns=optimizer.variable_parameters_names, data=[optimizer.contracted])
    parameters = optimizer.parameters.denormalize_and_descale_parameters_array(
        params_df, include_fixed=True
    )
    
    extra_arguments = {
        'iteration': optimizer.iter,
        'best_metric': optimizer.best_metric,
        'best_parameters': optimizer.best_parameters,
        **optimizer.eval_func_args
    }
    
    responses = optimizer.eval_func(parameters=parameters, **extra_arguments)
    optimizer.contracted_metric = responses[0]['metric']
    optimizer.contracted_response = responses[0]
    optimizer.nr_evaluations += 1
    
    # Update trial history
    optimizer.all_trials = np.vstack([optimizer.all_trials, optimizer.contracted.reshape(1, -1)])
    optimizer.all_trials_metrics = np.append(optimizer.all_trials_metrics, optimizer.contracted_metric)

def _perform_shrink(optimizer):
    """
    Perform the shrink operation on all vertices except the best.
    
    Args:
        optimizer: The NelderMead optimizer instance
    """
    # Generate shrink coefficient
    optimizer.shrink_coef = _generate_coefficient(optimizer, optimizer.shrink_coefficient)
    
    # Shrink all vertices except the best towards the best
    for i in range(1, optimizer.simplex_size):
        optimizer.simplex[i] = optimizer.best + optimizer.shrink_coef * (optimizer.simplex[i] - optimizer.best)
        optimizer.simplex[i] = _check_boundaries(optimizer, optimizer.simplex[i])
    
    # Evaluate all new vertices (except the best)
    import pandas as pd
    params_df = pd.DataFrame(columns=optimizer.variable_parameters_names, data=optimizer.simplex[1:])
    parameters = optimizer.parameters.denormalize_and_descale_parameters_array(
        params_df, include_fixed=True
    )
    
    extra_arguments = {
        'iteration': optimizer.iter,
        'best_metric': optimizer.best_metric,
        'best_parameters': optimizer.best_parameters,
        **optimizer.eval_func_args
    }
    
    responses = optimizer.eval_func(parameters=parameters, **extra_arguments)
    
    # Update metrics and responses for shrunk vertices
    for i in range(1, optimizer.simplex_size):
        optimizer.simplex_metrics[i] = responses[i-1]['metric']
        optimizer.current_responses[i] = responses[i-1]
    
    optimizer.nr_evaluations += len(responses)
    
    # Update trial history
    for i in range(1, optimizer.simplex_size):
        optimizer.all_trials = np.vstack([optimizer.all_trials, optimizer.simplex[i].reshape(1, -1)])
        optimizer.all_trials_metrics = np.append(optimizer.all_trials_metrics, optimizer.simplex_metrics[i])