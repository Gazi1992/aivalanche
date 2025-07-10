"""
Test file for the adaptive boundaries feature in DifferentialEvolution.

This script tests whether the optimizer can find an optimum located outside
the initial parameter boundaries when adaptive boundaries are enabled.
It uses the 2D Sphere function and compares runs with adaptive boundaries
enabled versus disabled.
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
    generate_parameters_config, # We might override bounds, but keep for structure
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
    """Simple callback to print progress periodically."""
    if iteration % 25 == 0 or iteration == 1:
        print(f"  Iter {iteration}: Best metric = {best_metric:.6f}")

def callback_after_better_solution(iteration, best_parameters, best_metric, **kwargs):
    """Callback for when a better solution is found."""
    print(f"  -> New best @ iter {iteration}: metric = {best_metric:.6f}, params = {dict(best_parameters)}")

# ----------------------------------------------------------------------------
# Main function to test adaptive vs fixed boundaries
# ----------------------------------------------------------------------------
def test_adaptive_vs_fixed_boundaries():
    """
    Tests and compares optimization runs with adaptive boundaries enabled vs disabled,
    starting with initial bounds that exclude the known optimum. Uses Sphere 2D.
    """
    print("\n=== Testing Adaptive vs Fixed Boundaries (Optimum Outside Initial Bounds) ===\n")

    func_name = "sphere_2d"
    try:
        # Get standard details, but we will override the bounds
        details_sphere = get_function_details(func_name)
        opt_loc = details_sphere['optimum_loc'] # Known optimum is [0, 0]
    except (KeyError, ValueError) as e:
        print(f"Fatal Error: Could not get Sphere 2D details: {e}")
        return None

    # --- Define CUSTOM initial bounds that EXCLUDE the optimum (0,0) ---
    custom_bounds = [
        (1.0, 3.0),  # x1 between 1 and 3
        (-3.0, -1.0) # x2 between -3 and -1
    ]
    print(f"Using custom initial bounds: x1 in [{custom_bounds[0][0]}, {custom_bounds[0][1]}], "
          f"x2 in [{custom_bounds[1][0]}, {custom_bounds[1][1]}]")
    print(f"Optimum at {opt_loc} is outside these initial bounds.")

    # --- Create Parameter Configuration with CUSTOM bounds ---
    # Manually create config list to ensure custom bounds are used
    param_config_custom = [
        {"name": "x1", "min": custom_bounds[0][0], "max": custom_bounds[0][1], "default": 2.0, "scale": "lin", "mode": "variable"},
        {"name": "x2", "min": custom_bounds[1][0], "max": custom_bounds[1][1], "default": -2.0, "scale": "lin", "mode": "variable"}
    ]
    parameters_custom = Parameters(param_config_custom)

    # --- Optimizer Settings ---
    optimizers = {}
    common_seed = 50
    common_pop_size = 40
    common_max_iterations = 200
    common_max_no_improve = 60
    # Use default adaptive boundary settings from the class definition

    # --- Run 1: Adaptive Boundaries ENABLED ---
    print("\n--- Running with Adaptive Boundaries ENABLED ---")
    optimizer_adaptive = DifferentialEvolution(
        seed=common_seed,
        eval_func=evaluate_test_function,
        eval_func_args={'func_details': details_sphere},
        parameters=parameters_custom, # Use custom-bounded parameters
        pop_size=common_pop_size,
        max_iterations=common_max_iterations,
        opt_min_or_max='min',
        max_iter_without_improvement=common_max_no_improve,
        callback_after_each_iter=callback_after_each_iter,
        # callback_after_better_solution=callback_after_better_solution,
        adaptive_boundaries=True # <<< ENABLED
    )
    optimizer_adaptive.run_optimization()
    optimizers['Adaptive'] = optimizer_adaptive
    print("--- Adaptive run finished ---")

    # --- Run 2: Adaptive Boundaries DISABLED ---
    print("\n--- Running with Adaptive Boundaries DISABLED ---")
    optimizer_fixed = DifferentialEvolution(
        seed=common_seed, # Use same seed for comparison
        eval_func=evaluate_test_function,
        eval_func_args={'func_details': details_sphere},
        parameters=parameters_custom, # Use same custom-bounded parameters
        pop_size=common_pop_size,
        max_iterations=common_max_iterations,
        opt_min_or_max='min',
        max_iter_without_improvement=common_max_no_improve,
        callback_after_each_iter=callback_after_each_iter,
        # callback_after_better_solution=callback_after_better_solution,
        adaptive_boundaries=False # <<< DISABLED
    )
    optimizer_fixed.run_optimization()
    optimizers['Fixed'] = optimizer_fixed
    print("--- Fixed run finished ---")

    # --- Comparison ---
    print("\n=== Comparison: Adaptive vs Fixed Boundaries ===")

    # 1. Final Results Table
    print("\nFinal Results:")
    print("-" * 70)
    print(f"{'Boundary Mode':<15} | {'Final Metric':<15} | {'Best Params':<30} | {'Dist to Optimum':<15}")
    print("-" * 70)
    for mode, optimizer in optimizers.items():
        best_p_str = "N/A"
        dist_str = "N/A"
        if optimizer.best_parameters is not None:
            best_p = optimizer.best_parameters
            best_p_str = f"x1={best_p.get('x1', np.nan):.3f}, x2={best_p.get('x2', np.nan):.3f}"
            x1 = best_p.get('x1', np.nan)
            x2 = best_p.get('x2', np.nan)
            if not (np.isnan(x1) or np.isnan(x2)):
                dist = np.sqrt((x1 - opt_loc[0])**2 + (x2 - opt_loc[1])**2)
                dist_str = f"{dist:.4f}"

        print(f"{mode:<15} | {optimizer.best_metric:<15.6f} | {best_p_str:<30} | {dist_str:<15}")
    print("-" * 70)
    print(f"(Expected optimum is {opt_loc} with value 0.0)")


    # 2. Convergence Plot
    plt.figure(figsize=(10, 6))
    for mode, optimizer in optimizers.items():
        history = optimizer.history
        if not history['bests'].empty:
            bests_df = history['bests']
            metrics_array = np.array(optimizer.all_bests_metrics).flatten()
            if len(metrics_array) == len(bests_df):
                plt.plot(bests_df['iter'], metrics_array, label=f"{mode} Boundaries", linewidth=2, alpha=0.9)
            else:
                print(f"Warning: Mismatch plot length for '{mode}'")

    plt.xlabel('Iteration')
    plt.ylabel('Best Metric (Sphere Function Value - lower is better)')
    plt.yscale('log') # Log scale usually helpful
    plt.title('Convergence: Adaptive vs Fixed Boundaries (Optimum Outside Initial Bounds)')
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    conv_plot_filename = 'adaptive_vs_fixed_convergence.png'
    plt.savefig(conv_plot_filename)
    print(f"\nConvergence plot saved to '{conv_plot_filename}'")
    plt.close()

    # 3. Boundary Evolution Plot (Only for the Adaptive run)
    print("\nPlotting boundary evolution for the Adaptive run...")
    fig_bound, ax_bound = optimizer_adaptive.plot_boundaries(
        normed=False, # Plot denormalized bounds to see real expansion
        title="Boundary Evolution (Adaptive Run)"
    )
    bound_plot_filename = 'adaptive_boundary_evolution.png'
    fig_bound.savefig(bound_plot_filename)
    print(f"Boundary evolution plot saved to '{bound_plot_filename}'")
    plt.close(fig_bound)

    # 4. Plot the Test Function and Results
    print("\nPlotting Sphere function with final results...")
    fig_func, axes_func = plot_test_function(details_sphere)
    if axes_func and len(axes_func) > 1:
        ax_contour = axes_func[1] # Add points to the contour plot
        colors = {'Adaptive': 'blue', 'Fixed': 'red'}
        markers = {'Adaptive': 'X', 'Fixed': 'P'} # X for adaptive, + for fixed
        for mode, optimizer in optimizers.items():
             if optimizer.best_parameters is not None:
                 best_p = optimizer.best_parameters
                 ax_contour.scatter(best_p.get('x1', np.nan), best_p.get('x2', np.nan),
                                    color=colors[mode], s=150, marker=markers[mode],
                                    label=f'{mode} Best Found', zorder=6, alpha=0.8)
        ax_contour.legend()
    func_plot_filename = 'sphere_function_with_results.png'
    fig_func.savefig(func_plot_filename)
    print(f"Function plot with results saved to '{func_plot_filename}'")
    plt.close(fig_func)


    return optimizers

# ----------------------------------------------------------------------------
# Main Execution Block
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    # Run the test
    results = test_adaptive_vs_fixed_boundaries()
    print("\nAdaptive boundaries test finished.")
