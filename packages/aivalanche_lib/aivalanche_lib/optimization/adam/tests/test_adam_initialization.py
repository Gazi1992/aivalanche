"""
Test Adam initialization behavior with fixed parameters
"""

import os
import sys
import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from aivalanche_lib.optimization.adam import Adam
from aivalanche_lib.parameters import Parameters


def test_initialization_details():
    """Test Adam initialization in detail."""
    print("\nTesting Adam Initialization Details")
    print("=" * 60)
    
    # Create parameters with mixed types
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 1.0},
        {'name': 'y_fixed', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 2.0, 'mode': 'fixed'},
        {'name': 'z', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 3.0},
        {'name': 'cat', 'type': 'categorical', 'values': ['A', 'B', 'C'], 'default': 'B'}
    ])
    
    print("\nParameter setup:")
    print(f"  All names: {parameters.names}")
    print(f"  Variable names: {parameters.variable_names}")
    print(f"  Fixed names: {parameters.fixed_names}")
    
    # Test normalization
    test_df = pd.DataFrame([{
        'x': 0.0,  # Should normalize to 0.5
        'y_fixed': 2.0,  # Fixed
        'z': -5.0,  # Should normalize to 0.0
        'cat': 'A'  # Categorical
    }])
    
    print("\n\nTest DataFrame:")
    print(test_df)
    
    normalized = parameters.norm_all(test_df)
    print("\n\nNormalized result:")
    print(normalized)
    print(f"Type: {type(normalized)}")
    print(f"Shape: {normalized.shape if hasattr(normalized, 'shape') else 'N/A'}")
    
    # Create Adam optimizer
    def eval_func(parameters, **kwargs):
        return [{'metric': 0.0}]
    
    optimizer = Adam(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        use_defaults_in_initial_point=True
    )
    
    print("\n\nAdam initialization:")
    print(f"  nr_parameters: {optimizer.nr_parameters}")
    print(f"  nr_variable_parameters: {optimizer.nr_variable_parameters}")
    print(f"  variable_parameters_names: {optimizer.variable_parameters_names}")
    
    # Initialize starting point
    optimizer._initialize_starting_point()
    
    print(f"\n  current_point: {optimizer.current_point}")
    print(f"  current_point shape: {optimizer.current_point.shape}")
    
    # Check what happens with initial point normalization
    print("\n\nDetailed initialization check:")
    
    # Create initial dict with defaults for variable params only
    default_dict = {}
    for param_name in optimizer.variable_parameters_names:
        param = optimizer.parameters.get_parameter(param_name)
        default_dict[param_name] = param.default
        print(f"  {param_name}: default = {param.default}")
    
    print(f"\nDefault dict for variable params: {default_dict}")
    
    params_df = pd.DataFrame([default_dict])
    print(f"\nParams DataFrame:")
    print(params_df)
    
    normalized = optimizer.parameters.norm_all(params_df)
    print(f"\nNormalized DataFrame:")
    print(normalized)
    
    # Test with explicit initial point
    print("\n\nTest with explicit initial point:")
    initial_df = pd.DataFrame([{
        'x': 2.5,
        'y_fixed': 999.0,  # Should be ignored
        'z': 0.0,
        'cat': 'C'  # Should be used as fixed default
    }])
    
    optimizer2 = Adam(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        initial_point=initial_df
    )
    
    optimizer2._initialize_starting_point()
    print(f"  current_point: {optimizer2.current_point}")
    print(f"  current_point shape: {optimizer2.current_point.shape}")


if __name__ == "__main__":
    test_initialization_details()
    print("\n[DONE] Test completed!")