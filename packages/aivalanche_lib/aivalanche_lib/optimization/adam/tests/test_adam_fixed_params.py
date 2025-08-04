"""
Test Adam optimizer with fixed parameters
"""

import os
import sys
import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from aivalanche_lib.optimization.adam import Adam
from aivalanche_lib.parameters import Parameters


def test_adam_with_fixed_params():
    """Test that Adam properly handles fixed parameters."""
    print("\nTesting Adam with Fixed Parameters")
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
        x = parameters['x'].iloc[0]
        y = parameters['y'].iloc[0]
        z = parameters['z'].iloc[0]
        metric = (x - 2.0)**2 + (y - 3.0)**2 + (z - 1.0)**2
        return [{'metric': metric}]
    
    # Run Adam optimization
    optimizer = Adam(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        max_iterations=100,
        learning_rate=0.1
    )
    
    print("\nOptimizer setup:")
    print(f"  nr_variable_parameters: {optimizer.nr_variable_parameters}")
    print(f"  variable_parameters_names: {optimizer.variable_parameters_names}")
    
    # Check initial point dimension
    optimizer._initialize_starting_point()
    print(f"\nInitial point shape: {optimizer.current_point.shape}")
    print(f"Expected shape: ({optimizer.nr_variable_parameters},)")
    
    if optimizer.current_point.shape[0] != optimizer.nr_variable_parameters:
        print("\n[ERROR] Initial point has wrong dimension!")
        print(f"Got {optimizer.current_point.shape[0]}, expected {optimizer.nr_variable_parameters}")
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
    
    print("\n[SUCCESS] Adam correctly handled fixed parameters!")
    return True


def test_adam_with_categorical():
    """Test that Adam handles categorical parameters."""
    print("\n\nTesting Adam with Categorical Parameters")
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
        x = parameters['x'].iloc[0]
        cat = parameters['cat'].iloc[0]
        # Different offset based on category
        offset = {'A': 0, 'B': 5, 'C': 10}[cat]
        metric = (x - 1.0)**2 + offset
        return [{'metric': metric}]
    
    try:
        optimizer = Adam(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            max_iterations=50
        )
        
        print("\nInitializing...")
        optimizer._initialize_starting_point()
        
        print(f"Initial point shape: {optimizer.current_point.shape}")
        print(f"Expected shape: ({optimizer.nr_variable_parameters},)")
        
        optimizer.run_optimization()
        
        print(f"\nResults:")
        print(f"  Best x: {optimizer.best_parameters['x']:.4f}")
        print(f"  Category: {optimizer.best_parameters['cat']}")
        
        print("\n[SUCCESS] Adam handled categorical parameter!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Adam failed with categorical parameter: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success1 = test_adam_with_fixed_params()
    success2 = test_adam_with_categorical()
    
    if success1 and success2:
        print("\n[DONE] All tests passed!")
    else:
        print("\n[FAILED] Some tests failed!")