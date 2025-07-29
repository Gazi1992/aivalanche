"""
Basic tests for ADAM optimizer.

This script tests the core functionality of the ADAM optimizer
on simple test functions.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from aivalanche_lib.optimization.adam import Adam
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


def test_adam_sphere_2d():
    """Test ADAM on 2D sphere function."""
    print("\n=== Testing ADAM on Sphere 2D ===")
    
    # Get function details
    func_details = get_function_details('sphere_2d')
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    eval_func = create_test_function_wrapper(func_details)
    
    # Create results directory in same location as test script
    test_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(test_dir, 'test_results_sphere_2d')
    os.makedirs(results_dir, exist_ok=True)
    
    # Create optimizer
    optimizer = Adam(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=100,
        learning_rate=0.1,
        gradient_tolerance=1e-6,
        results_dir=results_dir
    )
    
    # Run optimization
    optimizer.run_optimization()
    
    # Check results
    assert optimizer.best_metric < 1e-6, f"Failed to minimize sphere function: {optimizer.best_metric}"
    assert np.allclose(optimizer.best_parameters[['x1', 'x2']].values, [0, 0], atol=1e-3), \
        f"Failed to find correct minimum: {optimizer.best_parameters[['x1', 'x2']].values}"
    
    # Save results
    optimizer.write_best_parameters_to_file(os.path.join(results_dir, 'best_parameters.csv'))
    optimizer.write_optimization_info_to_file(os.path.join(results_dir, 'optimization_info.json'))
    
    # Create plots
    optimizer.plot_metrics(save_path=os.path.join(results_dir, 'metrics_evolution.png'))
    optimizer.plot_gradient_norm(save_path=os.path.join(results_dir, 'gradient_norm.png'))
    optimizer.plot_learning_rate(save_path=os.path.join(results_dir, 'learning_rate.png'))
    
    print(f"✓ ADAM successfully minimized sphere function")
    print(f"  Final metric: {optimizer.best_metric:.6e}")
    print(f"  Iterations: {optimizer.iter}")
    print(f"  Evaluations: {optimizer.nr_evaluations}")
    
    return optimizer


def test_adam_rosenbrock_2d():
    """Test ADAM on 2D Rosenbrock function."""
    print("\n=== Testing ADAM on Rosenbrock 2D ===")
    
    # Get function details
    func_details = get_function_details('rosenbrock_2d')
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    eval_func = create_test_function_wrapper(func_details)
    
    # Create results directory in same location as test script
    test_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(test_dir, 'test_results_rosenbrock_2d')
    os.makedirs(results_dir, exist_ok=True)
    
    # Create optimizer with smaller learning rate for Rosenbrock
    optimizer = Adam(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=500,
        learning_rate=0.01,
        gradient_tolerance=1e-6,
        beta1=0.9,
        beta2=0.999,
        results_dir=results_dir
    )
    
    # Run optimization
    optimizer.run_optimization()
    
    # Check results (Rosenbrock minimum is at (1, 1) with value 0)
    assert optimizer.best_metric < 1e-4, f"Failed to minimize Rosenbrock function: {optimizer.best_metric}"
    assert np.allclose(optimizer.best_parameters[['x1', 'x2']].values, [1, 1], atol=1e-2), \
        f"Failed to find correct minimum: {optimizer.best_parameters[['x1', 'x2']].values}"
    
    # Save results and create plots
    optimizer.write_best_parameters_to_file(os.path.join(results_dir, 'best_parameters.csv'))
    optimizer.plot_metrics(save_path=os.path.join(results_dir, 'metrics_evolution.png'))
    optimizer.plot_parameters_evolution(save_path=os.path.join(results_dir, 'parameters_evolution.png'))
    
    print(f"✓ ADAM successfully minimized Rosenbrock function")
    print(f"  Final metric: {optimizer.best_metric:.6e}")
    print(f"  Best parameters: x1={optimizer.best_parameters['x1']:.4f}, x2={optimizer.best_parameters['x2']:.4f}")
    
    return optimizer


def test_adam_with_learning_rate_decay():
    """Test ADAM with learning rate decay."""
    print("\n=== Testing ADAM with Learning Rate Decay ===")
    
    # Get function details
    func_details = get_function_details('ackley_nd')
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    eval_func = create_test_function_wrapper(func_details)
    
    # Create results directory in same location as test script
    test_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(test_dir, 'test_results_ackley_lr_decay')
    os.makedirs(results_dir, exist_ok=True)
    
    # Create optimizer with learning rate decay
    optimizer = Adam(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=200,
        learning_rate=0.1,
        learning_rate_decay=0.01,  # Decay factor
        gradient_tolerance=1e-6,
        results_dir=results_dir
    )
    
    # Run optimization
    optimizer.run_optimization()
    
    # Check that learning rate decayed
    final_lr = optimizer.all_learning_rates[-1]
    initial_lr = optimizer.learning_rate
    expected_final_lr = initial_lr / (1 + optimizer.learning_rate_decay * optimizer.iter)
    
    assert np.isclose(final_lr, expected_final_lr), \
        f"Learning rate decay not working correctly: {final_lr} vs {expected_final_lr}"
    
    # Save results
    optimizer.write_optimization_info_to_file(os.path.join(results_dir, 'optimization_info.json'))
    optimizer.plot_learning_rate(save_path=os.path.join(results_dir, 'learning_rate_decay.png'))
    
    print(f"✓ Learning rate decay working correctly")
    print(f"  Initial LR: {initial_lr}")
    print(f"  Final LR: {final_lr:.6f}")
    print(f"  Best metric: {optimizer.best_metric:.6e}")
    
    return optimizer


def test_adam_amsgrad():
    """Test ADAM with AMSGrad variant."""
    print("\n=== Testing ADAM with AMSGrad ===")
    
    # Get function details
    func_details = get_function_details('ackley_2d')
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    eval_func = create_test_function_wrapper(func_details)
    
    # Create results directory in same location as test script
    test_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(test_dir, 'test_results_ackley_amsgrad')
    os.makedirs(results_dir, exist_ok=True)
    
    # Create optimizer with AMSGrad
    optimizer = Adam(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=200,
        learning_rate=0.05,
        amsgrad=True,  # Enable AMSGrad
        gradient_tolerance=1e-6,
        results_dir=results_dir
    )
    
    # Run optimization
    optimizer.run_optimization()
    
    # Check that AMSGrad is being used
    assert optimizer.amsgrad is True, "AMSGrad should be enabled"
    assert optimizer.v_hat_max is not None, "v_hat_max should be initialized for AMSGrad"
    
    # Save results
    optimizer.write_best_parameters_to_file(os.path.join(results_dir, 'best_parameters.csv'))
    
    print(f"✓ AMSGrad variant working correctly")
    print(f"  Best metric: {optimizer.best_metric:.6e}")
    print(f"  Iterations: {optimizer.iter}")
    
    return optimizer


def test_adam_gradient_methods():
    """Test different gradient estimation methods."""
    print("\n=== Testing ADAM Gradient Estimation Methods ===")
    
    # Get function details
    func_details = get_function_details('sphere_3d')
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    eval_func = create_test_function_wrapper(func_details)
    
    results = {}
    
    # Test finite difference
    print("\nTesting finite difference gradient...")
    optimizer_fd = Adam(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=50,
        gradient_method='finite_difference',
        gradient_step_size=1e-5,
        gradient_step_size_relative=False
    )
    optimizer_fd.run_optimization()
    results['finite_difference'] = {
        'metric': optimizer_fd.best_metric,
        'evaluations': optimizer_fd.nr_evaluations,
        'iterations': optimizer_fd.iter
    }
    
    # Test simultaneous perturbation
    print("\nTesting simultaneous perturbation gradient...")
    optimizer_sp = Adam(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=50,
        gradient_method='simultaneous_perturbation',
        gradient_step_size=1e-3,
        gradient_step_size_relative=True
    )
    optimizer_sp.run_optimization()
    results['simultaneous_perturbation'] = {
        'metric': optimizer_sp.best_metric,
        'evaluations': optimizer_sp.nr_evaluations,
        'iterations': optimizer_sp.iter
    }
    
    # Compare results
    print("\n✓ Gradient estimation comparison:")
    for method, res in results.items():
        print(f"  {method}:")
        print(f"    Best metric: {res['metric']:.6e}")
        print(f"    Evaluations: {res['evaluations']}")
        print(f"    Iterations: {res['iterations']}")
    
    # Check that both methods found good solutions
    for method, res in results.items():
        assert res['metric'] < 1e-4, f"{method} failed to minimize function"
    
    return results


def test_adam_boundary_handling():
    """Test different boundary handling methods."""
    print("\n=== Testing ADAM Boundary Handling ===")
    
    # Create custom function that has optimum near boundary
    def boundary_test_func(x):
        # Optimum at (4.5, 4.5) - near upper boundary of [-5, 5]
        return (x[0] - 4.5)**2 + (x[1] - 4.5)**2
    
    func_details = {
        'func': boundary_test_func,
        'dim': 2,
        'bounds': [(-5, 5), (-5, 5)],
        'global_min': 0.0,
        'global_min_loc': [[4.5, 4.5]]
    }
    
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    eval_func = create_test_function_wrapper(func_details)
    
    # Test different boundary handling methods
    boundary_methods = ['clip', 'reflect', 'none']
    
    for method in boundary_methods:
        print(f"\nTesting {method} boundary handling...")
        
        optimizer = Adam(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            opt_min_or_max='min',
            max_iterations=100,
            learning_rate=0.1,
            boundary_handling=method,
            initial_point=pd.DataFrame({'x1': [0.0], 'x2': [0.0]})
        )
        
        # For 'none' method, we expect it might go outside bounds
        if method == 'none':
            # Just run without assertions about bounds
            optimizer.run_optimization()
        else:
            optimizer.run_optimization()
            
            # Check that parameters stayed within bounds
            history_df, _ = optimizer._get_history_as_df('points')
            assert (history_df['x1'] >= -5).all() and (history_df['x1'] <= 5).all(), \
                f"{method}: x1 went outside bounds"
            assert (history_df['x2'] >= -5).all() and (history_df['x2'] <= 5).all(), \
                f"{method}: x2 went outside bounds"
        
        print(f"  ✓ {method}: Best metric = {optimizer.best_metric:.6e}")
        print(f"    Best params: x1={optimizer.best_parameters['x1']:.4f}, x2={optimizer.best_parameters['x2']:.4f}")


def test_adam_with_callbacks():
    """Test ADAM with various callbacks."""
    print("\n=== Testing ADAM with Callbacks ===")
    
    # Get function details
    func_details = get_function_details('sphere_2d')
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    eval_func = create_test_function_wrapper(func_details)
    
    # Track callback executions
    callback_counts = {
        'first': 0,
        'each': 0,
        'better': 0,
        'last': 0
    }
    
    def callback_first(**kwargs):
        callback_counts['first'] += 1
        assert kwargs['iteration'] == 1
    
    def callback_each(**kwargs):
        callback_counts['each'] += 1
        assert 'gradient' in kwargs
        assert 'gradient_norm' in kwargs
    
    def callback_better(**kwargs):
        callback_counts['better'] += 1
        assert kwargs['optimizer'].better_solution_found
    
    def callback_last(**kwargs):
        callback_counts['last'] += 1
        assert kwargs['optimizer'].is_stop_criteria_reached
    
    # Create optimizer with callbacks
    optimizer = Adam(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=50,
        callback_after_first_iter=callback_first,
        callback_after_each_iter=callback_each,
        callback_after_better_solution=callback_better,
        callback_after_last_iter=callback_last
    )
    
    # Run optimization
    optimizer.run_optimization()
    
    # Check callback executions
    assert callback_counts['first'] == 1, "First iteration callback should execute once"
    assert callback_counts['each'] == optimizer.iter, "Each iteration callback count mismatch"
    assert callback_counts['better'] > 0, "Better solution callback should execute at least once"
    assert callback_counts['last'] == 1, "Last iteration callback should execute once"
    
    print(f"✓ Callbacks executed correctly:")
    print(f"  First iteration: {callback_counts['first']}")
    print(f"  Each iteration: {callback_counts['each']}")
    print(f"  Better solution: {callback_counts['better']}")
    print(f"  Last iteration: {callback_counts['last']}")
    
    return optimizer


def test_adam_stop_criteria():
    """Test various stopping criteria."""
    print("\n=== Testing ADAM Stop Criteria ===")
    
    # Get function details
    func_details = get_function_details('sphere_2d')
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    eval_func = create_test_function_wrapper(func_details)
    
    # Test 1: Metric threshold
    print("\nTest 1: Metric threshold")
    opt1 = Adam(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        metric_threshold=1e-4,
        max_iterations=1000
    )
    opt1.run_optimization()
    assert opt1.stop_reason == "metric threshold reached"
    assert opt1.best_metric < 1e-4
    print(f"  ✓ Stopped at iteration {opt1.iter} with metric {opt1.best_metric:.6e}")
    
    # Test 2: Gradient tolerance
    print("\nTest 2: Gradient tolerance")
    opt2 = Adam(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        gradient_tolerance=1e-3,
        max_iterations=1000
    )
    opt2.run_optimization()
    assert opt2.stop_reason == "gradient tolerance reached"
    assert opt2.gradient_norm < 1e-3
    print(f"  ✓ Stopped at iteration {opt2.iter} with gradient norm {opt2.gradient_norm:.6e}")
    
    # Test 3: Max iterations
    print("\nTest 3: Max iterations")
    opt3 = Adam(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=10
    )
    opt3.run_optimization()
    assert opt3.stop_reason == "maximum number of iterations reached"
    assert opt3.iter == 10
    print(f"  ✓ Stopped at max iterations: {opt3.iter}")
    
    # Test 4: No improvement
    print("\nTest 4: No improvement")
    # Use a difficult function where improvement plateaus
    opt4 = Adam(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        max_iterations=1000,
        max_iter_without_improvement=20,
        improvement_threshold=1e-6,
        learning_rate=0.001  # Small learning rate to plateau quickly
    )
    opt4.run_optimization()
    assert "without improvement" in opt4.stop_reason
    print(f"  ✓ Stopped after {opt4.iter_no_improvement} iterations without improvement")
    
    return [opt1, opt2, opt3, opt4]


if __name__ == "__main__":
    print("Running ADAM optimizer basic tests...")
    
    # Run tests
    test_adam_sphere_2d()
    test_adam_rosenbrock_2d()
    test_adam_with_learning_rate_decay()
    test_adam_amsgrad()
    test_adam_gradient_methods()
    test_adam_boundary_handling()
    test_adam_with_callbacks()
    test_adam_stop_criteria()
    
    print("\n[SUCCESS] All ADAM basic tests passed!")