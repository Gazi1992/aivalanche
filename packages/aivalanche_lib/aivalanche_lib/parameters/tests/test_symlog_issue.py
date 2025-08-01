"""Debug the specific symlog issue in test_symlog_clean."""

import numpy as np
import pandas as pd
from aivalanche_lib.parameters import Parameters

def test_symlog_issue():
    """Reproduce and debug the exact issue from test_symlog_clean."""
    
    # Define exactly the same parameter as in test_symlog_clean
    param_config = [{
        'name': 'momentum',
        'type': 'continuous',
        'min': -100,
        'max': 100,
        'default': 0,
        'scale': 'log'  # Will automatically use symlog due to mixed signs
    }]
    
    params = Parameters(param_config)
    
    print("Parameter info:")
    print(params.all_parameters[['name', 'type', 'min', 'max', 'default', 'scale', 'transform']])
    print("\nScaled info:")
    print(params.all_parameters_scaled[['name', 'min', 'max', 'default', 'transform']])
    print("\nNormalized info:")
    print(params.all_parameters_normed[['name', 'min', 'max', 'default']])
    
    # Test specific value: -10
    val = -10
    print(f"\nTesting value: {val}")
    
    # Create dataframe
    test_df = pd.DataFrame([{'momentum': val}])
    print(f"Input dataframe: {test_df}")
    
    # Scale and normalize
    normalized_df = params.scale_and_normalize_parameters_array(test_df)
    print(f"Normalized dataframe: {normalized_df}")
    print(f"Normalized value: {normalized_df['momentum'].iloc[0]:.10f}")
    
    # Denormalize and descale
    recovered_df = params.denormalize_and_descale_parameters_array(normalized_df)
    print(f"Recovered dataframe: {recovered_df}")
    print(f"Recovered value: {recovered_df['momentum'].iloc[0]:.10f}")
    
    # Let's trace through the steps manually
    print("\nManual calculation:")
    
    # Get the scaled min/max
    scaled_info = params.all_parameters_scaled[params.all_parameters_scaled['name'] == 'momentum'].iloc[0]
    min_scaled = scaled_info['min']
    max_scaled = scaled_info['max']
    
    print(f"Scaled min: {min_scaled}")
    print(f"Scaled max: {max_scaled}")
    
    # Step 1: Scale the value
    from aivalanche_lib.parameters.scale_norm import SYMLOG_THRESHOLD
    scaled_val = np.sign(val) * np.log10(1 + np.abs(val) / SYMLOG_THRESHOLD)
    print(f"Scaled value: {scaled_val:.10f}")
    
    # Step 2: Normalize
    normalized_val = (scaled_val - min_scaled) / (max_scaled - min_scaled)
    print(f"Normalized value (manual): {normalized_val:.10f}")
    
    # Check if there's a precision issue
    print(f"\nPrecision check:")
    print(f"scaled_val == -7.0? {scaled_val == -7.0}")
    print(f"min_scaled == -8.0? {min_scaled == -8.0}")
    print(f"max_scaled == 8.0? {max_scaled == 8.0}")
    
    # Test the full range
    print("\nFull range test:")
    test_values = [-100, -10, -1, 0, 1, 10, 100]
    for test_val in test_values:
        test_df = pd.DataFrame([{'momentum': test_val}])
        norm_df = params.scale_and_normalize_parameters_array(test_df)
        recov_df = params.denormalize_and_descale_parameters_array(norm_df)
        
        norm_val = norm_df['momentum'].iloc[0]
        recov_val = recov_df['momentum'].iloc[0]
        error = abs(test_val - recov_val)
        
        print(f"{test_val:8.1f} -> norm: {norm_val:8.6f} -> recovered: {recov_val:8.1f} (error: {error:.2e})")

if __name__ == "__main__":
    test_symlog_issue()