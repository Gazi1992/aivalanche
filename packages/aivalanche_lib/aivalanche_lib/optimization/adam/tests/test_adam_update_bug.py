"""
Test potential bug in Adam with fixed parameters
"""

import os
import sys
import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from aivalanche_lib.optimization.adam import Adam
from aivalanche_lib.parameters import Parameters


def test_update_dimension_mismatch():
    """Test if Adam fails with dimension mismatch."""
    print("\nTesting Adam Update Dimension Issue")
    print("=" * 60)
    
    # Create parameters with fixed
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y_fixed', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 1.0, 'mode': 'fixed'},
        {'name': 'z', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ])
    
    def eval_func(parameters, **kwargs):
        x = parameters['x'].iloc[0]
        z = parameters['z'].iloc[0]
        metric = x**2 + z**2
        return [{'metric': metric}]
    
    optimizer = Adam(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        max_iterations=5,  # Just a few iterations
        learning_rate=0.1
    )
    
    print("\nBefore optimization:")
    print(f"  nr_variable_parameters: {optimizer.nr_variable_parameters}")
    print(f"  gradient shape will be: ({optimizer.nr_variable_parameters},)")
    
    # Initialize
    optimizer._initialize_starting_point()
    print(f"  current_point shape: {optimizer.current_point.shape}")
    
    if optimizer.current_point.shape[0] != optimizer.nr_variable_parameters:
        print(f"\n[WARNING] Dimension mismatch detected!")
        print(f"  current_point has {optimizer.current_point.shape[0]} elements")
        print(f"  but only {optimizer.nr_variable_parameters} are variable")
        print("\nThis could cause issues during update!")
    
    try:
        print("\nRunning optimization...")
        optimizer.run_optimization()
        print("\n[SUCCESS] Optimization completed without errors")
        
    except Exception as e:
        print(f"\n[ERROR] Optimization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    test_update_dimension_mismatch()
    print("\n[DONE] Test completed!")