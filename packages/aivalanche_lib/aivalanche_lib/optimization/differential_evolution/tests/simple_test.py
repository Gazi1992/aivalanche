"""
Test file for the DifferentialEvolution class.

This script provides simple test cases to debug the DifferentialEvolution optimizer.
It includes two test functions:
1. A 2-parameter function (Rosenbrock) that can be easily visualized
2. A 6-parameter function (Ackley) that tests optimization in higher dimensions
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

# Import your modules
from aivalanche_lib import Parameters
from aivalanche_lib import DifferentialEvolution

# Define test functions

def rosenbrock(x, y):
    """
    Rosenbrock function - a classic optimization test function.
    Global minimum at (1, 1) with a value of 0.
    Has a narrow valley which is difficult for optimizers to navigate.
    """
    return (1 - x)**2 + 100 * (y - x**2)**2

def ackley(x):
    """
    Ackley function - a multimodal test function.
    Global minimum at origin with a value of 0.
    Has many local minima and tests ability to escape them.
    """
    n = len(x)
    a = 20
    b = 0.2
    c = 2 * np.pi

    sum1 = np.sum(np.square(x))
    sum2 = np.sum(np.cos(c * x))

    term1 = -a * np.exp(-b * np.sqrt(sum1 / n))
    term2 = -np.exp(sum2 / n)

    return term1 + term2 + a + np.exp(1)

# Evaluation functions for the optimizer

def evaluate_rosenbrock(parameters, **kwargs):
    """Evaluation function for Rosenbrock function."""
    results = []

    # Convert DataFrame to list of dictionaries
    params_list = parameters.to_dict('records')

    for params in params_list:
        x = params['x']
        y = params['y']
        value = rosenbrock(x, y)

        results.append({
            'metric': -value,  # Negative because we're maximizing
            'value': value
        })

    return results

def evaluate_ackley(parameters, **kwargs):
    """Evaluation function for Ackley function."""
    results = []

    # Convert DataFrame to list of dictionaries
    params_list = parameters.to_dict('records')

    for params in params_list:
        x_vals = [
            params['x1'],
            params['x2'],
            params['x3'],
            params['x4'],
            params['x5'],
            params['x6']
        ]
        value = ackley(np.array(x_vals))

        results.append({
            'metric': value,  # Negative because we're maximizing
            'value': value
        })

    return results

# Callback functions
def callback_after_each_iter(iteration, parameters, responses, best_parameters, best_metric, **kwargs):
    """Simple callback to print progress after each iteration."""
    print(f"Iteration {iteration}: Best metric = {best_metric}")

def callback_after_better_solution(iteration, best_parameters, best_metric, **kwargs):
    """Callback for when a better solution is found."""
    print(f"Better solution found at iteration {iteration}:")
    print(f"  Best metric = {best_metric}")
    print(f"  Best parameters = {best_parameters}")
    print("-" * 60)

# Test with 2D Rosenbrock function

def test_rosenbrock():
    """Test DifferentialEvolution with 2D Rosenbrock function."""
    print("\n=== Testing with 2D Rosenbrock function ===\n")

    # Define parameters
    params_data = [
        {"name": "x", "min": -2.0, "max": 2.0, "default": 0.0, "scale": "lin", "mode": "variable"},
        {"name": "y", "min": 5.0, "max": 10.0, "default": 0.0, "scale": "lin", "mode": "variable"}
    ]

    parameters = Parameters(params_data)

    # Create optimizer
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=evaluate_rosenbrock,
        parameters=parameters,
        pop_size=30,
        max_iterations=1000,
        opt_min_or_max='max',  # We're maximizing -rosenbrock
        max_iter_without_improvement=100,
        callback_after_each_iter=callback_after_each_iter,
        callback_after_better_solution=callback_after_better_solution,
        adaptive_boundaries=True
    )

    # Run optimization
    optimizer.run_optimization()

    # Print results
    print("\nFinal results:")
    print(f"Best metric: {optimizer.best_metric}")
    print(f"Best parameters: {optimizer.best_parameters}")
    print(f"Expected optimum: x=1.0, y=1.0")

    optimizer.plot_metrics(which = 'trials')
    optimizer.plot_metrics(which = 'survivors')
    optimizer.plot_metrics(which = 'bests')

    optimizer.plot_all_parameters_evolution(which = 'trials', iter_end=2)
    optimizer.plot_all_parameters_evolution(which = 'survivors')

    optimizer.plot_single_parameter_evolution(which = 'trials', parameter_name = 'y', cmap = 'jet')
    optimizer.plot_single_parameter_evolution(which = 'survivors', parameter_name = 'x', cmap = 'viridis')

    optimizer.plot_boundaries(normed=True)
    optimizer.plot_boundaries(normed=False)

    optimizer.write_best_parameters_to_file('best_parameters.csv')
    optimizer.write_current_population_to_file('last_population.csv')

    stats = optimizer.stats

    # Visualize the function and optimization result
    visualize_rosenbrock(optimizer.best_parameters)

    return optimizer

# Test with 6D Ackley function
def test_ackley():
    """Test DifferentialEvolution with 6D Ackley function."""
    print("\n=== Testing with 6D Ackley function ===\n")

    # Define parameters
    params_data = [
        {"name": "x1", "min": -5.0, "max": 5.0, "default": 0.0, "scale": "lin", "mode": "variable"},
        {"name": "x2", "min": 1, "max": 5.0, "default": 2.0, "scale": "log", "mode": "variable"},
        {"name": "x3", "min": -5.0, "max": 5.0, "default": 0.0, "scale": "lin", "mode": "variable"},
        {"name": "x4", "min": -5.0, "max": 5.0, "default": 0.0, "scale": "lin", "mode": "variable"},
        {"name": "x5", "min": -5.0, "max": 5.0, "default": 0.0, "scale": "lin", "mode": "variable"},
        {"name": "x6", "min": -5.0, "max": 5.0, "default": 0.0, "scale": "lin", "mode": "variable"}
    ]

    parameters = Parameters(params_data)

    # Create optimizer
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=evaluate_ackley,
        parameters=parameters,
        pop_size=50,
        max_iterations=1000,
        opt_min_or_max='min',  # We're maximizing -ackley
        max_iter_without_improvement=50,
        callback_after_each_iter=callback_after_each_iter,
        callback_after_better_solution=callback_after_better_solution
    )

    # Run optimization
    optimizer.run_optimization()

    optimizer.plot_metrics(which = 'trials', y_scale = 'linear')
    optimizer.plot_metrics(which = 'survivors', y_scale = 'linear')
    optimizer.plot_metrics(which = 'bests', y_scale = 'linear')
    optimizer.plot_all_parameters_evolution(which = 'trials', iter_end = 20, cmap = 'jet')
    optimizer.plot_all_parameters_evolution(which = 'survivors', cmap = 'viridis', nr_rows=2)

    # Print results
    print("\nFinal results:")
    print(f"Best metric: {optimizer.best_metric}")
    print(f"Best parameters: {optimizer.best_parameters}")
    print(f"Expected optimum: all parameters = 0.0")

    return optimizer

def visualize_rosenbrock(best_params=None):
    """Visualize the Rosenbrock function and optimization result."""
    x = np.linspace(-2, 2, 100)
    y = np.linspace(-1, 3, 100)
    X, Y = np.meshgrid(x, y)
    Z = rosenbrock(X, Y)

    # Create 3D surface plot
    fig = plt.figure(figsize=(12, 10))
    ax1 = fig.add_subplot(221, projection='3d')
    surf = ax1.plot_surface(X, Y, Z, cmap=cm.coolwarm, linewidth=0, antialiased=True, alpha=0.7)
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_zlabel('f(X,Y)')
    ax1.set_title('Rosenbrock Function')

    # If we have optimization result, plot it
    if best_params is not None:
        x_best = best_params['x']
        y_best = best_params['y']
        z_best = rosenbrock(x_best, y_best)
        ax1.scatter([x_best], [y_best], [z_best], color='black', s=100, marker='o')

    # Create contour plot
    ax2 = fig.add_subplot(222)
    contour = ax2.contourf(X, Y, Z, 50, cmap=cm.coolwarm)
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_title('Contour Plot of Rosenbrock Function')
    fig.colorbar(contour, ax=ax2)

    # If we have optimization result, plot it
    if best_params is not None:
        ax2.scatter([x_best], [y_best], color='black', s=100, marker='x')

    # Create zoomed contour plot around minimum
    ax3 = fig.add_subplot(223)
    x_zoom = np.linspace(0.5, 1.5, 100)
    y_zoom = np.linspace(0.5, 1.5, 100)
    X_zoom, Y_zoom = np.meshgrid(x_zoom, y_zoom)
    Z_zoom = rosenbrock(X_zoom, Y_zoom)
    contour_zoom = ax3.contourf(X_zoom, Y_zoom, Z_zoom, 50, cmap=cm.coolwarm)
    ax3.set_xlabel('X')
    ax3.set_ylabel('Y')
    ax3.set_title('Zoomed View Around Minimum (1,1)')

    # If we have optimization result and it's in the zoomed region, plot it
    if best_params is not None and 0.5 <= x_best <= 1.5 and 0.5 <= y_best <= 1.5:
        ax3.scatter([x_best], [y_best], color='black', s=100, marker='x')

    # Create log contour plot to see valley structure
    ax4 = fig.add_subplot(224)
    contour_log = ax4.contourf(X, Y, np.log(Z + 1), 50, cmap=cm.coolwarm)
    ax4.set_xlabel('X')
    ax4.set_ylabel('Y')
    ax4.set_title('Log Scale Contour Plot')

    # If we have optimization result, plot it
    if best_params is not None:
        ax4.scatter([x_best], [y_best], color='black', s=100, marker='x')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Run tests
    rosenbrock_optimizer = test_rosenbrock()

    # Uncomment to test with Ackley function
    # ackley_optimizer = test_ackley()
