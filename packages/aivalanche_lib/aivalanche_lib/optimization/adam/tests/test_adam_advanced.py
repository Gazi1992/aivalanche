"""
Advanced tests for ADAM optimizer including metamodel integration and animations.

This script tests more advanced features of the ADAM optimizer.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from aivalanche_lib.optimization.adam import Adam
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details, generate_parameters_config
from aivalanche_lib.optimization.adam.visualizations import _create_convergence_animation, _plot_optimization_summary


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


def test_adam_animation():
    """Test ADAM optimization animation for 2D functions."""
    print("\n=== Testing ADAM Animation ===")
    
    # Test functions for animation
    test_functions = ['rosenbrock_2d', 'himmelblau_2d', 'beale_2d']
    
    for func_name in test_functions:
        print(f"\nCreating animation for {func_name}...")
        
        # Get function details
        func_details = get_function_details(func_name)
        param_config = generate_parameters_config(func_details)
        parameters = Parameters(param_config)
        eval_func = create_test_function_wrapper(func_details)
        
        # Create results directory in same location as test script
        test_dir = os.path.dirname(os.path.abspath(__file__))
        results_dir = os.path.join(test_dir, f'test_results_animations_{func_name}')
        os.makedirs(results_dir, exist_ok=True)
        
        # Create optimizer
        optimizer = Adam(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            opt_min_or_max='min',
            max_iterations=100,
            learning_rate=0.05,
            results_dir=results_dir
        )
        
        # Run optimization
        optimizer.run_optimization()
        
        # Create animation
        animation_path = os.path.join(results_dir, f'adam_{func_name}_animation.gif')
        try:
            anim = _create_convergence_animation(
                optimizer,
                figsize=(10, 8),
                interval=50,
                fps=10,
                save_path=animation_path,
                func_details=func_details
            )
            print(f"  ✓ Animation saved to: {animation_path}")
        except Exception as e:
            print(f"  ⚠ Animation failed: {str(e)}")
        
        # Create summary plot
        summary_path = os.path.join(results_dir, f'adam_{func_name}_summary.png')
        _plot_optimization_summary(optimizer, save_path=summary_path)
        print(f"  ✓ Summary plot saved to: {summary_path}")
    
    return True


def test_adam_high_dimensional():
    """Test ADAM on high-dimensional problems."""
    print("\n=== Testing ADAM on High-Dimensional Problems ===")
    
    # Test on sphere function with different dimensions
    dimensions = [5, 10, 20]
    
    for dim in dimensions:
        print(f"\nTesting {dim}D sphere function...")
        
        # Create high-dimensional sphere function
        def sphere_nd(x):
            return np.sum(x**2)
        
        # Create parameter configuration
        param_config = []
        for i in range(dim):
            param_config.append({
                'name': f'x{i+1}',
                'min': -5.0,
                'max': 5.0,
                'default': 0.0,
                'mode': 'variable',
                'type': 'continuous'
            })
        
        parameters = Parameters(param_config)
        
        # Create evaluation function
        def eval_func(params_df, **kwargs):
            responses = []
            for _, row in params_df.iterrows():
                x_values = [row[f'x{i+1}'] for i in range(dim)]
                value = sphere_nd(np.array(x_values))
                responses.append({'metric': value})
            return responses
        
        # Create optimizer
        optimizer = Adam(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            opt_min_or_max='min',
            max_iterations=200,
            learning_rate=0.1,
            gradient_tolerance=1e-6,
            gradient_method='simultaneous_perturbation'  # More efficient for high-dim
        )
        
        # Run optimization
        optimizer.run_optimization()
        
        # Check results
        assert optimizer.best_metric < 1e-4, f"Failed to minimize {dim}D sphere"
        
        # Check that all parameters are close to 0
        best_params = optimizer.best_parameters
        for i in range(dim):
            assert abs(best_params[f'x{i+1}']) < 1e-2, f"Parameter x{i+1} not close to 0"
        
        print(f"  ✓ Successfully minimized {dim}D sphere")
        print(f"    Best metric: {optimizer.best_metric:.6e}")
        print(f"    Iterations: {optimizer.iter}")
        print(f"    Evaluations: {optimizer.nr_evaluations}")
    
    return True


def test_adam_with_fixed_parameters():
    """Test ADAM with some fixed parameters."""
    print("\n=== Testing ADAM with Fixed Parameters ===")
    
    # Create parameter configuration with mixed fixed/variable parameters
    param_config = [
        {'name': 'x1', 'min': -5.0, 'max': 5.0, 'default': 0.0, 'mode': 'variable', 'type': 'continuous'},
        {'name': 'x2', 'min': -5.0, 'max': 5.0, 'default': 1.0, 'mode': 'fixed', 'type': 'continuous'},
        {'name': 'x3', 'min': -5.0, 'max': 5.0, 'default': 0.0, 'mode': 'variable', 'type': 'continuous'},
        {'name': 'x4', 'min': -5.0, 'max': 5.0, 'default': -1.0, 'mode': 'fixed', 'type': 'continuous'}
    ]
    
    parameters = Parameters(param_config)
    
    # Create test function (sum of squares)
    def eval_func(params_df, **kwargs):
        responses = []
        for _, row in params_df.iterrows():
            value = row['x1']**2 + row['x2']**2 + row['x3']**2 + row['x4']**2
            responses.append({'metric': value})
        return responses
    
    # Create optimizer
    optimizer = Adam(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=100,
        learning_rate=0.1
    )
    
    # Run optimization
    optimizer.run_optimization()
    
    # Check that fixed parameters didn't change
    history_df, _ = optimizer._get_history_as_df('points')
    assert (history_df['x2'] == 1.0).all(), "Fixed parameter x2 should not change"
    assert (history_df['x4'] == -1.0).all(), "Fixed parameter x4 should not change"
    
    # Check that variable parameters optimized correctly
    assert abs(optimizer.best_parameters['x1']) < 1e-3, "Variable parameter x1 should be near 0"
    assert abs(optimizer.best_parameters['x3']) < 1e-3, "Variable parameter x3 should be near 0"
    
    # Expected minimum value: 0^2 + 1^2 + 0^2 + (-1)^2 = 2
    expected_min = 2.0
    assert abs(optimizer.best_metric - expected_min) < 1e-6, \
        f"Expected minimum {expected_min}, got {optimizer.best_metric}"
    
    print(f"✓ Fixed parameters handled correctly")
    print(f"  Variable parameters: x1={optimizer.best_parameters['x1']:.4f}, x3={optimizer.best_parameters['x3']:.4f}")
    print(f"  Fixed parameters: x2={optimizer.best_parameters['x2']:.4f}, x4={optimizer.best_parameters['x4']:.4f}")
    print(f"  Best metric: {optimizer.best_metric:.6f} (expected: {expected_min})")
    
    return optimizer


def test_adam_comparison_with_other_optimizers():
    """Compare ADAM with other optimizers on the same problem."""
    print("\n=== Comparing ADAM with Other Optimizers ===")
    
    from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
    from aivalanche_lib.optimization.nelder_mead import NelderMead
    
    # Get function details
    func_details = get_function_details('rosenbrock_2d')
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    eval_func = create_test_function_wrapper(func_details)
    
    results = {}
    
    # Test ADAM
    print("\nRunning ADAM...")
    adam_opt = Adam(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=200,
        learning_rate=0.01
    )
    adam_opt.run_optimization()
    results['ADAM'] = {
        'best_metric': adam_opt.best_metric,
        'iterations': adam_opt.iter,
        'evaluations': adam_opt.nr_evaluations
    }
    
    # Test Differential Evolution
    print("\nRunning Differential Evolution...")
    de_opt = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=50,
        pop_size=20
    )
    de_opt.run_optimization()
    results['DE'] = {
        'best_metric': de_opt.best_metric,
        'iterations': de_opt.iter,
        'evaluations': de_opt.nr_evaluations
    }
    
    # Test Nelder-Mead
    print("\nRunning Nelder-Mead...")
    nm_opt = NelderMead(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=200
    )
    nm_opt.run_optimization()
    results['Nelder-Mead'] = {
        'best_metric': nm_opt.best_metric,
        'iterations': nm_opt.iter,
        'evaluations': nm_opt.nr_evaluations
    }
    
    # Compare results
    print("\n✓ Optimizer Comparison on Rosenbrock 2D:")
    print(f"{'Optimizer':<15} {'Best Metric':<15} {'Iterations':<12} {'Evaluations':<12}")
    print("-" * 54)
    for opt_name, res in results.items():
        print(f"{opt_name:<15} {res['best_metric']:<15.6e} {res['iterations']:<12} {res['evaluations']:<12}")
    
    # All optimizers should find good solutions
    for opt_name, res in results.items():
        assert res['best_metric'] < 1e-2, f"{opt_name} failed to find good solution"
    
    return results


def test_adam_restart_capability():
    """Test restarting ADAM from a previous state."""
    print("\n=== Testing ADAM Restart Capability ===")
    
    # Get function details
    func_details = get_function_details('sphere_3d')
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    eval_func = create_test_function_wrapper(func_details)
    
    # First run: Stop early
    print("\nFirst run: 50 iterations")
    optimizer1 = Adam(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=50,
        learning_rate=0.1
    )
    optimizer1.run_optimization()
    
    # Save state
    best_params_1 = optimizer1.best_parameters.copy()
    best_metric_1 = optimizer1.best_metric
    final_point_1 = optimizer1.current_point.copy()
    
    print(f"  Best metric after 50 iterations: {best_metric_1:.6e}")
    
    # Second run: Continue from where we left off
    print("\nSecond run: Continue from previous best")
    optimizer2 = Adam(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=50,
        learning_rate=0.1,
        initial_point=pd.DataFrame([best_params_1])
    )
    optimizer2.run_optimization()
    
    best_metric_2 = optimizer2.best_metric
    
    print(f"  Best metric after restart: {best_metric_2:.6e}")
    
    # The restarted optimization should improve or maintain the result
    assert best_metric_2 <= best_metric_1 * 1.1, \
        "Restarted optimization should not significantly worsen"
    
    print(f"✓ Restart capability working correctly")
    print(f"  Improvement: {(best_metric_1 - best_metric_2) / best_metric_1 * 100:.2f}%")
    
    return optimizer1, optimizer2


def test_adam_with_noisy_function():
    """Test ADAM with a noisy objective function."""
    print("\n=== Testing ADAM with Noisy Function ===")
    
    # Create a noisy version of sphere function
    noise_level = 0.1
    rng = np.random.RandomState(42)
    
    def noisy_sphere(x):
        true_value = np.sum(x**2)
        noise = rng.normal(0, noise_level * (1 + true_value))
        return true_value + noise
    
    # Create parameter configuration
    param_config = [
        {'name': 'x1', 'min': -5.0, 'max': 5.0, 'default': 0.0, 'mode': 'variable', 'type': 'continuous'},
        {'name': 'x2', 'min': -5.0, 'max': 5.0, 'default': 0.0, 'mode': 'variable', 'type': 'continuous'}
    ]
    parameters = Parameters(param_config)
    
    # Create evaluation function
    def eval_func(params_df, **kwargs):
        responses = []
        for _, row in params_df.iterrows():
            x_values = [row['x1'], row['x2']]
            value = noisy_sphere(np.array(x_values))
            responses.append({'metric': value})
        return responses
    
    # Create optimizer with adjusted settings for noisy function
    optimizer = Adam(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=200,
        learning_rate=0.01,  # Smaller learning rate for stability
        gradient_step_size=0.01,  # Larger step size for gradient estimation
        gradient_method='simultaneous_perturbation',  # More robust to noise
        gradient_tolerance=1e-4  # Relax tolerance due to noise
    )
    
    # Run optimization
    optimizer.run_optimization()
    
    # Check that optimizer found a reasonable solution despite noise
    # With noise, we can't expect perfect convergence
    assert optimizer.best_metric < 1.0, "Failed to find reasonable solution with noisy function"
    
    # Check parameters are reasonably close to optimum
    assert abs(optimizer.best_parameters['x1']) < 0.5, "x1 too far from optimum"
    assert abs(optimizer.best_parameters['x2']) < 0.5, "x2 too far from optimum"
    
    print(f"✓ ADAM handled noisy function successfully")
    print(f"  Best metric: {optimizer.best_metric:.6f} (with noise level {noise_level})")
    print(f"  Best parameters: x1={optimizer.best_parameters['x1']:.4f}, x2={optimizer.best_parameters['x2']:.4f}")
    
    return optimizer


if __name__ == "__main__":
    print("Running ADAM optimizer advanced tests...")
    
    # Run tests
    test_adam_animation()
    test_adam_high_dimensional()
    test_adam_with_fixed_parameters()
    test_adam_comparison_with_other_optimizers()
    test_adam_restart_capability()
    test_adam_with_noisy_function()
    
    print("\n[SUCCESS] All ADAM advanced tests passed!")