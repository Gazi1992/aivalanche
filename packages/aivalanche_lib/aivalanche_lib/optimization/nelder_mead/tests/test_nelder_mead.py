"""
Test script for NelderMead optimizer.

This script tests the NelderMead optimizer with various test functions
from the aivalanche_lib.test_functions module.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation, PillowWriter

from aivalanche_lib.optimization.nelder_mead import NelderMead
from aivalanche_lib.optimization.nelder_mead.visualizations import _plot_simplex_animation
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import (
    ALL_FUNCTIONS, 
    get_function_details, 
    generate_parameters_config
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

def create_simplex_animation(optimizer, output_dir, param_names=None, func_details=None):
    """
    Wrapper function to create simplex animation using the visualizations module.
    
    Args:
        optimizer: The NelderMead optimizer instance
        output_dir: Directory to save the animation and frames
        param_names: List of two parameter names to plot. If None, uses first two parameters.
        func_details: Function details dictionary (optional, for creating heatmap)
    """
    # Prepare save path
    save_path = os.path.join(output_dir, 'simplex_animation.gif')
    
    # Create directory for frames (even though the new function doesn't save frames)
    frames_dir = os.path.join(output_dir, 'simplex_frames')
    os.makedirs(frames_dir, exist_ok=True)
    
    # Call the animation function from visualizations
    fig, anim = _plot_simplex_animation(
        optimizer,
        param_names=param_names,
        figsize=(10, 10),
        interval=100,
        fps=10,
        save_path=save_path
    )
    
    # Note: The function in visualizations.py doesn't currently support heatmap background
    # or saving individual frames, but the basic animation functionality is preserved
    
    if fig is not None:
        plt.close(fig)
        print("- Simplex animation saved")
    else:
        print("Could not create animation")

def test_function_optimization(func_name, max_iterations=100, results_base_dir=None):
    """
    Test optimization with a specific test function.
    
    Args:
        func_name: Name of the test function from ALL_FUNCTIONS
        max_iterations: Maximum iterations for optimization
        results_base_dir: Base directory for results (if None, uses default)
    """
    print(f"\n{'='*60}")
    print(f"Testing NelderMead optimizer with {func_name} function")
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
    optimizer = NelderMead(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=max_iterations,
        metric_threshold=1e-8,
        max_iter_without_improvement=30,
        improvement_threshold=0.001,
        reflection_coefficient=(0.9, 1.1),
        expansion_coefficient=(1.5, 2.5),
        contraction_coefficient=(0.3, 0.5),
        shrink_coefficient=(0.3, 0.5),
        initial_simplex_edge_length=0.5,
        defaults_in_initial_simplex=True,
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
    for history_type in ['bests', 'trials', 'simplexes']:
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
    
    # For 2D functions, create simplex visualizations
    if func_details['dim'] == 2:
        # Plot simplex evolution
        fig2, ax2 = optimizer.plot_simplex_evolution(
            parameter_names=optimizer.variable_parameters_names[:2],
            figsize=(10, 10),
            save_path=os.path.join(test_results_dir, 'simplex_evolution.png')
        )
        plt.close(fig2)
        print("- Simplex evolution plot saved")
        
        # Create animation
        print("\nCreating simplex animation...")
        create_simplex_animation(optimizer, test_results_dir, func_details=func_details)
        print("- Simplex animation saved")
    
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
    print("Testing NelderMead optimizer with fixed parameter")
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
    optimizer = NelderMead(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
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
            print("Usage: python test_nelder_mead.py [single|fixed|all] [function_name]")
    else:
        # Default: test multiple functions
        print("Running tests for multiple functions...")
        test_multiple_functions()
        
        print("\nTesting with fixed parameter...")
        test_with_fixed_parameter()
        
        print("\n[SUCCESS] All tests completed!")