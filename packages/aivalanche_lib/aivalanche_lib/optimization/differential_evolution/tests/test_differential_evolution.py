"""
Test script for DifferentialEvolution optimizer.

This script tests the DifferentialEvolution optimizer with various test functions
from the aivalanche_lib.test_functions module, following the same structure as
the NelderMead tests.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Any

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.optimization.differential_evolution.visualizations import _plot_population_animation
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import (
    ALL_FUNCTIONS, 
    get_function_details, 
    generate_parameters_config,
    plot_test_function
)


def create_test_function_wrapper(func_details):
    """
    Creates a wrapper function that adapts test functions to the format expected by the optimizer.
    
    Args:
        func_details: Dictionary containing function details from get_function_details
        
    Returns:
        A function that accepts parameters DataFrame and returns list of response dicts
    """
    func = func_details['func']
    dim = func_details['dim']
    
    def wrapper(parameters, **kwargs):
        responses = []
        
        for _, row in parameters.iterrows():
            # Extract parameter values in order (x1, x2, ..., xn)
            x_values = []
            for i in range(dim):
                param_name = f'x{i+1}'
                if param_name in row:
                    x_values.append(row[param_name])
            
            # Convert to numpy array
            x = np.array(x_values)
            
            # Evaluate function
            value = func(x)
            
            # Create response dict
            response = {
                'metric': value,
                'data': {f'x{i+1}': x_values[i] for i in range(len(x_values))}
            }
            responses.append(response)
        
        return responses
    
    return wrapper


def create_population_animation(optimizer, output_dir, param_names=None, func_details=None):
    """
    Wrapper function to create population animation using the visualizations module.
    
    Args:
        optimizer: The DifferentialEvolution optimizer instance
        output_dir: Directory to save the animation and frames
        param_names: List of two parameter names to plot. If None, uses first two parameters.
        func_details: Function details dictionary (optional, for creating heatmap)
    """
    # Prepare save path
    save_path = os.path.join(output_dir, 'population_animation.gif')
    
    # Create directory for frames
    frames_dir = os.path.join(output_dir, 'population_frames')
    os.makedirs(frames_dir, exist_ok=True)
    
    # Call the animation function from visualizations
    fig, anim = _plot_population_animation(
        optimizer,
        param_names=param_names,
        figsize=(10, 10),
        interval=100,
        fps=10,
        save_path=save_path,
        func_details=func_details
    )
    
    # Note: The function now supports heatmap background when func_details is provided
    
    if fig is not None:
        plt.close(fig)
        print("- Population animation saved")


def create_population_evolution_plot(optimizer, output_dir, param_names=None, func_details=None):
    """
    Create visualization showing the evolution of the population in 2D parameter space.
    
    Args:
        optimizer: The DifferentialEvolution optimizer instance
        output_dir: Directory to save the plots
        param_names: List of two parameter names to plot. If None, uses first two parameters.
        func_details: Function details dictionary (optional, for creating heatmap)
    """
    
    # Get parameter names and indices
    if param_names is None:
        # Use first two variable parameters
        if len(optimizer.variable_parameters_names) >= 2:
            param_names = optimizer.variable_parameters_names[:2]
        else:
            print("Warning: Less than 2 variable parameters, cannot create 2D visualization")
            return
    
    x_param = param_names[0]
    y_param = param_names[1]
    
    # Get history of survivors
    survivors_history = optimizer.all_survivors
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Create background heatmap if function details provided
    if func_details is not None and 'func' in func_details and func_details['dim'] == 2:
        # Create grid
        grid_size = 100
        x_range = func_details['bounds'][0]
        y_range = func_details['bounds'][1]
        x_grid = np.linspace(x_range[0], x_range[1], grid_size)
        y_grid = np.linspace(y_range[0], y_range[1], grid_size)
        X_grid, Y_grid = np.meshgrid(x_grid, y_grid)
        
        # Get function
        func = func_details['func']
        
        # Evaluate function on grid
        Z = np.zeros_like(X_grid)
        for i in range(grid_size):
            for j in range(grid_size):
                Z[i, j] = func(np.array([X_grid[i, j], Y_grid[i, j]]))
        
        # Apply log scale for better visualization
        Z_log = np.log10(Z + 1e-10)  # Add small value to avoid log(0)
        
        # Plot heatmap
        contour = ax.contourf(X_grid, Y_grid, Z_log, levels=50, cmap='viridis', alpha=0.7)
        ax.contour(X_grid, Y_grid, Z_log, levels=20, colors='black', alpha=0.2, linewidths=0.5)
        
        # Add colorbar
        cbar = plt.colorbar(contour, ax=ax)
        cbar.set_label('log10(Function Value)', fontsize=10)
    
    # Plot final population
    if len(survivors_history) > 0:
        final_pop = survivors_history[-1]
        ax.scatter(final_pop[x_param], final_pop[y_param], 
                  color='white', s=60, edgecolor='black', linewidth=1,
                  label='Final Population', zorder=5)
    
    # Mark best solution
    best_params = optimizer.best_parameters
    ax.scatter(best_params[x_param], best_params[y_param], 
              color='red', s=200, marker='*', edgecolor='black', linewidth=1,
              label=f'Best (metric={optimizer.best_metric:.2e})', zorder=10)
    
    # Set labels and title
    ax.set_xlabel(f'{x_param}', fontsize=12)
    ax.set_ylabel(f'{y_param}', fontsize=12)
    ax.set_title('Differential Evolution - Final Population Distribution', fontsize=14)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    # Save plot
    plot_path = os.path.join(output_dir, 'population_distribution.png')
    fig.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    print("- Population distribution plot saved")


def test_function_optimization(func_name, max_iterations=100, results_base_dir=None):
    """
    Test optimization with a specific test function.
    
    Args:
        func_name: Name of the test function from ALL_FUNCTIONS
        max_iterations: Maximum iterations for optimization
        results_base_dir: Base directory for results (if None, uses default)
    """
    print(f"\n{'='*60}")
    print(f"Testing DifferentialEvolution optimizer with {func_name} function")
    print(f"{'='*60}")
    
    # Get function details
    if func_name in ['sphere_nd', 'ackley_nd', 'rastrigin_nd', 'griewank_nd']:
        # For n-dimensional functions, use 2D for visualization
        func_details = get_function_details(func_name, n_dim=2)
    else:
        func_details = get_function_details(func_name)
    
    # Generate parameter configuration
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    
    # Create wrapper function
    eval_func = create_test_function_wrapper(func_details)
    
    # Set up results directory
    if results_base_dir is None:
        results_base_dir = os.path.dirname(__file__)
    test_results_dir = os.path.join(results_base_dir, f'test_results_{func_name}')
    os.makedirs(test_results_dir, exist_ok=True)
    
    # Create optimizer
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        pop_size=30 if func_details['dim'] <= 3 else 50,
        max_iterations=max_iterations,
        metric_threshold=1e-8,
        max_iter_without_improvement=30,
        improvement_threshold=0.001,
        adaptive_boundaries=True,
        boundary_constraint_method='clamp',
        results_dir=test_results_dir
    )
    
    # Run optimization
    optimizer.run_optimization()
    
    # Print results
    print(f"\nOptimization completed!")
    print(f"Best metric: {optimizer.best_metric:.6e}")
    print(f"Best parameters: {optimizer.best_parameters}")
    print(f"Number of iterations: {optimizer.iter}")
    print(f"Number of evaluations: {optimizer.nr_evaluations}")
    print(f"Stop reason: {optimizer.stop_reason}")
    
    # Check against known optimum
    optimum_val = func_details['optimum_val']
    print(f"\nKnown optimum value: {optimum_val}")
    print(f"Distance from optimum: {abs(optimizer.best_metric - optimum_val):.6e}")
    
    # Save results
    print("\nSaving results...")
    
    # Save best parameters
    best_params_file = optimizer.write_best_parameters_to_file(
        os.path.join(test_results_dir, 'best_parameters.csv')
    )
    print(f"- Best parameters saved")
    
    # Save optimization info
    info_file = optimizer.write_optimization_info_to_file(
        os.path.join(test_results_dir, 'optimization_info.json')
    )
    print(f"- Optimization info saved")
    
    # Save history files
    for history_type in ['bests', 'trials']:
        history_file = optimizer.write_history_to_file(
            which=history_type,
            file_path=os.path.join(test_results_dir, f'history_{history_type}.csv')
        )
        print(f"- {history_type.capitalize()} history saved")
    
    # Test visualizations
    print("\nCreating visualizations...")
    
    # Plot metrics evolution
    fig1, ax1 = optimizer.plot_metrics(
        which='bests',
        figsize=(8, 6),
        y_scale='log',
        save_path=os.path.join(test_results_dir, 'metrics_evolution.png')
    )
    plt.close(fig1)
    print("- Metrics evolution plot saved")
    
    # Plot parameter evolution
    fig2, ax2 = optimizer.plot_all_parameters_evolution(
        which='survivors',
        nr_rows=2 if func_details['dim'] > 2 else 1,
        save_path=os.path.join(test_results_dir, 'parameter_evolution.png')
    )
    plt.close(fig2)
    print("- Parameter evolution plot saved")
    
    # Plot adaptive boundaries if used
    if optimizer.adaptive_boundaries:
        fig3, ax3 = optimizer.plot_boundaries(
            normed=False,
            save_path=os.path.join(test_results_dir, 'boundary_evolution.png')
        )
        plt.close(fig3)
        print("- Boundary evolution plot saved")
    
    # For 2D functions, create additional visualizations
    if func_details['dim'] == 2:
        # Create population distribution plot
        create_population_evolution_plot(optimizer, test_results_dir, func_details=func_details)
        
        # Create animation
        print("\nCreating population animation...")
        create_population_animation(optimizer, test_results_dir, func_details=func_details)
        
        # Plot the test function itself
        fig_func, axes_func = plot_test_function(func_details)
        if axes_func and len(axes_func) > 1:
            ax_contour = axes_func[1]
            best_p = optimizer.best_parameters
            ax_contour.scatter(best_p['x1'], best_p['x2'], 
                             color='black', s=120, marker='X', 
                             label='DE Best Found', zorder=6)
            ax_contour.legend()
        fig_func.savefig(os.path.join(test_results_dir, 'function_visualization.png'))
        plt.close(fig_func)
        print("- Function visualization saved")
    
    print(f"\nAll files saved to: {test_results_dir}")
    
    return optimizer


def test_multiple_functions():
    """
    Test optimization with multiple test functions.
    """
    # Select a variety of test functions
    test_functions = [
        # 2D functions for full visualization
        'rosenbrock_2d',
        'sphere_2d', 
        'himmelblau_2d',
        'beale_2d',
        
        # 1D function
        'parabola_1d',
        
        # 3D function
        'sphere_3d',
        
        # n-dimensional functions (tested in 2D)
        'ackley_nd',
        'rastrigin_nd'
    ]
    
    results = {}
    
    for func_name in test_functions:
        try:
            optimizer = test_function_optimization(func_name, max_iterations=100)
            results[func_name] = {
                'success': True,
                'best_metric': optimizer.best_metric,
                'iterations': optimizer.iter,
                'evaluations': optimizer.nr_evaluations
            }
        except Exception as e:
            print(f"Error testing {func_name}: {str(e)}")
            results[func_name] = {'success': False, 'error': str(e)}
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY OF ALL TESTS")
    print("="*60)
    
    for func_name, result in results.items():
        if result['success']:
            print(f"{func_name}: SUCCESS - metric={result['best_metric']:.6e}, "
                  f"iters={result['iterations']}, evals={result['evaluations']}")
        else:
            print(f"{func_name}: FAILED - {result['error']}")
    
    return results


def test_single_function(func_name='rosenbrock_2d'):
    """
    Test a single function with detailed output.
    """
    return test_function_optimization(func_name, max_iterations=150)


def test_with_fixed_parameter():
    """Test optimization with one fixed parameter."""
    print("\n" + "="*60)
    print("Testing DifferentialEvolution optimizer with fixed parameter")
    print("="*60)
    
    # Get function details for rosenbrock
    func_details = get_function_details('rosenbrock_2d')
    
    # Create parameters with x1 fixed at 1.0
    param_config = [
        {'name': 'x1', 'min': -2.0, 'max': 2.0, 'default': 1.0, 'mode': 'fixed', 'type': 'continuous'},
        {'name': 'x2', 'min': -1.0, 'max': 3.0, 'default': 0.0, 'mode': 'variable', 'type': 'continuous'}
    ]
    parameters = Parameters(param_config)
    
    # Create wrapper function
    eval_func = create_test_function_wrapper(func_details)
    
    # Create optimizer
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        pop_size=20,
        max_iterations=50,
        metric_threshold=1e-6
    )
    
    # Run optimization
    optimizer.run_optimization()
    
    # Check results
    print(f"\nBest metric: {optimizer.best_metric}")
    print(f"Best parameters: {optimizer.best_parameters}")
    
    # With x1 fixed at 1.0, optimal x2 should be 1.0
    assert optimizer.best_parameters['x1'] == 1.0, "x1 should remain fixed at 1.0"
    assert abs(optimizer.best_parameters['x2'] - 1.0) < 0.01, "x2 should be close to 1.0"
    
    print("\n[PASS] Fixed parameter test passed!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Run specific test based on command line argument
        if sys.argv[1] == 'single':
            # Test single function with optional function name
            func_name = sys.argv[2] if len(sys.argv) > 2 else 'rosenbrock_2d'
            test_single_function(func_name)
        elif sys.argv[1] == 'fixed':
            test_with_fixed_parameter()
        elif sys.argv[1] == 'all':
            test_multiple_functions()
        else:
            print(f"Unknown test: {sys.argv[1]}")
            print("Usage: python test_differential_evolution.py [single|fixed|all] [function_name]")
    else:
        # Default: test multiple functions
        print("Running tests for multiple functions...")
        test_multiple_functions()
        
        print("\nTesting with fixed parameter...")
        test_with_fixed_parameter()
        
        print("\n[SUCCESS] All tests completed!")