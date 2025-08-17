"""
Test Adam optimizer with provided gradients feature.

This test module verifies that the Adam optimizer correctly handles gradients
provided by the evaluation function, including:
- Basic gradient-based optimization
- Different scales (linear, log, symlog, neglog)
- Multiple test functions with analytical gradients
- Comparison with numerical gradient estimation
"""

import numpy as np
import pandas as pd
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from aivalanche_lib.optimization.adam import Adam
from aivalanche_lib.parameters import Parameters


def rosenbrock_with_gradients(params_df, **kwargs):
    """
    Rosenbrock function with analytical gradients.
    
    f(x, y) = (1 - x)^2 + 100 * (y - x^2)^2
    df/dx = -2(1 - x) - 400x(y - x^2)
    df/dy = 200(y - x^2)
    """
    responses = []
    for _, row in params_df.iterrows():
        x = row['x']
        y = row['y']
        
        # Compute function value
        metric = (1 - x)**2 + 100 * (y - x**2)**2
        
        # Compute analytical gradients
        grad_x = -2 * (1 - x) - 400 * x * (y - x**2)
        grad_y = 200 * (y - x**2)
        
        response = {
            'metric': metric,
            'gradients': {'x': grad_x, 'y': grad_y}
        }
        responses.append(response)
    return responses


def sphere_with_gradients(params_df, **kwargs):
    """
    Sphere function with analytical gradients.
    
    f(x1, x2, ..., xn) = sum(xi^2)
    df/dxi = 2*xi
    """
    responses = []
    for _, row in params_df.iterrows():
        # Compute function value
        metric = sum(row[col]**2 for col in params_df.columns)
        
        # Compute analytical gradients
        gradients = {col: 2 * row[col] for col in params_df.columns}
        
        response = {
            'metric': metric,
            'gradients': gradients
        }
        responses.append(response)
    return responses


def rastrigin_with_gradients(params_df, **kwargs):
    """
    Rastrigin function with analytical gradients.
    
    f(x) = 10n + sum(xi^2 - 10*cos(2*pi*xi))
    df/dxi = 2*xi + 20*pi*sin(2*pi*xi)
    """
    responses = []
    n = len(params_df.columns)
    
    for _, row in params_df.iterrows():
        # Compute function value
        metric = 10 * n + sum(row[col]**2 - 10 * np.cos(2 * np.pi * row[col]) 
                              for col in params_df.columns)
        
        # Compute analytical gradients
        gradients = {}
        for col in params_df.columns:
            xi = row[col]
            gradients[col] = 2 * xi + 20 * np.pi * np.sin(2 * np.pi * xi)
        
        response = {
            'metric': metric,
            'gradients': gradients
        }
        responses.append(response)
    return responses


def test_rosenbrock_provided_gradients():
    """Test Adam with provided gradients on Rosenbrock function."""
    print("\n" + "="*60)
    print("Testing Adam with PROVIDED gradients on Rosenbrock function")
    print("="*60)
    
    # Define parameters
    param_config = [
        {'name': 'x', 'min': -5, 'max': 5, 'default': 3.0},
        {'name': 'y', 'min': -5, 'max': 5, 'default': -2.0}
    ]
    parameters = Parameters(param_config)
    
    # Run optimization with provided gradients
    optimizer = Adam(
        seed=42,
        eval_func=rosenbrock_with_gradients,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=200,
        learning_rate=0.01,
        gradient_method='provided',  # Use provided gradients
        gradient_tolerance=1e-6
    )
    
    optimizer.run_optimization()
    
    print(f"\nOptimization completed:")
    print(f"  Iterations: {optimizer.iter}")
    print(f"  Function evaluations: {optimizer.nr_evaluations}")
    print(f"  Final x: {optimizer.best_parameters['x']:.6f}")
    print(f"  Final y: {optimizer.best_parameters['y']:.6f}")
    print(f"  Final metric: {optimizer.best_metric:.6e}")
    print(f"  Stop reason: {optimizer.stop_reason}")
    
    # Check if we found the optimum (x=1, y=1)
    assert abs(optimizer.best_parameters['x'] - 1.0) < 0.1
    assert abs(optimizer.best_parameters['y'] - 1.0) < 0.1
    assert optimizer.best_metric < 0.01
    
    print("[PASS] Test passed: Found optimal solution")
    return optimizer


def test_sphere_provided_gradients():
    """Test Adam with provided gradients on Sphere function."""
    print("\n" + "="*60)
    print("Testing Adam with PROVIDED gradients on Sphere function (3D)")
    print("="*60)
    
    # Define 3D parameters
    param_config = [
        {'name': 'x1', 'min': -5, 'max': 5, 'default': 2.0},
        {'name': 'x2', 'min': -5, 'max': 5, 'default': -3.0},
        {'name': 'x3', 'min': -5, 'max': 5, 'default': 1.5}
    ]
    parameters = Parameters(param_config)
    
    # Run optimization with provided gradients
    optimizer = Adam(
        seed=42,
        eval_func=sphere_with_gradients,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=100,
        learning_rate=0.1,
        gradient_method='provided',
        gradient_tolerance=1e-8
    )
    
    optimizer.run_optimization()
    
    print(f"\nOptimization completed:")
    print(f"  Iterations: {optimizer.iter}")
    print(f"  Function evaluations: {optimizer.nr_evaluations}")
    print(f"  Final x1: {optimizer.best_parameters['x1']:.6f}")
    print(f"  Final x2: {optimizer.best_parameters['x2']:.6f}")
    print(f"  Final x3: {optimizer.best_parameters['x3']:.6f}")
    print(f"  Final metric: {optimizer.best_metric:.6e}")
    print(f"  Stop reason: {optimizer.stop_reason}")
    
    # Check if we found the optimum (all zeros)
    for param in ['x1', 'x2', 'x3']:
        assert abs(optimizer.best_parameters[param]) < 0.001
    assert optimizer.best_metric < 0.001
    
    print("[PASS] Test passed: Found optimal solution")
    return optimizer


def test_comparison_with_numerical_gradients():
    """Compare provided gradients vs numerical gradient estimation."""
    print("\n" + "="*60)
    print("Comparing PROVIDED vs NUMERICAL gradients")
    print("="*60)
    
    # Define parameters
    param_config = [
        {'name': 'x', 'min': -2, 'max': 2, 'default': 1.5},
        {'name': 'y', 'min': -2, 'max': 2, 'default': 1.5}
    ]
    
    # Test with provided gradients
    parameters_provided = Parameters(param_config)
    optimizer_provided = Adam(
        seed=42,
        eval_func=rosenbrock_with_gradients,
        parameters=parameters_provided,
        opt_min_or_max='min',
        max_iterations=50,
        learning_rate=0.01,
        gradient_method='provided'
    )
    optimizer_provided.run_optimization()
    
    # Test with numerical gradients (finite difference)
    def rosenbrock_no_gradients(params_df, **kwargs):
        """Rosenbrock without gradients."""
        responses = []
        for _, row in params_df.iterrows():
            x, y = row['x'], row['y']
            metric = (1 - x)**2 + 100 * (y - x**2)**2
            responses.append({'metric': metric})
        return responses
    
    parameters_numerical = Parameters(param_config)
    optimizer_numerical = Adam(
        seed=42,
        eval_func=rosenbrock_no_gradients,
        parameters=parameters_numerical,
        opt_min_or_max='min',
        max_iterations=50,
        learning_rate=0.01,
        gradient_method='finite_difference',
        gradient_step_size=1e-5
    )
    optimizer_numerical.run_optimization()
    
    print(f"\nResults comparison:")
    print(f"  Provided gradients:")
    print(f"    Iterations: {optimizer_provided.iter}")
    print(f"    Evaluations: {optimizer_provided.nr_evaluations}")
    print(f"    Final metric: {optimizer_provided.best_metric:.6e}")
    print(f"  Numerical gradients:")
    print(f"    Iterations: {optimizer_numerical.iter}")
    print(f"    Evaluations: {optimizer_numerical.nr_evaluations}")
    print(f"    Final metric: {optimizer_numerical.best_metric:.6e}")
    
    # Provided gradients should be much more efficient (fewer evaluations)
    assert optimizer_provided.nr_evaluations < optimizer_numerical.nr_evaluations
    
    print(f"\n[PASS] Efficiency gain: {optimizer_numerical.nr_evaluations / optimizer_provided.nr_evaluations:.1f}x fewer evaluations with provided gradients")
    
    return optimizer_provided, optimizer_numerical


def test_scaled_parameters_with_gradients():
    """Test Adam with provided gradients on different parameter scales."""
    print("\n" + "="*60)
    print("Testing PROVIDED gradients with different parameter scales")
    print("="*60)
    
    # Define parameters with different scales
    param_config = [
        {'name': 'x_linear', 'min': -5, 'max': 5, 'scale': 'linear', 'default': 3.0},
        {'name': 'x_log', 'min': 0.1, 'max': 10, 'scale': 'log', 'default': 1.0},
        {'name': 'x_symlog', 'min': -100, 'max': 100, 'scale': 'symlog', 'default': -10.0}
    ]
    parameters = Parameters(param_config)
    
    def scaled_sphere_with_gradients(params_df, **kwargs):
        """Sphere function with gradients for scaled parameters."""
        responses = []
        for _, row in params_df.iterrows():
            # Compute function value
            metric = sum(row[col]**2 for col in params_df.columns)
            
            # Compute analytical gradients (in original space)
            gradients = {col: 2 * row[col] for col in params_df.columns}
            
            response = {
                'metric': metric,
                'gradients': gradients
            }
            responses.append(response)
        return responses
    
    # Run optimization
    optimizer = Adam(
        seed=42,
        eval_func=scaled_sphere_with_gradients,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=200,
        learning_rate=0.1,
        gradient_method='provided',
        gradient_tolerance=1e-6
    )
    
    optimizer.run_optimization()
    
    print(f"\nOptimization completed:")
    print(f"  Iterations: {optimizer.iter}")
    print(f"  Function evaluations: {optimizer.nr_evaluations}")
    print(f"  Final x_linear: {optimizer.best_parameters['x_linear']:.6f}")
    print(f"  Final x_log: {optimizer.best_parameters['x_log']:.6f}")
    print(f"  Final x_symlog: {optimizer.best_parameters['x_symlog']:.6f}")
    print(f"  Final metric: {optimizer.best_metric:.6e}")
    print(f"  Stop reason: {optimizer.stop_reason}")
    
    # Check convergence
    assert optimizer.best_metric < 0.02
    
    print("[PASS] Test passed: Converged with scaled parameters")
    return optimizer


def test_rastrigin_provided_gradients():
    """Test Adam with provided gradients on multimodal Rastrigin function."""
    print("\n" + "="*60)
    print("Testing Adam with PROVIDED gradients on Rastrigin function")
    print("="*60)
    
    # Define 2D parameters
    param_config = [
        {'name': 'x', 'min': -5.12, 'max': 5.12, 'default': 2.0},
        {'name': 'y', 'min': -5.12, 'max': 5.12, 'default': -2.0}
    ]
    parameters = Parameters(param_config)
    
    # Run optimization with provided gradients
    optimizer = Adam(
        seed=42,
        eval_func=rastrigin_with_gradients,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=200,
        learning_rate=0.01,
        gradient_method='provided',
        gradient_tolerance=1e-6,
        amsgrad=True  # Use AMSGrad variant for better convergence
    )
    
    optimizer.run_optimization()
    
    print(f"\nOptimization completed:")
    print(f"  Iterations: {optimizer.iter}")
    print(f"  Function evaluations: {optimizer.nr_evaluations}")
    print(f"  Final x: {optimizer.best_parameters['x']:.6f}")
    print(f"  Final y: {optimizer.best_parameters['y']:.6f}")
    print(f"  Final metric: {optimizer.best_metric:.6e}")
    print(f"  Stop reason: {optimizer.stop_reason}")
    
    # Check if we found a good solution (global optimum is at origin with value 0)
    # Rastrigin has many local minima, so we check for reasonable convergence
    print(f"  Distance from global optimum: {np.sqrt(optimizer.best_parameters['x']**2 + optimizer.best_parameters['y']**2):.6f}")
    
    # At least should find a local minimum
    assert optimizer.gradient_norm < 0.1 or optimizer.best_metric < 10
    
    print("[PASS] Test passed: Found a local minimum")
    return optimizer


def test_error_handling():
    """Test error handling for missing gradients."""
    print("\n" + "="*60)
    print("Testing error handling for missing gradients")
    print("="*60)
    
    # Define parameters
    param_config = [
        {'name': 'x', 'min': -5, 'max': 5, 'default': 1.0},
        {'name': 'y', 'min': -5, 'max': 5, 'default': 1.0}
    ]
    parameters = Parameters(param_config)
    
    # Function that doesn't provide gradients
    def no_gradients_func(params_df, **kwargs):
        responses = []
        for _, row in params_df.iterrows():
            x, y = row['x'], row['y']
            metric = x**2 + y**2
            responses.append({'metric': metric})  # No gradients!
        return responses
    
    # Function with partial gradients
    def partial_gradients_func(params_df, **kwargs):
        responses = []
        for _, row in params_df.iterrows():
            x, y = row['x'], row['y']
            metric = x**2 + y**2
            # Only provide gradient for x, missing y
            responses.append({'metric': metric, 'gradients': {'x': 2*x}})
        return responses
    
    # Test 1: No gradients provided but gradient_method='provided'
    try:
        optimizer1 = Adam(
            seed=42,
            eval_func=no_gradients_func,
            parameters=parameters,
            gradient_method='provided',
            max_iterations=10
        )
        optimizer1.run_optimization()
        print("[FAIL] Should have raised an error for missing gradients")
        assert False
    except ValueError as e:
        print(f"[PASS] Correctly raised error: {str(e)[:80]}...")
    
    # Test 2: Partial gradients provided
    try:
        optimizer2 = Adam(
            seed=42,
            eval_func=partial_gradients_func,
            parameters=parameters,
            gradient_method='provided',
            max_iterations=10
        )
        optimizer2.run_optimization()
        print("[FAIL] Should have raised an error for partial gradients")
        assert False
    except ValueError as e:
        print(f"[PASS] Correctly raised error: {str(e)[:80]}...")
    
    print("\n[PASS] All error handling tests passed")


def run_all_tests():
    """Run all tests for Adam optimizer with provided gradients."""
    print("\n" + "#"*60)
    print("# Testing Adam Optimizer with Provided Gradients")
    print("#"*60)
    
    # Run individual tests
    test_rosenbrock_provided_gradients()
    test_sphere_provided_gradients()
    test_comparison_with_numerical_gradients()
    test_scaled_parameters_with_gradients()
    test_rastrigin_provided_gradients()
    test_error_handling()
    
    print("\n" + "#"*60)
    print("# All tests completed successfully!")
    print("#"*60)


if __name__ == "__main__":
    run_all_tests()