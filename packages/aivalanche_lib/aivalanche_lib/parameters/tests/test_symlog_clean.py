"""
Test the clean symlog transform integration in the Parameters module.
"""

import numpy as np
import pandas as pd
from aivalanche_lib.parameters import Parameters


def test_symlog_basic():
    """Test basic symlog functionality."""
    print("\n" + "="*60)
    print("TEST: Basic Symlog Transform")
    print("="*60)
    
    # Define parameter with mixed sign range
    param_config = [{
        'name': 'momentum',
        'type': 'continuous',
        'min': -100,
        'max': 100,
        'default': 0,
        'scale': 'log'  # Will automatically use symlog due to mixed signs
    }]
    
    params = Parameters(param_config)
    
    # Check that symlog transform was applied
    print("\nOriginal parameters:")
    print(params.all_parameters[['name', 'type', 'min', 'max', 'default', 'scale', 'transform']])
    
    print("\nScaled parameters:")
    print(params.all_parameters_scaled[['name', 'min', 'max', 'default', 'transform']])
    
    print("\nNormalized parameters:")
    print(params.all_parameters_normed[['name', 'min', 'max', 'default']])
    
    # Test random value generation
    print("\nRandom value generation (5 samples):")
    for i in range(5):
        random_params = params.generate_random_parameters()
        print(f"  Sample {i+1}: momentum = {random_params['momentum']:.3f}")

    # Test round-trip transformation
    print("\nRound-trip test:")
    test_values = [-100, -10, -1, 0, 1, 10, 100]
    print(f"{'Original':>10} -> {'Recovered':>10} | {'Error':>10}")
    print("-"*40)
    
    for val in test_values:
        # Forward transform
        test_df = pd.DataFrame([{'momentum': val}])
        normalized_df = params.scale_and_normalize_parameters_array(test_df)
        
        # Inverse transform
        recovered_df = params.denormalize_and_descale_parameters_array(normalized_df)
        recovered_val = recovered_df['momentum'].iloc[0]
        
        error = abs(val - recovered_val)
        print(f"{val:10.3f} -> {recovered_val:10.3f} | {error:10.2e}")


def test_transform_comparison():
    """Compare different parameter transforms."""
    print("\n" + "="*60)
    print("TEST: Transform Comparison")
    print("="*60)
    
    param_configs = [
        {
            'name': 'positive_only',
            'type': 'continuous',
            'min': 0.01,
            'max': 100,
            'default': 1,
            'scale': 'log'
        },
        {
            'name': 'negative_only',
            'type': 'continuous',
            'min': -100,
            'max': -0.01,
            'default': -1,
            'scale': 'log'
        },
        {
            'name': 'mixed_sign',
            'type': 'continuous',
            'min': -100,
            'max': 100,
            'default': 0,
            'scale': 'log'
        }
    ]
    
    params = Parameters(param_configs)
    
    print("\nTransform assignments:")
    for _, row in params.all_parameters.iterrows():
        print(f"{row['name']:15s}: transform = {row['transform']}")


if __name__ == "__main__":
    print("="*60)
    print("CLEAN SYMLOG TRANSFORM INTEGRATION TESTS")
    print("="*60)
    
    test_symlog_basic()
    test_transform_comparison()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)