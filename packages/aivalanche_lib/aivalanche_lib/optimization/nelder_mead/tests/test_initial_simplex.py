"""
Test script for Nelder-Mead initial simplex creation features.

This script tests:
1. Using defaults_in_initial_simplex to start with default parameter values
2. Providing an initial_point to start optimization
3. Different initial_point_mode settings ('corner' vs 'centroid')
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from aivalanche_lib.optimization.nelder_mead import NelderMead
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details, generate_parameters_config


def create_test_function_wrapper(func_details):
    """Create a wrapper function for test functions."""
    func = func_details['func']
    dim = func_details['dim']
    
    def wrapper(parameters, **kwargs):
        responses = []
        
        for _, row in parameters.iterrows():
            # Extract parameter values
            x_values = []
            for i in range(dim):
                param_name = f'x{i+1}'
                if param_name in row:
                    x_values.append(row[param_name])
            
            # Evaluate function
            value = func(np.array(x_values))
            
            # Create response
            response = {
                'metric': value,
                'data': {f'x{i+1}': x_values[i] for i in range(len(x_values))}
            }
            responses.append(response)
        
        return responses
    
    return wrapper


def test_defaults_in_initial_simplex():
    """Test using default values in initial simplex."""
    print("\n=== Testing defaults_in_initial_simplex ===")
    
    # Create a custom parameter configuration with specific defaults
    param_config = [
        {'name': 'x1', 'min': -5.0, 'max': 5.0, 'default': 1.5, 'mode': 'variable', 'type': 'continuous'},
        {'name': 'x2', 'min': -5.0, 'max': 5.0, 'default': 2.5, 'mode': 'variable', 'type': 'continuous'}
    ]
    parameters = Parameters(param_config)
    
    # Get Rosenbrock function for testing
    func_details = get_function_details('rosenbrock_2d')
    eval_func = create_test_function_wrapper(func_details)
    
    # Create optimizer with defaults_in_initial_simplex=True
    optimizer = NelderMead(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=50,
        defaults_in_initial_simplex=True,
        initial_simplex_edge_length=0.3
    )
    
    # Initialize and check initial simplex
    optimizer._initialize_simplex()
    print(f"\nInitial simplex shape: {optimizer.simplex.shape}")
    
    # Convert first vertex (which should be based on defaults) to denormalized values
    first_vertex_norm = optimizer.simplex[0]
    params_df = pd.DataFrame([first_vertex_norm], columns=optimizer.variable_parameters_names)
    denorm_params = optimizer.parameters.denormalize_and_descale_parameters_array(
        params_df, include_fixed=True
    )
    
    print(f"First vertex (should be near defaults):")
    print(f"  x1 = {denorm_params['x1'].iloc[0]:.4f} (default = 1.5)")
    print(f"  x2 = {denorm_params['x2'].iloc[0]:.4f} (default = 2.5)")
    
    # Check that we're reasonably close to defaults
    assert abs(denorm_params['x1'].iloc[0] - 1.5) < 0.5, "x1 should be close to default"
    assert abs(denorm_params['x2'].iloc[0] - 2.5) < 0.5, "x2 should be close to default"
    
    # Run optimization
    print("\nRunning optimization...")
    optimizer.run_optimization()
    
    print(f"Optimization completed in {optimizer.iter} iterations")
    print(f"Best metric: {optimizer.best_metric:.6f}")
    print(f"Best parameters: x1={optimizer.best_parameters['x1']:.4f}, x2={optimizer.best_parameters['x2']:.4f}")
    
    return optimizer


def test_initial_point_corner():
    """Test providing initial point with corner mode."""
    print("\n=== Testing initial_point with corner mode ===")
    
    # Get function details
    func_details = get_function_details('sphere_2d')
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    eval_func = create_test_function_wrapper(func_details)
    
    # Create initial point DataFrame
    initial_point_df = pd.DataFrame({
        'x1': [0.8],
        'x2': [-0.6]
    })
    
    # Create optimizer with initial point
    optimizer = NelderMead(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=50,
        initial_point=initial_point_df,
        initial_point_mode='corner',
        initial_simplex_edge_length=0.2
    )
    
    # Initialize and check initial simplex
    optimizer._initialize_simplex()
    print(f"\nInitial simplex shape: {optimizer.simplex.shape}")
    
    # Convert first vertex to denormalized values
    first_vertex_norm = optimizer.simplex[0]
    params_df = pd.DataFrame([first_vertex_norm], columns=optimizer.variable_parameters_names)
    denorm_params = optimizer.parameters.denormalize_and_descale_parameters_array(
        params_df, include_fixed=True
    )
    
    print(f"First vertex (should match initial point):")
    print(f"  x1 = {denorm_params['x1'].iloc[0]:.4f} (initial = 0.8)")
    print(f"  x2 = {denorm_params['x2'].iloc[0]:.4f} (initial = -0.6)")
    
    # Check that first vertex matches initial point
    assert abs(denorm_params['x1'].iloc[0] - 0.8) < 0.01, "x1 should match initial point"
    assert abs(denorm_params['x2'].iloc[0] - (-0.6)) < 0.01, "x2 should match initial point"
    
    # Run optimization
    print("\nRunning optimization...")
    optimizer.run_optimization()
    
    print(f"Optimization completed in {optimizer.iter} iterations")
    print(f"Best metric: {optimizer.best_metric:.6f}")
    print(f"Best parameters: x1={optimizer.best_parameters['x1']:.4f}, x2={optimizer.best_parameters['x2']:.4f}")
    
    return optimizer


def test_initial_point_centroid():
    """Test providing initial point with centroid mode."""
    print("\n=== Testing initial_point with centroid mode ===")
    
    # Get function details
    func_details = get_function_details('himmelblau_2d')
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    eval_func = create_test_function_wrapper(func_details)
    
    # Create initial point as CSV file
    initial_point_file = 'test_initial_point.csv'
    initial_data = pd.DataFrame({
        'name': ['x1', 'x2'],
        'value': [2.0, 1.5]
    })
    initial_data.to_csv(initial_point_file, index=False)
    
    # Create optimizer with initial point file
    optimizer = NelderMead(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=50,
        initial_point=initial_point_file,
        initial_point_mode='centroid',
        initial_simplex_edge_length=0.3
    )
    
    # Initialize and check initial simplex
    optimizer._initialize_simplex()
    print(f"\nInitial simplex shape: {optimizer.simplex.shape}")
    
    # Calculate centroid of initial simplex
    simplex_denorm = []
    for i in range(optimizer.simplex_size):
        vertex_norm = optimizer.simplex[i]
        params_df = pd.DataFrame([vertex_norm], columns=optimizer.variable_parameters_names)
        denorm_params = optimizer.parameters.denormalize_and_descale_parameters_array(
            params_df, include_fixed=True
        )
        simplex_denorm.append([denorm_params['x1'].iloc[0], denorm_params['x2'].iloc[0]])
    
    simplex_denorm = np.array(simplex_denorm)
    centroid = np.mean(simplex_denorm, axis=0)
    
    print(f"Centroid of initial simplex:")
    print(f"  x1 = {centroid[0]:.4f} (initial = 2.0)")
    print(f"  x2 = {centroid[1]:.4f} (initial = 1.5)")
    
    # Check that centroid is close to initial point
    assert abs(centroid[0] - 2.0) < 0.1, "Centroid x1 should be close to initial point"
    assert abs(centroid[1] - 1.5) < 0.1, "Centroid x2 should be close to initial point"
    
    # Run optimization
    print("\nRunning optimization...")
    optimizer.run_optimization()
    
    print(f"Optimization completed in {optimizer.iter} iterations")
    print(f"Best metric: {optimizer.best_metric:.6f}")
    print(f"Best parameters: x1={optimizer.best_parameters['x1']:.4f}, x2={optimizer.best_parameters['x2']:.4f}")
    
    # Clean up
    os.remove(initial_point_file)
    
    return optimizer


def visualize_initial_simplexes():
    """Create visualization comparing different initialization methods."""
    print("\n=== Visualizing initial simplex creation methods ===")
    
    # Common setup
    func_details = get_function_details('rosenbrock_2d')
    param_config = generate_parameters_config(func_details)
    eval_func = create_test_function_wrapper(func_details)
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Test 1: Default initialization (center of space)
    parameters1 = Parameters(param_config)
    opt1 = NelderMead(
        seed=42,
        eval_func=eval_func,
        parameters=parameters1,
        defaults_in_initial_simplex=False,
        initial_simplex_edge_length=0.3
    )
    opt1._initialize_simplex()
    
    # Test 2: With defaults
    param_config_defaults = [
        {'name': 'x1', 'min': -2.0, 'max': 2.0, 'default': 0.5, 'mode': 'variable', 'type': 'continuous'},
        {'name': 'x2', 'min': -1.0, 'max': 3.0, 'default': 1.5, 'mode': 'variable', 'type': 'continuous'}
    ]
    parameters2 = Parameters(param_config_defaults)
    opt2 = NelderMead(
        seed=42,
        eval_func=eval_func,
        parameters=parameters2,
        defaults_in_initial_simplex=True,
        initial_simplex_edge_length=0.3
    )
    opt2._initialize_simplex()
    
    # Test 3: With initial point (corner mode)
    parameters3 = Parameters(param_config)
    initial_point_df = pd.DataFrame({'x1': [-0.5], 'x2': [0.5]})
    opt3 = NelderMead(
        seed=42,
        eval_func=eval_func,
        parameters=parameters3,
        initial_point=initial_point_df,
        initial_point_mode='corner',
        initial_simplex_edge_length=0.3
    )
    opt3._initialize_simplex()
    
    # Plot each simplex
    for idx, (opt, ax, title) in enumerate([(opt1, axes[0], 'Default (center)'),
                                           (opt2, axes[1], 'With defaults'),
                                           (opt3, axes[2], 'With initial point')]):
        # Convert to denormalized coordinates for plotting
        simplex_denorm = []
        for i in range(opt.simplex_size):
            vertex_norm = opt.simplex[i]
            params_df = pd.DataFrame([vertex_norm], columns=opt.variable_parameters_names)
            denorm_params = opt.parameters.denormalize_and_descale_parameters_array(
                params_df, include_fixed=True
            )
            simplex_denorm.append([denorm_params['x1'].iloc[0], denorm_params['x2'].iloc[0]])
        
        simplex_denorm = np.array(simplex_denorm)
        
        # Plot simplex
        # Close the triangle by adding first point at the end
        simplex_closed = np.vstack([simplex_denorm, simplex_denorm[0]])
        ax.plot(simplex_closed[:, 0], simplex_closed[:, 1], 'b-', linewidth=2)
        ax.scatter(simplex_denorm[:, 0], simplex_denorm[:, 1], c='red', s=100, zorder=5)
        
        # Mark special points
        if idx == 1:  # defaults case
            ax.scatter(0.5, 1.5, c='green', s=200, marker='*', label='Default values')
        elif idx == 2:  # initial point case
            ax.scatter(-0.5, 0.5, c='green', s=200, marker='*', label='Initial point')
        
        # Mark centroid
        centroid = np.mean(simplex_denorm, axis=0)
        ax.scatter(centroid[0], centroid[1], c='orange', s=150, marker='x', label='Centroid')
        
        ax.set_xlabel('x1')
        ax.set_ylabel('x2')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig('nelder_mead_initial_simplex_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("Visualization saved as 'nelder_mead_initial_simplex_comparison.png'")


if __name__ == "__main__":
    # Run all tests
    print("Testing Nelder-Mead initial simplex features...")
    
    # Test 1: Using defaults in initial simplex
    opt1 = test_defaults_in_initial_simplex()
    
    # Test 2: Initial point with corner mode
    opt2 = test_initial_point_corner()
    
    # Test 3: Initial point with centroid mode
    opt3 = test_initial_point_centroid()
    
    # Create visualization
    visualize_initial_simplexes()
    
    print("\n[SUCCESS] All tests passed!")
    print("\nSummary:")
    print("- defaults_in_initial_simplex: Uses parameter default values to initialize simplex")
    print("- initial_point: Can provide starting point as DataFrame or CSV file")
    print("- initial_point_mode: 'corner' places initial point as first vertex, 'centroid' centers simplex around it")
    print("\nNote: Nelder-Mead does not support providing a full initial population (simplex),")
    print("only an initial point which is used to generate the simplex.")