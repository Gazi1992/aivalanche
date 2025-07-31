"""
Test script to demonstrate the new metamodel modes functionality.
"""

import numpy as np
import pandas as pd
import os
from datetime import datetime

from aivalanche_lib.optimization.differential_evolution import (
    DifferentialEvolution,
    METAMODEL_MODES,
    get_metamodel_mode_description,
    suggest_metamodel_mode
)
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details, generate_parameters_config


def test_metamodel_modes_functionality():
    """Test basic metamodel modes functionality."""
    print("\n" + "="*60)
    print("TESTING METAMODEL MODES FUNCTIONALITY")
    print("="*60)
    
    # Test available modes
    print("\nAvailable metamodel modes:")
    for mode in METAMODEL_MODES.keys():
        description = get_metamodel_mode_description(mode)
        print(f"  {mode}: {description}")
    
    # Test mode suggestions
    print("\nMode suggestions for different scenarios:")
    
    scenarios = [
        {'problem_type': 'smooth', 'desc': 'Smooth function'},
        {'problem_type': 'multimodal', 'desc': 'Multimodal function'},
        {'n_dim': 50, 'desc': 'High-dimensional (50D)'},
        {'function_noise': 'high', 'desc': 'Noisy function'},
        {'n_evaluations_budget': 300, 'accuracy_required': 'high', 'desc': 'Limited budget, high accuracy'},
        {'n_evaluations_budget': 300, 'desc': 'Limited budget'},
    ]
    
    for scenario in scenarios:
        desc = scenario.pop('desc')
        suggested_mode = suggest_metamodel_mode(**scenario)
        print(f"  {desc}: {suggested_mode}")


def run_metamodel_comparison():
    """Compare DE performance with and without metamodel on an expensive function."""
    print("\n" + "="*60)
    print("METAMODEL COMPARISON TEST")
    print("="*60)
    
    # Setup test function (Rosenbrock 5D)
    func_name = 'rosenbrock_nd'
    n_dim = 5
    func_details = get_function_details(func_name, n_dim=n_dim)
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    
    # Create an expensive evaluation function
    eval_count = 0
    eval_times = []
    
    def expensive_eval_func(parameters_df, **kwargs):
        """Simulate expensive function with artificial delay."""
        nonlocal eval_count
        responses = []
        
        for _, row in parameters_df.iterrows():
            # Extract parameter values
            x_values = []
            for i in range(n_dim):
                param_name = f'x{i+1}'
                if param_name in row:
                    x_values.append(row[param_name])
            
            x = np.array(x_values)
            
            # Simulate expensive computation (0.01 second per eval)
            import time
            start_time = time.time()
            value = func_details['func'](x)
            time.sleep(0.01)  # Artificial delay
            eval_time = time.time() - start_time
            
            eval_count += 1
            eval_times.append(eval_time)
            
            response = {
                'metric': value,
                'data': {f'x{i+1}': x_values[i] for i in range(len(x_values))}
            }
            responses.append(response)
        
        return responses
    
    # Test configurations
    test_configs = [
        {'name': 'No Metamodel', 'metamodel_mode': 'off'},
        {'name': 'Auto Metamodel', 'metamodel_mode': 'auto'},
        {'name': 'Fast Metamodel', 'metamodel_mode': 'fast'},
    ]
    
    results = {}
    
    for config in test_configs:
        print(f"\n{'='*40}")
        print(f"Running: {config['name']}")
        print(f"{'='*40}")
        
        # Reset counters
        eval_count = 0
        eval_times = []
        
        # Create optimizer
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=expensive_eval_func,
            parameters=parameters,
            opt_min_or_max='min',
            pop_size=30,
            max_iterations=50,
            max_iter_without_improvement=20,
            metamodel_mode=config['metamodel_mode']
        )
        
        # Run optimization
        start_time = datetime.now()
        optimizer.run_optimization()
        end_time = datetime.now()
        
        # Store results
        results[config['name']] = {
            'best_metric': optimizer.best_metric,
            'iterations': optimizer.iter,
            'actual_evaluations': eval_count,
            'total_time': (end_time - start_time).total_seconds(),
            'avg_eval_time': np.mean(eval_times) if eval_times else 0,
            'metamodel_stats': optimizer.get_metamodel_statistics()
        }
        
        # Print results
        print(f"\nResults for {config['name']}:")
        print(f"  Best metric: {optimizer.best_metric:.6e}")
        print(f"  Iterations: {optimizer.iter}")
        print(f"  Actual evaluations: {eval_count}")
        print(f"  Total time: {results[config['name']]['total_time']:.2f} seconds")
        
        if results[config['name']]['metamodel_stats']:
            stats = results[config['name']]['metamodel_stats']
            print(f"\n  Metamodel Statistics:")
            print(f"    Actual function evaluations: {stats['n_actual_evaluations']}")
            print(f"    Metamodel predictions: {stats['n_metamodel_evaluations']}")
            print(f"    Metamodel usage ratio: {stats['metamodel_usage_ratio']:.2%}")
            print(f"    Time saved: {stats['time_saved']:.2f} seconds")
            print(f"    Speedup factor: {stats['speedup_factor']:.2f}x")
    
    # Summary comparison
    print("\n" + "="*60)
    print("SUMMARY COMPARISON")
    print("="*60)
    
    baseline = results['No Metamodel']
    print(f"\nBaseline (No Metamodel):")
    print(f"  Time: {baseline['total_time']:.2f}s")
    print(f"  Evaluations: {baseline['actual_evaluations']}")
    print(f"  Best metric: {baseline['best_metric']:.6e}")
    
    for name, result in results.items():
        if name != 'No Metamodel':
            print(f"\n{name}:")
            print(f"  Time reduction: {(baseline['total_time'] - result['total_time']) / baseline['total_time'] * 100:.1f}%")
            print(f"  Evaluation reduction: {(baseline['actual_evaluations'] - result['actual_evaluations']) / baseline['actual_evaluations'] * 100:.1f}%")
            print(f"  Metric difference: {abs(result['best_metric'] - baseline['best_metric']):.6e}")


def test_custom_metamodel_configuration():
    """Test custom metamodel configuration."""
    print("\n" + "="*60)
    print("TESTING CUSTOM METAMODEL CONFIGURATION")
    print("="*60)
    
    # Setup simple test function
    func_details = get_function_details('sphere_nd', n_dim=3)
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    
    def eval_func(parameters_df, **kwargs):
        responses = []
        for _, row in parameters_df.iterrows():
            x = np.array([row[f'x{i+1}'] for i in range(3)])
            value = func_details['func'](x)
            responses.append({'metric': value})
        return responses
    
    # Custom metamodel configuration
    custom_config = {
        'enabled': True,
        'type': 'gaussian_process',
        'model_config': {
            'kernel': 'rbf',
            'alpha': 1e-5,
            'n_restarts_optimizer': 5
        },
        'acquisition_strategy': 'mixed',
        'acquisition_function': 'upper_confidence_bound',
        'min_training_points': 20,
        'update_frequency': 3,
        'exploration_ratio': 0.3,
        'uncertainty_threshold': 0.15,
        'validation_frequency': 8,
        'verbose': True
    }
    
    print("Creating optimizer with custom metamodel configuration...")
    
    try:
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            opt_min_or_max='min',
            pop_size=20,
            max_iterations=30,
            metamodel_mode='custom',
            metamodel_config=custom_config
        )
        
        print("Custom configuration accepted!")
        print("\nRunning optimization with custom metamodel...")
        
        optimizer.run_optimization()
        
        print(f"\nOptimization completed:")
        print(f"  Best metric: {optimizer.best_metric:.6e}")
        print(f"  Iterations: {optimizer.iter}")
        
        if optimizer.get_metamodel_statistics():
            stats = optimizer.get_metamodel_statistics()
            print(f"\nMetamodel usage:")
            print(f"  Usage ratio: {stats['metamodel_usage_ratio']:.2%}")
            
    except Exception as e:
        print(f"Error with custom configuration: {e}")


if __name__ == "__main__":
    # Test basic functionality
    test_metamodel_modes_functionality()
    
    # Run comparison test (comment out if metamodel package not available)
    try:
        run_metamodel_comparison()
    except ImportError as e:
        print(f"\nSkipping metamodel comparison test: {e}")
    
    # Test custom configuration
    try:
        test_custom_metamodel_configuration()
    except ImportError as e:
        print(f"\nSkipping custom configuration test: {e}")
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)