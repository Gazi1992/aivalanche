"""
Test file for the DifferentialEvolution class using the test_functions package.

This script provides simple test cases to debug the DifferentialEvolution optimizer.
It includes two test functions obtained from the test_functions package:
1. A 2-parameter function (Rosenbrock) that can be easily visualized
2. A 6-parameter function (Ackley) that tests optimization in higher dimensions
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
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
from aivalanche_lib.optimization.differential_evolution.visualizations import _plot_population_animation

# ----------------------------------------------------------------------------
# Animation Function for 2D Problems
# ----------------------------------------------------------------------------

def create_de_animation(optimizer, output_dir, func_details=None):
    """
    Wrapper function to create population animation using the visualizations module.
    
    Args:
        optimizer: The DifferentialEvolution optimizer instance
        output_dir: Directory to save the animation
        func_details: Function details dictionary (optional, for creating heatmap)
    """
    # Prepare save path
    save_path = os.path.join(output_dir, 'de_animation.gif')
    
    # Call the animation function from visualizations
    fig, anim = _plot_population_animation(
        optimizer,
        param_names=None,  # Will use first two parameters
        figsize=(10, 8),
        interval=100,
        fps=10,
        save_path=save_path,
        func_details=func_details
    )
    
    # Note: The function now supports heatmap background when func_details is provided
    
    if fig is not None:
        plt.close(fig)
        print(f"Animation saved to: {save_path}")
    else:
        print("Could not create animation")

# ----------------------------------------------------------------------------
# Generic Evaluation Function for Optimizers
# ----------------------------------------------------------------------------

def evaluate_test_function(parameters: pd.DataFrame, func_details: dict, **kwargs) -> List[Dict[str, Any]]:
    """
    Generic evaluation function wrapper for test functions from the package.

    Args:
        parameters (pd.DataFrame): DataFrame of parameters from the optimizer.
                                   Columns should be 'x1', 'x2', ...
        func_details (dict): The details dictionary for the test function
                             (obtained from get_function_details).
        **kwargs: Additional arguments possibly passed by the optimizer.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each containing at least 'metric'.
    """
    results = []
    target_func = func_details['func'] # The actual callable test function
    dim = func_details['dim']
    param_names = [f'x{i+1}' for i in range(dim)] # Expected parameter names

    params_list = parameters.to_dict('records')

    for params_row in params_list:
        # Construct the input vector for the test function
        try:
            input_vector = np.array([params_row[name] for name in param_names])
        except KeyError as e:
            print(f"Error: Missing parameter {e} in optimizer output.")
            print(f"Expected parameters: {param_names}")
            print(f"Received parameters: {list(params_row.keys())}")
            # Assign a penalty value or re-raise
            value = float('inf') # Assign large penalty for minimization
        else:
            # Call the actual test function (e.g., rosenbrock, ackley)
            value = target_func(input_vector)

        # Store results - Assuming MINIMIZATION for standard test functions
        results.append({
            'metric': value,
            'value': value # Store original value if needed separately
        })

    return results

# ----------------------------------------------------------------------------
# Callback functions
# ----------------------------------------------------------------------------
def callback_after_each_iter(iteration, parameters, responses, best_parameters, best_metric, **kwargs):
    """Simple callback to print progress after each iteration."""
    if iteration % 50 == 0 or iteration == 1: # Print less frequently
      print(f"Iter {iteration}: Best metric = {best_metric:.6f}")

def callback_after_better_solution(iteration, best_parameters, best_metric, **kwargs):
    """Callback for when a better solution is found."""
    # Limit printing frequency if needed
    # if iteration % 10 == 0 or iteration < 5:
    print(f"  -> New best @ iter {iteration}: metric = {best_metric:.6f}, params = {dict(best_parameters)}")
    # print("-" * 60) # Optional separator

# ----------------------------------------------------------------------------
# Test with 2D Rosenbrock function using the package
# ----------------------------------------------------------------------------
def test_rosenbrock(results_base_dir=None):
    """Test DifferentialEvolution with 2D Rosenbrock function from the package."""
    print("\n=== Testing with 2D Rosenbrock function (from test_functions) ===\n")

    func_name = "rosenbrock_2d"
    try:
        details_rosenbrock = get_function_details(func_name)
    except (KeyError, ValueError) as e:
        print(f"Error getting function details: {e}")
        return None

    # Generate parameter configuration and create Parameters object
    param_config = generate_parameters_config(details_rosenbrock)
    parameters = Parameters(param_config)
    
    # Set up results directory
    if results_base_dir is None:
        results_base_dir = os.path.dirname(__file__)
    test_results_dir = os.path.join(results_base_dir, 'test_results_rosenbrock_2d')
    os.makedirs(test_results_dir, exist_ok=True)

    # Create optimizer
    optimizer = DifferentialEvolution(
        seed=42,
        # Pass the evaluation function and the necessary details via eval_func_args
        eval_func=evaluate_test_function,
        eval_func_args={'func_details': details_rosenbrock},
        parameters=parameters,
        pop_size=30,
        max_iterations=300, # Reduced iterations for quicker test
        opt_min_or_max='min',  # Minimizing Rosenbrock directly
        max_iter_without_improvement=100,
        callback_after_each_iter=callback_after_each_iter,
        callback_after_better_solution=callback_after_better_solution,
        adaptive_boundaries=False, # Keep adaptive boundaries for this test
        boundary_constraint_method='clamp', # Example: Test clamping
        results_dir=test_results_dir
    )

    # Run optimization
    optimizer.run_optimization()

    # --- Results ---
    print("\nFinal results (Rosenbrock):")
    print(f"Best metric (min value): {optimizer.best_metric:.6f}")
    print(f"Best parameters found: {optimizer.best_parameters}")
    print(f"Expected optimum value: {details_rosenbrock['optimum_val']}")
    print(f"Expected optimum location: {details_rosenbrock['optimum_loc']}")

    # --- Plotting ---
    print("\nGenerating plots...")
    # Optimizer history plots
    fig_met_b, ax_met_b = optimizer.plot_metrics(which='bests', y_scale='log', title="Best Metric Evolution (Rosenbrock)")
    fig_met_b.savefig(os.path.join(test_results_dir, "metrics_evolution.png"))

    fig_hist, ax_hist = optimizer.plot_all_parameters_evolution(which='survivors', nr_rows=1, title="Survivor Parameter Distributions (Rosenbrock)")
    fig_hist.savefig(os.path.join(test_results_dir, "survivor_histograms.png"))

    if optimizer.adaptive_boundaries:
        fig_bound, ax_bound = optimizer.plot_boundaries(normed=False, title="Boundary Evolution (Rosenbrock)")
        fig_bound.savefig(os.path.join(test_results_dir, "boundaries.png"))

    # Plot the test function itself using the package plotter
    fig_func, axes_func = plot_test_function(details_rosenbrock)
    # Optionally plot the found optimum on the contour plot
    if axes_func and len(axes_func) > 1:
        ax_contour = axes_func[1]
        best_p = optimizer.best_parameters
        ax_contour.scatter(best_p['x1'], best_p['x2'], color='black', s=120, marker='X', label='DE Best Found', zorder=6)
        ax_contour.legend()
    fig_func.savefig(os.path.join(test_results_dir, "function_plot.png"))

    plt.close('all') # Close plots to avoid displaying them if running multiple tests
    print("Plots saved.")
    
    # Create animation for 2D problem
    print("\nCreating animation...")
    create_de_animation(optimizer, test_results_dir, func_details=details_rosenbrock)

    # Save results
    optimizer.write_best_parameters_to_file(os.path.join(test_results_dir, 'best_parameters.csv'))
    optimizer.write_optimization_info_to_file(os.path.join(test_results_dir, 'optimization_info.json'))
    
    # Save history files
    for history_type in ['bests', 'trials']:
        optimizer.write_history_to_file(
            which=history_type,
            file_path=os.path.join(test_results_dir, f'history_{history_type}.csv')
        )
    
    print(f"\nAll files saved to: {test_results_dir}")

    return optimizer

# ----------------------------------------------------------------------------
# Test with 6D Ackley function using the package
# ----------------------------------------------------------------------------
def test_ackley(results_base_dir=None):
    """Test DifferentialEvolution with 6D Ackley function from the package."""
    print("\n=== Testing with 6D Ackley function (from test_functions) ===\n")

    func_name = "ackley_nd"
    target_dim = 6
    try:
        details_ackley = get_function_details(func_name, n_dim=target_dim)
    except (KeyError, ValueError) as e:
        print(f"Error getting function details: {e}")
        return None

    # Generate parameter configuration and create Parameters object
    param_config = generate_parameters_config(details_ackley)
    parameters = Parameters(param_config)
    
    # Set up results directory
    if results_base_dir is None:
        results_base_dir = os.path.dirname(__file__)
    test_results_dir = os.path.join(results_base_dir, 'test_results_ackley_6d')
    os.makedirs(test_results_dir, exist_ok=True)

    # Create optimizer
    optimizer = DifferentialEvolution(
        seed=42,
        # Pass the evaluation function and the necessary details via eval_func_args
        eval_func=evaluate_test_function,
        eval_func_args={'func_details': details_ackley},
        parameters=parameters,
        pop_size=60, # Often need larger pop_size for higher dimensions
        max_iterations=500, # Increased iterations
        opt_min_or_max='min',  # Minimizing Ackley directly
        max_iter_without_improvement=75,
        callback_after_each_iter=callback_after_each_iter,
        # callback_after_better_solution=callback_after_better_solution, # Can be verbose
        adaptive_boundaries=False, # Keep boundaries fixed for this multimodal test
        results_dir=test_results_dir
    )

    # Run optimization
    optimizer.run_optimization()

    # --- Results ---
    print("\nFinal results (Ackley 6D):")
    print(f"Best metric (min value): {optimizer.best_metric:.6f}")
    print(f"Best parameters found: {optimizer.best_parameters}")
    print(f"Expected optimum value: {details_ackley['optimum_val']}")
    print(f"Expected optimum location: {details_ackley['optimum_loc']} (all zeros)")

    # --- Plotting ---
    print("\nGenerating plots...")
    # Optimizer history plots
    fig_met_b, ax_met_b = optimizer.plot_metrics(which='bests', y_scale='linear', title="Best Metric Evolution (Ackley 6D)")
    fig_met_b.savefig(os.path.join(test_results_dir, "metrics_evolution.png"))

    fig_hist, ax_hist = optimizer.plot_all_parameters_evolution(which='survivors', nr_rows=2, title="Survivor Parameter Distributions (Ackley 6D)")
    fig_hist.savefig(os.path.join(test_results_dir, "survivor_histograms.png"))

    # Cannot plot the function itself in 6D
    print("Cannot plot 6D function visually.")

    plt.close('all')
    print("Plots saved.")

    # Save results
    optimizer.write_best_parameters_to_file(os.path.join(test_results_dir, 'best_parameters.csv'))
    optimizer.write_optimization_info_to_file(os.path.join(test_results_dir, 'optimization_info.json'))
    
    # Save history files
    for history_type in ['bests', 'trials']:
        optimizer.write_history_to_file(
            which=history_type,
            file_path=os.path.join(test_results_dir, f'history_{history_type}.csv')
        )
    
    print(f"\nAll files saved to: {test_results_dir}")

    return optimizer


# ----------------------------------------------------------------------------
# Main Execution Block
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    print("Available test functions via package:", list_available_functions())

    # Run tests
    print("-" * 70)
    rosenbrock_optimizer = test_rosenbrock()
    print("-" * 70)

    # Uncomment to test with Ackley function
    ackley_optimizer = test_ackley()
    print("-" * 70)

    print("\nSimple tests finished.")
    print("Check saved plots and CSV/JSON files for results.")
