"""
Test file for initial population incorporation in DifferentialEvolution,
using the test_functions package.

This script tests different scenarios for initial population handling using
the 2D Rosenbrock function obtained from the test_functions package.
"""

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from tempfile import NamedTemporaryFile
from typing import List, Dict, Any

# Import modules
from aivalanche_lib import Parameters
from aivalanche_lib import DifferentialEvolution
from aivalanche_lib.test_functions import (
    get_function_details,
    plot_test_function,
    generate_parameters_config,
    list_available_functions
)


# ----------------------------------------------------------------------------
# Generic Evaluation Function
# ----------------------------------------------------------------------------
def evaluate_test_function(parameters: pd.DataFrame, func_details: dict, **kwargs) -> List[Dict[str, Any]]:
    """
    Generic evaluation function wrapper for test functions from the package.
    """
    results = []
    target_func = func_details['func'] # The actual callable test function
    dim = func_details['dim']
    param_names = [f'x{i+1}' for i in range(dim)] # Expected parameter names

    params_list = parameters.to_dict('records')

    for params_row in params_list:
        try:
            input_vector = np.array([params_row[name] for name in param_names])
        except KeyError as e:
            print(f"Error: Missing parameter {e} in optimizer output. Expected: {param_names}, Got: {list(params_row.keys())}")
            value = float('inf') # Assign large penalty for minimization
        else:
            value = target_func(input_vector)
        # Store results - Assuming MINIMIZATION
        results.append({'metric': value, 'value': value})
    return results

# ----------------------------------------------------------------------------
# Callbacks
# ----------------------------------------------------------------------------
def callback_after_each_iter(iteration, best_metric, **kwargs):
    if iteration % 20 == 0 or iteration == 1: # Print less frequently
        print(f"  Iter {iteration}: Best metric = {best_metric:.6f}")

def callback_after_better_solution(iteration, best_parameters, best_metric, **kwargs):
     print(f"  -> New best @ iter {iteration}: metric = {best_metric:.6f}, params = {dict(best_parameters)}")

# ----------------------------------------------------------------------------
# Base optimization function
# ----------------------------------------------------------------------------
def run_optimization(func_details: dict,
                     parameters_obj: Parameters, # Now expects a Parameters object
                     init_pop=None,
                     defaults_in_init_pop=False,
                     defaults_in_init_pop_ratio=0.2,
                     pop_size=30,
                     seed=42,
                     max_iterations=100, # Adjusted default for quicker tests
                     init_pop_out_of_range_param='keep'):
    """
    Run optimization with specified initial population settings using a function
    from the test_functions package.

    Args:
        func_details: Dictionary of details for the test function.
        parameters_obj: Instantiated Parameters object for the optimizer.
        init_pop: Initial population (DataFrame, list of dicts, or file path)
        defaults_in_init_pop: Whether to incorporate default values
        defaults_in_init_pop_ratio: Ratio for default incorporation.
        pop_size: Population size for the optimizer
        seed: Random seed for reproducibility
        max_iterations: Maximum iterations.
        init_pop_out_of_range_param: Strategy for handling out-of-range parameters

    Returns:
        The optimizer instance after running optimization
    """
    optimizer = DifferentialEvolution(
        seed=seed,
        eval_func=evaluate_test_function,
        eval_func_args={'func_details': func_details}, # Pass details here
        parameters=parameters_obj, # Use the passed Parameters object
        pop_size=pop_size,
        max_iterations=max_iterations,
        opt_min_or_max='min',  # Assuming minimization
        max_iter_without_improvement=50,
        callback_after_each_iter=callback_after_each_iter,
        # callback_after_better_solution=callback_after_better_solution,
        adaptive_boundaries=False, # Keep adaptive for most init pop tests
        init_pop=init_pop,
        defaults_in_init_pop=defaults_in_init_pop,
        defaults_in_init_pop_ratio=defaults_in_init_pop_ratio,
        init_pop_out_of_range_param=init_pop_out_of_range_param
    )
    optimizer.run_optimization()
    return optimizer

# ----------------------------------------------------------------------------
# Test Scenarios
# ----------------------------------------------------------------------------

# --- Get Rosenbrock details once ---
try:
    details_rosenbrock = get_function_details("rosenbrock_2d")
    # Standard parameter object for most tests
    param_config_std = generate_parameters_config(details_rosenbrock)
    parameters_std = Parameters(param_config_std)
    # Map old names 'x', 'y' to new names 'x1', 'x2' for init_pop data
    PARAM_MAP = {'x': 'x1', 'y': 'x2'}
except (KeyError, ValueError) as e:
    print(f"Fatal Error: Could not get Rosenbrock details from test_functions: {e}")
    exit()
# ------------------------------------


def test_no_init_pop():
    """Test optimization without initial population (baseline)."""
    print("\n============ TEST: No Initial Population (Baseline) ============")
    optimizer = run_optimization(details_rosenbrock, parameters_std, init_pop=None)
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizer

def test_dataframe_init_pop():
    """Test optimization with DataFrame as initial population."""
    print("\n============ TEST: DataFrame Initial Population ============")
    df = pd.DataFrame([
        {'x1': 0.9, 'x2': 0.9}, {'x1': 1.1, 'x2': 1.1},
        {'x1': 0.8, 'x2': 0.8}, {'x1': 1.2, 'x2': 1.2},
        {'x1': 0.0, 'x2': 0.0}
    ])
    optimizer = run_optimization(details_rosenbrock, parameters_std, init_pop=df)
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizer

def test_csv_init_pop():
    """Test optimization with CSV file as initial population."""
    print("\n============ TEST: CSV File Initial Population ============")
    with NamedTemporaryFile(suffix='.csv', mode='w+', delete=False, newline='') as tmp:
        df = pd.DataFrame([
             {'x1': 0.95, 'x2': 0.95}, {'x1': 1.05, 'x2': 1.05},
             {'x1': 0.9, 'x2': 1.1}, {'x1': 1.1, 'x2': 0.9}
        ])
        df.to_csv(tmp.name, index=False)
        tmp_name = tmp.name
    try:
        optimizer = run_optimization(details_rosenbrock, parameters_std, init_pop=tmp_name)
        print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    finally:
        if os.path.exists(tmp_name): os.unlink(tmp_name)
    return optimizer

def test_json_init_pop():
    """Test optimization with JSON file as initial population."""
    print("\n============ TEST: JSON File Initial Population ============")
    with NamedTemporaryFile(suffix='.json', mode='w+', delete=False) as tmp:
        df = pd.DataFrame([{'x1': 0.99, 'x2': 0.99}, {'x1': 1.01, 'x2': 1.01}])
        df.to_json(tmp.name, orient='records', indent=4)
        tmp_name = tmp.name
    try:
        optimizer = run_optimization(details_rosenbrock, parameters_std, init_pop=tmp_name)
        print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    finally:
        if os.path.exists(tmp_name): os.unlink(tmp_name)
    return optimizer

def test_list_dict_init_pop():
    """Test optimization with list of dictionaries as initial population."""
    print("\n============ TEST: List of Dictionaries Initial Population ============")
    init_pop = [{'x1': 0.7, 'x2': 0.7}, {'x1': 0.8, 'x2': 0.8},
                {'x1': 0.9, 'x2': 0.9}, {'x1': 1.1, 'x2': 1.1}]
    optimizer = run_optimization(details_rosenbrock, parameters_std, init_pop=init_pop)
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizer

def test_missing_params_init_pop():
    """Test optimization with initial population missing some parameters."""
    print("\n============ TEST: Initial Population with Missing Parameters ============")
    df = pd.DataFrame([{'x1': 0.9}, {'x1': 1.1}]) # Missing x2
    optimizer = run_optimization(details_rosenbrock, parameters_std, init_pop=df)
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizer

def test_extra_params_init_pop():
    """Test optimization with initial population having extra parameters."""
    print("\n============ TEST: Initial Population with Extra Parameters ============")
    df = pd.DataFrame([
        {'x1': 0.9, 'x2': 0.9, 'z': 1.0, 'extra': 'value'},
        {'x1': 1.1, 'x2': 1.1, 'z': 3.0, 'extra': 'value3'}
    ])
    optimizer = run_optimization(details_rosenbrock, parameters_std, init_pop=df)
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizer

def test_large_init_pop():
    """Test optimization with initial population larger than pop_size."""
    print("\n============ TEST: Initial Population Larger than pop_size ============")
    np.random.seed(42)
    df = pd.DataFrame({
        'x1': np.random.uniform(details_rosenbrock['bounds'][0][0], details_rosenbrock['bounds'][0][1], 50),
        'x2': np.random.uniform(details_rosenbrock['bounds'][1][0], details_rosenbrock['bounds'][1][1], 50)
    })
    df.loc[len(df)] = {'x1': 1.01, 'x2': 0.99} # Add near-optimal point
    optimizer = run_optimization(details_rosenbrock, parameters_std, init_pop=df, pop_size=30)
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizer

def test_duplicate_rows_init_pop():
    """Test optimization with initial population having duplicate rows."""
    print("\n============ TEST: Initial Population with Duplicate Rows ============")
    df = pd.DataFrame([{'x1': 0.9, 'x2': 0.9}, {'x1': 0.9, 'x2': 0.9}, {'x1': 1.1, 'x2': 1.1}])
    optimizer = run_optimization(details_rosenbrock, parameters_std, init_pop=df)
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizer

def test_defaults_in_init_pop():
    """Test optimization with defaults incorporated in initial population."""
    print("\n============ TEST: Defaults in Initial Population ============")
    df = pd.DataFrame([{'x1': 0.9, 'x2': 0.9}, {'x1': 1.1, 'x2': 1.1}])
    optimizer = run_optimization(details_rosenbrock, parameters_std, init_pop=df, defaults_in_init_pop=True)
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizer

def test_init_pop_with_optimal_value():
    """Test optimization with initial population containing the optimal value."""
    print("\n============ TEST: Initial Population with Optimal Value ============")
    opt_loc = details_rosenbrock['optimum_loc']
    df = pd.DataFrame([{'x1': opt_loc[0], 'x2': opt_loc[1]}])
    optimizer = run_optimization(details_rosenbrock, parameters_std, init_pop=df)
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizer

def test_out_of_range_params():
    """Test different strategies for handling out-of-range parameters in initial population."""
    print("\n============ TEST: Out-of-Range Parameter Handling Strategies ============")

    # Create special parameter set with narrower bounds for testing this specifically
    custom_params_data = [
        {"name": "x1", "min": -1.0, "max": 1.5, "default": 0.0, "scale": "lin", "mode": "variable"},
        {"name": "x2", "min": -0.5, "max": 2.0, "default": 0.0, "scale": "lin", "mode": "variable"}
    ]
    parameters_custom = Parameters(custom_params_data)

    init_pop_df = pd.DataFrame([
        {'x1': 0.0, 'x2': 0.0}, {'x1': -2.0, 'x2': -1.0}, # Out below
        {'x1': 2.0, 'x2': 3.0},  # Out above
        {'x1': 0.5, 'x2': 2.5}, {'x1': -1.5, 'x2': 1.0}  # Mixed
    ])
    original_values = init_pop_df.copy()
    optimizers_oor = {}

    for strategy in ['keep', 'extreme', 'random']:
        print(f"\n---- {strategy.upper()} Strategy ----")
        # NOTE: Pass the CUSTOM parameters object here, but the ORIGINAL func_details
        optimizer = run_optimization(
            func_details=details_rosenbrock, # Eval func still needs original math
            parameters_obj=parameters_custom, # Optimizer uses custom bounds for the check
            init_pop=original_values.copy(),
            init_pop_out_of_range_param=strategy,
            pop_size=10, # Smaller pop size for quicker test
            max_iterations=50
        )
        optimizers_oor[strategy] = optimizer
        print(f"Final result ({strategy.upper()}): {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")

    # Compare convergence
    plt.figure(figsize=(12, 6))
    for name, optimizer in optimizers_oor.items():
        history = optimizer.history
        if not history['bests'].empty:
            bests_df = history['bests']
            metrics_array = np.array(optimizer.all_bests_metrics).flatten()
            if len(metrics_array) == len(bests_df):
                 plt.plot(bests_df['iter'], metrics_array, label=f"OOR Strategy: {name}", linewidth=2)
            else:
                 print(f"Warning: Mismatch OOR plot length for '{name}'")

    plt.xlabel('Iteration')
    plt.ylabel('Rosenbrock Function Value (lower is better)')
    plt.title('Convergence Comparison: Out-of-Range Parameter Strategies')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('out_of_range_param_strategies_comparison.png')
    plt.close()
    print("\nComparison plot saved to 'out_of_range_param_strategies_comparison.png'")
    return optimizers_oor

def test_defaults_without_init_pop():
    """Test optimization with default values but no initial population."""
    print("\n============ TEST: Default Values Without Initial Population ============")
    optimizer = run_optimization(details_rosenbrock, parameters_std, init_pop=None, defaults_in_init_pop=True)
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizer

def test_defaults_with_different_ratios():
    """Test optimization with different ratios for default values incorporation."""
    print("\n============ TEST: Default Values with Different Ratios ============")
    init_pop = pd.DataFrame([{'x1': 0.5, 'x2': 0.5}, {'x1': 1.5, 'x2': 1.5}])
    ratios = [0.1, 0.3, 0.5, 0.7, 0.9]
    optimizers_ratio = {}

    for ratio in ratios:
        print(f"\n---- Defaults Ratio: {ratio} ----")
        optimizer = run_optimization(
            details_rosenbrock, parameters_std, init_pop=init_pop.copy(),
            defaults_in_init_pop=True, defaults_in_init_pop_ratio=ratio,
            pop_size=20, max_iterations=50
        )
        optimizers_ratio[f"Ratio {ratio}"] = optimizer
        print(f"Final result (Ratio {ratio}): {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")

    # Compare convergence
    plt.figure(figsize=(12, 6))
    for name, opt in optimizers_ratio.items():
         history = opt.history
         if not history['bests'].empty:
             bests_df = history['bests']
             metrics_array = np.array(opt.all_bests_metrics).flatten()
             if len(metrics_array) == len(bests_df):
                 plt.plot(bests_df['iter'], metrics_array, label=f"Default {name}", linewidth=2)
             else:
                  print(f"Warning: Mismatch ratio plot length for '{name}'")

    plt.xlabel('Iteration')
    plt.ylabel('Rosenbrock Function Value (lower is better)')
    plt.title('Convergence Comparison: Different Default Value Ratios')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('default_ratios_comparison.png')
    plt.close()
    print("\nComparison plot saved to 'default_ratios_comparison.png'")
    return optimizers_ratio

def test_invalid_defaults_ratio():
    """Test optimization with invalid ratio values that should be corrected to 0.2."""
    print("\n============ TEST: Invalid Default Ratio Values ============")
    init_pop = pd.DataFrame([{'x1': 0.5, 'x2': 0.5}, {'x1': 1.5, 'x2': 1.5}])
    test_cases = {"Negative Ratio": -0.5, "Zero Ratio": 0.0, "Ratio = 1": 1.0, "Ratio > 1": 1.5}
    optimizers_invalid = {}
    for name, ratio in test_cases.items():
        print(f"\n---- {name}: {ratio} (should be corrected to 0.2) ----")
        optimizer = run_optimization(
            details_rosenbrock, parameters_std, init_pop=init_pop.copy(),
            defaults_in_init_pop=True, defaults_in_init_pop_ratio=ratio,
            pop_size=20, max_iterations=50
        )
        optimizers_invalid[name] = optimizer
        print(f"Final result ({name}): {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizers_invalid

def test_defaults_with_full_init_pop():
    """Test case where defaults_in_init_pop is true but initial population fills entire population."""
    print("\n============ TEST: Defaults with Full Initial Population ============")
    np.random.seed(42)
    pop_size_full = 30
    full_init_pop = pd.DataFrame({
        'x1': np.random.uniform(details_rosenbrock['bounds'][0][0], details_rosenbrock['bounds'][0][1], pop_size_full),
        'x2': np.random.uniform(details_rosenbrock['bounds'][1][0], details_rosenbrock['bounds'][1][1], pop_size_full)
    })
    full_init_pop.iloc[0] = [1.1, 0.9] # Add near-optimal point
    optimizer = run_optimization(
        details_rosenbrock, parameters_std, init_pop=full_init_pop,
        defaults_in_init_pop=True, defaults_in_init_pop_ratio=0.3,
        pop_size=pop_size_full
    )
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    print("Note: Since init_pop filled the entire population, defaults should not have been incorporated.")
    return optimizer

# ----------------------------------------------------------------------------
# Comparison and Visualization - Modified
# ----------------------------------------------------------------------------
def compare_convergence(optimizers_dict):
    """Compare convergence of different optimization runs."""
    plt.figure(figsize=(12, 7))
    for name, optimizer in optimizers_dict.items():
        history = optimizer.history
        if not history['bests'].empty:
            bests_df = history['bests']
            metrics_array = np.array(optimizer.all_bests_metrics).flatten()
            # Check length consistency
            if len(metrics_array) == len(bests_df):
                 plt.plot(bests_df['iter'], metrics_array, label=name, alpha=0.8)
            else:
                 print(f"Warning: Length mismatch for '{name}'. Bests: {len(bests_df)}, Metrics: {len(metrics_array)}")

    plt.xlabel('Iteration')
    plt.ylabel('Rosenbrock Function Value (lower is better)')
    plt.yscale('log') # Use log scale for better view near optimum
    plt.title('Convergence Comparison: Different Initial Population Strategies')
    plt.legend(loc='upper right', fontsize='small')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.savefig('init_pop_convergence_comparison.png')
    print("\nOverall convergence plot saved to 'init_pop_convergence_comparison.png'")
    # plt.show()
    plt.close()

# Visualize using the test_functions plotter
def visualize_best_result(optimizer, details):
    """Visualize the function and the best result found by the optimizer."""
    print(f"\nVisualizing function '{details.get('name', 'Unknown')}' and best result...")
    fig, axes = plot_test_function(details)
    if axes and len(axes) > 1: # Add to contour plot
        ax_contour = axes[1]
        best_p = optimizer.best_parameters
        if 'x1' in best_p and 'x2' in best_p: # Check if parameters exist
             ax_contour.scatter(best_p['x1'], best_p['x2'], color='black', s=120, marker='X', label='DE Best Found', zorder=6)
             ax_contour.legend()
        else:
             print("Warning: Could not plot best parameters (missing x1 or x2).")
    save_name = f"{details.get('name', 'function')}_visualization_with_result.png"
    fig.savefig(save_name)
    print(f"Visualization saved to '{save_name}'")
    # plt.show()
    plt.close(fig)

# ----------------------------------------------------------------------------
# Main Execution Block
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    # Check available functions
    print("Available test functions:", list_available_functions())

    # --- Run all tests and collect optimizers ---
    all_optimizers = {}

    # Basic tests
    all_optimizers['No Init Pop'] = test_no_init_pop()
    all_optimizers['DataFrame'] = test_dataframe_init_pop()
    all_optimizers['CSV File'] = test_csv_init_pop()
    all_optimizers['JSON File'] = test_json_init_pop()
    all_optimizers['List of Dicts'] = test_list_dict_init_pop()

    # Edge cases
    all_optimizers['Missing Params'] = test_missing_params_init_pop()
    all_optimizers['Extra Params'] = test_extra_params_init_pop()
    all_optimizers['Large Pop'] = test_large_init_pop()
    all_optimizers['Duplicates'] = test_duplicate_rows_init_pop()
    all_optimizers['With Defaults'] = test_defaults_in_init_pop()
    all_optimizers['Optimal Value'] = test_init_pop_with_optimal_value()

    # Default value incorporation tests
    all_optimizers['Defaults Only'] = test_defaults_without_init_pop()
    all_optimizers['Defaults + Full Init'] = test_defaults_with_full_init_pop()
    invalid_ratio_results = test_invalid_defaults_ratio()
    all_optimizers.update({f'Invalid Ratio: {k}': v for k, v in invalid_ratio_results.items()})
    ratio_results = test_defaults_with_different_ratios()
    all_optimizers.update({f'Default {k}': v for k, v in ratio_results.items()})

    # Out-of-range tests
    out_of_range_results = test_out_of_range_params()
    all_optimizers.update({f'Out-of-Range: {k}': v for k, v in out_of_range_results.items()})

    # --- Compare and Visualize ---
    # Remove None entries if any test failed critically
    valid_optimizers = {k: v for k, v in all_optimizers.items() if v is not None}

    if valid_optimizers:
        compare_convergence(valid_optimizers)

        # Find the overall best optimizer from all runs
        best_optimizer_name = min(valid_optimizers, key=lambda k: valid_optimizers[k].best_metric)
        best_optimizer = valid_optimizers[best_optimizer_name]
        print(f"\nOverall best performance found with strategy: '{best_optimizer_name}'")
        visualize_best_result(best_optimizer, details_rosenbrock)

        # --- Print Summary Table ---
        print("\n===================== SUMMARY =====================")
        print("Test Name              | Final Metric   | Distance to Optimum (1,1)")
        print("-" * 60)
        opt_loc = details_rosenbrock['optimum_loc']
        for name, opt in valid_optimizers.items():
            if opt.best_parameters is not None and 'x1' in opt.best_parameters and 'x2' in opt.best_parameters:
                 x1 = opt.best_parameters['x1']
                 x2 = opt.best_parameters['x2']
                 dist = np.sqrt((x1 - opt_loc[0])**2 + (x2 - opt_loc[1])**2)
                 print(f"{name:22} | {opt.best_metric:14.6f} | {dist:20.6f}")
            else:
                 print(f"{name:22} | {'N/A':<14} | {'N/A':<20}")
        print("-" * 60)
    else:
        print("\nNo valid optimizer results to summarize or visualize.")

    print("\nInitial population tests finished.")
