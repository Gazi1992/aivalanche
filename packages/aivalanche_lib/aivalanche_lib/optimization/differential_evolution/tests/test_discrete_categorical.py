"""Test DE on discrete and categorical functions only."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from test_de_performance import test_function_optimization, create_test_results_dir, create_enhanced_animation, create_evolution_plots, create_performance_summary, save_test_summary
from aivalanche_lib.test_functions import get_function_details
from datetime import datetime

# Test only discrete and categorical functions
test_functions = [
    # Discrete functions
    'discrete_rastrigin_2d',
    'step_function_2d',
    'integer_quadratic_2d',
    # Mixed/Categorical functions
    'string_categorical_mixed_2d',
    'integer_categorical_2d',
    'discrete_categorical_2d',
    'mixed_discrete_continuous_2d',
    'categorical_interaction_2d'
]

print("Testing Discrete and Categorical Functions")
print("=" * 60)

# Create results directory
results_dir = create_test_results_dir('discrete_categorical_test')
results = {}

# Test each function
for func_name in test_functions:
    result = test_function_optimization(func_name, results_dir, max_iter=100)
    
    if result is not None:
        results[func_name] = result
        
        # Create visualizations for 2D functions
        func_details = get_function_details(func_name)
        func_results_dir = os.path.join(results_dir, func_name)
        
        # Always create evolution plots (works for all functions)
        create_evolution_plots(result['optimizer'], func_name, func_results_dir)
        
        # Create animation for 2D functions (now supports categorical)
        if result['optimizer'].nr_variable_parameters == 2:
            create_enhanced_animation(result['optimizer'], func_name, func_results_dir)
        else:
            print(f"  Skipping animation for {func_name} (not 2D)")

# Create summary plots
create_performance_summary(results, results_dir)

# Save test summary
summary = {
    'test_name': 'Discrete and Categorical Functions Test',
    'timestamp': datetime.now().isoformat(),
    'functions_tested': list(results.keys()),
    'results': {
        name: {
            'best_metric': res['best_metric'],
            'optimum_val': res['optimum_val'],
            'error': res['error'],
            'iterations': res['iterations'],
            'evaluations': res['evaluations'],
            'distance_to_optimum': res['distance_to_optimum'],
            'stop_reason': res['stop_reason'],
            'has_categorical': res['has_categorical']
        }
        for name, res in results.items()
    }
}
save_test_summary(results_dir, summary)

print(f"\n{'='*60}")
print("Test completed!")
print(f"Results saved to: {results_dir}")