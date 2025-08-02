"""
Evolutionary operators for the DifferentialEvolution class.

This module contains internal functions for:
- Population initialization
- Mutation operations
- Recombination (crossover) operations
- Selection operations
- Coefficient generation
- Boundary handling

Note: All functions in this module are prefixed with an underscore (_) to indicate
they are internal implementation details not meant to be called directly from outside
the DifferentialEvolution class.
"""

import numpy as np, pandas as pd, os
from scipy.stats.qmc import Halton

def _incorporate_initial_population(de_instance):
    """
    Incorporate provided initial population into donors.

    This function processes the initial population from various formats (CSV, JSON, DataFrame,
    or list of dicts) and incorporates it into the donor population after normalization and validation.

    Args:
        de_instance: Instance of DifferentialEvolution

    Returns:
        bool: True if initial population was successfully incorporated, False otherwise
    """

    # Convert initial population to DataFrame regardless of input format
    init_pop_df = None

    # Case 1: init_pop is a path to a file
    if isinstance(de_instance.init_pop, str):
        if not os.path.exists(de_instance.init_pop):
            print(f"Warning: Initial population file '{de_instance.init_pop}' not found. Using random initialization.")
            return False

        file_ext = de_instance.init_pop.lower().split('.')[-1]

        if file_ext == 'csv':
            init_pop_df = pd.read_csv(de_instance.init_pop)
        elif file_ext in ['json', 'jsn']:
            init_pop_df = pd.read_json(de_instance.init_pop)
        else:
            print(f"Warning: Unsupported file format '{file_ext}'. Using random initialization.")
            return False

    # Case 2: init_pop is already a DataFrame
    elif isinstance(de_instance.init_pop, pd.DataFrame):
        init_pop_df = de_instance.init_pop.copy()

    # Case 3: init_pop is a list of dictionaries
    elif isinstance(de_instance.init_pop, list) and all(isinstance(item, dict) for item in de_instance.init_pop):
        init_pop_df = pd.DataFrame(de_instance.init_pop)

    # Invalid format
    else:
        print("Warning: Initial population format not recognized. Using random initialization.")
        return False

    # Check 1: Keep only parameters that are part of variable_parameters
    extra_params = set(init_pop_df.columns) - set(de_instance.variable_parameters_names)
    missing_params = set(de_instance.variable_parameters_names) - set(init_pop_df.columns)

    if extra_params:
        print(f"Info: Removing {len(extra_params)} extra parameters not in variable_parameters: {', '.join(extra_params)}")
        init_pop_df = init_pop_df.drop(columns=list(extra_params))

    if missing_params:
        print(f"Info: {len(missing_params)} parameters missing from initial population: {', '.join(missing_params)}")
        # Fill missing parameters with NaN so they'll be randomized later
        for param in missing_params:
            init_pop_df[param] = np.nan

    # Check 2: Remove duplicate rows
    orig_rows = len(init_pop_df)
    init_pop_df = init_pop_df.drop_duplicates()
    if len(init_pop_df) < orig_rows:
        print(f"Info: Removed {orig_rows - len(init_pop_df)} duplicate rows from initial population")

    # Check 3: Ensure number of rows doesn't exceed pop_size
    if len(init_pop_df) > de_instance.pop_size:
        print(f"Info: Initial population size ({len(init_pop_df)}) exceeds population size ({de_instance.pop_size}). Randomly selecting {de_instance.pop_size} rows.")
        init_pop_df = init_pop_df.sample(n=de_instance.pop_size, random_state=de_instance.rng.randint(0, 10000))

    # Reorganize columns to match variable_parameters_names order
    for col in de_instance.variable_parameters_names:
        if col not in init_pop_df.columns:
            init_pop_df[col] = np.nan
    init_pop_df = init_pop_df[de_instance.variable_parameters_names]

    # Handle out-of-range parameter values
    init_pop_df = _handle_out_of_range_params(de_instance, init_pop_df)

    # Scale and normalize the DataFrame using Parameters class
    normalized_df = de_instance.parameters.norm_all(init_pop_df)

    # Convert to numpy array
    if isinstance(normalized_df, pd.DataFrame):
        normalized_values = normalized_df.values
    else:
        normalized_values = normalized_df

    # Replace random or all donors based on size
    if len(normalized_values) == de_instance.pop_size:
        # Replace all donors
        de_instance.donors = normalized_values
        print(f"Info: Replaced all {de_instance.pop_size} donors with initial population values")
    else:
        # Randomly select positions to replace
        num_to_replace = len(normalized_values)
        indices_to_replace = de_instance.rng.choice(de_instance.pop_size, size=num_to_replace, replace=False)

        # Replace selected donors
        de_instance.donors[indices_to_replace] = normalized_values
        print(f"Info: Replaced {num_to_replace} of {de_instance.pop_size} donors with initial population values")

    # Handle NaN values in the donors (from missing parameters)
    # Find positions of NaN values
    nan_mask = np.isnan(de_instance.donors)
    if np.any(nan_mask):
        # Generate random values for NaN positions using Halton sequence
        sampler = Halton(d=1, seed=de_instance.seed)

        # Replace NaN values with random values from Halton sequence
        nan_count = np.sum(nan_mask)
        random_values = sampler.random(nan_count).flatten()
        de_instance.donors[nan_mask] = random_values
        print(f"Info: Filled {nan_count} missing parameter values with random values")

    if len(normalized_values) == de_instance.pop_size:
        # All donors replaced - track all indices
        de_instance.init_pop_indices = np.arange(de_instance.pop_size)
    else:
        # Only some donors replaced - track which ones
        de_instance.init_pop_indices = indices_to_replace

    return True

def _handle_out_of_range_params(de_instance, init_pop_df):
    """
    Handle out-of-range parameter values in the initial population based on the
    init_pop_out_of_range_param setting.

    Args:
        de_instance: Instance of DifferentialEvolution
        init_pop_df: DataFrame containing the initial population

    Returns:
        pd.DataFrame: DataFrame with out-of-range parameters handled according to the setting
    """
    import numpy as np

    # If set to 'keep', no changes needed
    if de_instance.init_pop_out_of_range_param == 'keep':
        return init_pop_df

    # Make a copy to avoid modifying the original
    df = init_pop_df.copy()

    # Process each parameter
    for param in de_instance.variable_parameters_names:
        if param not in df.columns:
            continue

        # Get parameter boundaries from the Parameters object
        param_info = de_instance.parameters.get_parameter(param)
        if hasattr(param_info, 'min') and hasattr(param_info, 'max'):
            param_min = param_info.min
            param_max = param_info.max
        else:
            # For discrete parameters, get the min/max from values
            param_min = min(param_info.values)
            param_max = max(param_info.values)

        # Find values outside boundaries
        below_min_mask = df[param] < param_min
        above_max_mask = df[param] > param_max

        if de_instance.init_pop_out_of_range_param == 'extreme':
            # Set values below min to min
            if np.any(below_min_mask):
                count = below_min_mask.sum()
                df.loc[below_min_mask, param] = param_min
                print(f"Info: Set {count} values below minimum to {param_min} for parameter '{param}'")

            # Set values above max to max
            if np.any(above_max_mask):
                count = above_max_mask.sum()
                df.loc[above_max_mask, param] = param_max
                print(f"Info: Set {count} values above maximum to {param_max} for parameter '{param}'")

        elif de_instance.init_pop_out_of_range_param == 'random':
            # Generate random values for out-of-range parameters
            if np.any(below_min_mask):
                count = below_min_mask.sum()
                df.loc[below_min_mask, param] = de_instance.rng.uniform(
                    param_min,
                    param_max,
                    size=count
                )
                print(f"Info: Replaced {count} values below minimum with random values for parameter '{param}'")

            if np.any(above_max_mask):
                count = above_max_mask.sum()
                df.loc[above_max_mask, param] = de_instance.rng.uniform(
                    param_min,
                    param_max,
                    size=count
                )
                print(f"Info: Replaced {count} values above maximum with random values for parameter '{param}'")

    return df

def _incorporate_default_values(de_instance):
    """
    Incorporate default parameter values into the initial population.

    This function replaces a portion of the initial population with the default parameter
    values based on the defaults_in_init_pop_ratio setting. It respects the priority of
    the initial population by only replacing members that weren't already set by the
    initial population incorporation.

    Args:
        de_instance: Instance of DifferentialEvolution

    Returns:
        None: Updates de_instance.donors directly
    """
    import numpy as np

    # Validate the defaults_in_init_pop_ratio
    if de_instance.defaults_in_init_pop_ratio <= 0 or de_instance.defaults_in_init_pop_ratio >= 1:
        de_instance.defaults_in_init_pop_ratio = 0.2
        print("Warning: Invalid defaults_in_init_pop_ratio. Setting to default value of 0.2")

    # Determine how many members to replace with default values
    replace_count = int(de_instance.pop_size * de_instance.defaults_in_init_pop_ratio)

    if replace_count <= 0:
        print("Info: No members will be replaced with default values (ratio too small)")
        return

    # If init_pop was provided, we need to identify which donors were already set
    if hasattr(de_instance, 'init_pop_indices') and de_instance.init_pop_indices is not None:
        # These are indices that were already set by the initial population
        used_indices = set(de_instance.init_pop_indices)

        # Available indices are those not used by the initial population
        available_indices = np.array([i for i in range(de_instance.pop_size) if i not in used_indices])

        if len(available_indices) == 0:
            print("Info: All members already set by initial population. No default values will be incorporated.")
            return

        # Adjust replace_count if there are fewer available indices than desired replacements
        if replace_count > len(available_indices):
            replace_count = len(available_indices)
            print(f"Info: Adjusted replacement count to {replace_count} due to initial population priority")
    else:
        # If no init_pop was used, all indices are available
        available_indices = np.arange(de_instance.pop_size)

    print(f"Info: {replace_count} of {de_instance.pop_size} members will be replaced with default values (ratio = {de_instance.defaults_in_init_pop_ratio})")

    # Get the default values and normalize them
    defaults_dict = de_instance.parameters.get_defaults()
    # Filter to only variable parameters
    variable_params = de_instance.variable_parameters_names
    variable_defaults = {k: v for k, v in defaults_dict.items() if k in variable_params}
    
    # Normalize the default values
    normalized_defaults = de_instance.parameters.norm_all(variable_defaults)
    
    # Convert to array
    if isinstance(normalized_defaults, dict):
        default_values = np.array([normalized_defaults[param] for param in variable_params])
    else:
        default_values = normalized_defaults
    
    # Create array of default values for all members to replace
    # Repeat the default values for each member
    default_array = np.tile(default_values, (replace_count, 1))

    # Randomly select positions to replace from available indices
    indices_to_replace = de_instance.rng.choice(available_indices, size=replace_count, replace=False)

    # Replace selected donors with default values
    de_instance.donors[indices_to_replace] = default_array

def _generate_initial_population(de_instance):
    """
    Generate the initial population for the first iteration.

    This function first attempts to use the provided initial population.
    If that's not available or valid, it generates a random population using
    the Halton sequence. Then it incorporates default values if specified.

    Args:
        de_instance: Instance of DifferentialEvolution

    Returns:
        None: Updates de_instance.donors directly
    """
    # First try to use the provided initial population
    init_pop_success = False
    if de_instance.init_pop is not None:
        init_pop_success = _incorporate_initial_population(de_instance)

    # Generate donors randomly using Halton sequence if needed
    if not init_pop_success:
        sampler = Halton(d=de_instance.nr_variable_parameters, seed=de_instance.seed)
        de_instance.donors = sampler.random(de_instance.pop_size)
        print("Info: Generated initial population using Halton sequence")

    # Handle default values in initial population
    if de_instance.defaults_in_init_pop:
        _incorporate_default_values(de_instance)

def _generate_trials(de_instance):
    """
    Generate trial vectors for each target-donor pair.

    Args:
        de_instance: Instance of DifferentialEvolution

    Returns:
        None: Updates de_instance.trials directly
    """
    if de_instance.iter == 1:
        # In the first iteration, trials are equal to donors
        de_instance.trials = de_instance.donors
    else:
        # Generate recombinations between targets and donors
        _generate_recombinations(de_instance)

def _generate_donors(de_instance):
    """
    Generate donor vectors for each target.

    Args:
        de_instance: Instance of DifferentialEvolution

    Returns:
        None: Updates de_instance.donors directly
    """
    if de_instance.iter == 1:
        _generate_initial_population(de_instance)
    else:
        # Generate mutations for each target
        _generate_mutations(de_instance)

def _generate_mutations(de_instance, dice=None):
    """
    Generate mutation vectors using DE mutation operators.

    Args:
        de_instance: Instance of DifferentialEvolution
        dice: Optional predefined random indices for mutation

    Returns:
        None: Updates de_instance.donors directly
    """
    if dice is None:
        # Select 3 distinct random indices for each target
        dice = [
            de_instance.rng.choice([j for j in range(de_instance.pop_size) if j != i], size=(1, 3), replace=False)
            for i in range(de_instance.pop_size)
        ]
        dice = np.array(dice).reshape(-1, 3)

    # Extract random members from the population
    temp = de_instance.targets[dice].reshape(-1, 3, de_instance.nr_variable_parameters)
    de_instance.rand_mem_1 = temp[:, 0, :]
    de_instance.rand_mem_2 = temp[:, 1, :]
    de_instance.rand_mem_3 = temp[:, 2, :]

    # Calculate mutation coefficients
    de_instance.mut_coef_1 = _get_coefficient(de_instance, de_instance.mutation_factor_1)
    de_instance.mut_coef_2 = _get_coefficient(de_instance, de_instance.mutation_factor_2)
    de_instance.mut_coef_3 = _get_coefficient(de_instance, de_instance.mutation_factor_3)

    # Calculate donor vectors using DE mutation formula
    de_instance.donors = (
        de_instance.rand_mem_1 +                                              # Random vector 1
        de_instance.mut_coef_1 * (de_instance.rand_mem_2 - de_instance.rand_mem_3) +  # Scaled difference between random vectors 2 and 3
        de_instance.mut_coef_2 * (de_instance.best - de_instance.rand_mem_1) +        # Scaled difference between best and random vector 1
        de_instance.mut_coef_3 * (de_instance.best - de_instance.targets)             # Scaled difference between best and target
    )

    # Correct values outside boundaries
    _check_donors_boundaries(de_instance)

def _generate_recombinations(de_instance, dice=None):
    """
    Generate recombination vectors by crossing over targets and donors.

    Args:
        de_instance: Instance of DifferentialEvolution
        dice: Optional predefined random values for recombination

    Returns:
        None: Updates de_instance.trials directly
    """
    # Generate random values for each parameter
    if dice is None:
        dice = de_instance.rng.rand(de_instance.pop_size, de_instance.nr_variable_parameters)

    # Get recombination coefficient
    de_instance.recom_coef = _get_coefficient(de_instance, de_instance.recombination_factor)

    # Create trials by combining donors and targets
    de_instance.trials = np.where(dice < de_instance.recom_coef, de_instance.donors, de_instance.targets)

def _determine_survivors(de_instance):
    """
    Determine survivors for the next generation through selection.

    Args:
        de_instance: Instance of DifferentialEvolution

    Returns:
        None: Updates de_instance.survivors and de_instance.survivors_metrics directly
    """
    if de_instance.iter == 1:
        # In the first iteration, all trials become survivors
        de_instance.survivors = de_instance.trials
        de_instance.survivors_metrics = de_instance.trials_metrics
    else:
        # Selection: compare trials with targets and choose the better ones
        if de_instance.opt_min_or_max == 'max':
            mask = (de_instance.trials_metrics > de_instance.targets_metrics)
        else:  # min
            mask = (de_instance.trials_metrics < de_instance.targets_metrics)

        # Create survivors by selecting better solutions
        de_instance.survivors_metrics = np.where(mask, de_instance.trials_metrics, de_instance.targets_metrics)
        de_instance.survivors = np.where(mask.reshape(-1, 1), de_instance.trials, de_instance.targets)

def _determine_best(de_instance):
    """
    Determine the best solution in the current population.

    Args:
        de_instance: Instance of DifferentialEvolution

    Returns:
        bool: Whether a better solution was found
    """
    # Get the index of the best survivor
    if de_instance.opt_min_or_max == 'max':
        best_index = np.argmax(de_instance.survivors_metrics)
    else:  # min
        best_index = np.argmin(de_instance.survivors_metrics)

    current_best_metric = de_instance.survivors_metrics[best_index]
    previous_best_metric = de_instance.best_metric # Store previous best for clarity

    # Check if better solution found
    better_solution_found = False
    if de_instance.opt_min_or_max == 'max' and current_best_metric > previous_best_metric:
        better_solution_found = True
    elif de_instance.opt_min_or_max == 'min' and current_best_metric < previous_best_metric:
        better_solution_found = True

    # Update best if better solution found
    if better_solution_found:
        improvement_significant = False
        abs_previous_best = abs(previous_best_metric)

        # Use a small tolerance for checking if the previous best is effectively zero
        if abs_previous_best > np.finfo(float).eps: # Check if denominator is safely non-zero
            # Calculate relative improvement safely
            relative_improvement = np.inf # Default to infinity if calculation fails below

            # Ensure the difference calculation itself doesn't create issues if metrics are huge
            diff = current_best_metric - previous_best_metric
            if np.isfinite(diff):
                 # Perform division only if difference is finite
                 relative_improvement = abs(diff) / abs_previous_best

            # Check if the calculated relative improvement is finite and meets threshold
            if np.isfinite(relative_improvement) and relative_improvement >= de_instance.improvement_threshold:
                 improvement_significant = True
            # If relative_improvement ended up as inf (due to safe denominator but large diff/small denom),
            # consider it significant if the threshold is not also inf.
            elif np.isinf(relative_improvement) and np.isfinite(de_instance.improvement_threshold):
                 improvement_significant = True

        # else: # previous_best_metric is zero or very close to it
            # improvement_significant remains False, correctly handled below

        # Update no-improvement counter based on significance
        if improvement_significant:
             de_instance.iter_no_improvement = 0
        else:
             # If improvement wasn't significant OR if previous best was zero, increment counter
             de_instance.iter_no_improvement += 1

        # Update best solution details
        de_instance.best = de_instance.survivors[best_index]
        best_survivor_params_normed = pd.DataFrame([de_instance.best], columns=de_instance.variable_parameters_names)
        # Denormalize the best parameters (unnorm_all returns DataFrame with fixed params added)
        de_instance.best_parameters = de_instance.parameters.unnorm_all(
            best_survivor_params_normed
        ).iloc[0] # Get the Series

        de_instance.best_metric = current_best_metric
        # Ensure current_responses is list-like and indexable
        if isinstance(de_instance.current_responses, (list, np.ndarray, pd.Series)) and len(de_instance.current_responses) > best_index:
             de_instance.best_response = de_instance.current_responses[best_index]
        else:
             # Handle cases where current_responses might be structured differently or empty
             # Maybe store just the metric if the full response isn't guaranteed?
             # For now, set to None if indexing fails. Consider logging a warning.
             de_instance.best_response = None
             # print(f"Warning: Could not retrieve best_response at index {best_index}")

        de_instance.better_solution_found = True

    else: # No better solution found
        de_instance.iter_no_improvement += 1
        de_instance.better_solution_found = False

    # Return the flag indicating if a better solution was found in this iteration
    return better_solution_found

def _get_coefficient(de_instance, factor):
    """
    Get coefficient for mutation or recombination based on factor type.

    Args:
        de_instance: Instance of DifferentialEvolution
        factor: Factor value or range (float, int, tuple, or list)

    Returns:
        float or numpy.ndarray: Coefficient value(s)
    """
    if isinstance(factor, (float, int)):
        return factor
    elif isinstance(factor, (tuple, list)):
        return de_instance.rng.uniform(factor[0], factor[1], size=(de_instance.pop_size, 1))
    return None

def _check_donors_boundaries(de_instance):
    """
    Correct values outside boundaries [0, 1] in normalized donor vectors
    using the method specified by `de_instance.boundary_constraint_method`.

    Args:
        de_instance: Instance of DifferentialEvolution

    Returns:
        None: Updates de_instance.donors directly
    """
    # Get row and column indices of violations
    # Note: Assuming normalized boundaries [0, 1] for donors here
    # If adaptive boundaries modify these, this check needs adjustment,
    # but typically mutation happens *before* denormalization.
    # Using boundaries_min/max attributes for generality.
    upper_violation_mask = de_instance.donors > de_instance.boundaries_max
    lower_violation_mask = de_instance.donors < de_instance.boundaries_min

    constraint_method = de_instance.boundary_constraint_method

    # Process upper violations
    if np.any(upper_violation_mask):
        rows_upper, cols_upper = np.where(upper_violation_mask)

        if constraint_method == 'random_from_target':
            # Original method: Random value between target and upper boundary
            de_instance.donors[upper_violation_mask] = de_instance.rng.uniform(
                de_instance.targets[upper_violation_mask],        # Low limit = target value
                de_instance.boundaries_max[cols_upper],           # High limit = boundary max
                size=len(rows_upper)
            )
        elif constraint_method == 'clamp':
            # Clamp to the upper boundary
            de_instance.donors[upper_violation_mask] = de_instance.boundaries_max[cols_upper]
        elif constraint_method == 'random':
            # Replace with a new random value within the full [min, max] boundary range
            de_instance.donors[upper_violation_mask] = de_instance.rng.uniform(
                de_instance.boundaries_min[cols_upper],           # Low limit = boundary min
                de_instance.boundaries_max[cols_upper],           # High limit = boundary max
                size=len(rows_upper)
            )

    # Process lower violations
    if np.any(lower_violation_mask):
        rows_lower, cols_lower = np.where(lower_violation_mask)

        if constraint_method == 'random_from_target':
            # Original method: Random value between lower boundary and target
            de_instance.donors[lower_violation_mask] = de_instance.rng.uniform(
                de_instance.boundaries_min[cols_lower],           # Low limit = boundary min
                de_instance.targets[lower_violation_mask],        # High limit = target value
                size=len(rows_lower)
            )
        elif constraint_method == 'clamp':
            # Clamp to the lower boundary
            de_instance.donors[lower_violation_mask] = de_instance.boundaries_min[cols_lower]
        elif constraint_method == 'random':
            # Replace with a new random value within the full [min, max] boundary range
            de_instance.donors[lower_violation_mask] = de_instance.rng.uniform(
                de_instance.boundaries_min[cols_lower],           # Low limit = boundary min
                de_instance.boundaries_max[cols_lower],           # High limit = boundary max
                size=len(rows_lower)
            )
