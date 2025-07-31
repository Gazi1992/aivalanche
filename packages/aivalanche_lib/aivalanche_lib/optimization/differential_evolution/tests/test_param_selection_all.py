"""
Quick test to verify that param_selection='all' works correctly.
"""

import numpy as np
from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details, generate_parameters_config


def test_param_selection_all():
    """Test that param_selection='all' perturbs all parameters."""
    print("\n" + "="*60)
    print("TESTING param_selection='all'")
    print("="*60)
    
    # Setup test function
    func_name = 'sphere_nd'
    n_dim = 5
    func_details = get_function_details(func_name, n_dim=n_dim)
    param_config = generate_parameters_config(func_details)
    parameters = Parameters(param_config)
    
    # Create evaluation function
    def eval_func(parameters_df, **kwargs):
        responses = []
        for _, row in parameters_df.iterrows():
            x = np.array([row[f'x{i+1}'] for i in range(n_dim)])
            value = func_details['func'](x)
            responses.append({'metric': value})
        return responses
    
    # Test with emergency mode which uses param_selection='all'
    print("\nTesting with 'emergency' mode (uses param_selection='all')...")
    
    optimizer = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        pop_size=20,
        max_iterations=100,
        max_iter_without_improvement=10,  # Low threshold to trigger perturbation
        perturbation_mode='emergency'  # This mode uses param_selection='all'
    )
    
    # Run optimization
    optimizer.run_optimization()
    
    print(f"\nOptimization completed:")
    print(f"  Best metric: {optimizer.best_metric:.6e}")
    print(f"  Iterations: {optimizer.iter}")
    
    # Check perturbation history
    if hasattr(optimizer, 'perturbation_memory') and 'history' in optimizer.perturbation_memory:
        print(f"\nPerturbation events:")
        for event in optimizer.perturbation_memory['history']:
            n_params_perturbed = len(event.get('perturbed_params', []))
            print(f"  Iteration {event['iteration']}: {n_params_perturbed} parameters perturbed")
            if n_params_perturbed == n_dim:
                print(f"    ✓ All {n_dim} parameters were perturbed!")
            else:
                print(f"    ✗ Expected {n_dim} parameters, but only {n_params_perturbed} were perturbed")
    
    # Also test with custom configuration
    print("\n" + "-"*60)
    print("Testing with custom configuration using param_selection='all'...")
    
    optimizer2 = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        pop_size=20,
        max_iterations=100,
        max_iter_without_improvement=10,
        perturbation_mode='custom',
        perturbation_config={
            'trigger_ratio': 0.5,
            'param_selection': 'all',  # Explicitly set to 'all'
            'param_ratio': 0.5,  # This should be ignored
            'population_ratio': 0.5,
            'scale': 'adaptive',
            'memory_enabled': False,
            'cooldown_ratio': 0.1,
            'sigma_threshold': 0.01
        }
    )
    
    # Run optimization
    optimizer2.run_optimization()
    
    print(f"\nOptimization completed:")
    print(f"  Best metric: {optimizer2.best_metric:.6e}")
    print(f"  Iterations: {optimizer2.iter}")
    
    # Check perturbation history
    if hasattr(optimizer2, 'perturbation_memory') and 'history' in optimizer2.perturbation_memory:
        print(f"\nPerturbation events:")
        for event in optimizer2.perturbation_memory['history']:
            n_params_perturbed = len(event.get('perturbed_params', []))
            print(f"  Iteration {event['iteration']}: {n_params_perturbed} parameters perturbed")
            if n_params_perturbed == n_dim:
                print(f"    ✓ All {n_dim} parameters were perturbed!")
            else:
                print(f"    ✗ Expected {n_dim} parameters, but only {n_params_perturbed} were perturbed")


if __name__ == "__main__":
    test_param_selection_all()
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60)