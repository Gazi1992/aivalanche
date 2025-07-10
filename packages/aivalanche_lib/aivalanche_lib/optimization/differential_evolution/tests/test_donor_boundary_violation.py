"""
Test file for boundary constraint methods in DifferentialEvolution,
using the test_functions package.

This script tests the different strategies ('random_from_target', 'clamp', 'random')
for handling donor vectors that violate boundaries, using the 2D Rosenbrock function.
"""

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
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
# Generic Evaluation Function (Copied from updated simple_test.py)
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
# Callbacks (remain similar)
# ----------------------------------------------------------------------------
def callback_after_each_iter(iteration, best_metric, **kwargs):
    """Simple callback to print progress periodically."""
    if iteration % 20 == 0 or iteration == 1:
        print(f"  Iter {iteration}: Best metric = {best_metric:.6f}")

def callback_after_better_solution(iteration, best_parameters, best_metric, **kwargs):
    """Callback for when a better solution is found."""
    print(f"  -> New best @ iter {iteration}: metric = {best_metric:.6f}, params = {dict(best_parameters)}")

# ----------------------------------------------------------------------------
# Main function to test the boundary constraint methods - Modified
# ----------------------------------------------------------------------------
def test_boundary_constraints():
    """Tests and compares the different boundary constraint methods using Rosenbrock 2D."""
    print("\n=== Testing Donor Boundary Constraint Methods (using test_functions) ===\n")

    func_name = "rosenbrock_2d"
    try:
        details_rosenbrock = get_function_details(func_name)
        param_config = generate_parameters_config(details_rosenbrock)
        parameters = Parameters(param_config)
        opt_loc = details_rosenbrock['optimum_loc'] # Store optimum location
    except (KeyError, ValueError) as e:
        print(f"Fatal Error: Could not get Rosenbrock details: {e}")
        return None

    strategies = ['random_from_target', 'clamp', 'random']
    optimizers = {}
    common_seed = 42
    common_pop_size = 30
    common_max_iterations = 150
    common_max_no_improve = 50

    for strategy in strategies:
        print(f"--- Running strategy: {strategy} ---")

        optimizer = DifferentialEvolution(
            seed=common_seed,
            eval_func=evaluate_test_function, # Use generic evaluator
            eval_func_args={'func_details': details_rosenbrock}, # Pass details
            parameters=parameters, # Use parameters object created above
            pop_size=common_pop_size,
            max_iterations=common_max_iterations,
            opt_min_or_max='min', # Minimize Rosenbrock directly
            max_iter_without_improvement=common_max_no_improve,
            callback_after_each_iter=callback_after_each_iter,
            # callback_after_better_solution=callback_after_better_solution, # Can be verbose
            adaptive_boundaries=False, # Keep adaptive boundaries off
            boundary_constraint_method=strategy # Set the strategy here
        )

        optimizer.run_optimization()
        optimizers[strategy] = optimizer
        print(f"--- Strategy '{strategy}' finished ---")
        print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}\n")

    # --- Comparison ---
    print("\n=== Comparison of Boundary Constraint Strategies ===")

    # 1. Final Results Table - Updated parameter names
    print("\nFinal Results:")
    print("-" * 65)
    print(f"{'Strategy':<25} | {'Final Metric':<15} | {'Distance to Optimum (1,1)':<20}")
    print("-" * 65)
    for strategy, optimizer in optimizers.items():
         if optimizer.best_parameters is not None:
              x1 = optimizer.best_parameters.get('x1', np.nan) # Use .get for safety
              x2 = optimizer.best_parameters.get('x2', np.nan)
              dist = np.sqrt((x1 - opt_loc[0])**2 + (x2 - opt_loc[1])**2) if not (np.isnan(x1) or np.isnan(x2)) else np.nan
              print(f"{strategy:<25} | {optimizer.best_metric:<15.6f} | {dist:<20.6f}")
         else:
              print(f"{strategy:<25} | {'N/A':<15} | {'N/A':<20}")
    print("-" * 65)

    # 2. Convergence Plot
    plt.figure(figsize=(12, 7))
    for strategy, optimizer in optimizers.items():
        history = optimizer.history
        if not history['bests'].empty:
            bests_df = history['bests']
            metrics_array = np.array(optimizer.all_bests_metrics).flatten()
            if len(metrics_array) == len(bests_df):
                 plt.plot(bests_df['iter'], metrics_array, label=f"Strategy: {strategy}", linewidth=2, alpha=0.8)
            else:
                 print(f"Warning: Mismatch plot length for '{strategy}'")

    plt.xlabel('Iteration')
    plt.ylabel('Best Metric (Rosenbrock Function Value - lower is better)')
    plt.yscale('log') # Log scale often helpful
    plt.title('Convergence Comparison of Boundary Constraint Methods')
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plot_filename = 'boundary_constraint_strategies_comparison.png'
    plt.savefig(plot_filename)
    print(f"\nConvergence plot saved to '{plot_filename}'")
    plt.close() # Close plot

    return optimizers

# ----------------------------------------------------------------------------
# Main Execution Block
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    # Run the test
    results = test_boundary_constraints()
    print("\nBoundary constraint test finished.")
