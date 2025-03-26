"""
Test file for initial population incorporation in DifferentialEvolution.

This script tests different scenarios for initial population handling:
1. Initial population as DataFrame
2. Initial population as CSV file
3. Initial population as JSON file
4. Initial population as list of dictionaries
5. Initial population with missing parameters
6. Initial population with extra parameters
7. Initial population with more rows than pop_size
8. Initial population with duplicate rows
9. Default values in initial population
10. Out-of-range parameter handling ('keep', 'extreme', 'random')
"""

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from tempfile import NamedTemporaryFile

# Import your modules
from aivalanche_lib import Parameters
from aivalanche_lib import DifferentialEvolution

# Define the Rosenbrock function (same as in your test file)
def rosenbrock(x, y):
    """
    Rosenbrock function - a classic optimization test function.
    Global minimum at (1, 1) with a value of 0.
    Has a narrow valley which is difficult for optimizers to navigate.
    """
    return (1 - x)**2 + 100 * (y - x**2)**2

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

# Define parameter settings
def get_parameters():
    """Get parameter definitions for the Rosenbrock function."""
    params_data = [
        {"name": "x", "min": -2.0, "max": 2.0, "default": 0.0, "scale": "lin", "mode": "variable"},
        {"name": "y", "min": -1.0, "max": 3.0, "default": 0.0, "scale": "lin", "mode": "variable"}
    ]
    return Parameters(params_data)

# Callback to track progress
def callback_after_each_iter(iteration, best_metric, **kwargs):
    if iteration % 10 == 0:
        print(f"Iteration {iteration}: Best metric = {best_metric}")

def callback_after_better_solution(iteration, best_parameters, best_metric, **kwargs):
    print(f"Better solution at iteration {iteration}: metric = {best_metric:.4f}, params = {dict(best_parameters)}")

# Base optimization function
def run_optimization(init_pop=None, defaults_in_init_pop=False, defaults_in_init_pop_ratio=0.2,
                     pop_size=30, seed=42,
                     init_pop_out_of_range_param='keep'):
    """
    Run optimization with specified initial population settings.

    Args:
        init_pop: Initial population (DataFrame, list of dicts, or file path)
        defaults_in_init_pop: Whether to incorporate default values
        pop_size: Population size for the optimizer
        seed: Random seed for reproducibility
        init_pop_out_of_range_param: Strategy for handling out-of-range parameters

    Returns:
        The optimizer instance after running optimization
    """
    parameters = get_parameters()

    optimizer = DifferentialEvolution(
        seed=seed,
        eval_func=evaluate_rosenbrock,
        parameters=parameters,
        pop_size=pop_size,
        max_iterations=100,
        opt_min_or_max='max',  # We're maximizing -rosenbrock
        max_iter_without_improvement=50,
        callback_after_each_iter=callback_after_each_iter,
        callback_after_better_solution=callback_after_better_solution,
        adaptive_boundaries=True,
        init_pop=init_pop,
        defaults_in_init_pop=defaults_in_init_pop,
        defaults_in_init_pop_ratio=defaults_in_init_pop_ratio,
        init_pop_out_of_range_param=init_pop_out_of_range_param
    )

    # Run optimization
    optimizer.run_optimization()

    return optimizer

# Test scenarios

def test_no_init_pop():
    """Test optimization without initial population (baseline)."""
    print("\n============ TEST: No Initial Population (Baseline) ============")
    optimizer = run_optimization(init_pop=None)
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizer

def test_dataframe_init_pop():
    """Test optimization with DataFrame as initial population."""
    print("\n============ TEST: DataFrame Initial Population ============")
    # Create a DataFrame with some values close to the optimum
    df = pd.DataFrame([
        {'x': 0.9, 'y': 0.9},
        {'x': 1.1, 'y': 1.1},
        {'x': 0.8, 'y': 0.8},
        {'x': 1.2, 'y': 1.2},
        {'x': 0.0, 'y': 0.0}
    ])

    optimizer = run_optimization(init_pop=df)
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizer

def test_csv_init_pop():
    """Test optimization with CSV file as initial population."""
    print("\n============ TEST: CSV File Initial Population ============")
    # Create a temporary CSV file
    with NamedTemporaryFile(suffix='.csv', mode='w+', delete=False) as tmp:
        df = pd.DataFrame([
            {'x': 0.95, 'y': 0.95},
            {'x': 1.05, 'y': 1.05},
            {'x': 0.9, 'y': 1.1},
            {'x': 1.1, 'y': 0.9}
        ])
        df.to_csv(tmp.name, index=False)
        tmp_name = tmp.name

    try:
        optimizer = run_optimization(init_pop=tmp_name)
        print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)

    return optimizer

def test_json_init_pop():
    """Test optimization with JSON file as initial population."""
    print("\n============ TEST: JSON File Initial Population ============")
    # Create a temporary JSON file
    with NamedTemporaryFile(suffix='.json', mode='w+', delete=False) as tmp:
        df = pd.DataFrame([
            {'x': 0.99, 'y': 0.99},
            {'x': 1.01, 'y': 1.01}
        ])
        df.to_json(tmp.name, orient='records')
        tmp_name = tmp.name

    try:
        optimizer = run_optimization(init_pop=tmp_name)
        print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)

    return optimizer

def test_list_dict_init_pop():
    """Test optimization with list of dictionaries as initial population."""
    print("\n============ TEST: List of Dictionaries Initial Population ============")
    init_pop = [
        {'x': 0.7, 'y': 0.7},
        {'x': 0.8, 'y': 0.8},
        {'x': 0.9, 'y': 0.9},
        {'x': 1.1, 'y': 1.1}
    ]

    optimizer = run_optimization(init_pop=init_pop)
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizer

def test_missing_params_init_pop():
    """Test optimization with initial population missing some parameters."""
    print("\n============ TEST: Initial Population with Missing Parameters ============")
    # Create a DataFrame with only x values
    df = pd.DataFrame([
        {'x': 0.9},
        {'x': 1.1}
    ])

    optimizer = run_optimization(init_pop=df)
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizer

def test_extra_params_init_pop():
    """Test optimization with initial population having extra parameters."""
    print("\n============ TEST: Initial Population with Extra Parameters ============")
    # Create a DataFrame with extra parameters
    df = pd.DataFrame([
        {'x': 0.9, 'y': 0.9, 'z': 1.0, 'extra': 'value'},
        {'x': 1.1, 'y': 1.1, 'z': 3.0, 'extra': 'value3'}
    ])

    optimizer = run_optimization(init_pop=df)
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizer

def test_large_init_pop():
    """Test optimization with initial population larger than pop_size."""
    print("\n============ TEST: Initial Population Larger than pop_size ============")
    # Create a larger DataFrame
    np.random.seed(42)
    df = pd.DataFrame({
        'x': np.random.uniform(-2, 2, 50),
        'y': np.random.uniform(-1, 3, 50)
    })
    # Add one point very close to the optimum
    df = pd.concat([df, pd.DataFrame([{'x': 1.01, 'y': 0.99}])], ignore_index=True)

    optimizer = run_optimization(init_pop=df, pop_size=30)
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizer

def test_duplicate_rows_init_pop():
    """Test optimization with initial population having duplicate rows."""
    print("\n============ TEST: Initial Population with Duplicate Rows ============")
    # Create a DataFrame with duplicates
    df = pd.DataFrame([
        {'x': 0.9, 'y': 0.9},
        {'x': 0.9, 'y': 0.9},  # Duplicate
        {'x': 1.1, 'y': 1.1}
    ])

    optimizer = run_optimization(init_pop=df)
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizer

def test_defaults_in_init_pop():
    """Test optimization with defaults incorporated in initial population."""
    print("\n============ TEST: Defaults in Initial Population ============")
    # Create a small DataFrame
    df = pd.DataFrame([
        {'x': 0.9, 'y': 0.9},
        {'x': 1.1, 'y': 1.1}
    ])

    optimizer = run_optimization(init_pop=df, defaults_in_init_pop=True)
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizer

def test_init_pop_with_optimal_value():
    """Test optimization with initial population containing the optimal value."""
    print("\n============ TEST: Initial Population with Optimal Value ============")
    # Create a DataFrame with the optimal value
    df = pd.DataFrame([
        {'x': 1.0, 'y': 1.0}  # Optimal value
    ])

    optimizer = run_optimization(init_pop=df)
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizer

def test_out_of_range_params():
    """Test different strategies for handling out-of-range parameters in initial population."""
    print("\n============ TEST: Out-of-Range Parameter Handling Strategies ============")

    # Create a special parameter set with narrower bounds for better testing
    params_data = [
        {"name": "x", "min": -1.0, "max": 1.5, "default": 0.0, "scale": "lin", "mode": "variable"},
        {"name": "y", "min": -0.5, "max": 2.0, "default": 0.0, "scale": "lin", "mode": "variable"}
    ]
    parameters = Parameters(params_data)

    # Create initial population with out-of-range values
    init_pop_df = pd.DataFrame([
        # Valid values
        {'x': 0.0, 'y': 0.0},

        # Out of range (below min)
        {'x': -2.0, 'y': -1.0},

        # Out of range (above max)
        {'x': 2.0, 'y': 3.0},

        # Mixed (one parameter in range, one out of range)
        {'x': 0.5, 'y': 2.5},
        {'x': -1.5, 'y': 1.0}
    ])

    # Save original values for comparison
    original_values = init_pop_df.copy()

    # Test with 'keep' strategy
    print("\n---- KEEP Strategy ----")
    optimizer_keep = DifferentialEvolution(
        seed=42,
        eval_func=evaluate_rosenbrock,
        parameters=parameters,
        pop_size=10,
        max_iterations=100,
        opt_min_or_max='max',
        init_pop=original_values.copy(),
        init_pop_out_of_range_param='keep'
    )
    optimizer_keep.run_optimization()
    print(f"Final result (KEEP): {optimizer_keep.best_metric:.6f} at {dict(optimizer_keep.best_parameters)}")

    # Test with 'extreme' strategy
    print("\n---- EXTREME Strategy ----")
    optimizer_extreme = DifferentialEvolution(
        seed=42,
        eval_func=evaluate_rosenbrock,
        parameters=parameters,
        pop_size=10,
        max_iterations=50,
        opt_min_or_max='max',
        init_pop=original_values.copy(),
        init_pop_out_of_range_param='extreme'
    )
    optimizer_extreme.run_optimization()
    print(f"Final result (EXTREME): {optimizer_extreme.best_metric:.6f} at {dict(optimizer_extreme.best_parameters)}")

    # Test with 'random' strategy
    print("\n---- RANDOM Strategy ----")
    optimizer_random = DifferentialEvolution(
        seed=42,
        eval_func=evaluate_rosenbrock,
        parameters=parameters,
        pop_size=10,
        max_iterations=50,
        opt_min_or_max='max',
        init_pop=original_values.copy(),
        init_pop_out_of_range_param='random'
    )
    optimizer_random.run_optimization()
    print(f"Final result (RANDOM): {optimizer_random.best_metric:.6f} at {dict(optimizer_random.best_parameters)}")

    # Compare convergence
    plt.figure(figsize=(12, 6))

    strategies = {
        'Keep': optimizer_keep,
        'Extreme': optimizer_extreme,
        'Random': optimizer_random
    }

    for name, optimizer in strategies.items():
        # Extract best metrics history
        history = optimizer.history
        bests_df = history['bests']
        iterations = bests_df['iter'].unique()
        metrics = [-optimizer.all_bests_metrics[i-1][0] for i in iterations]  # Convert back to original function value

        plt.plot(iterations, metrics, label=f"Out-of-Range Strategy: {name}", linewidth=2)

    plt.xlabel('Iteration')
    plt.ylabel('Rosenbrock Function Value (lower is better)')
    # plt.yscale('log')
    plt.title('Convergence Comparison with Different Out-of-Range Parameter Strategies')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('out_of_range_param_strategies_comparison.png')

    print("\nComparison of out-of-range handling strategies saved to 'out_of_range_param_strategies_comparison.png'")

    return {
        'keep': optimizer_keep,
        'extreme': optimizer_extreme,
        'random': optimizer_random
    }

def test_defaults_without_init_pop():
    """Test optimization with default values but no initial population."""
    print("\n============ TEST: Default Values Without Initial Population ============")
    optimizer = run_optimization(init_pop=None, defaults_in_init_pop=True)
    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    return optimizer

def test_defaults_with_different_ratios():
    """Test optimization with different ratios for default values incorporation."""
    print("\n============ TEST: Default Values with Different Ratios ============")

    # Create a small initial population
    init_pop = pd.DataFrame([
        {'x': 0.5, 'y': 0.5},
        {'x': 1.5, 'y': 1.5}
    ])

    # Test cases with different ratios
    ratios = [0.1, 0.3, 0.5, 0.7, 0.9]
    optimizers = {}

    for ratio in ratios:
        print(f"\n---- Defaults Ratio: {ratio} ----")

        # Create optimizer with this ratio
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=evaluate_rosenbrock,
            parameters=get_parameters(),
            pop_size=20,
            max_iterations=50,
            opt_min_or_max='max',
            init_pop=init_pop.copy(),
            defaults_in_init_pop=True,
            defaults_in_init_pop_ratio=ratio
        )

        # Run optimization
        optimizer.run_optimization()

        # Store the result
        optimizers[f"Ratio {ratio}"] = optimizer
        print(f"Final result (Ratio {ratio}): {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")

    # Compare convergence
    plt.figure(figsize=(12, 6))

    for name, opt in optimizers.items():
        # Extract best metrics history
        history = opt.history
        bests_df = history['bests']
        iterations = bests_df['iter'].unique()
        metrics = [-opt.all_bests_metrics[i-1][0] for i in iterations]  # Convert back to original function value

        plt.plot(iterations, metrics, label=f"Default {name}", linewidth=2)

    plt.xlabel('Iteration')
    plt.ylabel('Rosenbrock Function Value (lower is better)')
    plt.title('Convergence Comparison with Different Default Value Ratios')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('default_ratios_comparison.png')

    print("\nComparison of default ratios saved to 'default_ratios_comparison.png'")

    return optimizers

def test_invalid_defaults_ratio():
    """Test optimization with invalid ratio values that should be corrected to 0.2."""
    print("\n============ TEST: Invalid Default Ratio Values ============")

    # Create a small initial population
    init_pop = pd.DataFrame([
        {'x': 0.5, 'y': 0.5},
        {'x': 1.5, 'y': 1.5}
    ])

    # Test cases with different invalid ratios
    test_cases = {
        "Negative Ratio": -0.5,
        "Zero Ratio": 0.0,
        "Ratio = 1": 1.0,
        "Ratio > 1": 1.5
    }

    optimizers = {}

    for name, ratio in test_cases.items():
        print(f"\n---- {name}: {ratio} (should be corrected to 0.2) ----")

        # Create optimizer with this invalid ratio
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=evaluate_rosenbrock,
            parameters=get_parameters(),
            pop_size=20,
            max_iterations=50,
            opt_min_or_max='max',
            init_pop=init_pop.copy(),
            defaults_in_init_pop=True,
            defaults_in_init_pop_ratio=ratio
        )

        # Run optimization
        optimizer.run_optimization()

        # Store the result
        optimizers[name] = optimizer
        print(f"Final result ({name}): {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")

    return optimizers

def test_defaults_with_full_init_pop():
    """Test case where defaults_in_init_pop is true but initial population fills entire population."""
    print("\n============ TEST: Defaults with Full Initial Population ============")

    # Create an initial population that will fill the entire population size
    np.random.seed(42)
    full_init_pop = pd.DataFrame({
        'x': np.random.uniform(-2, 2, 30),
        'y': np.random.uniform(-1, 3, 30)
    })

    # Add a point close to optimum to help convergence
    full_init_pop.iloc[0] = [1.1, 0.9]

    optimizer = run_optimization(
        init_pop=full_init_pop,
        defaults_in_init_pop=True,
        defaults_in_init_pop_ratio=0.3,
        pop_size=30
    )

    print(f"Final result: {optimizer.best_metric:.6f} at {dict(optimizer.best_parameters)}")
    print("Note: Since init_pop filled the entire population, defaults should not be incorporated")

    return optimizer

def compare_convergence(optimizers_dict):
    """
    Compare convergence of different optimization runs.

    Args:
        optimizers_dict: Dictionary of {test_name: optimizer_instance}
    """
    plt.figure(figsize=(12, 6))

    for name, optimizer in optimizers_dict.items():
        # Extract best metrics history
        history = optimizer.history
        bests_df = history['bests']
        iterations = bests_df['iter'].unique()
        metrics = [-optimizer.all_bests_metrics[i-1][0] for i in iterations]  # Convert back to original function value

        plt.plot(iterations, metrics, label=name)

    plt.xlabel('Iteration')
    plt.ylabel('Rosenbrock Function Value (lower is better)')
    # plt.yscale('log')
    plt.title('Convergence Comparison with Different Initial Population Strategies')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('init_pop_convergence_comparison.png')
    plt.show()

def visualize_rosenbrock(best_params=None):
    """Visualize the Rosenbrock function and optimization result."""
    import matplotlib.cm as cm

    x = np.linspace(-2, 2, 100)
    y = np.linspace(-1, 3, 100)
    X, Y = np.meshgrid(x, y)
    Z = rosenbrock(X, Y)

    # Create 3D surface plot
    fig = plt.figure(figsize=(12, 10))
    ax1 = fig.add_subplot(221, projection='3d')
    ax1.plot_surface(X, Y, Z, cmap=cm.coolwarm, linewidth=0, antialiased=True, alpha=0.7)
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
    ax3.contourf(X_zoom, Y_zoom, Z_zoom, 50, cmap=cm.coolwarm)
    ax3.set_xlabel('X')
    ax3.set_ylabel('Y')
    ax3.set_title('Zoomed View Around Minimum (1,1)')

    # If we have optimization result and it's in the zoomed region, plot it
    if best_params is not None and 0.5 <= x_best <= 1.5 and 0.5 <= y_best <= 1.5:
        ax3.scatter([x_best], [y_best], color='black', s=100, marker='x')

    # Create log contour plot to see valley structure
    ax4 = fig.add_subplot(224)
    ax4.contourf(X, Y, np.log(Z + 1), 50, cmap=cm.coolwarm)
    ax4.set_xlabel('X')
    ax4.set_ylabel('Y')
    ax4.set_title('Log Scale Contour Plot')

    # If we have optimization result, plot it
    if best_params is not None:
        ax4.scatter([x_best], [y_best], color='black', s=100, marker='x')

    plt.tight_layout()
    plt.savefig('rosenbrock_visualization.png')
    plt.show()

if __name__ == "__main__":
    # Run all tests and collect optimizers
    optimizers = {}

    # Basic tests
    optimizers['No Init Pop'] = test_no_init_pop()
    optimizers['DataFrame'] = test_dataframe_init_pop()
    optimizers['CSV File'] = test_csv_init_pop()
    optimizers['JSON File'] = test_json_init_pop()
    optimizers['List of Dicts'] = test_list_dict_init_pop()

    # Edge cases
    optimizers['Missing Params'] = test_missing_params_init_pop()
    optimizers['Extra Params'] = test_extra_params_init_pop()
    optimizers['Large Pop'] = test_large_init_pop()
    optimizers['Duplicates'] = test_duplicate_rows_init_pop()
    optimizers['With Defaults'] = test_defaults_in_init_pop()
    optimizers['Optimal Value'] = test_init_pop_with_optimal_value()

    # Default value incorporation tests
    optimizers['Defaults Only'] = test_defaults_without_init_pop()
    optimizers['Defaults + Full Init'] = test_defaults_with_full_init_pop()

    # Test with invalid ratios
    invalid_ratio_results = test_invalid_defaults_ratio()
    for name, opt in invalid_ratio_results.items():
        optimizers[f'Invalid Ratio: {name}'] = opt

    # Test with different ratios
    ratio_results = test_defaults_with_different_ratios()
    for name, opt in ratio_results.items():
        optimizers[f'Default {name}'] = opt

    # Out-of-range tests
    out_of_range_results = test_out_of_range_params()
    optimizers['Out-of-Range: Keep'] = out_of_range_results['keep']
    optimizers['Out-of-Range: Extreme'] = out_of_range_results['extreme']
    optimizers['Out-of-Range: Random'] = out_of_range_results['random']

    # Compare convergence
    compare_convergence(optimizers)

    # Visualize the best result
    best_optimizer_name = None
    best_metric = float('-inf')

    for name, opt in optimizers.items():
        if opt.best_metric > best_metric:
            best_metric = opt.best_metric
            best_optimizer_name = name

    if best_optimizer_name:
        print(f"\nVisualizing result from best strategy: {best_optimizer_name}")
        visualize_rosenbrock(optimizers[best_optimizer_name].best_parameters)

    # Print summary of results
    print("\n===================== SUMMARY =====================")
    print("Test Name              | Final Metric   | Distance to Optimum")
    print("-" * 60)
    for name, opt in optimizers.items():
        x = opt.best_parameters['x']
        y = opt.best_parameters['y']
        dist = np.sqrt((x - 1.0)**2 + (y - 1.0)**2)
        print(f"{name:22} | {-opt.best_metric:14.6f} | {dist:8.6f}")
