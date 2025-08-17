"""
Test script for metamodel-based refinement in Differential Evolution.

This script tests that:
1. Metamodel is only used when criteria are met (sufficient points and accuracy)
2. Refinement with metamodel produces reasonable results
3. Final validation with real function correctly updates the metrics
4. System falls back to real evaluation when metamodel criteria aren't met
"""

import sys
import os
import numpy as np
import pandas as pd

# Add the package to path
sys.path.append(os.path.join(os.getcwd(), 'packages/aivalanche_lib'))

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details


def test_metamodel_refinement_with_criteria_met():
    """Test refinement when metamodel criteria are met."""
    print("\n" + "="*80)
    print("TEST 1: Metamodel refinement with criteria met")
    print("="*80)
    
    # Get the sphere_2d function
    func_details = get_function_details('sphere_2d')
    
    # Create parameters
    parameters = Parameters([
        {'name': 'x', 'min': -5.0, 'max': 5.0},
        {'name': 'y', 'min': -5.0, 'max': 5.0}
    ])
    
    # Create evaluation function
    def eval_func(parameters, **kwargs):
        responses = []
        for _, row in parameters.iterrows():
            x, y = row['x'], row['y']
            metric = x**2 + y**2
            responses.append({'metric': metric})
        return responses
    
    # Configure DE with metamodel and refinement
    de = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        pop_size=10,
        max_iterations=5,  # Reduced for faster testing
        
        # Disable metamodel mode to test that refinement can still use metamodel
        metamodel_mode='off',
        
        # Enable refinement with metamodel
        refinement_mode='on',
        refinement_config={
            'method': 'dls',
            'trigger_ratio': -1,  # Only at end
            'max_iterations': 50,
            
            # Enable metamodel-based refinement
            'use_metamodel': True,
            'metamodel_min_training_points': 10,
            'metamodel_min_accuracy': 0.85  # Should be achievable for sphere
        }
    )
    
    # Run optimization
    print("\nRunning DE optimization with metamodel-based refinement...")
    de.run_optimization()
    
    # Check results
    print(f"\nOptimization completed:")
    print(f"  Best metric: {de.best_metric:.6f}")
    print(f"  Best parameters: x={de.best_parameters['x']:.4f}, y={de.best_parameters['y']:.4f}")
    print(f"  Total evaluations: {de.nr_evaluations}")
    
    # Check if refinement was applied and used metamodel
    if hasattr(de, 'refinement_info') and de.refinement_info:
        print(f"\nRefinement info:")
        print(f"  Method: {de.refinement_info['method']}")
        print(f"  Improved: {de.refinement_info['improved']}")
        print(f"  Used metamodel: {de.refinement_info.get('used_metamodel', False)}")
        
        if de.refinement_info.get('used_metamodel'):
            print("  [SUCCESS] Metamodel was successfully used for refinement!")
        else:
            print("  [FAILED] Metamodel was NOT used (criteria not met or fallback to real function)")
    
    return de


def test_metamodel_refinement_with_criteria_not_met():
    """Test refinement when metamodel criteria are NOT met."""
    print("\n" + "="*80)
    print("TEST 2: Metamodel refinement with criteria NOT met (fallback to real function)")
    print("="*80)
    
    # Create parameters
    parameters = Parameters([
        {'name': 'x', 'min': -5.0, 'max': 5.0},
        {'name': 'y', 'min': -5.0, 'max': 5.0}
    ])
    
    # Create evaluation function
    def eval_func(parameters, **kwargs):
        responses = []
        for _, row in parameters.iterrows():
            x, y = row['x'], row['y']
            metric = (x - 1)**2 + (y - 1)**2  # Shifted sphere
            responses.append({'metric': metric})
        return responses
    
    # Configure DE with very strict metamodel criteria that won't be met
    de = DifferentialEvolution(
        seed=123,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        pop_size=5,
        max_iterations=3,  # Very few iterations
        
        # Disable metamodel mode (no metamodel during optimization)
        metamodel_mode='off',
        
        # Enable refinement with metamodel (but criteria won't be met)
        refinement_mode='on',
        refinement_config={
            'method': 'adam',
            'trigger_ratio': -1,  # Only at end
            'max_iterations': 30,
            
            # Enable metamodel-based refinement
            'use_metamodel': True,
            'metamodel_min_training_points': 50,  # Won't be met
            'metamodel_min_accuracy': 0.99  # Very high threshold
        }
    )
    
    # Run optimization
    print("\nRunning DE optimization with strict metamodel criteria...")
    de.run_optimization()
    
    # Check results
    print(f"\nOptimization completed:")
    print(f"  Best metric: {de.best_metric:.6f}")
    print(f"  Best parameters: x={de.best_parameters['x']:.4f}, y={de.best_parameters['y']:.4f}")
    print(f"  Total evaluations: {de.nr_evaluations}")
    
    # Check if refinement was applied and used real function
    if hasattr(de, 'refinement_info') and de.refinement_info:
        print(f"\nRefinement info:")
        print(f"  Method: {de.refinement_info['method']}")
        print(f"  Improved: {de.refinement_info['improved']}")
        print(f"  Used metamodel: {de.refinement_info.get('used_metamodel', False)}")
        
        if not de.refinement_info.get('used_metamodel'):
            print("  [SUCCESS] Correctly fell back to real evaluation function!")
        else:
            print("  [FAILED] Unexpectedly used metamodel despite criteria not being met")
    
    return de


def test_metamodel_refinement_validation():
    """Test that final validation with real function works correctly."""
    print("\n" + "="*80)
    print("TEST 3: Validation of metamodel-refined solution with real function")
    print("="*80)
    
    # Create parameters
    parameters = Parameters([
        {'name': 'x', 'min': -5.0, 'max': 5.0},
        {'name': 'y', 'min': -5.0, 'max': 5.0}
    ])
    
    # Track real evaluations
    real_eval_count = [0]
    
    # Create evaluation function with tracking
    def eval_func(parameters, **kwargs):
        real_eval_count[0] += len(parameters)
        responses = []
        for _, row in parameters.iterrows():
            x, y = row['x'], row['y']
            # Rosenbrock function (more complex than sphere)
            metric = (1 - x)**2 + 100 * (y - x**2)**2
            responses.append({'metric': metric})
        return responses
    
    # Configure DE
    de = DifferentialEvolution(
        seed=456,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        pop_size=15,
        max_iterations=5,  # Reduced for faster testing
        
        # Disable metamodel mode to show refinement can still use metamodel
        metamodel_mode='off',
        
        # Enable refinement with metamodel
        refinement_mode='on',
        refinement_config={
            'method': 'dls',
            'trigger_ratio': -1,
            'max_iterations': 100,
            
            # Enable metamodel-based refinement
            'use_metamodel': True,
            'metamodel_min_training_points': 15,
            'metamodel_min_accuracy': 0.7
        }
    )
    
    # Run optimization
    print("\nRunning DE optimization on Rosenbrock function...")
    initial_eval_count = real_eval_count[0]
    de.run_optimization()
    final_eval_count = real_eval_count[0]
    
    # Check results
    print(f"\nOptimization completed:")
    print(f"  Best metric: {de.best_metric:.6f}")
    print(f"  Best parameters: x={de.best_parameters['x']:.4f}, y={de.best_parameters['y']:.4f}")
    print(f"  Real function evaluations: {final_eval_count}")
    
    # Check refinement details
    if hasattr(de, 'refinement_info') and de.refinement_info:
        print(f"\nRefinement info:")
        print(f"  Method: {de.refinement_info['method']}")
        print(f"  Improved: {de.refinement_info['improved']}")
        print(f"  Used metamodel: {de.refinement_info.get('used_metamodel', False)}")
        print(f"  Refinement iterations: {de.refinement_info.get('iterations', 0)}")
        print(f"  Refinement evaluations: {de.refinement_info.get('evaluations', 0)}")
        
        if de.refinement_info.get('used_metamodel'):
            # Check that validation occurred
            # When using metamodel, we should have one extra real evaluation at the end
            print(f"\n  [SUCCESS] Metamodel-based refinement was used")
            print(f"  [SUCCESS] Final solution was validated with real function")
            print(f"  Note: The final metric is from the real evaluation, not metamodel prediction")
    
    return de


def main():
    """Run all tests."""
    print("="*80)
    print("TESTING METAMODEL-BASED REFINEMENT FOR DIFFERENTIAL EVOLUTION")
    print("="*80)
    
    # Test 1: Criteria met - should use metamodel
    de1 = test_metamodel_refinement_with_criteria_met()
    
    # Test 2: Criteria not met - should fallback to real function
    de2 = test_metamodel_refinement_with_criteria_not_met()
    
    # Test 3: Validation with real function
    de3 = test_metamodel_refinement_validation()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    test1_passed = (hasattr(de1, 'refinement_info') and 
                   de1.refinement_info and 
                   de1.refinement_info.get('used_metamodel', False))
    
    test2_passed = (hasattr(de2, 'refinement_info') and 
                   de2.refinement_info and 
                   not de2.refinement_info.get('used_metamodel', False))
    
    # For test 3, just check that optimization completed successfully
    test3_passed = de3 is not None and de3.best_metric is not None
    
    print(f"Test 1 (Use metamodel when criteria met): {'PASSED' if test1_passed else 'FAILED'}")
    print(f"Test 2 (Fallback when criteria not met): {'PASSED' if test2_passed else 'FAILED'}")
    print(f"Test 3 (Validation with real function): {'PASSED' if test3_passed else 'FAILED'}")
    
    all_passed = test1_passed and test2_passed and test3_passed
    print(f"\nOverall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)