"""
Text-based comparison test for metamodel refinement.
Shows clear statistics comparing refinement with and without metamodel.
"""

import sys
import os
import numpy as np
import time
from typing import Dict

# Add the package to path
sys.path.append(os.path.join(os.getcwd(), 'packages/aivalanche_lib'))

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.parameters import Parameters


def run_test(use_metamodel: bool, function_name: str = 'sphere') -> Dict:
    """Run a single test with or without metamodel refinement."""
    
    # Create parameters
    parameters = Parameters([
        {'name': 'x', 'min': -5.0, 'max': 5.0},
        {'name': 'y', 'min': -5.0, 'max': 5.0}
    ])
    
    # Track evaluations
    eval_count = {'count': 0, 'refinement_start': 0}
    
    # Create evaluation function based on type
    if function_name == 'sphere':
        def eval_func(parameters, **kwargs):
            eval_count['count'] += len(parameters)
            responses = []
            for _, row in parameters.iterrows():
                x, y = row['x'], row['y']
                metric = x**2 + y**2
                responses.append({'metric': metric})
            return responses
        optimal_point = (0, 0)
        optimal_value = 0
    elif function_name == 'rosenbrock':
        def eval_func(parameters, **kwargs):
            eval_count['count'] += len(parameters)
            responses = []
            for _, row in parameters.iterrows():
                x, y = row['x'], row['y']
                metric = (1 - x)**2 + 100 * (y - x**2)**2
                responses.append({'metric': metric})
            return responses
        optimal_point = (1, 1)
        optimal_value = 0
    else:
        raise ValueError(f"Unknown function: {function_name}")
    
    # Configure DE
    de = DifferentialEvolution(
        seed=42,
        eval_func=eval_func,
        parameters=parameters,
        opt_min_or_max='min',
        pop_size=20,
        max_iterations=8,
        
        # No metamodel during main optimization
        metamodel_mode='off',
        
        # Configure refinement
        refinement_mode='on',
        refinement_config={
            'method': 'dls',
            'trigger_ratio': -1,  # Only at end
            'max_iterations': 100,
            'use_metamodel': use_metamodel,
            'metamodel_min_training_points': 20,
            'metamodel_min_accuracy': 0.8
        }
    )
    
    # Run optimization
    start_time = time.time()
    de.run_optimization()
    elapsed_time = time.time() - start_time
    
    # Mark refinement start
    eval_count['refinement_start'] = de.pop_size * de.iter
    
    # Calculate results
    distance_to_optimum = np.sqrt(
        (de.best_parameters['x'] - optimal_point[0])**2 + 
        (de.best_parameters['y'] - optimal_point[1])**2
    )
    
    results = {
        'use_metamodel': use_metamodel,
        'best_metric': de.best_metric,
        'best_x': de.best_parameters['x'],
        'best_y': de.best_parameters['y'],
        'distance_to_optimum': distance_to_optimum,
        'total_evaluations': eval_count['count'],
        'de_evaluations': eval_count['refinement_start'],
        'refinement_evaluations': eval_count['count'] - eval_count['refinement_start'],
        'elapsed_time': elapsed_time,
        'refinement_used_metamodel': False
    }
    
    # Check if metamodel was actually used
    if hasattr(de, 'refinement_info') and de.refinement_info:
        results['refinement_used_metamodel'] = de.refinement_info.get('used_metamodel', False)
        results['refinement_improved'] = de.refinement_info.get('improved', False)
        results['refinement_iterations'] = de.refinement_info.get('iterations', 0)
    
    return results


def compare_methods(function_name: str = 'sphere'):
    """Compare refinement with and without metamodel."""
    
    print(f"\n{'='*70}")
    print(f"COMPARING METAMODEL REFINEMENT - {function_name.upper()} FUNCTION")
    print(f"{'='*70}")
    
    # Run with metamodel
    print("\nRunning WITH metamodel refinement...")
    results_with = run_test(use_metamodel=True, function_name=function_name)
    
    # Run without metamodel
    print("Running WITHOUT metamodel refinement...")
    results_without = run_test(use_metamodel=False, function_name=function_name)
    
    # Print detailed comparison
    print(f"\n{'-'*70}")
    print("DETAILED RESULTS")
    print(f"{'-'*70}")
    
    print("\n1. SOLUTION QUALITY:")
    print(f"   {'Method':<25} {'Best Metric':<15} {'Distance to Optimum':<20}")
    print(f"   {'-'*60}")
    print(f"   {'With Metamodel':<25} {results_with['best_metric']:<15.6e} {results_with['distance_to_optimum']:<20.6f}")
    print(f"   {'Without Metamodel':<25} {results_without['best_metric']:<15.6e} {results_without['distance_to_optimum']:<20.6f}")
    
    # Quality comparison
    if results_with['best_metric'] < results_without['best_metric']:
        improvement = (results_without['best_metric'] - results_with['best_metric']) / results_without['best_metric'] * 100
        print(f"   --> Metamodel refinement is BETTER by {improvement:.2f}%")
    elif results_with['best_metric'] > results_without['best_metric']:
        degradation = (results_with['best_metric'] - results_without['best_metric']) / results_without['best_metric'] * 100
        print(f"   --> Metamodel refinement is WORSE by {degradation:.2f}%")
    else:
        print(f"   --> Both methods achieved the same quality")
    
    print("\n2. COMPUTATIONAL EFFICIENCY:")
    print(f"   {'Method':<25} {'Total Evals':<12} {'DE Evals':<12} {'Refine Evals':<15}")
    print(f"   {'-'*60}")
    print(f"   {'With Metamodel':<25} {results_with['total_evaluations']:<12} {results_with['de_evaluations']:<12} {results_with['refinement_evaluations']:<15}")
    print(f"   {'Without Metamodel':<25} {results_without['total_evaluations']:<12} {results_without['de_evaluations']:<12} {results_without['refinement_evaluations']:<15}")
    
    # Efficiency comparison
    eval_savings = results_without['refinement_evaluations'] - results_with['refinement_evaluations']
    eval_savings_pct = (eval_savings / results_without['refinement_evaluations']) * 100 if results_without['refinement_evaluations'] > 0 else 0
    
    print(f"   --> Evaluation savings: {eval_savings} ({eval_savings_pct:.1f}% reduction)")
    
    print("\n3. TIME PERFORMANCE:")
    print(f"   {'Method':<25} {'Time (seconds)':<15}")
    print(f"   {'-'*40}")
    print(f"   {'With Metamodel':<25} {results_with['elapsed_time']:<15.3f}")
    print(f"   {'Without Metamodel':<25} {results_without['elapsed_time']:<15.3f}")
    
    time_savings = results_without['elapsed_time'] - results_with['elapsed_time']
    time_savings_pct = (time_savings / results_without['elapsed_time']) * 100 if results_without['elapsed_time'] > 0 else 0
    
    if time_savings > 0:
        print(f"   --> Time savings: {time_savings:.3f}s ({time_savings_pct:.1f}% faster)")
    else:
        print(f"   --> Time overhead: {-time_savings:.3f}s ({-time_savings_pct:.1f}% slower)")
    
    print("\n4. REFINEMENT DETAILS:")
    print(f"   With Metamodel:")
    print(f"      - Actually used metamodel: {results_with['refinement_used_metamodel']}")
    print(f"      - Refinement improved: {results_with.get('refinement_improved', 'N/A')}")
    print(f"      - Refinement iterations: {results_with.get('refinement_iterations', 'N/A')}")
    print(f"   Without Metamodel:")
    print(f"      - Refinement improved: {results_without.get('refinement_improved', 'N/A')}")
    print(f"      - Refinement iterations: {results_without.get('refinement_iterations', 'N/A')}")
    
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    if eval_savings > 0:
        print(f"[SUCCESS] Metamodel refinement saved {eval_savings} evaluations ({eval_savings_pct:.1f}%)")
    else:
        print(f"[INFO] Metamodel refinement used {-eval_savings} more evaluations")
    
    if results_with['best_metric'] <= results_without['best_metric']:
        print(f"[SUCCESS] Solution quality maintained or improved")
    else:
        print(f"[INFO] Solution quality degraded slightly")
    
    if results_with['refinement_used_metamodel']:
        print(f"[SUCCESS] Metamodel was successfully used for refinement")
    else:
        print(f"[INFO] Metamodel criteria not met - fell back to real function")
    
    print(f"\nFor expensive objective functions, saving {eval_savings} evaluations")
    print(f"would provide significant computational savings.")
    
    return results_with, results_without


def main():
    """Run comparison for multiple test functions."""
    
    print("\n" + "="*70)
    print("METAMODEL REFINEMENT COMPARISON TEST")
    print("="*70)
    print("\nThis test compares Differential Evolution refinement with and without")
    print("using a metamodel (Gaussian Process) for the refinement phase.")
    
    # Test on different functions
    test_functions = ['sphere', 'rosenbrock']
    
    all_results = {}
    total_eval_savings = 0
    
    for func_name in test_functions:
        results_with, results_without = compare_methods(func_name)
        all_results[func_name] = {
            'with': results_with,
            'without': results_without
        }
        
        eval_savings = results_without['refinement_evaluations'] - results_with['refinement_evaluations']
        total_eval_savings += eval_savings
    
    # Overall summary
    print("\n" + "="*70)
    print("OVERALL SUMMARY ACROSS ALL FUNCTIONS")
    print("="*70)
    
    print(f"\nTotal evaluation savings: {total_eval_savings}")
    
    successful_uses = sum(1 for func in all_results.values() 
                         if func['with']['refinement_used_metamodel'])
    print(f"Metamodel successfully used: {successful_uses}/{len(test_functions)} functions")
    
    quality_maintained = sum(1 for func in all_results.values()
                            if func['with']['best_metric'] <= func['without']['best_metric'])
    print(f"Quality maintained/improved: {quality_maintained}/{len(test_functions)} functions")
    
    print("\n" + "="*70)
    print("TEST COMPLETED SUCCESSFULLY")
    print("="*70)
    
    return all_results


if __name__ == "__main__":
    results = main()