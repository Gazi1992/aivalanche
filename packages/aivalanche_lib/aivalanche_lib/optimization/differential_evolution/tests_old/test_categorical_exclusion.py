"""
Test that categorical parameters are properly excluded from perturbation and refinement.
"""

import numpy as np
import pandas as pd
from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import sphere


def test_categorical_parameter_exclusion():
    """Test that categorical parameters are excluded from perturbation and refinement."""
    
    print("\n" + "="*60)
    print("TESTING CATEGORICAL PARAMETER EXCLUSION")
    print("="*60)
    
    # Define mixed parameter types
    params = Parameters([
        {'name': 'x1', 'type': 'continuous', 'min': -5, 'max': 5, 'default': 0},
        {'name': 'x2', 'type': 'continuous', 'min': -5, 'max': 5, 'default': 0},
        {'name': 'discrete_param', 'type': 'discrete', 'values': [1, 2, 3, 4, 5], 'default': 3},
        {'name': 'category', 'type': 'categorical', 'values': ['A', 'B', 'C'], 'default': 'B'},
        {'name': 'optimizer', 'type': 'categorical', 'values': ['adam', 'sgd', 'rmsprop'], 'default': 'adam'}
    ])
    
    print("\nParameter types:")
    for _, row in params.all_parameters.iterrows():
        print(f"  {row['name']}: {row['type']}")
    
    # Create evaluation function that uses all parameters
    def eval_func(parameters_df, **kwargs):
        results = []
        for _, params in parameters_df.iterrows():
            # Use continuous parameters for sphere function
            x = np.array([params['x1'], params['x2']])
            base_metric = sphere(x)
            
            # Add penalties/bonuses based on other parameters
            # Discrete parameter affects magnitude
            base_metric *= params['discrete_param']
            
            # Categorical parameters affect the result
            if params['category'] == 'A':
                base_metric *= 1.1
            elif params['category'] == 'C':
                base_metric *= 0.9
            
            if params['optimizer'] == 'sgd':
                base_metric *= 1.05
            elif params['optimizer'] == 'rmsprop':
                base_metric *= 0.95
                
            results.append({'metric': base_metric})
        
        return pd.DataFrame(results)
    
    # Test 1: Perturbation excludes categorical parameters
    print("\n" + "-"*40)
    print("TEST 1: Perturbation System")
    print("-"*40)
    
    # Create optimizer with perturbation
    optimizer = DifferentialEvolution(
        eval_func=eval_func,
        parameters=params,
        pop_size=20,
        max_iterations=50,
        max_iter_without_improvement=10,  # Trigger perturbation quickly
        perturbation_mode='aggressive',
        refinement_mode='off',
        seed=42,
        verbose=False
    )
    
    # Access internal methods to test parameter selection
    from aivalanche_lib.optimization.differential_evolution.perturbation import (
        _setup_perturbation_config, _select_parameters_for_perturbation
    )
    
    # Setup perturbation config
    _setup_perturbation_config(optimizer)
    
    # Test parameter selection for all methods
    for method in ['random', 'variance', 'smart', 'all']:
        optimizer._perturbation_active_config['param_selection'] = method
        selected = _select_parameters_for_perturbation(optimizer)
        
        print(f"\nSelection method '{method}':")
        print(f"  Selected indices: {selected}")
        selected_names = [optimizer.variable_parameters_names[i] for i in selected]
        print(f"  Selected names: {selected_names}")
        
        # Verify no categorical parameters were selected
        variable_params = optimizer.parameters.variable_parameters
        for idx in selected:
            param_type = variable_params.iloc[idx]['type']
            assert param_type != 'categorical', \
                f"Categorical parameter at index {idx} was selected!"
    
    # Test 2: Refinement excludes categorical parameters
    print("\n" + "-"*40)
    print("TEST 2: Refinement System")
    print("-"*40)
    
    # Test refinement parameter creation
    from aivalanche_lib.optimization.differential_evolution.refinement import _create_refinement_parameters
    
    refinement_params = _create_refinement_parameters(optimizer)
    
    print(f"\nOriginal variable parameters: {optimizer.variable_parameters_names}")
    print(f"Refinement variable parameters: {refinement_params.variable_parameters_names}")
    
    # Verify categorical parameters are not in refinement parameters
    for name in refinement_params.variable_parameters_names:
        param_type = params.all_parameters[params.all_parameters['name'] == name]['type'].iloc[0]
        assert param_type != 'categorical', \
            f"Categorical parameter '{name}' included in refinement!"
    
    # Verify categorical parameters are marked as fixed in refinement
    for _, row in refinement_params.all_parameters.iterrows():
        if row['type'] == 'categorical':
            assert row['mode'] == 'fixed', \
                f"Categorical parameter '{row['name']}' not marked as fixed!"
    
    # Test 3: Run actual optimization to ensure it works
    print("\n" + "-"*40)
    print("TEST 3: Full Optimization Run")
    print("-"*40)
    
    optimizer2 = DifferentialEvolution(
        eval_func=eval_func,
        parameters=params,
        pop_size=30,
        max_iterations=100,
        perturbation_mode='auto',
        refinement_mode='light',
        seed=42,
        verbose=False
    )
    
    best_params, best_metric = optimizer2.run_optimization()
    
    print(f"\nOptimization completed successfully!")
    print(f"Best metric: {best_metric:.6f}")
    print(f"Best parameters:")
    for name, value in best_params.items():
        print(f"  {name}: {value}")
    
    # Verify categorical parameters have valid values
    assert best_params['category'] in ['A', 'B', 'C'], \
        f"Invalid category value: {best_params['category']}"
    assert best_params['optimizer'] in ['adam', 'sgd', 'rmsprop'], \
        f"Invalid optimizer value: {best_params['optimizer']}"
    
    print("\n✓ All tests passed! Categorical parameters are properly excluded.")


if __name__ == "__main__":
    test_categorical_parameter_exclusion()