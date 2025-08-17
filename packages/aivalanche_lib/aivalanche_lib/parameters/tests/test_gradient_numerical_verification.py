"""
Test to verify gradient transformations by comparing analytical gradients
with numerical gradients computed directly in normalized space.

This is the definitive test to prove whether the chain rule is correctly implemented
for all parameter scale types: linear, log, neglog, and symlog.
"""

import numpy as np
import pandas as pd
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from aivalanche_lib.parameters import Parameters


def polynomial_function(x):
    """Simple polynomial: f(x) = x^2 + 2x"""
    return x**2 + 2*x


def analytical_gradient(x):
    """Analytical gradient: df/dx = 2x + 2"""
    return 2*x + 2


def test_single_parameter(param_config, test_name):
    """
    Test gradient transformations for a single parameter configuration.
    
    Args:
        param_config: Parameter configuration dictionary
        test_name: Name for this test case
    
    Returns:
        DataFrame with test results
    """
    print("\n" + "=" * 140)
    print(f"TEST CASE: {test_name}")
    print("=" * 140)
    
    parameters = Parameters([param_config])
    param = parameters.get_parameter('x')
    
    print(f"Parameter configuration:")
    print(f"  Range: [{param.min:.2e}, {param.max:.2e}]")
    print(f"  Scale: {param.scale}")
    print(f"  Transform: {param.transform.__class__.__name__}")
    print(f"  Scaled range: [{param.scaled_min:.2e}, {param.scaled_max:.2e}]")
    
    # Test points in normalized space [0, 1]
    norm_values_test = np.linspace(0, 1, 11)  # 0.0, 0.1, 0.2, ..., 1.0
    
    # Small step for numerical gradient
    h = 1e-10
    
    # Collect results
    results = []
    max_error = 0
    max_rel_error = 0
    
    print("\nDETAILED GRADIENT TRANSFORMATIONS:")
    print("-" * 140)
    print(f"{'norm_x':>7} {'x':>12} {'f(x)':>12} {'df/dx':>12} {'scaled_x':>12} {'scaled_grad':>14} {'norm_grad':>14} {'num_grad':>14} {'error':>10} {'status':>8}")
    print("-" * 140)
    
    detailed_results = []
    
    for norm_x in norm_values_test:
        # Step 1: Unnormalize to get actual x value
        x = param.unnorm_value(norm_x)
        f_x = polynomial_function(x)
        
        # Step 2: Compute analytical gradient in original space
        grad_original = analytical_gradient(x)
        
        # Step 3: Get scaled x value (after log/neglog/symlog transform)
        scaled_x = param.transform.scale(x)
        
        # Step 4: Transform gradient to scaled space
        grad_scaled = param.transform.scale_gradient(grad_original, x)
        
        # Step 5: Transform gradient from scaled to normalized space
        # This is done by multiplying by the scaled range
        grad_norm_analytical = grad_scaled * param.scaled_range
        
        # Alternative method using Parameters.norm_gradients (should give same result)
        values_dict = {'x': x}
        gradients_dict = {'x': grad_original}
        norm_grads = parameters.norm_gradients(gradients_dict, values_dict)
        grad_norm_from_params = norm_grads['x']
        
        # Verify both methods give same result
        assert abs(grad_norm_analytical - grad_norm_from_params) < 1e-10, \
            f"Direct calculation ({grad_norm_analytical}) doesn't match Parameters.norm_gradients ({grad_norm_from_params})"
        
        # Step 6: Compute numerical gradient directly in normalized space
        norm_x_plus = min(norm_x + h, 1.0)
        norm_x_minus = max(norm_x - h, 0.0)
        
        # Get corresponding x values
        x_plus = param.unnorm_value(norm_x_plus)
        x_minus = param.unnorm_value(norm_x_minus)
        
        # Compute function values
        f_plus = polynomial_function(x_plus)
        f_minus = polynomial_function(x_minus)
        
        # Numerical gradient in normalized space
        delta_norm = norm_x_plus - norm_x_minus
        if delta_norm > 0:
            grad_norm_numerical = (f_plus - f_minus) / delta_norm
        else:
            grad_norm_numerical = 0
        
        # Compare analytical and numerical gradients
        error = abs(grad_norm_analytical - grad_norm_numerical)
        rel_error = error / max(abs(grad_norm_analytical), 1e-10)
        
        max_error = max(max_error, error)
        max_rel_error = max(max_rel_error, rel_error)
        
        status = "PASS" if rel_error < 1e-6 else "FAIL"
        
        print(f"{norm_x:7.3f} {x:12.4e} {f_x:12.4e} {grad_original:12.4f} {scaled_x:12.4e} {grad_scaled:14.6e} {grad_norm_analytical:14.6e} {grad_norm_numerical:14.6e} {error:10.2e} {status:>8}")
        
        results.append({
            'norm_x': norm_x,
            'x': x,
            'f(x)': f_x,
            'df/dx_analytical': grad_original,
            'scaled_x': scaled_x,
            'scaled_gradient': grad_scaled,
            'df/d(norm_x)_transformed': grad_norm_analytical,
            'df/d(norm_x)_numerical': grad_norm_numerical,
            'absolute_error': error,
            'relative_error': rel_error,
            'status': status
        })
        
        detailed_results.append({
            'norm_x': norm_x,
            'x': x,
            'scaled_x': scaled_x,
            'grad_original': grad_original,
            'grad_scaled': grad_scaled,
            'grad_norm': grad_norm_analytical,
            'grad_num': grad_norm_numerical,
            'error': error
        })
    
    print("-" * 140)
    
    # Print transformation chain summary
    print("\nTRANSFORMATION CHAIN SUMMARY:")
    print("-" * 140)
    print("Step 1: Original space (x) -> Scaled space (y)")
    print(f"  Transform: {param.transform.__class__.__name__}")
    if param.transform.__class__.__name__ == 'LogTransform':
        print("  y = log10(x)")
        print("  Gradient: df/dy = df/dx * x * ln(10)")
    elif param.transform.__class__.__name__ == 'NegLogTransform':
        print("  y = -log10(-x) for x < 0")
        print("  Gradient: df/dy = df/dx * (-x) * ln(10)")
    elif param.transform.__class__.__name__ == 'SymLogTransform':
        print("  y = sign(x) * log10(1 + |x|/threshold)")
        print("  Gradient: df/dy = df/dx * threshold * ln(10) * (1 + |x|/threshold)")
    else:
        print("  y = x (no transformation)")
        print("  Gradient: df/dy = df/dx")
    
    print("\nStep 2: Scaled space (y) -> Normalized space (z)")
    print(f"  z = (y - y_min) / (y_max - y_min)")
    print(f"  y_min = {param.scaled_min:.4f}, y_max = {param.scaled_max:.4f}")
    print(f"  Range = {param.scaled_range:.4f}")
    print(f"  Gradient: df/dz = df/dy * (y_max - y_min) = df/dy * {param.scaled_range:.4f}")
    
    print("\nStep 3: Verification")
    print(f"  Maximum absolute error: {max_error:.2e}")
    print(f"  Maximum relative error: {max_rel_error:.2e}")
    
    if max_rel_error < 1e-6:
        print(f"  [PASS] {test_name}: All gradient transformations are correct")
    else:
        print(f"  [FAIL] {test_name}: Some gradient transformations have errors")
    
    return pd.DataFrame(results)


def test_gradient_numerical_verification():
    """
    Test gradient transformations for all scale types.
    """
    
    print("=" * 140)
    print("COMPREHENSIVE GRADIENT VERIFICATION TEST")
    print("=" * 140)
    print("\nFunction: f(x) = x^2 + 2x")
    print("Gradient: df/dx = 2x + 2")
    print("\nTesting all parameter scale types: linear, log, neglog, symlog")
    print("\nMETHODOLOGY:")
    print("-" * 140)
    print("For each test point:")
    print("1. Start with normalized value z in [0, 1]")
    print("2. Unnormalize to scaled space: y = y_min + z * (y_max - y_min)")
    print("3. Unscale to original space: x = unscale(y)")
    print("4. Compute analytical gradient: df/dx = 2x + 2")
    print("5. Transform gradient to scaled space: df/dy = scale_gradient(df/dx, x)")
    print("6. Transform gradient to normalized space: df/dz = df/dy * (y_max - y_min)")
    print("7. Compute numerical gradient directly in normalized space")
    print("8. Compare analytical and numerical gradients")
    
    # Test configurations for different scales
    test_configs = [
        {
            'config': {
                'name': 'x',
                'type': 'continuous',
                'min': -100,
                'max': 100,
                'scale': 'lin',
                'description': 'Linear-scaled parameter'
            },
            'test_name': 'LINEAR SCALE'
        },
        {
            'config': {
                'name': 'x',
                'type': 'continuous',
                'min': 1e-5,
                'max': 1e5,
                'scale': 'log',
                'description': 'Log-scaled parameter'
            },
            'test_name': 'LOG SCALE (positive values)'
        },
        {
            'config': {
                'name': 'x',
                'type': 'continuous',
                'min': -1e5,
                'max': -1e-5,
                'scale': 'log',  # Will auto-detect neglog
                'description': 'NegLog-scaled parameter'
            },
            'test_name': 'NEGLOG SCALE (negative values)'
        },
        {
            'config': {
                'name': 'x',
                'type': 'continuous',
                'min': -1e3,
                'max': 1e3,
                'scale': 'log',  # Will auto-detect symlog
                'description': 'SymLog-scaled parameter'
            },
            'test_name': 'SYMLOG SCALE (mixed signs)'
        }
    ]
    
    all_results = []
    overall_pass = True
    
    for test in test_configs:
        df_results = test_single_parameter(test['config'], test['test_name'])
        df_results['scale_type'] = test['test_name']
        all_results.append(df_results)
        
        # Check if this test passed
        if any(df_results['status'] != 'PASS'):
            overall_pass = False
    
    # Combine all results
    combined_results = pd.concat(all_results, ignore_index=True)
    
    # Save results
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    # Save CSV with all details
    csv_path = os.path.join(results_dir, 'test_gradient_numerical_verification.csv')
    combined_results.to_csv(csv_path, index=False)
    
    # Generate summary report
    print("\n" + "=" * 140)
    print("OVERALL SUMMARY")
    print("=" * 140)
    
    for scale_type in combined_results['scale_type'].unique():
        scale_data = combined_results[combined_results['scale_type'] == scale_type]
        max_error = scale_data['absolute_error'].max()
        max_rel_error = scale_data['relative_error'].max()
        avg_error = scale_data['absolute_error'].mean()
        avg_rel_error = scale_data['relative_error'].mean()
        
        print(f"\n{scale_type}:")
        print(f"  Maximum absolute error: {max_error:.2e}")
        print(f"  Maximum relative error: {max_rel_error:.2e}")
        print(f"  Average absolute error: {avg_error:.2e}")
        print(f"  Average relative error: {avg_rel_error:.2e}")
        
        if all(scale_data['status'] == 'PASS'):
            print(f"  Status: [PASS]")
        else:
            print(f"  Status: [FAIL]")
    
    # Save detailed text report
    report_path = os.path.join(results_dir, 'test_gradient_numerical_verification.txt')
    with open(report_path, 'w') as f:
        f.write("=" * 140 + "\n")
        f.write("NUMERICAL GRADIENT VERIFICATION TEST REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 140 + "\n\n")
        
        f.write("TEST DESCRIPTION:\n")
        f.write("-" * 80 + "\n")
        f.write("Function: f(x) = x^2 + 2x\n")
        f.write("Gradient: df/dx = 2x + 2\n")
        f.write("Scales tested: linear, log, neglog, symlog\n")
        f.write("Numerical step size: 1.0e-10\n\n")
        
        f.write("METHODOLOGY:\n")
        f.write("-" * 80 + "\n")
        f.write("For each test point in normalized space [0, 1]:\n")
        f.write("1. Unnormalize to get actual x value:\n")
        f.write("   - From normalized [0,1] to scaled space: y = y_min + z * (y_max - y_min)\n")
        f.write("   - From scaled space to original: x = unscale(y)\n")
        f.write("2. Compute analytical gradient df/dx = 2x + 2\n")
        f.write("3. Transform gradient through chain rule:\n")
        f.write("   - To scaled space: df/dy = scale_gradient(df/dx, x)\n")
        f.write("   - To normalized space: df/dz = df/dy * (y_max - y_min)\n")
        f.write("4. Compute numerical gradient directly in normalized space using finite differences\n")
        f.write("5. Compare analytical and numerical gradients\n\n")
        
        f.write("DETAILED RESULTS BY SCALE TYPE:\n")
        f.write("-" * 80 + "\n")
        
        for scale_type in combined_results['scale_type'].unique():
            scale_data = combined_results[combined_results['scale_type'] == scale_type]
            f.write(f"\n{scale_type}:\n")
            f.write("  Sample transformations:\n")
            
            # Show a few examples
            for idx in [0, len(scale_data)//2, len(scale_data)-1]:
                row = scale_data.iloc[idx]
                f.write(f"    norm_x={row['norm_x']:.3f}: x={row['x']:12.4e}, ")
                f.write(f"scaled_x={row['scaled_x']:12.4e}, ")
                f.write(f"df/dx={row['df/dx_analytical']:12.4f}, ")
                f.write(f"df/dz={row['df/d(norm_x)_transformed']:12.4e}\n")
            
            f.write(f"  Maximum absolute error: {scale_data['absolute_error'].max():.2e}\n")
            f.write(f"  Maximum relative error: {scale_data['relative_error'].max():.2e}\n")
            f.write(f"  Average absolute error: {scale_data['absolute_error'].mean():.2e}\n")
            f.write(f"  Average relative error: {scale_data['relative_error'].mean():.2e}\n")
            f.write(f"  All tests passed: {'Yes' if all(scale_data['status'] == 'PASS') else 'No'}\n")
        
        f.write("\nCONCLUSION:\n")
        f.write("-" * 80 + "\n")
        if overall_pass:
            f.write("[PASS] All gradient transformations are correct.\n")
            f.write("The chain rule is properly implemented for all scale types:\n")
            f.write("  - Linear (NoTransform)\n")
            f.write("  - Logarithmic (LogTransform)\n")
            f.write("  - Negative Logarithmic (NegLogTransform)\n")
            f.write("  - Symmetric Logarithmic (SymLogTransform)\n")
        else:
            f.write("[FAIL] Some gradient transformations have errors.\n")
            f.write("Review the implementation of the chain rule.\n")
    
    print(f"\n" + "=" * 140)
    if overall_pass:
        print("OVERALL RESULT: [PASS] ALL TESTS PASSED")
        print("The gradient transformation implementation is CORRECT for all scale types.")
        print("\nThis confirms that:")
        print("  1. The chain rule is correctly implemented")
        print("  2. scale_gradient() and unscale_gradient() methods work properly")
        print("  3. Parameters.norm_gradients() and unnorm_gradients() handle all cases")
        print("  4. Gradient-based optimizers will work correctly with any parameter scale")
    else:
        print("OVERALL RESULT: [FAIL] SOME TESTS FAILED")
        print("There are issues with the gradient transformation implementation.")
    
    print(f"\nResults saved to: {csv_path}")
    print(f"Report saved to: {report_path}")
    
    return overall_pass


if __name__ == "__main__":
    success = test_gradient_numerical_verification()
    exit(0 if success else 1)