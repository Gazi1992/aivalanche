"""Test DE on a single function to verify visualizations."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from test_de_performance import test_function_optimization, create_test_results_dir, create_enhanced_animation
from aivalanche_lib.test_functions import get_function_details

# Choose which function to test
# test_func = 'rosenbrock_2d'  # Continuous - good for testing visualization
# test_func = 'himmelblau_2d'  # Has multiple minima - good for testing visualization
# test_func = 'discrete_rastrigin_2d'  # Discrete
# test_func = 'integer_quadratic_2d'  # Integer discrete - checking visualization
# test_func = 'string_categorical_mixed_2d'  # Mixed with categorical - testing categorical boundaries
test_func = 'rastrigin_nd'  # Testing nD function

print(f"Testing function: {test_func}")
# For nD functions, specify dimension
n_dim = 2 if test_func.endswith('_nd') else None
func_details = get_function_details(test_func, n_dim)
print(f"Function type: {func_details.get('param_types', ['continuous'])}")
print(f"Bounds: {func_details['bounds']}")

# Test the function
results_dir = create_test_results_dir('single_function_test')
result = test_function_optimization(test_func, results_dir, n_dim=n_dim, max_iter=50)

if result is not None:
    func_results_dir = os.path.join(results_dir, test_func)
    
    # Always create evolution plots (works for all functions)
    from test_de_performance import create_evolution_plots
    create_evolution_plots(result['optimizer'], test_func, func_results_dir)
    
    # Create animation for 2D functions (now supports categorical)
    if result['optimizer'].nr_variable_parameters == 2:
        # Determine n_dim for nD functions
        n_dim = 2 if test_func.endswith('_nd') else None
        create_enhanced_animation(result['optimizer'], test_func, func_results_dir, n_dim)
    else:
        print("\nSkipping animation (not a 2D function)")

print("\nTest completed!")
print(f"Results saved to: {results_dir}")