"""Test all transform types including NO transform."""

import numpy as np
import pandas as pd
from aivalanche_lib.parameters import Parameters


def test_all_transforms():
    """Test all transform types with detailed output."""
    
    # Define parameters with different transform types
    param_configs = [
        {
            'name': 'no_transform',
            'type': 'continuous',
            'min': -100,
            'max': 100,
            'default': 0,
            'scale': 'lin'  # Linear scale = no transform
        },
        {
            'name': 'log_positive',
            'type': 'continuous',
            'min': 0.01,
            'max': 100,
            'default': 1,
            'scale': 'log'  # Will use log transform
        },
        {
            'name': 'log_negative',
            'type': 'continuous',
            'min': -100,
            'max': -0.01,
            'default': -1,
            'scale': 'log'  # Will use neglog transform
        },
        {
            'name': 'symlog_mixed',
            'type': 'continuous',
            'min': -100,
            'max': 100,
            'default': 0,
            'scale': 'log'  # Will use symlog transform
        }
    ]
    
    params = Parameters(param_configs)
    
    print("="*80)
    print("PARAMETER TRANSFORM TEST")
    print("="*80)
    
    # Display transform assignments
    print("\nTransform assignments:")
    print(params.all_parameters[['name', 'type', 'min', 'max', 'default', 'scale', 'transform']])
    
    print("\nScaled parameters:")
    print(params.all_parameters_scaled[['name', 'min', 'max', 'default', 'transform']])
    
    print("\nNormalized parameters:")
    print(params.all_parameters_normed[['name', 'min', 'max', 'default']])
    
    # Test round-trip for each parameter
    print("\n" + "="*80)
    print("ROUND-TRIP TESTS")
    print("="*80)
    
    for param_name in params.all_parameters['name']:
        param_info = params.all_parameters[params.all_parameters['name'] == param_name].iloc[0]
        transform = param_info['transform']
        
        print(f"\nParameter: {param_name} (transform: {transform})")
        print("-"*60)
        
        # Get min/max for test values
        min_val = param_info['min']
        max_val = param_info['max']
        default_val = param_info['default']
        
        # Create test values
        if min_val < 0 and max_val > 0:
            # Mixed sign range
            test_values = [min_val, min_val/10, min_val/100, default_val, max_val/100, max_val/10, max_val]
        elif min_val > 0:
            # Positive only
            test_values = [min_val, min_val*10, default_val, max_val/10, max_val]
        else:
            # Negative only
            test_values = [min_val, min_val/10, default_val, max_val/10, max_val]
        
        print(f"{'Original':>15} -> {'Normalized':>15} -> {'Recovered':>15} | {'Error':>15} | {'Rel Error %':>12}")
        print("-"*90)
        
        for val in test_values:
            # Create single-row dataframe
            test_df = pd.DataFrame([{param_name: val}])
            
            # Forward transform: scale and normalize
            normalized_df = params.scale_and_normalize_parameters_array(test_df)
            norm_val = normalized_df[param_name].iloc[0]
            
            # Inverse transform: denormalize and descale
            recovered_df = params.denormalize_and_descale_parameters_array(normalized_df)
            recovered_val = recovered_df[param_name].iloc[0]
            
            # Calculate errors
            abs_error = abs(val - recovered_val)
            rel_error = abs_error / abs(val) * 100 if val != 0 else 0
            
            print(f"{val:15.6f} -> {norm_val:15.6f} -> {recovered_val:15.6f} | {abs_error:15.2e} | {rel_error:12.2e}%")
    
    # Test edge cases
    print("\n" + "="*80)
    print("EDGE CASE TESTS")
    print("="*80)
    
    # Test with multiple parameters at once
    print("\nMultiple parameters at once:")
    test_data = {
        'no_transform': 50,
        'log_positive': 10,
        'log_negative': -10,
        'symlog_mixed': -10
    }
    
    test_df = pd.DataFrame([test_data])
    print("\nOriginal values:")
    print(test_df)
    
    normalized_df = params.scale_and_normalize_parameters_array(test_df)
    print("\nNormalized values:")
    print(normalized_df)
    
    recovered_df = params.denormalize_and_descale_parameters_array(normalized_df)
    print("\nRecovered values:")
    print(recovered_df)
    
    print("\nErrors:")
    for col in test_data.keys():
        error = abs(test_data[col] - recovered_df[col].iloc[0])
        rel_error = error / abs(test_data[col]) * 100 if test_data[col] != 0 else 0
        print(f"{col}: {error:.2e} ({rel_error:.2e}%)")


def test_discrete_params():
    """Test discrete parameters with different scales."""
    print("\n" + "="*80)
    print("DISCRETE PARAMETER TESTS")
    print("="*80)
    
    param_configs = [
        {
            'name': 'discrete_linear',
            'type': 'discrete',
            'min': -10,
            'max': 10,
            'step': 1,
            'default': 0,
            'scale': 'lin'
        },
        {
            'name': 'discrete_log',
            'type': 'discrete',
            'min': 1,
            'max': 100,
            'step': 1,
            'default': 10,
            'scale': 'log'
        },
        {
            'name': 'discrete_list',
            'type': 'discrete',
            'values': [0.1, 0.5, 1.0, 5.0, 10.0],
            'default': 1.0,
            'scale': 'lin'
        }
    ]
    
    params = Parameters(param_configs)
    
    print("\nParameter definitions:")
    print(params.all_parameters[['name', 'type', 'min', 'max', 'step', 'values', 'default', 'scale', 'transform']])
    
    # Test round-trip
    for param_name in params.all_parameters['name']:
        print(f"\nTesting {param_name}:")
        
        # Generate some random values
        for i in range(5):
            random_params = params.generate_random_parameters()
            val = random_params[param_name]
            
            # Round-trip test
            test_df = pd.DataFrame([{param_name: val}])
            normalized_df = params.scale_and_normalize_parameters_array(test_df)
            recovered_df = params.denormalize_and_descale_parameters_array(normalized_df)
            recovered_val = recovered_df[param_name].iloc[0]
            
            error = abs(val - recovered_val) if not pd.isna(val) and not pd.isna(recovered_val) else float('nan')
            print(f"  Random {i+1}: {val} -> {recovered_val} (error: {error:.2e})")


def test_categorical_params():
    """Test categorical parameters."""
    print("\n" + "="*80)
    print("CATEGORICAL PARAMETER TESTS")
    print("="*80)
    
    param_configs = [
        {
            'name': 'optimizer',
            'type': 'categorical',
            'values': ['adam', 'sgd', 'rmsprop', 'adagrad'],
            'default': 'adam'
        },
        {
            'name': 'activation',
            'type': 'categorical',
            'values': ['relu', 'tanh', 'sigmoid', None],
            'default': 'relu'
        }
    ]
    
    params = Parameters(param_configs)
    
    print("\nParameter definitions:")
    print(params.all_parameters[['name', 'type', 'values', 'default']])
    
    print("\nScaled (indexed) parameters:")
    print(params.all_parameters_scaled[['name', 'min', 'max', 'default']])
    
    # Test all values
    for param_name in params.all_parameters['name']:
        param_info = params.all_parameters[params.all_parameters['name'] == param_name].iloc[0]
        values = param_info['values']
        
        print(f"\nTesting {param_name}:")
        for val in values:
            test_df = pd.DataFrame([{param_name: val}])
            normalized_df = params.scale_and_normalize_parameters_array(test_df)
            recovered_df = params.denormalize_and_descale_parameters_array(normalized_df)
            recovered_val = recovered_df[param_name].iloc[0]
            
            match = "OK" if val == recovered_val else "FAIL"
            print(f"  {str(val):10} -> {str(recovered_val):10} [{match}]")


if __name__ == "__main__":
    test_all_transforms()
    test_discrete_params()
    test_categorical_params()