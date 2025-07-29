"""
Quick test for metamodel integration in DifferentialEvolution.

This is a simplified test that can be run quickly to verify metamodel functionality.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any

from aivalanche_lib import Parameters, DifferentialEvolution


def simple_quadratic(parameters: pd.DataFrame, **kwargs) -> List[Dict[str, Any]]:
    """
    Simple quadratic function: f(x, y) = x^2 + y^2
    
    This is a fast-evaluating function used to test metamodel mechanics
    without the overhead of artificial delays.
    """
    responses = []
    
    for _, row in parameters.iterrows():
        x = row['x']
        y = row['y']
        
        # Simple quadratic
        metric = x**2 + y**2
        
        response = {
            'metric': metric,
            'data': {'x': x, 'y': y}
        }
        responses.append(response)
    
    return responses


def test_metamodel_basic():
    """Basic test to ensure metamodel integration works."""
    print("\nTesting basic metamodel integration...")
    
    # Define simple 2D problem
    param_config = [
        {'name': 'x', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ]
    
    # Create optimizer with metamodel
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=simple_quadratic,
        parameters=Parameters(param_config),
        opt_min_or_max='min',
        pop_size=10,
        max_iterations=5,
        use_metamodel=True,
        metamodel_type='gaussian_process',
        metamodel_acquisition_strategy='mixed',
        metamodel_min_training_points=8,
        metamodel_verbose=True
    )
    
    # Run optimization
    print("\nRunning optimization with metamodel...")
    optimizer.run_optimization()
    
    # Get statistics
    stats = optimizer.get_metamodel_statistics()
    
    # Print results
    print(f"\nOptimization completed!")
    print(f"Best metric: {optimizer.best_metric:.6f}")
    print(f"Best parameters: x={optimizer.best_parameters['x']:.4f}, y={optimizer.best_parameters['y']:.4f}")
    print(f"\nMetamodel Statistics:")
    print(f"  Actual evaluations: {stats['n_actual_evaluations']}")
    print(f"  Metamodel predictions: {stats['n_metamodel_evaluations']}")
    print(f"  Total evaluations: {stats['total_evaluations']}")
    print(f"  Metamodel usage ratio: {stats['metamodel_usage_ratio']:.1%}")
    
    # Verify results
    assert optimizer.best_metric < 1.0, "Should find solution close to origin"
    assert stats['n_metamodel_evaluations'] > 0, "Should have used metamodel"
    assert stats['n_actual_evaluations'] > 0, "Should have done actual evaluations"
    
    print("\n[PASS] Basic metamodel test passed!")
    return optimizer, stats


def test_metamodel_strategies():
    """Test different acquisition strategies quickly."""
    print("\nTesting different acquisition strategies...")
    
    strategies = ['periodic', 'uncertainty', 'mixed']
    param_config = [
        {'name': 'x', 'min': -3.0, 'max': 3.0, 'default': 0.0},
        {'name': 'y', 'min': -3.0, 'max': 3.0, 'default': 0.0}
    ]
    
    for strategy in strategies:
        print(f"\n  Testing {strategy} strategy...")
        
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=simple_quadratic,
            parameters=Parameters(param_config),
            opt_min_or_max='min',
            pop_size=8,
            max_iterations=3,
            use_metamodel=True,
            metamodel_acquisition_strategy=strategy,
            metamodel_min_training_points=6,
            metamodel_validation_frequency=2,
            metamodel_verbose=False
        )
        
        optimizer.run_optimization()
        stats = optimizer.get_metamodel_statistics()
        
        print(f"    Best metric: {optimizer.best_metric:.6f}")
        print(f"    Actual evals: {stats['n_actual_evaluations']}, "
              f"Metamodel evals: {stats['n_metamodel_evaluations']}")
        
        assert optimizer.best_metric < 1.0, f"{strategy} should find good solution"
    
    print("\n[PASS] Strategy test passed!")


def test_no_metamodel_comparison():
    """Quick comparison with and without metamodel."""
    print("\nComparing with and without metamodel...")
    
    param_config = [
        {'name': 'x', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ]
    
    common_settings = {
        'seed': 42,
        'eval_func': simple_quadratic,
        'parameters': Parameters(param_config),
        'opt_min_or_max': 'min',
        'pop_size': 15,
        'max_iterations': 5
    }
    
    # Without metamodel
    opt_no_mm = DifferentialEvolution(
        **common_settings,
        use_metamodel=False
    )
    opt_no_mm.run_optimization()
    
    # With metamodel
    opt_with_mm = DifferentialEvolution(
        **common_settings,
        use_metamodel=True,
        metamodel_min_training_points=10,
        metamodel_verbose=False
    )
    opt_with_mm.run_optimization()
    
    stats = opt_with_mm.get_metamodel_statistics()
    
    print(f"\nWithout metamodel:")
    print(f"  Best metric: {opt_no_mm.best_metric:.6f}")
    print(f"  Total evaluations: {opt_no_mm.nr_evaluations}")
    
    print(f"\nWith metamodel:")
    print(f"  Best metric: {opt_with_mm.best_metric:.6f}")
    print(f"  Actual evaluations: {stats['n_actual_evaluations']}")
    print(f"  Metamodel predictions: {stats['n_metamodel_evaluations']}")
    
    # Both should find similar solutions
    assert abs(opt_no_mm.best_metric - opt_with_mm.best_metric) < 0.1
    # Metamodel should use fewer actual evaluations
    assert stats['n_actual_evaluations'] < opt_no_mm.nr_evaluations
    
    print("\n[PASS] Comparison test passed!")


def main():
    """Run all quick tests."""
    print("="*60)
    print("Quick Metamodel Integration Tests for DE")
    print("="*60)
    
    # Test 1: Basic functionality
    optimizer, stats = test_metamodel_basic()
    
    # Test 2: Different strategies
    test_metamodel_strategies()
    
    # Test 3: Comparison
    test_no_metamodel_comparison()
    
    print("\n" + "="*60)
    print("All quick tests passed successfully!")
    print("="*60)
    
    return optimizer, stats


if __name__ == "__main__":
    optimizer, stats = main()