"""Debug symlog transform issue."""

import numpy as np

SYMLOG_THRESHOLD = 1e-6

def test_symlog_transform():
    """Test symlog transform and inverse."""
    test_values = [-100, -10, -1, 0, 1, 10, 100]
    
    print("Testing symlog transform:")
    print(f"SYMLOG_THRESHOLD = {SYMLOG_THRESHOLD}")
    print("-" * 80)
    print(f"{'Original':>15} -> {'Scaled':>15} -> {'Recovered':>15} | {'Error':>15}")
    print("-" * 80)
    
    for val in test_values:
        # Forward transform (scale)
        scaled = np.sign(val) * np.log10(1 + np.abs(val) / SYMLOG_THRESHOLD)
        
        # Inverse transform (descale)
        recovered = np.sign(scaled) * SYMLOG_THRESHOLD * (10**np.abs(scaled) - 1)
        
        error = abs(val - recovered)
        print(f"{val:15.6f} -> {scaled:15.6f} -> {recovered:15.6f} | {error:15.2e}")
    
    print("\nDetailed analysis for value -10:")
    val = -10
    print(f"Original value: {val}")
    
    # Step by step forward transform
    abs_val = np.abs(val)
    print(f"abs(val) = {abs_val}")
    
    ratio = abs_val / SYMLOG_THRESHOLD
    print(f"abs(val) / threshold = {ratio}")
    
    log_arg = 1 + ratio
    print(f"1 + ratio = {log_arg}")
    
    log_result = np.log10(log_arg)
    print(f"log10(1 + ratio) = {log_result}")
    
    scaled = np.sign(val) * log_result
    print(f"sign(val) * log10(1 + ratio) = {scaled}")
    
    # Step by step inverse transform
    print("\nInverse transform:")
    abs_scaled = np.abs(scaled)
    print(f"abs(scaled) = {abs_scaled}")
    
    exp_result = 10**abs_scaled
    print(f"10^abs(scaled) = {exp_result}")
    
    minus_one = exp_result - 1
    print(f"10^abs(scaled) - 1 = {minus_one}")
    
    mult_threshold = SYMLOG_THRESHOLD * minus_one
    print(f"threshold * (10^abs(scaled) - 1) = {mult_threshold}")
    
    recovered = np.sign(scaled) * mult_threshold
    print(f"sign(scaled) * threshold * (10^abs(scaled) - 1) = {recovered}")
    
    print(f"\nError: {abs(val - recovered)}")

if __name__ == "__main__":
    test_symlog_transform()