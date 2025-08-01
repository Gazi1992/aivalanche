"""Debug symlog normalization issue."""

import numpy as np
from aivalanche_lib.parameters.scale_norm import (
    SYMLOG_THRESHOLD,
    normalize_parameter_value,
    denormalize_parameter_value
)

def test_symlog_normalization():
    """Test normalization step for symlog."""
    
    print("SYMLOG NORMALIZATION DEBUG")
    print("="*80)
    
    # Original range: -100 to 100
    min_orig = -100
    max_orig = 100
    
    # Scaled range (after symlog transform)
    min_scaled = np.sign(min_orig) * np.log10(1 + np.abs(min_orig) / SYMLOG_THRESHOLD)
    max_scaled = np.sign(max_orig) * np.log10(1 + np.abs(max_orig) / SYMLOG_THRESHOLD)
    
    print(f"Original range: [{min_orig}, {max_orig}]")
    print(f"Scaled range: [{min_scaled:.6f}, {max_scaled:.6f}]")
    
    # Test values
    test_values = [-100, -10, -1, 0, 1, 10, 100]
    
    print("\nFull pipeline:")
    print(f"{'Original':>12} -> {'Scaled':>12} -> {'Normalized':>12} -> {'Denorm':>12} -> {'Descaled':>12}")
    print("-"*80)
    
    for val in test_values:
        # Step 1: Scale (symlog transform)
        scaled = np.sign(val) * np.log10(1 + np.abs(val) / SYMLOG_THRESHOLD)
        
        # Step 2: Normalize to [0, 1]
        normalized = normalize_parameter_value(scaled, min_scaled, max_scaled)
        
        # Step 3: Denormalize back to scaled space
        denorm = denormalize_parameter_value(normalized, min_scaled, max_scaled)
        
        # Step 4: Descale (inverse symlog)
        descaled = np.sign(denorm) * SYMLOG_THRESHOLD * (10**np.abs(denorm) - 1)
        
        print(f"{val:12.3f} -> {scaled:12.6f} -> {normalized:12.6f} -> {denorm:12.6f} -> {descaled:12.3f}")
    
    # Detailed analysis for -10
    print("\nDetailed analysis for value -10:")
    val = -10
    scaled = np.sign(val) * np.log10(1 + np.abs(val) / SYMLOG_THRESHOLD)
    print(f"Original: {val}")
    print(f"Scaled: {scaled:.10f}")
    print(f"Min scaled: {min_scaled:.10f}")
    print(f"Max scaled: {max_scaled:.10f}")
    
    # Manual normalization calculation
    range_scaled = max_scaled - min_scaled
    print(f"Scaled range: {range_scaled:.10f}")
    
    offset_from_min = scaled - min_scaled
    print(f"Offset from min: {offset_from_min:.10f}")
    
    normalized_manual = offset_from_min / range_scaled
    print(f"Normalized (manual): {normalized_manual:.10f}")
    
    normalized_func = normalize_parameter_value(scaled, min_scaled, max_scaled)
    print(f"Normalized (function): {normalized_func:.10f}")
    
    # Check why it might be clamped to 0
    print(f"\nIs scaled < min_scaled? {scaled < min_scaled}")
    print(f"Difference: {scaled - min_scaled}")

if __name__ == "__main__":
    test_symlog_normalization()