"""
Test script for Differential Evolution optimizer.

This script tests the DifferentialEvolution optimizer with various test functions
from the aivalanche_lib.test_functions module, including animations with landscape backgrounds.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib import cm
import matplotlib.colors as mcolors

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.optimization.differential_evolution.visualizations import _plot_population_animation
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


def test_function_optimization(func_name, max_iterations=100, results_base_dir=None):
    """
    Test optimization with a specific test function.
    
    Args:
        func_name: Name of the test function from ALL_FUNCTIONS
        max_iterations: Maximum iterations for optimization
        results_base_dir: Base directory for results (if None, uses default)
    """
    print(f"\n{'='*60}")
    print(f"Testing Differential Evolution with {func_name} function")
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
        pop_size=30,
        max_iterations=max_iterations,
        metric_threshold=1e-8,
        max_iter_without_improvement=30,
        improvement_threshold=0.001,
        mutation_factor_1=(0.5, 0.9),
        mutation_factor_2=(0.0, 0.3),
        recombination_factor=(0.7, 0.95),
        adaptive_boundaries=False,
        perturbation_mode='auto',
        use_local_refinement=False,  # Can be enabled for hybrid optimization
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
    
    # Check parameter accuracy
    if func_details.get('optimum_loc') is not None:
        optimum_loc = func_details['optimum_loc']
        param_distance = 0
        # Handle multiple optima (like Himmelblau)
        if isinstance(optimum_loc, list):
            min_distance = float('inf')
            for loc in optimum_loc:
                distance = 0
                for i, opt_val in enumerate(loc):
                    param_name = f'x{i+1}'
                    if param_name in optimizer.best_parameters:
                        distance += (optimizer.best_parameters[param_name] - opt_val) ** 2
                distance = np.sqrt(distance)
                min_distance = min(min_distance, distance)
            param_distance = min_distance
        else:
            for i, opt_val in enumerate(optimum_loc):
                param_name = f'x{i+1}'
                if param_name in optimizer.best_parameters:
                    param_distance += (optimizer.best_parameters[param_name] - opt_val) ** 2
            param_distance = np.sqrt(param_distance)
        print(f"Distance from optimal position: {param_distance:.6e}")
    
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
    for history_type in ['bests', 'trials', 'survivors']:
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
    
    # Plot parameter evolution (for 2D problems)
    if func_details['dim'] == 2:
        # Create animation with landscape
        print("\nCreating DE animation with landscape background...")
        try:
            save_path = os.path.join(test_results_dir, 'de_animation.gif')
            fig, anim = _plot_population_animation(
                optimizer, 
                param_names=None,  # Use first two parameters
                figsize=(10, 10),
                interval=100,
                fps=10,
                save_path=save_path,
                func_details=func_details
            )
            plt.close(fig)
            print("- DE animation saved")
        except Exception as e:
            print(f"Warning: Could not create animation: {e}")
        
        # Plot boundaries evolution if adaptive boundaries were used
        if optimizer.adaptive_boundaries:
            fig3, axes3 = optimizer.plot_boundaries(
                normed=False,
                save_path=os.path.join(test_results_dir, 'boundaries_evolution.png')
            )
            plt.close(fig3)
            print("- Boundaries evolution plot saved")
    
    # Plot all parameters evolution
    fig2, axes2 = optimizer.plot_all_parameters_evolution(
        which='survivors',
        save_path=os.path.join(test_results_dir, 'parameters_distribution.png')
    )
    plt.close(fig2)
    print("- Parameters distribution plot saved")
    
    return optimizer


def test_all_functions():
    """Test DE optimizer on all available test functions."""
    
    # Functions to test (focusing on those with known optima)
    test_functions = [
        # 1D functions
        'parabola_1d',
        
        # 2D functions (good for visualization)
        'sphere_2d',
        'rosenbrock_2d',
        'himmelblau_2d',
        'beale_2d',
        'griewank_2d',
        
        # N-dimensional functions (will use 2D version)
        'sphere_nd',
        'ackley_nd',
        'rastrigin_nd',
        'griewank_nd',
    ]
    
    results = {}
    
    for func_name in test_functions:
        try:
            print(f"\n\n{'*'*80}")
            print(f"{'*'*80}")
            optimizer = test_function_optimization(func_name, max_iterations=50)
            
            results[func_name] = {
                'success': True,
                'best_metric': optimizer.best_metric,
                'iterations': optimizer.iter,
                'evaluations': optimizer.nr_evaluations,
                'stop_reason': optimizer.stop_reason
            }
            
        except Exception as e:
            print(f"\nError testing {func_name}: {str(e)}")
            results[func_name] = {
                'success': False,
                'error': str(e)
            }
    
    # Print summary
    print("\n\n" + "="*80)
    print("SUMMARY OF ALL TESTS")
    print("="*80)
    
    for func_name, result in results.items():
        if result['success']:
            print(f"\n{func_name}: SUCCESS")
            print(f"  Best metric: {result['best_metric']:.6e}")
            print(f"  Iterations: {result['iterations']}")
            print(f"  Evaluations: {result['evaluations']}")
            print(f"  Stop reason: {result['stop_reason']}")
        else:
            print(f"\n{func_name}: FAILED")
            print(f"  Error: {result['error']}")
    
    return results


if __name__ == "__main__":
    # Test all functions
    results = test_all_functions()