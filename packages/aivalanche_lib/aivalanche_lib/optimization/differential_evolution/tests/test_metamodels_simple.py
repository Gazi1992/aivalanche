"""
Simple metamodel test to verify functionality and generate results.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from aivalanche_lib.optimization.differential_evolution import DifferentialEvolution
from aivalanche_lib.parameters import Parameters
from aivalanche_lib.test_functions import get_function_details

from test_utils import create_test_results_dir, save_test_summary, create_test_function_wrapper


def main():
    """Run simple metamodel test."""
    print("Simple Metamodel Test")
    print("=" * 60)
    
    # Create results directory
    results_dir = create_test_results_dir('metamodels_simple')
    
    # Test on a simple 2D function
    func_details = get_function_details('himmelblau_2d')
    eval_func = create_test_function_wrapper(func_details)
    
    parameters = Parameters([
        {'name': 'x', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0},
        {'name': 'y', 'type': 'continuous', 'min': -5.0, 'max': 5.0, 'default': 0.0}
    ])
    
    # Test configurations
    configs = {
        'Without Metamodel': {
            'pop_size': 20,
            'max_iterations': 50,
            'metamodel_mode': 'off'
        },
        'With Metamodel': {
            'pop_size': 20,
            'max_iterations': 50,
            'metamodel_mode': 'auto'
        }
    }
    
    results = {}
    
    for name, config in configs.items():
        print(f"\nTesting {name}...")
        
        optimizer = DifferentialEvolution(
            seed=42,
            eval_func=eval_func,
            parameters=parameters,
            **config
        )
        
        optimizer.run_optimization()
        
        results[name] = {
            'best_metric': optimizer.best_metric,
            'iterations': optimizer.iter,
            'evaluations': optimizer.nr_evaluations
        }
        
        print(f"  Best metric: {optimizer.best_metric:.6e}")
        print(f"  Evaluations: {optimizer.nr_evaluations}")
    
    # Create simple comparison plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot 1: Final metrics
    names = list(results.keys())
    metrics = [results[n]['best_metric'] for n in names]
    
    ax1.bar(names, metrics, color=['lightblue', 'lightgreen'])
    ax1.set_ylabel('Best Metric')
    ax1.set_title('Final Performance')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Evaluations
    evals = [results[n]['evaluations'] for n in names]
    
    ax2.bar(names, evals, color=['lightcoral', 'lightyellow'])
    ax2.set_ylabel('Function Evaluations')
    ax2.set_title('Computational Cost')
    ax2.grid(True, alpha=0.3)
    
    # Add percentage saved
    if evals[0] > 0:
        saved_pct = (evals[0] - evals[1]) / evals[0] * 100
        ax2.text(0.5, max(evals) * 0.9, f'Saved: {saved_pct:.1f}%', 
                ha='center', fontsize=14, weight='bold')
    
    plt.suptitle('Metamodel Test Results', fontsize=16)
    plt.tight_layout()
    
    plot_file = os.path.join(results_dir, 'metamodel_simple_comparison.png')
    plt.savefig(plot_file, dpi=150)
    plt.close()
    
    # Save summary
    summary = {
        'test_name': 'Simple Metamodel Test',
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'evaluations_saved': evals[0] - evals[1] if len(evals) >= 2 else 0
    }
    save_test_summary(results_dir, summary)
    
    print(f"\nResults saved to: {results_dir}")


if __name__ == "__main__":
    main()