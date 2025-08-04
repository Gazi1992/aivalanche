"""
Test Nelder-Mead optimizer with fixed parameters
"""

import os
import sys
import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from aivalanche_lib.optimization.nelder_mead import NelderMead
from aivalanche_lib.parameters import Parameters


def test_nelder_mead_with_fixed_params():
    """Test that Nelder-Mead properly handles fixed parameters."""
    print("\nTesting Nelder-Mead with Fixed Parameters")
    print("=" * 60)
    
    # Create parameters with one fixed
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 1.0, 'mode': 'fixed'},
        {'name': 'z', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ])
    
    print("\nParameter setup:")
    print(f"  Total parameters: {parameters.n_parameters}")
    print(f"  Variable parameters: {parameters.n_variable}")
    print(f"  Fixed parameters: {parameters.n_fixed}")
    print(f"  Variable names: {parameters.variable_names}")
    print(f"  Fixed names: {parameters.fixed_names}")
    
    # Simple objective function: (x-2)^2 + (y-3)^2 + (z-1)^2
    def eval_func(parameters, **kwargs):
        # Nelder-Mead expects one result per row in parameters DataFrame
        results = []
        for idx in range(len(parameters)):
            x = parameters['x'].iloc[idx]
            y = parameters['y'].iloc[idx]
            z = parameters['z'].iloc[idx]
            metric = (x - 2.0)**2 + (y - 3.0)**2 + (z - 1.0)**2
            results.append({'metric': metric})
        return results
    
    # Run Nelder-Mead optimization
    optimizer = NelderMead(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        max_iterations=100
    )
    
    print("\nOptimizer setup:")
    print(f"  nr_variable_parameters: {optimizer.nr_variable_parameters}")
    print(f"  variable_parameters_names: {optimizer.variable_parameters_names}")
    print(f"  simplex_size: {optimizer.simplex_size}")
    print(f"  simplex shape: {optimizer.simplex.shape}")
    
    # Check simplex dimensions
    expected_simplex_shape = (optimizer.nr_variable_parameters + 1, optimizer.nr_variable_parameters)
    if optimizer.simplex.shape != expected_simplex_shape:
        print(f"\n[ERROR] Simplex has wrong shape!")
        print(f"  Got: {optimizer.simplex.shape}")
        print(f"  Expected: {expected_simplex_shape}")
        return False
    
    # Run optimization
    print("\nRunning optimization...")
    optimizer.run_optimization()
    
    print(f"\nResults:")
    print(f"  Best metric: {optimizer.best_metric:.6f}")
    print(f"  Best parameters: {optimizer.best_parameters}")
    print(f"  Expected x ~= 2.0, got: {optimizer.best_parameters['x']:.4f}")
    print(f"  Expected y = 1.0 (fixed), got: {optimizer.best_parameters['y']:.4f}")
    print(f"  Expected z ~= 1.0, got: {optimizer.best_parameters['z']:.4f}")
    
    # Verify y remained fixed
    if abs(optimizer.best_parameters['y'] - 1.0) > 1e-6:
        print("\n[ERROR] Fixed parameter 'y' changed during optimization!")
        return False
    
    print("\n[SUCCESS] Nelder-Mead correctly handled fixed parameters!")
    return True


def test_nelder_mead_with_categorical():
    """Test that Nelder-Mead handles categorical parameters."""
    print("\n\nTesting Nelder-Mead with Categorical Parameters")
    print("=" * 60)
    
    # Create parameters with categorical
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'cat', 'type': 'categorical', 'values': ['A', 'B', 'C'], 'default': 'B'}
    ])
    
    print("\nParameter setup:")
    print(f"  Variable parameters: {parameters.variable_names}")
    print(f"  Fixed parameters: {parameters.fixed_names}")
    
    # Objective function
    def eval_func(parameters, **kwargs):
        results = []
        for idx in range(len(parameters)):
            x = parameters['x'].iloc[idx]
            cat = parameters['cat'].iloc[idx]
            # Different offset based on category
            offset = {'A': 0, 'B': 5, 'C': 10}[cat]
            metric = (x - 1.0)**2 + offset
            results.append({'metric': metric})
        return results
    
    try:
        optimizer = NelderMead(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            max_iterations=50
        )
        
        print("\nOptimizer setup:")
        print(f"  nr_variable_parameters: {optimizer.nr_variable_parameters}")
        print(f"  simplex shape: {optimizer.simplex.shape}")
        
        optimizer.run_optimization()
        
        print(f"\nResults:")
        print(f"  Best x: {optimizer.best_parameters['x']:.4f}")
        print(f"  Category: {optimizer.best_parameters['cat']}")
        
        print("\n[SUCCESS] Nelder-Mead handled categorical parameter!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Nelder-Mead failed with categorical parameter: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_nelder_mead_initial_simplex():
    """Test Nelder-Mead initial simplex generation with fixed params."""
    print("\n\nTesting Nelder-Mead Initial Simplex Generation")
    print("=" * 60)
    
    # Create mixed parameters
    parameters = Parameters([
        {'name': 'a', 'type': 'continuous', 'min': 0.0, 'max': 10.0, 'default': 5.0},
        {'name': 'b_fixed', 'type': 'continuous', 'min': 0.0, 'max': 10.0, 'default': 3.0, 'mode': 'fixed'},
        {'name': 'c', 'type': 'continuous', 'min': 0.0, 'max': 10.0, 'default': 7.0},
        {'name': 'd_cat', 'type': 'categorical', 'values': ['X', 'Y', 'Z'], 'default': 'Y'}
    ])
    
    def eval_func(parameters, **kwargs):
        # Return one result per row
        return [{'metric': 0.0} for _ in range(len(parameters))]
    
    # Test with custom initial simplex
    custom_simplex = pd.DataFrame([
        {'a': 2.0, 'b_fixed': 999.0, 'c': 3.0, 'd_cat': 'Z'},  # b_fixed should be ignored
        {'a': 8.0, 'b_fixed': 999.0, 'c': 7.0, 'd_cat': 'Z'},
        {'a': 5.0, 'b_fixed': 999.0, 'c': 9.0, 'd_cat': 'Z'},
        {'a': 4.0, 'b_fixed': 999.0, 'c': 1.0, 'd_cat': 'Z'}
    ])
    
    optimizer = NelderMead(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        initial_simplex=custom_simplex,
        max_iterations=1  # Just initialize
    )
    
    print("\nParameter setup:")
    print(f"  Variable parameters: {parameters.variable_names}")
    print(f"  Fixed parameters: {parameters.fixed_names}")
    
    print("\nSimplex check:")
    print(f"  Expected simplex vertices: {optimizer.nr_variable_parameters + 1}")
    print(f"  Expected dimensions: {optimizer.nr_variable_parameters}")
    print(f"  Actual simplex shape: {optimizer.simplex.shape}")
    
    # Initialize simplex
    optimizer._initialize_simplex()
    
    print("\nInitialized simplex (first vertex):")
    print(f"  Normalized values: {optimizer.simplex[0]}")
    
    # Denormalize to check
    simplex_df = pd.DataFrame(optimizer.simplex, columns=optimizer.variable_parameters_names)
    denorm = optimizer.parameters.unnorm_all(simplex_df)
    
    print("\nDenormalized first vertex:")
    print(f"  {denorm.iloc[0].to_dict()}")
    
    # Check that b_fixed has its default value, not 999
    if abs(denorm.iloc[0]['b_fixed'] - 3.0) > 1e-6:
        print(f"\n[ERROR] Fixed parameter not using default value!")
        print(f"  Expected b_fixed = 3.0, got {denorm.iloc[0]['b_fixed']}")
        return False
    
    print("\n[SUCCESS] Initial simplex correctly handled fixed parameters!")
    return True


if __name__ == "__main__":
    success1 = test_nelder_mead_with_fixed_params()
    success2 = test_nelder_mead_with_categorical()
    success3 = test_nelder_mead_initial_simplex()
    
    if success1 and success2 and success3:
        print("\n[DONE] All tests passed!")
    else:
        print("\n[FAILED] Some tests failed!")