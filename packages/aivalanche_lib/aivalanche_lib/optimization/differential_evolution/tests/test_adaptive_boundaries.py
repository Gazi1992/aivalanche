"""
Test script for Differential Evolution adaptive boundaries feature.

This script specifically tests the adaptive boundaries functionality of the
DifferentialEvolution optimizer with various scenarios and configurations.
The adaptive boundaries feature dynamically adjusts the search space during
optimization based on population distribution.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.optimization.differential_evolution.visualizations import _plot_population_animation
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import (
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


def create_constrained_parameters(func_details, boundary_scale=0.3, position='upper'):
    """
    Create Parameters object with artificially constrained boundaries.
    This tests the adaptive boundaries feature by starting with a small search space
    positioned away from the typical optimum location.
    
    Args:
        func_details: Function details dictionary
        boundary_scale: Factor to scale down the original boundaries (default 0.3 = 30% of range)
        position: Where to place the constrained region: 'upper', 'lower', or 'random'
        
    Returns:
        Parameters object with constrained boundaries
    """
    bounds = func_details['bounds']
    dim = func_details['dim']
    
    param_config = []
    
    for i in range(dim):
        param_name = f'x{i+1}'
        original_min, original_max = bounds[i]
        original_range = original_max - original_min
        
        # Calculate constrained range size
        constrained_range = original_range * boundary_scale
        
        # Position the constrained region away from center/optimum
        if position == 'upper':
            # Place in upper portion of original range
            constrained_max = original_max
            constrained_min = original_max - constrained_range
        elif position == 'lower':
            # Place in lower portion of original range
            constrained_min = original_min
            constrained_max = original_min + constrained_range
        elif position == 'random':
            # Random offset from one end
            import random
            if random.random() < 0.5:
                constrained_min = original_min
                constrained_max = original_min + constrained_range
            else:
                constrained_max = original_max
                constrained_min = original_max - constrained_range
        else:
            raise ValueError(f"Invalid position: {position}")
        
        # Default to middle of constrained range
        default_val = (constrained_min + constrained_max) / 2
        
        param_config.append({
            'name': param_name,
            'min': constrained_min,
            'max': constrained_max,
            'default': default_val,
            'scale': 'lin',
            'mode': 'variable'
        })
    
    # Create and properly initialize Parameters object
    parameters = Parameters(param_config)
    
    return parameters


def test_adaptive_boundaries_basic(func_name='rosenbrock_2d', max_iterations=100):
    """
    Basic test of adaptive boundaries functionality.
    
    Args:
        func_name: Name of the test function
        max_iterations: Maximum iterations for optimization
        
    Returns:
        Tuple of (optimizer_with_adaptive, optimizer_without_adaptive)
    """
    print(f"\n{'='*60}")
    print(f"Testing Adaptive Boundaries - Basic Test with {func_name}")
    print(f"{'='*60}")
    
    # Get function details
    func_details = get_function_details(func_name)
    
    # Create constrained parameters - use only 10% of range at upper end
    parameters_constrained = create_constrained_parameters(func_details, boundary_scale=0.1, position='upper')
    
    # Create wrapper function
    eval_func = create_test_function_wrapper(func_details)
    
    # Common optimizer settings
    common_settings = {
        'seed': 42,
        'eval_func': eval_func,
        'parameters': parameters_constrained,
        'opt_min_or_max': 'min',
        'pop_size': 30,
        'max_iterations': max_iterations,
        'metric_threshold': 1e-8,
        'max_iter_without_improvement': 50,
        'improvement_threshold': 0.001,
    }
    
    # Test WITH adaptive boundaries
    print("\n--- Running optimization WITH adaptive boundaries ---")
    optimizer_adaptive = DifferentialEvolution(
        adaptive_boundaries=True,
        adaptive_boundaries_edge_threshold=0.02,  # Very small threshold for aggressive adaptation
        adaptive_boundaries_pop_quantile=0.9,    # High quantile for sensitivity
        adaptive_boundaries_extension=0.3,       # 30% extension each time
        adaptive_boundaries_check_period=5,      # Check every 5 iterations
        **common_settings
    )
    
    optimizer_adaptive.run_optimization()
    
    # Test WITHOUT adaptive boundaries (for comparison)
    print("\n--- Running optimization WITHOUT adaptive boundaries ---")
    optimizer_fixed = DifferentialEvolution(
        adaptive_boundaries=False,
        **common_settings
    )
    
    optimizer_fixed.run_optimization()
    
    # Print comparison
    print(f"\n{'='*60}")
    print("RESULTS COMPARISON")
    print(f"{'='*60}")
    print(f"WITH Adaptive Boundaries:")
    print(f"  Best metric: {optimizer_adaptive.best_metric:.6e}")
    print(f"  Iterations: {optimizer_adaptive.iter}")
    print(f"  Evaluations: {optimizer_adaptive.nr_evaluations}")
    print(f"  Stop reason: {optimizer_adaptive.stop_reason}")
    
    print(f"\nWITHOUT Adaptive Boundaries:")
    print(f"  Best metric: {optimizer_fixed.best_metric:.6e}")
    print(f"  Iterations: {optimizer_fixed.iter}")
    print(f"  Evaluations: {optimizer_fixed.nr_evaluations}")
    print(f"  Stop reason: {optimizer_fixed.stop_reason}")
    
    # Check if adaptive boundaries improved results
    improvement_ratio = optimizer_fixed.best_metric / optimizer_adaptive.best_metric
    print(f"\nImprovement ratio: {improvement_ratio:.2f}x")
    
    return optimizer_adaptive, optimizer_fixed


def test_adaptive_boundaries_detailed(func_name='sphere_2d', max_iterations=80):
    """
    Detailed test with visualization and boundary tracking.
    
    Args:
        func_name: Name of the test function
        max_iterations: Maximum iterations for optimization
        
    Returns:
        DifferentialEvolution optimizer instance
    """
    print(f"\n{'='*60}")
    print(f"Testing Adaptive Boundaries - Detailed Test with {func_name}")
    print(f"{'='*60}")
    
    # Get function details
    func_details = get_function_details(func_name)
    
    # Create very constrained parameters - use only 5% of range at lower end (away from optimum at 0,0)
    parameters_constrained = create_constrained_parameters(func_details, boundary_scale=0.05, position='lower')
    
    # Create wrapper function
    eval_func = create_test_function_wrapper(func_details)
    
    # Set up results directory
    results_dir = os.path.join(os.path.dirname(__file__), f'test_adaptive_boundaries_{func_name}')
    os.makedirs(results_dir, exist_ok=True)
    
    # Create optimizer with adaptive boundaries
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=parameters_constrained,
        opt_min_or_max='min',
        pop_size=25,
        max_iterations=max_iterations,
        metric_threshold=1e-8,
        max_iter_without_improvement=40,
        improvement_threshold=0.001,
        adaptive_boundaries=True,
        adaptive_boundaries_edge_threshold=0.02,  # Very aggressive threshold
        adaptive_boundaries_pop_quantile=0.85,
        adaptive_boundaries_extension=0.25,
        adaptive_boundaries_check_period=5,
        perturbation_mode='off',
        results_dir=results_dir
    )
    
    # Store initial boundaries
    initial_boundaries = {
        'min': optimizer.boundaries_min.copy(),
        'max': optimizer.boundaries_max.copy(),
        'range': optimizer.boundaries_range.copy()
    }
    
    print(f"Initial parameter boundaries:")
    for i, param_name in enumerate(optimizer.variable_parameters_names):
        print(f"  {param_name}: [{initial_boundaries['min'][i]:.4f}, {initial_boundaries['max'][i]:.4f}]")
    
    # Run optimization
    optimizer.run_optimization()
    
    # Print final boundaries
    print(f"\nFinal parameter boundaries:")
    for i, param_name in enumerate(optimizer.variable_parameters_names):
        print(f"  {param_name}: [{optimizer.boundaries_min[i]:.4f}, {optimizer.boundaries_max[i]:.4f}]")
        expansion_min = optimizer.boundaries_min[i] - initial_boundaries['min'][i]
        expansion_max = optimizer.boundaries_max[i] - initial_boundaries['max'][i]
        print(f"    Expansion: min {expansion_min:+.4f}, max {expansion_max:+.4f}")
    
    # Print results
    print(f"\nOptimization Results:")
    print(f"  Best metric: {optimizer.best_metric:.6e}")
    print(f"  Best parameters: {optimizer.best_parameters}")
    print(f"  Iterations: {optimizer.iter}")
    print(f"  Evaluations: {optimizer.nr_evaluations}")
    print(f"  Stop reason: {optimizer.stop_reason}")
    
    # Check against known optimum
    optimum_val = func_details['optimum_val']
    print(f"\nKnown optimum value: {optimum_val}")
    print(f"Distance from optimum: {abs(optimizer.best_metric - optimum_val):.6e}")
    
    # Save results and create visualizations
    print(f"\nSaving results to: {results_dir}")
    
    # Save optimization info
    optimizer.write_optimization_info_to_file(
        os.path.join(results_dir, 'optimization_info.json')
    )
    
    # Save history files
    for history_type in ['bests', 'trials', 'survivors']:
        optimizer.write_history_to_file(
            which=history_type,
            file_path=os.path.join(results_dir, f'history_{history_type}.csv')
        )
    
    # Create visualizations
    print("Creating visualizations...")
    
    # Plot metrics evolution
    fig1, ax1 = optimizer.plot_metrics(
        which='bests',
        figsize=(10, 6),
        y_scale='log',
        save_path=os.path.join(results_dir, 'metrics_evolution.png')
    )
    plt.close(fig1)
    
    # Plot boundaries evolution
    if hasattr(optimizer, 'all_boundaries') and len(optimizer.all_boundaries) > 0:
        # Check if boundaries actually changed (more than one iteration recorded)
        unique_iters = optimizer.all_boundaries.index.get_level_values('iter').unique()
        if len(unique_iters) > 1:
            fig2, axes2 = optimizer.plot_boundaries(
                normed=False,
                save_path=os.path.join(results_dir, 'boundaries_evolution.png')
            )
            plt.close(fig2)
            print("- Boundaries evolution plot saved")
            print(f"  Boundary changes recorded at iterations: {list(unique_iters)}")
        else:
            print("- No boundary changes recorded (boundaries remained constant)")
    else:
        print("- No boundaries data available")
    
    # Plot parameter evolution
    fig3, axes3 = optimizer.plot_all_parameters_evolution(
        which='survivors',
        save_path=os.path.join(results_dir, 'parameters_distribution.png')
    )
    plt.close(fig3)
    
    # Create animation if 2D
    if func_details['dim'] == 2:
        try:
            save_path = os.path.join(results_dir, 'adaptive_boundaries_animation.gif')
            fig, anim = _plot_population_animation(
                optimizer,
                param_names=None,
                figsize=(12, 10),
                interval=150,
                fps=8,
                save_path=save_path,
                func_details=func_details
            )
            plt.close(fig)
            print("- Animation saved")
        except Exception as e:
            print(f"Warning: Could not create animation: {e}")
    
    print("- All visualizations saved")
    
    return optimizer


def test_adaptive_boundaries_configurations():
    """
    Test different adaptive boundaries configurations.
    """
    print(f"\n{'='*60}")
    print("Testing Different Adaptive Boundaries Configurations")
    print(f"{'='*60}")
    
    func_name = 'sphere_2d'
    func_details = get_function_details(func_name)
    parameters_constrained = create_constrained_parameters(func_details, boundary_scale=0.1, position='upper')
    eval_func = create_test_function_wrapper(func_details)
    
    # Different configurations to test
    configs = [
        {
            'name': 'Conservative',
            'adaptive_boundaries_edge_threshold': 0.02,
            'adaptive_boundaries_pop_quantile': 0.9,
            'adaptive_boundaries_extension': 0.05,
            'adaptive_boundaries_check_period': 15
        },
        {
            'name': 'Moderate',
            'adaptive_boundaries_edge_threshold': 0.05,
            'adaptive_boundaries_pop_quantile': 0.75,
            'adaptive_boundaries_extension': 0.1,
            'adaptive_boundaries_check_period': 10
        },
        {
            'name': 'Aggressive',
            'adaptive_boundaries_edge_threshold': 0.1,
            'adaptive_boundaries_pop_quantile': 0.6,
            'adaptive_boundaries_extension': 0.2,
            'adaptive_boundaries_check_period': 5
        }
    ]
    
    results = {}
    
    for config in configs:
        print(f"\n--- Testing {config['name']} Configuration ---")
        
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters_constrained,
            opt_min_or_max='min',
            pop_size=25,
            max_iterations=50,
            adaptive_boundaries=True,
            perturbation_mode='off',
            **{k: v for k, v in config.items() if k != 'name'}
        )
        
        optimizer.run_optimization()
        
        results[config['name']] = {
            'best_metric': optimizer.best_metric,
            'iterations': optimizer.iter,
            'evaluations': optimizer.nr_evaluations,
            'boundary_changes': len(optimizer.all_boundaries.index.get_level_values('iter').unique()) - 1 if hasattr(optimizer, 'all_boundaries') else 0
        }
        
        print(f"  Best metric: {optimizer.best_metric:.6e}")
        print(f"  Iterations: {optimizer.iter}")
        print(f"  Boundary adaptations: {results[config['name']]['boundary_changes']}")
    
    # Print comparison
    print(f"\n{'='*40}")
    print("CONFIGURATION COMPARISON")
    print(f"{'='*40}")
    for name, result in results.items():
        print(f"{name:12}: metric={result['best_metric']:.2e}, "
              f"iters={result['iterations']:2d}, "
              f"adaptations={result['boundary_changes']:2d}")
    
    return results


def test_adaptive_boundaries_edge_cases():
    """
    Test edge cases for adaptive boundaries.
    """
    print(f"\n{'='*60}")
    print("Testing Adaptive Boundaries Edge Cases")
    print(f"{'='*60}")
    
    # Test 1: Very small initial boundaries
    print("\n--- Test 1: Very small initial boundaries ---")
    func_details = get_function_details('sphere_2d')
    
    # Create extremely constrained parameters
    very_constrained_config = [
        {
            'name': 'x1',
            'min': -0.1,
            'max': 0.1,
            'default': 0.0,
            'scale': 'lin',
            'mode': 'variable'
        },
        {
            'name': 'x2',
            'min': -0.1,
            'max': 0.1,
            'default': 0.0,
            'scale': 'lin',
            'mode': 'variable'
        }
    ]
    parameters_tiny = Parameters(very_constrained_config)
    eval_func = create_test_function_wrapper(func_details)
    
    optimizer_tiny = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=parameters_tiny,
        opt_min_or_max='min',
        pop_size=20,
        max_iterations=40,
        adaptive_boundaries=True,
        adaptive_boundaries_edge_threshold=0.05,
        adaptive_boundaries_extension=0.5,  # Large extension
        adaptive_boundaries_check_period=5,
        perturbation_mode='off'
    )
    
    optimizer_tiny.run_optimization()
    
    print(f"  Initial range: x1=[-0.1, 0.1], x2=[-0.1, 0.1]")
    print(f"  Final range: x1=[{optimizer_tiny.boundaries_min[0]:.3f}, {optimizer_tiny.boundaries_max[0]:.3f}], "
          f"x2=[{optimizer_tiny.boundaries_min[1]:.3f}, {optimizer_tiny.boundaries_max[1]:.3f}]")
    print(f"  Best metric: {optimizer_tiny.best_metric:.6e}")
    
    # Test 2: High-dimensional function
    print("\n--- Test 2: High-dimensional function ---")
    func_details_nd = get_function_details('sphere_nd', n_dim=5)
    parameters_5d = create_constrained_parameters(func_details_nd, boundary_scale=0.15, position='upper')
    eval_func_5d = create_test_function_wrapper(func_details_nd)
    
    optimizer_5d = DifferentialEvolution(
        seed=42,
        eval_func=eval_func_5d,
        parameters=parameters_5d,
        opt_min_or_max='min',
        pop_size=30,
        max_iterations=30,
        adaptive_boundaries=True,
        adaptive_boundaries_check_period=8,
        perturbation_mode='off'
    )
    
    optimizer_5d.run_optimization()
    
    print(f"  5D optimization with adaptive boundaries")
    print(f"  Best metric: {optimizer_5d.best_metric:.6e}")
    print(f"  Boundary adaptations: {len(optimizer_5d.all_boundaries.index.get_level_values('iter').unique()) - 1 if hasattr(optimizer_5d, 'all_boundaries') else 0}")
    
    return optimizer_tiny, optimizer_5d


if __name__ == "__main__":
    print("Testing Differential Evolution Adaptive Boundaries Feature")
    print("=" * 70)
    
    # Run tests
    try:
        # Basic comparison test
        opt_adaptive, opt_fixed = test_adaptive_boundaries_basic('rosenbrock_2d', max_iterations=60)
        
        # Detailed test with visualizations
        opt_detailed = test_adaptive_boundaries_detailed('sphere_2d', max_iterations=60)
        
        # Configuration comparison
        config_results = test_adaptive_boundaries_configurations()
        
        # Edge cases
        opt_tiny, opt_5d = test_adaptive_boundaries_edge_cases()
        
        print(f"\n{'='*70}")
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print(f"{'='*70}")
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        import traceback
        traceback.print_exc()