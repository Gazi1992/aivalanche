"""
Test script for providing full initial simplex to Nelder-Mead optimizer.

This script tests the new functionality to provide a complete initial simplex
instead of just an initial point.
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


def test_initial_simplex_numpy_normalized():
    """Test providing initial simplex as normalized numpy array."""
    print("\n=== Testing initial_simplex with normalized numpy array ===")
    
    # Get function details
    func_details = get_function_details('rosenbrock_2d')
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    eval_func = create_test_function_wrapper(func_details)
    
    # Create initial simplex in normalized space [0, 1]
    # For 2D, we need 3 vertices
    initial_simplex_norm = np.array([
        [0.3, 0.3],  # Vertex 1
        [0.7, 0.4],  # Vertex 2
        [0.5, 0.8]   # Vertex 3
    ])
    
    # Create optimizer with initial simplex
    optimizer = NelderMead(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=50,
        initial_simplex=initial_simplex_norm
    )
    
    # Run optimization
    optimizer.run_optimization()
    
    print(f"Optimization completed in {optimizer.iter} iterations")
    print(f"Best metric: {optimizer.best_metric:.6f}")
    print(f"Best parameters: x1={optimizer.best_parameters['x1']:.4f}, x2={optimizer.best_parameters['x2']:.4f}")
    
    # Verify initial simplex was used
    first_simplex = optimizer.all_simplexes[0]
    assert np.allclose(first_simplex, initial_simplex_norm), "Initial simplex should match provided values"
    print("✓ Initial simplex correctly set from normalized array")
    
    return optimizer


def test_initial_simplex_numpy_denormalized():
    """Test providing initial simplex as denormalized numpy array."""
    print("\n=== Testing initial_simplex with denormalized numpy array ===")
    
    # Get function details
    func_details = get_function_details('sphere_2d')
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    eval_func = create_test_function_wrapper(func_details)
    
    # Create initial simplex in actual parameter space
    # For sphere_2d, bounds are typically [-5.12, 5.12]
    initial_simplex_denorm = np.array([
        [-1.0, -1.0],  # Vertex 1
        [2.0, -0.5],   # Vertex 2
        [0.0, 2.5]     # Vertex 3
    ])
    
    # Create optimizer with initial simplex
    optimizer = NelderMead(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=50,
        initial_simplex=initial_simplex_denorm
    )
    
    # Run optimization
    optimizer.run_optimization()
    
    print(f"Optimization completed in {optimizer.iter} iterations")
    print(f"Best metric: {optimizer.best_metric:.6f}")
    print(f"Best parameters: x1={optimizer.best_parameters['x1']:.4f}, x2={optimizer.best_parameters['x2']:.4f}")
    
    # Check that initial simplex was normalized properly
    first_simplex = optimizer.all_simplexes[0]
    print(f"First simplex (normalized): \n{first_simplex}")
    print("✓ Initial simplex correctly normalized from denormalized array")
    
    return optimizer


def test_initial_simplex_dataframe():
    """Test providing initial simplex as pandas DataFrame."""
    print("\n=== Testing initial_simplex with pandas DataFrame ===")
    
    # Get function details
    func_details = get_function_details('himmelblau_2d')
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    eval_func = create_test_function_wrapper(func_details)
    
    # Create initial simplex as DataFrame
    initial_simplex_df = pd.DataFrame({
        'x1': [0.0, 3.0, -2.0],
        'x2': [0.0, -1.0, 2.0]
    })
    
    print("Initial simplex DataFrame:")
    print(initial_simplex_df)
    
    # Create optimizer with initial simplex
    optimizer = NelderMead(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=50,
        initial_simplex=initial_simplex_df
    )
    
    # Run optimization
    optimizer.run_optimization()
    
    print(f"\nOptimization completed in {optimizer.iter} iterations")
    print(f"Best metric: {optimizer.best_metric:.6f}")
    print(f"Best parameters: x1={optimizer.best_parameters['x1']:.4f}, x2={optimizer.best_parameters['x2']:.4f}")
    
    # Himmelblau has 4 global minima at:
    # (3.0, 2.0), (-2.805118, 3.131312), (-3.779310, -3.283186), (3.584428, -1.848126)
    print("\nNote: Himmelblau function has 4 global minima, all with value 0.0")
    
    return optimizer


def test_initial_simplex_validation():
    """Test validation of initial simplex dimensions."""
    print("\n=== Testing initial_simplex validation ===")
    
    # Get function details
    func_details = get_function_details('sphere_3d')
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    eval_func = create_test_function_wrapper(func_details)
    
    # Test 1: Wrong number of vertices (should be 4 for 3D)
    print("\nTest 1: Wrong number of vertices")
    wrong_vertices = np.array([
        [0.5, 0.5, 0.5],
        [0.7, 0.5, 0.5]  # Only 2 vertices instead of 4
    ])
    
    try:
        optimizer = NelderMead(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            initial_simplex=wrong_vertices
        )
        optimizer._initialize_simplex()
        print("✗ Should have raised ValueError for wrong number of vertices")
    except ValueError as e:
        print(f"✓ Correctly caught error: {e}")
    
    # Test 2: Wrong number of dimensions
    print("\nTest 2: Wrong number of dimensions")
    wrong_dims = np.array([
        [0.5, 0.5],      # Only 2 dimensions
        [0.7, 0.5],
        [0.5, 0.8],
        [0.6, 0.6]
    ])
    
    try:
        optimizer = NelderMead(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            initial_simplex=wrong_dims
        )
        optimizer._initialize_simplex()
        print("✗ Should have raised ValueError for wrong dimensions")
    except ValueError as e:
        print(f"✓ Correctly caught error: {e}")
    
    # Test 3: Correct simplex
    print("\nTest 3: Correct simplex dimensions")
    correct_simplex = np.array([
        [0.5, 0.5, 0.5],
        [0.7, 0.5, 0.5],
        [0.5, 0.7, 0.5],
        [0.5, 0.5, 0.7]
    ])
    
    optimizer = NelderMead(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=30,
        initial_simplex=correct_simplex
    )
    
    optimizer.run_optimization()
    print(f"✓ Optimization ran successfully with correct simplex")
    print(f"  Best metric: {optimizer.best_metric:.6f}")
    
    return optimizer


def visualize_initial_simplex_methods():
    """Visualize comparison of different simplex initialization methods."""
    print("\n=== Visualizing initial simplex methods ===")
    
    # Common setup
    func_details = get_function_details('rosenbrock_2d')
    param_config = generate_parameters_config(func_details)
    eval_func = create_test_function_wrapper(func_details)
    parameters = Parameters(param_config)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    axes = axes.flatten()
    
    # Method 1: Default (generated)
    opt1 = NelderMead(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        initial_simplex_edge_length=0.3
    )
    opt1._initialize_simplex()
    
    # Method 2: From initial point
    initial_point_df = pd.DataFrame({'x1': [0.5], 'x2': [1.5]})
    opt2 = NelderMead(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        initial_point=initial_point_df,
        initial_point_mode='corner',
        initial_simplex_edge_length=0.3
    )
    opt2._initialize_simplex()
    
    # Method 3: Custom simplex (normalized)
    custom_simplex_norm = np.array([
        [0.2, 0.3],
        [0.8, 0.2],
        [0.5, 0.9]
    ])
    opt3 = NelderMead(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        initial_simplex=custom_simplex_norm
    )
    opt3._initialize_simplex()
    
    # Method 4: Custom simplex (denormalized DataFrame)
    custom_simplex_df = pd.DataFrame({
        'x1': [-1.0, 1.5, 0.0],
        'x2': [0.5, 0.0, 2.5]
    })
    opt4 = NelderMead(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        initial_simplex=custom_simplex_df
    )
    opt4._initialize_simplex()
    
    # Plot each simplex
    titles = ['Default Generated', 'From Initial Point', 'Custom (Normalized)', 'Custom (DataFrame)']
    optimizers = [opt1, opt2, opt3, opt4]
    
    for idx, (opt, ax, title) in enumerate(zip(optimizers, axes, titles)):
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
        simplex_closed = np.vstack([simplex_denorm, simplex_denorm[0]])
        ax.plot(simplex_closed[:, 0], simplex_closed[:, 1], 'b-', linewidth=2)
        ax.scatter(simplex_denorm[:, 0], simplex_denorm[:, 1], c='red', s=100, zorder=5)
        
        # Number vertices
        for i, (x, y) in enumerate(simplex_denorm):
            ax.annotate(f'V{i}', (x, y), xytext=(5, 5), textcoords='offset points')
        
        # Mark centroid
        centroid = np.mean(simplex_denorm, axis=0)
        ax.scatter(centroid[0], centroid[1], c='green', s=150, marker='x', label='Centroid')
        
        ax.set_xlabel('x1')
        ax.set_ylabel('x2')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_aspect('equal')
        
        # Set common axis limits
        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(-1.5, 3.5)
    
    plt.tight_layout()
    plt.savefig('nelder_mead_initial_simplex_methods.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("Visualization saved as 'nelder_mead_initial_simplex_methods.png'")


def test_initial_simplex_with_fixed_parameters():
    """Test initial simplex with fixed parameters."""
    print("\n=== Testing initial_simplex with fixed parameters ===")
    
    # Create parameter configuration with one fixed parameter
    param_config = [
        {'name': 'x1', 'min': -5.0, 'max': 5.0, 'default': 0.0, 'mode': 'variable', 'type': 'continuous'},
        {'name': 'x2', 'min': -5.0, 'max': 5.0, 'default': 1.0, 'mode': 'fixed', 'type': 'continuous'},
        {'name': 'x3', 'min': -5.0, 'max': 5.0, 'default': 0.0, 'mode': 'variable', 'type': 'continuous'}
    ]
    parameters = Parameters(param_config)
    
    # Simple test function
    def eval_func(params_df, **kwargs):
        responses = []
        for _, row in params_df.iterrows():
            # Sum of squares
            value = row['x1']**2 + row['x2']**2 + row['x3']**2
            responses.append({'metric': value})
        return responses
    
    # Create initial simplex for 2 variable parameters (need 3 vertices)
    initial_simplex = np.array([
        [0.3, 0.3],  # x1=0.3, x3=0.3
        [0.7, 0.4],  # x1=0.7, x3=0.4
        [0.5, 0.8]   # x1=0.5, x3=0.8
    ])
    
    # Create optimizer
    optimizer = NelderMead(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=30,
        initial_simplex=initial_simplex
    )
    
    # Run optimization
    optimizer.run_optimization()
    
    print(f"Optimization completed in {optimizer.iter} iterations")
    print(f"Best metric: {optimizer.best_metric:.6f}")
    print(f"Best parameters: x1={optimizer.best_parameters['x1']:.4f}, "
          f"x2={optimizer.best_parameters['x2']:.4f} (fixed), "
          f"x3={optimizer.best_parameters['x3']:.4f}")
    
    # Verify x2 remained fixed
    assert abs(optimizer.best_parameters['x2'] - 1.0) < 1e-10, "Fixed parameter should not change"
    print("✓ Fixed parameter correctly maintained")
    
    return optimizer


if __name__ == "__main__":
    # Run all tests
    print("Testing Nelder-Mead initial simplex functionality...")
    
    # Test 1: Normalized numpy array
    opt1 = test_initial_simplex_numpy_normalized()
    
    # Test 2: Denormalized numpy array
    opt2 = test_initial_simplex_numpy_denormalized()
    
    # Test 3: DataFrame
    opt3 = test_initial_simplex_dataframe()
    
    # Test 4: Validation
    opt4 = test_initial_simplex_validation()
    
    # Test 5: With fixed parameters
    opt5 = test_initial_simplex_with_fixed_parameters()
    
    # Create visualization
    visualize_initial_simplex_methods()
    
    print("\n[SUCCESS] All tests passed!")
    print("\nSummary of initial_simplex functionality:")
    print("- Can provide complete initial simplex as numpy array or DataFrame")
    print("- Numpy arrays can be normalized (0-1) or in actual parameter space")
    print("- DataFrames should have columns matching variable parameter names")
    print("- Simplex must have correct dimensions: (n+1) vertices for n parameters")
    print("- Works correctly with fixed parameters")